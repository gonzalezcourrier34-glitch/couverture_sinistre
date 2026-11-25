"""POST /api/v1/fiches : la fiche d'analyse d'un sinistre, en PDF.

**Provenance** : nouveau (21/11/2026, DEMARCHE 7.130). Met en page une réponse de `/analyses` ou de `/decisions`,
renvoyée telle quelle avec la déclaration : rien n'est recalculé, le modèle n'est pas rappelé. La fiche porte ce
que l'écran montre : la décision, son motif, les faits, les questions ou les réserves, les clauses citées ; puis,
à la suite, le texte entier de chaque article cité, lu dans la base, les passages cités surlignés.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status

from couverture.analyse import prolog
from couverture.api import config
from couverture.api.dependances import get_base
from couverture.api.schemas import FicheRequest
from couverture.api.securite import require_api_key
from couverture.api.service import contrat_public
from couverture.contrat.base import Base
from couverture.analyse.fiche import fiche_pdf, nom_fichier

router = APIRouter(prefix="/api/v1", tags=["décisions"], dependencies=[Depends(require_api_key)])


@router.post("/fiches", response_class=Response,
             responses={200: {"content": {"application/pdf": {}}, "description": "La fiche, en PDF."}})
def fiche(demande: FicheRequest, base: Base = Depends(get_base)) -> Response:  # noqa: B008
    """Produit la fiche PDF d'une décision.

    Raises
    ------
    HTTPException
        404 si le contrat est inconnu.
    """
    try:
        contrat = contrat_public(base.contrat(demande.contrat_id))
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e).strip("'\"")) from e
    reponse = demande.reponse.model_dump(mode="json")
    cites = {c["clause_id"] for c in reponse["citations"]}
    if config.CODE_ACCES:
        # En ligne, la réponse vient du navigateur : elle ne fait joindre que des clauses que les règles citent,
        # pas n'importe quel article du contrat (7.161).
        cites &= prolog.clauses_citees(demande.contrat_id)
    clauses = {c.id: {"texte": c.texte, "chemin": c.chemin, "pages": c.pages}
               for c in base.clauses(demande.contrat_id) if c.id in cites}
    pdf = fiche_pdf(demande.sinistre.strip(), reponse, contrat, clauses=clauses)
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{nom_fichier(reponse)}"'})
