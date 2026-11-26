# Banc d'essai — assureur-b-habitation-2017, méthode `regles`, lecture par `mistral:mistral-medium-2604` (verifiee, exemples, verification mistral-small-2603)

2026-11-25T22:46:10 · jeu quatre (20 cas, empreinte `effcbe87b5002f6f`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « quatre » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 1.333 | ✗ |
| chaine | faux_refus | ≤ 1 | 1 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.833 | ✗ |
| chaine | instables | ≤ 3 | 2 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 5.75 | ✓ |

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 83% (80% – 85%) | 75% (70% – 80%) | **1.333 (1 – 2)** | **1 (1 – 1)** | 37% (35% – 40%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 6.67 | 1.33 |
| Non couvert | 3.67 | 1 |
| À préciser | 6.33 | 1 |

Instables : **2** sur 20 · rappel des clauses : 36% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 27.0 s · par cas, un à la fois (10 cas) : médiane 3.54 s, 95e centile 5.75 s (lecture 2.84 s, décision 0.02 s) · en masse (quatre à la fois) : médiane 4.66 s, 95e centile 7.52 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 80% | 2 ⚠ | 1 |
| garantie : ? | 20 | 80% | 2 ⚠ | 1 |
| thème : base | 5 | 100% | 0 | 0 |
| thème : condition | 2 | 0% | 1 ⚠ | 0 |
| thème : definition | 2 | 50% | 0 | 1 |
| thème : exclusion | 5 | 80% | 1 ⚠ | 0 |
| thème : manque | 2 | 100% | 0 | 0 |
| thème : option | 4 | 100% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `q-b10` attendu NC, obtenu C C C — Je travaille de chez moi deux jours par semaine. Hier, j'ai fait tomber de mon bureau l'ordinateur portable qu… *(La garantie matériel multimédia ne vise que le matériel dont l'assuré est propriétaire ; le heurt exclut les dégâts caus)*
- **⚠ couvert à tort** `q-b15` attendu NC, obtenu C NC NC — Dimanche matin, un raccord a lâché sous l'évier de la cuisine. J'ai coupé l'eau tout de suite, il n'y a aucun … *(L'assistance d'urgence ne paie que le réparateur qu'elle mandate après appel au moment des faits ; une intervention orga)*
- `q-b04` attendu C, obtenu NC NC NC — Jeudi soir, pendant la tempête (la station météo de l'aéroport a relevé des rafales à 110 km/h), ma tonnelle e… *(Le vent dépasse 80 km/h, donc il y a tempête ; les objets non fixés à l'extérieur sont exclus sauf le mobilier de jardin)*
- `q-b18` attendu NC, obtenu ? ? ? — Il y a six semaines, j'ai commandé un robot-tondeuse neuf à 890 € sur le site internet d'un vendeur installé à… *(Même si la protection liée à internet est souscrite, l'achat en ligne n'est garanti que si le vendeur est établi au Luxe)*
- `q-b20` attendu ?, obtenu C C ? — Ce matin, j'ai découvert que la façade et la porte de garage de la maison où j'habite avaient été couvertes de… *(Le vandalisme sur le bâtiment n'est couvert (jusqu'à 2 500 €) que si l'assuré en est propriétaire, que la maison est occ)*
