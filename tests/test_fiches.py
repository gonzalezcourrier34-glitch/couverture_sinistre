"""Contrat compilé (méthode « fiches ») : compilation, contrôle, décision par rôles, relecture, CLI.

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
from couverture.consignes import archiver
from couverture.fiches import (
    SYSTEME_FAITS,
    SYSTEME_FICHES,
    SYSTEME_ROUTAGE,
    JugeFiches,
    PipelineFiches,
    decider_fiche,
    decider_fiches,
)
from couverture.llm import ReponseLente
from couverture.models import Condition, Decision, EtatCondition, Fiche
from couverture.relecture import SYSTEME_RELECTURE
from couverture.segmentation import segmenter_lignes

CG_FICTIF = Path(__file__).resolve().parents[1] / "data" / "contrats" / "fictif_habitat_serein.md"

Q_VOL = "L'événement est-il un vol ?"
Q_VELO = "Le bien volé est-il un vélo ?"
Q_LIEU = "Le vélo se trouvait-il dans les locaux d'habitation ou une dépendance ?"
Q_COMMUNES = "Le vol a-t-il été commis dans les parties communes ?"
Q_FAMILLE = "Le vol a-t-il été commis par un membre de la famille ?"
Q_PREVENTION = "Les mesures de prévention ont-elles été respectées ?"

FICHE_VELO = {"fiches": [{
    "nom": "Vol de vélo", "clause_id": "4.3", "evenements": ["vol"], "objet": "Vol des vélos au logement ou en dépendance.",
    "perimetre": [
        {"role": "evenement", "enonce": Q_VOL, "clause_id": "4.3", "extrait": "sont garantis contre le vol"},
        {"role": "bien", "enonce": Q_VELO, "clause_id": "4.3", "extrait": "Les vélos, y compris à assistance électrique"},
        {"role": "lieu", "enonce": Q_LIEU, "clause_id": "4.3",
         "extrait": "lorsqu'ils se trouvent dans les locaux d'habitation ou dans une dépendance"},
    ],
    "circonstances": [],
    "obligations": [{"enonce": Q_PREVENTION, "clause_id": "4.5", "extrait": "l'assuré doit fermer à clé toutes les portes d'accès", "lien_causal": True}],
    "exclusions": [
        {"enonce": Q_COMMUNES, "clause_id": "4.4",
         "extrait": "les vols commis dans les parties communes de l'immeuble, y compris dans un local à vélos collectif",
         "a_demander": True},
        {"enonce": Q_FAMILLE, "clause_id": "4.4",
         "extrait": "les vols commis par les membres de la famille de l'assuré", "a_demander": False},
    ],
    "limites": [{"enonce": "Franchise", "clause_id": "4.4", "extrait": "phrase inventée qui n'existe pas"}],
}]}

FICHE_INCENDIE = {"fiches": [{
    "nom": "Incendie", "clause_id": "2.1", "evenements": ["incendie"], "objet": "Dommages causés par l'incendie.",
    "perimetre": [{"role": "evenement", "enonce": "L'événement est-il un incendie au sens du contrat ?", "clause_id": "1.5",
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
    """Répond selon la consigne ; `etats` donne la réponse à chaque question (INCONNUE par défaut)."""

    nom = "script"

    def __init__(self, etats=None, relectures=None, evenements=("vol",)):
        self.etats = etats or {}
        self.relectures = relectures
        self.evenements = list(evenements)
        self.relues: list[dict] = []
        self.appels: list[str] = []
        self.roles: dict[str, str] = {}

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
        if systeme == SYSTEME_FAITS:
            self.appels.append("faits")
            return json.dumps({"evenements": self.evenements, "bien": "vélo", "lieu": ""})
        if systeme == SYSTEME_FICHES:
            self.appels.append("fiches")
            questions = json.loads(message.split("## Questions\n", 1)[1])
            self.roles.update({q["question"]: q["role"] for q in questions})
            return json.dumps({"reponses": [{"id": q["id"], "etat": self.etats.get(q["question"], "INCONNUE"),
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


LOCAL_COMMUN = {Q_VOL: "REMPLIE", Q_VELO: "REMPLIE", Q_LIEU: "REMPLIE", Q_COMMUNES: "REMPLIE"}
CHEZ_MOI = {Q_VOL: "REMPLIE", Q_VELO: "REMPLIE", Q_LIEU: "REMPLIE", Q_COMMUNES: "NON_REMPLIE",
            "Résulte-t-il d'un défaut d'entretien ?": "NON_REMPLIE", Q_PREVENTION: "REMPLIE"}


def _c(nature, etat, role="", groupe="G", **kw):
    return Condition(nature=nature, role=role, groupe=groupe, clause_id="x", extrait="e",
                     enonce=f"{nature} {role} {etat}", etat=EtatCondition(etat), **kw)


def fiche(nom="G"):
    return Fiche(id=nom, nom=nom, clause_id="x")


# --- Compilation ------------------------------------------------------------------------------

def test_unites_section_et_sous_sections(clauses):
    from couverture.models import Clause, TypeClause

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


def test_compilation_range_les_questions_par_role(compile_):
    velo = next(f for f in compile_.fiches if f.id == "4.3")
    assert [p.role for p in velo.conditions] == ["evenement", "bien", "lieu"]
    assert all(p.valide for p in velo.conditions + velo.exclusions + velo.obligations)
    assert velo.obligations[0].nature == "obligation" and velo.obligations[0].lien_causal
    assert not velo.limites[0].valide, "extrait inventé : écarté"
    assert any("4.3" in a and "extrait introuvable" in a for a in compile_.avertissements)
    assert len(compile_.exclusions_generales) == 2 and not compile_.exclusions_generales[0].a_demander
    assert compile_.consigne == "v2" and compile_.empreinte == "abc:v2"


def test_compilation_stockee_et_perimee(tmp_path, clauses, compile_):
    base = Base(tmp_path / "b.sqlite")
    base.enregistrer(Contrat(id="fictif", empreinte="abc"), clauses, "")
    base.enregistrer_compilation(compile_)
    assert base.compilation("fictif").fiches[0].nom
    base.enregistrer(Contrat(id="fictif", empreinte="nouveau"), clauses, "")  # contrat modifié
    assert base.compilation("fictif") is None, "compilation d'une autre version du contrat : ignorée"
    assert base.compilation("fictif", a_jour=False) is not None, "mais gardée pour la relecture"


def test_compilation_d_une_ancienne_consigne_refusee(tmp_path, clauses, compile_):
    base = Base(tmp_path / "b.sqlite")
    base.enregistrer(Contrat(id="fictif", empreinte="abc"), clauses, "")
    base.enregistrer_compilation(compile_.model_copy(update={"consigne": "v1", "empreinte": "abc:v1"}))
    with pytest.raises(LookupError, match="consigne v1"):
        PipelineFiches.depuis_base(base, "fictif", ScriptLLM())


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

    llm = Lent(set())
    vues = []
    seconde = compiler("fictif", "abc", clauses, llm, existante=premiere, progression=vues.append)
    assert llm.appels == ["compilation"], "seule la garantie en échec est refaite ; les générales sont gardées"
    assert seconde.echecs == [] and {"2.1", "4.3"} <= {f.id for f in seconde.fiches}
    assert any("4.3" in v and "fiche" in v for v in vues)
    assert a_refaire(premiere.model_copy(update={"echecs": []}), unites(clauses)) == {"4.3"}, \
        "compilation antérieure au champ `echecs` : l'échec se lit dans les avertissements"


def test_citations_reparees(clauses):
    from couverture.validation import passage_exact

    texte = ("Il y a effraction lorsque l'accès (porte, fenêtre, chambranle, châssis) a été endommagé ou le "
             "mécanisme de fermeture (serrure, quincaillerie) a été forcé.")
    assert passage_exact("l'accès a été endommagé ou le mécanisme de fermeture a été forcé", texte) == (
        "l'accès (porte, fenêtre, chambranle, châssis) a été endommagé ou le mécanisme de fermeture "
        "(serrure, quincaillerie) a été forcé")
    assert passage_exact("le vol de bijoux dans la cave", texte) is None, "mots absents : refusé"
    assert passage_exact("accès endommagé", texte) is None, "trop court pour être sûr"

    class MauvaisNumero(ScriptLLM):
        def completer(self, systeme, message):
            if systeme == SYSTEME_COMPILATION and "Garantie 2.1 " in message:
                f = json.loads(json.dumps(FICHE_INCENDIE))
                f["fiches"][0]["perimetre"][0]["clause_id"] = "2.1"  # la définition, citée sous 2.1
                return json.dumps(f)
            return super().completer(systeme, message)

    c = compiler("fictif", "abc", clauses, MauvaisNumero(), paralleles=1)
    incendie = next(f for f in c.fiches if f.id == "2.1")
    assert incendie.conditions[0].valide and incendie.conditions[0].clause_id == "1.5"

    velo = next(f for f in c.fiches if f.id == "4.3")
    velo.conditions[1].extrait, velo.conditions[1].valide = "vélos y compris à électrique sont garantis contre le vol", False
    assert reparer_compilation(c, clauses) >= 1
    assert velo.conditions[1].valide and velo.conditions[1].extrait.startswith("vélos, y compris à assistance électrique")


def test_compilation_laisse_du_temps_au_modele():
    from couverture.llm import OpenAICompatibleLLM

    llm = OpenAICompatibleLLM("m", "http://x", max_tokens=8000, timeout=120, extra={"top_p": 1})
    copie = pour_compiler(llm)
    assert (copie.max_tokens, copie.timeout) == (16000, 300)
    assert (llm.max_tokens, llm.timeout) == (8000, 120), "l'analyse garde ses réglages"


# --- Décision par rôles ---------------------------------------------------------------------------

def test_perimetre_contraire_hors_de_la_fiche():
    rattachement, decision, motif, _, _ = decider_fiche([
        _c("garantie", "REMPLIE", "evenement"), _c("garantie", "NON_REMPLIE", "lieu"), _c("exclusion", "REMPLIE")])
    assert (rattachement, decision) == ("hors périmètre", Decision.NON_COUVERT) and "périmètre" in motif


def test_exclusion_seulement_pour_une_garantie_rattachee():
    perimetre_inconnu = [_c("garantie", "REMPLIE", "evenement"), _c("garantie", "INCONNUE", "lieu"),
                         _c("exclusion", "REMPLIE")]
    rattachement, decision, _, demander, _ = decider_fiche(perimetre_inconnu)
    assert (rattachement, decision) == ("possible", Decision.INCERTAIN) and demander, "on demande le lieu, pas l'exclusion"
    rattachement, decision, motif, _, _ = decider_fiche([
        _c("garantie", "REMPLIE", "evenement"), _c("garantie", "REMPLIE", "lieu"), _c("exclusion", "REMPLIE")])
    assert decision == Decision.NON_COUVERT and "exclusion" in motif


def test_charge_de_la_preuve():
    """L'assuré établit les conditions de la garantie ; l'assureur, l'exclusion. Une exclusion dont
    rien n'indique qu'elle joue ne bloque pas : elle devient une réserve."""
    base = [_c("garantie", "REMPLIE", "evenement"), _c("garantie", "REMPLIE", "bien")]
    _, decision, motif, demander, confiance = decider_fiche(base + [_c("exclusion", "INCONNUE", question="Vice connu ?")])
    assert decision == Decision.COUVERT and "sous réserve" in motif and demander == ["Vice connu ?"] and confiance == 0.7


def test_un_appel_qui_echoue_n_efface_que_sa_fiche(clauses, compile_):
    class GeneralesMuettes(ScriptLLM):
        def completer(self, systeme, message):
            if systeme == SYSTEME_FICHES and "intentionnel" in message:
                raise ValueError("réponse illisible")
            return super().completer(systeme, message)

    r = PipelineFiches(compile_, clauses, GeneralesMuettes(LOCAL_COMMUN)).analyser("Vélo volé dans le local commun.")
    assert r.verdict.decision == Decision.NON_COUVERT
    assert any("Exclusions générales" in a for a in r.verdict.avertissements)


def test_routage_garde_les_evenements_du_lexique(clauses, compile_):
    from couverture.fiches import extraire_faits_modele

    faits = extraire_faits_modele("J'ai laissé une bougie sur la table du jardin, elle a fondu.",
                                  ScriptLLM(evenements=["dommage_accidentel"]))
    assert "incendie" in faits.evenements and "dommage_accidentel" in faits.evenements


def test_circonstances_et_obligations():
    base = [_c("garantie", "REMPLIE", "evenement"), _c("garantie", "REMPLIE", "bien")]
    assert decider_fiche(base + [_c("garantie", "NON_REMPLIE", "circonstance")])[1] == Decision.NON_COUVERT
    assert decider_fiche(base + [_c("garantie", "INCONNUE", "circonstance")])[1] == Decision.INCERTAIN
    # Obligation non respectée : déchéance seulement s'il y a un lien causal → à apprécier.
    _, decision, motif, demander, _ = decider_fiche(base + [_c("obligation", "NON_REMPLIE")])
    assert decision == Decision.INCERTAIN and "lien causal" in motif and demander
    assert decider_fiche(base + [_c("obligation", "NON_REMPLIE", lien_causal=False)])[1] == Decision.NON_COUVERT
    # Obligation inconnue : couvert, avec la question et une confiance plafonnée.
    _, decision, _, demander, confiance = decider_fiche(base + [_c("obligation", "INCONNUE")])
    assert decision == Decision.COUVERT and demander and confiance == 0.7


def test_une_exclusion_ne_fait_pas_tomber_une_autre_garantie():
    decision, motif, _, _ = decider_fiches([
        (fiche("Vol"), [_c("garantie", "REMPLIE", "evenement"), _c("exclusion", "REMPLIE")]),
        (fiche("Incendie"), [_c("garantie", "REMPLIE", "evenement"), _c("exclusion", "NON_REMPLIE")]),
    ])
    assert decision == Decision.COUVERT and "Incendie" in motif


def test_velo_local_commun_les_autres_vols_hors_perimetre():
    """Le cas de la consigne : une fiche rattachée refuse ; « vol sur la personne » est hors de son
    périmètre (autre lieu) ; « vol chez le réparateur » aussi."""
    contenu = [_c("garantie", "REMPLIE", "evenement"), _c("garantie", "REMPLIE", "bien"),
               _c("garantie", "REMPLIE", "lieu"), _c("exclusion", "REMPLIE"), _c("obligation", "INCONNUE")]
    personne = [_c("garantie", "REMPLIE", "evenement"), _c("garantie", "NON_REMPLIE", "lieu"),
                _c("garantie", "INCONNUE", "circonstance")]
    decision, motif, demander, _ = decider_fiches([(fiche("Vol du contenu"), contenu), (fiche("Vol sur la personne"), personne)])
    assert decision == Decision.NON_COUVERT and not demander
    assert "exclusion" in motif and "personne" not in motif, "seules les fiches rattachées expliquent le refus"


def test_refus_avec_une_autre_garantie_possible_le_dit():
    """Risque de refus à tort : une autre garantie reste possible. On refuse, mais on pose la question
    et la confiance baisse."""
    contenu = [_c("garantie", "REMPLIE", "evenement"), _c("garantie", "REMPLIE", "lieu"), _c("exclusion", "REMPLIE")]
    personne = [_c("garantie", "REMPLIE", "evenement"), _c("garantie", "INCONNUE", "lieu", question="Où étiez-vous ?")]
    decision, _, demander, confiance = decider_fiches([(fiche("Contenu"), contenu), (fiche("Personne"), personne)])
    assert decision == Decision.NON_COUVERT and "Où étiez-vous ?" in demander and confiance <= 0.6


def test_aucune_garantie_ne_s_applique():
    decision, motif, _, _ = decider_fiches([
        (fiche("Incendie"), [_c("garantie", "NON_REMPLIE", "evenement")]),
        (fiche("Transport"), [_c("garantie", "REMPLIE", "evenement"), _c("garantie", "NON_REMPLIE", "lieu")]),
    ])
    assert decision == Decision.NON_COUVERT and "aucune garantie ne s'applique" in motif
    assert decider_fiches([])[0] == Decision.INCERTAIN


# --- De bout en bout ------------------------------------------------------------------------------

def test_velo_local_commun_non_couvert(clauses, compile_):
    llm = ScriptLLM(LOCAL_COMMUN)
    r = PipelineFiches(compile_, clauses, llm).analyser("On m'a volé mon vélo dans le local commun de l'immeuble.")
    v = r.verdict
    assert v.decision == Decision.NON_COUVERT
    assert [c.enonce for c in v.conditions if c.decisive] == [Q_COMMUNES]
    assert all(c.valide for c in v.citations) and v.citations, "les citations viennent des fiches"
    famille = next(c for c in v.conditions if c.enonce == Q_FAMILLE)
    assert famille.etat == EtatCondition.NON_REMPLIE and famille.justification.startswith("Présumée absente")
    assert llm.appels == ["faits", "fiches", "fiches"], "faits, puis un appel par fiche et un pour les exclusions générales"
    assert llm.roles[Q_LIEU] == "lieu" and llm.roles[Q_PREVENTION] == "obligation", "le modèle voit le rôle"


def test_relecture_ignore_les_presumees_et_peut_rendre_prudent(clauses, compile_):
    llm = ScriptLLM(CHEZ_MOI)
    r = PipelineFiches(compile_, clauses, llm, relecteur=llm).analyser("Mon vélo a été volé chez moi, porte fracturée.")
    assert r.verdict.decision == Decision.COUVERT
    relues = {l["question"] for l in llm.relues}
    assert Q_COMMUNES in relues
    assert not any("famille" in q or "intentionnel" in q for q in relues), "présumées absentes : pas relues"

    # Une exclusion contestée devient une réserve (c'est à l'assureur de la prouver) : toujours couvert.
    conteste = ScriptLLM(CHEZ_MOI, relectures=lambda l: "contestee" if "parties communes" in l["question"] else "confirmee")
    r = PipelineFiches(compile_, clauses, conteste, relecteur=conteste).analyser("Mon vélo a été volé chez moi.")
    assert r.verdict.decision == Decision.COUVERT and r.verdict.confiance == 0.7 and r.verdict.informations_manquantes
    # Un lieu contesté (c'est à l'assuré de l'établir) rend la réponse incertaine.
    conteste = ScriptLLM(CHEZ_MOI, relectures=lambda l: "contestee" if l["question"] == Q_LIEU else "confirmee")
    r = PipelineFiches(compile_, clauses, conteste, relecteur=conteste).analyser("Mon vélo a été volé chez moi.")
    assert r.verdict.decision == Decision.INCERTAIN and r.verdict.decision_avant_relecture == Decision.COUVERT


def test_routage_par_le_modele_si_evenement_inconnu(clauses, compile_):
    llm = ScriptLLM(LOCAL_COMMUN, evenements=["autre"])
    r = PipelineFiches(compile_, clauses, llm).analyser("Mon vélo n'est plus là où je l'avais rangé.")
    assert r.verdict.decision == Decision.NON_COUVERT
    assert "choisies par le modèle" in r.verdict.avertissements[0]


def test_exclusion_generale_limitee_a_sa_partie(clauses, compile_):
    from couverture.models import Point

    c = compile_.model_copy(deep=True)
    c.exclusions_generales.append(Point(id="g.x", nature="exclusion", enonce="Biens dont vous avez la garde ?",
                                        clause_id="2.2", extrait="x", a_demander=True))
    juge = JugeFiches(ScriptLLM(), c, clauses)
    velo = next(f for f in c.fiches if f.id == "4.3")
    groupes, chemins = juge._questions([velo])
    enonces = {x.enonce for x in chemins[0][1]}
    assert "Biens dont vous avez la garde ?" not in enonces, "exclusion rangée dans la partie incendie : pas pour le vol"
    assert "Le dommage est-il intentionnel ?" in enonces, "partie 8 sans garantie : vaut pour tout le contrat"
    assert "Biens dont vous avez la garde ?" not in {p.enonce for _, g in groupes for p, _ in g}, "pas de question pour rien"


# --- Ligne de commande ---------------------------------------------------------------------------

def test_cli_compiler_relire_analyser(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("COUVERTURE_RELECTURE", "non")
    llm = ScriptLLM(LOCAL_COMMUN)
    monkeypatch.setattr(cli, "llm_configure", lambda *a, **k: llm)
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
    for fi in donnees["fiches"]:
        fi["limites"] = []  # le relecteur retire la limite à la citation inventée
    f.write_text(json.dumps(donnees, ensure_ascii=False), encoding="utf-8")
    assert cli.main(["--donnees", str(d), "fiches", "--contrat", "fictif", "--importer", str(f), "--relu-par", "SG"]) == 0
    assert cli.main(["--donnees", str(d), "fiches", "--contrat", "fictif"]) == 0
    sortie = capsys.readouterr().out
    assert "relu par SG" in sortie and "lieu" in sortie and "obligation" in sortie

    assert cli.main(["--donnees", str(d), "analyser", "--contrat", "fictif", "--methode", "fiches",
                     "Mon vélo a été volé dans le local commun."]) == 0
    court = capsys.readouterr().out
    assert "NON_COUVERT" in court and "parties communes" in court and "Preuves" in court
    assert len(court.splitlines()) < 12, "la sortie par défaut tient sur un écran"
    assert cli.main(["--donnees", str(d), "analyser", "--contrat", "fictif", "--methode", "fiches", "--detail",
                     "Mon vélo a été volé dans le local commun."]) == 0
    sortie = capsys.readouterr().out
    assert "‹lieu›" in sortie and "présumée(s) absente(s)" in sortie


def test_archive_des_consignes(tmp_path):
    ecrites = archiver(tmp_path)
    assert any(e.endswith("grille-conditions/v3.txt") for e in ecrites)
    assert archiver(tmp_path) == [], "une version archivée n'est jamais réécrite"
    racine = Path(__file__).resolve().parents[1] / "docs" / "consignes"
    for f in ("grille-conditions/v1.txt", "compilation/v1.txt", "fiches/v1.txt"):
        assert (racine / f).exists(), f"l'histoire des consignes est gardée : {f}"


# --- Modèles : un rapide pour les analyses, un qui réfléchit pour les contrats ---------------------

def test_deux_modeles(monkeypatch):
    from couverture import llm as module_llm

    for v in ("COUVERTURE_MODELE", "COUVERTURE_MODELE_CONTRAT", "COUVERTURE_REFLEXION",
              "COUVERTURE_REFLEXION_CONTRAT", "COUVERTURE_FOURNISSEUR", "ANTHROPIC_API_KEY", "COUVERTURE_LLM_URL"):
        monkeypatch.delenv(v, raising=False)
    monkeypatch.setenv("MISTRAL_API_KEY", "k")
    monkeypatch.setenv("COUVERTURE_MODELE", "mistral-small-latest")
    monkeypatch.setenv("COUVERTURE_MODELE_CONTRAT", "mistral-large-latest")
    analyse, contrat = module_llm.configurer("analyse"), module_llm.configurer("contrat")
    assert analyse.modele == "mistral-small-latest" and analyse.extra["reasoning_effort"] == "none"
    assert contrat.modele == "mistral-large-latest" and contrat.extra["reasoning_effort"] == "low"
    monkeypatch.delenv("COUVERTURE_MODELE_CONTRAT")
    assert module_llm.configurer("contrat").modele == "mistral-small-latest", "par défaut, le même modèle"
    monkeypatch.setenv("COUVERTURE_REFLEXION", "medium")
    assert module_llm.configurer().extra["reasoning_effort"] == "medium", "le réglage explicite l'emporte"


def test_evaluation_en_parallele_garde_l_ordre():
    import time

    from couverture.evaluation import evaluer
    from couverture.models import Faits, Resultat, Verdict

    class Lente:
        def analyser(self, sinistre):
            time.sleep(0.05 if sinistre == "a" else 0.0)
            d = Decision.COUVERT if sinistre == "a" else Decision.NON_COUVERT
            return Resultat(sinistre=sinistre, faits=Faits(), clauses_consultees=[],
                            verdict=Verdict(decision=d, justification=""))

    cas = [{"id": "a", "sinistre": "a", "attendu": "COUVERT"}, {"id": "b", "sinistre": "b", "attendu": "NON_COUVERT"}]
    r = evaluer(Lente(), cas, paralleles=2)
    assert [l["id"] for l in r["cas"]] == ["a", "b"] and r["exactitude"] == 1.0


def test_barre_de_progression():
    import io

    from couverture.progression import Barre, duree

    class Terminal(io.StringIO):
        def isatty(self):
            return True

    t = Terminal()
    b = Barre(4, "Évaluation", flux=t)
    b.avancer("velo-01")
    b.avancer("velo-02")
    b.terminer()
    assert "2/4" in t.getvalue() and "velo-02" in t.getvalue() and "reste ~" in t.getvalue()
    assert duree(125) == "2 min 05 s" and duree(9) == "9 s"
    fichier = io.StringIO()  # pas un terminal : rien n'est écrit
    Barre(3, "X", flux=fichier).avancer()
    assert fichier.getvalue() == ""


# --- Deuxième mesure : alternatives et exclusions partielles --------------------------------------

def test_les_biens_sont_des_alternatives():
    """Incendie de la façade : « bâtiment ? » oui, « contenu ? » inconnu. Le contrat couvre l'un OU l'autre."""
    base = [_c("garantie", "REMPLIE", "evenement"), _c("garantie", "REMPLIE", "lieu")]
    _, decision, _, _, _ = decider_fiche(base + [_c("garantie", "REMPLIE", "bien"), _c("garantie", "INCONNUE", "bien")])
    assert decision == Decision.COUVERT
    rattachement, decision, _, _, _ = decider_fiche(base + [_c("garantie", "NON_REMPLIE", "bien"), _c("garantie", "NON_REMPLIE", "bien")])
    assert (rattachement, decision) == ("hors périmètre", Decision.NON_COUVERT), "aucun bien couvert"
    rattachement, _, _, _, _ = decider_fiche(base + [_c("garantie", "NON_REMPLIE", "bien"), _c("garantie", "INCONNUE", "bien")])
    assert rattachement == "possible"
    # Les autres rôles restent cumulatifs : un lieu contraire écarte la fiche.
    assert decider_fiche([_c("garantie", "REMPLIE", "evenement"), _c("garantie", "REMPLIE", "bien"),
                          _c("garantie", "NON_REMPLIE", "lieu")])[0] == "hors périmètre"


def test_exclusion_partielle(clauses, compile_):
    """Tuyau du lave-linge : l'exclusion « canalisation à l'origine » ne retire que le tuyau."""
    class Partielle(ScriptLLM):
        def completer(self, systeme, message):
            reponse = super().completer(systeme, message)
            if systeme == SYSTEME_FICHES:
                d = json.loads(reponse)
                questions = json.loads(message.split("## Questions\n", 1)[1])
                for r, q in zip(d["reponses"], questions):
                    if q["question"] == Q_COMMUNES:
                        r["etat"], r["justification"] = "PARTIELLE", "seul le cadenas est exclu"
                return json.dumps(d)
            return reponse

    r = PipelineFiches(compile_, clauses, Partielle(CHEZ_MOI)).analyser("Vélo et cadenas volés chez moi.")
    v = r.verdict
    assert v.decision == Decision.COUVERT and "sauf" in v.justification and "cadenas" in v.justification
    assert any(c.decisive and c.enonce == Q_COMMUNES for c in v.conditions), "la partie exclue est montrée"


def test_evaluation_survit_a_une_limite_de_debit():
    from couverture.evaluation import evaluer
    from couverture.llm import CleRefusee, ErreurLLM
    from couverture.models import Faits, Resultat, Verdict

    class Capricieux:
        def analyser(self, sinistre):
            if sinistre == "b":
                raise ErreurLLM("Erreur 429 du fournisseur : Rate limit exceeded")
            return Resultat(sinistre=sinistre, faits=Faits(), clauses_consultees=[],
                            verdict=Verdict(decision=Decision.COUVERT, justification=""))

    cas = [{"id": i, "sinistre": i, "attendu": "COUVERT"} for i in ("a", "b", "c")]
    r = evaluer(Capricieux(), cas, paralleles=2)
    assert r["erreurs_fournisseur"] == 1 and r["cas"][1]["erreur"] and r["exactitude"] == round(2 / 3, 3)

    class CleFausse:
        def analyser(self, sinistre):
            raise CleRefusee("Clé API refusée (401).")

    with pytest.raises(CleRefusee):
        evaluer(CleFausse(), cas, paralleles=2)


def test_limite_de_debit_attendue_puis_reussie(monkeypatch):
    import io
    import urllib.error

    from couverture import llm as module_llm

    monkeypatch.setattr(module_llm.time, "sleep", lambda s: None)
    appels = []

    class Reponse(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def urlopen(requete, timeout):
        appels.append(1)
        if len(appels) < 5:  # quatre refus d'affilée : l'ancien code abandonnait ici
            raise urllib.error.HTTPError(requete.full_url, 429, "x", {}, io.BytesIO(b"Rate limit exceeded"))
        return Reponse(b'{"ok": true}')

    monkeypatch.setattr(module_llm.urllib.request, "urlopen", urlopen)
    assert module_llm._poster("http://x", {}, {}, 10) == {"ok": True} and len(appels) == 5


def test_relecture_independante_comparee_par_le_code(clauses):
    """La relecture répond elle-même ; le code compare. Accord : confirmée. « Inconnu » : un doute,
    noté, sans effet. Oui contre non : contestée (la ligne redevient inconnue)."""
    from couverture.models import ClauseRetenue
    from couverture.relecture import relire

    index = {c.id: c for c in clauses}

    def ligne(enonce, etat):
        return Condition(nature="exclusion", groupe="G", clause_id="4.4", extrait="x", enonce=enonce,
                         etat=EtatCondition(etat))

    accord, doute, desaccord = ligne("A ?", "REMPLIE"), ligne("B ?", "NON_REMPLIE"), ligne("C ?", "NON_REMPLIE")

    class Relecteur:
        nom = "r"

        def completer(self, systeme, message):
            assert "etat_propose" not in message and "justification" not in message, "il ne voit pas la réponse"
            return json.dumps({"relectures": [{"id": 1, "etat": "REMPLIE", "raison": "…"},
                                              {"id": 2, "etat": "INCONNUE", "raison": "…"},
                                              {"id": 3, "etat": "REMPLIE", "raison": "…"}]})

    notes = relire("Vélo volé.", [accord, doute, desaccord],
                   [ClauseRetenue(clause=index["4.4"], score=0, raison="")], Relecteur())
    assert accord.relecture == "confirmee" and accord.etat == EtatCondition.REMPLIE
    assert doute.relecture == "doute" and doute.etat == EtatCondition.NON_REMPLIE, "un doute ne change rien"
    assert desaccord.relecture == "contestee" and desaccord.etat == EtatCondition.INCONNUE
    assert len(notes) == 2


def test_la_relecture_ne_peut_que_rendre_prudent():
    """Une exclusion contestée redevient inconnue ; avec la charge de la preuve, cela donnerait
    « couvert ». La borne l'empêche : deux lectures divergentes donnent INCERTAIN."""
    from couverture.relecture import borner

    assert borner(Decision.NON_COUVERT, Decision.COUVERT)[0] == Decision.INCERTAIN
    assert "divergent" in borner(Decision.NON_COUVERT, Decision.COUVERT)[1]
    assert borner(Decision.COUVERT, Decision.INCERTAIN) == (Decision.INCERTAIN, "")
    assert borner(Decision.NON_COUVERT, Decision.NON_COUVERT) == (Decision.NON_COUVERT, "")


def test_velo_local_commun_relecture_qui_conteste_l_exclusion(clauses, compile_):
    conteste = ScriptLLM(LOCAL_COMMUN, relectures=lambda l: "contestee" if l["question"] == Q_COMMUNES else "confirmee")
    r = PipelineFiches(compile_, clauses, conteste, relecteur=conteste).analyser("Vélo volé dans le local commun.")
    assert r.verdict.decision == Decision.INCERTAIN, "jamais COUVERT après avoir conclu à un refus"
    assert r.verdict.decision_avant_relecture == Decision.NON_COUVERT


def test_tableau_de_plusieurs_executions():
    from couverture.cli import tableau_repete

    def rapport(obtenu_b, exactitude):
        return {"cas": [{"id": "a", "attendu": "COUVERT", "obtenu": "COUVERT"},
                        {"id": "b", "attendu": "NON_COUVERT", "obtenu": obtenu_b}],
                "exactitude": exactitude, "exactitude_stricte": exactitude, "faux_couverts": 0,
                "faux_refus": 0, "taux_incertain": 0.5 if obtenu_b == "INCERTAIN" else 0.0}

    t = tableau_repete([rapport("NON_COUVERT", 1.0), rapport("INCERTAIN", 0.5), rapport("NON_COUVERT", 1.0)])
    assert "NC ? NC" in t and "Cas instables : 1 sur 2" in t and "83% (50% – 100%)" in t
