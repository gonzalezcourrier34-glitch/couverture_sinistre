# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-medium-latest` (verifiee, exemples, verification mistral-small)

2026-11-22T15:00:13 · golden set v13, partie « test » (31 cas, empreinte `eae57de51468c0ab`) · cas validés par l'auteur : 0 sur 31


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 1 | ✓ |
| lecture | decisions_changees | ≤ 2 | 4 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 0 | ✓ |
| lecture | cas_avec_contradiction | ≤ 5 | 4 | ✓ |
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.903 | ✓ |
| chaine | instables | ≤ 3 | 0 | ✓ |
| chaine | rappel_questions | ≥ 0.8 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 6.82 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-22T13:30:47, mistral:mistral-medium-latest · verifiee, exemples, verification mistral-small)

- lecture · rappel_faits : 0.899 → 0.89

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

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **4** par exécution, dont **0** cas vers un couvert à tort.

Rappel des faits idéaux : 89% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 4 cas · faits vagues : 0 cas · faits en trop : 22 cas · faits retirés (sans appui ou non dits) : 23 cas

### La lecture change la décision

- `velo-06` idéal NC, lu ? ? ? · manque : violence = non; vol_sur_personne = non · en trop : effraction = oui; laisse_sans_surveillance = oui · retiré sans appui : simple_disparition = non; vol_sur_personne = non
- `val-09` idéal NC, lu ? ? ? · **contredit** : evenement : autre lu accident · manque : embrasement = non; flammes = non
- `g-h03` idéal C, lu ? ? ? · en trop : bien_a_l_origine_sinistre = oui
- `g2-p01` idéal C, lu ? ? ? · **contredit** : effraction : non lu oui · manque : bien = objet_divers; portes_fermees = oui · en trop : auteur = tiers; fermeture = cle; proprietaire = assure; simple_disparition = non; vol_sur_personne = non · retiré sans appui : vol_sur_personne = non

### Contradictions sans effet sur la décision

- `val-08` : bien : electronique/element_batiment lu appareil_electromenager/mobilier
- `g-l07` : evenement : autre lu accident

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 90% (90% – 90%) | 77% (77% – 77%) | **0 (0 – 0)** | **0 (0 – 0)** | 26% (26% – 26%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 15 | 0 |
| Non couvert | 8 | 0 |
| À préciser | 5 | 3 |

Instables : **0** sur 31 · rappel des clauses : 86% · rappel des questions : 100% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 30.8 s · par cas, un à la fois (10 cas) : médiane 4.62 s, 95e centile 6.82 s (lecture 3.64 s, décision 0.02 s) · en masse (quatre à la fois) : médiane 3.61 s, 95e centile 5.17 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 31 | 90% | 0 | 0 |
| garantie : 2.1 | 3 | 67% | 0 | 0 |
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
| thème : piege | 16 | 88% | 0 | 0 |
| thème : variante | 4 | 75% | 0 | 0 |

### Erreurs et instabilités

- `velo-06` attendu NC, obtenu ? ? ? — Mon vélo était attaché à un arceau dans la rue avec un antivol. L'antivol a été coupé et le vélo volé. *(Vol dans la rue, sans violence : hors du bâtiment, et ce n'est pas un « vol commis sur l'assuré … suite à violences ».)*
- `val-09` attendu NC, obtenu ? ? ? — Mon fer à repasser, laissé à plat sur la planche, a brûlé la housse et laissé une marque sur le tissu, sans fl… *(Définition de l'incendie : les brûlures et le contact d'une source de chaleur sans embrasement ne sont pas un incendie.)*
- `g2-p01` attendu C, obtenu ? ? ? — Pendant mes vacances, des cambrioleurs ont ouvert ma porte sans la casser : il n'y a que des traces de tournev… *(Pas d'effraction au sens du contrat, mais la porte était fermée à clé : l'obligation est respectée, le vol dans le bâtim)*
