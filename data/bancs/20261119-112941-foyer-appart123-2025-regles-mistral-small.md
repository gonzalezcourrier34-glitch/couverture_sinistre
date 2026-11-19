# Banc d'essai — foyer-appart123-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-19T11:17:57 · golden set v10 (97 cas, empreinte `68cb3c13ea714708`) · cas validés par l'auteur : 0 sur 97


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 1.9 | ✓ |
| lecture | decisions_changees | ≤ 2 | 22 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 10 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 17 | ✗ |
| chaine | faux_couverts | ≤ 0 | 5.333 | ✗ |
| chaine | faux_refus | ≤ 1 | 0.333 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.883 | ✓ |
| chaine | instables | ≤ 3 | 10 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 0.727 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 39.15 | ✗ |

## Depuis le banc précédent (2026-11-19T10:05:33)

- lecture · rappel_faits : 0.871 → 0.877
- chaine · exactitude : 0.862 → 0.883
- chaine · exactitude_stricte : 0.673 → 0.763
- chaine · faux_couverts : 1.667 → 5.333
- chaine · faux_refus : 0 → 0.333

## Couche 1 — règles seules (faits idéaux, sans modèle)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 100% | 91% | **0** | **0** | 16% |

Rappel des questions attendues : 100% · questions posées par réponse « incertain » : 1.9

Raisonnement par hypothèses : incertains tranchés par une ou deux questions : 62% · questions inutiles retirées : 50

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

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **22** par exécution, dont **10** cas vers un couvert à tort.

Rappel des faits idéaux : 88% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 17 cas · faits vagues : 0 cas · faits en trop : 83 cas · faits retirés (sans appui ou non dits) : 80 cas

### La lecture change la décision

- **⚠ vers couvert** `bougie-04` idéal NC, lu C NC C · **contredit** : lieu : jardin lu logement/terrasse · manque : absence = oui · en trop : auteur = assure; sejour_temporaire = oui · retiré sans appui : auteur = assure; chaleur_sans_feu = non; demenagement = non; occasion_fete_familiale = non
- **⚠ vers couvert** `val-01` idéal ?, lu C C C · manque : absence = oui; effraction = non; fenetres_fermees = non; portes_fermees = oui; vol_sur_personne = non · en trop : auteur = tiers; proprietaire = assure · retiré sans appui : effraction = non; fenetres_fermees = non; fermeture = aucune; simple_disparition = non; violence = non; vol_sur_personne = non
- **⚠ vers couvert** `val-03` idéal NC, lu NC C NC · manque : vol_sur_personne = non · en trop : auteur = tiers; simple_disparition = non · retiré sans appui : fermeture = aucune; portes_fermees = non
- **⚠ vers couvert** `red-b06` idéal NC, lu C C C · **contredit** : evenement : bris lu vandalisme · manque : type_dommage = rayure_ou_ecaillement · en trop : effraction = non · retiré sans appui : auteur = tiers; effraction = non; fenetres_fermees = non; fermeture = aucune; intentionnel = oui; manque_entretien = non
- **⚠ vers couvert** `g-p03` idéal ?, lu C C C · **contredit** : bien : objet_divers lu cles · manque : effraction = non; portes_fermees = oui · en trop : fermeture = cle; sejour_temporaire = oui · retiré sans appui : effraction = non; fermeture = cle; simple_disparition = non
- **⚠ vers couvert** `g-h02` idéal ?, lu C C C · en trop : cause_perte_alimentaire = coupure_soudaine_reseau; chaleur_sans_feu = oui; demenagement = non; proprietaire = assure; sejour_temporaire = non; usage_professionnel = non · retiré sans appui : chaleur_sans_feu = non; demenagement = non; embrasement = non; flammes = non; occasion_fete_familiale = non; sejour_temporaire = non; usage_professionnel = non
- **⚠ vers couvert** `g2-i04` idéal ?, lu NC NC C · en trop : auteur = tiers; evenement = vol; proprietaire = assure; simple_disparition = oui · retiré sans appui : auteur = tiers; fermeture = aucune; simple_disparition = non
- **⚠ vers couvert** `g2-i08` idéal ?, lu ? C ? · **contredit** : lieu : autre_batiment lu voie_publique · en trop : auteur = tiers; violence = oui; vol_sur_personne = oui · retiré sans appui : fermeture = aucune; violence = non
- **⚠ vers couvert** `g2-i11` idéal ?, lu ? C C · **contredit** : lieu : terrasse lu logement · en trop : type_dommage = bris · retiré sans appui : construction_close = oui; effraction = non; intentionnel = non
- **⚠ vers couvert** `g2-p08` idéal NC, lu C C C · **contredit** : cause_eau : piscine_exterieure lu debordement_aquarium · retiré sans appui : sejour_temporaire = non
- `velo-03` idéal NC, lu NC NC ? · **contredit** : fermeture : cadenas lu cle · manque : vol_sur_personne = non · en trop : auteur = tiers; portes_fermees = oui; proprietaire = assure · retiré sans appui : sejour_temporaire = non; serrure_surete = non; simple_disparition = non; violence = non
- `velo-04` idéal NC, lu ? NC NC · manque : effraction = non; fermeture = aucune; vol_sur_personne = non · en trop : auteur = tiers; proprietaire = assure · retiré sans appui : auteur = tiers; effraction = non; fermeture = aucune; simple_disparition = non; vol_sur_personne = non
- `velo-06` idéal NC, lu ? NC ? · manque : fermeture = cadenas; violence = non; vol_sur_personne = non · en trop : auteur = tiers; effraction = oui; proprietaire = assure; simple_disparition = non · retiré sans appui : fermeture = aucune; violence = non; vol_sur_personne = non
- `val-10` idéal NC, lu NC NC ? · manque : prevention_gel = non · en trop : demenagement = non; periode_gel = oui; sejour_temporaire = non; travaux_batiment = aucun · retiré sans appui : prevention_gel = non; sejour_temporaire = non
- `val-11` idéal NC, lu ? ? ? · en trop : alea_tempete = vent; demenagement = non; sejour_temporaire = non · retiré sans appui : alea_tempete = vent; periode_gel = non
- `val-12` idéal C, lu C NC C · **contredit** : cause_eau : fuite_installation lu debordement_recipient · en trop : absence = non; auteur = assure; sejour_temporaire = non; travaux_batiment = aucun · retiré sans appui : sejour_temporaire = non
- `val-13` idéal C, lu C ? C · **contredit** : cause_eau : infiltration_toiture lu infiltration_exterieure · manque : cause_eau = infiltration_toiture · en trop : alea_tempete = vent; construction_close = oui; residence_principale = oui · retiré sans appui : construction_close = oui; demenagement = non; sejour_temporaire = non
- `red-t03` idéal NC, lu ? ? ? · manque : annexe_ancree_beton = non; construction_close = non · retiré sans appui : annexe_ancree_beton = non; construction_close = non
- `red-b01` idéal C, lu NC NC NC · en trop : auteur = famille; intentionnel = oui; type_dommage = bris
- `g-q02` idéal ?, lu NC NC NC · en trop : evenement = vol; proprietaire = assure; simple_disparition = oui · retiré sans appui : assurance_responsabilite_tiers = inapplicable; couverture_rc_locative = inapplicable; detenteur_vehicule = inapplicable; fermeture = aucune; malveillance_auteur = inapplicable; materiel_jardin_range = inapplicable; pret_ou_location_habitation = inapplicable; sejour_temporaire = non; vol_sur_personne = non
- `g-h03` idéal C, lu ? ? ? · en trop : bien_a_l_origine_sinistre = oui
- `g2-i01` idéal ?, lu NC NC NC · en trop : auteur = tiers; lieu = parties_communes; proprietaire = assure; simple_disparition = non · retiré sans appui : fermeture = aucune; simple_disparition = non; vol_sur_personne = non
- `g2-i02` idéal C, lu C ? ? · **contredit** : bien : objet_divers lu bijoux/electronique/valeurs; effraction : non lu oui · manque : bien = objet_divers · en trop : auteur = tiers; fermeture = cle; proprietaire = assure; type_dommage = rayure_ou_ecaillement · retiré sans appui : serrure_surete = non; simple_disparition = non; violence = non; vol_sur_personne = non
- `g2-i03` idéal C, lu NC NC NC · en trop : cause_eau = infiltration_exterieure; sejour_temporaire = non · retiré sans appui : demenagement = non
- `g2-i16` idéal ?, lu NC NC NC · en trop : auteur = assure; bien = element_batiment; cause_eau = infiltration_exterieure; demenagement = non; intentionnel = non; travaux_batiment = aucun
- `g2-i07` idéal NC, lu ? ? ? · **contredit** : lieu : voie_publique lu vehicule · manque : vol_sur_personne = non · en trop : auteur = tiers; proprietaire = assure; simple_disparition = non · retiré sans appui : fermeture = aucune; sejour_temporaire = oui; vol_sur_personne = non
- `g2-p04` idéal NC, lu ? ? ? · **contredit** : evenement : vol lu mazout · en trop : auteur = tiers · retiré sans appui : auteur = tiers; bien_a_l_origine_sinistre = oui; intentionnel = oui
- `g2-l03` idéal C, lu ? ? ? · manque : absence = non; bien = objet_divers · en trop : auteur = tiers; effraction = oui; fermeture = cle; portes_fermees = oui; proprietaire = assure; vol_sur_personne = non · retiré sans appui : absence = non; effraction = non; violence = non

### Contradictions sans effet sur la décision

- `bougie-01` : evenement : autre lu degat_eaux
- `bougie-03` : evenement : autre lu fumee
- `val-09` : bien : objet_divers lu mobilier; evenement : autre lu fumee
- `g-l07` : evenement : autre lu bris
- `g2-p01` : bien : objet_divers lu cles; bien : objet_divers lu element_batiment; effraction : non lu oui

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 88% (88% – 89%) | 76% (75% – 77%) | **5.333 (5 – 6)** | **0.333 (0 – 1)** | 23% (22% – 24%) |

Instables : **10** sur 97 · rappel des clauses : 72% · rappel des questions : 73% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 208.7 s · par cas, un à la fois (10 cas) : médiane 3.41 s, 95e centile 39.15 s (lecture 2.87 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.71 s, 95e centile 37.66 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 97 | 89% | 5 ⚠ | 0 |
| garantie : 1.4 | 2 | 100% | 0 | 0 |
| garantie : 2.1 | 13 | 92% | 1 ⚠ | 0 |
| garantie : 2.10 | 40 | 85% | 2 ⚠ | 0 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.12 | 1 | 100% | 0 | 0 |
| garantie : 2.2 | 6 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.5 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 4 | 100% | 0 | 0 |
| garantie : 2.7 | 16 | 88% | 1 ⚠ | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 7 | 71% | 1 ⚠ | 0 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 24 | 92% | 1 ⚠ | 0 |
| thème : info_manquante | 16 | 94% | 0 | 0 |
| thème : langue | 11 | 100% | 0 | 0 |
| thème : multi | 8 | 100% | 0 | 0 |
| thème : piege | 55 | 84% | 5 ⚠ | 0 |
| thème : variante | 13 | 85% | 1 ⚠ | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `bougie-04` attendu NC, obtenu C NC C — Pendant mes vacances, une bougie laissée sur la table du jardin s'est enflammée et a brûlé la table et le salo… *(Vrai incendie, mais table et salon de jardin = contenu du jardin, exclu du contenu assuré (12/contenu). INCERTAIN défend)*
- **⚠ couvert à tort** `val-01` attendu NC, obtenu C C C — Pendant que j'étais au travail, quelqu'un est entré par la fenêtre de ma chambre, au rez-de-chaussée, que j'av… *(Obligation de prévention (2.10) : en cas d'absence, « fermer correctement les fenêtres […] facilement accessibles ». Lie)*
- **⚠ couvert à tort** `val-03` attendu NC, obtenu NC C NC — Des amis que j'hébergeais pour le week-end se sont fait voler leur ordinateur lors d'un cambriolage de mon app… *(Exclusion 2.10 : le vol des biens appartenant à des hôtes (alors que la définition du contenu les inclut : piège).)*
- **⚠ couvert à tort** `red-b06` attendu NC, obtenu C C C — La vitre de la fenêtre de la cuisine est rayée sur toute sa largeur. *(Exclusion 2.9 : les rayures et écaillements des vitres.)*
- **⚠ couvert à tort** `g-p03` attendu NC, obtenu C C C — Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune… *(Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct.)*
- **⚠ couvert à tort** `g2-i04` attendu ?, obtenu NC NC C — Mes bijoux ont disparu de ma chambre après le passage du plombier. *(Une disparition n'est pas un vol établi (simple disparition exclue) ; et un vol par une personne autorisée à se trouver )*
- **⚠ couvert à tort** `g2-p08` attendu NC, obtenu C C C — Le bain à bulles installé sur ma terrasse a fui et l'eau a abîmé le canapé du salon. *(Exclusion 2.7 : l'écoulement d'eau des piscines et des bains à bulles extérieurs.)*
- `velo-03` attendu NC, obtenu NC NC ? — Mon vélo a été volé dans ma cave privative, fermée à clé. Le cadenas de la porte a été forcé. *(Cave en immeuble à appartements : vol couvert à 1 000 EUR « si ces locaux sont fermés avec une serrure de sûreté » (2.10)*
- `velo-04` attendu NC, obtenu ? NC NC — Mon vélo a été volé dans ma cave privative. J'avais oublié de la fermer à clé et il n'y a aucune trace d'effra… *(Cave non fermée : pas de serrure de sûreté (condition du plafond caves), et obligation de prévention non respectée avec )*
- `velo-06` attendu NC, obtenu ? NC ? — Mon vélo était attaché à un arceau dans la rue avec un antivol. L'antivol a été coupé et le vélo volé. *(Vol dans la rue, sans violence : hors du bâtiment, et ce n'est pas un « vol commis sur l'assuré … suite à violences ».)*
- `val-11` attendu NC, obtenu ? ? ? — Pendant un orage, la pluie s'est infiltrée par la fenêtre mal jointée de ma chambre et a abîmé le mur et la mo… *(Exclusion 2.7 : une infiltration par les fenêtres, autre que celle due à une fuite des installations hydrauliques extéri)*
- `val-12` attendu C, obtenu C NC C — Ma baignoire a débordé pendant que j'étais au téléphone ; l'eau a abîmé mon parquet. *(2.7 couvre l'ensemble des dégâts des eaux ; l'exclusion du récipient vise un récipient NON relié à l'installation hydrau)*
- `val-13` attendu C, obtenu C ? C — La tempête a arraché des tuiles de l'immeuble et la pluie est entrée dans mon salon, abîmant le plafond et le … *(2.2 : les dommages matériels directement causés par la tempête. Garantie non écrite en règles : test de l'aveu de limite)*
- `red-b01` attendu C, obtenu ? ? ? — Mon fils a cassé la vitre de la porte-fenêtre du salon avec un ballon. *(2.9 : le bris de vitres.)*
- `red-b05` attendu NC, obtenu ? NC ? — Le grand miroir que je venais d'acheter, encore dans son carton et pas encore accroché, s'est brisé quand je l… *(Exclusion 2.9 : les dommages aux vitres et biens assimilés non placés.)*
- `g2-i01` attendu ?, obtenu NC NC NC — Mon vélo a été volé dans le local de mon immeuble. *(« Le local de mon immeuble » : local commun (vol exclu dans les parties communes) ou cave privative (couverte si serrure)*
- `g2-i02` attendu ?, obtenu C ? ? — On a cambriolé mon appartement pendant le week-end où j'étais absent. La serrure porte des rayures, mais la po… *(Des traces sans réparation nécessaire ne sont pas une effraction (définition). Sans effraction, l'obligation de fermer à)*
- `g2-i07` attendu NC, obtenu ? ? ? — Mon ordinateur portable a été volé dans ma voiture, garée devant chez moi. *(La voiture n'est pas le bâtiment, et ce n'est pas un vol commis sur l'assuré avec violences.)*
- `g2-p04` attendu NC, obtenu ? ? ? — On a siphonné le fioul de la cuve de chauffage, dans ma cave. *(Exclusion 2.10 : le vol de mazout de chauffage.)*
