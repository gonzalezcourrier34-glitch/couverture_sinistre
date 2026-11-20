"""Les routes de l'API, par HTTP : application réelle, dépendances remplacées (base temporaire, oracle Python,
fausse chaîne d'analyse), sur le modèle des tests de SortirIA (`tests/test_api/test_ratings_api.py`)."""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from couverture.api import config, dependances, service  # noqa: E402
from couverture.api.main import app  # noqa: E402
from couverture.api.routes import decision  # noqa: E402
from couverture.llm import ErreurLLM  # noqa: E402
from test_api_service import CONTRAT, base, oracle, regles  # noqa: E402,F401  (fixtures partagées)

CLE = {"x-api-key": "secret"}


class FausseChaine:
    def __init__(self, base, oracle, erreur=False):
        self.base, self.decideur, self.erreur = base, oracle, erreur

    def analyser(self, sinistre):
        if self.erreur:
            raise ErreurLLM("délai dépassé")
        r, _ = service.decider(self.base, CONTRAT, {"evenement": ["responsabilite"], "origine_rc": "personne",
                                                    "victime": "tiers"}, self.decideur)
        return r.model_copy(update={"sinistre": sinistre})


class FaussesChaines:
    def __init__(self, base, oracle, erreur=False):
        self.base, self.oracle, self.erreur = base, oracle, erreur

    def pour(self, contrat_id):
        self.base.contrat(contrat_id)
        return FausseChaine(self.base, self.oracle, self.erreur)


class FauxJournal:
    def __init__(self):
        self.notes, self.erreurs = [], []

    def noter(self, r, duree_ms=0):
        self.notes.append(r)

    def noter_erreur(self, contrat_id, methode, erreur):
        self.erreurs.append(erreur)


@pytest.fixture
def client(base, oracle, monkeypatch):  # noqa: F811
    monkeypatch.setattr(config, "API_KEY", "secret")
    journal = FauxJournal()
    app.dependency_overrides[dependances.get_base] = lambda: base
    app.dependency_overrides[dependances.get_pipelines] = lambda: FaussesChaines(base, oracle)
    app.dependency_overrides[dependances.get_journal] = lambda: journal
    app.dependency_overrides[decision.get_decideur] = lambda: oracle
    c = TestClient(app)
    c.journal = journal
    yield c
    app.dependency_overrides.clear()


def test_sante_et_health_publiques(client):
    assert client.get("/health").json() == {"status": "ok"}
    s = client.get("/api/v1/sante").json()
    assert CONTRAT in s["contrats_decidables"] and s["cle_api_configuree"] is True


def test_cle_api_exigee(client, monkeypatch):
    assert client.get("/api/v1/contrats").status_code == 401
    assert client.get("/api/v1/contrats", headers={"x-api-key": "faux"}).status_code == 401
    assert client.get("/api/v1/contrats", headers=CLE).status_code == 200
    monkeypatch.setattr(config, "API_KEY", "")                     # serveur sans clé : tout est refusé
    assert client.get("/api/v1/contrats", headers=CLE).status_code == 500


def test_contrats_contrat_clauses(client):
    liste = client.get("/api/v1/contrats", headers=CLE).json()
    assert liste[0]["id"] == CONTRAT and liste[0]["regles"] is True and "fichier" not in liste[0]
    assert client.get(f"/api/v1/contrats/{CONTRAT}", headers=CLE).json()["assureur"] == "A"
    assert client.get("/api/v1/contrats/inconnu", headers=CLE).status_code == 404
    garanties = client.get(f"/api/v1/contrats/{CONTRAT}/clauses?type=garantie", headers=CLE).json()
    assert garanties and all(c["type"] == "garantie" for c in garanties)
    assert client.get(f"/api/v1/contrats/{CONTRAT}/clauses?type=farfelu", headers=CLE).status_code == 422


def test_vocabulaire(client):
    voc = client.get("/api/v1/vocabulaire?evenement=responsabilite", headers=CLE).json()
    assert "origine_rc" in voc and "cause_eau" not in voc and voc["origine_rc"]["question"]


def test_analyse(client):
    r = client.post("/api/v1/analyses", headers=CLE, json={
        "contrat_id": CONTRAT, "sinistre": "En faisant du vélo, j'ai renversé un piéton qui s'est cassé le poignet."})
    assert r.status_code == 200, r.text
    corps = r.json()
    assert corps["decision"] == "COUVERT" and corps["citations"] and corps["faits"]["victime"] == "tiers"
    assert len(client.journal.notes) == 1
    assert client.post("/api/v1/analyses", headers=CLE, json={"contrat_id": CONTRAT, "sinistre": "court"}).status_code == 422
    assert client.post("/api/v1/analyses", headers=CLE, json={"contrat_id": "inconnu",
                                                              "sinistre": "Mon vélo a été volé hier soir."}).status_code == 404


def test_analyse_modele_en_panne(client, base, oracle):  # noqa: F811
    app.dependency_overrides[dependances.get_pipelines] = lambda: FaussesChaines(base, oracle, erreur=True)
    r = client.post("/api/v1/analyses", headers=CLE, json={"contrat_id": CONTRAT, "sinistre": "Mon vélo a été volé hier."})
    assert r.status_code == 502 and client.journal.erreurs


def test_decision_puis_question(client):
    r = client.post("/api/v1/decisions", headers=CLE, json={
        "contrat_id": CONTRAT, "faits": {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"]}}).json()
    assert r["decision"] == "INCERTAIN" and any(q["variable"] == "fermeture" for q in r["a_preciser"])
    r2 = client.post("/api/v1/decisions", headers=CLE, json={
        "contrat_id": CONTRAT, "faits": r["faits"] | {"fermeture": "cadenas"}}).json()
    assert r2["decision"] == "NON_COUVERT"
    assert client.post("/api/v1/decisions", headers=CLE, json={"contrat_id": CONTRAT, "faits": {}}).status_code == 422


def test_documentation(client):
    assert client.get("/", follow_redirects=False).headers["location"] == "/docs"
    chemins = client.get("/openapi.json").json()["paths"]
    assert {"/api/v1/analyses", "/api/v1/decisions", "/api/v1/sante"} <= set(chemins)


def test_une_route_par_fichier():
    """Chaque module de `routes/` déclare exactement une route (règle du projet)."""
    import importlib
    import pkgutil

    from couverture.api import routes

    for m in pkgutil.iter_modules(routes.__path__):
        module = importlib.import_module(f"couverture.api.routes.{m.name}")
        assert len(module.router.routes) == 1, m.name
