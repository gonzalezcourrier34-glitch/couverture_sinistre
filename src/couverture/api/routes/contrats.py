"""GET /api/v1/contrats : les contrats de la base.

**Provenance** : nouveau (20/11/2026) ; reprend `GET /api/contrats` de l'ancienne interface (`web.py`).
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from couverture.api.dependances import get_base
from couverture.api.securite import require_api_key
from couverture.api.service import contrat_public
from couverture.contrat.base import Base

router = APIRouter(prefix="/api/v1", tags=["contrats"], dependencies=[Depends(require_api_key)])


@router.get("/contrats")
def contrats(base: Base = Depends(get_base)) -> list[dict[str, Any]]:  # noqa: B008
    """Les contrats lus : assureur (anonymisé), produit, version, statut du découpage, et `regles` (vrai si le
    moteur peut décider sur ce contrat)."""
    return [contrat_public(c) for c in base.contrats()]
