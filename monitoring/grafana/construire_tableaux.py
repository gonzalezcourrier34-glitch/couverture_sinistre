"""Génère les tableaux de bord Grafana, comme `construire_tableau_modeles.py` dans SortirIA.

Les requêtes sont écrites ici, lisibles, et non dans un JSON de 2 000 lignes. Un test les
exécute toutes sur une vraie base SQLite et échoue si le JSON n'est plus à jour.

    python -m monitoring.grafana.construire_tableaux

Grafana lit directement la base SQLite du projet (`data/base.sqlite`), avec le plugin
`frser-sqlite-datasource`. Deux tableaux :
  - « Couverture sinistre — Réponses » : usage, décisions, fiabilité (contrôle des citations),
    temps de réponse, ce qui manque, versions des consignes en service, erreurs ;
  - « Couverture sinistre — Contrats » : lecture de chaque contrat, alertes, clauses par type.
"""

from __future__ import annotations

import json
from pathlib import Path

DOSSIER = Path(__file__).parent / "provisioning" / "dashboards"
SOURCE = {"type": "frser-sqlite-datasource", "uid": "couverture-sqlite"}

# Période choisie en haut du tableau (macros du plugin SQLite).
PERIODE = "unixepoch(date) BETWEEN $__unixEpochFrom() AND $__unixEpochTo()"
JOUR = "unixepoch(date(date))"
OK = "erreur IS NULL"


def panneau(titre, sql, genre="timeseries", largeur=12, hauteur=8, description="", unite=None, empile=False):
    serie = genre == "timeseries"
    p = {
        "title": titre,
        "type": genre,
        "description": description,
        "datasource": SOURCE,
        "targets": [{
            "refId": "A", "datasource": SOURCE,
            "queryText": sql, "rawQueryText": sql,
            "queryType": "time series" if serie else "table",
            "timeColumns": ["time"] if serie else [],
        }],
        "fieldConfig": {"defaults": {}, "overrides": []},
        "options": {},
        "_taille": (largeur, hauteur),
    }
    if unite:
        p["fieldConfig"]["defaults"]["unit"] = unite
    if serie:
        p["fieldConfig"]["defaults"]["custom"] = {"drawStyle": "bars" if empile else "line", "fillOpacity": 60 if empile else 10,
                                                  "stacking": {"mode": "normal" if empile else "none"}}
    if genre == "stat":
        p["options"] = {"reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False}, "colorMode": "value"}
    return p


def titre_section(titre):
    return {"type": "row", "title": titre, "collapsed": False, "panels": [], "_taille": (24, 1)}


def placer(panneaux):
    """Calcule les positions (grille Grafana de 24 colonnes), de gauche à droite puis de haut en bas."""
    x = y = hauteur_ligne = 0
    for i, p in enumerate(panneaux, start=1):
        largeur, hauteur = p.pop("_taille")
        if x + largeur > 24:
            x, y, hauteur_ligne = 0, y + hauteur_ligne, 0
        p["gridPos"] = {"x": x, "y": y, "w": largeur, "h": hauteur}
        p["id"] = i
        x += largeur
        hauteur_ligne = max(hauteur_ligne, hauteur)
        if x >= 24:
            x, y, hauteur_ligne = 0, y + hauteur_ligne, 0
    return panneaux


def tableau(uid, titre, panneaux, description):
    return {
        "uid": uid, "title": titre, "description": description,
        "tags": ["couverture-sinistre"], "timezone": "browser", "schemaVersion": 39, "version": 1,
        "editable": True, "refresh": "5m",
        "time": {"from": "now-30d", "to": "now"},
        "panels": placer(panneaux),
    }


def tableau_reponses() -> dict:
    p = [
        titre_section("Usage"),
        panneau("Analyses", f"SELECT COUNT(*) AS analyses FROM analyses WHERE {OK} AND {PERIODE}", "stat", 6, 4),
        panneau("Part d'INCERTAIN", f"SELECT AVG(decision = 'INCERTAIN') AS incertain FROM analyses WHERE {OK} AND {PERIODE}",
                "stat", 6, 4, "Trop haut : le système ne tranche presque jamais. Trop bas sur des cas ambigus : il tranche au hasard.", "percentunit"),
        panneau("Réponses fermes (couvert / non couvert)",
                f"SELECT AVG(decision != 'INCERTAIN') AS fermes FROM analyses WHERE {OK} AND {PERIODE}",
                "stat", 6, 4, "Part des réponses tranchées sans question à poser.", "percentunit"),
        panneau("Erreurs du modèle", f"SELECT COUNT(*) AS erreurs FROM analyses WHERE erreur IS NOT NULL AND {PERIODE}", "stat", 6, 4),
        panneau("Décisions par jour",
                f"""SELECT {JOUR} AS time,
       SUM(decision = 'COUVERT') AS couvert,
       SUM(decision = 'NON_COUVERT') AS non_couvert,
       SUM(decision = 'INCERTAIN') AS incertain
FROM analyses WHERE {OK} AND {PERIODE}
GROUP BY date(date) ORDER BY time""", empile=True),
        panneau("Part d'INCERTAIN par jour",
                f"SELECT {JOUR} AS time, AVG(decision = 'INCERTAIN') AS incertain FROM analyses WHERE {OK} AND {PERIODE} "
                f"GROUP BY date(date) ORDER BY time", unite="percentunit"),
        titre_section("Fiabilité : ce que les contrôles rattrapent"),
        panneau("Rattrapages par jour",
                f"""SELECT {JOUR} AS time,
       SUM(decision_initiale != decision) AS corrigees_par_controle,
       SUM(citations_rejetees + conditions_ecartees) AS preuves_ecartees
FROM analyses WHERE {OK} AND {PERIODE}
GROUP BY date(date) ORDER BY time""",
                description="Réponses corrigées par le contrôle des citations, citations ou conditions écartées faute de preuve."),
        panneau("Temps de réponse par jour",
                f"SELECT {JOUR} AS time, AVG(duree_ms) AS moyen, MAX(duree_ms) AS maximum FROM analyses WHERE {OK} AND {PERIODE} "
                f"GROUP BY date(date) ORDER BY time", unite="ms"),
        panneau("INCERTAIN par contrat",
                f"""SELECT contrat_id AS contrat, COUNT(*) AS analyses,
       ROUND(AVG(decision = 'INCERTAIN'), 2) AS part_incertain,
       ROUND(AVG(confiance), 2) AS confiance_moyenne,
       SUM(contestations > 0) AS contestees
FROM analyses WHERE {OK} AND {PERIODE}
GROUP BY contrat_id ORDER BY part_incertain DESC""", "table",
                description="Un contrat dont la part d'INCERTAIN est anormale est souvent un contrat mal lu."),
        panneau("Sinistres déclarés",
                f"SELECT evenement, bien, lieu, COUNT(*) AS analyses FROM analyses WHERE {OK} AND {PERIODE} "
                f"GROUP BY evenement, bien, lieu ORDER BY analyses DESC LIMIT 20", "table"),
        titre_section("Ce qui manque, versions, erreurs"),
        panneau("Questions à poser à l'assuré les plus fréquentes",
                f"""SELECT q.value AS question, COUNT(*) AS fois
FROM analyses, json_each(analyses.questions) AS q
WHERE {OK} AND {PERIODE}
GROUP BY q.value ORDER BY fois DESC LIMIT 15""", "table", 12, 9,
                "Les informations à aller chercher ailleurs : souvent les conditions particulières."),
        panneau("Versions des consignes en service",
                f"""SELECT consignes, juge, MIN(date) AS depuis, COUNT(*) AS analyses,
       ROUND(AVG(decision = 'INCERTAIN'), 2) AS part_incertain,
       SUM(contestations > 0) AS contestees, CAST(AVG(duree_ms) AS INTEGER) AS duree_moyenne_ms
FROM analyses WHERE {OK} AND {PERIODE}
GROUP BY consignes, juge ORDER BY depuis DESC""", "table", 12, 9,
                "Chaque réponse porte les versions des consignes et le modèle qui l'ont produite (voir `couverture versions`)."),
        panneau("Dernières erreurs",
                f"SELECT date, contrat_id AS contrat, methode, erreur FROM analyses WHERE erreur IS NOT NULL AND {PERIODE} "
                f"ORDER BY date DESC LIMIT 20", "table", 24, 7),
    ]
    return tableau("couverture-reponses", "Couverture sinistre — Réponses", p,
                   "Ce que le système répond, ce que ses contrôles rattrapent, et ce qui lui manque. Source : table `analyses`.")


def tableau_contrats() -> dict:
    p = [
        panneau("Contrats", "SELECT COUNT(*) AS contrats FROM contrats", "stat", 6, 4),
        panneau("À vérifier", "SELECT COUNT(*) AS a_verifier FROM contrats WHERE statut != 'OK'", "stat", 6, 4,
                "Contrats mal lus selon les contrôles du découpage : un profil d'assureur corrige."),
        panneau("Clauses", "SELECT COUNT(*) AS clauses FROM clauses", "stat", 12, 4),
        panneau("Lecture des contrats",
                """SELECT id AS contrat, assureur, produit, version, statut,
       json_extract(rapport, '$.nb_clauses') AS clauses,
       json_array_length(json_extract(rapport, '$.alertes')) AS alertes,
       ingere_le
FROM contrats ORDER BY statut DESC, id""", "table", 24, 8),
        panneau("Clauses par type",
                """SELECT contrat_id AS contrat,
       SUM(type = 'garantie') AS garanties, SUM(type = 'exclusion') AS exclusions,
       SUM(type = 'condition') AS conditions, SUM(type = 'limite') AS limites,
       SUM(type = 'definition') AS definitions, SUM(type = 'autre') AS sans_type
FROM clauses GROUP BY contrat_id ORDER BY contrat_id""", "table", 12, 8,
                "Un contrat sans exclusion, ou avec beaucoup de clauses sans type, a été mal lu."),
        panneau("Alertes",
                """SELECT c.id AS contrat, a.value AS alerte
FROM contrats AS c, json_each(json_extract(c.rapport, '$.alertes')) AS a
ORDER BY c.id""", "table", 12, 8),
    ]
    return tableau("couverture-contrats", "Couverture sinistre — Contrats", p,
                   "Comment chaque contrat a été lu. Source : tables `contrats` et `clauses`.")


TABLEAUX = {"couverture-reponses.json": tableau_reponses, "couverture-contrats.json": tableau_contrats}


def contenu(fabrique) -> str:
    return json.dumps(fabrique(), ensure_ascii=False, indent=2) + "\n"


def ecrire() -> list[Path]:
    DOSSIER.mkdir(parents=True, exist_ok=True)
    chemins = []
    for nom, fabrique in TABLEAUX.items():
        chemin = DOSSIER / nom
        chemin.write_text(contenu(fabrique), encoding="utf-8")
        chemins.append(chemin)
    return chemins


if __name__ == "__main__":
    for c in ecrire():
        print(f"Écrit : {c}")
