"""La logique de l'API, sans FastAPI : ce que les routes appellent et renvoient.

**Provenance** : nouveau module (20/11/2026). Sur le modèle de SortirIA (`app/search_service.py` à côté de
`app/interface_api.py`) : les routes ne font que valider la requête et traduire les erreurs en codes HTTP ; tout
le reste est ici, et se teste sans serveur. La mise en forme de la lecture des clauses est à part, dans
`lecture_clauses.py` ; ce qui sert aux deux méthodes reste ici (la réponse à plusieurs sinistres, les clauses
consultables en ligne, le compte des tokens).

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
from couverture.models import Clause, Faits, Resultat


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
        "lecture": "",                           # idem (13.4)
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
        return r, reponse_plusieurs(r, [(p.titre, p, reponse_complete(pipeline, p)) for p in r.parties])
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


def rassembler(lignes: list[tuple[str, dict[str, Any]]]) -> tuple[list[dict[str, Any]], list[str]]:
    """Les questions et les réserves d'une déclaration à plusieurs sinistres, pour les deux méthodes (7.222).

    Chaque sinistre garde les siennes, dans sa ligne de `sinistres`. Pour l'ensemble : les questions de chacun,
    précédées de son titre (on y répond d'un bloc) ; une réserve que plusieurs sinistres partagent (le même rappel
    du règlement) une seule fois, et retirée de leurs lignes ; aucune réserve sur un sinistre refusé. Modifie les
    lignes en place ; rend `a_preciser` et `questions` pour l'ensemble.

    Seul un sinistre « à préciser » a des questions : la chaîne de règles met aussi ses réserves dans
    `informations_manquantes`, et l'écran les demandait au client pour des sinistres déjà couverts (vu à l'essai du
    28 nov., 7.232). Une réserve reste une réserve, dans sa ligne."""
    reserves = {i: [p["question"] for p in x["a_preciser"] if p["nature"] == "reserve"]
                for i, (_, x) in enumerate(lignes)}
    for _, x in lignes:
        if x["decision"] == "NON_COUVERT":
            x["a_preciser"] = [p for p in x["a_preciser"] if p["nature"] != "reserve"]
    compte: dict[str, int] = {}
    for _, x in lignes:
        for v in {p["variable"] for p in x["a_preciser"] if p["nature"] == "reserve"}:
            compte[v] = compte.get(v, 0) + 1
    communes: dict[str, dict[str, Any]] = {}
    for _, x in lignes:
        for p in x["a_preciser"]:
            if p["nature"] == "reserve" and compte[p["variable"]] > 1:
                garde = communes.get(p["variable"])
                if garde is None or len(p["question"]) < len(garde["question"]):
                    communes[p["variable"]] = p        # la plus courte : la moins attachée à l'un des sinistres
        x["a_preciser"] = [p for p in x["a_preciser"] if p["nature"] != "reserve" or compte[p["variable"]] == 1]
    # Pour l'ensemble : les questions de chacun, et les seules réserves partagées ; les autres restent dans leur
    # ligne (vu à l'essai : une réserve propre à un sinistre s'affichait aussi « pour toute la déclaration »).
    a_preciser = [p | {"question": f"{titre} — {p['question']}", "variable": f"{p['variable']}_{i}"}
                  for i, (titre, x) in enumerate(lignes, 1) if x["decision"] == "INCERTAIN"
                  for p in x["a_preciser"] if p["nature"] == "question"]
    a_preciser += list(communes.values())
    questions = [f"{titre} — {q}" for i, (titre, x) in enumerate(lignes) if x["decision"] == "INCERTAIN"
                 for q in x["questions"] if not any(q.startswith(r) for r in reserves[i])]
    return a_preciser, questions


def reponse_plusieurs(r: Resultat, lignes: list[tuple[str, Resultat, dict[str, Any]]]) -> dict[str, Any]:
    """La réponse de l'API pour une déclaration à plusieurs sinistres, la même pour les deux méthodes (7.222).

    `r` : la réponse d'ensemble (`chaine.plusieurs_sinistres`, que les deux méthodes appellent) ; `lignes` : pour
    chaque sinistre, son titre, son résultat et sa réponse de l'API. Chacun garde sa réponse complète dans
    `sinistres` ; pour l'ensemble, ses questions précédées de son titre et les réserves partagées (`rassembler`), ses
    limites et, pour la lecture des clauses, ses chapitres. Les questions de l'ensemble vont aussi au journal."""
    sortie = reponse(r, None)
    sortie["sinistres"] = [x | {"titre": titre, "declaration": p.sinistre} for titre, p, x in lignes]
    sortie["a_preciser"], sortie["questions"] = rassembler([(x["titre"], x) for x in sortie["sinistres"]])
    vues: set[str] = set()
    sortie["limites"] = [lim for x in sortie["sinistres"] for lim in x["limites"]
                         if not ((cle := json.dumps(lim, sort_keys=True, ensure_ascii=False)) in vues or vues.add(cle))]
    sortie["chapitres"] = list(dict.fromkeys(c for x in sortie["sinistres"] for c in x.get("chapitres", [])))
    r.verdict.informations_manquantes = list(sortie["questions"])
    return sortie
