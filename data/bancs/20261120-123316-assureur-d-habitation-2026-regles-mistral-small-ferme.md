# Banc d'essai — assureur-d-habitation-2026, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-20T12:30:18 · jeu ferme (25 cas, empreinte `10ac77778aa67e9a`) · cas validés par l'auteur : 0 sur 25

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 1 | ✓ |
| chaine | instables | ≤ 3 | 0 | ✓ |
| chaine | rappel_questions | ≥ 0.8 | 0 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 21.5 | ✗ |

## Depuis le banc précédent de même configuration (2026-11-20T12:20:07, mistral:mistral-small-latest · verifiee)

- chaine · exactitude : 0.92 → 1
- chaine · exactitude_stricte : 0.92 → 1

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 100% (100% – 100%) | 100% (100% – 100%) | **0 (0 – 0)** | **0 (0 – 0)** | 28% (28% – 28%) |

Instables : **0** sur 25 · rappel des clauses : 4% · rappel des questions : 0% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 40.2 s · par cas, un à la fois (10 cas) : médiane 4.1 s, 95e centile 21.5 s (lecture 2.84 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.63 s, 95e centile 21.1 s

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

Aucune.
