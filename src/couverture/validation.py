"""Étape 5 — Contrôle du verdict. Aucune décision ne sort sans preuve vérifiable.

- Chaque citation doit viser une clause réellement fournie au juge et en reprendre le texte.
- COUVERT exige au moins une citation valide d'une garantie.
- Toute décision ferme exige au moins une citation valide.
- INCERTAIN doit dire quoi vérifier.
"""

from __future__ import annotations

import re

from .models import ClauseRetenue, Decision, TypeClause, Verdict
from .texte import normaliser


def _compact(texte: str) -> str:
    return re.sub(r"[^a-z0-9%€]+", " ", normaliser(texte)).strip()


def extrait_present(extrait: str, texte_clause: str) -> bool:
    """L'extrait figure dans la clause, à la ponctuation et aux accents près.
    Les coupures « … » ou « [...] » sont acceptées : chaque morceau doit être présent."""
    morceaux = [m for m in re.split(r"\.\.\.|…|\[\s*\.*\s*\]", extrait) if _compact(m)]
    cible = _compact(texte_clause)
    return bool(morceaux) and all(_compact(m) in cible for m in morceaux)


def valider(verdict: Verdict, retenues: list[ClauseRetenue], relocaliser: bool = False) -> Verdict:
    """`relocaliser` : si l'extrait n'est pas dans la clause annoncée, le chercher dans les autres.
    Utilisé pour la méthode « document brut », où le modèle ne connaît pas nos identifiants."""
    v = verdict.model_copy(deep=True)
    v.decision_initiale = verdict.decision
    clauses = {r.clause.id: r.clause for r in retenues}

    for c in v.citations:
        clause = clauses.get(c.clause_id)
        if clause is not None and extrait_present(c.extrait, clause.texte):
            pass
        elif relocaliser and (trouvee := next((x for x in clauses.values() if extrait_present(c.extrait, x.texte)), None)):
            c.clause_id, clause = trouvee.id, trouvee
        elif clause is None:
            c.valide = False
            v.avertissements.append(f"Citation d'une clause non fournie au juge : {c.clause_id}")
            continue
        else:
            c.valide = False
            v.avertissements.append(f"Extrait introuvable dans l'art. {c.clause_id} : « {c.extrait[:60]} »")
            continue
        c.role = clause.type.value  # le rôle vient du contrat, pas du modèle
        c.pages = clause.pages

    valides = [c for c in v.citations if c.valide]

    if v.decision == Decision.COUVERT and not any(c.role == TypeClause.GARANTIE.value for c in valides):
        v.decision = Decision.INCERTAIN
        v.avertissements.append("COUVERT rétrogradé en INCERTAIN : aucune garantie citée de façon vérifiable.")
    if v.decision != Decision.INCERTAIN and not valides:
        v.decision = Decision.INCERTAIN
        v.avertissements.append("Décision rétrogradée en INCERTAIN : aucune citation vérifiable.")
    if v.decision == Decision.INCERTAIN and not (v.ambiguites or v.informations_manquantes):
        v.informations_manquantes.append("Faire examiner le dossier par un gestionnaire.")
    if any(not c.valide for c in v.citations):
        v.confiance = min(v.confiance, 0.5)
    return v
