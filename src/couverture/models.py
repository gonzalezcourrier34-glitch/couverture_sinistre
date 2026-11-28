"""Modèles de données partagés par toutes les étapes de la pipeline."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class TypeClause(str, Enum):
    """Le rôle d'une clause dans le contrat."""

    DEFINITION = "definition"
    GARANTIE = "garantie"
    EXCLUSION = "exclusion"
    CONDITION = "condition"
    LIMITE = "limite"
    AUTRE = "autre"


class Clause(BaseModel):
    """Plus petite unité numérotée des conditions générales (ex. « 4.3 »)."""

    id: str
    article: str
    titre: str
    chemin: list[str]
    texte: str
    type: TypeClause
    # Section dont la clause dépend : ses voisines dans ce groupe sont ses exclusions/conditions.
    groupe: str = ""
    pages: list[int] = Field(default_factory=list)
    renvois: list[str] = Field(default_factory=list)


class ClauseRetenue(BaseModel):
    """Clause sélectionnée par la recherche, avec la raison de sa sélection."""

    clause: Clause
    score: float
    raison: str


class Faits(BaseModel):
    """Faits extraits de la description du sinistre."""

    evenements: list[str] = Field(default_factory=list)
    biens: list[str] = Field(default_factory=list)
    lieux: list[str] = Field(default_factory=list)
    circonstances: list[str] = Field(default_factory=list)


class Decision(str, Enum):
    """Les trois réponses possibles."""

    COUVERT = "COUVERT"
    NON_COUVERT = "NON_COUVERT"
    INCERTAIN = "INCERTAIN"


#: La décision telle qu'on la montre (le badge, le début d'une phrase), et telle qu'on la dit dans une phrase.
#: Un seul endroit pour les deux méthodes, la fiche et les messages (7.222) : jamais le code interne à l'écran.
LIBELLES_DECISION = {Decision.COUVERT: "Couvert", Decision.NON_COUVERT: "Non couvert", Decision.INCERTAIN: "À préciser"}
DECISION_DITE = {d: libelle[:1].lower() + libelle[1:] for d, libelle in LIBELLES_DECISION.items()}


class Citation(BaseModel):
    """Un extrait de clause cité par la réponse ; `valide` passe à faux si l'extrait n'est pas retrouvé dans la clause."""

    clause_id: str
    extrait: str
    role: str = "autre"
    valide: bool = True
    pages: list[int] = Field(default_factory=list)


class EtatCondition(str, Enum):
    """L'état d'une condition au vu des faits : remplie, non remplie, ou inconnue."""

    REMPLIE = "REMPLIE"
    NON_REMPLIE = "NON_REMPLIE"
    INCONNUE = "INCONNUE"


class Condition(BaseModel):
    """Une vérification élémentaire : un fait du sinistre confronté à un passage du contrat."""

    nature: str  # "garantie" (doit être remplie pour être couvert), "exclusion" (si remplie, pas couvert), "limite", "obligation"
    role: str = ""  # rôle dans la règle : périmètre, circonstance, obligation, exclusion
    lien_causal: bool = True  # obligation de prévention : refus seulement s'il y a un lien causal
    groupe: str = ""  # nom de la garantie examinée, pour les conditions de garantie
    clause_id: str
    extrait: str
    enonce: str  # la question posée au fait : « Le vol a-t-il eu lieu dans les parties communes ? »
    etat: EtatCondition = EtatCondition.INCONNUE
    justification: str = ""  # ce qui, dans la description du sinistre, fonde l'état
    question: str = ""  # à poser au client si l'état est inconnu
    valide: bool = True
    pages: list[int] = Field(default_factory=list)
    decisive: bool = False
    # Relecture par le juge de la grille : "confirmee", "contestee" ou "" (pas relue).
    relecture: str = ""
    relecture_raison: str = ""
    etat_propose: EtatCondition | None = None  # état d'origine, si la relecture l'a contesté


class Verdict(BaseModel):
    """La réponse à une déclaration : décision, justification, citations, conditions examinées, points à préciser,
    confiance."""

    decision: Decision
    justification: str
    citations: list[Citation] = Field(default_factory=list)
    conditions: list[Condition] = Field(default_factory=list)
    ambiguites: list[str] = Field(default_factory=list)
    informations_manquantes: list[str] = Field(default_factory=list)
    confiance: float = Field(ge=0.0, le=1.0, default=0.5)
    mode: str = "inconnu"
    # Décision du juge avant contrôle des citations : mesure ce que le contrôle a corrigé.
    decision_initiale: Decision | None = None
    # Décision de la grille avant la relecture, si la relecture l'a changée.
    decision_avant_relecture: Decision | None = None
    avertissements: list[str] = Field(default_factory=list)
    # Méthode « règles » : l'arbre de preuve du moteur Prolog, et sa lecture en lignes.
    preuve: list[dict] = Field(default_factory=list)
    raisonnement: list[str] = Field(default_factory=list)


class Resultat(BaseModel):
    """Sortie complète de la pipeline, traçable de bout en bout."""

    sinistre: str
    contrat_id: str | None = None
    methode: str = "pipeline"
    faits: Faits
    clauses_consultees: list[ClauseRetenue]
    verdict: Verdict
    # Temps par étape, en millisecondes (méthode « regles ») : lecture des faits, décision du moteur.
    durees_ms: dict[str, int] = Field(default_factory=dict)
    # Une déclaration qui contient plusieurs sinistres (7.168) : un résultat par sinistre, chacun avec son titre
    # et les phrases de la déclaration qui le concernent (dans `sinistre`). Vide pour un seul sinistre.
    titre: str = ""
    parties: list[Resultat] = Field(default_factory=list)
    # Tokens du modèle de la lecture des clauses (7.219) : {"envoyes", "recus", "cache"} ; vide pour la chaîne de règles.
    tokens: dict[str, int] = Field(default_factory=dict)
    cout_usd: float | None = None      # estimé d'après le tarif du modèle (7.219) ; None : inconnu


Resultat.model_rebuild()
