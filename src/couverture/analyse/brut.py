"""La référence « chatbot » (DEMARCHE 7.237) : tout le contrat dans le message, un seul appel, le modèle conclut.

C'est la solution simple que la lecture des clauses doit battre pour justifier sa construction : ni désignation, ni
dossier, ni jugement clause par clause, ni logique fixe, ni règles. La consigne est celle de l'ancienne méthode
`brut` (retirée en 7.110 sans avoir été passée sur les jeux de mesure), reprise telle qu'archivée :
`docs/consignes/document-brut/v1.txt`. Rien n'y est ajouté, pour mesurer la référence et non une version améliorée.

Le contrôle des citations est seulement compté : une réponse ferme dont aucun extrait ne se retrouve dans le
contrat n'est pas changée (le chatbot ne le ferait pas), mais le bilan dit combien il y en a.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from ..consignes import ARCHIVE
from ..llm import LLM, extraire_json
from ..models import Clause, Decision

VERSION = "v1"


def consigne() -> str:
    """Le texte archivé de la consigne, lu à chaque appel de la commande (il n'est jamais réécrit)."""
    return (ARCHIVE / "document-brut" / f"{VERSION}.txt").read_text(encoding="utf-8").strip()


def message(clauses: list[Clause], declaration: str) -> str:
    """Le contrat entier, clause par clause dans l'ordre du document, puis la déclaration à la fin : le début de
    l'envoi est le même pour tous les sinistres d'un contrat, et le fournisseur le reprend de son cache."""
    blocs = [f"[{c.id}] {' > '.join(c.chemin)}\n{c.texte}" for c in clauses]
    return "## Conditions générales\n" + "\n\n".join(blocs) + f"\n\n## Sinistre\n{declaration}"


def _plat(t: str) -> str:
    """Pour retrouver un extrait : sans accents, sans casse, sans ponctuation, espaces réduits."""
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", t)).strip()


@dataclass
class Avis:
    """La réponse du modèle, telle qu'il l'a donnée, et ce que le contrôle des citations en dit."""

    decision: Decision
    justification: str = ""
    citations: list[dict] = field(default_factory=list)
    retrouvees: int = 0            # extraits retrouvés mot pour mot (à la ponctuation près) dans le contrat
    manquantes: list[str] = field(default_factory=list)

    @property
    def ferme_sans_preuve(self) -> bool:
        """Une réponse ferme sans aucun extrait retrouvé : ce que la lecture des clauses aurait refusé."""
        return self.decision != Decision.INCERTAIN and self.retrouvees == 0


def lire(clauses: list[Clause], llm: LLM, declaration: str) -> Avis:
    """Un appel ; une réponse illisible lève `ValueError` (la commande la compte comme une erreur du cas)."""
    donnees = extraire_json(llm.completer(consigne(), message(clauses, declaration)))
    try:
        decision = Decision(str(donnees.get("decision", "")).strip().upper())
    except ValueError:
        decision = Decision.INCERTAIN
    citations = [c for c in donnees.get("citations") or [] if isinstance(c, dict)]
    texte = _plat(" ".join(c.texte for c in clauses))
    retrouvees, manquantes = 0, []
    for c in citations:
        # Un extrait coupé (« … ») se retrouve morceau par morceau.
        morceaux = [_plat(m) for m in re.split(r"\.\.\.|…|\[\.\.\.\]", str(c.get("extrait", "")))]
        morceaux = [m for m in morceaux if m]
        if morceaux and all(m in texte for m in morceaux):
            retrouvees += 1
        else:
            manquantes.append(str(c.get("clause_id", "?")))
    return Avis(decision, str(donnees.get("justification", "")), citations, retrouvees, manquantes)
