# Banc d'essai — assureur-b-habitation-2017, méthode `regles`, lecture par `mistral:mistral-medium-2604` (verifiee, exemples, verification mistral-small-2603)

2026-11-26T13:33:41 · jeu cinq (20 cas, empreinte `82b25a5568eae836`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « cinq » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 1.667 | ✗ |
| chaine | faux_refus | ≤ 1 | 2 | ✗ |
| chaine | exactitude | ≥ 0.85 | 0.717 | ✗ |
| chaine | instables | ≤ 3 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 8.09 | ✓ |

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 72% (70% – 75%) | 72% (70% – 75%) | **1.667 (1 – 2)** | **2 (2 – 2)** | 40% (40% – 40%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 4 | 1.67 |
| Non couvert | 4.33 | 2 |
| À préciser | 6 | 2 |

Instables : **1** sur 20 · rappel des clauses : 18% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 33.9 s · par cas, un à la fois (10 cas) : médiane 4.36 s, 95e centile 8.09 s (lecture 3.1 s, décision 0.03 s) · en masse (quatre à la fois) : médiane 4.71 s, 95e centile 8.52 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 70% | 2 ⚠ | 2 |
| garantie : ? | 20 | 70% | 2 ⚠ | 2 |
| thème : base | 4 | 75% | 0 | 1 |
| thème : condition | 1 | 0% | 0 | 0 |
| thème : definition | 3 | 100% | 0 | 0 |
| thème : exclusion | 7 | 43% | 2 ⚠ | 1 |
| thème : manque | 1 | 100% | 0 | 0 |
| thème : option | 4 | 100% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `c-b04` attendu NC, obtenu C C NC — Après l'orage de dimanche, la box internet que mon fournisseur d'accès m'a mise à disposition ne s'allume plus… *(La garantie dégâts électriques exclut les équipements dont l'assuré n'est pas propriétaire ; la box appartient au fourni)*
- **⚠ couvert à tort** `c-b11` attendu NC, obtenu C C C — Mon lecteur de musique portable est tombé de ma poche dans l'escalier et la prise du casque est cassée. Le rép… *(La garantie matériel multimédia exclut les dommages d'un montant inférieur à 60 €.)*
- `c-b02` attendu NC, obtenu ? ? ? — Depuis cet hiver la ventilation de la salle de bains ne fonctionne plus. L'eau ruisselle sur les murs après ch… *(Les dommages causés par la condensation sont exclus de la garantie dégâts des eaux ; il n'y a ni rupture ni débordement )*
- `c-b06` attendu C, obtenu NC NC NC — Après trois jours de grosses chutes de neige, le toit de mon abri à voiture s'est affaissé sous le poids et la… *(Le poids de la neige est garanti ; les constructions ouvertes sont exclues sauf les car-ports solidement fixés au bâtime)*
- `c-b08` attendu C, obtenu ? ? ? — Hier au café on m'a volé mon sac, avec dedans les clés de ma maison. J'ai porté plainte le soir même et je vou… *(La garantie vol prend en charge le remplacement des clés et serrures après vol des clés, la plainte et la déclaration so)*
- `c-b15` attendu C, obtenu NC NC NC — La tombe familiale qui m'appartient, au cimetière de ma commune, a été saccagée pendant la nuit : la stèle a é… *(L'extension « sépulture » couvre les sépultures appartenant à un assuré situées au Luxembourg ou à moins de 50 km des fr)*
