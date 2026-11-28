"""`couverture journal` : le journal des analyses résumé par jour (DEMARCHE 7.239). Aucun appel au modèle.

  couverture journal                          # le journal de la base locale, les 30 derniers jours
  couverture journal --fichier journaux.txt   # en ligne : les journaux de l'hébergeur, exportés dans un fichier
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from ..analyse.journal import Journal, lire_sortie, resume_par_jour
from ..contrat.base import Base


def ajouter(sous) -> None:
    """Déclare la commande « journal » et ses options."""
    p = sous.add_parser("journal", help="Le journal des analyses, par jour : nombre, erreurs, « à préciser », durée, coût")
    p.add_argument("--jours", type=int, default=30, metavar="N", help="Les N derniers jours (30 par défaut)")
    p.add_argument("--fichier", metavar="CHEMIN",
                   help="Lire les lignes « journal » d'un export des journaux de l'hébergeur au lieu de la base")
    p.set_defaults(executer=executer)


def executer(a, base: Base, donnees: Path) -> int:
    """Affiche le résumé ; les lignes d'un fichier exporté sont prises toutes, sans filtre de date."""
    if a.fichier:
        analyses = lire_sortie(Path(a.fichier).read_text(encoding="utf-8").splitlines())
    else:
        fin = datetime.now(timezone.utc) + timedelta(days=1)
        analyses = Journal(base.chemin).lignes(fin - timedelta(days=a.jours + 1), fin)
    print(resume_par_jour(analyses))
    return 0
