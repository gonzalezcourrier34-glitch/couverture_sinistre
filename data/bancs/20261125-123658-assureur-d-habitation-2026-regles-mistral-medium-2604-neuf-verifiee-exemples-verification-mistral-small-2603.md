# Banc d'essai — assureur-d-habitation-2026, méthode `regles`, lecture par `mistral:mistral-medium-2604` (verifiee, exemples, verification mistral-small-2603)

2026-11-25T12:35:03 · jeu neuf (20 cas, empreinte `3578cb21a2a49535`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « neuf » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 1 | ✗ |
| chaine | faux_refus | ≤ 1 | 1 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.8 | ✗ |
| chaine | instables | ≤ 3 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 6.42 | ✓ |

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 80% (80% – 80%) | 58% (55% – 60%) | **1 (1 – 1)** | **1 (1 – 1)** | 28% (25% – 30%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 6 | 1 |
| Non couvert | 6.33 | 1 |
| À préciser | 3.67 | 2 |

Instables : **1** sur 20 · rappel des clauses : 44% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 22.9 s · par cas, un à la fois (10 cas) : médiane 4.43 s, 95e centile 6.42 s (lecture 3.08 s, décision 0.02 s) · en masse (quatre à la fois) : médiane 4.1 s, 95e centile 5.71 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 80% | 1 ⚠ | 1 |
| garantie : ? | 20 | 80% | 1 ⚠ | 1 |
| thème : base | 6 | 83% | 0 | 1 |
| thème : condition | 2 | 50% | 0 | 0 |
| thème : definition | 1 | 0% | 1 ⚠ | 0 |
| thème : exclusion | 4 | 75% | 0 | 0 |
| thème : manque | 2 | 100% | 0 | 0 |
| thème : option | 5 | 100% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `n-d15` attendu NC, obtenu C C C — En passant à pied devant le terrain de sport, j'ai reçu en plein visage le ballon d'un adolescent : mes lunett… *(Le recours après un accident causé par un tiers entre bien dans la garantie, mais l'assureur n'intervient pas quand l'en)*
- `n-d05` attendu NC, obtenu ? ? ? — Ma commune a été reconnue en état de catastrophe naturelle pour la sécheresse de l'été dernier. La maison n'a … *(Pour la sécheresse, la garantie catastrophes naturelles écarte les éléments annexes à l'habitation, dont les murs de clô)*
- `n-d10` attendu C, obtenu NC NC NC — En arrosant mes jardinières j'ai fait tomber un pot en terre cuite contre le panneau en verre qui sert de gard… *(La casse est accidentelle et le bris de glaces couvre les parois vitrées qui équipent les balcons des locaux occupés à t)*
- `n-d16` attendu C, obtenu ? ? ? — Un orage de grêle a criblé d'impacts mes volets roulants en aluminium et l'enduit de la façade côté ouest. Dan… *(La grêle sur les façades et les volets est garantie lorsque le phénomène a endommagé d'autres bâtiments du voisinage, ce)*
- `n-d19` attendu ?, obtenu ? ? NC — En rentrant du travail hier soir j'ai trouvé l'appartement fouillé : ma console de jeux et mon ordinateur ont … *(Le vol n'est garanti que s'il y a effraction ou escalade avec traces apparentes (ou violences, vol des clés, fausse qual)*
