# Suivi : MLflow et Grafana

Ce qui est surveillé, comment, et où le voir. Organisation reprise de SortirIA.

## Lancement

```bash
docker compose up -d --build
```

| Service | Adresse | Rôle |
|---|---|---|
| Application | http://localhost:8020 | L'interface ; lit `data/contrats` au démarrage |
| MLflow | http://localhost:5010 | Exécutions (ingestions, bancs) et registre des consignes |
| Grafana | http://localhost:3011 | Tableaux de bord (identifiant `admin`, mot de passe `GRAFANA_ADMIN_PASSWORD` du `.env`) |

Les ports évitent ceux de SortirIA (5000, 3001, 8010) : les deux projets peuvent tourner en même temps.

Sans docker : `uv sync --extra dev --extra suivi` installe MLflow ; les exécutions vont alors dans `data/mlflow/mlflow.db`, à consulter avec `mlflow ui --backend-store-uri sqlite:///data/mlflow/mlflow.db`.

## Les couches

| Couche | Ce qu'on y voit | Où |
|---|---|---|
| **Banc** | Le golden set rejoué : règles, lecture, chaîne, portes ; un rapport par passage | `couverture banc`, `data/bancs/`, `docs/METRIQUES.md` |
| **Journal** | Une ligne par analyse : décision (avant contrôle et finale), confiance, faits, questions, durée, versions des consignes. Jamais le texte du sinistre | table `analyses`, `src/couverture/journal.py` |
| **Grafana** | Deux tableaux, lus directement dans la base SQLite | `monitoring/grafana/` |
| **MLflow** | Une exécution par ingestion et par banc ; le registre des consignes | `src/couverture/suivi.py`, `src/couverture/consignes.py` |

## MLflow

**Expérience `couverture-ingestion`** : une exécution par `couverture ingerer` ; métriques par contrat `contrat/<id>/clauses/<type>`, `…/alertes`, `…/ok` ; artefact `rapports.json`.

**Expérience `couverture-evaluation`** : une exécution par `couverture banc`.
- paramètres : contrat, méthode (`regles` ou `brut`), modèle de lecture, version du golden set, versions de chaque consigne ;
- métriques : toutes celles du banc, par couche (`regles/exactitude`, `lecture/decisions_changees`, `chaine/faux_couverts`, `chaine/instables`…), et `portes_passees`.

Usage typique : **comparer deux modèles de lecture** (Mistral Small contre Large) ou deux versions d'une consigne, sur la même version du golden set.

**Registre des consignes (Prompt Registry)** : `couverture versions --enregistrer` crée une version MLflow par texte différent et pose l'alias `production` sur la version en service.

**Garde-fou** : `config/versions_consignes.json` garde la version et l'empreinte de chaque consigne. Si un texte change sans que sa version change dans `src/couverture/consignes.py`, `couverture versions` et la CI échouent.

**Le suivi ne fait jamais échouer le travail** : sans MLflow, avec `MLFLOW_ACTIF=false`, si le serveur ne répond pas en 3 s, ou en cas d'erreur, le travail continue sans suivi.

## Grafana

Source : la base `data/base.sqlite`, montée en lecture seule, avec le plugin `frser-sqlite-datasource`.

- **« Couverture sinistre — Réponses »** (table `analyses`) : analyses, part d'INCERTAIN, réponses fermes, erreurs du modèle ; décisions et INCERTAIN par jour ; réponses corrigées par le contrôle des citations ; temps de réponse ; INCERTAIN par contrat ; questions à poser les plus fréquentes ; versions des consignes en service ; dernières erreurs.
- **« Couverture sinistre — Contrats »** (tables `contrats` et `clauses`) : contrats et contrats à vérifier, lecture de chaque contrat, clauses par type, alertes.

Les tableaux sont **générés** par `python -m monitoring.grafana.construire_tableaux`. Un test exécute chaque requête sur une vraie base SQLite et échoue si le JSON n'a pas été régénéré.

## Retiré le 18 nov. 2026

La dérive (PSI), le bilan hebdomadaire et l'agent de réparation servaient les anciennes méthodes ; ils ont été retirés avec elles (DEMARCHE 7.36). Pour un usage réel, la dérive se suivrait sur les faits lus et la part d'INCERTAIN, depuis le journal.

## Ce qui n'est pas fait

- **Traces des appels au modèle** dans MLflow (prompt, réponse, tokens, durée) : il faudrait instrumenter `llm.py` avec `mlflow.start_span`.
- **Coût** : les tokens ne sont pas encore relevés.
