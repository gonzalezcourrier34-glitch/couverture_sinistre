# Suivi : MLflow, Grafana, dérive et bilan

Ce qui est surveillé, comment, et où le voir. Organisation reprise de SortirIA.

## Lancement

```bash
docker compose up -d --build
```

| Service | Adresse | Rôle |
|---|---|---|
| Application | http://localhost:8020 | L'interface ; lit `data/contrats` au démarrage |
| MLflow | http://localhost:5010 | Exécutions (ingestions, évaluations) et registre des consignes |
| Grafana | http://localhost:3011 | Tableaux de bord (identifiant `admin`, mot de passe `GRAFANA_ADMIN_PASSWORD` du `.env`) |

Les ports évitent ceux de SortirIA (5000, 3001, 8010) : les deux projets peuvent tourner en même temps.

Sans docker : `uv sync --extra dev --extra suivi` (ou `pip install -e ".[suivi]"`) installe MLflow ; les exécutions vont alors dans `data/mlflow/mlflow.db`, à consulter avec `mlflow ui --backend-store-uri sqlite:///data/mlflow/mlflow.db`.

## Les couches, de la plus simple à la plus détaillée

| Couche | Ce qu'on y voit | Où |
|---|---|---|
| **Bilan** | Ce qui demande une intervention, puis les chiffres de la semaine, les questions qui reviennent, la dérive | `couverture bilan [--envoyer]`, `src/couverture/bilan.py` |
| **Journal** | Une ligne par analyse : décision (avant contrôle, avant relecture, finale), confiance, faits, contestations, questions, durée, versions des consignes. Jamais le texte du sinistre | table `analyses`, `src/couverture/journal.py` |
| **Grafana** | Deux tableaux, lus directement dans la base SQLite | `monitoring/grafana/` |
| **MLflow** | Une exécution par ingestion et par évaluation, avec paramètres, métriques et rapport complet ; le registre des consignes | `src/couverture/suivi.py`, `src/couverture/consignes.py` |

## MLflow

**Expérience `couverture-ingestion`** : une exécution par `couverture ingerer`.
- paramètres : versions de chaque consigne, modèle du juge de qualité, modèle d'embeddings ;
- métriques par contrat : `contrat/<id>/clauses/<type>`, `…/alertes`, `…/ok`, `…/qualite_typage` ;
- artefact : `rapports.json`, le rapport de contrôle de chaque contrat.

**Expérience `couverture-evaluation`** : une exécution par `couverture evaluer`, et une par méthode avec `couverture comparer`.
- paramètres : contrat et son empreinte, méthode, modèle du juge, modèle du relecteur, modèle d'embeddings, versions de chaque consigne, empreinte du jeu de test ;
- métriques : `exactitude`, `faux_couverts`, `taux_incertain`, `rappel_clauses_moyen`, `citations_rejetees`, `conditions_contestees`, `decisions_changees_par_relecture`, `faux_couverts_evites_par_relecture`, et leurs valeurs avant contrôle ;
- artefact : `rapport.json`, cas par cas.

Usages typiques :
- **comparer deux versions d'une consigne** sur les mêmes cas : filtrer par `consigne/grille-conditions`, regarder `faux_couverts` et `rappel_clauses_moyen` ;
- **comparer deux modèles** (`mistral-large-latest` contre `mistral-small-latest`) : même jeu de test (même empreinte), autre `modele/juge` ;
- **mesurer la relecture** : `faux_couverts_evites_par_relecture` contre le coût d'un appel de plus.

**Registre des consignes (Prompt Registry)** : `couverture versions --enregistrer` crée une version MLflow par texte différent et pose l'alias `production` sur la version en service. Relancé sans changement, il ne crée rien.

**Garde-fou** : `config/versions_consignes.json` garde la version et l'empreinte de chaque consigne. Si un texte change sans que sa version change dans `src/couverture/consignes.py`, `couverture versions` et la CI échouent. Pour modifier une consigne : changer le texte, augmenter la version, `couverture versions --manifeste`.

**Le suivi ne fait jamais échouer le travail** : sans MLflow, avec `MLFLOW_ACTIF=false`, si le serveur ne répond pas en 3 s, ou en cas d'erreur, le travail continue sans suivi et le dit.

## Grafana

Source : la base `data/base.sqlite`, montée en lecture seule, avec le plugin `frser-sqlite-datasource` (installé au démarrage du conteneur). Pas de PostgreSQL à ajouter.

**« Couverture sinistre — Réponses »** (table `analyses`)

| Partie | Panneaux |
|---|---|
| Usage | analyses, part d'INCERTAIN, décisions changées par la relecture, erreurs du modèle ; décisions par jour ; part d'INCERTAIN par jour |
| Fiabilité | par jour : analyses contestées par la relecture, décisions qu'elle a changées, réponses corrigées par le contrôle des citations, preuves écartées ; temps de réponse ; INCERTAIN par contrat ; sinistres déclarés |
| Ce qui manque, versions, erreurs | questions à poser à l'assuré les plus fréquentes ; versions des consignes et modèles en service, avec leurs résultats ; dernières erreurs |

**« Couverture sinistre — Contrats »** (tables `contrats` et `clauses`) : contrats et contrats à vérifier, qualité moyenne du typage, lecture de chaque contrat (statut, clauses, score de qualité, alertes, embeddings), clauses par type, alertes, types contestés par le juge de qualité.

Les tableaux sont **générés** par `python -m monitoring.grafana.construire_tableaux` : les requêtes y sont lisibles. Un test exécute chaque requête sur une vraie base SQLite et échoue si le JSON n'a pas été régénéré.

## Dérive

`couverture derive` : les 7 derniers jours contre les 28 précédents, avec le PSI (moins de 0,1 stable, de 0,1 à 0,25 modérée, plus de 0,25 forte), sur les questions (événement, bien, lieu), les réponses (décision, confiance) et la fiabilité (contestations, preuves écartées). Par contrat : alerte si la part d'INCERTAIN dépasse 60 % et a monté de 20 points. Au moins 30 analyses par période.

## Alertes : ce qui existe vraiment

| Signal | Comment on est prévenu |
|---|---|
| Contrat mal lu (contrôles ou juge de qualité sous 80 %) | statut `A_VERIFIER` à l'ingestion ; section « À faire » du bilan ; tableau Contrats |
| Proposition de réparation en attente | section « À faire » du bilan |
| Dérive forte, contrat dont l'INCERTAIN explose | `couverture derive` ; section « À faire » du bilan |
| Erreurs du modèle (clé refusée, quota) | section « À faire » du bilan ; panneau « Dernières erreurs » |
| Consigne modifiée sans nouvelle version | la CI échoue |

Le bilan part par mail avec `couverture bilan --envoyer` si un serveur SMTP est configuré dans `.env` ; à planifier chaque lundi (tâche planifiée Windows, cron, ou job du déploiement).

## Ce qui n'est pas fait (et ce qu'il faudrait)

- **Traces des appels au modèle** dans MLflow (prompt, réponse, tokens, durée), comme `mlflow.langchain.autolog()` dans SortirIA : le projet n'utilise pas LangChain ; il faudrait instrumenter `llm.py` avec `mlflow.start_span`.
- **Coût** : les tokens ne sont pas encore relevés.
- **Registre de modèles** (la « chaîne » de SortirIA, avec les alias `production` et `precedente`) : les versions des consignes et des modèles sont déjà dans chaque exécution, mais pas encore regroupées en une version de chaîne.
