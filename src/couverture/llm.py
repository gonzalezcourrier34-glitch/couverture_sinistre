"""Clients de modèles de langage. Aucune dépendance : de simples appels HTTP.

Le fournisseur est Mistral (européen, données hébergées dans l'UE) : `MistralLLM`, sur une API au format
OpenAI (`OpenAICompatibleLLM`). Les tests branchent des modèles factices qui respectent le protocole `LLM`.
La configuration se fait par variables d'environnement, voir `configurer()`.
"""

from __future__ import annotations

import copy
import json
import os
import random
import re
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Protocol


class LLM(Protocol):
    nom: str

    def completer(self, systeme: str, message: str) -> str: ...


class ErreurLLM(RuntimeError):
    """Le fournisseur n'a pas pu répondre (clé, quota, réseau) : inutile de réessayer la même question."""

    def __init__(self, message: str, code: int | None = None):
        super().__init__(message)
        self.code = code  # code HTTP, s'il y en a un


class CleRefusee(ErreurLLM):
    """Clé absente ou refusée : rien ne marchera, on arrête tout (même une évaluation en cours)."""


# Appels simultanés vers le fournisseur, pour tout le programme (les cas d'une évaluation et les
# fiches d'un cas tournent en parallèle) : au-delà, Mistral répond 429, « Rate limit exceeded ».
APPELS_SIMULTANES = threading.BoundedSemaphore(max(1, int(os.environ.get("COUVERTURE_APPELS_SIMULTANES", "4") or 4)))


class ReponseTronquee(ValueError):
    """Le modèle a atteint la limite de longueur avant de finir (souvent en réfléchissant longuement).
    Traitée comme une réponse illisible : les juges réessaient, puis répondent prudemment.

    Avec COUVERTURE_DEBUG=oui, le début de la réponse coupée est écrit dans data/debug/
    pour voir ce qui a rempli la limite (liste trop longue, répétition…)."""

    def __init__(self, message: str, texte: str = ""):
        super().__init__(message)
        self.texte = texte
        if texte and os.environ.get("COUVERTURE_DEBUG", "").lower() in {"oui", "1", "true"}:
            dossier = Path("data/debug")
            dossier.mkdir(parents=True, exist_ok=True)
            fichier = dossier / f"reponse-coupee-{time.strftime('%Y%m%d-%H%M%S')}.txt"
            fichier.write_text(texte, encoding="utf-8")
            self.args = (f"{message} (texte reçu : {fichier})",)


class ReponseLente(ReponseTronquee):
    """Pas de réponse dans le délai : presque toujours un modèle qui réfléchit ou écrit trop longtemps."""


def _poster(url: str, corps: dict, entetes: dict, timeout: int, tentatives: int = 7, relances_lentes: int = 0) -> dict:
    """POST JSON avec nouvelles tentatives sur les erreurs passagères : 429 (limite de débit) et
    5xx, en attendant de plus en plus longtemps (2, 4, 8… jusqu'à 60 s, un peu d'aléa pour que les
    appels parallèles ne repartent pas ensemble). Au plus `APPELS_SIMULTANES` appels à la fois ;
    l'attente entre deux tentatives ne bloque pas les autres appels.

    `relances_lentes` : une requête sans réponse dans le délai est relancée autant de fois (7.114). Pour une lecture,
    courte, un appel qui ne répond pas en 15 s est presque toujours bloqué chez le fournisseur ; relancé, il répond en
    2 ou 3 s. Pour un travail long (la rédaction), on ne relance pas : le modèle écrivait encore."""
    donnees = json.dumps(corps).encode("utf-8")
    attente = 2.0
    for essai in range(1, tentatives + 1):
        requete = urllib.request.Request(url, data=donnees, headers={"content-type": "application/json", **entetes})
        try:
            with APPELS_SIMULTANES, urllib.request.urlopen(requete, timeout=timeout) as reponse:
                return json.loads(reponse.read())
        except TimeoutError as e:
            if relances_lentes > 0:
                relances_lentes -= 1
                continue
            raise ReponseLente(f"pas de réponse après {timeout} s") from e
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            if e.code in (429, 500, 502, 503, 504) and essai < tentatives:
                delai = float((e.headers.get("retry-after") if e.headers else None) or attente)
                time.sleep(min(delai, 60) + random.random())
                attente = min(attente * 2, 60)
                continue
            if e.code in (401, 403):
                raise CleRefusee(f"Clé API refusée ({e.code}). Vérifier la clé dans le fichier .env.") from e
            raise ErreurLLM(f"Erreur {e.code} du fournisseur : {detail}", code=e.code) from e
        except urllib.error.URLError as e:
            if isinstance(e.reason, TimeoutError):
                if relances_lentes > 0:
                    relances_lentes -= 1
                    continue
                raise ReponseLente(f"pas de réponse après {timeout} s") from e
            if essai < tentatives:
                time.sleep(attente)
                attente *= 2
                continue
            raise ErreurLLM(f"Fournisseur injoignable : {e.reason}") from e
    raise ErreurLLM("Échec après plusieurs tentatives.")


def texte_du_message(contenu) -> str:
    """Le texte d'une réponse, quel que soit son format : une chaîne, ou une liste de morceaux
    (Mistral récent : [{"type": "text", "text": …}, {"type": "thinking", …}]). Les morceaux
    de réflexion du modèle sont ignorés : seule la réponse compte."""
    if contenu is None:
        return ""
    if isinstance(contenu, str):
        return contenu
    morceaux = []
    for m in contenu:
        if isinstance(m, str):
            morceaux.append(m)
        elif isinstance(m, dict) and m.get("type", "text") == "text":
            morceaux.append(str(m.get("text", "")))
    return "".join(morceaux)


def reflexion_du_message(contenu) -> str:
    """Le texte des morceaux de réflexion (« thinking »), pour le diagnostic seulement."""
    if not isinstance(contenu, list):
        return ""
    morceaux = []
    for m in contenu:
        if isinstance(m, dict) and m.get("type") == "thinking":
            t = m.get("thinking", "")
            morceaux.append(t if isinstance(t, str) else texte_du_message(t))
    return "".join(morceaux)


class OpenAICompatibleLLM:
    """Pour un modèle servi derrière une API compatible OpenAI (vLLM, Ollama, Azure…).
    `json_mode` demande au serveur de garantir une réponse JSON valide, s'il le permet."""

    def __init__(self, modele: str, url: str, cle_api: str = "", max_tokens: int = 8000, timeout: int = 120,
                 json_mode: bool = False, fournisseur: str = "openai-compatible", extra: dict | None = None,
                 relances_lentes: int = 0):
        """`extra` : paramètres propres à un fournisseur, ajoutés à chaque requête. `relances_lentes` : voir `_poster`."""
        self.relances_lentes = relances_lentes
        self.modele, self.url, self.cle_api = modele, url.rstrip("/"), cle_api
        self.max_tokens, self.timeout, self.json_mode = max_tokens, timeout, json_mode
        self.extra = extra or {}
        self.nom = f"{fournisseur}:{modele}"
        self.reflexion_refusee = False   # le modèle a refusé reasoning_effort
        self.derniere_reflexion = 0      # caractères de réflexion dans la dernière réponse (diagnostic)
        self.schema_refuse = False       # le serveur a refusé une sortie contrainte par un schéma

    # Une sortie contrainte par un schéma JSON (structured outputs) : les valeurs hors liste sont impossibles.
    accepte_schema = True

    def completer(self, systeme: str, message: str, schema: dict | None = None) -> str:
        corps = {
            "model": self.modele,
            "max_tokens": self.max_tokens,
            "temperature": 0,
            "messages": [{"role": "system", "content": systeme}, {"role": "user", "content": message}],
        }
        if self.json_mode:
            corps["response_format"] = {"type": "json_object"}
        # Schéma non strict : les variables restent facultatives (une forme stricte les exige toutes, et le
        # modèle remplit alors au lieu de laisser vide, DEMARCHE 7.40). Les valeurs hors liste sont de toute
        # façon retirées par le code.
        if schema is not None and self.json_mode and not self.schema_refuse:
            corps["response_format"] = {"type": "json_schema",
                                        "json_schema": {"name": "reponse", "schema": schema, "strict": False}}
        corps.update(self.extra)
        entetes = {"authorization": f"Bearer {self.cle_api}"} if self.cle_api else {}
        try:
            donnees = _poster(f"{self.url}/chat/completions", corps, entetes, self.timeout,
                              relances_lentes=self.relances_lentes)
        except ErreurLLM as e:
            # Serveur qui refuse le schéma : on revient au simple mode JSON, et on n'y revient plus.
            if corps.get("response_format", {}).get("type") == "json_schema" and e.code in (400, 422):
                self.schema_refuse = True
                return self.completer(systeme, message)
            # Modèle qui ne règle pas sa réflexion : on retire le paramètre et on n'y revient plus.
            if "reasoning_effort" not in corps or "reasoning" not in str(e).lower():
                raise
            self.extra.pop("reasoning_effort", None)
            corps.pop("reasoning_effort")
            self.reflexion_refusee = True
            donnees = _poster(f"{self.url}/chat/completions", corps, entetes, self.timeout,
                              relances_lentes=self.relances_lentes)
        choix = donnees["choices"][0]
        self.derniere_reflexion = len(reflexion_du_message(choix["message"].get("content")))
        if choix.get("finish_reason") == "length":
            contenu = choix["message"].get("content")
            reflexion = reflexion_du_message(contenu)
            jetons = (donnees.get("usage") or {}).get("completion_tokens", "?")
            raise ReponseTronquee(
                f"réponse coupée à {self.max_tokens} tokens",
                f"# {jetons} tokens produits, dont réflexion : {len(reflexion)} caractères\n\n"
                f"## Réflexion\n{reflexion}\n\n## Réponse\n{texte_du_message(contenu)}")
        return texte_du_message(choix["message"].get("content"))


class MistralLLM(OpenAICompatibleLLM):
    """API de Mistral (La Plateforme, console.mistral.ai). Compatible OpenAI, avec mode JSON.
    Modèles conseillés : mistral-large-latest (résultats), mistral-small-latest (moins cher)."""

    URL = "https://api.mistral.ai/v1"
    MODELE_DEFAUT = "mistral-large-latest"

    def __init__(self, modele: str | None = None, cle_api: str | None = None, reflexion: str | None = None, **kwargs):
        modele = modele or os.environ.get("COUVERTURE_MODELE") or self.MODELE_DEFAUT
        super().__init__(
            modele=modele,
            url=os.environ.get("MISTRAL_URL", self.URL),
            cle_api=cle_api or os.environ["MISTRAL_API_KEY"],
            json_mode=True,
            fournisseur="mistral",
            # Mistral refuse temperature=0 (décodage glouton) si top_p n'est pas exactement 1.
            extra={"top_p": 1, **_reflexion_mistral(modele, reflexion)},
            **kwargs,
        )


def _reflexion_mistral(modele: str = "", reflexion: str | None = None) -> dict:
    """Niveau de réflexion demandé à Mistral (`reasoning_effort`).
    Mistral Large 4 réfléchit au niveau « high » si on ne dit rien (des minutes par réponse) et
    n'accepte pas « none » : on demande « low ». Mistral Small accepte « none » : pour répondre
    oui / non à des questions courtes, c'est le plus rapide. COUVERTURE_REFLEXION impose un niveau
    (low, medium, high, none), « defaut » n'envoie rien. Un modèle qui refuse le paramètre est
    rappelé sans lui (voir `completer`)."""
    niveau = (reflexion if reflexion is not None else os.environ.get("COUVERTURE_REFLEXION", "")).strip().lower()
    if not niveau:
        niveau = "none" if "small" in modele else "low"
    return {} if niveau in {"defaut", "défaut"} else {"reasoning_effort": niveau}


def configurer(usage: str = "analyse") -> LLM | None:
    """Le modèle à utiliser, d'après l'environnement (ou le fichier .env), ou None sans clé :

    MISTRAL_API_KEY=...                 la clé
    COUVERTURE_MODELE=...               modèle des analyses (par défaut mistral-large-latest)
    COUVERTURE_MODELE_CONTRAT=...       modèle de la rédaction des règles (usage « contrat » ; par défaut le même)

    Deux usages, deux besoins : le travail sur un contrat se fait une fois et gagne à un modèle qui
    réfléchit (Mistral Large) ; l'analyse d'un sinistre se répète et gagne à un modèle rapide."""
    cle = os.environ.get("MISTRAL_API_KEY", "").strip()
    if not cle or cle.startswith("colle"):  # valeur d'exemple du .env laissée telle quelle
        return None
    modele_contrat = os.environ.get("COUVERTURE_MODELE_CONTRAT", "").strip() if usage == "contrat" else ""
    if modele_contrat:
        return MistralLLM(modele=modele_contrat, reflexion=os.environ.get("COUVERTURE_REFLEXION_CONTRAT", "low"))
    if usage == "contrat":
        return MistralLLM()
    # L'analyse : des lectures courtes ; un appel bloqué chez le fournisseur est relancé au bout de 15 s (7.114).
    return MistralLLM(timeout=15, relances_lentes=1)


# --- Réponses JSON ------------------------------------------------------------------------------------

def extraire_json(texte: str) -> dict:
    """L'objet JSON d'une réponse de modèle (avec ou sans bloc de code autour)."""
    texte = re.sub(r"^```(?:json)?|```$", "", texte.strip(), flags=re.MULTILINE).strip()
    debut, fin = texte.find("{"), texte.rfind("}")
    if debut == -1 or fin == -1:
        raise ValueError("Aucun objet JSON dans la réponse du modèle")
    return json.loads(texte[debut : fin + 1])


def appeler_json(llm: LLM, systeme: str, message: str, tentatives: int = 2) -> dict:
    """Un appel dont on attend un JSON ; une réponse coupée ou illisible est redemandée une fois."""
    erreur: Exception | None = None
    for _ in range(tentatives):
        try:
            return extraire_json(llm.completer(systeme, message))
        except ErreurLLM:
            raise
        except ReponseTronquee as e:
            erreur = e
            message += "\n\nTa réponse précédente était trop longue. Recommence plus court."
        except Exception as e:  # noqa: BLE001
            erreur = e
            message += "\n\nTa réponse précédente n'était pas un JSON valide. Réponds uniquement par l'objet JSON."
    raise ValueError(str(erreur))


def pour_travail_long(llm: LLM, max_tokens: int = 16000, timeout: int = 300) -> LLM:
    """Le travail sur un contrat (rédaction des règles) se fait une fois : on laisse au modèle le temps
    de réfléchir. Mistral Large a réfléchi jusqu'à 7 500 tokens sur une clause complexe."""
    copie = copy.copy(llm)
    if hasattr(copie, "max_tokens"):
        copie.max_tokens = max(getattr(copie, "max_tokens", 0), max_tokens)
    if hasattr(copie, "timeout"):
        copie.timeout = max(getattr(copie, "timeout", 0), timeout)
    if hasattr(copie, "extra"):
        copie.extra = dict(copie.extra)
    if hasattr(copie, "relances_lentes"):
        copie.relances_lentes = 0     # un travail long n'est pas bloqué : il écrit encore
    return copie


def completer_avec_schema(llm: LLM, systeme: str, message: str, schema: dict) -> str:
    """Avec un client qui sait contraindre sa sortie (Mistral), le schéma est envoyé ; sinon (modèles factices
    des tests), la consigne seule décrit la forme."""
    if getattr(llm, "accepte_schema", False):
        return llm.completer(systeme, message, schema=schema)
    return llm.completer(systeme, message)
