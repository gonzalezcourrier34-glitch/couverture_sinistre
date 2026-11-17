"""Stockage multi-contrats (SQLite).

Chaque contrat est lu et découpé une seule fois, à l'ingestion. Les questions
portent ensuite sur un contrat précis : on ne mélange jamais les clauses de deux contrats.

Tables :
  contrats(id, assureur, produit, version, fichier, empreinte, statut, rapport, texte_brut, ingere_le)
  clauses(contrat_id, id, ordre, article, groupe, titre, chemin, texte, type, pages)
  renvois(contrat_id, source_id, cible_id)
  vecteurs(contrat_id, clause_id, modele, vecteur)   embeddings des clauses, un jeu par modèle
  compilations(contrat_id, empreinte, donnees)      contrat compilé en fiches (voir compilation.py)

Les compilations ne sont pas effacées par une ré-ingestion : elles coûtent des appels au
modèle et peuvent avoir été relues par un humain. Leur empreinte dit à quel contrat elles
correspondent ; une compilation dont l'empreinte ne correspond plus est ignorée.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel

from .models import Clause, ContratCompile, TypeClause

SCHEMA = """
CREATE TABLE IF NOT EXISTS contrats (
    id TEXT PRIMARY KEY,
    assureur TEXT, produit TEXT, version TEXT,
    fichier TEXT, empreinte TEXT,
    statut TEXT, rapport TEXT,
    texte_brut TEXT,
    ingere_le TEXT
);
CREATE TABLE IF NOT EXISTS clauses (
    contrat_id TEXT REFERENCES contrats(id) ON DELETE CASCADE,
    id TEXT, ordre INTEGER, article TEXT, groupe TEXT,
    titre TEXT, chemin TEXT, texte TEXT, type TEXT, pages TEXT,
    PRIMARY KEY (contrat_id, id)
);
CREATE TABLE IF NOT EXISTS renvois (
    contrat_id TEXT REFERENCES contrats(id) ON DELETE CASCADE,
    source_id TEXT, cible_id TEXT
);
CREATE TABLE IF NOT EXISTS vecteurs (
    contrat_id TEXT REFERENCES contrats(id) ON DELETE CASCADE,
    clause_id TEXT, modele TEXT, vecteur TEXT,
    PRIMARY KEY (contrat_id, clause_id, modele)
);
CREATE TABLE IF NOT EXISTS compilations (
    contrat_id TEXT PRIMARY KEY,
    empreinte TEXT, donnees TEXT
);
CREATE INDEX IF NOT EXISTS idx_clauses_type ON clauses(contrat_id, type);
CREATE INDEX IF NOT EXISTS idx_clauses_groupe ON clauses(contrat_id, groupe);
"""


class Contrat(BaseModel):
    id: str
    assureur: str = ""
    produit: str = ""
    version: str = ""
    fichier: str = ""
    empreinte: str = ""
    statut: str = ""
    rapport: dict = {}
    ingere_le: str = ""


class Base:
    def __init__(self, chemin: str | Path):
        self.chemin = str(chemin)
        Path(self.chemin).parent.mkdir(parents=True, exist_ok=True)
        with self._cx() as cx:
            cx.executescript(SCHEMA)

    def _cx(self) -> sqlite3.Connection:
        cx = sqlite3.connect(self.chemin)
        cx.execute("PRAGMA foreign_keys = ON")
        return cx

    def enregistrer(self, contrat: Contrat, clauses: list[Clause], texte_brut: str) -> None:
        """Remplace entièrement le contrat (ré-ingestion idempotente)."""
        contrat.ingere_le = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._cx() as cx:
            cx.execute("DELETE FROM contrats WHERE id = ?", (contrat.id,))
            cx.execute(
                "INSERT INTO contrats VALUES (?,?,?,?,?,?,?,?,?,?)",
                (contrat.id, contrat.assureur, contrat.produit, contrat.version, contrat.fichier,
                 contrat.empreinte, contrat.statut, json.dumps(contrat.rapport, ensure_ascii=False),
                 texte_brut, contrat.ingere_le),
            )
            cx.executemany(
                "INSERT INTO clauses VALUES (?,?,?,?,?,?,?,?,?,?)",
                [
                    (contrat.id, c.id, i, c.article, c.groupe, c.titre, json.dumps(c.chemin, ensure_ascii=False),
                     c.texte, c.type.value, json.dumps(c.pages))
                    for i, c in enumerate(clauses)
                ],
            )
            cx.executemany(
                "INSERT INTO renvois VALUES (?,?,?)",
                [(contrat.id, c.id, cible) for c in clauses for cible in c.renvois],
            )

    def contrats(self) -> list[Contrat]:
        with self._cx() as cx:
            lignes = cx.execute(
                "SELECT id, assureur, produit, version, fichier, empreinte, statut, rapport, ingere_le FROM contrats ORDER BY id"
            ).fetchall()
        return [
            Contrat(id=l[0], assureur=l[1], produit=l[2], version=l[3], fichier=l[4], empreinte=l[5],
                    statut=l[6], rapport=json.loads(l[7] or "{}"), ingere_le=l[8])
            for l in lignes
        ]

    def contrat(self, contrat_id: str) -> Contrat:
        for c in self.contrats():
            if c.id == contrat_id:
                return c
        raise KeyError(f"Contrat inconnu : {contrat_id}")

    def empreinte(self, contrat_id: str) -> str | None:
        with self._cx() as cx:
            l = cx.execute("SELECT empreinte FROM contrats WHERE id = ?", (contrat_id,)).fetchone()
        return l[0] if l else None

    def texte_brut(self, contrat_id: str) -> str:
        with self._cx() as cx:
            l = cx.execute("SELECT texte_brut FROM contrats WHERE id = ?", (contrat_id,)).fetchone()
        if not l:
            raise KeyError(f"Contrat inconnu : {contrat_id}")
        return l[0]

    def clauses(self, contrat_id: str) -> list[Clause]:
        with self._cx() as cx:
            lignes = cx.execute(
                "SELECT id, article, groupe, titre, chemin, texte, type, pages FROM clauses "
                "WHERE contrat_id = ? ORDER BY ordre",
                (contrat_id,),
            ).fetchall()
            renvois = cx.execute("SELECT source_id, cible_id FROM renvois WHERE contrat_id = ?", (contrat_id,)).fetchall()
        par_source: dict[str, list[str]] = {}
        for s, c in renvois:
            par_source.setdefault(s, []).append(c)
        if not lignes:
            raise KeyError(f"Contrat inconnu ou vide : {contrat_id}")
        return [
            Clause(id=l[0], article=l[1], groupe=l[2], titre=l[3], chemin=json.loads(l[4]), texte=l[5],
                   type=TypeClause(l[6]), pages=json.loads(l[7]), renvois=par_source.get(l[0], []))
            for l in lignes
        ]

    def enregistrer_vecteurs(self, contrat_id: str, modele: str, vecteurs: dict[str, list[float]]) -> None:
        with self._cx() as cx:
            cx.execute("DELETE FROM vecteurs WHERE contrat_id = ? AND modele = ?", (contrat_id, modele))
            cx.executemany(
                "INSERT INTO vecteurs VALUES (?,?,?,?)",
                [(contrat_id, cid, modele, json.dumps(v)) for cid, v in vecteurs.items()],
            )

    def vecteurs(self, contrat_id: str, modele: str) -> dict[str, list[float]]:
        with self._cx() as cx:
            lignes = cx.execute(
                "SELECT clause_id, vecteur FROM vecteurs WHERE contrat_id = ? AND modele = ?", (contrat_id, modele)
            ).fetchall()
        return {cid: json.loads(v) for cid, v in lignes}

    def maj_rapport(self, contrat_id: str, rapport: dict) -> None:
        """Met à jour le rapport et le statut qu'il porte (un juge peut faire passer un contrat à A_VERIFIER)."""
        with self._cx() as cx:
            cx.execute("UPDATE contrats SET rapport = ?, statut = COALESCE(?, statut) WHERE id = ?",
                       (json.dumps(rapport, ensure_ascii=False), rapport.get("statut"), contrat_id))

    def supprimer(self, contrat_id: str) -> None:
        """Retire un contrat et tout ce qui en dépend (clauses, renvois, vecteurs)."""
        with self._cx() as cx:
            cx.execute("DELETE FROM contrats WHERE id = ?", (contrat_id,))
            cx.execute("DELETE FROM compilations WHERE contrat_id = ?", (contrat_id,))

    def enregistrer_compilation(self, compilation: ContratCompile) -> None:
        with self._cx() as cx:
            cx.execute("INSERT OR REPLACE INTO compilations VALUES (?,?,?)",
                       (compilation.contrat_id, compilation.empreinte, compilation.model_dump_json()))

    def compilation(self, contrat_id: str, a_jour: bool = True) -> ContratCompile | None:
        """Le contrat compilé ; avec `a_jour`, seulement s'il correspond au contrat actuellement en base."""
        with self._cx() as cx:
            l = cx.execute("SELECT empreinte, donnees FROM compilations WHERE contrat_id = ?", (contrat_id,)).fetchone()
        if not l:
            return None
        if a_jour and l[0].split(":")[0] != (self.empreinte(contrat_id) or ""):
            return None
        return ContratCompile.model_validate_json(l[1])
