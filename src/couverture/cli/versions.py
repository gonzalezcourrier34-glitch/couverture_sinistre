"""`couverture versions` : les consignes versionnées (le garde-fou de la CI)."""

from __future__ import annotations

from pathlib import Path

from .. import consignes
from ..base import Base


def ajouter(sous) -> None:
    p = sous.add_parser("versions", help="Versions des consignes : vérifier, ou réécrire le manifeste")
    p.add_argument("--manifeste", action="store_true", help="Réécrire config/versions_consignes.json")
    p.set_defaults(executer=executer)


def executer(a, base: Base, donnees: Path) -> int:
    if a.manifeste:
        for nom, info in consignes.ecrire_manifeste().items():
            print(f"{nom:<32} {info['version']:<8} {info['empreinte']}")
        print(f"Manifeste écrit : {consignes.MANIFESTE}")
        return 0
    problemes = consignes.verifier()
    for nom, info in consignes.etat_actuel().items():
        print(f"{nom:<32} {info['version']:<8} {info['empreinte']}")
    for p_ in problemes:
        print(f"! {p_}")
    return 1 if problemes else 0
