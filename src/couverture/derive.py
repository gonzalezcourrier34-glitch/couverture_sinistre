"""Dérive : la semaine écoulée ressemble-t-elle aux semaines d'avant ?

Même méthode que SortirIA (`agent/drift.py`) : les 7 derniers jours comparés aux 28
précédents, variable par variable, avec le PSI (Population Stability Index) :

    PSI = Σ (part récente − part de référence) × ln(part récente / part de référence)

Repères usuels : moins de 0,1 stable ; de 0,1 à 0,25 dérive modérée ; plus de 0,25 forte.

Ce qu'on surveille, et ce qu'une dérive voudrait dire :
  - les questions : type d'événement, bien, lieu → les sinistres déclarés changent
    (saison, nouveau produit) ; le jeu de test n'est peut-être plus représentatif ;
  - les réponses : décision, confiance → le système répond autrement ; un nouveau
    contrat mal lu, ou un changement du modèle chez le fournisseur ;
  - la fiabilité : contestations de la relecture, citations rejetées → le modèle se
    trompe plus souvent ;
  - par contrat : un taux d'INCERTAIN anormal signale souvent un contrat mal lu.
"""

from __future__ import annotations

import math
from collections import Counter
from datetime import datetime, timedelta, timezone

from .journal import Journal

EPS = 1e-4
MINIMUM = 30   # analyses minimales dans chaque période pour parler de dérive
SEUILS = (0.1, 0.25)

VARIABLES = {
    "evenement": ("questions", lambda r: r["evenement"]),
    "bien": ("questions", lambda r: r["bien"]),
    "lieu": ("questions", lambda r: r["lieu"]),
    "decision": ("reponses", lambda r: r["decision"]),
    "confiance": ("reponses", lambda r: "faible" if r["confiance"] < 0.5 else ("moyenne" if r["confiance"] < 0.8 else "haute")),
    "contestee": ("fiabilite", lambda r: "oui" if (r["contestations"] or 0) > 0 else "non"),
    "citation_rejetee": ("fiabilite", lambda r: "oui" if (r["citations_rejetees"] or 0) + (r["conditions_ecartees"] or 0) > 0 else "non"),
}


def psi(recent: list[str], reference: list[str]) -> float:
    categories = set(recent) | set(reference)
    cr, cf = Counter(recent), Counter(reference)
    total = 0.0
    for c in categories:
        a = max(cr[c] / len(recent), EPS)
        e = max(cf[c] / len(reference), EPS)
        total += (a - e) * math.log(a / e)
    return round(total, 4)


def niveau(valeur: float) -> str:
    return "stable" if valeur < SEUILS[0] else ("modérée" if valeur < SEUILS[1] else "forte")


def parts(valeurs: list[str]) -> dict[str, float]:
    n = len(valeurs) or 1
    return {k: round(v / n, 3) for k, v in Counter(valeurs).most_common()}


def calculer(journal: Journal, maintenant: datetime | None = None, jours: int = 7, reference: int = 28) -> dict:
    maintenant = maintenant or datetime.now(timezone.utc)
    debut_recent = maintenant - timedelta(days=jours)
    debut_ref = debut_recent - timedelta(days=reference)
    recent = [r for r in journal.lignes(debut_recent, maintenant + timedelta(seconds=1)) if not r["erreur"]]
    ref = [r for r in journal.lignes(debut_ref, debut_recent) if not r["erreur"]]
    resultat = {
        "periode": f"{jours} derniers jours contre les {reference} précédents",
        "volumes": {"recent": len(recent), "reference": len(ref)},
        "variables": {},
        "contrats": {},
        "alertes": [],
    }
    if len(recent) < MINIMUM or len(ref) < MINIMUM:
        resultat["statut"] = f"pas assez d'analyses (il en faut {MINIMUM} dans chaque période)"
        return resultat

    for nom, (famille, extraire) in VARIABLES.items():
        a, e = [extraire(r) for r in recent], [extraire(r) for r in ref]
        valeur = psi(a, e)
        resultat["variables"][nom] = {"famille": famille, "psi": valeur, "niveau": niveau(valeur),
                                      "recent": parts(a), "reference": parts(e)}
        if valeur >= SEUILS[1]:
            resultat["alertes"].append(f"Dérive forte sur « {nom} » ({famille}) : PSI {valeur}.")

    # Par contrat : taux d'INCERTAIN récent contre référence (un contrat mal lu se voit ici).
    for contrat in sorted({r["contrat_id"] for r in recent}):
        rc = [r for r in recent if r["contrat_id"] == contrat]
        rf = [r for r in ref if r["contrat_id"] == contrat]
        t = lambda rs: sum(r["decision"] == "INCERTAIN" for r in rs) / len(rs) if rs else None  # noqa: E731
        resultat["contrats"][contrat] = {"analyses": len(rc), "incertain_recent": t(rc), "incertain_reference": t(rf)}
        if len(rc) >= 10 and t(rc) >= 0.6 and (t(rf) is None or t(rc) - t(rf) >= 0.2):
            resultat["alertes"].append(
                f"Contrat {contrat} : {t(rc):.0%} d'INCERTAIN cette période. Contrat mal lu, ou questions nouvelles ?")
    resultat["statut"] = "alerte" if resultat["alertes"] else "stable"
    return resultat
