"""Interface web : une API JSON et une page HTML, sans framework de front.

  GET  /                          la page
  GET  /api/contrats              contrats disponibles et leur statut d'ingestion
  GET  /api/contrats/{id}/clauses toutes les clauses d'un contrat (pour afficher le texte complet)
  POST /api/analyser              {"contrat_id", "sinistre", "methode"} → résultat complet
"""

from __future__ import annotations

import time
from pathlib import Path

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route

from .base import Base
from .llm import ErreurLLM
from .pipeline import Pipeline, PipelineDocumentBrut, llm_configure

PAGE = Path(__file__).with_name("static") / "index.html"


def creer_app(base: Base) -> Starlette:
    from .journal import Journal

    cache: dict[tuple[str, str], object] = {}
    journal = Journal(base.chemin)

    def pipeline(contrat_id: str, methode: str):
        cle = (contrat_id, methode)
        if cle not in cache:
            if methode == "brut":
                llm = llm_configure()
                if llm is None:
                    raise ValueError("La méthode « document brut » demande un modèle configuré.")
                cache[cle] = PipelineDocumentBrut.depuis_base(base, contrat_id, llm)
            else:
                cache[cle] = Pipeline.depuis_base(base, contrat_id, methode=methode)
        return cache[cle]

    async def accueil(_: Request):
        return HTMLResponse(PAGE.read_text(encoding="utf-8"))

    async def contrats(_: Request):
        return JSONResponse({
            "modele": (llm.nom if (llm := llm_configure()) else None),
            "contrats": [
                {"id": c.id, "assureur": c.assureur, "produit": c.produit, "version": c.version,
                 "statut": c.statut, "nb_clauses": c.rapport.get("nb_clauses"), "alertes": c.rapport.get("alertes", [])}
                for c in base.contrats()
            ],
        })

    async def clauses(request: Request):
        try:
            cl = base.clauses(request.path_params["contrat_id"])
        except KeyError as e:
            return JSONResponse({"erreur": str(e)}, status_code=404)
        return JSONResponse([c.model_dump(mode="json") for c in cl])

    async def analyser(request: Request):
        corps = await request.json()
        sinistre = (corps.get("sinistre") or "").strip()
        if len(sinistre) < 10:
            return JSONResponse({"erreur": "Décrivez le sinistre en une phrase au moins."}, status_code=400)
        if len(sinistre) > 2000:
            return JSONResponse({"erreur": "Description trop longue (2 000 caractères au plus)."}, status_code=400)
        try:
            methode = corps.get("methode", "conditions")
            if methode not in ("conditions", "direct", "brut"):
                return JSONResponse({"erreur": f"Méthode inconnue : {methode}"}, status_code=400)
            p = pipeline(corps.get("contrat_id", ""), methode)
        except (KeyError, ValueError) as e:
            return JSONResponse({"erreur": str(e)}, status_code=400)
        debut = time.perf_counter()
        try:
            resultat = p.analyser(sinistre)
        except ErreurLLM as e:
            journal.noter_erreur(corps.get("contrat_id", ""), methode, str(e))
            return JSONResponse({"erreur": f"Le modèle n'a pas répondu : {e}"}, status_code=502)
        journal.noter(resultat, duree_ms=int((time.perf_counter() - debut) * 1000))
        return JSONResponse(resultat.model_dump(mode="json"))

    return Starlette(routes=[
        Route("/", accueil),
        Route("/api/contrats", contrats),
        Route("/api/contrats/{contrat_id}/clauses", clauses),
        Route("/api/analyser", analyser, methods=["POST"]),
    ])


def lancer(base: Base, hote: str = "127.0.0.1", port: int = 8000) -> None:
    from .llm import configurer

    llm = configurer()
    print(f"Juge : {llm.nom if llm else 'heuristique (aucun modèle configuré)'}")
    import uvicorn

    uvicorn.run(creer_app(base), host=hote, port=port)
