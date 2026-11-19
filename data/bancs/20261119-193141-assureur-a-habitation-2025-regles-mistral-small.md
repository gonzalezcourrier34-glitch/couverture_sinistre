# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-19T19:20:26 · golden set v12 (97 cas, empreinte `0534a0545f66a07d`) · cas validés par l'auteur : 0 sur 97


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 1.9 | ✓ |
| lecture | decisions_changees | ≤ 2 | 22.33 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 9 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 16 | ✗ |
| chaine | faux_couverts | ≤ 0 | 5.333 | ✗ |
| chaine | faux_refus | ≤ 1 | 1.333 | ✗ |
| chaine | exactitude | ≥ 0.85 | 0.883 | ✓ |
| chaine | instables | ≤ 3 | 15 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 0.722 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 37.68 | ✗ |

## Depuis le banc précédent de même configuration (2026-11-19T18:12:17, mistral:mistral-small-latest · verifiee)

- lecture · rappel_faits : 0.875 → 0.887
- chaine · exactitude : 0.862 → 0.883
- chaine · exactitude_stricte : 0.718 → 0.742
- chaine · faux_couverts : 4.333 → 5.333
- chaine · faux_refus : 4.333 → 1.333

## Couche 1 — règles seules (faits idéaux, sans modèle)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 100% | 91% | **0** | **0** | 18% |

Rappel des questions attendues : 100% · questions posées par réponse « incertain » : 1.9

Raisonnement par hypothèses : incertains tranchés par une ou deux questions : 65% · questions inutiles retirées : 31

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 97 | 100% | 0 | 0 |
| garantie : 1.4 | 2 | 100% | 0 | 0 |
| garantie : 2.1 | 13 | 100% | 0 | 0 |
| garantie : 2.10 | 39 | 100% | 0 | 0 |
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
| garantie : 6.1 | 1 | 100% | 0 | 0 |
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

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **22.33** par exécution, dont **9** cas vers un couvert à tort.

Rappel des faits idéaux : 89% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 16 cas · faits vagues : 0 cas · faits en trop : 90 cas · faits retirés (sans appui ou non dits) : 78 cas

### La lecture change la décision

- **⚠ vers couvert** `bougie-04` idéal NC, lu C ? C · manque : absence = oui · en trop : auteur = assure; cause_dommage = autre; intentionnel = non; manque_entretien = non; proprietaire = assure; travaux_batiment = aucun; travaux_vitres = aucun; type_dommage = bris · retiré sans appui : cause_dommage = autre; chaleur_sans_feu = non; effraction = non; travaux_batiment = aucun
- **⚠ vers couvert** `red-b05` idéal NC, lu C C C · manque : vitre_placee = non · en trop : auteur = assure
- **⚠ vers couvert** `red-b06` idéal NC, lu C C C · **contredit** : evenement : bris lu vandalisme · manque : type_dommage = rayure_ou_ecaillement · en trop : effraction = non · retiré sans appui : auteur = tiers; effraction = non; fenetres_fermees = non; fermeture = aucune; intentionnel = oui; manque_entretien = non
- **⚠ vers couvert** `g-p03` idéal ?, lu C C C · **contredit** : bien : objet_divers lu cles · manque : absence = oui; effraction = non; portes_fermees = oui · en trop : fermeture = cle; sejour_temporaire = oui · retiré sans appui : effraction = non; fermeture = cle; simple_disparition = non
- **⚠ vers couvert** `g-h02` idéal ?, lu C ? ? · manque : lieu = logement · en trop : cause_perte_alimentaire = coupure_soudaine_reseau; chaleur_sans_feu = oui; proprietaire = assure; usage_professionnel = non · retiré sans appui : cause_perte_alimentaire = coupure_soudaine_reseau; chaleur_sans_feu = non; embrasement = non; flammes = non
- **⚠ vers couvert** `g2-i04` idéal ?, lu NC C NC · en trop : auteur = tiers; evenement = vol; proprietaire = assure; sejour_temporaire = non; simple_disparition = oui; vol_sur_personne = non · retiré sans appui : auteur = tiers; sejour_temporaire = non; simple_disparition = non; vol_sur_personne = non
- **⚠ vers couvert** `g2-i08` idéal ?, lu NC C NC · **contredit** : lieu : autre_batiment lu voie_publique · en trop : auteur = tiers; laisse_sans_surveillance = oui; proprietaire = assure; simple_disparition = non; violence = non; violence = oui; vol_sur_personne = oui · retiré sans appui : auteur = tiers; effraction = non; fermeture = aucune; sejour_temporaire = non; simple_disparition = non
- **⚠ vers couvert** `g2-i11` idéal ?, lu C C C · **contredit** : lieu : terrasse lu logement · en trop : vent_dommages_voisins = oui · retiré sans appui : vent_dommages_voisins = oui
- **⚠ vers couvert** `g2-p08` idéal NC, lu C C C · **contredit** : cause_eau : piscine_exterieure lu debordement_aquarium · en trop : type_dommage = moisissure · retiré sans appui : travaux_batiment = aucun
- `velo-03` idéal NC, lu ? ? ? · **contredit** : fermeture : cadenas lu cle · manque : vol_sur_personne = non · en trop : proprietaire = assure; simple_disparition = non; violence = non · retiré sans appui : sejour_temporaire = non; serrure_surete = non; simple_disparition = non; violence = non; vol_sur_personne = non
- `velo-04` idéal NC, lu NC NC ? · manque : effraction = non; fermeture = aucune; vol_sur_personne = non · en trop : proprietaire = assure; simple_disparition = non · retiré sans appui : effraction = non; fermeture = aucune; simple_disparition = non; vol_sur_personne = non
- `velo-06` idéal NC, lu NC ? NC · manque : fermeture = cadenas; violence = non; vol_sur_personne = non · en trop : auteur = tiers; dispositifs_antivol_installes = non; dispositifs_antivol_installes = oui; effraction = oui; laisse_sans_surveillance = non; proprietaire = assure; sejour_temporaire = oui; simple_disparition = non · retiré sans appui : fermeture = aucune; intentionnel = oui; laisse_sans_surveillance = non; manque_entretien = non; sejour_temporaire = oui; violence = non; vol_sur_personne = non
- `autre-02` idéal C, lu NC C C · en trop : manque_entretien = oui; travaux_batiment = aucun; type_dommage = moisissure; type_dommage = opacification_ou_perte_etancheite
- `val-11` idéal NC, lu ? ? ? · en trop : auteur = assure; type_dommage = moisissure · retiré sans appui : construction_close = oui
- `val-12` idéal C, lu C C NC · **contredit** : cause_eau : fuite_installation lu debordement_recipient · en trop : auteur = assure; type_dommage = moisissure; type_dommage = opacification_ou_perte_etancheite
- `val-13` idéal C, lu C C ? · **contredit** : cause_eau : infiltration_toiture lu infiltration_exterieure · manque : cause_eau = infiltration_toiture · en trop : alea_tempete = vent; type_dommage = bris; vent_dommages_voisins = oui · retiré sans appui : construction_close = oui
- `red-t03` idéal NC, lu ? NC ? · manque : annexe_ancree_beton = non; construction_close = non · retiré sans appui : annexe_ancree_beton = non; construction_close = non
- `g-q02` idéal ?, lu NC NC NC · en trop : evenement = vol; proprietaire = assure; simple_disparition = oui; vol_sur_personne = non · retiré sans appui : fermeture = aucune; sejour_temporaire = non
- `g-q04` idéal C, lu C C NC · en trop : cause_eau = infiltration_exterieure; type_dommage = moisissure · retiré sans appui : type_dommage = moisissure
- `g-h03` idéal C, lu ? ? ? · en trop : bien_a_l_origine_sinistre = oui
- `g-h05` idéal C, lu ? C C
- `g2-i01` idéal ?, lu NC NC NC · en trop : lieu = parties_communes; occupation_partielle = oui; proprietaire = assure; simple_disparition = non · retiré sans appui : auteur = tiers; fermeture = aucune; sejour_temporaire = non; vol_sur_personne = non
- `g2-i02` idéal C, lu C NC NC · **contredit** : bien : objet_divers lu cles; effraction : non lu oui · manque : bien = objet_divers · en trop : auteur = tiers; fermeture = cle; proprietaire = assure; simple_disparition = non; type_dommage = rayure_ou_ecaillement; violence = non; vol_sur_personne = non · retiré sans appui : sejour_temporaire = non; serrure_surete = non; simple_disparition = non; violence = non; vol_sur_personne = non
- `g2-i03` idéal C, lu NC NC NC · en trop : cause_eau = infiltration_exterieure; type_dommage = moisissure
- `g2-i06` idéal ?, lu ? ? NC · en trop : periode_gel = oui; prevention_gel = non; travaux_batiment = aucun · retiré sans appui : prevention_gel = non; type_dommage = opacification_ou_perte_etancheite
- `g2-i16` idéal ?, lu NC NC NC · en trop : auteur = assure; bien = element_batiment; cause_eau = infiltration_exterieure; type_dommage = moisissure
- `g2-p01` idéal C, lu NC NC NC · **contredit** : effraction : non lu oui · manque : absence = oui; bien = objet_divers · en trop : fermeture = cle · retiré sans appui : cles_a_proximite = non
- `g2-p04` idéal NC, lu ? ? ? · **contredit** : bien : mazout lu citerne; evenement : vol lu mazout · en trop : auteur = tiers · retiré sans appui : intentionnel = oui
- `g2-m02` idéal C, lu ? ? ? · en trop : alea_tempete = vent; cause_eau = infiltration_exterieure; construction_close = oui; travaux_batiment = aucun; type_dommage = bris · retiré sans appui : construction_close = oui; construction_delabree = non; type_dommage = bris

### Contradictions sans effet sur la décision

- `bougie-01` : evenement : autre lu accident
- `bougie-03` : evenement : autre lu fumee
- `val-09` : evenement : autre lu fumee
- `g-l07` : evenement : autre lu accident
- `g2-i07` : vehicule_voie_publique : oui lu non

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 88% (88% – 89%) | 74% (73% – 75%) | **5.333 (5 – 6)** | **1.333 (1 – 2)** | 24% (22% – 26%) |

Instables : **15** sur 97 · rappel des clauses : 68% · rappel des questions : 72% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 201.3 s · par cas, un à la fois (10 cas) : médiane 2.78 s, 95e centile 37.68 s (lecture 2.6 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.57 s, 95e centile 37.04 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 97 | 89% | 5 ⚠ | 1 |
| garantie : 1.4 | 2 | 100% | 0 | 0 |
| garantie : 2.1 | 13 | 92% | 1 ⚠ | 0 |
| garantie : 2.10 | 39 | 87% | 1 ⚠ | 1 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.12 | 1 | 100% | 0 | 0 |
| garantie : 2.2 | 6 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.5 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 4 | 100% | 0 | 0 |
| garantie : 2.7 | 16 | 81% | 1 ⚠ | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 7 | 71% | 2 ⚠ | 0 |
| garantie : 6.1 | 1 | 100% | 0 | 0 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 24 | 92% | 2 ⚠ | 0 |
| thème : info_manquante | 16 | 94% | 0 | 0 |
| thème : langue | 11 | 100% | 0 | 0 |
| thème : multi | 8 | 100% | 0 | 0 |
| thème : piege | 55 | 82% | 5 ⚠ | 1 |
| thème : variante | 13 | 85% | 1 ⚠ | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `bougie-04` attendu NC, obtenu C ? C — Pendant mes vacances, une bougie laissée sur la table du jardin s'est enflammée et a brûlé la table et le salo… *(Vrai incendie, mais table et salon de jardin = contenu du jardin, exclu du contenu assuré (12/contenu). INCERTAIN défend)*
- **⚠ couvert à tort** `red-b05` attendu NC, obtenu C C C — Le grand miroir que je venais d'acheter, encore dans son carton et pas encore accroché, s'est brisé quand je l… *(Exclusion 2.9 : les dommages aux vitres et biens assimilés non placés.)*
- **⚠ couvert à tort** `red-b06` attendu NC, obtenu C C C — La vitre de la fenêtre de la cuisine est rayée sur toute sa largeur. *(Exclusion 2.9 : les rayures et écaillements des vitres.)*
- **⚠ couvert à tort** `g-p03` attendu NC, obtenu C C C — Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune… *(Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct.)*
- **⚠ couvert à tort** `g2-i04` attendu ?, obtenu NC C ? — Mes bijoux ont disparu de ma chambre après le passage du plombier. *(Une disparition n'est pas un vol établi (simple disparition exclue) ; et un vol par une personne autorisée à se trouver )*
- **⚠ couvert à tort** `g2-i08` attendu ?, obtenu ? C ? — On m'a volé mon sac au restaurant. *(Hors du bâtiment, seul le vol commis sur l'assuré avec violences ou menaces est couvert : à préciser.)*
- **⚠ couvert à tort** `g2-p08` attendu NC, obtenu C C C — Le bain à bulles installé sur ma terrasse a fui et l'eau a abîmé le canapé du salon. *(Exclusion 2.7 : l'écoulement d'eau des piscines et des bains à bulles extérieurs.)*
- `velo-04` attendu NC, obtenu NC NC ? — Mon vélo a été volé dans ma cave privative. J'avais oublié de la fermer à clé et il n'y a aucune trace d'effra… *(Cave non fermée : pas de serrure de sûreté (condition du plafond caves), et obligation de prévention non respectée avec )*
- `velo-06` attendu NC, obtenu ? ? NC — Mon vélo était attaché à un arceau dans la rue avec un antivol. L'antivol a été coupé et le vélo volé. *(Vol dans la rue, sans violence : hors du bâtiment, et ce n'est pas un « vol commis sur l'assuré … suite à violences ».)*
- `autre-02` attendu C, obtenu ? C C — Le tuyau du lave-linge a cédé et l'eau a abîmé le parquet et le canapé. *(Dégâts des eaux couverts (2.7) ; le tuyau à l'origine est exclu (2.7-b) mais sa réparation relève des garanties compléme)*
- `val-11` attendu NC, obtenu ? ? ? — Pendant un orage, la pluie s'est infiltrée par la fenêtre mal jointée de ma chambre et a abîmé le mur et la mo… *(Exclusion 2.7 : une infiltration par les fenêtres, autre que celle due à une fuite des installations hydrauliques extéri)*
- `val-12` attendu C, obtenu C C NC — Ma baignoire a débordé pendant que j'étais au téléphone ; l'eau a abîmé mon parquet. *(2.7 couvre l'ensemble des dégâts des eaux ; l'exclusion du récipient vise un récipient NON relié à l'installation hydrau)*
- `val-13` attendu C, obtenu C C ? — La tempête a arraché des tuiles de l'immeuble et la pluie est entrée dans mon salon, abîmant le plafond et le … *(2.2 : les dommages matériels directement causés par la tempête. Garantie non écrite en règles : test de l'aveu de limite)*
- `red-t03` attendu NC, obtenu ? NC ? — Le poids de la neige a fait s'effondrer mon carport en bois, simplement posé sur des plots, sans ancrage en bé… *(Exclusion 2.2 : annexes faisant partie du bâtiment non fixées au sol par un ancrage en béton.)*
- `g-q02` attendu ?, obtenu NC ? NC — Mon ordinateur portable a disparu de mon appartement. *(« Disparu » n'est pas « volé » : la simple disparition est exclue ; il faut établir le vol.)*
- `g-q04` attendu C, obtenu C C ? — De l'eau coule du plafond de ma salle de bain et a abîmé le mur. *(2.7 couvre l'ensemble des dégâts des eaux ; la cause inconnue n'établit aucune exclusion (c'est à l'assureur de la prouv)*
- `g-h02` attendu C, obtenu C ? ? — Une panne de courant de dix heures a fait décongeler tout le contenu de mon congélateur. *(2.6 : denrées décongelées après 6 heures d'arrêt (limite 500 EUR). Non traduite.)*
- `g-h05` attendu C, obtenu ? C C — Les égouts publics ont refoulé pendant un gros orage et l'eau sale a envahi la salle de bain. *(2.3 : le refoulement d'égouts publics est une catastrophe naturelle couverte ; 2.7 l'exclut. Non traduite.)*
- `g2-i01` attendu ?, obtenu NC NC NC — Mon vélo a été volé dans le local de mon immeuble. *(« Le local de mon immeuble » : local commun (vol exclu dans les parties communes) ou cave privative (couverte si serrure)*
- `g2-i02` attendu ?, obtenu ? NC NC — On a cambriolé mon appartement pendant le week-end où j'étais absent. La serrure porte des rayures, mais la po… *(Des traces sans réparation nécessaire ne sont pas une effraction (définition). Sans effraction, l'obligation de fermer à)*
- `g2-i11` attendu ?, obtenu C C ? — Après le gros coup de vent d'hier, des tuiles de l'immeuble sont tombées sur mon balcon et l'ont abîmé. *(La tempête suppose un vent d'au moins 80 km/h ou des dégâts aux biens voisins (définition) : non précisé. Garantie 2.2 n)*
- `g2-p01` attendu C, obtenu NC NC NC — Pendant mes vacances, des cambrioleurs ont ouvert ma porte sans la casser : il n'y a que des traces de tournev… *(Pas d'effraction au sens du contrat, mais la porte était fermée à clé : l'obligation est respectée, le vol dans le bâtim)*
- `g2-p04` attendu NC, obtenu ? ? ? — On a siphonné le fioul de la cuve de chauffage, dans ma cave. *(Exclusion 2.10 : le vol de mazout de chauffage.)*
