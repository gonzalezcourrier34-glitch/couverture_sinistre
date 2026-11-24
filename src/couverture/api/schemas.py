"""Les corps des requêtes et des réponses de l'API (Pydantic), pour la validation et la documentation `/docs`.

**Provenance** : nouveau module (20/11/2026), sur le modèle des `BaseModel` de SortirIA (`SearchRequest`,
`RatingRequest`).
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


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
    """

    contrat_id: str = Field(min_length=1, examples=["assureur-a-habitation-2025"])
    sinistre: str = Field(min_length=10, max_length=2000, examples=[
        "En faisant du vélo dans le parc, j'ai renversé un piéton. Il s'est cassé le poignet."])
    souscription: dict[str, str] = Field(default_factory=dict, examples=[{"formule": "privilege"}])


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
    clause_id: str
    extrait: str
    role: str
    valide: bool = True
    pages: list[int] = Field(default_factory=list)


class Limite(BaseModel):
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
    sinistres : list[dict]
        Quand la déclaration contient plusieurs sinistres : la réponse complète de chacun, avec son `titre` et les
        phrases de la déclaration qui le concernent (`declaration`). La `justification` d'ensemble les résume, une
        ligne par sinistre ; la `decision` d'ensemble n'est ferme que s'ils reçoivent tous la même.
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
    sinistres: list[dict[str, Any]] = Field(default_factory=list)


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
