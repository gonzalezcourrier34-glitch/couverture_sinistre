# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-19T18:12:17 · golden set v12 (97 cas, empreinte `0534a0545f66a07d`) · cas validés par l'auteur : 0 sur 97


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 1.9 | ✓ |
| lecture | decisions_changees | ≤ 2 | 23.33 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 8 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 22 | ✗ |
| chaine | faux_couverts | ≤ 0 | 4.333 | ✗ |
| chaine | faux_refus | ≤ 1 | 4.333 | ✗ |
| chaine | exactitude | ≥ 0.85 | 0.862 | ✓ |
| chaine | instables | ≤ 3 | 13 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 0.722 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 4.29 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-19T15:55:50, mistral:mistral-small-latest · verifiee)

- lecture · rappel_faits : 0.893 → 0.875
- chaine · exactitude : 0.897 → 0.862
- chaine · exactitude_stricte : 0.763 → 0.718
- chaine · faux_refus : 0.667 → 4.333

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

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **23.33** par exécution, dont **8** cas vers un couvert à tort.

Rappel des faits idéaux : 88% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 22 cas · faits vagues : 0 cas · faits en trop : 89 cas · faits retirés (sans appui ou non dits) : 79 cas

### La lecture change la décision

- **⚠ vers couvert** `bougie-04` idéal NC, lu C C NC · manque : absence = oui · en trop : auteur = assure; intentionnel = non; travaux_batiment = aucun; type_dommage = bris · retiré sans appui : manque_entretien = non
- **⚠ vers couvert** `red-b06` idéal NC, lu C C C · **contredit** : evenement : bris lu vandalisme · manque : type_dommage = rayure_ou_ecaillement · en trop : effraction = non · retiré sans appui : auteur = tiers; effraction = non; fenetres_fermees = non; fermeture = aucune; intentionnel = oui; manque_entretien = non
- **⚠ vers couvert** `g-p03` idéal ?, lu C C C · **contredit** : bien : objet_divers lu cles · manque : portes_fermees = oui · en trop : fermeture = cle · retiré sans appui : fermeture = cle; simple_disparition = non
- **⚠ vers couvert** `g-h02` idéal ?, lu ? C ? · manque : lieu = logement · en trop : cause_perte_alimentaire = coupure_soudaine_reseau; chaleur_sans_feu = oui; proprietaire = assure; usage_professionnel = non · retiré sans appui : cause_perte_alimentaire = coupure_soudaine_reseau; chaleur_sans_feu = non; embrasement = non; flammes = non
- **⚠ vers couvert** `g2-i04` idéal ?, lu C C NC · en trop : auteur = tiers; effraction = non; evenement = vol; proprietaire = assure; simple_disparition = oui; violence = non; vol_sur_personne = non · retiré sans appui : auteur = tiers; fermeture = aucune; sejour_temporaire = non; simple_disparition = non; vol_sur_personne = non
- **⚠ vers couvert** `g2-i08` idéal ?, lu NC C ? · **contredit** : lieu : autre_batiment lu voie_publique · en trop : auteur = tiers; laisse_sans_surveillance = oui; proprietaire = assure; simple_disparition = non; violence = non; violence = oui; vol_sur_personne = oui · retiré sans appui : auteur = tiers; fermeture = aucune; violence = non
- **⚠ vers couvert** `g2-i11` idéal ?, lu C ? C · **contredit** : lieu : terrasse lu logement · en trop : type_dommage = bris; vent_dommages_voisins = oui
- **⚠ vers couvert** `g2-p08` idéal NC, lu C NC C · **contredit** : cause_eau : piscine_exterieure lu debordement_aquarium · manque : cause_eau = piscine_exterieure · en trop : type_dommage = moisissure · retiré sans appui : cause_eau = debordement_aquarium; travaux_batiment = aucun; type_dommage = moisissure
- `velo-03` idéal NC, lu ? ? ? · **contredit** : fermeture : cadenas lu cle · manque : vol_sur_personne = non · en trop : auteur = tiers; proprietaire = assure; simple_disparition = non · retiré sans appui : sejour_temporaire = non; serrure_surete = non; simple_disparition = non; violence = non; vol_sur_personne = non
- `velo-04` idéal NC, lu ? ? ? · manque : effraction = non; fermeture = aucune; vol_sur_personne = non · en trop : auteur = tiers; proprietaire = assure; simple_disparition = non · retiré sans appui : effraction = non; fermeture = aucune; sejour_temporaire = non; simple_disparition = non; vol_sur_personne = non
- `val-03` idéal NC, lu NC ? NC · en trop : auteur = tiers; simple_disparition = non; violence = non · retiré sans appui : fermeture = aucune; portes_fermees = non; simple_disparition = non
- `val-10` idéal NC, lu ? ? NC · manque : prevention_gel = non · en trop : periode_gel = oui; travaux_batiment = aucun; type_dommage = bris · retiré sans appui : prevention_gel = non
- `val-11` idéal NC, lu ? ? ? · en trop : auteur = assure; type_dommage = moisissure · retiré sans appui : alea_tempete = vent; construction_close = oui
- `val-13` idéal C, lu ? C C · **contredit** : cause_eau : infiltration_toiture lu infiltration_exterieure · manque : cause_eau = infiltration_toiture · en trop : alea_tempete = vent; construction_close = oui; type_dommage = moisissure; vent_dommages_voisins = oui · retiré sans appui : construction_delabree = non; periode_gel = non
- `red-t03` idéal NC, lu NC NC ? · **contredit** : bien : element_batiment lu materiaux_construction · manque : annexe_ancree_beton = non; construction_close = non · retiré sans appui : annexe_ancree_beton = non; construction_close = non; construction_delabree = non
- `red-b01` idéal C, lu NC NC NC · **contredit** : evenement : bris lu accident · en trop : auteur = famille
- `red-b02` idéal C, lu NC NC NC · **contredit** : evenement : bris lu accident · manque : type_dommage = felure · en trop : auteur = assure
- `g-q02` idéal ?, lu NC NC NC · en trop : evenement = vol; proprietaire = assure; simple_disparition = oui; vol_sur_personne = non · retiré sans appui : fermeture = aucune; sejour_temporaire = non; vol_sur_personne = non
- `g-h03` idéal C, lu ? ? ? · en trop : bien_a_l_origine_sinistre = oui
- `g-h05` idéal C, lu C NC ?
- `g2-i01` idéal ?, lu NC NC NC · en trop : auteur = tiers; effraction = oui; lieu = parties_communes; occupation_partielle = oui; proprietaire = assure; simple_disparition = non; violence = non; vol_sur_personne = non · retiré sans appui : auteur = tiers; fermeture = aucune; sejour_temporaire = non; vol_sur_personne = non
- `g2-i02` idéal C, lu C NC NC · **contredit** : effraction : non lu oui · manque : bien = objet_divers · en trop : auteur = tiers; fermeture = cle; proprietaire = assure; simple_disparition = non; type_dommage = rayure_ou_ecaillement; violence = non; vol_sur_personne = non · retiré sans appui : sejour_temporaire = non; serrure_surete = non; vol_sur_personne = non
- `g2-i03` idéal C, lu NC NC NC · en trop : cause_eau = infiltration_exterieure; type_dommage = moisissure
- `g2-i06` idéal ?, lu ? NC ? · en trop : periode_gel = oui; prevention_gel = non; travaux_batiment = aucun · retiré sans appui : prevention_gel = non; type_dommage = opacification_ou_perte_etancheite
- `g2-i16` idéal ?, lu NC NC NC · en trop : auteur = assure; bien = element_batiment; cause_eau = infiltration_exterieure; travaux_batiment = aucun
- `g2-p01` idéal C, lu NC NC NC · **contredit** : effraction : non lu oui · manque : absence = oui; bien = objet_divers · en trop : cles_a_proximite = non; fermeture = cle · retiré sans appui : cles_a_proximite = non
- `g2-p04` idéal NC, lu ? ? ? · **contredit** : bien : mazout lu citerne; evenement : vol lu mazout · en trop : auteur = tiers · retiré sans appui : auteur = tiers; bien_a_l_origine_sinistre = non; intentionnel = oui
- `g2-l03` idéal C, lu NC NC NC · manque : absence = non; bien = objet_divers · en trop : auteur = tiers; effraction = oui; fermeture = cle; portes_fermees = oui; proprietaire = assure; violence = non; vol_sur_personne = non · retiré sans appui : absence = non; effraction = oui; simple_disparition = non
- `g2-m02` idéal C, lu ? ? ? · en trop : alea_tempete = vent; cause_eau = infiltration_exterieure; construction_close = oui; travaux_batiment = aucun; type_dommage = bris · retiré sans appui : construction_delabree = non; periode_gel = non

### Contradictions sans effet sur la décision

- `bougie-01` : evenement : autre lu accident
- `bougie-03` : evenement : autre lu fumee
- `val-09` : evenement : autre lu fumee
- `red-b03` : evenement : bris lu accident
- `red-b04` : evenement : bris lu accident
- `red-b05` : evenement : bris lu accident
- `g-l03` : evenement : autre lu accident
- `g-l07` : evenement : autre lu accident
- `g2-i07` : vehicule_voie_publique : oui lu non

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 86% (84% – 88%) | 72% (71% – 72%) | **4.333 (3 – 5)** | **4.333 (4 – 5)** | 23% (22% – 24%) |

Instables : **13** sur 97 · rappel des clauses : 65% · rappel des questions : 72% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 215.3 s · par cas, un à la fois (10 cas) : médiane 2.95 s, 95e centile 4.29 s (lecture 2.84 s, décision 0.0 s) · en masse (quatre à la fois) : médiane 3.72 s, 95e centile 37.19 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 97 | 88% | 5 ⚠ | 4 |
| garantie : 1.4 | 2 | 100% | 0 | 0 |
| garantie : 2.1 | 13 | 92% | 1 ⚠ | 0 |
| garantie : 2.10 | 39 | 85% | 2 ⚠ | 2 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.12 | 1 | 100% | 0 | 0 |
| garantie : 2.2 | 6 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.5 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 4 | 100% | 0 | 0 |
| garantie : 2.7 | 16 | 88% | 1 ⚠ | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 7 | 57% | 1 ⚠ | 2 |
| garantie : 6.1 | 1 | 100% | 0 | 0 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 24 | 88% | 1 ⚠ | 2 |
| thème : info_manquante | 16 | 88% | 1 ⚠ | 0 |
| thème : langue | 11 | 91% | 0 | 1 |
| thème : multi | 8 | 100% | 0 | 0 |
| thème : piege | 55 | 82% | 5 ⚠ | 2 |
| thème : variante | 13 | 92% | 1 ⚠ | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `bougie-04` attendu NC, obtenu C C NC — Pendant mes vacances, une bougie laissée sur la table du jardin s'est enflammée et a brûlé la table et le salo… *(Vrai incendie, mais table et salon de jardin = contenu du jardin, exclu du contenu assuré (12/contenu). INCERTAIN défend)*
- **⚠ couvert à tort** `red-b06` attendu NC, obtenu C C C — La vitre de la fenêtre de la cuisine est rayée sur toute sa largeur. *(Exclusion 2.9 : les rayures et écaillements des vitres.)*
- **⚠ couvert à tort** `g-p03` attendu NC, obtenu C C C — Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune… *(Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct.)*
- **⚠ couvert à tort** `g2-i04` attendu ?, obtenu C C NC — Mes bijoux ont disparu de ma chambre après le passage du plombier. *(Une disparition n'est pas un vol établi (simple disparition exclue) ; et un vol par une personne autorisée à se trouver )*
- **⚠ couvert à tort** `g2-i08` attendu ?, obtenu ? C ? — On m'a volé mon sac au restaurant. *(Hors du bâtiment, seul le vol commis sur l'assuré avec violences ou menaces est couvert : à préciser.)*
- **⚠ couvert à tort** `g2-p08` attendu NC, obtenu C NC C — Le bain à bulles installé sur ma terrasse a fui et l'eau a abîmé le canapé du salon. *(Exclusion 2.7 : l'écoulement d'eau des piscines et des bains à bulles extérieurs.)*
- `velo-06` attendu NC, obtenu NC ? ? — Mon vélo était attaché à un arceau dans la rue avec un antivol. L'antivol a été coupé et le vélo volé. *(Vol dans la rue, sans violence : hors du bâtiment, et ce n'est pas un « vol commis sur l'assuré … suite à violences ».)*
- `val-03` attendu NC, obtenu NC ? NC — Des amis que j'hébergeais pour le week-end se sont fait voler leur ordinateur lors d'un cambriolage de mon app… *(Exclusion 2.10 : le vol des biens appartenant à des hôtes (alors que la définition du contenu les inclut : piège).)*
- `val-05` attendu NC, obtenu ? NC NC — Au retour de vacances, je ne retrouve plus ma montre de valeur. Aucune trace de passage ni d'effraction dans l… *(2.10 : « le vol du contenu situé dans le bâtiment sauf la simple disparition ».)*
- `val-11` attendu NC, obtenu ? ? ? — Pendant un orage, la pluie s'est infiltrée par la fenêtre mal jointée de ma chambre et a abîmé le mur et la mo… *(Exclusion 2.7 : une infiltration par les fenêtres, autre que celle due à une fuite des installations hydrauliques extéri)*
- `val-13` attendu C, obtenu ? C C — La tempête a arraché des tuiles de l'immeuble et la pluie est entrée dans mon salon, abîmant le plafond et le … *(2.2 : les dommages matériels directement causés par la tempête. Garantie non écrite en règles : test de l'aveu de limite)*
- `red-t03` attendu NC, obtenu NC NC ? — Le poids de la neige a fait s'effondrer mon carport en bois, simplement posé sur des plots, sans ancrage en bé… *(Exclusion 2.2 : annexes faisant partie du bâtiment non fixées au sol par un ancrage en béton.)*
- `red-b01` attendu C, obtenu NC NC NC — Mon fils a cassé la vitre de la porte-fenêtre du salon avec un ballon. *(2.9 : le bris de vitres.)*
- `red-b02` attendu C, obtenu NC NC NC — J'ai fait tomber une casserole sur ma table de cuisson vitrocéramique, qui s'est fendue. *(2.9 : les tables de cuisson en vitrocéramique sont assimilées aux vitres.)*
- `g-h02` attendu C, obtenu ? C ? — Une panne de courant de dix heures a fait décongeler tout le contenu de mon congélateur. *(2.6 : denrées décongelées après 6 heures d'arrêt (limite 500 EUR). Non traduite.)*
- `g-h05` attendu C, obtenu C NC ? — Les égouts publics ont refoulé pendant un gros orage et l'eau sale a envahi la salle de bain. *(2.3 : le refoulement d'égouts publics est une catastrophe naturelle couverte ; 2.7 l'exclut. Non traduite.)*
- `g2-i01` attendu ?, obtenu NC NC NC — Mon vélo a été volé dans le local de mon immeuble. *(« Le local de mon immeuble » : local commun (vol exclu dans les parties communes) ou cave privative (couverte si serrure)*
- `g2-i02` attendu ?, obtenu ? NC NC — On a cambriolé mon appartement pendant le week-end où j'étais absent. La serrure porte des rayures, mais la po… *(Des traces sans réparation nécessaire ne sont pas une effraction (définition). Sans effraction, l'obligation de fermer à)*
- `g2-i11` attendu ?, obtenu C ? C — Après le gros coup de vent d'hier, des tuiles de l'immeuble sont tombées sur mon balcon et l'ont abîmé. *(La tempête suppose un vent d'au moins 80 km/h ou des dégâts aux biens voisins (définition) : non précisé. Garantie 2.2 n)*
- `g2-p01` attendu C, obtenu NC NC NC — Pendant mes vacances, des cambrioleurs ont ouvert ma porte sans la casser : il n'y a que des traces de tournev… *(Pas d'effraction au sens du contrat, mais la porte était fermée à clé : l'obligation est respectée, le vol dans le bâtim)*
- `g2-p04` attendu NC, obtenu ? ? ? — On a siphonné le fioul de la cuve de chauffage, dans ma cave. *(Exclusion 2.10 : le vol de mazout de chauffage.)*
- `g2-l03` attendu C, obtenu NC NC NC — Je n'étais pas absente et la porte n'était pas ouverte : quelqu'un est entré pendant que je dormais et a pris … *(Vol du contenu dans le bâtiment ; l'obligation de fermer à clé ne vaut qu'en cas d'absence.)*
