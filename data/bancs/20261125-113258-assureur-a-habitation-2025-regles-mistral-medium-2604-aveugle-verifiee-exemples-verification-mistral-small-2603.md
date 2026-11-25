# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-medium-2604` (verifiee, exemples, verification mistral-small-2603)

2026-11-25T11:31:08 · jeu aveugle (20 cas, empreinte `586a54c8b3ff46f1`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « aveugle » : sans faits idéaux, la chaîne complète seule

## Portes : **PASSE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.95 | ✓ |
| chaine | instables | ≤ 3 | 0 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 6.33 | ✓ |

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 95% (95% – 95%) | 75% (75% – 75%) | **0 (0 – 0)** | **0 (0 – 0)** | 25% (25% – 25%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 8 | 0 |
| Non couvert | 7 | 0 |
| À préciser | 4 | 1 |

Instables : **0** sur 20 · rappel des clauses : 50% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 24.3 s · par cas, un à la fois (10 cas) : médiane 3.32 s, 95e centile 6.33 s (lecture 2.56 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 4.15 s, 95e centile 6.54 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 95% | 0 | 0 |
| garantie : ? | 20 | 95% | 0 | 0 |
| thème : base | 7 | 86% | 0 | 0 |
| thème : condition | 1 | 100% | 0 | 0 |
| thème : definition | 3 | 100% | 0 | 0 |
| thème : exclusion | 4 | 100% | 0 | 0 |
| thème : manque | 3 | 100% | 0 | 0 |
| thème : option | 2 | 100% | 0 | 0 |

### Erreurs et instabilités

- `av-a07` attendu C, obtenu ? ? ? — J'ai claqué la porte de mon appartement en sortant les poubelles et mes clés sont restées à l'intérieur. Je vo… *(L'oubli des clés à l'intérieur ouvre droit au dépannage serrurier, et l'assuré contacte l'assistance avant toute interve)*
