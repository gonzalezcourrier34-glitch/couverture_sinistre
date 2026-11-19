# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-19T15:55:50 · golden set v12 (97 cas, empreinte `0534a0545f66a07d`) · cas validés par l'auteur : 0 sur 97


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 1.9 | ✓ |
| lecture | decisions_changees | ≤ 2 | 19.67 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 7 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 15 | ✗ |
| chaine | faux_couverts | ≤ 0 | 4.333 | ✗ |
| chaine | faux_refus | ≤ 1 | 0.667 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.897 | ✓ |
| chaine | instables | ≤ 3 | 11 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 0.722 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 5.37 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-19T15:40:08, mistral:mistral-small-latest · verifiee)

- lecture · rappel_faits : 0.892 → 0.893
- chaine · exactitude : 0.863 → 0.897
- chaine · exactitude_stricte : 0.736 → 0.763
- chaine · faux_couverts : 4 → 4.333
- chaine · faux_refus : 2 → 0.667

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

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **19.67** par exécution, dont **7** cas vers un couvert à tort.

Rappel des faits idéaux : 89% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 15 cas · faits vagues : 0 cas · faits en trop : 85 cas · faits retirés (sans appui ou non dits) : 79 cas

### La lecture change la décision

- **⚠ vers couvert** `bougie-04` idéal NC, lu C C NC · **contredit** : lieu : jardin lu logement/terrasse · en trop : cause_dommage = autre; intentionnel = non; manque_entretien = non; proprietaire = assure; travaux_batiment = aucun; travaux_vitres = aucun; type_dommage = bris · retiré sans appui : chaleur_sans_feu = non; effraction = non; manque_entretien = non
- **⚠ vers couvert** `val-09` idéal NC, lu C NC NC · **contredit** : bien : objet_divers lu mobilier; evenement : autre lu electricite; evenement : autre lu fumee · manque : embrasement = non · en trop : chaleur_sans_feu = oui; proprietaire = assure · retiré sans appui : embrasement = non; usage_professionnel = non
- **⚠ vers couvert** `val-14` idéal NC, lu NC C NC · manque : vol_sur_personne = non · en trop : auteur = tiers; proprietaire = assure; simple_disparition = non; violence = non · retiré sans appui : fermeture = aucune; vol_sur_personne = non
- **⚠ vers couvert** `red-b06` idéal NC, lu C C C · **contredit** : evenement : bris lu vandalisme · manque : type_dommage = rayure_ou_ecaillement · en trop : effraction = non · retiré sans appui : auteur = tiers; effraction = non; intentionnel = oui; manque_entretien = non
- **⚠ vers couvert** `g-p03` idéal ?, lu C C C · **contredit** : bien : objet_divers lu cles · manque : portes_fermees = oui · en trop : fermeture = cle · retiré sans appui : fermeture = cle; simple_disparition = non
- **⚠ vers couvert** `g2-i08` idéal ?, lu C NC C · **contredit** : lieu : autre_batiment lu voie_publique · en trop : auteur = tiers; laisse_sans_surveillance = oui; proprietaire = assure; simple_disparition = non; violence = non; violence = oui; vol_sur_personne = oui · retiré sans appui : auteur = tiers; fermeture = aucune
- **⚠ vers couvert** `g2-p08` idéal NC, lu C C C · **contredit** : cause_eau : piscine_exterieure lu debordement_aquarium · manque : cause_eau = piscine_exterieure · en trop : travaux_batiment = aucun · retiré sans appui : cause_eau = debordement_aquarium
- `velo-03` idéal NC, lu NC ? ? · **contredit** : fermeture : cadenas lu cle · manque : vol_sur_personne = non · en trop : portes_fermees = oui; proprietaire = assure; simple_disparition = non; violence = non · retiré sans appui : auteur = tiers; sejour_temporaire = non; serrure_surete = non; vol_sur_personne = non
- `velo-04` idéal NC, lu NC ? ? · manque : effraction = non; fermeture = aucune; vol_sur_personne = non · en trop : proprietaire = assure · retiré sans appui : effraction = non; fermeture = aucune; sejour_temporaire = non; simple_disparition = non; vol_sur_personne = non
- `val-11` idéal NC, lu ? ? ? · en trop : auteur = assure; residence_principale = oui · retiré sans appui : construction_close = oui
- `val-13` idéal C, lu C ? ? · **contredit** : cause_eau : infiltration_toiture lu infiltration_exterieure · manque : cause_eau = infiltration_toiture · en trop : alea_tempete = vent; travaux_batiment = aucun
- `red-t03` idéal NC, lu ? ? ? · manque : annexe_ancree_beton = non; construction_close = non · retiré sans appui : annexe_ancree_beton = non; construction_close = non
- `red-b01` idéal C, lu NC NC NC · en trop : auteur = famille; effraction = non; intentionnel = oui; manque_entretien = non; proprietaire = assure; travaux_batiment = aucun; travaux_vitres = aucun; type_dommage = bris; vitre_placee = oui · retiré sans appui : auteur = famille; effraction = non; manque_entretien = non
- `g-q02` idéal ?, lu NC NC NC · en trop : evenement = vol; proprietaire = assure; simple_disparition = oui; vol_sur_personne = non · retiré sans appui : fermeture = aucune; sejour_temporaire = non
- `g-h03` idéal C, lu ? ? ? · en trop : bien_a_l_origine_sinistre = oui
- `g-h05` idéal C, lu ? C C
- `g2-i01` idéal ?, lu NC NC NC · en trop : auteur = tiers; effraction = oui; lieu = parties_communes; occupation_partielle = oui; proprietaire = assure; simple_disparition = non; violence = non; vol_sur_personne = non · retiré sans appui : auteur = tiers; fermeture = aucune; sejour_temporaire = non; vol_sur_personne = non
- `g2-i02` idéal C, lu NC C NC · **contredit** : bien : objet_divers lu bijoux; effraction : non lu oui · manque : bien = objet_divers · en trop : auteur = tiers; fermeture = cle; proprietaire = assure; simple_disparition = non; type_dommage = rayure_ou_ecaillement; violence = non; vol_sur_personne = non · retiré sans appui : sejour_temporaire = non; serrure_surete = non; simple_disparition = non; violence = non; vol_sur_personne = non
- `g2-i03` idéal C, lu NC NC NC · en trop : cause_eau = infiltration_exterieure
- `g2-i04` idéal ?, lu NC NC NC · en trop : auteur = tiers; evenement = vol; proprietaire = assure; simple_disparition = oui · retiré sans appui : auteur = tiers; effraction = non; fermeture = aucune; sejour_temporaire = non; vol_sur_personne = non
- `g2-i16` idéal ?, lu NC NC NC · en trop : auteur = assure; bien = element_batiment; cause_eau = infiltration_exterieure; intentionnel = non; travaux_batiment = aucun
- `g2-i07` idéal ?, lu NC NC ? · manque : vehicule_voie_publique = oui; vol_sur_personne = non · en trop : auteur = tiers; effraction = oui; laisse_sans_surveillance = oui; proprietaire = assure; simple_disparition = non; violence = non · retiré sans appui : demenagement = non; fermeture = aucune; sejour_temporaire = non; simple_disparition = non; vehicule_voie_publique = non; vol_sur_personne = non
- `g2-p04` idéal NC, lu ? ? ? · **contredit** : evenement : vol lu mazout · en trop : auteur = tiers · retiré sans appui : auteur = tiers; bien_a_l_origine_sinistre = non; intentionnel = oui
- `g2-l03` idéal C, lu C NC NC · **contredit** : bien : objet_divers lu valeurs · manque : absence = non; bien = objet_divers · en trop : auteur = tiers; effraction = oui; portes_fermees = oui; violence = non; vol_sur_personne = non; vol_sur_personne = oui · retiré sans appui : absence = non; fermeture = cle; vol_sur_personne = non

### Contradictions sans effet sur la décision

- `bougie-03` : evenement : autre lu fumee
- `g-l07` : evenement : autre lu bris
- `g2-i11` : lieu : terrasse lu logement
- `g2-p01` : bien : objet_divers lu cles; bien : objet_divers lu element_batiment; effraction : non lu oui

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 90% (89% – 91%) | 76% (74% – 77%) | **4.333 (3 – 6)** | **0.667 (0 – 1)** | 26% (24% – 27%) |

Instables : **11** sur 97 · rappel des clauses : 69% · rappel des questions : 72% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 210.9 s · par cas, un à la fois (10 cas) : médiane 4.06 s, 95e centile 5.37 s (lecture 3.28 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.74 s, 95e centile 37.68 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 97 | 89% | 6 ⚠ | 0 |
| garantie : 1.4 | 2 | 100% | 0 | 0 |
| garantie : 2.1 | 13 | 85% | 2 ⚠ | 0 |
| garantie : 2.10 | 39 | 87% | 2 ⚠ | 0 |
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
| garantie : 6.1 | 1 | 100% | 0 | 0 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 24 | 92% | 1 ⚠ | 0 |
| thème : info_manquante | 16 | 81% | 1 ⚠ | 0 |
| thème : langue | 11 | 100% | 0 | 0 |
| thème : multi | 8 | 100% | 0 | 0 |
| thème : piege | 55 | 84% | 5 ⚠ | 0 |
| thème : variante | 13 | 92% | 1 ⚠ | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `bougie-04` attendu NC, obtenu C C NC — Pendant mes vacances, une bougie laissée sur la table du jardin s'est enflammée et a brûlé la table et le salo… *(Vrai incendie, mais table et salon de jardin = contenu du jardin, exclu du contenu assuré (12/contenu). INCERTAIN défend)*
- **⚠ couvert à tort** `val-09` attendu NC, obtenu C NC NC — Mon fer à repasser, laissé à plat sur la planche, a brûlé la housse et laissé une marque sur le tissu, sans fl… *(Définition de l'incendie : les brûlures et le contact d'une source de chaleur sans embrasement ne sont pas un incendie.)*
- **⚠ couvert à tort** `red-b06` attendu NC, obtenu C C C — La vitre de la fenêtre de la cuisine est rayée sur toute sa largeur. *(Exclusion 2.9 : les rayures et écaillements des vitres.)*
- **⚠ couvert à tort** `g-p03` attendu NC, obtenu C C C — Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune… *(Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct.)*
- **⚠ couvert à tort** `g2-i08` attendu ?, obtenu C ? ? — On m'a volé mon sac au restaurant. *(Hors du bâtiment, seul le vol commis sur l'assuré avec violences ou menaces est couvert : à préciser.)*
- **⚠ couvert à tort** `g2-p08` attendu NC, obtenu C C C — Le bain à bulles installé sur ma terrasse a fui et l'eau a abîmé le canapé du salon. *(Exclusion 2.7 : l'écoulement d'eau des piscines et des bains à bulles extérieurs.)*
- `velo-03` attendu NC, obtenu NC ? ? — Mon vélo a été volé dans ma cave privative, fermée à clé. Le cadenas de la porte a été forcé. *(Cave en immeuble à appartements : vol couvert à 1 000 EUR « si ces locaux sont fermés avec une serrure de sûreté » (2.10)*
- `velo-04` attendu NC, obtenu NC ? ? — Mon vélo a été volé dans ma cave privative. J'avais oublié de la fermer à clé et il n'y a aucune trace d'effra… *(Cave non fermée : pas de serrure de sûreté (condition du plafond caves), et obligation de prévention non respectée avec )*
- `val-11` attendu NC, obtenu ? ? ? — Pendant un orage, la pluie s'est infiltrée par la fenêtre mal jointée de ma chambre et a abîmé le mur et la mo… *(Exclusion 2.7 : une infiltration par les fenêtres, autre que celle due à une fuite des installations hydrauliques extéri)*
- `val-13` attendu C, obtenu C ? ? — La tempête a arraché des tuiles de l'immeuble et la pluie est entrée dans mon salon, abîmant le plafond et le … *(2.2 : les dommages matériels directement causés par la tempête. Garantie non écrite en règles : test de l'aveu de limite)*
- `val-14` attendu NC, obtenu NC ? NC — Lors d'un cambriolage avec la porte fracturée, on m'a volé mon chat de race. *(Exclusion 2.10 : le vol des animaux.)*
- `red-b01` attendu C, obtenu ? ? ? — Mon fils a cassé la vitre de la porte-fenêtre du salon avec un ballon. *(2.9 : le bris de vitres.)*
- `g-q02` attendu ?, obtenu ? NC ? — Mon ordinateur portable a disparu de mon appartement. *(« Disparu » n'est pas « volé » : la simple disparition est exclue ; il faut établir le vol.)*
- `g-h05` attendu C, obtenu ? C C — Les égouts publics ont refoulé pendant un gros orage et l'eau sale a envahi la salle de bain. *(2.3 : le refoulement d'égouts publics est une catastrophe naturelle couverte ; 2.7 l'exclut. Non traduite.)*
- `g2-i01` attendu ?, obtenu NC NC NC — Mon vélo a été volé dans le local de mon immeuble. *(« Le local de mon immeuble » : local commun (vol exclu dans les parties communes) ou cave privative (couverte si serrure)*
- `g2-i02` attendu ?, obtenu NC C NC — On a cambriolé mon appartement pendant le week-end où j'étais absent. La serrure porte des rayures, mais la po… *(Des traces sans réparation nécessaire ne sont pas une effraction (définition). Sans effraction, l'obligation de fermer à)*
- `g2-p04` attendu NC, obtenu ? ? ? — On a siphonné le fioul de la cuve de chauffage, dans ma cave. *(Exclusion 2.10 : le vol de mazout de chauffage.)*
- `g2-l03` attendu C, obtenu C NC NC — Je n'étais pas absente et la porte n'était pas ouverte : quelqu'un est entré pendant que je dormais et a pris … *(Vol du contenu dans le bâtiment ; l'obligation de fermer à clé ne vaut qu'en cas d'absence.)*
