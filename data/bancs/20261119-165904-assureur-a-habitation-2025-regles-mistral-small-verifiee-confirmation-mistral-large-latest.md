# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee, confirmation mistral-large-latest)

2026-11-19T16:27:31 · golden set v12 (97 cas, empreinte `0534a0545f66a07d`) · cas validés par l'auteur : 0 sur 97


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 1.9 | ✓ |
| lecture | decisions_changees | ≤ 2 | 18.67 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 8 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 17 | ✗ |
| chaine | faux_couverts | ≤ 0 | 1.333 | ✗ |
| chaine | faux_refus | ≤ 1 | 1.333 | ✗ |
| chaine | exactitude | ≥ 0.85 | 0.89 | ✓ |
| chaine | instables | ≤ 3 | 15 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 0.75 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 106.37 | ✗ |

## Depuis le banc précédent de même configuration (2026-11-19T10:05:33, mistral:mistral-small-latest · verifiee, confirmation mistral-large-latest)

- lecture · rappel_faits : 0.871 → 0.89
- chaine · exactitude : 0.862 → 0.89
- chaine · exactitude_stricte : 0.673 → 0.746
- chaine · faux_couverts : 1.667 → 1.333
- chaine · faux_refus : 0 → 1.333

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

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **18.67** par exécution, dont **8** cas vers un couvert à tort.

Rappel des faits idéaux : 89% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 17 cas · faits vagues : 0 cas · faits en trop : 82 cas · faits retirés (sans appui ou non dits) : 80 cas

### La lecture change la décision

- **⚠ vers couvert** `bougie-04` idéal NC, lu ? C NC · **contredit** : lieu : jardin lu logement/terrasse · manque : absence = oui · en trop : auteur = assure; cause_dommage = autre; travaux_batiment = aucun; travaux_vitres = aucun; type_dommage = bris · retiré sans appui : chaleur_sans_feu = non; effraction = non; manque_entretien = non
- **⚠ vers couvert** `val-01` idéal ?, lu ? C ? · manque : absence = oui; effraction = non; fenetres_fermees = non; portes_fermees = oui · en trop : auteur = tiers; fermeture = aucune; proprietaire = assure; simple_disparition = non; violence = non · retiré sans appui : fenetres_fermees = non; simple_disparition = non
- **⚠ vers couvert** `red-b06` idéal NC, lu C C C · **contredit** : evenement : bris lu vandalisme · manque : type_dommage = rayure_ou_ecaillement · retiré sans appui : auteur = tiers; effraction = non; fenetres_fermees = non; intentionnel = oui; manque_entretien = non
- **⚠ vers couvert** `g-p03` idéal ?, lu C C C · **contredit** : bien : objet_divers lu cles · manque : absence = oui; portes_fermees = oui · en trop : fermeture = cle · retiré sans appui : fermeture = cle; simple_disparition = non
- **⚠ vers couvert** `g-h02` idéal ?, lu ? C ? · en trop : cause_perte_alimentaire = coupure_soudaine_reseau; chaleur_sans_feu = oui; proprietaire = assure; usage_professionnel = non · retiré sans appui : cause_perte_alimentaire = coupure_soudaine_reseau; embrasement = non; flammes = non
- **⚠ vers couvert** `g2-i11` idéal ?, lu ? ? C · **contredit** : lieu : terrasse lu logement · en trop : type_dommage = bris; vent_dommages_voisins = oui
- **⚠ vers couvert** `g2-p04` idéal NC, lu C C C · **contredit** : evenement : vol lu mazout · en trop : auteur = tiers; bien_a_l_origine_sinistre = non · retiré sans appui : auteur = tiers; intentionnel = oui
- **⚠ vers couvert** `g2-p08` idéal NC, lu C C C · **contredit** : cause_eau : piscine_exterieure lu debordement_aquarium · en trop : travaux_batiment = aucun
- `velo-04` idéal NC, lu ? NC NC · manque : fermeture = aucune; vol_sur_personne = non · en trop : proprietaire = assure · retiré sans appui : fermeture = aucune; simple_disparition = non; vol_sur_personne = non
- `val-11` idéal NC, lu ? ? ? · en trop : auteur = assure · retiré sans appui : alea_tempete = vent; construction_close = oui
- `val-12` idéal C, lu NC C C · **contredit** : cause_eau : fuite_installation lu debordement_recipient · en trop : absence = non; auteur = assure; intentionnel = non; travaux_batiment = aucun
- `val-13` idéal C, lu ? ? C · **contredit** : cause_eau : infiltration_toiture lu infiltration_exterieure · manque : cause_eau = infiltration_toiture · en trop : alea_tempete = vent; construction_close = oui; travaux_batiment = aucun · retiré sans appui : construction_delabree = non
- `red-b01` idéal C, lu NC NC NC · en trop : auteur = famille; intentionnel = oui; manque_entretien = non; proprietaire = assure; travaux_batiment = aucun; travaux_vitres = aucun; type_dommage = bris; vitre_placee = oui · retiré sans appui : auteur = famille; effraction = non; manque_entretien = non
- `g-q02` idéal ?, lu NC NC NC · en trop : evenement = vol; proprietaire = assure; simple_disparition = oui; vol_sur_personne = non · retiré sans appui : fermeture = aucune; sejour_temporaire = non; vol_sur_personne = non
- `g-h03` idéal C, lu ? ? ? · en trop : bien_a_l_origine_sinistre = oui
- `g-h05` idéal C, lu ? C C
- `g2-i01` idéal ?, lu NC NC NC · en trop : auteur = tiers; effraction = oui; lieu = parties_communes; occupation_partielle = oui; proprietaire = assure; simple_disparition = non; violence = non; vol_sur_personne = non · retiré sans appui : fermeture = aucune; sejour_temporaire = non; vol_sur_personne = non
- `g2-i02` idéal C, lu C NC C · **contredit** : bien : objet_divers lu bijoux; bien : objet_divers lu cles; effraction : non lu oui · manque : bien = objet_divers · en trop : auteur = tiers; fermeture = cle; proprietaire = assure; simple_disparition = non; type_dommage = rayure_ou_ecaillement; violence = non; vol_sur_personne = non · retiré sans appui : fermeture = cle; portes_fermees = oui; sejour_temporaire = non; serrure_surete = non; simple_disparition = non
- `g2-i03` idéal C, lu NC NC NC · en trop : cause_eau = infiltration_exterieure
- `g2-i04` idéal ?, lu NC NC NC · en trop : auteur = tiers; evenement = vol; proprietaire = assure; sejour_temporaire = non; simple_disparition = oui; vol_sur_personne = non · retiré sans appui : auteur = tiers; sejour_temporaire = non; vol_sur_personne = non
- `g2-i06` idéal ?, lu ? ? NC · en trop : periode_gel = oui; prevention_gel = non; travaux_batiment = aucun · retiré sans appui : prevention_gel = non
- `g2-i08` idéal ?, lu NC NC NC · **contredit** : lieu : autre_batiment lu voie_publique · en trop : auteur = tiers; laisse_sans_surveillance = oui; proprietaire = assure; sejour_temporaire = oui; simple_disparition = non; violence = non; vol_sur_personne = oui · retiré sans appui : auteur = tiers; effraction = non; fermeture = aucune; simple_disparition = non
- `g2-i16` idéal ?, lu NC NC NC · en trop : auteur = assure; bien = element_batiment; cause_eau = infiltration_exterieure; travaux_batiment = aucun
- `g2-p01` idéal C, lu NC C C · **contredit** : bien : objet_divers lu element_batiment; effraction : non lu oui · manque : absence = oui; bien = objet_divers; portes_fermees = oui · en trop : auteur = tiers; cles_a_proximite = non; fermeture = cle; proprietaire = assure; sejour_temporaire = oui; simple_disparition = non · retiré sans appui : violence = non; vol_sur_personne = non
- `g2-i07` idéal ?, lu NC ? ? · manque : vehicule_voie_publique = oui; vol_sur_personne = non · en trop : auteur = tiers; effraction = oui; laisse_sans_surveillance = oui; proprietaire = assure; simple_disparition = non; violence = non · retiré sans appui : demenagement = non; fermeture = aucune; sejour_temporaire = non; vehicule_voie_publique = non; vol_sur_personne = non
- `g2-l03` idéal C, lu NC NC NC · manque : absence = non; bien = objet_divers · en trop : auteur = tiers; effraction = oui; fermeture = cle; portes_fermees = oui; proprietaire = assure; simple_disparition = non; violence = non; vol_sur_personne = non · retiré sans appui : absence = non; effraction = non; effraction = oui; simple_disparition = non; violence = non; vol_sur_personne = non

### Contradictions sans effet sur la décision

- `velo-03` : fermeture : cadenas lu cle
- `bougie-03` : evenement : autre lu fumee
- `val-09` : bien : objet_divers lu mobilier; evenement : autre lu fumee
- `g-l02` : absence : oui lu non
- `g-l03` : evenement : autre lu degat_eaux; flammes : non lu oui
- `g-l07` : evenement : autre lu bris

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 89% (87% – 92%) | 75% (70% – 78%) | **1.333 (1 – 2)** | **1.333 (1 – 2)** | 32% (28% – 37%) |

Instables : **15** sur 97 · rappel des clauses : 66% · rappel des questions : 75% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 565.2 s · par cas, un à la fois (10 cas) : médiane 8.1 s, 95e centile 106.37 s (lecture 3.2 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 12.37 s, 95e centile 71.32 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 97 | 87% | 1 ⚠ | 2 |
| garantie : 1.4 | 2 | 100% | 0 | 0 |
| garantie : 2.1 | 13 | 85% | 0 | 0 |
| garantie : 2.10 | 39 | 85% | 0 | 2 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.12 | 1 | 100% | 0 | 0 |
| garantie : 2.2 | 6 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.5 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 4 | 100% | 0 | 0 |
| garantie : 2.7 | 16 | 75% | 1 ⚠ | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 7 | 86% | 0 | 0 |
| garantie : 6.1 | 1 | 100% | 0 | 0 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 24 | 96% | 0 | 0 |
| thème : info_manquante | 16 | 94% | 0 | 0 |
| thème : langue | 11 | 91% | 0 | 1 |
| thème : multi | 8 | 75% | 0 | 0 |
| thème : piege | 55 | 87% | 1 ⚠ | 1 |
| thème : variante | 13 | 77% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `val-01` attendu NC, obtenu ? C ? — Pendant que j'étais au travail, quelqu'un est entré par la fenêtre de ma chambre, au rez-de-chaussée, que j'av… *(Obligation de prévention (2.10) : en cas d'absence, « fermer correctement les fenêtres […] facilement accessibles ». Lie)*
- **⚠ couvert à tort** `g2-p08` attendu NC, obtenu C C C — Le bain à bulles installé sur ma terrasse a fui et l'eau a abîmé le canapé du salon. *(Exclusion 2.7 : l'écoulement d'eau des piscines et des bains à bulles extérieurs.)*
- `velo-04` attendu NC, obtenu ? NC NC — Mon vélo a été volé dans ma cave privative. J'avais oublié de la fermer à clé et il n'y a aucune trace d'effra… *(Cave non fermée : pas de serrure de sûreté (condition du plafond caves), et obligation de prévention non respectée avec )*
- `velo-05` attendu C, obtenu ? C C — Des cambrioleurs ont fracturé la porte de mon appartement et ont volé mon vélo, rangé dans l'entrée. *(Vol du contenu dans le bâtiment, avec effraction. Le vélo non motorisé est du contenu (12/contenu). Franchise 7.7.)*
- `velo-06` attendu NC, obtenu ? ? NC — Mon vélo était attaché à un arceau dans la rue avec un antivol. L'antivol a été coupé et le vélo volé. *(Vol dans la rue, sans violence : hors du bâtiment, et ce n'est pas un « vol commis sur l'assuré … suite à violences ».)*
- `bougie-02` attendu C, obtenu ? C C — Une bougie allumée est tombée dans le salon, la nappe a pris feu et les flammes ont brûlé la table. *(Flammes, embrasement de la nappe : incendie au sens du contrat (2.1, 12/incendie).)*
- `bougie-04` attendu NC, obtenu ? ? NC — Pendant mes vacances, une bougie laissée sur la table du jardin s'est enflammée et a brûlé la table et le salo… *(Vrai incendie, mais table et salon de jardin = contenu du jardin, exclu du contenu assuré (12/contenu). INCERTAIN défend)*
- `val-07` attendu C, obtenu C C ? — Dans le métro, deux individus m'ont menacé avec un couteau et ont pris mon portefeuille et mon téléphone. *(2.10 : le vol commis sur l'assuré, en dehors des biens assurés, suite à violences et/ou menaces (limite 2 500 EUR).)*
- `val-11` attendu NC, obtenu ? ? ? — Pendant un orage, la pluie s'est infiltrée par la fenêtre mal jointée de ma chambre et a abîmé le mur et la mo… *(Exclusion 2.7 : une infiltration par les fenêtres, autre que celle due à une fuite des installations hydrauliques extéri)*
- `val-12` attendu C, obtenu ? C C — Ma baignoire a débordé pendant que j'étais au téléphone ; l'eau a abîmé mon parquet. *(2.7 couvre l'ensemble des dégâts des eaux ; l'exclusion du récipient vise un récipient NON relié à l'installation hydrau)*
- `val-13` attendu C, obtenu ? ? C — La tempête a arraché des tuiles de l'immeuble et la pluie est entrée dans mon salon, abîmant le plafond et le … *(2.2 : les dommages matériels directement causés par la tempête. Garantie non écrite en règles : test de l'aveu de limite)*
- `red-t03` attendu NC, obtenu NC ? NC — Le poids de la neige a fait s'effondrer mon carport en bois, simplement posé sur des plots, sans ancrage en bé… *(Exclusion 2.2 : annexes faisant partie du bâtiment non fixées au sol par un ancrage en béton.)*
- `red-b01` attendu C, obtenu ? ? ? — Mon fils a cassé la vitre de la porte-fenêtre du salon avec un ballon. *(2.9 : le bris de vitres.)*
- `g-l07` attendu NC, obtenu ? NC NC — Ce n'est pas un vol : mon fils a pris mon vélo sans me le dire et il l'a cassé en tombant. *(Négation. Pas de vol (et un vol par un descendant serait exclu, 2.10-a) ; aucune garantie de base ne couvre la casse d'u)*
- `g-p04` attendu C, obtenu ? ? ? — Le chauffe-eau a fui ; le parquet est abîmé et le chauffe-eau lui-même est hors d'usage. *(2.7 : le parquet est couvert ; le chauffe-eau à l'origine du sinistre est exclu (exclusion partielle).)*
- `g-h05` attendu C, obtenu ? C C — Les égouts publics ont refoulé pendant un gros orage et l'eau sale a envahi la salle de bain. *(2.3 : le refoulement d'égouts publics est une catastrophe naturelle couverte ; 2.7 l'exclut. Non traduite.)*
- `g-m02` attendu C, obtenu ? ? ? — Un incendie chez le voisin s'est propagé à mon appartement ; les pompiers ont inondé le salon en l'éteignant. *(2.1 : incendie ; l'eau d'extinction en est la conséquence.)*
- `g2-i01` attendu ?, obtenu NC NC NC — Mon vélo a été volé dans le local de mon immeuble. *(« Le local de mon immeuble » : local commun (vol exclu dans les parties communes) ou cave privative (couverte si serrure)*
- `g2-i02` attendu ?, obtenu ? NC ? — On a cambriolé mon appartement pendant le week-end où j'étais absent. La serrure porte des rayures, mais la po… *(Des traces sans réparation nécessaire ne sont pas une effraction (définition). Sans effraction, l'obligation de fermer à)*
- `g2-i11` attendu ?, obtenu ? ? C — Après le gros coup de vent d'hier, des tuiles de l'immeuble sont tombées sur mon balcon et l'ont abîmé. *(La tempête suppose un vent d'au moins 80 km/h ou des dégâts aux biens voisins (définition) : non précisé. Garantie 2.2 n)*
- `g2-p01` attendu C, obtenu NC C C — Pendant mes vacances, des cambrioleurs ont ouvert ma porte sans la casser : il n'y a que des traces de tournev… *(Pas d'effraction au sens du contrat, mais la porte était fermée à clé : l'obligation est respectée, le vol dans le bâtim)*
- `g2-p04` attendu NC, obtenu ? ? ? — On a siphonné le fioul de la cuve de chauffage, dans ma cave. *(Exclusion 2.10 : le vol de mazout de chauffage.)*
- `g2-l03` attendu C, obtenu NC NC NC — Je n'étais pas absente et la porte n'était pas ouverte : quelqu'un est entré pendant que je dormais et a pris … *(Vol du contenu dans le bâtiment ; l'obligation de fermer à clé ne vaut qu'en cas d'absence.)*
