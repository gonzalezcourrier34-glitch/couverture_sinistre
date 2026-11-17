"""Juge par conditions : la décision est calculée, pas devinée.

Le modèle ne répond pas « couvert ou non ». Il fait ce que fait un gestionnaire :
  1. il liste les garanties qui pourraient viser le sinistre, et pour chacune ses conditions ;
  2. il liste les exclusions qui pourraient s'appliquer ;
  3. il confronte chaque condition aux faits décrits : REMPLIE, NON_REMPLIE ou INCONNUE,
     avec le passage du contrat qui la fonde.

Ensuite, du code ordinaire :
  - vérifie chaque citation (une condition sans preuve est écartée) ;
  - calcule la décision par des règles explicites ;
  - en déduit ce qu'il faut demander au client quand une condition décisive est inconnue.

« Je ne sais pas » n'est donc pas une hésitation du modèle : c'est une condition
dont l'état est inconnu, et on sait laquelle.
"""

from __future__ import annotations

from .juges import extraire_json, formater_clauses
from .llm import LLM, ErreurLLM, ReponseTronquee
from .models import (
    Citation,
    ClauseRetenue,
    Condition,
    Decision,
    EtatCondition,
    Faits,
    Verdict,
)
from .validation import extrait_present

SYSTEME_CONDITIONS = """Tu es gestionnaire sinistres. On te donne la description d'un sinistre et des clauses numérotées des conditions générales. Tu ne dois PAS dire si le sinistre est couvert : tu dois préparer la grille de vérification, condition par condition. La décision sera calculée à partir de ta grille.

1. "garanties" : chaque garantie du contrat qui pourrait viser cet événement et ce bien (il peut y en avoir plusieurs : vol dans le logement, vol dans une cave…). Pour chacune, ses conditions d'application, une condition = un seul fait vérifiable (lieu, fermeture à clé, effraction, flammes, option souscrite…). Inclus toujours la condition « l'événement est bien celui que vise la garantie ».
2. "exclusions" : chaque exclusion des clauses fournies qui pourrait concerner ce sinistre, même si tu penses qu'elle ne s'applique pas.
3. "limites" : franchises, plafonds, vétusté à signaler.

Règles de lecture :
- Lis le sinistre tel qu'il est écrit, sans y ajouter de cause. « Avec la chaleur » sans autre précision désigne la chaleur ambiante (été, soleil), pas celle d'un objet.
- Un fait ne s'applique qu'à l'objet ou au lieu exact que vise la clause. Exemple : une clause sur les portes du logement ne dit rien d'un local commun.
- Formule chaque condition de garantie pour que REMPLIE soit favorable à l'assuré (« Le vélo est-il un bien couvert ? » et non « Le vélo est-il un bien exclu ? »). Ce qui retire la garantie va dans "exclusions".
- Quand une condition repose sur un terme défini au lexique (incendie, vol, effraction…), cite la définition (clause 12/…), pas la clause qui emploie le mot.
- L'extrait doit contenir les mots qui fondent la condition, pas seulement une phrase d'introduction.
- Si une clause fournie permet de trancher (par exemple la définition d'un bien), tranche : INCONNUE est réservé à ce que la description du sinistre ne dit pas.

Pour chaque condition et chaque exclusion :
- "etat" : "REMPLIE" si la description du sinistre l'établit, "NON_REMPLIE" si la description établit le contraire, "INCONNUE" si la description ne permet pas de le savoir. N'invente aucun fait : dans le doute, INCONNUE.
- Pour une exclusion, "REMPLIE" signifie que l'exclusion s'applique.
- "extrait" : passage copié mot pour mot de la clause (30 mots au plus).
- "justification" : ce qui, dans la description, fonde l'état (ou « non précisé »).
- "question" : si INCONNUE, la question précise à poser à l'assuré.

Sois bref : la grille doit tenir en une page.
- Au plus 3 garanties, les plus pertinentes ; au plus 5 conditions par garantie.
- Au plus 5 exclusions : seulement celles qui visent ce type d'événement, de bien ou de lieu. Ignore les exclusions générales sans rapport (guerre, nucléaire, faute intentionnelle…) sauf si la description les évoque.
- Au plus 3 limites.
- "justification" : 15 mots au plus. "question" : vide sauf si INCONNUE.
- Ne cite jamais une clause de définition comme garantie ou exclusion.

Réponds uniquement par un objet JSON :
{
  "garanties": [
    {"nom": "Vol dans les caves", "conditions": [
      {"clause_id": "2.10", "extrait": "…", "enonce": "Le vol a-t-il eu lieu dans une cave ?", "etat": "REMPLIE", "justification": "…", "question": ""}
    ]}
  ],
  "exclusions": [
    {"clause_id": "2.10-a", "extrait": "…", "enonce": "Le vol a-t-il eu lieu dans les parties communes ?", "etat": "REMPLIE", "justification": "…", "question": ""}
  ],
  "limites": [{"clause_id": "2.10", "extrait": "…", "enonce": "Plafond de 1 000 € pour les caves"}],
  "resume": "2 ou 3 phrases pour l'assuré, sans conclure sur la couverture"
}"""


def lire_grille(donnees: dict) -> list[Condition]:
    conditions: list[Condition] = []
    for g in donnees.get("garanties", []):
        for c in g.get("conditions", []):
            conditions.append(Condition(nature="garantie", groupe=g.get("nom", ""), **_champs(c)))
    for c in donnees.get("exclusions", []):
        conditions.append(Condition(nature="exclusion", groupe="Exclusions", **_champs(c)))
    for c in donnees.get("limites", []):
        conditions.append(Condition(nature="limite", groupe="Limites", **{**_champs(c), "etat": EtatCondition.REMPLIE}))
    return conditions


def _champs(c: dict) -> dict:
    etat = str(c.get("etat", "INCONNUE")).upper().replace(" ", "_")
    return {
        "clause_id": str(c.get("clause_id", "")),
        "extrait": c.get("extrait", ""),
        "enonce": c.get("enonce", ""),
        "justification": c.get("justification", ""),
        "question": c.get("question", ""),
        **({"etat": EtatCondition(etat)} if etat in EtatCondition.__members__ else {}),
    }


def verifier_conditions(conditions: list[Condition], retenues: list[ClauseRetenue]) -> list[str]:
    """Écarte les conditions dont la citation ne tient pas. Renvoie les avertissements."""
    clauses = {r.clause.id: r.clause for r in retenues}
    avertissements = []
    for c in conditions:
        clause = clauses.get(c.clause_id)
        if clause is None:
            c.valide = False
            avertissements.append(f"Condition écartée : clause {c.clause_id} non fournie (« {c.enonce} »).")
        elif not extrait_present(c.extrait, clause.texte):
            c.valide = False
            avertissements.append(f"Condition écartée : extrait introuvable dans l'art. {c.clause_id} (« {c.enonce} »).")
        else:
            c.pages = clause.pages
    return avertissements


def decider(conditions: list[Condition]) -> tuple[Decision, str, list[str], float]:
    """Règles de décision, appliquées aux seules conditions prouvées.

    1. Une exclusion REMPLIE → NON_COUVERT.
    2. Une garantie dont toutes les conditions sont REMPLIES → COUVERT,
       sauf si une exclusion est INCONNUE → INCERTAIN (on dit laquelle).
    3. Sinon, une garantie sans condition NON_REMPLIE mais avec des INCONNUES → INCERTAIN.
    4. Sinon, toutes les garanties ont une condition NON_REMPLIE → NON_COUVERT.
    5. Aucune garantie prouvée → INCERTAIN (rien ne permet de conclure).
    """
    valides = [c for c in conditions if c.valide]
    exclusions = [c for c in valides if c.nature == "exclusion"]
    chemins: dict[str, list[Condition]] = {}
    for c in valides:
        if c.nature == "garantie":
            chemins.setdefault(c.groupe or c.clause_id, []).append(c)

    def marquer(cs: list[Condition]) -> list[Condition]:
        for c in cs:
            c.decisive = True
        return cs

    def questions(cs: list[Condition]) -> list[str]:
        return [c.question or c.enonce for c in cs]

    exclues = [c for c in exclusions if c.etat == EtatCondition.REMPLIE]
    if exclues:
        marquer(exclues)
        refs = ", ".join(dict.fromkeys(f"art. {c.clause_id}" for c in exclues))
        return Decision.NON_COUVERT, f"Non couvert : une exclusion du contrat s'applique ({refs}).", [], 0.9

    exclusions_inconnues = [c for c in exclusions if c.etat == EtatCondition.INCONNUE]
    satisfaits = {nom: cs for nom, cs in chemins.items() if all(c.etat == EtatCondition.REMPLIE for c in cs)}
    ouverts = {
        nom: cs for nom, cs in chemins.items()
        if nom not in satisfaits and not any(c.etat == EtatCondition.NON_REMPLIE for c in cs)
    }

    if satisfaits:
        nom, cs = next(iter(satisfaits.items()))
        marquer(cs)
        if exclusions_inconnues:
            marquer(exclusions_inconnues)
            return (Decision.INCERTAIN,
                    f"La garantie « {nom} » s'applique, mais une exclusion dépend d'un fait non précisé.",
                    questions(exclusions_inconnues), 0.6)
        return Decision.COUVERT, f"La garantie « {nom} » s'applique : toutes ses conditions sont remplies et aucune exclusion ne s'applique.", [], 0.85

    if ouverts:
        inconnues = [c for cs in ouverts.values() for c in cs if c.etat == EtatCondition.INCONNUE]
        marquer(inconnues)
        noms = ", ".join(f"« {n} »" for n in ouverts)
        return (Decision.INCERTAIN,
                f"La couverture dépend de faits non précisés pour la garantie {noms}.",
                questions(inconnues + exclusions_inconnues), 0.5)

    if chemins:
        manquees = [c for cs in chemins.values() for c in cs if c.etat == EtatCondition.NON_REMPLIE]
        marquer(manquees)
        refs = ", ".join(dict.fromkeys(f"art. {c.clause_id}" for c in manquees))
        return (Decision.NON_COUVERT,
                f"Non couvert : aucune garantie ne s'applique, une de leurs conditions n'est pas remplie ({refs}).",
                [], 0.75)

    return Decision.INCERTAIN, "Aucune garantie du contrat n'a pu être rattachée à ce sinistre de façon vérifiable.", ["Faire examiner le dossier par un gestionnaire."], 0.2


class JugeConditions:
    def __init__(self, llm: LLM, tentatives: int = 2, relecteur: LLM | None = None):
        """`relecteur` : le juge de la grille (voir `relecture.py`), qui relit les conditions
        décisives. Idéalement un autre appel, voire un autre modèle, que celui qui a rempli la grille."""
        self.llm = llm
        self.tentatives = tentatives
        self.relecteur = relecteur

    def juger(self, sinistre: str, faits: Faits, retenues: list[ClauseRetenue]) -> Verdict:
        message = f"## Sinistre déclaré\n{sinistre}\n\n## Clauses du contrat\n{formater_clauses(retenues)}"
        donnees, erreur = None, None
        for _ in range(self.tentatives):
            try:
                donnees = extraire_json(self.llm.completer(SYSTEME_CONDITIONS, message))
                conditions = lire_grille(donnees)
                break
            except ErreurLLM:
                raise  # clé refusée, fournisseur injoignable : ce n'est pas un problème de réponse
            except ReponseTronquee as e:
                erreur = e
                message += ("\n\nTa réponse précédente était trop longue et a été coupée. Recommence en plus court : "
                            "2 garanties et 3 exclusions au plus, justifications de 10 mots, uniquement l'objet JSON.")
            except Exception as e:
                erreur = e
                message += "\n\nTa réponse précédente n'était pas un JSON valide. Réponds uniquement par l'objet JSON."
        else:
            return Verdict(decision=Decision.INCERTAIN, justification="Le modèle n'a pas produit de grille exploitable.",
                           confiance=0.0, mode=f"conditions:{self.llm.nom}",
                           avertissements=[f"Réponse illisible : {erreur}"])

        avertissements = verifier_conditions(conditions, retenues)
        decision, motif, a_demander, confiance = decider(conditions)
        resume = (donnees.get("resume") or "").strip()
        avant_relecture = None

        if self.relecteur is not None:
            from .relecture import a_relire, relire

            notes = relire(sinistre, a_relire(decision, conditions), retenues, self.relecteur)
            avertissements += notes
            if any(c.relecture == "contestee" for c in conditions):
                for c in conditions:
                    c.decisive = False
                avant_relecture = decision
                decision, motif, a_demander, confiance = decider(conditions)
                from .relecture import borner

                decision, divergence = borner(avant_relecture, decision)
                if divergence:
                    motif, confiance = divergence, min(confiance, 0.4)
                if decision != avant_relecture:
                    motif += f" (La relecture a contesté la première analyse, qui concluait {avant_relecture.value}.)"
                    resume = ""  # le résumé du modèle portait sur la première analyse
                else:
                    avant_relecture = None
            elif any(n.startswith("Relecture indisponible") for n in notes):
                confiance = min(confiance, 0.6)

        citations = [
            Citation(clause_id=c.clause_id, extrait=c.extrait, role=c.nature, valide=c.valide, pages=c.pages)
            for c in sorted(conditions, key=lambda c: (not c.decisive, c.nature != "exclusion"))
            if c.valide and c.nature != "limite"
        ]
        return Verdict(
            decision=decision,
            justification=motif + (f" {resume}" if resume else ""),
            citations=citations,
            conditions=conditions,
            informations_manquantes=list(dict.fromkeys(a_demander)),
            # Une condition inventée (hors limites) entame la confiance dans tout le raisonnement.
            confiance=min(confiance, 0.5) if any(not c.valide and c.nature != "limite" for c in conditions) else confiance,
            mode=f"conditions:{self.llm.nom}" + (f"+relecture:{self.relecteur.nom}" if self.relecteur else ""),
            avertissements=avertissements,
            decision_avant_relecture=avant_relecture,
        )
