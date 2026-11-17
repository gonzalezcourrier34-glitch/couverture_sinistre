# Couverture sinistre

Dit si un sinistre est couvert par un contrat d'assurance habitation, **pourquoi**, et **sur quelles clauses**. Quand le contrat ne permet pas de trancher, la réponse est **INCERTAIN**, avec ce qu'il faut demander à l'assuré.

> Une réponse assurée sans justification vaut moins qu'un « je ne sais pas » étayé.

- Chaque fichier et chaque choix, avec un lexique : [docs/EXPLICATIONS.md](docs/EXPLICATIONS.md)
- La démarche dans l'ordre, échecs et remises en question compris : [docs/DEMARCHE.md](docs/DEMARCHE.md)
- Chaque version des consignes envoyées au modèle : [docs/consignes/](docs/consignes/README.md)
- Le suivi (MLflow, Grafana) : [monitoring/README.md](monitoring/README.md)

## L'idée

Coller le contrat dans un chatbot échoue : l'exclusion qui décide ne ressemble pas à la question, le sens des mots est au lexique, chaque assureur rédige autrement, et rien n'est vérifiable.

Le principe du projet : **le modèle établit des faits, le code décide, et chaque preuve est vérifiée**. Le travail difficile se fait **une fois par contrat** :

```
Une fois par contrat
  PDF ─► nettoyage ─► clauses typées ─► contrôles + juge de qualité ─► base
      ─► compilation : chaque garantie devient une fiche de questions, rangées par rôle
         (périmètre, circonstances, obligations, exclusions, limites), chaque extrait vérifié
         dans le contrat ─► relecture humaine possible (export / import)

À chaque sinistre
  déclaration ─► faits (événement, bien, lieu) ─► fiches de l'événement
             ─► le modèle répond oui / non / inconnu ─► décision calculée par des règles
             ─► relecture des lignes décisives ─► réponse courte, preuves, questions à poser
```

Les règles de décision reprennent le raisonnement d'un gestionnaire, et le contrat Foyer fait lui-même ces distinctions :
- un **périmètre** contraire (autre lieu, autre bien) écarte la garantie ;
- une **exclusion** ne retire qu'une garantie qui s'applique ;
- une **obligation de prévention** non respectée ne fait refuser que s'il y a un lien causal ;
- **charge de la preuve** : l'assuré établit la garantie, l'assureur l'exclusion. Une exclusion inconnue donne « couvert, sous réserve ».

## Méthodes comparables (`couverture comparer`)

| Méthode | Principe |
|---|---|
| `fiches` | Contrat compilé ; le modèle répond à des questions déjà écrites |
| `conditions` | Le modèle remplit une grille à chaque sinistre, le code décide (méthode par défaut) |
| `brut` | Le contrat entier dans le prompt : la référence « chatbot » à battre |

## Installation

Avec [uv](https://docs.astral.sh/uv/) :

```bash
uv sync --extra dev          # ajouter --extra suivi pour MLflow
cp .env.example .env         # puis y mettre la clé Mistral
uv run pytest -q
```

`.env` (jamais versionné) :

```
MISTRAL_API_KEY=votre-clé
COUVERTURE_MODELE=mistral-small-latest            # analyses : rapide, sans réflexion
COUVERTURE_MODELE_CONTRAT=mistral-large-latest    # compilation, qualité, réparation : une fois par contrat
```

Anthropic (`ANTHROPIC_API_KEY`) et tout modèle compatible OpenAI (`COUVERTURE_LLM_URL`) sont aussi pris en charge. Sans modèle, un juge prudent sans modèle répond (`--hors-ligne`).

## Utilisation

```bash
uv run couverture modele                                   # modèles configurés, test de connexion
uv run couverture ingerer                                  # lit data/contrats/
uv run couverture compiler --contrat foyer-appart123-2025  # une fois par contrat (Mistral Large, ~15 min)
uv run couverture fiches   --contrat foyer-appart123-2025  # relire les fiches (--exporter / --importer)
uv run couverture analyser --contrat foyer-appart123-2025 --methode fiches "Mon vélo a été volé dans le local commun…"
uv run couverture evaluer  --contrat foyer-appart123-2025 --methode fiches   # tableau ; --detail pour le JSON
uv run couverture serveur                                  # interface sur http://127.0.0.1:8000
```

`analyser` donne la décision, le motif, les preuves décisives et les questions à poser ; `--detail` montre toutes les fiches. Les commandes longues affichent une barre de progression. Autres commandes : `contrats`, `clauses`, `comparer`, `reparer`, `propositions`, `versions`, `derive`, `bilan` (`--help`).

Avec docker : `docker compose up -d --build` lance l'application (8020), MLflow (5010) et Grafana (3011).

## Arborescence

```
src/couverture/      le code (un module par étape, voir docs/EXPLICATIONS.md)
data/contrats/       conditions générales, catalogue.json, SOURCES.md (liens des CG réelles)
data/sinistres.jsonl 14 sinistres de test, dont les deux de l'énoncé
data/annotations/    réponse attendue et clauses à citer, contrat par contrat
config/              manifeste des versions des consignes
docs/                explications, démarche, archive des consignes
monitoring/          Grafana et guide du suivi
tests/               tests (pytest), sans clé ni réseau
```

`data/base.sqlite` est produite par `ingerer` et `compiler`, et n'est pas versionnée. Les CG réelles non plus (documents des assureurs) : leurs liens sont dans `data/contrats/SOURCES.md`.

## Données de test

Les sinistres sont indépendants des contrats. Des variations changent **un seul fait** (local fermé ou non, cave privative, flammes ou non) : si la réponse bascule quand le fait change, le système raisonne vraiment sur le contrat. Pour chaque contrat, `data/annotations/` donne la réponse attendue, les clauses qui doivent être citées, et les réponses `acceptables` pour les cas qu'on ne peut trancher sans les conditions particulières.

## Résultats à ce stade

- **Tests** : 98 passent, sans clé ni réseau ; la CI les relance à chaque envoi.
- **Foyer appart 123** (48 pages) : 147 clauses, dont 63 définitions ; compilé en 36 fiches et 350 questions.
- **Évaluation Foyer, 14 cas, méthode `fiches`** : **93 %** de réponses justes ou acceptables (57 % exactes), **0 couvert à tort, 0 refus à tort**, en une minute. Les INCERTAIN restants sont surtout des cas qu'on ne peut trancher sans les conditions particulières. Historique des mesures : [docs/DEMARCHE.md](docs/DEMARCHE.md).

## Limites connues

- Les conditions particulières du client (options, capitaux) ne sont pas lues ; beaucoup d'INCERTAIN deviendraient des réponses fermes.
- La responsabilité civile de Foyer est typée « autre » par le découpage : pas encore compilée.
- Les tableaux de plafonds sont lus comme du texte.
- Prochaine étape envisagée : des règles explicites sur un vocabulaire de faits commun à tous les contrats (voir DEMARCHE, partie 8).
