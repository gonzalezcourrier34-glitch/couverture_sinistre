# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-medium-latest` (verifiee, exemples, verification mistral-small)

2026-11-22T13:29:00 · jeu ferme (20 cas, empreinte `6997c9e1e2012a80`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0.333 | ✗ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.983 | ✓ |
| chaine | instables | ≤ 3 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 6.77 | ✓ |

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 98% (95% – 100%) | 93% (90% – 95%) | **0.333 (0 – 1)** | **0 (0 – 0)** | 25% (25% – 25%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 8 | 0.33 |
| Non couvert | 6.67 | 0 |
| À préciser | 5 | 0 |

Instables : **1** sur 20 · rappel des clauses : 41% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 20.9 s · par cas, un à la fois (10 cas) : médiane 4.75 s, 95e centile 6.77 s (lecture 3.46 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 4.03 s, 95e centile 5.91 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 95% | 1 ⚠ | 0 |
| garantie : ? | 20 | 95% | 1 ⚠ | 0 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 3 | 100% | 0 | 0 |
| thème : exclusion | 3 | 100% | 0 | 0 |
| thème : extension | 2 | 100% | 0 | 0 |
| thème : incertain | 5 | 100% | 0 | 0 |
| thème : piege | 4 | 75% | 1 ⚠ | 0 |
| thème : rc | 2 | 100% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `f-a02` attendu NC, obtenu C NC NC — J'ai oublié le fer à repasser posé sur une chemise pendant que je répondais au téléphone. La chemise et la hou… *(Le lexique précise que les brûlures aux linges et vêtements et l'excès de chaleur sans embrasement ne constituent pas un)*
