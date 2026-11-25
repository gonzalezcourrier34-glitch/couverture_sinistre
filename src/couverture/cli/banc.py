"""`couverture banc` : le golden set (ou le jeu fermé) rejoué couche par couche, avec des portes."""

from __future__ import annotations

import sys
from pathlib import Path

from ..contrat.base import Base
from ..mesure import banc
from ..mesure.evaluation import JEUX_FERMES
from .commun import chaine


def ajouter(sous) -> None:
    """Déclare la commande « banc » et ses options."""
    p = sous.add_parser("banc", help="Banc d'essai : le golden set rejoué (règles, lecture, chaîne), avec des portes")
    p.add_argument("--contrat", required=True)
    p.add_argument("--couches", default="regles,chaine",
                   help="regles (sans modèle, SWI-Prolog), chaine (avec le modèle ; donne aussi la lecture)")
    p.add_argument("--repetitions", type=int, default=3)
    p.add_argument("--paralleles", type=int, default=4)
    p.add_argument("--figer", nargs="?", const="", metavar="NOTE",
                   help="Enregistrer la version du golden set (après l'avoir modifié ou validé)")
    p.add_argument("--fiche", action="store_true", help="Écrire data/golden/A_VALIDER.md, la fiche de relecture des cas")
    p.add_argument("--jeu", choices=["golden", *JEUX_FERMES], default="golden",
                   help="ferme, aveugle, neuf : les cas écrits sans voir les règles (data/<jeu>), chaîne complète seule")
    p.add_argument("--partie", choices=["tout", "mise_au_point", "test"], default="tout",
                   help="golden : les seuls cas de mise au point, ou de test (data/lecture/partage.json)")
    p.set_defaults(executer=executer)


def executer(a, base: Base, donnees: Path) -> int:
    """Le golden set rejoué couche par couche ; sort en erreur si une porte échoue (pour la CI)."""
    contrat_id = a.contrat

    if a.fiche:
        f = Path(donnees) / "golden" / "A_VALIDER.md"
        f.write_text(banc.fiche_validation(donnees, contrat_id), encoding="utf-8")
        print(f"Fiche de validation : {f}")
        return 0

    if a.figer is not None:
        v = banc.figer(donnees, contrat_id, a.figer)
        print(f"Golden set figé : version {v['version']} (empreinte {v['empreintes'][contrat_id]}).")
        return 0
    voulues = [c.strip() for c in a.couches.split(",") if c.strip()]
    fabrique = (lambda: chaine(base, contrat_id)) if "chaine" in voulues else None
    try:
        r = banc.passer(donnees, contrat_id, "regles", voulues, a.repetitions, a.paralleles, pipeline_fabrique=fabrique,
                        jeu=a.jeu, partie=a.partie)
    except ValueError as e:
        sys.exit(str(e))
    _, md = banc.enregistrer(donnees, r)
    print(banc.resume_console(r, md))
    return 0 if r["passe"] else 1
