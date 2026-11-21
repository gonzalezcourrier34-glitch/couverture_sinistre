# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee, exemples)

2026-11-21T15:18:25 · jeu ferme (20 cas, empreinte `6997c9e1e2012a80`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0.333 | ✗ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.9 | ✓ |
| chaine | instables | ≤ 3 | 3 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 5 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-21T14:41:10, mistral:mistral-small-latest · verifiee, exemples)

- chaine · exactitude : 0.883 → 0.9
- chaine · exactitude_stricte : 0.783 → 0.8
- chaine · faux_couverts : 0.667 → 0.333

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 90% (85% – 95%) | 80% (75% – 85%) | **0.333 (0 – 1)** | **0 (0 – 0)** | 38% (35% – 40%) |

Instables : **3** sur 20 · rappel des clauses : 41% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 38.3 s · par cas, un à la fois (10 cas) : médiane 3.81 s, 95e centile 5.0 s (lecture 2.81 s, décision 0.03 s) · en masse (quatre à la fois) : médiane 4.58 s, 95e centile 37.33 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 95% | 0 | 0 |
| garantie : ? | 20 | 95% | 0 | 0 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 3 | 100% | 0 | 0 |
| thème : exclusion | 3 | 100% | 0 | 0 |
| thème : extension | 2 | 100% | 0 | 0 |
| thème : incertain | 5 | 100% | 0 | 0 |
| thème : piege | 4 | 75% | 0 | 0 |
| thème : rc | 2 | 100% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `f-a11` attendu NC, obtenu NC C NC — Mon chat a sauté sur le meuble du salon et a fait tomber mon grand vase en verre soufflé, qui s'est brisé en m… *(Un vase en verre n'est ni une vitre ni un bien assimilé : exclu du bris de vitrages ; le heurt causé au contenu par un a)*
- `f-a12` attendu C, obtenu C ? C — Après une panne du réseau électrique, tout le quartier est resté sans courant pendant une dizaine d'heures. To… *(La perte de denrées après une coupure de courant soudaine due au réseau, de plus de 6 heures, est couverte par 2.6 (limi)*
- `f-a14` attendu NC, obtenu ? ? ? — Pendant le gros coup de vent de mardi, le store banne de mon balcon a été arraché et ses bras sont complètemen… *(Quelle que soit la vitesse du vent, la garantie tempête exclut les dégâts à tout objet situé à l'extérieur, même fixé à )*
- `f-a18` attendu C, obtenu C C ? — En faisant du vélo dans le parc, je n'ai pas vu un piéton qui traversait l'allée et je l'ai renversé. Il s'est… *(Dommage corporel causé à un tiers pendant une activité de loisir de la vie privée, avec un vélo sans moteur : RC vie pri)*
