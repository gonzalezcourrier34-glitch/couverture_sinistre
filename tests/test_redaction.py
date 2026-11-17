"""Rédaction des règles par le modèle : JSON → Prolog, contrôles, acceptation (sans réseau ni SWI-Prolog).

Le modèle est simulé : ses propositions sont écrites ici, une bonne et des fautives, pour vérifier
que chaque contrôle attrape la faute qu'il vise. L'évaluation des règles fusionnées passe par
l'oracle Python (moteur_reference.py)."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from couverture import prolog, redaction
from couverture.models import Clause, TypeClause
from moteur_reference import Contrat, Moteur

CONTRAT = "foyer-appart123-2025"
CHEMIN = ["2 Les garanties de base de l’assurance habitation", "2.2 Tempête, la grêle, la pression de la neige ou de la glace"]
CLAUSES = [
    Clause(id="2.2", article="2.2", titre="Tempête", chemin=CHEMIN, type=TypeClause.GARANTIE, groupe="2",
           texte="Nous couvrons les dommages matériels directement causés par les aléas précisés. Limites d’indemnisation "
                 "Nous couvrons dans les limites suivantes les dégâts causés aux biens suivants : Abri de jardin et son "
                 "éventuel contenu 1.000 EUR"),
    Clause(id="2.2-a", article="2.2-a", titre="Exclusions", chemin=CHEMIN + ["Exclusions"], type=TypeClause.EXCLUSION,
           groupe="2.2",
           texte="Nous n’indemnisons pas les dégâts causés : - aux constructions non entièrement closes ou couvertes "
                 "- à tout objet situé à l'extérieur même ceux fixés à demeure - aux matériaux à pied d’œuvre"),
    Clause(id="12/tempete", article="12/tempete", titre="Tempête", chemin=["12 Définitions", "Tempête"],
           type=TypeClause.DEFINITION, groupe="12",
           texte="• L’action du vent mesurée à une vitesse de pointe d’au moins 80 km/h par la station de l’I.R.M. la "
                 "plus proche du bâtiment • L’action du vent qui endommage d’autres biens qui sont situés dans les 10 km"),
]

BONNE = {
    "evenements": ["tempete"],
    "definitions": [{"concept": "tempete", "condition": {"f": ["vent_fort", "oui"]}, "article": "12/tempete",
                     "texte": "L’action du vent mesurée à une vitesse de pointe d’au moins 80 km/h"}],
    "garanties": [{
        "id": "tempete_batiment", "nom": "Tempête", "article": "2.2",
        "texte": "Nous couvrons les dommages matériels directement causés par les aléas précisés",
        "perimetre": [{"f": ["evenement", "tempete"]},
                      {"ou": [{"concept": "contenu"}, {"f": ["bien", "element_batiment"]}]},
                      {"concept": "batiment"}],
        "circonstances": [{"condition": {"concept": "tempete"}, "article": "12/tempete",
                           "texte": "L’action du vent mesurée à une vitesse de pointe d’au moins 80 km/h"}],
        "obligations": [],
        "exclusions": [
            {"condition": {"f": ["construction_close", "non"]}, "portee": "tout", "a_demander": True, "article": "2.2-a",
             "texte": "aux constructions non entièrement closes ou couvertes"},
            {"condition": {"ou": [{"f": ["lieu", "jardin"]}, {"f": ["lieu", "terrasse"]}]}, "portee": "tout",
             "a_demander": False, "article": "2.2-a", "texte": "à tout objet situé à l'extérieur même ceux fixés à demeure"}],
        "limites": [{"article": "2.2", "texte": "Abri de jardin et son éventuel contenu", "montant": "1.000 EUR"}]}],
    "vocabulaire_manquant": [
        {"variable": "vent_fort", "valeurs": ["oui", "non"], "question": "Le vent a-t-il dépassé 80 km/h ?", "pourquoi": "définition"},
        {"variable": "construction_close", "valeurs": ["oui", "non"], "question": "La construction était-elle close ?",
         "pourquoi": "exclusion"}],
    "non_traduit": [{"article": "2.2-a", "texte": "aux matériaux à pied d’œuvre", "pourquoi": "pas de fait pour cela"}],
}


class FauxModele:
    nom = "faux-large"

    def __init__(self, reponse):
        self.reponse = reponse
        self.messages = []

    def completer(self, systeme, message):
        self.messages.append(message)
        return json.dumps(self.reponse, ensure_ascii=False)


@pytest.fixture
def voc_etendu(tmp_path, monkeypatch):
    """Un vocabulaire copié, que l'acceptation peut modifier sans toucher au vrai."""
    copie = tmp_path / "vocabulaire.json"
    copie.write_text((prolog.DOSSIER / "vocabulaire.json").read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(prolog, "vocabulaire", lambda: json.loads(copie.read_text(encoding="utf-8"))["variables"])
    return copie


def controles(prop):
    pl = prolog.fichier_regles(CONTRAT).read_text(encoding="utf-8")
    return redaction.controler(copy.deepcopy(prop), CLAUSES, pl, "2.2")


def bloquants(ps, controle=None):
    return [p for p in ps if p["gravite"] == redaction.BLOQUANT and (controle is None or p["controle"] == controle)]


# --- JSON → Prolog ---------------------------------------------------------------------------------------

def test_termes_et_chaines():
    assert redaction.terme({"si": [{"f": ["lieu", "cave"]}, {"non": {"concept": "batiment"}}]}) == \
        "si(f(lieu, cave), non(concept(batiment)))"
    assert redaction.terme(None) == "faux"
    assert redaction.atome("2.2-a") == "'2.2-a'" and redaction.atome("l'eau") == "'l\\'eau'"
    assert redaction.chaine('dit « x » et "y"') == '"dit « x » et \\"y\\""'
    for mauvais in ({"f": ["lieu"]}, {"et": []}, {"peut_etre": 1}, "lieu = cave", {"f": ["a", "b"], "non": 1}):
        with pytest.raises(redaction.ErreurProposition):
            redaction.terme(mauvais)


def test_regles_generees_et_fusion_evaluees_par_l_oracle(tmp_path):
    pl = redaction.en_prolog(BONNE, "2.2", "test")
    assert "evenement_traduit(tempete)." in pl and "perimetre(tempete_batiment, f(evenement, tempete))." in pl
    assert "exclusion(tempete_batiment, f(construction_close, non), tout, oui, '2.2-a'," in pl
    fusion = tmp_path / "fusion.pl"
    fusion.write_text(redaction.fusionner(prolog.fichier_regles(CONTRAT).read_text(encoding="utf-8"), pl), encoding="utf-8")
    contrat = Contrat(fusion)
    tempete = {"evenement": ["tempete", "degat_eaux"], "bien": ["element_batiment", "mobilier"], "lieu": ["logement"],
               "cause_eau": "infiltration_exterieure", "vent_fort": "oui", "construction_close": "oui"}
    assert Moteur(contrat, tempete).decider()["decision"] == "COUVERT", "la tempête, désormais traduite, couvre"
    d = Moteur(contrat, {k: v for k, v in tempete.items() if k != "vent_fort"}).decider()
    assert d["decision"] == "INCERTAIN" and "vent_fort" in d["retenues"][0]["questions"]
    terrasse = {"evenement": ["tempete"], "bien": ["mobilier"], "lieu": ["terrasse"], "vent_fort": "oui"}
    assert Moteur(contrat, terrasse).decider()["decision"] == "NON_COUVERT"


# --- Les contrôles attrapent chaque faute -------------------------------------------------------------------

def test_vocabulaire_nouveau_declare_bloque_jusqu_a_acceptation(voc_etendu):
    ps = controles(BONNE)
    voc = bloquants(ps, "vocabulaire")
    assert len(voc) == 2 and all("déclaré par le modèle" in p["message"] for p in voc)
    ajouts = redaction.accepter_vocabulaire(BONNE, voc_etendu)
    assert len(ajouts) == 2 and not bloquants(controles(BONNE), "vocabulaire")
    assert redaction.accepter_vocabulaire(BONNE, voc_etendu) == [], "pas de doublon"


def test_fait_invente_non_declare():
    prop = copy.deepcopy(BONNE)
    prop["garanties"][0]["perimetre"].append({"f": ["bien", "toiture"]})
    assert any("toiture : hors vocabulaire, et non déclaré" in p["message"] for p in bloquants(controles(prop)))


def test_citation_reparee_ou_refusee():
    prop = copy.deepcopy(BONNE)
    prop["garanties"][0]["exclusions"][1]["texte"] = "à tout objet situé à l'extérieur fixés à demeure"
    prop["garanties"][0]["limites"][0]["texte"] = "Nous couvrons les abris de jardin sans limite"
    ps = controles(prop)
    assert any(p["gravite"] == redaction.INFO and "réparée" in p["message"] for p in ps)
    assert any("ne figure pas" in p["message"] for p in bloquants(ps, "citation"))
    prop["garanties"][0]["texte"], prop["garanties"][0]["article"] = "x", "9.9"
    assert any("article 9.9 inconnu" in p["message"] for p in bloquants(controles(prop), "citation"))


def test_exclusion_oubliee_bloque():
    """La faute la plus coûteuse : une exclusion de la liste oubliée en silence."""
    assert bloquants(controles({**BONNE, "non_traduit": []}), "couverture"), "matériaux à pied d'œuvre : ni traduit ni déclaré"
    prop = copy.deepcopy(BONNE)
    prop["non_traduit"] = []
    del prop["garanties"][0]["exclusions"][1]
    messages = [p["message"] for p in bloquants(controles(prop), "couverture")]
    assert any("situé à l'extérieur" in m for m in messages) and any("pied d’œuvre" in m for m in messages)
    assert any("déclaré non traduit" in p["message"] for p in bloquants(controles(BONNE), "couverture"))


def test_concepts_et_identifiants():
    prop = copy.deepcopy(BONNE)
    prop["garanties"][0]["perimetre"].append({"concept": "grele"})
    prop["garanties"][0]["id"] = "vol_batiment"
    prop["definitions"].append({"concept": "batiment", "condition": {"f": ["lieu", "logement"]}, "article": "2.2",
                                "texte": "Nous couvrons les dommages matériels"})
    ps = bloquants(controles(prop))
    assert any("concept inconnu : grele" in p["message"] for p in ps)
    assert any("vol_batiment existe déjà" in p["message"] for p in ps)
    assert any("batiment est déjà défini" in p["message"] for p in ps)


def test_structure_mal_formee():
    prop = copy.deepcopy(BONNE)
    prop["garanties"][0]["perimetre"].append("evenement = tempete")
    assert bloquants(controles(prop), "structure")


# --- La commande, de bout en bout ---------------------------------------------------------------------------

def test_rediger_controler_accepter(tmp_path, monkeypatch, voc_etendu):
    regles = tmp_path / f"{CONTRAT}.pl"
    regles.write_text(prolog.fichier_regles(CONTRAT).read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(prolog, "fichier_regles", lambda c: regles)
    modele = FauxModele(BONNE)

    doc = redaction.rediger(CONTRAT, "2.2", CLAUSES, modele, dossier=tmp_path)
    assert "12/tempete" in modele.messages[0] and "vent_fort" not in modele.messages[0]
    assert "contenu" in modele.messages[0], "le modèle reçoit les concepts déjà définis"
    js, pl = redaction.chemins(CONTRAT, "2.2", tmp_path)
    assert js.exists() and pl.exists() and doc["meta"]["modele"] == "faux-large"
    with pytest.raises(redaction.ErreurProposition):
        redaction.accepter(CONTRAT, "2.2", tmp_path)

    # Le relecteur accepte le vocabulaire et retire l'élément non traduit (les matériaux : hors sujet ici).
    redaction.accepter_vocabulaire(doc["proposition"], voc_etendu)
    corrige = json.loads(js.read_text(encoding="utf-8"))
    corrige["proposition"]["non_traduit"] = []
    corrige["proposition"]["garanties"][0]["exclusions"].append(
        {"condition": {"f": ["materiaux_a_pied_oeuvre", "oui"]}, "portee": "tout", "a_demander": False,
         "article": "2.2-a", "texte": "aux matériaux à pied d’œuvre"})
    corrige["proposition"]["vocabulaire_manquant"].append(
        {"variable": "materiaux_a_pied_oeuvre", "valeurs": ["oui", "non"], "question": "?", "pourquoi": "exclusion"})
    redaction.accepter_vocabulaire(corrige["proposition"], voc_etendu)
    js.write_text(json.dumps(corrige, ensure_ascii=False), encoding="utf-8")
    doc = redaction.recontroler(CONTRAT, "2.2", CLAUSES, tmp_path)
    assert not bloquants(doc["controles"]), doc["controles"]
    assert "aucun contrôle bloquant" in redaction.resumer(doc)

    redaction.accepter(CONTRAT, "2.2", tmp_path)
    texte = regles.read_text(encoding="utf-8")
    assert "garantie(tempete_batiment," in texte and texte.startswith(":- encoding(utf8).")
    assert redaction.articles_proposes(CONTRAT, tmp_path) == ["2.2"]


def test_jeu_redaction_coherent():
    from couverture.evaluation import charger_cas, fichiers_jeu

    racine = Path(__file__).resolve().parents[1] / "data"
    cas = charger_cas(*fichiers_jeu(racine, CONTRAT, "redaction"))
    assert len(cas) >= 10 and {c["famille"] for c in cas} == {"tempete", "bris"}


def test_consigne_de_redaction_versionnee():
    from couverture.consignes import CONSIGNES

    assert CONSIGNES["couverture-redaction-regles"][2] == "v2"


# --- Après la première rédaction réelle (Mistral Large, 17 nov. 2026, docs/DEMARCHE.md 7.20) ---------------

REELLE = Path(__file__).parent / "fixtures" / "redaction-2.2-mistral-large-v1.json"


def test_ecart_au_schema_explique_en_clair():
    """La vraie réponse pour 2.2 : une définition sans « concept » ni « condition ». Le message dit quoi corriger."""
    prop = json.loads(REELLE.read_text(encoding="utf-8"))["proposition"]
    ecarts = redaction.erreurs_schema(prop)
    assert ecarts == ["definitions : un élément de « definitions » n'a pas concept, condition (champs reçus : id, nom, article, texte)"]
    assert [p["controle"] for p in controles(prop)] == ["structure"]


def test_reprise_unique_sur_ecart_au_schema(tmp_path, monkeypatch):
    regles = tmp_path / f"{CONTRAT}.pl"
    regles.write_text(prolog.fichier_regles(CONTRAT).read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(prolog, "fichier_regles", lambda c: regles)
    mauvaise = copy.deepcopy(BONNE)
    mauvaise["definitions"] = [{"id": "tempete", "nom": "Tempête", "article": "12/tempete", "texte": "x"}]

    class DeuxTemps(FauxModele):
        def completer(self, systeme, message):
            self.messages.append(message)
            return json.dumps(mauvaise if len(self.messages) == 1 else BONNE, ensure_ascii=False)

    modele = DeuxTemps(None)
    doc = redaction.rediger(CONTRAT, "2.2", CLAUSES, modele, dossier=tmp_path)
    assert len(modele.messages) == 2 and "ne respecte pas le schéma" in modele.messages[1]
    assert "n'a pas concept, condition" in modele.messages[1]
    assert doc["proposition"] == BONNE and doc["meta"]["premiere_reponse"]["ecarts"]
    assert not [p for p in doc["controles"] if p["controle"] == "structure"]


def test_definition_de_l_evenement_couvert_exigee():
    """Mistral avait oublié que la « tempête » du contrat exige un vent d'au moins 80 km/h."""
    prop = copy.deepcopy(BONNE)
    prop["definitions"], prop["garanties"][0]["circonstances"] = [], []
    assert any("12/tempete" in p["message"] for p in bloquants(controles(prop), "couverture"))


def test_prolog_pas_lance_sur_concept_inconnu(tmp_path, monkeypatch):
    """Le plantage du 17 nov. : un concept inconnu (sanitaires) faisait échouer SWI-Prolog en pleine
    non-régression, et la réponse du modèle était perdue. Désormais la réponse est gardée et Prolog attend."""
    regles = tmp_path / f"{CONTRAT}.pl"
    regles.write_text(prolog.fichier_regles(CONTRAT).read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(prolog, "fichier_regles", lambda c: regles)
    appels = []
    monkeypatch.setattr(redaction, "controler_avec_prolog", lambda *a: appels.append(a) or [])
    prop = copy.deepcopy(BONNE)
    prop["garanties"][0]["perimetre"].append({"concept": "sanitaires"})
    doc = redaction.rediger(CONTRAT, "2.2", CLAUSES, FauxModele(prop), dossier=tmp_path, cas=[("x", {})])
    assert not appels and any("sanitaires" in p["message"] for p in bloquants(doc["controles"], "concept"))
    assert redaction.chemins(CONTRAT, "2.2", tmp_path)[0].exists()


# --- Après la rédaction v2 de 2.9 (7.22) ------------------------------------------------------------------

def test_citation_rattachee_a_la_bonne_clause():
    """Mistral citait la définition des sanitaires sous « 12 » au lieu de « 12/sanitaires »."""
    prop = copy.deepcopy(BONNE)
    prop["definitions"][0]["article"] = "12"
    ps = controles(prop)
    assert any("rattachée à 12/tempete" in p["message"] for p in ps if p["gravite"] == redaction.INFO)
    assert not bloquants(ps, "citation")


def test_exclusion_d_un_bien_a_portee_totale_signalee():
    prop = copy.deepcopy(BONNE)
    prop["garanties"][0]["exclusions"].append(
        {"condition": {"f": ["bien", "mobilier_jardin"]}, "portee": "tout", "a_demander": False, "article": "2.2-a",
         "texte": "à tout objet situé à l'extérieur même ceux fixés à demeure"})
    assert any(p["controle"] == "portée" and p["gravite"] == redaction.A_RELIRE for p in controles(prop))


def test_hierarchie_a_trois_valeurs():
    """Un fait précis vaut pour sa catégorie ; un fait vague ne tranche pas pour une valeur précise ;
    une exclusion qui vise la télé ne devient pas partielle parce que la télé est aussi de l'électronique."""
    contrat = Contrat(prolog.fichier_regles(CONTRAT))
    h = [("bien", "vitre", "element_batiment"), ("bien", "appareil_audiovisuel", "electronique")]
    t = lambda texte: Terme_(texte)  # noqa: E731
    m = Moteur(contrat, {"bien": ["vitre"]}, h)
    assert m.eval(t("f(bien, element_batiment)")) == "oui" and m.eval(t("f(bien, velo)")) == "non"
    m = Moteur(contrat, {"bien": ["element_batiment"]}, h)
    assert m.eval(t("f(bien, vitre)")) == "inconnu" and m.inconnues(t("f(bien, vitre)")) == ["bien"]
    m = Moteur(contrat, {"bien": ["element_batiment", "vitre"]}, h)
    assert m.eval(t("f(bien, vitre)")) == "oui"
    m = Moteur(contrat, {"bien": ["mobilier"]}, h)
    assert m.eval(t("f(bien, vitre)")) == "non"


def Terme_(texte):
    from moteur_reference import lire_clauses
    return lire_clauses(f"x({texte}).")[0].args[0]


def test_parents_du_vocabulaire_valides():
    for v, d in prolog.vocabulaire().items():
        for enfant, parents in d.get("parents", {}).items():
            assert enfant in d["valeurs"] and set(parents) <= set(d["valeurs"]), (v, enfant)


def test_regles_2_9_relues_et_hierarchie(tmp_path):
    """Les règles 2.9 de Mistral Large, portées corrigées à la relecture, fusionnées au contrat."""
    texte = prolog.fichier_regles(CONTRAT).read_text(encoding="utf-8")
    if "garantie(bris_vitrages," in texte:          # acceptée le 17 nov. (DEMARCHE 7.23)
        c = Contrat(prolog.fichier_regles(CONTRAT))
    else:
        doc = json.loads((prolog.DOSSIER / "propositions" / CONTRAT / "2.9.json").read_text(encoding="utf-8"))
        fusion = tmp_path / "fusion.pl"
        fusion.write_text(redaction.fusionner(texte, redaction.en_prolog(doc["proposition"], "2.9")), encoding="utf-8")
        c = Contrat(fusion)
    vitre = {"evenement": ["bris"], "bien": ["vitre"], "lieu": ["logement"]}
    assert Moteur(c, vitre).decider()["decision"] == "COUVERT"
    vague = Moteur(c, {**vitre, "bien": ["element_batiment"]}).decider()
    assert vague["decision"] == "INCERTAIN" and "bien" in vague["retenues"][0]["questions"], \
        "« élément du bâtiment » ne dit pas « vitre » : on demande, on ne refuse pas"
    tele = Moteur(c, {**vitre, "bien": ["appareil_audiovisuel", "electronique"]}).decider()
    assert tele["decision"] == "NON_COUVERT", "la télé est aussi de l'électronique : l'exclusion reste totale"
    deux = Moteur(c, {**vitre, "bien": ["vitre", "appareil_audiovisuel"]}).decider()
    assert deux["decision"] == "COUVERT" and deux["retenues"][0]["partielles"] == ["appareil_audiovisuel"]
