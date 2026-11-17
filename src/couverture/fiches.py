"""Analyse d'un sinistre avec le contrat compilé (méthode « fiches »).

À la question, le modèle n'a plus qu'un métier : lire la déclaration et répondre
oui / non / inconnu à des questions déjà écrites, déjà vérifiées contre le contrat.
Il ne choisit pas les garanties, ne formule pas les conditions, ne cite rien : les
citations viennent des fiches, donc elles existent toujours.

1. Faits : un petit appel dit de quel événement il s'agit, quel bien, où (le lexique écrit à
   la main de `faits.py` ne sert plus qu'en secours).
2. Routage : les fiches de cet événement. Si rien ne correspond, le modèle choisit dans la liste.
3. Réponses : un appel pour toutes les questions des fiches retenues et des exclusions générales.
4. Décision : par rôles, fiche par fiche (`decider_fiche`), puis pour l'ensemble (`decider_fiches`).
5. Relecture des lignes décisives, comme dans la méthode « conditions ».

Les rôles viennent du droit des assurances, et le contrat Foyer les distingue lui-même
(art. 2.10 : « Obligation de prévention… nous refuserons notre intervention s'il existe un
lien causal direct… En cas d'effraction, le non-respect de ces obligations est sans incidence ») :
  - périmètre (événement, bien, lieu) : ce qui rattache une garantie au sinistre ;
  - circonstances (effraction, violences…) : les autres conditions pour qu'elle joue ;
  - obligations de prévention : leur non-respect ouvre une déchéance, à examiner ;
  - exclusions : elles retirent une garantie qui s'applique ;
  - limites : plafonds et franchises, signalés.
"""

from __future__ import annotations

import json
import re

from .compilation import EVENEMENTS
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

PERIMETRE = ("evenement", "bien", "lieu")
OUI, NON, INCONNUE = EtatCondition.REMPLIE, EtatCondition.NON_REMPLIE, EtatCondition.INCONNUE

SYSTEME_FAITS = """Lis la déclaration d'un sinistre et dis ce qu'elle décrit, sans rien ajouter.
- "evenements" : parmi {evenements} (un ou deux au plus ; "autre" si aucun ne convient).
- "bien" : le ou les biens endommagés ou volés, tels que décrits.
- "lieu" : où se trouvait le bien, tel que décrit, ou "" si la déclaration ne le dit pas.
Réponds uniquement par un objet JSON : {{"evenements": ["vol"], "bien": "vélo", "lieu": "local commun de l'immeuble"}}""".format(
    evenements=", ".join(EVENEMENTS))

SYSTEME_FICHES = """Tu es gestionnaire sinistres. On te donne la déclaration d'un sinistre et des questions numérotées, préparées à partir du contrat. Chaque question a un rôle et le passage du contrat qui la fonde. Réponds à chaque question en lisant la déclaration.

- "etat" : "REMPLIE" si la déclaration établit que la réponse est OUI, "NON_REMPLIE" si elle établit que c'est NON, "INCONNUE" sinon.
- Rôles "evenement", "bien", "lieu" : la déclaration décrit presque toujours ce qui s'est passé, quel bien et où. Si elle décrit un autre événement, un autre bien ou un autre lieu que celui de la question, réponds NON_REMPLIE (un vol dans un local commun n'est pas un vol « sur la personne »).
- Rôles "circonstance", "obligation", "exclusion" : une déclaration n'en parle souvent pas. Si elle n'en dit rien, réponds INCONNUE. N'invente aucun fait.
- Une question qui énumère des possibilités (« bâtiment ou contenu », « incendie, explosion ou foudre ») est REMPLIE si l'une d'elles l'est. S'il y a plusieurs biens endommagés, une question sur le bien est REMPLIE si au moins l'un d'eux est concerné.
- Une pièce ou une partie du logement (salon, cuisine, chambre, terrasse, « chez moi », « mon appartement ») désigne le bâtiment assuré, à l'adresse du contrat, sauf si la déclaration dit autre chose.
- Exclusion : si elle ne vise qu'une partie des dommages déclarés (le tuyau à l'origine, alors que le parquet et le canapé sont aussi abîmés), réponds "PARTIELLE" et dis dans la justification ce qu'elle exclut.
- Lis la déclaration telle qu'elle est écrite, sans y ajouter de cause. « Avec la chaleur » sans autre précision désigne la chaleur ambiante, pas celle d'un objet.
- "justification" : ce qui, dans la déclaration, fonde la réponse ; 15 mots au plus.
- "question" : si INCONNUE, la question précise à poser à l'assuré ; sinon vide.
- "resume" : 2 phrases pour l'assuré, sans conclure sur la couverture.

Réponds uniquement par un objet JSON :
{"reponses": [{"id": "q1", "etat": "REMPLIE", "justification": "…", "question": ""}], "resume": "…"}"""

SYSTEME_ROUTAGE = """On te donne la déclaration d'un sinistre et la liste des garanties d'un contrat. Indique les garanties qui pourraient indemniser ce sinistre (au plus 3). Réponds uniquement par un objet JSON : {"fiches": ["id", "id"]}"""


def section(identifiant: str) -> str:
    """« 2.10#1 » → « 2 », « 5.10 » → « 5 », « 4~2 » → « 4 » : la partie du contrat."""
    return re.split(r"[.#~/]", identifiant)[0]


def utilisable(f: Fiche) -> bool:
    return any(p.valide and p.role == "evenement" for p in f.conditions)


def extraire_faits_modele(sinistre: str, llm: LLM) -> Faits:
    """Les faits par le modèle ; le lexique de `faits.py` en secours s'il ne répond pas."""
    secours = extraire_faits(sinistre)
    try:
        d = extraire_json(llm.completer(SYSTEME_FAITS, f"## Déclaration\n{sinistre}"))
    except ErreurLLM:
        raise
    except Exception:  # noqa: BLE001
        return secours
    # On garde aussi les événements du lexique : « bougie » → incendie n'est pas toujours vu par le
    # modèle, qui peut classer une table abîmée en « dommage accidentel ». Une fiche de trop est
    # écartée par son périmètre ; une fiche manquante, rien ne la rattrape.
    evts = list(dict.fromkeys([e for e in d.get("evenements", []) if e in EVENEMENTS] + secours.evenements))
    if not evts:
        return secours
    bien, lieu = str(d.get("bien", "")).strip(), str(d.get("lieu", "")).strip()
    return Faits(evenements=evts, biens=[bien] if bien else secours.biens, lieux=[lieu] if lieu else secours.lieux,
                 circonstances=secours.circonstances)


def router(faits: Faits, compilation: ContratCompile) -> list[Fiche]:
    return [f for f in compilation.fiches if utilisable(f) and set(f.evenements) & set(faits.evenements)]


def router_par_le_modele(sinistre: str, compilation: ContratCompile, llm: LLM) -> list[Fiche]:
    utilisables = {f.id: f for f in compilation.fiches if utilisable(f)}
    liste = "\n".join(f"- {f.id} : {f.nom} — {f.objet}" for f in utilisables.values())
    donnees = extraire_json(llm.completer(SYSTEME_ROUTAGE, f"## Sinistre\n{sinistre}\n\n## Garanties\n{liste}"))
    return [utilisables[i] for i in donnees.get("fiches", []) if i in utilisables][:3]


def _condition(p: Point, groupe: str, nature: str) -> Condition:
    return Condition(nature=nature, role=p.role, groupe=groupe, clause_id=p.clause_id, extrait=p.extrait,
                     enonce=p.enonce, pages=p.pages, valide=p.valide, lien_causal=p.lien_causal)


# --- Décision -------------------------------------------------------------------------------------

RATTACHEE, POSSIBLE, HORS = "rattachée", "possible", "hors périmètre"


def decider_fiche(conditions: list[Condition]) -> tuple[str, Decision, str, list[str], float]:
    """Une fiche, comme un gestionnaire la lit. Renvoie (rattachement, décision, motif, à demander, confiance).

    1. Périmètre : un « non » (autre événement, autre bien, autre lieu) → hors périmètre.
    2. Circonstance « non » (pas d'effraction, pas de violence) → la garantie ne joue pas.
    3. Périmètre entièrement établi → fiche rattachée ; sinon → possible (on demande ce qui manque).
    4. Fiche rattachée :
       - une exclusion qui s'applique → NON_COUVERT ;
       - une circonstance inconnue → INCERTAIN (c'est à l'assuré d'établir les conditions de la garantie) ;
       - une obligation de prévention non respectée → INCERTAIN : la déchéance dépend du lien
         causal, qu'un gestionnaire doit apprécier (NON_COUVERT si le contrat ne l'exige pas) ;
       - sinon COUVERT. Une exclusion ou une obligation **inconnue** ne bloque pas : c'est à
         l'assureur de prouver qu'une exclusion s'applique. Elle devient une réserve (« sous réserve
         de vérifier… »), avec sa question et une confiance plafonnée à 0,7.
    Une exclusion n'est jamais consultée pour une garantie qui ne s'applique pas."""
    valides = [c for c in conditions if c.valide]
    perimetre = [c for c in valides if c.nature == "garantie" and c.role in PERIMETRE]
    circonstances = [c for c in valides if c.nature == "garantie" and c.role not in PERIMETRE]
    obligations = [c for c in valides if c.nature == "obligation"]
    exclusions = [c for c in valides if c.nature == "exclusion"]

    def marquer(cs):
        for c in cs:
            c.decisive = True
        return ", ".join(dict.fromkeys(f"art. {c.clause_id}" for c in cs))

    def demander(cs):
        return [c.question or c.enonce for c in cs]

    # Les questions de rôle « bien » énumèrent les catégories couvertes (bâtiment, contenu…) : ce
    # sont des alternatives. Il suffit qu'une soit établie ; hors périmètre seulement si toutes sont « non ».
    biens = [c for c in perimetre if c.role == "bien"]
    autres = [c for c in perimetre if c.role != "bien"]
    if biens and any(c.etat == OUI for c in biens):
        perimetre = autres + [c for c in biens if c.etat == OUI]
    hors = [c for c in autres if c.etat == NON] + (biens if biens and all(c.etat == NON for c in biens) else [])
    if hors:
        return HORS, Decision.NON_COUVERT, f"hors de son périmètre ({marquer(hors)})", [], 0.8
    manquees = [c for c in circonstances if c.etat == NON]
    if manquees:
        return RATTACHEE, Decision.NON_COUVERT, f"une condition n'est pas remplie ({marquer(manquees)})", [], 0.75
    perimetre_inconnu = [c for c in perimetre if c.etat == INCONNUE]
    if perimetre_inconnu or not perimetre:
        a_voir = perimetre_inconnu + [c for c in circonstances if c.etat == INCONNUE]
        marquer(a_voir)
        return POSSIBLE, Decision.INCERTAIN, "pourrait s'appliquer, selon des faits non précisés", demander(a_voir), 0.4

    appliquees = [c for c in exclusions if c.etat == OUI]
    if appliquees:
        return RATTACHEE, Decision.NON_COUVERT, f"une exclusion s'applique ({marquer(appliquees)})", [], 0.85
    ouvertes = [c for c in circonstances if c.etat == INCONNUE]
    if ouvertes:
        marquer(ouvertes)
        return RATTACHEE, Decision.INCERTAIN, "s'applique, selon des faits non précisés", demander(ouvertes), 0.55
    non_respectees = [c for c in obligations if c.etat == NON]
    if non_respectees:
        refs = marquer(non_respectees)
        if not any(c.lien_causal for c in non_respectees):
            return RATTACHEE, Decision.NON_COUVERT, f"une obligation de prévention n'est pas respectée ({refs})", [], 0.7
        return (RATTACHEE, Decision.INCERTAIN,
                f"une obligation de prévention n'est pas respectée ({refs}) : refus seulement s'il y a un lien causal avec le sinistre",
                ["Le non-respect de l'obligation a-t-il permis ou facilité le sinistre ?"], 0.5)
    marquer([c for c in perimetre + circonstances])
    partielles = [c for c in exclusions if c.justification.startswith("Partielle")]
    sauf = ("; sauf ce qu'exclut " + ", ".join(dict.fromkeys(f"l'art. {c.clause_id}" for c in partielles))
            + " (" + "; ".join(c.justification.removeprefix("Partielle : ") for c in partielles) + ")") if partielles else ""
    for c in partielles:
        c.decisive = True
    reserves = [c for c in exclusions + obligations if c.etat == INCONNUE
                and not c.justification.startswith("Présumée absente")]
    if reserves:
        return (RATTACHEE, Decision.COUVERT,
                f"s'applique : périmètre et conditions établis{sauf} ; sous réserve des vérifications ci-dessous",
                demander(reserves), 0.7)
    return (RATTACHEE, Decision.COUVERT,
            f"s'applique : périmètre et conditions établis{sauf}" + ("" if sauf else ", aucune exclusion"), [], 0.85)


def decider_fiches(chemins: list[tuple[Fiche, list[Condition]]]) -> tuple[Decision, str, list[str], float]:
    """Combine les fiches : COUVERT si une fiche rattachée l'est ; sinon INCERTAIN si une fiche
    rattachée l'est ; sinon NON_COUVERT si une fiche rattachée refuse (les fiches seulement
    « possibles » ajoutent leurs questions et baissent la confiance) ; sinon INCERTAIN si une fiche
    est possible ; sinon NON_COUVERT (aucune garantie ne s'applique) ; sinon INCERTAIN (rien à examiner)."""
    issues = []
    for fiche, conditions in chemins:
        for c in conditions:
            c.decisive = False
        issues.append((fiche, conditions, decider_fiche(conditions)))

    def garder_marques(retenues):
        for _, cs in chemins:
            for c in cs:
                c.decisive = False
        for _, cs, _ in retenues:
            decider_fiche(cs)

    def motif(retenues, prefixe):
        return prefixe + " ; ".join(f"« {f.nom} » : {r[2]}" for f, _, r in retenues) + "."

    rattachees = [x for x in issues if x[2][0] == RATTACHEE]
    possibles = [x for x in issues if x[2][0] == POSSIBLE]
    for d, prefixe in ((Decision.COUVERT, "Couvert. "), (Decision.INCERTAIN, "À préciser. ")):
        retenues = [x for x in rattachees if x[2][1] == d]
        if retenues:
            garder_marques(retenues[:1] if d == Decision.COUVERT else retenues)
            r = retenues[0][2]
            questions = list(dict.fromkeys(q for x in retenues for q in x[2][3]))
            return d, motif(retenues[:1] if d == Decision.COUVERT else retenues, prefixe), questions, r[4]
    if rattachees:
        garder_marques(rattachees)
        questions = list(dict.fromkeys(q for x in possibles for q in x[2][3]))
        confiance = min(x[2][4] for x in rattachees)
        return Decision.NON_COUVERT, motif(rattachees, "Non couvert. "), questions, min(confiance, 0.6) if possibles else confiance
    if possibles:
        garder_marques(possibles)
        return (Decision.INCERTAIN, motif(possibles, "À préciser. "),
                list(dict.fromkeys(q for x in possibles for q in x[2][3])), 0.4)
    if issues:
        garder_marques(issues)
        return Decision.NON_COUVERT, motif(issues, "Non couvert : aucune garantie ne s'applique. "), [], min(x[2][4] for x in issues)
    return (Decision.INCERTAIN, "Aucune garantie du contrat ne vise ce type d'événement.",
            ["Faire examiner le dossier par un gestionnaire."], 0.2)


# --- Juge -----------------------------------------------------------------------------------------

class JugeFiches:
    def __init__(self, llm: LLM, compilation: ContratCompile, clauses: list[Clause], tentatives: int = 2,
                 relecteur: LLM | None = None):
        if relecteur is not None:  # la relecture de plusieurs fiches est longue : on lui laisse le temps
            from .compilation import pour_compiler

            relecteur = pour_compiler(relecteur, max_tokens=8000, timeout=240)
        self.llm, self.compilation, self.tentatives, self.relecteur = llm, compilation, tentatives, relecteur
        self.index = {c.id: c for c in clauses}

    def _questions(self, fiches: list[Fiche]):
        """Les questions, par groupe (une fiche, puis les exclusions générales), et pour chaque fiche
        ce qui compte pour elle. Une exclusion générale n'est posée qu'une fois, mais compte pour
        chaque fiche de sa partie du contrat (art. 5.10 : responsabilité civile seulement)."""
        generales = [(p, _condition(p, "Exclusions générales", "exclusion"))
                     for p in self.compilation.exclusions_generales if p.valide]
        avec_garanties = {section(f.id) for f in self.compilation.fiches}
        groupes, chemins = [], []
        for f in fiches:
            propres = [(p, _condition(p, f.nom, "garantie")) for p in f.conditions if p.valide]
            propres += [(p, _condition(p, f"Obligations — {f.nom}", "obligation")) for p in f.obligations if p.valide]
            propres += [(p, _condition(p, f"Exclusions — {f.nom}", "exclusion")) for p in f.exclusions if p.valide]
            applicables = [c for p, c in generales
                           if section(p.clause_id) not in avec_garanties or section(p.clause_id) == section(f.id)]
            groupes.append((f.nom, propres))
            chemins.append((f, [c for _, c in propres] + applicables))
        poses = {id(c) for _, cs in chemins for c in cs}
        communes = [(p, c) for p, c in generales if id(c) in poses]
        if communes:
            groupes.append(("Exclusions générales", communes))
        return groupes, chemins

    def _repondre(self, sinistre: str, groupe: list[tuple[Point, Condition]]) -> tuple[dict | None, str | None]:
        """Un appel pour les questions d'un groupe. Petit, donc rapide et rarement coupé."""
        role = {"garantie": None, "obligation": "obligation", "exclusion": "exclusion"}
        liste = [{"id": f"q{n}", "role": role[c.nature] or c.role or "circonstance", "garantie": c.groupe,
                  "question": p.enonce, "passage": f"art. {p.clause_id} : {p.extrait}"}
                 for n, (p, c) in enumerate(groupe, start=1)]
        message = f"## Sinistre déclaré\n{sinistre}\n\n## Questions\n{json.dumps(liste, ensure_ascii=False, indent=1)}"
        erreur = None
        for _ in range(self.tentatives):
            try:
                return extraire_json(self.llm.completer(SYSTEME_FICHES, message)), None
            except ErreurLLM:
                raise
            except ReponseTronquee as e:
                erreur = e
                message += "\n\nTa réponse précédente était trop longue. Justifications de 8 mots au plus."
            except Exception as e:  # noqa: BLE001
                erreur = e
                message += "\n\nTa réponse précédente n'était pas un JSON valide. Réponds uniquement par l'objet JSON."
        return None, str(erreur)

    def juger(self, sinistre: str, fiches: list[Fiche]) -> Verdict:
        from concurrent.futures import ThreadPoolExecutor

        groupes, chemins = self._questions(fiches)
        mode = f"fiches:{self.llm.nom}" + (f"+relecture:{self.relecteur.nom}" if self.relecteur else "")
        if not fiches:
            decision, motif, demander, confiance = decider_fiches([])
            return Verdict(decision=decision, justification=motif, informations_manquantes=demander,
                           confiance=confiance, mode=mode)

        with ThreadPoolExecutor(max_workers=4) as pool:
            resultats = list(pool.map(lambda g: self._repondre(sinistre, g[1]), groupes))
        if all(d is None for d, _ in resultats):
            return Verdict(decision=Decision.INCERTAIN, justification="Le modèle n'a pas répondu aux questions.",
                           confiance=0.0, mode=mode, avertissements=[f"Réponse illisible : {resultats[0][1]}"])

        avertissements, resumes = [], []
        for (nom, groupe), (donnees, erreur) in zip(groupes, resultats):
            if donnees is None:
                avertissements.append(f"Pas de réponse pour « {nom} » ({erreur}) : ses questions restent inconnues.")
            reponses = {str(r.get("id")): r for r in (donnees or {}).get("reponses", []) if isinstance(r, dict)}
            if donnees and (donnees.get("resume") or "").strip():
                resumes.append(donnees["resume"].strip())
            for n, (p, c) in enumerate(groupe, start=1):
                r = reponses.get(f"q{n}")
                if r is None and donnees is not None:
                    avertissements.append(f"Pas de réponse à « {p.enonce} » : laissée inconnue.")
                r = r or {}
                etat = str(r.get("etat", "INCONNUE")).upper().replace(" ", "_")
                c.justification, c.question = str(r.get("justification", "")), str(r.get("question", ""))
                if etat == "PARTIELLE" and c.nature == "exclusion":
                    # Elle n'exclut qu'une partie des dommages : la garantie joue pour le reste.
                    etat, c.justification = "NON_REMPLIE", f"Partielle : {c.justification}"
                c.etat = EtatCondition(etat) if etat in EtatCondition.__members__ else INCONNUE
                if c.nature == "exclusion" and not p.a_demander and c.etat == INCONNUE:
                    c.etat = NON
                    c.justification = "Présumée absente : la déclaration ne l'évoque pas."
        questions = [(None, p, c) for _, g in groupes for p, c in g]
        donnees = {"resume": resumes[0] if resumes else ""}

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
                from .relecture import borner

                decision, divergence = borner(avant, decision)
                if divergence:
                    motif, confiance = divergence, min(confiance, 0.4)
                if decision != avant:
                    motif += f" (La relecture a contesté la première analyse, qui concluait {avant.value}.)"
                    resume = ""
                else:
                    avant = None
            elif any(n.startswith("Relecture indisponible") for n in notes):
                confiance = min(confiance, 0.6)

        limites = [_condition(p, "Limites", "limite") for f in fiches for p in f.limites if p.valide]
        for c in limites:
            c.etat = OUI
        citations = [Citation(clause_id=c.clause_id, extrait=c.extrait, role=c.nature, valide=True, pages=c.pages)
                     for c in toutes if c.decisive]
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
        from .consignes import CONSIGNES

        compilation = base.compilation(contrat_id)
        if compilation is None:
            raise LookupError(f"Le contrat {contrat_id} n'est pas compilé (ou a changé depuis) : "
                              f"lancer `couverture compiler --contrat {contrat_id}`.")
        version = CONSIGNES["couverture-compilation"][2]
        if compilation.consigne != version:
            raise LookupError(f"Le contrat {contrat_id} a été compilé avec la consigne {compilation.consigne}, "
                              f"la méthode attend la {version} : lancer `couverture compiler --contrat {contrat_id}`.")
        return cls(compilation, base.clauses(contrat_id), llm, relecteur)

    def analyser(self, sinistre: str) -> Resultat:
        faits = extraire_faits_modele(sinistre, self.llm)
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
