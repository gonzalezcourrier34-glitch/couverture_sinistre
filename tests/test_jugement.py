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
    assert etat.defauts == ["3.1.2.1 (couvre) : la phrase citée n'est pas dans la clause : « La Compagnie couvre tout »"]
    invente = tempete()
    invente[2] = Jugement("3.1.2.2", "exclut", "Les objets non fixés", "Les chaises étaient posées sur la pelouse")
    etat = juger(base, [repere(base, "3.1.2 Tempête et grêle")], invente)
    assert etat.defauts[0].startswith("3.1.2.2 (exclut) : la phrase citée n'est pas dans la déclaration") and etat.decision == Decision.INCERTAIN


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
    assert etat.decision == Decision.INCERTAIN and "optionnelle" in etat.questions[0] and t in etat.questions[0]


def test_rien_ne_couvre_non_couvert_et_un_jugement_hors_dossier_est_signale(base):
    etat = juger(base, [repere(base, "3.1.2 Tempête et grêle")],
                 tempete(effet_garantie="sans_effet") + [Jugement("3.1.6.1", "sans_effet")])
    assert etat.decision == Decision.NON_COUVERT and etat.non_attendus == ["3.1.6.1"]


def test_la_contresignature_des_regles():
    couvert = jugement.Etat(Decision.COUVERT)
    refus = jugement.Etat(Decision.NON_COUVERT, excluent=[Jugement("3.1.2.2", "exclut", "Les objets non fixés")])
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


def test_les_clauses_sans_effet_se_rendent_en_liste():
    """La réponse courte : le détail pour ce qui couvre, exclut ou reste à vérifier, une liste d'identifiants pour
    le reste. Une clause détaillée et aussi listée garde son détail."""
    rendus = jugement.depuis_reponse({"jugements": [{"clause": "3.1.2.1", "effet": "couvre", "extrait_contrat": "x"}],
                                      "sans_effet": ["3.1.2.2", "2.10", "3.1.2.1"]})
    assert [(j.clause_id, j.effet) for j in rendus] == [("3.1.2.1", "couvre"), ("3.1.2.2", "sans_effet"), ("2.10", "sans_effet")]


def test_une_clause_qui_reduit_l_indemnite_ne_refuse_pas(base):
    """« L'indemnité sera réduite de 50 % » n'est pas un refus : la garantie couvre, et la limite s'affiche."""
    etat = juger(base, [repere(base, "3.1.2 Tempête et grêle")], tempete(effet_exclusion="limite"))
    assert etat.decision == Decision.COUVERT and [j.clause_id for j in etat.limitent] == ["3.1.2.2"]


def test_une_citation_abregee_de_la_declaration_est_admise_si_chaque_morceau_y_est(base):
    """Le modèle abrège par « … » : admis si chaque morceau est dans la déclaration ; une phrase réécrite, non."""
    abregee = tempete(effet_exclusion="exclut")
    abregee[2] = Jugement("3.1.2.2", "exclut", "Les objets non fixés", "La tempête de samedi [...] Rien n'était fixé")
    assert juger(base, [repere(base, "3.1.2 Tempête et grêle")], abregee).decision == Decision.NON_COUVERT
    abregee[2] = Jugement("3.1.2.2", "exclut", "Les objets non fixés", "Les chaises n'étaient pas attachées")
    etat = juger(base, [repere(base, "3.1.2 Tempête et grêle")], abregee)
    assert etat.decision == Decision.INCERTAIN and "« Les chaises n'étaient pas attachées »" in etat.defauts[0]


def test_un_identifiant_ecrit_sans_son_signe_de_tete_est_retabli(base):
    """« 25 » pour « S25 », « 3.1.2 » pour « §3.1.2 » : rétabli s'il n'y a qu'une candidate dans le dossier."""
    from test_dossier import clause
    dossier = [clause("S25", ("Exclusions",), "Sont toujours exclus les dommages intentionnels"), clause("2.4", ("Eau",), "x")]
    gardes, defauts = jugement.controler([Jugement("25", "sans_effet"), Jugement("[2.4]", "sans_effet"),
                                          Jugement("26", "sans_effet")], dossier, DECLARATION)
    assert [j.clause_id for j in gardes] == ["S25", "2.4"] and defauts == ["26 (sans_effet) : clause hors du dossier"]


def test_une_citation_du_contrat_qui_saute_des_mots_devient_le_passage_exact(base):
    """« La Compagnie assure la tempête » pour « La Compagnie assure contre la tempête » : le passage exact remplace."""
    sautee = tempete()
    sautee[1] = Jugement("3.1.2.1", "couvre", "La Compagnie assure la tempête", "La tempête de samedi")
    etat = juger(base, [repere(base, "3.1.2 Tempête et grêle")], sautee)
    assert etat.decision == Decision.COUVERT and etat.couvrent[0].extrait_contrat == "La Compagnie assure contre la tempête"


def test_une_limite_mal_citee_compte_pour_lue_sans_etre_retenue(base):
    mal = tempete()
    mal[2] = Jugement("3.1.2.2", "limite", "L'indemnité sera réduite de moitié")
    etat = juger(base, [repere(base, "3.1.2 Tempête et grêle")], mal)
    assert etat.decision == Decision.COUVERT and not etat.limitent and not etat.manquants and "limite" in etat.defauts[0]



def test_un_alinea_juge_a_part_revient_a_sa_clause(base):
    """Le modèle juge « 3.1.2.2.1 » et « 3.1.2.2.3 », alinéas de la clause 3.1.2.2 : le plus lourd fait le
    jugement de la clause, sans défaut signalé, et sa citation se vérifie dans la clause."""
    alineas = [j for j in tempete() if j.clause_id != "3.1.2.2"] + [
        Jugement("3.1.2.2.1", "sans_effet"), Jugement("3.1.2.2.3", "exclut", "Les objets non fixés", "Rien n'était fixé")]
    etat = juger(base, [repere(base, "3.1.2 Tempête et grêle")], alineas)
    assert etat.decision == Decision.NON_COUVERT and [j.clause_id for j in etat.excluent] == ["3.1.2.2"]
    assert not etat.defauts and not etat.manquants


def test_un_refus_sans_clause_citee_ne_l_emporte_pas_sur_des_regles_qui_couvrent():
    """7.205 : « aucune garantie examinée ne couvre » n'est pas un refus fondé sur une clause : face à des règles qui
    couvrent, la réponse est à préciser. Un refus qui cite son exclusion, lui, tient seul."""
    absence = jugement.Etat(Decision.NON_COUVERT, motif="aucune garantie examinée ne couvre ce sinistre")
    assert jugement.arbitrer(absence, Decision.COUVERT)[0] == Decision.INCERTAIN
    refus = jugement.Etat(Decision.NON_COUVERT, excluent=[Jugement("3.1.2.2", "exclut", "Les objets non fixés")])
    assert jugement.arbitrer(refus, Decision.COUVERT)[0] == Decision.NON_COUVERT
    # 7.210 : ni sur des règles qui hésitent.
    assert jugement.arbitrer(absence, Decision.INCERTAIN)[0] == Decision.INCERTAIN
    assert jugement.arbitrer(absence, Decision.NON_COUVERT) == (Decision.NON_COUVERT, "")


def test_un_doute_qui_ne_peut_pas_faire_couvrir_ne_retient_pas_la_reponse():
    """7.210 : la seule garantie qui pouvait couvrir est exclue, clause citée. Une question posée dans un chapitre
    qui ne porte pas de garantie (qui est propriétaire ?), ou empruntée par renvoi à la garantie exclue (quelle
    formule ?), ne change rien : la réponse suit l'exclusion. Un chapeau d'options, lui, peut ouvrir une garantie :
    son doute reste."""
    from couverture.analyse.jugement import Ligne

    garantie = [Ligne("G", "G.1", "garantie", True, Jugement("G.1", "couvre", "La tempête", "la tempête")),
                Ligne("G", "G.2", "exclusion", True, Jugement("G.2", "exclut", "les objets extérieurs", "le store"))]
    qui = Ligne("D", "D.1", "exclusion", True, Jugement("D.1", "a_verifier", "Si vous êtes propriétaire",
                                                         question="Propriétaire ou locataire ?"))
    renvoi = Ligne("P", "G.1", "renvoi", True, Jugement("G.1", "a_verifier", "Selon la formule",
                                                       question="Quelle formule ?"))
    etat = jugement.decider(garantie + [qui], sans_couverture={"D"})
    assert etat.decision == Decision.NON_COUVERT and "exclues" in etat.motif and not etat.questions
    assert jugement.decider(garantie + [renvoi]).decision == Decision.NON_COUVERT
    assert jugement.decider(garantie + [qui]).decision == Decision.INCERTAIN, "un chapeau d'options garde son doute"
