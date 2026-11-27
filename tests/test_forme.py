"""La forme commune des réponses (7.222) : les deux méthodes, un sinistre ou plusieurs, rendent la même forme
(`schemas.Decision`), celle que l'écran lit. Un test par méthode et par cas, avec des modèles factices : sans frais.

Ce que la forme garantit, quelle que soit la méthode :
- un sinistre : pas de liste `sinistres`, la réponse est la sienne ;
- plusieurs : une réponse complète par sinistre (`Sinistre`, avec son titre), chacune avec sa décision ;
- les questions de chaque sinistre sont reprises pour l'ensemble, précédées de son titre (on y répond d'un bloc) ;
- une réserve que plusieurs sinistres partagent n'est dite qu'une fois, et aucune ne porte sur un sinistre refusé ;
- un « à préciser » a toujours au moins une question : sinon le client n'a rien à quoi répondre.
"""

from __future__ import annotations

import json

import pytest
from test_clauses import DECLARATION, Modele, Regles, jugements
from test_dossier import CONTRAT as CLAUSES_DU_CONTRAT

from couverture.analyse import clauses
from couverture.api import lecture_clauses, service
from couverture.api.schemas import Decision as Reponse
from couverture.api.schemas import au_format
from couverture.contrat.base import Base, Contrat
from couverture.models import Decision, Faits, Resultat, Verdict

CHAISES = "La tempête de samedi a emporté mes chaises de jardin."
VITRE = "La tempête de samedi a cassé la vitre de la véranda."


@pytest.fixture
def base(tmp_path):
    b = Base(tmp_path / "base.sqlite")
    b.enregistrer(Contrat(id="c1"), CLAUSES_DU_CONTRAT, "texte")
    return b


# ## La chaîne de règles, réduite à ce que le service en lit

def resultat_regles(titre: str | None, decision: Decision, questions=()) -> Resultat:
    r = Resultat(sinistre=titre or DECLARATION, contrat_id="c1", methode="regles", faits=Faits(), clauses_consultees=[],
                 verdict=Verdict(decision=decision, justification="Motif.", informations_manquantes=list(questions)))
    if titre:
        r.titre = titre
    return r


class ChaineRegles:
    """`analyser` rend le résultat donné ; `decideur` n'est pas appelé (aucun événement lu)."""

    def __init__(self, resultat: Resultat):
        self.resultat = resultat

    def analyser(self, sinistre, **_):
        return self.resultat


def par_les_regles(plusieurs: bool) -> dict:
    if not plusieurs:
        return service.analyser(ChaineRegles(resultat_regles(None, Decision.INCERTAIN)), DECLARATION)[1]
    ensemble = resultat_regles(None, Decision.INCERTAIN)
    ensemble.parties = [resultat_regles("Les chaises", Decision.INCERTAIN, ["Les chaises étaient-elles fixées ?"]),
                        resultat_regles("La vitre", Decision.COUVERT)]
    return service.analyser(ChaineRegles(ensemble), CHAISES + " " + VITRE)[1]


# ## La lecture des clauses

def doute() -> dict:
    rendus = jugements(**{"3_1_2_1": "a_verifier"})
    for j in rendus["jugements"]:
        if j["effet"] == "a_verifier":
            j["question"] = "Les chaises étaient-elles fixées ?"
    return rendus


def par_les_clauses(base, plusieurs: bool) -> dict:
    juge = Modele({"chapitres": ["3.1.2"], "motif": ""}, doute())
    if not plusieurs:
        return lecture_clauses.analyser_clauses(base, Regles(Decision.INCERTAIN), "c1", DECLARATION, juge)[1]

    class Decoupage:
        def completer(self, systeme, message):
            return json.dumps({"sinistres": [{"titre": "Les chaises", "phrases": [CHAISES]},
                                             {"titre": "La vitre", "phrases": [VITRE]}]}, ensure_ascii=False)

    class Juge:
        def completer(self, systeme, message):
            if systeme == clauses.SYSTEME_DESIGNATION:
                return json.dumps({"chapitres": ["3.1.2"], "motif": ""})
            rendus = doute() if CHAISES in message else jugements(**{"3_1_2_1": "couvre"})
            return json.dumps(rendus, ensure_ascii=False)

    regles = Regles(Decision.COUVERT)
    regles.llm = Decoupage()
    return lecture_clauses.analyser_clauses(base, regles, "c1", CHAISES + " " + VITRE, Juge())[1]


# ## La même forme, pour les deux méthodes

@pytest.mark.parametrize("methode", ["regles", "clauses"])
@pytest.mark.parametrize("plusieurs", [False, True], ids=["un sinistre", "plusieurs sinistres"])
def test_les_deux_methodes_rendent_la_meme_forme(base, methode, plusieurs):
    sortie = par_les_regles(plusieurs) if methode == "regles" else par_les_clauses(base, plusieurs)
    reponse = Reponse.model_validate(sortie)                 # la forme, et ses invariants (schemas.Decision)
    assert au_format(sortie) == reponse.model_dump(mode="json")
    assert (reponse.mode == "clauses") == (methode == "clauses")
    lignes = reponse.sinistres or [reponse]
    assert len(lignes) == (2 if plusieurs else 1)
    for s in lignes:
        if s.decision == "INCERTAIN":
            assert s.questions or any(p.nature == "question" for p in s.a_preciser), "un « à préciser » sans question"
        if s.decision == "NON_COUVERT":
            assert not [p for p in s.a_preciser if p.nature == "reserve"], "une réserve sur un refus"
    if plusieurs:
        assert [s.titre for s in reponse.sinistres] == ["Les chaises", "La vitre"]
        decisions = {s.decision for s in reponse.sinistres}
        assert len(decisions) == 2, "chaque sinistre garde sa décision"
        assert all(q.startswith(("Les chaises — ", "La vitre — ")) for q in reponse.questions)


def test_la_forme_refuse_ce_que_l_ecran_ne_saurait_pas_lire():
    """Un seul sinistre rangé dans la liste, ou ses questions oubliées dans l'ensemble : refusé à la validation."""
    sortie = par_les_regles(True)
    with pytest.raises(ValueError, match="un seul sinistre"):
        Reponse.model_validate(sortie | {"sinistres": sortie["sinistres"][:1]})
    with pytest.raises(ValueError, match="absentes de l'ensemble"):
        Reponse.model_validate(sortie | {"questions": []})
