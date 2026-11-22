# Banc d'essai — assureur-b-habitation-2017, méthode `regles`, lecture par `mistral:mistral-medium-latest` (verifiee, exemples)

2026-11-22T13:17:56 · jeu ferme (20 cas, empreinte `e419734e12e73607`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 1 | ✗ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.8 | ✗ |
| chaine | instables | ≤ 3 | 0 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 4.89 | ✓ |

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 80% (80% – 80%) | 75% (75% – 75%) | **1 (1 – 1)** | **0 (0 – 0)** | 40% (40% – 40%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 7 | 1 |
| Non couvert | 4 | 0 |
| À préciser | 5 | 3 |

Instables : **0** sur 20 · rappel des clauses : 32% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 20.8 s · par cas, un à la fois (10 cas) : médiane 3.52 s, 95e centile 4.89 s (lecture 2.78 s, décision 0.02 s) · en masse (quatre à la fois) : médiane 3.93 s, 95e centile 5.98 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 80% | 1 ⚠ | 0 |
| garantie : ? | 20 | 80% | 1 ⚠ | 0 |
| thème : assistance | 1 | 0% | 0 | 0 |
| thème : base | 4 | 100% | 0 | 0 |
| thème : exclusion | 4 | 75% | 0 | 0 |
| thème : incertain | 5 | 80% | 1 ⚠ | 0 |
| thème : piege | 4 | 100% | 0 | 0 |
| thème : rc | 2 | 50% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `f-b18` attendu ?, obtenu C C C — J'ai garé ma voiture devant la gare pour la journée. En revenant, la vitre arrière était brisée et mon ordinat… *(Le vol de matériel multimédia dans un véhicule fracturé est prévu, mais seulement si le véhicule était fermé à clé et le)*
- `f-b07` attendu NC, obtenu ? ? ? — Dans le bus en allant au travail, j'avais posé mon sac sur le siège à côté de moi. Quelqu'un l'a pris en desce… *(Vol à la sauvette (bien à portée de main pris à l'insu de l'assuré) hors du logement : exclu de la garantie vol.)*
- `f-b12` attendu C, obtenu ? ? ? — Le tuyau d'arrivée d'eau de ma machine à laver a éclaté. L'eau a traversé le plancher et abîmé le plafond et u… *(Dégât des eaux garanti qui se propage chez un tiers : couvert par le recours des tiers (frais annexes), alors que la RC )*
- `f-b13` attendu NC, obtenu ? ? ? — J'ai signé mon contrat il y a deux semaines. Hier soir, ma chaudière s'est mise à fuir et j'ai appelé le numér… *(Les interventions d'urgence pour fuites d'eau et chauffage central sont soumises à un délai d'attente de 30 jours après )*
