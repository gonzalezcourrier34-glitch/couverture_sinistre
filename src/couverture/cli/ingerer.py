"""`couverture ingerer` : lit les contrats et remplit la base."""

from __future__ import annotations

from pathlib import Path

from ..base import Base
from ..ingestion import fichiers_contrats, ingerer_dossier
from ..progression import Barre


def ajouter(sous) -> None:
    p = sous.add_parser("ingerer", help="Lire les contrats de <donnees>/contrats et remplir la base")
    p.add_argument("--forcer", action="store_true", help="Relire même les fichiers inchangés")
    p.set_defaults(executer=executer)


def executer(a, base: Base, donnees: Path) -> int:
    """Lit les contrats de <donnees>/contrats et remplit la base."""
    barre = Barre(len(fichiers_contrats(donnees / "contrats")), "Ingestion")
    contrats = ingerer_dossier(donnees / "contrats", base, forcer=a.forcer, barre=barre)
    barre.terminer()
    for c in contrats:
        print(f"{c.statut:<11} {c.id:<28} {c.rapport.get('nb_clauses', 0):>4} clauses  {c.rapport.get('par_type', {})}")
        for alerte in c.rapport.get("alertes", []):
            print(f"{'':<11} ! {alerte}")
    if any(c.statut != "OK" for c in base.contrats()):
        print("\nDes contrats sont à vérifier : un profil d'assureur (data/profils/) corrige le découpage.")
    return 0
