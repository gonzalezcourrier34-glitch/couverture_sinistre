# Banc d'essai — assureur-d-habitation-2026, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee, exemples)

2026-11-21T15:23:52 · jeu ferme (25 cas, empreinte `10ac77778aa67e9a`) · cas validés par l'auteur : 0 sur 25

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **PASSE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.947 | ✓ |
| chaine | instables | ≤ 3 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 5.44 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-21T14:46:42, mistral:mistral-small-latest · verifiee, exemples)

- chaine · exactitude : 1 → 0.947
- chaine · exactitude_stricte : 1 → 0.947

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 95% (92% – 96%) | 95% (92% – 96%) | **0 (0 – 0)** | **0 (0 – 0)** | 33% (32% – 36%) |

Instables : **1** sur 25 · rappel des clauses : 4% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 48.7 s · par cas, un à la fois (10 cas) : médiane 3.75 s, 95e centile 5.44 s (lecture 2.33 s, décision 0.03 s) · en masse (quatre à la fois) : médiane 4.3 s, 95e centile 37.73 s

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

- `f-d01` attendu C, obtenu ? ? ? — J'ai oublié une poêle d'huile sur le feu de la gazinière, elle s'est enflammée. La hotte, les placards du haut… *(Incendie hors d'un foyer normal, fumée comprise : garantie commune aux trois formules. Le feu n'a pas pris naissance dan)*
- `f-d08` attendu C, obtenu C ? C — Lors de la crue du mois dernier, l'eau est montée d'un mètre dans le rez-de-chaussée. L'arrêté de catastrophe … *(Inondation reconnue catastrophe naturelle par arrêté publié au JO, déclarée dix jours après la publication, donc dans le)*
