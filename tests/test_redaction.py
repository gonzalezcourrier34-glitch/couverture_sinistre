"""Rédaction des règles par le modèle : JSON → Prolog, contrôles, acceptation (sans réseau ni SWI-Prolog).

Le modèle est simulé : ses propositions sont écrites ici, une bonne et des fautives, pour vérifier
que chaque contrôle attrape la faute qu'il vise. L'évaluation des règles fusionnées passe par
l'oracle Python (moteur_reference.py)."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from couverture import lecture, prolog, redaction
from couverture.models import Clause, TypeClause
from moteur_reference import Contrat, Moteur

CONTRAT = "assureur-a-habitation-2025"
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
    """Un vocabulaire copié (le dossier entier), que l'acceptation peut modifier sans toucher au vrai."""
    import shutil
    copie = shutil.copytree(prolog.VOCABULAIRE, tmp_path / "vocabulaire")
    monkeypatch.setattr(prolog, "VOCABULAIRE", copie)
    return copie


def controles(prop):
    # Comme `recontroler` : sans le bloc déjà accepté pour l'article, ici la tempête (2.2, acceptée le 19 nov.).
    pl = redaction.retirer_article(prolog.fichier_regles(CONTRAT).read_text(encoding="utf-8"), "2.2")
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
    sans_tempete = redaction.retirer_article(prolog.fichier_regles(CONTRAT).read_text(encoding="utf-8"), "2.2")
    fusion.write_text(redaction.fusionner(sans_tempete, pl), encoding="utf-8")
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
    assert any(p["message"].startswith("vent_fort = oui") for p in voc)
    assert all("déclaré par le modèle" in p["message"] for p in voc)
    ajouts = redaction.accepter_vocabulaire(BONNE, voc_etendu)
    assert any(x.startswith("vent_fort (oui, non)") for x in ajouts) and not bloquants(controles(BONNE), "vocabulaire")
    assert redaction.accepter_vocabulaire(BONNE, voc_etendu) == [], "pas de doublon"
    assert prolog.vocabulaire(voc_etendu)["vent_fort"]["pour"] == ["tempete"], \
        "une variable nouvelle ne vaut que pour les événements de sa garantie (7.56)"
    prop = copy.deepcopy(BONNE)
    prop["vocabulaire_manquant"] = [{"variable": "grele", "valeurs": ["oui", "non"], "question": "Grêle ?",
                                     "aide": {"oui": "grêlons, impacts de grêle", "peut-etre": "ignorée"}}]
    redaction.accepter_vocabulaire(prop, voc_etendu)
    assert prolog.vocabulaire(voc_etendu)["grele"]["aide"] == \
        {"oui": "grêlons, impacts de grêle"}, "l'aide est reprise, pour les seules valeurs déclarées (7.62)"
    prop["vocabulaire_manquant"] = [{"variable": "bien", "valeurs": ["tablette"], "parent": "electronique"}]
    redaction.accepter_vocabulaire(prop, voc_etendu)
    assert prolog.vocabulaire(voc_etendu)["bien"]["parents"]["tablette"] == ["electronique"], \
        "une valeur plus fine est rattachée à sa valeur existante (7.64)"
    sans = copy.deepcopy(BONNE)
    sans["vocabulaire_manquant"] = [{"variable": "bien", "valeurs": ["liseuse"], "question": "?"}]
    assert any("sans « parent »" in p["message"] for p in controles(sans))


def test_fait_invente_non_declare():
    prop = copy.deepcopy(BONNE)
    prop["garanties"][0]["perimetre"].append({"f": ["bien", "cheminee"]})
    assert any("cheminee : hors vocabulaire, et non déclaré" in p["message"] for p in bloquants(controles(prop)))


def test_citation_reparee_ou_refusee():
    prop = copy.deepcopy(BONNE)
    prop["garanties"][0]["exclusions"][1]["texte"] = "à tout objet situé à l'extérieur fixés à demeure"
    prop["garanties"][0]["limites"][0]["texte"] = "Nous couvrons les abris de jardin sans limite"
    ps = controles(prop)
    assert any(p["gravite"] == redaction.INFO and "réparée" in p["message"] for p in ps)
    assert any("ne figure pas" in p["message"] for p in bloquants(ps, "citation"))
    prop["garanties"][0]["texte"], prop["garanties"][0]["article"] = "x", "9.9"
    assert any("article 9.9 inconnu" in p["message"] for p in bloquants(controles(prop), "citation"))


def test_non_traduit_en_simple_phrase():
    """Assureur B 3.1.6 : Mistral Large a rendu « non_traduit » comme une liste de phrases. Le schéma le signale
    (une reprise est demandée au modèle) et les contrôles ne plantent pas : le passage reste bloquant."""
    prop = copy.deepcopy(BONNE)
    prop["non_traduit"] = ["aux matériaux à pied d’œuvre : pas de fait pour cela"]
    assert any("non_traduit" in e and "pas un objet" in e for e in redaction.erreurs_schema(prop))
    messages = [p["message"] for p in bloquants(controles(prop), "couverture")]
    assert any("déclaré non traduit" in m and "pied d’œuvre" in m for m in messages)


def _deux_garanties(communes: bool) -> dict:
    """BONNE plus une extension, avec les exclusions de l'article en commun ou laissées à la seule garantie de base."""
    prop = copy.deepcopy(BONNE)
    ext = {**copy.deepcopy(prop["garanties"][0]), "id": "tempete_extension", "exclusions": [], "circonstances": []}
    prop["garanties"].append(ext)
    if communes:
        prop["exclusions_communes"] = prop["garanties"][0].pop("exclusions")
        prop["garanties"][0]["exclusions"] = []
    return prop


def test_exclusions_de_l_article_pour_toutes_ses_garanties():
    """Assureur B 3.1.6 (7.53) : une extension sans les exclusions de l'article couvrirait sans elles."""
    assert any("tempete_extension" in p["message"] for p in bloquants(controles(_deux_garanties(False)), "exclusions"))
    prop = _deux_garanties(True)
    assert not bloquants(controles(prop), "exclusions")
    assert not [p for p in bloquants(controles(prop), "couverture") if "absente" in p["message"]], \
        "les exclusions communes comptent pour la couverture de la liste"
    pl = redaction.en_prolog(prop, "2.2")
    assert "exclusion([tempete_batiment, tempete_extension], f(construction_close, non), tout, oui, '2.2-a'" in pl


def test_reserve_d_exclusion_et_condition_dans_une_limite_a_relire():
    prop = copy.deepcopy(BONNE)
    prop["garanties"][0]["exclusions"][1]["texte"] = "à tout objet situé à l'extérieur même ceux fixés à demeure, sauf x"
    prop["garanties"][0]["limites"][0]["texte"] = "Abri de jardin s'il est fermé"
    ps = [p for p in controles(prop) if p["gravite"] == redaction.A_RELIRE]
    assert any(p["controle"] == "réserve" for p in ps) and any(p["controle"] == "limite" for p in ps)
    prop["garanties"][0]["exclusions"][1]["condition"] = {"et": [{"f": ["lieu", "jardin"]}, {"non": {"f": ["bien", "plantation"]}}]}
    assert not any(p["controle"] == "réserve" for p in controles(prop))


def test_variable_nouvelle_sans_plus_proche_a_relire():
    ps = controles(BONNE)
    assert any(p["controle"] == "vocabulaire" and "plus_proche" in p["message"] and p["gravite"] == redaction.A_RELIRE
               for p in ps)


def test_le_vocabulaire_donne_au_modele_porte_les_questions():
    """Sans le sens des variables, Mistral Large a créé « agression » à côté de « violence » (7.53)."""
    message = redaction.message_redaction("2.2", [], [], "")
    assert "violence : oui, non — « Y a-t-il eu violences physiques ou menaces ? »" in message


def test_condition_nue_enveloppee_et_signalee():
    """Assureur B 3.1.6 v3 (7.54) : les circonstances rendues comme {"f": …}, deux fois de suite. Elles sont enveloppées
    avec la citation de leur garantie, et l'avertissement revient tant qu'elles ne sont pas précisées."""
    prop = copy.deepcopy(BONNE)
    prop["garanties"][0]["circonstances"].append({"f": ["vent_fort", "oui"]})
    ps = controles(prop)
    assert not bloquants(ps, "structure")
    assert any(p["controle"] == "structure" and p["gravite"] == redaction.A_RELIRE for p in ps)
    redaction.controler(prop, CLAUSES, prolog.fichier_regles(CONTRAT).read_text(encoding="utf-8"), "2.2")
    c = prop["garanties"][0]["circonstances"][-1]
    assert c["a_preciser"] and c["article"] == "2.2" and c["condition"] == {"f": ["vent_fort", "oui"]}
    assert any(p["controle"] == "structure" for p in controles(prop)), "toujours signalée au contrôle suivant"


def test_liste_d_exclusions_numerotee_et_incise():
    texte = ("En outre, ne sont pas assurés : 3.1.6.2.1 les vols simples ; 3.1.6.2.5 les vols de véhicules "
             "automoteurs – à l’exception des engins de jardinage –, des remorques non enfermées ; 3.1.6.2.8 le vol des animaux.")
    items = redaction.items_exclusion(texte)
    assert any(i.startswith("les vols de véhicules automoteurs – à l’exception") and "remorques" in i for i in items)
    assert any(i.startswith("le vol des animaux") for i in items) and len(items) == 3


def test_hors_decision_cite_et_non_bloquant():
    prop = copy.deepcopy(BONNE)
    prop["hors_decision"] = prop.pop("non_traduit")
    ps = controles(prop)
    assert not bloquants(ps, "couverture") and any("hors décision" in p["message"] for p in ps)
    prop["hors_decision"][0]["texte"] = "texte inventé"
    assert any("hors décision" in p["message"] for p in bloquants(controles(prop), "citation"))


def test_definition_classee_hors_decision_ne_bloque_pas():
    # 12/tempete restreint la garantie (le titre de l'article dit « Tempête ») : non employée, elle bloque ; citée
    # « hors décision » par le relecteur, elle compte comme employée (7.99, le contenu de A en responsabilité civile).
    prop = copy.deepcopy(BONNE)
    prop["definitions"] = []
    prop["garanties"][0]["circonstances"] = []
    assert any("12/tempete" in p["message"] for p in bloquants(controles(prop)))
    prop["hors_decision"] = [{"article": "12/tempete", "texte": "L’action du vent mesurée à une vitesse de pointe",
                              "pourquoi": "essai"}]
    assert not any("12/tempete" in p["message"] for p in bloquants(controles(prop)))


def test_condition_des_conditions_particulieres_mise_en_reserve():
    """7.69 : « en fonction des couvertures mentionnées dans vos conditions particulières » devient une réserve
    (exclusion « non condition », à demander), pour tout contrat ; une formule à plusieurs valeurs reste posée."""
    prop = copy.deepcopy(BONNE)
    g = prop["garanties"][0]
    g["circonstances"].append({"condition": {"f": ["couverture_contenu", "oui"]}, "article": "2.2",
                               "texte": "en fonction des couvertures mentionnées dans vos conditions particulières"})
    g["circonstances"].append({"condition": {"f": ["formule", "privilege"]}, "article": "2.2",
                               "texte": "selon la formule de vos conditions particulières"})
    g["perimetre"].append({"f": ["option_tempete_x", "oui"]})
    prop["vocabulaire_manquant"].append({"variable": "option_tempete_x", "valeurs": ["oui", "non"],
                                         "question": "Vos conditions particulières mentionnent-elles la tempête ?"})
    notes = redaction.conditions_particulieres_en_reserve(prop)
    assert len(notes) == 2
    assert [c["condition"] for c in g["circonstances"]] == [{"concept": "tempete"}, {"f": ["formule", "privilege"]}]
    assert {"f": ["option_tempete_x", "oui"]} not in g["perimetre"]
    reserves = [x for x in g["exclusions"] if "non" in x["condition"]]
    assert [x["condition"]["non"]["f"][0] for x in reserves] == ["couverture_contenu", "option_tempete_x"]
    assert all(x["a_demander"] and x["portee"] == "tout" for x in reserves)
    assert redaction.conditions_particulieres_en_reserve(prop) == [], "une seconde passe ne change rien"


def test_non_traduit_d_accessoires_ne_bloque_pas():
    prop = copy.deepcopy(BONNE)
    assert any("déclaré non traduit" in p["message"] for p in bloquants(controles(prop), "couverture"))
    prop["garanties"][0]["accessoire"] = True
    assert not any("déclaré non traduit" in p["message"] for p in bloquants(controles(prop), "couverture"))


def test_extension_de_definition_en_prolog_et_controles(voc_etendu):
    """7.69 : une extension de lieu élargit une définition du contrat (le bâtiment) au lieu d'être une garantie."""
    prop = copy.deepcopy(BONNE)
    prop["extensions"] = [{"concept": "batiment", "condition": {"et": [{"f": ["sejour_temporaire", "oui"]},
                                                                    {"f": ["lieu", "autre_batiment"]}]},
                           "article": "2.2", "texte": "Nous couvrons les dommages matériels"}]
    assert "extension(batiment, et([f(sejour_temporaire, oui), f(lieu, autre_batiment)]), '2.2'" in redaction.en_prolog(prop, "2.2")
    assert not [p for p in bloquants(controles(prop), "concept") if "extension" in p["message"]]
    prop["extensions"][0]["concept"] = "piscine_couverte"
    assert any("extension d'un concept inconnu" in p["message"] and "concepts de ce contrat" in p["message"]
               and "batiment" in p["message"] for p in bloquants(controles(prop), "concept")), \
        "le message donne les concepts du contrat (7.72 : le modèle employait ceux d'un autre assureur)"
    prop["extensions"][0]["concept"] = "batiment"
    voc = prolog.vocabulaire(voc_etendu)
    voc["sejour_temporaire"]["pour"] = ["vol"]
    voc["sejour_temporaire"].pop("si", None)
    redaction.ranger(voc, voc_etendu)
    ajouts = redaction.accepter_vocabulaire(prop, voc_etendu)
    sejour = prolog.vocabulaire(voc_etendu)["sejour_temporaire"]
    assert sejour["pour"] == ["vol"] and sejour["si"] == {"lieu": ["autre_batiment"]}, \
        "lue pour le vol comme avant, et aussi quand le lieu lu est un autre bâtiment (7.70)"
    assert any("sejour_temporaire : lue aussi si lieu = autre_batiment" in a for a in ajouts)


def test_variable_d_extension_lue_si_son_lieu_est_lu():
    """7.70 : une variable d'extension n'allonge pas la lecture de chaque sinistre ; elle est demandée quand le
    temps 1 a lu le lieu qui l'entame. Une variable d'accessoire n'est pas lue."""
    voc = {"evenement": {"valeurs": ["incendie"]}, "bien": {"valeurs": []}, "lieu": {"valeurs": []},
           "flammes": {"valeurs": ["oui", "non"], "pour": ["incendie"]},
           "sejour_temporaire": {"valeurs": ["oui", "non"], "pour": ["vol"], "si": {"lieu": ["autre_batiment"]}},
           "malveillance_auteur": {"valeurs": ["oui", "non"], "pour": [redaction.ACCESSOIRE]}}
    au_logement = lecture.variables_du_temps_2(voc, ["incendie"], {"lieu": ["logement"]})
    a_l_hotel = lecture.variables_du_temps_2(voc, ["incendie"], {"lieu": ["autre_batiment"]})
    assert set(au_logement) == {"flammes"} and set(a_l_hotel) == {"flammes", "sejour_temporaire"}


def test_circonstance_propre_a_un_evenement_et_obligation_situation():
    """7.71 : « la chute ; le vol hors du bâtiment, pour autant qu'une plainte soit déposée » : la plainte ne vaut
    que pour le vol. Et une obligation écrite comme une situation ferait refuser tout autre sinistre."""
    prop = copy.deepcopy(BONNE)
    g = prop["garanties"][0]
    g["perimetre"] = [{"ou": [{"f": ["evenement", "heurt"]}, {"f": ["evenement", "vol"]}]}]
    g["circonstances"] = [{"condition": {"et": [{"f": ["evenement", "vol"]}, {"f": ["plainte_deposee", "oui"]}]},
                           "article": "2.2", "texte": "pour autant qu'une plainte soit déposée"}]
    assert redaction.circonstances_par_evenement(prop)
    assert g["circonstances"][0]["condition"] == {"si": [{"f": ["evenement", "vol"]}, {"f": ["plainte_deposee", "oui"]}]}
    assert redaction.circonstances_par_evenement(prop) == [], "une seconde passe ne change rien"
    g["obligations"] = [{"condition": {"et": [{"f": ["lieu", "vehicule"]}, {"f": ["vehicule_ferme_cle", "oui"]}]},
                         "exception": None, "lien_causal": False, "article": "2.2", "texte": "fermer le véhicule à clé"}]
    assert redaction.obligations_mal_formees(prop)
    g["obligations"][0]["condition"] = {"si": [{"f": ["lieu", "vehicule"]}, {"f": ["vehicule_ferme_cle", "oui"]}]}
    assert redaction.obligations_mal_formees(prop) == []


def test_variables_lues_selon_l_evenement_et_le_lieu_qui_les_entourent(voc_etendu):
    """7.71 : « vol et laissé sans surveillance » ne se lit que pour le vol ; « véhicule et habitacle fermé » ne se
    lit que si le lieu lu est un véhicule. Une valeur hors identifiant est refusée en clair."""
    prop = copy.deepcopy(BONNE)
    g = prop["garanties"][0]
    g["perimetre"] = [{"ou": [{"f": ["evenement", "heurt"]}, {"f": ["evenement", "vol"]}]}]
    g["exclusions"] = [
        {"condition": {"et": [{"f": ["evenement", "vol"]}, {"f": ["sans_surveillance_x", "oui"]}]}, "portee": "tout",
         "a_demander": True, "article": "2.2", "texte": "t"},
        {"condition": {"et": [{"f": ["evenement", "vol"]}, {"f": ["lieu", "vehicule"]}, {"f": ["habitacle_x", "non"]}]},
         "portee": "tout", "a_demander": True, "article": "2.2", "texte": "t"}]
    prop["vocabulaire_manquant"] = [
        {"variable": "sans_surveillance_x", "valeurs": ["oui", "non"], "question": "?"},
        {"variable": "habitacle_x", "valeurs": ["oui", "non"], "question": "?"},
        {"variable": "periode_x", "valeurs": ["22h_7h", "jour"], "question": "?"}]
    assert redaction.evenements_par_variable(prop)["sans_surveillance_x"] == ["vol"]
    assert redaction.lieux_par_variable(prop) == {"habitacle_x": ["vehicule"]}
    ajouts = redaction.accepter_vocabulaire(prop, voc_etendu)
    voc = prolog.vocabulaire(voc_etendu)
    assert voc["habitacle_x"]["seulement_si"] == {"lieu": ["vehicule"]} and "seulement_si" not in voc["sans_surveillance_x"]
    assert "periode_x" not in voc and any(a.startswith("! periode_x refusée") and "22h_7h" in a for a in ajouts)
    a_la_cave = lecture.variables_du_temps_2(voc, ["vol"], {"lieu": ["cave"]})
    dans_la_voiture = lecture.variables_du_temps_2(voc, ["vol"], {"lieu": ["vehicule"]})
    assert "habitacle_x" not in a_la_cave and "habitacle_x" in dans_la_voiture and "sans_surveillance_x" in a_la_cave


def test_vocabulaire_sans_pseudo_evenement_ni_variable_lue_partout(voc_etendu):
    """7.73 : une variable déjà lue pour le vol, employée par une accessoire, ne reçoit pas « accessoire » dans son
    « pour » ; une variable d'extension sans lieu qui la déclenche n'est pas lue pour chaque sinistre ; une ligne
    par fait dans le compte rendu."""
    prop = copy.deepcopy(BONNE)
    prop["evenements"] = []
    prop["garanties"] = [{"id": "frais_x", "nom": "Frais", "article": "2.2", "texte": "t", "accessoire": True,
                          "perimetre": [{"f": ["sejour_temporaire", "oui"]}], "circonstances": [], "obligations": [],
                          "exclusions": [], "limites": []}]
    prop["extensions"] = [
        {"concept": "batiment", "condition": {"et": [{"f": ["demenagement", "oui"]}, {"f": ["delai_x", "court"]}]},
         "article": "2.2", "texte": "t"},
        {"concept": "batiment", "condition": {"et": [{"f": ["lieu", "autre_batiment"]},
                                                     {"ou": [{"f": ["pays_x", "lu"]}, {"f": ["pays_x", "autre"]}]}]},
         "article": "2.2", "texte": "t"}]
    prop["vocabulaire_manquant"] = [{"variable": "delai_x", "valeurs": ["court", "long"], "question": "?"},
                                    {"variable": "pays_x", "valeurs": ["lu", "autre"], "question": "?"}]
    avant = prolog.vocabulaire(voc_etendu)["sejour_temporaire"]["pour"]
    ajouts = redaction.accepter_vocabulaire(prop, voc_etendu)
    voc = prolog.vocabulaire(voc_etendu)
    assert voc["sejour_temporaire"]["pour"] == avant and redaction.ACCESSOIRE not in avant
    assert voc["delai_x"]["pour"] == [redaction.EXTENSION]
    assert "delai_x" not in lecture.variables_du_temps_2(voc, ["incendie"], {"lieu": ["logement"]})
    assert len(ajouts) == len(set(ajouts)) and sum(a.startswith("pays_x : lue aussi si") for a in ajouts) == 1


def test_accessoire_sans_exclusion_ne_bloque_pas():
    """7.73 : une accessoire ne décide rien ; qu'elle n'ait pas les exclusions de l'article ne bloque pas."""
    prop = copy.deepcopy(BONNE)
    prop["garanties"][0]["exclusions"] = []
    ctl = controles(prop)
    assert any(c["controle"] == "exclusions" and c["gravite"] == redaction.BLOQUANT for c in ctl)
    prop["garanties"][0]["accessoire"] = True
    assert not any(c["controle"] == "exclusions" and c["gravite"] == redaction.BLOQUANT for c in controles(prop))


def test_une_reduction_d_indemnite_n_est_pas_une_obligation():
    """7.81 : « l'indemnité due sera réduite de moitié » ne refuse pas ; une obligation tirée d'une telle clause
    bloque (le jeu fermé, f-b02 : le gel sans vidange était refusé)."""
    devoir = "vidanger ou protéger les conduites"
    clauses = CLAUSES + [Clause(id="9.9", article="9.9", titre="Prévention", chemin=["9", "9.9"], type=TypeClause.CONDITION,
                                texte=f"L'assuré doit {devoir}. Sinon, l'indemnité due sera réduite de moitié.")]
    prop = copy.deepcopy(BONNE)
    prop["garanties"][0]["obligations"] = [{"condition": {"f": ["prevention_gel", "oui"]}, "exception": None,
                                            "lien_causal": True, "article": "9.9", "texte": devoir}]
    pl = redaction.retirer_article(prolog.fichier_regles(CONTRAT).read_text(encoding="utf-8"), "2.2")
    ctl = redaction.controler(copy.deepcopy(prop), clauses, pl, "2.2")
    assert any(c["gravite"] == redaction.BLOQUANT and "réduit l'indemnité" in c["message"] for c in ctl)


def test_article_d_exclusions_generales_vise_toutes_les_garanties():
    """7.88 : un article sans garantie, fait d'exclusions générales, les applique à tout le contrat (`tous`)."""
    prop = {"evenements": [], "garanties": [], "definitions": [], "exclusions_communes": [
        {"condition": {"f": ["intentionnel", "oui"]}, "portee": "tout", "a_demander": False, "article": "S25",
         "texte": "les dommages intentionnellement causés"}]}
    assert not any("aucune garantie" in e for e in redaction.erreurs_schema(prop))
    pl = redaction.en_prolog(prop, "S25")
    assert "exclusion(tous, f(intentionnel, oui), tout, non, 'S25'" in pl and "evenement_traduit" not in pl


def test_article_sans_garantie_ses_reserves_ne_sont_pas_lues(voc_etendu):
    """7.90 : une variable d'un article sans garantie, qui ne sert qu'à une exclusion jamais demandée (une option,
    une rixe), n'est jamais lue ; un bien sous un « non » n'entame pas une extension."""
    prop = {"evenements": [], "garanties": [], "definitions": [],
            "exclusions_communes": [{"condition": {"et": [{"f": ["bien", "velo"]}, {"non": {"f": ["option_x", "oui"]}}]},
                                     "portee": {"bien": "velo"}, "a_demander": False, "article": "2.2", "texte": "t"}],
            "extensions": [{"concept": "batiment", "article": "2.2", "texte": "t", "condition": {"et": [
                {"f": ["lieu", "autre_batiment"]}, {"f": ["pays_y", "lu"]}, {"non": {"f": ["bien", "bijoux"]}}]}}],
            "vocabulaire_manquant": [{"variable": "option_x", "valeurs": ["oui", "non"], "question": "?"},
                                     {"variable": "pays_y", "valeurs": ["lu", "autre"], "question": "?"}]}
    redaction.accepter_vocabulaire(prop, voc_etendu)
    voc = prolog.vocabulaire(voc_etendu)
    assert voc["option_x"]["pour"] == [redaction.JAMAIS]
    assert "option_x" not in lecture.variables_du_temps_2(voc, ["vol"], {"lieu": ["logement"]})
    assert voc["pays_y"]["si"] == {"lieu": ["autre_batiment"]}, "« sans les bijoux » n'entame pas l'extension"


def test_garantie_accessoire_en_prolog():
    prop = copy.deepcopy(BONNE)
    prop["garanties"][0]["accessoire"] = True
    pl = redaction.en_prolog(prop, "4")
    assert "accessoire(tempete_batiment)." in pl
    assert "evenement_traduit(" not in pl, "des frais accessoires ne traduisent pas l'événement (7.68)"


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

    # Corrigée puis acceptée de nouveau, la proposition remplace l'ancienne (7.58) au lieu de s'y ajouter.
    corrige["proposition"]["garanties"][0]["nom"] = "Tempête (corrigée)"
    js.write_text(json.dumps(corrige, ensure_ascii=False), encoding="utf-8")
    assert not bloquants(redaction.recontroler(CONTRAT, "2.2", CLAUSES, tmp_path)["controles"])
    redaction.accepter(CONTRAT, "2.2", tmp_path)
    texte = regles.read_text(encoding="utf-8")
    assert texte.count("garantie(tempete_batiment,") == 1 and "Tempête (corrigée)" in texte
    assert texte.count("% --- Art. 2.2 : proposition") == 1


def test_jeu_redaction_coherent():
    from couverture.evaluation import charger_cas, fichiers_jeu

    racine = Path(__file__).resolve().parents[1] / "data"
    cas = charger_cas(*fichiers_jeu(racine, CONTRAT, "redaction"))
    assert len(cas) >= 10 and {c["famille"] for c in cas} == {"tempete", "bris"}


def test_consigne_de_redaction_versionnee():
    from couverture.consignes import CONSIGNES

    assert CONSIGNES["couverture-redaction-regles"][2] == "v12"


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


def test_une_variable_jamais_lue_le_reste(voc_etendu):
    """7.91 : une option des conditions particulières (« jamais » lue) employée par une garantie reste non lue."""
    voc = prolog.vocabulaire(voc_etendu)
    voc["pack_y"] = {"valeurs": ["oui", "non"], "question": "?", "pour": [redaction.JAMAIS]}
    redaction.ranger(voc, voc_etendu)
    prop = {"evenements": ["tempete"], "definitions": [], "garanties": [{
        "id": "t", "nom": "t", "article": "1", "texte": "t", "perimetre": [{"f": ["evenement", "tempete"]}],
        "circonstances": [], "obligations": [], "limites": [],
        "exclusions": [{"condition": {"non": {"f": ["pack_y", "oui"]}}, "portee": "tout", "a_demander": True,
                        "article": "1", "texte": "t"}]}], "vocabulaire_manquant": []}
    redaction.accepter_vocabulaire(prop, voc_etendu)
    assert prolog.vocabulaire(voc_etendu)["pack_y"]["pour"] == [redaction.JAMAIS]


def test_concepts_definis_l_un_par_l_autre():
    """7.91 : une extension de `batiment` qui emploie `contenu`, lui-même défini dans le `batiment`, bouclait."""
    pl = ('definition(contenu, et([f(bien, mobilier), concept(batiment)]), \'1.2-a\', "c").\n'
          'definition(batiment, f(lieu, logement), \'1.1-a\', "b").\n')
    prop = {"extensions": [{"concept": "batiment", "condition": {"et": [{"f": ["lieu", "autre_batiment"]},
                                                                         {"concept": "contenu"}]}}]}
    assert redaction.cycle_de_concepts(pl, prop) in (["batiment", "contenu", "batiment"], ["contenu", "batiment", "contenu"])
    prop["extensions"][0]["condition"]["et"][1] = {"f": ["bien", "mobilier"]}
    assert redaction.cycle_de_concepts(pl, prop) == []


def test_exclusion_commune_qui_nomme_ses_garanties():
    """7.96 : les biens exclus des dommages aux biens n'excluent pas la responsabilité civile (« cibles »)."""
    prop = {"garanties": [], "exclusions_communes": [
        {"condition": {"f": ["bien", "vehicule_moteur"]}, "portee": {"bien": "vehicule_moteur"}, "a_demander": False,
         "article": "1.2-b", "texte": "t", "cibles": ["vol_vandalisme", "bris_glaces"]},
        {"condition": {"f": ["intentionnel", "oui"]}, "portee": "tout", "a_demander": False, "article": "S25", "texte": "t"}]}
    pl = redaction.en_prolog(prop, "1.2")
    assert "exclusion([vol_vandalisme, bris_glaces], f(bien, vehicule_moteur)" in pl
    assert "exclusion(tous, f(intentionnel, oui)" in pl


def test_le_vocabulaire_est_range():
    """7.119 : le socle et les variables que plusieurs contrats emploient sont dans commun.json ; celles qu'un
    seul emploie, dans son fichier. Après des règles écrites à la main : `couverture regles --contrat … --ranger`."""
    assert redaction.mal_rangees() == []
    voc = prolog.vocabulaire()
    assert list(voc)[:3] == ["evenement", "bien", "lieu"]
    for contrat in prolog.contrats_regles():
        propres = json.loads((prolog.VOCABULAIRE / f"{contrat}.json").read_text(encoding="utf-8"))["variables"]
        assert propres and set(propres) <= prolog.variables_employees(contrat)
        assert not any(set(propres) & prolog.variables_employees(c) for c in prolog.contrats_regles() if c != contrat)
