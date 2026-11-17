"""Contrat compilé (méthode « fiches ») : compilation, contrôle, décision fiche par fiche, relecture, CLI.

Tout tourne hors ligne : un faux modèle répond selon la consigne qu'il reçoit."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from couverture import cli
from couverture.base import Base, Contrat
from couverture.chargement import charger_lignes
from couverture.compilation import (
    SYSTEME_COMPILATION,
    SYSTEME_EXCLUSIONS_GENERALES,
    a_refaire,
    compiler,
    pour_compiler,
    reparer_compilation,
    unites,
    verifier_import,
)
from couverture.llm import ReponseLente
from couverture.consignes import archiver
from couverture.fiches import SYSTEME_FICHES, SYSTEME_ROUTAGE, JugeFiches, PipelineFiches, decider_fiches
from couverture.models import Clause, Condition, Decision, EtatCondition, Fiche, TypeClause
from couverture.relecture import SYSTEME_RELECTURE
from couverture.segmentation import segmenter_lignes

CG_FICTIF = Path(__file__).resolve().parents[1] / "data" / "contrats" / "fictif_habitat_serein.md"

FICHE_VELO = {"fiches": [{
    "nom": "Vol de vélo", "clause_id": "4.3", "evenements": ["vol"], "objet": "Vol des vélos au logement ou en dépendance.",
    "conditions": [
        {"enonce": "Le bien volé est-il un vélo ?", "clause_id": "4.3", "extrait": "Les vélos, y compris à assistance électrique"},
        {"enonce": "Le vélo se trouvait-il dans les locaux d'habitation ou une dépendance ?", "clause_id": "4.3",
         "extrait": "lorsqu'ils se trouvent dans les locaux d'habitation ou dans une dépendance"},
    ],
    "exclusions": [
        {"enonce": "Le vol a-t-il été commis dans les parties communes ?", "clause_id": "4.4",
         "extrait": "les vols commis dans les parties communes de l'immeuble, y compris dans un local à vélos collectif",
         "a_demander": True},
        {"enonce": "Le vol a-t-il été commis par un membre de la famille ?", "clause_id": "4.4",
         "extrait": "les vols commis par les membres de la famille de l'assuré", "a_demander": False},
    ],
    "limites": [{"enonce": "Franchise", "clause_id": "4.4", "extrait": "phrase inventée qui n'existe pas"}],
}]}

FICHE_INCENDIE = {"fiches": [{
    "nom": "Incendie", "clause_id": "2.1", "evenements": ["incendie"], "objet": "Dommages causés par l'incendie.",
    "conditions": [{"enonce": "L'événement est-il un incendie au sens du contrat ?", "clause_id": "1.5",
                    "extrait": "Combustion avec flammes en dehors d'un foyer normal"}],
    "exclusions": [],
}]}

GENERALES = {"exclusions": [
    {"enonce": "Le dommage est-il intentionnel ?", "clause_id": "8.1",
     "extrait": "les dommages causés ou provoqués intentionnellement par l'assuré", "a_demander": False},
    {"enonce": "Résulte-t-il d'un défaut d'entretien ?", "clause_id": "8.1",
     "extrait": "les dommages résultant d'un défaut d'entretien caractérisé", "a_demander": True},
]}


class ScriptLLM:
    """Répond selon la consigne ; `reponses_fiches(questions)` fabrique les réponses aux questions."""

    nom = "script"

    def __init__(self, reponses_fiches=None, relectures=None):
        self.reponses_fiches = reponses_fiches or (lambda qs: {})
        self.relectures = relectures
        self.relues: list[dict] = []
        self.appels: list[str] = []

    def completer(self, systeme, message):
        if systeme == SYSTEME_COMPILATION:
            self.appels.append("compilation")
            if "Garantie 4.3" in message:
                return json.dumps(FICHE_VELO)
            if "Garantie 2.1 " in message:
                return json.dumps(FICHE_INCENDIE)
            return json.dumps({"fiches": []})
        if systeme == SYSTEME_EXCLUSIONS_GENERALES:
            self.appels.append("generales")
            return json.dumps(GENERALES)
        if systeme == SYSTEME_FICHES:
            self.appels.append("fiches")
            questions = json.loads(message.split("## Questions\n", 1)[1])
            etats = self.reponses_fiches(questions)
            return json.dumps({"reponses": [{"id": q["id"], "etat": etats.get(q["question"], "INCONNUE"),
                                             "justification": "…", "question": "?"} for q in questions],
                               "resume": "Résumé."})
        if systeme == SYSTEME_RELECTURE:
            self.appels.append("relecture")
            lignes = json.loads(message.split("## Lignes à contrôler\n", 1)[1])
            self.relues.extend(lignes)
            avis = self.relectures or (lambda l: "confirmee")
            return json.dumps({"relectures": [{"id": l["id"], "avis": avis(l), "raison": "…"} for l in lignes]})
        if systeme == SYSTEME_ROUTAGE:
            return json.dumps({"fiches": ["4.3"]})
        raise AssertionError("consigne inattendue")


@pytest.fixture(scope="module")
def clauses():
    return segmenter_lignes(charger_lignes(CG_FICTIF))


@pytest.fixture(scope="module")
def compile_(clauses):
    return compiler("fictif", "abc", clauses, ScriptLLM(), paralleles=2)


def velo_local_commun(questions):
    return {"Le bien volé est-il un vélo ?": "REMPLIE",
            "Le vélo se trouvait-il dans les locaux d'habitation ou une dépendance ?": "NON_REMPLIE",
            "Le vol a-t-il été commis dans les parties communes ?": "REMPLIE"}


# --- Compilation ------------------------------------------------------------------------------

def test_unites_section_et_sous_sections(clauses):
    u = dict(unites(clauses))
    assert set(u) == {"2.1", "3.1", "4.1", "4.2", "4.3", "5.1", "6.1", "7.1"}
    ids = {c.id for c in u["4.3"]}
    assert {"4.3", "4.4", "4.5"} <= ids, "exclusions rangées en fin de section"
    assert "8.1" not in ids, "les exclusions générales sont compilées à part"
    assert "1.6" in ids, "définition d'un terme employé (parties communes)"

    def c(id_, type_, groupe):
        return Clause(id=id_, article=id_, titre="Exclusions" if "-" in id_ else id_, chemin=[id_], texte="texte",
                      type=type_, groupe=groupe)

    style_foyer = [c("2.1", TypeClause.GARANTIE, "2"), c("2.10", TypeClause.GARANTIE, "2"),
                   c("2.10-a", TypeClause.EXCLUSION, "2.10"), c("2.13~1", TypeClause.CONDITION, "2"),
                   c("2.14~1", TypeClause.GARANTIE, "2"), c("2.14~2", TypeClause.GARANTIE, "2")]
    u = dict(unites(style_foyer))
    assert set(u) == {"2.1", "2.10", "2.14"}, "les morceaux d'une même garantie sont réunis"
    assert [x.id for x in u["2.10"]] == ["2.10", "2.10-a"]
    assert [x.id for x in u["2.1"]] == ["2.1"], "pas l'assistance de la section : le contrat a des sous-sections"


def test_compilation_verifie_chaque_extrait(compile_):
    velo = next(f for f in compile_.fiches if f.id == "4.3")
    assert all(p.valide for p in velo.conditions + velo.exclusions)
    assert not velo.limites[0].valide, "extrait inventé : écarté"
    assert any("4.3" in a and "extrait introuvable" in a for a in compile_.avertissements)
    assert len(compile_.exclusions_generales) == 2 and not compile_.exclusions_generales[0].a_demander
    assert compile_.consigne == "v1" and compile_.empreinte == "abc:v1"


def test_compilation_stockee_et_perimee(tmp_path, clauses, compile_):
    base = Base(tmp_path / "b.sqlite")
    base.enregistrer(Contrat(id="fictif", empreinte="abc"), clauses, "")
    base.enregistrer_compilation(compile_)
    assert base.compilation("fictif").fiches[0].nom
    base.enregistrer(Contrat(id="fictif", empreinte="nouveau"), clauses, "")  # contrat modifié
    assert base.compilation("fictif") is None, "compilation d'une autre version du contrat : ignorée"
    assert base.compilation("fictif", a_jour=False) is not None, "mais gardée pour la relecture"


def test_import_refuse_les_citations_inventees(clauses, compile_):
    copie = compile_.model_copy(deep=True)
    velo = next(f for f in copie.fiches if f.id == "4.3")
    velo.conditions[0].enonce = "Question reformulée par un humain ?"
    velo.conditions[1].extrait = "texte qui n'est pas dans le contrat"
    problemes = verifier_import(copie, clauses)
    assert len(problemes) == 2  # la citation modifiée et la limite déjà fausse
    assert velo.conditions[0].valide and not velo.conditions[1].valide


def test_reprise_ne_refait_que_les_echecs(clauses):
    class Lent(ScriptLLM):
        def __init__(self, lentes):
            super().__init__()
            self.lentes = lentes

        def completer(self, systeme, message):
            if systeme == SYSTEME_COMPILATION and any(f"Garantie {g} " in message for g in self.lentes):
                self.appels.append("lente")
                raise ReponseLente("pas de réponse après 300 s")
            return super().completer(systeme, message)

    premiere = compiler("fictif", "abc", clauses, Lent({"4.3"}), paralleles=1)
    assert premiere.echecs == ["4.3"] and not any(f.id == "4.3" for f in premiere.fiches)
    assert any(f.id == "2.1" for f in premiere.fiches)

    llm = Lent(set())
    vues = []
    seconde = compiler("fictif", "abc", clauses, llm, existante=premiere, progression=vues.append)
    assert llm.appels == ["compilation"], "seule la garantie en échec est refaite ; les générales sont gardées"
    assert seconde.echecs == [] and {"2.1", "4.3"} <= {f.id for f in seconde.fiches}
    assert not any("4.3 non compilée" in a for a in seconde.avertissements)
    assert any("4.3" in v and "fiche" in v for v in vues)

    # Compilation faite avant le champ `echecs` : l'échec se lit dans les avertissements.
    ancienne = premiere.model_copy(update={"echecs": []})
    assert a_refaire(ancienne, unites(clauses)) == {"4.3"}


def test_citation_rattachee_a_la_bonne_clause(clauses):
    class MauvaisNumero(ScriptLLM):
        def completer(self, systeme, message):
            if systeme == SYSTEME_COMPILATION and "Garantie 2.1 " in message:
                fiche = json.loads(json.dumps(FICHE_INCENDIE))
                fiche["fiches"][0]["conditions"][0]["clause_id"] = "2.1"  # la définition, citée sous 2.1
                return json.dumps(fiche)
            return super().completer(systeme, message)

    c = compiler("fictif", "abc", clauses, MauvaisNumero(), paralleles=1)
    incendie = next(f for f in c.fiches if f.id == "2.1")
    assert incendie.conditions[0].valide and incendie.conditions[0].clause_id == "1.5"


def test_citation_avec_mots_sautes_recalee_sur_le_texte_exact(clauses):
    from couverture.validation import passage_exact
    texte = ("Il y a effraction lorsque l'accès (porte, fenêtre, chambranle, châssis) a été endommagé ou le "
             "mécanisme de fermeture (serrure, quincaillerie) a été forcé.")
    assert passage_exact("l'accès a été endommagé ou le mécanisme de fermeture a été forcé", texte) == (
        "l'accès (porte, fenêtre, chambranle, châssis) a été endommagé ou le mécanisme de fermeture "
        "(serrure, quincaillerie) a été forcé")
    assert passage_exact("le vol de bijoux dans la cave", texte) is None, "mots absents : refusé"
    assert passage_exact("accès endommagé", texte) is None, "trop court pour être sûr"

    # Sur une compilation existante, sans appel au modèle.
    c = compiler("fictif", "abc", clauses, ScriptLLM(), paralleles=1)
    velo = next(f for f in c.fiches if f.id == "4.3")
    velo.conditions[1].extrait, velo.conditions[1].valide = "lorsqu'ils se trouvent dans les locaux d'habitation", False
    velo.conditions[0].extrait, velo.conditions[0].valide = "Les vélos garantis contre le vol", False
    velo.conditions[0].extrait = "vélos y compris à électrique sont garantis contre le vol"  # « assistance » sauté
    assert reparer_compilation(c, clauses) >= 1
    assert velo.conditions[0].valide and velo.conditions[0].extrait.startswith("vélos, y compris à assistance électrique")


def test_compilation_laisse_du_temps_au_modele():
    from couverture.llm import OpenAICompatibleLLM
    llm = OpenAICompatibleLLM("m", "http://x", max_tokens=8000, timeout=120, extra={"top_p": 1})
    copie = pour_compiler(llm)
    assert (copie.max_tokens, copie.timeout) == (16000, 300)
    assert (llm.max_tokens, llm.timeout) == (8000, 120), "l'analyse garde ses réglages"


# --- Décision ------------------------------------------------------------------------------------

def test_velo_local_commun_non_couvert(clauses, compile_):
    llm = ScriptLLM(velo_local_commun)
    r = PipelineFiches(compile_, clauses, llm).analyser("On m'a volé mon vélo dans le local commun de l'immeuble.")
    v = r.verdict
    assert v.decision == Decision.NON_COUVERT
    decisives = [c for c in v.conditions if c.decisive]
    assert any("parties communes" in c.enonce for c in decisives)
    assert all(c.valide for c in v.citations) and v.citations, "les citations viennent des fiches"
    famille = next(c for c in v.conditions if "famille" in c.enonce)
    assert famille.etat == EtatCondition.NON_REMPLIE and famille.justification.startswith("Présumée absente")
    entretien = next(c for c in v.conditions if "entretien" in c.enonce)
    assert entretien.etat == EtatCondition.INCONNUE, "exclusion à demander : reste inconnue"
    assert llm.appels == ["fiches"], "routage par les faits : un seul appel"


def _cond(nature, etat, groupe="G"):
    return Condition(nature=nature, groupe=groupe, clause_id="x", extrait="e", enonce=f"{nature} {etat}",
                     etat=EtatCondition(etat))


def test_une_exclusion_ne_fait_pas_tomber_une_autre_garantie():
    vol = Fiche(id="a", nom="Vol", clause_id="a")
    incendie = Fiche(id="b", nom="Incendie", clause_id="b")
    decision, motif, _, _ = decider_fiches([
        (vol, [_cond("garantie", "REMPLIE", "Vol"), _cond("exclusion", "REMPLIE")]),
        (incendie, [_cond("garantie", "REMPLIE", "Incendie"), _cond("exclusion", "NON_REMPLIE")]),
    ])
    assert decision == Decision.COUVERT and "Incendie" in motif


def test_toutes_les_fiches_refusent():
    a, b = Fiche(id="a", nom="Vol", clause_id="a"), Fiche(id="b", nom="Bris", clause_id="b")
    decision, motif, _, _ = decider_fiches([(a, [_cond("garantie", "NON_REMPLIE", "Vol")]),
                                            (b, [_cond("garantie", "NON_REMPLIE", "Bris")])])
    assert decision == Decision.NON_COUVERT and "« Vol »" in motif and "« Bris »" in motif


def test_relecture_ignore_les_presumees_et_peut_rendre_prudent(clauses, compile_):
    couvert = lambda qs: {"Le bien volé est-il un vélo ?": "REMPLIE",  # noqa: E731
                          "Le vélo se trouvait-il dans les locaux d'habitation ou une dépendance ?": "REMPLIE",
                          "Le vol a-t-il été commis dans les parties communes ?": "NON_REMPLIE",
                          "Résulte-t-il d'un défaut d'entretien ?": "NON_REMPLIE"}
    llm = ScriptLLM(couvert)
    r = PipelineFiches(compile_, clauses, llm, relecteur=llm).analyser("Mon vélo a été volé chez moi, porte fracturée.")
    assert r.verdict.decision == Decision.COUVERT
    relues = {l["question"] for l in llm.relues}
    assert "Le vol a-t-il été commis dans les parties communes ?" in relues
    assert not any("famille" in q or "intentionnel" in q for q in relues), "présumées absentes : pas relues"

    conteste = ScriptLLM(couvert, relectures=lambda l: "contestee" if "parties communes" in l["question"] else "confirmee")
    r = PipelineFiches(compile_, clauses, conteste, relecteur=conteste).analyser("Mon vélo a été volé chez moi.")
    assert r.verdict.decision == Decision.INCERTAIN and r.verdict.decision_avant_relecture == Decision.COUVERT


def test_routage_par_le_modele_si_evenement_inconnu(clauses, compile_):
    llm = ScriptLLM(velo_local_commun)
    r = PipelineFiches(compile_, clauses, llm).analyser("Mon vélo n'est plus là où je l'avais rangé.")
    assert r.verdict.decision == Decision.NON_COUVERT
    assert "choisies par le modèle" in r.verdict.avertissements[0]


def test_aucune_fiche_pour_l_evenement(clauses, compile_):
    juge = JugeFiches(ScriptLLM(), compile_, clauses)
    v = juge.juger("Un météorite est tombé.", [])
    assert v.decision == Decision.INCERTAIN


# --- Ligne de commande ---------------------------------------------------------------------------

def test_cli_compiler_relire_analyser(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("COUVERTURE_RELECTURE", "non")
    llm = ScriptLLM(velo_local_commun)
    monkeypatch.setattr(cli, "llm_configure", lambda: llm)
    d = tmp_path / "donnees"
    (d / "contrats").mkdir(parents=True)
    (d / "contrats" / "fictif.md").write_text(CG_FICTIF.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr("couverture.llm.configurer_embeddings", lambda: None)
    assert cli.main(["--donnees", str(d), "ingerer"]) == 0
    assert cli.main(["--donnees", str(d), "compiler"]) == 0
    assert "fictif" in capsys.readouterr().out
    nb = len(llm.appels)
    assert cli.main(["--donnees", str(d), "compiler"]) == 0
    assert len(llm.appels) == nb and "déjà compilé" in capsys.readouterr().out, "pas de recompilation inutile"

    f = tmp_path / "fiches.json"
    assert cli.main(["--donnees", str(d), "fiches", "--contrat", "fictif", "--exporter", str(f)]) == 0
    donnees = json.loads(f.read_text(encoding="utf-8"))
    for fiche in donnees["fiches"]:
        fiche["limites"] = []  # le relecteur retire la limite à la citation inventée
    f.write_text(json.dumps(donnees, ensure_ascii=False), encoding="utf-8")
    assert cli.main(["--donnees", str(d), "fiches", "--contrat", "fictif", "--importer", str(f), "--relu-par", "SG"]) == 0
    assert cli.main(["--donnees", str(d), "fiches", "--contrat", "fictif"]) == 0
    assert "relu par SG" in capsys.readouterr().out

    assert cli.main(["--donnees", str(d), "analyser", "--contrat", "fictif", "--methode", "fiches",
                     "Mon vélo a été volé dans le local commun."]) == 0
    sortie = capsys.readouterr().out
    assert "NON_COUVERT" in sortie and "présumée(s) absente(s)" in sortie


def test_archive_des_consignes(tmp_path):
    ecrites = archiver(tmp_path)
    assert any(e.endswith("grille-conditions/v3.txt") for e in ecrites)
    assert archiver(tmp_path) == [], "une version archivée n'est jamais réécrite"
    archive_v1 = Path(__file__).resolve().parents[1] / "docs" / "consignes" / "grille-conditions" / "v1.txt"
    assert archive_v1.exists(), "l'histoire des consignes est gardée"
