# Banc d'essai — assureur-b-habitation-2017, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-19T18:09:21 · jeu ferme (20 cas, empreinte `e419734e12e73607`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0.667 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.6 | ✗ |
| chaine | instables | ≤ 3 | 3 | ✓ |
| chaine | rappel_questions | ≥ 0.8 | 0 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 5.38 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-19T17:55:49, mistral:mistral-small-latest · verifiee)

- chaine · exactitude : 0.617 → 0.6
- chaine · exactitude_stricte : 0.567 → 0.533
- chaine · faux_couverts : 1 → 0
- chaine · faux_refus : 1 → 0.667

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 60% (60% – 60%) | 53% (50% – 55%) | **0 (0 – 0)** | **0.667 (0 – 1)** | 58% (55% – 60%) |

Instables : **3** sur 20 · rappel des clauses : 10% · rappel des questions : 0% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 44.9 s · par cas, un à la fois (10 cas) : médiane 4.07 s, 95e centile 5.38 s (lecture 3.46 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.79 s, 95e centile 37.48 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 60% | 0 | 1 |
| garantie : ? | 20 | 60% | 0 | 1 |
| thème : assistance | 1 | 0% | 0 | 0 |
| thème : base | 4 | 50% | 0 | 1 |
| thème : exclusion | 4 | 50% | 0 | 0 |
| thème : incertain | 5 | 80% | 0 | 0 |
| thème : piege | 4 | 50% | 0 | 0 |
| thème : rc | 2 | 100% | 0 | 0 |

### Erreurs et instabilités

- `f-b01` attendu C, obtenu ? ? ? — Une braise a sauté du poêle à bois et est tombée sur le tapis du salon. Le tapis est brûlé sur une vingtaine d… *(Contrairement à une définition stricte de l'incendie, 3.1.1.1.6 couvre les dégâts au mobilier causés par le contact avec)*
- `f-b02` attendu C, obtenu C ? C — Je suis parti un mois en Asie en février et j'avais coupé le chauffage. À mon retour, une conduite avait gelé … *(Le dégât des eaux est couvert ; si les conduites n'ont pas été vidangées ou protégées (absence de plus de 15 jours, loca)*
- `f-b03` attendu NC, obtenu ? ? ? — Pendant l'orage de la nuit, l'eau est entrée par la fenêtre de toit de la chambre que j'avais laissée entrouve… *(Les entrées d'eau de pluie par des ouvertures (fenêtres, lucarnes), fermées ou non, sont exclues des dégâts des eaux ; l)*
- `f-b04` attendu NC, obtenu ? ? ? — L'an dernier j'ai eu une fuite dans la salle de bain, qui a été remboursée. Depuis quelques mois, des taches d… *(Les dommages causés par des champignons ou moisissures sont exclus, même lorsqu'ils font suite à un sinistre couvert.)*
- `f-b05` attendu C, obtenu NC NC C — Des cambrioleurs ont forcé la porte-fenêtre de la terrasse pendant que nous étions au cinéma. Ils ont pris une… *(Vol avec effraction du contenu dans le logement et plainte déposée : garantie vol 3.1.6.1 (les plafonds pour objets de v)*
- `f-b06` attendu NC, obtenu ? ? ? — J'avais laissé ma porte d'entrée ouverte le temps de descendre chercher le courrier. Quelqu'un en a profité po… *(Vol sans forcement ni dégradation d'une fermeture : c'est un vol simple, exclu de la garantie vol (3.1.6.2.1).)*
- `f-b08` attendu C, obtenu ? ? ? — En passant l'aspirateur, j'ai cogné le manche dans le grand miroir de l'entrée : il est fendu de haut en bas. *(Fêlure accidentelle d'un miroir : couverte par la garantie bris de vitrages, sans exclusion applicable.)*
- `f-b10` attendu NC, obtenu NC NC ? — La même surtension a aussi grillé mon vieux congélateur du garage, qui avait 18 ans. Il ne redémarre plus. *(La garantie dégâts électriques exclut les appareils de plus de 15 ans.)*
- `f-b13` attendu NC, obtenu ? ? ? — J'ai signé mon contrat il y a deux semaines. Hier soir, ma chaudière s'est mise à fuir et j'ai appelé le numér… *(Les interventions d'urgence pour fuites d'eau et chauffage central sont soumises à un délai d'attente de 30 jours après )*
- `f-b17` attendu ?, obtenu NC NC NC — On a forcé la porte de la remise au fond de mon jardin et on m'a volé la tondeuse et la caisse à outils. J'ai … *(Le vol dans une annexe n'est couvert (2.500 EUR) que si elle est équipée d'une serrure à cylindre ; à défaut, seule la f)*
