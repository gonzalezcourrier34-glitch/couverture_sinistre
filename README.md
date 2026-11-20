# Couverture sinistre

Dit si un sinistre est couvert par un contrat d'assurance habitation, **pourquoi**, et **sur quelles clauses**. Quand le contrat ne permet pas de trancher, la réponse est **INCERTAIN**, avec la question qui tranche.

> Une réponse assurée sans justification vaut moins qu'un « je ne sais pas » étayé.

- Chaque fichier et chaque choix, avec un lexique : [docs/EXPLICATIONS.md](docs/EXPLICATIONS.md)
- La démarche dans l'ordre, échecs et remises en question compris : [docs/DEMARCHE.md](docs/DEMARCHE.md)
- Comment on mesure (jeux de cas, métriques, portes) : [docs/METRIQUES.md](docs/METRIQUES.md)
- Chaque version des consignes envoyées au modèle : [docs/consignes/](docs/consignes/README.md)
- Le suivi (bancs, journal, Grafana) : [monitoring/README.md](monitoring/README.md)

## L'idée

Coller le contrat dans un chatbot échoue : l'exclusion qui décide ne ressemble pas à la question, le sens des mots est au lexique, et rien n'est vérifiable.

Ici, **le modèle lit, la logique décide, le code vérifie** :

```
Une fois par contrat
  conditions générales ─► clauses découpées et contrôlées ─► base
                       ─► règles Prolog : périmètre, conditions, obligations, exclusions, limites,
                          chacune avec la phrase du contrat qu'elle traduit, mot pour mot
                          (écrites à la main ou par Mistral Large, toujours contrôlées par le code)

À chaque sinistre
  déclaration ─► le modèle la traduit en faits d'un vocabulaire commun (vol, vélo, cave, cadenas…)
             ─► Prolog décide : COUVERT, NON_COUVERT ou INCERTAIN (logique à trois valeurs)
             ─► si INCERTAIN : il essaie chaque réponse possible et dit quelle question tranche
             ─► réponse, preuves citées, et l'arbre de preuve jusqu'aux faits déclarés
```

Les règles reprennent le raisonnement d'un gestionnaire, et le contrat lui-même fait ces distinctions :
- un **périmètre** contraire (autre lieu, autre bien) écarte la garantie ;
- une **exclusion** ne retire qu'une garantie qui s'applique ;
- une **obligation de prévention** non respectée ne fait refuser que s'il y a un lien causal ;
- **charge de la preuve** : l'assuré établit la garantie, l'assureur l'exclusion.

## Installation

Avec [uv](https://docs.astral.sh/uv/) :

```bash
uv sync --extra dev
cp .env.example .env         # puis y mettre la clé Mistral
uv run pytest -q
```

`.env` (jamais versionné) :

```
MISTRAL_API_KEY=votre-clé
COUVERTURE_MODELE=mistral-small-latest            # lecture des déclarations
COUVERTURE_MODELE_CONTRAT=mistral-large-latest    # rédaction des règles : une fois par contrat
```

**SWI-Prolog** (gratuit) : `winget install SWI-Prolog.SWI-Prolog` sous Windows, `apt install swi-prolog-nox` sous Linux.

## Utilisation

```bash
uv run couverture ingerer                                   # lit data/contrats/ et remplit la base
uv run couverture analyser --contrat assureur-a-habitation-2025 "Mon vélo a été volé dans ma cave fermée par un cadenas."
uv run couverture regles   --contrat assureur-a-habitation-2025   # vérifie les règles (sans modèle) ; --faits pour un cas
uv run couverture rediger  --contrat assureur-a-habitation-2025 --article 2.2   # Mistral Large rédige, le code contrôle
uv run couverture banc     --contrat assureur-a-habitation-2025   # golden set (97 cas) : règles, lecture, chaîne, portes
uv run couverture exemples --indexer                               # banque d'exemples de lecture (mistral-embed), à refaire si le golden set change
uv run couverture banc     --contrat assureur-a-habitation-2025 --partie test   # les seuls cas de test (data/lecture/partage.json)
uv run couverture api                                       # l'API (FastAPI), documentation sur http://127.0.0.1:8001/docs
```

### L'API

```bash
uv run couverture api                                       # http://127.0.0.1:8001/docs
```

Une API FastAPI, une route par fichier (`src/couverture/api/routes/`), sur le modèle de celle de SortirIA. Clé dans
l'en-tête `x-api-key` (`COUVERTURE_API_KEY` dans `.env` ; sans elle, les routes protégées refusent tout) :

| Route | Rôle |
|---|---|
| `GET /api/v1/sante` | l'API, le moteur et le modèle répondent (publique) |
| `GET /api/v1/contrats`, `/contrats/{id}`, `/contrats/{id}/clauses` | les contrats et leur texte |
| `GET /api/v1/vocabulaire` | les faits que le moteur comprend |
| `POST /api/v1/analyses` | une déclaration → couvert, non couvert ou incertain, avec les citations |
| `POST /api/v1/decisions` | des faits → la décision, sans modèle (résout un « incertain ») |

### L'interface

```bash
cd frontend
npm install
npm start                                                   # http://localhost:4220 (l'API doit tourner)
```

Angular 21, sur le modèle de l'interface de SortirIA, aux couleurs du système de design public de foyer.lu. Le contrat,
la déclaration, la décision avec ses clauses citées (texte complet au clic) ; pour « à préciser », les questions à poser
au client, et ses réponses donnent la décision tout de suite. La clé de l'API reste côté serveur (`frontend/proxy.conf.mjs`).

Une réponse « incertain » dit, dans `a_preciser`, quoi demander au client ; ses réponses, ajoutées aux `faits` de la
réponse, se soumettent à `/decisions` : décision immédiate, gratuite, déterministe.

`analyser` donne la décision, le motif, les preuves, les questions à poser et l'**arbre de preuve** du moteur. Autres commandes : `contrats`, `clauses`, `versions`, `modele` (`--help`).

Avec docker : `docker compose up -d --build` lance l'API (8021) et Grafana (3011).

## Arborescence

```
src/couverture/      le code : lecture.py (le modèle lit), prolog.py (le moteur décide), chaine.py (la réponse),
                     redaction/ (Mistral Large rédige les règles), banc.py, exemples.py, cli/ et api/ (une
                     commande, une route par fichier), découpage des contrats, base
regles/              vocabulaire commun, moteur Prolog, règles par contrat, faits idéaux des cas
data/contrats/       conditions générales, catalogue.json, SOURCES.md (liens des CG réelles)
data/golden/         le golden set : sinistres, réponses attendues, version figée
config/              manifeste des versions des consignes
docs/                explications, démarche, métriques, archive des consignes
monitoring/          Grafana et guide du suivi
tests/               tests (pytest), sans clé ni réseau ; un second moteur en Python pour le test différentiel
```

`data/base.sqlite` n'est pas versionnée, ni les CG réelles (documents des assureurs) : leurs liens sont dans `data/contrats/SOURCES.md`.

## Résultats à ce stade

Contrat Assureur A « Habitation A » (48 pages, 147 clauses). Golden set de 97 cas (dont 13 où la bonne réponse est « incertain »), écrit par Claude et à valider par l'auteur :

| Mesure | Justes | Couverts à tort | Refus à tort |
|---|---|---|---|
| **Règles seules** (faits idéaux, SWI-Prolog) | **100 %** | **0** | **0** |
| Chaîne complète, lecture Mistral Small vérifiée et confirmée (3 exécutions) | 90 % | 1,3 | 1 |
| Chaîne complète, lecture Mistral Large (3 exécutions) | 91 % | 0 | 0,3 |

Deuxième contrat, **Assureur B Habitation**, garantie vol (8 sous-garanties, 11 exclusions) : règles **rédigées par Mistral Large**, contrôlées par le code, relues, puis testées sur 15 cas.

| Mesure (Assureur B, 15 cas) | Justes | Couverts à tort | Refus à tort |
|---|---|---|---|
| **Règles seules** | **100 %** | **0** | **0** |
| Chaîne complète, Mistral Small (3 exécutions) | 76 % (62 % au premier banc) | **0** | **0** |

Les erreurs trouvées sur Assureur B ont été corrigées dans la méthode (consigne de rédaction, contrôles, moteur), ce qui a aussi amélioré Assureur A. Détail et progression : `docs/DEMARCHE.md`, sections 7.52 à 7.61.

Les règles sont justes ; **toutes les erreurs restantes viennent de la lecture des faits**. La lecture par Small se fait en deux temps (l'événement, puis les questions qui le concernent), puis chaque fait est vérifié ; le moteur empêche qu'un doute fasse couvrir, et avant toute réponse ferme il fait confirmer les faits qui la portent : sinon, la réponse est « je ne sais pas », avec la question. Un cas prend 2,9 s (médiane, un cas à la fois). Mistral Large lit encore mieux, mais 15 minutes par passage du banc contre 2 à 3 avec Small. Le chantier en cours : des exemples de lecture choisis pour chaque déclaration, à la place des cas particuliers écrits dans le vocabulaire (DEMARCHE 7.107, 7.108). Sur LegalBench (133 clauses externes, Mistral Small sans règles), le modèle cite juste mais tranche 90 % des cas que des lecteurs jugent ambigus : c'est ce que les règles évitent. La seule vraie mesure reste à faire : un jeu fermé écrit par l'auteur, sans voir les règles.

## Limites connues

- Les conditions particulières du client (options, capitaux) ne sont pas lues ; beaucoup d'INCERTAIN deviendraient des réponses fermes.
- Une partie des garanties n'est pas encore traduite en règles (tempête, électricité, responsabilité de l'immeuble…) : elles répondent « à examiner par un gestionnaire ».
- Le moteur n'est pas plus juste que le vocabulaire de faits : une condition que le vocabulaire ne sait pas exprimer est ignorée.
