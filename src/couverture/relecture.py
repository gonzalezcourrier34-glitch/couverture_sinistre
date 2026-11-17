"""Juge de la grille : une seconde lecture, indépendante, des conditions qui décident.

Le contrôle des citations (`validation.py`) vérifie qu'un passage **existe** dans le
contrat. Il ne vérifie pas qu'il **justifie** l'état donné à la condition : le modèle
peut citer la bonne exclusion et se tromper sur son application aux faits.

Le relecteur reçoit, pour chaque condition qui pèse sur la décision, le sinistre, le
texte complet de la clause, la question, l'état proposé et sa justification. Il ne voit
pas la décision finale. Pour chacune, il confirme ou conteste.

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

SYSTEME_RELECTURE = """Tu es relecteur dans un service sinistres. Un collègue a préparé une grille de vérification : pour chaque condition, il a dit si les faits du sinistre la remplissent. Tu dois contrôler son travail, ligne par ligne, avec rigueur et sans complaisance.

Pour chaque ligne, lis le texte complet de la clause et la description du sinistre, puis réponds :
- "confirmee" si le passage cité et les faits décrits établissent bien l'état proposé ;
- "contestee" si l'état n'est pas établi : le passage ne dit pas cela, il ne vise pas cette situation, une autre phrase de la clause change le sens, ou les faits décrits ne permettent pas de le savoir. Dans le doute, conteste.

Ne te fie pas à la justification du collègue : vérifie-la. N'invente aucun fait.

Réponds uniquement par un objet JSON :
{"relectures": [{"id": 1, "avis": "confirmee" | "contestee", "raison": "une phrase", "question": "si contestée, la question à poser à l'assuré"}]}"""


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
        lignes.append({
            "id": n,
            "nature": c.nature,
            "question": c.enonce,
            "etat_propose": c.etat.value,
            "justification_du_collegue": c.justification,
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
        else:
            c.relecture = "confirmee" if a.get("avis") == "confirmee" else "contestee"
            c.relecture_raison = str(a.get("raison", ""))
        if c.relecture == "contestee":
            c.etat_propose, c.etat = c.etat, EtatCondition.INCONNUE
            question = (a or {}).get("question") or c.question or c.enonce
            c.question = str(question)
            avertissements.append(f"Relecture : « {c.enonce} » (art. {c.clause_id}) contestée. {c.relecture_raison}")
    return avertissements
