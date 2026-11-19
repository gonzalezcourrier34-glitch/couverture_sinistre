# Banc d'essai — assureur-b-habitation-2017, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-19T17:44:11 · jeu ferme (20 cas, empreinte `e419734e12e73607`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 1.333 | ✗ |
| chaine | exactitude | ≥ 0.85 | 0.567 | ✗ |
| chaine | instables | ≤ 3 | 2 | ✓ |
| chaine | rappel_questions | ≥ 0.8 | 0 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 5.5 | ✓ |

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 57% (55% – 60%) | 52% (50% – 55%) | **0 (0 – 0)** | **1.333 (1 – 2)** | 37% (35% – 40%) |

Instables : **2** sur 20 · rappel des clauses : 20% · rappel des questions : 0% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 44.4 s · par cas, un à la fois (10 cas) : médiane 4.09 s, 95e centile 5.5 s (lecture 3.59 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 4.17 s, 95e centile 37.62 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 60% | 0 | 1 |
| garantie : ? | 20 | 60% | 0 | 1 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 4 | 100% | 0 | 0 |
| thème : exclusion | 4 | 50% | 0 | 0 |
| thème : incertain | 5 | 60% | 0 | 0 |
| thème : piege | 4 | 25% | 0 | 1 |
| thème : rc | 2 | 50% | 0 | 0 |

### Erreurs et instabilités

- `f-b01` attendu C, obtenu ? ? ? — Une braise a sauté du poêle à bois et est tombée sur le tapis du salon. Le tapis est brûlé sur une vingtaine d… *(Contrairement à une définition stricte de l'incendie, 3.1.1.1.6 couvre les dégâts au mobilier causés par le contact avec)*
- `f-b02` attendu C, obtenu NC NC NC — Je suis parti un mois en Asie en février et j'avais coupé le chauffage. À mon retour, une conduite avait gelé … *(Le dégât des eaux est couvert ; si les conduites n'ont pas été vidangées ou protégées (absence de plus de 15 jours, loca)*
- `f-b03` attendu NC, obtenu ? ? ? — Pendant l'orage de la nuit, l'eau est entrée par la fenêtre de toit de la chambre que j'avais laissée entrouve… *(Les entrées d'eau de pluie par des ouvertures (fenêtres, lucarnes), fermées ou non, sont exclues des dégâts des eaux ; l)*
- `f-b04` attendu NC, obtenu ? ? ? — L'an dernier j'ai eu une fuite dans la salle de bain, qui a été remboursée. Depuis quelques mois, des taches d… *(Les dommages causés par des champignons ou moisissures sont exclus, même lorsqu'ils font suite à un sinistre couvert.)*
- `f-b05` attendu C, obtenu C C NC — Des cambrioleurs ont forcé la porte-fenêtre de la terrasse pendant que nous étions au cinéma. Ils ont pris une… *(Vol avec effraction du contenu dans le logement et plainte déposée : garantie vol 3.1.6.1 (les plafonds pour objets de v)*
- `f-b06` attendu NC, obtenu ? ? ? — J'avais laissé ma porte d'entrée ouverte le temps de descendre chercher le courrier. Quelqu'un en a profité po… *(Vol sans forcement ni dégradation d'une fermeture : c'est un vol simple, exclu de la garantie vol (3.1.6.2.1).)*
- `f-b13` attendu NC, obtenu NC ? NC — J'ai signé mon contrat il y a deux semaines. Hier soir, ma chaudière s'est mise à fuir et j'ai appelé le numér… *(Les interventions d'urgence pour fuites d'eau et chauffage central sont soumises à un délai d'attente de 30 jours après )*
- `f-b16` attendu ?, obtenu NC NC NC — Mon chien s'est échappé du jardin et a mordu le facteur à la jambe. Il a eu des points de suture et me réclame… *(Les dommages causés par un animal domestique relèvent de la RC vie privée, qui fait partie d'une option ; la réponse dép)*
- `f-b17` attendu ?, obtenu NC NC NC — On a forcé la porte de la remise au fond de mon jardin et on m'a volé la tondeuse et la caisse à outils. J'ai … *(Le vol dans une annexe n'est couvert (2.500 EUR) que si elle est équipée d'une serrure à cylindre ; à défaut, seule la f)*
- `f-b19` attendu ?, obtenu NC NC NC — Mon violon est tombé de son pupitre pendant que je rangeais la pièce. La table d'harmonie est fendue et il fau… *(La casse accidentelle d'un instrument de musique n'est couverte que par la garantie optionnelle « dommages aux biens » d)*
