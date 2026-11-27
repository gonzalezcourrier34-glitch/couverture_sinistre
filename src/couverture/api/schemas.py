"""Les corps des requêtes et des réponses de l'API (Pydantic), pour la validation et la documentation `/docs`.

**Provenance** : nouveau module (20/11/2026), sur le modèle des `BaseModel` de SortirIA (`SearchRequest`,
`RatingRequest`).
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class AnalyseRequest(BaseModel):
    """Une déclaration de sinistre à analyser.

    Attributes
    ----------
    contrat_id : str
        Le contrat (voir `GET /api/v1/contrats`).
    sinistre : str
        La déclaration, en français, telle que le client l'écrit (10 à 2 000 caractères).
    souscription : dict[str, str]
        Facultatif : ce que disent les conditions particulières du client (la formule, les options), parmi
        celles du contrat (`souscription` de `GET /api/v1/contrats`). Ce qui n'est pas renseigné reste une
        question ou une réserve.
    methode : str | None
        Facultatif : `regles` (la chaîne de règles, quelques secondes) ou `clauses` (chaque clause jugée par le
        modèle, contresignée par les règles : deux à trois minutes). Sans valeur : celle du serveur
        (`COUVERTURE_METHODE`).
    chapitres : list[str] | None
        Facultatif, lecture des clauses seulement : les `chapitres` d'une analyse précédente du même sinistre, quand on
        le relit complété par les réponses du client. La désignation n'est pas redemandée (7.218).
    lecture : str | None
        Facultatif, avec `chapitres` : la `lecture` de cette analyse précédente (un jeton). Si le serveur l'a encore,
        seules les clauses douteuses et leur garantie sont rejugées (13.4) ; sinon, la relecture est entière.
    """

    contrat_id: str = Field(min_length=1, examples=["assureur-a-habitation-2025"])
    sinistre: str = Field(min_length=10, max_length=2000, examples=[
        "En faisant du vélo dans le parc, j'ai renversé un piéton. Il s'est cassé le poignet."])
    souscription: dict[str, str] = Field(default_factory=dict, examples=[{"formule": "privilege"}])
    methode: Literal["regles", "clauses"] | None = None
    # Lecture des clauses, relue après les réponses du client : les chapitres de la lecture précédente (7.218).
    chapitres: list[str] | None = Field(default=None, max_length=60)
    # Le jeton de la lecture précédente, pour ne rejuger que ce qui était en doute (13.4).
    lecture: str | None = Field(default=None, max_length=64)


class DecisionRequest(BaseModel):
    """Des faits déjà connus, à soumettre au moteur sans modèle.

    Attributes
    ----------
    contrat_id : str
        Le contrat.
    faits : dict[str, str | list[str]]
        {variable: valeur} au vocabulaire commun (voir `GET /api/v1/vocabulaire`) ; `evenement`, `bien` et
        `lieu` acceptent une liste. Typiquement : les `faits` d'une analyse, plus les réponses du client aux
        questions de `a_preciser`.
    """

    contrat_id: str = Field(min_length=1, examples=["assureur-b-habitation-2017"])
    faits: dict[str, str | list[str]] = Field(examples=[{
        "evenement": ["responsabilite"], "origine_rc": "animal_compagnie", "victime": "tiers",
        "option_rc_vie_privee": "oui"}])


class APreciser(BaseModel):
    """Un point que la réponse laisse ouvert : une question à poser à l'assuré, ou une réserve à vérifier."""

    variable: str
    nature: Literal["question", "reserve"]
    question: str
    valeurs: list[str]
    libelles: dict[str, str] = Field(default_factory=dict)
    aide: dict[str, str] = Field(default_factory=dict)


class FaitAffiche(BaseModel):
    """Un fait tel qu'on le montre : « Lieu : voie publique »."""

    variable: str
    libelle: str
    valeur: str


class Citation(BaseModel):
    """Un extrait de clause cité à l'appui de la réponse ; `valide` dit s'il a été retrouvé mot pour mot dans la clause."""

    clause_id: str
    extrait: str
    role: str
    valide: bool = True
    pages: list[int] = Field(default_factory=list)


class Limite(BaseModel):
    """Un plafond ou une franchise de la garantie retenue, avec la clause qui le dit."""

    clause_id: str
    extrait: str
    montant: str


class Decision(BaseModel):
    """La réponse : la décision en tête, ce qui la fonde en dessous.

    Attributes
    ----------
    decision : str
        `COUVERT`, `NON_COUVERT` ou `INCERTAIN`.
    a_preciser : list[APreciser]
        Ce qu'il faut demander au client (`question`), ou ce qui reste sous réserve (`reserve`).
    citations : list[Citation]
        Les passages du contrat qui fondent la décision, vérifiés mot pour mot.
    faits : dict
        Les faits retenus, à renvoyer à `POST /api/v1/decisions` avec les réponses aux questions.
    faits_affiches : list[FaitAffiche]
        Les mêmes faits, avec les libellés du vocabulaire, pour l'affichage.
    sinistres : list[Sinistre]
        Quand la déclaration contient plusieurs sinistres : la réponse complète de chacun (`Sinistre`), avec son
        `titre` et les phrases de la déclaration qui le concernent (`declaration`). Vide pour un seul sinistre :
        la réponse est alors la sienne. La `justification` d'ensemble les résume, une ligne par sinistre ; la
        `decision` d'ensemble n'est ferme que s'ils reçoivent tous la même ; `a_preciser` et `questions` reprennent
        celles de chacun, précédées de son titre, et les réserves qu'ils partagent, une fois (7.222).

    La même forme pour les deux méthodes (`mode` : `regles:…` ou `clauses`) : l'écran ne lit qu'elle.
    """

    contrat_id: str | None
    decision: Literal["COUVERT", "NON_COUVERT", "INCERTAIN"]
    justification: str
    confiance: float
    a_preciser: list[APreciser]
    questions: list[str]
    citations: list[Citation]
    limites: list[Limite]
    faits: dict[str, Any]
    faits_affiches: list[FaitAffiche] = Field(default_factory=list)
    avertissements: list[str]
    raisonnement: list[str]
    mode: str
    durees_ms: dict[str, int]
    sinistres: list[Sinistre] = Field(default_factory=list)
    chapitres: list[str] = Field(default_factory=list)
    # Lecture des clauses, réponse « à préciser » : le jeton qui retrouve ses jugements côté serveur (13.4).
    lecture: str = ""

    @model_validator(mode="after")
    def _une_forme_par_cas(self) -> Decision:
        """Un sinistre : pas de liste ; plusieurs : chacun le sien, sans sous-sinistres, et ses questions reprises."""
        if len(self.sinistres) == 1:
            raise ValueError("un seul sinistre ne se range pas dans `sinistres` : la réponse est la sienne")
        for s in self.sinistres:
            if s.sinistres:
                raise ValueError(f"le sinistre « {s.titre} » contient lui-même des sinistres")
            manquantes = [q for q in s.questions if f"{s.titre} — {q}" not in self.questions]
            if manquantes:
                raise ValueError(f"questions du sinistre « {s.titre} » absentes de l'ensemble : {manquantes}")
        return self


class Sinistre(Decision):
    """La réponse pour l'un des sinistres d'une déclaration qui en raconte plusieurs (7.168, 7.218, 7.222)."""

    titre: str = Field(min_length=1)
    declaration: str = ""


Decision.model_rebuild()


def au_format(reponse: dict[str, Any]) -> dict[str, Any]:
    """Une réponse du service, validée et mise à la forme de l'API (`Decision`) : celle que rend `/analyses`. Le
    flux `/analyses/suivi` la passe aussi par là, pour que l'écran reçoive toujours la même forme (7.222)."""
    return Decision.model_validate(reponse).model_dump(mode="json")


class FicheRequest(BaseModel):
    """Une décision à mettre en page (PDF).

    Attributes
    ----------
    contrat_id : str
        Le contrat de la décision.
    sinistre : str
        La déclaration du client (et, s'il y en a, ses réponses aux questions).
    reponse : Decision
        La réponse de `POST /api/v1/analyses` ou de `POST /api/v1/decisions`, telle quelle.
    """

    contrat_id: str = Field(min_length=1, examples=["assureur-a-habitation-2025"])
    sinistre: str = Field(min_length=1, max_length=4000)
    reponse: Decision
