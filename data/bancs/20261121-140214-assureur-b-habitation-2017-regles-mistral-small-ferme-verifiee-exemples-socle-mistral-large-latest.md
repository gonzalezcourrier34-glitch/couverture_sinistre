# Banc d'essai — assureur-b-habitation-2017, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee, exemples, socle mistral-large-latest)

2026-11-21T13:52:15 · jeu ferme (20 cas, empreinte `e419734e12e73607`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.65 | ✗ |
| chaine | instables | ≤ 3 | 7 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 31.19 | ✗ |

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 65% (60% – 70%) | 60% (55% – 65%) | **0 (0 – 0)** | **0 (0 – 0)** | 63% (50% – 70%) |

Instables : **7** sur 20 · rappel des clauses : 18% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 121.0 s · par cas, un à la fois (10 cas) : médiane 30.76 s, 95e centile 31.19 s (lecture 14.67 s, décision 0.02 s) · en masse (quatre à la fois) : médiane 26.33 s, 95e centile 30.81 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 60% | 0 | 0 |
| garantie : ? | 20 | 60% | 0 | 0 |
| thème : assistance | 1 | 0% | 0 | 0 |
| thème : base | 4 | 25% | 0 | 0 |
| thème : exclusion | 4 | 25% | 0 | 0 |
| thème : incertain | 5 | 100% | 0 | 0 |
| thème : piege | 4 | 100% | 0 | 0 |
| thème : rc | 2 | 50% | 0 | 0 |

### Erreurs et instabilités

- `f-b01` attendu C, obtenu C ? ? — Une braise a sauté du poêle à bois et est tombée sur le tapis du salon. Le tapis est brûlé sur une vingtaine d… *(Contrairement à une définition stricte de l'incendie, 3.1.1.1.6 couvre les dégâts au mobilier causés par le contact avec)*
- `f-b03` attendu NC, obtenu ? NC ? — Pendant l'orage de la nuit, l'eau est entrée par la fenêtre de toit de la chambre que j'avais laissée entrouve… *(Les entrées d'eau de pluie par des ouvertures (fenêtres, lucarnes), fermées ou non, sont exclues des dégâts des eaux ; l)*
- `f-b05` attendu C, obtenu ? C C — Des cambrioleurs ont forcé la porte-fenêtre de la terrasse pendant que nous étions au cinéma. Ils ont pris une… *(Vol avec effraction du contenu dans le logement et plainte déposée : garantie vol 3.1.6.1 (les plafonds pour objets de v)*
- `f-b06` attendu NC, obtenu ? NC ? — J'avais laissé ma porte d'entrée ouverte le temps de descendre chercher le courrier. Quelqu'un en a profité po… *(Vol sans forcement ni dégradation d'une fermeture : c'est un vol simple, exclu de la garantie vol (3.1.6.2.1).)*
- `f-b07` attendu NC, obtenu ? ? ? — Dans le bus en allant au travail, j'avais posé mon sac sur le siège à côté de moi. Quelqu'un l'a pris en desce… *(Vol à la sauvette (bien à portée de main pris à l'insu de l'assuré) hors du logement : exclu de la garantie vol.)*
- `f-b09` attendu C, obtenu ? ? ? — La foudre est tombée tout près de la maison pendant l'orage. Depuis, mon lave-linge acheté il y a quatre ans e… *(Appareils endommagés par l'action de l'électricité ; ils ont moins de 15 ans et rien n'indique une usure ou une garantie)*
- `f-b11` attendu C, obtenu ? C C — Pendant la tempête de samedi, la station météo a relevé des rafales à 110 km/h. Une partie des tuiles de ma ma… *(Vent supérieur à 80 km/h (tempête), toiture endommagée puis pluie entrée par l'ouverture : la toiture et les dégâts inté)*
- `f-b12` attendu C, obtenu ? ? ? — Le tuyau d'arrivée d'eau de ma machine à laver a éclaté. L'eau a traversé le plancher et abîmé le plafond et u… *(Dégât des eaux garanti qui se propage chez un tiers : couvert par le recours des tiers (frais annexes), alors que la RC )*
- `f-b13` attendu NC, obtenu ? ? ? — J'ai signé mon contrat il y a deux semaines. Hier soir, ma chaudière s'est mise à fuir et j'ai appelé le numér… *(Les interventions d'urgence pour fuites d'eau et chauffage central sont soumises à un délai d'attente de 30 jours après )*
- `f-b14` attendu NC, obtenu C C ? — Je suis resté quatre mois d'affilée chez ma fille à Montréal. À mon retour, la porte de mon appartement avait … *(Quatre mois d'absence (environ 120 nuits consécutives) dépassent les 110 nuits consécutives admises pour une résidence p)*
- `f-b15` attendu ?, obtenu ? NC ? — Après un violent orage, l'eau a dévalé du champ derrière chez moi et a envahi tout le rez-de-chaussée de ma ma… *(Le ruissellement consécutif à des pluies torrentielles relève uniquement de la garantie optionnelle Pluies & inondations)*
