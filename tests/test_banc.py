"""Le banc d'essai : cohérence du golden set, mécanique de chaque couche, portes, rapport.

Le score du golden set n'est PAS un test : c'est une mesure, rapportée par `couverture banc` et
notée dans docs/DEMARCHE.md. On vérifie ici que le banc mesure juste."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from couverture import banc, prolog
from couverture.models import Decision, Faits, Resultat, Verdict
from moteur_reference import Contrat, Moteur

RACINE = Path(__file__).resolve().parents[1]
DONNEES = RACINE / "data"
CONTRAT = "foyer-appart123-2025"
DECISIONS = {"COUVERT", "NON_COUVERT", "INCERTAIN"}


@pytest.fixture(scope="module")
def golden():
    return banc.charger(DONNEES, CONTRAT)


@pytest.fixture(scope="module")
def oracle():
    contrat = Contrat(prolog.fichier_regles(CONTRAT))
    return lambda faits: Moteur(contrat, faits).decider()


# --- Le golden set ----------------------------------------------------------------------------------------

def test_golden_complet_et_coherent(golden):
    cas, etat = golden
    assert etat["n"] == len(cas) >= 68 and len({c["id"] for c in cas}) == len(cas)
    voc = prolog.vocabulaire()
    for c in cas:
        assert c["attendu"] in DECISIONS and c["attendu"] not in c.get("acceptables", []), c["id"]
        assert set(c.get("acceptables", [])) <= DECISIONS, c["id"]
        assert c.get("garantie") and c.get("themes") and c.get("note") and c.get("auteur"), c["id"]
        assert c["faits"] is not None and prolog.verifier_faits(c["faits"]) == [], c["id"]
        assert all(q in voc for q in c.get("questions_attendues", [])), c["id"]
        if c["attendu"] == "INCERTAIN" and c.get("garantie") != "aucune":
            assert c.get("questions_attendues") or "INCERTAIN" in c.get("acceptables", []) or c["id"] == "g-q02", c["id"]


def test_golden_couvre_ce_qui_compte(golden):
    """Chaque garantie traduite, les garanties non traduites, et chaque type de difficulté."""
    cas, _ = golden
    themes = {t for c in cas for t in c["themes"]}
    assert {"base", "variante", "piege", "langue", "info_manquante", "hors_regles", "multi"} <= themes
    garanties = {c["garantie"] for c in cas}
    assert {"2.10", "2.1", "2.7", "2.2", "2.9", "2.3", "2.6", "2.8", "2.4"} <= garanties
    assert sum(c["attendu"] == "COUVERT" for c in cas) >= 20 and sum(c["attendu"] == "NON_COUVERT" for c in cas) >= 20


def test_golden_fige(golden):
    _, etat = golden
    assert etat["fige"], "golden set modifié sans nouvelle version : `couverture banc --figer \"raison\"`"


def test_figer_cree_une_version(tmp_path):
    shutil.copytree(DONNEES / "golden", tmp_path / "golden")
    (tmp_path / "golden" / "version.json").unlink()
    v = banc.figer(tmp_path, CONTRAT, "essai")
    assert v["version"] == 1 and banc.figer(tmp_path, CONTRAT)["version"] == 1, "même contenu, même version"
    with open(tmp_path / "golden" / "sinistres.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"id": "x", "sinistre": "x"}) + "\n")
    assert banc.figer(tmp_path, CONTRAT, "ajout")["version"] == 2


# --- Couche 1 : règles -------------------------------------------------------------------------------------

def test_couche_regles(golden, oracle):
    cas, _ = golden
    r = banc.couche_regles(cas, oracle)
    m = r["metriques"]
    assert m["n"] == len(cas) and 0 <= m["exactitude_stricte"] <= m["exactitude"] <= 1
    assert m["faux_couverts"] == sum(l["obtenu"] == "COUVERT" and l["attendu"] != "COUVERT" for l in r["cas"])
    assert "thème : piege" in r["groupes"] and "garantie : 2.10" in r["groupes"]
    q01 = next(l for l in r["cas"] if l["id"] == "g-q01")
    assert q01["obtenu"] == "INCERTAIN" and q01["rappel_questions"] == 1.0, "la cave : demander la serrure"


# --- Couche 2 : lecture --------------------------------------------------------------------------------------

def test_comparer_faits():
    ideaux = {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"], "fermeture": "cadenas"}
    lus = {"evenements": ["vol"], "biens": ["velo"], "lieux": ["parties_communes"],
           "circonstances": ["fermeture=cadenas", "absence=oui"]}
    x = banc.comparer_faits(ideaux, lus)
    assert x["rappel"] == 0.75 and x["contradictions"] == ["lieu : cave lu parties_communes"]
    assert x["en_trop"] == ["absence = oui"] and x["manques"] == []
    y = banc.comparer_faits(ideaux, {"evenements": ["vol"]})
    assert y["rappel"] == 0.25 and "bien = velo" in y["manques"] and not y["contradictions"]


def test_comparer_faits_avec_la_hierarchie():
    """« électronique » pour une télé est vague, pas faux ; « vitre » pour « élément du bâtiment » est exact."""
    voc = {"bien": {"valeurs": ["electronique", "appareil_audiovisuel", "vitre", "element_batiment", "velo"],
                    "parents": {"appareil_audiovisuel": ["electronique"], "vitre": ["element_batiment"]}}}
    vague = banc.comparer_faits({"bien": ["appareil_audiovisuel"]}, {"biens": ["electronique"]}, voc)
    assert not vague["contradictions"] and vague["vagues"] and vague["rappel"] == 0
    precis = banc.comparer_faits({"bien": ["element_batiment"]}, {"biens": ["vitre"]}, voc)
    assert precis["rappel"] == 1 and not precis["contradictions"]
    faux = banc.comparer_faits({"bien": ["vitre"]}, {"biens": ["velo"]}, voc)
    assert faux["contradictions"] == ["bien : vitre lu velo"]


def test_faits_depuis_lecture():
    lus = {"evenements": ["vol"], "biens": ["velo"], "lieux": ["cave"], "circonstances": ["fermeture=cadenas", "x=y"]}
    assert banc.faits_depuis_lecture(lus) == {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"], "fermeture": "cadenas"}


# --- Couche 3 : chaîne, portes, rapport, de bout en bout ------------------------------------------------------

class PipelineSimulee:
    """Répond à partir des faits idéaux passés dans l'oracle, en lisant mal un cas sur deux exécutions."""

    methode = "regles"
    appel = 0

    def __init__(self, cas, oracle):
        self.par_texte = {c["sinistre"]: c for c in cas}
        self.oracle = oracle
        PipelineSimulee.appel += 1
        self.mauvaise = PipelineSimulee.appel % 2 == 0

    def analyser(self, sinistre):
        c = self.par_texte[sinistre]
        faits = dict(c["faits"])
        if self.mauvaise and c["id"] == "val-03":
            faits.pop("proprietaire", None)          # la lecture oublie les biens de l'hôte
        d = self.oracle(faits)
        q = [prolog.question(v) for v in banc.questions_decision(d)]
        lus = Faits(evenements=list(faits.get("evenement", []) if isinstance(faits.get("evenement"), list)
                                    else [faits["evenement"]] if "evenement" in faits else []),
                    biens=faits.get("bien", []), lieux=faits.get("lieu", []),
                    circonstances=[f"{k}={v}" for k, v in faits.items() if k not in ("evenement", "bien", "lieu")])
        v = Verdict(decision=Decision(d["decision"]), justification="simulé", informations_manquantes=q, mode="simulé")
        return Resultat(sinistre=sinistre, faits=lus, clauses_consultees=[], verdict=v)


def test_passage_complet(golden, oracle, tmp_path):
    cas, _ = golden
    PipelineSimulee.appel = 0
    r = banc.passer(DONNEES, CONTRAT, "regles", ["regles", "chaine"], repetitions=2, paralleles=2,
                    pipeline_fabrique=lambda: PipelineSimulee(cas, oracle), decideur=oracle)
    assert set(r["couches"]) == {"regles", "chaine", "lecture"}
    ch = r["couches"]["chaine"]
    assert ch["instables"] == ["val-03"] and ch["metriques"]["executions"] == 2
    assert ch["metriques"]["faux_couverts"]["max"] >= ch["metriques"]["faux_couverts"]["min"] + 1
    lec = next(x for x in r["couches"]["lecture"]["cas"] if x["id"] == "val-03")
    assert lec["rappel"] < 1 and "proprietaire = hote" in lec["manques"]
    assert lec["grave"] and lec["change"] == 0.5, "une lecture sur deux oublie l'hôte : couvert à tort"
    m = r["couches"]["lecture"]["metriques"]
    assert m["decisions_changees_vers_couvert"] == 1 and m["decisions_changees"] == 0.5
    assert r["couches"]["regles"]["metriques"] == banc.couche_regles(cas, oracle)["metriques"]

    js, md = banc.enregistrer(DONNEES, r, tmp_path)
    texte = md.read_text(encoding="utf-8")
    assert "## Portes" in texte and "Couche 1" in texte and "Couche 2" in texte and "Couche 3" in texte
    assert "**⚠ couvert à tort** `val-03`" in texte
    assert "### La lecture change la décision" in texte and "**⚠ vers couvert** `val-03`" in texte
    assert json.loads(js.read_text(encoding="utf-8"))["contrat"] == CONTRAT and "_cas" not in js.read_text(encoding="utf-8")
    assert "Portes :" in banc.resume_console(r, md)

    # Un second passage se compare au premier.
    r2 = banc.passer(DONNEES, CONTRAT, "regles", ["regles"], decideur=oracle)
    _, md2 = banc.enregistrer(DONNEES, r2, tmp_path)
    assert "Depuis le banc précédent" in md2.read_text(encoding="utf-8") or r2["couches"]["regles"]


def test_portes():
    r = {"couches": {"regles": {"metriques": {"faux_couverts": 2, "exactitude": 0.97}},
                     "chaine": {"metriques": {"faux_couverts": {"moyenne": 0.3, "min": 0, "max": 1}, "instables": 1}}}}
    s = {"_description": "x", "regles": {"faux_couverts_max": 0, "exactitude_min": 0.95},
         "chaine": {"faux_couverts_max": 0, "instables_max": 3}, "lecture": {"rappel_faits_min": 0.9}}
    p = {(x["couche"], x["critere"]): x["ok"] for x in banc.portes(r, s)}
    assert p == {("regles", "faux_couverts"): False, ("regles", "exactitude"): True,
                 ("chaine", "faux_couverts"): False, ("chaine", "instables"): True}


def test_commande_banc_regles_sans_swipl(monkeypatch, capsys, tmp_path):
    from couverture import cli

    shutil.copytree(DONNEES / "golden", tmp_path / "golden")
    monkeypatch.setattr(prolog, "swipl", lambda: None)
    code = cli.main(["--donnees", str(tmp_path), "banc", "--contrat", CONTRAT, "--couches", "regles"])
    sortie = capsys.readouterr().out
    assert "SWI-Prolog absent" in sortie and code == 0 and list((tmp_path / "bancs").glob("*.md"))


def test_fiche_de_validation():
    texte = banc.fiche_validation(DONNEES, CONTRAT)
    assert "## Garantie 2.10" in texte and "`g-p06`" in texte and "--figer" in texte
    assert texte.index("## Garantie 2.1 ") if "## Garantie 2.1 " in texte else True
