"""POST /api/v1/analyses : une déclaration de sinistre → couvert, non couvert ou incertain.

**Provenance** : nouveau (20/11/2026) ; reprend `POST /api/analyser` de l'ancienne interface, méthode
« règles » seule. Le modèle lit les faits, le moteur Prolog décide, le code vérifie les citations.

Route `def` (pas `async`) : l'appel au modèle et au moteur bloque ; FastAPI le fait tourner dans un fil à part.
"""

from __future__ import annotations

import time

from fastapi import APIRouter, Depends, HTTPException, status

from couverture.api import service
from couverture.api.acces import limiter_analyses
from couverture.api.dependances import Pipelines, get_journal, get_pipelines, methode, modele_des_clauses
from couverture.api.schemas import AnalyseRequest, Decision
from couverture.api.securite import require_api_key
from couverture.analyse.journal import Journal
from couverture.llm import ErreurLLM

router = APIRouter(prefix="/api/v1", tags=["décisions"], dependencies=[Depends(require_api_key)])


@router.post("/analyses", response_model=Decision, dependencies=[Depends(limiter_analyses)])
def analyser(demande: AnalyseRequest, pipelines: Pipelines = Depends(get_pipelines),  # noqa: B008
             journal: Journal = Depends(get_journal)) -> dict:  # noqa: B008
    """Analyse une déclaration sur un contrat.

    Raises
    ------
    HTTPException
        404 contrat inconnu ; 409 contrat sans règles ; 503 moteur ou modèle indisponible ; 502 le modèle n'a pas
        répondu.
    """
    try:
        chaine = pipelines.pour(demande.contrat_id)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e).strip("'\"")) from e
    except LookupError as e:
        code = status.HTTP_503_SERVICE_UNAVAILABLE if "SWI-Prolog" in str(e) else status.HTTP_409_CONFLICT
        raise HTTPException(status_code=code, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)) from e
    debut = time.perf_counter()
    try:
        if methode(demande) == "clauses":
            resultat, reponse = service.analyser_clauses(pipelines.base, chaine, demande.contrat_id,
                                                         demande.sinistre.strip(), modele_des_clauses(),
                                                         souscription=demande.souscription, chapitres=demande.chapitres)
        else:
            resultat, reponse = service.analyser(chaine, demande.sinistre.strip(), souscription=demande.souscription)
    except (ErreurLLM, ValueError) as e:   # ValueError : une réponse du modèle coupée ou illisible
        journal.noter_erreur(demande.contrat_id, methode(demande), str(e))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Le modèle n'a pas répondu : {e}") from e
    journal.noter(resultat, duree_ms=int((time.perf_counter() - debut) * 1000))
    return reponse
