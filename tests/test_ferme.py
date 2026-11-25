"""Le jeu fermé (7.79) : deux annotateurs à l'aveugle, les accords gardés, les désaccords arbitrés."""

import json

from couverture.mesure import banc, ferme


def ecrire(chemin, lignes):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in lignes), encoding="utf-8")


def test_accords_desaccords_arbitrage_et_banc(tmp_path, monkeypatch):
    d = tmp_path / "ferme"
    monkeypatch.setattr(ferme, "DOSSIER", d)
    cas = [
        {"id": "f-a01", "contrat": "assureur-a", "declaration": "Incendie de la cuisine.", "attendu": "COUVERT",
         "acceptables": [], "articles": ["2.1"], "citation": "c", "question_attendue": "", "theme": "base", "justification": "j"},
        {"id": "f-a02", "contrat": "assureur-a", "declaration": "Vélo volé dans la rue.", "attendu": "NON_COUVERT",
         "acceptables": ["INCERTAIN"], "articles": ["2.10"], "citation": "c", "question_attendue": "", "theme": "piege", "justification": "j"},
        {"id": "f-b01", "contrat": "assureur-b", "declaration": "Bijoux volés.", "attendu": "INCERTAIN",
         "acceptables": [], "articles": ["3.1.6"], "citation": "c", "question_attendue": "Effraction ?", "theme": "incertain", "justification": "j"},
        {"id": "f-b02", "contrat": "assureur-b", "declaration": "Tempête.", "attendu": "COUVERT",
         "acceptables": [], "articles": ["3.1.2"], "citation": "c", "question_attendue": "", "theme": "base", "justification": "j"}]
    avis = [{"id": "f-a01", "attendu": "COUVERT", "acceptables": []},
            {"id": "f-a02", "attendu": "INCERTAIN", "acceptables": [], "articles": ["2.10"]},   # accepté par l'agent : souple
            {"id": "f-b01", "attendu": "NON_COUVERT", "acceptables": [], "articles": ["3.1.6.2"],
             "justification": "vol simple", "question_attendue": ""},                         # désaccord
            {"id": "f-b02", "attendu": "NON_COUVERT", "acceptables": []}]                      # désaccord
    ecrire(d / "cas_agent.jsonl", cas)
    ecrire(d / "avis_second.jsonl", avis)
    ferme.comparer()
    lignes = (d / "arbitrage.csv").read_text(encoding="utf-8-sig").splitlines()
    assert len(lignes) == 3 and lignes[1].startswith("f-b01;")
    ferme.exporter()
    assert len(ferme.lire(d / "sinistres.jsonl")) == 2, "les désaccords non arbitrés attendent"
    (d / "arbitrage.csv").write_text("\n".join([lignes[0], lignes[1] + "second", lignes[2] + "ecarter"]) + "\n",
                                     encoding="utf-8-sig")
    ferme.comparer()   # garde les choix déjà faits
    ferme.exporter()
    b = ferme.lire(d / "annotations" / "assureur-b-habitation-2017.jsonl")
    assert [(x["sinistre_id"], x["attendu"]) for x in b] == [("f-b01", "NON_COUVERT")]
    a = {x["sinistre_id"]: x for x in ferme.lire(d / "annotations" / "assureur-a-habitation-2025.jsonl")}
    assert a["f-a02"]["attendu"] == "NON_COUVERT" and a["f-a02"]["acceptables"] == ["INCERTAIN"]
    cas_banc, etat = banc.charger(tmp_path, "assureur-a-habitation-2025", "ferme")
    assert etat["jeu"] == "ferme" and etat["n"] == 2 and all(c.get("faits") is None for c in cas_banc)


def test_le_second_jeu_ferme_se_monte_et_se_rejoue_comme_le_premier(tmp_path, monkeypatch):
    """7.185. « aveugle » : un second jeu écrit sans voir les règles, dans son dossier, avec les mêmes commandes.
    Ses déclarations comptent parmi les cas de mesure dont les exemples de lecture doivent rester loin."""
    from couverture.analyse import exemples
    from couverture.mesure import evaluation

    assert "aveugle" in evaluation.JEUX_FERMES and "aveugle" in evaluation.JEUX
    s, a = evaluation.fichiers_jeu(tmp_path, "assureur-a-habitation-2025", "aveugle")
    assert s == tmp_path / "aveugle" / "sinistres.jsonl" and a.parent == tmp_path / "aveugle" / "annotations"
    monkeypatch.chdir(tmp_path)
    d = tmp_path / "data" / "aveugle"
    cas = [{"id": "av-a01", "contrat": "assureur-a", "declaration": "Incendie de la cuisine.", "attendu": "COUVERT",
            "acceptables": [], "articles": ["2.1"], "citation": "c", "question_attendue": "", "theme": "base", "justification": "j"}]
    ecrire(d / "cas_agent.jsonl", cas)
    ecrire(d / "avis_second.jsonl", [{"id": "av-a01", "attendu": "COUVERT", "acceptables": []}])
    monkeypatch.setattr(ferme, "DOSSIER", ferme.DOSSIER)          # main() le change : le remettre après le test
    ferme.main(["--jeu", "aveugle", "comparer"])
    ferme.main(["--jeu", "aveugle", "exporter"])
    sinistres = ferme.lire(d / "sinistres.jsonl")
    assert [x["id"] for x in sinistres] == ["av-a01"] and sinistres[0]["source"] == "aveugle"
    cas_banc, etat = banc.charger(tmp_path / "data", "assureur-a-habitation-2025", "aveugle")
    assert etat["jeu"] == "aveugle" and etat["n"] == 1
    (tmp_path / "data" / "golden").mkdir()
    ecrire(tmp_path / "data" / "golden" / "sinistres.jsonl", [])
    assert "av-a01" in {c["id"] for c in exemples.cas_de_mesure(tmp_path / "data")}
