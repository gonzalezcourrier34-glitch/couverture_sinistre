# Banc d'essai — assureur-d-habitation-2026, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee, exemples, socle mistral-large-latest)

2026-11-21T14:02:15 · jeu ferme (25 cas, empreinte `10ac77778aa67e9a`) · cas validés par l'auteur : 0 sur 25

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 1 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.64 | ✗ |
| chaine | instables | ≤ 3 | 9 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 31.46 | ✗ |

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 64% (60% – 68%) | 64% (60% – 68%) | **0 (0 – 0)** | **1 (1 – 1)** | 60% (56% – 64%) |

Instables : **9** sur 25 · rappel des clauses : 0% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 156.1 s · par cas, un à la fois (10 cas) : médiane 30.74 s, 95e centile 31.46 s (lecture 23.99 s, décision 0.02 s) · en masse (quatre à la fois) : médiane 30.52 s, 95e centile 31.53 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 25 | 64% | 0 | 1 |
| garantie : ? | 25 | 64% | 0 | 1 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 6 | 67% | 0 | 1 |
| thème : exclusion | 4 | 0% | 0 | 0 |
| thème : incertain | 6 | 100% | 0 | 0 |
| thème : piege | 6 | 67% | 0 | 0 |
| thème : rc | 2 | 50% | 0 | 0 |

### Erreurs et instabilités

- `f-d01` attendu C, obtenu ? C C — J'ai oublié une poêle d'huile sur le feu de la gazinière, elle s'est enflammée. La hotte, les placards du haut… *(Incendie hors d'un foyer normal, fumée comprise : garantie commune aux trois formules. Le feu n'a pas pris naissance dan)*
- `f-d02` attendu C, obtenu C ? ? — Pendant la tempête de mardi, le vent a arraché une partie des tuiles de mon toit, plusieurs maisons de la rue … *(Vent assez fort pour endommager d'autres bâtiments du voisinage : la tempête est garantie. La pluie entrée le lendemain,)*
- `f-d05` attendu C, obtenu C C ? — On a essayé de cambrioler mon appartement pendant que j'étais au travail : la porte d'entrée a été forcée au p… *(Détérioration des biens immobiliers à la suite d'une tentative de vol avec effraction laissant des traces : garantie com)*
- `f-d06` attendu C, obtenu C ? ? — Nous sommes partis une semaine en vacances et j'ai oublié de mettre l'alarme alors que mon contrat l'exige. De… *(Vol avec effraction : garanti. Le défaut de mise en service de la protection exigée réduit l'indemnité de 50 % au plus ()*
- `f-d08` attendu C, obtenu NC NC NC — Lors de la crue du mois dernier, l'eau est montée d'un mètre dans le rez-de-chaussée. L'arrêté de catastrophe … *(Inondation reconnue catastrophe naturelle par arrêté publié au JO, déclarée dix jours après la publication, donc dans le)*
- `f-d10` attendu NC, obtenu ? NC ? — Des jeunes ont tagué toute la façade de ma maison et mon portail pendant la nuit. Il faut repeindre. *(Les tags commis à l'extérieur du logement sont expressément exclus des détériorations immobilières, et la garantie vanda)*
- `f-d11` attendu NC, obtenu ? NC NC — Mon fils de 19 ans, qui vit à la maison, a pris ma console de jeux et mon appareil photo pour les revendre. Je… *(Vol commis par un descendant sans plainte nominative : exclu. En plus, il n'y a ni effraction ni escalade.)*
- `f-d12` attendu NC, obtenu NC ? NC — J'avais laissé mes clés dans la boîte aux lettres pour que ma voisine arrose les plantes. Quelqu'un les a pris… *(L'extension au vol des clés ne joue pas : les clés laissées dans une boîte aux lettres et toutes les conséquences de leu)*
- `f-d13` attendu NC, obtenu ? ? ? — Le tuyau d'arrivée d'eau enterré dans le jardin a cassé. L'eau s'est infiltrée dans le sous-sol aménagé et a a… *(Les dommages causés par une fuite de canalisation enterrée sont exclus de la garantie venues d'eau. Même souscrit, le Pa)*
- `f-d14` attendu NC, obtenu NC NC ? — Pendant la tempête de la semaine dernière (rafales à 130 km/h), le trampoline des enfants, qui était dans le j… *(Les objets en plein air sont exclus de la garantie tempête. Un trampoline ne fait pas partie du mobilier de jardin du Pa)*
- `f-d15` attendu NC, obtenu ? ? ? — Mon cheval, que je garde dans le pré derrière la maison, s'est échappé et a renversé un cycliste sur la route.… *(La responsabilité civile vie privée exclut les dommages causés par les animaux autres que les animaux de compagnie (chie)*
- `f-d16` attendu NC, obtenu ? ? ? — Le garagiste a mal réparé ma voiture : la panne est revenue au bout d'une semaine et il refuse de reprendre le… *(La protection juridique est optionnelle, mais la question ne se pose pas : les litiges liés à la réparation d'un véhicul)*
- `f-d17` attendu NC, obtenu ? NC NC — J'ai fait du feu dans ma cheminée ouverte et la fumée a été rabattue dans le salon. Les murs, le plafond et le… *(L'enfumage accidentel est garanti, sauf la fumée provenant d'une cheminée à foyer ouvert, exclue expressément. Il n'y a )*
- `f-d18` attendu NC, obtenu ? ? ? — Je suis allée chercher les enfants à l'école sans fermer la porte à clé. En rentrant, mon ordinateur portable … *(Le vol n'est garanti que s'il y a effraction ou escalade avec traces apparentes, ou dans les cas d'extension (menaces, v)*
