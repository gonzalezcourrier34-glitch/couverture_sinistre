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

    def analyser(self, sinistre, suivi=None):
        if suivi:
            suivi("socle")
            suivi("socle", "evenement : responsabilite")
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
    # La méthode du serveur vient du .env du poste (COUVERTURE_METHODE) : les tests fixent la leur, sans quoi un
    # .env réglé sur « clauses » envoyait les analyses des tests au vrai modèle (7.204).
    monkeypatch.setattr(config, "METHODE", "regles")
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
    assert s["methode"] == "regles" and s["modele_clauses"] is None, "la méthode du serveur, pour l'en-tête"
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


def test_analyse_suivie(client, base, oracle):  # noqa: F811
    """7.134 : le même résultat que `/analyses`, précédé d'une ligne JSON par étape ; une panne arrive dans le flux."""
    import json

    demande = {"contrat_id": CONTRAT, "sinistre": "En faisant du vélo, j'ai renversé un piéton qui s'est cassé le poignet."}
    r = client.post("/api/v1/analyses/suivi", headers=CLE, json=demande)
    assert r.status_code == 200 and r.headers["content-type"].startswith("application/x-ndjson")
    lignes = [json.loads(l) for l in r.text.splitlines() if l.strip()]
    assert lignes[0] == {"etape": "socle"} and lignes[1]["detail"] == "evenement : responsabilite"
    assert lignes[-1]["etape"] == "fin" and lignes[-1]["reponse"]["decision"] == "COUVERT"
    assert lignes[-1]["reponse"] == client.post("/api/v1/analyses", headers=CLE, json=demande).json() | {
        "durees_ms": lignes[-1]["reponse"]["durees_ms"]}
    assert client.post("/api/v1/analyses/suivi", headers=CLE, json=demande | {"contrat_id": "inconnu"}).status_code == 404
    app.dependency_overrides[dependances.get_pipelines] = lambda: FaussesChaines(base, oracle, erreur=True)
    panne = [json.loads(l) for l in client.post("/api/v1/analyses/suivi", headers=CLE, json=demande).text.splitlines()]
    assert panne[-1]["etape"] == "erreur" and panne[-1]["code"] == 502 and client.journal.erreurs


def test_fiche_pdf(client):
    """7.130 : la réponse d'une analyse, renvoyée telle quelle, revient en PDF."""
    declaration = "En faisant du vélo, j'ai renversé un piéton qui s'est cassé le poignet."
    reponse = client.post("/api/v1/analyses", headers=CLE, json={"contrat_id": CONTRAT, "sinistre": declaration}).json()
    r = client.post("/api/v1/fiches", headers=CLE, json={"contrat_id": CONTRAT, "sinistre": declaration, "reponse": reponse})
    assert r.status_code == 200, r.text
    assert r.headers["content-type"] == "application/pdf" and r.content.startswith(b"%PDF")
    assert "fiche-sinistre-" in r.headers["content-disposition"]
    assert client.post("/api/v1/fiches", headers=CLE, json={"contrat_id": "inconnu", "sinistre": declaration,
                                                           "reponse": reponse}).status_code == 404
    assert client.post("/api/v1/fiches", json={"contrat_id": CONTRAT, "sinistre": declaration,
                                               "reponse": reponse}).status_code == 401


def test_documentation(client):
    assert client.get("/", follow_redirects=False).headers["location"] == "/docs"
    chemins = client.get("/openapi.json").json()["paths"]
    assert {"/api/v1/analyses", "/api/v1/analyses/suivi", "/api/v1/decisions", "/api/v1/fiches",
            "/api/v1/sante"} <= set(chemins)


def test_une_route_par_fichier():
    """Chaque module de `routes/` déclare exactement une route (règle du projet)."""
    import importlib
    import pkgutil

    from couverture.api import routes

    for m in pkgutil.iter_modules(routes.__path__):
        module = importlib.import_module(f"couverture.api.routes.{m.name}")
        assert len(module.router.routes) == 1, m.name


# --- Mise en ligne : code d'accès, limite d'appels, texte du contrat (7.161) --------------------------------

def basic(code: str) -> dict:
    import base64
    return {"Authorization": "Basic " + base64.b64encode(f"visiteur:{code}".encode()).decode()}


def test_en_ligne_le_code_d_acces_remplace_la_cle(client, monkeypatch):
    """Sans proxy pour ajouter la clé, l'écran en ligne s'ouvre avec un code d'accès, demandé par le navigateur."""
    monkeypatch.setattr(config, "CODE_ACCES", "sésame-42")
    assert client.get("/health").status_code == 200, "l'hébergeur doit pouvoir vérifier que le service vit"
    refus = client.get("/api/v1/contrats")
    assert refus.status_code == 401 and refus.headers["www-authenticate"].startswith("Basic")
    assert client.get("/api/v1/sante").status_code == 401, "en ligne, rien n'est ouvert sans le code"
    assert client.get("/api/v1/contrats", headers=basic("faux")).status_code == 401
    assert client.get("/api/v1/contrats", headers=CLE).status_code == 401, "la clé seule ne suffit pas en ligne"
    assert client.get("/api/v1/contrats", headers=basic("sésame-42")).status_code == 200, "le code dispense de la clé"
    monkeypatch.setattr(config, "CODE_ACCES", "")
    assert client.get("/api/v1/contrats").status_code == 401 and client.get("/api/v1/contrats", headers=CLE).status_code == 200


def test_en_ligne_le_contrat_ne_se_telecharge_pas(client, monkeypatch):
    """Hors ligne, une clause se lit seule ou avec les autres. En ligne : pas la liste, et une à une seulement
    les clauses que les règles citent, celles qu'une réponse peut montrer."""
    from couverture.analyse import prolog
    citees = sorted(prolog.clauses_citees(CONTRAT))
    toutes = client.get(f"/api/v1/contrats/{CONTRAT}/clauses", headers=CLE).json()
    presentes = {c["id"] for c in toutes}
    citee = next(c for c in citees if c in presentes)
    autre = next((c for c in sorted(presentes) if c not in citees), None)
    une = client.get(f"/api/v1/contrats/{CONTRAT}/clauses/{citee}", headers=CLE)
    assert une.status_code == 200 and une.json()["id"] == citee
    if autre:
        assert client.get(f"/api/v1/contrats/{CONTRAT}/clauses/{autre}", headers=CLE).status_code == 200
    assert client.get(f"/api/v1/contrats/{CONTRAT}/clauses/inconnue", headers=CLE).status_code == 404
    avec_barre = next((c for c in citees if "/" in c and c in presentes), None)       # « 12/batiment » : l'identifiant contient une barre
    if avec_barre:
        assert client.get(f"/api/v1/contrats/{CONTRAT}/clauses/{avec_barre}", headers=CLE).json()["id"] == avec_barre

    monkeypatch.setattr(config, "CODE_ACCES", "sésame-42")
    code = basic("sésame-42")
    assert client.get(f"/api/v1/contrats/{CONTRAT}/clauses", headers=code).status_code == 403
    assert client.get(f"/api/v1/contrats/{CONTRAT}/clauses/{citee}", headers=code).status_code == 200
    if autre:
        assert client.get(f"/api/v1/contrats/{CONTRAT}/clauses/{autre}", headers=code).status_code == 403


def test_en_ligne_les_analyses_sont_comptees(client, monkeypatch):
    from couverture.api import acces
    monkeypatch.setattr(config, "CODE_ACCES", "sésame-42")
    monkeypatch.setattr(config, "LIMITE_JOUR", 2)
    monkeypatch.setitem(acces._compte, "jour", "")
    corps = {"contrat_id": CONTRAT, "sinistre": "En faisant du vélo, j'ai renversé un piéton qui s'est cassé le poignet."}
    code = basic("sésame-42")
    assert [client.post("/api/v1/analyses", json=corps, headers=code).status_code for _ in range(3)] == [200, 200, 429]
    assert client.post("/api/v1/decisions", json={"contrat_id": CONTRAT, "faits": {"evenement": ["vol"]}},
                       headers=code).status_code == 200, "le moteur seul n'appelle pas le modèle : il n'est pas compté"
    monkeypatch.setattr(config, "CODE_ACCES", "")
    monkeypatch.setitem(acces._compte, "jour", "")
    assert client.post("/api/v1/analyses", json=corps, headers=CLE).status_code == 200, "hors ligne, pas de limite"


def test_la_methode_clauses_se_choisit_par_requete(client, monkeypatch):
    """7.201 : `methode: clauses` passe par la lecture des clauses ; le suivi annonce d'abord ses étapes. Sans
    `methode`, c'est la chaîne de règles, comme avant (le réglage du serveur est éteint par défaut)."""
    import json

    from couverture.api import service
    from couverture.api.routes import analyse, analyse_suivie

    appels = []

    def lecture(base, chaine, contrat_id, sinistre, llm, suivi=None, souscription=None):
        appels.append(contrat_id)
        (suivi or (lambda e, d=None: None))("designation", "1 garantie à examiner, 5 clauses au dossier")
        r, sortie = service.analyser(chaine, sinistre)
        r.methode = "clauses"
        return r, sortie | {"mode": "clauses"}

    monkeypatch.setattr(service, "analyser_clauses", lecture)
    for module in (analyse, analyse_suivie):
        monkeypatch.setattr(module, "modele_des_clauses", lambda: None)
    demande = {"contrat_id": CONTRAT, "sinistre": "En faisant du vélo, j'ai renversé un piéton qui s'est cassé le poignet."}
    assert client.post("/api/v1/analyses", headers=CLE, json=demande).json()["mode"] != "clauses" and not appels
    assert client.post("/api/v1/analyses", headers=CLE, json=demande | {"methode": "clauses"}).json()["mode"] == "clauses"
    lignes = [json.loads(l) for l in client.post("/api/v1/analyses/suivi", headers=CLE,
                                                 json=demande | {"methode": "clauses"}).text.splitlines() if l.strip()]
    assert [e["cle"] for e in lignes[0]["etapes"]] == ["designation", "jugement", "regles", "decision"]
    assert "minutes" in lignes[0]["annonce"]
    assert lignes[1]["etape"] == "designation" and lignes[-1]["etape"] == "fin" and len(appels) == 2
    assert client.post("/api/v1/analyses", headers=CLE, json=demande | {"methode": "autre"}).status_code == 422


def test_le_suivi_bat_pendant_une_longue_attente(client, monkeypatch):
    """7.208 : une étape longue (un appel au modèle de plusieurs minutes) n'est pas un silence : le flux envoie des
    lignes vides en attendant, que l'écran ignore, pour que l'hébergeur ne coupe pas la requête."""
    import json
    import time

    from couverture.api.routes import analyse_suivie

    def lecture(base, chaine, contrat_id, sinistre, llm, suivi=None, souscription=None):
        time.sleep(0.35)
        r, sortie = service.analyser(chaine, sinistre)
        return r, sortie | {"mode": "clauses"}

    monkeypatch.setattr(service, "analyser_clauses", lecture)
    monkeypatch.setattr(analyse_suivie, "modele_des_clauses", lambda: None)
    monkeypatch.setattr(analyse_suivie, "BATTEMENT_S", 0.05)
    demande = {"contrat_id": CONTRAT, "methode": "clauses",
               "sinistre": "En faisant du vélo, j'ai renversé un piéton qui s'est cassé le poignet."}
    texte = client.post("/api/v1/analyses/suivi", headers=CLE, json=demande).text
    lignes = texte.split("\n")
    assert sum(1 for l in lignes if not l.strip()) >= 3, "des battements pendant l'attente"
    pleines = [json.loads(l) for l in lignes if l.strip()]
    assert "etapes" in pleines[0] and pleines[-1]["etape"] == "fin" and pleines[-1]["reponse"]["mode"] == "clauses"
