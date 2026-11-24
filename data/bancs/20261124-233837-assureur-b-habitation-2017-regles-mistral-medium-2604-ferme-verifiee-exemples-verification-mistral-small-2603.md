# Banc d'essai — assureur-b-habitation-2017, méthode `regles`, lecture par `mistral:mistral-medium-2604` (verifiee, exemples, verification mistral-small-2603)

2026-11-24T23:36:24 · jeu ferme (20 cas, empreinte `e419734e12e73607`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.933 | ✓ |
| chaine | instables | ≤ 3 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 11.31 | ✗ |

## Depuis le banc précédent de même configuration (2026-11-24T22:48:53, mistral:mistral-medium-2604 · verifiee, exemples, verification mistral-small-2603)

- chaine · exactitude : 0.9 → 0.933
- chaine · exactitude_stricte : 0.85 → 0.883

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 93% (90% – 95%) | 88% (85% – 90%) | **0 (0 – 0)** | **0 (0 – 0)** | 37% (35% – 40%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 8 | 0 |
| Non couvert | 4.67 | 0 |
| À préciser | 6 | 1.33 |

Instables : **1** sur 20 · rappel des clauses : 36% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 25.5 s · par cas, un à la fois (10 cas) : médiane 4.34 s, 95e centile 11.31 s (lecture 3.24 s, décision 0.03 s) · en masse (quatre à la fois) : médiane 5.29 s, 95e centile 6.88 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 95% | 0 | 0 |
| garantie : ? | 20 | 95% | 0 | 0 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 4 | 100% | 0 | 0 |
| thème : exclusion | 4 | 75% | 0 | 0 |
| thème : incertain | 5 | 100% | 0 | 0 |
| thème : piege | 4 | 100% | 0 | 0 |
| thème : rc | 2 | 100% | 0 | 0 |

### Erreurs et instabilités

- `f-b06` attendu NC, obtenu NC ? NC — J'avais laissé ma porte d'entrée ouverte le temps de descendre chercher le courrier. Quelqu'un en a profité po… *(Vol sans forcement ni dégradation d'une fermeture : c'est un vol simple, exclu de la garantie vol (3.1.6.2.1).)*
- `f-b07` attendu NC, obtenu ? ? ? — Dans le bus en allant au travail, j'avais posé mon sac sur le siège à côté de moi. Quelqu'un l'a pris en desce… *(Vol à la sauvette (bien à portée de main pris à l'insu de l'assuré) hors du logement : exclu de la garantie vol.)*
