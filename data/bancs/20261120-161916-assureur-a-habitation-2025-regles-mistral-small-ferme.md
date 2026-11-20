# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-20T16:16:47 · jeu ferme (20 cas, empreinte `6997c9e1e2012a80`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0.667 | ✗ |
| chaine | faux_refus | ≤ 1 | 0.667 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.85 | ✓ |
| chaine | instables | ≤ 3 | 4 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 5.53 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-20T15:49:12, mistral:mistral-small-latest · verifiee)

- chaine · faux_couverts : 1.667 → 0.667
- chaine · faux_refus : 0.333 → 0.667

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 85% (80% – 90%) | 75% (70% – 80%) | **0.667 (0 – 1)** | **0.667 (0 – 1)** | 38% (35% – 40%) |

Instables : **4** sur 20 · rappel des clauses : 40% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 38.1 s · par cas, un à la fois (10 cas) : médiane 3.06 s, 95e centile 5.53 s (lecture 2.49 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.1 s, 95e centile 69.1 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 90% | 0 | 0 |
| garantie : ? | 20 | 90% | 0 | 0 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 3 | 100% | 0 | 0 |
| thème : exclusion | 3 | 100% | 0 | 0 |
| thème : extension | 2 | 50% | 0 | 0 |
| thème : incertain | 5 | 100% | 0 | 0 |
| thème : piege | 4 | 75% | 0 | 0 |
| thème : rc | 2 | 100% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `f-a02` attendu NC, obtenu NC C NC — J'ai oublié le fer à repasser posé sur une chemise pendant que je répondais au téléphone. La chemise et la hou… *(Le lexique précise que les brûlures aux linges et vêtements et l'excès de chaleur sans embrasement ne constituent pas un)*
- **⚠ couvert à tort** `f-a11` attendu NC, obtenu NC NC C — Mon chat a sauté sur le meuble du salon et a fait tomber mon grand vase en verre soufflé, qui s'est brisé en m… *(Un vase en verre n'est ni une vitre ni un bien assimilé : exclu du bris de vitrages ; le heurt causé au contenu par un a)*
- `f-a12` attendu C, obtenu ? C ? — Après une panne du réseau électrique, tout le quartier est resté sans courant pendant une dizaine d'heures. To… *(La perte de denrées après une coupure de courant soudaine due au réseau, de plus de 6 heures, est couverte par 2.6 (limi)*
- `f-a14` attendu NC, obtenu ? ? ? — Pendant le gros coup de vent de mardi, le store banne de mon balcon a été arraché et ses bras sont complètemen… *(Quelle que soit la vitesse du vent, la garantie tempête exclut les dégâts à tout objet situé à l'extérieur, même fixé à )*
- `f-a18` attendu C, obtenu C NC NC — En faisant du vélo dans le parc, je n'ai pas vu un piéton qui traversait l'allée et je l'ai renversé. Il s'est… *(Dommage corporel causé à un tiers pendant une activité de loisir de la vie privée, avec un vélo sans moteur : RC vie pri)*
