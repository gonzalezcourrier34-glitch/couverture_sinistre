"""Méthode « regles » : règles Prolog d'un contrat, moteur, lecture des faits, mise en forme.

Sans SWI-Prolog, les règles sont vérifiées par une seconde implémentation du moteur en Python
(tests/moteur_reference.py). Avec SWI-Prolog, un test différentiel vérifie que les deux moteurs
donnent les mêmes réponses sur tous les cas."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from couverture import prolog
from couverture.models import Decision
from moteur_reference import Contrat, Moteur, Terme

RACINE = Path(__file__).resolve().parents[1]
CONTRAT = "foyer-appart123-2025"
REGLES = RACINE / "regles" / f"{CONTRAT}.pl"
CAS = RACINE / "regles" / "cas" / f"{CONTRAT}.jsonl"
ANNOTATIONS = RACINE / "data" / "annotations" / f"{CONTRAT}.jsonl"


def lire(chemin):
    return [json.loads(l) for l in chemin.read_text(encoding="utf-8").splitlines() if l.strip()]


@pytest.fixture(scope="module")
def contrat():
    return Contrat(REGLES)


@pytest.fixture(scope="module")
def cas():
    attendus = {a["sinistre_id"]: a for a in lire(ANNOTATIONS)}
    return [(c["sinistre_id"], c["faits"], attendus[c["sinistre_id"]]) for c in lire(CAS)]


# --- Les règles, par l'oracle Python ----------------------------------------------------------------

def test_regles_sur_les_faits_ideaux(contrat, cas):
    """Les règles seules : aucune erreur coûteuse, et les deux couverts à tort des fiches corrigés."""
    obtenus = {i: Moteur(contrat, faits).decider()["decision"] for i, faits, _ in cas}
    for i, _, a in cas:
        assert obtenus[i] in [a["attendu"], *a.get("acceptables", [])], f"{i} : {obtenus[i]} au lieu de {a['attendu']}"
    assert obtenus["velo-03"] == "NON_COUVERT", "cave fermée au cadenas : la serrure de sûreté exclut le cadenas"
    assert obtenus["bougie-04"] == "NON_COUVERT", "le contenu ne comprend pas le contenu du jardin"
    assert sum(obtenus[i] == a["attendu"] for i, _, a in cas) >= 13


def test_trois_valeurs_et_questions(contrat):
    garage = Moteur(contrat, {"evenement": "vol", "bien": ["velo"], "lieu": ["garage"], "fermeture": "cle",
                              "effraction": "oui"}).decider()
    assert garage["decision"] == "INCERTAIN" and garage["retenues"][0]["questions"] == ["serrure_surete"]
    # Un lieu inconnu n'est pas un « non » : la garantie reste possible, et on demande où.
    sans_lieu = Moteur(contrat, {"evenement": "vol", "bien": ["velo"]}).decider()
    assert sans_lieu["decision"] == "INCERTAIN"
    assert any("lieu" in r["questions"] for r in sans_lieu["retenues"])
    # L'effraction excuse le non-respect de l'obligation de fermeture (« sans incidence »).
    absent = {"evenement": "vol", "bien": ["velo"], "lieu": ["logement"], "absence": "oui", "portes_fermees": "non"}
    assert Moteur(contrat, absent).decider()["decision"] == "INCERTAIN", "lien causal à apprécier"
    assert Moteur(contrat, {**absent, "effraction": "oui"}).decider()["decision"] == "COUVERT"


def test_exclusion_partielle(contrat):
    r = Moteur(contrat, {"evenement": "degat_eaux", "bien": ["mobilier", "canalisation"], "lieu": ["logement"]}).decider()
    assert r["decision"] == "COUVERT" and r["retenues"][0]["partielles"] == ["canalisation"]
    seul = Moteur(contrat, {"evenement": "degat_eaux", "bien": ["canalisation"], "lieu": ["logement"]}).decider()
    assert seul["decision"] == "NON_COUVERT", "si seul le bien exclu est touché, l'exclusion est totale"


def test_regles_dans_le_vocabulaire(contrat):
    voc = prolog.vocabulaire()

    def feuilles(t):
        if isinstance(t, Terme):
            if t.nom == "f":
                yield t.args
            for a in t.args:
                yield from feuilles(a)
        elif isinstance(t, list):
            for a in t:
                yield from feuilles(a)

    employes = {(v, x) for f in contrat.faits for v, x in feuilles(f)}
    employes |= {("bien", x.args[2].args[0]) for x in contrat.regles("exclusion", 6) if isinstance(x.args[2], Terme)}
    hors = [(v, x) for v, x in employes if v not in voc or x not in voc[v]["valeurs"]]
    assert employes and not hors, hors


def test_faits_des_cas_dans_le_vocabulaire(cas):
    for i, faits, _ in cas:
        assert prolog.verifier_faits(faits) == [], i


# --- Le pont Python ------------------------------------------------------------------------------------

def test_but_prolog_sans_injection():
    b = prolog.but({"evenement": "vol", "lieu": ["cave", "garage"]})
    assert "assertz(fait(lieu, cave))" in b and "assertz(fait(lieu, garage))" in b and "decider_json" in b
    with pytest.raises(prolog.ErreurRegles):
        prolog.but({"lieu": "cave)), halt, (true"})
    assert prolog.verifier_faits({"lieu": "lune"}) == ["lieu = lune : valeur non permise"]
    assert prolog.verifier_faits({"evenement": ["vol", "incendie"]})[0].startswith("evenement n'admet qu'une valeur")


class FauxLLM:
    nom = "faux"

    def __init__(self, faits):
        self.faits = faits

    def completer(self, systeme, message):
        assert "Vocabulaire" in message and "parties_communes" in message, "le modèle reçoit le vocabulaire"
        return json.dumps({"faits": self.faits})


def test_lecture_des_faits_filtre_le_hors_vocabulaire():
    faits, ecarts = prolog.extraire_faits_regles(
        "Vélo volé dans le local commun.",
        FauxLLM({"evenement": "vol", "bien": "velo", "lieu": ["parties_communes", "lune"], "couleur": "rouge",
                 "effraction": None}))
    assert faits == {"evenement": "vol", "bien": ["velo"], "lieu": ["parties_communes"]}
    assert len(ecarts) == 2


def test_verdict_mis_en_forme():
    """La forme de ce que renvoie moteur.pl (decider_json), mise en verdict : preuves, questions, confiance."""
    reponse = {"decision": "NON_COUVERT", "possibles": [], "retenues": [{
        "id": "vol_batiment", "garantie": "Vol du contenu dans le bâtiment", "article": "2.10",
        "rattachement": "rattachée", "decision": "NON_COUVERT", "motif": "une exclusion s'applique",
        "preuves": [{"article": "2.10-a", "texte": "le vol ou le vandalisme dans les parties communes du bâtiment",
                     "role": "exclusion"}], "questions": [], "reserves": [], "partielles": []}]}
    p = prolog.PipelineRegles(CONTRAT, [], FauxLLM({"evenement": "vol", "lieu": ["parties_communes"]}),
                              decideur=lambda faits: reponse)
    r = p.analyser("Vélo volé dans le local commun.")
    v = r.verdict
    assert v.decision == Decision.INCERTAIN, "sans les clauses en base, la citation ne se vérifie pas : prudence"
    assert r.faits.lieux == ["parties_communes"]

    from couverture.models import Clause, TypeClause
    clause = Clause(id="2.10-a", article="2.10-a", titre="Exclusions", chemin=["2.10-a"], type=TypeClause.EXCLUSION,
                    texte="nous ne garantissons pas : • le vol ou le vandalisme dans les parties communes du bâtiment",
                    pages=[12])
    p = prolog.PipelineRegles(CONTRAT, [clause], FauxLLM({"evenement": "vol"}), decideur=lambda faits: reponse)
    v = p.analyser("Vélo volé dans le local commun.").verdict
    assert v.decision == Decision.NON_COUVERT and v.citations[0].valide and v.citations[0].pages == [12]
    assert "2.10-a" not in v.justification or "exclusion" in v.justification


# --- Avec SWI-Prolog : les deux moteurs doivent concorder ------------------------------------------------

avec_swipl = pytest.mark.skipif(prolog.swipl() is None, reason="SWI-Prolog absent")


@avec_swipl
def test_prolog_et_oracle_concordent(contrat, cas):
    for i, faits, _ in cas:
        p = prolog.decider(CONTRAT, faits)
        o = Moteur(contrat, faits).decider()
        assert p["decision"] == o["decision"], i
        assert [r["id"] for r in p["retenues"]] == [r["id"] for r in o["retenues"]], i


@avec_swipl
def test_prolog_charge_sans_avertissement():
    assert prolog.executer(CONTRAT, "vocabulaire_json")
    assert len(prolog.executer(CONTRAT, "citations_json")) >= 30


def test_commande_regles_sans_swipl(monkeypatch, capsys, tmp_path):
    from couverture import cli

    monkeypatch.setattr(prolog, "swipl", lambda: None)
    assert cli.main(["--donnees", str(tmp_path), "regles", "--contrat", CONTRAT]) == 1
    assert "winget install SWI-Prolog" in capsys.readouterr().out
