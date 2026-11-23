"""Mise en ligne : un code d'accès devant toute l'application, et une limite d'analyses par jour.

**Provenance** : nouveau (23/11/2026, DEMARCHE 7.161).

En local, l'écran passe par le proxy de développement, qui ajoute la clé de l'API : la clé n'entre jamais dans
le navigateur. En ligne il n'y a pas de proxy, et une page ouverte à tous dépenserait le crédit du modèle de
langage pour n'importe qui. Quand `COUVERTURE_CODE_ACCES` est défini :

- toute requête (l'écran, l'API, la documentation) demande ce code, par l'authentification HTTP « Basic » : le
  navigateur affiche sa propre fenêtre, une fois, et renvoie ensuite le code tout seul. Le nom d'utilisateur
  est libre, seul le mot de passe compte. `/health` reste ouvert, pour l'hébergeur ;
- une requête qui a donné le bon code n'a plus besoin de la clé `x-api-key` ;
- les analyses, qui appellent le modèle, sont comptées : au-delà de `COUVERTURE_LIMITE_JOUR` par jour, elles
  sont refusées (429). Le compte est en mémoire : il repart de zéro quand le service redémarre.

Sans `COUVERTURE_CODE_ACCES`, rien de tout cela ne s'applique : c'est le fonctionnement local, avec la clé.
"""

from __future__ import annotations

import base64
import binascii
import secrets
import threading
from datetime import datetime, timezone

from fastapi import HTTPException, status
from starlette.responses import PlainTextResponse

from couverture.api import config

LIBRES = {"/health"}


def code_valide(autorisation: str) -> bool:
    """`Authorization: Basic base64(nom:code)` porte-t-il le code d'accès ? Comparaison à temps constant."""
    schema, _, jeton = autorisation.partition(" ")
    if schema.lower() != "basic" or not jeton:
        return False
    try:
        _, _, code = base64.b64decode(jeton.strip(), validate=True).decode("utf-8").partition(":")
    except (binascii.Error, UnicodeDecodeError):
        return False
    return bool(config.CODE_ACCES) and secrets.compare_digest(code.encode(), config.CODE_ACCES.encode())


class CodeAcces:
    """Intergiciel ASGI : sans le code, 401 et l'invite du navigateur ; avec, la requête est marquée
    (`request.state.acces`) et passe. Écrit en ASGI pur pour laisser intacte la réponse en flux du suivi."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or not config.CODE_ACCES or scope["path"] in LIBRES:
            await self.app(scope, receive, send)
            return
        autorisation = dict(scope["headers"]).get(b"authorization", b"").decode("latin-1")
        if code_valide(autorisation):
            scope.setdefault("state", {})["acces"] = True
            await self.app(scope, receive, send)
            return
        refus = PlainTextResponse("Code d'accès requis.", status_code=status.HTTP_401_UNAUTHORIZED,
                                  headers={"WWW-Authenticate": 'Basic realm="Couverture des sinistres", charset="UTF-8"'})
        await refus(scope, receive, send)


_compte = {"jour": "", "n": 0}
_verrou = threading.Lock()


def limiter_analyses() -> None:
    """Dépendance des routes d'analyse : en ligne, pas plus de `COUVERTURE_LIMITE_JOUR` analyses par jour (UTC).

    Raises
    ------
    HTTPException
        429 quand la limite du jour est atteinte.
    """
    if not config.CODE_ACCES or config.LIMITE_JOUR <= 0:
        return
    jour = datetime.now(timezone.utc).date().isoformat()
    with _verrou:
        if _compte["jour"] != jour:
            _compte.update(jour=jour, n=0)
        if _compte["n"] >= config.LIMITE_JOUR:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                                detail=f"Limite de {config.LIMITE_JOUR} analyses par jour atteinte pour cette démonstration.")
        _compte["n"] += 1
