"""Juge de la grille : une seconde lecture, indépendante, des conditions qui décident.

Le contrôle des citations (`validation.py`) vérifie qu'un passage **existe** dans le
contrat. Il ne vérifie pas qu'il **justifie** l'état donné à la condition : le modèle
peut citer la bonne exclusion et se tromper sur son application aux faits.

Le relecteur reçoit, pour chaque condition qui pèse sur la décision, le sinistre, le
texte complet de la clause et la question. Il ne voit ni la décision, ni la réponse de la
première analyse, ni sa justification : il répond lui-même (consigne v2), et **c'est le code
qui compare**. Une condition est contestée si les deux réponses diffèrent. En v1, le relecteur
voyait la réponse et donnait un avis « confirmée » ou « contestée » ; Mistral Small posait
parfois « contestée » sur un raisonnement d'accord, ce qui rendait la réponse incertaine à tort.

Ce qu'on relit, selon la décision :
  - NON_COUVERT par exclusion : les exclusions jugées applicables ;
  - NON_COUVERT faute de garantie : les conditions jugées non remplies ;
  - COUVERT : les conditions de la garantie retenue ET les exclusions jugées non applicables.
    C'est là que se cache l'erreur la plus coûteuse : une exclusion écartée à tort donne un
    « couvert » à tort ;
  - INCERTAIN : rien, la réponse admet déjà sa limite.

Une condition contestée redevient INCONNUE, avec la raison et la question à poser, et la
décision est recalculée par les mêmes règles. Une contestation ne peut donc que rendre la
réponse plus prudente, jamais l'inverse. Même principe que le juge de SortirIA
(`agent/nodes.py:judge_quality`) : un contrôle, pas une étape indispensable ; s'il est en
panne, la décision reste, avec un avertissement et une confiance plafonnée.
"""

from __future__ import annotations

import json

from .llm import LLM, ErreurLLM
from .models import ClauseRetenue, Condition, Decision, EtatCondition

SYSTEME_RELECTURE = """Tu es relecteur dans un service sinistres. On te donne la déclaration d'un sinistre et des questions numérotées, chacune avec le texte complet de la clause du contrat qui la fonde. Réponds toi-même à chaque question, avec rigueur, en lisant la clause et la déclaration.

- "etat" : "REMPLIE" si la déclaration et la clause établissent que la réponse est OUI, "NON_REMPLIE" si elles établissent que c'est NON, "INCONNUE" si la déclaration ne permet pas de le savoir. N'invente aucun fait.
- Pour une exclusion, "REMPLIE" signifie que l'exclusion s'applique.
- "raison" : une phrase.
- "question" : si INCONNUE, la question à poser à l'assuré.

Réponds uniquement par un objet JSON :
{"relectures": [{"id": 1, "etat": "REMPLIE", "raison": "…", "question": ""}]}"""


def borner(avant: Decision, apres: Decision) -> tuple[Decision, str]:
    """Garantie, par le code, que la relecture ne peut que rendre la réponse plus prudente.

    Recalculée après relecture, la décision peut changer de sens : une exclusion contestée
    redevient inconnue, et la charge de la preuve transforme une exclusion inconnue en
    « couvert, sous réserve ». Sans borne, la relecture ferait alors passer un refus à COUVERT
    (observé sur Foyer). Règle : après relecture, une décision ne peut devenir qu'INCERTAIN.
    Deux lectures qui mènent à deux décisions fermes différentes donnent INCERTAIN."""
    if apres == avant or apres == Decision.INCERTAIN:
        return apres, ""
    return Decision.INCERTAIN, (f"Les deux lectures divergent : la première analyse concluait {avant.value}, "
                                f"la relecture mène à {apres.value}. À examiner par un gestionnaire.")


def a_relire(decision: Decision, conditions: list[Condition]) -> list[Condition]:
    valides = [c for c in conditions if c.valide and c.nature != "limite"]
    if decision == Decision.NON_COUVERT:
        return [c for c in valides if c.decisive]
    if decision == Decision.COUVERT:
        garanties = [c for c in valides if c.decisive and c.nature == "garantie"]
        ecartees = [c for c in valides if c.nature == "exclusion" and c.etat == EtatCondition.NON_REMPLIE]
        return garanties + ecartees
    return []


def relire(sinistre: str, conditions: list[Condition], retenues: list[ClauseRetenue], relecteur: LLM) -> list[str]:
    """Relit les conditions données et marque celles qui sont confirmées ou contestées.
    Renvoie des avertissements. Une contestation remet la condition à INCONNUE."""
    if not conditions:
        return []
    textes = {r.clause.id: r.clause.texte for r in retenues}
    lignes = []
    for n, c in enumerate(conditions, start=1):
        # Le relecteur ne voit ni la réponse ni la justification de la première analyse : il répond
        # lui-même, et c'est le code qui compare. Une étiquette « contestée » posée sur un
        # raisonnement d'accord (observé avec Mistral Small) n'est donc plus possible.
        lignes.append({
            "id": n,
            "nature": c.nature,
            "question": c.enonce,
            "passage_cite": c.extrait,
            "clause": f"art. {c.clause_id} : {textes.get(c.clause_id, '')[:3000]}",
        })
    message = f"## Sinistre déclaré\n{sinistre}\n\n## Lignes à contrôler\n{json.dumps(lignes, ensure_ascii=False, indent=1)}"
    from .juges import extraire_json

    try:
        avis = {int(a.get("id", 0)): a for a in extraire_json(relecteur.completer(SYSTEME_RELECTURE, message)).get("relectures", [])}
    except ErreurLLM:
        raise
    except Exception as e:  # noqa: BLE001
        return [f"Relecture indisponible ({e}) : décision non relue."]

    avertissements = []
    for n, c in enumerate(conditions, start=1):
        a = avis.get(n)
        if a is None:
            c.relecture, c.relecture_raison = "contestee", "Le relecteur ne s'est pas prononcé."
        elif "etat" in a:
            # Seul un désaccord net compte : oui contre non. Un « inconnu » du relecteur, qui ne
            # voit pas la première réponse, est un doute : noté, il ne change pas la réponse.
            etat = str(a.get("etat", "")).upper().replace(" ", "_")
            fermes = {EtatCondition.REMPLIE.value, EtatCondition.NON_REMPLIE.value}
            if etat == c.etat.value:
                c.relecture = "confirmee"
            elif etat in fermes and c.etat.value in fermes:
                c.relecture = "contestee"
            else:
                c.relecture = "doute"
            c.relecture_raison = str(a.get("raison", "")) + (
                "" if c.relecture == "confirmee" else f" (relecture : {etat or 'sans réponse'} ; première analyse : {c.etat.value})")
            if c.relecture == "doute":
                avertissements.append(f"Relecture : doute sur « {c.enonce} » (art. {c.clause_id}). {c.relecture_raison}")
        else:  # ancien format : un avis sur la réponse du collègue
            c.relecture = "confirmee" if a.get("avis") == "confirmee" else "contestee"
            c.relecture_raison = str(a.get("raison", ""))
        if c.relecture == "contestee":
            c.etat_propose, c.etat = c.etat, EtatCondition.INCONNUE
            question = (a or {}).get("question") or c.question or c.enonce
            c.question = str(question)
            avertissements.append(f"Relecture : « {c.enonce} » (art. {c.clause_id}) contestée. {c.relecture_raison}")
    return avertissements
