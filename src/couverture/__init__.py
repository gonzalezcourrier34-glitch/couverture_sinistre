"""Pipeline de décision de couverture d'un sinistre à partir des conditions générales."""

from .models import Decision, Resultat, Verdict
from .pipeline import Pipeline

__all__ = ["Pipeline", "Resultat", "Verdict", "Decision"]
__version__ = "0.1.0"
