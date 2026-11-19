# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-19T13:54:52 · golden set v11 (97 cas, empreinte `0534a0545f66a07d`) · cas validés par l'auteur : 0 sur 97


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 1.9 | ✓ |
| lecture | decisions_changees | ≤ 2 | 21.33 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 8 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 16 | ✗ |
| chaine | faux_couverts | ≤ 0 | 4 | ✗ |
| chaine | faux_refus | ≤ 1 | 1.667 | ✗ |
| chaine | exactitude | ≥ 0.85 | 0.876 | ✓ |
| chaine | instables | ≤ 3 | 12 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 0.75 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 10.45 | ✗ |

## Depuis le banc précédent (2026-11-19T12:49:13)

- lecture · rappel_faits : 0.877 → 0.887
- chaine · exactitude : 0.88 → 0.876
- chaine · exactitude_stricte : 0.756 → 0.749
- chaine · faux_couverts : 4.667 → 4
- chaine · faux_refus : 0.667 → 1.667

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

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **21.33** par exécution, dont **8** cas vers un couvert à tort.

Rappel des faits idéaux : 89% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 16 cas · faits vagues : 0 cas · faits en trop : 82 cas · faits retirés (sans appui ou non dits) : 79 cas

### La lecture change la décision

- **⚠ vers couvert** `bougie-04` idéal NC, lu C C C · **contredit** : lieu : jardin lu logement/terrasse · manque : absence = oui · en trop : auteur = assure; cause_dommage = autre; travaux_batiment = aucun; type_dommage = bris · retiré sans appui : auteur = assure; chaleur_sans_feu = non; effraction = non; intentionnel = non; manque_entretien = non; travaux_batiment = aucun; travaux_vitres = aucun
- **⚠ vers couvert** `red-b06` idéal NC, lu C C C · **contredit** : evenement : bris lu vandalisme · manque : type_dommage = rayure_ou_ecaillement · retiré sans appui : auteur = tiers; effraction = non; fenetres_fermees = non; fermeture = aucune; intentionnel = oui; manque_entretien = non
- **⚠ vers couvert** `g-p03` idéal ?, lu C C C · **contredit** : bien : objet_divers lu cles · manque : absence = oui; effraction = non; portes_fermees = oui · en trop : fermeture = cle; sejour_temporaire = oui · retiré sans appui : effraction = non; simple_disparition = non
- **⚠ vers couvert** `g-h02` idéal ?, lu C C C · en trop : cause_perte_alimentaire = coupure_soudaine_reseau; chaleur_sans_feu = oui; proprietaire = assure; usage_professionnel = non · retiré sans appui : embrasement = non; flammes = non
- **⚠ vers couvert** `g2-i11` idéal ?, lu C C C · **contredit** : lieu : terrasse lu logement · en trop : construction_close = oui; vent_dommages_voisins = oui · retiré sans appui : travaux_batiment = aucun
- **⚠ vers couvert** `g2-i16` idéal ?, lu C C NC · en trop : auteur = assure; bien = element_batiment; cause_eau = infiltration_exterieure · retiré sans appui : intentionnel = non
- **⚠ vers couvert** `g2-p04` idéal NC, lu ? C C · **contredit** : evenement : vol lu mazout · en trop : auteur = tiers; bien_a_l_origine_sinistre = non · retiré sans appui : intentionnel = oui
- **⚠ vers couvert** `g2-p08` idéal NC, lu C C C · **contredit** : cause_eau : piscine_exterieure lu debordement_aquarium · retiré sans appui : travaux_batiment = aucun
- `velo-03` idéal NC, lu ? ? ? · **contredit** : fermeture : cadenas lu cle · manque : vol_sur_personne = non · en trop : auteur = tiers; portes_fermees = oui; proprietaire = assure; simple_disparition = non · retiré sans appui : auteur = tiers; sejour_temporaire = non; serrure_surete = non; simple_disparition = non; violence = non; vol_sur_personne = non
- `velo-06` idéal NC, lu ? NC ? · manque : fermeture = cadenas; violence = non; vol_sur_personne = non · en trop : auteur = tiers; dispositifs_antivol_installes = oui; effraction = oui; proprietaire = assure; simple_disparition = non · retiré sans appui : fermeture = aucune; laisse_sans_surveillance = non; sejour_temporaire = non; simple_disparition = non; violence = non; vol_sur_personne = non
- `val-10` idéal NC, lu ? ? ? · manque : prevention_gel = non · en trop : periode_gel = oui; travaux_batiment = aucun · retiré sans appui : prevention_gel = non
- `val-11` idéal NC, lu ? ? ? · en trop : auteur = assure; construction_close = oui; intentionnel = non; periode_gel = non; travaux_batiment = aucun · retiré sans appui : construction_close = oui
- `val-12` idéal C, lu NC NC NC · **contredit** : cause_eau : fuite_installation lu debordement_recipient · en trop : absence = non; absence = oui; auteur = assure; intentionnel = non; travaux_batiment = aucun
- `val-13` idéal C, lu ? C C · **contredit** : cause_eau : infiltration_toiture lu infiltration_exterieure · manque : cause_eau = infiltration_toiture · en trop : alea_tempete = vent · retiré sans appui : construction_close = oui
- `red-b01` idéal C, lu NC NC C · en trop : auteur = famille; intentionnel = oui; proprietaire = assure; type_dommage = bris; vitre_placee = oui · retiré sans appui : effraction = non; manque_entretien = non; travaux_batiment = aucun; travaux_vitres = aucun
- `g-q02` idéal ?, lu NC NC NC · en trop : evenement = vol; proprietaire = assure; simple_disparition = oui · retiré sans appui : fermeture = aucune; sejour_temporaire = non; vol_sur_personne = non
- `g-q04` idéal C, lu NC C C · en trop : cause_eau = infiltration_exterieure
- `g-h03` idéal C, lu ? ? ? · en trop : bien_a_l_origine_sinistre = oui
- `g2-i01` idéal ?, lu NC NC NC · en trop : auteur = tiers; effraction = oui; lieu = parties_communes; occupation_partielle = oui; proprietaire = assure; simple_disparition = non; vol_sur_personne = non · retiré sans appui : fermeture = aucune; sejour_temporaire = non; violence = non; vol_sur_personne = non
- `g2-i02` idéal C, lu C NC C · **contredit** : bien : objet_divers lu bijoux; effraction : non lu oui · manque : bien = objet_divers · en trop : auteur = tiers; fermeture = cle; proprietaire = assure; type_dommage = rayure_ou_ecaillement · retiré sans appui : manque_entretien = non; sejour_temporaire = non; serrure_surete = non; simple_disparition = non; violence = non; vol_sur_personne = non
- `g2-i03` idéal C, lu NC NC NC · en trop : cause_eau = infiltration_exterieure
- `g2-i04` idéal ?, lu NC NC NC · en trop : auteur = tiers; evenement = vol; proprietaire = assure; sejour_temporaire = non; simple_disparition = oui; vol_sur_personne = non
- `g2-i07` idéal ?, lu NC ? ? · manque : vehicule_voie_publique = oui · en trop : auteur = tiers; effraction = oui; laisse_sans_surveillance = oui; materiel_laisse_en_vue = oui; proprietaire = assure; vehicule_ferme_cle = non; violence = non · retiré sans appui : fenetres_fermees = non; fermeture = aucune; sejour_temporaire = non; simple_disparition = non; vehicule_ferme_cle = non; vehicule_voie_publique = non; violence = non
- `g2-l03` idéal C, lu C NC NC · manque : absence = non; bien = objet_divers · en trop : auteur = tiers; portes_fermees = oui; vol_sur_personne = non; vol_sur_personne = oui · retiré sans appui : absence = non; fermeture = cle; portes_fermees = oui
- `g2-l04` idéal C, lu NC C C · en trop : manque_entretien = oui · retiré sans appui : travaux_batiment = aucun
- `g2-m01` idéal C, lu ? C C · manque : embrasement = oui · en trop : cause_dommage = autre; effraction = oui; intentionnel = non; type_dommage = bris · retiré sans appui : cause_dommage = autre; chaleur_sans_feu = non; travaux_batiment = aucun; travaux_vitres = aucun
- `g2-m02` idéal C, lu C ? C · en trop : alea_tempete = vent; cause_eau = infiltration_exterieure; type_dommage = bris · retiré sans appui : construction_close = oui; effraction = non

### Contradictions sans effet sur la décision

- `bougie-01` : evenement : autre lu degat_eaux
- `bougie-03` : evenement : autre lu fumee
- `val-09` : bien : objet_divers lu mobilier; evenement : autre lu fumee
- `g-l07` : evenement : autre lu bris
- `g2-i08` : lieu : autre_batiment lu voie_publique
- `g2-p01` : bien : objet_divers lu cles; bien : objet_divers lu element_batiment; effraction : non lu oui

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 88% (87% – 89%) | 75% (72% – 77%) | **4 (4 – 4)** | **1.667 (1 – 2)** | 22% (21% – 25%) |

Instables : **12** sur 97 · rappel des clauses : 68% · rappel des questions : 75% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 209.2 s · par cas, un à la fois (10 cas) : médiane 3.74 s, 95e centile 10.45 s (lecture 2.83 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.58 s, 95e centile 38.55 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 97 | 87% | 4 ⚠ | 1 |
| garantie : 1.4 | 2 | 100% | 0 | 0 |
| garantie : 2.1 | 13 | 85% | 1 ⚠ | 0 |
| garantie : 2.10 | 39 | 87% | 1 ⚠ | 0 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.12 | 1 | 100% | 0 | 0 |
| garantie : 2.2 | 6 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.5 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 4 | 100% | 0 | 0 |
| garantie : 2.7 | 16 | 75% | 1 ⚠ | 1 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 7 | 71% | 1 ⚠ | 0 |
| garantie : 6.1 | 1 | 100% | 0 | 0 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 24 | 92% | 1 ⚠ | 0 |
| thème : info_manquante | 16 | 94% | 0 | 0 |
| thème : langue | 11 | 91% | 0 | 0 |
| thème : multi | 8 | 88% | 0 | 0 |
| thème : piege | 55 | 84% | 4 ⚠ | 1 |
| thème : variante | 13 | 85% | 1 ⚠ | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `bougie-04` attendu NC, obtenu C C C — Pendant mes vacances, une bougie laissée sur la table du jardin s'est enflammée et a brûlé la table et le salo… *(Vrai incendie, mais table et salon de jardin = contenu du jardin, exclu du contenu assuré (12/contenu). INCERTAIN défend)*
- **⚠ couvert à tort** `red-b06` attendu NC, obtenu C C C — La vitre de la fenêtre de la cuisine est rayée sur toute sa largeur. *(Exclusion 2.9 : les rayures et écaillements des vitres.)*
- **⚠ couvert à tort** `g-p03` attendu NC, obtenu C C C — Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune… *(Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct.)*
- **⚠ couvert à tort** `g2-p08` attendu NC, obtenu C C C — Le bain à bulles installé sur ma terrasse a fui et l'eau a abîmé le canapé du salon. *(Exclusion 2.7 : l'écoulement d'eau des piscines et des bains à bulles extérieurs.)*
- `velo-06` attendu NC, obtenu ? NC ? — Mon vélo était attaché à un arceau dans la rue avec un antivol. L'antivol a été coupé et le vélo volé. *(Vol dans la rue, sans violence : hors du bâtiment, et ce n'est pas un « vol commis sur l'assuré … suite à violences ».)*
- `val-11` attendu NC, obtenu ? ? ? — Pendant un orage, la pluie s'est infiltrée par la fenêtre mal jointée de ma chambre et a abîmé le mur et la mo… *(Exclusion 2.7 : une infiltration par les fenêtres, autre que celle due à une fuite des installations hydrauliques extéri)*
- `val-12` attendu C, obtenu NC NC NC — Ma baignoire a débordé pendant que j'étais au téléphone ; l'eau a abîmé mon parquet. *(2.7 couvre l'ensemble des dégâts des eaux ; l'exclusion du récipient vise un récipient NON relié à l'installation hydrau)*
- `val-13` attendu C, obtenu ? C C — La tempête a arraché des tuiles de l'immeuble et la pluie est entrée dans mon salon, abîmant le plafond et le … *(2.2 : les dommages matériels directement causés par la tempête. Garantie non écrite en règles : test de l'aveu de limite)*
- `red-b01` attendu C, obtenu ? ? C — Mon fils a cassé la vitre de la porte-fenêtre du salon avec un ballon. *(2.9 : le bris de vitres.)*
- `red-b05` attendu NC, obtenu ? NC ? — Le grand miroir que je venais d'acheter, encore dans son carton et pas encore accroché, s'est brisé quand je l… *(Exclusion 2.9 : les dommages aux vitres et biens assimilés non placés.)*
- `g-q04` attendu C, obtenu ? C C — De l'eau coule du plafond de ma salle de bain et a abîmé le mur. *(2.7 couvre l'ensemble des dégâts des eaux ; la cause inconnue n'établit aucune exclusion (c'est à l'assureur de la prouv)*
- `g2-i01` attendu ?, obtenu NC NC NC — Mon vélo a été volé dans le local de mon immeuble. *(« Le local de mon immeuble » : local commun (vol exclu dans les parties communes) ou cave privative (couverte si serrure)*
- `g2-i02` attendu ?, obtenu C NC C — On a cambriolé mon appartement pendant le week-end où j'étais absent. La serrure porte des rayures, mais la po… *(Des traces sans réparation nécessaire ne sont pas une effraction (définition). Sans effraction, l'obligation de fermer à)*
- `g2-i11` attendu ?, obtenu C ? C — Après le gros coup de vent d'hier, des tuiles de l'immeuble sont tombées sur mon balcon et l'ont abîmé. *(La tempête suppose un vent d'au moins 80 km/h ou des dégâts aux biens voisins (définition) : non précisé. Garantie 2.2 n)*
- `g2-i16` attendu C, obtenu C C ? — De l'eau de mon appartement s'est infiltrée chez le voisin du dessous, qui me demande de payer ses réparations… *(2.5 : responsabilité civile du fait du bâtiment et du contenu envers les tiers. Garantie non traduite.)*
- `g2-p01` attendu C, obtenu ? ? ? — Pendant mes vacances, des cambrioleurs ont ouvert ma porte sans la casser : il n'y a que des traces de tournev… *(Pas d'effraction au sens du contrat, mais la porte était fermée à clé : l'obligation est respectée, le vol dans le bâtim)*
- `g2-p04` attendu NC, obtenu ? ? ? — On a siphonné le fioul de la cuve de chauffage, dans ma cave. *(Exclusion 2.10 : le vol de mazout de chauffage.)*
- `g2-l03` attendu C, obtenu C NC NC — Je n'étais pas absente et la porte n'était pas ouverte : quelqu'un est entré pendant que je dormais et a pris … *(Vol du contenu dans le bâtiment ; l'obligation de fermer à clé ne vaut qu'en cas d'absence.)*
- `g2-l04` attendu C, obtenu ? C C — Le lave-vaisselle est tombé en panne et a fui pendant la nuit ; le parquet de la cuisine est gondolé. *(2.7 : l'ensemble des dommages causés par l'eau.)*
- `g2-m01` attendu C, obtenu ? C C — Un court-circuit a provoqué un incendie dans le salon ; pour entrer, les pompiers ont dû casser la porte d'ent… *(2.1 : l'incendie, et les dégâts causés pour l'éteindre.)*
- `g2-m02` attendu C, obtenu C ? C — La tempête a cassé la fenêtre du salon et la pluie a abîmé le canapé. *(La vitre est couverte par le bris de vitrages (2.9) ; le canapé relève de la tempête (2.2), non traduite.)*
