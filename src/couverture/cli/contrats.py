"""`couverture contrats` : les contrats de la base et leur statut."""

from __future__ import annotations

from pathlib import Path

from ..base import Base


def ajouter(sous) -> None:
    sous.add_parser("contrats", help="Lister les contrats de la base").set_defaults(executer=executer)


def executer(a, base: Base, donnees: Path) -> int:
    for c in base.contrats():
        print(f"{c.statut:<11} {c.id:<28} {c.assureur} — {c.produit} ({c.version})")
    return 0
