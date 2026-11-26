# Banc d'essai — assureur-d-habitation-2026, méthode `regles`, lecture par `mistral:mistral-medium-2604` (verifiee, exemples, verification mistral-small-2603)

2026-11-25T22:48:13 · jeu quatre (20 cas, empreinte `d4970c048feca97a`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « quatre » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 2.333 | ✗ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.65 | ✗ |
| chaine | instables | ≤ 3 | 2 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 5.63 | ✓ |

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 65% (65% – 65%) | 65% (65% – 65%) | **2.333 (2 – 3)** | **0 (0 – 0)** | 38% (35% – 40%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 4.33 | 2.33 |
| Non couvert | 4.67 | 1 |
| À préciser | 4 | 3.67 |

Instables : **2** sur 20 · rappel des clauses : 50% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 20.6 s · par cas, un à la fois (10 cas) : médiane 3.57 s, 95e centile 5.63 s (lecture 2.97 s, décision 0.02 s) · en masse (quatre à la fois) : médiane 3.7 s, 95e centile 5.45 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 65% | 3 ⚠ | 0 |
| garantie : ? | 20 | 65% | 3 ⚠ | 0 |
| thème : base | 5 | 60% | 0 | 0 |
| thème : condition | 3 | 100% | 0 | 0 |
| thème : definition | 1 | 100% | 0 | 0 |
| thème : exclusion | 5 | 40% | 2 ⚠ | 0 |
| thème : manque | 2 | 50% | 1 ⚠ | 0 |
| thème : option | 4 | 75% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `q-d17` attendu NC, obtenu C NC NC — Pour le mariage de notre fils, 90 invités, nous avions loué l'orangerie d'un château inscrit aux monuments his… *(La situation ressemble à l'extension fêtes familiales (moins de 150 personnes, incendie dans le local loué), mais les ré)*
- **⚠ couvert à tort** `q-d18` attendu ?, obtenu C C C — Je rentre d'un long séjour chez mon fils au Canada et j'ai trouvé la porte-fenêtre de la cuisine fracturée. La… *(Vol par effraction, donc garanti en principe, mais la garantie vol du contenu est suspendue à partir du 46e jour d'inocc)*
- **⚠ couvert à tort** `q-d20` attendu NC, obtenu C C C — Pendant une semaine de vacances à Marrakech, dans un appartement loué par une plateforme, j'ai oublié de ferme… *(La responsabilité civile villégiature ne vaut que dans l'Union européenne, au Royaume-Uni, en Suisse, à Andorre et à Mon)*
- `q-d01` attendu C, obtenu ? ? ? — Hier après-midi un drone, je ne sais pas à qui il appartient, est tombé sur ma fenêtre de toit. Le vitrage est… *(La chute d'un engin volant est un événement de la garantie incendie et événements annexes, sans condition sur son propri)*
- `q-d04` attendu C, obtenu ? ? ? — Pendant la tempête de mardi (des rafales à plus de 110 km/h relevées par la station météo, plusieurs toitures … *(Choc d'un objet projeté par le vent sur le bâtiment assuré, avec l'intensité exigée (plus de 100 km/h et autres bâtiment)*
- `q-d05` attendu NC, obtenu ? ? ? — Après une coupure puis un retour brutal du courant dans le quartier, mon disque dur externe ne répond plus. Le… *(Quelle que soit la formule, la garantie dommages électriques exclut les frais de reconstitution de données, seule chose )*
- `q-d09` attendu ?, obtenu NC NC NC — La tempête de la nuit de jeudi (120 km/h relevés à l'aérodrome voisin) a tordu ma pergola en aluminium, qui es… *(La pergola ne fait pas partie des biens immobiliers de base et la garantie tempête exclut les objets en plein air ; elle)*
- `q-d19` attendu C, obtenu C ? ? — En faisant mes courses dans un magasin de bricolage, une pile de carrelage mal rangée m'est tombée sur le pied… *(Dommage subi lors d'un accident de la vie privée, imputable à un tiers non assuré au contrat et non indemnisable par une)*
