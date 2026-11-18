"""Banc LegalBench : lecture des données, contrôle des citations, métriques. Sans réseau ni modèle :
les cas ci-dessous sont inventés pour les tests (ce ne sont pas des cas de LegalBench)."""

import json

from couverture import legalbench as lb

POLICE = "Harbor's policy covers loss of property caused by fire. Losses caused by flood are not covered."
CAS = [
    {"id": "t-1", "split": "test", "policy": POLICE, "claim": "A kitchen fire destroyed the sofa.", "attendu": "COUVERT"},
    {"id": "t-2", "split": "test", "policy": POLICE, "claim": "The river flooded the basement.", "attendu": "NON_COUVERT"},
    {"id": "t-3", "split": "test", "policy": POLICE, "claim": "Smoke from the neighbour's barbecue stained the walls.", "attendu": "INCERTAIN"},
]


class Modele:
    nom = "faux"

    def __init__(self, reponses):
        self.reponses = reponses

    def completer(self, systeme, message):
        assert "mot pour mot" in systeme
        for cle, r in self.reponses.items():
            if cle in message:
                return json.dumps(r)
        return "pas de JSON"


def test_reponses_normalisees():
    assert [lb.normaliser(x) for x in ("A", "Yes", "B", "No", "C", "It's ambiguous")] == \
        ["COUVERT", "COUVERT", "NON_COUVERT", "NON_COUVERT", "INCERTAIN", "INCERTAIN"]
    assert lb.normaliser("peut-être") is None


def test_lecture_tsv_d_origine(tmp_path):
    f = tmp_path / "test.tsv"
    f.write_text("answer\tclaim\tindex\tpolicy\nA\tFire.\t0\tCovers fire.\nC\tSmoke.\t1\tCovers fire.\n", encoding="utf-8")
    cas = lb.charger(f)
    assert [c["attendu"] for c in cas] == ["COUVERT", "INCERTAIN"] and cas[1]["id"] == "test-1"


def test_controle_des_citations():
    """Une réponse ferme sans citation retrouvée devient INCERTAIN ; une réponse illisible aussi."""
    m = Modele({
        "kitchen fire": {"decision": "COUVERT", "citation": "covers loss of property caused by fire", "raison": "incendie"},
        "river": {"decision": "NON_COUVERT", "citation": "floods are excluded", "raison": "citation inventée"},
    })
    r = lb.passer(CAS, m, paralleles=1)
    par_id = {l["id"]: l for l in r["cas"]}
    assert par_id["t-1"]["decision"] == "COUVERT" and par_id["t-1"]["citation_trouvee"]
    assert par_id["t-2"]["brute"] == "NON_COUVERT" and par_id["t-2"]["decision"] == "INCERTAIN"
    assert par_id["t-3"]["brute"] == "ERREUR" and par_id["t-3"]["decision"] == "INCERTAIN"
    assert r["citations_introuvables"] == 1 and r["changees_par_le_controle"] == 2
    assert r["brute"]["exactitude"] == r["controlee"]["exactitude"] == round(2 / 3, 3)
    assert r["brute"]["erreurs"] == 1 and r["controlee"]["faux_couverts"] == 0


def test_metriques():
    lignes = [{"attendu": "COUVERT", "decision": "COUVERT"}, {"attendu": "NON_COUVERT", "decision": "COUVERT"},
              {"attendu": "INCERTAIN", "decision": "INCERTAIN"}, {"attendu": "INCERTAIN", "decision": "NON_COUVERT"}]
    m = lb.metriques(lignes)
    assert m["exactitude"] == 0.5 and m["faux_couverts"] == 1 and m["faux_refus"] == 0
    assert m["rappel_par_classe"] == {"COUVERT": 1.0, "NON_COUVERT": 0.0, "INCERTAIN": 0.5}
    assert m["exactitude_equilibree"] == 0.5 and m["precision_incertain"] == 1.0


def test_rapport_et_commande(tmp_path, monkeypatch, capsys):
    from couverture import cli, llm

    dossier = tmp_path / "externes" / "legalbench"
    dossier.mkdir(parents=True)
    (dossier / lb.FICHIER).write_text("".join(json.dumps(c) + "\n" for c in CAS), encoding="utf-8")
    m = Modele({"kitchen fire": {"decision": "COUVERT", "citation": "caused by fire", "raison": "…"}})
    monkeypatch.setattr(llm, "configurer", lambda usage="analyse": m)
    assert cli.main(["--donnees", str(tmp_path), "legalbench", "--limite", "2", "--paralleles", "1"]) == 0
    sortie = capsys.readouterr().out
    assert "Banc LegalBench" in sortie and "2 cas" in sortie
    md = next((tmp_path / "bancs").glob("*legalbench-faux.md")).read_text(encoding="utf-8")
    assert "CC BY 4.0" in md and "Confusion, après contrôle" in md
