# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-medium-2604` (verifiee, exemples, verification mistral-small-2603)

2026-11-25T10:47:52 · jeu ferme (20 cas, empreinte `6997c9e1e2012a80`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **PASSE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 1 | ✓ |
| chaine | instables | ≤ 3 | 0 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 7.06 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-24T23:34:39, mistral:mistral-medium-2604 · verifiee, exemples, verification mistral-small-2603)


## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 100% (100% – 100%) | 95% (95% – 95%) | **0 (0 – 0)** | **0 (0 – 0)** | 25% (25% – 25%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 8 | 0 |
| Non couvert | 7 | 0 |
| À préciser | 5 | 0 |

Instables : **0** sur 20 · rappel des clauses : 41% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 28.4 s · par cas, un à la fois (10 cas) : médiane 4.92 s, 95e centile 7.06 s (lecture 3.29 s, décision 0.04 s) · en masse (quatre à la fois) : médiane 5.48 s, 95e centile 7.59 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 100% | 0 | 0 |
| garantie : ? | 20 | 100% | 0 | 0 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 3 | 100% | 0 | 0 |
| thème : exclusion | 3 | 100% | 0 | 0 |
| thème : extension | 2 | 100% | 0 | 0 |
| thème : incertain | 5 | 100% | 0 | 0 |
| thème : piege | 4 | 100% | 0 | 0 |
| thème : rc | 2 | 100% | 0 | 0 |

### Erreurs et instabilités

Aucune.
