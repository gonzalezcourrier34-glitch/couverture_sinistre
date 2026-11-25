"""Les clauses attendues par garantie (7.189) : écrites du seul découpage, avant tout sinistre."""

import sqlite3

from couverture.analyse import attendu
from couverture.contrat.base import Base, Contrat
from test_dossier import BASE, CONTRAT, clause


def test_chaque_garantie_a_ses_clauses_attendues_avec_leur_role():
    """La tempête : son chapeau, son étendue, ses exclusions, les exclusions communes à toutes les garanties,
    l'article auquel elle renvoie, la définition qu'elle emploie. Seule la définition ne demande pas de jugement."""
    garanties, attendues = attendu.calculer(CONTRAT)
    tempete = next(g for g in garanties if g.titre == "3.1.2 Tempête et grêle")
    lignes = {a.clause_id: (a.role, a.bloque) for a in attendues if a.garantie == tempete.repere}
    assert lignes == {"3.1.2": ("autre", True), "3.1.2.1": ("garantie", True), "3.1.2.2": ("exclusion", True),
                      "2.10": ("exclusion_generale", True), "2.11": ("renvoi", True), "1.28": ("definition", False)}
    assert not tempete.optionnelle and tempete.porte_garantie


def test_tout_le_contrat_est_couvert_quel_que_soit_le_type_donne_par_le_decoupage():
    """Une garantie dont aucune clause n'est classée « garantie » (une erreur de découpage courante) a quand même
    ses clauses attendues ; un chapitre sous un titre d'option est marqué optionnel ; aucune clause hors lexique
    ne reste hors de la table."""
    contrat = CONTRAT + [
        clause("6.1", ("6 Les garanties optionnelles", "6.1 Pack multimédia"), "Si vos conditions particulières…",
               attendu.TypeClause.EXCLUSION),
        clause("6.1-a", ("6 Les garanties optionnelles", "6.1 Pack multimédia", "Obligations"), "Véhicule fermé à clé.",
               attendu.TypeClause.CONDITION)]
    garanties, attendues = attendu.calculer(contrat)
    pack = next(g for g in garanties if "6.1" in {a.clause_id for a in attendues if a.garantie == g.repere})
    assert pack.optionnelle and not pack.porte_garantie
    couvertes = {a.clause_id for a in attendues}
    assert {c.id for c in contrat if not attendu.dossier.est_definition(c)} <= couvertes
    assert len({g.repere for g in garanties}) == len(garanties)


def test_les_tables_s_enregistrent_et_se_relisent_par_une_requete(tmp_path):
    """La question « quelles exclusions faut-il examiner pour le vol ? » est une requête, pas un appel au modèle."""
    base = Base(tmp_path / "base.sqlite")
    base.enregistrer(Contrat(id="c1"), CONTRAT, "texte")
    n_garanties, n_lignes = attendu.enregistrer(base, "c1")
    assert n_garanties == len(attendu.garanties(base, "c1")) > 0 and n_lignes == len(attendu.attendues(base, "c1"))
    vol = next(g for g in attendu.garanties(base, "c1") if g.titre == "3.1.6 Vol")
    with sqlite3.connect(base.chemin) as cx:
        exclusions = [l[0] for l in cx.execute(
            "SELECT clause_id FROM clauses_attendues WHERE contrat_id = 'c1' AND garantie = ? AND bloque = 1 "
            "AND role IN ('exclusion', 'exclusion_generale') ORDER BY clause_id", (vol.repere,))]
    assert exclusions == ["2.10", "3.1.6.2"]
    assert attendu.enregistrer(base, "c1") == (n_garanties, n_lignes), "recalculer remplace, sans doublon"


def test_le_chapeau_d_un_grand_titre_n_attend_pas_tout_ce_que_le_titre_contient():
    """Un grand titre qui a un texte à lui (« 3.1 Garanties de base : … ») forme une ligne pour ce texte seul.
    Sinon, désigner la tempête ferait attendre un jugement sur le vol, et rien ne serait jamais « couvert »."""
    contrat = CONTRAT + [clause("3.1", BASE, "Les garanties qui suivent s'appliquent au bâtiment désigné.")]
    garanties, attendues = attendu.calculer(contrat)
    chapeau = next(g for g in garanties if g.chemin == BASE)
    ids = {a.clause_id for a in attendues if a.garantie == chapeau.repere}
    assert "3.1" in ids and "2.10" in ids and not ids & {"3.1.2.1", "3.1.6.2", "3.1.9"}
