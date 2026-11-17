"""Assemblage : chargement → segmentation → faits → recherche → décision → contrôle."""

from __future__ import annotations

from pathlib import Path

from .base import Base
from .chargement import charger_lignes
from .faits import enrichir_requete, extraire_faits
from .juges import Juge, JugeDocumentBrut, JugeHeuristique
from .models import Clause, ClauseRetenue, Resultat
from .recherche import Recherche
from .segmentation import segmenter_lignes
from .validation import valider


def llm_configure(usage: str = "analyse"):
    """Le modèle configuré (Mistral, Anthropic ou API compatible OpenAI), ou None. Voir `llm.configurer` :
    usage « analyse » (chaque sinistre, modèle rapide) ou « contrat » (compilation, qualité, réparation)."""
    from .llm import configurer

    return configurer(usage)


def juge_par_defaut(methode: str = "conditions") -> Juge:
    """Avec un modèle : le juge par conditions.
    Sans modèle : le juge heuristique."""
    llm = llm_configure()
    if llm is None:
        return JugeHeuristique()
    from .conditions import JugeConditions
    from .llm import configurer_relecteur

    return JugeConditions(llm, relecteur=configurer_relecteur(llm))


class Pipeline:
    def __init__(self, clauses: list[Clause], juge: Juge | None = None, k: int = 5, max_clauses: int = 16,
                 contrat_id: str | None = None, methode: str = "conditions",
                 vecteurs: dict[str, list[float]] | None = None, vectoriseur=None):
        if not clauses:
            raise ValueError("Aucune clause trouvée : vérifier le format des conditions générales.")
        self.clauses = clauses
        self.contrat_id = contrat_id
        self.recherche = Recherche(clauses, vecteurs, vectoriseur)
        self.juge = juge or juge_par_defaut(methode)
        self.methode = "heuristique" if isinstance(self.juge, JugeHeuristique) else methode
        self.k, self.max_clauses = k, max_clauses

    @classmethod
    def depuis_base(cls, base: "Base", contrat_id: str, juge: Juge | None = None, vectoriseur=None,
                    **kwargs) -> "Pipeline":
        """Clauses du contrat et, si un vectoriseur est configuré et que les embeddings
        ont été calculés à l'ingestion, recherche hybride (mots + sens)."""
        if vectoriseur is None:
            from .llm import configurer_embeddings

            vectoriseur = configurer_embeddings()
        vecteurs = base.vecteurs(contrat_id, vectoriseur.nom) if vectoriseur else {}
        return cls(base.clauses(contrat_id), juge=juge, contrat_id=contrat_id,
                   vecteurs=vecteurs, vectoriseur=vectoriseur, **kwargs)

    @classmethod
    def depuis_fichier(cls, chemin: str | Path, juge: Juge | None = None, **kwargs) -> "Pipeline":
        return cls(segmenter_lignes(charger_lignes(chemin)), juge=juge, **kwargs)

    def analyser(self, sinistre: str) -> Resultat:
        faits = extraire_faits(sinistre)
        retenues = self.recherche.rechercher(enrichir_requete(sinistre, faits), k=self.k,
                                             max_clauses=self.max_clauses, question=sinistre)
        verdict = valider(self.juge.juger(sinistre, faits, retenues), retenues)
        return Resultat(sinistre=sinistre, contrat_id=self.contrat_id, methode=self.methode, faits=faits, clauses_consultees=retenues, verdict=verdict)


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
        faits = extraire_faits(sinistre)
        toutes = [ClauseRetenue(clause=c, score=0.0, raison="document complet") for c in self.clauses]
        verdict = valider(self.juge.juger(sinistre, faits, []), toutes, relocaliser=True)
        return Resultat(sinistre=sinistre, contrat_id=self.contrat_id, methode=self.methode,
                        faits=faits, clauses_consultees=[], verdict=verdict)
