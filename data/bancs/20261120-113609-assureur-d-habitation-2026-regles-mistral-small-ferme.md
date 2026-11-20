# Banc d'essai — assureur-d-habitation-2026, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-20T11:32:54 · jeu ferme (25 cas, empreinte `10ac77778aa67e9a`) · cas validés par l'auteur : 0 sur 25

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.88 | ✓ |
| chaine | instables | ≤ 3 | 0 | ✓ |
| chaine | rappel_questions | ≥ 0.8 | 0 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 5.29 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-20T11:13:48, mistral:mistral-small-latest · verifiee)

- chaine · exactitude : 0.827 → 0.88
- chaine · exactitude_stricte : 0.827 → 0.88
- chaine · faux_refus : 0.667 → 0

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 88% (88% – 88%) | 88% (88% – 88%) | **0 (0 – 0)** | **0 (0 – 0)** | 40% (40% – 40%) |

Instables : **0** sur 25 · rappel des clauses : 4% · rappel des questions : 0% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 54.0 s · par cas, un à la fois (10 cas) : médiane 2.89 s, 95e centile 5.29 s (lecture 2.43 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.27 s, 95e centile 38.09 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 25 | 88% | 0 | 0 |
| garantie : ? | 25 | 88% | 0 | 0 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 6 | 100% | 0 | 0 |
| thème : exclusion | 4 | 100% | 0 | 0 |
| thème : incertain | 6 | 100% | 0 | 0 |
| thème : piege | 6 | 83% | 0 | 0 |
| thème : rc | 2 | 0% | 0 | 0 |

### Erreurs et instabilités

- `f-d09` attendu C, obtenu ? ? ? — Mon fils de 12 ans a perdu l'équilibre à vélo et a cassé le rétroviseur et rayé la portière d'une voiture garé… *(Dommage matériel causé à un tiers par un enfant mineur dont l'assuré est civilement responsable, dans la vie privée, ave)*
- `f-d15` attendu NC, obtenu ? ? ? — Mon cheval, que je garde dans le pré derrière la maison, s'est échappé et a renversé un cycliste sur la route.… *(La responsabilité civile vie privée exclut les dommages causés par les animaux autres que les animaux de compagnie (chie)*
- `f-d16` attendu NC, obtenu ? ? ? — Le garagiste a mal réparé ma voiture : la panne est revenue au bout d'une semaine et il refuse de reprendre le… *(La protection juridique est optionnelle, mais la question ne se pose pas : les litiges liés à la réparation d'un véhicul)*
