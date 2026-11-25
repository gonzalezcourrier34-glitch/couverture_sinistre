# Banc d'essai — assureur-b-habitation-2017, méthode `regles`, lecture par `mistral:mistral-medium-2604` (verifiee, exemples, verification mistral-small-2603)

2026-11-25T10:50:09 · jeu ferme (20 cas, empreinte `e419734e12e73607`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **PASSE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.9 | ✓ |
| chaine | instables | ≤ 3 | 0 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 8.2 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-24T23:50:32, mistral:mistral-medium-2604 · verifiee, exemples, verification mistral-small-2603)

- chaine · exactitude : 0.917 → 0.9
- chaine · exactitude_stricte : 0.867 → 0.85

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 90% (90% – 90%) | 85% (85% – 85%) | **0 (0 – 0)** | **0 (0 – 0)** | 40% (40% – 40%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 8 | 0 |
| Non couvert | 4 | 0 |
| À préciser | 6 | 2 |

Instables : **0** sur 20 · rappel des clauses : 36% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 38.2 s · par cas, un à la fois (10 cas) : médiane 4.61 s, 95e centile 8.2 s (lecture 3.33 s, décision 0.06 s) · en masse (quatre à la fois) : médiane 6.56 s, 95e centile 13.78 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 90% | 0 | 0 |
| garantie : ? | 20 | 90% | 0 | 0 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 4 | 100% | 0 | 0 |
| thème : exclusion | 4 | 50% | 0 | 0 |
| thème : incertain | 5 | 100% | 0 | 0 |
| thème : piege | 4 | 100% | 0 | 0 |
| thème : rc | 2 | 100% | 0 | 0 |

### Erreurs et instabilités

- `f-b06` attendu NC, obtenu ? ? ? — J'avais laissé ma porte d'entrée ouverte le temps de descendre chercher le courrier. Quelqu'un en a profité po… *(Vol sans forcement ni dégradation d'une fermeture : c'est un vol simple, exclu de la garantie vol (3.1.6.2.1).)*
- `f-b07` attendu NC, obtenu ? ? ? — Dans le bus en allant au travail, j'avais posé mon sac sur le siège à côté de moi. Quelqu'un l'a pris en desce… *(Vol à la sauvette (bien à portée de main pris à l'insu de l'assuré) hors du logement : exclu de la garantie vol.)*
