"""Configuration de l'API.

**Provenance** : sur le modèle de `app/config.py` de SortirIA (20/11/2026). Les valeurs viennent du `.env` à
la racine du projet (jamais versionné) ou de l'environnement, qui l'emporte.

- `COUVERTURE_API_KEY` : la clé que les clients envoient dans `x-api-key`. Sans elle, les routes protégées
  refusent tout (500) : mieux vaut une erreur qu'une API ouverte.
- `COUVERTURE_BASE` : la base SQLite des contrats (défaut `data/base.sqlite`).
- `COUVERTURE_CODE_ACCES` : mise en ligne (voir `acces.py`). Défini, il est demandé à toute requête, il dispense
  de la clé, et il ferme la consultation libre du texte des contrats.
- `COUVERTURE_LIMITE_JOUR` : en ligne, le nombre d'analyses acceptées par jour (défaut 300 ; 0 : sans limite).
- `COUVERTURE_FRONT` : le dossier de l'écran construit (`npm run build`), que l'API sert alors à la racine.
- `COUVERTURE_METHODE` : la méthode d'analyse par défaut, `clauses` (la lecture clause par clause, contresignée
  par les règles, 7.201 ; défaut depuis la mesure du jeu « quatre », 7.207) ou `regles` (la chaîne de règles
  seule). Une requête peut la choisir (`methode`).
- `COUVERTURE_MODELE_CLAUSES` : le modèle de la lecture des clauses (défaut `mistral-large-latest`, 7.200).
"""

from __future__ import annotations

import os

from couverture.config import charger_env

charger_env(".env")

API_KEY = os.getenv("COUVERTURE_API_KEY", "")
BASE = os.getenv("COUVERTURE_BASE", "data/base.sqlite")
CODE_ACCES = os.getenv("COUVERTURE_CODE_ACCES", "")
LIMITE_JOUR = int(os.getenv("COUVERTURE_LIMITE_JOUR", "300") or 0)
FRONT = os.getenv("COUVERTURE_FRONT", "")
METHODE = os.getenv("COUVERTURE_METHODE", "clauses").strip() or "clauses"
MODELE_CLAUSES = os.getenv("COUVERTURE_MODELE_CLAUSES", "mistral-large-latest").strip() or "mistral-large-latest"
VERSION = "1.0.0"
