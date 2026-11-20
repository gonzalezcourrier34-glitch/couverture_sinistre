# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee, exemples)

2026-11-20T17:07:29 · jeu ferme (20 cas, empreinte `6997c9e1e2012a80`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **PASSE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 1 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.95 | ✓ |
| chaine | instables | ≤ 3 | 0 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 6.05 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-20T16:41:19, mistral:mistral-small-latest · verifiee, exemples)

- chaine · exactitude : 0.9 → 0.95
- chaine · exactitude_stricte : 0.8 → 0.85
- chaine · faux_couverts : 0.333 → 0
- chaine · faux_refus : 0.667 → 1

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 95% (95% – 95%) | 85% (85% – 85%) | **0 (0 – 0)** | **1 (1 – 1)** | 30% (30% – 30%) |

Instables : **0** sur 20 · rappel des clauses : 38% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 36.3 s · par cas, un à la fois (10 cas) : médiane 4.0 s, 95e centile 6.05 s (lecture 3.18 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.79 s, 95e centile 37.49 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 95% | 0 | 1 |
| garantie : ? | 20 | 95% | 0 | 1 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 3 | 100% | 0 | 0 |
| thème : exclusion | 3 | 100% | 0 | 0 |
| thème : extension | 2 | 100% | 0 | 0 |
| thème : incertain | 5 | 100% | 0 | 0 |
| thème : piege | 4 | 100% | 0 | 0 |
| thème : rc | 2 | 50% | 0 | 1 |

### Erreurs et instabilités

- `f-a18` attendu C, obtenu NC NC NC — En faisant du vélo dans le parc, je n'ai pas vu un piéton qui traversait l'allée et je l'ai renversé. Il s'est… *(Dommage corporel causé à un tiers pendant une activité de loisir de la vie privée, avec un vélo sans moteur : RC vie pri)*
