"""La méthode de référence « document brut » : tout le contrat dans le prompt, aucune structure.

Le système lui-même est dans `prolog.py` (`PipelineRegles`) : le modèle lit les faits, Prolog décide.
"""

from __future__ import annotations

from .base import Base
from .juges import JugeDocumentBrut
from .models import Clause, ClauseRetenue, Faits, Resultat
from .validation import valider


def llm_configure(usage: str = "analyse"):
    """Le modèle configuré (Mistral, Anthropic ou API compatible OpenAI), ou None. Voir `llm.configurer`."""
    from .llm import configurer

    return configurer(usage)


class PipelineDocumentBrut:
    """Méthode de référence : le contrat entier dans le prompt, aucune recherche.
    Les citations sont contrôlées de la même façon, pour que la comparaison soit juste ;
    `verdict.decision_initiale` garde la réponse non contrôlée, celle d'un chatbot."""

    methode = "document-brut"

    def __init__(self, clauses: list[Clause], texte_brut: str, llm, contrat_id: str | None = None):
        self.clauses = clauses
        self.juge = JugeDocumentBrut(llm, texte_brut)
        self.contrat_id = contrat_id

    @classmethod
    def depuis_base(cls, base: Base, contrat_id: str, llm) -> "PipelineDocumentBrut":
        return cls(base.clauses(contrat_id), base.texte_brut(contrat_id), llm, contrat_id)

    def analyser(self, sinistre: str) -> Resultat:
        toutes = [ClauseRetenue(clause=c, score=0.0, raison="document complet") for c in self.clauses]
        verdict = valider(self.juge.juger(sinistre, Faits(), []), toutes, relocaliser=True)
        return Resultat(sinistre=sinistre, contrat_id=self.contrat_id, methode=self.methode,
                        faits=Faits(), clauses_consultees=[], verdict=verdict)
