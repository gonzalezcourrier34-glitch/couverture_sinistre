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
| `regles` | Le contrat en **règles Prolog** ; le modèle ne fait que lire les faits de la déclaration, un moteur logique décide |
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

La méthode `regles` demande **SWI-Prolog** (gratuit) : `winget install SWI-Prolog.SWI-Prolog` sous Windows, `apt install swi-prolog-nox` sous Linux.

Anthropic (`ANTHROPIC_API_KEY`) et tout modèle compatible OpenAI (`COUVERTURE_LLM_URL`) sont aussi pris en charge. Sans modèle, un juge prudent sans modèle répond (`--hors-ligne`).

## Utilisation

```bash
uv run couverture modele                                   # modèles configurés, test de connexion
uv run couverture ingerer                                  # lit data/contrats/
uv run couverture regles   --contrat foyer-appart123-2025  # vérifie les règles Prolog (sans modèle)
uv run couverture rediger  --contrat foyer-appart123-2025 --article 2.2 --article 2.9  # Mistral Large rédige des règles, le code les contrôle
uv run couverture banc     --contrat foyer-appart123-2025  # banc d'essai : golden set (97 cas), règles, lecture, chaîne, portes
uv run couverture analyser --contrat foyer-appart123-2025 --methode regles "…"
uv run couverture compiler --contrat foyer-appart123-2025  # fiches : une fois par contrat (Mistral Large, ~15 min)
uv run couverture fiches   --contrat foyer-appart123-2025  # relire les fiches (--exporter / --importer)
uv run couverture analyser --contrat foyer-appart123-2025 --methode fiches "Mon vélo a été volé dans le local commun…"
uv run couverture evaluer  --contrat foyer-appart123-2025 --methode fiches   # tableau ; --detail pour le JSON
uv run couverture evaluer  --contrat foyer-appart123-2025 --methode regles --jeu validation --repetitions 3
uv run couverture serveur                                  # interface sur http://127.0.0.1:8000
```

`analyser` donne la décision, le motif, les preuves décisives et les questions à poser ; `--detail` montre toutes les fiches. Les commandes longues affichent une barre de progression. Autres commandes : `contrats`, `clauses`, `comparer`, `reparer`, `propositions`, `versions`, `derive`, `bilan` (`--help`).

Avec docker : `docker compose up -d --build` lance l'application (8020), MLflow (5010) et Grafana (3011).

## Arborescence

```
src/couverture/      le code (un module par étape, voir docs/EXPLICATIONS.md)
regles/              vocabulaire commun, moteur Prolog, règles par contrat, faits des cas de test
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

Comment on évalue (jeux de cas, métriques, seuils, ce que valent les chiffres) : [docs/METRIQUES.md](docs/METRIQUES.md).

- **Tests** : 161 passent (plus 2 tests Prolog là où SWI-Prolog est installé), sans clé ni réseau ; la CI les relance à chaque envoi.
- **Foyer appart 123** (48 pages) : 147 clauses, dont 63 définitions ; compilé en 36 fiches et 350 questions.
- **Évaluation Foyer, 14 cas, trois exécutions** :

  | Méthode | Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Durée |
  |---|---|---|---|---|---|
  | `fiches` | 74 % | 60 % | 2 | 0 | ~1 min |
  | **`regles`** (Prolog) | **100 %** | **90 %** | **0** | **0** | **3 à 4 s** |

  Réserve : les règles ont été écrites en connaissant ces 14 cas, et trois garanties seulement sont en règles.
- **Jeu de validation, 15 cas nouveaux** (`--jeu validation`), règles seules sur les faits idéaux : 87 % justes ou acceptables, mais **2 couverts à tort**. Les deux viennent d'obligations de prévention que le vocabulaire n'exprime pas (fenêtres laissées ouvertes, mesures contre le gel). Mesure enregistrée avant toute correction. Chaîne complète (le modèle lit les faits) : 67 %, 2 couverts et 1 refus à tort : la lecture des faits coûte 20 points sur des cas nouveaux. Corrigé ensuite (cause et dommage, événements non traduits, fenêtres, gel, texte des règles) : 100 % sur les faits idéaux, mais ces 15 cas sont désormais de la mise au point ; un nouveau jeu reste à écrire (DEMARCHE 7.18). Chaîne complète après correction : 87 %, aucun refus à tort, mais 4 cas sur 15 instables d'une exécution à l'autre (la lecture des faits).
- **Règles rédigées par Mistral Large** (tempête, bris de vitrages) : exclusions toutes traduites, citations exactes, faits manquants déclarés ; un écart au schéma et une définition restrictive oubliée, désormais contrôlés (DEMARCHE 7.20). Détail : [docs/DEMARCHE.md](docs/DEMARCHE.md), 7.17.

- **Banc d'essai** (`data/golden/`, 68 cas, trois couches, portes), premier passage complet : règles seules 85 % (2 couverts et 7 refus à tort), chaîne complète 83 % avec **5 couverts à tort** (2 viennent des règles, 3 de la lecture des faits) et 8 cas instables. Le bris de vitrages, rédigé par Mistral Large, est en service. Puis tous les périls du contrat nommés : règles seules 96 %, aucun refus à tort ; la lecture v3 a fait reculer la chaîne (une règle perdue en réécrivant la consigne), corrigée en v4. Avec les quatre phrases du contrat qui manquaient (clé, récipient, fumée, casier) : **règles seules 100 %, aucun couvert ni refus à tort** ; les erreurs restantes viennent toutes de la lecture des faits. Quand la réponse est « incertain », le moteur Prolog essaie chaque réponse possible et dit quelle question tranche (« serrure de sûreté ? oui → couvert ; non → non couvert ») ; les questions inutiles ne sont plus posées. Golden set complété (v5, 97 cas, dont 13 où la bonne réponse est « incertain ») : il a trouvé 4 couverts et 3 refus à tort dans les règles ; corrigées (exclusions générales 1.4, exclusions de 2.7, clés, plantations, mazout, mérule et vandalisme « à examiner »), elles repassent à **100 %, aucun couvert ni refus à tort**. Détail : DEMARCHE 7.21 à 7.31.

## Limites connues

- Les conditions particulières du client (options, capitaux) ne sont pas lues ; beaucoup d'INCERTAIN deviendraient des réponses fermes.
- La responsabilité civile de Foyer est typée « autre » par le découpage : pas encore compilée.
- Les tableaux de plafonds sont lus comme du texte.
- Le moteur n'est pas plus juste que le vocabulaire de faits : une obligation que le vocabulaire ne sait pas demander est ignorée.
