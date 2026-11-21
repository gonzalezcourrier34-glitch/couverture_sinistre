# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee, exemples)

2026-11-21T16:18:25 · jeu ferme (20 cas, empreinte `6997c9e1e2012a80`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 1 | ✗ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.867 | ✓ |
| chaine | instables | ≤ 3 | 2 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 4.75 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-21T15:18:25, mistral:mistral-small-latest · verifiee, exemples)

- chaine · exactitude : 0.9 → 0.867
- chaine · exactitude_stricte : 0.8 → 0.767
- chaine · faux_couverts : 0.333 → 1

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 87% (85% – 90%) | 77% (75% – 80%) | **1 (1 – 1)** | **0 (0 – 0)** | 38% (35% – 40%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 7.33 | 1 |
| Non couvert | 4 | 0 |
| À préciser | 6 | 1.67 |

Instables : **2** sur 20 · rappel des clauses : 42% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 34.5 s · par cas, un à la fois (10 cas) : médiane 3.79 s, 95e centile 4.75 s (lecture 2.97 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.64 s, 95e centile 36.2 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 90% | 1 ⚠ | 0 |
| garantie : ? | 20 | 90% | 1 ⚠ | 0 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 3 | 100% | 0 | 0 |
| thème : exclusion | 3 | 67% | 1 ⚠ | 0 |
| thème : extension | 2 | 100% | 0 | 0 |
| thème : incertain | 5 | 100% | 0 | 0 |
| thème : piege | 4 | 75% | 0 | 0 |
| thème : rc | 2 | 100% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `f-a11` attendu NC, obtenu C C C — Mon chat a sauté sur le meuble du salon et a fait tomber mon grand vase en verre soufflé, qui s'est brisé en m… *(Un vase en verre n'est ni une vitre ni un bien assimilé : exclu du bris de vitrages ; le heurt causé au contenu par un a)*
- `f-a12` attendu C, obtenu C ? C — Après une panne du réseau électrique, tout le quartier est resté sans courant pendant une dizaine d'heures. To… *(La perte de denrées après une coupure de courant soudaine due au réseau, de plus de 6 heures, est couverte par 2.6 (limi)*
- `f-a14` attendu NC, obtenu ? ? ? — Pendant le gros coup de vent de mardi, le store banne de mon balcon a été arraché et ses bras sont complètemen… *(Quelle que soit la vitesse du vent, la garantie tempête exclut les dégâts à tout objet situé à l'extérieur, même fixé à )*
- `f-a18` attendu C, obtenu C C ? — En faisant du vélo dans le parc, je n'ai pas vu un piéton qui traversait l'allée et je l'ai renversé. Il s'est… *(Dommage corporel causé à un tiers pendant une activité de loisir de la vie privée, avec un vélo sans moteur : RC vie pri)*
