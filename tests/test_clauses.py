"""La lecture des clauses de bout en bout (7.188, 7.189), avec un modèle factice : désigner, composer, juger,
joindre, décider, contresigner."""

import json

import pytest
from test_dossier import CONTRAT

from couverture.analyse import attendu, clauses, dossier
from couverture.contrat.base import Base, Contrat
from couverture.models import Decision

DECLARATION = "La tempête de samedi a emporté mes chaises de jardin. Rien n'était fixé."


class Modele:
    """Rend, dans l'ordre, les réponses qu'on lui a données, et garde ce qu'on lui a envoyé."""

    def __init__(self, *reponses):
        self.reponses, self.recus = [json.dumps(r, ensure_ascii=False) for r in reponses], []

    def completer(self, systeme, message):
        self.recus.append((systeme, message))
        return self.reponses[len(self.recus) - 1]


@pytest.fixture
def base(tmp_path):
    b = Base(tmp_path / "base.sqlite")
    b.enregistrer(Contrat(id="c1"), CONTRAT, "texte")
    return b


def jugements(**effets):
    cites = {"3.1.2.1": ("La Compagnie assure contre la tempête", "La tempête de samedi"),
             "3.1.2.2": ("Les objets non fixés", "Rien n'était fixé"), "2.10": ("une chute de pierres", "La tempête de samedi")}
    return {"jugements": [{"clause": c, "effet": effets.get(c.replace(".", "_"), "sans_effet"),
                           "extrait_contrat": cites.get(c, ("", ""))[0], "extrait_declaration": cites.get(c, ("", ""))[1]}
                          for c in ("3.1.2", "3.1.2.1", "3.1.2.2", "2.10", "2.11")]}


def test_de_la_declaration_a_la_decision(base):
    """Le modèle désigne un sous-article ; le code amène toute la garantie, demande un jugement pour chaque clause
    qui bloque, et calcule la réponse. Les tables des clauses attendues se créent au premier appel."""
    modele = Modele({"chapitres": ["3.1.2.1"], "motif": "tempête"}, jugements(**{"3_1_2_1": "couvre"}))
    lecture = clauses.lire(base, "c1", modele, DECLARATION, regles=Decision.COUVERT)
    assert lecture.decision == Decision.COUVERT and lecture.desaccord == ""
    assert lecture.garanties == [next(g.repere for g in attendu.garanties(base, "c1") if "Tempête" in g.titre)]
    assert [c.id for c in lecture.dossier] == ["1.28", "2.10", "2.11", "3.1.2", "3.1.2.1", "3.1.2.2"]
    table, envoi = modele.recus[0][1], modele.recus[1][1]
    assert table.startswith("## Table des matières") and table.endswith(DECLARATION), "la déclaration à la fin"
    assert "[3.1.2.2] (à juger)" in envoi and "[1.28] (à lire, sans jugement)" in envoi and "[3.1.6.2]" not in envoi


def test_l_exclusion_que_les_regles_ignoraient_refuse_et_le_desaccord_est_dit(base):
    """Les règles disaient « couvert » ; la clause lue exclut, avec ses deux citations : non couvert, et le
    désaccord est affiché. C'est le cas qui manquait aux trois jeux écrits à l'aveugle."""
    modele = Modele({"chapitres": ["3.1.2"], "motif": ""}, jugements(**{"3_1_2_1": "couvre", "3_1_2_2": "exclut"}))
    lecture = clauses.lire(base, "c1", modele, DECLARATION, regles=Decision.COUVERT)
    assert lecture.decision == Decision.NON_COUVERT and "l'emporte" in lecture.desaccord
    assert [j.clause_id for j in lecture.etat.excluent] == ["3.1.2.2"]


def test_couvert_sans_la_contresignature_des_regles_devient_a_preciser(base):
    modele = Modele({"chapitres": ["3.1.2"], "motif": ""}, jugements(**{"3_1_2_1": "couvre"}))
    lecture = clauses.lire(base, "c1", modele, DECLARATION, regles=Decision.NON_COUVERT)
    assert lecture.etat.decision == Decision.COUVERT and lecture.decision == Decision.INCERTAIN
    assert "NON_COUVERT" in lecture.desaccord


def test_un_modele_qui_ne_juge_pas_tout_n_obtient_pas_couvert(base):
    partiel = jugements(**{"3_1_2_1": "couvre"})
    partiel["jugements"] = [j for j in partiel["jugements"] if j["clause"] not in ("3.1.2.2", "2.10")]
    modele = Modele({"chapitres": ["3.1.2"], "motif": ""}, partiel, {"jugements": []})
    lecture = clauses.lire(base, "c1", modele, DECLARATION)
    assert lecture.decision == Decision.INCERTAIN and lecture.etat.manquants == ["2.10", "3.1.2.2"]
    assert len(modele.recus) == 3, "redemandées une fois, pas deux"


def test_un_repere_inconnu_ou_rien_de_designe_ne_couvre_ni_ne_refuse(base):
    modele = Modele({"chapitres": ["9.9"], "motif": ""})
    lecture = clauses.lire(base, "c1", modele, DECLARATION)
    assert lecture.garanties == [] and lecture.decision == Decision.INCERTAIN and len(modele.recus) == 1
    assert dossier.inconnus(CONTRAT, lecture.designes) == ["9.9"]


def test_la_commande_juger_affiche_la_decision_et_ses_clauses(base, monkeypatch, capsys, tmp_path):
    """`couverture juger` : deux appels au modèle, la décision, puis les clauses qui la portent avec leur extrait."""
    import argparse

    from couverture import llm
    from couverture.cli import juger

    modele = Modele({"chapitres": ["3.1.2"], "motif": ""}, jugements(**{"3_1_2_1": "couvre", "3_1_2_2": "exclut"}))
    monkeypatch.setattr(llm, "MistralLLM", lambda **_: modele)
    a = argparse.Namespace(contrat="c1", sinistre=DECLARATION, jeu=None, cas=[], modele="m", regles=False, detail=True,
                           echantillon=0, mesure_finale=False)
    assert juger.executer(a, base, tmp_path) == 0
    sortie = capsys.readouterr().out
    assert sortie.startswith("NON_COUVERT") and "[exclut] 3.1.2.2 : « Les objets non fixés »" in sortie
    assert "d'après : « Rien n'était fixé »" in sortie and len(modele.recus) == 2
    assert "=== réponse suivante ===" in (tmp_path / "debug" / "juger_declaration.txt").read_text(encoding="utf-8")


def test_une_clause_oubliee_est_redemandee_une_fois(base):
    """Le modèle oublie l'exclusion : la jointure le voit, un second appel la redemande seule, et la réponse tient."""
    premiere = jugements(**{"3_1_2_1": "couvre"})
    premiere["jugements"] = [j for j in premiere["jugements"] if j["clause"] != "3.1.2.2"]
    seconde = {"jugements": [{"clause": "3.1.2.2", "effet": "exclut", "extrait_contrat": "Les objets non fixés",
                              "extrait_declaration": "Rien n'était fixé"}]}
    modele = Modele({"chapitres": ["3.1.2"], "motif": ""}, premiere, seconde)
    lecture = clauses.lire(base, "c1", modele, DECLARATION)
    assert lecture.decision == Decision.NON_COUVERT and lecture.relancees == ["3.1.2.2"] and not lecture.etat.manquants
    relance = modele.recus[2][1]
    assert relance.startswith("Ces clauses n'ont pas reçu") and "[3.1.2.2] (à juger)" in relance and "[3.1.2.1]" not in relance


def test_les_jugements_d_une_analyse_sont_gardes_en_table(base):
    """Sur demande, l'analyse et ses jugements s'écrivent : on peut relire après coup ce que chaque clause a reçu."""
    import sqlite3
    modele = Modele({"chapitres": ["3.1.2"], "motif": ""}, jugements(**{"3_1_2_1": "couvre", "3_1_2_2": "exclut"}))
    clauses.lire(base, "c1", modele, DECLARATION, garder=True)
    with sqlite3.connect(base.chemin) as cx:
        assert cx.execute("SELECT contrat_id, decision FROM analyses_clauses").fetchall() == [("c1", "NON_COUVERT")]
        assert cx.execute("SELECT clause_id, extrait_declaration FROM jugements WHERE effet = 'exclut'").fetchall() \
            == [("3.1.2.2", "Rien n'était fixé")]
        assert cx.execute("SELECT count(*) FROM jugements").fetchone() == (5,)


def test_le_jeu_jamais_regarde_ne_se_lance_pas_par_megarde(base, tmp_path):
    """`juger --jeu quatre` s'arrête avant tout appel, sauf avec --mesure-finale."""
    import argparse

    from couverture.cli import juger

    a = argparse.Namespace(contrat="c1", sinistre=None, jeu="quatre", cas=[], modele="m", regles=False, detail=False,
                           echantillon=0, mesure_finale=False)
    with pytest.raises(SystemExit) as arret:
        juger.executer(a, base, tmp_path)
    assert "mesure finale" in str(arret.value)


def test_le_message_met_en_tete_ce_qui_revient_a_chaque_sinistre(base):
    """Pour le cache : les exclusions générales d'abord, les garanties ensuite, les définitions et la déclaration
    à la fin. Deux sinistres du même contrat partagent ainsi le début de l'envoi."""
    modele = Modele({"chapitres": ["3.1.2"], "motif": ""}, jugements(**{"3_1_2_1": "couvre"}))
    clauses.lire(base, "c1", modele, DECLARATION)
    envoi = modele.recus[1][1]
    places = [envoi.index(f"[{i}]") for i in ("2.10", "2.11", "3.1.2", "3.1.2.2", "1.28")]
    assert places == sorted(places) and envoi.endswith(DECLARATION)
