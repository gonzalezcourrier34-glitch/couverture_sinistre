import json
from pathlib import Path

import pytest

from couverture.base import Base
from couverture.chargement import charger_lignes
from couverture.controles import controler
from couverture.evaluation import charger_cas, evaluer
from couverture.faits import enrichir_requete, extraire_faits
from couverture.ingestion import ingerer_dossier, ingerer_fichier
from couverture.juges import JugeHeuristique, JugeLLM, extraire_json
from couverture.models import Decision, TypeClause
from couverture.pipeline import Pipeline, PipelineDocumentBrut
from couverture.recherche import Recherche
from couverture.segmentation import segmenter_lignes
from couverture.validation import extrait_present

RACINE = Path(__file__).parent.parent
DONNEES = RACINE / "data"
CG_FICTIF = DONNEES / "contrats" / "fictif_habitat_serein.md"
PDF_REEL = Path(__file__).parent / "fixtures" / "cg_style_reel.pdf"


@pytest.fixture(scope="module")
def clauses():
    return segmenter_lignes(charger_lignes(CG_FICTIF))


@pytest.fixture(scope="module")
def clauses_pdf():
    return segmenter_lignes(charger_lignes(PDF_REEL))


class FauxLLM:
    """Renvoie une réponse préparée et garde le dernier message reçu."""

    nom = "faux"

    def __init__(self, reponse):
        self.reponse = reponse if isinstance(reponse, str) else json.dumps(reponse, ensure_ascii=False)
        self.dernier_message = ""

    def completer(self, systeme, message):
        self.dernier_message = message
        return self.reponse


# --- Lecture et découpage -----------------------------------------------------

def test_segmentation_markdown(clauses):
    par_id = {c.id: c for c in clauses}
    assert len([c for c in clauses if c.id != "preambule"]) == 29
    assert par_id["1.5"].type == TypeClause.DEFINITION
    assert par_id["4.3"].type == TypeClause.GARANTIE
    assert par_id["4.4"].type == TypeClause.EXCLUSION and par_id["4.4"].groupe == "4"
    assert par_id["8.1"].type == TypeClause.EXCLUSION
    assert par_id["9.1"].type == TypeClause.LIMITE
    assert par_id["10.2"].type == TypeClause.CONDITION
    assert "4.1" in par_id["4.3"].renvois and "4.2" in par_id["4.3"].renvois


def test_pdf_nettoyage():
    textes = [l.texte for l in charger_lignes(PDF_REEL)]
    assert not any("SOMMAIRE" in t or "......" in t for t in textes), "le sommaire doit être retiré"
    assert not any("Réf. AT-2026" in t or t.startswith("Page ") for t in textes), "en-têtes et pieds retirés"
    assert any("l'incendie, l'explosion" in t for t in textes), "mot coupé en fin de ligne recollé"


def test_pdf_intertitres_sans_numero(clauses_pdf):
    par_id = {c.id: c for c in clauses_pdf}
    assert par_id["2.2-a"].type == TypeClause.GARANTIE
    assert par_id["2.2-b"].type == TypeClause.EXCLUSION and par_id["2.2-b"].groupe == "2.2"
    assert par_id["2.2-c"].type == TypeClause.CONDITION  # « MESURES DE PRÉVENTION » en capitales
    assert par_id["2.2-a"].renvois == ["4.2"]
    assert par_id["2.2-b"].pages == [4]


def test_pdf_lexique_eclate(clauses_pdf):
    termes = {c.titre for c in clauses_pdf if c.type == TypeClause.DEFINITION}
    assert {"Dépendances", "Effraction", "Incendie", "Mobilier de jardin", "Parties communes"} <= termes


def test_controles(clauses, clauses_pdf):
    assert controler(clauses)["statut"] == "OK"
    rapport = controler(clauses_pdf)
    assert rapport["statut"] == "A_VERIFIER"  # contrat d'essai trop court : alerte attendue
    assert any("Peu de clauses" in a for a in rapport["alertes"])


# --- Base multi-contrats -----------------------------------------------------

def test_ingestion_base(tmp_path):
    base = Base(tmp_path / "b.sqlite")
    dossier = tmp_path / "contrats"
    dossier.mkdir()
    (dossier / "a.md").write_text(CG_FICTIF.read_text(encoding="utf-8"), encoding="utf-8")
    (dossier / "b.pdf").write_bytes(PDF_REEL.read_bytes())
    (dossier / "catalogue.json").write_text(json.dumps({"a.md": {"id": "contrat-a", "assureur": "A"}}), encoding="utf-8")

    contrats = ingerer_dossier(dossier, base)
    assert {c.id for c in contrats} == {"contrat-a", "b"}
    a = base.clauses("contrat-a")
    assert len(a) == 30 and {c.id for c in base.clauses("b")}.isdisjoint({"4.3"})  # jamais de mélange
    assert {x.id: x for x in a}["4.3"].renvois  # renvois relus depuis la base

    # Ré-ingestion d'un fichier inchangé : rien n'est refait.
    avant = base.contrat("contrat-a").ingere_le
    ingerer_fichier(dossier / "a.md", base, {"id": "contrat-a"})
    assert base.contrat("contrat-a").ingere_le == avant


# --- Recherche ---------------------------------------------------------------

@pytest.mark.parametrize(
    "requete, attendues",
    [
        ("vol de vélo dans le local à vélos de l'immeuble", {"4.3", "4.4", "1.6"}),
        ("une bougie a brûlé la table", {"2.1", "2.2", "1.5"}),
        ("fuite du lave-linge", {"3.1", "3.2"}),
    ],
)
def test_recherche_garantie_exclusion_definition(clauses, requete, attendues):
    ids = {r.clause.id for r in Recherche(clauses).rechercher(enrichir_requete(requete, extraire_faits(requete)))}
    assert attendues <= ids


def test_recherche_suit_les_renvois(clauses_pdf):
    q = "vol de mon vélo dans ma cave"
    retenues = Recherche(clauses_pdf).rechercher(enrichir_requete(q, extraire_faits(q)))
    raisons = {r.clause.id: r.raison for r in retenues}
    assert "4.2" in raisons and "2.2-b" in raisons


# --- Contrôle des citations --------------------------------------------------

def test_extrait_tolere_accents_ponctuation_et_coupures():
    texte = "Ne sont pas garantis : les vols commis dans les parties communes de l'immeuble, y compris dans un local à vélos collectif."
    assert extrait_present("les vols commis dans les parties communes … local a velos collectif", texte)
    assert not extrait_present("les vols commis dans la rue", texte)


def test_citation_inventee_retrograde_la_decision(clauses):
    faux = FauxLLM({"decision": "COUVERT", "justification": "…", "confiance": 0.9,
                    "citations": [{"clause_id": "4.3", "extrait": "tous les vélos sont toujours garantis"}]})
    r = Pipeline(clauses, juge=JugeLLM(faux)).analyser("On m'a volé mon vélo dans la rue.")
    assert r.verdict.decision == Decision.INCERTAIN
    assert r.verdict.decision_initiale == Decision.COUVERT
    assert not r.verdict.citations[0].valide and r.verdict.confiance <= 0.5


def test_clause_non_fournie_est_rejetee(clauses):
    faux = FauxLLM({"decision": "NON_COUVERT", "justification": "…", "confiance": 0.8,
                    "citations": [{"clause_id": "99.9", "extrait": "n'importe quoi"}]})
    r = Pipeline(clauses, juge=JugeLLM(faux)).analyser("Ma table est abîmée.")
    assert r.verdict.decision == Decision.INCERTAIN
    assert any("non fournie" in a for a in r.verdict.avertissements)


def test_verdict_valide_passe_avec_pages(clauses):
    faux = FauxLLM({"decision": "NON_COUVERT", "justification": "Local collectif exclu.", "confiance": 0.85,
                    "citations": [{"clause_id": "4.4", "extrait": "les vols commis dans les parties communes de l'immeuble, y compris dans un local à vélos collectif", "role": "garantie"}]})
    r = Pipeline(clauses, juge=JugeLLM(faux)).analyser("Mon vélo a été volé dans le local à vélos commun.")
    c = r.verdict.citations[0]
    assert r.verdict.decision == Decision.NON_COUVERT
    assert c.valide and c.role == "exclusion" and c.pages == [1]  # le rôle vient du contrat
    assert "[4.4]" in faux.dernier_message


def test_json_mal_forme_donne_incertain(clauses):
    r = Pipeline(clauses, juge=JugeLLM(FauxLLM("je pense que oui"))).analyser("vol de vélo")
    assert r.verdict.decision == Decision.INCERTAIN and r.verdict.confiance == 0.0


def test_extraire_json_bloc_markdown():
    assert extraire_json('```json\n{"decision": "COUVERT"}\n```') == {"decision": "COUVERT"}


# --- Méthode de référence « document brut » ---------------------------------

def test_document_brut_relocalise_les_citations(clauses):
    faux = FauxLLM({"decision": "NON_COUVERT", "justification": "…", "confiance": 0.9,
                    "citations": [{"clause_id": "Article 4", "extrait": "y compris dans un local à vélos collectif"}]})
    p = PipelineDocumentBrut(clauses, CG_FICTIF.read_text(encoding="utf-8"), faux, "x")
    r = p.analyser("Vélo volé dans le local commun.")
    assert r.methode == "document-brut"
    assert r.verdict.citations[0].clause_id == "4.4" and r.verdict.citations[0].valide
    assert "Habitat Serein" in faux.dernier_message  # le contrat entier est dans le prompt


# --- Évaluation ----------------------------------------------------------------

def test_jeu_de_test_coherent():
    cas = charger_cas(DONNEES / "sinistres.jsonl", DONNEES / "annotations" / "fictif-habitat-serein.jsonl")
    assert len(cas) == 14
    assert {"velo-01", "bougie-01"} <= {c["id"] for c in cas}  # les deux cas du recruteur


def test_heuristique_ne_dit_jamais_couvert_a_tort(clauses):
    cas = charger_cas(DONNEES / "sinistres.jsonl", DONNEES / "annotations" / "fictif-habitat-serein.jsonl")
    rapport = evaluer(Pipeline(clauses, juge=JugeHeuristique()), cas)
    assert rapport["faux_couverts"] == 0
    assert rapport["citations_rejetees"] == 0


# --- Contrat réel (si le PDF est présent dans data/contrats) -------------------

FOYER = DONNEES / "contrats" / "foyer_appart123_2025.pdf"


@pytest.mark.skipif(not FOYER.exists(), reason="PDF Foyer appart 123 absent de data/contrats")
def test_contrat_foyer_lu_et_exclusion_parties_communes_trouvee():
    clauses = segmenter_lignes(charger_lignes(FOYER))
    rapport = controler(clauses)
    assert rapport["statut"] == "OK", rapport["alertes"]
    par_id = {c.id: c for c in clauses}
    assert "parties communes" in par_id["2.10-a"].texte and par_id["2.10-a"].type == TypeClause.EXCLUSION
    assert len([c for c in clauses if c.type == TypeClause.DEFINITION]) > 40  # lexique éclaté terme par terme

    q = "Je me fais voler mon vélo dans le local commun de l'immeuble, qui n'était pas fermé à clé."
    ids = {r.clause.id for r in Recherche(clauses).rechercher(enrichir_requete(q, extraire_faits(q)))}
    assert {"2.10", "2.10-a"} <= ids


# --- Juge par conditions : la décision est calculée -------------------------------

from couverture.conditions import JugeConditions, decider, lire_grille  # noqa: E402
from couverture.models import EtatCondition  # noqa: E402

PARTIES_COMMUNES = "les vols commis dans les parties communes de l'immeuble, y compris dans un local à vélos collectif"
VOL_LOGEMENT = "résultant d'un vol ou d'une tentative de vol commis à l'intérieur des locaux d'habitation"


def grille(etat_lieu="REMPLIE", etat_exclusion="REMPLIE", extrait_exclusion=PARTIES_COMMUNES):
    return {
        "garanties": [{"nom": "Vol dans le logement", "conditions": [
            {"clause_id": "4.1", "extrait": VOL_LOGEMENT, "enonce": "Le vol a-t-il eu lieu dans le logement ?",
             "etat": etat_lieu, "justification": "…", "question": "Où était le vélo ?"},
        ]}],
        "exclusions": [
            {"clause_id": "4.4", "extrait": extrait_exclusion, "enonce": "Le vol a-t-il eu lieu dans les parties communes ?",
             "etat": etat_exclusion, "justification": "…", "question": "Le local est-il commun à l'immeuble ?"},
        ],
        "limites": [{"clause_id": "9.1", "extrait": "Une franchise de 150 €", "enonce": "Franchise de 150 €"}],
        "resume": "…",
    }


def analyser_conditions(clauses, reponse, sinistre="Mon vélo a été volé."):
    return Pipeline(clauses, juge=JugeConditions(FauxLLM(reponse))).analyser(sinistre)


def test_conditions_exclusion_remplie_donne_non_couvert(clauses):
    v = analyser_conditions(clauses, grille(etat_lieu="NON_REMPLIE")).verdict
    assert v.decision == Decision.NON_COUVERT
    decisives = [c for c in v.conditions if c.decisive]
    assert [c.clause_id for c in decisives] == ["4.4"] and decisives[0].pages == [1]
    assert v.citations[0].clause_id == "4.4"  # la clause décisive est citée en premier


def test_conditions_tout_rempli_donne_couvert(clauses):
    v = analyser_conditions(clauses, grille(etat_lieu="REMPLIE", etat_exclusion="NON_REMPLIE")).verdict
    assert v.decision == Decision.COUVERT


def test_conditions_inconnue_donne_incertain_et_la_question(clauses):
    v = analyser_conditions(clauses, grille(etat_lieu="INCONNUE", etat_exclusion="INCONNUE")).verdict
    assert v.decision == Decision.INCERTAIN
    assert "Où était le vélo ?" in v.informations_manquantes


def test_conditions_garantie_remplie_mais_exclusion_inconnue(clauses):
    v = analyser_conditions(clauses, grille(etat_lieu="REMPLIE", etat_exclusion="INCONNUE")).verdict
    assert v.decision == Decision.INCERTAIN
    assert v.informations_manquantes == ["Le local est-il commun à l'immeuble ?"]


def test_conditions_exclusion_sans_preuve_est_ecartee(clauses):
    # Le modèle invente une exclusion : elle est écartée, la décision ne peut pas s'appuyer dessus.
    v = analyser_conditions(clauses, grille(etat_lieu="REMPLIE", etat_exclusion="REMPLIE",
                                            extrait_exclusion="les vélos ne sont jamais couverts")).verdict
    assert v.decision == Decision.COUVERT
    assert any("Condition écartée" in a for a in v.avertissements) and v.confiance <= 0.5


def test_conditions_aucune_garantie_applicable():
    conds = lire_grille({"garanties": [{"nom": "Vol", "conditions": [
        {"clause_id": "x", "extrait": "e", "enonce": "Dans le logement ?", "etat": "NON_REMPLIE"}]}]})
    assert decider(conds)[0] == Decision.NON_COUVERT
    assert decider([])[0] == Decision.INCERTAIN
    assert lire_grille({"exclusions": [{"clause_id": "x", "extrait": "e", "enonce": "?", "etat": "peut-être"}]})[0].etat == EtatCondition.INCONNUE


# --- Configuration du modèle (Mistral) ----------------------------------------------

import io  # noqa: E402
import urllib.error  # noqa: E402

from couverture import llm as module_llm  # noqa: E402
from couverture.config import charger_env, lire_env  # noqa: E402

VARIABLES = ["MISTRAL_API_KEY", "ANTHROPIC_API_KEY", "COUVERTURE_LLM_URL", "COUVERTURE_FOURNISSEUR", "COUVERTURE_MODELE",
             "COUVERTURE_REFLEXION", "COUVERTURE_DEBUG"]


@pytest.fixture
def env_vide(monkeypatch):
    for v in VARIABLES:
        monkeypatch.delenv(v, raising=False)
    return monkeypatch


def test_lire_env(tmp_path):
    f = tmp_path / ".env"
    f.write_text('# commentaire\nMISTRAL_API_KEY="abc"\nexport COUVERTURE_MODELE=mistral-small-latest # petit\nVIDE=\n', encoding="utf-8")
    assert lire_env(f) == {"MISTRAL_API_KEY": "abc", "COUVERTURE_MODELE": "mistral-small-latest", "VIDE": ""}


def test_charger_env_n_ecrase_pas(env_vide, tmp_path):
    f = tmp_path / ".env"
    f.write_text("MISTRAL_API_KEY=fichier\nCOUVERTURE_MODELE=mistral-small-latest\n", encoding="utf-8")
    env_vide.setenv("MISTRAL_API_KEY", "environnement")
    assert charger_env(f) == ["COUVERTURE_MODELE"]
    import os
    assert os.environ["MISTRAL_API_KEY"] == "environnement"


def test_configurer_choisit_mistral(env_vide):
    assert module_llm.configurer() is None
    env_vide.setenv("MISTRAL_API_KEY", "colle-ta-cle-ici")  # valeur d'exemple ignorée
    assert module_llm.configurer() is None
    env_vide.setenv("MISTRAL_API_KEY", "k")
    env_vide.setenv("ANTHROPIC_API_KEY", "a")
    llm = module_llm.configurer()
    assert isinstance(llm, module_llm.MistralLLM) and llm.nom == "mistral:mistral-large-latest"
    env_vide.setenv("COUVERTURE_FOURNISSEUR", "anthropic")
    assert isinstance(module_llm.configurer(), module_llm.AnthropicLLM)
    env_vide.setenv("COUVERTURE_FOURNISSEUR", "inconnu")
    with pytest.raises(module_llm.ErreurLLM):
        module_llm.configurer()


class _Reponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_mistral_requete_et_reessai(env_vide, monkeypatch):
    env_vide.setenv("MISTRAL_API_KEY", "secret")
    envoyees = []

    def faux_urlopen(requete, timeout):
        envoyees.append(requete)
        if len(envoyees) == 1:  # première tentative : limite de débit
            raise urllib.error.HTTPError(requete.full_url, 429, "trop", {"retry-after": "0"}, io.BytesIO(b""))
        return _Reponse(json.dumps({"choices": [{"message": {"content": '{"ok": true}'}}]}).encode())

    monkeypatch.setattr(module_llm.urllib.request, "urlopen", faux_urlopen)
    monkeypatch.setattr(module_llm.time, "sleep", lambda s: None)
    assert module_llm.MistralLLM().completer("sys", "msg") == '{"ok": true}'
    r = envoyees[-1]
    corps = json.loads(r.data)
    assert r.full_url == "https://api.mistral.ai/v1/chat/completions"
    assert r.get_header("Authorization") == "Bearer secret"
    assert corps["response_format"] == {"type": "json_object"} and corps["temperature"] == 0
    assert corps["top_p"] == 1  # exigé par Mistral avec temperature=0
    assert len(envoyees) == 2


def test_cle_refusee_message_clair(env_vide, monkeypatch):
    env_vide.setenv("MISTRAL_API_KEY", "mauvaise")

    def refus(requete, timeout):
        raise urllib.error.HTTPError(requete.full_url, 401, "non", {}, io.BytesIO(b"Unauthorized"))

    monkeypatch.setattr(module_llm.urllib.request, "urlopen", refus)
    with pytest.raises(module_llm.ErreurLLM, match="Clé API refusée"):
        module_llm.MistralLLM().completer("sys", "msg")


# --- Recherche hybride (mots + sens, fusion RRF) -------------------------------------

import re as _re  # noqa: E402

from couverture.ingestion import calculer_vecteurs  # noqa: E402
from couverture.recherche import texte_a_vectoriser  # noqa: E402


class FauxVectoriseur:
    """Embeddings jouets : une dimension par notion. « chouravé » est du vol, comme le ferait
    un vrai modèle, alors qu'aucun mot n'est commun avec le contrat."""

    nom = "faux:embed"
    NOTIONS = [r"\bvol|chourav|derob", r"incend|feu\b|flamm", r"\beau\b|fuite", r"commun"]

    def __init__(self, panne=False):
        self.appels = 0
        self.panne = panne

    def vectoriser(self, textes):
        self.appels += 1
        if self.panne:
            raise RuntimeError("service indisponible")
        return [[0.1] + [len(_re.findall(n, normaliser_t(t))) for n in self.NOTIONS] for t in textes]


def normaliser_t(t):
    from couverture.texte import normaliser
    return normaliser(t)


def test_recherche_par_le_sens_trouve_ce_que_les_mots_ratent(clauses):
    question = "On m'a chouravé ma bicyclette"
    sans = {r.clause.id for r in Recherche(clauses).rechercher(question)}
    vecteurs = dict(zip([c.id for c in clauses], FauxVectoriseur().vectoriser([texte_a_vectoriser(c) for c in clauses])))
    avec = Recherche(clauses, vecteurs, FauxVectoriseur()).rechercher(question)
    raisons = {r.clause.id: r.raison for r in avec}
    assert "4.1" not in sans
    assert "4.1" in raisons and "sens" in raisons["4.1"]
    assert "4.4" in raisons  # l'enveloppe suit : l'exclusion du même article est ramenée


def test_recherche_sans_vecteurs_reste_lexicale(clauses):
    r = Recherche(clauses, {}, FauxVectoriseur())
    assert not r.hybride  # un vectoriseur sans vecteurs calculés ne change rien


def test_ingestion_calcule_les_vecteurs_une_fois(tmp_path):
    base = Base(tmp_path / "b.sqlite")
    f = tmp_path / "a.md"
    f.write_text(CG_FICTIF.read_text(encoding="utf-8"), encoding="utf-8")
    ingerer_fichier(f, base, {"id": "a"})
    assert base.vecteurs("a", FauxVectoriseur.nom) == {}
    v = FauxVectoriseur()
    c = ingerer_fichier(f, base, {"id": "a"}, vectoriseur=v)  # clé ajoutée après coup : seuls les vecteurs
    assert len(base.vecteurs("a", v.nom)) == 30 and "30 vecteurs" in c.rapport["embeddings"]
    ingerer_fichier(f, base, {"id": "a"}, vectoriseur=v)
    assert v.appels == 1  # rien n'a changé : pas de nouvel appel
    p = Pipeline.depuis_base(base, "a", juge=JugeHeuristique(), vectoriseur=FauxVectoriseur())
    assert p.recherche.hybride


def test_panne_des_embeddings_ne_bloque_pas(tmp_path):
    base = Base(tmp_path / "b.sqlite")
    statut = calculer_vecteurs("x", [], base, FauxVectoriseur(panne=True))
    assert statut.startswith("échec")


# --- Profils d'assureur ----------------------------------------------------------------

from couverture.chargement import Ligne  # noqa: E402
from couverture.profils import ProfilInvalide, valider_profil  # noqa: E402
from couverture.reparation import Propositions, candidats_titres, diagnostiquer, proposer_reparation, verifier  # noqa: E402


def contrat_maison():
    """Un assureur qui titre ses exclusions « Les situations hors contrat » : non reconnu par défaut."""
    textes = ["Article 1 Lexique", "Effraction : forcement d'une serrure.", "Dépendance : cave ou garage.",
              "Vol : soustraction frauduleuse.", "Réf. MAISON-2026 page"]
    for n, (titre, objet) in enumerate([("Vol", "le vol des biens dans le logement"),
                                        ("Incendie", "les dommages causés par l'incendie"),
                                        ("Dégâts des eaux", "les fuites des conduites")], start=2):
        textes += [f"Article {n} {titre}", f"Nous garantissons {objet}.",
                   "Les situations hors contrat", f"Le {titre.lower()} commis dans le hall de l'immeuble.",
                   "Réf. MAISON-2026 page"]
    textes += ["Article 5 Dispositions communes", "Les situations hors contrat", "La guerre et les émeutes."]
    return [Ligne(page=1, texte=t) for t in textes]


def test_profil_change_le_typage():
    lignes = contrat_maison()
    sans = {c.id: c.type for c in segmenter_lignes(lignes)}
    profil = valider_profil({"nom": "maison", "intertitres": {"Les situations hors contrat": "exclusion"}})
    avec = {c.id: c.type for c in segmenter_lignes(lignes, profil)}
    assert TypeClause.EXCLUSION not in sans.values()
    assert avec["2-a"] == TypeClause.EXCLUSION and avec["5-a"] == TypeClause.EXCLUSION


def test_profil_invalide():
    with pytest.raises(ProfilInvalide):
        valider_profil({"nom": "x", "intertitres": {"Les cas": "peut-etre"}})
    with pytest.raises(ProfilInvalide):
        valider_profil({"nom": "Pas Bon"})


# --- Agent de réparation : il propose, un humain décide ---------------------------------

PROPOSITION = {
    "intertitres": [
        {"ligne": "Les situations hors contrat", "type": "exclusion", "raison": "liste ce qui n'est pas couvert"},
        {"ligne": "Ce que nous refusons toujours", "type": "exclusion", "raison": "inventée"},
    ],
    "lignes_ignorees": [
        {"motif": r"^Réf\. MAISON-2026", "exemple": "Réf. MAISON-2026 page", "raison": "pied de page"},
        {"motif": r"^Nous garantissons", "exemple": "Nous garantissons le vol des biens dans le logement.", "raison": "piège"},
    ],
    "lexique": "deux_points",
    "explication": "Les exclusions sont titrées « Les situations hors contrat ».",
}


def test_verification_garde_le_vrai_et_ecarte_le_reste():
    lignes = contrat_maison()
    v = verifier(PROPOSITION, {}, "maison", lignes)
    assert v["profil"]["intertitres"] == {"les situations hors contrat": "exclusion"}
    assert v["profil"]["lignes_ignorees"] == [r"^Réf\. MAISON-2026"]
    assert any("absent du contrat" in e for e in v["ecarts"])
    assert any("contenu contractuel" in e for e in v["ecarts"])
    assert v["ameliore"] and len(v["apres"]["alertes"]) < len(v["avant"]["alertes"])


def test_proposition_validee_par_un_humain(tmp_path):
    donnees = tmp_path
    (donnees / "contrats").mkdir()
    lignes = contrat_maison()
    rapport = controler(segmenter_lignes(lignes))
    assert any(d["famille"] == "sans_exclusion" for d in diagnostiquer(rapport))
    assert "Les situations hors contrat" in candidats_titres(lignes)[:3]  # le plus fréquent d'abord

    depot = Propositions(donnees)
    p = proposer_reparation("maison-2026", "maison.pdf", lignes, rapport, None, "maison", FauxLLM(PROPOSITION), depot)
    assert p["statut"] == "a_valider" and not (donnees / "profils").exists()  # rien d'appliqué

    depot.accepter(p["numero"])
    assert json.loads((donnees / "profils" / "maison.json").read_text(encoding="utf-8"))["intertitres"]
    assert json.loads((donnees / "contrats" / "catalogue.json").read_text(encoding="utf-8"))["maison.pdf"]["profil"] == "maison"
    with pytest.raises(ValueError):
        depot.accepter(p["numero"])  # déjà acceptée


def test_proposition_sans_amelioration_est_refusee(tmp_path):
    lignes = contrat_maison()
    rapport = controler(segmenter_lignes(lignes))
    vide = {"intertitres": [], "lignes_ignorees": [], "explication": "rien"}
    p = proposer_reparation("m", "m.pdf", lignes, rapport, None, "maison", FauxLLM(vide), Propositions(tmp_path))
    assert p["statut"] == "refusee_par_la_verification"


# --- Juge de la grille : la relecture ne peut que rendre plus prudent ------------------------

def relecteur(avis: str, raison: str = "…", question: str = ""):
    return FauxLLM({"relectures": [{"id": i, "avis": avis, "raison": raison, "question": question} for i in range(1, 6)]})


def juge_avec_relecture(reponse, relu):
    return JugeConditions(FauxLLM(reponse), relecteur=relu)


def test_relecture_confirme(clauses):
    v = Pipeline(clauses, juge=juge_avec_relecture(grille(etat_lieu="NON_REMPLIE"), relecteur("confirmee"))).analyser("Vélo volé.").verdict
    assert v.decision == Decision.NON_COUVERT and v.decision_avant_relecture is None
    assert all(c.relecture == "confirmee" for c in v.conditions if c.decisive)


def test_relecture_conteste_une_exclusion(clauses):
    relu = relecteur("contestee", "Le local n'est pas décrit comme commun.", "Le local est-il commun à l'immeuble ?")
    v = Pipeline(clauses, juge=juge_avec_relecture(grille(etat_lieu="INCONNUE"), relu)).analyser("Vélo volé.").verdict
    assert v.decision == Decision.INCERTAIN and v.decision_avant_relecture == Decision.NON_COUVERT
    exclusion = next(c for c in v.conditions if c.nature == "exclusion")
    assert exclusion.relecture == "contestee" and exclusion.etat_propose == EtatCondition.REMPLIE
    assert "Le local est-il commun à l'immeuble ?" in v.informations_manquantes


def test_relecture_evite_un_faux_couvert(clauses):
    # Le modèle a écarté l'exclusion ; la relecture la conteste : plus de « couvert ».
    v = Pipeline(clauses, juge=juge_avec_relecture(grille(etat_lieu="REMPLIE", etat_exclusion="NON_REMPLIE"),
                                                   relecteur("contestee"))).analyser("Vélo volé.").verdict
    assert v.decision_avant_relecture == Decision.COUVERT and v.decision != Decision.COUVERT


def test_relecture_en_panne_ne_change_pas_la_decision(clauses):
    v = Pipeline(clauses, juge=juge_avec_relecture(grille(etat_lieu="NON_REMPLIE"), FauxLLM("pas de json"))).analyser("Vélo volé.").verdict
    assert v.decision == Decision.NON_COUVERT and v.confiance <= 0.6
    assert any("Relecture indisponible" in a for a in v.avertissements)


def test_pas_de_relecture_si_incertain(clauses):
    relu = relecteur("contestee")
    Pipeline(clauses, juge=juge_avec_relecture(grille(etat_lieu="INCONNUE", etat_exclusion="INCONNUE"), relu)).analyser("Vélo volé.")
    assert relu.dernier_message == ""  # rien à relire : la réponse admet déjà sa limite


# --- Juge de qualité à l'ingestion ------------------------------------------------------

from couverture.qualite import appliquer, echantillon, juger_qualite  # noqa: E402


def test_echantillon_stratifie_et_reproductible(clauses):
    a, b = echantillon(clauses, "graine"), echantillon(clauses, "graine")
    assert [c.id for c in a] == [c.id for c in b]
    assert {c.type for c in a} >= {TypeClause.GARANTIE, TypeClause.EXCLUSION, TypeClause.DEFINITION}


def test_juge_qualite_score_et_alerte(clauses):
    choisies = echantillon(clauses, "g")
    fausse = choisies[0]
    jugements = [{"id": c.id, "juste": c is not fausse, "type_propose": "exclusion" if c is fausse else c.type.value}
                 for c in choisies]
    q = juger_qualite(clauses, FauxLLM({"jugements": jugements}), "g", seuil=1.0)
    assert q["score"] < 1 and q["erreurs"][0]["clause_id"] == fausse.id
    r = appliquer(controler(clauses), q)
    assert r["statut"] == "A_VERIFIER" and any("Typage douteux" in a for a in r["alertes"])
    assert diagnostiquer(r)[-1]["famille"] == "typage_douteux"


def test_juge_qualite_en_panne_ne_bloque_pas(tmp_path):
    base = Base(tmp_path / "b.sqlite")
    f = tmp_path / "a.md"
    f.write_text(CG_FICTIF.read_text(encoding="utf-8"), encoding="utf-8")
    c = ingerer_fichier(f, base, {"id": "a"}, juge_qualite=FauxLLM("illisible"))
    assert c.statut == "OK" and "erreur" in c.rapport["qualite"]
    assert base.contrat("a").statut == "OK"


def test_verification_tient_compte_du_juge_de_qualite():
    # Le juge de qualité dit que « Les situations hors contrat » sont des exclusions, pas « autre ».
    lignes = contrat_maison()
    corrections = [{"clause_id": "2-a", "titre": "Les situations hors contrat", "type": "autre", "type_propose": "exclusion", "raison": "…"}]
    v = verifier({"intertitres": [{"ligne": "Les situations hors contrat", "type": "exclusion"}]}, {}, "maison", lignes, corrections)
    assert v["ameliore"] and v["apres"]["corrections_qualite"].startswith("1/1")


# --- Journal, dérive et bilan --------------------------------------------------------------

from datetime import datetime, timedelta, timezone  # noqa: E402

from couverture.bilan import construire_bilan, envoyer  # noqa: E402
from couverture.derive import calculer, psi  # noqa: E402
from couverture.journal import Journal  # noqa: E402
from couverture.models import Citation, Faits, Resultat, Verdict  # noqa: E402

MAINTENANT = datetime(2026, 11, 17, 8, 0, tzinfo=timezone.utc)


def resultat(decision="NON_COUVERT", evenement="vol", contrat="foyer", questions=()):
    v = Verdict(decision=Decision(decision), justification="…", confiance=0.9 if decision != "INCERTAIN" else 0.5,
                citations=[Citation(clause_id="4.4", extrait="x")], informations_manquantes=list(questions))
    return Resultat(sinistre="Un sinistre décrit en une phrase.", contrat_id=contrat, methode="conditions",
                    faits=Faits(evenements=[evenement]), clauses_consultees=[], verdict=v)


def remplir(journal, n, debut, pas=2, **kw):
    for i in range(n):
        journal.noter(resultat(**kw), date=debut + timedelta(hours=i * pas))


def test_psi():
    assert psi(["a"] * 50 + ["b"] * 50, ["a"] * 50 + ["b"] * 50) == 0
    assert psi(["a"] * 90 + ["b"] * 10, ["a"] * 10 + ["b"] * 90) > 0.25


def test_derive_stable_puis_forte(tmp_path):
    j = Journal(str(tmp_path / "b.sqlite"))
    assert "pas assez" in calculer(j, MAINTENANT)["statut"]
    remplir(j, 120, MAINTENANT - timedelta(days=30), evenement="vol")
    remplir(j, 40, MAINTENANT - timedelta(days=6), evenement="vol")
    assert calculer(j, MAINTENANT)["statut"] == "stable"
    remplir(j, 80, MAINTENANT - timedelta(days=5), pas=1, evenement="degat_des_eaux", decision="INCERTAIN")
    d = calculer(j, MAINTENANT)
    assert d["variables"]["evenement"]["niveau"] == "forte" and d["statut"] == "alerte"
    assert any("Contrat foyer" in a for a in d["alertes"])


def test_bilan(tmp_path, monkeypatch):
    base = Base(tmp_path / "b.sqlite")
    j = Journal(base.chemin)
    remplir(j, 6, MAINTENANT - timedelta(days=2), decision="INCERTAIN", questions=["L'option vélo est-elle souscrite ?"])
    j.noter_erreur("foyer", "conditions", "Clé API refusée (401).", date=MAINTENANT - timedelta(days=1))
    texte, resume = construire_bilan(base, tmp_path, maintenant=MAINTENANT)
    assert resume["analyses"] == 6 and resume["erreurs"] == 1 and resume["taux_incertain"] == 1
    assert "L'option vélo est-elle souscrite ? (6 fois)" in texte
    assert "## À faire" in texte and "Clé API refusée" in texte
    for v in ("SMTP_HOTE", "BILAN_DESTINATAIRE"):
        monkeypatch.delenv(v, raising=False)
    assert envoyer(texte, "bilan").startswith("Mail non envoyé")


def test_le_journal_ne_garde_pas_le_texte_du_sinistre(tmp_path):
    j = Journal(str(tmp_path / "b.sqlite"))
    j.noter(resultat(), date=MAINTENANT)
    ligne = j.lignes(MAINTENANT - timedelta(days=1), MAINTENANT + timedelta(days=1))[0]
    assert "Un sinistre" not in json.dumps(ligne) and ligne["longueur"] == len("Un sinistre décrit en une phrase.")


# --- Versionnage des consignes (garde-fou de la CI) -----------------------------------------------

from couverture import consignes  # noqa: E402


def test_manifeste_des_consignes_a_jour():
    """Échoue si une consigne a changé sans nouvelle version, ou si le manifeste n'est pas à jour :
    `couverture versions --manifeste`."""
    assert consignes.verifier() == []


def test_garde_fou_texte_change_sans_version():
    manifeste = consignes.etat_actuel()
    manifeste["couverture-relecture"] = {**manifeste["couverture-relecture"], "empreinte": "0000000000000000"}
    assert any("pas sa version" in p for p in consignes.verifier(manifeste))


class FauxMlflow:
    """Ce dont le code a besoin du module mlflow, en mémoire."""

    def __init__(self):
        self.appels = []
        self.prompts = {}
        outer = self

        class Genai:
            def load_prompt(self_, uri):
                nom = uri.removeprefix("prompts:/").split("@")[0]
                if nom not in outer.prompts:
                    raise KeyError(nom)
                return outer.prompts[nom]

            def register_prompt(self_, name, template, commit_message, tags):
                outer.appels.append(("register_prompt", name))
                p = type("P", (), {"template": template, "version": len(outer.appels)})()
                outer.prompts[name] = p
                return p

            def set_prompt_alias(self_, name, alias, version):
                outer.appels.append(("alias", name, alias))

        self.genai = Genai()

    def set_tracking_uri(self, uri): self.appels.append(("uri", uri))
    def set_experiment(self, nom): self.appels.append(("experience", nom))
    def start_run(self, run_name): self.appels.append(("debut", run_name)); return object()
    def end_run(self): self.appels.append(("fin",))
    def log_params(self, p): self.appels.append(("params", p))
    def log_metrics(self, m): self.appels.append(("metriques", m))
    def set_tags(self, t): self.appels.append(("tags", t))
    def log_artifact(self, chemin): self.appels.append(("artefact", Path(chemin).name, Path(chemin).read_text(encoding="utf-8")))


def test_enregistrement_des_consignes_idempotent():
    m = FauxMlflow()
    premiere = consignes.enregistrer_dans_mlflow(m)
    assert sum(a[0] == "register_prompt" for a in m.appels) == len(consignes.CONSIGNES)
    assert ("alias", "couverture-relecture", "production") in m.appels
    seconde = consignes.enregistrer_dans_mlflow(m)
    assert all("inchangée" in l for l in seconde) and len(premiere) == len(seconde)


# --- Suivi MLflow : jamais bloquant -------------------------------------------------------------------

from couverture import suivi  # noqa: E402


def test_metriques_ingestion_et_evaluation(tmp_path):
    base = Base(tmp_path / "b.sqlite")
    f = tmp_path / "a.md"
    f.write_text(CG_FICTIF.read_text(encoding="utf-8"), encoding="utf-8")
    c = ingerer_fichier(f, base, {"id": "a"})
    m = suivi.metriques_ingestion([c])
    assert m["contrat/a/clauses/exclusion"] == 7 and m["contrat/a/ok"] == 1 and m["contrats_a_verifier"] == 0
    assert suivi.metriques_evaluation({"n": 14, "exactitude": 0.5, "rappel_clauses_moyen": None}) == {"n": 14.0, "exactitude": 0.5}
    p = suivi.parametres_communs()
    assert p["consigne/grille-conditions"] == "v3" and p["modele/juge"].startswith("aucun")


def test_execution_enregistre_et_ne_bloque_jamais(monkeypatch):
    m = FauxMlflow()
    monkeypatch.setattr(suivi, "module_mlflow", lambda: m)
    with suivi.execution("couverture-evaluation", "essai") as s:
        s.parametres({"methode": "conditions"})
        s.metriques({"exactitude": 0.5})
        s.artefact_json("rapport.json", {"n": 1})
    noms = [a[0] for a in m.appels]
    assert noms == ["experience", "debut", "params", "metriques", "artefact", "fin"]

    m.log_metrics = lambda _: (_ for _ in ()).throw(RuntimeError("serveur tombé"))
    with suivi.execution("x", "y") as s:
        s.metriques({"a": 1})  # l'erreur du suivi ne remonte pas

    monkeypatch.setattr(suivi, "module_mlflow", lambda: None)
    with suivi.execution("x", "y") as s:
        s.metriques({"a": 1})  # sans MLflow : rien, sans erreur


def test_mlflow_desactive(monkeypatch):
    monkeypatch.setenv("MLFLOW_ACTIF", "false")
    assert suivi.module_mlflow() is None


def test_cli_evaluer_de_bout_en_bout(tmp_path, monkeypatch, capsys):
    from couverture import cli

    (tmp_path / "contrats").mkdir()
    (tmp_path / "annotations").mkdir()
    (tmp_path / "contrats" / "c.md").write_text(CG_FICTIF.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "contrats" / "catalogue.json").write_text(json.dumps({"c.md": {"id": "fictif-habitat-serein"}}), encoding="utf-8")
    (tmp_path / "sinistres.jsonl").write_bytes((DONNEES / "sinistres.jsonl").read_bytes())
    (tmp_path / "annotations" / "fictif-habitat-serein.jsonl").write_bytes(
        (DONNEES / "annotations" / "fictif-habitat-serein.jsonl").read_bytes())
    for v in ("MISTRAL_API_KEY", "ANTHROPIC_API_KEY", "COUVERTURE_LLM_URL"):
        monkeypatch.delenv(v, raising=False)
    monkeypatch.setenv("MLFLOW_ACTIF", "false")
    monkeypatch.chdir(tmp_path)
    assert cli.main(["--donnees", str(tmp_path), "ingerer"]) == 0
    assert cli.main(["--donnees", str(tmp_path), "evaluer", "--contrat", "fictif-habitat-serein", "--hors-ligne"]) == 0
    assert '"faux_couverts": 0' in capsys.readouterr().out
    assert cli.main(["--donnees", str(tmp_path), "bilan"]) == 0
    assert cli.main(["--donnees", str(tmp_path), "versions"]) == 0


# --- Tableaux Grafana : à jour, et chaque requête s'exécute -----------------------------------------

import sqlite3  # noqa: E402

from monitoring.grafana import construire_tableaux as grafana  # noqa: E402


def test_tableaux_grafana_a_jour():
    """Échoue si le JSON n'a pas été régénéré : `python -m monitoring.grafana.construire_tableaux`."""
    for nom, fabrique in grafana.TABLEAUX.items():
        assert (grafana.DOSSIER / nom).read_text(encoding="utf-8") == grafana.contenu(fabrique), nom


def test_requetes_grafana_sur_une_vraie_base(tmp_path):
    base = Base(tmp_path / "b.sqlite")
    f = tmp_path / "a.md"
    f.write_text(CG_FICTIF.read_text(encoding="utf-8"), encoding="utf-8")
    # Le juge conteste le type de toutes les exclusions (l'échantillon en contient toujours : il est stratifié).
    jugements = [{"id": c.id, "juste": c.type != TypeClause.EXCLUSION, "type_propose": "garantie"}
                 for c in segmenter_lignes(charger_lignes(f))]
    ingerer_fichier(f, base, {"id": "a", "assureur": "Fictif"}, juge_qualite=FauxLLM({"jugements": jugements}))
    j = Journal(base.chemin)
    remplir(j, 5, MAINTENANT - timedelta(days=2), decision="INCERTAIN", contrat="a", questions=["L'option est-elle souscrite ?"])
    remplir(j, 3, MAINTENANT - timedelta(days=1), decision="NON_COUVERT", contrat="a")
    j.noter_erreur("a", "conditions", "Clé API refusée (401).", date=MAINTENANT)

    attendu = {"Analyses": [(8,)], "Erreurs du modèle": [(1,)], "Contrats": [(1,)],
               "Questions à poser à l'assuré les plus fréquentes": [("L'option est-elle souscrite ?", 5)]}
    with sqlite3.connect(base.chemin) as cx:
        for fabrique in grafana.TABLEAUX.values():
            for p in fabrique()["panels"]:
                if p["type"] == "row":
                    continue
                sql = p["targets"][0]["rawQueryText"]
                sql = sql.replace("$__unixEpochFrom()", "0").replace("$__unixEpochTo()", "4000000000")
                lignes = cx.execute(sql).fetchall()  # chaque requête s'exécute
                if p["title"] in attendu:
                    assert lignes == attendu[p["title"]], p["title"]
                if p["type"] == "timeseries":
                    colonnes = [d[0] for d in cx.execute(sql).description]
                    assert colonnes[0] == "time" and lignes, p["title"]
            # Le juge de qualité a contesté un type : il apparaît dans le tableau des contrats.
        conteste = [p for p in grafana.tableau_contrats()["panels"] if p["title"] == "Types contestés par le juge de qualité"][0]
        assert len(cx.execute(conteste["targets"][0]["rawQueryText"]).fetchall()) >= 1


def test_reponse_en_morceaux():
    """Mistral récent renvoie une liste de morceaux ; la réflexion du modèle est ignorée."""
    contenu = [{"type": "thinking", "thinking": [{"type": "text", "text": "je réfléchis"}]},
               {"type": "text", "text": '{"ok": '}, {"type": "text", "text": "true}"}]
    assert module_llm.texte_du_message(contenu) == '{"ok": true}'
    assert module_llm.texte_du_message("simple") == "simple"
    assert module_llm.texte_du_message(None) == ""


# --- Réponses coupées et fichiers de documentation -----------------------------------------------

def test_reponse_coupee_signalee(env_vide, monkeypatch):
    env_vide.setenv("MISTRAL_API_KEY", "k")
    monkeypatch.setattr(module_llm.urllib.request, "urlopen", lambda r, timeout: _Reponse(json.dumps(
        {"choices": [{"finish_reason": "length", "message": {"content": [{"type": "thinking", "thinking": []}]}}]}).encode()))
    with pytest.raises(module_llm.ReponseTronquee):
        module_llm.MistralLLM().completer("sys", "msg")


class LLMQuiCoupe:
    nom = "coupe"

    def completer(self, systeme, message):
        raise module_llm.ReponseTronquee("réponse coupée à 8000 tokens")


def test_juges_prudents_si_reponse_coupee(clauses):
    from couverture.juges import JugeLLM
    for juge in (JugeLLM(LLMQuiCoupe()), JugeConditions(LLMQuiCoupe())):
        v = Pipeline(clauses, juge=juge).analyser("Vélo volé dans le local commun.").verdict
        assert v.decision == Decision.INCERTAIN and v.confiance == 0.0
    q = juger_qualite(clauses, LLMQuiCoupe(), "g")
    assert "coupée" in q["erreur"]



def test_grille_coupee_puis_raccourcie(clauses, tmp_path, monkeypatch):
    """Une réponse coupée relance une demande plus courte, et non « JSON invalide »."""
    class CoupePuisRepond:
        nom = "coupe-puis-repond"

        def __init__(self):
            self.messages = []

        def completer(self, systeme, message):
            self.messages.append(message)
            if len(self.messages) == 1:
                raise module_llm.ReponseTronquee("réponse coupée à 8000 tokens", '{"garanties": [')
            return json.dumps(grille(etat_exclusion="REMPLIE"))

    llm = CoupePuisRepond()
    v = Pipeline(clauses, juge=JugeConditions(llm)).analyser("Vélo volé dans le local commun.").verdict
    assert v.decision == Decision.NON_COUVERT
    assert "trop longue" in llm.messages[1]
    # Avec COUVERTURE_DEBUG, le début de la réponse coupée est gardé pour diagnostic.
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("COUVERTURE_DEBUG", "oui")
    e = module_llm.ReponseTronquee("réponse coupée", "debut")
    assert "data/debug" in str(e).replace("\\", "/")
    assert list((tmp_path / "data" / "debug").glob("reponse-coupee-*.txt"))


def test_mistral_reflexion_courte_et_repli(env_vide, monkeypatch):
    """Réflexion « low » envoyée par défaut ; retirée si le modèle la refuse."""
    import urllib.error
    env_vide.setenv("MISTRAL_API_KEY", "k")
    corps_envoyes = []

    def faux_urlopen(requete, timeout):
        corps = json.loads(requete.data)
        corps_envoyes.append(corps)
        if "reasoning_effort" in corps:
            raise urllib.error.HTTPError(requete.full_url, 422, "x", {},
                                         io.BytesIO(b'{"message": "reasoning_effort not supported"}'))
        return _Reponse(json.dumps({"choices": [{"finish_reason": "stop", "message": {"content": "{}"}}]}).encode())

    monkeypatch.setattr(module_llm.urllib.request, "urlopen", faux_urlopen)
    llm = module_llm.MistralLLM()
    assert llm.completer("s", "m") == "{}"
    assert corps_envoyes[0]["reasoning_effort"] == "low" and "reasoning_effort" not in corps_envoyes[1]
    llm.completer("s", "m")
    assert len(corps_envoyes) == 3  # le paramètre n'est plus renvoyé ensuite
    env_vide.setenv("COUVERTURE_REFLEXION", "defaut")
    assert "reasoning_effort" not in module_llm.MistralLLM().extra


def test_delai_depasse_lisible(env_vide, monkeypatch):
    env_vide.setenv("MISTRAL_API_KEY", "k")
    appels = []

    def lent(requete, timeout):
        appels.append(1)
        raise TimeoutError("The read operation timed out")

    monkeypatch.setattr(module_llm.urllib.request, "urlopen", lent)
    with pytest.raises(module_llm.ReponseLente, match="pas de réponse après"):
        module_llm.MistralLLM().completer("s", "m")
    assert len(appels) == 1  # pas quatre fois la même requête lente

def test_ingestion_ignore_la_documentation_et_retire_les_contrats_disparus(tmp_path):
    base = Base(tmp_path / "b.sqlite")
    d = tmp_path / "contrats"
    d.mkdir()
    (d / "a.md").write_text(CG_FICTIF.read_text(encoding="utf-8"), encoding="utf-8")
    (d / "b.md").write_text(CG_FICTIF.read_text(encoding="utf-8"), encoding="utf-8")
    (d / "SOURCES.md").write_text("# Liens des contrats", encoding="utf-8")
    assert {c.id for c in ingerer_dossier(d, base)} == {"a", "b"}
    (d / "b.md").unlink()
    ingerer_dossier(d, base)
    assert [c.id for c in base.contrats()] == ["a"]
    with sqlite3.connect(base.chemin) as cx:
        cx.execute("PRAGMA foreign_keys = ON")
        assert cx.execute("SELECT COUNT(*) FROM clauses WHERE contrat_id = 'b'").fetchone()[0] == 0
