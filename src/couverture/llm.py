"""Clients de modèles de langage. Aucune dépendance : de simples appels HTTP.

N'importe quel modèle peut être branché tant qu'il respecte le protocole `LLM`.
Fournisseurs pris en charge :
  - Mistral (fournisseur européen, données hébergées dans l'UE) : `MistralLLM` ;
  - Anthropic : `AnthropicLLM` ;
  - toute API compatible OpenAI (vLLM, Ollama, Azure…) : `OpenAICompatibleLLM`.
Le choix se fait par variables d'environnement, voir `configurer()`.
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


def _poster(url: str, corps: dict, entetes: dict, timeout: int, tentatives: int = 7) -> dict:
    """POST JSON avec nouvelles tentatives sur les erreurs passagères : 429 (limite de débit) et
    5xx, en attendant de plus en plus longtemps (2, 4, 8… jusqu'à 60 s, un peu d'aléa pour que les
    appels parallèles ne repartent pas ensemble). Au plus `APPELS_SIMULTANES` appels à la fois ;
    l'attente entre deux tentatives ne bloque pas les autres appels."""
    donnees = json.dumps(corps).encode("utf-8")
    attente = 2.0
    for essai in range(1, tentatives + 1):
        requete = urllib.request.Request(url, data=donnees, headers={"content-type": "application/json", **entetes})
        try:
            with APPELS_SIMULTANES, urllib.request.urlopen(requete, timeout=timeout) as reponse:
                return json.loads(reponse.read())
        except TimeoutError as e:
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
                raise ReponseLente(f"pas de réponse après {timeout} s") from e
            if essai < tentatives:
                time.sleep(attente)
                attente *= 2
                continue
            raise ErreurLLM(f"Fournisseur injoignable : {e.reason}") from e
    raise ErreurLLM("Échec après plusieurs tentatives.")


class AnthropicLLM:
    URL = "https://api.anthropic.com/v1/messages"

    def __init__(self, modele: str | None = None, cle_api: str | None = None, max_tokens: int = 8000, timeout: int = 120):
        self.modele = modele or os.environ.get("COUVERTURE_MODELE") or "claude-sonnet-5-5"
        self.cle_api = cle_api or os.environ["ANTHROPIC_API_KEY"]
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.nom = f"anthropic:{self.modele}"

    def completer(self, systeme: str, message: str) -> str:
        corps = {
            "model": self.modele,
            "max_tokens": self.max_tokens,
            "temperature": 0,
            "system": systeme,
            "messages": [{"role": "user", "content": message}],
        }
        entetes = {"x-api-key": self.cle_api, "anthropic-version": "2023-06-01"}
        donnees = _poster(self.URL, corps, entetes, self.timeout)
        if donnees.get("stop_reason") == "max_tokens":
            raise ReponseTronquee(f"réponse coupée à {self.max_tokens} tokens")
        return "".join(bloc.get("text", "") for bloc in donnees.get("content", []))


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
                 json_mode: bool = False, fournisseur: str = "openai-compatible", extra: dict | None = None):
        """`extra` : paramètres propres à un fournisseur, ajoutés à chaque requête."""
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
            donnees = _poster(f"{self.url}/chat/completions", corps, entetes, self.timeout)
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
            donnees = _poster(f"{self.url}/chat/completions", corps, entetes, self.timeout)
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


FOURNISSEURS = ("mistral", "anthropic", "openai-compatible")


def configurer(usage: str = "analyse") -> LLM | None:
    """Le modèle à utiliser, d'après l'environnement (ou le fichier .env) :

    COUVERTURE_FOURNISSEUR=mistral|anthropic|openai-compatible   force le choix (facultatif)
    MISTRAL_API_KEY=...                                         → Mistral
    ANTHROPIC_API_KEY=...                                       → Anthropic
    COUVERTURE_LLM_URL=... (+ COUVERTURE_LLM_CLE)               → API compatible OpenAI
    COUVERTURE_MODELE=...                                       modèle des analyses (facultatif)
    COUVERTURE_MODELE_CONFIRMATION=...                          modèle qui confirme les faits portant une
                                                                réponse ferme (facultatif ; sinon celui de la lecture)
    COUVERTURE_MODELE_CONTRAT=...                               modèle du travail sur les contrats :
                                                                compilation, juge de qualité, réparation
                                                                (facultatif ; par défaut COUVERTURE_MODELE)

    Deux usages, deux besoins : le travail sur un contrat se fait une fois et gagne à un modèle qui
    réfléchit (Mistral Large) ; l'analyse d'un sinistre se répète et gagne à un modèle rapide.

    Sans fournisseur forcé, l'ordre est : Mistral, Anthropic, compatible OpenAI. Sinon None :
    la pipeline tourne alors avec le juge heuristique, sans modèle."""
    choix = os.environ.get("COUVERTURE_FOURNISSEUR", "").strip().lower()
    if choix and choix not in FOURNISSEURS:
        raise ErreurLLM(f"COUVERTURE_FOURNISSEUR inconnu : {choix} (attendu : {', '.join(FOURNISSEURS)})")

    def present(variable: str) -> bool:
        valeur = os.environ.get(variable, "").strip()
        return bool(valeur) and not valeur.startswith("colle")  # valeur d'exemple du .env laissée telle quelle

    if usage == "confirmation":
        # La confirmation des faits qui portent une réponse ferme (7.66) : quelques faits, une réponse courte ;
        # un modèle plus fort que celui de la lecture, s'il est demandé. Sinon None : le modèle de la lecture.
        modele = os.environ.get("COUVERTURE_MODELE_CONFIRMATION", "").strip()
        if not modele:
            return None
        if choix in ("", "mistral") and present("MISTRAL_API_KEY"):
            return MistralLLM(modele=modele)
        if choix in ("", "anthropic") and present("ANTHROPIC_API_KEY"):
            return AnthropicLLM(modele=modele)
        return None
    modele_contrat = os.environ.get("COUVERTURE_MODELE_CONTRAT", "").strip() if usage == "contrat" else ""
    if choix in ("", "mistral") and present("MISTRAL_API_KEY"):
        if modele_contrat:
            return MistralLLM(modele=modele_contrat, reflexion=os.environ.get("COUVERTURE_REFLEXION_CONTRAT", "low"))
        return MistralLLM()
    if choix in ("", "anthropic") and present("ANTHROPIC_API_KEY"):
        return AnthropicLLM(modele=modele_contrat or None)
    if choix in ("", "openai-compatible") and present("COUVERTURE_LLM_URL"):
        return OpenAICompatibleLLM(
            modele=modele_contrat or os.environ.get("COUVERTURE_MODELE", "default"),
            url=os.environ["COUVERTURE_LLM_URL"],
            cle_api=os.environ.get("COUVERTURE_LLM_CLE", ""),
        )
    if choix:
        raise ErreurLLM(f"Fournisseur « {choix} » demandé, mais sa clé ou son adresse n'est pas renseignée.")
    return None


# --- Embeddings (recherche par le sens) -----------------------------------------------


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
    return copie


def completer_avec_schema(llm: LLM, systeme: str, message: str, schema: dict) -> str:
    """Avec un client qui sait contraindre sa sortie (Mistral, API compatible OpenAI), le schéma est
    envoyé ; sinon (Anthropic, modèles factices des tests), la consigne seule décrit la forme."""
    if getattr(llm, "accepte_schema", False):
        return llm.completer(systeme, message, schema=schema)
    return llm.completer(systeme, message)
