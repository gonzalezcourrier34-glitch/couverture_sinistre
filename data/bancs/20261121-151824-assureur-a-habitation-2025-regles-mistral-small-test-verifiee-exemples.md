# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee, exemples)

2026-11-21T15:14:37 · golden set v12, partie « test » (31 cas, empreinte `0534a0545f66a07d`) · cas validés par l'auteur : 0 sur 31


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 1 | ✓ |
| lecture | decisions_changees | ≤ 2 | 6.33 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 2 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 5 | ✓ |
| chaine | faux_couverts | ≤ 0 | 2 | ✗ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.85 | ✓ |
| chaine | instables | ≤ 3 | 2 | ✓ |
| chaine | rappel_questions | ≥ 0.8 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 6.23 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-21T14:36:56, mistral:mistral-small-latest · verifiee, exemples)

- lecture · rappel_faits : 0.854 → 0.85
- chaine · exactitude : 0.86 → 0.85

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

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **6.33** par exécution, dont **2** cas vers un couvert à tort.

Rappel des faits idéaux : 85% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 5 cas · faits vagues : 1 cas · faits en trop : 25 cas · faits retirés (sans appui ou non dits) : 23 cas

### La lecture change la décision

- **⚠ vers couvert** `g-p03` idéal ?, lu C C C · **contredit** : bien : objet_divers lu cles · manque : effraction = non; portes_fermees = oui · retiré sans appui : effraction = non; simple_disparition = non
- **⚠ vers couvert** `g2-p08` idéal NC, lu C C C · **contredit** : cause_eau : piscine_exterieure lu debordement_aquarium · en trop : auteur = assure; intentionnel = non; type_dommage = opacification_ou_perte_etancheite · retiré sans appui : travaux_batiment = aucun
- `velo-06` idéal NC, lu ? ? NC · manque : fermeture = cadenas; violence = non; vol_sur_personne = non · en trop : acces_voleur = sans_effraction; effraction = oui; laisse_sans_surveillance = oui · retiré sans appui : fermeture = aucune; simple_disparition = non; vol_sur_personne = non
- `red-b01` idéal C, lu NC NC NC · en trop : auteur = famille; effraction = non; intentionnel = oui; proprietaire = assure; travaux_batiment = aucun; travaux_vitres = aucun; type_dommage = bris; vitre_placee = oui
- `g-h03` idéal C, lu ? ? ? · en trop : bien_a_l_origine_sinistre = oui
- `g2-i06` idéal ?, lu ? NC NC · en trop : periode_gel = oui; prevention_gel = non; travaux_batiment = aucun
- `g2-p01` idéal C, lu ? ? ? · **contredit** : effraction : non lu oui · manque : bien = objet_divers; portes_fermees = oui · en trop : acces_voleur = sans_effraction; auteur = tiers; fermeture = cle; proprietaire = assure; sejour_temporaire = oui; simple_disparition = non; violence = non; vol_sur_personne = non · retiré sans appui : acces_voleur = fausse_qualite; auteur = tiers; serrure_surete = cle; simple_disparition = non

### Contradictions sans effet sur la décision

- `val-09` : evenement : autre lu fumee
- `g-l07` : evenement : autre lu accident

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 85% (84% – 87%) | 77% (74% – 81%) | **2 (2 – 2)** | **0 (0 – 0)** | 19% (16% – 23%) |

Instables : **2** sur 31 · rappel des clauses : 84% · rappel des questions : 100% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 59.4 s · par cas, un à la fois (10 cas) : médiane 4.46 s, 95e centile 6.23 s (lecture 2.8 s, décision 0.04 s) · en masse (quatre à la fois) : médiane 4.55 s, 95e centile 37.3 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 31 | 84% | 2 ⚠ | 0 |
| garantie : 2.1 | 3 | 100% | 0 | 0 |
| garantie : 2.10 | 13 | 77% | 1 ⚠ | 0 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.6 | 2 | 100% | 0 | 0 |
| garantie : 2.7 | 5 | 80% | 1 ⚠ | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 3 | 67% | 0 | 0 |
| garantie : aucune | 1 | 100% | 0 | 0 |
| thème : base | 1 | 100% | 0 | 0 |
| thème : hors_regles | 9 | 89% | 0 | 0 |
| thème : info_manquante | 3 | 100% | 0 | 0 |
| thème : langue | 4 | 100% | 0 | 0 |
| thème : multi | 2 | 100% | 0 | 0 |
| thème : piege | 16 | 81% | 2 ⚠ | 0 |
| thème : variante | 4 | 75% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `g-p03` attendu NC, obtenu C C C — Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune… *(Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct.)*
- **⚠ couvert à tort** `g2-p08` attendu NC, obtenu C C C — Le bain à bulles installé sur ma terrasse a fui et l'eau a abîmé le canapé du salon. *(Exclusion 2.7 : l'écoulement d'eau des piscines et des bains à bulles extérieurs.)*
- `velo-06` attendu NC, obtenu ? ? NC — Mon vélo était attaché à un arceau dans la rue avec un antivol. L'antivol a été coupé et le vélo volé. *(Vol dans la rue, sans violence : hors du bâtiment, et ce n'est pas un « vol commis sur l'assuré … suite à violences ».)*
- `red-b01` attendu C, obtenu ? ? ? — Mon fils a cassé la vitre de la porte-fenêtre du salon avec un ballon. *(2.9 : le bris de vitres.)*
- `red-b05` attendu NC, obtenu ? NC NC — Le grand miroir que je venais d'acheter, encore dans son carton et pas encore accroché, s'est brisé quand je l… *(Exclusion 2.9 : les dommages aux vitres et biens assimilés non placés.)*
- `g2-p01` attendu C, obtenu ? ? ? — Pendant mes vacances, des cambrioleurs ont ouvert ma porte sans la casser : il n'y a que des traces de tournev… *(Pas d'effraction au sens du contrat, mais la porte était fermée à clé : l'obligation est respectée, le vol dans le bâtim)*
