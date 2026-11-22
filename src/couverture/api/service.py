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

from typing import Any

from couverture import chaine, lecture, prolog
from couverture.base import Base, Contrat
from couverture.models import Clause, Faits, Resultat
from couverture.validation import valider


class SansModele:
    """Le « modèle » d'une décision sur faits : aucun appel n'est fait, seul son nom figure dans le verdict."""

    nom = "aucun"

    def completer(self, systeme: str, message: str) -> str:  # pragma: no cover - jamais appelé
        raise RuntimeError("Une décision sur faits n'appelle pas de modèle.")


def a_des_regles(contrat_id: str) -> bool:
    """Vrai si le contrat a des règles Prolog (`regles/<contrat>.pl`) : seuls ceux-là peuvent décider."""
    return prolog.fichier_regles(contrat_id).exists()


def contrat_public(c: Contrat) -> dict[str, Any]:
    """Ce que l'API montre d'un contrat (ni le chemin du fichier, ni son empreinte)."""
    return {"id": c.id, "assureur": c.assureur, "produit": c.produit, "version": c.version, "statut": c.statut,
            "nb_clauses": c.rapport.get("nb_clauses"), "alertes": c.rapport.get("alertes", []),
            "regles": a_des_regles(c.id)}


def clause_publique(c: Clause) -> dict[str, Any]:
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


def a_preciser(d: dict, voc: dict | None = None, faits: dict | None = None) -> list[dict[str, Any]]:
    """Ce qu'il faut demander au client, variable par variable, avec les valeurs possibles.

    `question` : sans la réponse, la garantie ne tranche pas (la décision est « incertain ») ; `reserve` : la
    garantie couvre, sous réserve de ce point (une exclusion que l'assureur aurait à prouver). Le choix est celui
    de `chaine.points_a_preciser`, le même que pour les questions du verdict. Seules les variables du vocabulaire
    y figurent : une question sans réponses possibles (le lien de causalité, une appréciation) ne se répond pas par
    un bouton, et `/decisions` l'ignorerait ; elle reste dans `questions`, en phrase (7.125)."""
    voc = voc if voc is not None else prolog.vocabulaire()
    return [{"variable": v, "nature": n, "question": voc.get(v, {}).get("question", f"Préciser : {v}"),
             "valeurs": valeurs_proposees(v, voc, faits or {}), "aide": voc.get(v, {}).get("aide", {})}
            for v, n in chaine.points_a_preciser(d, voc, faits) if v in voc]


def valeurs_proposees(variable: str, voc: dict, faits: dict) -> list[str]:
    """Les réponses possibles à une question. Si le fait est déjà connu en gros (« une fuite »), seules ses
    précisions sont proposées (« le gel ») : reproposer la valeur déjà connue ramenait la même question (7.128)."""
    valeurs = list(voc.get(variable, {}).get("valeurs", []))
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
        "a_preciser": a_preciser(d, faits=faits_depuis(r.faits)) if d else [],
        "questions": v.informations_manquantes,
        "citations": [c.model_dump(mode="json") for c in v.citations if c.valide],
        "limites": [{"clause_id": c.clause_id, "extrait": c.extrait, "montant": c.enonce}
                    for c in v.conditions if c.nature == "limite"],
        "faits": faits_depuis(r.faits),
        "avertissements": v.avertissements,
        "raisonnement": v.raisonnement,
        "mode": v.mode,
        "durees_ms": r.durees_ms,
    }


NON_CONFIRME = " : fait décisif non confirmé par la déclaration"


def analyser(pipeline, sinistre: str, suivi=None) -> tuple[Resultat, dict[str, Any]]:
    """La déclaration lue par le modèle, la décision du moteur. Rend le résultat complet (pour le journal) et
    la réponse de l'API.

    Les variables à préciser viennent d'une seconde décision du moteur, sans modèle, sur les faits retenus. Un
    fait décisif que la confirmation n'a pas retrouvé dans la déclaration (7.49) est retiré des faits rendus et
    devient la première question : renvoyés tels quels à `/decisions`, les faits ne doivent pas redonner la
    réponse que la confirmation a suspendue."""
    r = pipeline.analyser(sinistre, suivi=suivi) if suivi is not None else pipeline.analyser(sinistre)
    faits = faits_depuis(r.faits)
    doutes = [a.removesuffix(NON_CONFIRME) for a in r.verdict.avertissements if a.endswith(NON_CONFIRME)]
    for v in doutes:
        faits.pop(v, None)
    d = pipeline.decideur(faits) if faits.get("evenement") else None
    if d is not None and doutes:
        d = d | {"retenues": [{"questions": doutes}] + d.get("retenues", [])}
    sortie = reponse(r, d)
    sortie["faits"] = faits
    return r, sortie


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
    retenus, ecarts = lecture.au_vocabulaire(faits, voc)
    decideur = decideur or (lambda f: prolog.decider(contrat_id, f))
    d = decideur(retenus)
    p = chaine.PipelineRegles(contrat_id, clauses, SansModele(), decideur=decideur)
    verdict, consultees = p.verdict(d, retenus)
    verdict.avertissements = ecarts + verdict.avertissements
    verdict = valider(verdict, consultees)
    r = Resultat(sinistre="", contrat_id=contrat_id, methode="regles", faits=chaine.faits_lisibles(retenus),
                 clauses_consultees=consultees, verdict=verdict)
    return r, reponse(r, d)
