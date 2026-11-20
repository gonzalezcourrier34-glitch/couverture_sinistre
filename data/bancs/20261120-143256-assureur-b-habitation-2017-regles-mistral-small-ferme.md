# Banc d'essai — assureur-b-habitation-2017, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-20T14:30:28 · jeu ferme (20 cas, empreinte `e419734e12e73607`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0.333 | ✗ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.85 | ✓ |
| chaine | instables | ≤ 3 | 5 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 0 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 4.75 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-20T14:02:20, mistral:mistral-small-latest · verifiee)

- chaine · exactitude : 0.633 → 0.85
- chaine · exactitude_stricte : 0.583 → 0.783
- chaine · faux_couverts : 1 → 0.333
- chaine · faux_refus : 0.667 → 0

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 85% (75% – 90%) | 78% (65% – 85%) | **0.333 (0 – 1)** | **0 (0 – 0)** | 43% (40% – 50%) |

Instables : **5** sur 20 · rappel des clauses : 32% · rappel des questions : 0% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 37.1 s · par cas, un à la fois (10 cas) : médiane 3.6 s, 95e centile 4.75 s (lecture 2.77 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 4.01 s, 95e centile 35.24 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 90% | 0 | 0 |
| garantie : ? | 20 | 90% | 0 | 0 |
| thème : assistance | 1 | 0% | 0 | 0 |
| thème : base | 4 | 100% | 0 | 0 |
| thème : exclusion | 4 | 75% | 0 | 0 |
| thème : incertain | 5 | 100% | 0 | 0 |
| thème : piege | 4 | 100% | 0 | 0 |
| thème : rc | 2 | 100% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `f-b18` attendu ?, obtenu ? ? C — J'ai garé ma voiture devant la gare pour la journée. En revenant, la vitre arrière était brisée et mon ordinat… *(Le vol de matériel multimédia dans un véhicule fracturé est prévu, mais seulement si le véhicule était fermé à clé et le)*
- `f-b02` attendu C, obtenu C C ? — Je suis parti un mois en Asie en février et j'avais coupé le chauffage. À mon retour, une conduite avait gelé … *(Le dégât des eaux est couvert ; si les conduites n'ont pas été vidangées ou protégées (absence de plus de 15 jours, loca)*
- `f-b03` attendu NC, obtenu ? NC ? — Pendant l'orage de la nuit, l'eau est entrée par la fenêtre de toit de la chambre que j'avais laissée entrouve… *(Les entrées d'eau de pluie par des ouvertures (fenêtres, lucarnes), fermées ou non, sont exclues des dégâts des eaux ; l)*
- `f-b07` attendu NC, obtenu NC ? ? — Dans le bus en allant au travail, j'avais posé mon sac sur le siège à côté de moi. Quelqu'un l'a pris en desce… *(Vol à la sauvette (bien à portée de main pris à l'insu de l'assuré) hors du logement : exclu de la garantie vol.)*
- `f-b12` attendu C, obtenu C C ? — Le tuyau d'arrivée d'eau de ma machine à laver a éclaté. L'eau a traversé le plancher et abîmé le plafond et u… *(Dégât des eaux garanti qui se propage chez un tiers : couvert par le recours des tiers (frais annexes), alors que la RC )*
- `f-b13` attendu NC, obtenu ? ? ? — J'ai signé mon contrat il y a deux semaines. Hier soir, ma chaudière s'est mise à fuir et j'ai appelé le numér… *(Les interventions d'urgence pour fuites d'eau et chauffage central sont soumises à un délai d'attente de 30 jours après )*
