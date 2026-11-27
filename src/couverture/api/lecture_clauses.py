"""La lecture des clauses, mise en forme pour l'API (DEMARCHE 7.188, branchée en 7.201 ; à part depuis 7.222).

La déclaration est jugée clause par clause par le modèle (`analyse.clauses`), contresignée par la chaîne de règles,
puis mise à la forme commune des réponses (`schemas.Decision`) : la phrase, les citations, les questions (les siennes,
et celles des règles quand elles retiennent la réponse), les rappels du règlement. Plusieurs sinistres : chacun jugé
à part, en même temps, puis réunis comme pour la chaîne de règles (`service.reponse_plusieurs`).
"""

from __future__ import annotations

from typing import Any

from couverture.analyse import chaine, lecture, prolog
from couverture.analyse.jugement import DITE
from couverture.api import service
from couverture.contrat.base import Base
from couverture.models import Citation, Faits, Resultat

ETAPES_CLAUSES = [
    {"cle": "designation", "titre": "Trouver les chapitres du contrat qui concernent ce sinistre"},
    {"cle": "jugement", "titre": "Juger chaque clause du dossier, citation à l'appui"},
    {"cle": "regles", "titre": "Faire contresigner la réponse par les règles traduites"},
    {"cle": "decision", "titre": "Décider : une logique fixe, pas le modèle"},
]

ANNONCE_CLAUSES = ("Chaque clause qui peut jouer est relue et jugée, citation à l'appui : comptez deux à trois "
                   "minutes.")

ROLE_DE_L_EFFET = {"couvre": "garantie", "exclut": "exclusion", "a_verifier": "condition"}


def avec_souscription(sinistre: str, contrat_id: str, souscription: dict | None) -> str:
    """La déclaration, suivie de ce que disent les conditions particulières du client, en mots : la lecture des
    clauses n'a pas de variables, elle lit des phrases (et ses citations s'y vérifient comme dans le reste)."""
    if not souscription:
        return sinistre
    voc = prolog.vocabulaire()
    lignes = [f"{prolog.libelle(v, voc)} : {prolog.libelle(v, voc, x)}" for v, x in souscription.items() if x]
    return sinistre + ("\n\nConditions particulières du client : " + " ; ".join(lignes) + "." if lignes else "")


def sinistres_distincts(pipeline, sinistre: str) -> list[dict]:
    """Les sinistres distincts d'une déclaration, pour la lecture des clauses (7.218) : la même étape que la chaîne de
    règles (7.168), avec le modèle de lecture des faits, et le même garde-fou (chaque phrase retrouvée mot pour mot
    dans la déclaration). [] s'il n'y en a qu'un, si le découpage est coupé (`COUVERTURE_DECOUPAGE=non`) ou s'il
    échoue : la déclaration se juge alors d'un bloc, comme avant."""
    import os

    if os.environ.get("COUVERTURE_DECOUPAGE", "oui").lower() in {"non", "0", "false"}:
        return []
    llm = getattr(pipeline, "llm", None)
    if llm is None:
        return []
    try:
        return lecture.decouper_sinistres(sinistre, llm)
    except Exception:  # noqa: BLE001 - sans découpage, la réponse d'un bloc reste valable
        return []



class SuiviCommun:
    """Le suivi de plusieurs lectures menées en même temps : une étape s'affiche commencée à la première qui y entre,
    finie quand toutes l'ont finie (le détail est celui de la dernière, précédé du nombre de sinistres)."""

    def __init__(self, suivi, n: int, en_tete: str = "") -> None:
        import threading

        self.suivi, self.n, self.en_tete = suivi, n, en_tete
        self.commencees: set[str] = set()
        self.finies: dict[str, int] = {}
        self.verrou = threading.Lock()

    def __call__(self, etape: str, detail: str | None = None) -> None:
        with self.verrou:
            if detail is None:
                if etape not in self.commencees:
                    self.commencees.add(etape)
                    self.suivi(etape)
                return
            self.finies[etape] = self.finies.get(etape, 0) + 1
            if self.finies[etape] == self.n:
                tete = self.en_tete if etape == "designation" else f"{self.n} sinistres"
                self.suivi(etape, f"{tete} — {detail}")


def analyser_clauses(base: Base, pipeline, contrat_id: str, sinistre: str, llm, suivi=None,
                     souscription: dict | None = None, chapitres: list[str] | None = None
                     ) -> tuple[Resultat, dict[str, Any]]:
    """La lecture des clauses d'une déclaration. Si elle raconte plusieurs sinistres (un vol et une fuite), chacun est
    jugé à part, en même temps, avec sa propre contresignature, et reçoit sa ligne (7.218) ; sinon, d'un bloc.

    `chapitres` : ceux de la lecture précédente, quand on relit la déclaration complétée par les réponses du client.
    La désignation n'est pas redemandée ; à plusieurs sinistres, chacun reçoit tous ces chapitres (on ne sait pas lequel
    venait de quel sinistre, et un chapitre de trop coûte des tokens, un chapitre de moins une exclusion oubliée)."""
    parties = sinistres_distincts(pipeline, sinistre)
    if not parties:
        return analyser_clauses_un(base, pipeline, contrat_id, sinistre, llm, suivi=suivi, souscription=souscription,
                                   chapitres=chapitres)
    from concurrent.futures import ThreadPoolExecutor

    suivre = SuiviCommun(suivi or (lambda etape, detail=None: None), len(parties),
                         f"{len(parties)} sinistres dans la déclaration, chacun jugé à part")
    with ThreadPoolExecutor(max_workers=len(parties)) as fil:
        lus = list(fil.map(lambda p: analyser_clauses_un(base, pipeline, contrat_id, p["texte"], llm, suivi=suivre,
                                                         souscription=souscription, chapitres=chapitres), parties))
    return plusieurs_lectures(contrat_id, sinistre, [(p["titre"], r, x) for p, (r, x) in zip(parties, lus)])


def plusieurs_lectures(contrat_id: str, sinistre: str, lus: list[tuple[str, Resultat, dict[str, Any]]]
                       ) -> tuple[Resultat, dict[str, Any]]:
    """Une déclaration à plusieurs sinistres, lue clause par clause : l'ensemble par `chaine.plusieurs_sinistres` et
    la réponse par `service.reponse_plusieurs`, comme pour la chaîne de règles (7.222). Les sinistres sont lus en
    même temps : l'attente est celle du plus long."""
    from couverture.models import Decision as D
    from couverture.models import Verdict

    for titre, r, _ in lus:
        r.titre = titre
    # Les faits du journal : ceux que les règles ont lus pour le premier sinistre ; la réponse n'en montre pas.
    ensemble = Resultat(sinistre=sinistre, contrat_id=contrat_id, methode="clauses", faits=lus[0][1].faits,
                        clauses_consultees=[], verdict=Verdict(decision=D.INCERTAIN, justification="", mode="clauses"))
    r = chaine.plusieurs_sinistres(ensemble, [p for _, p, _ in lus], en_parallele=True)
    sortie = service.reponse_plusieurs(r, lus)
    sortie["faits"], sortie["faits_affiches"] = {}, []
    return r, sortie


def analyser_clauses_un(base: Base, pipeline, contrat_id: str, sinistre: str, llm, suivi=None,
                        souscription: dict | None = None, chapitres: list[str] | None = None
                        ) -> tuple[Resultat, dict[str, Any]]:
    """La déclaration jugée clause par clause ; la chaîne de règles tourne en même temps, pour contresigner un
    « couvert ». Rend le résultat (pour le journal) et la réponse de l'API, au même format que `analyser`.

    Si la chaîne de règles ne répond pas, un « couvert » n'est pas contresigné et devient « incertain » : la
    contresignature est la garde contre un couvert à tort, elle ne se saute pas en silence."""
    import time
    from concurrent.futures import ThreadPoolExecutor

    from couverture.analyse import clauses as lecture_des_clauses
    from couverture.models import Decision as D

    suivre = suivi or (lambda etape, detail=None: None)
    declaration = avec_souscription(sinistre, contrat_id, souscription)
    debut = time.perf_counter()
    temps: dict[str, int] = {}

    def regles() -> tuple[Resultat | None, str]:
        """La chaîne de règles, en silence : elle tourne pendant la lecture, et son étape ne s'affiche qu'au moment de
        contresigner, pour que l'écran raconte l'analyse dans l'ordre (7.202)."""
        t0 = time.perf_counter()
        try:
            r = pipeline.analyser(sinistre, **({"souscription": souscription} if souscription else {}))
        except Exception as e:  # noqa: BLE001 - la contresignature manque, on le dit plus bas
            return None, f"les règles n'ont pas répondu ({str(e)[:80]})"
        temps["regles"] = int((time.perf_counter() - t0) * 1000)
        return r, f"les règles traduites répondent « {DITE[r.verdict.decision]} »"

    def contresigner(en_cours):
        suivre("regles")
        r, detail = en_cours.result()
        suivre("regles", detail)
        return r      # le résultat entier : sa décision, et ses obstacles pour la relecture ciblée (7.211)

    compteur = service.Compteur(llm)
    with ThreadPoolExecutor(max_workers=1) as fil:
        en_cours = fil.submit(regles)
        lu = lecture_des_clauses.lire(base, contrat_id, compteur, declaration, suivi=suivre,
                                      regles=lambda: contresigner(en_cours), chapitres=chapitres)
        r_regles = en_cours.result()[0]
    temps["lecture"] = int((time.perf_counter() - debut) * 1000)
    decision, desaccord = lu.decision, lu.desaccord
    if r_regles is None and decision == D.COUVERT:
        decision, desaccord = D.INCERTAIN, "les règles traduites n'ont pas répondu : un « couvert » non contresigné reste à examiner"
    r, sortie = resultat_clauses(base, contrat_id, sinistre, lu, decision, desaccord, r_regles, temps)
    poser_les_questions_des_regles(pipeline, lu, decision, r_regles, r, sortie)
    citer_le_refus_des_regles(decision, r_regles, r, sortie)
    r.tokens, r.cout_usd = compteur.totaux(), service.cout(compteur.modele, compteur.totaux())
    service.noter_citees(contrat_id, [c["clause_id"] for c in sortie["citations"]] + [x["clause_id"] for x in sortie["limites"]])
    return r, sortie


def poser_les_questions_des_regles(pipeline, lu, decision, r_regles: Resultat | None, r: Resultat,
                                   sortie: dict[str, Any]) -> None:
    """La lecture des clauses tranche, les règles hésitent, la réponse est ramenée à « à préciser » : ce sont les
    questions des règles qui la débloquent, avec leurs réponses proposées (7.222). Sans elles, le client lisait
    « à préciser » sans rien à quoi répondre. La décision ne change pas ; les réponses s'ajoutent à la déclaration,
    que les deux lectures relisent."""
    from couverture.models import Decision as D

    if (r_regles is None or r_regles.parties or decision != D.INCERTAIN or lu.etat.decision == D.INCERTAIN
            or r_regles.verdict.decision != D.INCERTAIN):
        return
    try:
        points = [p for p in service.reponse_complete(pipeline, r_regles)["a_preciser"] if p["nature"] == "question"]
    except Exception:  # noqa: BLE001 - sans le moteur, les phrases des règles suffisent
        points = []
    # Celles qui ont des réponses proposées, puis celles en phrase qu'elles ne disent pas déjà (le lien de causalité).
    textes = [p["question"] for p in points]
    textes += [q for q in r_regles.verdict.informations_manquantes if not any(q.startswith(t) for t in textes)]
    nouvelles = [q for q in textes if q not in sortie["questions"]]
    if not nouvelles:
        return
    sortie["a_preciser"] = points + sortie["a_preciser"]
    sortie["questions"] = nouvelles + sortie["questions"]
    r.verdict.informations_manquantes = nouvelles + list(r.verdict.informations_manquantes)
    ligne = "Questions des règles, posées parce qu'elles retiennent la réponse : " + " ; ".join(nouvelles)
    sortie["raisonnement"].append(ligne)
    r.verdict.raisonnement.append(ligne)


def citer_le_refus_des_regles(decision, r_regles: Resultat | None, r: Resultat, sortie: dict[str, Any]) -> None:
    """La lecture des clauses refuse sans rien citer (« aucune garantie examinée ne couvre ce sinistre ») et les règles
    refusent aussi, en citant leurs clauses : on montre celles-ci (7.222). Une réponse doit dire sur quel article elle
    s'appuie ; la décision ne change pas, et la phrase dit d'où viennent les citations."""
    from couverture.models import Decision as D

    if decision != D.NON_COUVERT or sortie["citations"] or r_regles is None or r_regles.parties:
        return
    if r_regles.verdict.decision != D.NON_COUVERT:
        return
    citees = [c for c in r_regles.verdict.citations if c.valide]
    if not citees:
        return
    sortie["citations"] = [c.model_dump(mode="json") for c in citees]
    sortie["justification"] += " Les règles traduites refusent aussi : les clauses citées sont les leurs."
    r.verdict.citations = list(citees)
    r.verdict.justification = sortie["justification"]
    sortie["raisonnement"].append("Clauses citées : celles des règles traduites, qui refusent aussi ; la lecture des "
                                  "clauses n'en citait aucune")



def phrase_des_clauses(e, decision, desaccord: str, r_regles: Resultat | None, titres: dict[str, str]) -> str:
    """La phrase de la réponse, pour la lecture des clauses : la décision, puis ce qui la fonde, clause par clause,
    avec le motif que le modèle a donné ; et, quand les règles ne contresignent pas, ce qu'elles disent, elles (7.222).
    Avant : « Une garantie couvre, aucune clause examinée n'exclut », qui ne disait ni laquelle, ni pourquoi."""
    from couverture.models import Decision as D

    def ref(j) -> str:
        titre = (titres.get(j.clause_id) or "").strip().removeprefix(j.clause_id).strip(" .:-")
        return f"art. {j.clause_id}" + (f" ({titre[:70]})" if titre and titre != j.clause_id else "")

    def motif(j) -> str:
        m = (j.motif or "").strip().rstrip(".")
        return f" : {m[:220]}" if m else ""

    morceaux = []
    if e.couvrent:
        morceaux.append("La garantie qui s'applique : " + " ; ".join(ref(j) + motif(j) for j in e.couvrent[:2]) + ".")
    if e.excluent:
        morceaux.append("Ce qui l'exclut : " + " ; ".join(ref(j) + motif(j) for j in e.excluent[:2]) + ".")
    if e.a_verifier:
        morceaux.append("Ce qui reste à vérifier : " + " ; ".join(
            ref(j) + (f" — {j.question.strip()}" if j.question.strip() else motif(j)) for j in e.a_verifier[:3]) + ".")
    if not morceaux:
        morceaux.append(e.motif[:1].upper() + e.motif[1:] + ".")
    if desaccord:
        regles = r_regles.verdict if r_regles is not None else None
        dit = regles.justification.strip() if regles is not None else ""
        for prefixe in ("À préciser.", "À préciser :", "Non couvert.", "Non couvert :", "Couvert."):
            dit = dit.removeprefix(prefixe).strip()
        if decision == D.INCERTAIN and e.decision != D.INCERTAIN and len(dit.strip(" .")) > 10:
            # Leur phrase dit laquelle de leurs garanties hésite, et sur quoi : plus parlant que « à examiner ».
            morceaux.append("Les règles traduites du contrat ne contresignent pas : " + dit)
        else:
            morceaux.append(desaccord[:1].upper() + desaccord[1:] + ".")
    return chaine.LIBELLES_DECISION[decision] + ". " + " ".join(morceaux)


def resultat_clauses(base: Base, contrat_id: str, sinistre: str, lu, decision, desaccord: str,
                     r_regles: Resultat | None, temps: dict[str, int]) -> tuple[Resultat, dict[str, Any]]:
    """Une lecture des clauses, mise au format des réponses de l'API. Les faits sont vides : cette méthode ne lit pas
    de variables ; ce qu'elle a retenu de la déclaration est dans les citations et le raisonnement."""
    from couverture.models import Decision as D
    from couverture.models import Verdict

    e = lu.etat
    du_contrat = base.clauses(contrat_id)
    pages = {c.id: c.pages for c in du_contrat}
    titres = {c.id: c.titre for c in du_contrat}
    # Le rôle affiché est celui de la clause dans le contrat, pas l'effet que le modèle lui prête : un préambule ou
    # une garantie qui écarte le sinistre ne s'affiche pas « exclusion » (vu à l'essai, 7.222). L'effet est dit par
    # la phrase (« Ce qui l'exclut : … »).
    types = {c.id: ("clause" if c.type.value == "autre" else c.type.value) for c in du_contrat}
    citations = [Citation(clause_id=j.clause_id, extrait=j.extrait_contrat,
                          role=types.get(j.clause_id) or ROLE_DE_L_EFFET[j.effet],
                          pages=pages.get(j.clause_id, []))
                 for j in [*e.couvrent, *e.excluent, *e.a_verifier] if j.extrait_contrat]
    noms = {"couvre": "couvre", "exclut": "exclut", "limite": "limite", "a_verifier": "à vérifier"}
    raisonnement = [f"Chapitres désignés : {', '.join(lu.designes) or 'aucun'}",
                    f"Garanties examinées : {', '.join(lu.garanties) or 'aucune'} ({len(lu.dossier)} clauses au dossier)"]
    raisonnement += [f"[{noms[j.effet]}] art. {j.clause_id} : « {j.extrait_contrat} »"
                     + (f" ← « {j.extrait_declaration} »" if j.extrait_declaration else "")
                     + (f" — {j.motif}" if j.motif else "")
                     for j in [*e.couvrent, *e.excluent, *e.limitent, *e.a_verifier]]
    if lu.relancees:
        raisonnement.append(f"Clauses redemandées au modèle, faute de jugement : {', '.join(lu.relancees)}")
    if e.questions_retirees:
        raisonnement.append("Questions non posées, leur réponse ne changerait pas la décision : art. "
                            + ", ".join(e.questions_retirees))
    raisonnement += [f"Relecture ciblée — {ligne}" for ligne in lu.arbitrage]
    avertissements = ([desaccord] if desaccord else []) \
        + ([f"clauses attendues sans jugement : {', '.join(e.manquants)}"] if e.manquants else []) \
        + [f"jugement écarté — {d}" for d in e.defauts[:5]]
    # Celles de la décision : une fois chacune (deux clauses peuvent poser la même), et celle d'une option qui
    # couvre seule, qu'aucune clause ne pose (7.208).
    questions = list(e.questions)
    regles = r_regles.verdict.decision if r_regles else None
    # Pas une probabilité : l'accord des deux lectures du contrat (les clauses et les règles), affiché comme tel.
    confiance = 1.0 if regles == e.decision else 0.5
    justification = phrase_des_clauses(e, decision, desaccord, r_regles, titres)
    verdict = Verdict(decision=decision, justification=justification, citations=citations,
                      informations_manquantes=questions, confiance=confiance, mode="clauses",
                      decision_initiale=e.decision, avertissements=avertissements, raisonnement=raisonnement)
    faits = r_regles.faits if r_regles else Faits()      # pour le journal seulement : la réponse n'en montre pas
    r = Resultat(sinistre=sinistre, contrat_id=contrat_id, methode="clauses", faits=faits, clauses_consultees=[],
                 verdict=verdict, durees_ms=temps)
    sortie = {
        "contrat_id": contrat_id, "decision": decision.value, "justification": justification, "confiance": confiance,
        # Les rappels du règlement (délai de déclaration, plafond) : des réserves, qui n'empêchent pas de répondre.
        # Pas sur un refus : un délai de déclaration ne dit rien à qui n'est pas couvert (7.222).
        "a_preciser": [{"variable": f"rappel_{j.clause_id}", "nature": "reserve",
                        "question": f"{j.question or j.extrait_contrat} (art. {j.clause_id})", "valeurs": [],
                        "libelles": {}, "aide": {}} for j in lu.rappels if decision != D.NON_COUVERT],
        "questions": questions,
        "citations": [c.model_dump(mode="json") for c in citations],
        "limites": [{"clause_id": j.clause_id, "extrait": j.extrait_contrat, "montant": j.motif or j.extrait_contrat}
                    for j in e.limitent],
        "faits": {}, "faits_affiches": [], "sinistres": [], "avertissements": avertissements,
        "raisonnement": raisonnement, "mode": "clauses", "durees_ms": temps,
        # Pour relire après les réponses du client sans redemander la désignation (7.218).
        "chapitres": list(lu.designes),
    }
    return r, sortie
