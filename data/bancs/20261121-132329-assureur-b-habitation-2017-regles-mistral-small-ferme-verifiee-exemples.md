# Banc d'essai — assureur-b-habitation-2017, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee, exemples)

2026-11-21T13:20:49 · jeu ferme (20 cas, empreinte `e419734e12e73607`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **PASSE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.883 | ✓ |
| chaine | instables | ≤ 3 | 3 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 5.94 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-21T12:48:47, mistral:mistral-small-latest · verifiee, exemples)

- chaine · exactitude : 0.817 → 0.883
- chaine · exactitude_stricte : 0.767 → 0.833

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 88% (80% – 95%) | 83% (75% – 90%) | **0 (0 – 0)** | **0 (0 – 0)** | 38% (35% – 40%) |

Instables : **3** sur 20 · rappel des clauses : 29% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 38.3 s · par cas, un à la fois (10 cas) : médiane 4.8 s, 95e centile 5.94 s (lecture 3.72 s, décision 0.02 s) · en masse (quatre à la fois) : médiane 5.85 s, 95e centile 36.0 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 95% | 0 | 0 |
| garantie : ? | 20 | 95% | 0 | 0 |
| thème : assistance | 1 | 0% | 0 | 0 |
| thème : base | 4 | 100% | 0 | 0 |
| thème : exclusion | 4 | 100% | 0 | 0 |
| thème : incertain | 5 | 100% | 0 | 0 |
| thème : piege | 4 | 100% | 0 | 0 |
| thème : rc | 2 | 100% | 0 | 0 |

### Erreurs et instabilités

- `f-b06` attendu NC, obtenu NC ? ? — J'avais laissé ma porte d'entrée ouverte le temps de descendre chercher le courrier. Quelqu'un en a profité po… *(Vol sans forcement ni dégradation d'une fermeture : c'est un vol simple, exclu de la garantie vol (3.1.6.2.1).)*
- `f-b12` attendu C, obtenu C C ? — Le tuyau d'arrivée d'eau de ma machine à laver a éclaté. L'eau a traversé le plancher et abîmé le plafond et u… *(Dégât des eaux garanti qui se propage chez un tiers : couvert par le recours des tiers (frais annexes), alors que la RC )*
- `f-b13` attendu NC, obtenu ? ? ? — J'ai signé mon contrat il y a deux semaines. Hier soir, ma chaudière s'est mise à fuir et j'ai appelé le numér… *(Les interventions d'urgence pour fuites d'eau et chauffage central sont soumises à un délai d'attente de 30 jours après )*
- `f-b15` attendu ?, obtenu ? ? NC — Après un violent orage, l'eau a dévalé du champ derrière chez moi et a envahi tout le rez-de-chaussée de ma ma… *(Le ruissellement consécutif à des pluies torrentielles relève uniquement de la garantie optionnelle Pluies & inondations)*
