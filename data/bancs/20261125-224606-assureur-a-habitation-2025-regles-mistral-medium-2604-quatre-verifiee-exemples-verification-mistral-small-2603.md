# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-medium-2604` (verifiee, exemples, verification mistral-small-2603)

2026-11-25T22:44:27 · jeu quatre (20 cas, empreinte `542772b62b5cbc60`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « quatre » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0.667 | ✗ |
| chaine | faux_refus | ≤ 1 | 1 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.617 | ✗ |
| chaine | instables | ≤ 3 | 3 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 6.4 | ✓ |

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 62% (60% – 65%) | 57% (55% – 60%) | **0.667 (0 – 1)** | **1 (1 – 1)** | 35% (30% – 40%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 5.33 | 0.67 |
| Non couvert | 4 | 3 |
| À préciser | 3 | 4 |

Instables : **3** sur 20 · rappel des clauses : 34% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 20.0 s · par cas, un à la fois (10 cas) : médiane 3.62 s, 95e centile 6.4 s (lecture 3.09 s, décision 0.02 s) · en masse (quatre à la fois) : médiane 3.77 s, 95e centile 5.55 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 60% | 0 | 1 |
| garantie : ? | 20 | 60% | 0 | 1 |
| thème : base | 6 | 67% | 0 | 0 |
| thème : condition | 3 | 33% | 0 | 0 |
| thème : definition | 2 | 100% | 0 | 0 |
| thème : exclusion | 7 | 57% | 0 | 1 |
| thème : manque | 1 | 0% | 0 | 0 |
| thème : option | 1 | 100% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `q-a05` attendu NC, obtenu ? C C — J'avais fait poser un store banne au-dessus de ma terrasse, solidement vissé dans la façade. Pendant la tempêt… *(Il y a bien tempête au sens du lexique (d'autres biens endommagés aux alentours), mais la garantie exclut tout objet sit)*
- `q-a02` attendu C, obtenu NC NC NC — Le tuyau de descente des eaux de pluie de l'immeuble d'à côté s'est rompu pendant l'averse. L'eau a giclé cont… *(L'infiltration par une fenêtre est en principe exclue, sauf si elle vient d'une fuite des installations hydrauliques ext)*
- `q-a08` attendu C, obtenu ? C C — Pour les 80 ans de ma mère, nous avions loué une salle des fêtes près de chez nous. J'y avais apporté la veill… *(Le contenu déplacé temporairement dans un autre bâtiment est garanti contre le vol avec effraction des locaux ; la porte)*
- `q-a09` attendu NC, obtenu ? ? ? — Pendant mon match au club de tennis, quelqu'un a forcé le cadenas de mon vestiaire individuel et a pris ma mon… *(Même s'il y a eu forçage, le vol du contenu rangé dans un casier d'une association sportive est expressément exclu de la)*
- `q-a13` attendu ?, obtenu NC NC NC — Un court-circuit dans une multiprise a grillé mon ordinateur fixe et ses deux écrans, dans la pièce qui me ser… *(L'action de l'électricité est garantie, mais pas pour les appareils informatiques à usage professionnel (qui ne font d'a)*
- `q-a14` attendu C, obtenu C C ? — Je garde chez moi, contre paiement, les deux enfants de ma voisine tous les mercredis. La semaine dernière la … *(La responsabilité civile vie privée couvre la garde rémunérée de cinq enfants de tiers au plus, y compris pour les domma)*
- `q-a16` attendu ?, obtenu NC NC NC — Pour arrondir mes fins de mois, je tonds des pelouses chez des particuliers que je trouve grâce à une applicat… *(Un service rémunéré ne reste de la vie privée que s'il passe par une plateforme agréée, entre particuliers, et sous le p)*
- `q-a17` attendu C, obtenu ? ? ? — Je suis en vacances au Portugal et le syndic vient de m'appeler : un incendie a détruit ma cuisine cette nuit,… *(L'incendie est un sinistre couvert survenu à l'adresse assurée pendant que l'assuré est à l'étranger et sa présence est )*
- `q-a18` attendu NC, obtenu ? ? ? — Depuis l'incendie de ma cuisine la semaine dernière, mon appartement est inhabitable et vous m'avez logé à l'h… *(La prestation de garde d'animaux après un sinistre couvert est limitée aux chiens et aux chats, et l'assistance ne couvr)*
