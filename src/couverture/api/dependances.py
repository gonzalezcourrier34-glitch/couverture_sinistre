"""Ce que les routes reçoivent par `Depends` : la base, le journal, les chaînes d'analyse.

**Provenance** : nouveau module (20/11/2026), sur le modèle des dépendances de SortirIA (`get_connection`,
`get_search_services`) : des fonctions que les tests remplacent par `app.dependency_overrides`.
"""

from __future__ import annotations

import threading
from functools import lru_cache

from couverture.api import config
from couverture.base import Base
from couverture.journal import Journal


@lru_cache(maxsize=1)
def get_base() -> Base:
    """La base des contrats (`COUVERTURE_BASE`), ouverte une fois."""
    return Base(config.BASE)


@lru_cache(maxsize=1)
def get_journal() -> Journal:
    """Le journal des analyses, dans la même base (pour le suivi et Grafana)."""
    return Journal(get_base().chemin)


class Pipelines:
    """Une chaîne d'analyse par contrat (lecture par le modèle, décision par le moteur), créée à la première
    demande et gardée : le moteur Prolog du contrat reste chargé."""

    def __init__(self, base: Base):
        self.base = base
        self._chaines: dict[str, object] = {}
        self._verrou = threading.Lock()

    def pour(self, contrat_id: str):
        """La chaîne du contrat.

        Raises
        ------
        KeyError
            Contrat inconnu.
        LookupError
            Contrat sans règles, ou SWI-Prolog absent.
        RuntimeError
            Aucun modèle configuré (`MISTRAL_API_KEY`).
        """
        with self._verrou:
            if contrat_id not in self._chaines:
                from couverture.llm import configurer
                from couverture.chaine import PipelineRegles

                self.base.contrat(contrat_id)
                llm = configurer()
                if llm is None:
                    raise RuntimeError("Aucun modèle configuré : MISTRAL_API_KEY dans le .env du serveur.")
                self._chaines[contrat_id] = PipelineRegles.depuis_base(self.base, contrat_id, llm)
            return self._chaines[contrat_id]


@lru_cache(maxsize=1)
def get_pipelines() -> Pipelines:
    return Pipelines(get_base())
