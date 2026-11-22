"""API de couverture des sinistres (FastAPI).

**Provenance** : nouveau module (20/11/2026), sur le modèle de `app/main.py` de SortirIA : une application
FastAPI, une route par fichier (`routes/`), `/health` pour Docker, `/` vers la documentation interactive.

Routes (préfixe `/api/v1`, clé API dans `x-api-key` sauf `sante`) :

- `GET  /sante`                           l'API, le moteur et le modèle répondent ;
- `GET  /contrats`                        les contrats, et ceux sur lesquels le moteur décide ;
- `GET  /contrats/{contrat_id}`           un contrat ;
- `GET  /contrats/{contrat_id}/clauses`   son texte, découpé en clauses ;
- `GET  /vocabulaire`                     les faits que le moteur comprend ;
- `POST /analyses`                        une déclaration → décision (le modèle lit, le moteur décide) ;
- `POST /analyses/suivi`                  la même analyse, racontée étape par étape pendant qu'elle se fait ;
- `POST /decisions`                       des faits → décision (le moteur seul, sans modèle) ;
- `POST /fiches`                          une décision → sa fiche en PDF.

Lancement : `couverture api` (port 8001), ou `uvicorn couverture.api.main:app`.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from couverture.api import config
from couverture.api.routes import (analyse, analyse_suivie, clauses, contrat, contrats, decision, fiche, sante,
                                   vocabulaire)

app = FastAPI(
    title="Couverture des sinistres",
    description=(
        "Dit si un sinistre est couvert par les conditions générales d'un contrat d'assurance habitation, en citant "
        "les clauses. Le modèle lit la déclaration, la logique décide, le code vérifie. Une réponse « incertain » "
        "dit ce qu'il faut demander au client ; ses réponses, ajoutées aux faits, se soumettent à `/decisions`."
    ),
    version=config.VERSION,
)
for module in (sante, contrats, contrat, clauses, vocabulaire, analyse, analyse_suivie, decision, fiche):
    app.include_router(module.router)


@app.get("/", include_in_schema=False)
def racine() -> RedirectResponse:
    """Redirige vers la documentation interactive (`/docs`)."""
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["supervision"])
def health() -> dict[str, str]:
    """L'API répond (contrôle de Docker) : toujours `{"status": "ok"}`."""
    return {"status": "ok"}
