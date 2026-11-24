# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-medium-2604` (verifiee, exemples, verification mistral-small-2603)

2026-11-24T10:13:56 · golden set v13, partie « test » (31 cas, empreinte `eae57de51468c0ab`) · cas validés par l'auteur : 0 sur 31


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 1 | ✓ |
| lecture | decisions_changees | ≤ 2 | 3 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 0 | ✓ |
| lecture | cas_avec_contradiction | ≤ 5 | 3 | ✓ |
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.935 | ✓ |
| chaine | instables | ≤ 3 | 0 | ✓ |
| chaine | rappel_questions | ≥ 0.8 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 6.8 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-24T09:46:43, mistral:mistral-medium-2604 · verifiee, exemples, verification mistral-small-2603)

- lecture · rappel_faits : 0.891 → 0.895

## Couche 1 — règles seules (faits idéaux, sans modèle)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 100% | 94% | **0** | **0** | 10% |

Rappel des questions attendues : 100% · questions posées par réponse « incertain » : 1

Raisonnement par hypothèses : incertains tranchés par une ou deux questions : 33% · questions inutiles retirées : 7

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 31 | 100% | 0 | 0 |
| garantie : 2.1 | 3 | 100% | 0 | 0 |
| garantie : 2.10 | 13 | 100% | 0 | 0 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.6 | 2 | 100% | 0 | 0 |
| garantie : 2.7 | 5 | 100% | 0 | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 3 | 100% | 0 | 0 |
| garantie : aucune | 1 | 100% | 0 | 0 |
| thème : base | 1 | 100% | 0 | 0 |
| thème : hors_regles | 9 | 100% | 0 | 0 |
| thème : info_manquante | 3 | 100% | 0 | 0 |
| thème : langue | 4 | 100% | 0 | 0 |
| thème : multi | 2 | 100% | 0 | 0 |
| thème : piege | 16 | 100% | 0 | 0 |
| thème : variante | 4 | 100% | 0 | 0 |

### Erreurs des règles

Aucune.

## Couche 2 — lecture des faits par le modèle

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **3** par exécution, dont **0** cas vers un couvert à tort.

Rappel des faits idéaux : 90% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 3 cas · faits vagues : 0 cas · faits en trop : 25 cas · faits retirés (sans appui ou non dits) : 22 cas

### La lecture change la décision

- `velo-06` idéal NC, lu ? ? ? · manque : fermeture = cadenas; violence = non; vol_sur_personne = non · en trop : auteur = tiers; effraction = oui; laisse_sans_surveillance = oui; proprietaire = assure; simple_disparition = non · retiré sans appui : auteur = tiers; simple_disparition = non; vol_sur_personne = non
- `g-h03` idéal C, lu ? ? ? · en trop : bien_a_l_origine_sinistre = oui
- `g2-p01` idéal C, lu ? ? ? · **contredit** : effraction : non lu oui · manque : bien = objet_divers; portes_fermees = oui · en trop : acces_voleur = sans_effraction; auteur = tiers; fermeture = cle; proprietaire = assure; vol_sur_personne = non · retiré sans appui : simple_disparition = non

### Contradictions sans effet sur la décision

- `val-09` : evenement : autre lu fumee
- `g-l07` : evenement : autre lu accident

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 94% (94% – 94%) | 81% (81% – 81%) | **0 (0 – 0)** | **0 (0 – 0)** | 23% (23% – 23%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 15 | 0 |
| Non couvert | 9 | 0 |
| À préciser | 5 | 2 |

Instables : **0** sur 31 · rappel des clauses : 87% · rappel des questions : 100% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 34.4 s · par cas, un à la fois (10 cas) : médiane 4.03 s, 95e centile 6.8 s (lecture 3.25 s, décision 0.02 s) · en masse (quatre à la fois) : médiane 3.8 s, 95e centile 5.86 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 31 | 94% | 0 | 0 |
| garantie : 2.1 | 3 | 100% | 0 | 0 |
| garantie : 2.10 | 13 | 85% | 0 | 0 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.6 | 2 | 100% | 0 | 0 |
| garantie : 2.7 | 5 | 100% | 0 | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 3 | 100% | 0 | 0 |
| garantie : aucune | 1 | 100% | 0 | 0 |
| thème : base | 1 | 100% | 0 | 0 |
| thème : hors_regles | 9 | 100% | 0 | 0 |
| thème : info_manquante | 3 | 100% | 0 | 0 |
| thème : langue | 4 | 100% | 0 | 0 |
| thème : multi | 2 | 100% | 0 | 0 |
| thème : piege | 16 | 94% | 0 | 0 |
| thème : variante | 4 | 75% | 0 | 0 |

### Erreurs et instabilités

- `velo-06` attendu NC, obtenu ? ? ? — Mon vélo était attaché à un arceau dans la rue avec un antivol. L'antivol a été coupé et le vélo volé. *(Vol dans la rue, sans violence : hors du bâtiment, et ce n'est pas un « vol commis sur l'assuré … suite à violences ».)*
- `g2-p01` attendu C, obtenu ? ? ? — Pendant mes vacances, des cambrioleurs ont ouvert ma porte sans la casser : il n'y a que des traces de tournev… *(Pas d'effraction au sens du contrat, mais la porte était fermée à clé : l'obligation est respectée, le vol dans le bâtim)*
