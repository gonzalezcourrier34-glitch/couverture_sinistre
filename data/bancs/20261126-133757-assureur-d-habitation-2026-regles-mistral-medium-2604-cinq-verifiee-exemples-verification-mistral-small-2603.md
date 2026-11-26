# Banc d'essai — assureur-d-habitation-2026, méthode `regles`, lecture par `mistral:mistral-medium-2604` (verifiee, exemples, verification mistral-small-2603)

2026-11-26T13:36:13 · jeu cinq (20 cas, empreinte `803c89e5c297b233`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « cinq » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 1 | ✗ |
| chaine | faux_refus | ≤ 1 | 3 | ✗ |
| chaine | exactitude | ≥ 0.85 | 0.517 | ✗ |
| chaine | instables | ≤ 3 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 6.32 | ✓ |

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 52% (50% – 55%) | 42% (40% – 45%) | **1 (1 – 1)** | **3 (3 – 3)** | 48% (45% – 50%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 1 | 1 |
| Non couvert | 4.33 | 4 |
| À préciser | 5 | 4.67 |

Instables : **1** sur 20 · rappel des clauses : 3% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 21.7 s · par cas, un à la fois (10 cas) : médiane 3.49 s, 95e centile 6.32 s (lecture 2.64 s, décision 0.02 s) · en masse (quatre à la fois) : médiane 3.88 s, 95e centile 5.68 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 55% | 1 ⚠ | 3 |
| garantie : ? | 20 | 55% | 1 ⚠ | 3 |
| thème : base | 2 | 0% | 0 | 0 |
| thème : condition | 2 | 0% | 0 | 1 |
| thème : definition | 3 | 33% | 0 | 1 |
| thème : exclusion | 6 | 67% | 1 ⚠ | 1 |
| thème : manque | 2 | 100% | 0 | 0 |
| thème : option | 5 | 80% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `c-d19` attendu NC, obtenu C C C — Nous avons hérité de la maison de mes parents, que nous assurons chez vous ; elle est vide et personne n'y a m… *(Les locaux inoccupés ou inutilisés depuis plus de 12 mois consécutifs sont exclus des biens immobiliers assurés.)*
- `c-d01` attendu C, obtenu ? ? ? — Mardi après-midi, un avion militaire est passé au-dessus du village avec un énorme bang. Deux carreaux des fen… *(L'ébranlement dû au franchissement du mur du son est un événement annexe de la garantie incendie, acquise dans toutes le)*
- `c-d06` attendu C, obtenu ? ? ? — Pendant les fortes pluies de dimanche, l'eau est entrée par la bouche d'aération de la VMC au plafond de la sa… *(Les infiltrations par les gaines d'aération ou de ventilation font partie des venues d'eau garanties.)*
- `c-d08` attendu NC, obtenu NC ? ? — Ma trottinette électrique a pris feu pendant qu'elle chargeait dans l'entrée. J'ai pu éteindre vite et l'appar… *(Les engins de déplacement personnel motorisés (dont la trottinette électrique) sont exclus des biens mobiliers assurés.)*
- `c-d09` attendu C, obtenu NC NC NC — En tondant ma pelouse avec mon tracteur-tondeuse, un caillou a été projeté par-dessus la haie et a cassé la vi… *(La RC vie privée couvre expressément l'usage des tondeuses autoportées dans la propriété ou à ses abords, malgré l'exclu)*
- `c-d12` attendu C, obtenu ? ? ? — Je me déplace en fauteuil roulant manuel. En descendant un trottoir en ville, il a basculé : le cadre est fêlé… *(Le fauteuil roulant, automoteur ou non, est assuré en cas de bris accidentel en tous lieux, sans franchise.)*
- `c-d15` attendu C, obtenu NC NC NC — Un feu de broussailles parti du terrain d'à côté a gagné ma propriété : la clôture en bois et le portail ont b… *(L'incendie est garanti ; le défaut de débroussaillage réduit seulement l'indemnité de 50 %, il ne supprime pas la garant)*
- `c-d16` attendu NC, obtenu ? ? ? — J'ai 46 ans. En changeant une ampoule chez moi, je suis tombé de l'escabeau et me suis fracturé l'épaule. Le m… *(Pour un assuré de 18 ans ou plus, aucun capital n'est versé si le taux d'invalidité permanente est inférieur à 10 %.)*
- `c-d18` attendu C, obtenu NC NC NC — Pendant nos vacances en Italie, un incendie s'est déclaré dans notre hôtel en pleine nuit. Nous avons été évac… *(Les bagages sont assurés dans les chambres d'hôtel de l'Union européenne et l'incendie est un événement garanti.)*
- `c-d20` attendu ?, obtenu NC NC NC — En vacances à Barcelone, on m'a volé mon portefeuille dans le métro : carte d'identité, permis de conduire et … *(Le vol des papiers en tous lieux de l'Union européenne n'est garanti qu'en formules Confort et Excellence.)*
