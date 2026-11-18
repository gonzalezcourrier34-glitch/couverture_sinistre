"""La méthode de référence : le contrat entier dans le prompt, comme dans un chatbot.

`JugeDocumentBrut` sert de point de comparaison (« un PDF dans un chatbot ») : le banc le fait
tourner avec `--methode brut`, et ses citations sont contrôlées comme celles des règles.
Les anciennes méthodes (grille de conditions, fiches compilées) ont été retirées le 18 nov. 2026 :
voir `docs/DEMARCHE.md` (7.36) ; leurs consignes restent archivées dans `docs/consignes/`.
"""

from __future__ import annotations

from .llm import LLM, ErreurLLM, extraire_json
from .models import ClauseRetenue, Decision, Faits, Verdict


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
