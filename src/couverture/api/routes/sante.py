"""GET /api/v1/sante : l'API, la base, le moteur et le modèle répondent-ils ?

**Provenance** : sur le modèle de `GET /api/v1/sante` de SortirIA (20/11/2026). Publique : c'est le contrôle
de Docker et de la supervision.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from couverture.api import config
from couverture.api.dependances import get_base
from couverture.api.service import a_des_regles
from couverture.contrat.base import Base

router = APIRouter(prefix="/api/v1", tags=["supervision"])


@router.get("/sante")
def sante(base: Base = Depends(get_base)) -> dict[str, Any]:  # noqa: B008
    """État du service : version, contrats décidables, moteur Prolog, modèle configuré, clé API configurée ; la
    méthode par défaut et, pour la lecture des clauses, son modèle (l'écran les affiche en tête, 7.209).

    Returns
    -------
    dict[str, Any]
        `statut` vaut `ok` si au moins un contrat a des règles et que SWI-Prolog est installé, `degrade` sinon.
    """
    from couverture.llm import configurer
    from couverture.analyse.prolog import swipl

    decidables = [c.id for c in base.contrats() if a_des_regles(c.id)]
    llm = configurer()
    prolog_ok = swipl() is not None
    return {"statut": "ok" if decidables and prolog_ok else "degrade", "version": config.VERSION,
            "contrats_decidables": decidables, "prolog": prolog_ok, "modele": llm.nom if llm else None,
            "cle_api_configuree": bool(config.API_KEY), "methode": config.METHODE,
            "modele_clauses": config.MODELE_CLAUSES if config.METHODE == "clauses" else None}
