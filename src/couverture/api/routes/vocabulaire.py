"""GET /api/v1/vocabulaire : les faits que le moteur comprend, avec leurs questions et leurs valeurs.

**Provenance** : nouveau (20/11/2026). Ce qu'un client doit connaître pour appeler `POST /api/v1/decisions`
sans passer par le modèle, ou pour afficher les questions de `a_preciser`.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query

from couverture.api.securite import require_api_key

router = APIRouter(prefix="/api/v1", tags=["vocabulaire"], dependencies=[Depends(require_api_key)])


@router.get("/vocabulaire")
def vocabulaire(evenement: str | None = Query(default=None, description="Ne garder que les variables de cet événement")
                ) -> dict[str, Any]:
    """Les variables : question, valeurs, sens des valeurs, événements auxquels elles s'appliquent.

    Avec `evenement`, seules les variables qui s'y appliquent (et celles qui s'appliquent à tout)."""
    from couverture.analyse.prolog import vocabulaire as voc

    garder = ("libelle", "question", "valeurs", "libelles", "aide", "pour", "plusieurs")
    return {v: {k: d[k] for k in garder if k in d} for v, d in voc().items()
            if d.get("pour") != ["jamais"] and (evenement is None or not d.get("pour") or evenement in d["pour"])}
