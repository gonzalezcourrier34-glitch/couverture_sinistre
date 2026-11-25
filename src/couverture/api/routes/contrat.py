"""GET /api/v1/contrats/{contrat_id} : un contrat.

**Provenance** : nouveau (20/11/2026).
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from couverture.api.dependances import get_base
from couverture.api.securite import require_api_key
from couverture.api.service import contrat_public
from couverture.contrat.base import Base

router = APIRouter(prefix="/api/v1", tags=["contrats"], dependencies=[Depends(require_api_key)])


@router.get("/contrats/{contrat_id}")
def contrat(contrat_id: str, base: Base = Depends(get_base)) -> dict[str, Any]:  # noqa: B008
    """Un contrat, comme dans la liste.

    Raises
    ------
    HTTPException
        404 si le contrat est inconnu.
    """
    try:
        return contrat_public(base.contrat(contrat_id))
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e).strip("'\"")) from e
