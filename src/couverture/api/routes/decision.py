"""POST /api/v1/decisions : des faits connus → la décision du moteur, sans modèle.

**Provenance** : nouveau (20/11/2026). Résout un « incertain » : les `faits` d'une analyse, plus les réponses du
client aux questions de `a_preciser`, renvoyés ici. Gratuit (aucun appel au modèle), déterministe, en
quelques millisecondes. Sert aussi aux systèmes qui ont déjà les faits (un formulaire de déclaration).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from couverture.api import service
from couverture.api.dependances import get_base
from couverture.api.schemas import Decision, DecisionRequest
from couverture.api.securite import require_api_key
from couverture.contrat.base import Base

router = APIRouter(prefix="/api/v1", tags=["décisions"], dependencies=[Depends(require_api_key)])


def get_decideur():
    """Le moteur Prolog (None : celui du contrat). Remplacé dans les tests par l'oracle Python."""
    return None


@router.post("/decisions", response_model=Decision)
def decider(demande: DecisionRequest, base: Base = Depends(get_base),  # noqa: B008
            decideur=Depends(get_decideur)) -> dict:  # noqa: B008
    """Décide sur des faits donnés.

    Les variables ou valeurs hors vocabulaire sont ignorées et signalées dans `avertissements`.

    Raises
    ------
    HTTPException
        404 contrat inconnu ; 409 contrat sans règles ; 422 aucun événement dans les faits ; 503 moteur
        indisponible.
    """
    if not demande.faits.get("evenement"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail="Les faits doivent dire l'événement (`evenement`).")
    try:
        _, reponse = service.decider(base, demande.contrat_id, dict(demande.faits), decideur)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e).strip("'\"")) from e
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001 - moteur Prolog absent ou en erreur
        if "SWI-Prolog" in str(e) or e.__class__.__name__ == "ErreurRegles":
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)) from e
        raise
    return reponse
