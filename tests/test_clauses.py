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
    assert len(modele.recus) == 2, "un refus cité n'est pas relu (7.212 : essayé, retiré)"


def test_couvert_sans_la_contresignature_des_regles_devient_a_preciser(base):
    modele = Modele({"chapitres": ["3.1.2"], "motif": ""}, jugements(**{"3_1_2_1": "couvre"}))
    lecture = clauses.lire(base, "c1", modele, DECLARATION, regles=Decision.NON_COUVERT)
    assert lecture.etat.decision == Decision.COUVERT and lecture.decision == Decision.INCERTAIN
    assert "« non couvert »" in lecture.desaccord


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
                           echantillon=0, mesure_finale=False, paralleles=1, rejouer=False)
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


def test_le_jeu_jamais_regarde_ne_se_lance_pas_par_megarde(base, tmp_path, monkeypatch):
    """Un jeu jamais regardé (ici « cinq », comme avant sa mesure) s'arrête avant tout appel, sauf avec
    --mesure-finale."""
    import argparse

    from couverture.cli import juger

    monkeypatch.setattr(juger, "JEUX_JAMAIS_VUS", ("cinq",))
    a = argparse.Namespace(contrat="c1", sinistre=None, jeu="cinq", cas=[], modele="m", regles=False, detail=False,
                           echantillon=0, mesure_finale=False, paralleles=1, rejouer=False)
    with pytest.raises(SystemExit) as arret:
        juger.executer(a, base, tmp_path)
    assert "mesure finale" in str(arret.value)


def test_la_stabilite_compare_les_passes_d_un_jeu(tmp_path):
    """7.220 : les bilans de trois passes ; un cas change de décision, un autre garde sa décision sur d'autres clauses."""
    from couverture.cli import juger

    def bilan(nom, cas):
        (tmp_path / nom).write_text(json.dumps({"cas": [
            {"id": i, "obtenu": o, "juste": j, "clauses": cl} for i, o, j, cl in cas]}), encoding="utf-8")

    (tmp_path / "juger_bilan_c1_cinq_m.json").write_text(json.dumps({"cas": [     # la passe 1 : sans les clauses
        {"id": "a", "obtenu": "COUVERT", "juste": True}, {"id": "b", "obtenu": "NON_COUVERT", "juste": True}]}),
        encoding="utf-8")
    bilan("juger_bilan_c1_cinq_m_p2.json", [("a", "COUVERT", True, ["1"]), ("b", "INCERTAIN", False, ["2"])])
    bilan("juger_bilan_c1_cinq_m_p3.json", [("a", "COUVERT", True, ["1", "3"]), ("b", "NON_COUVERT", True, ["2"])])
    bilan("juger_bilan_c1_cinq_m_rejeu.json", [("a", "NON_COUVERT", False, [])])     # un rejeu n'est pas une passe
    sortie = juger.stabilite(tmp_path, "cinq", "m")
    assert "3 passes (1, 2, 3) · 2 cas communs" in sortie
    assert "instables : 1 sur 2 — b NON_COUVERT → INCERTAIN → NON_COUVERT" in sortie
    assert "justes : 2, 1, 2" in sortie and "même décision, autres clauses : 1 sur 1 — a" in sortie
    assert "Aucun bilan" in juger.stabilite(tmp_path, "quatre", "m")


def test_le_message_met_en_tete_ce_qui_revient_a_chaque_sinistre(base):
    """Pour le cache : les exclusions générales d'abord, les garanties ensuite, les définitions et la déclaration
    à la fin. Deux sinistres du même contrat partagent ainsi le début de l'envoi."""
    modele = Modele({"chapitres": ["3.1.2"], "motif": ""}, jugements(**{"3_1_2_1": "couvre"}))
    clauses.lire(base, "c1", modele, DECLARATION)
    envoi = modele.recus[1][1]
    places = [envoi.index(f"[{i}]") for i in ("2.10", "2.11", "3.1.2", "3.1.2.2", "1.28")]
    assert places == sorted(places) and envoi.endswith(DECLARATION)


class Regles:
    """La chaîne de règles, pour la contresignature : rend la décision qu'on lui a donnée, ou tombe en panne."""

    def __init__(self, decision=None, questions=()):
        self.decision, self.questions = decision, list(questions)

    def analyser(self, sinistre, **_):
        from couverture.models import Faits, Resultat, Verdict
        if self.decision is None:
            raise RuntimeError("panne du modèle")
        return Resultat(sinistre=sinistre, contrat_id="c1", methode="regles", faits=Faits(), clauses_consultees=[],
                        verdict=Verdict(decision=self.decision, justification=".",
                                        informations_manquantes=self.questions))


def test_l_api_rend_une_lecture_des_clauses_au_format_de_ses_reponses(base):
    """7.201 : la même forme qu'une analyse par les règles (le schéma `Decision` l'accepte), les étapes racontées,
    la clause qui couvre citée, et la contresignature faite."""
    from couverture.api import lecture_clauses, service
    from couverture.api.schemas import Decision as Reponse

    etapes = []
    modele = Modele({"chapitres": ["3.1.2"], "motif": ""}, jugements(**{"3_1_2_1": "couvre"}))
    r, sortie = lecture_clauses.analyser_clauses(base, Regles(Decision.COUVERT), "c1", DECLARATION, modele,
                                         suivi=lambda e, d=None: etapes.append((e, d)))
    Reponse(**sortie)
    assert sortie["decision"] == "COUVERT" and sortie["mode"] == "clauses" and r.methode == "clauses"
    assert [c["clause_id"] for c in sortie["citations"]] == ["3.1.2.1"] and sortie["citations"][0]["role"] == "garantie"
    assert any("« La tempête de samedi »" in ligne for ligne in sortie["raisonnement"])
    assert [e for e, d in etapes] == ["designation", "designation", "jugement", "jugement", "regles", "regles",
                                     "decision", "decision"], "dans l'ordre de l'écran, chaque étape ouverte puis close"
    assert sortie["confiance"] == 1.0


def test_plusieurs_sinistres_sont_juges_chacun_a_part(base):
    """7.218 : une déclaration qui raconte deux sinistres (le découpage de 7.168, par le modèle de lecture des faits)
    reçoit une ligne par sinistre ; chacun est jugé et contresigné à part, et l'écran suit les étapes une seule fois."""
    import threading

    from couverture.analyse import clauses
    from couverture.api import lecture_clauses, service
    from couverture.api.schemas import Decision as Reponse

    chaises = "La tempête de samedi a emporté mes chaises de jardin."
    vitre = "La tempête de samedi a cassé la vitre de la véranda."

    class Decoupage:
        def completer(self, systeme, message):
            return json.dumps({"sinistres": [{"titre": "Les chaises", "phrases": [chaises]},
                                             {"titre": "La vitre", "phrases": [vitre]}]}, ensure_ascii=False)

    class Juge:
        """Répond selon la consigne, quel que soit l'ordre des appels : les deux sinistres sont jugés en même temps."""

        def __init__(self):
            self.recus, self.verrou = [], threading.Lock()

        def completer(self, systeme, message):
            with self.verrou:
                self.recus.append(message)
            if systeme == clauses.SYSTEME_DESIGNATION:
                return json.dumps({"chapitres": ["3.1.2"], "motif": ""})
            return json.dumps(jugements(**{"3_1_2_1": "couvre"}), ensure_ascii=False)

    regles = Regles(Decision.COUVERT)
    regles.llm = Decoupage()
    etapes, juge = [], Juge()
    r, sortie = lecture_clauses.analyser_clauses(base, regles, "c1", chaises + " " + vitre, juge,
                                         suivi=lambda e, d=None: etapes.append((e, d)))
    Reponse(**sortie)
    assert sortie["decision"] == "COUVERT" and len(r.parties) == 2
    assert [x["titre"] for x in sortie["sinistres"]] == ["Les chaises", "La vitre"]
    assert sortie["justification"].startswith("2 sinistres dans cette déclaration")
    assert {x["declaration"] for x in sortie["sinistres"]} == {chaises, vitre}
    assert sum(chaises in m for m in juge.recus) >= 2 and sum(vitre in m for m in juge.recus) >= 2, "chacun jugé à part"
    for e in ("designation", "jugement", "regles", "decision"):     # les deux lectures avancent chacune à son pas
        ouvertes = [i for i, (x, d) in enumerate(etapes) if x == e and d is None]
        closes = [i for i, (x, d) in enumerate(etapes) if x == e and d is not None]
        assert len(ouvertes) == 1 and len(closes) == 1 and ouvertes[0] < closes[0], "ouverte puis close, une seule fois"
    assert next(d for e, d in etapes if e == "designation" and d).startswith("2 sinistres dans la déclaration, chacun")


def test_la_relecture_apres_les_reponses_ne_redemande_pas_les_chapitres(base):
    """7.218 : relue avec les réponses du client, la déclaration garde les chapitres de la première lecture : un seul
    appel (le jugement), le même dossier, et la réponse rend ses chapitres pour la relecture suivante."""
    from couverture.api import lecture_clauses, service

    premier = Modele({"chapitres": ["3.1.2"], "motif": ""}, jugements(**{"3_1_2_1": "couvre"}))
    _, sortie = lecture_clauses.analyser_clauses(base, Regles(Decision.COUVERT), "c1", DECLARATION, premier)
    assert sortie["chapitres"] == ["3.1.2"]
    relu = Modele(jugements(**{"3_1_2_1": "couvre"}))
    complete = DECLARATION + "\n\nPrécisions du client :\n- Les chaises étaient-elles attachées ? Non."
    _, apres = lecture_clauses.analyser_clauses(base, Regles(Decision.COUVERT), "c1", complete, relu,
                                        chapitres=sortie["chapitres"])
    assert len(relu.recus) == 1 and relu.recus[0][0] == clauses.SYSTEME_JUGEMENT, "pas de désignation redemandée"
    assert relu.recus[0][1].endswith(complete) and apres["decision"] == "COUVERT"
    assert premier.recus[1][1].split("## Déclaration")[0] == relu.recus[0][1].split("## Déclaration")[0], \
        "le même dossier, dans le même ordre : le cache du fournisseur le reprend"


def test_la_lecture_compte_ses_tokens_et_retient_ses_clauses_citees(base, monkeypatch):
    """7.219 : les tokens du modèle des clauses et leur coût estimé, pour le journal ; et les clauses citées, que l'on
    pourra ouvrir en ligne (comme celles que les règles citent)."""
    from couverture.api import lecture_clauses, service

    class Large(Modele):
        modele = "mistral-large-latest"

        def completer(self, systeme, message):
            self.dernier_usage = {"prompt_tokens": 10000, "completion_tokens": 4000,
                                  "prompt_tokens_details": {"cached_tokens": 6000}}
            return super().completer(systeme, message)

    monkeypatch.setattr(service, "_CITEES_PAR_LA_LECTURE", {})
    monkeypatch.setattr(service.prolog, "clauses_citees", lambda c: {"9.9"})
    r, _ = lecture_clauses.analyser_clauses(base, Regles(Decision.COUVERT), "c1", DECLARATION,
                                    Large({"chapitres": ["3.1.2"], "motif": ""}, jugements(**{"3_1_2_1": "couvre"})))
    assert r.tokens == {"envoyes": 20000, "recus": 8000, "cache": 12000}, "deux appels : désigner, juger"
    assert r.cout_usd == round((8000 * 1.36 + 12000 * 0.14 + 8000 * 4.18) / 1e6, 5)
    assert service.clauses_consultables("c1") == {"9.9", "3.1.2.1"}
    assert service.cout("un-modele-inconnu", r.tokens) is None


def test_une_decision_differente_par_sinistre_laisse_l_ensemble_a_preciser():
    """Deux sinistres, deux décisions : pas de réponse pour le tout ; les questions portent le titre du sinistre."""
    from couverture.api import lecture_clauses, service
    from couverture.models import Faits, Resultat, Verdict

    def lu(decision, questions):
        r = Resultat(sinistre="s", contrat_id="c1", methode="clauses", faits=Faits(), clauses_consultees=[],
                     verdict=Verdict(decision=decision, justification="Motif.", informations_manquantes=questions))
        return r, {"decision": decision.value, "justification": "Motif.", "confiance": 1.0, "a_preciser": [],
                   "questions": questions, "citations": [], "limites": [], "raisonnement": [], "avertissements": [],
                   "durees_ms": {"lecture": 10}}

    _, sortie = lecture_clauses.plusieurs_lectures("c1", "s", [("Le vol", *lu(Decision.COUVERT, [])),
                                                       ("La fuite", *lu(Decision.INCERTAIN, ["Était-ce le gel ?"]))])
    assert sortie["decision"] == "INCERTAIN"
    assert sortie["questions"] == ["La fuite — Était-ce le gel ?"]
    assert "1. Le vol : Couvert. Motif." in sortie["justification"]


def test_un_couvert_que_les_regles_ne_peuvent_contresigner_reste_a_examiner(base):
    """La chaîne de règles en panne : la lecture couvre, mais un couvert non contresigné devient « incertain »."""
    from couverture.api import lecture_clauses, service

    modele = Modele({"chapitres": ["3.1.2"], "motif": ""}, jugements(**{"3_1_2_1": "couvre"}))
    _, sortie = lecture_clauses.analyser_clauses(base, Regles(None), "c1", DECLARATION, modele)
    assert sortie["decision"] == "INCERTAIN" and "n'ont pas répondu" in sortie["avertissements"][0]


def test_les_conditions_particulieres_s_ajoutent_a_la_declaration_en_mots(base):
    from couverture.api import lecture_clauses, service

    assert lecture_clauses.avec_souscription("Ma cave a été inondée.", "c1", {}) == "Ma cave a été inondée."
    lu = lecture_clauses.avec_souscription("Ma cave a été inondée.", "c1", {"formule": "confort"})
    assert lu.startswith("Ma cave a été inondée.\n\nConditions particulières du client : ") and lu.endswith(".")


def test_une_question_du_reglement_du_sinistre_devient_un_rappel(base, monkeypatch):
    """Le délai de déclaration ne dit pas si le sinistre est couvert : la garantie couvre, la question reste
    affichée comme un rappel, sans faire de la réponse un « à préciser »."""
    from couverture.api import lecture_clauses, service

    monkeypatch.setattr(dossier, "est_reglement", lambda c: c.id == "2.11")
    rendus = jugements(**{"3_1_2_1": "couvre"})
    for j in rendus["jugements"]:
        if j["clause"] == "2.11":
            j.update(effet="a_verifier", extrait_contrat="Déclarer le sinistre", question="Déclaré dans les 8 jours ?")
    modele = Modele({"chapitres": ["3.1.2"], "motif": ""}, rendus)
    lu = clauses.lire(base, "c1", modele, DECLARATION)
    assert lu.decision == Decision.COUVERT and [j.clause_id for j in lu.rappels] == ["2.11"]
    _, sortie = lecture_clauses.resultat_clauses(base, "c1", DECLARATION, lu, lu.decision, "", None, {})
    assert sortie["a_preciser"][0]["nature"] == "reserve" and "8 jours" in sortie["a_preciser"][0]["question"]


def test_une_question_posee_par_deux_clauses_ne_s_affiche_qu_une_fois(base):
    """7.208 : en ligne, la même question est arrivée deux fois dans une réponse ; la réponse reprend les
    questions de la décision, chacune une fois."""
    from couverture.api import lecture_clauses, service

    rendus = jugements(**{"3_1_2_1": "a_verifier", "3_1_2_2": "a_verifier"})
    for j in rendus["jugements"]:
        if j["effet"] == "a_verifier":
            j["question"] = "Les chaises étaient-elles fixées ?"
    lu = clauses.lire(base, "c1", Modele({"chapitres": ["3.1.2"], "motif": ""}, rendus), DECLARATION)
    assert lu.decision == Decision.INCERTAIN
    _, sortie = lecture_clauses.resultat_clauses(base, "c1", DECLARATION, lu, lu.decision, "", None, {})
    assert sortie["questions"] == ["Les chaises étaient-elles fixées ?"]


def resultat_des_regles(decision, *conditions):
    """Ce que la chaîne de règles rend : une décision, et les conditions qu'elle a examinées."""
    from couverture.models import Faits, Resultat, Verdict
    return Resultat(sinistre=DECLARATION, contrat_id="c1", methode="regles", faits=Faits(), clauses_consultees=[],
                    verdict=Verdict(decision=decision, justification="", conditions=list(conditions)))


def condition(nature, clause_id, etat, enonce):
    from couverture.models import Condition
    return Condition(nature=nature, clause_id=clause_id, extrait="", enonce=enonce, etat=etat)


def test_la_relecture_ciblee_garde_le_couvert_quand_la_declaration_ecarte_chaque_obstacle(base):
    """7.211 : la lecture couvre, les règles hésitent sur une exclusion (« les chaises étaient-elles fixées ? »).
    Une seule question de plus au modèle, sur cet obstacle ; il l'écarte en citant la déclaration mot pour mot :
    le « couvert » tient, et le désaccord est dit."""
    from couverture.models import EtatCondition as E

    regles = resultat_des_regles(Decision.INCERTAIN,
                                 condition("exclusion", "3.1.2.2", E.INCONNUE, "Les objets étaient-ils non fixés ?"),
                                 condition("garantie", "3.1.2.1", E.REMPLIE, "Est-ce une tempête ?"))
    revue = {"obstacles": [{"numero": 1, "avis": "ecarte", "extrait_declaration": "La tempête de samedi a emporté mes chaises de jardin"}]}
    modele = Modele({"chapitres": ["3.1.2"], "motif": ""}, jugements(**{"3_1_2_1": "couvre"}), revue)
    lecture = clauses.lire(base, "c1", modele, DECLARATION, regles=regles)
    assert lecture.decision == Decision.COUVERT and "écartés" in lecture.desaccord
    assert len(modele.recus) == 3 and "Obstacle 1 : exclusion, clause [3.1.2.2]" in modele.recus[2][1]
    assert "3.1.2.1" not in modele.recus[2][1].split("## Déclaration")[0], "une condition remplie n'est pas un obstacle"
    assert lecture.arbitrage and lecture.arbitrage[0].startswith("art. 3.1.2.2")


def test_la_relecture_ciblee_ne_garde_pas_le_couvert_sans_citation_exacte_ni_sur_un_doute(base):
    """La garde contre les couverts à tort ne s'affaiblit pas : un obstacle « écarté » sans citation retrouvée dans
    la déclaration, confirmé, ou inconnu, laisse la réponse à préciser. Sans obstacle dit par les règles (une simple
    décision), aucune relecture : rien n'est demandé de plus."""
    from couverture.models import EtatCondition as E

    regles = resultat_des_regles(Decision.NON_COUVERT,
                                 condition("exclusion", "3.1.2.2", E.REMPLIE, "Les objets étaient-ils non fixés ?"))
    for avis in ({"numero": 1, "avis": "ecarte", "extrait_declaration": "Les chaises étaient vissées au sol"},
                 {"numero": 1, "avis": "confirme"}, {"numero": 1, "avis": "inconnu"}):
        modele = Modele({"chapitres": ["3.1.2"], "motif": ""}, jugements(**{"3_1_2_1": "couvre"}), {"obstacles": [avis]})
        lecture = clauses.lire(base, "c1", modele, DECLARATION, regles=regles)
        assert lecture.decision == Decision.INCERTAIN, avis
    modele = Modele({"chapitres": ["3.1.2"], "motif": ""}, jugements(**{"3_1_2_1": "couvre"}))
    assert clauses.lire(base, "c1", modele, DECLARATION, regles=Decision.NON_COUVERT).decision == Decision.INCERTAIN
    assert len(modele.recus) == 2


def test_rejouer_reprend_les_reponses_gardees_sans_appeler_le_modele(base, tmp_path, monkeypatch, capsys):
    """`juger --rejouer` relit les réponses d'un passage précédent dans l'ordre des appels : sans rien de nouveau à
    demander, aucun appel n'est fait. Le rejeu s'écrit à part, l'original reste intact."""
    import argparse

    from couverture import llm
    from couverture.cli import juger

    gardees = [json.dumps({"chapitres": ["3.1.2"], "motif": ""}),
               json.dumps(jugements(**{"3_1_2_1": "couvre", "3_1_2_2": "exclut"}), ensure_ascii=False)]
    (tmp_path / "debug").mkdir()
    original = tmp_path / "debug" / "juger_declaration.txt"
    original.write_text("\n\n=== réponse suivante ===\n\n".join(gardees), encoding="utf-8")
    modele = Modele()
    monkeypatch.setattr(llm, "MistralLLM", lambda **_: modele)
    a = argparse.Namespace(contrat="c1", sinistre=DECLARATION, jeu=None, cas=[], modele="m", regles=False, detail=False,
                           echantillon=0, mesure_finale=False, paralleles=1, rejouer=True)
    assert juger.executer(a, base, tmp_path) == 0
    assert capsys.readouterr().out.startswith("NON_COUVERT") and modele.recus == []
    assert (tmp_path / "debug" / "juger_declaration_rejeu.txt").exists()
    assert original.read_text(encoding="utf-8") == "\n\n=== réponse suivante ===\n\n".join(gardees)


# 7.222 : ce que la journée d'essai du site a montré.

SERRURE = {"variable": "serrure_surete", "nature": "question", "question": "Une serrure de sûreté ?",
           "valeurs": ["oui", "non"], "libelles": {"oui": "Oui", "non": "Non"}, "aide": {}}


def test_quand_les_regles_retiennent_le_couvert_leurs_questions_sont_posees(base, monkeypatch):
    """La lecture couvre, les règles hésitent : « à préciser », avec les questions des règles et leurs réponses
    proposées. Sans elles, le client lisait « à préciser » sans rien à quoi répondre (le vélo de la cave)."""
    from couverture.api import lecture_clauses, service

    monkeypatch.setattr(service, "reponse_complete", lambda pipeline, r: {"a_preciser": [SERRURE]})
    modele = Modele({"chapitres": ["3.1.2"], "motif": ""}, jugements(**{"3_1_2_1": "couvre"}))
    r, sortie = lecture_clauses.analyser_clauses(base, Regles(Decision.INCERTAIN, ["Une serrure de sûreté ?"]), "c1",
                                         DECLARATION, modele)
    assert sortie["decision"] == "INCERTAIN" and sortie["questions"] == ["Une serrure de sûreté ?"]
    assert sortie["a_preciser"][0]["valeurs"] == ["oui", "non"]
    assert r.verdict.informations_manquantes == ["Une serrure de sûreté ?"]
    assert "« à préciser »" in sortie["justification"] and "INCERTAIN" not in sortie["justification"]


def test_les_questions_des_regles_ne_s_ajoutent_pas_quand_elles_concordent(base, monkeypatch):
    from couverture.api import lecture_clauses, service

    monkeypatch.setattr(service, "reponse_complete", lambda pipeline, r: {"a_preciser": [SERRURE]})
    modele = Modele({"chapitres": ["3.1.2"], "motif": ""}, jugements(**{"3_1_2_1": "couvre"}))
    _, sortie = lecture_clauses.analyser_clauses(base, Regles(Decision.COUVERT), "c1", DECLARATION, modele)
    assert sortie["decision"] == "COUVERT" and sortie["questions"] == [] and sortie["a_preciser"] == []


def test_un_sinistre_refuse_ne_porte_pas_de_rappel(base, monkeypatch):
    from couverture.api import lecture_clauses, service

    monkeypatch.setattr(dossier, "est_reglement", lambda c: c.id == "2.11")
    rendus = jugements(**{"3_1_2_1": "couvre", "3_1_2_2": "exclut"})
    for j in rendus["jugements"]:
        if j["clause"] == "2.11":
            j.update(effet="a_verifier", extrait_contrat="Déclarer le sinistre", question="Déclaré dans les 8 jours ?")
    lu = clauses.lire(base, "c1", Modele({"chapitres": ["3.1.2"], "motif": ""}, rendus), DECLARATION)
    assert lu.decision == Decision.NON_COUVERT and lu.rappels
    _, sortie = lecture_clauses.resultat_clauses(base, "c1", DECLARATION, lu, lu.decision, "", None, {})
    assert sortie["a_preciser"] == []


def test_plusieurs_sinistres_un_rappel_partage_une_fois_aucun_sur_un_refus():
    """Pour les deux méthodes : chaque sinistre garde ses questions ; un rappel commun s'affiche une fois pour la
    déclaration (la plus courte de ses formulations), et pas sur un sinistre refusé."""
    from couverture.api import lecture_clauses, service

    def rappel(question):
        return {"variable": "rappel_7.4", "nature": "reserve", "question": question, "valeurs": [], "libelles": {},
                "aide": {}}

    vol = {"decision": "INCERTAIN", "questions": ["Une serrure de sûreté ?"],
           "a_preciser": [SERRURE, rappel("Combien de chambres, et la valeur du vélo ? (art. 7.4)")]}
    gel = {"decision": "COUVERT", "questions": [], "a_preciser": [rappel("Combien de chambres ? (art. 7.4)")]}
    auto = {"decision": "NON_COUVERT", "questions": [], "a_preciser": [rappel("Déclaré dans les 8 jours ? (art. 7.1)")]}
    a_preciser, questions = service.rassembler([("Le vol", vol), ("Le gel", gel), ("La voiture", auto)])
    assert questions == ["Le vol — Une serrure de sûreté ?"]
    assert [p["question"] for p in a_preciser] == ["Le vol — Une serrure de sûreté ?", "Combien de chambres ? (art. 7.4)"]
    assert a_preciser[0]["variable"] == "serrure_surete_1"
    assert vol["a_preciser"] == [SERRURE] and gel["a_preciser"] == [] and auto["a_preciser"] == []

    propre = {"variable": "rappel_7.1", "nature": "reserve", "question": "Déclaré dans les 24 heures ?", "valeurs": [],
              "libelles": {}, "aide": {}}
    a_preciser, _ = service.rassembler([("Le vol", {"decision": "COUVERT", "questions": [], "a_preciser": [propre]}),
                                        ("Le gel", {"decision": "COUVERT", "questions": [], "a_preciser": []})])
    assert a_preciser == [], "une réserve propre à un sinistre reste dans sa ligne, pas « pour toute la déclaration »"


def test_un_refus_sans_citation_prend_les_clauses_des_regles_qui_refusent_aussi(base):
    """« Accident avec ma voiture » : la lecture ne trouve aucune garantie et ne cite rien ; les règles refusent aussi,
    en citant leurs clauses. La réponse les montre, et dit d'où elles viennent ; la décision ne change pas."""
    from couverture.api import lecture_clauses, service
    from couverture.models import Citation, Faits, Resultat, Verdict

    class ReglesQuiCitent(Regles):
        def analyser(self, sinistre, **_):
            v = Verdict(decision=Decision.NON_COUVERT, justification=".",
                        citations=[Citation(clause_id="2.10", extrait="une chute de pierres", role="exclusion")])
            return Resultat(sinistre=sinistre, contrat_id="c1", methode="regles", faits=Faits(),
                            clauses_consultees=[], verdict=v)

    modele = Modele({"chapitres": ["3.1.2"], "motif": ""}, jugements())
    r, sortie = lecture_clauses.analyser_clauses(base, ReglesQuiCitent(Decision.NON_COUVERT), "c1", DECLARATION, modele)
    assert sortie["decision"] == "NON_COUVERT" and [c["clause_id"] for c in sortie["citations"]] == ["2.10"]
    assert "les clauses citées sont les leurs" in sortie["justification"] and r.verdict.citations


def test_la_phrase_dit_quelle_clause_et_pourquoi_et_ce_que_disent_les_regles(base, monkeypatch):
    """7.222 : « Une garantie couvre, aucune clause examinée n'exclut » ne disait ni laquelle ni pourquoi. La phrase
    nomme la clause, le motif du modèle, et, quand les règles ne contresignent pas, ce qu'elles disent, elles."""
    from couverture.api import lecture_clauses, service
    from couverture.models import Faits, Resultat, Verdict

    class ReglesQuiHesitent(Regles):
        def analyser(self, sinistre, **_):
            v = Verdict(decision=Decision.INCERTAIN, justification="À préciser. « Tempête » (3.1.2) : s'applique, "
                                                                     "selon des faits non précisés.")
            return Resultat(sinistre=sinistre, contrat_id="c1", methode="regles", faits=Faits(),
                            clauses_consultees=[], verdict=v)

    monkeypatch.setattr(service, "reponse_complete", lambda pipeline, r: {"a_preciser": []})
    rendus = jugements(**{"3_1_2_1": "couvre"})
    for j in rendus["jugements"]:
        if j["clause"] == "3.1.2.1":
            j["motif"] = "la tempête a emporté les chaises de jardin"
    _, sortie = lecture_clauses.analyser_clauses(base, ReglesQuiHesitent(Decision.INCERTAIN), "c1", DECLARATION,
                                         Modele({"chapitres": ["3.1.2"], "motif": ""}, rendus))
    phrase = sortie["justification"]
    assert phrase.startswith("À préciser. La garantie qui s'applique : art. 3.1.2.1")
    assert "la tempête a emporté les chaises de jardin" in phrase
    assert "ne contresignent pas : « Tempête » (3.1.2) : s'applique, selon des faits non précisés." in phrase


def test_la_ligne_d_un_sinistre_ne_repete_pas_sa_decision():
    """Relu le 27 nov. : la phrase de chaque sinistre commence par sa décision ; la ligne d'ensemble ne la redit pas."""
    from couverture.api import lecture_clauses, service
    from couverture.models import Faits, Resultat, Verdict

    def lu(decision, phrase):
        r = Resultat(sinistre="s", contrat_id="c1", methode="clauses", faits=Faits(), clauses_consultees=[],
                     verdict=Verdict(decision=decision, justification=phrase))
        return r, {"decision": decision.value, "justification": phrase, "confiance": 1.0, "a_preciser": [],
                   "questions": [], "citations": [], "limites": [], "raisonnement": [], "avertissements": [],
                   "durees_ms": {}}

    _, sortie = lecture_clauses.plusieurs_lectures("c1", "s", [("Le vol", *lu(Decision.COUVERT, "Couvert. Par l'art. 2.10.")),
                                                       ("Le gel", *lu(Decision.NON_COUVERT, "Non couvert. Exclu."))])
    assert "1. Le vol : Couvert. Par l'art. 2.10." in sortie["justification"]
    assert "Couvert. Couvert." not in sortie["justification"] and "Non couvert. Non couvert." not in sortie["justification"]


def test_les_questions_en_phrase_des_regles_ne_se_perdent_pas(base, monkeypatch):
    """Relu le 27 nov. : une question des règles sans réponses proposées (le lien de causalité) s'ajoute à celles
    qui en ont."""
    from couverture.api import lecture_clauses, service

    monkeypatch.setattr(service, "reponse_complete", lambda pipeline, r: {"a_preciser": [SERRURE]})
    modele = Modele({"chapitres": ["3.1.2"], "motif": ""}, jugements(**{"3_1_2_1": "couvre"}))
    regles = Regles(Decision.INCERTAIN, ["Une serrure de sûreté ? (oui : couvert)", "Le vol est-il lié à l'effraction ?"])
    _, sortie = lecture_clauses.analyser_clauses(base, regles, "c1", DECLARATION, modele)
    assert sortie["questions"] == ["Une serrure de sûreté ?", "Le vol est-il lié à l'effraction ?"]
