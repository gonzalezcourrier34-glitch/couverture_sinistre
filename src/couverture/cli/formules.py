"""`couverture formules` : lit le tableau des garanties par formule d'un contrat."""

from __future__ import annotations

from pathlib import Path

from ..analyse import prolog
from ..contrat import tableaux
from ..contrat.base import Base
from ..contrat.ingestion import charger_catalogue


def ajouter(sous) -> None:
    """Déclare la commande « formules » et ses options."""
    p = sous.add_parser("formules", help="Lire le tableau des garanties par formule d'un contrat (une page du PDF)")
    p.add_argument("--contrat", required=True)
    p.add_argument("--page", type=int, required=True, help="Page du tableau, numérotée à partir de 1")
    p.set_defaults(executer=executer)


def executer(a, base: Base, donnees: Path) -> int:
    """Lit le tableau des garanties par formule (7.92) et l'écrit dans regles/formules/<contrat>.json."""
    contrat_id, page = a.contrat, a.page

    fichiers = [f for f, m in charger_catalogue(donnees / "contrats").items()
                if m.get("id") == contrat_id and (donnees / "contrats" / f).exists()]
    if not fichiers:
        print(f"Aucun fichier du catalogue pour {contrat_id} dans {donnees / 'contrats'}.")
        return 1
    formules = prolog.vocabulaire()["formule"]["valeurs"]
    try:
        doc = tableaux.extraire(donnees / "contrats" / fichiers[0], page, contrat_id, formules)
    except (ValueError, IndexError) as e:
        print(f"Tableau illisible page {page} : {e}")
        return 1
    print(f"Tableau des formules ({', '.join(doc['formules'])}), page {page} : {len(doc['lignes'])} lignes → "
          f"{tableaux.chemin(contrat_id)}")
    for l in doc["lignes"]:
        lie = doc["correspondance"].get(l["libelle"])
        print(f"  {l['libelle'][:60]:60} inclus : {', '.join(l['inclus']) or '-':28} option : {', '.join(l['option']) or '-':20}"
              f"{' → ' + ', '.join(lie) if lie else ''}")
    return 0
