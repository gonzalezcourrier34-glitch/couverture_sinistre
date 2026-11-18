# Golden set — le banc d'essai de référence

Un jeu de sinistres **figé, étiqueté et versionné**, sur lequel on rejoue tout le système à chaque
changement : `uv run couverture banc --contrat foyer-appart123-2025`.

## Ce qu'il contient (version 5, 97 cas)

| Origine | Cas | Écrits |
|---|---|---|
| `recruteur` | 2 | les deux cas de l'énoncé (vélo, bougie) |
| `mise_au_point` | 12 | variations des deux cas, ayant servi à écrire les règles |
| `validation_ex` | 15 | l'ancien jeu de validation, devenu mise au point (DEMARCHE 7.18) |
| `redaction` | 10 | tempête et bris de vitrages, écrits avant toute règle |
| `golden` | 58 | nouveaux : langue, informations manquantes, pièges, garanties non traduites, sinistres multiples ; en v5, 13 cas dont la bonne réponse est « incertain », les garanties 2.5, 2.11, 2.12 et les exclusions générales 1.4 |

Chaque cas porte : la réponse attendue (`attendu`), les réponses tolérées (`acceptables`), les
clauses qui la fondent (`clauses_attendues`), les questions qu'un gestionnaire poserait
(`questions_attendues`, variables du vocabulaire), la garantie, des **thèmes** (`base`, `variante`,
`piege`, `langue`, `info_manquante`, `hors_regles`, `multi`), l'origine, l'**auteur**, une note qui cite
le contrat, et ses **faits idéaux** (`regles/cas/golden/`).

## Trois couches, pour savoir où naît une erreur

1. **Règles** : les faits idéaux dans le moteur, sans modèle. Une erreur ici vient des règles ou du vocabulaire.
2. **Lecture** : les faits lus par le modèle comparés aux faits idéaux. Une *contradiction* (lieu lu
   « parties communes » au lieu de « cave ») est l'erreur la plus dangereuse.
3. **Chaîne** : la méthode complète, trois exécutions ; les cas *instables* sont listés.

Les **portes** (`seuils.json`) disent si le système est présentable. Couverts à tort : zéro. La commande
sort en erreur si une porte échoue (branchable sur la CI). Chaque passage est gardé dans `data/bancs/`
(JSON et rapport Markdown) et comparé au précédent.

## Les règles du jeu

- **Le golden set ne sert qu'à mesurer.** Corriger les règles en regardant un cas qui échoue est
  légitime (c'est le but), mais le score sur ce cas devient de la mise au point : seuls les cas
  écrits **sans connaître les règles** mesurent la généralisation. D'où le champ `auteur`.
- **Les réponses attendues sont proposées par Claude, à valider par l'auteur** (`--fiche` écrit
  `A_VALIDER.md`). Un cas validé porte « validé par … » dans `statut` ; le rapport compte les cas validés.
- **Toute modification est versionnée** : `couverture banc --figer "raison"` ; un banc lancé sur un
  golden set modifié sans nouvelle version le signale, et le test `test_golden_fige` échoue.
- **On ajoute, on ne retire pas** : un cas faux se corrige (avec la raison dans la note), un cas
  ne disparaît pas parce qu'il échoue.
- **Les seuils se resserrent**, ils ne se relâchent pas sans le noter dans `docs/DEMARCHE.md`.

## Ce qui manque encore

- Des cas **écrits par l'auteur** (ou un gestionnaire), sans Claude : les seuls vraiment aveugles.
- Les **montants** (limites d'indemnisation) : les cas les citent, le banc ne les vérifie pas encore.
