"""Ligne de commande : une commande par module, comme les routes de l'API.

  couverture ingerer                               # lit data/contrats/ et remplit la base
  couverture contrats                              # liste les contrats et leur statut
  couverture clauses  --contrat assureur-a-habitation-2025
  couverture regles   --contrat assureur-a-habitation-2025 [--faits '{"evenement": "vol"}']   # sans modèle
  couverture formules --contrat assureur-d-habitation-2026 --page 4                          # tableau des formules
  couverture rediger  --contrat assureur-a-habitation-2025 --article 2.2                     # Mistral Large rédige
  couverture analyser --contrat assureur-a-habitation-2025 "Mon vélo a été volé dans le local commun…"
  couverture banc     --contrat assureur-a-habitation-2025 [--jeu ferme] [--partie test]     # bancs, portes
  couverture exemples [--partager] [--indexer] [--proches "texte"]                          # banque d'exemples
  couverture api      --port 8001                  # l'API FastAPI (/docs), clé COUVERTURE_API_KEY
  couverture versions [--manifeste]                # consignes versionnées
  couverture modele                                # modèle configuré, test de connexion
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ..config import charger_env
from ..contrat.base import Base
from . import analyser, api, banc, clauses, contrats, exemples, formules, ingerer, juger, modele, rediger, regles, versions

COMMANDES = (ingerer, contrats, clauses, regles, formules, rediger, analyser, juger, banc, exemples, api, versions, modele)


def main(argv: list[str] | None = None) -> int:
    """Lit la ligne de commande, charge `.env`, ouvre la base et lance la commande demandée ; rend son code de sortie."""
    p = argparse.ArgumentParser(prog="couverture", description="Le sinistre est-il couvert par les conditions générales ?")
    p.add_argument("--donnees", default="data", help="Dossier des données (défaut : data)")
    p.add_argument("--base", default=None, help="Base SQLite (défaut : <donnees>/base.sqlite)")
    sous = p.add_subparsers(dest="commande", required=True)
    for commande in COMMANDES:
        commande.ajouter(sous)
    a = p.parse_args(argv)
    charger_env(".env")  # clés API : fichier .env à la racine du projet
    donnees = Path(a.donnees)
    return a.executer(a, Base(a.base or donnees / "base.sqlite"), donnees)


def principal() -> int:
    """Point d'entrée : une erreur du fournisseur de modèle s'affiche en une ligne, sans trace."""
    from ..llm import ErreurLLM

    try:
        return main()
    except ErreurLLM as e:
        print(f"Erreur du modèle : {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(principal())
