# Suivi : bancs, journal et Grafana

Ce qui est surveillé, comment, et où le voir. Organisation reprise de SortirIA.

## Lancement

```bash
docker compose up -d --build
```

| Service | Adresse | Rôle |
|---|---|---|
| API | http://localhost:8021/docs | L'API (clé `COUVERTURE_API_KEY`) ; lit `data/contrats` au démarrage |
| Grafana | http://localhost:3011 | Tableaux de bord (identifiant `admin`, mot de passe `GRAFANA_ADMIN_PASSWORD` du `.env`) |

Les ports évitent ceux de SortirIA (3001, 8010) : les deux projets peuvent tourner en même temps.

## Les couches

| Couche | Ce qu'on y voit | Où |
|---|---|---|
| **Banc** | Le golden set ou le jeu fermé rejoué : règles, lecture, chaîne, portes ; un rapport par passage | `couverture banc`, `data/bancs/`, `docs/METRIQUES.md` |
| **Journal** | Une ligne par analyse : décision (avant contrôle et finale), confiance, faits, questions, durée, versions des consignes. Jamais le texte du sinistre | table `analyses`, `src/couverture/journal.py` |
| **Grafana** | Deux tableaux, lus directement dans la base SQLite | `monitoring/grafana/` |
| **Consignes** | La version et l'empreinte de chaque consigne envoyée au modèle | `config/versions_consignes.json`, `src/couverture/consignes.py` |

**Garde-fou** : `config/versions_consignes.json` garde la version et l'empreinte de chaque consigne. Si un texte change sans que sa version change dans `src/couverture/consignes.py`, `couverture versions` et la CI échouent. Chaque version garde son texte dans `docs/consignes/`.

## Grafana

Source : la base `data/base.sqlite`, montée en lecture seule, avec le plugin `frser-sqlite-datasource`.

- **« Couverture sinistre — Réponses »** (table `analyses`) : analyses, part d'INCERTAIN, réponses fermes, erreurs du modèle ; décisions et INCERTAIN par jour ; réponses corrigées par le contrôle des citations ; temps de réponse ; INCERTAIN par contrat ; questions à poser les plus fréquentes ; versions des consignes en service ; dernières erreurs.
- **« Couverture sinistre — Contrats »** (tables `contrats` et `clauses`) : contrats et contrats à vérifier, lecture de chaque contrat, clauses par type, alertes.

Les tableaux sont **générés** par `python -m monitoring.grafana.construire_tableaux`. Un test exécute chaque requête sur une vraie base SQLite et échoue si le JSON n'a pas été régénéré.

## Retiré

- Le 18 nov. 2026 : la dérive (PSI), le bilan hebdomadaire et l'agent de réparation, avec les anciennes méthodes (DEMARCHE 7.36).
- Le 20 nov. 2026 : MLflow (exécutions des bancs, registre des consignes). Les rapports de `data/bancs/` et le manifeste des consignes en tiennent lieu (DEMARCHE 7.110).

## Ce qui n'est pas fait

- **Traces des appels au modèle** (prompt, réponse, tokens, durée).
- **Coût** : les tokens ne sont pas encore relevés.
