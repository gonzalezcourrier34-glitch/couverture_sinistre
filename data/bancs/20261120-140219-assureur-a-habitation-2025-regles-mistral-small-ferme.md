# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-20T13:59:48 · jeu ferme (20 cas, empreinte `6997c9e1e2012a80`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 2 | ✗ |
| chaine | faux_refus | ≤ 1 | 1 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.783 | ✗ |
| chaine | instables | ≤ 3 | 3 | ✓ |
| chaine | rappel_questions | ≥ 0.8 | 0 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 6.23 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-20T12:33:17, mistral:mistral-small-latest · verifiee)

- chaine · exactitude : 0.8 → 0.783
- chaine · exactitude_stricte : 0.7 → 0.717
- chaine · faux_couverts : 1.667 → 2
- chaine · faux_refus : 0 → 1

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 78% (75% – 80%) | 72% (65% – 75%) | **2 (2 – 2)** | **1 (1 – 1)** | 35% (35% – 35%) |

Instables : **3** sur 20 · rappel des clauses : 40% · rappel des questions : 0% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 38.5 s · par cas, un à la fois (10 cas) : médiane 3.16 s, 95e centile 6.23 s (lecture 2.4 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.09 s, 95e centile 68.89 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 80% | 2 ⚠ | 1 |
| garantie : ? | 20 | 80% | 2 ⚠ | 1 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 3 | 100% | 0 | 0 |
| thème : exclusion | 3 | 67% | 1 ⚠ | 0 |
| thème : extension | 2 | 100% | 0 | 0 |
| thème : incertain | 5 | 80% | 1 ⚠ | 0 |
| thème : piege | 4 | 75% | 0 | 0 |
| thème : rc | 2 | 50% | 0 | 1 |

### Erreurs et instabilités

- **⚠ couvert à tort** `f-a13` attendu NC, obtenu C C C — Une surtension pendant l'orage a grillé l'ordinateur que mon employeur m'a fourni pour le télétravail, ainsi q… *(Le matériel à usage professionnel est exclu de la garantie action de l'électricité, et le « matériel » ne fait pas parti)*
- **⚠ couvert à tort** `f-a17` attendu ?, obtenu C C C — J'ai emménagé dans mon nouvel appartement à Namur il y a deux mois. Hier soir, un court-circuit dans la cuisin… *(L'incendie est un péril couvert, mais après un déménagement en Belgique l'assurance prend fin si l'assureur n'a pas été )*
- `f-a12` attendu C, obtenu C ? ? — Après une panne du réseau électrique, tout le quartier est resté sans courant pendant une dizaine d'heures. To… *(La perte de denrées après une coupure de courant soudaine due au réseau, de plus de 6 heures, est couverte par 2.6 (limi)*
- `f-a14` attendu NC, obtenu ? NC ? — Pendant le gros coup de vent de mardi, le store banne de mon balcon a été arraché et ses bras sont complètemen… *(Quelle que soit la vitesse du vent, la garantie tempête exclut les dégâts à tout objet situé à l'extérieur, même fixé à )*
- `f-a16` attendu ?, obtenu ? ? C — La rivière a débordé après plusieurs jours de pluie et l'eau est montée à 30 cm dans mon appartement au rez-de… *(L'inondation est couverte, sauf pour un bâtiment (et son contenu) construit plus de 18 mois après le classement de la zo)*
- `f-a18` attendu C, obtenu NC NC NC — En faisant du vélo dans le parc, je n'ai pas vu un piéton qui traversait l'allée et je l'ai renversé. Il s'est… *(Dommage corporel causé à un tiers pendant une activité de loisir de la vie privée, avec un vélo sans moteur : RC vie pri)*
