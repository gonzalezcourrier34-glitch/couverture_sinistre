"""Clients de modèles de langage. Aucune dépendance : de simples appels HTTP.

N'importe quel modèle peut être branché tant qu'il respecte le protocole `LLM`.
Fournisseurs pris en charge :
  - Mistral (fournisseur européen, données hébergées dans l'UE) : `MistralLLM` ;
  - Anthropic : `AnthropicLLM` ;
  - toute API compatible OpenAI (vLLM, Ollama, Azure…) : `OpenAICompatibleLLM`.
Le choix se fait par variables d'environnement, voir `configurer()`.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Protocol


class LLM(Protocol):
    nom: str

    def completer(self, systeme: str, message: str) -> str: ...


class ErreurLLM(RuntimeError):
    pass


def _poster(url: str, corps: dict, entetes: dict, timeout: int, tentatives: int = 4) -> dict:
    """POST JSON avec nouvelles tentatives sur les erreurs passagères :
    429 (limite de débit) et 5xx, en attendant de plus en plus longtemps."""
    donnees = json.dumps(corps).encode("utf-8")
    attente = 2.0
    for essai in range(1, tentatives + 1):
        requete = urllib.request.Request(url, data=donnees, headers={"content-type": "application/json", **entetes})
        try:
            with urllib.request.urlopen(requete, timeout=timeout) as reponse:
                return json.loads(reponse.read())
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            if e.code in (429, 500, 502, 503, 504) and essai < tentatives:
                delai = float(e.headers.get("retry-after") or attente)
                time.sleep(min(delai, 30))
                attente *= 2
                continue
            if e.code in (401, 403):
                raise ErreurLLM(f"Clé API refusée ({e.code}). Vérifier la clé dans le fichier .env.") from e
            raise ErreurLLM(f"Erreur {e.code} du fournisseur : {detail}") from e
        except urllib.error.URLError as e:
            if essai < tentatives:
                time.sleep(attente)
                attente *= 2
                continue
            raise ErreurLLM(f"Fournisseur injoignable : {e.reason}") from e
    raise ErreurLLM("Échec après plusieurs tentatives.")


class AnthropicLLM:
    URL = "https://api.anthropic.com/v1/messages"

    def __init__(self, modele: str | None = None, cle_api: str | None = None, max_tokens: int = 3000, timeout: int = 90):
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
        return "".join(bloc.get("text", "") for bloc in donnees.get("content", []))


class OpenAICompatibleLLM:
    """Pour un modèle servi derrière une API compatible OpenAI (vLLM, Ollama, Azure…).
    `json_mode` demande au serveur de garantir une réponse JSON valide, s'il le permet."""

    def __init__(self, modele: str, url: str, cle_api: str = "", max_tokens: int = 3000, timeout: int = 90,
                 json_mode: bool = False, fournisseur: str = "openai-compatible"):
        self.modele, self.url, self.cle_api = modele, url.rstrip("/"), cle_api
        self.max_tokens, self.timeout, self.json_mode = max_tokens, timeout, json_mode
        self.nom = f"{fournisseur}:{modele}"

    def completer(self, systeme: str, message: str) -> str:
        corps = {
            "model": self.modele,
            "max_tokens": self.max_tokens,
            "temperature": 0,
            "messages": [{"role": "system", "content": systeme}, {"role": "user", "content": message}],
        }
        if self.json_mode:
            corps["response_format"] = {"type": "json_object"}
        entetes = {"authorization": f"Bearer {self.cle_api}"} if self.cle_api else {}
        donnees = _poster(f"{self.url}/chat/completions", corps, entetes, self.timeout)
        return donnees["choices"][0]["message"]["content"]


class MistralLLM(OpenAICompatibleLLM):
    """API de Mistral (La Plateforme, console.mistral.ai). Compatible OpenAI, avec mode JSON.
    Modèles conseillés : mistral-large-latest (résultats), mistral-small-latest (moins cher)."""

    URL = "https://api.mistral.ai/v1"
    MODELE_DEFAUT = "mistral-large-latest"

    def __init__(self, modele: str | None = None, cle_api: str | None = None, **kwargs):
        super().__init__(
            modele=modele or os.environ.get("COUVERTURE_MODELE") or self.MODELE_DEFAUT,
            url=os.environ.get("MISTRAL_URL", self.URL),
            cle_api=cle_api or os.environ["MISTRAL_API_KEY"],
            json_mode=True,
            fournisseur="mistral",
            **kwargs,
        )


FOURNISSEURS = ("mistral", "anthropic", "openai-compatible")


def configurer() -> LLM | None:
    """Le modèle à utiliser, d'après l'environnement (ou le fichier .env) :

    COUVERTURE_FOURNISSEUR=mistral|anthropic|openai-compatible   force le choix (facultatif)
    MISTRAL_API_KEY=...                                         → Mistral
    ANTHROPIC_API_KEY=...                                       → Anthropic
    COUVERTURE_LLM_URL=... (+ COUVERTURE_LLM_CLE)               → API compatible OpenAI
    COUVERTURE_MODELE=...                                       nom du modèle (facultatif)

    Sans fournisseur forcé, l'ordre est : Mistral, Anthropic, compatible OpenAI. Sinon None :
    la pipeline tourne alors avec le juge heuristique, sans modèle."""
    choix = os.environ.get("COUVERTURE_FOURNISSEUR", "").strip().lower()
    if choix and choix not in FOURNISSEURS:
        raise ErreurLLM(f"COUVERTURE_FOURNISSEUR inconnu : {choix} (attendu : {', '.join(FOURNISSEURS)})")

    def present(variable: str) -> bool:
        valeur = os.environ.get(variable, "").strip()
        return bool(valeur) and not valeur.startswith("colle")  # valeur d'exemple du .env laissée telle quelle

    if choix in ("", "mistral") and present("MISTRAL_API_KEY"):
        return MistralLLM()
    if choix in ("", "anthropic") and present("ANTHROPIC_API_KEY"):
        return AnthropicLLM()
    if choix in ("", "openai-compatible") and present("COUVERTURE_LLM_URL"):
        return OpenAICompatibleLLM(
            modele=os.environ.get("COUVERTURE_MODELE", "default"),
            url=os.environ["COUVERTURE_LLM_URL"],
            cle_api=os.environ.get("COUVERTURE_LLM_CLE", ""),
        )
    if choix:
        raise ErreurLLM(f"Fournisseur « {choix} » demandé, mais sa clé ou son adresse n'est pas renseignée.")
    return None


# --- Embeddings (recherche par le sens) -----------------------------------------------


class Vectoriseur(Protocol):
    nom: str

    def vectoriser(self, textes: list[str]) -> list[list[float]]: ...


class MistralEmbeddings:
    """`mistral-embed` : un vecteur par texte, pour la recherche par le sens.
    Même principe que SortirIA (`agent/services.py:embed_with_mistral`)."""

    URL = "https://api.mistral.ai/v1"
    MODELE_DEFAUT = "mistral-embed"
    LOT = 32               # textes par appel
    LONGUEUR_MAX = 6000    # caractères gardés par texte (les clauses longues sont tronquées)

    def __init__(self, modele: str | None = None, cle_api: str | None = None, timeout: int = 90):
        self.modele = modele or os.environ.get("COUVERTURE_MODELE_EMBEDDINGS") or self.MODELE_DEFAUT
        self.cle_api = cle_api or os.environ["MISTRAL_API_KEY"]
        self.url = os.environ.get("MISTRAL_URL", self.URL).rstrip("/")
        self.timeout = timeout
        self.nom = f"mistral:{self.modele}"

    def vectoriser(self, textes: list[str]) -> list[list[float]]:
        vecteurs: list[list[float]] = []
        for debut in range(0, len(textes), self.LOT):
            lot = [t[: self.LONGUEUR_MAX] or " " for t in textes[debut : debut + self.LOT]]
            donnees = _poster(f"{self.url}/embeddings", {"model": self.modele, "input": lot},
                              {"authorization": f"Bearer {self.cle_api}"}, self.timeout)
            ordonnes = sorted(donnees["data"], key=lambda d: d.get("index", 0))
            vecteurs.extend(d["embedding"] for d in ordonnes)
        return vecteurs


def configurer_embeddings() -> Vectoriseur | None:
    """Le vectoriseur configuré, ou None (la recherche se fait alors par les mots seuls).
    Actif dès que MISTRAL_API_KEY est renseignée ; COUVERTURE_EMBEDDINGS=aucun le coupe."""
    if os.environ.get("COUVERTURE_EMBEDDINGS", "").strip().lower() in ("aucun", "non", "0"):
        return None
    cle = os.environ.get("MISTRAL_API_KEY", "").strip()
    if cle and not cle.startswith("colle"):
        return MistralEmbeddings()
    return None


def configurer_relecteur(principal: LLM | None) -> LLM | None:
    """Le juge de la grille. Par défaut, le même fournisseur que le modèle principal, avec le modèle
    `COUVERTURE_MODELE_RELECTURE` s'il est donné (un autre modèle rend la relecture plus indépendante).
    `COUVERTURE_RELECTURE=non` la désactive."""
    if principal is None or os.environ.get("COUVERTURE_RELECTURE", "").strip().lower() in ("non", "aucun", "0"):
        return None
    modele = os.environ.get("COUVERTURE_MODELE_RELECTURE", "").strip()
    if not modele:
        return principal
    if isinstance(principal, MistralLLM):
        return MistralLLM(modele=modele)
    if isinstance(principal, AnthropicLLM):
        return AnthropicLLM(modele=modele)
    if isinstance(principal, OpenAICompatibleLLM):
        return OpenAICompatibleLLM(modele=modele, url=principal.url, cle_api=principal.cle_api,
                                   json_mode=principal.json_mode)
    return principal
