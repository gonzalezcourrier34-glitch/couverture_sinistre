"""La fiche PDF d'une décision (7.130) : elle se produit, tient en une page, et porte ce que l'écran montre."""

from __future__ import annotations

from datetime import datetime
from io import BytesIO

from couverture.analyse import fiche

REPONSE = {
    "contrat_id": "assureur-a-habitation-2025", "decision": "INCERTAIN", "confiance": 0.4,
    "justification": "Je ne peux pas trancher : la déclaration ne répond pas clairement à « Comment le local était-il fermé ? »",
    "faits": {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"], "effraction": "oui"},
    "a_preciser": [{"variable": "serrure_surete", "nature": "question", "valeurs": ["oui", "non"],
                    "question": "La cave était-elle fermée par une serrure de sûreté ?"},
                   {"variable": "attache", "nature": "reserve", "valeurs": ["oui", "non"],
                    "question": "Le vélo était-il attaché à un point fixe ?"}],
    "questions": ["La cave était-elle fermée par une serrure de sûreté ? (oui → couvert ; non → non couvert)"],
    "citations": [{"clause_id": "2.10", "extrait": "le vol du contenu situé dans le bâtiment", "role": "garantie", "pages": [11]},
                  {"clause_id": "2.10", "extrait": "si ces locaux sont fermés avec une serrure de sûreté", "role": "garantie", "pages": [11]},
                  {"clause_id": "2.10-a", "extrait": "le vol ou le vandalisme dans les parties communes", "role": "exclusion", "pages": [12]}],
    "limites": [{"clause_id": "2.10", "extrait": "Le vol dans les dépendances : 2 500 EUR", "montant": "2 500 EUR"}],
    "avertissements": [], "mode": "regles:test",
}


def texte(pdf: bytes) -> tuple[int, str]:
    import pdfplumber  # déjà une dépendance du projet : il lit les conditions générales

    with pdfplumber.open(BytesIO(pdf)) as document:
        return len(document.pages), " ".join(p.extract_text() or "" for p in document.pages)


def test_la_fiche_se_produit():
    assert fiche.fiche_pdf("Dégât.", {"decision": "COUVERT", "justification": "Couvert."}).startswith(b"%PDF")
    assert fiche.fiche_pdf("On a volé mon vélo.", REPONSE, {"assureur": "Assureur A"}).startswith(b"%PDF")
    assert fiche.nom_fichier(REPONSE, datetime(2026, 11, 21, 17, 5)) == "fiche-sinistre-assureur-a-habitation-2025-20261121-1705.pdf"
    assert fiche.propre("a → b <c>") == "a : b &lt;c&gt;"
    assert [a["extraits"] for a in fiche._citations_par_article(REPONSE["citations"])] == [
        ["le vol du contenu situé dans le bâtiment", "si ces locaux sont fermés avec une serrure de sûreté"],
        ["le vol ou le vandalisme dans les parties communes"]]


def test_la_fiche_porte_la_decision_et_ses_preuves():
    pdf = fiche.fiche_pdf("On a forcé la porte de ma cave <b>& volé</b> mon vélo.", REPONSE,
                          {"assureur": "Assureur A", "produit": "Habitation A", "version": "01/01/2025"},
                          datetime(2026, 11, 21, 17, 0))
    pages, t = texte(pdf)
    assert pages == 1
    for attendu in ("Fiche d'analyse de sinistre", "Assureur A", "21/11/2026", "À préciser", "confiance 40 %",
                    "<b>& volé</b>", "serrure de sûreté ?", "point fixe ?", "Art. 2.10", "Art. 2.10-a",
                    "parties communes", "2 500 EUR", "ne remplace pas"):
        assert attendu in t, attendu
    assert "→" not in t


def test_les_articles_cites_sont_joints_en_entier():
    """7.135 : après la fiche, le texte entier de chaque article cité, les passages cités surlignés."""
    clauses = {"2.10": {"texte": "Nous assurons le vol du contenu situé dans le bâtiment.\nDans les dépendances, la garantie "
                                 "est acquise si ces locaux sont fermés avec une serrure de sûreté. <Voir 2.10-a>",
                        "chemin": ["2. Garanties", "2.10 Vol"], "pages": [11, 12]}}
    pages, t = texte(fiche.fiche_pdf("On a volé mon vélo.", REPONSE, {"assureur": "Assureur A"}, clauses=clauses))
    assert pages == 2
    for attendu in ("Les articles cités, en entier", "2. Garanties > 2.10 Vol", "p. 11, 12", "Nous assurons le vol",
                    "<Voir"):
        assert attendu in t, attendu
    assert fiche.surligne("Le vol du contenu, ici.\nSuite & fin.", ["vol du contenu", "absent"]) == (
        'Le <span backColor="#fdf3bf">vol du contenu</span>, ici.<br/>Suite &amp; fin.')
    # L'article 2.10-a est cité mais absent de `clauses` : la fiche se produit quand même.
    assert texte(fiche.fiche_pdf("x", REPONSE, clauses={}))[0] == 1
