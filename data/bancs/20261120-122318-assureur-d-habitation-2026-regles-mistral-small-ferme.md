# Banc d'essai — assureur-d-habitation-2026, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-20T12:20:07 · jeu ferme (25 cas, empreinte `10ac77778aa67e9a`) · cas validés par l'auteur : 0 sur 25

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.92 | ✓ |
| chaine | instables | ≤ 3 | 0 | ✓ |
| chaine | rappel_questions | ≥ 0.8 | 0 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 21.81 | ✗ |

## Depuis le banc précédent de même configuration (2026-11-20T11:32:54, mistral:mistral-small-latest · verifiee)

- chaine · exactitude : 0.88 → 0.92
- chaine · exactitude_stricte : 0.88 → 0.92

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 92% (92% – 92%) | 92% (92% – 92%) | **0 (0 – 0)** | **0 (0 – 0)** | 36% (36% – 36%) |

Instables : **0** sur 25 · rappel des clauses : 4% · rappel des questions : 0% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 44.5 s · par cas, un à la fois (10 cas) : médiane 4.21 s, 95e centile 21.81 s (lecture 3.07 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.34 s, 95e centile 36.8 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 25 | 92% | 0 | 0 |
| garantie : ? | 25 | 92% | 0 | 0 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 6 | 100% | 0 | 0 |
| thème : exclusion | 4 | 100% | 0 | 0 |
| thème : incertain | 6 | 100% | 0 | 0 |
| thème : piege | 6 | 83% | 0 | 0 |
| thème : rc | 2 | 50% | 0 | 0 |

### Erreurs et instabilités

- `f-d09` attendu C, obtenu ? ? ? — Mon fils de 12 ans a perdu l'équilibre à vélo et a cassé le rétroviseur et rayé la portière d'une voiture garé… *(Dommage matériel causé à un tiers par un enfant mineur dont l'assuré est civilement responsable, dans la vie privée, ave)*
- `f-d14` attendu NC, obtenu ? ? ? — Pendant la tempête de la semaine dernière (rafales à 130 km/h), le trampoline des enfants, qui était dans le j… *(Les objets en plein air sont exclus de la garantie tempête. Un trampoline ne fait pas partie du mobilier de jardin du Pa)*
