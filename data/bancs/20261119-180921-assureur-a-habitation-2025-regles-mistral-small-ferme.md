# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-19T18:06:47 · jeu ferme (20 cas, empreinte `6997c9e1e2012a80`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 2 | ✗ |
| chaine | faux_refus | ≤ 1 | 1 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.733 | ✗ |
| chaine | instables | ≤ 3 | 1 | ✓ |
| chaine | rappel_questions | ≥ 0.8 | 0 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 5.62 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-19T17:53:24, mistral:mistral-small-latest · verifiee)

- chaine · exactitude : 0.767 → 0.733
- chaine · exactitude_stricte : 0.667 → 0.633
- chaine · faux_couverts : 1.667 → 2
- chaine · faux_refus : 0 → 1

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 73% (70% – 75%) | 63% (60% – 65%) | **2 (2 – 2)** | **1 (1 – 1)** | 37% (35% – 40%) |

Instables : **1** sur 20 · rappel des clauses : 38% · rappel des questions : 0% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 38.3 s · par cas, un à la fois (10 cas) : médiane 3.89 s, 95e centile 5.62 s (lecture 2.98 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.15 s, 95e centile 68.2 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 75% | 2 ⚠ | 1 |
| garantie : ? | 20 | 75% | 2 ⚠ | 1 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 3 | 100% | 0 | 0 |
| thème : exclusion | 3 | 67% | 1 ⚠ | 0 |
| thème : extension | 2 | 50% | 0 | 0 |
| thème : incertain | 5 | 80% | 1 ⚠ | 0 |
| thème : piege | 4 | 75% | 0 | 1 |
| thème : rc | 2 | 50% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `f-a13` attendu NC, obtenu C C C — Une surtension pendant l'orage a grillé l'ordinateur que mon employeur m'a fourni pour le télétravail, ainsi q… *(Le matériel à usage professionnel est exclu de la garantie action de l'électricité, et le « matériel » ne fait pas parti)*
- **⚠ couvert à tort** `f-a17` attendu ?, obtenu C C C — J'ai emménagé dans mon nouvel appartement à Namur il y a deux mois. Hier soir, un court-circuit dans la cuisin… *(L'incendie est un péril couvert, mais après un déménagement en Belgique l'assurance prend fin si l'assureur n'a pas été )*
- `f-a10` attendu C, obtenu NC NC NC — Une cocotte en fonte m'a échappé des mains et est tombée sur ma plaque de cuisson vitrocéramique : elle est fe… *(Les tables de cuisson en vitrocéramique sont assimilées aux vitres dans la garantie bris de vitrages, et aucune exclusio)*
- `f-a12` attendu C, obtenu ? ? ? — Après une panne du réseau électrique, tout le quartier est resté sans courant pendant une dizaine d'heures. To… *(La perte de denrées après une coupure de courant soudaine due au réseau, de plus de 6 heures, est couverte par 2.6 (limi)*
- `f-a14` attendu NC, obtenu NC ? NC — Pendant le gros coup de vent de mardi, le store banne de mon balcon a été arraché et ses bras sont complètemen… *(Quelle que soit la vitesse du vent, la garantie tempête exclut les dégâts à tout objet situé à l'extérieur, même fixé à )*
- `f-a18` attendu C, obtenu ? ? ? — En faisant du vélo dans le parc, je n'ai pas vu un piéton qui traversait l'allée et je l'ai renversé. Il s'est… *(Dommage corporel causé à un tiers pendant une activité de loisir de la vie privée, avec un vélo sans moteur : RC vie pri)*
