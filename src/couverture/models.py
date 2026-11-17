"""Modèles de données partagés par toutes les étapes de la pipeline."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class TypeClause(str, Enum):
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

    @property
    def reference(self) -> str:
        return f"Art. {self.id}"


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
    COUVERT = "COUVERT"
    NON_COUVERT = "NON_COUVERT"
    INCERTAIN = "INCERTAIN"


class Citation(BaseModel):
    clause_id: str
    extrait: str
    role: str = "autre"
    valide: bool = True
    pages: list[int] = Field(default_factory=list)


class EtatCondition(str, Enum):
    REMPLIE = "REMPLIE"
    NON_REMPLIE = "NON_REMPLIE"
    INCONNUE = "INCONNUE"


class Condition(BaseModel):
    """Une vérification élémentaire : un fait du sinistre confronté à un passage du contrat."""

    nature: str  # "garantie" (doit être remplie pour être couvert), "exclusion" (si remplie, pas couvert), "limite", "obligation"
    role: str = ""  # méthode « fiches » : "evenement", "bien", "lieu", "circonstance"
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


class Point(BaseModel):
    """Une question d'une fiche compilée, écrite une fois pour toutes à partir du contrat.

    Condition de garantie : OUI est favorable à l'assuré. Exclusion : OUI veut dire qu'elle s'applique.
    `a_demander` (exclusions) : vrai si c'est un fait qu'un gestionnaire demanderait (lieu, fermeture,
    entretien) ; faux si l'exclusion est présumée absente tant que la déclaration ne l'évoque pas
    (faute intentionnelle, guerre…). Sans cette distinction, toute exclusion « inconnue »
    rendrait chaque réponse incertaine."""

    id: str
    nature: str  # "condition", "obligation", "exclusion" ou "limite"
    # Pour une condition : "evenement", "bien", "lieu" (le périmètre de la garantie) ou "circonstance".
    role: str = ""
    enonce: str
    clause_id: str
    extrait: str
    a_demander: bool = True
    # Obligation de prévention : son non-respect ne fait refuser que s'il a un lien causal avec le sinistre.
    lien_causal: bool = True
    valide: bool = True
    pages: list[int] = Field(default_factory=list)


class Fiche(BaseModel):
    """Une garantie traduite en questions fermées, vérifiées contre le texte du contrat."""

    id: str
    nom: str
    clause_id: str
    evenements: list[str] = Field(default_factory=list)
    objet: str = ""
    conditions: list[Point] = Field(default_factory=list)  # périmètre puis circonstances
    obligations: list[Point] = Field(default_factory=list)
    exclusions: list[Point] = Field(default_factory=list)
    limites: list[Point] = Field(default_factory=list)


class ContratCompile(BaseModel):
    """Le contrat compilé : ses fiches et ses exclusions générales, avec leur provenance."""

    contrat_id: str
    empreinte: str  # empreinte du contrat + version de la consigne de compilation
    modele: str = ""
    consigne: str = ""
    compile_le: str = ""
    relu_par: str = ""  # renseigné quand un humain a relu et réimporté les fiches
    fiches: list[Fiche] = Field(default_factory=list)
    exclusions_generales: list[Point] = Field(default_factory=list)
    avertissements: list[str] = Field(default_factory=list)
    # Garanties dont la compilation a échoué (délai, réponse coupée) : refaites au prochain `compiler`.
    echecs: list[str] = Field(default_factory=list)

    def points(self) -> list[Point]:
        return [p for f in self.fiches for p in f.conditions + f.obligations + f.exclusions + f.limites] + self.exclusions_generales


class Resultat(BaseModel):
    """Sortie complète de la pipeline, traçable de bout en bout."""

    sinistre: str
    contrat_id: str | None = None
    methode: str = "pipeline"
    faits: Faits
    clauses_consultees: list[ClauseRetenue]
    verdict: Verdict
