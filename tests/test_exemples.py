"""La banque d'exemples de lecture et le partage mise au point / test (DEMARCHE 7.107), sans appel au modèle."""

import json
import shutil
from pathlib import Path

import pytest

from couverture import exemples, lecture

DONNEES = Path(__file__).resolve().parents[1] / "data"


@pytest.fixture
def donnees(tmp_path):
    (tmp_path / "golden").mkdir()
    shutil.copy(DONNEES / "golden" / "sinistres.jsonl", tmp_path / "golden" / "sinistres.jsonl")
    return tmp_path


def test_le_tirage_ne_depend_que_de_l_identifiant():
    assert exemples.tirage("velo-01") == exemples.tirage("velo-01")
    cotes = [exemples.tirage(f"cas-{i}") for i in range(1000)]
    assert 0.25 < cotes.count("test") / 1000 < 0.35


def test_le_partage_fige_ne_deplace_aucun_cas(donnees):
    p = exemples.partager(donnees)
    assert p["test"] and p["mise_au_point"] and not set(p["test"]) & set(p["mise_au_point"])
    # Un cas déplacé à la main reste où on l'a mis : un nouveau partage n'y touche pas.
    deplace = p["test"][0]
    p["test"].remove(deplace)
    p["mise_au_point"].append(deplace)
    exemples.chemin_partage(donnees).write_text(json.dumps(p), encoding="utf-8")
    assert deplace in exemples.partager(donnees)["mise_au_point"]


def test_le_partage_versionne_couvre_tout_le_golden_set():
    p = exemples.charger_partage(DONNEES)
    ids = {c["id"] for c in exemples.cas_golden(DONNEES)}
    assert ids == set(p["test"]) | set(p["mise_au_point"])


def test_la_banque_ne_contient_jamais_un_cas_de_test(donnees):
    p = exemples.partager(donnees)
    b = exemples.banque(donnees)
    assert b and not {x["id"] for x in b} & set(p["test"])
    assert all("faits" in x and "declaration" in x for x in b)


def test_filtrer_refuse_un_cas_hors_partage(donnees):
    exemples.partager(donnees)
    cas = [{"id": "inconnu-01"}]
    with pytest.raises(ValueError):
        exemples.filtrer(cas, donnees, "test")
    assert exemples.filtrer(cas, donnees, "tout") == cas


def ex(i, v, evts=("vol",)):
    return {"id": i, "vecteur": v, "evenements": list(evts)}


def test_choisir_garde_le_seuil_l_evenement_et_la_diversite():
    q = [1.0, 0.0, 0.0]
    banque = [ex("a", [1.0, 0.0, 0.0]), ex("a-bis", [0.99, 0.01, 0.0]), ex("b", [0.9, 0.44, 0.0]),
              ex("loin", [0.0, 1.0, 0.0]), ex("eau", [1.0, 0.0, 0.0], ("degat_eaux",))]
    ids = [x["id"] for x, _ in exemples.choisir(q, banque, k=2, seuil=0.8, diversite=0.3, evenement="vol")]
    # le plus proche, puis celui qui apporte autre chose (pas son quasi-doublon) ; ni le lointain ni un autre événement
    assert ids == ["a", "b"]
    assert exemples.choisir(q, [ex("loin", [0.0, 1.0, 0.0])], seuil=0.8) == []


def test_indexer_ne_recalcule_que_ce_qui_a_change(donnees, tmp_path):
    exemples.partager(donnees)
    appels = []

    def embed(textes):
        appels.append(len(textes))
        return [[float(len(t)), 1.0, 0.0] for t in textes]

    base = tmp_path / "base.sqlite"
    n = exemples.indexer(base, donnees, embed)
    assert n["calcules"] == n["exemples"] > 0
    assert exemples.indexer(base, donnees, embed)["calcules"] == 0
    assert len(appels) == 1
    index = exemples.charger_index(base)
    assert len(index) == n["exemples"] and len(index[0]["vecteur"]) == 3
    proches = exemples.proches(index[0]["declaration"], base, embed, k=1, seuil=0.0)
    assert proches and proches[0][1] == pytest.approx(1.0, abs=1e-6)


def test_les_exemples_vont_aux_details_du_meme_evenement(monkeypatch):
    """7.108, 7.116 : les détails reçoivent les exemples du même événement, réduits aux variables de l'appel ; le
    socle n'en reçoit plus (Small y recopiait les biens des exemples). Sans exemples, les messages restent ceux
    d'avant."""

    class Modele:
        nom, accepte_schema = "schema", True

        def __init__(self):
            self.appels = []

        def completer(self, systeme, message, schema=None):
            self.appels.append(message)
            if len(self.appels) == 1:
                return json.dumps({"faits": {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"]}})
            return json.dumps({"faits": {"fermeture": "cadenas"}})

    vus = []

    def choix(evenement=None):
        vus.append(evenement)
        return [{"declaration": "Mon vélo a été volé dans ma cave fermée à clé.",
                 "faits": {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"], "fermeture": "cle",
                           "cause_eau": "gel"}}]

    m = Modele()
    lecture.extraire_faits_regles("On m'a volé mon vélo dans ma cave fermée par un cadenas.", m, exemples=choix, verifier=False)
    socle, details = m.appels
    assert vus == ["vol"]
    assert "## Exemples" not in socle
    assert "fermeture = cle" in details and "cause_eau = gel" not in details
    m2 = Modele()
    lecture.extraire_faits_regles("On m'a volé mon vélo dans ma cave fermée par un cadenas.", m2, verifier=False)
    assert "## Exemples" not in m2.appels[0]


def test_une_declaration_n_est_jamais_son_propre_exemple():
    class B(exemples.Banque):
        def __init__(self):
            self.index = [{"id": "a", "declaration": "Vélo volé.", "faits": {}, "evenements": ["vol"], "vecteur": [1.0, 0.0]},
                          {"id": "b", "declaration": "Vélo volé dans la cave.", "faits": {}, "evenements": ["vol"],
                           "vecteur": [0.99, 0.1]}]
            self.embed, self.k, self.seuil = (lambda t: [[1.0, 0.0]]), 3, 0.5
    assert [x["id"] for x in B().pour("Vélo volé.")()] == ["b"]
    assert B().pour("") is not None and exemples.bloc([], ("evenement",)) == ""


def test_les_exemples_sont_la_lecture_par_defaut(monkeypatch, tmp_path):
    """7.112 : les exemples sont actifs sans rien régler ; COUVERTURE_EXEMPLES=non les coupe. Sans clé ou sans
    banque indexée, la chaîne lit sans exemples, sans erreur."""
    from couverture import chaine, prolog
    from couverture.base import Base

    monkeypatch.setattr(prolog, "swipl", lambda: "swipl")
    monkeypatch.delenv("COUVERTURE_EXEMPLES", raising=False)
    assert exemples.actifs()
    monkeypatch.setenv("COUVERTURE_EXEMPLES", "non")
    assert not exemples.actifs()
    monkeypatch.delenv("COUVERTURE_EXEMPLES")

    base = Base(tmp_path / "base.sqlite")
    monkeypatch.setattr(base, "clauses", lambda contrat_id: [])
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    assert chaine.PipelineRegles.depuis_base(base, "assureur-a-habitation-2025", object()).exemples is None
    monkeypatch.setenv("MISTRAL_API_KEY", "k")
    assert chaine.PipelineRegles.depuis_base(base, "assureur-a-habitation-2025", object()).exemples is None  # banque vide
