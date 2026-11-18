"""Barre de progression pour les commandes longues (évaluation, compilation, ingestion).

    Évaluation  [██████████░░░░░░░░░░]  7/14  écoulé 1 min 52 s, reste ~1 min 50 s  velo-05

Sans dépendance. Elle s'écrit sur la sortie d'erreur, pour ne pas se mêler aux résultats (le JSON
du banc reste propre), et seulement dans un terminal : rien dans un fichier ni
dans les tests. Utilisable depuis plusieurs fils d'exécution (les cas tournent en parallèle).
"""

from __future__ import annotations

import sys
import threading
import time


def duree(secondes: float) -> str:
    secondes = int(secondes)
    if secondes < 60:
        return f"{secondes} s"
    return f"{secondes // 60} min {secondes % 60:02d} s"


class Barre:
    def __init__(self, total: int, libelle: str, largeur: int = 20, flux=None):
        self.total, self.libelle, self.largeur = max(total, 0), libelle, largeur
        self.flux = flux or sys.stderr
        self.actif = bool(getattr(self.flux, "isatty", lambda: False)())
        self.fait, self.debut, self.verrou = 0, time.monotonic(), threading.Lock()
        self.dernier, self.longueur = "", 0
        self._dessiner()

    def _ligne(self) -> str:
        part = self.fait / self.total if self.total else 1.0
        pleins = int(part * self.largeur)
        ecoule = time.monotonic() - self.debut
        reste = f", reste ~{duree(ecoule / self.fait * (self.total - self.fait))}" if 0 < self.fait < self.total else ""
        detail = f"  {self.dernier}" if self.dernier else ""
        return (f"{self.libelle}  [{'█' * pleins}{'░' * (self.largeur - pleins)}]  "
                f"{self.fait}/{self.total}  écoulé {duree(ecoule)}{reste}{detail}")

    def _effacer(self) -> None:
        # Retour en début de ligne et espaces : marche aussi dans l'ancienne console Windows,
        # qui ne comprend pas toujours les codes d'effacement.
        self.flux.write("\r" + " " * self.longueur + "\r")

    def _dessiner(self) -> None:
        if self.actif:
            ligne = self._ligne()
            self._effacer()
            self.flux.write(ligne)
            self.longueur = len(ligne)
            self.flux.flush()

    def avancer(self, detail: str = "") -> None:
        with self.verrou:
            self.fait += 1
            self.dernier = detail
            self._dessiner()

    def ecrire(self, texte: str) -> None:
        """Un message au-dessus de la barre (sur la sortie standard), puis la barre redessinée."""
        with self.verrou:
            if self.actif:
                self._effacer()
                self.flux.flush()
            print(texte, flush=True)
            self._dessiner()

    def terminer(self) -> None:
        with self.verrou:
            if self.actif:
                self._dessiner()
                self.flux.write("\n")
                self.flux.flush()
