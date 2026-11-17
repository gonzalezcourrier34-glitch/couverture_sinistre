"""Étape 4 — Décision : le sinistre est-il couvert ?

Deux juges interchangeables :
- `JugeLLM` : le juge principal, qui raisonne sur les clauses retenues ;
- `JugeHeuristique` : un juge de secours sans modèle, volontairement prudent,
  qui ne tranche que les cas nets et répond INCERTAIN sinon.
"""

from __future__ import annotations

import json
import re
from typing import Protocol

from .faits import enrichir_requete
from .llm import LLM, ErreurLLM
from .models import Citation, ClauseRetenue, Decision, Faits, TypeClause, Verdict
from .texte import jetons

SYSTEME = """Tu es gestionnaire sinistres dans une compagnie d'assurance. On te donne la description d'un sinistre et des extraits numérotés des conditions générales du contrat. Tu dois dire si le sinistre est couvert.

Règles :
1. Appuie-toi uniquement sur les clauses fournies, jamais sur ce que disent habituellement les contrats.
2. Raisonne dans cet ordre : (a) quelle garantie vise cet événement et ce bien ? (b) les conditions de cette garantie sont-elles établies par les faits décrits ? (c) une exclusion s'applique-t-elle ? (d) quelles limites (franchise, plafond, vétusté) faut-il signaler ?
3. COUVERT : une garantie s'applique, ses conditions sont établies par les faits, et aucune exclusion ne s'applique.
4. NON_COUVERT : aucune garantie ne vise l'événement, ou une exclusion s'applique clairement.
5. INCERTAIN : la décision dépend d'un fait que la description ne donne pas (option souscrite, lieu exact, effraction, gravité du dommage…) ou une clause peut se lire de deux façons. Dis alors exactement ce qu'il faut vérifier et ce que serait la décision dans chaque cas.
6. Une citation reprend mot pour mot un passage d'une clause fournie (30 mots au plus), avec l'identifiant de la clause.
7. N'invente aucun fait.

Réponds uniquement par un objet JSON, sans texte autour :
{
  "decision": "COUVERT" | "NON_COUVERT" | "INCERTAIN",
  "justification": "3 à 6 phrases en langage clair pour un client",
  "citations": [{"clause_id": "4.3", "extrait": "passage exact", "role": "garantie|exclusion|condition|limite|definition"}],
  "ambiguites": ["point du contrat ou des faits qui peut se lire de deux façons"],
  "informations_manquantes": ["question précise à poser au client"],
  "confiance": 0.0 à 1.0
}"""


def formater_clauses(retenues: list[ClauseRetenue]) -> str:
    blocs = []
    for r in retenues:
        c = r.clause
        blocs.append(f"[{c.id}] ({c.type.value}) {' > '.join(c.chemin)}\n{c.texte}")
    return "\n\n".join(blocs)


def extraire_json(texte: str) -> dict:
    texte = re.sub(r"^```(?:json)?|```$", "", texte.strip(), flags=re.MULTILINE).strip()
    debut, fin = texte.find("{"), texte.rfind("}")
    if debut == -1 or fin == -1:
        raise ValueError("Aucun objet JSON dans la réponse du modèle")
    return json.loads(texte[debut : fin + 1])


class Juge(Protocol):
    def juger(self, sinistre: str, faits: Faits, retenues: list[ClauseRetenue]) -> Verdict: ...


class JugeLLM:
    def __init__(self, llm: LLM, tentatives: int = 2):
        self.llm = llm
        self.tentatives = tentatives

    def juger(self, sinistre: str, faits: Faits, retenues: list[ClauseRetenue]) -> Verdict:
        message = (
            f"## Sinistre déclaré\n{sinistre}\n\n"
            f"## Faits repérés automatiquement (indicatifs)\n{faits.model_dump_json()}\n\n"
            f"## Clauses du contrat\n{formater_clauses(retenues)}"
        )
        erreur: Exception | None = None
        for _ in range(self.tentatives):
            try:
                donnees = extraire_json(self.llm.completer(SYSTEME, message))
                donnees["mode"] = self.llm.nom
                return Verdict.model_validate(donnees)
            except ErreurLLM:
                raise  # clé refusée, fournisseur injoignable : pas une réponse illisible
            except Exception as e:  # réponse mal formée : on redemande une fois
                erreur = e
                message += "\n\nTa réponse précédente n'était pas un JSON valide. Réponds uniquement par l'objet JSON."
        return Verdict(
            decision=Decision.INCERTAIN,
            justification="Le modèle n'a pas produit de réponse exploitable.",
            confiance=0.0,
            mode=self.llm.nom,
            avertissements=[f"Réponse du modèle illisible : {erreur}"],
        )


class JugeHeuristique:
    """Juge sans modèle. Ne remplace pas le JugeLLM : il sert à faire tourner la chaîne
    hors ligne et de garde-fou. Il ne répond COUVERT que si aucune exclusion ne recoupe
    le sinistre, et préfère INCERTAIN dès qu'il y a un doute."""

    nom = "heuristique"

    @staticmethod
    def _extrait(texte: str, vocab: set[str], bonus: frozenset[str] = frozenset(), n: int = 40) -> str:
        """Le passage de la clause (phrase ou élément de liste) qui recoupe le plus le sinistre.
        Les termes du lieu (« parties communes ») comptent triple : c'est souvent lui qui décide."""
        passages = [p.strip(" :") for p in re.split(r"(?<=[.;])\s+|\s:\s|\s*•\s*", texte) if len(p.strip()) > 15]
        if not passages:
            passages = [texte]
        meilleur = max(passages, key=lambda p: len(vocab & set(jetons(p))) + 2 * len(bonus & set(jetons(p))))
        return " ".join(meilleur.rstrip(".;").split()[:n])

    def juger(self, sinistre: str, faits: Faits, retenues: list[ClauseRetenue]) -> Verdict:
        brut = set(jetons(sinistre))
        enrichi = set(jetons(enrichir_requete(sinistre, faits)))
        # Pour les exclusions, on ajoute le vocabulaire contractuel du lieu (« hors des locaux »,
        # « parties communes ») : c'est le lieu qui fait le plus souvent sortir un sinistre du contrat.
        vocab_exclusion = set(jetons(enrichir_requete(sinistre, Faits(lieux=faits.lieux))))
        termes_lieu = frozenset(vocab_exclusion - brut)

        def recoupement(r: ClauseRetenue, vocab: set[str]) -> int:
            return len(vocab & set(jetons(r.clause.texte + " " + r.clause.titre)))

        garanties = sorted(
            (r for r in retenues if r.clause.type == TypeClause.GARANTIE and recoupement(r, enrichi) >= 2),
            key=lambda r: recoupement(r, enrichi),
            reverse=True,
        )
        exclusions = [r for r in retenues if r.clause.type == TypeClause.EXCLUSION and recoupement(r, vocab_exclusion) >= 1]
        conditions = [r for r in retenues if r.clause.type in (TypeClause.CONDITION, TypeClause.LIMITE)]

        citations = [Citation(clause_id=r.clause.id, extrait=self._extrait(r.clause.texte, vocab_exclusion, termes_lieu), role="exclusion") for r in exclusions[:3]]
        citations += [Citation(clause_id=r.clause.id, extrait=self._extrait(r.clause.texte, enrichi), role="garantie") for r in garanties[:2]]
        a_verifier = [f"Vérifier {r.clause.reference} ({r.clause.titre})" for r in conditions]
        a_verifier += [f"Vérifier si l'exclusion {r.clause.reference} s'applique" for r in exclusions]

        meilleure_garantie = max((recoupement(r, brut) for r in garanties), default=0)
        exclusion_forte = max((recoupement(r, vocab_exclusion) for r in exclusions), default=0)

        if not garanties:
            decision, confiance = Decision.NON_COUVERT, 0.35
            justification = "Aucune garantie du contrat ne semble viser cet événement."
        elif not exclusions:
            decision, confiance = Decision.COUVERT, 0.5
            justification = f"La garantie {garanties[0].clause.reference} semble s'appliquer et aucune exclusion ne recoupe le sinistre."
        elif exclusion_forte >= 3 and exclusion_forte > meilleure_garantie:
            decision, confiance = Decision.NON_COUVERT, 0.45
            justification = f"Une exclusion ({exclusions[0].clause.reference}) recoupe fortement la description du sinistre."
        else:
            decision, confiance = Decision.INCERTAIN, 0.3
            justification = "Une garantie et une ou plusieurs exclusions peuvent s'appliquer : il faut un examen humain ou un modèle."

        return Verdict(
            decision=decision,
            justification=justification,
            citations=citations,
            informations_manquantes=a_verifier,
            confiance=confiance,
            mode=self.nom,
        )


SYSTEME_BRUT = """Tu es gestionnaire sinistres. On te donne le texte complet des conditions générales d'un contrat d'assurance habitation et la description d'un sinistre. Dis si le sinistre est couvert.

Réponds uniquement par un objet JSON, sans texte autour :
{
  "decision": "COUVERT" | "NON_COUVERT" | "INCERTAIN",
  "justification": "3 à 6 phrases",
  "citations": [{"clause_id": "numéro de l'article tel qu'écrit dans le document", "extrait": "passage exact (30 mots au plus)", "role": "garantie|exclusion|condition|limite|definition"}],
  "ambiguites": [],
  "informations_manquantes": [],
  "confiance": 0.0 à 1.0
}"""


class JugeDocumentBrut:
    """Méthode de référence : tout le contrat dans le prompt, sans structuration.
    C'est « injecter le document brut dans un chatbot » ; la pipeline doit faire mieux."""

    def __init__(self, llm: LLM, texte_contrat: str):
        self.llm = llm
        self.texte = texte_contrat

    def juger(self, sinistre: str, faits: Faits, retenues: list[ClauseRetenue]) -> Verdict:
        message = f"## Conditions générales\n{self.texte}\n\n## Sinistre déclaré\n{sinistre}"
        try:
            donnees = extraire_json(self.llm.completer(SYSTEME_BRUT, message))
            donnees["mode"] = f"document-brut:{self.llm.nom}"
            return Verdict.model_validate(donnees)
        except ErreurLLM:
            raise
        except Exception as e:
            return Verdict(
                decision=Decision.INCERTAIN,
                justification="Réponse illisible.",
                confiance=0.0,
                mode=f"document-brut:{self.llm.nom}",
                avertissements=[f"Réponse du modèle illisible : {e}"],
            )
