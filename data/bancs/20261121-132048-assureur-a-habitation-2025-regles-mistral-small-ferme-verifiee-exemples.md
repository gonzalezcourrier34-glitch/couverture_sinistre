# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee, exemples)

2026-11-21T13:18:07 · jeu ferme (20 cas, empreinte `6997c9e1e2012a80`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0.667 | ✗ |
| chaine | faux_refus | ≤ 1 | 0.333 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.933 | ✓ |
| chaine | instables | ≤ 3 | 3 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 4.95 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-21T12:51:33, mistral:mistral-small-latest · verifiee, exemples)

- chaine · exactitude : 0.917 → 0.933
- chaine · exactitude_stricte : 0.817 → 0.833
- chaine · faux_couverts : 0.333 → 0.667

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 93% (85% – 100%) | 83% (75% – 90%) | **0.667 (0 – 1)** | **0.333 (0 – 1)** | 32% (30% – 35%) |

Instables : **3** sur 20 · rappel des clauses : 42% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 41.0 s · par cas, un à la fois (10 cas) : médiane 3.52 s, 95e centile 4.95 s (lecture 2.95 s, décision 0.03 s) · en masse (quatre à la fois) : médiane 3.61 s, 95e centile 38.2 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 85% | 1 ⚠ | 1 |
| garantie : ? | 20 | 85% | 1 ⚠ | 1 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 3 | 100% | 0 | 0 |
| thème : exclusion | 3 | 67% | 1 ⚠ | 0 |
| thème : extension | 2 | 100% | 0 | 0 |
| thème : incertain | 5 | 100% | 0 | 0 |
| thème : piege | 4 | 75% | 0 | 0 |
| thème : rc | 2 | 50% | 0 | 1 |

### Erreurs et instabilités

- **⚠ couvert à tort** `f-a11` attendu NC, obtenu C NC C — Mon chat a sauté sur le meuble du salon et a fait tomber mon grand vase en verre soufflé, qui s'est brisé en m… *(Un vase en verre n'est ni une vitre ni un bien assimilé : exclu du bris de vitrages ; le heurt causé au contenu par un a)*
- `f-a14` attendu NC, obtenu ? NC NC — Pendant le gros coup de vent de mardi, le store banne de mon balcon a été arraché et ses bras sont complètemen… *(Quelle que soit la vitesse du vent, la garantie tempête exclut les dégâts à tout objet situé à l'extérieur, même fixé à )*
- `f-a18` attendu C, obtenu NC C C — En faisant du vélo dans le parc, je n'ai pas vu un piéton qui traversait l'allée et je l'ai renversé. Il s'est… *(Dommage corporel causé à un tiers pendant une activité de loisir de la vie privée, avec un vélo sans moteur : RC vie pri)*
