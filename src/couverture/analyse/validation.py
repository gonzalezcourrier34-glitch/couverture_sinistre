"""Étape 5 — Contrôle du verdict. Aucune décision ne sort sans preuve vérifiable.

- Chaque citation doit viser une clause réellement fournie au juge et en reprendre le texte.
- COUVERT exige au moins une citation valide d'une garantie.
- Toute décision ferme exige au moins une citation valide.
- INCERTAIN doit dire quoi vérifier.
"""

from __future__ import annotations

import re

from ..models import ClauseRetenue, Decision, TypeClause, Verdict
from ..texte import normaliser


def _compact(texte: str) -> str:
    return re.sub(r"[^a-z0-9%€]+", " ", normaliser(texte)).strip()


def extrait_present(extrait: str, texte_clause: str) -> bool:
    """L'extrait figure dans la clause, à la ponctuation et aux accents près.
    Les coupures « … » ou « [...] » sont acceptées : chaque morceau doit être présent."""
    morceaux = [m for m in re.split(r"\.\.\.|…|\[\s*\.*\s*\]", extrait) if _compact(m)]
    cible = _compact(texte_clause)
    return bool(morceaux) and all(_compact(m) in cible for m in morceaux)


def passage_exact(extrait: str, texte_clause: str, ecart_max: int = 6, mots_min: int = 4) -> str | None:
    """Le passage **littéral** de la clause qu'un extrait cite avec des coupures non signalées.

    Le modèle écrit « l'accès a été endommagé » quand le contrat dit « l'accès (porte, fenêtre,
    chambranle, châssis) a été endommagé ». Ce n'est pas une invention, mais ce n'est pas une
    citation exacte. Si tous les mots de l'extrait figurent dans la clause, dans l'ordre, avec au
    plus `ecart_max` mots sautés à chaque fois, on renvoie le passage exact qui va du premier au
    dernier mot : la citation devient littérale. Sinon, None : l'extrait reste refusé."""
    cibles = _compact(extrait).split()
    if len(cibles) < mots_min:
        return None
    jetons = [(m, _compact(m.group())) for m in re.finditer(r"[\w%€]+", texte_clause)]
    jetons = [(m, t) for m, t in jetons if t]
    meilleur = None
    for depart, (_, t) in enumerate(jetons):
        if t != cibles[0]:
            continue
        i, fin, ok = depart, depart, True
        for cible in cibles[1:]:
            suivant = next((j for j in range(i + 1, min(i + 2 + ecart_max, len(jetons))) if jetons[j][1] == cible), None)
            if suivant is None:
                ok = False
                break
            i = fin = suivant
        if ok and (meilleur is None or fin - depart < meilleur[1] - meilleur[0]):
            meilleur = (depart, fin)
    if meilleur is None:
        return None
    return texte_clause[jetons[meilleur[0]][0].start():jetons[meilleur[1]][0].end()]


RETROGRADE = ("À préciser : la réponse « couvert » ne s'appuie sur aucune garantie citée de façon vérifiable ; "
              "à faire examiner par un gestionnaire. Ce que disent les règles : ")


def valider(verdict: Verdict, retenues: list[ClauseRetenue], relocaliser: bool = False,
            roles_des_regles: bool = False, refus_sans_citation: bool = False) -> Verdict:
    """`relocaliser` : si l'extrait n'est pas dans la clause annoncée, le chercher dans les autres.
    Utilisé pour la méthode « document brut », où le modèle ne connaît pas nos identifiants.
    `roles_des_regles` : le rôle d'une citation est celui que la règle lui donne (la phrase d'une garantie, d'une
    exclusion), pas le type de la clause entière. Pour la méthode « règles » (7.143) : la phrase citée est
    retrouvée mot pour mot, et une clause typée à l'ingestion « exclusion » ou « autre » peut contenir la phrase
    qui accorde la garantie. Sans cela (le modèle cite), le rôle vient du contrat, pas du modèle.
    `refus_sans_citation` : un refus qui n'a rien à citer est admis. Un seul cas (7.177) : le contrat est traduit en
    entier et aucune de ses garanties ne porte sur l'événement ; la preuve est l'absence, que l'arbre montre garantie
    par garantie. Partout ailleurs, une réponse ferme sans citation vérifiable redevient « à préciser »."""
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
        if not roles_des_regles:
            c.role = clause.type.value  # le rôle vient du contrat, pas du modèle
        c.pages = clause.pages

    valides = [c for c in v.citations if c.valide]

    if v.decision == Decision.COUVERT and not any(c.role == TypeClause.GARANTIE.value for c in valides):
        v.decision = Decision.INCERTAIN
        v.avertissements.append("COUVERT rétrogradé en INCERTAIN : aucune garantie citée de façon vérifiable.")
        # La justification ne doit pas dire « Couvert. » sous une réponse « à préciser » (7.143).
        v.justification = RETROGRADE + v.justification
        v.confiance = min(v.confiance, 0.4)
    if v.decision != Decision.INCERTAIN and not valides \
            and not (refus_sans_citation and v.decision == Decision.NON_COUVERT):
        v.decision = Decision.INCERTAIN
        v.avertissements.append("Décision rétrogradée en INCERTAIN : aucune citation vérifiable.")
    if v.decision == Decision.INCERTAIN and not (v.ambiguites or v.informations_manquantes):
        v.informations_manquantes.append("Faire examiner le dossier par un gestionnaire.")
    if any(not c.valide for c in v.citations):
        v.confiance = min(v.confiance, 0.5)
    return v
