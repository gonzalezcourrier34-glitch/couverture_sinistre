"""La logique de l'API (`couverture/api/service.py`), sans serveur ni FastAPI : l'oracle Python tient lieu de
moteur, une base temporaire tient lieu de base des contrats (20/11/2026)."""

from __future__ import annotations

import pytest

from couverture.api import service
from couverture.base import Base, Contrat
from couverture.models import Clause, Faits, TypeClause
from moteur_reference import Contrat as Regles, Explorateur
from couverture import chaine, prolog

CONTRAT = "assureur-a-habitation-2025"


@pytest.fixture(scope="module")
def regles():
    return Regles(prolog.fichier_regles(CONTRAT))


@pytest.fixture
def oracle(regles):
    def decider(f):  # comme moteur.pl : libellés et preuves des garanties retenues
        d = Explorateur(regles, f).decider()
        for r in d["retenues"] + d.get("possibles", []) + d.get("accessoires", []):
            g = next(x for x in regles.regles("garantie", 4) if x.args[0] == r["id"])
            r.update(garantie=g.args[1], article=g.args[2], motif="…",
                     preuves=[{"article": g.args[2], "texte": g.args[3], "role": "garantie"}])
        return d
    return decider


@pytest.fixture
def base(tmp_path, regles):
    """Une base avec le contrat A et, pour chaque garantie des règles, une clause qui porte son texte."""
    b = Base(tmp_path / "b.sqlite")
    clauses, vus = [], set()
    for g in regles.regles("garantie", 4):
        article, texte = str(g.args[2]), str(g.args[3])
        if article in vus:
            continue
        vus.add(article)
        clauses.append(Clause(id=article, article=article, titre=str(g.args[1]), chemin=[article], texte=texte,
                              type=TypeClause.GARANTIE))
    b.enregistrer(Contrat(id=CONTRAT, assureur="A", statut="OK"), clauses, "")
    return b


def test_faits_aller_retour():
    faits = {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"], "fermeture": "cadenas"}
    assert service.faits_depuis(chaine.faits_lisibles(faits)) == faits
    assert service.faits_depuis(Faits()) == {}


def test_decision_couverte_avec_citation(base, oracle):
    faits = {"evenement": ["responsabilite"], "origine_rc": "personne", "victime": "tiers"}
    _, r = service.decider(base, CONTRAT, faits, oracle)
    assert r["decision"] == "COUVERT" and r["citations"] and r["mode"].startswith("regles:aucun")
    assert r["faits"]["origine_rc"] == "personne"
    assert {"variable": "evenement", "libelle": "Événement", "valeur": "responsabilité civile"} == r["faits_affiches"][0]


def test_incertain_puis_reponse_du_client(base, oracle):
    """Un « incertain » dit quoi demander ; la réponse ajoutée aux faits tranche (le vélo dans la cave)."""
    _, r = service.decider(base, CONTRAT, {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"]}, oracle)
    assert r["decision"] == "INCERTAIN"
    fermeture = next(q for q in r["a_preciser"] if q["variable"] == "fermeture")
    assert fermeture["nature"] == "question" and "cadenas" in fermeture["valeurs"]
    assert fermeture["libelles"]["cle"] == "clé" and set(fermeture["libelles"]) == set(fermeture["valeurs"])
    _, r2 = service.decider(base, CONTRAT, r["faits"] | {"fermeture": "cadenas"}, oracle)
    assert r2["decision"] == "NON_COUVERT"


def test_faits_hors_vocabulaire_signales(base, oracle):
    _, r = service.decider(base, CONTRAT, {"evenement": ["responsabilite"], "couleur": "bleu",
                                          "origine_rc": "soucoupe"}, oracle)
    assert any("couleur" in a for a in r["avertissements"]) and any("soucoupe" in a for a in r["avertissements"])
    assert "couleur" not in r["faits"]


def test_contrat_inconnu_ou_sans_regles(base, oracle):
    with pytest.raises(KeyError):
        service.decider(base, "inconnu", {"evenement": ["vol"]}, oracle)
    base.enregistrer(Contrat(id="sans-regles"), [], "")
    with pytest.raises(LookupError):
        service.decider(base, "sans-regles", {"evenement": ["vol"]}, oracle)


def test_analyse_un_fait_non_confirme_devient_la_question(base, oracle):
    """Un fait décisif que la confirmation n'a pas retrouvé (7.49) : retiré des faits rendus, première question."""
    class Chaine:
        decideur = staticmethod(oracle)

        def analyser(self, sinistre):
            resultat, _ = service.decider(base, CONTRAT, {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"],
                                                          "fermeture": "cadenas"}, oracle)
            resultat.verdict.avertissements.append("fermeture" + service.NON_CONFIRME)
            return resultat

    _, r = service.analyser(Chaine(), "On m'a volé mon vélo dans la cave.")
    assert "fermeture" not in r["faits"] and r["a_preciser"][0]["variable"] == "fermeture"


def test_traduction_des_conditions_declaree():
    """7.169. Chaque jeu de conditions dit s'il est traduit en entier ; sans déclaration, il ne l'est pas."""
    import json

    from couverture import prolog

    declare = json.loads((prolog.DOSSIER / "traduction.json").read_text(encoding="utf-8"))
    for contrat_id, d in declare.items():
        if contrat_id.startswith("_"):
            continue
        assert service.traduction(contrat_id) == {"complet": d["complet"], "traduction": d["detail"]} and d["detail"]
    assert service.traduction("contrat-inconnu") == {"complet": False, "traduction": ""}


def test_souscription_publiee_et_gardee_a_la_decision(base, oracle):
    """Le contrat dit ce que ses conditions particulières précisent ; donnée dans les faits, une option n'est pas
    retirée comme « hors sujet » et n'est plus demandée (7.141)."""
    public = service.contrat_public(base.contrat(CONTRAT))
    assert {s["variable"] for s in public["souscription"]} == {"couverture_rc_locative", "option_materiel_multimedia"}
    assert all(s["libelle"] and set(s["libelles"]) == set(s["valeurs"]) for s in public["souscription"])
    faits = {"evenement": ["accident"], "bien": ["appareil_informatique"], "lieu": ["logement"]}
    _, r = service.decider(base, CONTRAT, faits, oracle)
    assert r["decision"] == "INCERTAIN" and "option_materiel_multimedia" in {p["variable"] for p in r["a_preciser"]}
    _, r = service.decider(base, CONTRAT, faits | {"option_materiel_multimedia": "oui"}, oracle)
    assert r["decision"] == "COUVERT" and r["faits"]["option_materiel_multimedia"] == "oui"
    assert r["faits_affiches"][-1]["libelle"] == "Garantie « matériel multimédia » souscrite"
