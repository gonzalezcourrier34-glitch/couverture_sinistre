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
from couverture.pipeline import PipelineDocumentBrut
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


# --- Contrat réel (si le PDF est présent dans data/contrats) -------------------

PDF_ASSUREUR_A = DONNEES / "contrats" / "assureur_a_habitation_2025.pdf"


@pytest.mark.skipif(not PDF_ASSUREUR_A.exists(), reason="PDF Assureur A Habitation A absent de data/contrats")
def test_contrat_assureur_a_lu_et_exclusion_parties_communes_trouvee():
    clauses = segmenter_lignes(charger_lignes(PDF_ASSUREUR_A))
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


def resultat(decision="NON_COUVERT", evenement="vol", contrat="assureur-a", questions=()):
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
    manifeste["couverture-faits-regles"] = {**manifeste["couverture-faits-regles"], "empreinte": "0000000000000000"}
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
    assert ("alias", "couverture-faits-regles", "production") in m.appels
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
    banc = {"couches": {"chaine": {"metriques": {"exactitude": {"moyenne": 0.75, "min": 0.7}, "instables": 14, "note": "x"}}}}
    assert suivi.metriques_banc(banc) == {"chaine/exactitude": 0.75, "chaine/instables": 14.0}
    p = suivi.parametres_communs("mistral:mistral-small-latest")
    assert p["consigne/faits-regles"] == "v4" and p["modele/lecture"] == "mistral:mistral-small-latest"


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
    """« 3.1.6.1 Etendue de la garantie » (Assureur B) : le profil parle du titre sans son numéro."""
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
