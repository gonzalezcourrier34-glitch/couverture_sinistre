"""Clé API des routes protégées.

**Provenance** : repris de SortirIA, `app/security.py` (lui-même repris de l'Assistant RAG OpenAgenda) ; la
variable s'appelle ici `COUVERTURE_API_KEY` (20/11/2026).

Le client envoie la clé dans l'en-tête HTTP :

    x-api-key: <votre_clé>
"""

from __future__ import annotations

import secrets

from fastapi import HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader

from couverture.api import config

api_key_header = APIKeyHeader(name="x-api-key", scheme_name="Clé API",
                              description="Clé personnelle requise pour appeler l'API", auto_error=False)


def require_api_key(request: Request, api_key: str | None = Security(api_key_header)) -> str:
    """Vérifie la clé API envoyée par le client.

    La comparaison utilise `secrets.compare_digest`, pour ne pas laisser deviner la clé au temps de réponse.

    Parameters
    ----------
    request : Request
        La requête ; en ligne, `acces.CodeAcces` y a noté que le code d'accès est bon.
    api_key : str | None
        Clé transmise dans l'en-tête `x-api-key`, injectée par FastAPI ; `None` si l'en-tête est absent.

    Returns
    -------
    str
        La clé validée.

    Raises
    ------
    HTTPException
        500 si la clé du serveur (`COUVERTURE_API_KEY`) n'est pas configurée ; 401 si la clé est absente ou
        invalide.
    """
    # En ligne, le code d'accès a déjà été vérifié pour cette requête (`acces.CodeAcces`) : il tient lieu de clé.
    if getattr(request.state, "acces", False):
        return "code d'accès"
    if not config.API_KEY:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="La clé API du serveur n'est pas configurée.")
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Clé API manquante.")
    if not secrets.compare_digest(api_key, config.API_KEY):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Clé API invalide.")
    return api_key
