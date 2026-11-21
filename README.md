# Couverture sinistre

Dit si un sinistre est couvert par un contrat d'assurance habitation, **pourquoi**, et **sur quelles clauses**. Quand le contrat ne permet pas de trancher, la réponse est **« à préciser »**, avec la question à poser.

> Une réponse assurée sans justification vaut moins qu'un « je ne sais pas » étayé.

- [Note de conception](#note-de-conception) : le besoin, le choix, les résultats, ce qui a été essayé, les limites
- [Démonstration en 5 minutes](#démonstration-en-5-minutes)
- [Installation](#installation) et [utilisation](#utilisation)
- Pour aller plus loin : [la démarche](docs/DEMARCHE.md) (chaque essai et sa mesure, échecs compris), [les explications](docs/EXPLICATIONS.md) (chaque fichier, un lexique), [les mesures](docs/METRIQUES.md), [les consignes versionnées](docs/consignes/README.md), [le suivi](monitoring/README.md)

## Note de conception

### 1. Le besoin

Un gestionnaire reçoit une déclaration en langage courant et doit dire si le contrat la couvre. Trois choses comptent pour lui, dans cet ordre :

1. **ne pas couvrir à tort** : c'est l'erreur qui coûte ;
2. **pouvoir vérifier** : chaque réponse renvoie à la phrase du contrat, qu'il relit en un clic ;
3. **savoir quoi demander** quand la déclaration ne suffit pas, plutôt qu'une réponse devinée.

Et la question de l'énoncé : que faire à la place du contrat collé dans un chatbot, et comment tenir des centaines de contrats.

### 2. Le choix : le modèle lit, la logique décide, le code vérifie

Coller le contrat dans un chatbot échoue pour trois raisons : l'exclusion qui décide ne ressemble pas à la question, le sens des mots est au lexique du contrat, et rien n'est vérifiable. Le modèle n'a donc ici qu'un rôle : **lire**.

```
Une fois par contrat
  conditions générales (PDF) ─► clauses découpées, contrôlées, stockées en base
                             ─► règles : périmètre, conditions, obligations, exclusions, limites,
                                chacune avec la phrase du contrat qu'elle traduit, mot pour mot
                                (rédigées par Mistral Large, contrôlées par le code, relues)

À chaque sinistre (environ 4 secondes)
  déclaration ─► Mistral Small la traduit en faits d'un vocabulaire fermé (vol, vélo, cave, cadenas…)
             ─► chaque fait est vérifié : ce que la déclaration ne dit pas est retiré
             ─► le moteur (Prolog, logique à trois valeurs) décide : couvert, non couvert, à préciser
             ─► une réponse ferme doit reposer sur des faits confirmés ; sinon : à préciser, avec la question
             ─► réponse, clauses citées, arbre de preuve
```

Le moteur reprend le raisonnement d'un gestionnaire : un périmètre contraire écarte la garantie ; une exclusion ne retire qu'une garantie qui s'applique ; une obligation de prévention non respectée ne fait refuser que s'il y a un lien causal ; l'assuré établit la garantie, l'assureur l'exclusion. Deux garde-fous tiennent partout : **un doute ne fait jamais couvrir**, et **chaque citation est retrouvée mot pour mot dans le contrat** par le code.

### 3. Les deux questions de l'énoncé

| Question | Réponse | Clause citée |
|---|---|---|
| Vélo volé dans le local commun de l'immeuble, non fermé à clé | **Non couvert** | Art. 2.10-a : « le vol ou le vandalisme dans les parties communes du bâtiment » |
| Bougie laissée sur la table du jardin, fondue par la chaleur | **Non couvert** | Art. 12 : l'excès de chaleur sans embrasement n'est pas un incendie ; le contenu du jardin n'est pas du contenu assuré |

Contrat « Assureur A » (48 pages, 147 clauses). Les réponses attendues ont été établies d'après le texte des conditions générales, avec l'aide de Claude ; elles sont à relire par un juriste.

### 4. Ce que cela donne

Trois contrats de trois assureurs (anonymisés A, B, D), sur le même moteur. Mesures du 21 novembre 2026, trois passages par banc, lecture par Mistral Small :

| Banc | Réponses justes | Couverts à tort | Refus à tort |
|---|---|---|---|
| Règles seules, faits exacts (A, les 31 cas de test) | 100 % | 0 | 0 |
| A, partie test du golden set (31 cas jamais utilisés pour régler) | 85 % | 2 | 0 |
| A, jeu fermé (20 cas écrits sans voir les règles) | 87 % | 1 | 0 |
| B, jeu fermé (20 cas) | 85 % | 0 | 0 |
| D, jeu fermé (25 cas) | 100 % | 0 | 0 |

- **Un « non couvert » n'est jamais faux**, sur aucun banc.
- **Toutes les erreurs viennent de la lecture**, pas des règles : avec des faits exacts, le moteur ne se trompe pas.
- Les erreurs sont des « à préciser » de trop (une question au lieu d'une réponse) et, chez A, deux cas couverts à tort de façon répétée : des clés lues comme le bien volé, un bain à bulles lu comme du mobilier.
- Les jeux sont petits : un écart de 3 ou 4 points entre deux passages n'est pas significatif.

### 5. Ce qui a été essayé, et ce que la mesure a dit

Chaque essai est mesuré avant d'être gardé ; les échecs sont dans [la démarche](docs/DEMARCHE.md), avec leurs chiffres.

| Essai | Ce que la mesure a dit | Décision |
|---|---|---|
| Le modèle seul, sans règles (LegalBench, 133 cas d'assurance) | Il cite juste, mais tranche 90 % des cas que des lecteurs jugent ambigus | Écarté : c'est ce que les règles évitent |
| Des exemples de lecture choisis par similarité (mistral-embed) | Gain chez A ; mais montrés à la première étape, le modèle les recopiait (des denrées ajoutées à un congélateur grillé) | Gardés à la seule étape vérifiée |
| Faire vérifier par le modèle le bien qu'il a lu | Partie test de A : 87 % → 82 % ; il retirait des biens justes | Retiré |
| Un modèle plus fort (Mistral Large) pour la première étape | 17 à 31 secondes par cas, au lieu de 4 | Non retenu |
| Remplacer les cas particuliers de la consigne par des exemples | Une phrase retirée sans perte ; une autre faisait perdre un cas chez D | Une sur deux gardée |
| Une graine fixe pour stabiliser la lecture | Faits identiques aux trois passages : 35 déclarations sur 96, contre 30 sans | Sans effet |
| Relire deux fois et comparer | Non codé : les erreurs restantes se répètent à l'identique, deux lectures seraient d'accord sur l'erreur | Écarté |
| Vérifier par le code tout ce qu'on demande au client | 8 défauts d'affichage, vus à l'écran puis par une revue de 267 situations (question hors sujet, déjà répondue, sans réponse possible) ; les bancs ne les voyaient pas | Corrigés, et la revue reste en test |

Ce que cela apprend : le modèle sait dire si un fait est **écrit** ; il ne sait pas se corriger sur le choix d'une **catégorie**. La suite passe donc par plus d'exemples validés, pas par plus de consignes.

### 6. Tenir des centaines de contrats

Ce qui est fait :
- **un seul moteur**, sans rien de propre à un assureur ;
- **un vocabulaire à deux étages** : 50 questions communes (l'événement, le bien, le lieu, l'effraction, l'auteur…) et 19 à 48 questions propres à chaque contrat, rangées par le code ;
- **les règles rédigées par Mistral Large**, puis contrôlées : vocabulaire, citations mot pour mot, cohérence des concepts ;
- **des jeux fermés** écrits à partir du seul texte du contrat, par deux annotateurs indépendants, pour mesurer sans biais.

Ce que coûte un contrat de plus, honnêtement : la rédaction automatique est rapide (11 minutes pour un premier lot de six articles), mais la **relecture humaine reste lourde** sur les articles qui définissent les biens assurés : le modèle y invente des concepts, et ce lot a déclenché 80 contrôles bloquants. Les garanties demandent moins. Le temps complet par contrat n'a pas été mesuré.

Ce qui manque pour des centaines : les deux tiers du vocabulaire restent propres à un contrat (sans doute moins : des doublons entre assureurs restent à chercher) ; trois contrats ne prouvent pas cent ; tout est en habitation.

### 7. Limites

- Les **conditions particulières** du client (options, capitaux, formule) ne sont pas lues : une réponse qui en dépend est « à préciser ».
- La **lecture** : Mistral Small lit parfois un vélo comme un « véhicule à moteur ». Le garde-fou transforme l'erreur en question, pas en bonne réponse.
- Le moteur n'est pas plus juste que son vocabulaire : il ne sait pas dire « une fuite, mais pas le gel ».
- Seuls des **PDF** de conditions générales sont lus ; aucun document n'est produit.
- Les réponses attendues des jeux de référence ont été proposées par des modèles, puis arbitrées sur citations ; elles n'ont pas été validées par un juriste.

## Démonstration en 5 minutes

À répéter avant : `uv run couverture api` dans un terminal, `npm start` dans `frontend`, puis http://localhost:4220. La lecture varie d'un appel à l'autre : rejouer chaque étape une fois avant de la montrer.

| Temps | Ce qu'on montre | Ce qu'on dit |
|---|---|---|
| 0:00 | L'écran d'accueil | Le modèle lit, la logique décide, le code vérifie |
| 0:30 | Assureur A, la question 1 de l'énoncé : le vélo volé dans le local commun | Non couvert ; l'article est cité ; un clic sur son numéro ouvre le texte entier, le passage surligné |
| 1:30 | La question 2 : la bougie sur la table du jardin | Non couvert, pour deux raisons que le contrat écrit lui-même |
| 2:15 | Une déclaration incomplète (un vol sans dire comment le local était fermé) | « À préciser » : la question à poser, les réponses possibles ; la réponse du client donne la décision tout de suite, sans nouvel appel au modèle |
| 3:15 | La même déclaration sur Assureur B ou D | Autre contrat, autres règles, même moteur |
| 3:45 | `uv run couverture regles --contrat assureur-a-habitation-2025` | Les règles se vérifient sans modèle : vocabulaire, 171 citations retrouvées mot pour mot |
| 4:15 | Le tableau des essais (section 5) | Ce qui a marché, ce qui a été retiré, et pourquoi |
| 4:45 | Les limites (section 7) | Ce que le système ne sait pas faire |

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
# COUVERTURE_MODELE_SOCLE=mistral-large-latest    # essai (7.118) : un autre modèle pour le seul temps 1 de la lecture
# COUVERTURE_GRAINE=0                             # graine des appels au modèle (0 par défaut ; non : aucune) (7.123)
```

**SWI-Prolog** (gratuit) : `winget install SWI-Prolog.SWI-Prolog` sous Windows, `apt install swi-prolog-nox` sous Linux.

## Utilisation

```bash
uv run couverture ingerer                                   # lit data/contrats/ et remplit la base
uv run couverture analyser --contrat assureur-a-habitation-2025 "Mon vélo a été volé dans ma cave fermée par un cadenas."
uv run couverture regles   --contrat assureur-a-habitation-2025   # vérifie les règles (sans modèle) ; --faits pour un cas
uv run couverture rediger  --contrat assureur-a-habitation-2025 --article 2.2   # Mistral Large rédige, le code contrôle
uv run couverture banc     --contrat assureur-a-habitation-2025   # golden set (112 cas) : règles, lecture, chaîne, portes
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
la déclaration, la décision avec ses clauses citées (l'article entier dans une fenêtre, au clic sur son numéro) ; pour
« à préciser », les questions à poser au client, et ses réponses donnent la décision tout de suite. La clé de l'API reste côté serveur (`frontend/proxy.conf.mjs`).

Une réponse « incertain » dit, dans `a_preciser`, quoi demander au client ; ses réponses, ajoutées aux `faits` de la
réponse, se soumettent à `/decisions` : décision immédiate, gratuite, déterministe.

`analyser` donne la décision, le motif, les preuves, les questions à poser et l'**arbre de preuve** du moteur. Autres commandes : `contrats`, `clauses`, `versions`, `modele` (`--help`).

Avec docker : `docker compose up -d --build` lance l'API (8021) et Grafana (3011).

## Arborescence

```
src/couverture/      le code : lecture.py (le modèle lit), prolog.py (le moteur décide), chaine.py (la réponse),
                     redaction/ (Mistral Large rédige les règles), banc.py, exemples.py, cli/ et api/ (une
                     commande, une route par fichier), découpage des contrats, base
regles/              moteur Prolog, règles par contrat, vocabulaire (commun.json + un fichier par contrat), faits idéaux des cas
data/contrats/       conditions générales, catalogue.json, SOURCES.md (liens des CG réelles)
data/golden/         le golden set : sinistres, réponses attendues, version figée
config/              manifeste des versions des consignes
docs/                explications, démarche, métriques, archive des consignes
monitoring/          Grafana et guide du suivi
tests/               tests (pytest), sans clé ni réseau ; un second moteur en Python pour le test différentiel
```

`data/base.sqlite` n'est pas versionnée, ni les CG réelles (documents des assureurs) : leurs liens sont dans `data/contrats/SOURCES.md`.

## Mesurer

```bash
uv run couverture banc --contrat assureur-a-habitation-2025 --partie test   # les cas jamais utilisés pour régler
uv run couverture banc --contrat assureur-b-habitation-2017 --jeu ferme     # les cas écrits sans voir les règles
```

Chaque banc fait trois passages, écrit son rapport dans `data/bancs/` et se compare au précédent de même configuration. Il affiche les réponses justes et fausses par type de réponse, les cas instables et le temps par cas. Lancer les bancs l'un après l'autre : en parallèle, ils se ralentissent et faussent les temps. Détail : [docs/METRIQUES.md](docs/METRIQUES.md).
