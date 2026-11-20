# Banc d'essai — assureur-d-habitation-2026, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-20T10:34:22 · jeu ferme (25 cas, empreinte `10ac77778aa67e9a`) · cas validés par l'auteur : 0 sur 25

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 1 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.453 | ✗ |
| chaine | instables | ≤ 3 | 1 | ✓ |
| chaine | rappel_questions | ≥ 0.8 | 0 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 3.67 | ✓ |

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 45% (44% – 48%) | 45% (44% – 48%) | **0 (0 – 0)** | **1 (1 – 1)** | 71% (68% – 72%) |

Instables : **1** sur 25 · rappel des clauses : 0% · rappel des questions : 0% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 43.8 s · par cas, un à la fois (10 cas) : médiane 2.27 s, 95e centile 3.67 s (lecture 2.26 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 2.14 s, 95e centile 20.16 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 25 | 48% | 0 | 1 |
| garantie : ? | 25 | 48% | 0 | 1 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 6 | 33% | 0 | 0 |
| thème : exclusion | 4 | 50% | 0 | 0 |
| thème : incertain | 6 | 83% | 0 | 0 |
| thème : piege | 6 | 33% | 0 | 1 |
| thème : rc | 2 | 0% | 0 | 0 |

### Erreurs et instabilités

- `f-d01` attendu C, obtenu ? ? ? — J'ai oublié une poêle d'huile sur le feu de la gazinière, elle s'est enflammée. La hotte, les placards du haut… *(Incendie hors d'un foyer normal, fumée comprise : garantie commune aux trois formules. Le feu n'a pas pris naissance dan)*
- `f-d02` attendu C, obtenu ? ? ? — Pendant la tempête de mardi, le vent a arraché une partie des tuiles de mon toit, plusieurs maisons de la rue … *(Vent assez fort pour endommager d'autres bâtiments du voisinage : la tempête est garantie. La pluie entrée le lendemain,)*
- `f-d03` attendu C, obtenu ? ? ? — Le tuyau d'arrivée de ma machine à laver a lâché pendant la nuit. Le parquet du couloir a gonflé et les plinth… *(Fuite d'un appareil à effet d'eau : garantie venues d'eau. Seul le tuyau à l'origine du dommage n'est pas remboursé (fra)*
- `f-d04` attendu C, obtenu ? ? ? — Notre maison de campagne, assurée chez vous, n'est pas chauffée l'hiver. Je n'avais pas vidé les tuyaux et pen… *(Le gel des conduites est garanti, y compris la réparation de la conduite gelée (l'exclusion de l'élément d'origine ne s')*
- `f-d05` attendu C, obtenu C ? ? — On a essayé de cambrioler mon appartement pendant que j'étais au travail : la porte d'entrée a été forcée au p… *(Détérioration des biens immobiliers à la suite d'une tentative de vol avec effraction laissant des traces : garantie com)*
- `f-d06` attendu C, obtenu NC NC NC — Nous sommes partis une semaine en vacances et j'ai oublié de mettre l'alarme alors que mon contrat l'exige. De… *(Vol avec effraction : garanti. Le défaut de mise en service de la protection exigée réduit l'indemnité de 50 % au plus ()*
- `f-d08` attendu C, obtenu ? ? ? — Lors de la crue du mois dernier, l'eau est montée d'un mètre dans le rez-de-chaussée. L'arrêté de catastrophe … *(Inondation reconnue catastrophe naturelle par arrêté publié au JO, déclarée dix jours après la publication, donc dans le)*
- `f-d09` attendu C, obtenu ? ? ? — Mon fils de 12 ans a perdu l'équilibre à vélo et a cassé le rétroviseur et rayé la portière d'une voiture garé… *(Dommage matériel causé à un tiers par un enfant mineur dont l'assuré est civilement responsable, dans la vie privée, ave)*
- `f-d13` attendu NC, obtenu ? ? ? — Le tuyau d'arrivée d'eau enterré dans le jardin a cassé. L'eau s'est infiltrée dans le sous-sol aménagé et a a… *(Les dommages causés par une fuite de canalisation enterrée sont exclus de la garantie venues d'eau. Même souscrit, le Pa)*
- `f-d14` attendu NC, obtenu ? ? ? — Pendant la tempête de la semaine dernière (rafales à 130 km/h), le trampoline des enfants, qui était dans le j… *(Les objets en plein air sont exclus de la garantie tempête. Un trampoline ne fait pas partie du mobilier de jardin du Pa)*
- `f-d15` attendu NC, obtenu ? ? ? — Mon cheval, que je garde dans le pré derrière la maison, s'est échappé et a renversé un cycliste sur la route.… *(La responsabilité civile vie privée exclut les dommages causés par les animaux autres que les animaux de compagnie (chie)*
- `f-d16` attendu NC, obtenu ? ? ? — Le garagiste a mal réparé ma voiture : la panne est revenue au bout d'une semaine et il refuse de reprendre le… *(La protection juridique est optionnelle, mais la question ne se pose pas : les litiges liés à la réparation d'un véhicul)*
- `f-d17` attendu NC, obtenu ? ? ? — J'ai fait du feu dans ma cheminée ouverte et la fumée a été rabattue dans le salon. Les murs, le plafond et le… *(L'enfumage accidentel est garanti, sauf la fumée provenant d'une cheminée à foyer ouvert, exclue expressément. Il n'y a )*
- `f-d25` attendu ?, obtenu NC NC NC — Des voleurs ont forcé la porte de mon garage, un bâtiment à part au fond du jardin, et ont pris deux vélos et … *(Le garage séparé est une dépendance. En formule Eco, les vols dans les dépendances et le contenu des dépendances sont ex)*
