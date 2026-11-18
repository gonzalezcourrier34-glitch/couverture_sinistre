# Banc d'essai — foyer-appart123-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-18T22:20:56 · golden set v7 (97 cas, empreinte `0b83f83b91580639`) · cas validés par l'auteur : 0 sur 97


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 0.8 | ✓ |
| lecture | decisions_changees | ≤ 2 | 20.67 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 5 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 17 | ✗ |
| chaine | faux_couverts | ≤ 0 | 1.333 | ✗ |
| chaine | faux_refus | ≤ 1 | 1 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.897 | ✓ |
| chaine | instables | ≤ 3 | 12 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 0.727 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 4.07 | ✓ |

## Depuis le banc précédent (2026-11-18T22:02:35)

- regles · exactitude_stricte : 0.804 → 0.814
- lecture · rappel_faits : 0.871 → 0.868
- chaine · exactitude : 0.887 → 0.897
- chaine · exactitude_stricte : 0.649 → 0.67
- chaine · faux_couverts : 2.333 → 1.333

## Couche 1 — règles seules (faits idéaux, sans modèle)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 100% | 81% | **0** | **0** | 26% |

Rappel des questions attendues : 100% · questions posées par réponse « incertain » : 0.8

Raisonnement par hypothèses : incertains tranchés par une ou deux questions : 24% · questions inutiles retirées : 12

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 97 | 100% | 0 | 0 |
| garantie : 1.4 | 2 | 100% | 0 | 0 |
| garantie : 2.1 | 13 | 100% | 0 | 0 |
| garantie : 2.10 | 40 | 100% | 0 | 0 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.12 | 1 | 100% | 0 | 0 |
| garantie : 2.2 | 6 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.5 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 4 | 100% | 0 | 0 |
| garantie : 2.7 | 16 | 100% | 0 | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 7 | 100% | 0 | 0 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 24 | 100% | 0 | 0 |
| thème : info_manquante | 16 | 100% | 0 | 0 |
| thème : langue | 11 | 100% | 0 | 0 |
| thème : multi | 8 | 100% | 0 | 0 |
| thème : piege | 55 | 100% | 0 | 0 |
| thème : variante | 13 | 100% | 0 | 0 |

### Erreurs des règles

Aucune.

## Couche 2 — lecture des faits par le modèle

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **20.67** par exécution, dont **5** cas vers un couvert à tort.

Rappel des faits idéaux : 87% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 17 cas · faits vagues : 2 cas · faits en trop : 67 cas · faits retirés (sans appui ou non dits) : 73 cas

### La lecture change la décision

- **⚠ vers couvert** `val-01` idéal ?, lu C ? ? · manque : absence = oui; effraction = non; fenetres_fermees = non; portes_fermees = oui; vol_sur_personne = non · en trop : auteur = tiers; fermeture = aucune; proprietaire = assure; simple_disparition = non; violence = non · retiré sans appui : effraction = non; fenetres_fermees = non; fermeture = aucune; simple_disparition = non; violence = non; vol_sur_personne = non
- **⚠ vers couvert** `g-p03` idéal ?, lu C C C · **contredit** : bien : objet_divers lu cles · manque : absence = oui; portes_fermees = oui · en trop : auteur = tiers; fermeture = cle · retiré sans appui : fermeture = cle
- **⚠ vers couvert** `g2-i08` idéal ?, lu C ? ? · **contredit** : lieu : autre_batiment lu voie_publique · en trop : auteur = tiers; proprietaire = assure; simple_disparition = non; violence = oui; vol_sur_personne = oui · retiré sans appui : effraction = non; fermeture = aucune; simple_disparition = non; violence = non
- **⚠ vers couvert** `g2-i11` idéal ?, lu ? C ? · **contredit** : lieu : terrasse lu logement · en trop : type_dommage = bris · retiré sans appui : effraction = non; travaux_batiment = aucun; travaux_vitres = aucun
- **⚠ vers couvert** `g2-i16` idéal ?, lu C C C · en trop : auteur = assure; bien = element_batiment · retiré sans appui : intentionnel = non
- `velo-04` idéal NC, lu NC ? NC · manque : fermeture = aucune; vol_sur_personne = non · retiré sans appui : absence = oui; fermeture = aucune; portes_fermees = non
- `velo-06` idéal NC, lu NC NC ? · **contredit** : fermeture : cadenas lu cle · manque : fermeture = cadenas; violence = non; vol_sur_personne = non · en trop : auteur = tiers; effraction = oui; proprietaire = assure · retiré sans appui : fermeture = aucune; simple_disparition = non; violence = non; vol_sur_personne = non
- `val-03` idéal NC, lu NC ? ? · manque : vol_sur_personne = non · en trop : auteur = tiers · retiré sans appui : auteur = tiers; fermeture = aucune
- `val-10` idéal NC, lu ? ? ? · manque : prevention_gel = non · retiré sans appui : prevention_gel = non
- `val-11` idéal NC, lu ? ? ?
- `val-12` idéal C, lu NC NC NC · **contredit** : cause_eau : fuite_installation lu debordement_recipient · en trop : absence = oui
- `val-13` idéal C, lu ? ? ? · **contredit** : cause_eau : infiltration_toiture lu infiltration_exterieure
- `val-14` idéal NC, lu ? ? ? · manque : vol_sur_personne = non · en trop : auteur = tiers; proprietaire = assure · retiré sans appui : fermeture = aucune; vol_sur_personne = non
- `red-b01` idéal C, lu NC NC NC · en trop : auteur = famille; cause_dommage = autre; intentionnel = oui; type_dommage = bris; vitre_placee = oui · retiré sans appui : effraction = non; manque_entretien = non; travaux_batiment = aucun; travaux_vitres = aucun
- `red-b06` idéal NC, lu ? ? ? · **contredit** : evenement : bris lu vandalisme · manque : type_dommage = rayure_ou_ecaillement · retiré sans appui : auteur = tiers; intentionnel = oui
- `g-q02` idéal ?, lu NC NC NC · en trop : evenement = vol; fermeture = aucune; proprietaire = assure; simple_disparition = oui; vol_sur_personne = non · retiré sans appui : fermeture = aucune; violence = non; vol_sur_personne = non
- `g-q04` idéal C, lu NC C C · en trop : cause_eau = infiltration_exterieure
- `g-h06` idéal C, lu ? C ? · en trop : auteur = tiers; effraction = oui; intentionnel = oui; travaux_batiment = aucun; travaux_vitres = aucun; type_dommage = bris; vitre_placee = oui · retiré sans appui : travaux_batiment = aucun; travaux_vitres = aucun
- `g2-i01` idéal ?, lu NC NC NC · en trop : auteur = tiers; lieu = parties_communes; proprietaire = assure; simple_disparition = non; simple_disparition = oui · retiré sans appui : fermeture = aucune; simple_disparition = non; vol_sur_personne = non
- `g2-i02` idéal C, lu C ? ? · **contredit** : bien : objet_divers lu cles; effraction : non lu oui · manque : bien = objet_divers · en trop : auteur = tiers; fermeture = cle; proprietaire = assure · retiré sans appui : manque_entretien = non; serrure_surete = non; simple_disparition = non; violence = non; vol_sur_personne = non
- `g2-i03` idéal C, lu NC NC NC · en trop : cause_eau = infiltration_exterieure
- `g2-i04` idéal ?, lu NC NC NC · en trop : auteur = tiers; evenement = vol; fermeture = aucune; proprietaire = assure; simple_disparition = oui · retiré sans appui : fermeture = aucune
- `g2-p01` idéal C, lu C ? C · **contredit** : bien : objet_divers lu cles; effraction : non lu oui · manque : absence = oui; bien = objet_divers; portes_fermees = oui · en trop : fermeture = cle
- `g2-i07` idéal NC, lu ? ? ? · manque : lieu = voie_publique; vol_sur_personne = non · en trop : auteur = tiers; proprietaire = assure; simple_disparition = non · retiré sans appui : fermeture = aucune; vol_sur_personne = non
- `g2-p04` idéal NC, lu ? ? ? · **contredit** : evenement : vol lu mazout · en trop : auteur = tiers · retiré sans appui : auteur = tiers; intentionnel = oui
- `g2-l03` idéal C, lu ? ? ? · manque : absence = non; bien = objet_divers · en trop : auteur = tiers; effraction = oui; fermeture = cle; portes_fermees = oui; violence = non; vol_sur_personne = non · retiré sans appui : absence = non; fermeture = cle; portes_fermees = oui; vol_sur_personne = non
- `g2-m02` idéal C, lu ? C C · en trop : cause_dommage = autre; cause_eau = infiltration_exterieure; type_dommage = bris; vitre_placee = oui · retiré sans appui : effraction = non; travaux_batiment = aucun; travaux_vitres = aucun

### Contradictions sans effet sur la décision

- `bougie-01` : evenement : autre lu degat_eaux
- `val-09` : bien : objet_divers lu mobilier; evenement : autre lu fumee
- `red-t03` : lieu : garage lu annexe
- `g-l03` : evenement : autre lu degat_eaux
- `g-l07` : evenement : autre lu bris
- `g-h02` : bien : objet_divers lu electronique
- `g-h03` : bien : element_batiment lu mazout

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 90% (89% – 91%) | 67% (67% – 67%) | **1.333 (1 – 2)** | **1 (1 – 1)** | 36% (35% – 36%) |

Instables : **12** sur 97 · rappel des clauses : 64% · rappel des questions : 73% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 203.9 s · par cas, un à la fois (10 cas) : médiane 3.07 s, 95e centile 4.07 s (lecture 2.86 s, décision 0.0 s) · en masse (quatre à la fois) : médiane 2.93 s, 95e centile 68.12 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 97 | 91% | 2 ⚠ | 1 |
| garantie : 1.4 | 2 | 100% | 0 | 0 |
| garantie : 2.1 | 13 | 100% | 0 | 0 |
| garantie : 2.10 | 40 | 85% | 2 ⚠ | 0 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.12 | 1 | 100% | 0 | 0 |
| garantie : 2.2 | 6 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.5 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 4 | 100% | 0 | 0 |
| garantie : 2.7 | 16 | 88% | 0 | 1 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 7 | 86% | 0 | 0 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 24 | 96% | 0 | 0 |
| thème : info_manquante | 16 | 94% | 0 | 0 |
| thème : langue | 11 | 100% | 0 | 0 |
| thème : multi | 8 | 100% | 0 | 0 |
| thème : piege | 55 | 86% | 2 ⚠ | 1 |
| thème : variante | 13 | 100% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `val-01` attendu NC, obtenu C ? ? — Pendant que j'étais au travail, quelqu'un est entré par la fenêtre de ma chambre, au rez-de-chaussée, que j'av… *(Obligation de prévention (2.10) : en cas d'absence, « fermer correctement les fenêtres […] facilement accessibles ». Lie)*
- **⚠ couvert à tort** `g-p03` attendu NC, obtenu C C C — Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune… *(Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct.)*
- `velo-04` attendu NC, obtenu NC ? NC — Mon vélo a été volé dans ma cave privative. J'avais oublié de la fermer à clé et il n'y a aucune trace d'effra… *(Cave non fermée : pas de serrure de sûreté (condition du plafond caves), et obligation de prévention non respectée avec )*
- `velo-06` attendu NC, obtenu NC ? ? — Mon vélo était attaché à un arceau dans la rue avec un antivol. L'antivol a été coupé et le vélo volé. *(Vol dans la rue, sans violence : hors du bâtiment, et ce n'est pas un « vol commis sur l'assuré … suite à violences ».)*
- `val-03` attendu NC, obtenu NC ? ? — Des amis que j'hébergeais pour le week-end se sont fait voler leur ordinateur lors d'un cambriolage de mon app… *(Exclusion 2.10 : le vol des biens appartenant à des hôtes (alors que la définition du contenu les inclut : piège).)*
- `val-11` attendu NC, obtenu ? ? ? — Pendant un orage, la pluie s'est infiltrée par la fenêtre mal jointée de ma chambre et a abîmé le mur et la mo… *(Exclusion 2.7 : une infiltration par les fenêtres, autre que celle due à une fuite des installations hydrauliques extéri)*
- `val-12` attendu C, obtenu NC NC NC — Ma baignoire a débordé pendant que j'étais au téléphone ; l'eau a abîmé mon parquet. *(2.7 couvre l'ensemble des dégâts des eaux ; l'exclusion du récipient vise un récipient NON relié à l'installation hydrau)*
- `val-14` attendu NC, obtenu ? ? ? — Lors d'un cambriolage avec la porte fracturée, on m'a volé mon chat de race. *(Exclusion 2.10 : le vol des animaux.)*
- `red-b01` attendu C, obtenu ? ? ? — Mon fils a cassé la vitre de la porte-fenêtre du salon avec un ballon. *(2.9 : le bris de vitres.)*
- `red-b05` attendu NC, obtenu ? NC ? — Le grand miroir que je venais d'acheter, encore dans son carton et pas encore accroché, s'est brisé quand je l… *(Exclusion 2.9 : les dommages aux vitres et biens assimilés non placés.)*
- `g-q04` attendu C, obtenu ? C C — De l'eau coule du plafond de ma salle de bain et a abîmé le mur. *(2.7 couvre l'ensemble des dégâts des eaux ; la cause inconnue n'établit aucune exclusion (c'est à l'assureur de la prouv)*
- `g-h06` attendu C, obtenu ? C ? — Pendant une manifestation qui a dégénéré, des émeutiers ont brisé les fenêtres de mon appartement au rez-de-ch… *(2.4 : détérioration par des personnes prenant part à un attentat (émeutes) ; aussi 2.9. Non traduites.)*
- `g2-i01` attendu ?, obtenu NC NC NC — Mon vélo a été volé dans le local de mon immeuble. *(« Le local de mon immeuble » : local commun (vol exclu dans les parties communes) ou cave privative (couverte si serrure)*
- `g2-i02` attendu ?, obtenu C ? ? — On a cambriolé mon appartement pendant le week-end où j'étais absent. La serrure porte des rayures, mais la po… *(Des traces sans réparation nécessaire ne sont pas une effraction (définition). Sans effraction, l'obligation de fermer à)*
- `g2-i04` attendu ?, obtenu ? ? NC — Mes bijoux ont disparu de ma chambre après le passage du plombier. *(Une disparition n'est pas un vol établi (simple disparition exclue) ; et un vol par une personne autorisée à se trouver )*
- `g2-i11` attendu ?, obtenu ? C ? — Après le gros coup de vent d'hier, des tuiles de l'immeuble sont tombées sur mon balcon et l'ont abîmé. *(La tempête suppose un vent d'au moins 80 km/h ou des dégâts aux biens voisins (définition) : non précisé. Garantie 2.2 n)*
- `g2-p01` attendu C, obtenu C ? C — Pendant mes vacances, des cambrioleurs ont ouvert ma porte sans la casser : il n'y a que des traces de tournev… *(Pas d'effraction au sens du contrat, mais la porte était fermée à clé : l'obligation est respectée, le vol dans le bâtim)*
- `g2-i07` attendu NC, obtenu ? ? ? — Mon ordinateur portable a été volé dans ma voiture, garée devant chez moi. *(La voiture n'est pas le bâtiment, et ce n'est pas un vol commis sur l'assuré avec violences.)*
- `g2-p04` attendu NC, obtenu ? ? ? — On a siphonné le fioul de la cuve de chauffage, dans ma cave. *(Exclusion 2.10 : le vol de mazout de chauffage.)*
- `g2-m02` attendu C, obtenu ? C C — La tempête a cassé la fenêtre du salon et la pluie a abîmé le canapé. *(La vitre est couverte par le bris de vitrages (2.9) ; le canapé relève de la tempête (2.2), non traduite.)*
