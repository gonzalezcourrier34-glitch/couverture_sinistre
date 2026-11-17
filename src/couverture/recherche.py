"""Étape 3 — Recherche des clauses utiles.

Recherche hybride, sur le modèle de SortirIA (`app/search_query.py`) :
  - par les mots : BM25, qui retrouve les termes juridiques précis (« effraction », « dépendance ») ;
  - par le sens : embeddings Mistral, qui rapprochent « on m'a piqué mon vélo » de « vol » ;
  - fusion des rangs (RRF) : score = 1/(60 + rang mots) + 1/(60 + rang sens).
Sans embeddings (pas de clé), la recherche se fait par les mots seuls.

La recherche seule ne suffit pas pour un contrat d'assurance : l'exclusion qui fait basculer
la décision est souvent loin de la garantie et n'emploie pas les mots du client.
On complète donc la recherche lexicale par l'enveloppe structurelle du contrat :
  1. les exclusions, conditions et limites de la même section que chaque garantie trouvée ;
  2. les exclusions générales qui recoupent le sinistre ;
  3. les clauses visées par un renvoi (« au sens de l'article 1.5 ») ;
  4. les définitions des termes employés dans les clauses retenues.
"""

from __future__ import annotations

import math
from collections import Counter

from .models import Clause, ClauseRetenue, TypeClause
from .texte import jetons, normaliser


class BM25:
    def __init__(self, documents: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.docs = [Counter(d) for d in documents]
        self.longueurs = [len(d) for d in documents]
        self.longueur_moy = sum(self.longueurs) / max(len(documents), 1)
        n = len(documents)
        df = Counter(t for d in documents for t in set(d))
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def scores(self, requete: list[str]) -> list[float]:
        resultats = []
        for doc, longueur in zip(self.docs, self.longueurs):
            s = 0.0
            for t in set(requete):
                if t not in doc:
                    continue
                tf = doc[t]
                s += self.idf[t] * tf * (self.k1 + 1) / (tf + self.k1 * (1 - self.b + self.b * longueur / self.longueur_moy))
            resultats.append(s)
        return resultats


RRF_K = 60     # fusion des rangs : 1 / (60 + rang), comme dans SortirIA
POOL = 30      # rangs pris en compte dans chaque classement


def texte_a_vectoriser(c: Clause) -> str:
    """Ce qu'on donne au modèle d'embeddings pour une clause : son chemin de titres et son texte."""
    return " > ".join(c.chemin) + "\n" + c.texte


def cosinus(a: list[float], b: list[float]) -> float:
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / (na * nb) if na and nb else 0.0


def rangs(scores: list[float], seuil: float = 0.0) -> dict[int, int]:
    """Rang (1, 2, …) des POOL meilleurs indices dont le score dépasse le seuil."""
    ordre = sorted((i for i, s in enumerate(scores) if s > seuil), key=lambda i: scores[i], reverse=True)
    return {i: r for r, i in enumerate(ordre[:POOL], start=1)}


class Recherche:
    def __init__(self, clauses: list[Clause], vecteurs: dict[str, list[float]] | None = None,
                 vectoriseur=None):
        """`vecteurs` : embeddings des clauses (calculés à l'ingestion) ; `vectoriseur` : pour vectoriser
        la question. Il faut les deux pour la recherche par le sens."""
        self.clauses = clauses
        # Les titres sont répétés pour peser davantage que le corps du texte.
        corpus = [jetons((" ".join(c.chemin) + " ") * 2 + c.texte) for c in clauses]
        self.bm25 = BM25(corpus)
        self.vecteurs = vecteurs or {}
        self.vectoriseur = vectoriseur if self.vecteurs else None

    @property
    def hybride(self) -> bool:
        return self.vectoriseur is not None

    def scores_sens(self, question: str) -> list[float] | None:
        if not self.hybride:
            return None
        q = self.vectoriseur.vectoriser([question])[0]
        return [cosinus(q, self.vecteurs[c.id]) if c.id in self.vecteurs else -1.0 for c in self.clauses]

    def rechercher(self, requete: str, k: int = 5, max_clauses: int = 14,
                   question: str | None = None) -> list[ClauseRetenue]:
        """`requete` : description enrichie du vocabulaire du contrat (pour les mots) ;
        `question` : description d'origine (pour le sens), par défaut la requête."""
        scores = self.bm25.scores(jetons(requete))
        rang_mots = rangs(scores)
        sens = self.scores_sens(question or requete)
        rang_sens = rangs(sens, seuil=-1.0) if sens else {}
        fusion = [
            (1 / (RRF_K + rang_mots[i]) if i in rang_mots else 0.0)
            + (1 / (RRF_K + rang_sens[i]) if i in rang_sens else 0.0)
            for i in range(len(self.clauses))
        ]
        retenues: dict[str, ClauseRetenue] = {}

        def ajouter(i: int, raison: str) -> None:
            c = self.clauses[i]
            if c.id not in retenues:
                retenues[c.id] = ClauseRetenue(clause=c, score=round(fusion[i], 4), raison=raison)

        def origine(i: int) -> str:
            if i in rang_mots and i in rang_sens and rang_mots[i] <= k and rang_sens[i] <= k:
                return "pertinente par les mots et par le sens"
            if i in rang_sens and (i not in rang_mots or rang_sens[i] < rang_mots[i]):
                return "pertinente par le sens"
            return "pertinente par les mots"

        classement = sorted(range(len(self.clauses)), key=lambda i: fusion[i], reverse=True)
        for i in classement[:k]:
            if fusion[i] > 0:
                ajouter(i, origine(i))

        # 1. Enveloppe : les exclusions, conditions et limites voisines (même section) et les
        #    sous-sections (« 2.10 Vol » → « 2.10-a Exclusions ») de chaque garantie ou exclusion trouvée.
        enveloppe = (TypeClause.EXCLUSION, TypeClause.CONDITION, TypeClause.LIMITE)
        ancres = [r.clause for r in retenues.values() if r.clause.type in (TypeClause.GARANTIE, TypeClause.EXCLUSION)]
        for a in ancres:
            for i, c in enumerate(self.clauses):
                if c.groupe == a.id and c.type in enveloppe + (TypeClause.GARANTIE,):
                    ajouter(i, f"sous-section de {a.id}")
                elif c.groupe == a.groupe and c.type in enveloppe:
                    ajouter(i, f"même section que {a.id}")

        # 2. Exclusions générales qui recoupent le sinistre.
        for i, c in enumerate(self.clauses):
            proche = scores[i] > 0 or rang_sens.get(i, POOL + 1) <= 2 * k
            if c.type == TypeClause.EXCLUSION and "general" in normaliser(" ".join(c.chemin)) and proche:
                ajouter(i, "exclusion générale")

        # 3. Renvois explicites (« dans les conditions de l'article 4.2 »).
        index = {c.id: i for i, c in enumerate(self.clauses)}
        for r in list(retenues.values()):
            for cible in r.clause.renvois:
                if cible in index:
                    ajouter(index[cible], f"renvoi depuis {r.clause.id}")

        # 4. Définitions des termes présents dans les clauses retenues ou dans la requête.
        contexte = normaliser(requete + " " + " ".join(r.clause.texte for r in retenues.values()))
        for i, c in enumerate(self.clauses):
            if c.type == TypeClause.DEFINITION and normaliser(c.titre) in contexte:
                ajouter(i, "définition d'un terme employé")

        # Tri dans l'ordre du contrat, plafonné en gardant les meilleurs scores.
        selection = sorted(retenues.values(), key=lambda r: r.score, reverse=True)[:max_clauses]
        ordre = {c.id: n for n, c in enumerate(self.clauses)}
        return sorted(selection, key=lambda r: ordre[r.clause.id])
