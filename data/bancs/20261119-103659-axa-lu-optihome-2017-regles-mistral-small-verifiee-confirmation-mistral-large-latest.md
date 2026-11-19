# Banc d'essai — axa-lu-optihome-2017, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee, confirmation mistral-large-latest)

2026-11-19T10:30:40 · golden set v9 (15 cas, empreinte `6e6521c0eaa83be7`) · cas validés par l'auteur : 0 sur 15


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 0.5 | ✗ |
| regles | questions_par_incertain | ≤ 3 | 1.5 | ✓ |
| lecture | decisions_changees | ≤ 2 | 4 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 1 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 2 | ✓ |
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.822 | ✗ |
| chaine | instables | ≤ 3 | 1 | ✓ |
| chaine | rappel_questions | ≥ 0.8 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 53.12 | ✗ |

## Depuis le banc précédent (2026-11-18T22:35:06)

- regles · exactitude_stricte : 0.933 → 0.867
- lecture · rappel_faits : 0.823 → 0.754
- chaine · exactitude : 0.755 → 0.822
- chaine · exactitude_stricte : 0.555 → 0.622

## Couche 1 — règles seules (faits idéaux, sans modèle)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 100% | 87% | **0** | **0** | 13% |

Rappel des questions attendues : 50% · questions posées par réponse « incertain » : 1.5

Raisonnement par hypothèses : incertains tranchés par une ou deux questions : 50% · questions inutiles retirées : 15

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

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **4** par exécution, dont **1** cas vers un couvert à tort.

Rappel des faits idéaux : 75% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 2 cas · faits vagues : 0 cas · faits en trop : 7 cas · faits retirés (sans appui ou non dits) : 13 cas

### La lecture change la décision

- **⚠ vers couvert** `axa-v03` idéal NC, lu C C C · manque : auteur = tiers; proprietaire = assure; vol_sur_personne = non · en trop : type_dommage = bris; vitre_placee = oui · retiré sans appui : travaux_batiment = aucun; vol_sur_personne = non
- `axa-v06` idéal NC, lu ? ? ? · manque : auteur = tiers; effraction = non; violence = non · retiré sans appui : effraction = non; violence = non
- `axa-v08` idéal NC, lu NC ? NC · manque : auteur = tiers; violence = non · en trop : abus_confiance = non; sejour_temporaire = non
- `axa-v09` idéal NC, lu ? ? ? · **contredit** : bien : objet_divers lu mobilier · manque : auteur = tiers; serrure_surete = non; vol_sur_personne = non · retiré sans appui : serrure_surete = non
- `axa-v12` idéal NC, lu NC ? ? · manque : effraction = non; proprietaire = assure; violence = non; vol_sur_personne = non · en trop : abus_confiance = oui · retiré sans appui : effraction = non; vol_sur_personne = non

### Contradictions sans effet sur la décision

- `axa-v05` : bien : valeurs lu objet_divers

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 82% (80% – 87%) | 62% (60% – 67%) | **0 (0 – 0)** | **0 (0 – 0)** | 51% (47% – 53%) |

Instables : **1** sur 15 · rappel des clauses : 77% · rappel des questions : 100% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 72.4 s · par cas, un à la fois (10 cas) : médiane 7.75 s, 95e centile 53.12 s (lecture 3.4 s, décision 0.02 s) · en masse (quatre à la fois) : médiane 8.64 s, 95e centile 46.49 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 15 | 87% | 0 | 0 |
| garantie : 3.1.6 | 15 | 87% | 0 | 0 |
| thème : base | 6 | 100% | 0 | 0 |
| thème : incertain | 2 | 100% | 0 | 0 |
| thème : piege | 7 | 71% | 0 | 0 |

### Erreurs et instabilités

- `axa-v06` attendu NC, obtenu ? ? ? — Dans le tram, on m'a subtilisé mon portefeuille dans la poche sans que je m'en rende compte. J'ai la formule P… *(Vol à la tire hors du bâtiment désigné (3.1.6.2.2), et vol simple.)*
- `axa-v09` attendu NC, obtenu ? ? ? — J'habite un appartement. Ma cave, fermée par un simple cadenas, a été forcée et on y a volé des skis. J'ai por… *(Occupation partielle : contenu des caves exclu s'il n'est pas fermé par une serrure de sûreté (3.1.6.2.7).)*
- `axa-v12` attendu NC, obtenu NC ? ? — Je soupçonne la femme de ménage d'avoir pris des bijoux pendant qu'elle travaillait chez nous. Aucune effracti… *(Personne au service de l'Assuré pendant les heures de service (3.1.6.2.4) ; c'est aussi un vol simple.)*
