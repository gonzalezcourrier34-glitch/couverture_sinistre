"""Le dossier de clauses d'un sinistre (7.188) : ce que le code ajoute aux chapitres désignés, sans modèle."""

from couverture.analyse import dossier
from couverture.models import Clause, TypeClause


def clause(id_, chemin, texte, type_=TypeClause.AUTRE, renvois=()):
    return Clause(id=id_, article=id_.split(".")[0], titre=chemin[-1], chemin=list(chemin), texte=texte, type=type_,
                  renvois=list(renvois))


BASE = ("3 L'assurance des biens", "3.1 Garanties de base")
CONTRAT = [
    clause("1.28", ("1 Lexique", "1.28 Mobilier de jardin"), "Les chaises, les parasols, le trampoline.", TypeClause.DEFINITION),
    clause("1.52", ("1 Lexique", "1.52 Vol"), "Soustraction frauduleuse.", TypeClause.DEFINITION),
    clause("1.52.1", ("1 Lexique", "1.52 Vol", "1.52.1 Vol simple"), "Vol sans effraction.", TypeClause.DEFINITION),
    clause("1.30", ("1 Lexique", "1.30 Objets personnels (en séjour)"), "Vêtements emportés.", TypeClause.GARANTIE),
    clause("2.10", ("2 Conditions générales communes à toutes les garanties", "2.10 Exclusions"),
           "Ne sont jamais couverts : une chute de pierres.", TypeClause.EXCLUSION),
    clause("2.11", ("2 Conditions générales communes à toutes les garanties", "2.11 Obligations"), "Déclarer le sinistre."),
    clause("3.1.2", (*BASE, "3.1.2 Tempête et grêle"), "Applicable si les conditions particulières le mentionnent."),
    clause("3.1.2.1", (*BASE, "3.1.2 Tempête et grêle", "3.1.2.1 Étendue"), "La Compagnie assure contre la tempête.",
           TypeClause.GARANTIE, renvois=["2.11"]),
    clause("3.1.2.2", (*BASE, "3.1.2 Tempête et grêle", "3.1.2.2 Exclusions"),
           "Les objets non fixés, à l'exception du mobilier de jardin.", TypeClause.EXCLUSION),
    clause("3.1.6.1", (*BASE, "3.1.6 Vol", "3.1.6.1 Étendue"), "Le vol par effraction d'objets personnels.", TypeClause.GARANTIE),
    clause("3.1.6.2", (*BASE, "3.1.6 Vol", "3.1.6.2 Exclusions"), "Le vol simple.", TypeClause.EXCLUSION),
    clause("3.1.9", (*BASE, "3.1.9 Frais annexes"), "x " * 3000),
]


def ids(designes, declaration=""):
    return [c.id for c in dossier.composer(CONTRAT, designes, declaration)]


def test_un_sous_article_designe_amene_toute_la_garantie_ses_exclusions_et_les_exclusions_generales():
    """Désigner « 3.1.2.1 Étendue » amène tout 3.1.2 (le chapeau, l'étendue, les exclusions), les exclusions
    communes à toutes les garanties, l'article auquel la garantie renvoie, et la définition du mot qu'elle emploie.
    Le vol, non désigné, n'y est pas ; le chapitre voisin de 3 000 mots non plus."""
    d = ids(["3.1.2.1"])
    assert d == ["1.28", "2.10", "2.11", "3.1.2", "3.1.2.1", "3.1.2.2"]


def test_le_lexique_suit_les_mots_de_la_declaration_et_du_dossier():
    """Une entrée du lexique entre quand son terme paraît, avec ses sous-entrées ; ce qui est entre parenthèses
    dans son titre ne compte pas, et son type (ici « garantie », une erreur de découpage) non plus."""
    d = ids(["3.1.6.1"])
    assert {"1.52", "1.52.1", "1.30"} <= set(d) and "1.28" not in d
    assert "1.28" in ids(["3.1.6.1"], "On a volé mon mobilier de jardin.")
    assert [c.id for c in CONTRAT if dossier.est_definition(c)] == ["1.28", "1.52", "1.52.1", "1.30"]


def test_les_exclusions_generales_sont_toujours_au_dossier_meme_sans_rien_designer():
    assert ids([]) == ["2.10"]
    assert dossier.inconnus(CONTRAT, ["3.1.2", "9.9", "3.1.6.2"]) == ["9.9"]
    assert ids(["9.9"]) == ["2.10"]


def test_la_table_des_matieres_ne_liste_pas_le_lexique_et_donne_un_repere_par_chapitre():
    table = dossier.table_des_matieres(CONTRAT)
    assert "Mobilier de jardin" not in table and "    [3.1.2] 3.1.2 Tempête et grêle (23 mots)" in table
    assert "      [3.1.6.2] 3.1.6.2 Exclusions (3 mots)" in table and "  [2.10] 2.10 Exclusions (9 mots)" in table
    assert "[3.1.2.1] 3.1.2.1 Étendue (6 mots) — La Compagnie assure contre la tempête.…" in table, "le début d'une garantie"
    lignes = [l.split(" — ")[0] for l in table.splitlines()]
    reperes = [l.split("]")[0].strip().lstrip("[") for l in lignes]
    assert len(set(reperes)) == len(reperes), "deux chapitres ne portent jamais le même repère"
    vol = next(r for r, l in zip(reperes, lignes, strict=True) if l.endswith("3.1.6 Vol (9 mots)"))
    assert vol.startswith("§") and ids([vol]) == ["1.52", "1.52.1", "1.30", "2.10", "3.1.6.1", "3.1.6.2"]


def test_les_clauses_du_reglement_du_sinistre_se_reconnaissent_a_leur_titre():
    """7.203 : la déclaration et ses délais, l'estimation, l'indemnité, la franchise ; pas une garantie qui parle
    d'un sinistre, ni une entrée du lexique."""
    from couverture.analyse.dossier import est_reglement
    oui = [("7 Sinistres", "7.1 Vos obligations"), ("TITRE X - EN CAS DE SINISTRE", "Article 36.1 Déclaration"),
           ("2 Communes", "2.11 Obligations et formalités à respecter en cas de sinistre"),
           ("2 Communes", "2.5 Estimation des biens", "2.5.2.1 Mobilier"), ("5 RC", "5.9 Limites d’indemnisation"),
           ("Que devez-vous faire en cas de sinistre ?",), ("7 Sinistres", "7.7 Franchise"), ("DÉCLARATION ?",)]
    non = [("Article 30 EN CAS DE SINISTRE AFFECTANT", "Article 30.1 Retour prématuré"), ("3.1.9.8 Frais d’expertise",),
           ("1 Lexique", "1.40 Sinistre"), ("3 Garanties", "3.1.4 Dégâts des eaux"),
           ("2 Communes", "2.8 Déclaration du risque")]
    assert all(est_reglement(clause("x", ch, "texte")) for ch in oui)
    assert not any(est_reglement(clause("x", ch, "texte")) for ch in non)
