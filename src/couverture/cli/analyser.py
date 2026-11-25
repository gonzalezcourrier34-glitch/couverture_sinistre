"""`couverture analyser` : un sinistre, sur un contrat."""

from __future__ import annotations

import time
from pathlib import Path

from ..analyse.journal import Journal
from ..contrat.base import Base
from .affichage import afficher, afficher_court
from .commun import chaine


def ajouter(sous) -> None:
    """Déclare la commande « analyser » et ses options."""
    p = sous.add_parser("analyser", help="Analyser un sinistre sur un contrat")
    p.add_argument("--contrat", required=True)
    p.add_argument("sinistre")
    p.add_argument("--json", action="store_true", help="Sortie JSON complète (traçabilité)")
    p.add_argument("--detail", action="store_true", help="Toutes les conditions et l'arbre de preuve complet")
    p.set_defaults(executer=executer)


def executer(a, base: Base, donnees: Path) -> int:
    """Analyse la déclaration, note l'analyse au journal et affiche la réponse (courte, détaillée ou en JSON)."""
    debut = time.perf_counter()
    r = chaine(base, a.contrat).analyser(a.sinistre)
    Journal(base.chemin).noter(r, duree_ms=int((time.perf_counter() - debut) * 1000))
    print(r.model_dump_json(indent=2) if a.json else afficher(r) if a.detail else afficher_court(r))
    return 0
