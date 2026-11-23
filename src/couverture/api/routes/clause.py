"""GET /api/v1/contrats/{contrat_id}/clauses/{clause_id} : une clause du contrat (23/11/2026, DEMARCHE 7.161).

**Provenance** : nouveau. L'écran s'en sert pour afficher l'article entier d'une clause citée, sans télécharger
le contrat. En ligne (`COUVERTURE_CODE_ACCES`), seules les clauses que les règles citent sont servies.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from couverture import prolog
from couverture.api import config
from couverture.api.dependances import get_base
from couverture.api.securite import require_api_key
from couverture.api.service import clause_publique
from couverture.base import Base

router = APIRouter(prefix="/api/v1", tags=["contrats"], dependencies=[Depends(require_api_key)])


@router.get("/contrats/{contrat_id}/clauses/{clause_id:path}")
def clause(contrat_id: str, clause_id: str, base: Base = Depends(get_base)) -> dict[str, Any]:  # noqa: B008
    """Une clause du contrat : celle qu'une réponse cite, pour en lire l'article entier.

    En ligne (`COUVERTURE_CODE_ACCES`), seules les clauses que les règles du contrat citent sont servies.

    Raises
    ------
    HTTPException
        404 si le contrat ou la clause est inconnu ; 403, en ligne, pour une clause qu'aucune règle ne cite.
    """
    try:
        base.contrat(contrat_id)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e).strip("'\"")) from e
    trouvee = next((c for c in base.clauses(contrat_id) if c.id == clause_id), None)
    if trouvee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Clause inconnue : {clause_id}")
    if config.CODE_ACCES and clause_id not in prolog.clauses_citees(contrat_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="En ligne, seules les clauses citées dans une réponse se consultent.")
    return clause_publique(trouvee)
