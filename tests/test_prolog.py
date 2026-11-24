"""Méthode « regles » : règles Prolog d'un contrat, moteur, lecture des faits, mise en forme.

Sans SWI-Prolog, les règles sont vérifiées par une seconde implémentation du moteur en Python
(tests/moteur_reference.py). Avec SWI-Prolog, un test différentiel vérifie que les deux moteurs
donnent les mêmes réponses sur tous les cas."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from couverture import chaine, lecture, prolog
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
    f, notes = lecture.au_vocabulaire({"evenement": ["accident"], "bien": ["miroir"], "lieu": ["logement"]}, voc)
    assert f["evenement"] == ["bris"] and notes
    f, _ = lecture.au_vocabulaire({"evenement": ["accident"], "bien": ["objet_divers"]}, voc)
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
        if systeme == lecture.SYSTEME_VERIFICATION:  # la vérification ne retire rien ici
            return json.dumps({"verdicts": {}})
        assert "Vocabulaire" in message, "le modèle reçoit le vocabulaire"
        return json.dumps({"faits": self.faits})


def test_lecture_des_faits_filtre_le_hors_vocabulaire():
    faits, ecarts = lecture.extraire_faits_regles(
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
    p = chaine.PipelineRegles(CONTRAT, [], FauxLLM({"evenement": "vol", "lieu": ["parties_communes"]}),
                              decideur=lambda faits: reponse)
    r = p.analyser("Vélo volé dans le local commun.")
    v = r.verdict
    assert v.decision == Decision.INCERTAIN, "sans les clauses en base, la citation ne se vérifie pas : prudence"
    assert r.faits.lieux == ["parties_communes"]

    from couverture.models import Clause, TypeClause
    clause = Clause(id="2.10-a", article="2.10-a", titre="Exclusions", chemin=["2.10-a"], type=TypeClause.EXCLUSION,
                    texte="nous ne garantissons pas : • le vol ou le vandalisme dans les parties communes du bâtiment",
                    pages=[12])
    p = chaine.PipelineRegles(CONTRAT, [clause], FauxLLM({"evenement": "vol"}), decideur=lambda faits: reponse)
    v = p.analyser("Vélo volé dans le local commun.").verdict
    assert v.decision == Decision.NON_COUVERT and v.citations[0].valide and v.citations[0].pages == [12]
    assert "2.10-a" not in v.justification or "exclusion" in v.justification


def test_la_reponse_ne_nomme_que_les_garanties_etablies():
    """7.164. Une exclusion certaine écarte une garantie même quand on ne sait pas si elle s'appliquerait. La réponse
    cite alors l'exclusion, sans nommer cette garantie : rien ne dit qu'elle concernait le sinistre."""
    from pathlib import Path
    assert chaine.EXCLUE_SANS_ETRE_ETABLIE in Path(prolog.MOTEUR).read_text(encoding="utf-8"), \
        "le moteur et la chaîne doivent employer le même motif"

    def retenue(nom, motif, article="3.1.6.2", texte="les vols des biens se trouvant à l'extérieur"):
        return {"id": nom, "garantie": nom, "article": "3.1.6.1", "rattachement": "rattachée", "decision": "NON_COUVERT",
                "motif": motif, "preuves": [{"article": article, "texte": texte, "role": "exclusion"}],
                "questions": [], "reserves": [], "partielles": []}

    def phrase(retenues):
        reponse = {"decision": "NON_COUVERT", "possibles": [], "retenues": retenues}
        p = chaine.PipelineRegles(CONTRAT, [], FauxLLM({"evenement": "vol"}), decideur=lambda faits: reponse)
        return p.verdict(reponse, {"evenement": ["vol"]})[0]

    sans = chaine.EXCLUE_SANS_ETRE_ETABLIE
    v = phrase([retenue("Vol Privilège concierge", sans), retenue("Vol par agression", sans)])
    assert v.justification == "Non couvert : le contrat exclut ce cas (3.1.6.2)."
    assert [c.clause_id for c in v.citations] == ["3.1.6.2"], "la clause d'exclusion reste citée"

    v = phrase([retenue("Vol du contenu", "une exclusion s'applique", "2.10-a"), retenue("Vol par agression", sans)])
    assert "Vol du contenu" in v.justification and "agression" not in v.justification
    assert {c.clause_id for c in v.citations} == {"2.10-a", "3.1.6.2"}

    v = phrase([retenue("Vol du contenu", "une exclusion s'applique", "2.10-a")])
    assert v.justification == "Non couvert. « Vol du contenu » (3.1.6.1) : une exclusion s'applique."


def test_une_garantie_sans_rapport_avec_l_evenement_n_est_ni_nommee_ni_citee():
    """7.165. La bougie fondue de l'énoncé : aucune garantie ne s'applique. La réponse ne cite pas les articles du vol."""
    def hors(nom, article):
        return {"id": nom, "garantie": nom, "article": article, "rattachement": "hors", "decision": "NON_COUVERT",
                "motif": "hors de son périmètre", "preuves": [{"article": article, "texte": "…", "role": "garantie"}],
                "questions": [], "reserves": [], "partielles": []}

    def verdict(reponse):
        p = chaine.PipelineRegles(CONTRAT, [], FauxLLM({"evenement": "accident"}), decideur=lambda faits: reponse)
        return p.verdict(reponse, {"evenement": ["accident"]})[0]

    rs = [hors("vol_batiment", "2.10"), hors("incendie", "2.1")]
    v = verdict({"decision": "NON_COUVERT", "aucune": True, "possibles": [], "retenues": rs, "visent_evenement": []})
    assert v.justification == "Non couvert : aucune garantie de ce contrat ne porte sur cet événement." and not v.citations
    v = verdict({"decision": "NON_COUVERT", "aucune": True, "possibles": [], "retenues": rs, "visent_evenement": ["incendie"]})
    assert v.justification == "Non couvert : aucune garantie ne s'applique." and [c.clause_id for c in v.citations] == ["2.1"]
    v = verdict({"decision": "INCERTAIN", "aucune": False, "non_traduits": ["accident"], "possibles": [], "retenues": rs,
                 "visent_evenement": []})
    assert "pas encore traduite en règles." in v.justification and "vol_batiment" not in v.justification and not v.citations
    v = verdict({"decision": "NON_COUVERT", "aucune": True, "possibles": [], "retenues": rs})
    assert len(v.citations) == 2, "sans l'indication du moteur, rien ne change"

    from moteur_reference import Contrat, Explorateur
    a = Contrat(prolog.fichier_regles(CONTRAT))
    d = Explorateur(a, {"evenement": ["accident"], "bien": ["mobilier_jardin"], "lieu": ["jardin"]}).decider()
    assert d["decision"] == "NON_COUVERT" and d["aucune"] and "vol_batiment" not in d["visent_evenement"]
    d = Explorateur(a, {"evenement": ["vol"], "bien": ["velo"], "lieu": ["parties_communes"]}).decider()
    assert "vol_batiment" in d["visent_evenement"]


def test_la_phrase_regroupe_par_article_et_se_tait_quand_le_dossier_part_chez_un_gestionnaire():
    """7.167. Trois garanties du même article écartées pour la même raison se disent une fois. Et quand l'événement
    relève d'une garantie non traduite, les garanties qui ne jouent pas ne sont ni nommées ni citées."""
    def retenue(nom, article, rattachement="hors", motif="hors de son périmètre"):
        return {"id": nom, "garantie": nom, "article": article, "rattachement": rattachement, "decision": "NON_COUVERT",
                "motif": motif, "preuves": [{"article": article, "texte": nom, "role": "garantie"}],
                "questions": [], "reserves": [], "partielles": []}

    def verdict(reponse):
        p = chaine.PipelineRegles(CONTRAT, [], FauxLLM({"evenement": "accident"}), decideur=lambda faits: reponse)
        return p.verdict(reponse, {"evenement": ["accident"]})[0]

    bris = [retenue("Bris de glaces", "2.7-a"), retenue("Bris de glace +", "2.7-a"), retenue("Incendie", "2.1-a")]
    ids = [r["id"] for r in bris]
    v = verdict({"decision": "NON_COUVERT", "possibles": [], "retenues": [dict(r, rattachement="rattachée") for r in bris]})
    assert v.justification == ("Non couvert. « Bris de glaces », « Bris de glace + » (2.7-a) : hors de son périmètre ; "
                               "« Incendie » (2.1-a) : hors de son périmètre.")

    v = verdict({"decision": "INCERTAIN", "aucune": False, "non_traduits": ["accident"], "possibles": [], "retenues": bris,
                 "visent_evenement": ids})
    assert v.justification.endswith("pas encore traduite en règles.") and not v.citations
    possible = retenue("Bris de vitrages", "3.1.5.1", "possible", "pourrait s'appliquer, selon des faits non précisés")
    v = verdict({"decision": "INCERTAIN", "aucune": False, "non_traduits": ["accident"], "possibles": [],
                 "retenues": bris + [possible], "visent_evenement": ids + ["Bris de vitrages"]})
    assert "« Bris de vitrages » (3.1.5.1) : pourrait s'appliquer" in v.justification and "2.7-a" not in v.justification
    assert [c.clause_id for c in v.citations] == ["3.1.5.1"]


class FauxLLMPlusieurs:
    """Lit « vol » ou « bris » selon le texte reçu, et découpe la déclaration comme on le lui a dit."""
    nom = "faux"

    def __init__(self, decoupage):
        self.decoupage, self.decoupes = decoupage, 0

    def completer(self, systeme, message):
        if systeme == lecture.SYSTEME_DECOUPAGE:
            self.decoupes += 1
            return json.dumps({"sinistres": self.decoupage})
        if systeme == lecture.SYSTEME_VERIFICATION:
            return json.dumps({"verdicts": {}})
        declaration = message.split("Déclaration")[-1]
        evenements = [e for e, mot in (("vol", "volé"), ("bris", "fêlée")) if mot in declaration]
        return json.dumps({"faits": {"evenement": evenements, "lieu": ["garage"]}})


def test_plusieurs_sinistres_une_reponse_pour_chacun(monkeypatch):
    """7.168. Une déclaration qui raconte deux sinistres reçoit deux lignes, chacune avec sa décision et sa clause ;
    une cause et ses conséquences restent un seul sinistre ; une phrase que la déclaration ne contient pas est écartée."""
    from couverture.api import service
    from couverture.models import Clause, TypeClause

    declaration = "On m'a volé mon vélo dans le garage. J'ai porté plainte. Une vitre de la véranda est fêlée."
    clauses = [Clause(id=i, article=i, titre="t", chemin=[i], type=t, texte=x, pages=[1]) for i, t, x in (
        ("2.10-a", TypeClause.EXCLUSION, "le vol sans effraction"), ("2.9", TypeClause.GARANTIE, "le bris des vitres"))]

    def decideur(faits):
        if faits.get("evenement") == ["vol"]:
            return {"decision": "NON_COUVERT", "possibles": [], "retenues": [{
                "id": "vol", "garantie": "Vol", "article": "2.10", "rattachement": "rattachée", "decision": "NON_COUVERT",
                "motif": "une exclusion s'applique", "questions": [], "reserves": [], "partielles": [],
                "preuves": [{"article": "2.10-a", "texte": "le vol sans effraction", "role": "exclusion"}]}]}
        return {"decision": "COUVERT", "possibles": [], "retenues": [{
            "id": "bris", "garantie": "Bris de vitres", "article": "2.9", "rattachement": "rattachée", "decision": "COUVERT",
            "motif": "s'applique", "questions": [], "reserves": [], "partielles": [],
            "preuves": [{"article": "2.9", "texte": "le bris des vitres", "role": "garantie"}]}]}

    deux = [{"titre": "Vol du vélo", "phrases": ["On m'a volé mon vélo dans le garage.", "J'ai porté plainte.",
                                                "Le voleur portait un masque."]},
            {"titre": "Vitre fêlée", "phrases": ["Une vitre de la véranda est fêlée."]}]
    llm = FauxLLMPlusieurs(deux)
    p = chaine.PipelineRegles(CONTRAT, clauses, llm, decideur=decideur)
    r = p.analyser(declaration)
    assert [x.titre for x in r.parties] == ["Vol du vélo", "Vitre fêlée"]
    assert r.parties[0].sinistre == "On m'a volé mon vélo dans le garage. J'ai porté plainte.", "la phrase inventée est écartée"
    assert [x.verdict.decision for x in r.parties] == [Decision.NON_COUVERT, Decision.COUVERT]
    assert r.verdict.decision == Decision.INCERTAIN, "pas de réponse ferme pour le tout quand les sinistres diffèrent"
    lignes = r.verdict.justification.split("\n")
    assert lignes[0].startswith("2 sinistres dans cette déclaration")
    assert lignes[1].startswith("1. Vol du vélo : Non couvert.") and "(2.10)" in lignes[1]
    assert lignes[2].startswith("2. Vitre fêlée : Couvert.") and "(2.9)" in lignes[2]
    assert {c.clause_id for c in r.verdict.citations} == {"2.10-a", "2.9"}

    _, sortie = service.analyser(p, declaration)
    assert [s["titre"] for s in sortie["sinistres"]] == ["Vol du vélo", "Vitre fêlée"]
    assert [s["decision"] for s in sortie["sinistres"]] == ["NON_COUVERT", "COUVERT"]
    assert sortie["a_preciser"] == [] and sortie["sinistres"][1]["citations"][0]["clause_id"] == "2.9"

    # Une cause et ses conséquences : le modèle ne rend qu'un sinistre, la réponse est celle d'avant.
    p = chaine.PipelineRegles(CONTRAT, clauses, FauxLLMPlusieurs([deux[0]]), decideur=decideur)
    r = p.analyser(declaration)
    assert r.parties == [] and "\n" not in r.verdict.justification
    # Un seul événement lu : le découpage n'est pas demandé.
    llm = FauxLLMPlusieurs(deux)
    chaine.PipelineRegles(CONTRAT, clauses, llm, decideur=decideur).analyser("On m'a volé mon vélo dans le garage.")
    assert llm.decoupes == 0
    # Et il se désactive.
    monkeypatch.setenv("COUVERTURE_DECOUPAGE", "non")
    llm = FauxLLMPlusieurs(deux)
    assert chaine.PipelineRegles(CONTRAT, clauses, llm, decideur=decideur).analyser(declaration).parties == []
    assert llm.decoupes == 0


def test_verdict_evenement_non_traduit():
    reponse = {"decision": "INCERTAIN", "non_traduits": ["tempete"], "aucune": False, "possibles": [], "retenues": [{
        "id": "degats_eaux", "garantie": "Dégâts causés par l’eau", "article": "2.7", "rattachement": "rattachée",
        "decision": "NON_COUVERT", "motif": "une exclusion s'applique", "preuves": [], "questions": [],
        "reserves": [], "partielles": []}]}
    p = chaine.PipelineRegles(CONTRAT, [], FauxLLM({"evenement": ["tempete", "degat_eaux"]}), decideur=lambda f: reponse)
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
        assert p.get("exclusions_etablies") == o.get("exclusions_etablies"), i
        assert sorted(p.get("visent_evenement")) == sorted(o.get("visent_evenement")), i


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
           "type_dommage": "bris", "flammes": "oui", "auteur": "tiers"}
    gardes, retires = prolog.filtrer_faits(lus)
    assert gardes == {"evenement": ["incendie"], "bien": ["mobilier"], "flammes": "oui", "auteur": "tiers"}
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

    faits, ecarts = lecture.extraire_faits_regles("Vélo volé dans le local à vélos de la résidence.", Espion())
    assert "parties_communes (locaux partagés de l'immeuble : local à vélos" in Espion.message
    assert "Où se trouvaient les biens ?" in Espion.message
    assert "cause_eau" not in faits and any("hors sujet" in e for e in ecarts)
    assert "ne donne pas de lieu" in lecture.SYSTEME_LECTURE_SOCLE


def test_un_contrat_ne_lit_que_ses_variables(tmp_path, monkeypatch):
    """Étanchéité entre assureurs (7.57) : une variable ajoutée pour Assureur B (« plainte déposée ») n'entre pas dans
    la lecture d'un vol chez Assureur A, dont les règles ne l'emploient pas."""
    contrat_a = lecture.variables_du_contrat("assureur-a-habitation-2025")
    assert {"effraction", "cles_a_proximite", "serrure_surete"} <= contrat_a
    regles = tmp_path / "x.pl"
    regles.write_text("% f(commentaire, oui)\n/* f(bloc, oui) */\nperimetre(g, f(effraction, oui)).\n", encoding="utf-8")
    monkeypatch.setattr(prolog, "fichier_regles", lambda c: regles)
    # `acces_voleur` implique `effraction` (« sans_effraction » → « non ») : lue aussi (7.101).
    assert lecture.variables_du_contrat("x") == {"effraction", "acces_voleur"}

    class Espion:
        nom = "espion"
        messages = []

        def completer(self, systeme, message):
            Espion.messages.append(message)
            return json.dumps({"faits": {"evenement": ["vol"], "violence": "oui"}})

    faits, _ = lecture.extraire_faits_regles("On m'a volé mon vélo.", Espion(), variables={"effraction"}, verifier=False)
    detail = Espion.messages[-1].split("## Déjà établi")[0]
    assert "effraction" in detail and "violence" not in detail and "violence" not in faits


def test_consigne_de_lecture_garde_ses_regles():
    """La v3 avait perdu « une pièce du logement → lieu = logement » en en ajoutant une autre : dix cas
    couverts sont devenus incertains (DEMARCHE 7.24 bis). Les règles qui ont fait leurs preuves restent, sauf
    celles qu'on retire exprès, une par une et banc à l'appui, quand la banque d'exemples les montre (7.120 : le vol
    sur la personne)."""
    c = lecture.SYSTEME_LECTURE_SOCLE + lecture.SYSTEME_LECTURE_DETAILS
    for regle in ("lieu = logement", "fermeture = cle", "flammes = oui et embrasement = oui",
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
    lignes, motif = chaine.questions_explorees(exploration, ["serrure_surete", "flammes", "lien_causal"], "À préciser.")
    assert lignes[0].startswith(lecture.question("serrure_surete")) and "oui → couvert ; non → non couvert" in lignes[0]
    assert lecture.question("flammes") not in " ".join(lignes), "la question inutile n'est pas posée"
    assert lecture.question("lien_causal") in lignes, "une question sans domaine reste posée"
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
    lignes = chaine.arbre_lisible(d["preuve"])
    texte = "\n".join(lignes)
    assert lignes[0].startswith("Garantie « Vol du contenu dans le bâtiment » (art. 2.10) → non couvert")
    assert "[non] Condition non remplie — art. 2.10" in texte
    assert "serrure_de_surete (art. 12/serrure-de-surete" in texte
    assert "[oui] fermeture = cadenas (déclaré : cadenas)" in texte
    assert "sans objet ici" in texte, "la condition du garage ne s'applique pas à une cave"
    assert "l'assureur devrait les prouver" in texte, "les exclusions présumées sont comptées, pas listées"
    assert len(lignes) < len(chaine.arbre_lisible(d["preuve"], complet=True))


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
    p = chaine.PipelineRegles(CONTRAT, [], FauxLLM(faits), decideur=oracle)
    v = p.analyser("On m'a volé mon vélo dans ma cave fermée par un cadenas.").verdict
    assert v.preuve and v.raisonnement[0].startswith("Garantie « Vol du contenu dans le bâtiment »")
    from couverture.cli.affichage import afficher_court
    from couverture.models import Resultat
    sortie = afficher_court(Resultat(sinistre="…", contrat_id=CONTRAT, methode="regles", faits=chaine.faits_lisibles(faits),
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

    m = Modele()
    # Les variables d'un contrat, comme en service : sur tout le vocabulaire, la longueur mesurée plus bas
    # grandirait avec chaque contrat ajouté (7.151), ce que la lecture d'un sinistre ne fait pas.
    faits, ecarts = lecture.extraire_faits_regles("On m'a volé mon vélo dans ma cave fermée par un cadenas.", m, verifier=False,
                                                  variables=lecture.variables_du_contrat("assureur-a-habitation-2025"))
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


def test_schema_refuse_retombe_sur_le_mode_json(monkeypatch):
    from couverture import llm as module_llm

    envois = []

    def poster(url, corps, entetes, timeout, **_):
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

    faits, _ = lecture.extraire_faits_regles("On m'a volé mon vélo dans ma cave.", Modele(), verifier=False)
    assert faits == {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"]}
    assert "la clé dont le voleur s'est servi" in lecture.SYSTEME_LECTURE_SOCLE


def test_lecture_verifiee(monkeypatch):
    """Les deux temps, puis chaque fait du temps 2 soumis comme une affirmation : « non dit » le retire (7.43).
    Le socle n'est jamais soumis."""
    class Modele:
        nom, accepte_schema = "verif", True

        def __init__(self):
            self.systemes, self.affirmations = [], ""

        def completer(self, systeme, message, schema=None):
            self.systemes.append(systeme)
            if systeme == lecture.SYSTEME_LECTURE_SOCLE:
                return json.dumps({"faits": {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"]}})
            if systeme == lecture.SYSTEME_LECTURE_DETAILS:
                return json.dumps({"faits": {"fermeture": "aucune", "auteur": "tiers", "absence": "oui"}})
            self.affirmations = message
            assert set(schema["properties"]["verdicts"]["properties"]) == {"fermeture", "auteur", "absence"}
            return json.dumps({"verdicts": {"fermeture": "non_dit", "auteur": "non_dit", "absence": "dit"}})

    m = Modele()
    faits, ecarts = lecture.extraire_faits_regles("Pendant mes vacances, on m'a volé mon vélo dans ma cave.", m)
    assert faits == {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"], "absence": "oui"}
    assert m.systemes[-1] == lecture.SYSTEME_VERIFICATION and len(m.systemes) == 3
    assert "Comment le local était-il fermé ?" in m.affirmations and "evenement" not in m.affirmations.split("## Déclaration")[0]
    assert sum("non dit" in e for e in ecarts) == 2


def test_verification_illisible_ne_retire_rien():
    class Modele:
        nom = "illisible"

        def completer(self, systeme, message):
            return "je ne sais pas"

    lus = {"evenement": ["vol"], "fermeture": "cle"}
    gardes, ecarts = lecture.verifier_details("Volé.", lus, Modele(), prolog.vocabulaire())
    assert gardes == lus and "illisible" in ecarts[0]


def test_un_doute_ne_fait_jamais_couvrir(monkeypatch, contrat):
    """La vérification a jugé « non dit » la fenêtre laissée ouverte : sans ce fait, le moteur couvrirait.
    Le moteur arbitre : la lecture non vérifiée est gardée (7.44)."""
    class Modele:
        nom, accepte_schema = "verif", True

        def completer(self, systeme, message, schema=None):
            if systeme == lecture.SYSTEME_LECTURE_SOCLE:
                return json.dumps({"faits": {"evenement": ["vol"], "bien": ["appareil_audiovisuel"], "lieu": ["logement"]}})
            if systeme == lecture.SYSTEME_LECTURE_DETAILS:
                return json.dumps({"faits": {"absence": "oui", "effraction": "non", "fenetres_fermees": "non",
                                             "fermeture": "aucune"}})
            return json.dumps({"verdicts": {"absence": "dit", "effraction": "non_dit", "fenetres_fermees": "non_dit",
                                            "fermeture": "non_dit"}})

    oracle = lambda f: Moteur(contrat, f).decider()
    sinistre = "Pendant que j'étais au travail, on est entré par la fenêtre que j'avais laissée ouverte et on a volé la télé."
    faits, ecarts = lecture.extraire_faits_regles(sinistre, Modele(), oracle)
    assert faits.get("fenetres_fermees") == "non" and any("vérification écartée" in e for e in ecarts)
    assert oracle(faits)["decision"] != "COUVERT"
    # Sans arbitre (ou quand retirer ne fait pas couvrir), la vérification s'applique.
    faits_sans, _ = lecture.extraire_faits_regles(sinistre, Modele())
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


def test_je_ne_sais_pas_plutot_qu_une_reponse_fausse(contrat):
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
    assert "fermeture" in lecture.faits_decisifs(faits, oracle, "NON_COUVERT")

    class Modele:
        nom, accepte_schema = "confirme", True

        def __init__(self, verdict):
            self.verdict, self.confirmations = verdict, []

        def completer(self, systeme, message, schema=None):
            if systeme == lecture.SYSTEME_LECTURE_SOCLE:
                return json.dumps({"faits": {k: faits[k] for k in ("evenement", "bien", "lieu")}})
            if systeme == lecture.SYSTEME_LECTURE_DETAILS:
                return json.dumps({"faits": {"fermeture": "cadenas"}})
            props = set(schema["properties"]["verdicts"]["properties"])
            self.confirmations.append(props)
            if len(self.confirmations) == 1:  # la vérification de la lecture garde le cadenas
                return json.dumps({"verdicts": {v: "dit" for v in props}})
            # la confirmation des faits décisifs, ensuite
            return json.dumps({"verdicts": {v: (self.verdict if v == "fermeture" else "dit") for v in props}})

    sinistre = "On m'a volé mon vélo dans ma cave."
    doute = chaine.PipelineRegles(CONTRAT, [], Modele("non_dit"), decideur=oracle).analyser(sinistre).verdict
    assert doute.decision.value == "INCERTAIN" and (doute.decision_initiale or doute.decision).value == "INCERTAIN"
    assert doute.informations_manquantes[0].startswith(lecture.question("fermeture"))
    assert doute.justification.startswith("Je ne peux pas trancher")
    # 7.127 : en mots du client (la question), sans nom de variable, et sans annoncer la décision d'après.
    assert lecture.question("fermeture") in doute.justification and "fermeture :" not in doute.justification
    assert "Garantie en jeu" in doute.justification and ". Non couvert." not in doute.justification
    m = Modele("dit")
    confirme = chaine.PipelineRegles(CONTRAT, [], m, decideur=oracle).analyser(sinistre).verdict
    # (sans clauses fournies, le contrôle des citations rétrograde toute réponse : on lit la réponse avant lui)
    assert (confirme.decision_initiale or confirme.decision).value == "NON_COUVERT", "confirmé : la réponse ferme reste"
    assert "fermeture" in m.confirmations[-1], "le fait décisif est soumis à confirmation"


def test_un_fait_qui_en_dit_un_autre():
    """7.94 : « sans effraction » dit « effraction = non », sauf si l'effraction est déjà lue."""
    voc = {"acces_voleur": {"valeurs": ["sans_effraction", "escalade"], "implique": {"sans_effraction": {"effraction": "non"}}},
           "effraction": {"valeurs": ["oui", "non"]}}
    assert lecture.impliquer({"acces_voleur": "sans_effraction"}, voc)[0]["effraction"] == "non"
    assert lecture.impliquer({"acces_voleur": "sans_effraction", "effraction": "oui"}, voc)[0]["effraction"] == "oui"
    assert lecture.impliquer({"acces_voleur": "escalade"}, voc)[0] == {"acces_voleur": "escalade"}


def test_la_source_d_un_fait_deduit():
    """7.95 : on confirme « acces_voleur = sans_effraction », d'où vient « effraction = non »."""
    voc = {"acces_voleur": {"valeurs": ["sans_effraction"], "implique": {"sans_effraction": {"effraction": "non"}}},
           "effraction": {"valeurs": ["oui", "non"]}}
    assert lecture.sources_impliquees({"acces_voleur": "sans_effraction", "effraction": "non"}, voc) == {"effraction": "acces_voleur"}
    assert lecture.sources_impliquees({"acces_voleur": "sans_effraction", "effraction": "oui"}, voc) == {}


def test_accident_retire_quand_un_autre_evenement_le_dit():
    """7.97 : « accident » lu avec « responsabilité » ou « tempête » est retiré ; seul, il reste."""
    voc = {"evenement": {"valeurs": ["accident", "responsabilite", "tempete", "bris"], "plusieurs": True, "preciser": {"accident": [
        {"si": {"bien": ["vitre"]}, "en": "bris"},
        {"si": {"evenement": ["responsabilite", "tempete", "bris"]}, "en": None}]}},
        "bien": {"valeurs": ["vitre", "mobilier"]}}
    assert lecture.preciser({"evenement": ["accident", "responsabilite"]}, voc)[0]["evenement"] == ["responsabilite"]
    assert lecture.preciser({"evenement": ["accident"], "bien": "vitre"}, voc)[0]["evenement"] == ["bris"]
    assert lecture.preciser({"evenement": ["accident"], "bien": "mobilier"}, voc)[0]["evenement"] == ["accident"]


def test_un_fait_ajoute_une_valeur_a_une_variable_multiple():
    """7.105 : « les égouts ont refoulé » (`cause_eau = inondation`) est aussi une catastrophe naturelle ; l'eau reste."""
    voc = {"cause_eau": {"valeurs": ["inondation", "gel"], "implique": {"inondation": {"evenement": "catastrophe_naturelle"}}},
           "evenement": {"valeurs": ["degat_eaux", "catastrophe_naturelle"], "plusieurs": True}}
    faits, notes = lecture.impliquer({"evenement": ["degat_eaux"], "cause_eau": "inondation"}, voc)
    assert faits["evenement"] == ["degat_eaux", "catastrophe_naturelle"] and notes
    assert lecture.impliquer({"evenement": ["degat_eaux"], "cause_eau": "gel"}, voc)[0]["evenement"] == ["degat_eaux"]
    deja = {"evenement": ["catastrophe_naturelle"], "cause_eau": "inondation"}
    assert lecture.impliquer(deja, voc) == (deja, [])


def test_condition_fausse_sur_un_perimetre_inconnu_ne_refuse_pas():
    """7.105 : « jai une fuite » chez B (bien et lieu inconnus). La dégradation du linge et la décongélation ont un
    périmètre fait d'un bien, inconnu, et une condition fausse (pas d'incendie) : elles ne jouent pas, mais ne sont
    pas rattachées ; leur refus ne l'emporte plus sur les dégâts des eaux, possibles."""
    contrat_b = Contrat(prolog.fichier_regles("assureur-b-habitation-2017"))
    faits = {"evenement": ["degat_eaux"], "cause_eau": "fuite_installation"}
    d = Moteur(contrat_b, faits).decider()
    assert d["decision"] == "INCERTAIN"
    linge = next(r for r in d["garanties"] if r["id"] == "linge")
    assert linge["rattachement"] == "hors"
    if prolog.swipl() is not None:
        assert prolog.decider("assureur-b-habitation-2017", faits)["decision"] == "INCERTAIN"


def test_obligation_engagee_sans_lien_causal_se_demande():
    """7.106 : vol dans la voiture garée (B, `f-b18`). L'obligation « dans un véhicule, fermé à clé et rien en vue »
    fait refuser sans lien causal ; le lieu est établi, l'exigence inconnue : on la demande, au lieu de couvrir sous
    réserve. Une obligation à lien causal (A, fenêtres fermées pendant l'absence, le voleur passé par la porte) reste
    une réserve."""
    contrat_b = Contrat(prolog.fichier_regles("assureur-b-habitation-2017"))
    faits = {"evenement": ["vol"], "bien": ["appareil_informatique"], "lieu": ["vehicule"], "effraction": "oui",
             "plainte_deposee": "oui"}
    # 7.181 : le matériel multimédia est une option. Tant qu'on ne sait pas si elle est souscrite, c'est elle qu'on
    # demande d'abord (inutile de demander si la voiture était fermée pour une garantie qui n'est pas au contrat).
    d = Moteur(contrat_b, faits).decider()
    assert d["decision"] == "INCERTAIN"
    vol = next(r for r in d["garanties"] if r["id"] == "materiel_multimedia_vol")
    assert vol["questions"] == ["option_materiel_multimedia"]
    d = Moteur(contrat_b, faits | {"option_materiel_multimedia": "oui"}).decider()
    assert d["decision"] == "INCERTAIN"
    vol = next(r for r in d["garanties"] if r["id"] == "materiel_multimedia_vol")
    assert "vehicule_ferme_cle" in vol["questions"]
    contrat_a = Contrat(prolog.fichier_regles("assureur-a-habitation-2025"))
    porte = {"evenement": ["vol"], "bien": ["mobilier"], "lieu": ["logement"], "absence": "oui", "portes_fermees": "oui",
             "effraction": "non", "plainte_deposee": "oui"}
    vol_a = next(r for r in Moteur(contrat_a, porte).decider()["garanties"] if r["id"] == "vol_batiment")
    assert vol_a["decision"] != "INCERTAIN" or "fenetres_fermees" not in vol_a["questions"]
    if prolog.swipl() is not None:
        assert prolog.decider("assureur-b-habitation-2017", faits)["decision"] == "INCERTAIN"


def test_demenagement_non_signale_se_demande():
    """7.106 : A, art. 9 (`f-a17`). Emménagé depuis plus de 30 jours, sans dire si l'assureur a été prévenu :
    l'incendie n'est plus couvert d'office, on demande ; sans déménagement dit, il reste couvert."""
    contrat_a = Contrat(prolog.fichier_regles("assureur-a-habitation-2025"))
    faits = {"evenement": ["incendie"], "bien": ["mobilier"], "lieu": ["logement"], "flammes": "oui", "embrasement": "oui"}
    assert Moteur(contrat_a, faits).decider()["decision"] == "COUVERT"
    d = Moteur(contrat_a, faits | {"emmenagement": "plus_30_jours"}).decider()
    assert d["decision"] == "INCERTAIN"
    assert "demenagement_signale" in d["retenues"][0]["questions"]
    if prolog.swipl() is not None:
        assert prolog.decider("assureur-a-habitation-2025", faits | {"emmenagement": "plus_30_jours"})["decision"] == "INCERTAIN"


def test_une_option_seule_a_couvrir_donne_a_preciser():
    """7.109 : le ruissellement chez B (`f-b15`) n'est couvert que par l'option « pluies et inondations », dont on ne
    sait pas si elle est souscrite : « à préciser », avec le point des conditions particulières, et non plus « couvert
    sous réserve ». Une garantie de base qui couvre l'emporte : l'incendie reste couvert."""
    contrat_b = Contrat(prolog.fichier_regles("assureur-b-habitation-2017"))
    faits = {"evenement": ["catastrophe_naturelle"], "bien": ["element_batiment"], "lieu": ["logement"],
             "catastrophe": "ruissellement", "dommages_dans_72h": "oui"}
    d = Moteur(contrat_b, faits).decider()
    assert d["decision"] == "INCERTAIN"
    pluies = next(r for r in d["garanties"] if r["id"] == "pluies_inondations")
    assert pluies["questions"] == ["option_pluies_inondations"]
    if prolog.swipl() is not None:
        assert prolog.decider("assureur-b-habitation-2017", faits)["decision"] == "INCERTAIN"


def test_le_multimedia_de_b_est_une_option_qui_se_demande():
    """7.181. Le « matériel multimédia » de B (3.1.7) est une option, mais elle n'était déclarée nulle part : écrite
    en exclusion « option non souscrite », elle couvrait un ordinateur cassé sans demander si elle était souscrite.
    Écrite comme les autres, elle se demande ; souscrite elle couvre, non souscrite elle refuse."""
    cid = "assureur-b-habitation-2017"
    contrat_b = Contrat(prolog.fichier_regles(cid))
    faits = {"evenement": ["bris"], "bien": ["appareil_informatique"], "lieu": ["logement"]}
    attendus = [(faits, "INCERTAIN"), (faits | {"option_materiel_multimedia": "oui"}, "COUVERT"),
                (faits | {"option_materiel_multimedia": "non"}, "NON_COUVERT")]
    for f, attendu in attendus:
        d = Moteur(contrat_b, f).decider()
        assert d["decision"] == attendu, f
        if prolog.swipl() is not None:
            assert prolog.decider(cid, f)["decision"] == attendu, f
    bris = next(r for r in Moteur(contrat_b, faits).decider()["garanties"] if r["id"] == "materiel_multimedia_bris")
    assert bris["questions"] == ["option_materiel_multimedia"]


def test_une_option_qui_ouvre_une_garantie_ne_se_declare_plus_en_tete():
    """7.181. Chez A et B, plus aucune option n'est déclarée en tête du fichier de règles : chacune est une
    circonstance de son article. Chez D, les quatre déclarations restent : ces options-là lèvent une exclusion pour
    un bien (la véranda, la piscine), elles n'ouvrent pas une garantie."""
    for cid in ("assureur-a-habitation-2025", "assureur-b-habitation-2017"):
        assert Contrat(prolog.fichier_regles(cid)).regles("option", 1) == [], cid
    assert len(Contrat(prolog.fichier_regles("assureur-d-habitation-2026")).regles("option", 1)) == 4


def test_l_evenement_est_precise_avant_les_questions_du_temps_2():
    """7.113 : « accident » sur un miroir est un bris (7.86). Précisé après la lecture, il l'était trop tard : le
    temps 2 posait les questions de l'« accident » et ne demandait jamais si le miroir était posé (`red-b05`)."""
    class Modele:
        nom, accepte_schema = "schema", True

        def __init__(self):
            self.appels = []

        def completer(self, systeme, message, schema=None):
            self.appels.append(message)
            if len(self.appels) == 1:
                return json.dumps({"faits": {"evenement": ["accident"], "bien": ["miroir"], "lieu": ["logement"]}})
            return json.dumps({"faits": {"vitre_placee": "non"}})

    m = Modele()
    faits, notes = lecture.extraire_faits_regles("Le miroir, pas encore accroché, s'est brisé en tombant.", m,
                                                 verifier=False)
    assert "vitre_placee" in m.appels[1]
    assert faits["evenement"] == ["bris"] and faits["vitre_placee"] == "non"


def test_un_velo_n_est_pas_un_vehicule_a_moteur():
    """7.113 : le vélo avait sa place dans l'aide de « personne », et Small lisait quand même « véhicule à moteur »
    (`f-a18`). Il a sa valeur, `velo_trottinette`, qui précise « personne » : les règles qui visent « personne »
    s'y appliquent sans changer."""
    contrat_a = Contrat(prolog.fichier_regles("assureur-a-habitation-2025"))
    faits = {"evenement": ["responsabilite"], "auteur": "assure", "victime": "tiers", "origine_rc": "velo_trottinette"}
    assert Moteur(contrat_a, faits).decider()["decision"] == "COUVERT"
    if prolog.swipl() is not None:
        assert prolog.decider("assureur-a-habitation-2025", faits)["decision"] == "COUVERT"


def test_on_ne_demande_au_client_que_ce_qui_compte():
    """7.114 : une réserve n'est montrée que pour une réponse couverte, et jamais une réserve qui vaut pour tous
    les sinistres (le déménagement non signalé) ; les questions restent posées, une seule fois chacune."""
    voc = prolog.vocabulaire()
    incertain = {"decision": "INCERTAIN", "retenues": [{"questions": ["vitre_placee"],
                                                        "reserves": ["emmenagement", "travaux_vitres"]}]}
    assert chaine.points_a_preciser(incertain, voc) == [("vitre_placee", "question")]
    couvert = {"decision": "COUVERT", "retenues": [{"questions": [], "reserves": ["emmenagement", "travaux_vitres"]}]}
    assert chaine.points_a_preciser(couvert, voc) == [("travaux_vitres", "reserve")]
    refus = {"decision": "NON_COUVERT", "retenues": [{"questions": []}], "possibles": [{"questions": ["fermeture"]}]}
    assert chaine.points_a_preciser(refus, voc) == [("fermeture", "question")]
    # 7.124 : une réserve hors sujet pour l'événement lu n'est pas posée (l'eau pour un piéton renversé à vélo).
    rc = {"decision": "COUVERT", "retenues": [{"questions": [], "reserves": ["cause_eau", "manque_entretien", "travaux_vitres"]}]}
    assert chaine.points_a_preciser(rc, voc, {"evenement": ["responsabilite"]}) == []
    assert ("cause_eau", "reserve") in chaine.points_a_preciser(rc, voc, {"evenement": ["degat_eaux"]})
    assert ("cause_eau", "reserve") in chaine.points_a_preciser(rc, voc), "sans événement connu, la réserve reste"
    # 7.125 : la cause de l'eau déjà dite ne se redemande pas ; un « accident » compte comme un heurt.
    assert ("cause_eau", "reserve") not in chaine.points_a_preciser(rc, voc, {"evenement": ["degat_eaux"], "cause_eau": "gel"})
    # 7.128 : même connue en gros (« une fuite », qui pourrait être le gel), la réserve ne se redemande pas ; une
    # question sur un fait vague ne propose que ses précisions ; « couvert » n'annonce pas de question qui tranche.
    assert ("cause_eau", "reserve") not in chaine.points_a_preciser(
        rc, voc, {"evenement": ["degat_eaux"], "cause_eau": "fuite_installation"})
    from couverture.api import service
    assert service.valeurs_proposees("cause_eau", voc, {"cause_eau": "fuite_installation"}) == ["gel"]
    assert "gel" in service.valeurs_proposees("cause_eau", voc, {}) and "fuite_installation" in service.valeurs_proposees("cause_eau", voc, {})
    _, m = chaine.questions_explorees({"questions": [], "ensemble": ["travaux_vitres"]}, ["travaux_vitres"], "Couvert. « Bris ».")
    assert "tranche" not in m
    assert prolog.evenements_etendus(["accident"]) == {"accident", "heurt", "bris"}
    heurt = next(v for v, d in voc.items() if d.get("pour") and "heurt" in d["pour"] and "accident" not in d["pour"])
    assert heurt in prolog.filtrer_faits({"evenement": ["accident"], heurt: voc[heurt]["valeurs"][0]})[0]
    _, motif = chaine.questions_explorees({"questions": [], "ensemble": ["manque_entretien"]}, [], "Couvert.")
    assert motif == "Couvert."


def test_l_exploration_ne_reintroduit_pas_une_reserve_ecartee():
    """7.115 : sur une réponse couverte, l'exploration du moteur classait aussi le déménagement (une réserve qui vaut
    pour tous les sinistres), que `points_a_preciser` avait écarté : il revenait par là dans les questions."""
    exploration = {"questions": [
        {"variable": "emmenagement", "effet": "décisive", "issues": [{"valeurs": ["plus_30_jours"], "decision": "INCERTAIN"}]},
        {"variable": "travaux_vitres", "effet": "possible", "issues": []}]}
    lignes, _ = chaine.questions_explorees(exploration, ["travaux_vitres"], "")
    assert lignes == [lecture.question("travaux_vitres")]


def test_libelles_du_vocabulaire():
    """Chaque variable a un nom à montrer, et aucun libellé de valeur ne vise une valeur qui n'existe pas (7.137)."""
    voc = prolog.vocabulaire()
    assert [v for v, d in voc.items() if not d.get("libelle")] == []
    assert [(v, x) for v, d in voc.items() for x in d.get("libelles", {}) if x not in d["valeurs"]] == []
    assert prolog.libelle("evenement", voc) == "Événement"
    assert prolog.libelle("lieu", voc, "voie_publique") == "voie publique"
    assert prolog.libelle("inconnue", voc) == "inconnue" and prolog.libelle("lieu", voc, "ailleurs_encore") == "ailleurs encore"


def test_faits_affiches_socle_en_tete():
    lignes = prolog.faits_affiches({"victime": "tiers", "lieu": ["voie_publique"], "evenement": ["responsabilite"],
                                    "origine_rc": "velo_trottinette"})
    assert [(x["libelle"], x["valeur"]) for x in lignes] == [
        ("Événement", "responsabilité civile"), ("Lieu", "voie publique"),
        ("À l'origine du dommage", "vélo ou trottinette"), ("Victime", "tiers")]


def test_variable_sans_evenements_seulement_si_une_regle_vaut_pour_tout():
    """Une variable sans « pour » est lue pour chaque sinistre : ce n'est permis que si une règle qui vise toutes
    les garanties (`tous`) l'emploie. « absence », employée pour le seul vol, était lue pour un accident de vélo
    et s'affichait dans les faits (7.138)."""
    import re
    generales = set()
    for contrat in prolog.contrats_regles():
        texte = prolog.fichier_regles(contrat).read_text(encoding="utf-8")
        for regle in re.findall(r"^[a-z_]+\(tous,.*?\)\.\s*$", texte, flags=re.M | re.S):
            generales |= set(re.findall(r"\bf\(\s*([a-z][a-z0-9_]*)\s*,", regle))
    sans = [v for v, d in prolog.vocabulaire().items() if v not in lecture.SOCLE and not d.get("pour")]
    assert [v for v in sans if v not in generales] == []


# --- Les conditions particulières données avec la déclaration (7.141) --------------------------------------------

def test_souscription_d_un_contrat():
    """Ce que les conditions particulières précisent se lit dans le vocabulaire (« source ») et dans les règles
    du contrat : ses options à lui, et ses formules à lui."""
    voc = prolog.vocabulaire()
    a, b, d = (prolog.souscription(c, voc) for c in ("assureur-a-habitation-2025", "assureur-b-habitation-2017",
                                                      "assureur-d-habitation-2026"))
    assert set(a) == {"couverture_rc_locative", "option_materiel_multimedia"}
    assert b["formule"]["valeurs"] == ["privilege", "active", "standard"]
    assert d["formule"]["valeurs"] == ["eco", "confort", "excellence"] and "pack_jardin" in d and "pack_jardin" not in b
    # Aucune formule déclarée pour un contrat qui n'existe pas, et rien sans règles.
    assert all(set(x) <= set(prolog.contrats_regles()) for v in voc.values() for x in [v.get("par_contrat") or {}])
    assert prolog.souscription("contrat-sans-regles", voc) == {}


def test_souscription_retenue_ou_signalee():
    b = "assureur-b-habitation-2017"
    faits, ecarts = prolog.retenir_souscription(b, {"formule": "eco", "option_vol": "oui", "pack_jardin": "oui",
                                                    "option_tempete": ""})
    assert faits == {"option_vol": "oui"} and len(ecarts) == 2, "la formule d'un autre contrat et le pack de D"
    assert prolog.retenir_souscription(b, None) == ({}, [])


def test_la_declaration_peut_encore_dire_la_formule():
    """« J'ai la formule Privilège » : la déclaration le dit parfois (golden b-v05), la lecture le cherche toujours.
    La souscription donnée s'ajoute à la lecture, elle ne la remplace pas."""
    voc = prolog.vocabulaire()
    assert "formule" in lecture.variables_du_temps_2(voc, ["vol"])


def test_souscription_donnee_tranche_sans_confirmation(contrat):
    """Un ordinateur cassé chez A : sans l'option, « à préciser » ; avec l'option donnée par les conditions
    particulières, « couvert », et ce fait n'est pas soumis à la confirmation sur la déclaration (il n'en vient pas)."""
    def oracle(f):
        d = Explorateur(contrat, f).decider()
        for r in d["retenues"] + d.get("possibles", []) + d.get("accessoires", []):
            g = next(x for x in contrat.regles("garantie", 4) if x.args[0] == r["id"])
            r.update(garantie=g.args[1], article=g.args[2], motif="…", preuves=[])
        return d

    class Modele:
        nom, accepte_schema = "souscription", True

        def __init__(self):
            self.juges = set()

        def completer(self, systeme, message, schema=None):
            if systeme == lecture.SYSTEME_LECTURE_SOCLE:
                return json.dumps({"faits": {"evenement": ["accident"], "bien": ["appareil_informatique"],
                                             "lieu": ["logement"]}})
            if systeme == lecture.SYSTEME_LECTURE_DETAILS:
                return json.dumps({"faits": {}})
            props = set(schema["properties"]["verdicts"]["properties"])
            self.juges |= props
            return json.dumps({"verdicts": {v: "dit" for v in props}})

    sinistre = "J'ai fait tomber mon ordinateur portable dans le salon, l'écran est cassé."
    sans = chaine.PipelineRegles(CONTRAT, [], Modele(), decideur=oracle).analyser(sinistre)
    assert sans.verdict.decision.value == "INCERTAIN"
    m = Modele()
    avec = chaine.PipelineRegles(CONTRAT, [], m, decideur=oracle).analyser(
        sinistre, souscription={"option_materiel_multimedia": "oui", "pack_jardin": "oui"})
    # Sans clauses en base, la validation rétrograde un « couvert » sans citation : on lit la décision du moteur.
    assert (avec.verdict.decision_initiale or avec.verdict.decision).value == "COUVERT"
    assert "option_materiel_multimedia" not in m.juges
    assert "option_materiel_multimedia=oui" in avec.faits.circonstances
    assert any("pack_jardin" in a for a in avec.verdict.avertissements), "l'option d'un autre contrat est signalée"
    refus = chaine.PipelineRegles(CONTRAT, [], Modele(), decideur=oracle).analyser(
        sinistre, souscription={"option_materiel_multimedia": "non"})
    assert (refus.verdict.decision_initiale or refus.verdict.decision).value == "NON_COUVERT"


def test_sans_evenement_le_moteur_n_est_pas_interroge():
    """Un texte qui n'est pas une déclaration : « je n'ai pas reconnu de sinistre », la question « que s'est-il
    passé ? », aucune garantie citée ; et le moteur n'est pas appelé (7.142)."""
    class Modele:
        nom, accepte_schema = "rien", True

        def completer(self, systeme, message, schema=None):
            return json.dumps({"faits": {}}) if "verdicts" not in str(schema) else json.dumps({"verdicts": {}})

    def moteur(faits):
        raise AssertionError("le moteur ne doit pas être interrogé sans événement")

    etapes = []
    r = chaine.PipelineRegles(CONTRAT, [], Modele(), decideur=moteur).analyser(
        "Bonjour, pouvez-vous me rappeler demain matin ?", suivi=lambda e, d=None: etapes.append((e, d)),
        souscription={"option_materiel_multimedia": "oui"})
    assert r.verdict.decision.value == "INCERTAIN" and r.verdict.justification == chaine.SANS_EVENEMENT
    assert r.verdict.informations_manquantes == [lecture.question("evenement")] and not r.verdict.citations
    assert r.faits.circonstances == ["option_materiel_multimedia=oui"], "ce qui est donné reste dans les faits"
    assert ("decision", "aucun sinistre reconnu : les règles ne sont pas appliquées") in etapes


def test_la_lecture_ne_propose_que_les_formules_du_contrat():
    """7.154 : la lecture d'une déclaration faite pour B ne peut pas répondre une formule de D. Le vocabulaire vu
    par un contrat ne garde, pour une variable « par_contrat », que ses noms, leur aide et leurs libellés."""
    b, d = "assureur-b-habitation-2017", "assureur-d-habitation-2026"
    voc = prolog.vocabulaire()
    vu_b, vu_d = prolog.vocabulaire_du_contrat(b), prolog.vocabulaire_du_contrat(d)
    assert vu_b["formule"]["valeurs"] == voc["formule"]["par_contrat"][b] and "excellence" not in vu_b["formule"]["valeurs"]
    assert set(vu_d["formule"].get("aide") or {}) <= set(vu_d["formule"]["valeurs"])
    assert vu_b["effraction"] == voc["effraction"] and voc["formule"]["valeurs"] != vu_b["formule"]["valeurs"], \
        "le vocabulaire commun n'est pas modifié"
    assert prolog.vocabulaire_du_contrat("assureur-a-habitation-2025")["formule"]["valeurs"] == voc["formule"]["valeurs"]

    class Modele:
        nom, appels = "faux", []

        def completer(self, systeme, message, schema=None):
            self.appels.append(schema)
            return json.dumps({"faits": {"evenement": ["vol"]} if len(self.appels) == 1 else {"formule": "excellence"}})

    m = Modele()
    faits, ecarts = lecture.extraire_faits_regles("Vol chez moi, j'ai la formule Excellence.", m, verifier=False,
                                                  variables=lecture.variables_du_contrat(b), voc=vu_b)
    assert "excellence" not in lecture.schema_faits({"formule": vu_b["formule"]})["properties"]["faits"]["properties"]["formule"]["enum"]
    assert "formule" not in faits and any("excellence" in e for e in ecarts), "une formule d'un autre contrat n'est pas retenue"


def test_deux_biens_exclus_declares_ensemble_ne_sont_pas_couverts():
    """7.156 : les vitraux et les marquises de C avaient été mis dans le périmètre du bris de glaces pour que leur
    exclusion soit citée ; déclarés ensemble, chacun n'étant exclu que pour lui-même, ils donnaient « couvert »."""
    from moteur_reference import Contrat, Explorateur
    f = prolog.fichier_regles("assureur-c-habitation-2025")
    if not f.exists() or "bris_glaces_batiment" not in f.read_text(encoding="utf-8"):
        pytest.skip("le bris de glaces du contrat C n'est pas traduit")
    c = Contrat(f)
    for biens in (["vitrail"], ["vitrail", "marquise"], ["marquise", "serre"]):
        d = Explorateur(c, {"evenement": ["bris"], "bien": biens, "formule": "confort"}).decider()
        assert d["decision"] != "COUVERT", biens
    assert Explorateur(c, {"evenement": ["bris"], "bien": ["vitre"], "formule": "confort"}).decider()["decision"] == "COUVERT"


HORS_PERIMETRE = [("assureur-a-habitation-2025", {"evenement": ["bris"], "bien": ["objet_verre_non_vitre"], "lieu": ["logement"]}, "objets en verre"),
                  ("assureur-a-habitation-2025", {"evenement": ["bris"], "bien": ["serre"], "lieu": ["jardin"]}, "serres"),
                  ("assureur-c-habitation-2025", {"evenement": ["bris"], "bien": ["vitrail"], "formule": "confort"}, "vitraux"),
                  ("assureur-c-habitation-2025", {"evenement": ["bris"], "bien": ["vitrail", "marquise"], "formule": "confort"}, "vitraux")]


def test_aucune_garantie_mais_une_exclusion_ecrite_est_citee():
    """7.157 : un vase brisé n'entre dans aucune garantie, et le contrat exclut « les objets en verre » : la décision
    reste « non couvert », et c'est cette clause qu'on cite, pas le texte de garanties sans rapport."""
    from moteur_reference import Contrat, Explorateur
    for cid, faits, mot in HORS_PERIMETRE:
        f = prolog.fichier_regles(cid)
        if not f.exists() or "garantie(" not in f.read_text(encoding="utf-8"):
            continue
        regles = Contrat(f)
        d = Explorateur(regles, faits).decider()
        assert d["decision"] == "NON_COUVERT" and d.get("aucune") is True, (cid, faits)
        assert any(mot in x["texte"] for x in d["exclusions_etablies"]), (cid, faits)
        for r in d["retenues"]:      # la référence ne rend pas les libellés des garanties : comme le fait moteur.pl
            g = next(x for x in regles.regles("garantie", 4) if x.args[0] == r["id"])
            r.update(garantie=g.args[1], article=g.args[2], motif="hors de son périmètre", preuves=[])
        v, _ = chaine.PipelineRegles(cid, [], FauxLLM({}), decideur=lambda _: d).verdict(d, faits)
        assert v.decision == Decision.NON_COUVERT and "exclut expressément" in v.justification
        assert v.citations and all(c.role == "exclusion" for c in v.citations) and any(mot in c.extrait for c in v.citations)
    # Une garantie s'applique : rien n'est ajouté, la décision et ses citations sont celles d'avant.
    a = Contrat(prolog.fichier_regles("assureur-a-habitation-2025"))
    assert Explorateur(a, {"evenement": ["bris"], "bien": ["vitre"], "lieu": ["logement"]}).decider()["exclusions_etablies"] == []
    assert Explorateur(a, {"evenement": ["vol"], "bien": ["velo"], "lieu": ["parties_communes"]}).decider()["exclusions_etablies"] == []


@avec_swipl
def test_exclusions_etablies_prolog_et_reference_concordent():
    from moteur_reference import Contrat, Explorateur
    for cid, faits, _ in HORS_PERIMETRE:
        if not prolog.a_des_garanties(cid):
            continue
        p, o = prolog.decider(cid, faits), Explorateur(Contrat(prolog.fichier_regles(cid)), faits).decider()
        assert p["decision"] == o["decision"] == "NON_COUVERT" and p["exclusions_etablies"] == o["exclusions_etablies"] != []


def test_tous_les_biens_declares_exclus_il_ne_reste_rien_a_couvrir(tmp_path):
    """7.159 : l'exclusion d'un bien ne retire que ce bien quand d'autres sont déclarés ; si chacun est exclu, la
    garantie ne couvre plus rien. Avant, des espèces et un animal volés ensemble étaient « couverts »."""
    from moteur_reference import Contrat, Explorateur
    regles = tmp_path / "essai.pl"
    regles.write_text('''evenement_traduit(vol).
garantie(vol, "Vol", '1', "le vol des biens assurés").
perimetre(vol, f(evenement, vol)).
exclusion(vol, f(bien, valeurs), bien(valeurs), non, '2', "les fonds et valeurs").
exclusion(vol, f(bien, animal), bien(animal), non, '2', "les animaux").
''', encoding="utf-8")
    c = Contrat(regles)
    decide = lambda biens: Explorateur(c, {"evenement": ["vol"], "bien": biens}).decider()
    assert decide(["valeurs"])["decision"] == "NON_COUVERT"
    assert decide(["valeurs", "animal"])["decision"] == "NON_COUVERT", "deux biens exclus ne font pas un bien couvert"
    mixte = decide(["valeurs", "electronique"])
    assert mixte["decision"] == "COUVERT" and mixte["retenues"][0]["partielles"] == ["valeurs"], "le reste demeure couvert"
    assert decide(["electronique"])["decision"] == "COUVERT"


@avec_swipl
def test_biens_tous_exclus_prolog_et_reference_concordent():
    from moteur_reference import Contrat, Explorateur
    cid = "assureur-c-habitation-2025"
    if not prolog.a_des_garanties(cid) or "'S2-b'" not in prolog.fichier_regles(cid).read_text(encoding="utf-8"):
        pytest.skip("les biens non assurés du contrat C ne sont pas traduits")
    base = {"evenement": ["vol"], "lieu": ["logement"], "effraction": "oui", "formule": "confort"}
    for biens, attendu in ((["valeurs"], "NON_COUVERT"), (["valeurs", "animal"], "NON_COUVERT"),
                           (["valeurs", "electronique"], "COUVERT"), (["electronique"], "COUVERT")):
        faits = base | {"bien": biens}
        p, o = prolog.decider(cid, faits), Explorateur(Contrat(prolog.fichier_regles(cid)), faits).decider()
        assert p["decision"] == o["decision"] == attendu, biens


CAS_B_SOIR = [
    # Bagages (4.2.2), protection numérique (4.1.4), annulation (4.2.1), assistance voyage (4.2.3) : écrits le
    # 24 nov. au soir, sans cas dans le jeu fermé de B. Ces essais ne mesurent rien : ils fixent ce que les règles
    # répondent sur des faits exacts, et que le moteur Prolog et le moteur de référence concordent (7.176).
    ("valise volée en voyage, option, plainte",
     {"evenement": ["vol"], "bien": ["objet_divers"], "lieu": ["voie_publique"], "en_voyage": "oui",
      "option_bagages": "oui", "plainte_deposee": "oui"}, "COUVERT"),
    ("valise volée en voyage, option inconnue",
     {"evenement": ["vol"], "bien": ["objet_divers"], "lieu": ["voie_publique"], "en_voyage": "oui",
      "plainte_deposee": "oui"}, "INCERTAIN"),
    ("valise oubliée",
     {"evenement": ["vol"], "bien": ["objet_divers"], "lieu": ["voie_publique"], "en_voyage": "oui",
      "option_bagages": "oui", "plainte_deposee": "oui", "bagage_oublie": "oui"}, "NON_COUVERT"),
    ("valise perdue, option",
     {"evenement": ["voyage"], "objet_voyage": "perte_bagage", "option_bagages": "oui"}, "COUVERT"),
    ("usurpation d'identité, option",
     {"evenement": ["litige"], "litige_internet": "usurpation_identite", "domaine_litige": "autre",
      "option_e_protection": "oui"}, "COUVERT"),
    ("carte utilisée, code communiqué",
     {"evenement": ["litige"], "litige_internet": "fraude_paiement", "domaine_litige": "autre",
      "option_e_protection": "oui", "code_secret_divulgue": "oui"}, "NON_COUVERT"),
    ("litige avec l'employeur",
     {"evenement": ["litige"], "domaine_litige": "travail"}, "NON_COUVERT"),
    ("achat en ligne, vendeur inconnu",
     {"evenement": ["litige"], "litige_internet": "achat_bien_internet", "domaine_litige": "consommation",
      "option_e_protection": "oui", "bien": ["electronique"]}, "INCERTAIN"),
    ("voyage annulé, proche hospitalisé, option",
     {"evenement": ["voyage"], "objet_voyage": "annulation", "motif_annulation": "sante_ou_deces_proche",
      "option_annulation": "oui"}, "COUVERT"),
    ("voyage annulé, changement d'avis",
     {"evenement": ["voyage"], "objet_voyage": "annulation", "motif_annulation": "autre",
      "option_annulation": "oui"}, "NON_COUVERT"),
    ("voyage annulé pour une épidémie",
     {"evenement": ["voyage"], "objet_voyage": "annulation", "motif_annulation": "sante_ou_deces_proche",
      "option_annulation": "oui", "cause_annulation_exclue": "epidemie_pollution_catastrophe"}, "NON_COUVERT"),
    ("rapatriement, assistance appelée",
     {"evenement": ["voyage"], "objet_voyage": "incident_medical", "option_assistance_voyage": "oui",
      "assistance_voyage_appelee": "oui"}, "COUVERT"),
    ("rapatriement, appel non dit",
     {"evenement": ["voyage"], "objet_voyage": "incident_medical", "option_assistance_voyage": "oui"}, "INCERTAIN"),
    ("rapatriement organisé seul",
     {"evenement": ["voyage"], "objet_voyage": "incident_medical", "option_assistance_voyage": "oui",
      "assistance_voyage_appelee": "non"}, "NON_COUVERT"),
    ("médecin payé à l'étranger, sans hospitalisation",
     {"evenement": ["voyage"], "objet_voyage": "soins_sans_hospitalisation", "option_assistance_voyage": "oui",
      "assistance_voyage_appelee": "non", "sinistre_a_l_etranger": "oui"}, "COUVERT"),
    ("médecin payé au Luxembourg",
     {"evenement": ["voyage"], "objet_voyage": "soins_sans_hospitalisation", "option_assistance_voyage": "oui",
      "sinistre_a_l_etranger": "non"}, "NON_COUVERT"),
]


def _b_soir_traduit() -> bool:
    cid = "assureur-b-habitation-2017"
    if not prolog.a_des_garanties(cid):
        return False
    texte = prolog.fichier_regles(cid).read_text(encoding="utf-8")
    return all(g in texte for g in ("bagages_perte", "e_protection", "annulation_voyage", "assistance_voyage",
                                    "sinistre_a_l_etranger"))


@pytest.mark.parametrize("nom,faits,attendu", CAS_B_SOIR, ids=[c[0] for c in CAS_B_SOIR])
def test_b_voyage_et_numerique_sur_faits_exacts(nom, faits, attendu):
    from moteur_reference import Contrat, Moteur
    if not _b_soir_traduit():
        pytest.skip("les articles 4.1.4 et 4.2.1 à 4.2.3 de B ne sont pas tous acceptés")
    cid = "assureur-b-habitation-2017"
    assert Moteur(Contrat(prolog.fichier_regles(cid)), faits).decider()["decision"] == attendu, nom
    if prolog.swipl() is not None:
        assert prolog.decider(cid, faits)["decision"] == attendu, nom


def test_contrat_traduit_en_entier_un_evenement_sans_garantie_est_un_refus(monkeypatch):
    """7.177. Un voyage annulé déclaré chez A recevait « relève d'une garantie qui n'est pas encore traduite » : A est
    traduit en entier et n'a pas de garantie de voyage. Seul sujet de la déclaration, l'événement est refusé ; avec
    autre chose, le dossier reste à examiner et la phrase dit ce qui manque."""
    monkeypatch.setattr(prolog, "traduction_complete", lambda contrat_id: True)
    garantie = {"id": "degats_eaux", "garantie": "Dégâts causés par l’eau", "article": "2.7", "rattachement": "rattachée",
                "decision": "COUVERT", "motif": "périmètre et conditions établis", "preuves": [], "questions": [],
                "reserves": [], "partielles": []}

    def verdict(evenements, retenues):
        reponse = {"decision": "INCERTAIN", "non_traduits": ["voyage"], "aucune": False, "possibles": [],
                   "retenues": retenues}
        p = chaine.PipelineRegles(CONTRAT, [], FauxLLM({"evenement": evenements}), decideur=lambda f: reponse)
        return p.verdict(reponse, {"evenement": evenements})[0]

    seul = verdict(["voyage"], [])
    assert seul.decision == Decision.NON_COUVERT and seul.confiance == 0.85 and not seul.informations_manquantes
    assert seul.justification == "Non couvert : aucune garantie de ce contrat ne porte sur cet événement."
    mixte = verdict(["voyage", "degat_eaux"], [garantie])
    assert mixte.decision == Decision.INCERTAIN and mixte.confiance <= 0.3
    assert "aucune garantie de ce contrat ne porte sur « voyage »" in mixte.justification
    assert "pas encore traduite" not in mixte.justification
    # Jusqu'au bout de la chaîne : la validation des citations ne ramène pas ce refus à « à préciser ». C'est ce
    # qu'elle faisait au premier essai (« Décision : INCERTAIN », sous « Non couvert »), le refus n'ayant rien à citer.
    reponse = {"decision": "INCERTAIN", "non_traduits": ["voyage"], "aucune": False, "possibles": [], "retenues": []}
    p = chaine.PipelineRegles(CONTRAT, [], FauxLLM({"evenement": ["voyage"]}), decideur=lambda f: reponse)
    v = p.analyser("J'ai dû annuler mon voyage.").verdict
    assert v.decision == Decision.NON_COUVERT and not v.informations_manquantes and not v.citations
    monkeypatch.setattr(prolog, "traduction_complete", lambda contrat_id: False)
    v = p.analyser("J'ai dû annuler mon voyage.").verdict
    assert v.decision == Decision.INCERTAIN and "pas encore traduite" in v.justification


def test_contrat_en_partie_traduit_l_evenement_part_chez_un_gestionnaire():
    """Sans déclaration de traduction complète, rien ne change : jamais un refus sur une garantie non traduite."""
    reponse = {"decision": "INCERTAIN", "non_traduits": ["voyage"], "aucune": False, "possibles": [], "retenues": []}
    p = chaine.PipelineRegles(CONTRAT, [], FauxLLM({"evenement": ["voyage"]}), decideur=lambda f: reponse)
    v = p.verdict(reponse, {"evenement": ["voyage"]})[0]
    assert v.decision == Decision.INCERTAIN and "pas encore traduite" in v.justification


def test_traduction_complete_lue_dans_le_fichier(tmp_path, monkeypatch):
    monkeypatch.undo()                                   # le vrai `traduction_complete`, pas celui de conftest
    monkeypatch.setattr(prolog, "DOSSIER", tmp_path)
    assert prolog.traduction_complete("x") is False, "fichier absent : pas complet"
    (tmp_path / "traduction.json").write_text(json.dumps({"x": {"complet": True}, "y": {"complet": "oui"}}), encoding="utf-8")
    assert prolog.traduction_complete("x") is True
    assert prolog.traduction_complete("y") is False and prolog.traduction_complete("z") is False


REGLES_ECARTEE = """
evenement_traduit(vol).
garantie(bagages, "Bagages", '1', "les bagages emportés en voyage").
perimetre(bagages, f(evenement, vol)).
perimetre(bagages, f(en_voyage, oui)).
exclusion(bagages, f(bien, valeurs), tout, non, '1', "les valeurs ne sont pas des bagages").
garantie(agression, "Vol par agression", '2', "le vol par agression").
perimetre(agression, f(evenement, vol)).
perimetre(agression, f(violence, oui)).
exclusion(agression, f(auteur, famille), tout, non, '2', "les vols commis par un proche").
"""


def test_une_garantie_ecartee_ne_l_emporte_pas_sur_une_garantie_possible(tmp_path):
    """7.179. De l'argent volé, sans qu'on sache si c'était en voyage ni avec violence. L'exclusion des bagages est
    établie, mais rien ne rattache le vol aux bagages : la garantie est écartée, elle ne refuse pas à la place du
    vol par agression, encore possible. Le moteur refusait ; chaque exclusion des bagages portait, à la main, « et
    en voyage » pour l'éviter (leçon 174)."""
    f = tmp_path / "contrat.pl"
    f.write_text(REGLES_ECARTEE, encoding="utf-8")
    contrat = Contrat(f)
    vol = {"evenement": ["vol"], "bien": ["valeurs"]}
    d = Moteur(contrat, vol).decider()
    assert d["decision"] == "INCERTAIN" and [r["id"] for r in d["retenues"]] == ["agression"]
    assert d["retenues"][0]["questions"] == ["violence"]
    assert Moteur(contrat, vol | {"auteur": "famille"}).decider()["decision"] == "NON_COUVERT", \
        "toutes les garanties écartées, aucune possible : refus"
    assert Moteur(contrat, vol | {"violence": "non"}).decider()["decision"] == "NON_COUVERT", \
        "l'autre garantie hors de son périmètre : refus"
    assert Moteur(contrat, vol | {"en_voyage": "oui"}).decider()["decision"] == "NON_COUVERT", \
        "rattaché aux bagages, le vol est refusé par leur exclusion : la règle d'avant, inchangée"
    assert Moteur(contrat, vol | {"violence": "oui"}).decider()["decision"] == "COUVERT"


@avec_swipl
def test_garantie_ecartee_prolog_et_reference_concordent():
    """La même règle dans les deux moteurs, sur un contrat réel : l'option « tremblement de terre » non souscrite
    écarte cette garantie, sans refuser une catastrophe naturelle que « pluies et inondations » peut couvrir."""
    cid = "assureur-b-habitation-2017"
    if "pluies_inondations" not in prolog.fichier_regles(cid).read_text(encoding="utf-8"):
        pytest.skip("la section 3.2 de B n'est pas traduite")
    base = {"evenement": ["catastrophe_naturelle"], "bien": ["mobilier"], "lieu": ["logement"],
            "option_tremblement_terre": "non"}
    for faits, attendu in ((base, "INCERTAIN"), (base | {"option_pluies_inondations": "non"}, "NON_COUVERT"),
                           (base | {"catastrophe": "tremblement_terre"}, "NON_COUVERT")):
        p, o = prolog.decider(cid, faits), Moteur(Contrat(prolog.fichier_regles(cid)), faits).decider()
        assert p["decision"] == o["decision"] == attendu, faits
