"""GET /api/v1/contrats/{contrat_id}/clauses : le texte du contrat, découpé en clauses.

**Provenance** : nouveau (20/11/2026) ; reprend `GET /api/contrats/{id}/clauses` de l'ancienne interface. Sert
à afficher, à côté d'une décision, le texte complet des clauses citées.
"""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from couverture.api.dependances import get_base
from couverture.api.securite import require_api_key
from couverture.api.service import clause_publique
from couverture.base import Base

router = APIRouter(prefix="/api/v1", tags=["contrats"], dependencies=[Depends(require_api_key)])


@router.get("/contrats/{contrat_id}/clauses")
def clauses(
    contrat_id: str,
    type: Literal["garantie", "exclusion", "condition", "limite", "definition", "autre"] | None = Query(  # noqa: A002, B008
        default=None, description="Ne garder qu'un type de clause"),
    base: Base = Depends(get_base),  # noqa: B008
) -> list[dict[str, Any]]:
    """Les clauses du contrat, dans l'ordre du document : identifiant, titre, type, texte, pages.

    Raises
    ------
    HTTPException
        404 si le contrat est inconnu.
    """
    try:
        base.contrat(contrat_id)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e).strip("'\"")) from e
    return [clause_publique(c) for c in base.clauses(contrat_id) if type is None or c.type.value == type]
