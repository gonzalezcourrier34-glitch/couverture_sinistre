# Banc d'essai — assureur-b-habitation-2017, méthode `regles`, lecture par `mistral:mistral-medium-latest` (verifiee, exemples, verification mistral-small)

2026-11-22T13:33:16 · jeu ferme (20 cas, empreinte `e419734e12e73607`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 1 | ✗ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.817 | ✗ |
| chaine | instables | ≤ 3 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 5.65 | ✓ |

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 82% (80% – 85%) | 77% (75% – 80%) | **1 (1 – 1)** | **0 (0 – 0)** | 38% (35% – 40%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 8 | 1 |
| Non couvert | 3.33 | 0 |
| À préciser | 5 | 2.67 |

Instables : **1** sur 20 · rappel des clauses : 33% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 21.9 s · par cas, un à la fois (10 cas) : médiane 3.97 s, 95e centile 5.65 s (lecture 3.0 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 4.29 s, 95e centile 6.27 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 80% | 1 ⚠ | 0 |
| garantie : ? | 20 | 80% | 1 ⚠ | 0 |
| thème : assistance | 1 | 0% | 0 | 0 |
| thème : base | 4 | 100% | 0 | 0 |
| thème : exclusion | 4 | 50% | 0 | 0 |
| thème : incertain | 5 | 80% | 1 ⚠ | 0 |
| thème : piege | 4 | 100% | 0 | 0 |
| thème : rc | 2 | 100% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `f-b18` attendu ?, obtenu C C C — J'ai garé ma voiture devant la gare pour la journée. En revenant, la vitre arrière était brisée et mon ordinat… *(Le vol de matériel multimédia dans un véhicule fracturé est prévu, mais seulement si le véhicule était fermé à clé et le)*
- `f-b06` attendu NC, obtenu ? ? ? — J'avais laissé ma porte d'entrée ouverte le temps de descendre chercher le courrier. Quelqu'un en a profité po… *(Vol sans forcement ni dégradation d'une fermeture : c'est un vol simple, exclu de la garantie vol (3.1.6.2.1).)*
- `f-b07` attendu NC, obtenu ? ? ? — Dans le bus en allant au travail, j'avais posé mon sac sur le siège à côté de moi. Quelqu'un l'a pris en desce… *(Vol à la sauvette (bien à portée de main pris à l'insu de l'assuré) hors du logement : exclu de la garantie vol.)*
- `f-b13` attendu NC, obtenu ? ? NC — J'ai signé mon contrat il y a deux semaines. Hier soir, ma chaudière s'est mise à fuir et j'ai appelé le numér… *(Les interventions d'urgence pour fuites d'eau et chauffage central sont soumises à un délai d'attente de 30 jours après )*
