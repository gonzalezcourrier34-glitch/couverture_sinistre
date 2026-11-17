"""Lecture du fichier .env, sans dépendance.

Les clés API ne sont jamais écrites dans le code : elles vont dans un fichier `.env`
à la racine du projet (ignoré par git), ou dans les variables d'environnement.
Une variable déjà définie dans l'environnement n'est pas écrasée par le fichier.
"""

from __future__ import annotations

import os
from pathlib import Path


def lire_env(chemin: str | Path) -> dict[str, str]:
    valeurs: dict[str, str] = {}
    chemin = Path(chemin)
    if not chemin.exists():
        return valeurs
    for ligne in chemin.read_text(encoding="utf-8-sig").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#") or "=" not in ligne:
            continue
        cle, valeur = ligne.split("=", 1)
        cle = cle.strip().removeprefix("export ").strip()
        valeur = valeur.strip()
        if len(valeur) >= 2 and valeur[0] == valeur[-1] and valeur[0] in "\"'":
            valeur = valeur[1:-1]
        elif " #" in valeur:
            valeur = valeur.split(" #", 1)[0].strip()
        if cle:
            valeurs[cle] = valeur
    return valeurs


def charger_env(chemin: str | Path = ".env") -> list[str]:
    """Charge le fichier dans l'environnement. Renvoie les noms des variables ajoutées."""
    ajoutees = []
    for cle, valeur in lire_env(chemin).items():
        if cle not in os.environ and valeur:
            os.environ[cle] = valeur
            ajoutees.append(cle)
    return ajoutees
