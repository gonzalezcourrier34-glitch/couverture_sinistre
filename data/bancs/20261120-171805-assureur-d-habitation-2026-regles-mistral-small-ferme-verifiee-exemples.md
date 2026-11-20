# Banc d'essai — assureur-d-habitation-2026, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee, exemples)

2026-11-20T17:13:02 · jeu ferme (25 cas, empreinte `10ac77778aa67e9a`) · cas validés par l'auteur : 0 sur 25

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **PASSE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.973 | ✓ |
| chaine | instables | ≤ 3 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 6.65 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-20T16:46:52, mistral:mistral-small-latest · verifiee, exemples)

- chaine · exactitude : 1 → 0.973
- chaine · exactitude_stricte : 1 → 0.973

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 97% (96% – 100%) | 97% (96% – 100%) | **0 (0 – 0)** | **0 (0 – 0)** | 31% (28% – 32%) |

Instables : **1** sur 25 · rappel des clauses : 4% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 87.0 s · par cas, un à la fois (10 cas) : médiane 4.2 s, 95e centile 6.65 s (lecture 2.97 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 4.56 s, 95e centile 69.57 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 25 | 96% | 0 | 0 |
| garantie : ? | 25 | 96% | 0 | 0 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 6 | 83% | 0 | 0 |
| thème : exclusion | 4 | 100% | 0 | 0 |
| thème : incertain | 6 | 100% | 0 | 0 |
| thème : piege | 6 | 100% | 0 | 0 |
| thème : rc | 2 | 100% | 0 | 0 |

### Erreurs et instabilités

- `f-d08` attendu C, obtenu ? ? C — Lors de la crue du mois dernier, l'eau est montée d'un mètre dans le rez-de-chaussée. L'arrêté de catastrophe … *(Inondation reconnue catastrophe naturelle par arrêté publié au JO, déclarée dix jours après la publication, donc dans le)*
