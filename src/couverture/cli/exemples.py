"""`couverture exemples` : la banque d'exemples de lecture et le partage mise au point / test."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from .. import exemples
from ..base import Base


def ajouter(sous) -> None:
    p = sous.add_parser("exemples", help="La banque d'exemples de lecture et le partage mise au point / test")
    p.add_argument("--partager", action="store_true", help="Figer le partage des cas (les cas déjà partagés ne bougent pas)")
    p.add_argument("--indexer", action="store_true", help="Calculer les vecteurs des exemples (mistral-embed), dans la base")
    p.add_argument("--proches", metavar="TEXTE", help="Les exemples les plus proches d'une déclaration, avec leur score")
    p.add_argument("--evenement", help="Avec --proches : les seuls exemples de cet événement")
    p.add_argument("-k", type=int, default=4)
    p.add_argument("--seuil", type=float, default=None, help="Avec --proches : score minimal (défaut : exemples.SEUIL)")
    p.set_defaults(executer=executer)


def executer(a, base: Base, donnees: Path) -> int:
    """La banque d'exemples (7.107) : partage, vecteurs, et les plus proches d'une déclaration."""
    a_partager, a_indexer, texte, evenement, k, seuil = a.partager, a.indexer, a.proches, a.evenement, a.k, a.seuil

    if a_partager:
        p = exemples.partager(donnees)
        print(f"Partage figé : {len(p['mise_au_point'])} cas de mise au point, {len(p['test'])} de test "
              f"({exemples.chemin_partage(donnees)}).")
    if a_indexer or texte:
        if not os.environ.get("MISTRAL_API_KEY"):
            sys.exit("Les vecteurs demandent mistral-embed : définir MISTRAL_API_KEY dans .env.")
        embed = exemples.EmbeddingsMistral()
    if a_indexer:
        n = exemples.indexer(base.chemin, donnees, embed)
        print(f"Banque : {n['exemples']} exemples, {n['calcules']} vecteur(s) calculé(s), {n['retires']} retiré(s).")
    if texte:
        options = {"k": k, "evenement": evenement} | ({"seuil": seuil} if seuil is not None else {})
        choisis = exemples.proches(texte, base.chemin, embed, **options)
        if not choisis:
            print("Aucun exemple au-dessus du seuil : on n'en enverrait aucun.")
        for x, score in choisis:
            print(f"{score:.3f}  {x['id']:<10} {', '.join(x['evenements']):<20} {x['declaration'][:90]}")
    if not (a_partager or a_indexer or texte):
        p = exemples.charger_partage(donnees)
        b = exemples.banque(donnees)
        print(f"Partage : {len(p['mise_au_point'])} cas de mise au point, {len(p['test'])} de test ; "
              f"banque : {len(b)} exemples ; indexés : {len(exemples.charger_index(base.chemin))}.")
    return 0
