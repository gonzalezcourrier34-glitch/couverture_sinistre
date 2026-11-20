"""API de couverture des sinistres (FastAPI).

**Provenance** : nouveau paquet écrit le 20/11/2026, sur le modèle de l'API de SortirIA (`app/main.py`,
`app/security.py`) : préfixe `/api/v1`, clé API dans l'en-tête `x-api-key`, une route par fichier
(`routes/`), la logique hors des routes (`service.py`). Lancement : `couverture api` ou
`uvicorn couverture.api.main:app`.
"""
