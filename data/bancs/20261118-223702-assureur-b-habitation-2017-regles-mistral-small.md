# Banc d'essai — assureur-b-habitation-2017, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-18T22:35:06 · golden set v7 (15 cas, empreinte `dded110154b31222`) · cas validés par l'auteur : 0 sur 15


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 1 | ✓ |
| lecture | decisions_changees | ≤ 2 | 3.67 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 0 | ✓ |
| lecture | cas_avec_contradiction | ≤ 5 | 1 | ✓ |
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.755 | ✗ |
| chaine | instables | ≤ 3 | 1 | ✓ |
| chaine | rappel_questions | ≥ 0.8 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 4.7 | ✓ |

## Depuis le banc précédent (2026-11-18T22:19:18)

- lecture · rappel_faits : 0.812 → 0.823
- chaine · exactitude : 0.622 → 0.755
- chaine · exactitude_stricte : 0.467 → 0.555
- chaine · faux_refus : 1 → 0

## Couche 1 — règles seules (faits idéaux, sans modèle)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 100% | 93% | **0** | **0** | 20% |

Rappel des questions attendues : 100% · questions posées par réponse « incertain » : 1

Raisonnement par hypothèses : incertains tranchés par une ou deux questions : 33% · questions inutiles retirées : 15

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 15 | 100% | 0 | 0 |
| garantie : 3.1.6 | 15 | 100% | 0 | 0 |
| thème : base | 6 | 100% | 0 | 0 |
| thème : incertain | 2 | 100% | 0 | 0 |
| thème : piege | 7 | 100% | 0 | 0 |

### Erreurs des règles

Aucune.

## Couche 2 — lecture des faits par le modèle

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **3.67** par exécution, dont **0** cas vers un couvert à tort.

Rappel des faits idéaux : 82% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 1 cas · faits vagues : 0 cas · faits en trop : 6 cas · faits retirés (sans appui ou non dits) : 14 cas

### La lecture change la décision

- `b-v03` idéal NC, lu ? ? ? · manque : auteur = tiers; plainte_deposee = non; vol_sur_personne = non · retiré sans appui : plainte_deposee = non; sejour_temporaire = non; violence = non; vol_sur_personne = non
- `b-v06` idéal NC, lu ? ? ? · manque : auteur = tiers; effraction = non; proprietaire = assure; violence = non · retiré sans appui : auteur = tiers; effraction = non; violence = non
- `b-v09` idéal NC, lu ? ? ? · **contredit** : bien : objet_divers lu mobilier_jardin · manque : auteur = tiers; serrure_surete = non · retiré sans appui : sejour_temporaire = non; serrure_surete = non; violence = non
- `b-v12` idéal NC, lu ? ? NC · manque : auteur = personnel_prive; effraction = non; violence = non; vol_sur_personne = non · en trop : abus_confiance = oui; confiance_assure = oui · retiré sans appui : auteur = personnel_prive; effraction = non; vol_sur_personne = non


## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 76% (73% – 80%) | 56% (53% – 60%) | **0 (0 – 0)** | **0 (0 – 0)** | 58% (53% – 60%) |

Instables : **1** sur 15 · rappel des clauses : 80% · rappel des questions : 100% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 26.3 s · par cas, un à la fois (10 cas) : médiane 3.32 s, 95e centile 4.7 s (lecture 3.21 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.62 s, 95e centile 35.64 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 15 | 73% | 0 | 0 |
| garantie : 3.1.6 | 15 | 73% | 0 | 0 |
| thème : base | 6 | 83% | 0 | 0 |
| thème : incertain | 2 | 100% | 0 | 0 |
| thème : piege | 7 | 57% | 0 | 0 |

### Erreurs et instabilités

- `b-v02` attendu NC, obtenu ? ? ? — J'avais laissé la porte de l'appartement ouverte pour descendre les poubelles. En remontant, mon portefeuille … *(Vol simple : ni effraction ni violence (3.1.6.2.1).)*
- `b-v06` attendu NC, obtenu ? ? ? — Dans le tram, on m'a subtilisé mon portefeuille dans la poche sans que je m'en rende compte. J'ai la formule P… *(Vol à la tire hors du bâtiment désigné (3.1.6.2.2), et vol simple.)*
- `b-v09` attendu NC, obtenu ? ? ? — J'habite un appartement. Ma cave, fermée par un simple cadenas, a été forcée et on y a volé des skis. J'ai por… *(Occupation partielle : contenu des caves exclu s'il n'est pas fermé par une serrure de sûreté (3.1.6.2.7).)*
- `b-v12` attendu NC, obtenu ? ? NC — Je soupçonne la femme de ménage d'avoir pris des bijoux pendant qu'elle travaillait chez nous. Aucune effracti… *(Personne au service de l'Assuré pendant les heures de service (3.1.6.2.4) ; c'est aussi un vol simple.)*
