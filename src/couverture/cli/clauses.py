"""`couverture clauses` : le découpage d'un contrat."""

from __future__ import annotations

from pathlib import Path

from ..contrat.base import Base


def ajouter(sous) -> None:
    """Déclare la commande « clauses » et ses options."""
    p = sous.add_parser("clauses", help="Afficher le découpage d'un contrat")
    p.add_argument("--contrat", required=True)
    p.set_defaults(executer=executer)


def executer(a, base: Base, donnees: Path) -> int:
    """Affiche une ligne par clause : identifiant, type, pages, titre."""
    for c in base.clauses(a.contrat):
        print(f"{c.id:>24}  {c.type.value:<10}  p.{','.join(map(str, c.pages)):<6}  {c.titre}")
    return 0
