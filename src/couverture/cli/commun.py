"""Ce que plusieurs commandes partagent : la chaîne d'analyse d'un contrat."""

from __future__ import annotations

import sys

from ..base import Base
from ..llm import configurer


def chaine(base: Base, contrat_id: str):
    """La chaîne d'analyse du contrat : le modèle lit les faits, Prolog décide. Quitte si rien n'est configuré."""
    from ..chaine import PipelineRegles

    llm = configurer()
    if llm is None:
        sys.exit("L'analyse a besoin d'un modèle : définir MISTRAL_API_KEY dans .env.")
    try:
        return PipelineRegles.depuis_base(base, contrat_id, llm)
    except LookupError as e:
        sys.exit(str(e))
