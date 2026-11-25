"""Réglages communs aux tests."""
import pytest

from couverture.analyse import prolog


@pytest.fixture(autouse=True)
def traduction_non_declaree(monkeypatch):
    """Les tests ne dépendent pas de l'état déclaré dans `regles/traduction.json` : par défaut, aucun contrat n'est
    tenu pour traduit en entier. Un test qui porte sur un contrat complet le dit lui-même (7.177)."""
    monkeypatch.setattr(prolog, "traduction_complete", lambda contrat_id: False)


@pytest.fixture(autouse=True)
def aucun_appel_au_modele(monkeypatch):
    """Les tests n'appellent jamais le vrai modèle, quel que soit le `.env` du poste : un appel réseau échoue tout de
    suite. Un test qui simule le fournisseur remplace `urlopen` ou `_poster` lui-même, après celui-ci (7.204)."""
    from couverture import llm

    def interdit(*_, **__):
        raise RuntimeError("Un test a voulu appeler le vrai modèle : à remplacer par un modèle factice.")

    monkeypatch.setattr(llm.urllib.request, "urlopen", interdit)
