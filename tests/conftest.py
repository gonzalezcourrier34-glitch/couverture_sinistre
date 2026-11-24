"""Réglages communs aux tests."""
import pytest

from couverture import prolog


@pytest.fixture(autouse=True)
def traduction_non_declaree(monkeypatch):
    """Les tests ne dépendent pas de l'état déclaré dans `regles/traduction.json` : par défaut, aucun contrat n'est
    tenu pour traduit en entier. Un test qui porte sur un contrat complet le dit lui-même (7.177)."""
    monkeypatch.setattr(prolog, "traduction_complete", lambda contrat_id: False)
