# Banc d'essai — assureur-d-habitation-2026, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-20T10:54:53 · jeu ferme (25 cas, empreinte `10ac77778aa67e9a`) · cas validés par l'auteur : 0 sur 25

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0.333 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.707 | ✗ |
| chaine | instables | ≤ 3 | 2 | ✓ |
| chaine | rappel_questions | ≥ 0.8 | 0 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 4.37 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-20T10:48:06, mistral:mistral-small-latest · verifiee)

- chaine · exactitude : 0.667 → 0.707
- chaine · exactitude_stricte : 0.667 → 0.707
- chaine · faux_couverts : 1 → 0
- chaine · faux_refus : 0 → 0.333

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 71% (68% – 72%) | 71% (68% – 72%) | **0 (0 – 0)** | **0.333 (0 – 1)** | 45% (40% – 48%) |

Instables : **2** sur 25 · rappel des clauses : 3% · rappel des questions : 0% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 46.4 s · par cas, un à la fois (10 cas) : médiane 3.15 s, 95e centile 4.37 s (lecture 2.48 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 2.92 s, 95e centile 20.84 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 25 | 72% | 0 | 0 |
| garantie : ? | 25 | 72% | 0 | 0 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 6 | 83% | 0 | 0 |
| thème : exclusion | 4 | 100% | 0 | 0 |
| thème : incertain | 6 | 83% | 0 | 0 |
| thème : piege | 6 | 50% | 0 | 0 |
| thème : rc | 2 | 0% | 0 | 0 |

### Erreurs et instabilités

- `f-d05` attendu C, obtenu ? ? NC — On a essayé de cambrioler mon appartement pendant que j'étais au travail : la porte d'entrée a été forcée au p… *(Détérioration des biens immobiliers à la suite d'une tentative de vol avec effraction laissant des traces : garantie com)*
- `f-d06` attendu C, obtenu ? ? ? — Nous sommes partis une semaine en vacances et j'ai oublié de mettre l'alarme alors que mon contrat l'exige. De… *(Vol avec effraction : garanti. Le défaut de mise en service de la protection exigée réduit l'indemnité de 50 % au plus ()*
- `f-d09` attendu C, obtenu ? ? ? — Mon fils de 12 ans a perdu l'équilibre à vélo et a cassé le rétroviseur et rayé la portière d'une voiture garé… *(Dommage matériel causé à un tiers par un enfant mineur dont l'assuré est civilement responsable, dans la vie privée, ave)*
- `f-d15` attendu NC, obtenu ? ? ? — Mon cheval, que je garde dans le pré derrière la maison, s'est échappé et a renversé un cycliste sur la route.… *(La responsabilité civile vie privée exclut les dommages causés par les animaux autres que les animaux de compagnie (chie)*
- `f-d16` attendu NC, obtenu ? ? ? — Le garagiste a mal réparé ma voiture : la panne est revenue au bout d'une semaine et il refuse de reprendre le… *(La protection juridique est optionnelle, mais la question ne se pose pas : les litiges liés à la réparation d'un véhicul)*
- `f-d18` attendu NC, obtenu ? ? ? — Je suis allée chercher les enfants à l'école sans fermer la porte à clé. En rentrant, mon ordinateur portable … *(Le vol n'est garanti que s'il y a effraction ou escalade avec traces apparentes, ou dans les cas d'extension (menaces, v)*
- `f-d19` attendu ?, obtenu ? ? NC — Pendant l'orage, la foudre est tombée sur un poteau électrique de la rue. Depuis, la télé, la box internet et … *(C'est une surtension, pas un impact direct de la foudre sur le logement : la garantie dommages électriques s'applique, m)*
- `f-d23` attendu ?, obtenu NC NC NC — À chaque grosse pluie, l'eau traverse le mur de façade côté ouest et a taché le placo et la peinture de la cha… *(Les infiltrations au travers des murs et façades sont garanties, sauf quand la garantie décennale du constructeur doit s)*
