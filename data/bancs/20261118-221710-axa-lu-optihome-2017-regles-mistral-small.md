# Banc d'essai — axa-lu-optihome-2017, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-18T22:14:46 · golden set v7 (15 cas, empreinte `dded110154b31222`) · cas validés par l'auteur : 0 sur 15


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 1 | ✓ |
| lecture | decisions_changees | ≤ 2 | 5.33 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 0 | ✓ |
| lecture | cas_avec_contradiction | ≤ 5 | 4 | ✓ |
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 1.333 | ✗ |
| chaine | exactitude | ≥ 0.85 | 0.622 | ✗ |
| chaine | instables | ≤ 3 | 3 | ✓ |
| chaine | rappel_questions | ≥ 0.8 | 0.667 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 5.24 | ✓ |

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

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **5.33** par exécution, dont **0** cas vers un couvert à tort.

Rappel des faits idéaux : 69% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 4 cas · faits vagues : 0 cas · faits en trop : 2 cas · faits retirés (sans appui ou non dits) : 14 cas

### La lecture change la décision

- `axa-v03` idéal NC, lu ? NC ? · manque : auteur = tiers; proprietaire = assure; vol_sur_personne = non · retiré sans appui : violence = non; vol_sur_personne = non
- `axa-v04` idéal ?, lu NC ? ? · manque : auteur = tiers; proprietaire = assure; vol_sur_personne = non · retiré sans appui : abus_confiance = non; sejour_temporaire = non; violence = non; vol_sur_personne = non
- `axa-v06` idéal NC, lu ? ? ? · manque : auteur = tiers; effraction = non; proprietaire = assure; violence = non · retiré sans appui : abus_confiance = non; auteur = tiers; effraction = non; violence = non
- `axa-v09` idéal NC, lu ? ? ? · **contredit** : bien : objet_divers lu mobilier; bien : objet_divers lu mobilier_jardin · manque : auteur = tiers; occupation_partielle = oui; proprietaire = assure; serrure_surete = non; vol_sur_personne = non · retiré sans appui : serrure_surete = non; vol_sur_personne = non
- `axa-v10` idéal C, lu NC NC NC · **contredit** : lieu : annexe lu garage · manque : auteur = tiers; proprietaire = assure; vol_sur_personne = non · retiré sans appui : serrure_surete = non; vol_sur_personne = non
- `axa-v12` idéal NC, lu ? NC NC · manque : proprietaire = assure; violence = non; vol_sur_personne = non · en trop : abus_confiance = oui · retiré sans appui : abus_confiance = oui
- `axa-v14` idéal C, lu NC NC NC · **contredit** : proprietaire : assure lu hote · manque : vol_sur_personne = non · retiré sans appui : violence = non; vol_sur_personne = non

### Contradictions sans effet sur la décision

- `axa-v05` : bien : valeurs lu objet_divers

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 62% (53% – 67%) | 42% (33% – 47%) | **0 (0 – 0)** | **1.333 (1 – 2)** | 58% (53% – 60%) |

Instables : **3** sur 15 · rappel des clauses : 69% · rappel des questions : 67% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 35.2 s · par cas, un à la fois (10 cas) : médiane 3.48 s, 95e centile 5.24 s (lecture 3.24 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.33 s, 95e centile 69.3 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 15 | 53% | 0 | 2 |
| garantie : 3.1.6 | 15 | 53% | 0 | 2 |
| thème : base | 6 | 50% | 0 | 2 |
| thème : incertain | 2 | 50% | 0 | 0 |
| thème : piege | 7 | 57% | 0 | 0 |

### Erreurs et instabilités

- `axa-v02` attendu NC, obtenu ? ? ? — J'avais laissé la porte de l'appartement ouverte pour descendre les poubelles. En remontant, mon portefeuille … *(Vol simple : ni effraction ni violence (3.1.6.2.1).)*
- `axa-v04` attendu ?, obtenu NC ? ? — Cambriolage pendant la nuit : la porte du garage attenant à la maison a été fracturée et des outils et deux vé… *(Rien ne dit si une plainte a été déposée : condition de la garantie, à demander.)*
- `axa-v06` attendu NC, obtenu ? ? ? — Dans le tram, on m'a subtilisé mon portefeuille dans la poche sans que je m'en rende compte. J'ai la formule P… *(Vol à la tire hors du bâtiment désigné (3.1.6.2.2), et vol simple.)*
- `axa-v09` attendu NC, obtenu ? ? ? — J'habite un appartement. Ma cave, fermée par un simple cadenas, a été forcée et on y a volé des skis. J'ai por… *(Occupation partielle : contenu des caves exclu s'il n'est pas fermé par une serrure de sûreté (3.1.6.2.7).)*
- `axa-v10` attendu C, obtenu NC NC NC — Notre garage séparé de la maison, au fond du terrain, est fermé par une serrure à cylindre. Elle a été forcée … *(Annexe non contiguë équipée d'une serrure à cylindre (3.1.6.1, 2 500 €).)*
- `axa-v12` attendu NC, obtenu ? NC NC — Je soupçonne la femme de ménage d'avoir pris des bijoux pendant qu'elle travaillait chez nous. Aucune effracti… *(Personne au service de l'Assuré pendant les heures de service (3.1.6.2.4) ; c'est aussi un vol simple.)*
- `axa-v14` attendu C, obtenu NC ? ? — En vacances à Lisbonne, notre chambre d'hôtel a été forcée et mon appareil photo volé. Nous avons porté plaint… *(Vol par effraction dans un bâtiment partout dans le monde, séjour temporaire (3.1.6.1, 2 500 €).)*
