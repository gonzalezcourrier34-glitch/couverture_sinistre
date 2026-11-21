# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee, exemples, socle mistral-large-latest)

2026-11-21T13:42:42 · jeu ferme (20 cas, empreinte `6997c9e1e2012a80`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0.333 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.65 | ✗ |
| chaine | instables | ≤ 3 | 7 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 31.25 | ✗ |

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 65% (60% – 70%) | 55% (50% – 60%) | **0 (0 – 0)** | **0.333 (0 – 1)** | 63% (60% – 65%) |

Instables : **7** sur 20 · rappel des clauses : 27% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 106.9 s · par cas, un à la fois (10 cas) : médiane 30.76 s, 95e centile 31.25 s (lecture 11.0 s, décision 0.02 s) · en masse (quatre à la fois) : médiane 17.13 s, 95e centile 30.86 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 65% | 0 | 0 |
| garantie : ? | 20 | 65% | 0 | 0 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 3 | 100% | 0 | 0 |
| thème : exclusion | 3 | 33% | 0 | 0 |
| thème : extension | 2 | 0% | 0 | 0 |
| thème : incertain | 5 | 100% | 0 | 0 |
| thème : piege | 4 | 50% | 0 | 0 |
| thème : rc | 2 | 50% | 0 | 0 |

### Erreurs et instabilités

- `f-a01` attendu C, obtenu C C ? — Une poêle d'huile a pris feu sur ma cuisinière pendant que je préparais des frites. Les flammes ont attaqué le… *(Le feu s'est propagé aux placards (embrasement, donc incendie au sens du lexique) et la suie/fumée est expressément couv)*
- `f-a02` attendu NC, obtenu ? ? ? — J'ai oublié le fer à repasser posé sur une chemise pendant que je répondais au téléphone. La chemise et la hou… *(Le lexique précise que les brûlures aux linges et vêtements et l'excès de chaleur sans embrasement ne constituent pas un)*
- `f-a05` attendu C, obtenu C ? C — Pendant que j'étais au travail, quelqu'un a forcé la serrure de ma porte d'entrée : la serrure est à changer. … *(Vol du contenu dans le logement avec serrure forcée (effraction) et plainte déposée immédiatement : garantie vol 2.10, d)*
- `f-a08` attendu C, obtenu ? ? ? — En rentrant à pied le soir, deux hommes m'ont menacé avec un couteau dans la rue et m'ont pris mon sac avec mo… *(Le vol hors du logement est couvert lorsqu'il est commis avec menaces ou violences (limite 2.500 EUR ; valeurs 250 EUR, )*
- `f-a10` attendu C, obtenu ? C C — Une cocotte en fonte m'a échappé des mains et est tombée sur ma plaque de cuisson vitrocéramique : elle est fe… *(Les tables de cuisson en vitrocéramique sont assimilées aux vitres dans la garantie bris de vitrages, et aucune exclusio)*
- `f-a11` attendu NC, obtenu ? NC NC — Mon chat a sauté sur le meuble du salon et a fait tomber mon grand vase en verre soufflé, qui s'est brisé en m… *(Un vase en verre n'est ni une vitre ni un bien assimilé : exclu du bris de vitrages ; le heurt causé au contenu par un a)*
- `f-a12` attendu C, obtenu ? ? C — Après une panne du réseau électrique, tout le quartier est resté sans courant pendant une dizaine d'heures. To… *(La perte de denrées après une coupure de courant soudaine due au réseau, de plus de 6 heures, est couverte par 2.6 (limi)*
- `f-a13` attendu NC, obtenu ? ? ? — Une surtension pendant l'orage a grillé l'ordinateur que mon employeur m'a fourni pour le télétravail, ainsi q… *(Le matériel à usage professionnel est exclu de la garantie action de l'électricité, et le « matériel » ne fait pas parti)*
- `f-a14` attendu NC, obtenu NC ? NC — Pendant le gros coup de vent de mardi, le store banne de mon balcon a été arraché et ses bras sont complètemen… *(Quelle que soit la vitesse du vent, la garantie tempête exclut les dégâts à tout objet situé à l'extérieur, même fixé à )*
- `f-a18` attendu C, obtenu C NC ? — En faisant du vélo dans le parc, je n'ai pas vu un piéton qui traversait l'allée et je l'ai renversé. Il s'est… *(Dommage corporel causé à un tiers pendant une activité de loisir de la vie privée, avec un vélo sans moteur : RC vie pri)*
- `f-a19` attendu NC, obtenu ? ? ? — J'ai emprunté la tondeuse de mon voisin pour le week-end et je l'ai cassée en roulant sur une grosse pierre ca… *(La tondeuse empruntée est un bien dont l'assuré a la garde ; la RC vie privée exclut les dommages aux biens confiés.)*
