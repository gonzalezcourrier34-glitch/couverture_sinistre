"""Contrôles automatiques à l'ingestion d'un contrat.

Avec des centaines de contrats, personne ne relit chaque découpage. Ces contrôles
repèrent ceux qui ont mal été lus ; un contrat « A_VERIFIER » n'est pas servi
tant qu'un humain ne l'a pas regardé.
"""

from __future__ import annotations

from collections import Counter

from .models import Clause, TypeClause
from .segmentation import extraire_renvois, resoudre
from .texte import normaliser


def controler(clauses: list[Clause]) -> dict:
    ids = [c.id for c in clauses]
    types = Counter(c.type.value for c in clauses)
    n = len(clauses)

    groupes_garantie = {c.groupe for c in clauses if c.type == TypeClause.GARANTIE}
    groupes_exclusion = {c.groupe for c in clauses if c.type == TypeClause.EXCLUSION}
    exclusions_generales = any(
        c.type == TypeClause.EXCLUSION and "general" in normaliser(" ".join(c.chemin)) for c in clauses
    )
    renvois_casses = sorted(
        {f"{c.id} → {ref}" for c in clauses for ref in extraire_renvois(c.texte) if not resoudre(ref, ids)}
    )

    alertes: list[str] = []
    if n < 15:
        alertes.append(f"Peu de clauses ({n}) : le découpage a probablement échoué.")
    if n and types.get("autre", 0) / n > 0.4:
        alertes.append(f"{types['autre']} clauses sur {n} sans type : titres non reconnus.")
    if not types.get("garantie"):
        alertes.append("Aucune garantie détectée.")
    if not types.get("exclusion"):
        alertes.append("Aucune exclusion détectée : un contrat sans exclusion n'existe pas.")
    if not types.get("definition"):
        alertes.append("Aucune définition détectée (lexique non reconnu ?).")
    if not exclusions_generales:
        alertes.append("Pas d'exclusions générales repérées.")
    if len(renvois_casses) > max(3, 0.05 * n):
        alertes.append(f"{len(renvois_casses)} renvois vers des clauses introuvables.")

    return {
        "statut": "OK" if not alertes else "A_VERIFIER",
        "nb_clauses": n,
        "par_type": dict(types),
        "garanties_sans_exclusion_voisine": sorted(groupes_garantie - groupes_exclusion),
        "renvois_casses": renvois_casses[:20],
        "clauses_tres_longues": [c.id for c in clauses if len(c.texte) > 3000],
        "alertes": alertes,
    }
