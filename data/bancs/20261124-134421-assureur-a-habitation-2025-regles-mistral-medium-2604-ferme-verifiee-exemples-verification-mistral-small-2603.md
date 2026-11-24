# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-medium-2604` (verifiee, exemples, verification mistral-small-2603)

2026-11-24T13:42:39 · jeu ferme (20 cas, empreinte `6997c9e1e2012a80`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 1 | ✗ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.95 | ✓ |
| chaine | instables | ≤ 3 | 0 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 4.87 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-24T12:08:02, mistral:mistral-medium-2604 · verifiee, exemples, verification mistral-small-2603)

- chaine · exactitude : 1 → 0.95
- chaine · exactitude_stricte : 0.95 → 0.9
- chaine · faux_couverts : 0 → 1

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 95% (95% – 95%) | 90% (90% – 90%) | **1 (1 – 1)** | **0 (0 – 0)** | 20% (20% – 20%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 8 | 1 |
| Non couvert | 7 | 0 |
| À préciser | 4 | 0 |

Instables : **0** sur 20 · rappel des clauses : 46% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 21.1 s · par cas, un à la fois (10 cas) : médiane 3.96 s, 95e centile 4.87 s (lecture 3.03 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.87 s, 95e centile 5.34 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 95% | 1 ⚠ | 0 |
| garantie : ? | 20 | 95% | 1 ⚠ | 0 |
| thème : assistance | 1 | 0% | 1 ⚠ | 0 |
| thème : base | 3 | 100% | 0 | 0 |
| thème : exclusion | 3 | 100% | 0 | 0 |
| thème : extension | 2 | 100% | 0 | 0 |
| thème : incertain | 5 | 100% | 0 | 0 |
| thème : piege | 4 | 100% | 0 | 0 |
| thème : rc | 2 | 100% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `f-a20` attendu ?, obtenu C C C — En sortant les poubelles, la porte de mon appartement s'est refermée avec les clés à l'intérieur. Un serrurier… *(Le dépannage serrurier (clés oubliées à l'intérieur) est prévu jusqu'à 300 EUR, mais seulement s'il est organisé avec la)*
