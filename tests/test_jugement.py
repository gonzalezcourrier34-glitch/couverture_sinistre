"""Les jugements clause par clause, la jointure et la décision (7.188, 7.189) : tout se teste sans modèle."""

import pytest

from couverture.analyse import jugement
from couverture.analyse.jugement import Jugement
from couverture.analyse import attendu
from couverture.contrat.base import Base, Contrat
from couverture.models import Decision
from test_dossier import CONTRAT

DECLARATION = "La tempête de samedi a emporté mes chaises de jardin. Rien n'était fixé."


@pytest.fixture
def base(tmp_path):
    b = Base(tmp_path / "base.sqlite")
    b.enregistrer(Contrat(id="c1"), CONTRAT, "texte")
    attendu.enregistrer(b, "c1")
    return b


def repere(base, titre):
    return next(g.repere for g in attendu.garanties(base, "c1") if g.titre == titre)


def juger(base, garanties, jugements, optionnelles=frozenset(), declaration=DECLARATION):
    gardes, defauts = jugement.controler(jugements, CONTRAT, declaration)
    lignes, non_attendus = jugement.joindre(base, "c1", garanties, gardes)
    return jugement.decider(lignes, optionnelles, non_attendus, defauts)


def tempete(effet_garantie="couvre", effet_exclusion="sans_effet", effet_generale="sans_effet", **champs):
    """Les quatre jugements attendus pour la tempête (son chapeau, son étendue, ses exclusions, les exclusions
    générales, le renvoi), que chaque test fait varier."""
    return [Jugement("3.1.2", "sans_effet"),
            Jugement("3.1.2.1", effet_garantie, "La Compagnie assure contre la tempête", "La tempête de samedi"),
            Jugement("3.1.2.2", effet_exclusion, "Les objets non fixés", "Rien n'était fixé", **champs),
            Jugement("2.10", effet_generale, "une chute de pierres", "La tempête de samedi"),
            Jugement("2.11", "sans_effet")]


def test_couvert_quand_une_garantie_couvre_et_que_rien_n_exclut(base):
    etat = juger(base, [repere(base, "3.1.2 Tempête et grêle")], tempete())
    assert etat.decision == Decision.COUVERT and not etat.manquants and not etat.defauts
    assert [j.clause_id for j in etat.couvrent] == ["3.1.2.1"] and etat.garanties == {"3.1.2": "couvre"}


def test_non_couvert_quand_une_exclusion_de_la_garantie_joue(base):
    etat = juger(base, [repere(base, "3.1.2 Tempête et grêle")], tempete(effet_exclusion="exclut"))
    assert etat.decision == Decision.NON_COUVERT and [j.clause_id for j in etat.excluent] == ["3.1.2.2"]
    assert etat.couvrent == [] and etat.garanties == {"3.1.2": "exclue"}


def test_a_preciser_quand_un_point_reste_a_verifier_avec_sa_question(base):
    etat = juger(base, [repere(base, "3.1.2 Tempête et grêle")],
                 tempete(effet_exclusion="a_verifier", question="Les chaises étaient-elles fixées ?"))
    assert etat.decision == Decision.INCERTAIN and etat.questions == ["Les chaises étaient-elles fixées ?"]


def test_une_exclusion_generale_refuse_meme_si_la_garantie_couvre(base):
    etat = juger(base, [repere(base, "3.1.2 Tempête et grêle")], tempete(effet_generale="exclut"))
    assert etat.decision == Decision.NON_COUVERT and [j.portee for j in etat.excluent] == ["tout"]


def test_une_clause_attendue_sans_jugement_interdit_la_reponse_franche(base):
    """Le cœur de la refonte : le modèle a oublié les exclusions de la tempête. Hier, la chaîne couvrait ; ici la
    jointure nomme la clause manquante, et la réponse n'est pas « couvert »."""
    etat = juger(base, [repere(base, "3.1.2 Tempête et grêle")], [j for j in tempete() if j.clause_id != "3.1.2.2"])
    assert etat.decision == Decision.INCERTAIN and etat.manquants == ["3.1.2.2"]


def test_une_citation_fausse_ecarte_le_jugement_qui_devient_manquant(base):
    faux = tempete()
    faux[1] = Jugement("3.1.2.1", "couvre", "La Compagnie couvre tout", "La tempête de samedi")
    etat = juger(base, [repere(base, "3.1.2 Tempête et grêle")], faux)
    assert etat.decision == Decision.INCERTAIN and etat.manquants == ["3.1.2.1"]
    assert etat.defauts == ["3.1.2.1 : la phrase citée n'est pas dans la clause"]
    invente = tempete()
    invente[2] = Jugement("3.1.2.2", "exclut", "Les objets non fixés", "Les chaises étaient posées sur la pelouse")
    etat = juger(base, [repere(base, "3.1.2 Tempête et grêle")], invente)
    assert etat.defauts == ["3.1.2.2 : la phrase citée n'est pas dans la déclaration"] and etat.decision == Decision.INCERTAIN


def test_deux_garanties_en_concurrence_l_exclusion_de_l_une_ne_tue_pas_l_autre(base):
    """Le vol est exclu (vol simple), la tempête couvre : couvert. L'exclusion du vol n'atteint que le vol."""
    t, v = repere(base, "3.1.2 Tempête et grêle"), repere(base, "3.1.6 Vol")
    vol = [Jugement("3.1.6.1", "sans_effet"), Jugement("3.1.6.2", "exclut", "Le vol simple", "Rien n'était fixé")]
    etat = juger(base, [t, v], tempete() + vol)
    assert etat.decision == Decision.COUVERT and etat.garanties == {"3.1.2": "couvre", v: "exclue"}
    # … sauf si le refus vaut pour tout le contrat (un bien que le contrat n'assure pas).
    vol[1].portee = "tout"
    assert juger(base, [t, v], tempete() + vol).decision == Decision.NON_COUVERT


def test_une_option_qui_couvre_seule_reste_a_preciser(base):
    t = repere(base, "3.1.2 Tempête et grêle")
    etat = juger(base, [t], tempete(), optionnelles={t})
    assert etat.decision == Decision.INCERTAIN and "optionnelle" in etat.questions[0]


def test_rien_ne_couvre_non_couvert_et_un_jugement_hors_dossier_est_signale(base):
    etat = juger(base, [repere(base, "3.1.2 Tempête et grêle")],
                 tempete(effet_garantie="sans_effet") + [Jugement("3.1.6.1", "sans_effet")])
    assert etat.decision == Decision.NON_COUVERT and etat.non_attendus == ["3.1.6.1"]


def test_la_contresignature_des_regles():
    couvert, refus = jugement.Etat(Decision.COUVERT), jugement.Etat(Decision.NON_COUVERT)
    assert jugement.arbitrer(couvert, Decision.COUVERT) == (Decision.COUVERT, "")
    decision, desaccord = jugement.arbitrer(couvert, Decision.NON_COUVERT)
    assert decision == Decision.INCERTAIN and "NON_COUVERT" in desaccord
    assert jugement.arbitrer(couvert, Decision.INCERTAIN)[0] == Decision.INCERTAIN
    decision, desaccord = jugement.arbitrer(refus, Decision.COUVERT)
    assert decision == Decision.NON_COUVERT and "l'emporte" in desaccord
    assert jugement.arbitrer(couvert, None) == (Decision.COUVERT, ""), "sans règles pour ce contrat, la lecture tient seule"


def test_la_reponse_du_modele_se_lit_sans_planter():
    r = {"jugements": [{"clause": "3.1.2.1", "effet": "couvre", "extrait_contrat": "x", "extrait_declaration": "y"},
                       {"clause": "3.1.2.2", "effet": "peut-être"}, "n'importe quoi", {"effet": "exclut"},
                       {"clause": "2.10", "effet": "exclut", "portee": "tout"}]}
    js = jugement.depuis_reponse(r)
    assert [(j.clause_id, j.effet, j.portee) for j in js] == [("3.1.2.1", "couvre", "garantie"), ("2.10", "exclut", "tout")]
    assert jugement.depuis_reponse({}) == []


def test_un_refus_venu_d_une_autre_partie_du_contrat_interdit_le_couvert_franc(base):
    """La portée d'un refus ne repose pas sur le seul modèle. Le vol et la tempête sont voisins (même titre) : le
    refus de l'un laisse l'autre couvrir. Le même refus, venu d'un chapitre rangé ailleurs (les biens assurés, une
    option), peut valoir pour tout : à préciser, pas « couvert »."""
    t, v = repere(base, "3.1.2 Tempête et grêle"), repere(base, "3.1.6 Vol")
    vol = [Jugement("3.1.6.1", "sans_effet"), Jugement("3.1.6.2", "exclut", "Le vol simple", "Rien n'était fixé")]
    gardes, _ = jugement.controler(tempete() + vol, CONTRAT, DECLARATION)
    lignes, _ = jugement.joindre(base, "c1", [t, v], gardes)
    voisins = {t: ("3", "3.1", "3.1.2"), v: ("3", "3.1", "3.1.6")}
    assert jugement.decider(lignes, chemins=voisins).decision == Decision.COUVERT
    ailleurs = {t: ("3", "3.1", "3.1.2"), v: ("1 Les biens assurés", "1.2")}
    etat = jugement.decider(lignes, chemins=ailleurs)
    assert etat.decision == Decision.INCERTAIN and "portée" in etat.motif


def test_une_clause_ne_couvre_que_dans_sa_propre_garantie(base):
    """La tempête renvoie à l'article 2.11. Si le modèle juge que 2.11 « couvre », cela ne fait pas couvrir la
    tempête : une clause empruntée y apporterait sa couverture sans ses propres exclusions."""
    js = tempete(effet_garantie="sans_effet")
    js[4] = Jugement("2.11", "couvre", "Déclarer le sinistre", "La tempête de samedi")
    etat = juger(base, [repere(base, "3.1.2 Tempête et grêle")], js)
    assert etat.decision == Decision.NON_COUVERT and etat.couvrent == []
