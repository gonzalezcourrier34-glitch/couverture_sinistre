import json
from pathlib import Path

import pytest

from couverture.base import Base
from couverture.chargement import charger_lignes
from couverture.controles import controler
from couverture.evaluation import charger_cas
from couverture.ingestion import ingerer_dossier, ingerer_fichier
from couverture.llm import extraire_json
from couverture.models import Decision, TypeClause
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


# --- Contrôle des citations --------------------------------------------------

def test_extrait_tolere_accents_ponctuation_et_coupures():
    texte = "Ne sont pas garantis : les vols commis dans les parties communes de l'immeuble, y compris dans un local à vélos collectif."
    assert extrait_present("les vols commis dans les parties communes … local a velos collectif", texte)
    assert not extrait_present("les vols commis dans la rue", texte)


def controle(clauses, reponse: dict):
    """Un verdict fixé d'avance, passé au contrôle des citations seul (toutes les clauses fournies)."""
    from couverture.models import ClauseRetenue, Verdict
    from couverture.validation import valider

    retenues = [ClauseRetenue(clause=c, score=0.0, raison="test") for c in clauses]
    return valider(Verdict.model_validate({**reponse, "mode": "fixe"}), retenues)


def test_citation_inventee_retrograde_la_decision(clauses):
    v = controle(clauses, {"decision": "COUVERT", "justification": "…", "confiance": 0.9,
                           "citations": [{"clause_id": "4.3", "extrait": "tous les vélos sont toujours garantis"}]})
    assert v.decision == Decision.INCERTAIN and v.decision_initiale == Decision.COUVERT
    assert not v.citations[0].valide and v.confiance <= 0.5


def test_clause_non_fournie_est_rejetee(clauses):
    v = controle(clauses, {"decision": "NON_COUVERT", "justification": "…", "confiance": 0.8,
                           "citations": [{"clause_id": "99.9", "extrait": "n'importe quoi"}]})
    assert v.decision == Decision.INCERTAIN
    assert any("non fournie" in a for a in v.avertissements)


def test_verdict_valide_passe_avec_pages(clauses):
    v = controle(clauses, {"decision": "NON_COUVERT", "justification": "Local collectif exclu.", "confiance": 0.85,
                           "citations": [{"clause_id": "4.4", "extrait": "les vols commis dans les parties communes de l'immeuble, y compris dans un local à vélos collectif", "role": "garantie"}]})
    c = v.citations[0]
    assert v.decision == Decision.NON_COUVERT
    assert c.valide and c.role == "exclusion" and c.pages == [1]  # le rôle vient du contrat


def test_extraire_json_bloc_markdown():
    assert extraire_json('```json\n{"decision": "COUVERT"}\n```') == {"decision": "COUVERT"}


# --- Évaluation ----------------------------------------------------------------

def test_jeu_de_test_coherent():
    cas = charger_cas(DONNEES / "sinistres.jsonl", DONNEES / "annotations" / "fictif-habitat-serein.jsonl")
    assert len(cas) == 14
    assert {"velo-01", "bougie-01"} <= {c["id"] for c in cas}  # les deux cas du recruteur


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



# --- Configuration du modèle (Mistral) ----------------------------------------------

import io  # noqa: E402
import urllib.error  # noqa: E402

from couverture import llm as module_llm  # noqa: E402
from couverture.config import charger_env, lire_env  # noqa: E402

VARIABLES = ["MISTRAL_API_KEY", "COUVERTURE_MODELE", "COUVERTURE_MODELE_CONTRAT", "COUVERTURE_REFLEXION", "COUVERTURE_DEBUG"]


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
    llm = module_llm.configurer()
    assert isinstance(llm, module_llm.MistralLLM) and llm.nom == "mistral:mistral-large-latest"
    env_vide.setenv("COUVERTURE_MODELE_CONTRAT", "mistral-large-2")
    assert module_llm.configurer("contrat").nom == "mistral:mistral-large-2"
    assert module_llm.configurer().nom == "mistral:mistral-large-latest"


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


# --- Profils d'assureur ----------------------------------------------------------------

from couverture.chargement import Ligne  # noqa: E402
from couverture.profils import ProfilInvalide, valider_profil  # noqa: E402


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


def test_nous_vous_assurons_est_une_garantie():
    from couverture.segmentation import classer
    from couverture.models import TypeClause
    chemin = ["5 La responsabilité civile vie privée", "5.1 Les dispositions générales et votre responsabilité civile"]
    assert classer(chemin, "Nous vous assurons dans le monde entier lorsque votre responsabilité est mise en cause") \
        == TypeClause.GARANTIE
    assert classer(chemin, "Nous assurons votre responsabilité contractuelle") == TypeClause.GARANTIE


def test_profil_invalide():
    with pytest.raises(ProfilInvalide):
        valider_profil({"nom": "x", "intertitres": {"Les cas": "peut-etre"}})
    with pytest.raises(ProfilInvalide):
        valider_profil({"nom": "Pas Bon"})


# --- Journal --------------------------------------------------------------

from datetime import datetime, timedelta, timezone  # noqa: E402

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
    manifeste["couverture-lecture-socle"] = {**manifeste["couverture-lecture-socle"], "empreinte": "0000000000000000"}
    assert any("pas sa version" in p for p in consignes.verifier(manifeste))


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
    ingerer_fichier(f, base, {"id": "a", "assureur": "Fictif"})
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


def test_profil_reconnait_un_titre_numerote():
    """« 3.1.6.1 Etendue de la garantie » (AXA) : le profil parle du titre sans son numéro."""
    from couverture.segmentation import type_du_profil

    assert type_du_profil("3.1.6.1 Etendue de la garantie", {"etendue de la garantie": "garantie"}).value == "garantie"
    assert type_du_profil("Etendue de la garantie", {"etendue de la garantie": "garantie"}).value == "garantie"
    assert type_du_profil("3.1.6 Vol", {"etendue de la garantie": "garantie"}) is None


def test_renvoi_vers_un_sous_point_enumere():
    """« 3.1.7.2.9 les pertes… » est énuméré dans le texte de la clause 3.1.7.2 : le renvoi y mène."""
    from couverture.segmentation import resoudre

    ids = ["3.1.7", "3.1.7.1", "3.1.7.2", "4.1"]
    assert resoudre("3.1.7.2.9", ids) == ["3.1.7.2"]
    assert resoudre("3.1.7.2.9.1", ids) == ["3.1.7.2"]
    assert resoudre("3.1", ids) == ["3.1.7", "3.1.7.1", "3.1.7.2"]
    assert resoudre("5.2", ids) == [] and resoudre("4", ids) == ["4.1"]
    assert resoudre("9.9.9", ids) == []


# --- 7.87 : un contrat en deux colonnes (assureur D) -------------------------------------------------------------

from couverture.chargement import _deux_colonnes  # noqa: E402


class _PageFactice:
    """Une page pdfplumber réduite à ce que `_deux_colonnes` lit : des mots placés."""

    def __init__(self, mots, largeur=600):
        self.width, self._mots = largeur, mots

    def extract_words(self, **_):
        return self._mots

    def extract_text(self, **_):
        return "une colonne"


def _mot(texte, x0, top):
    return {"text": texte, "x0": x0, "x1": x0 + 8 * len(texte), "top": top}


def test_deux_colonnes_lues_colonne_par_colonne():
    """Le PDF entrelaçait les lignes des deux colonnes (« ART 2.3 Tempête … de débordements et renversements ») ;
    lue colonne par colonne, la page garde l'ordre du texte. Un titre sur toute la largeur coupe la page en bandes."""
    mots = [_mot("TITRE I - LES GARANTIES DES DOMMAGES", 40, 10)]
    for k in range(25):
        mots += [_mot(f"gauche{k}", 40, 30 + 12 * k), _mot(f"droite{k}", 340, 30 + 12 * k)]
    lignes = _deux_colonnes(_PageFactice(mots)).splitlines()
    assert lignes[0].startswith("TITRE I")
    assert lignes[1:26] == [f"gauche{k}" for k in range(25)] and lignes[26] == "droite0"
    pleine = [_mot("une phrase qui traverse toute la largeur de la page sans gouttière", 40, 30 + 12 * k) for k in range(45)]
    assert _deux_colonnes(_PageFactice(pleine)) == "une colonne"


def test_articles_a_tirets_lettrine_et_lexique_en_capitales():
    lignes = [Ligne(1, t) for t in [
        "LES DÉFINITIONS", "DOMMAGE CORPOREL", "Toute atteinte corporelle subie par une personne.",
        "FRANCHISE", "Somme qui reste à votre charge.", "ESPÈCES", "Billets et pièces de monnaie.",
        "ART 2-9 C atastrophes naturelles", "Ce que nous garantissons", "Les dommages matériels directs.",
        "1 Panne d'un appareil", "Le texte d'un point de liste."]]
    cl = {c.id: c for c in segmenter_lignes(lignes, {"titres_numerotes": "articles"})}
    assert {c.titre for c in cl.values() if c.type == TypeClause.DEFINITION} >= {"DOMMAGE CORPOREL", "FRANCHISE", "ESPÈCES"}
    assert any(c.id.startswith("2.9") and "Article 2.9 Catastrophes naturelles" in c.chemin for c in cl.values())
    assert not any(c.id.startswith("1") for c in cl.values()), "« 1 Panne » est un point de liste, pas un article"
    assert "Le texte d'un point de liste." in next(c.texte for c in cl.values() if c.id.startswith("2.9"))


def test_profil_colonnes_pages_et_articles():
    p = valider_profil({"nom": "assureur-d", "colonnes": 2, "pages_ignorees": [[11, 23]], "titres_numerotes": "articles"})
    assert p["colonnes"] == 2 and p["pages_ignorees"] == [[11, 23]] and p["titres_numerotes"] == "articles"
    assert "colonnes" not in valider_profil({"nom": "assureur-b"}), "un profil sans ces clés garde son empreinte"
    for faux in ({"colonnes": 3}, {"pages_ignorees": [[5, 2]]}, {"titres_numerotes": "aucun"}):
        with pytest.raises(ProfilInvalide):
            valider_profil({"nom": "x", **faux})


def test_une_lecture_sans_reponse_est_relancee_une_fois(env_vide, monkeypatch):
    """7.114 : l'analyse relance une fois un appel sans réponse en 15 s (un appel bloqué chez le fournisseur faisait
    monter le 95e centile à 20 s et plus) ; la rédaction, longue, ne relance pas."""
    env_vide.setenv("MISTRAL_API_KEY", "k")
    appels = []

    def une_fois_lent(requete, timeout):
        appels.append(timeout)
        if len(appels) == 1:
            raise TimeoutError("The read operation timed out")
        return _Reponse(json.dumps({"choices": [{"message": {"content": "{}"}, "finish_reason": "stop"}]}).encode())

    monkeypatch.setattr(module_llm.urllib.request, "urlopen", une_fois_lent)
    assert module_llm.configurer().completer("s", "m") == "{}"
    assert appels == [15, 15]
    long_ = module_llm.pour_travail_long(module_llm.configurer())
    assert long_.relances_lentes == 0 and long_.timeout == 300


def test_un_autre_modele_pour_le_temps_1(monkeypatch):
    """7.118 : COUVERTURE_MODELE_SOCLE donne le temps 1 (événement, bien, lieu) à un autre modèle ; les détails
    et la vérification restent au modèle de l'analyse. Sans la variable, rien ne change."""
    import json

    from couverture import lecture, llm

    class Modele:
        accepte_schema = True

        def __init__(self, nom):
            self.nom, self.systemes = nom, []

        def completer(self, systeme, message, schema=None):
            self.systemes.append(systeme)
            if systeme == lecture.SYSTEME_LECTURE_SOCLE:
                return json.dumps({"faits": {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"]}})
            return json.dumps({"faits": {"fermeture": "cadenas"}})

    petit, grand = Modele("petit"), Modele("grand")
    faits, _ = lecture.extraire_faits_regles("On m'a volé mon vélo dans ma cave fermée par un cadenas.", petit,
                                             verifier=False, llm_socle=grand)
    assert grand.systemes == [lecture.SYSTEME_LECTURE_SOCLE] and petit.systemes == [lecture.SYSTEME_LECTURE_DETAILS]
    assert faits["bien"] == ["velo"] and faits["fermeture"] == "cadenas"
    monkeypatch.delenv("COUVERTURE_MODELE_SOCLE", raising=False)
    assert llm.modele_du_socle() is None
    monkeypatch.setenv("MISTRAL_API_KEY", "cle-de-test")
    monkeypatch.setenv("COUVERTURE_MODELE_SOCLE", "mistral-large-latest")
    assert llm.modele_du_socle().modele == "mistral-large-latest"
    monkeypatch.setenv("COUVERTURE_MODELE", "mistral-large-latest")
    assert llm.modele_du_socle(llm.MistralLLM()) is None, "déjà le modèle de l'analyse"


def test_la_graine_du_tirage(monkeypatch):
    """7.123 : chaque appel à Mistral porte une graine fixe, pour que la même déclaration donne la même lecture."""
    from couverture import llm

    monkeypatch.setenv("MISTRAL_API_KEY", "cle-de-test")
    monkeypatch.delenv("COUVERTURE_GRAINE", raising=False)
    assert llm.MistralLLM(modele="mistral-small-latest").extra["random_seed"] == 0
    monkeypatch.setenv("COUVERTURE_GRAINE", "7")
    assert llm.MistralLLM(modele="mistral-small-latest").extra["random_seed"] == 7
    monkeypatch.setenv("COUVERTURE_GRAINE", "non")
    assert "random_seed" not in llm.MistralLLM(modele="mistral-small-latest").extra


def test_le_suivi_dit_chaque_etape_au_debut_puis_a_la_fin():
    """7.134 : `suivi` est appelé au début de chaque étape de la lecture, puis à sa fin avec ce qu'elle a donné."""
    import json

    from couverture import lecture

    class Modele:
        nom, accepte_schema = "suivi", True

        def completer(self, systeme, message, schema=None):
            if systeme == lecture.SYSTEME_LECTURE_SOCLE:
                return json.dumps({"faits": {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"]}})
            if systeme == lecture.SYSTEME_LECTURE_DETAILS:
                return json.dumps({"faits": {"fermeture": "cadenas", "absence": "oui"}})
            return json.dumps({"verdicts": {"fermeture": "dit", "absence": "non_dit"}})

    fil = []
    lecture.extraire_faits_regles("On m'a volé mon vélo dans ma cave fermée par un cadenas.", Modele(),
                                  suivi=lambda etape, detail=None: fil.append((etape, detail)))
    assert [e for e, _ in fil] == ["socle", "socle", "details", "details", "verification", "verification"]
    assert [d is None for _, d in fil] == [True, False] * 3
    assert fil[1][1] == "evenement : vol ; bien : velo ; lieu : cave"
    assert "fermeture : cadenas" in fil[3][1] and "absence" in fil[5][1] and "non dit" in fil[5][1]


def test_un_autre_modele_pour_verifier(monkeypatch):
    """7.136 : COUVERTURE_MODELE_VERIFICATION donne la vérification des faits à un autre modèle que celui qui lit."""
    import json

    from couverture import lecture, llm

    class Modele:
        accepte_schema = True

        def __init__(self, nom):
            self.nom, self.systemes = nom, []

        def completer(self, systeme, message, schema=None):
            self.systemes.append(systeme)
            if systeme == lecture.SYSTEME_LECTURE_SOCLE:
                return json.dumps({"faits": {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"]}})
            if systeme == lecture.SYSTEME_LECTURE_DETAILS:
                return json.dumps({"faits": {"fermeture": "cadenas"}})
            return json.dumps({"verdicts": {"fermeture": "dit"}})

    lecteur, verificateur = Modele("lecteur"), Modele("verificateur")
    lecture.extraire_faits_regles("On m'a volé mon vélo dans ma cave fermée par un cadenas.", lecteur,
                                  llm_verification=verificateur)
    assert verificateur.systemes == [lecture.SYSTEME_VERIFICATION] and lecture.SYSTEME_VERIFICATION not in lecteur.systemes
    monkeypatch.setenv("MISTRAL_API_KEY", "cle-de-test")
    monkeypatch.delenv("COUVERTURE_MODELE_VERIFICATION", raising=False)
    assert llm.modele_de_verification() is None
    monkeypatch.setenv("COUVERTURE_MODELE_VERIFICATION", "mistral-small-latest")
    assert llm.modele_de_verification().modele == "mistral-small-latest"


def test_role_de_la_regle_pour_une_garantie_dans_une_clause_typee_exclusion(clauses):
    """7.143 : la clause 4.4 est typée « exclusion » à l'ingestion. Citée mot pour mot par une règle comme la phrase
    d'une garantie, elle porte un « couvert » ; une définition seule ne le porte pas, et la justification ne dit
    alors plus « Couvert. »."""
    from couverture.models import ClauseRetenue, Verdict
    from couverture.validation import RETROGRADE, valider

    retenues = [ClauseRetenue(clause=c, score=0.0, raison="test") for c in clauses]
    extrait = "les vols commis dans les parties communes de l'immeuble, y compris dans un local à vélos collectif"

    def verdict(role):
        return Verdict.model_validate({"decision": "COUVERT", "justification": "Couvert. …", "confiance": 0.85, "mode": "fixe",
                                       "citations": [{"clause_id": "4.4", "extrait": extrait, "role": role}]})

    garde = valider(verdict("garantie"), retenues, roles_des_regles=True)
    assert garde.decision == Decision.COUVERT and garde.citations[0].role == "garantie"
    sans = valider(verdict("définition"), retenues, roles_des_regles=True)
    assert sans.decision == Decision.INCERTAIN and sans.justification.startswith(RETROGRADE) and sans.confiance <= 0.4
    # Quand c'est un modèle qui cite, le rôle vient toujours du contrat : la même citation ne porte pas un « couvert ».
    assert valider(verdict("garantie"), retenues).decision == Decision.INCERTAIN


def test_noms_du_modele_resout_un_alias(env_vide, monkeypatch):
    """« mistral-medium-latest » est un alias : `GET /models` dit quel modèle il désigne aujourd'hui (7.145)."""
    env_vide.setenv("MISTRAL_API_KEY", "secret")
    vues = []

    def faux_urlopen(requete, timeout):
        vues.append(requete.full_url)
        return _Reponse(json.dumps({"data": [
            {"id": "mistral-small-2603", "aliases": ["mistral-small-latest"]},
            {"id": "mistral-medium-3-5", "aliases": ["mistral-medium-latest", "mistral-medium-2604"]}]}).encode())

    monkeypatch.setattr(module_llm.urllib.request, "urlopen", faux_urlopen)
    llm = module_llm.MistralLLM("mistral-medium-latest")
    assert module_llm.noms_du_modele(llm) == ["mistral-medium-2604", "mistral-medium-3-5", "mistral-medium-latest"]
    assert vues == ["https://api.mistral.ai/v1/models"]
    assert module_llm.noms_du_modele(module_llm.MistralLLM("inconnu")) == []
    monkeypatch.setattr(module_llm.urllib.request, "urlopen", lambda r, timeout: (_ for _ in ()).throw(OSError("réseau")))
    assert module_llm.noms_du_modele(llm) == [], "sans réponse du fournisseur : pas d'erreur, pas de liste"
