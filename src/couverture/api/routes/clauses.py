"""GET /api/v1/contrats/{contrat_id}/clauses : le texte du contrat, découpé en clauses.
Pour une seule clause : `routes/clause.py`.

**Provenance** : nouveau (20/11/2026) ; reprend `GET /api/contrats/{id}/clauses` de l'ancienne interface. Sert
à afficher, à côté d'une décision, le texte complet des clauses citées.
"""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from couverture.api import config
from couverture.api.dependances import get_base
from couverture.api.securite import require_api_key
from couverture.api.service import clause_publique
from couverture.contrat.base import Base

router = APIRouter(prefix="/api/v1", tags=["contrats"], dependencies=[Depends(require_api_key)])


@router.get("/contrats/{contrat_id}/clauses")
def clauses(
    contrat_id: str,
    type: Literal["garantie", "exclusion", "condition", "limite", "definition", "autre"] | None = Query(
        default=None, description="Ne garder qu'un type de clause"),
    base: Base = Depends(get_base),  # noqa: B008
) -> list[dict[str, Any]]:
    """Les clauses du contrat, dans l'ordre du document : identifiant, titre, type, texte, pages.

    Raises
    ------
    HTTPException
        404 si le contrat est inconnu.
    """
    if config.CODE_ACCES:
        # En ligne, le contrat entier ne se télécharge pas : seulement, une à une, les clauses qu'une réponse cite.
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="En ligne, le texte du contrat ne se consulte que clause par clause, pour les "
                                   "clauses citées dans une réponse.")
    try:
        base.contrat(contrat_id)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e).strip("'\"")) from e
    return [clause_publique(c) for c in base.clauses(contrat_id) if type is None or c.type.value == type]
