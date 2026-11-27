"""POST /api/v1/analyses/suivi : la même analyse que `/analyses`, racontée pendant qu'elle se fait.

**Provenance** : nouveau (21/11/2026, DEMARCHE 7.134), sur le modèle du suivi en direct de SortirIA. La réponse est
un flux de lignes JSON (`application/x-ndjson`), une par événement :

- `{"etapes": [{"cle": ..., "titre": ...}]}` : en premier, avec la méthode `clauses` : la liste de ses étapes (7.201) ;
- `{"etape": "socle"}` : une étape commence (`socle`, `details`, `verification`, `decision`, `confirmation`) ;
- `{"etape": "socle", "detail": "evenement : vol ; bien : velo"}` : elle est finie, voici ce qu'elle a donné ;
- `{"etape": "fin", "reponse": {...}}` : la décision, la même que celle de `/analyses` ;
- `{"etape": "erreur", "code": 502, "detail": "..."}` : le modèle n'a pas répondu.

L'analyse tourne dans un fil ; ses étapes passent par une file, que le flux vide au fur et à mesure. Tant
qu'aucune étape n'arrive, une ligne vide part toutes les `BATTEMENT_S` secondes : la lecture des clauses peut
rester plus de deux minutes sur un seul appel au modèle, et l'hébergeur (Azure Container Apps) coupe une requête
restée muette quatre minutes (7.208). L'écran ignore les lignes vides.
"""

from __future__ import annotations

import json
import queue
import threading
import time
from collections.abc import Iterator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from couverture.api import lecture_clauses, service
from couverture.api.acces import limiter_analyses
from couverture.api.dependances import Pipelines, get_journal, get_pipelines, methode, modele_des_clauses
from couverture.api.schemas import AnalyseRequest, au_format
from couverture.api.securite import require_api_key
from couverture.analyse.journal import Journal
from couverture.llm import ErreurLLM

BATTEMENT_S = 15.0

router = APIRouter(prefix="/api/v1", tags=["décisions"], dependencies=[Depends(require_api_key)])


@router.post("/analyses/suivi", response_class=StreamingResponse, dependencies=[Depends(limiter_analyses)],
             responses={200: {"content": {"application/x-ndjson": {}}, "description": "Une ligne JSON par étape."}})
def analyser_avec_suivi(demande: AnalyseRequest, pipelines: Pipelines = Depends(get_pipelines),  # noqa: B008
                        journal: Journal = Depends(get_journal)) -> StreamingResponse:  # noqa: B008
    """Analyse une déclaration, en disant chaque étape dès qu'elle commence et dès qu'elle finit.

    Raises
    ------
    HTTPException
        404 contrat inconnu ; 409 contrat sans règles ; 503 moteur ou modèle indisponible. Une panne du modèle en
        cours d'analyse arrive dans le flux (`etape: erreur`), le flux étant déjà ouvert.
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

    file: queue.Queue = queue.Queue()
    sinistre = demande.sinistre.strip()

    def suivre(etape: str, detail: str | None = None) -> None:
        file.put({"etape": etape} if detail is None else {"etape": etape, "detail": detail})

    par_clauses = methode(demande) == "clauses"
    if par_clauses:
        file.put({"etapes": lecture_clauses.ETAPES_CLAUSES, "annonce": lecture_clauses.ANNONCE_CLAUSES})

    def travailler() -> None:
        debut = time.perf_counter()
        try:
            if par_clauses:
                resultat, reponse = lecture_clauses.analyser_clauses(pipelines.base, chaine, demande.contrat_id, sinistre,
                                                             modele_des_clauses(), suivi=suivre,
                                                             souscription=demande.souscription,
                                                             chapitres=demande.chapitres)
            else:
                resultat, reponse = service.analyser(chaine, sinistre, suivi=suivre, souscription=demande.souscription)
        except (ErreurLLM, ValueError) as e:   # ValueError : une réponse du modèle coupée ou illisible, comme /analyses
            journal.noter_erreur(demande.contrat_id, methode(demande), str(e))
            file.put({"etape": "erreur", "code": 502, "detail": f"Le modèle n'a pas répondu : {e}"})
            file.put(None)
            return
        except Exception as e:  # noqa: BLE001 - le flux est ouvert : l'erreur doit y arriver, pas se perdre
            file.put({"etape": "erreur", "code": 500, "detail": f"L'analyse a échoué : {e}"})
            file.put(None)
            return
        try:
            # À part : une réponse mal formée est une erreur du code, pas du modèle (la validation lève une
            # ValueError, que la clause d'au-dessus aurait comptée comme une panne du modèle).
            forme = au_format(reponse)
            journal.noter(resultat, duree_ms=int((time.perf_counter() - debut) * 1000))
            file.put({"etape": "fin", "reponse": forme})
        except Exception as e:  # noqa: BLE001 - le flux est ouvert : l'erreur doit y arriver, pas se perdre
            file.put({"etape": "erreur", "code": 500, "detail": f"L'analyse a échoué : {e}"})
        finally:
            file.put(None)

    def lignes() -> Iterator[str]:
        threading.Thread(target=travailler, daemon=True).start()
        while True:
            try:
                message = file.get(timeout=BATTEMENT_S)
            except queue.Empty:
                yield "\n"  # rien de neuf : un battement, pour que la connexion ne soit pas coupée
                continue
            if message is None:
                return
            yield json.dumps(message, ensure_ascii=False) + "\n"

    return StreamingResponse(lignes(), media_type="application/x-ndjson",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
