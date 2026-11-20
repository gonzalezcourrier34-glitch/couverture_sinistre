# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-20T14:40:48 · jeu ferme (20 cas, empreinte `6997c9e1e2012a80`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 1 | ✗ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.85 | ✓ |
| chaine | instables | ≤ 3 | 3 | ✓ |
| chaine | rappel_questions | ≥ 0.8 | 0 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 5.21 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-20T14:27:52, mistral:mistral-small-latest · verifiee)

- chaine · exactitude_stricte : 0.75 → 0.767
- chaine · faux_refus : 0.333 → 0

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 85% (80% – 90%) | 77% (75% – 80%) | **1 (1 – 1)** | **0 (0 – 0)** | 27% (25% – 30%) |

Instables : **3** sur 20 · rappel des clauses : 42% · rappel des questions : 0% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 41.0 s · par cas, un à la fois (10 cas) : médiane 4.04 s, 95e centile 5.21 s (lecture 2.71 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.43 s, 95e centile 6.54 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 80% | 1 ⚠ | 0 |
| garantie : ? | 20 | 80% | 1 ⚠ | 0 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 3 | 100% | 0 | 0 |
| thème : exclusion | 3 | 100% | 0 | 0 |
| thème : extension | 2 | 50% | 0 | 0 |
| thème : incertain | 5 | 60% | 1 ⚠ | 0 |
| thème : piege | 4 | 75% | 0 | 0 |
| thème : rc | 2 | 100% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `f-a17` attendu ?, obtenu C C C — J'ai emménagé dans mon nouvel appartement à Namur il y a deux mois. Hier soir, un court-circuit dans la cuisin… *(L'incendie est un péril couvert, mais après un déménagement en Belgique l'assurance prend fin si l'assureur n'a pas été )*
- `f-a07` attendu ?, obtenu NC NC ? — Ma cave au sous-sol de l'immeuble a été forcée et vidée : on m'a pris une caisse à outils, un vélo d'apparteme… *(Le vol du contenu des caves en immeuble à appartements n'est pris en charge (jusqu'à 1.000 EUR) que si la cave est fermé)*
- `f-a12` attendu C, obtenu ? C C — Après une panne du réseau électrique, tout le quartier est resté sans courant pendant une dizaine d'heures. To… *(La perte de denrées après une coupure de courant soudaine due au réseau, de plus de 6 heures, est couverte par 2.6 (limi)*
- `f-a14` attendu NC, obtenu ? ? ? — Pendant le gros coup de vent de mardi, le store banne de mon balcon a été arraché et ses bras sont complètemen… *(Quelle que soit la vitesse du vent, la garantie tempête exclut les dégâts à tout objet situé à l'extérieur, même fixé à )*
- `f-a15` attendu NC, obtenu NC ? ? — Après les orages, le ruisseau derrière l'immeuble a débordé et l'eau a envahi les caves. Mes cartons de livres… *(Le débordement relève des catastrophes naturelles, mais en cas d'inondation le contenu entreposé à moins de 10 cm du sol)*
