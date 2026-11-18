# Banc d'essai — axa-lu-optihome-2017, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-18T22:19:18 · golden set v7 (15 cas, empreinte `dded110154b31222`) · cas validés par l'auteur : 0 sur 15


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 1 | ✓ |
| lecture | decisions_changees | ≤ 2 | 6.33 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 0 | ✓ |
| lecture | cas_avec_contradiction | ≤ 5 | 2 | ✓ |
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 1 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.622 | ✗ |
| chaine | instables | ≤ 3 | 4 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 0.833 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 5.3 | ✓ |

## Depuis le banc précédent (2026-11-18T22:14:46)

- lecture · rappel_faits : 0.69 → 0.812
- chaine · exactitude_stricte : 0.422 → 0.467
- chaine · faux_refus : 1.333 → 1

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

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **6.33** par exécution, dont **0** cas vers un couvert à tort.

Rappel des faits idéaux : 81% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 2 cas · faits vagues : 0 cas · faits en trop : 9 cas · faits retirés (sans appui ou non dits) : 13 cas

### La lecture change la décision

- `axa-v03` idéal NC, lu ? ? ? · manque : auteur = tiers; vol_sur_personne = non · en trop : violence = non · retiré sans appui : sejour_temporaire = non; violence = non; vol_sur_personne = non
- `axa-v04` idéal ?, lu ? NC ? · manque : auteur = tiers; proprietaire = assure; vol_sur_personne = non · en trop : occupation_partielle = non · retiré sans appui : abus_confiance = non; sejour_temporaire = non; violence = non; vol_sur_personne = non
- `axa-v06` idéal NC, lu ? ? ? · **contredit** : vol_sur_personne : oui lu non · manque : auteur = tiers; effraction = non; violence = non · retiré sans appui : auteur = tiers; effraction = non; violence = non
- `axa-v09` idéal NC, lu ? ? ? · manque : auteur = tiers; serrure_surete = non; vol_sur_personne = non · retiré sans appui : abus_confiance = non; sejour_temporaire = non; serrure_surete = non; violence = non; vol_sur_personne = non
- `axa-v10` idéal C, lu NC NC NC · manque : auteur = tiers; proprietaire = assure; vol_sur_personne = non · en trop : violence = non · retiré sans appui : abus_confiance = non; sejour_temporaire = non; serrure_surete = non; violence = non; vol_sur_personne = non
- `axa-v12` idéal NC, lu NC ? ? · manque : effraction = non; violence = non; vol_sur_personne = non · en trop : abus_confiance = oui; confiance_assure = oui · retiré sans appui : confiance_assure = oui; effraction = non; vol_sur_personne = non
- `axa-v14` idéal C, lu ? C ? · manque : proprietaire = assure; vol_sur_personne = non · en trop : violence = non · retiré sans appui : proprietaire = hote; violence = non; vol_sur_personne = non
- `axa-v15` idéal ?, lu NC ? NC · manque : auteur = tiers; vol_sur_personne = non · en trop : abus_confiance = non; lien_causal_travaux = oui; occupation_partielle = non; sejour_temporaire = non; violence = non · retiré sans appui : abus_confiance = non; confiance_assure = non; occupation_partielle = non; sejour_temporaire = non; violence = non; vol_sur_personne = non

### Contradictions sans effet sur la décision

- `axa-v05` : bien : valeurs lu objet_divers

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 62% (60% – 67%) | 47% (40% – 53%) | **0 (0 – 0)** | **1 (1 – 1)** | 56% (53% – 60%) |

Instables : **4** sur 15 · rappel des clauses : 71% · rappel des questions : 83% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 19.0 s · par cas, un à la fois (10 cas) : médiane 4.08 s, 95e centile 5.3 s (lecture 3.57 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.29 s, 95e centile 19.16 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 15 | 67% | 0 | 1 |
| garantie : 3.1.6 | 15 | 67% | 0 | 1 |
| thème : base | 6 | 67% | 0 | 1 |
| thème : incertain | 2 | 100% | 0 | 0 |
| thème : piege | 7 | 57% | 0 | 0 |

### Erreurs et instabilités

- `axa-v02` attendu NC, obtenu ? ? ? — J'avais laissé la porte de l'appartement ouverte pour descendre les poubelles. En remontant, mon portefeuille … *(Vol simple : ni effraction ni violence (3.1.6.2.1).)*
- `axa-v04` attendu ?, obtenu ? NC ? — Cambriolage pendant la nuit : la porte du garage attenant à la maison a été fracturée et des outils et deux vé… *(Rien ne dit si une plainte a été déposée : condition de la garantie, à demander.)*
- `axa-v06` attendu NC, obtenu ? ? ? — Dans le tram, on m'a subtilisé mon portefeuille dans la poche sans que je m'en rende compte. J'ai la formule P… *(Vol à la tire hors du bâtiment désigné (3.1.6.2.2), et vol simple.)*
- `axa-v09` attendu NC, obtenu ? ? ? — J'habite un appartement. Ma cave, fermée par un simple cadenas, a été forcée et on y a volé des skis. J'ai por… *(Occupation partielle : contenu des caves exclu s'il n'est pas fermé par une serrure de sûreté (3.1.6.2.7).)*
- `axa-v10` attendu C, obtenu NC NC NC — Notre garage séparé de la maison, au fond du terrain, est fermé par une serrure à cylindre. Elle a été forcée … *(Annexe non contiguë équipée d'une serrure à cylindre (3.1.6.1, 2 500 €).)*
- `axa-v12` attendu NC, obtenu NC ? ? — Je soupçonne la femme de ménage d'avoir pris des bijoux pendant qu'elle travaillait chez nous. Aucune effracti… *(Personne au service de l'Assuré pendant les heures de service (3.1.6.2.4) ; c'est aussi un vol simple.)*
- `axa-v14` attendu C, obtenu ? C ? — En vacances à Lisbonne, notre chambre d'hôtel a été forcée et mon appareil photo volé. Nous avons porté plaint… *(Vol par effraction dans un bâtiment partout dans le monde, séjour temporaire (3.1.6.1, 2 500 €).)*
- `axa-v15` attendu NC, obtenu NC ? NC — Notre maison est en rénovation, avec un échafaudage sur la façade. Des voleurs sont entrés par une fenêtre de … *(Bâtiment en rénovation (3.1.6.2.9), sauf si l'Assuré démontre que les travaux n'ont pas contribué au vol : ici l'échafau)*
