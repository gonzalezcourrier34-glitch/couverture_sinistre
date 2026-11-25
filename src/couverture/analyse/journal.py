"""Journal des analyses : chaque question posée au système, et ce qu'il a répondu.

Sert à trois choses, comme le journal des recherches de SortirIA (`app/search_log.py`) :
  - mesurer en production ce que l'évaluation ne voit pas (taux d'INCERTAIN réel, contestations) ;
  - repérer ce qui manque : les questions à poser qui reviennent sans cesse (souvent les
    conditions particulières : « l'option est-elle souscrite ? ») ;
  - suivre la dérive dans Grafana (monitoring/).

Le texte du sinistre n'est pas conservé : seulement sa longueur et les faits repérés
(événement, bien, lieu). Une déclaration de sinistre peut contenir des données personnelles.

En ligne (23/11/2026, DEMARCHE 7.163), la base vit dans le conteneur et repart de l'image à chaque réveil : le
journal y serait perdu. Quand `COUVERTURE_JOURNAL_SORTIE` est défini (l'image en ligne le fait), chaque ligne
est aussi écrite sur la sortie standard, en JSON, que l'hébergeur collecte. La même ligne, donc sans le texte.
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone

from ..consignes import versions_courtes
from ..models import Resultat

SCHEMA_JOURNAL = """
CREATE TABLE IF NOT EXISTS analyses (
    date TEXT, contrat_id TEXT, methode TEXT, juge TEXT,
    decision TEXT, decision_initiale TEXT, decision_avant_relecture TEXT,
    confiance REAL, longueur INTEGER,
    evenement TEXT, bien TEXT, lieu TEXT,
    citations_rejetees INTEGER, conditions_ecartees INTEGER, contestations INTEGER,
    questions TEXT, duree_ms INTEGER, erreur TEXT,
    consignes TEXT
);
CREATE INDEX IF NOT EXISTS idx_analyses_date ON analyses(date);
"""
COLONNES = ("date", "contrat_id", "methode", "juge", "decision", "decision_initiale", "decision_avant_relecture",
            "confiance", "longueur", "evenement", "bien", "lieu", "citations_rejetees", "conditions_ecartees",
            "contestations", "questions", "duree_ms", "erreur", "consignes")


def sortie(ligne: dict) -> None:
    """Écrit la ligne du journal sur la sortie standard, si `COUVERTURE_JOURNAL_SORTIE` est défini."""
    if os.getenv("COUVERTURE_JOURNAL_SORTIE"):
        print(json.dumps({"journal": "analyse", **ligne}, ensure_ascii=False), flush=True)


class Journal:
    """Le journal des analyses, dans la base ; la table est créée (ou complétée) à l'ouverture."""

    def __init__(self, chemin_base: str):
        self.chemin = chemin_base
        with sqlite3.connect(self.chemin) as cx:
            cx.executescript(SCHEMA_JOURNAL)
            colonnes = {r[1] for r in cx.execute("PRAGMA table_info(analyses)")}
            if "consignes" not in colonnes:  # journal créé avant le versionnage des consignes
                cx.execute("ALTER TABLE analyses ADD COLUMN consignes TEXT")

    def noter(self, r: Resultat, duree_ms: int = 0, date: datetime | None = None) -> None:
        """Note une analyse : décision, confiance, faits repérés, points à préciser, durée, versions des consignes. Le texte
        de la déclaration n'est pas gardé, seulement sa longueur."""
        v = r.verdict
        ligne = (
            (date or datetime.now(timezone.utc)).isoformat(timespec="seconds"),
            r.contrat_id, r.methode, v.mode,
            v.decision.value,
            (v.decision_initiale or v.decision).value,
            v.decision_avant_relecture.value if v.decision_avant_relecture else None,
            v.confiance, len(r.sinistre),
            (r.faits.evenements or ["inconnu"])[0], (r.faits.biens or ["inconnu"])[0], (r.faits.lieux or ["inconnu"])[0],
            sum(not c.valide for c in v.citations),
            sum(not c.valide for c in v.conditions),
            sum(c.relecture == "contestee" for c in v.conditions),
            json.dumps(v.informations_manquantes, ensure_ascii=False), duree_ms, None,
            versions_courtes(),  # versions des consignes en service : quelle consigne a produit cette réponse
        )
        with sqlite3.connect(self.chemin) as cx:
            cx.execute(f"INSERT INTO analyses VALUES ({','.join('?' * 19)})", ligne)
        sortie(dict(zip(COLONNES, ligne, strict=True)))

    def noter_erreur(self, contrat_id: str, methode: str, erreur: str, date: datetime | None = None) -> None:
        """Note une analyse qui a échoué, avec le début du message d'erreur."""
        ligne = ((date or datetime.now(timezone.utc)).isoformat(timespec="seconds"), contrat_id, methode, erreur[:300])
        with sqlite3.connect(self.chemin) as cx:
            cx.execute("INSERT INTO analyses (date, contrat_id, methode, erreur) VALUES (?,?,?,?)", ligne)
        sortie(dict(zip(("date", "contrat_id", "methode", "erreur"), ligne, strict=True)))

    def lignes(self, depuis: datetime, jusqua: datetime) -> list[dict]:
        """Les analyses notées entre deux dates."""
        with sqlite3.connect(self.chemin) as cx:
            cx.row_factory = sqlite3.Row
            rows = cx.execute(
                "SELECT * FROM analyses WHERE date >= ? AND date < ? ORDER BY date",
                (depuis.isoformat(timespec="seconds"), jusqua.isoformat(timespec="seconds")),
            ).fetchall()
        return [dict(r) for r in rows]
