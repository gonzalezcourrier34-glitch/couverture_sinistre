"""La chaîne d'analyse : la lecture (lecture.py), la décision (prolog.py), la confirmation des faits décisifs, puis
la réponse, avec ses citations vérifiées et ses questions."""

from __future__ import annotations

import os
import time

from . import prolog
from .lecture import (affirmation, extraire_faits_regles, faits_decisifs, juger_affirmations, question,
                      sources_impliquees, variables_du_contrat)
from .llm import LLM, ErreurLLM
from .models import Citation, Clause, ClauseRetenue, Condition, Decision, EtatCondition, Faits, Resultat, Verdict
from .validation import valider


class PipelineRegles:
    methode = "regles"

    def __init__(self, contrat_id: str, clauses: list[Clause], llm: LLM, decideur=None):
        """`decideur(faits) -> dict` : par défaut SWI-Prolog ; remplaçable dans les tests."""
        self.contrat_id, self.clauses, self.llm = contrat_id, clauses, llm
        self.decideur = decideur or (lambda faits: prolog.decider(contrat_id, faits))
        self.variables = variables_du_contrat(contrat_id)
        self.exemples = None                  # la banque d'exemples (7.108, par défaut depuis 7.112)

    @classmethod
    def depuis_base(cls, base, contrat_id: str, llm: LLM) -> "PipelineRegles":
        if not prolog.fichier_regles(contrat_id).exists():
            raise LookupError(f"Pas de règles Prolog pour {contrat_id} (regles/{contrat_id}.pl).")
        if prolog.swipl() is None:
            raise LookupError("SWI-Prolog introuvable : `winget install SWI-Prolog.SWI-Prolog` (Windows).")
        p = cls(contrat_id, base.clauses(contrat_id), llm)
        from . import exemples
        # Les exemples demandent la clé (un vecteur par déclaration) et une banque indexée (`couverture exemples
        # --indexer`) ; sans l'une ou l'autre, la lecture se fait sans exemples, comme avant 7.108.
        if exemples.actifs() and os.environ.get("MISTRAL_API_KEY", "").strip():
            banque = exemples.Banque(base.chemin, exemples.EmbeddingsMistral())
            if banque.index:
                p.exemples = banque
        return p

    def analyser(self, sinistre: str) -> Resultat:
        debut = time.perf_counter()
        try:
            choix = self.exemples.pour(sinistre) if self.exemples is not None else None
            faits, ecarts = extraire_faits_regles(sinistre, self.llm, self.decideur, self.variables, choix)
        except ErreurLLM:
            raise
        except Exception as e:  # noqa: BLE001
            v = Verdict(decision=Decision.INCERTAIN, justification="Le modèle n'a pas pu lire la déclaration.",
                        confiance=0.0, mode=f"regles:{self.llm.nom}", avertissements=[str(e)])
            return Resultat(sinistre=sinistre, contrat_id=self.contrat_id, methode=self.methode, faits=Faits(),
                            clauses_consultees=[], verdict=v)
        lu = time.perf_counter()
        d = self.decideur(faits)
        decide = time.perf_counter()
        doutes: list[str] = []
        if d["decision"] in ("COUVERT", "NON_COUVERT"):
            d, doutes, avert = self.confirmer(sinistre, faits, d)
            ecarts = ecarts + avert
        verdict, consultees = self.verdict(d, faits)
        if doutes:
            # « Je ne sais pas » plutôt qu'une réponse fausse : un fait qui porte la décision n'est pas confirmé.
            verdict.decision = Decision.INCERTAIN
            verdict.confiance = min(verdict.confiance, 0.4)
            verdict.justification = ("Je ne peux pas trancher : la déclaration ne dit pas clairement "
                                     + " ; ni ".join(f"« {affirmation(v, faits[v], prolog.vocabulaire())[2:]} »" for v in doutes)
                                     + ". " + verdict.justification)
            # Une seule ligne par question : la version classée par le moteur (« oui → couvert ; non → … »)
            # remplace la question nue, au lieu de s'y ajouter.
            deja = verdict.informations_manquantes
            verdict.informations_manquantes = [question(v) for v in doutes
                                               if not any(q.startswith(question(v)) for q in deja)] + deja
            verdict.raisonnement = [f"Réponse suspendue : fait décisif non confirmé ({', '.join(doutes)}) ; "
                                    "ci-dessous, le raisonnement sans ce fait."] + verdict.raisonnement
        verdict.avertissements = ecarts + verdict.avertissements
        verdict = valider(verdict, consultees)
        return Resultat(sinistre=sinistre, contrat_id=self.contrat_id, methode=self.methode,
                        faits=faits_lisibles(faits), clauses_consultees=consultees, verdict=verdict,
                        durees_ms={"lecture": int((lu - debut) * 1000), "decision": int((decide - lu) * 1000)})

    def confirmer(self, sinistre: str, faits: dict, d: dict) -> tuple[dict, list[str], list[str]]:
        """Une réponse ferme doit reposer sur des faits confirmés (7.49). Le moteur dit quels faits portent la
        décision ; le modèle confirme, sur la déclaration, que chacun y est écrit. Un seul « non dit » : la
        réponse devient « incertain », avec la question sur ce fait. Rend (décision, faits douteux, avertissements)."""
        decisifs = faits_decisifs(faits, self.decideur, d["decision"])
        if not decisifs:
            return d, [], []
        # Un fait déduit d'un autre (« implique », 7.94) n'est pas écrit tel quel : on confirme le fait qui le dit
        # (« entré sans effraction »), pas sa conséquence (« effraction = non »), que la confirmation jugeait « non
        # dite » une fois sur trois (f-d18, 7.95).
        voc = prolog.vocabulaire()
        sources = sources_impliquees(faits, voc)
        a_juger = list(dict.fromkeys(sources.get(v, v) for v in decisifs))
        try:
            verdicts = juger_affirmations(sinistre, {v: faits[v] for v in a_juger}, self.llm, voc)
        except ErreurLLM:
            raise
        except Exception as e:  # noqa: BLE001
            return d, [], [f"confirmation des faits décisifs illisible ({e}) : réponse gardée"]
        doutes = [v for v in decisifs if verdicts.get(sources.get(v, v)) == "non_dit"]
        if not doutes:
            return d, [], []
        sans = {k: x for k, x in faits.items() if k not in doutes}
        return self.decideur(sans), doutes, [f"{v} : fait décisif non confirmé par la déclaration" for v in doutes]

    def verdict(self, d: dict, faits: dict) -> tuple[Verdict, list[ClauseRetenue]]:
        decision = Decision(d["decision"])
        retenues = d.get("retenues", [])
        motifs = [f"« {r['garantie']} » ({r['article']}) : {r['motif']}" for r in retenues]
        non_traduits = d.get("non_traduits") or []
        if d.get("aucune"):
            motif = "Non couvert : aucune garantie ne s'applique."
        else:
            motif = {"COUVERT": "Couvert. ", "NON_COUVERT": "Non couvert. ", "INCERTAIN": "À préciser. "}[decision.value] \
                + " ; ".join(motifs[:3]) + "."
        accessoires = d.get("accessoires") or []
        if accessoires and decision == Decision.COUVERT:
            # 7.68 : ce qui peut s'ajouter à la garantie qui couvre, sans changer la décision.
            motif += " Peuvent s'y ajouter : " + " ; ".join(
                f"« {a['garantie']} » ({a['article']})" + (" sous réserve de précisions" if a.get("decision") == "INCERTAIN"
                                                          or a.get("reserves") else "") for a in accessoires[:4]) + "."
        if non_traduits:
            evts = ", ".join(non_traduits)
            motif = (f"À examiner par un gestionnaire : l'événement « {evts} » relève d'une garantie qui n'est pas "
                     f"encore traduite en règles. Ce que disent les garanties traduites : " + (" ; ".join(motifs[:3]) or "rien") + ".")
        vars_ = [v for v, _ in points_a_preciser(d, prolog.vocabulaire())]
        demander = list(dict.fromkeys(question(v) for v in vars_))
        exploration = d.get("exploration")
        if exploration:
            demander, motif = questions_explorees(exploration, vars_, motif)
        confiance = {"COUVERT": 0.85, "NON_COUVERT": 0.85, "INCERTAIN": 0.4}[decision.value]
        if non_traduits:
            confiance = 0.3
        if decision == Decision.COUVERT and any(r.get("reserves") for r in retenues):
            confiance = 0.7
        if decision == Decision.NON_COUVERT and demander:
            confiance = 0.6

        index = {c.id: c for c in self.clauses}
        preuves = [p for r in (retenues if not d.get("aucune") else retenues[:3]) for p in r.get("preuves", [])
                   + r.get("partielles", [])]
        conditions, vus = [], set()
        for p in preuves:
            cle = (p["article"], p["texte"])
            if cle in vus:
                continue
            vus.add(cle)
            nature = "exclusion" if "exclusion" in p["role"] else "limite" if p["role"] == "limite" else "garantie"
            conditions.append(Condition(nature=nature, groupe=p["role"], clause_id=p["article"], extrait=p["texte"],
                                        enonce=p["role"].capitalize() + (f" (sauf {p['bien']})" if p.get("bien") else ""),
                                        etat=EtatCondition.REMPLIE, decisive=True,
                                        pages=index[p["article"]].pages if p["article"] in index else []))
        for r in retenues:
            for lim in r.get("limites", []):
                conditions.append(Condition(nature="limite", groupe="Limites", clause_id=lim["article"],
                                            extrait=lim["texte"], enonce=f"{lim['montant']}", etat=EtatCondition.REMPLIE))
        citations = [Citation(clause_id=c.clause_id, extrait=c.extrait, role=c.nature, pages=c.pages)
                     for c in conditions if c.nature != "limite"]
        consultees = [ClauseRetenue(clause=index[i], score=0.0, raison="règle")
                      for i in dict.fromkeys(c.clause_id for c in conditions) if i in index]
        v = Verdict(decision=decision, justification=motif, citations=citations, conditions=conditions,
                    informations_manquantes=demander, confiance=confiance, mode=f"regles:{self.llm.nom}+prolog",
                    preuve=d.get("preuve", []), raisonnement=arbre_lisible(d.get("preuve", [])))
        return v, consultees


# --- Arbre de preuve, en lignes lisibles --------------------------------------------------------------

MARQUE = {"oui": "[oui]", "non": "[non]", "inconnu": "[ ? ]"}


def _vu(n: dict) -> str:
    return f"déclaré : {', '.join(n['declare'])}" if n["declare"] else "non déclaré"


def _condition(n: dict, prof: int, lignes: list[str], complet: bool, cites: set) -> None:
    """Une condition et ses sous-conditions, élaguée : d'un « ou » vrai, la branche vraie ; d'un « et »
    faux, les branches fausses ; un « si » dont la prémisse est fausse est sans objet. Ce qui a décidé
    reste, le reste se compte. Le texte d'une définition n'est cité qu'une fois."""
    ind, m, t = "  " * prof, MARQUE[n["etat"]], n["type"]
    enfants = n["enfants"]
    if t == "fait":
        lignes.append(f"{ind}{m} {n['variable']} = {n['attendu']} ({_vu(n)})")
    elif t in ("vrai", "faux"):
        lignes.append(f"{ind}{m} {t}")
    elif t == "concept":
        texte = "" if n["nom"] in cites and not complet else f" : « {n['texte']} »"
        cites.add(n["nom"])
        lignes.append(f"{ind}{m} {n['nom']} (art. {n['article']}{texte})")
        _condition(enfants[0], prof + 1, lignes, complet, cites)
    elif t == "non":
        lignes.append(f"{ind}{m} pas :")
        _condition(enfants[0], prof + 1, lignes, complet, cites)
    elif t == "si" and enfants[0]["etat"] == "non" and not complet:
        lignes.append(f"{ind}{m} sans objet ici :")
        _condition(enfants[0], prof + 1, lignes, complet, cites)
    elif t == "si":
        lignes.append(f"{ind}{m} si … alors … :")
        for e in enfants:
            _condition(e, prof + 1, lignes, complet, cites)
    elif t == "ou" and all(e["type"] == "fait" for e in enfants) and len({e["variable"] for e in enfants}) == 1:
        lignes.append(f"{ind}{m} {enfants[0]['variable']} parmi {', '.join(e['attendu'] for e in enfants)} ({_vu(enfants[0])})")
    else:
        garder = {("ou", "oui"): "oui", ("et", "non"): "non"}.get((t, n["etat"]))
        montres = enfants if complet or garder is None else [e for e in enfants if e["etat"] == garder]
        lignes.append(f"{ind}{m} {'toutes' if t == 'et' else 'l’une'} de :")
        for e in montres:
            _condition(e, prof + 1, lignes, complet, cites)
        if len(montres) < len(enfants):
            lignes.append(f"{ind}  … {len(enfants) - len(montres)} autre(s), sans effet sur la conclusion")


SENS = {
    "périmètre": ("Périmètre", {"oui": "établi", "non": "non établi", "inconnu": "inconnu"}),
    "condition": ("Condition", {"oui": "remplie", "non": "non remplie", "inconnu": "inconnue"}),
    "obligation": ("Obligation", {"oui": "respectée", "non": "non respectée", "inconnu": "à vérifier"}),
    "exclusion": ("Exclusion", {"oui": "s'applique", "non": "ne s'applique pas", "inconnu": "à établir"}),
}


def arbre_lisible(preuve: list[dict], complet: bool = False) -> list[str]:
    """L'arbre de preuve du moteur (moteur.pl, arbres_de_preuve/2) en lignes : la garantie, puis chaque nœud avec
    sa phrase du contrat et son état, jusqu'aux faits déclarés. Sans `complet`, les exclusions qui ne
    jouent pas, et celles que l'assureur devrait prouver sans que la déclaration les évoque, sont
    comptées au lieu d'être listées."""
    lignes: list[str] = []
    for g in preuve:
        lignes.append(f"Garantie « {g['nom']} » (art. {g['article']}) → {ISSUE.get(g['decision'], g['decision'])}")
        cites: set = set()
        ecartees, presumees = 0, []
        for n in g["enfants"]:
            if n["type"] == "exclusion" and not complet:
                if n["etat"] == "non":
                    ecartees += 1
                    continue
                if n["etat"] == "inconnu" and n.get("a_demander") == "non":
                    presumees.append(n["article"])
                    continue
            role, sens = SENS[n["type"]]
            phrase = f" — art. {n['article']} : « {n['texte']} »" if n.get("article") else ""
            lignes.append(f"  {MARQUE[n['etat']]} {role} {sens[n['etat']]}{phrase}")
            for e in n["enfants"]:
                _condition(e, 3, lignes, complet, cites)
            if n["type"] == "obligation" and n["exception"]["etat"] == "oui":
                lignes.append("      sans incidence ici :")
                _condition(n["exception"], 4, lignes, complet, cites)
        if ecartees:
            lignes.append(f"  {ecartees} exclusion(s) examinée(s) : aucune ne s'applique")
        if presumees:
            arts = ", ".join(dict.fromkeys(presumees))
            lignes.append(f"  {len(presumees)} exclusion(s) que la déclaration n'évoque pas (art. {arts}) : "
                          "l'assureur devrait les prouver, elles ne changent pas la réponse")
    return lignes


ISSUE = {"COUVERT": "couvert", "NON_COUVERT": "non couvert", "INCERTAIN": "encore incertain", "ERREUR": "?"}


def points_a_preciser(d: dict, voc: dict) -> list[tuple[str, str]]:
    """Ce qu'on dit au client de préciser, variable par variable : (variable, "question" | "reserve"). Le même
    choix pour le texte du verdict et pour l'API (7.114).

    - `question` : sans la réponse, la garantie ne tranche pas ; pour un refus, aussi les questions des garanties
      possibles (une autre pourrait couvrir) ;
    - `reserve` : seulement quand c'est couvert, ce que l'assureur pourra vérifier (une exclusion qu'il aurait à
      prouver). Pour une réponse à préciser ou un refus, une réserve ne change rien : elle n'est pas posée ;
    - jamais une réserve qui vaut pour tous les sinistres (« pour » couvre tous les événements : le déménagement
      non signalé) : elle n'apprend rien sur celui-ci. Si la déclaration la met en jeu, le moteur en fait une
      question (exclusion entamée), et elle est posée."""
    tous = set(voc.get("evenement", {}).get("valeurs", []))
    retenues, possibles = d.get("retenues", []), d.get("possibles", [])
    points: dict[str, str] = {}
    for r in retenues:
        for v in r.get("questions", []):
            points.setdefault(v, "question")
    if d.get("decision") == "NON_COUVERT":
        for r in possibles:
            for v in r.get("questions", []):
                points.setdefault(v, "question")
    if d.get("decision") == "COUVERT":
        for r in retenues:
            for v in r.get("reserves", []):
                if not (tous and set(voc.get(v, {}).get("pour", [])) >= tous):
                    points.setdefault(v, "reserve")
    return list(points.items())


def questions_explorees(exploration: dict, vars_: list[str], motif: str) -> tuple[list[str], str]:
    """Les questions classées par le raisonnement par hypothèses du moteur (moteur.pl, explorer/2) :
    décisives d'abord, avec ce que chaque réponse entraîne ; les inutiles ne sont pas posées.
    Les questions sans domaine (le lien de causalité, une appréciation) sont gardées telles quelles. Seules les
    variables choisies par `points_a_preciser` sont posées : l'exploration ne réintroduit pas une réserve écartée
    (le déménagement sur une réponse couverte, 7.115)."""
    explorees = {q["variable"]: q for q in exploration.get("questions", [])}
    lignes = []
    for q in exploration.get("questions", []):
        if q["effet"] == "inutile" or q["variable"] not in vars_:
            continue
        texte = question(q["variable"])
        if q["effet"] == "décisive":
            issues = " ; ".join(f"{'/'.join(i['valeurs'][:4])}{'…' if len(i['valeurs']) > 4 else ''} → {ISSUE[i['decision']]}"
                                for i in q["issues"])
            texte += f" ({issues})"
        lignes.append(texte)
    lignes += [question(v) for v in vars_ if v not in explorees]
    ensemble = exploration.get("ensemble") or []
    if ensemble:
        motif += (" Une seule question tranche : " if len(ensemble) == 1 else " Ces deux questions tranchent : ") \
            + " ; ".join(f"« {question(v)} »" for v in ensemble) + "."
    return list(dict.fromkeys(lignes)), motif


def faits_lisibles(faits: dict) -> Faits:
    def liste(v):
        x = faits.get(v)
        return [] if x is None else (x if isinstance(x, list) else [x])

    autres = [f"{v}={x}" for v, x in faits.items() if v not in ("evenement", "bien", "lieu")]
    return Faits(evenements=liste("evenement"), biens=liste("bien"), lieux=liste("lieu"), circonstances=autres)
