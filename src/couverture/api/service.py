"""La logique de l'API, sans FastAPI : ce que les routes appellent et renvoient.

**Provenance** : nouveau module (20/11/2026). Sur le modèle de SortirIA (`app/search_service.py` à côté de
`app/interface_api.py`) : les routes ne font que valider la requête et traduire les erreurs en codes HTTP ; tout
le reste est ici, et se teste sans serveur.

Deux façons d'obtenir une décision :

- **analyse** : la déclaration en français → le modèle lit les faits → le moteur Prolog décide ;
- **décision** : les faits déjà connus (une analyse précédente, plus les réponses du client aux questions) → le
  moteur décide, sans modèle. C'est ainsi qu'un « incertain » se résout : on répond aux questions de
  `a_preciser`, on ajoute les réponses aux `faits` rendus, on redemande.
"""

from __future__ import annotations

import json

from typing import Any

from couverture.analyse import chaine, lecture, prolog
from couverture.contrat.base import Base, Contrat
from couverture.models import Citation, Clause, Faits, Resultat


class SansModele:
    """Le « modèle » d'une décision sur faits : aucun appel n'est fait, seul son nom figure dans le verdict."""

    nom = "aucun"

    def completer(self, systeme: str, message: str) -> str:  # pragma: no cover - jamais appelé
        """Jamais appelée : une décision sur des faits déjà établis n'a rien à faire lire."""
        raise RuntimeError("Une décision sur faits n'appelle pas de modèle.")


def a_des_regles(contrat_id: str) -> bool:
    """Vrai si le contrat a des règles Prolog (`regles/<contrat>.pl`) : seuls ceux-là peuvent décider."""
    return prolog.a_des_garanties(contrat_id)


def contrat_public(c: Contrat) -> dict[str, Any]:
    """Ce que l'API montre d'un contrat (ni le chemin du fichier, ni son empreinte)."""
    return {"id": c.id, "assureur": c.assureur, "produit": c.produit, "version": c.version, "statut": c.statut,
            "nb_clauses": c.rapport.get("nb_clauses"), "alertes": c.rapport.get("alertes", []),
            "regles": a_des_regles(c.id), "souscription": souscription_publique(c.id)} | traduction(c.id)


def traduction(contrat_id: str) -> dict[str, Any]:
    """Ces conditions générales sont-elles traduites en règles en entier ? (7.169) Lu dans `regles/traduction.json`,
    tenu à la main : `complet` (faux tant que rien n'est déclaré) et `traduction`, ce qui est traduit et ce qui reste."""
    try:
        d = json.loads((prolog.DOSSIER / "traduction.json").read_text(encoding="utf-8")).get(contrat_id) or {}
    except (OSError, ValueError):
        d = {}
    return {"complet": bool(d.get("complet")), "traduction": str(d.get("detail") or "")}


def souscription_publique(contrat_id: str) -> list[dict[str, Any]]:
    """Ce que les conditions particulières peuvent préciser pour ce contrat : la formule, les options (7.141)."""
    voc = prolog.vocabulaire()
    return [{"variable": v, "libelle": prolog.libelle(v, voc), "question": d.get("question", ""),
             "valeurs": d["valeurs"], "libelles": {x: prolog.libelle(v, voc, x) for x in d["valeurs"]}}
            for v, d in prolog.souscription(contrat_id, voc).items()]


def clause_publique(c: Clause) -> dict[str, Any]:
    """Une clause telle que l'API la renvoie."""
    return {"id": c.id, "article": c.article, "titre": c.titre, "chemin": c.chemin, "type": c.type.value,
            "texte": c.texte, "pages": c.pages, "renvois": c.renvois}


def faits_depuis(faits: Faits) -> dict[str, Any]:
    """Les faits lus, sous la forme que `decider` accepte : {variable: valeur}, des listes pour le socle."""
    sortie: dict[str, Any] = {}
    if faits.evenements:
        sortie["evenement"] = list(faits.evenements)
    if faits.biens:
        sortie["bien"] = list(faits.biens)
    if faits.lieux:
        sortie["lieu"] = list(faits.lieux)
    for c in faits.circonstances:
        variable, _, valeur = c.partition("=")
        if variable and valeur:
            sortie[variable] = valeur
    return sortie


def a_preciser(d: dict, voc: dict | None = None, faits: dict | None = None,
               contrat_id: str | None = None) -> list[dict[str, Any]]:
    """Ce qu'il faut demander au client, variable par variable, avec les valeurs possibles.

    `question` : sans la réponse, la garantie ne tranche pas (la décision est « incertain ») ; `reserve` : la
    garantie couvre, sous réserve de ce point (une exclusion que l'assureur aurait à prouver). Le choix est celui
    de `chaine.points_a_preciser`, le même que pour les questions du verdict. Seules les variables du vocabulaire
    y figurent : une question sans réponses possibles (le lien de causalité, une appréciation) ne se répond pas par
    un bouton, et `/decisions` l'ignorerait ; elle reste dans `questions`, en phrase (7.125)."""
    voc = voc if voc is not None else prolog.vocabulaire()
    return [{"variable": v, "nature": n, "question": voc.get(v, {}).get("question", f"Préciser : {v}"),
             "valeurs": (valeurs := valeurs_proposees(v, voc, faits or {}, contrat_id)),
             "libelles": {x: prolog.libelle(v, voc, x) for x in valeurs}, "aide": voc.get(v, {}).get("aide", {})}
            for v, n in chaine.points_a_preciser(d, voc, faits) if v in voc]


def valeurs_proposees(variable: str, voc: dict, faits: dict, contrat_id: str | None = None) -> list[str]:
    """Les réponses possibles à une question. Si le fait est déjà connu en gros (« une fuite »), seules ses
    précisions sont proposées (« le gel ») : reproposer la valeur déjà connue ramenait la même question (7.128)."""
    d = voc.get(variable, {})
    # Les valeurs du contrat, quand la variable les déclare : les formules de B ne sont pas celles de D (7.141).
    valeurs = list(prolog.vocabulaire_du_contrat(contrat_id, {variable: d})[variable].get("valeurs", [])) if d else []
    connu = faits.get(variable)
    connues = set(connu if isinstance(connu, list) else [connu]) if connu not in (None, "", []) else set()
    if not connues:
        return valeurs
    parents = voc.get(variable, {}).get("parents", {})
    precisions = [x for x in valeurs if x not in connues and connues & set(parents.get(x, []))]
    return precisions or [x for x in valeurs if x not in connues]


def reponse(r: Resultat, d: dict | None = None) -> dict[str, Any]:
    """La réponse de l'API pour une décision : courte en tête, traçable en dessous."""
    v = r.verdict
    return {
        "contrat_id": r.contrat_id,
        "decision": v.decision.value,
        "justification": v.justification,
        "confiance": v.confiance,
        "a_preciser": a_preciser(d, faits=faits_depuis(r.faits), contrat_id=r.contrat_id) if d else [],
        "questions": v.informations_manquantes,
        "citations": [c.model_dump(mode="json") for c in v.citations if c.valide],
        "limites": [{"clause_id": c.clause_id, "extrait": c.extrait, "montant": c.enonce}
                    for c in v.conditions if c.nature == "limite"],
        "faits": faits_depuis(r.faits),
        "faits_affiches": prolog.faits_affiches(faits_depuis(r.faits)),
        "sinistres": [],
        "chapitres": [],                         # la lecture des clauses seulement (7.218) : même forme partout
        "avertissements": v.avertissements,
        "raisonnement": v.raisonnement,
        "mode": v.mode,
        "durees_ms": r.durees_ms,
    }


NON_CONFIRME = " : fait décisif non confirmé par la déclaration"


def analyser(pipeline, sinistre: str, suivi=None, souscription: dict | None = None) -> tuple[Resultat, dict[str, Any]]:
    """La déclaration lue par le modèle, la décision du moteur. Rend le résultat complet (pour le journal) et
    la réponse de l'API.

    Les variables à préciser viennent d'une seconde décision du moteur, sans modèle, sur les faits retenus. Un
    fait décisif que la confirmation n'a pas retrouvé dans la déclaration (7.49) est retiré des faits rendus et
    devient la première question : renvoyés tels quels à `/decisions`, les faits ne doivent pas redonner la
    réponse que la confirmation a suspendue."""
    options = ({"suivi": suivi} if suivi is not None else {}) | ({"souscription": souscription} if souscription else {})
    r = pipeline.analyser(sinistre, **options)
    if r.parties:
        # Plusieurs sinistres (7.168) : une réponse par sinistre. Rien n'est à demander pour l'ensemble : les
        # questions appartiennent à chaque sinistre, et se lisent dans sa ligne et dans `sinistres`.
        sortie = reponse(r, None)
        sortie["sinistres"] = [reponse_complete(pipeline, p) | {"titre": p.titre, "declaration": p.sinistre}
                               for p in r.parties]
        return r, sortie
    return r, reponse_complete(pipeline, r)


def reponse_complete(pipeline, r: Resultat) -> dict[str, Any]:
    """La réponse de l'API pour un résultat : ses questions classées par le moteur, ses faits à renvoyer."""
    faits = faits_depuis(r.faits)
    doutes = [a.removesuffix(NON_CONFIRME) for a in r.verdict.avertissements if a.endswith(NON_CONFIRME)]
    for v in doutes:
        faits.pop(v, None)
    d = pipeline.decideur(faits) if faits.get("evenement") else None
    if d is not None and doutes:
        d = d | {"retenues": [{"questions": doutes}] + d.get("retenues", [])}
    sortie = reponse(r, d)
    if d is None:
        # Aucun événement lu (7.142) : la seule question utile est « que s'est-il passé ? », avec ses réponses.
        voc = prolog.vocabulaire()
        sortie["a_preciser"] = [{"variable": "evenement", "nature": "question", "question": voc["evenement"]["question"],
                                 "valeurs": list(voc["evenement"]["valeurs"]),
                                 "libelles": {x: prolog.libelle("evenement", voc, x) for x in voc["evenement"]["valeurs"]},
                                 "aide": voc["evenement"].get("aide", {})}]
    sortie["faits"] = faits
    sortie["faits_affiches"] = prolog.faits_affiches(faits)
    return sortie


def decider(base: Base, contrat_id: str, faits: dict[str, Any], decideur=None) -> tuple[Resultat, dict[str, Any]]:
    """Les faits donnés par le client → la décision du moteur, sans modèle.

    Les faits sont ramenés au vocabulaire comme ceux que le modèle lit (variables ou valeurs inconnues
    retirées et signalées, valeurs vagues précisées, faits impliqués ajoutés). `KeyError` si le contrat est
    inconnu, `LookupError` s'il n'a pas de règles."""
    base.contrat(contrat_id)                      # KeyError si le contrat est inconnu
    clauses = base.clauses(contrat_id)
    if not a_des_regles(contrat_id):
        raise LookupError(f"Pas de règles pour {contrat_id} : seule l'analyse documentaire est possible.")
    voc = prolog.vocabulaire()
    # Les conditions particulières (la formule, une option) ne sont pas jugées « hors sujet » d'après l'événement,
    # comme le serait un fait lu : c'est aux règles de dire si elles servent (7.141).
    souscrits, ecarts_souscription = prolog.retenir_souscription(
        contrat_id, {v: x for v, x in faits.items() if v in prolog.souscription(contrat_id, voc) and isinstance(x, str)}, voc)
    retenus, ecarts = lecture.au_vocabulaire({v: x for v, x in faits.items() if v not in souscrits}, voc)
    retenus, ecarts = retenus | souscrits, ecarts + ecarts_souscription
    decideur = decideur or (lambda f: prolog.decider(contrat_id, f))
    d = decideur(retenus)
    p = chaine.PipelineRegles(contrat_id, clauses, SansModele(), decideur=decideur)
    verdict, consultees = p.verdict(d, retenus)
    verdict.avertissements = ecarts + verdict.avertissements
    verdict = p.valider(verdict, consultees)
    r = Resultat(sinistre="", contrat_id=contrat_id, methode="regles", faits=chaine.faits_lisibles(retenus),
                 clauses_consultees=consultees, verdict=verdict)
    return r, reponse(r, d)


# # La lecture des clauses (DEMARCHE 7.188, branchée en 7.201)

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


# # Les clauses consultables en ligne (7.219)
#
# En ligne, l'article entier et la fiche ne servent que des clauses qu'une réponse peut citer, pour que le contrat ne
# se télécharge pas clause par clause (7.161). Pour la chaîne de règles, ce sont celles que ses règles citent, connues
# d'avance. La lecture des clauses peut citer n'importe quelle clause du dossier : on retient celles qu'elle a
# effectivement citées dans une réponse rendue. En mémoire : un redémarrage les oublie, et une ancienne réponse se
# relit alors par une nouvelle analyse.

_CITEES_PAR_LA_LECTURE: dict[str, set[str]] = {}


def noter_citees(contrat_id: str, ids) -> None:
    """Retient les clauses qu'une réponse de la lecture des clauses vient de citer."""
    _CITEES_PAR_LA_LECTURE.setdefault(contrat_id, set()).update(i for i in ids if i)


def clauses_consultables(contrat_id: str) -> set[str]:
    """Les clauses qu'une réponse cite ou a citées : celles des règles, et celles des lectures des clauses rendues."""
    return prolog.clauses_citees(contrat_id) | _CITEES_PAR_LA_LECTURE.get(contrat_id, set())


# # Les tokens de la lecture des clauses (7.219)

# Tarif vérifié le 25 nov. 2026 (docs.mistral.ai), en dollars par million de tokens : envoyés, repris du cache, reçus.
TARIFS = {"mistral-large": (1.36, 0.14, 4.18), "mistral-medium": (1.50, 0.15, 7.50), "mistral-small": (0.15, 0.015, 0.60)}


def cout(modele: str, tokens: dict[str, int]) -> float | None:
    """Le coût estimé d'une analyse, en dollars, d'après le tarif du modèle ; None pour un modèle sans tarif connu."""
    tarif = next((t for nom, t in TARIFS.items() if nom in (modele or "")), None)
    if tarif is None or not tokens:
        return None
    envoyes, cache, recus = tokens.get("envoyes", 0), tokens.get("cache", 0), tokens.get("recus", 0)
    return round(((envoyes - cache) * tarif[0] + cache * tarif[1] + recus * tarif[2]) / 1e6, 5)


class Compteur:
    """Le modèle de la lecture des clauses, plus le compte de ses tokens. Une copie du client par compteur : à
    plusieurs sinistres, les lectures vont en même temps, et chaque client garde l'usage de son dernier appel."""

    def __init__(self, llm) -> None:
        import copy

        self.llm = copy.copy(llm)
        self.accepte_schema = getattr(llm, "accepte_schema", False)
        self.modele = getattr(llm, "modele", "")
        self.envoyes = self.recus = self.cache = 0

    def completer(self, systeme: str, message: str, **options) -> str:
        texte = self.llm.completer(systeme, message, **options)
        usage = getattr(self.llm, "dernier_usage", None) or {}
        self.envoyes += usage.get("prompt_tokens") or 0
        self.recus += usage.get("completion_tokens") or 0
        self.cache += (usage.get("prompt_tokens_details") or {}).get("cached_tokens") or 0
        return texte

    def totaux(self) -> dict[str, int]:
        return {"envoyes": self.envoyes, "recus": self.recus, "cache": self.cache}


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
    """Une déclaration à plusieurs sinistres, lue clause par clause : une ligne par sinistre, comme pour la chaîne de
    règles (`chaine.plusieurs_sinistres`). La décision d'ensemble n'est ferme que si tous reçoivent la même. Les
    questions et les réserves sont celles de chaque sinistre, précédées de son titre."""
    from couverture.models import Decision as D
    from couverture.models import Verdict

    for titre, r, _ in lus:
        r.titre = titre
    decisions = {x["decision"] for _, _, x in lus}
    decision = D(decisions.pop()) if len(decisions) == 1 else D.INCERTAIN
    lignes = []
    for i, (titre, _, x) in enumerate(lus, 1):
        libelle = chaine.LIBELLES_DECISION[D(x["decision"])]
        lignes.append(f"{i}. {titre} : {libelle}. {x['justification']}")
    justification = f"{len(lus)} sinistres dans cette déclaration, une réponse pour chacun.\n" + "\n".join(lignes)

    def unique(elements: list) -> list:
        vus, sortie = set(), []
        for e in elements:
            cle = json.dumps(e, sort_keys=True, ensure_ascii=False)
            if cle not in vus:
                vus.add(cle)
                sortie.append(e)
        return sortie

    questions = [f"{titre} — {q}" for titre, _, x in lus for q in x["questions"]]
    a_preciser = unique([p | {"question": f"{titre} — {p['question']}", "variable": f"{p['variable']}_{i}"}
                         for i, (titre, _, x) in enumerate(lus, 1) for p in x["a_preciser"]])
    raisonnement = [ligne for i, (titre, _, x) in enumerate(lus, 1)
                    for ligne in [f"— Sinistre {i} : {titre} —", *x["raisonnement"]]]
    avertissements = list(dict.fromkeys(a for _, _, x in lus for a in x["avertissements"]))
    confiance = min(x["confiance"] for _, _, x in lus)
    durees: dict[str, int] = {}
    for _, _, x in lus:
        for k, ms in x["durees_ms"].items():
            durees[k] = max(durees.get(k, 0), ms)          # menés en même temps : le plus long fait l'attente
    citations = [c for _, r, _ in lus for c in r.verdict.citations]
    verdict = Verdict(decision=decision, justification=justification, citations=citations,
                      informations_manquantes=questions, confiance=confiance, mode="clauses",
                      decision_initiale=decision, avertissements=avertissements, raisonnement=raisonnement)
    tokens = {k: sum(r.tokens.get(k, 0) for _, r, _ in lus) for k in ("envoyes", "recus", "cache")}
    r = Resultat(sinistre=sinistre, contrat_id=contrat_id, methode="clauses", faits=lus[0][1].faits,
                 clauses_consultees=[], verdict=verdict, durees_ms=durees, parties=[r for _, r, _ in lus],
                 tokens=tokens, cout_usd=round(sum(r.cout_usd or 0 for _, r, _ in lus), 5)
                 if any(r.cout_usd is not None for _, r, _ in lus) else None)
    sortie = {
        "contrat_id": contrat_id, "decision": decision.value, "justification": justification, "confiance": confiance,
        "a_preciser": a_preciser, "questions": questions,
        "citations": unique([c for _, _, x in lus for c in x["citations"]]),
        "limites": unique([lim for _, _, x in lus for lim in x["limites"]]),
        "faits": {}, "faits_affiches": [],
        "sinistres": [x | {"titre": titre, "declaration": r.sinistre} for titre, r, x in lus],
        "avertissements": avertissements, "raisonnement": raisonnement, "mode": "clauses", "durees_ms": durees,
        "chapitres": list(dict.fromkeys(c for _, _, x in lus for c in x.get("chapitres", []))),
    }
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
        return r, f"les règles traduites répondent « {r.verdict.decision.value} »"

    def contresigner(en_cours):
        suivre("regles")
        r, detail = en_cours.result()
        suivre("regles", detail)
        return r      # le résultat entier : sa décision, et ses obstacles pour la relecture ciblée (7.211)

    compteur = Compteur(llm)
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
    r.tokens, r.cout_usd = compteur.totaux(), cout(compteur.modele, compteur.totaux())
    noter_citees(contrat_id, [c["clause_id"] for c in sortie["citations"]] + [x["clause_id"] for x in sortie["limites"]])
    return r, sortie


def resultat_clauses(base: Base, contrat_id: str, sinistre: str, lu, decision, desaccord: str,
                     r_regles: Resultat | None, temps: dict[str, int]) -> tuple[Resultat, dict[str, Any]]:
    """Une lecture des clauses, mise au format des réponses de l'API. Les faits sont vides : cette méthode ne lit pas
    de variables ; ce qu'elle a retenu de la déclaration est dans les citations et le raisonnement."""
    from couverture.models import Verdict

    e = lu.etat
    pages = {c.id: c.pages for c in base.clauses(contrat_id)}
    citations = [Citation(clause_id=j.clause_id, extrait=j.extrait_contrat, role=ROLE_DE_L_EFFET[j.effet],
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
    justification = e.motif[:1].upper() + e.motif[1:] + "."
    if decision != e.decision:
        justification += f" Réponse ramenée à « {decision.value} » : {desaccord}."
    verdict = Verdict(decision=decision, justification=justification, citations=citations,
                      informations_manquantes=questions, confiance=confiance, mode="clauses",
                      decision_initiale=e.decision, avertissements=avertissements, raisonnement=raisonnement)
    faits = r_regles.faits if r_regles else Faits()      # pour le journal seulement : la réponse n'en montre pas
    r = Resultat(sinistre=sinistre, contrat_id=contrat_id, methode="clauses", faits=faits, clauses_consultees=[],
                 verdict=verdict, durees_ms=temps)
    sortie = {
        "contrat_id": contrat_id, "decision": decision.value, "justification": justification, "confiance": confiance,
        # Les rappels du règlement (délai de déclaration, plafond) : des réserves, qui n'empêchent pas de répondre.
        "a_preciser": [{"variable": f"rappel_{j.clause_id}", "nature": "reserve",
                        "question": f"{j.question or j.extrait_contrat} (art. {j.clause_id})", "valeurs": [],
                        "libelles": {}, "aide": {}} for j in lu.rappels],
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
