# Banc d'essai — assureur-b-habitation-2017, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-19T15:20:19 · golden set v12 (15 cas, empreinte `60454afe2fa4e1ae`) · cas validés par l'auteur : 0 sur 15


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 1.5 | ✓ |
| lecture | decisions_changees | ≤ 2 | 3.67 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 1 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 0 | ✓ |
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.778 | ✗ |
| chaine | instables | ≤ 3 | 2 | ✓ |
| chaine | rappel_questions | ≥ 0.8 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 6.16 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-19T14:48:23, mistral:mistral-small-latest · verifiee)

- lecture · rappel_faits : 0.819 → 0.804
- chaine · exactitude : 0.733 → 0.778
- chaine · exactitude_stricte : 0.467 → 0.511

## Couche 1 — règles seules (faits idéaux, sans modèle)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 100% | 87% | **0** | **0** | 13% |

Rappel des questions attendues : 100% · questions posées par réponse « incertain » : 1.5

Raisonnement par hypothèses : incertains tranchés par une ou deux questions : 50% · questions inutiles retirées : 16

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

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **3.67** par exécution, dont **1** cas vers un couvert à tort.

Rappel des faits idéaux : 80% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 0 cas · faits vagues : 0 cas · faits en trop : 7 cas · faits retirés (sans appui ou non dits) : 15 cas

### La lecture change la décision

- **⚠ vers couvert** `b-v03` idéal NC, lu C C C · manque : auteur = tiers; proprietaire = assure; vol_sur_personne = non · en trop : type_dommage = bris · retiré sans appui : vol_sur_personne = non
- `b-v08` idéal NC, lu ? ? ? · manque : auteur = tiers; effraction = non · en trop : abus_confiance = non · retiré sans appui : auteur = tiers; effraction = non; sejour_temporaire = non
- `b-v09` idéal NC, lu ? ? ? · manque : auteur = tiers; serrure_surete = non; vol_sur_personne = non · en trop : violence = non · retiré sans appui : sejour_temporaire = non; serrure_surete = non; vehicule_vole = non
- `b-v12` idéal NC, lu NC ? ? · manque : auteur = personnel_prive; violence = non; vol_sur_personne = non · en trop : abus_confiance = oui; confiance_assure = oui · retiré sans appui : auteur = personnel_prive; sejour_temporaire = non; violence = non; vol_sur_personne = non


## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 78% (73% – 80%) | 51% (47% – 53%) | **0 (0 – 0)** | **0 (0 – 0)** | 49% (47% – 53%) |

Instables : **2** sur 15 · rappel des clauses : 83% · rappel des questions : 100% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 21.0 s · par cas, un à la fois (10 cas) : médiane 4.7 s, 95e centile 6.16 s (lecture 3.57 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 4.6 s, 95e centile 12.43 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 15 | 80% | 0 | 0 |
| garantie : 3.1.6 | 15 | 80% | 0 | 0 |
| thème : base | 6 | 100% | 0 | 0 |
| thème : incertain | 2 | 100% | 0 | 0 |
| thème : piege | 7 | 57% | 0 | 0 |

### Erreurs et instabilités

- `b-v02` attendu NC, obtenu ? NC ? — J'avais laissé la porte de l'appartement ouverte pour descendre les poubelles. En remontant, mon portefeuille … *(Vol simple : ni effraction ni violence (3.1.6.2.1).)*
- `b-v06` attendu NC, obtenu ? ? ? — Dans le tram, on m'a subtilisé mon portefeuille dans la poche sans que je m'en rende compte. J'ai la formule P… *(Vol à la tire hors du bâtiment désigné (3.1.6.2.2), et vol simple.)*
- `b-v09` attendu NC, obtenu ? ? ? — J'habite un appartement. Ma cave, fermée par un simple cadenas, a été forcée et on y a volé des skis. J'ai por… *(Occupation partielle : contenu des caves exclu s'il n'est pas fermé par une serrure de sûreté (3.1.6.2.7).)*
- `b-v12` attendu NC, obtenu NC ? ? — Je soupçonne la femme de ménage d'avoir pris des bijoux pendant qu'elle travaillait chez nous. Aucune effracti… *(Personne au service de l'Assuré pendant les heures de service (3.1.6.2.4) ; c'est aussi un vol simple.)*
