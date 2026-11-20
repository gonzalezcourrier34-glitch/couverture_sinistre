# Banc d'essai — assureur-d-habitation-2026, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-20T16:22:03 · jeu ferme (25 cas, empreinte `10ac77778aa67e9a`) · cas validés par l'auteur : 0 sur 25

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.987 | ✓ |
| chaine | instables | ≤ 3 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 19.86 | ✗ |

## Depuis le banc précédent de même configuration (2026-11-20T15:54:58, mistral:mistral-small-latest · verifiee)

- chaine · exactitude : 1 → 0.987
- chaine · exactitude_stricte : 1 → 0.987

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 99% (96% – 100%) | 99% (96% – 100%) | **0 (0 – 0)** | **0 (0 – 0)** | 29% (28% – 32%) |

Instables : **1** sur 25 · rappel des clauses : 4% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 48.1 s · par cas, un à la fois (10 cas) : médiane 2.94 s, 95e centile 19.86 s (lecture 2.34 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.29 s, 95e centile 37.12 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 25 | 100% | 0 | 0 |
| garantie : ? | 25 | 100% | 0 | 0 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 6 | 100% | 0 | 0 |
| thème : exclusion | 4 | 100% | 0 | 0 |
| thème : incertain | 6 | 100% | 0 | 0 |
| thème : piege | 6 | 100% | 0 | 0 |
| thème : rc | 2 | 100% | 0 | 0 |

### Erreurs et instabilités

- `f-d11` attendu NC, obtenu NC NC ? — Mon fils de 19 ans, qui vit à la maison, a pris ma console de jeux et mon appareil photo pour les revendre. Je… *(Vol commis par un descendant sans plainte nominative : exclu. En plus, il n'y a ni effraction ni escalade.)*
