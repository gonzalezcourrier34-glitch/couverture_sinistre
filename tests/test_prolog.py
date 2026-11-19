"""Méthode « regles » : règles Prolog d'un contrat, moteur, lecture des faits, mise en forme.

Sans SWI-Prolog, les règles sont vérifiées par une seconde implémentation du moteur en Python
(tests/moteur_reference.py). Avec SWI-Prolog, un test différentiel vérifie que les deux moteurs
donnent les mêmes réponses sur tous les cas."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from couverture import prolog
from couverture.models import Decision
from moteur_reference import Explorateur, Contrat, Moteur, Terme

RACINE = Path(__file__).resolve().parents[1]
CONTRAT = "assureur-a-habitation-2025"
REGLES = RACINE / "regles" / f"{CONTRAT}.pl"
CAS = RACINE / "regles" / "cas" / f"{CONTRAT}.jsonl"
ANNOTATIONS = RACINE / "data" / "annotations" / f"{CONTRAT}.jsonl"
CAS_VALIDATION = RACINE / "regles" / "cas" / "validation" / f"{CONTRAT}.jsonl"


def lire(chemin):
    return [json.loads(l) for l in chemin.read_text(encoding="utf-8").splitlines() if l.strip()]


@pytest.fixture(scope="module")
def contrat():
    return Contrat(REGLES)


@pytest.fixture(scope="module")
def cas():
    attendus = {a["sinistre_id"]: a for a in lire(ANNOTATIONS)}
    return [(c["sinistre_id"], c["faits"], attendus[c["sinistre_id"]]) for c in lire(CAS)]


@pytest.fixture(scope="module")
def cas_validation():
    from couverture.evaluation import fichiers_jeu

    _, annotations = fichiers_jeu(RACINE / "data", CONTRAT, "validation")
    attendus = {a["sinistre_id"]: a for a in lire(annotations)}
    return [(c["sinistre_id"], c["faits"], attendus[c["sinistre_id"]]) for c in lire(CAS_VALIDATION)]


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


def contrat_sans(tmp_path, *articles):
    """Le contrat Assureur A sans les articles donnés : un test qui a besoin d'une garantie non traduite la retire
    lui-même, au lieu de dépendre de l'avancement des traductions (7.63)."""
    from couverture import redaction
    texte = prolog.fichier_regles(CONTRAT).read_text(encoding="utf-8")
    for a in articles:
        texte = redaction.retirer_article(texte, a)
    f = tmp_path / "contrat.pl"
    f.write_text(texte, encoding="utf-8")
    return Contrat(f)


def test_extension_de_definition(tmp_path):
    """7.69 : « nous étendons la garantie au contenu lors d'un séjour temporaire » élargit le lieu assuré pour
    toutes les garanties qui l'emploient. L'extension n'est jamais présumée, et n'est demandée que si la
    déclaration l'entame."""
    regles = tmp_path / "c.pl"
    regles.write_text(''':- discontiguous garantie/4, perimetre/2, circonstance/4, extension/4.
evenement_traduit(incendie).
definition(batiment, ou([f(lieu, logement), f(lieu, cave)]), '12', "les constructions à l'adresse").
extension(batiment, et([f(sejour_temporaire, oui), f(lieu, autre_batiment)]), '3.1', "le contenu lors d'un séjour temporaire").
garantie(incendie, "Incendie", '2.1', "Nous couvrons l'incendie").
perimetre(incendie, f(evenement, incendie)).
perimetre(incendie, concept(batiment)).
''', encoding="utf-8")
    contrat = Contrat(regles)
    def d(**f):
        return Moteur(contrat, {"evenement": "incendie", **f}).decider()
    assert d(lieu="logement")["decision"] == "COUVERT"
    assert d(lieu="autre_batiment", sejour_temporaire="oui")["decision"] == "COUVERT"
    assert d(lieu="autre_batiment", sejour_temporaire="non")["decision"] == "NON_COUVERT"
    assert d(lieu="autre_batiment")["decision"] == "NON_COUVERT", \
        "un autre bâtiment ne dit pas qu'on y séjourne : l'extension n'est entamée que par ses propres faits (7.71)"
    entamee = d(sejour_temporaire="oui")
    assert entamee["decision"] == "INCERTAIN" and entamee["retenues"][0]["questions"] == ["lieu"]
    inconnu = d()
    assert inconnu["retenues"][0]["questions"] == ["lieu"], "le séjour n'est pas demandé quand rien ne l'évoque"


def test_garantie_accessoire_ne_change_jamais_la_decision(tmp_path):
    """7.68 : des frais de logement provisoire ne disent pas si un incendie est couvert. Une garantie accessoire
    n'entre pas dans la décision ; si le sinistre est couvert, elle est listée, avec ses questions."""
    regles = tmp_path / "c.pl"
    regles.write_text(''':- discontiguous garantie/4, perimetre/2, circonstance/4, accessoire/1.
evenement_traduit(incendie).
garantie(incendie, "Incendie", '1', "Nous couvrons l'incendie").
perimetre(incendie, f(evenement, incendie)).
circonstance(incendie, f(flammes, oui), '1', "des flammes").
garantie(logement_provisoire, "Frais de logement provisoire", '4', "les frais de logement provisoire").
perimetre(logement_provisoire, f(evenement, incendie)).
circonstance(logement_provisoire, f(non_habitabilite, oui), '4', "si le logement est inhabitable").
accessoire(logement_provisoire).
garantie(sejour, "Extension en séjour temporaire", '3.1', "en séjour temporaire").
perimetre(sejour, f(sejour_temporaire, oui)).
accessoire(sejour).
garantie(complementaires, "Garanties complémentaires", '4', "en cas de sinistre assuré").
accessoire(complementaires).
''', encoding="utf-8")
    contrat = Contrat(regles)
    couvert = Moteur(contrat, {"evenement": ["incendie"], "flammes": "oui"}).decider()
    assert couvert["decision"] == "COUVERT" and [g["id"] for g in couvert["garanties"]] == ["incendie"]
    acc = couvert["accessoires"]
    assert [a["id"] for a in acc] == ["logement_provisoire", "complementaires"] and acc[0]["decision"] == "INCERTAIN", \
        "sans périmètre, elle suit tout sinistre couvert ; au périmètre seulement possible (le séjour), elle n'est pas listée"
    assert "non_habitabilite" in acc[0]["questions"]
    refuse = Moteur(contrat, {"evenement": ["incendie"], "flammes": "non", "non_habitabilite": "oui"}).decider()
    assert refuse["decision"] == "NON_COUVERT" and refuse["accessoires"] == [], \
        "un sinistre non couvert n'ouvre aucune garantie accessoire, même si ses conditions sont remplies"
    doute = Moteur(contrat, {"evenement": ["incendie"]}).decider()
    assert doute["decision"] == "INCERTAIN" and doute["accessoires"] == [] and doute["retenues"][0]["questions"] == ["flammes"], \
        "la question posée est celle de la garantie de base, pas celle des frais"


def test_accident_sur_une_vitre_est_un_bris():
    """7.86 : « accident » lu pour un miroir cogné devient « bris » ; un violon tombé reste un accident."""
    voc = prolog.vocabulaire()
    f, notes = prolog.au_vocabulaire({"evenement": ["accident"], "bien": ["miroir"], "lieu": ["logement"]}, voc)
    assert f["evenement"] == ["bris"] and notes
    f, _ = prolog.au_vocabulaire({"evenement": ["accident"], "bien": ["objet_divers"]}, voc)
    assert f["evenement"] == ["accident"]


def test_evenement_non_traduit_jamais_refuse(tmp_path):
    """Un événement dont la garantie n'est pas en règles (la tempête) : INCERTAIN, même si une garantie traduite
    refuse, ou couvre (7.84 : couvrir une partie du sinistre n'est pas couvrir la demande). « autre » ne compte pas."""
    contrat = contrat_sans(tmp_path, "2.2")
    tempete = {"evenement": ["tempete", "degat_eaux"], "bien": ["element_batiment"], "lieu": ["logement"],
               "cause_eau": "infiltration_exterieure"}
    d = Moteur(contrat, tempete).decider()
    assert d["decision"] == "INCERTAIN" and d["non_traduits"] == ["tempete"]
    assert Moteur(contrat, {**tempete, "evenement": ["degat_eaux"]}).decider()["decision"] == "NON_COUVERT"
    brulure = {"evenement": ["autre"], "bien": ["objet_divers"], "lieu": ["logement"], "flammes": "non", "embrasement": "non"}
    assert Moteur(contrat, brulure).decider()["decision"] == "NON_COUVERT"
    feu = {"evenement": ["incendie", "tempete"], "bien": ["mobilier"], "lieu": ["logement"], "flammes": "oui", "embrasement": "oui"}
    d = Moteur(contrat, feu).decider()
    assert d["decision"] == "INCERTAIN" and d["non_traduits"] == ["tempete"]
    assert Moteur(contrat, {**feu, "evenement": ["incendie"]}).decider()["decision"] == "COUVERT"


def test_trous_trouves_par_le_golden_v5(tmp_path):
    contrat = contrat_sans(tmp_path, "2.11", "2.12")
    """Les sept erreurs du golden v5 (DEMARCHE 7.30), une par une."""
    eau = {"evenement": ["degat_eaux"], "bien": ["element_batiment"], "lieu": ["logement"]}
    d = lambda f: Moteur(contrat, f).decider()["decision"]
    assert d({**eau, "cause_eau": "infiltration_toiture"}) == "COUVERT"          # le toit n'est pas exclu
    assert d({**eau, "cause_eau": "infiltration_exterieure"}) == "NON_COUVERT"   # la fenêtre l'est
    assert d({**eau, "cause_eau": "piscine_exterieure"}) == "NON_COUVERT"
    assert d({**eau, "cause_eau": "fuite_installation", "manque_entretien": "oui"}) == "NON_COUVERT"   # 1.4
    assert d({**eau, "cause_eau": "fuite_installation", "corrosion_visible": "oui"}) == "NON_COUVERT"
    # Inconnues, les exclusions que l'assureur doit prouver ne deviennent pas des questions.
    assert d({**eau, "cause_eau": "fuite_installation"}) == "COUVERT"
    assert d({"evenement": ["bris"], "bien": ["vitre"], "lieu": ["logement"], "intentionnel": "oui"}) == "NON_COUVERT"
    assert d({"evenement": ["vol"], "bien": ["cles"], "lieu": ["voie_publique"]}) == "COUVERT"
    assert d({"evenement": ["vol"], "bien": ["plantation"], "lieu": ["jardin"]}) == "NON_COUVERT"
    assert d({"evenement": ["vol"], "bien": ["mazout"], "lieu": ["cave"]}) == "NON_COUVERT"
    # 2.11 et 2.12 ne sont pas traduites : « à examiner », jamais « non couvert ».
    for e in ("vandalisme", "merule"):
        assert d({**eau, "evenement": [e]}) == "INCERTAIN"


def test_garanties_hors_sujet_ne_posent_pas_de_question(contrat):
    """Pas de question sur les flammes pour une tempête ; pas de « vol commis sur vous ? » pour un garage."""
    eau = Moteur(contrat, {"evenement": ["degat_eaux"], "bien": ["element_batiment"], "lieu": ["logement"]}).decider()
    assert next(g for g in eau["garanties"] if g["id"] == "incendie")["rattachement"] == "hors"
    scooter = Moteur(contrat, {"evenement": "vol", "bien": ["vehicule_moteur"], "lieu": ["garage"],
                               "effraction": "oui"}).decider()
    assert scooter["decision"] == "NON_COUVERT" and not scooter["possibles"]
    rue = Moteur(contrat, {"evenement": "vol", "bien": ["electronique"], "lieu": ["voie_publique"]}).decider()
    assert rue["decision"] == "INCERTAIN" and "vol_sur_personne" in rue["retenues"][0]["questions"]


def test_obligations_fenetres_et_gel(contrat):
    fenetre = {"evenement": "vol", "bien": ["electronique"], "lieu": ["logement"], "absence": "oui",
               "portes_fermees": "oui", "fenetres_fermees": "non", "effraction": "non"}
    d = Moteur(contrat, fenetre).decider()
    assert d["decision"] == "INCERTAIN" and d["retenues"][0]["questions"] == ["lien_causal"]
    assert Moteur(contrat, {**fenetre, "effraction": "oui"}).decider()["decision"] == "COUVERT", "l'effraction excuse"
    gel = {"evenement": "degat_eaux", "bien": ["element_batiment"], "lieu": ["logement"], "cause_eau": "gel"}
    assert Moteur(contrat, {**gel, "prevention_gel": "non"}).decider()["decision"] == "NON_COUVERT"
    # Le gel est établi, la prévention inconnue : l'exclusion est « entamée », on pose la question (7.58).
    # Avant, la réponse était « couvert sous réserve » ; le golden set (g2-i06) attend la question.
    d = Moteur(contrat, gel).decider()
    assert d["decision"] == "INCERTAIN" and d["retenues"][0]["questions"] == ["prevention_gel"]
    # Rien ne dit que l'eau vient du gel : l'exclusion n'est pas évoquée, elle reste une réserve.
    fuite = {"evenement": "degat_eaux", "bien": ["element_batiment"], "lieu": ["logement"]}
    d = Moteur(contrat, fuite).decider()
    assert d["decision"] == "COUVERT" and "cause_eau" in d["retenues"][0]["reserves"]


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


def test_jeu_de_validation_coherent(cas, cas_validation):
    """Le jeu de validation est complet et distinct de la mise au point. Son score n'est PAS un test :
    c'est une mesure (docs/DEMARCHE.md), et corriger les règles pour la faire monter la viderait de son sens."""
    from couverture.evaluation import charger_cas, fichiers_jeu

    sinistres = charger_cas(*fichiers_jeu(RACINE / "data", CONTRAT, "validation"))
    assert len(sinistres) >= 15 and {s["id"] for s in sinistres} == {i for i, _, _ in cas_validation}
    assert not {i for i, _, _ in cas} & {i for i, _, _ in cas_validation}
    for i, faits, _ in cas_validation:
        assert prolog.verifier_faits(faits) == [], i
    with pytest.raises(ValueError):
        fichiers_jeu(RACINE / "data", CONTRAT, "autre")


# --- Le pont Python ------------------------------------------------------------------------------------

def test_but_prolog_sans_injection():
    b = prolog.but({"evenement": "vol", "lieu": ["cave", "garage"]})
    assert "assertz(fait(lieu, cave))" in b and "assertz(fait(lieu, garage))" in b and "decider_json" in b
    with pytest.raises(prolog.ErreurRegles):
        prolog.but({"lieu": "cave)), halt, (true"})
    assert prolog.verifier_faits({"lieu": "lune"}) == ["lieu = lune : valeur non permise"]
    assert prolog.verifier_faits({"effraction": ["oui", "non"]})[0].startswith("effraction n'admet qu'une valeur")
    assert prolog.verifier_faits({"evenement": ["tempete", "degat_eaux"]}) == [], "la cause et le dommage"


class FauxLLM:
    nom = "faux"

    def __init__(self, faits):
        self.faits = faits

    def completer(self, systeme, message):
        if systeme == prolog.SYSTEME_VERIFICATION:  # la vérification ne retire rien ici
            return json.dumps({"verdicts": {}})
        assert "Vocabulaire" in message, "le modèle reçoit le vocabulaire"
        return json.dumps({"faits": self.faits})


def test_lecture_des_faits_filtre_le_hors_vocabulaire():
    faits, ecarts = prolog.extraire_faits_regles(
        "Vélo volé dans le local commun.",
        FauxLLM({"evenement": "vol", "bien": "velo", "lieu": ["parties_communes", "lune"], "couleur": "rouge",
                 "effraction": None}))
    assert faits == {"evenement": ["vol"], "bien": ["velo"], "lieu": ["parties_communes"]}
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


def test_verdict_evenement_non_traduit():
    reponse = {"decision": "INCERTAIN", "non_traduits": ["tempete"], "aucune": False, "possibles": [], "retenues": [{
        "id": "degats_eaux", "garantie": "Dégâts causés par l’eau", "article": "2.7", "rattachement": "rattachée",
        "decision": "NON_COUVERT", "motif": "une exclusion s'applique", "preuves": [], "questions": [],
        "reserves": [], "partielles": []}]}
    p = prolog.PipelineRegles(CONTRAT, [], FauxLLM({"evenement": ["tempete", "degat_eaux"]}), decideur=lambda f: reponse)
    v = p.analyser("La tempête a fait entrer la pluie.").verdict
    assert v.decision == Decision.INCERTAIN and v.confiance <= 0.3
    assert "tempete" in v.justification and "pas encore traduite" in v.justification


# --- Avec SWI-Prolog : les deux moteurs doivent concorder ------------------------------------------------

avec_swipl = pytest.mark.skipif(prolog.swipl() is None, reason="SWI-Prolog absent")


@avec_swipl
def test_prolog_et_oracle_concordent(contrat, cas, cas_validation):
    """Les deux moteurs, sur tous les cas (golden set compris) : même décision, mêmes garanties retenues,
    et le même raisonnement par hypothèses (questions, effets, issues, ensemble qui tranche)."""
    golden = [(d["sinistre_id"], d["faits"], None)
              for d in lire(RACINE / "regles" / "cas" / "golden" / f"{CONTRAT}.jsonl")]
    for i, faits, _ in cas + cas_validation + golden:
        p = prolog.decider(CONTRAT, faits)
        o = Explorateur(contrat, faits).decider()
        assert p["decision"] == o["decision"], i
        assert [r["id"] for r in p["retenues"]] == [r["id"] for r in o["retenues"]], i
        assert p.get("exploration") == o.get("exploration"), i
        assert p["preuve"] == o["preuve"], i


@avec_swipl
def test_prolog_charge_sans_avertissement():
    assert prolog.executer(CONTRAT, "vocabulaire_json")
    assert len(prolog.executer(CONTRAT, "citations_json")) >= 30


def test_commande_regles_sans_swipl(monkeypatch, capsys, tmp_path):
    from couverture import cli

    monkeypatch.setattr(prolog, "swipl", lambda: None)
    assert cli.main(["--donnees", str(tmp_path), "regles", "--contrat", CONTRAT]) == 1
    assert "winget install SWI-Prolog" in capsys.readouterr().out


def clauses_dispersees(chemin: Path) -> list[str]:
    """Les prédicats dont les clauses ne se suivent pas (SWI-Prolog le signale par un avertissement, que
    `prolog.executer` traite comme une erreur), hors ceux déclarés `discontiguous`. Ce test le voit sans SWI-Prolog."""
    import re

    texte = chemin.read_text(encoding="utf-8")
    declares = set(re.findall(r"(\w+)/\d+", " ".join(re.findall(r":- discontiguous ([^.]*)\.", texte, re.S))))
    vus, precedent, disperses = set(), None, []
    for ligne in texte.splitlines():
        m = re.match(r"^([a-z]\w*)\s*(\(|:-|\.)", ligne)
        if not m:
            continue
        nom = m.group(1)
        if nom != precedent and nom in vus and nom not in declares:
            disperses.append(nom)
        vus.add(nom)
        precedent = nom
    return disperses


def test_clauses_groupees_sans_swipl():
    """La faute du 17 nov. : `ancetre` et `vague` insérés au milieu des clauses de `eval`."""
    assert clauses_dispersees(prolog.MOTEUR) == []
    assert clauses_dispersees(REGLES) == []


# --- Lecture v3 : le sens des valeurs, et les faits hors sujet retirés (7.24) ---------------------------------

def test_faits_hors_sujet_retires():
    lus = {"evenement": ["incendie"], "bien": ["mobilier"], "cause_eau": "fuite_installation",
           "type_dommage": "bris", "flammes": "oui", "absence": "oui"}
    gardes, retires = prolog.filtrer_faits(lus)
    assert gardes == {"evenement": ["incendie"], "bien": ["mobilier"], "flammes": "oui", "absence": "oui"}
    assert len(retires) == 2 and all("hors sujet" in r for r in retires)
    assert prolog.filtrer_faits({"bien": ["velo"], "cause_eau": "gel"})[1] == [], "sans événement lu, on ne juge pas"
    assert prolog.filtrer_faits({"evenement": ["vol", "bris"], "effraction": "oui", "vitre_placee": "oui"})[1] == []


def test_lecture_recoit_le_sens_des_valeurs():
    class Espion:
        nom = "espion"
        message = ""

        def completer(self, systeme, message):
            Espion.message += message
            return json.dumps({"faits": {"evenement": ["vol"], "bien": ["velo"], "lieu": ["parties_communes"],
                                         "cause_eau": "gel"}})

    faits, ecarts = prolog.extraire_faits_regles("Vélo volé dans le local à vélos de la résidence.", Espion())
    assert "parties_communes (locaux partagés de l'immeuble : local à vélos" in Espion.message
    assert "Où se trouvaient les biens ?" in Espion.message
    assert "cause_eau" not in faits and any("hors sujet" in e for e in ecarts)
    assert "ne donne pas de lieu" in prolog.SYSTEME_FAITS_REGLES


def test_un_contrat_ne_lit_que_ses_variables(tmp_path, monkeypatch):
    """Étanchéité entre assureurs (7.57) : une variable ajoutée pour Assureur B (« plainte déposée ») n'entre pas dans
    la lecture d'un vol chez Assureur A, dont les règles ne l'emploient pas."""
    contrat_a = prolog.variables_du_contrat("assureur-a-habitation-2025")
    assert {"effraction", "cles_a_proximite", "serrure_surete"} <= contrat_a
    regles = tmp_path / "x.pl"
    regles.write_text("% f(commentaire, oui)\n/* f(bloc, oui) */\nperimetre(g, f(effraction, oui)).\n", encoding="utf-8")
    monkeypatch.setattr(prolog, "fichier_regles", lambda c: regles)
    assert prolog.variables_du_contrat("x") == {"effraction"}

    class Espion:
        nom = "espion"
        messages = []

        def completer(self, systeme, message):
            Espion.messages.append(message)
            return json.dumps({"faits": {"evenement": ["vol"], "violence": "oui"}})

    monkeypatch.setenv("COUVERTURE_LECTURE", "deux_temps")
    faits, _ = prolog.extraire_faits_regles("On m'a volé mon vélo.", Espion(), variables={"effraction"})
    detail = Espion.messages[-1].split("## Déjà établi")[0]
    assert "effraction" in detail and "violence" not in detail and "violence" not in faits


def test_consigne_de_lecture_garde_ses_regles():
    """La v3 avait perdu « une pièce du logement → lieu = logement » en en ajoutant une autre : dix cas
    couverts sont devenus incertains (DEMARCHE 7.24 bis). Les règles qui ont fait leurs preuves restent."""
    c = prolog.SYSTEME_FAITS_REGLES
    for regle in ("lieu = logement", "fermeture = cle", "flammes = oui et embrasement = oui", "vol_sur_personne = oui",
                  "depot_moins_30j = oui", "prevention_gel = non", "bien = element_batiment", "bien = canalisation", "[\"tempete\", \"degat_eaux\"]"):
        assert regle in c, regle


def test_golden_conforme_au_filtre():
    for l in (RACINE / "regles" / "cas" / "golden" / f"{CONTRAT}.jsonl").read_text(encoding="utf-8").splitlines():
        d = json.loads(l)
        assert prolog.filtrer_faits(d["faits"])[1] == [], d["sinistre_id"]


# --- Les quatre phrases du contrat qui manquaient (7.25) ------------------------------------------------------

def test_cle_recipient_fumee_casier(contrat):
    vol = {"evenement": ["vol"], "bien": ["objet_divers"], "lieu": ["logement"], "absence": "oui", "portes_fermees": "oui"}
    d = Moteur(contrat, {**vol, "effraction": "non", "cles_a_proximite": "oui"}).decider()
    assert d["decision"] == "INCERTAIN" and "lien_causal" in d["retenues"][0]["questions"], "clé sous le paillasson"
    assert Moteur(contrat, {**vol, "effraction": "oui", "cles_a_proximite": "oui"}).decider()["decision"] == "COUVERT", \
        "l'effraction excuse"
    eau = {"evenement": ["degat_eaux"], "bien": ["element_batiment"], "lieu": ["logement"]}
    assert Moteur(contrat, {**eau, "cause_eau": "debordement_recipient"}).decider()["decision"] == "NON_COUVERT"
    assert Moteur(contrat, {**eau, "cause_eau": "debordement_aquarium"}).decider()["decision"] == "COUVERT"
    fumee = {"evenement": ["fumee"], "bien": ["element_batiment"], "lieu": ["logement"], "flammes": "oui", "embrasement": "non"}
    assert Moteur(contrat, fumee).decider()["decision"] == "COUVERT", "2.1 : suie et fumée, sans incendie"
    casier = Moteur(contrat, {"evenement": ["vol"], "bien": ["velo"], "lieu": ["casier"]}).decider()
    assert casier["decision"] == "NON_COUVERT" and not casier["possibles"], \
        "exclusion certaine : pas de question « commis sur vous ? »"


# --- Le raisonnement par hypothèses (Prolog, explorer/2 ; miroir : Explorateur) ---------------------------------

def test_question_decisive_et_paire(contrat):
    garage = {"evenement": "vol", "bien": ["velo"], "lieu": ["garage"], "fermeture": "cle", "effraction": "oui"}
    e = Explorateur(contrat, garage).decider()["exploration"]
    assert e["ensemble"] == ["serrure_surete"]
    q = e["questions"][0]
    assert q["effet"] == "décisive" and q["issues"] == [{"decision": "COUVERT", "valeurs": ["oui"]},
                                                        {"decision": "NON_COUVERT", "valeurs": ["non"]}]
    cave = Explorateur(contrat, {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"]}).decider()["exploration"]
    assert cave["ensemble"] == ["fermeture", "serrure_surete"], "aucune seule ne suffit, la paire tranche"


def test_questions_inutiles_retirees(contrat):
    disparu = Explorateur(contrat, {"bien": ["electronique"], "lieu": ["logement"]}).decider()["exploration"]
    effets = {q["variable"]: q["effet"] for q in disparu["questions"]}
    assert effets.get("flammes") == "inutile", "pour un ordinateur disparu, les flammes ne changent rien"
    assert [q["effet"] for q in disparu["questions"]] == sorted((q["effet"] for q in disparu["questions"]),
                                                               key=lambda e: ["décisive", "utile", "inutile"].index(e))


def test_verdict_avec_exploration():
    exploration = {"ensemble": ["serrure_surete"], "questions": [
        {"variable": "serrure_surete", "effet": "décisive",
         "issues": [{"decision": "COUVERT", "valeurs": ["oui"]}, {"decision": "NON_COUVERT", "valeurs": ["non"]}]},
        {"variable": "flammes", "effet": "inutile", "issues": [{"decision": "INCERTAIN", "valeurs": ["non", "oui"]}]}]}
    lignes, motif = prolog.questions_explorees(exploration, ["serrure_surete", "flammes", "lien_causal"], "À préciser.")
    assert lignes[0].startswith(prolog.question("serrure_surete")) and "oui → couvert ; non → non couvert" in lignes[0]
    assert prolog.question("flammes") not in " ".join(lignes), "la question inutile n'est pas posée"
    assert prolog.question("lien_causal") in lignes, "une question sans domaine reste posée"
    assert "Une seule question tranche" in motif


# --- Arbre de preuve (moteur.pl, arbres_de_preuve/2) -----------------------------------------------------

def test_arbre_de_preuve_cave_au_cadenas(contrat):
    """Le vélo dans la cave fermée au cadenas : l'arbre montre la condition non remplie, sa phrase du contrat,
    la définition de la serrure de sûreté et le fait déclaré qui la contredit."""
    d = Explorateur(contrat, {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"], "fermeture": "cadenas"}).decider()
    assert d["decision"] == "NON_COUVERT" and [g["id"] for g in d["preuve"]] == ["vol_batiment"]
    g = d["preuve"][0]
    condition = next(n for n in g["enfants"] if n["type"] == "condition" and n["etat"] == "non")
    assert condition["texte"] == "si ces locaux sont fermés avec une serrure de sûreté"
    lignes = prolog.arbre_lisible(d["preuve"])
    texte = "\n".join(lignes)
    assert lignes[0].startswith("Garantie « Vol du contenu dans le bâtiment » (art. 2.10) → non couvert")
    assert "[non] Condition non remplie — art. 2.10" in texte
    assert "serrure_de_surete (art. 12/serrure-de-surete" in texte
    assert "[oui] fermeture = cadenas (déclaré : cadenas)" in texte
    assert "sans objet ici" in texte, "la condition du garage ne s'applique pas à une cave"
    assert "l'assureur devrait les prouver" in texte, "les exclusions présumées sont comptées, pas listées"
    assert len(lignes) < len(prolog.arbre_lisible(d["preuve"], complet=True))


def test_arbre_de_preuve_suit_chaque_decision(contrat, cas):
    """Chaque arbre redit la décision de sa garantie, et un nœud n'est jamais « oui » si ses enfants
    l'interdisent (cohérence de la logique à trois valeurs dans la trace)."""
    def coherent(n):
        es = [e["etat"] for e in n["enfants"]]
        if n["type"] == "et" and es:
            assert n["etat"] == ("non" if "non" in es else "inconnu" if "inconnu" in es else "oui")
        if n["type"] == "ou" and es:
            assert n["etat"] == ("oui" if "oui" in es else "inconnu" if "inconnu" in es else "non")
        for e in n["enfants"]:
            coherent(e)
    for i, faits, _ in cas:
        d = Explorateur(contrat, faits).decider()
        retenues = {r["id"]: r["decision"] for r in d["retenues"]}
        assert {g["id"]: g["decision"] for g in d["preuve"]} == retenues, i
        for g in d["preuve"]:
            coherent(g)


def test_la_reponse_porte_l_arbre_de_preuve(contrat):
    faits = {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"], "fermeture": "cadenas"}
    def oracle(f):  # l'oracle ne rend pas les libellés des garanties : on les ajoute comme le fait moteur.pl
        d = Explorateur(contrat, f).decider()
        for r in d["retenues"]:
            g = next(x for x in contrat.regles("garantie", 4) if x.args[0] == r["id"])
            r.update(garantie=g.args[1], article=g.args[2], motif="…", preuves=[])
        return d
    p = prolog.PipelineRegles(CONTRAT, [], FauxLLM(faits), decideur=oracle)
    v = p.analyser("On m'a volé mon vélo dans ma cave fermée par un cadenas.").verdict
    assert v.preuve and v.raisonnement[0].startswith("Garantie « Vol du contenu dans le bâtiment »")
    from couverture import cli
    from couverture.models import Resultat
    sortie = cli.afficher_court(Resultat(sinistre="…", contrat_id=CONTRAT, methode="regles", faits=prolog.faits_lisibles(faits),
                                         clauses_consultees=[], verdict=v))
    assert "Arbre de preuve (moteur Prolog) :" in sortie and "[non] Condition non remplie" in sortie


# --- Lecture en deux temps (7.38) ----------------------------------------------------------------------------

def test_lecture_en_deux_temps(monkeypatch):
    """Temps 1 : événement, bien, lieu. Temps 2 : seulement les questions de cet événement, avec ce qui est établi.
    Chaque appel envoie un schéma qui ne permet que les valeurs du vocabulaire."""
    class Modele:
        nom, accepte_schema = "schema", True

        def __init__(self):
            self.appels = []

        def completer(self, systeme, message, schema=None):
            self.appels.append((systeme, message, schema))
            if len(self.appels) == 1:
                return json.dumps({"faits": {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"]}})
            return json.dumps({"faits": {"fermeture": "cadenas", "lieu": ["logement"], "cause_eau": "gel"}})

    monkeypatch.setenv("COUVERTURE_LECTURE", "deux_temps")
    m = Modele()
    faits, ecarts = prolog.extraire_faits_regles("On m'a volé mon vélo dans ma cave fermée par un cadenas.", m)
    assert faits == {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"], "fermeture": "cadenas"}, \
        "le temps 2 ne réécrit pas le lieu, et une cause d'eau n'est pas demandée pour un vol"
    (s1, m1, sch1), (s2, m2, sch2) = m.appels
    assert set(sch1["properties"]["faits"]["properties"]) == {"evenement", "bien", "lieu"}
    assert "velo" in sch1["properties"]["faits"]["properties"]["bien"]["items"]["enum"]
    details = set(sch2["properties"]["faits"]["properties"])
    assert {"fermeture", "effraction", "absence"} <= details and not details & {"cause_eau", "flammes", "evenement"}
    assert sch2["properties"]["faits"]["properties"]["fermeture"]["enum"][0] == "inconnu", "« inconnu » d'abord"
    assert "required" not in sch2["properties"]["faits"], "aucune variable obligatoire : le modèle remplirait (7.40)"
    assert "evenement = vol" in m2 and "## Déjà établi" in m2
    assert len(m2) < len(m1) + 3000, "la consigne du temps 2 est courte"


def test_les_regles_v4_sont_toutes_dans_les_deux_temps():
    """Couper la consigne en deux ne doit perdre aucune règle (la leçon de la v3, 7.24 bis)."""
    import re as _re

    deux = prolog.SYSTEME_LECTURE_SOCLE + prolog.SYSTEME_LECTURE_DETAILS
    for ligne in prolog.SYSTEME_FAITS_REGLES.splitlines():
        if ligne.startswith("- "):
            coeur = _re.sub(r"Sinon, ne la mets pas", "Sinon, réponds", ligne)[:60]
            assert coeur in deux, ligne


def test_lecture_un_temps_toujours_disponible(monkeypatch):
    monkeypatch.setenv("COUVERTURE_LECTURE", "un_temps")
    appels = []

    class Modele:
        nom = "ancien"

        def completer(self, systeme, message):
            appels.append(systeme)
            return json.dumps({"faits": {"evenement": ["vol"]}})

    prolog.extraire_faits_regles("Vélo volé.", Modele())
    assert appels == [prolog.SYSTEME_FAITS_REGLES]


def test_schema_refuse_retombe_sur_le_mode_json(monkeypatch):
    from couverture import llm as module_llm

    envois = []

    def poster(url, corps, entetes, timeout):
        envois.append(corps.get("response_format"))
        if corps["response_format"]["type"] == "json_schema":
            raise module_llm.ErreurLLM("Erreur 422 du fournisseur : schema", code=422)
        return {"choices": [{"message": {"content": '{"faits": {}}'}, "finish_reason": "stop"}]}

    monkeypatch.setattr(module_llm, "_poster", poster)
    m = module_llm.OpenAICompatibleLLM(modele="x", url="http://serveur", json_mode=True)
    assert module_llm.completer_avec_schema(m, "s", "m", {"type": "object"}) == '{"faits": {}}'
    assert [e["type"] for e in envois] == ["json_schema", "json_object"] and m.schema_refuse
    module_llm.completer_avec_schema(m, "s", "m", {"type": "object"})
    assert envois[-1]["type"] == "json_object", "on ne redemande pas un schéma refusé"


def test_inconnu_n_est_pas_un_fait(monkeypatch):
    """« inconnu » (la réponse normale) est retiré avant tout : la variable reste inconnue et la question sera posée."""
    class Modele:
        nom, accepte_schema = "schema", True
        n = 0

        def completer(self, systeme, message, schema=None):
            Modele.n += 1
            if Modele.n == 1:
                return json.dumps({"faits": {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"]}})
            return json.dumps({"faits": {"fermeture": "inconnu", "serrure_surete": "inconnu", "auteur": "inconnu"}})

    monkeypatch.setenv("COUVERTURE_LECTURE", "deux_temps")
    faits, _ = prolog.extraire_faits_regles("On m'a volé mon vélo dans ma cave.", Modele())
    assert faits == {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"]}
    assert "la clé dont le voleur s'est servi" in prolog.SYSTEME_LECTURE_SOCLE


def test_lecture_en_parallele(monkeypatch):
    """Le mode en parallèle (essayé en 7.41, écarté en 7.42) : le socle (courte) et la lecture complète v4,
    en même temps. Le socle vient de la première ; le reste de la seconde."""
    import threading
    import time as _time

    class Modele:
        nom, accepte_schema = "parallele", True

        def __init__(self):
            self.en_cours, self.max_simultanes, self.verrou = 0, 0, threading.Lock()

        def completer(self, systeme, message, schema=None):
            with self.verrou:
                self.en_cours += 1
                self.max_simultanes = max(self.max_simultanes, self.en_cours)
            _time.sleep(0.05)
            with self.verrou:
                self.en_cours -= 1
            if systeme == prolog.SYSTEME_LECTURE_SOCLE:
                return json.dumps({"faits": {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"]}})
            assert systeme == prolog.SYSTEME_FAITS_REGLES and "cause_eau" in schema["properties"]["faits"]["properties"]
            return json.dumps({"faits": {"evenement": ["vol"], "bien": ["velo", "cles"], "fermeture": "cadenas"}})

    monkeypatch.delenv("COUVERTURE_LECTURE", raising=False)
    assert prolog.mode_lecture() == "verifiee", "la meilleure lecture mesurée est le défaut (7.45)"
    monkeypatch.setenv("COUVERTURE_LECTURE", "en_parallele")
    m = Modele()
    faits, _ = prolog.extraire_faits_regles("On m'a volé mon vélo dans ma cave fermée par un cadenas.", m)
    assert faits == {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"], "fermeture": "cadenas"}, \
        "le socle l'emporte (pas de clés), le lieu vient du socle, le détail de la lecture complète"
    assert m.max_simultanes == 2, "les deux lectures partent en même temps"


def test_lecture_verifiee(monkeypatch):
    """Les deux temps, puis chaque fait du temps 2 soumis comme une affirmation : « non dit » le retire (7.43).
    Le socle n'est jamais soumis."""
    class Modele:
        nom, accepte_schema = "verif", True

        def __init__(self):
            self.systemes, self.affirmations = [], ""

        def completer(self, systeme, message, schema=None):
            self.systemes.append(systeme)
            if systeme == prolog.SYSTEME_LECTURE_SOCLE:
                return json.dumps({"faits": {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"]}})
            if systeme == prolog.SYSTEME_LECTURE_DETAILS:
                return json.dumps({"faits": {"fermeture": "aucune", "auteur": "tiers", "absence": "oui"}})
            self.affirmations = message
            assert set(schema["properties"]["verdicts"]["properties"]) == {"fermeture", "auteur", "absence"}
            return json.dumps({"verdicts": {"fermeture": "non_dit", "auteur": "non_dit", "absence": "dit"}})

    monkeypatch.setenv("COUVERTURE_LECTURE", "verifiee")
    m = Modele()
    faits, ecarts = prolog.extraire_faits_regles("Pendant mes vacances, on m'a volé mon vélo dans ma cave.", m)
    assert faits == {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"], "absence": "oui"}
    assert m.systemes[-1] == prolog.SYSTEME_VERIFICATION and len(m.systemes) == 3
    assert "Comment le local était-il fermé ?" in m.affirmations and "evenement" not in m.affirmations.split("## Déclaration")[0]
    assert sum("non dit" in e for e in ecarts) == 2


def test_recours_retablit_un_fait_retire_qui_tranche():
    """7.78 : la vérification retire « serrure de sûreté : non » (un cadenas écrit) et la réponse reste
    « incertain ». Seul un fait retiré qui changerait la décision est soumis au recours ; rétabli s'il est dit."""
    def decideur(f):
        return {"decision": "NON_COUVERT" if f.get("serrure_surete") == "non" else "INCERTAIN"}

    soumis = []

    def recours(faits):
        soumis.append(dict(faits))
        return {v: "dit" for v in faits}

    voc = prolog.vocabulaire()
    faits = {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"]}
    retires = {"serrure_surete": "non", "absence": "oui"}
    f2, rappels = prolog.rappeler(faits, retires, voc, decideur, recours)
    assert rappels == ["serrure_surete"] and f2["serrure_surete"] == "non"
    assert soumis == [{"serrure_surete": "non"}], "l'absence ne change rien : elle n'est pas soumise"
    f3, rappels = prolog.rappeler(faits, retires, voc, decideur, lambda fs: {v: "non_dit" for v in fs})
    assert f3 == faits and rappels == []


def test_verification_illisible_ne_retire_rien():
    class Modele:
        nom = "illisible"

        def completer(self, systeme, message):
            return "je ne sais pas"

    lus = {"evenement": ["vol"], "fermeture": "cle"}
    gardes, ecarts = prolog.verifier_details("Volé.", lus, Modele(), prolog.vocabulaire())
    assert gardes == lus and "illisible" in ecarts[0]


def test_un_doute_ne_fait_jamais_couvrir(monkeypatch, contrat):
    """La vérification a jugé « non dit » la fenêtre laissée ouverte : sans ce fait, le moteur couvrirait.
    Le moteur arbitre : la lecture non vérifiée est gardée (7.44)."""
    class Modele:
        nom, accepte_schema = "verif", True

        def completer(self, systeme, message, schema=None):
            if systeme == prolog.SYSTEME_LECTURE_SOCLE:
                return json.dumps({"faits": {"evenement": ["vol"], "bien": ["appareil_audiovisuel"], "lieu": ["logement"]}})
            if systeme == prolog.SYSTEME_LECTURE_DETAILS:
                return json.dumps({"faits": {"absence": "oui", "effraction": "non", "fenetres_fermees": "non",
                                             "fermeture": "aucune"}})
            return json.dumps({"verdicts": {"absence": "dit", "effraction": "non_dit", "fenetres_fermees": "non_dit",
                                            "fermeture": "non_dit"}})

    monkeypatch.setenv("COUVERTURE_LECTURE", "verifiee")
    oracle = lambda f: Moteur(contrat, f).decider()
    sinistre = "Pendant que j'étais au travail, on est entré par la fenêtre que j'avais laissée ouverte et on a volé la télé."
    faits, ecarts = prolog.extraire_faits_regles(sinistre, Modele(), oracle)
    assert faits.get("fenetres_fermees") == "non" and any("vérification écartée" in e for e in ecarts)
    assert oracle(faits)["decision"] != "COUVERT"
    # Sans arbitre (ou quand retirer ne fait pas couvrir), la vérification s'applique.
    faits_sans, _ = prolog.extraire_faits_regles(sinistre, Modele())
    assert "fenetres_fermees" not in faits_sans


# --- Le moteur chargé une fois (7.46) -----------------------------------------------------------------------

FAUX_SWIPL = """#!/usr/bin/env python3
import json, sys
for ligne in sys.stdin:
    ligne = ligne.strip()
    if ligne == "pret.":
        print(json.dumps({"pret": True}), flush=True)
    elif ligne.startswith("faits("):
        print(json.dumps({"decision": "INCERTAIN", "demande": ligne, "retenues": []}), flush=True)
"""


@pytest.mark.skipif(sys.platform == "win32", reason="le faux SWI-Prolog est un script Python")
def test_moteur_permanent_protocole(tmp_path, monkeypatch):
    """Sans SWI-Prolog : un faux moteur vérifie le protocole (une demande par ligne, une ligne JSON en retour),
    qu'un seul processus sert toutes les décisions, et qu'un processus arrêté est relancé."""
    exe = tmp_path / "swipl"
    exe.write_text(FAUX_SWIPL, encoding="utf-8")
    exe.chmod(0o755)
    monkeypatch.setenv("COUVERTURE_SWIPL", str(exe))
    monkeypatch.delenv("COUVERTURE_PROLOG_PERMANENT", raising=False)
    prolog._MOTEURS.clear()
    d = prolog.decider(CONTRAT, {"evenement": ["vol"], "bien": ["velo"], "fermeture": "cadenas"})
    assert d["demande"] == "faits([evenement-vol, bien-velo, fermeture-cadenas])."
    m = prolog._MOTEURS[CONTRAT]
    prolog.decider(CONTRAT, {"evenement": ["incendie"]})
    assert prolog._MOTEURS[CONTRAT] is m, "le même processus sert les décisions suivantes"
    m.p.kill()
    m.p.wait()
    assert prolog.decider(CONTRAT, {"evenement": ["vol"]})["decision"] == "INCERTAIN"
    assert prolog._MOTEURS[CONTRAT] is not m, "un processus arrêté est relancé"
    with pytest.raises(prolog.ErreurRegles):
        prolog.decider(CONTRAT, {"evenement": ["vol); halt"]})
    prolog._fermer_moteurs()
    prolog._MOTEURS.clear()


@avec_swipl
def test_moteur_permanent_decide_comme_un_processus_par_decision(cas):
    """Le moteur chargé une fois rend exactement ce que rend un SWI-Prolog lancé pour chaque décision."""
    prolog._MOTEURS.clear()
    for i, faits, _ in cas:
        assert prolog.moteur_permanent(CONTRAT).decider(faits) == prolog.executer(CONTRAT, "decider_json", faits), i
    prolog._fermer_moteurs()
    prolog._MOTEURS.clear()


def test_je_ne_sais_pas_plutot_qu_une_reponse_fausse(monkeypatch, contrat):
    """Une réponse ferme doit reposer sur des faits confirmés (7.49). Le moteur désigne les faits qui portent
    la décision ; si le modèle ne les retrouve pas dans la déclaration, la réponse devient « incertain »."""
    faits = {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"], "fermeture": "cadenas"}

    def oracle(f):  # l'oracle ne rend pas les libellés des garanties : on les ajoute comme le fait moteur.pl
        d = Explorateur(contrat, f).decider()
        for r in d["retenues"] + d.get("possibles", []):
            g = next(x for x in contrat.regles("garantie", 4) if x.args[0] == r["id"])
            r.update(garantie=g.args[1], article=g.args[2], motif="…", preuves=[])
        return d

    assert oracle(faits)["decision"] == "NON_COUVERT"
    assert "fermeture" in prolog.faits_decisifs(faits, oracle, "NON_COUVERT")

    class Modele:
        nom, accepte_schema = "confirme", True

        def __init__(self, verdict):
            self.verdict, self.confirmations = verdict, []

        def completer(self, systeme, message, schema=None):
            if systeme == prolog.SYSTEME_LECTURE_SOCLE:
                return json.dumps({"faits": {k: faits[k] for k in ("evenement", "bien", "lieu")}})
            if systeme == prolog.SYSTEME_LECTURE_DETAILS:
                return json.dumps({"faits": {"fermeture": "cadenas"}})
            props = set(schema["properties"]["verdicts"]["properties"])
            self.confirmations.append(props)
            if len(self.confirmations) == 1:  # la vérification de la lecture garde le cadenas
                return json.dumps({"verdicts": {v: "dit" for v in props}})
            # la confirmation des faits décisifs, ensuite
            return json.dumps({"verdicts": {v: (self.verdict if v == "fermeture" else "dit") for v in props}})

    monkeypatch.setenv("COUVERTURE_LECTURE", "verifiee")
    sinistre = "On m'a volé mon vélo dans ma cave."
    doute = prolog.PipelineRegles(CONTRAT, [], Modele("non_dit"), decideur=oracle).analyser(sinistre).verdict
    assert doute.decision.value == "INCERTAIN" and (doute.decision_initiale or doute.decision).value == "INCERTAIN"
    assert doute.informations_manquantes[0].startswith(prolog.question("fermeture"))
    assert doute.justification.startswith("Je ne peux pas trancher")
    m = Modele("dit")
    confirme = prolog.PipelineRegles(CONTRAT, [], m, decideur=oracle).analyser(sinistre).verdict
    # (sans clauses fournies, le contrôle des citations rétrograde toute réponse : on lit la réponse avant lui)
    assert (confirme.decision_initiale or confirme.decision).value == "NON_COUVERT", "confirmé : la réponse ferme reste"
    assert "fermeture" in m.confirmations[-1], "le fait décisif est soumis à confirmation"

    # Un modèle plus fort peut confirmer à la place du modèle de lecture (7.66) : c'est lui qui tranche.
    from couverture import llm as llm_mod
    lecteur, juge = Modele("dit"), Modele("non_dit")
    juge.confirmations = [set()]          # le juge ne fait que la confirmation : il répond tout de suite
    monkeypatch.setattr(llm_mod, "configurer", lambda usage="analyse": juge if usage == "confirmation" else None)
    v = prolog.PipelineRegles(CONTRAT, [], lecteur, decideur=oracle).analyser(sinistre).verdict
    assert v.decision.value == "INCERTAIN" and "fermeture" in juge.confirmations[-1], \
        "le modèle de confirmation a refusé le cadenas : la réponse est suspendue"
    assert all("fermeture" not in c for c in lecteur.confirmations[1:]), "le lecteur n'a pas confirmé lui-même"
