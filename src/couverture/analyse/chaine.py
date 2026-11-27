"""La chaîne d'analyse : la lecture (lecture.py), la décision (prolog.py), la confirmation des faits décisifs, puis
la réponse, avec ses citations vérifiées et ses questions."""

from __future__ import annotations

import os
import time

from ..llm import LLM, ErreurLLM
from ..models import Citation, Clause, ClauseRetenue, Condition, Decision, EtatCondition, Faits, Resultat, Verdict
from ..models import LIBELLES_DECISION as _LIBELLES_DECISION
from . import prolog
from .lecture import (decouper_sinistres, extraire_faits_regles, faits_decisifs, juger_affirmations, question,
                      sources_impliquees, variables_du_contrat)
from .validation import valider


def numero(article: str) -> str:
    """Le numéro d'article tel qu'il est imprimé dans le contrat : « 4~1 », premier morceau de l'article 4 dans la
    base, se lit « 4 »."""
    return str(article).split("~")[0]


# Le motif d'une garantie que le moteur écarte par une exclusion certaine sans savoir si elle s'appliquerait
# (regles/moteur.pl, `issue` avec un périmètre inconnu). Le même texte des deux côtés : un test le vérifie.
EXCLUE_SANS_ETRE_ETABLIE = "exclue, que la garantie s'applique ou non"
SANS_GARANTIE = "Non couvert : aucune garantie de ce contrat ne porte sur cet événement."


def phrases_des_garanties(retenues: list[dict]) -> list[str]:
    """Une phrase par article et par motif (7.167) : trois garanties du même article écartées pour la même raison
    se disent une fois, « A », « B », « C » (2.7-a) : hors de son périmètre."""
    groupes: dict[tuple[str, str], list[str]] = {}
    for r in retenues:
        noms = groupes.setdefault((numero(r["article"]), r["motif"]), [])
        if r["garantie"] not in noms:
            noms.append(r["garantie"])
    return [", ".join(f"« {n} »" for n in noms) + f" ({article}) : {motif}" for (article, motif), noms in groupes.items()]


SANS_EVENEMENT = ("À préciser. Je n'ai pas reconnu de sinistre dans ce texte : il ne dit pas ce qui s'est passé "
                  "(un vol, un incendie, un dégât des eaux, un dommage causé à quelqu'un…). Aucune garantie n'a été "
                  "examinée.")


def phrase_de_la_reponse(d: dict, decision: Decision, retenues: list[dict], exclues: list[dict],
                         non_traduits: list[str], sans_garantie: list[str]) -> str:
    """La phrase de la réponse : la décision, puis les garanties en jeu et leur motif. Un dossier qui part chez un
    gestionnaire dit pourquoi (un événement pas encore traduit, ou sans garantie au contrat)."""
    motifs = phrases_des_garanties(retenues)
    if exclues:
        motif = ("Non couvert : aucune garantie ne s'applique, et le contrat l'exclut expressément ("
                 + " ; ".join(dict.fromkeys(f"« {x['garantie']} », {numero(x['article'])}" for x in exclues[:3])) + ").")
    elif d.get("aucune"):
        # Les garanties de l'événement, et pourquoi elles ne jouent pas : leurs clauses citées le disent (7.222).
        motif = ("Non couvert : aucune garantie ne s'applique. " + " ; ".join(motifs[:3]) + "." if retenues
                 else SANS_GARANTIE)
    elif decision == Decision.NON_COUVERT and retenues and all(r.get("motif") == EXCLUE_SANS_ETRE_ETABLIE
                                                              for r in retenues):
        # 7.164 : aucune garantie n'est établie, une exclusion les écarte toutes. La phrase cite l'exclusion,
        # pas des garanties dont rien ne dit qu'elles concernaient ce sinistre.
        articles = dict.fromkeys(numero(p["article"]) for r in retenues for p in r.get("preuves", []))
        motif = "Non couvert : le contrat exclut ce cas" + (f" ({' ; '.join(list(articles)[:3])})" if articles else "") + "."
    else:
        # Une garantie n'est nommée que si le sinistre s'y rattache : celles qu'une exclusion écarte sans qu'elles
        # soient établies ne le sont pas (leur clause d'exclusion reste citée).
        nommees = phrases_des_garanties([r for r in retenues if decision != Decision.NON_COUVERT
                                         or r.get("motif") != EXCLUE_SANS_ETRE_ETABLIE])
        motif = {"COUVERT": "Couvert. ", "NON_COUVERT": "Non couvert. ", "INCERTAIN": "À préciser. "}[decision.value] \
            + " ; ".join(nommees[:3]) + "."
    accessoires = d.get("accessoires") or []
    if accessoires and decision == Decision.COUVERT:
        # 7.68 : ce qui peut s'ajouter à la garantie qui couvre, sans changer la décision.
        motif += " Peuvent s'y ajouter : " + " ; ".join(
            f"« {a['garantie']} » ({numero(a['article'])})" + (" sous réserve de précisions" if a.get("decision") == "INCERTAIN"
                                                      or a.get("reserves") else "") for a in accessoires[:4]) + "."
    if non_traduits:
        evts = ", ".join(non_traduits)
        motif = (f"À examiner par un gestionnaire : l'événement « {evts} » relève d'une garantie qui n'est pas "
                 f"encore traduite en règles." + (" Ce que disent les garanties traduites : " + " ; ".join(motifs[:3]) + "."
                                                if motifs else ""))
    elif sans_garantie:
        evts = ", ".join(sans_garantie)
        motif = (f"À examiner par un gestionnaire : aucune garantie de ce contrat ne porte sur « {evts} », et la "
                 f"déclaration parle aussi d'autre chose." + (" Pour le reste : " + " ; ".join(motifs[:3]) + "."
                                                              if motifs else ""))
    return motif


def confiance_de_la_reponse(decision: Decision, retenues: list[dict], vars_: list[str], demander: list[str],
                            non_traduits: list[str], sans_garantie: list[str], motif: str) -> tuple[float, str]:
    """La confiance affichée, d'après la décision et ce qui reste à vérifier ; et la phrase, sans sa mention
    « sous réserve » quand aucune réserve ne concerne ce sinistre."""
    confiance = {"COUVERT": 0.85, "NON_COUVERT": 0.85, "INCERTAIN": 0.4}[decision.value]
    if non_traduits or sans_garantie:
        confiance = 0.3
    if decision == Decision.COUVERT and any(r.get("reserves") for r in retenues):
        if vars_:
            confiance = 0.7
        else:
            # Les seules réserves sont hors sujet pour ce sinistre (7.124) : rien n'est à vérifier.
            motif = motif.replace(" ; sous réserve des vérifications à faire", "")
    if decision == Decision.NON_COUVERT and demander:
        confiance = 0.6
    return confiance, motif


def conditions_citees(d: dict, retenues: list[dict], exclues: list[dict], index: dict[str, Clause]) -> list[Condition]:
    """Les phrases du contrat sur lesquelles la réponse s'appuie, une fois chacune : les preuves des garanties
    retenues (ou les exclusions expresses, quand aucune garantie ne s'applique), puis les limites."""
    preuves = [p for r in (retenues if not d.get("aucune") else retenues[:3]) for p in r.get("preuves", [])
               + r.get("partielles", [])]
    if exclues:
        preuves = [{"article": x["article"], "texte": x["texte"], "role": "exclusion"} for x in exclues[:5]]
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
    return conditions


class PipelineRegles:
    """La chaîne d'analyse d'un sinistre sur un contrat : le modèle lit les faits, le moteur de règles décide, le code
    rédige la réponse et vérifie les citations."""

    methode = "regles"

    def __init__(self, contrat_id: str, clauses: list[Clause], llm: LLM, decideur=None):
        """`decideur(faits) -> dict` : par défaut SWI-Prolog ; remplaçable dans les tests."""
        self.contrat_id, self.clauses, self.llm = contrat_id, clauses, llm
        self.decideur = decideur or (lambda faits: prolog.decider(contrat_id, faits))
        self.variables = variables_du_contrat(contrat_id)
        self.voc = prolog.vocabulaire_du_contrat(contrat_id)     # les formules de ce contrat, pas celles d'un autre (7.154)
        self.exemples = None                  # la banque d'exemples (7.108, par défaut depuis 7.112)
        self.llm_socle = None                 # un autre modèle pour le temps 1 (COUVERTURE_MODELE_SOCLE, 7.118)
        self.llm_verification = None          # un autre modèle pour vérifier et confirmer (7.136)

    @classmethod
    def depuis_base(cls, base, contrat_id: str, llm: LLM) -> "PipelineRegles":
        """La chaîne d'un contrat de la base, avec ses modèles de lecture et de vérification et la banque d'exemples ;
        `LookupError` sans règles pour ce contrat ou sans SWI-Prolog."""
        if not prolog.fichier_regles(contrat_id).exists():
            raise LookupError(f"Pas de règles Prolog pour {contrat_id} (regles/{contrat_id}.pl).")
        if prolog.swipl() is None:
            raise LookupError("SWI-Prolog introuvable : `winget install SWI-Prolog.SWI-Prolog` (Windows).")
        p = cls(contrat_id, base.clauses(contrat_id), llm)
        from . import exemples
        from ..llm import modele_de_verification, modele_du_socle
        p.llm_socle = modele_du_socle(llm)
        p.llm_verification = modele_de_verification(llm)
        # Les exemples demandent la clé (un vecteur par déclaration) et une banque indexée (`couverture exemples
        # --indexer`) ; sans l'une ou l'autre, la lecture se fait sans exemples, comme avant 7.108.
        if exemples.actifs() and os.environ.get("MISTRAL_API_KEY", "").strip():
            banque = exemples.Banque(base.chemin, exemples.EmbeddingsMistral())
            if banque.index:
                p.exemples = banque
        return p

    def analyser(self, sinistre: str, suivi=None, souscription: dict | None = None) -> Resultat:
        """L'analyse d'une déclaration. Si elle contient plusieurs sinistres, chacun reçoit sa réponse (7.168).

        La déclaration est d'abord analysée d'un bloc, comme toujours. Si la lecture y trouve au moins deux
        événements, le modèle dit s'ils font un seul sinistre (une cause et ses conséquences) ou plusieurs ; dans le
        second cas, la chaîne entière est rejouée sur les phrases de chaque sinistre, et la réponse les liste.
        `COUVERTURE_DECOUPAGE=non` revient à une réponse pour le tout."""
        r = self.analyser_un(sinistre, suivi=suivi, souscription=souscription)
        if len(r.faits.evenements) < 2 or os.environ.get("COUVERTURE_DECOUPAGE", "oui").lower() in {"non", "0", "false"}:
            return r
        try:
            parties = decouper_sinistres(sinistre, self.llm)
        except Exception as e:  # noqa: BLE001 - sans découpage, la réponse d'un bloc reste valable
            r.verdict.avertissements = r.verdict.avertissements + [f"découpage en sinistres impossible ({e})"]
            return r
        if not parties:
            return r
        if suivi:
            suivi("confirmation", f"{len(parties)} sinistres dans la déclaration : chacun est analysé à part")
        analyses = []
        for p in parties:
            x = self.analyser_un(p["texte"], souscription=souscription)
            x.titre = p["titre"]
            analyses.append(x)
        return plusieurs_sinistres(r, analyses)

    def analyser_un(self, sinistre: str, suivi=None, souscription: dict | None = None) -> Resultat:
        """`suivi(etape, detail=None)` : le fil de l'analyse, étape par étape (7.134) ; None : rien.
        `souscription` : ce que disent les conditions particulières du client ({variable: valeur} : la formule,
        les options) ; ces faits s'ajoutent à ceux lus dans la déclaration, et l'emportent sur eux (7.141)."""
        dire = suivi or (lambda etape, detail=None: None)
        debut = time.perf_counter()
        try:
            choix = self.exemples.pour(sinistre) if self.exemples is not None else None
            faits, ecarts = extraire_faits_regles(sinistre, self.llm, self.decideur, self.variables, choix,
                                                  llm_socle=self.llm_socle, suivi=suivi,
                                                  llm_verification=self.llm_verification, voc=self.voc)
        except ErreurLLM:
            raise
        except Exception as e:  # noqa: BLE001
            v = Verdict(decision=Decision.INCERTAIN, justification="Le modèle n'a pas pu lire la déclaration.",
                        confiance=0.0, mode=f"regles:{self.llm.nom}", avertissements=[str(e)])
            return Resultat(sinistre=sinistre, contrat_id=self.contrat_id, methode=self.methode, faits=Faits(),
                            clauses_consultees=[], verdict=v)
        lu = time.perf_counter()
        souscrits, ecarts_souscription = prolog.retenir_souscription(self.contrat_id, souscription)
        # Le contrat du client fait foi : ce qu'il donne l'emporte sur ce que la déclaration en dit.
        faits = {v: x for v, x in faits.items() if v not in souscrits} | souscrits
        ecarts = ecarts + ecarts_souscription
        if not faits.get("evenement"):
            # Sans événement, le moteur n'a rien à décider : il rendait toutes les garanties « possibles » et une
            # question sans rapport (« d'où venait l'eau ? » pour un texte qui n'est pas une déclaration, 7.142).
            dire("decision")
            dire("decision", "aucun sinistre reconnu : les règles ne sont pas appliquées")
            dire("confirmation")
            dire("confirmation", "rien à confirmer")
            v = Verdict(decision=Decision.INCERTAIN, confiance=0.0, mode=f"regles:{self.llm.nom}+prolog",
                        justification=SANS_EVENEMENT, informations_manquantes=[question("evenement")],
                        avertissements=ecarts)
            return Resultat(sinistre=sinistre, contrat_id=self.contrat_id, methode=self.methode,
                            faits=faits_lisibles(faits), clauses_consultees=[], verdict=v,
                            durees_ms={"lecture": int((lu - debut) * 1000), "decision": 0})
        dire("decision")
        d = self.decideur(faits)
        decide = time.perf_counter()
        libelles = {"COUVERT": "couvert", "NON_COUVERT": "non couvert", "INCERTAIN": "à préciser"}
        dire("decision", f"le moteur répond : {libelles.get(d['decision'], d['decision'])}")
        doutes: list[str] = []
        dire("confirmation")
        if d["decision"] in ("COUVERT", "NON_COUVERT"):
            d, doutes, avert = self.confirmer(sinistre, faits, d, donnes=set(souscrits))
            ecarts = ecarts + avert
        dire("confirmation", ("non confirmé dans la déclaration : " + " ; ".join(v.replace("_", " ") for v in doutes)
                              + " ; la réponse devient « à préciser »") if doutes
             else "les faits qui portent la réponse sont confirmés" if d["decision"] != "INCERTAIN"
             else "rien à confirmer : la réponse est déjà « à préciser »")
        verdict, consultees = self.verdict(d, faits)
        if doutes:
            # « Je ne sais pas » plutôt qu'une réponse fausse : un fait qui porte la décision n'est pas confirmé.
            verdict.decision = Decision.INCERTAIN
            verdict.confiance = min(verdict.confiance, 0.4)
            # En mots du client (7.127) : la question, pas le nom de la variable ni la valeur écartée ; et la
            # décision sans ce fait n'est pas annoncée comme la réponse (« Couvert. » après « je ne peux pas
            # trancher » se contredisait).
            reste = verdict.justification
            for prefixe in ("Couvert. ", "Non couvert. ", "À préciser. "):
                reste = reste.removeprefix(prefixe)
            verdict.justification = ("Je ne peux pas trancher : la déclaration ne répond pas clairement à "
                                     + " ; ni à ".join(f"« {question(v)} »" for v in doutes)
                                     + " Selon la réponse, la décision change. Garantie en jeu : " + reste)
            # Une seule ligne par question : la version classée par le moteur (« oui → couvert ; non → … »)
            # remplace la question nue, au lieu de s'y ajouter.
            deja = verdict.informations_manquantes
            verdict.informations_manquantes = [question(v) for v in doutes
                                               if not any(q.startswith(question(v)) for q in deja)] + deja
            verdict.raisonnement = [f"Réponse suspendue : fait décisif non confirmé ({', '.join(doutes)}) ; "
                                    "ci-dessous, le raisonnement sans ce fait."] + verdict.raisonnement
        verdict.avertissements = ecarts + verdict.avertissements
        verdict = self.valider(verdict, consultees)
        return Resultat(sinistre=sinistre, contrat_id=self.contrat_id, methode=self.methode,
                        faits=faits_lisibles(faits), clauses_consultees=consultees, verdict=verdict,
                        durees_ms={"lecture": int((lu - debut) * 1000), "decision": int((decide - lu) * 1000)})

    def confirmer(self, sinistre: str, faits: dict, d: dict, donnes=None) -> tuple[dict, list[str], list[str]]:
        """Une réponse ferme doit reposer sur des faits confirmés (7.49). Le moteur dit quels faits portent la
        décision ; le modèle confirme, sur la déclaration, que chacun y est écrit. Un seul « non dit » : la
        réponse devient « incertain », avec la question sur ce fait. Rend (décision, faits douteux, avertissements)."""
        # Un fait donné par les conditions particulières ne se confirme pas dans la déclaration : il n'en vient
        # pas (7.141). Le même fait lu dans la déclaration (« j'ai la formule Privilège ») se confirme comme un autre.
        decisifs = [v for v in faits_decisifs(faits, self.decideur, d["decision"]) if v not in (donnes or ())]
        if not decisifs:
            return d, [], []
        voc = prolog.vocabulaire()
        # Un fait déduit d'un autre (« implique », 7.94) n'est pas écrit tel quel : on confirme le fait qui le dit
        # (« entré sans effraction »), pas sa conséquence (« effraction = non »), que la confirmation jugeait « non
        # dite » une fois sur trois (f-d18, 7.95).
        sources = sources_impliquees(faits, voc)
        a_juger = list(dict.fromkeys(sources.get(v, v) for v in decisifs))
        try:
            verdicts = juger_affirmations(sinistre, {v: faits[v] for v in a_juger},
                                          self.llm_verification or self.llm, voc)
        except ErreurLLM:
            raise
        except Exception as e:  # noqa: BLE001
            return d, [], [f"confirmation des faits décisifs illisible ({e}) : réponse gardée"]
        doutes = [v for v in decisifs if verdicts.get(sources.get(v, v)) == "non_dit"]
        if not doutes:
            return d, [], []
        sans = {k: x for k, x in faits.items() if k not in doutes}
        return self.decideur(sans), doutes, [f"{v} : fait décisif non confirmé par la déclaration" for v in doutes]

    def valider(self, verdict: Verdict, consultees: list[ClauseRetenue]) -> Verdict:
        """La validation des citations, avec la seule exception admise (7.177) : dans un contrat traduit en entier,
        « aucune garantie ne porte sur cet événement » est un refus qui n'a aucune phrase à citer. Sans cette
        exception, la validation le ramenait à « à préciser », sous une phrase qui disait « non couvert »."""
        sans_citation = (verdict.decision == Decision.NON_COUVERT and verdict.justification == SANS_GARANTIE
                         and prolog.traduction_complete(self.contrat_id))
        return valider(verdict, consultees, roles_des_regles=True, refus_sans_citation=sans_citation)

    def _perimetre_de_la_reponse(self, d: dict, faits: dict) -> tuple[dict, Decision, list[dict], list[str], list[str]]:
        """Ce dont la réponse parlera : les garanties qui portent sur l'événement déclaré, et les événements que les
        règles ne traitent pas (pas encore traduits, ou sans garantie dans un contrat traduit en entier). Un contrat
        traduit en entier refuse un événement pour lequel il n'a aucune garantie."""
        decision = Decision(d["decision"])
        retenues = d.get("retenues", [])
        if "visent_evenement" in d:
            # 7.165 : une garantie écartée dès son périmètre n'est nommée et citée que si elle porte sur l'événement
            # déclaré. Les garanties du vol n'ont rien à dire d'une bougie fondue.
            vises = set(d["visent_evenement"])
            retenues = [r for r in retenues if r.get("rattachement") != "hors" or r.get("id") in vises]
        non_traduits = d.get("non_traduits") or []
        sans_garantie = []
        if non_traduits and prolog.traduction_complete(self.contrat_id):
            # 7.177 : « pas encore traduite » est faux quand tout le contrat est traduit. Il n'a alors aucune
            # garantie pour cet événement. Si la déclaration ne porte que sur lui, c'est un refus ; si elle porte
            # aussi sur autre chose, le dossier reste à examiner, mais la phrase dit ce qui manque et pourquoi.
            evenements = faits.get("evenement") or []
            evenements = evenements if isinstance(evenements, list) else [evenements]
            sans_garantie, non_traduits = non_traduits, []
            if evenements and set(evenements) <= set(sans_garantie):
                decision = Decision.NON_COUVERT
                d = d | {"decision": "NON_COUVERT", "aucune": True, "retenues": [], "possibles": [], "non_traduits": [],
                         "exclusions_etablies": [], "accessoires": [], "exploration": None}
                retenues, sans_garantie = [], []
        if non_traduits or sans_garantie:
            # 7.167 : quand le dossier part chez un gestionnaire, dire des garanties traduites qu'elles ne jouent pas
            # n'apporte rien. Restent celles qui s'appliquent ou pourraient s'appliquer.
            retenues = [r for r in retenues if r.get("rattachement") != "hors"]
        return d, decision, retenues, non_traduits, sans_garantie

    def verdict(self, d: dict, faits: dict) -> tuple[Verdict, list[ClauseRetenue]]:
        """De la décision du moteur à la réponse : la phrase, les citations des clauses, les questions à poser et les
        réserves. Rend le verdict et les clauses consultées."""
        d, decision, retenues, non_traduits, sans_garantie = self._perimetre_de_la_reponse(d, faits)
        # Aucune garantie ne s'applique, mais le contrat exclut ce cas en toutes lettres (7.157) : on cite la clause
        # qui l'exclut, plutôt que le texte de garanties sans rapport.
        exclues = (d.get("exclusions_etablies") or []) if d.get("aucune") else []
        motif = phrase_de_la_reponse(d, decision, retenues, exclues, non_traduits, sans_garantie)
        vars_ = [v for v, _ in points_a_preciser(d, prolog.vocabulaire(), faits)]
        demander = list(dict.fromkeys(question(v) for v in vars_))
        exploration = d.get("exploration")
        if exploration:
            demander, motif = questions_explorees(exploration, vars_, motif)
        confiance, motif = confiance_de_la_reponse(decision, retenues, vars_, demander, non_traduits, sans_garantie, motif)

        index = {c.id: c for c in self.clauses}
        conditions = conditions_citees(d, retenues, exclues, index)
        # Le rôle d'une citation est celui de la règle (7.143) : « garantie » pour la seule phrase qui accorde la
        # garantie, pas pour une définition ou une circonstance citée avec elle.
        citations = [Citation(clause_id=c.clause_id, extrait=c.extrait, pages=c.pages,
                              role=c.nature if c.nature == "exclusion" or c.groupe == "garantie" else c.groupe)
                     for c in conditions if c.nature != "limite"]
        consultees = [ClauseRetenue(clause=index[i], score=0.0, raison="règle")
                      for i in dict.fromkeys(c.clause_id for c in conditions) if i in index]
        v = Verdict(decision=decision, justification=motif, citations=citations, conditions=conditions,
                    informations_manquantes=demander, confiance=confiance, mode=f"regles:{self.llm.nom}+prolog",
                    preuve=d.get("preuve", []), raisonnement=arbre_lisible(d.get("preuve", [])))
        return v, consultees


# --- Arbre de preuve, en lignes lisibles --------------------------------------------------------------

MARQUE = {"oui": "[oui]", "non": "[non]", "inconnu": "[ ? ]"}


LIBELLES_DECISION = _LIBELLES_DECISION     # un seul endroit : models.py


def ligne_du_sinistre(numero_: int, r: Resultat) -> str:
    """« 2. Titre : Non couvert. La raison, avec son article. À demander : … » : une ligne par sinistre."""
    v = r.verdict
    reste = v.justification
    for prefixe in ("Couvert. ", "Non couvert. ", "Non couvert : ", "À préciser. "):
        if reste.startswith(prefixe):
            reste = reste[len(prefixe):]
            break
    reste = reste[:1].upper() + reste[1:]
    # Les questions que la raison ne pose pas déjà : la phrase du moteur cite souvent celles qui tranchent.
    a_poser = [q for q in v.informations_manquantes[:2] if q not in reste] if v.decision == Decision.INCERTAIN else []
    demander = " À demander : " + " ; ".join(a_poser) if a_poser else ""
    return f"{numero_}. {r.titre} : {LIBELLES_DECISION[v.decision]}. {reste}{demander}"


def plusieurs_sinistres(ensemble: Resultat, analyses: list[Resultat], en_parallele: bool = False) -> Resultat:
    """La réponse à une déclaration qui contient plusieurs sinistres (7.168) : une ligne par sinistre, chacun avec
    sa décision. La décision d'ensemble n'est ferme que si tous les sinistres reçoivent la même ; sinon « à
    préciser » : il n'y a pas une réponse pour le tout. Les citations sont celles des sinistres, sans doublon.

    La même pour les deux méthodes (7.222) : la lecture des clauses lit ses sinistres en même temps
    (`en_parallele` : l'attente est celle du plus long), la chaîne de règles l'un après l'autre (les temps
    s'additionnent). Les tokens et le coût sont la somme de ceux des sinistres."""
    decisions = {x.verdict.decision for x in analyses}
    decision = decisions.pop() if len(decisions) == 1 else Decision.INCERTAIN
    # Citations, conditions et clauses consultées : celles de chaque sinistre, dans l'ordre, sans doublon.
    citations, conditions, consultees = [], [], []
    vus_c, vus_k, vus_cl = set(), set(), set()
    for x in analyses:
        for c in x.verdict.citations:
            if (c.clause_id, c.extrait) not in vus_c:
                vus_c.add((c.clause_id, c.extrait))
                citations.append(c)
        for k in x.verdict.conditions:
            if (k.clause_id, k.extrait, k.nature) not in vus_k:
                vus_k.add((k.clause_id, k.extrait, k.nature))
                conditions.append(k)
        for cl in x.clauses_consultees:
            if cl.clause.id not in vus_cl:
                vus_cl.add(cl.clause.id)
                consultees.append(cl)
    raisonnement = [ligne for i, x in enumerate(analyses, 1)
                    for ligne in [f"— Sinistre {i} : {x.titre} —", *x.verdict.raisonnement]]
    avertissements = ensemble.verdict.avertissements + [a for x in analyses for a in x.verdict.avertissements]
    v = Verdict(decision=decision, citations=citations, conditions=conditions, informations_manquantes=[],
                confiance=min(x.verdict.confiance for x in analyses), mode=ensemble.verdict.mode,
                justification=f"{len(analyses)} sinistres dans cette déclaration, une réponse pour chacun.\n"
                + "\n".join(ligne_du_sinistre(i, x) for i, x in enumerate(analyses, 1)),
                avertissements=list(dict.fromkeys(avertissements)), raisonnement=raisonnement,
                decision_initiale=decision)
    # Le découpage de la déclaration, puis l'analyse de chaque sinistre : l'un après l'autre, ou en même temps.
    durees = dict(ensemble.durees_ms)
    for x in analyses:
        for k, ms in x.durees_ms.items():
            durees[k] = max(durees.get(k, 0), ms) if en_parallele else durees.get(k, 0) + ms
    tokens: dict[str, int] = {}
    for x in analyses:
        for k, n in (x.tokens or {}).items():
            tokens[k] = tokens.get(k, 0) + n
    couts = [x.cout_usd for x in analyses if x.cout_usd is not None]
    return Resultat(sinistre=ensemble.sinistre, contrat_id=ensemble.contrat_id, methode=ensemble.methode,
                    faits=ensemble.faits, clauses_consultees=consultees, verdict=v, durees_ms=durees, parties=analyses,
                    tokens=tokens, cout_usd=round(sum(couts), 5) if couts else None)


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
        # L'élagage : d'un « ou » vrai on ne montre que les branches vraies, d'un « et » faux que les fausses.
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
                # Une exclusion qui ne joue pas, ou que l'assureur aurait à prouver sans que la déclaration
                # l'évoque, n'est pas détaillée : elle est comptée, en bas de la garantie.
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


def points_a_preciser(d: dict, voc: dict, faits: dict | None = None) -> list[tuple[str, str]]:
    """Ce qu'on dit au client de préciser, variable par variable : (variable, "question" | "reserve"). Le même
    choix pour le texte du verdict et pour l'API (7.114).

    - `question` : sans la réponse, la garantie ne tranche pas ; pour un refus, aussi les questions des garanties
      possibles (une autre pourrait couvrir) ;
    - `reserve` : seulement quand c'est couvert, ce que l'assureur pourra vérifier (une exclusion qu'il aurait à
      prouver). Pour une réponse à préciser ou un refus, une réserve ne change rien : elle n'est pas posée ;
    - jamais une réserve qui vaut pour tous les sinistres (« pour » couvre tous les événements : le déménagement
      non signalé) : elle n'apprend rien sur celui-ci. Si la déclaration la met en jeu, le moteur en fait une
      question (exclusion entamée), et elle est posée ;
    - jamais une réserve hors sujet pour les événements des `faits` (7.124) : « d'où venait l'eau ? » ne se
      demande pas pour un piéton renversé à vélo. C'est la règle de `prolog.filtrer_faits` : la réponse du client
      serait retirée des faits comme hors sujet. Sans événement connu, on ne peut pas juger : la réserve reste ;
    - jamais une réserve sur un fait déjà connu (7.125, 7.128) : la cause de l'eau ne se redemande pas quand la
      déclaration l'a dite, même en gros (« une fuite », qui pourrait être le gel) : redemandée, elle revenait
      après chaque réponse."""
    tous = set(voc.get("evenement", {}).get("valeurs", []))
    faits = faits or {}
    ev = faits.get("evenement") or []
    lus = prolog.evenements_etendus(ev if isinstance(ev, list) else [ev], voc)

    def hors_sujet(v):
        pour = set(voc.get(v, {}).get("pour", [])) & tous
        return bool(lus and pour and not pour & lus)

    def deja_connu(v):
        return faits.get(v) not in (None, "", [])

    retenues, possibles = d.get("retenues", []), d.get("possibles", [])
    points: dict[str, str] = {}
    # L'ordre compte : une variable déjà notée « question » ne redevient pas « réserve » (setdefault).
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
                # Écartées : la réserve qui vaut pour tous les sinistres, la hors sujet, la déjà répondue.
                if not (tous and set(voc.get(v, {}).get("pour", [])) >= tous) and not hors_sujet(v) \
                        and not deja_connu(v):
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
    # « Une seule question tranche » ne cite que des questions qu'on pose : pas une réserve écartée (7.124). Et
    # rien ne reste à trancher quand la réponse est « couvert » : ce sont des réserves, pas des questions (7.128).
    ensemble = [v for v in exploration.get("ensemble") or [] if v in vars_]
    if ensemble and not motif.startswith("Couvert"):
        motif += (" Une seule question tranche : " if len(ensemble) == 1 else " Ces deux questions tranchent : ") \
            + " ; ".join(f"« {question(v)} »" for v in ensemble) + "."
    return list(dict.fromkeys(lignes)), motif


def faits_lisibles(faits: dict) -> Faits:
    """Les faits du moteur (variable → valeur) sous la forme affichée : événements, biens, lieux, et le reste en
    « variable=valeur »."""
    def liste(v):
        x = faits.get(v)
        return [] if x is None else (x if isinstance(x, list) else [x])

    autres = [f"{v}={x}" for v, x in faits.items() if v not in ("evenement", "bien", "lieu")]
    return Faits(evenements=liste("evenement"), biens=liste("bien"), lieux=liste("lieu"), circonstances=autres)
