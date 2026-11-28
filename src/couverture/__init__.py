"""Couverture d'un sinistre à partir des conditions générales, en citant les clauses. Deux méthodes : le modèle juge
chaque clause et une logique fixe décide (par défaut), ou le modèle lit les faits et Prolog décide."""

from .models import Decision, Resultat, Verdict

__all__ = ["Resultat", "Verdict", "Decision"]
__version__ = "0.4.0"
