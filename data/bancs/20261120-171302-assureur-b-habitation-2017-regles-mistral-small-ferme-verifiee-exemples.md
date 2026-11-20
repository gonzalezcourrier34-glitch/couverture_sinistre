# Banc d'essai — assureur-b-habitation-2017, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee, exemples)

2026-11-20T17:09:57 · jeu ferme (20 cas, empreinte `e419734e12e73607`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.817 | ✗ |
| chaine | instables | ≤ 3 | 3 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 6.87 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-20T16:43:54, mistral:mistral-small-latest · verifiee, exemples)


## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 82% (80% – 85%) | 77% (75% – 80%) | **0 (0 – 0)** | **0 (0 – 0)** | 45% (40% – 50%) |

Instables : **3** sur 20 · rappel des clauses : 28% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 47.0 s · par cas, un à la fois (10 cas) : médiane 4.34 s, 95e centile 6.87 s (lecture 4.07 s, décision 0.03 s) · en masse (quatre à la fois) : médiane 4.63 s, 95e centile 37.85 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 85% | 0 | 0 |
| garantie : ? | 20 | 85% | 0 | 0 |
| thème : assistance | 1 | 0% | 0 | 0 |
| thème : base | 4 | 100% | 0 | 0 |
| thème : exclusion | 4 | 50% | 0 | 0 |
| thème : incertain | 5 | 100% | 0 | 0 |
| thème : piege | 4 | 100% | 0 | 0 |
| thème : rc | 2 | 100% | 0 | 0 |

### Erreurs et instabilités

- `f-b03` attendu NC, obtenu NC ? ? — Pendant l'orage de la nuit, l'eau est entrée par la fenêtre de toit de la chambre que j'avais laissée entrouve… *(Les entrées d'eau de pluie par des ouvertures (fenêtres, lucarnes), fermées ou non, sont exclues des dégâts des eaux ; l)*
- `f-b07` attendu NC, obtenu ? NC ? — Dans le bus en allant au travail, j'avais posé mon sac sur le siège à côté de moi. Quelqu'un l'a pris en desce… *(Vol à la sauvette (bien à portée de main pris à l'insu de l'assuré) hors du logement : exclu de la garantie vol.)*
- `f-b10` attendu NC, obtenu ? ? ? — La même surtension a aussi grillé mon vieux congélateur du garage, qui avait 18 ans. Il ne redémarre plus. *(La garantie dégâts électriques exclut les appareils de plus de 15 ans.)*
- `f-b13` attendu NC, obtenu ? ? ? — J'ai signé mon contrat il y a deux semaines. Hier soir, ma chaudière s'est mise à fuir et j'ai appelé le numér… *(Les interventions d'urgence pour fuites d'eau et chauffage central sont soumises à un délai d'attente de 30 jours après )*
- `f-b15` attendu ?, obtenu ? NC ? — Après un violent orage, l'eau a dévalé du champ derrière chez moi et a envahi tout le rez-de-chaussée de ma ma… *(Le ruissellement consécutif à des pluies torrentielles relève uniquement de la garantie optionnelle Pluies & inondations)*
