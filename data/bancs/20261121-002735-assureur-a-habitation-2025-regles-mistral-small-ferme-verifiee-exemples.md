# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee, exemples)

2026-11-21T00:25:20 · jeu ferme (20 cas, empreinte `6997c9e1e2012a80`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0.333 | ✗ |
| chaine | faux_refus | ≤ 1 | 0.333 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.917 | ✓ |
| chaine | instables | ≤ 3 | 3 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 3.75 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-21T00:06:36, mistral:mistral-small-latest · verifiee, exemples)

- chaine · exactitude : 0.933 → 0.917
- chaine · exactitude_stricte : 0.833 → 0.817
- chaine · faux_refus : 0 → 0.333

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 92% (90% – 95%) | 82% (80% – 85%) | **0.333 (0 – 1)** | **0.333 (0 – 1)** | 35% (30% – 40%) |

Instables : **3** sur 20 · rappel des clauses : 40% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 34.8 s · par cas, un à la fois (10 cas) : médiane 3.14 s, 95e centile 3.75 s (lecture 2.46 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.62 s, 95e centile 35.3 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 90% | 1 ⚠ | 1 |
| garantie : ? | 20 | 90% | 1 ⚠ | 1 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 3 | 100% | 0 | 0 |
| thème : exclusion | 3 | 67% | 1 ⚠ | 0 |
| thème : extension | 2 | 100% | 0 | 0 |
| thème : incertain | 5 | 100% | 0 | 0 |
| thème : piege | 4 | 100% | 0 | 0 |
| thème : rc | 2 | 50% | 0 | 1 |

### Erreurs et instabilités

- **⚠ couvert à tort** `f-a11` attendu NC, obtenu C NC NC — Mon chat a sauté sur le meuble du salon et a fait tomber mon grand vase en verre soufflé, qui s'est brisé en m… *(Un vase en verre n'est ni une vitre ni un bien assimilé : exclu du bris de vitrages ; le heurt causé au contenu par un a)*
- `f-a12` attendu C, obtenu C ? ? — Après une panne du réseau électrique, tout le quartier est resté sans courant pendant une dizaine d'heures. To… *(La perte de denrées après une coupure de courant soudaine due au réseau, de plus de 6 heures, est couverte par 2.6 (limi)*
- `f-a18` attendu C, obtenu NC C ? — En faisant du vélo dans le parc, je n'ai pas vu un piéton qui traversait l'allée et je l'ai renversé. Il s'est… *(Dommage corporel causé à un tiers pendant une activité de loisir de la vie privée, avec un vélo sans moteur : RC vie pri)*
