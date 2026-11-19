"""Couverture d'un sinistre à partir des conditions générales : le modèle lit les faits, Prolog décide."""

from .models import Decision, Resultat, Verdict

__all__ = ["Resultat", "Verdict", "Decision"]
__version__ = "0.4.0"
