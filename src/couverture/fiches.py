"""Analyse d'un sinistre avec le contrat compilé (méthode « fiches »).

À la question, le modèle n'a plus qu'un métier : lire la déclaration et répondre
oui / non / inconnu à des questions déjà écrites, déjà vérifiées contre le contrat.
Il ne choisit pas les garanties, ne formule pas les conditions, ne cite rien : les
citations viennent des fiches, donc elles existent toujours.

1. Routage : les fiches dont l'événement correspond aux faits repérés dans la déclaration.
   Si rien ne correspond, le modèle choisit parmi la liste des fiches (nom + objet).
2. Réponses : un appel pour toutes les questions des fiches retenues et des exclusions générales.
3. Décision : les règles de `conditions.decider`, appliquées fiche par fiche. Une exclusion du
   vol ne fait pas tomber la garantie incendie. Une fiche couverte suffit pour COUVERT.
4. Relecture des lignes décisives, comme dans la méthode « conditions ».
"""

from __future__ import annotations

import json

from .conditions import decider
from .faits import extraire_faits
from .juges import extraire_json
from .llm import LLM, ErreurLLM, ReponseTronquee
from .models import (
    Citation,
    Clause,
    ClauseRetenue,
    Condition,
    ContratCompile,
    Decision,
    EtatCondition,
    Faits,
    Fiche,
    Point,
    Resultat,
    Verdict,
)
from .validation import valider

SYSTEME_FICHES = """Tu es gestionnaire sinistres. On te donne la déclaration d'un sinistre et des questions numérotées, préparées à partir du contrat. Chaque question est accompagnée du passage du contrat qui la fonde. Réponds à chaque question en lisant la déclaration.

- "etat" : "REMPLIE" si la déclaration établit que la réponse est OUI, "NON_REMPLIE" si elle établit que c'est NON, "INCONNUE" si elle ne permet pas de le savoir. N'invente aucun fait : dans le doute, INCONNUE.
- Lis la déclaration telle qu'elle est écrite, sans y ajouter de cause. « Avec la chaleur » sans autre précision désigne la chaleur ambiante, pas celle d'un objet.
- Une question ne porte que sur l'objet ou le lieu exact qu'elle nomme.
- "justification" : ce qui, dans la déclaration, fonde la réponse ; 15 mots au plus.
- "question" : si INCONNUE, la question précise à poser à l'assuré ; sinon vide.
- "resume" : 2 phrases pour l'assuré, sans conclure sur la couverture.

Réponds uniquement par un objet JSON :
{"reponses": [{"id": "q1", "etat": "REMPLIE", "justification": "…", "question": ""}], "resume": "…"}"""

SYSTEME_ROUTAGE = """On te donne la déclaration d'un sinistre et la liste des garanties d'un contrat. Indique les garanties qui pourraient indemniser ce sinistre (au plus 3). Réponds uniquement par un objet JSON : {"fiches": ["id", "id"]}"""


def router(faits: Faits, compilation: ContratCompile) -> list[Fiche]:
    utilisables = [f for f in compilation.fiches if any(p.valide for p in f.conditions)]
    return [f for f in utilisables if set(f.evenements) & set(faits.evenements)]


def router_par_le_modele(sinistre: str, compilation: ContratCompile, llm: LLM) -> list[Fiche]:
    utilisables = {f.id: f for f in compilation.fiches if any(p.valide for p in f.conditions)}
    liste = "\n".join(f"- {f.id} : {f.nom} — {f.objet}" for f in utilisables.values())
    donnees = extraire_json(llm.completer(SYSTEME_ROUTAGE, f"## Sinistre\n{sinistre}\n\n## Garanties\n{liste}"))
    return [utilisables[i] for i in donnees.get("fiches", []) if i in utilisables][:3]


def _condition(p: Point, groupe: str, nature: str) -> Condition:
    return Condition(nature=nature, groupe=groupe, clause_id=p.clause_id, extrait=p.extrait, enonce=p.enonce,
                     pages=p.pages, valide=p.valide)


def decider_fiches(chemins: list[tuple[Fiche, list[Condition]]]) -> tuple[Decision, str, list[str], float]:
    """Les règles de `decider`, fiche par fiche (chaque fiche avec ses exclusions et les générales).
    COUVERT si une fiche l'est ; sinon INCERTAIN si une fiche l'est ; sinon NON_COUVERT.
    Les marques « décisif » sont celles de la fiche (ou des fiches) qui expliquent la décision."""
    issues = []
    for fiche, conditions in chemins:
        for c in conditions:
            c.decisive = False
        issues.append((fiche, conditions, decider(conditions)))

    for d in (Decision.COUVERT, Decision.INCERTAIN):
        retenues = [(f, cs, r) for f, cs, r in issues if r[0] == d]
        if retenues:
            for _, cs, _ in issues:
                for c in cs:
                    c.decisive = False
            for _, cs, _ in retenues:
                decider(cs)  # remet les marques des fiches qui expliquent la décision
            decision, motif, demander, confiance = retenues[0][2]
            if d == Decision.INCERTAIN and len(retenues) > 1:
                noms = ", ".join(f"« {f.nom} »" for f, _, _ in retenues)
                motif = f"La couverture dépend de faits non précisés pour les garanties {noms}."
                demander = list(dict.fromkeys(q for _, _, r in retenues for q in r[2]))
            return decision, motif, demander, confiance

    if not issues:
        return (Decision.INCERTAIN, "Aucune garantie du contrat ne vise ce type d'événement.",
                ["Faire examiner le dossier par un gestionnaire."], 0.2)
    for _, cs, _ in issues:
        decider(cs)  # chaque fiche garde ses marques : toutes expliquent le refus
    raisons = "; ".join(f"« {f.nom} » : {r[1].removeprefix('Non couvert : ')}" for f, _, r in issues)
    confiance = min(r[3] for _, _, r in issues)
    return Decision.NON_COUVERT, f"Non couvert. {raisons}", [], confiance


class JugeFiches:
    def __init__(self, llm: LLM, compilation: ContratCompile, clauses: list[Clause], tentatives: int = 2,
                 relecteur: LLM | None = None):
        self.llm, self.compilation, self.tentatives, self.relecteur = llm, compilation, tentatives, relecteur
        self.index = {c.id: c for c in clauses}

    def _questions(self, fiches: list[Fiche]) -> tuple[list[tuple[str, Point, Condition]], list[tuple[Fiche, list[Condition]]]]:
        """Numérote les questions ; une exclusion générale n'est posée qu'une fois, mais compte pour chaque fiche."""
        questions: list[tuple[str, Point, Condition]] = []
        generales = [(p, _condition(p, "Exclusions générales", "exclusion"))
                     for p in self.compilation.exclusions_generales if p.valide]
        chemins = []
        for f in fiches:
            propres = [(p, _condition(p, f.nom, "garantie")) for p in f.conditions if p.valide]
            propres += [(p, _condition(p, f"Exclusions — {f.nom}", "exclusion")) for p in f.exclusions if p.valide]
            questions += [(f"q{len(questions) + n}", p, c) for n, (p, c) in enumerate(propres, start=1)]
            chemins.append((f, [c for _, c in propres]))
        questions += [(f"q{len(questions) + n}", p, c) for n, (p, c) in enumerate(generales, start=1)]
        for i, (f, cs) in enumerate(chemins):
            chemins[i] = (f, cs + [c for _, c in generales])
        return questions, chemins

    def juger(self, sinistre: str, fiches: list[Fiche]) -> Verdict:
        questions, chemins = self._questions(fiches)
        mode = f"fiches:{self.llm.nom}" + (f"+relecture:{self.relecteur.nom}" if self.relecteur else "")
        if not fiches:
            decision, motif, demander, confiance = decider_fiches([])
            return Verdict(decision=decision, justification=motif, informations_manquantes=demander,
                           confiance=confiance, mode=mode)

        liste = [{"id": q, "nature": "condition de garantie" if c.nature == "garantie" else "exclusion",
                  "garantie": c.groupe, "question": p.enonce, "passage": f"art. {p.clause_id} : {p.extrait}"}
                 for q, p, c in questions]
        message = f"## Sinistre déclaré\n{sinistre}\n\n## Questions\n{json.dumps(liste, ensure_ascii=False, indent=1)}"
        donnees, erreur = None, None
        for _ in range(self.tentatives):
            try:
                donnees = extraire_json(self.llm.completer(SYSTEME_FICHES, message))
                break
            except ErreurLLM:
                raise
            except ReponseTronquee as e:
                erreur = e
                message += "\n\nTa réponse précédente était trop longue. Justifications de 8 mots au plus."
            except Exception as e:  # noqa: BLE001
                erreur = e
                message += "\n\nTa réponse précédente n'était pas un JSON valide. Réponds uniquement par l'objet JSON."
        if donnees is None:
            return Verdict(decision=Decision.INCERTAIN, justification="Le modèle n'a pas répondu aux questions.",
                           confiance=0.0, mode=mode, avertissements=[f"Réponse illisible : {erreur}"])

        reponses = {str(r.get("id")): r for r in donnees.get("reponses", []) if isinstance(r, dict)}
        avertissements = []
        for q, p, c in questions:
            r = reponses.get(q)
            if r is None:
                avertissements.append(f"Pas de réponse à « {p.enonce} » : laissée inconnue.")
                r = {}
            etat = str(r.get("etat", "INCONNUE")).upper().replace(" ", "_")
            c.etat = EtatCondition(etat) if etat in EtatCondition.__members__ else EtatCondition.INCONNUE
            c.justification, c.question = str(r.get("justification", "")), str(r.get("question", ""))
            if c.nature == "exclusion" and not p.a_demander and c.etat == EtatCondition.INCONNUE:
                c.etat = EtatCondition.NON_REMPLIE
                c.justification = "Présumée absente : la déclaration ne l'évoque pas."

        decision, motif, demander, confiance = decider_fiches(chemins)
        resume = (donnees.get("resume") or "").strip()
        toutes = [c for _, _, c in questions]
        avant = None
        if self.relecteur is not None:
            from .relecture import a_relire, relire

            retenues = [ClauseRetenue(clause=self.index[c.clause_id], score=0.0, raison="fiche")
                        for c in toutes if c.clause_id in self.index]
            cibles = a_relire(decision, toutes)
            if decision == Decision.COUVERT:  # les exclusions de la fiche retenue, pas celles des autres
                dans = {id(c) for _, cs in chemins if any(c.decisive and c.nature == "garantie" for c in cs) for c in cs}
                cibles = [c for c in cibles if id(c) in dans]
            # Une exclusion présumée absente n'est pas relue : « dans le doute, conteste » la rendrait inconnue.
            cibles = [c for c in cibles if not c.justification.startswith("Présumée absente")]
            notes = relire(sinistre, cibles, retenues, self.relecteur)
            avertissements += notes
            if any(c.relecture == "contestee" for c in toutes):
                avant = decision
                decision, motif, demander, confiance = decider_fiches(chemins)
                if decision != avant:
                    motif += f" (La relecture a contesté la première analyse, qui concluait {avant.value}.)"
                    resume = ""
                else:
                    avant = None
            elif any(n.startswith("Relecture indisponible") for n in notes):
                confiance = min(confiance, 0.6)

        limites = [_condition(p, "Limites", "limite") for f in fiches for p in f.limites if p.valide]
        for c in limites:
            c.etat = EtatCondition.REMPLIE
        citations = [Citation(clause_id=c.clause_id, extrait=c.extrait, role=c.nature, valide=True, pages=c.pages)
                     for c in sorted(toutes, key=lambda c: not c.decisive) if c.decisive]
        return Verdict(decision=decision, justification=motif + (f" {resume}" if resume else ""),
                       citations=citations, conditions=toutes + limites,
                       informations_manquantes=list(dict.fromkeys(demander)), confiance=confiance, mode=mode,
                       avertissements=avertissements, decision_avant_relecture=avant)


class PipelineFiches:
    methode = "fiches"

    def __init__(self, compilation: ContratCompile, clauses: list[Clause], llm: LLM, relecteur: LLM | None = None):
        self.compilation, self.clauses, self.llm = compilation, clauses, llm
        self.contrat_id = compilation.contrat_id
        self.juge = JugeFiches(llm, compilation, clauses, relecteur=relecteur)

    @classmethod
    def depuis_base(cls, base, contrat_id: str, llm: LLM, relecteur: LLM | None = None) -> "PipelineFiches":
        compilation = base.compilation(contrat_id)
        if compilation is None:
            raise LookupError(f"Le contrat {contrat_id} n'est pas compilé (ou a changé depuis) : "
                              f"lancer `couverture compiler --contrat {contrat_id}`.")
        return cls(compilation, base.clauses(contrat_id), llm, relecteur)

    def analyser(self, sinistre: str) -> Resultat:
        faits = extraire_faits(sinistre)
        fiches = router(faits, self.compilation)
        avertissement = None
        if not fiches:
            try:
                fiches = router_par_le_modele(sinistre, self.compilation, self.llm)
                avertissement = "Événement non reconnu dans la déclaration : garanties choisies par le modèle."
            except ErreurLLM:
                raise
            except Exception as e:  # noqa: BLE001
                avertissement = f"Routage impossible ({e})."
        verdict = self.juge.juger(sinistre, fiches)
        if avertissement:
            verdict.avertissements.insert(0, avertissement)
        index = {c.id: c for c in self.clauses}
        cites = dict.fromkeys(c.clause_id for c in verdict.conditions if c.clause_id in index)
        consultees = [ClauseRetenue(clause=index[i], score=0.0, raison="fiche compilée") for i in cites]
        verdict = valider(verdict, consultees)
        return Resultat(sinistre=sinistre, contrat_id=self.contrat_id, methode=self.methode, faits=faits,
                        clauses_consultees=consultees, verdict=verdict)
