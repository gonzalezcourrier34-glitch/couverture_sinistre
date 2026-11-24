# Banc d'essai — assureur-d-habitation-2026, méthode `regles`, lecture par `mistral:mistral-medium-2604` (verifiee, exemples, verification mistral-small-2603)

2026-11-24T15:33:14 · jeu ferme (25 cas, empreinte `10ac77778aa67e9a`) · cas validés par l'auteur : 0 sur 25

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **PASSE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 1 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.947 | ✓ |
| chaine | instables | ≤ 3 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 6.88 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-24T15:18:03, mistral:mistral-medium-2604 · verifiee, exemples, verification mistral-small-2603)


## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 95% (92% – 96%) | 95% (92% – 96%) | **0 (0 – 0)** | **1 (1 – 1)** | 29% (28% – 32%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 7.67 | 0 |
| Non couvert | 9 | 1 |
| À préciser | 7 | 0.33 |

Instables : **1** sur 25 · rappel des clauses : 4% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 26.7 s · par cas, un à la fois (10 cas) : médiane 4.62 s, 95e centile 6.88 s (lecture 3.34 s, décision 0.02 s) · en masse (quatre à la fois) : médiane 3.89 s, 95e centile 6.24 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 25 | 96% | 0 | 1 |
| garantie : ? | 25 | 96% | 0 | 1 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 6 | 83% | 0 | 1 |
| thème : exclusion | 4 | 100% | 0 | 0 |
| thème : incertain | 6 | 100% | 0 | 0 |
| thème : piege | 6 | 100% | 0 | 0 |
| thème : rc | 2 | 100% | 0 | 0 |

### Erreurs et instabilités

- `f-d05` attendu C, obtenu C C ? — On a essayé de cambrioler mon appartement pendant que j'étais au travail : la porte d'entrée a été forcée au p… *(Détérioration des biens immobiliers à la suite d'une tentative de vol avec effraction laissant des traces : garantie com)*
- `f-d08` attendu C, obtenu NC NC NC — Lors de la crue du mois dernier, l'eau est montée d'un mètre dans le rez-de-chaussée. L'arrêté de catastrophe … *(Inondation reconnue catastrophe naturelle par arrêté publié au JO, déclarée dix jours après la publication, donc dans le)*
