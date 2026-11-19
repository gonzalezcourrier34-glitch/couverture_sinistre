# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-19T15:40:08 · golden set v12 (97 cas, empreinte `0534a0545f66a07d`) · cas validés par l'auteur : 0 sur 97


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 1.9 | ✓ |
| lecture | decisions_changees | ≤ 2 | 22.33 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 8 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 15 | ✗ |
| chaine | faux_couverts | ≤ 0 | 4 | ✗ |
| chaine | faux_refus | ≤ 1 | 2 | ✗ |
| chaine | exactitude | ≥ 0.85 | 0.863 | ✓ |
| chaine | instables | ≤ 3 | 11 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 0.611 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 21.15 | ✗ |

## Depuis le banc précédent de même configuration (2026-11-19T15:22:10, mistral:mistral-small-latest · verifiee)

- lecture · rappel_faits : 0.891 → 0.892
- chaine · exactitude : 0.869 → 0.863
- chaine · exactitude_stricte : 0.732 → 0.736
- chaine · faux_couverts : 3.667 → 4
- chaine · faux_refus : 3 → 2

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

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **22.33** par exécution, dont **8** cas vers un couvert à tort.

Rappel des faits idéaux : 89% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 15 cas · faits vagues : 0 cas · faits en trop : 87 cas · faits retirés (sans appui ou non dits) : 77 cas

### La lecture change la décision

- **⚠ vers couvert** `bougie-04` idéal NC, lu NC NC C · **contredit** : lieu : jardin lu logement/terrasse · manque : absence = oui · en trop : auteur = assure; cause_dommage = autre; intentionnel = non; travaux_batiment = aucun; travaux_vitres = aucun; type_dommage = bris · retiré sans appui : chaleur_sans_feu = non; effraction = non; manque_entretien = non
- **⚠ vers couvert** `val-09` idéal NC, lu C NC C · **contredit** : bien : objet_divers lu mobilier; evenement : autre lu electricite; evenement : autre lu fumee · manque : embrasement = non; flammes = non · en trop : chaleur_sans_feu = oui; proprietaire = assure; usage_professionnel = non · retiré sans appui : embrasement = non; flammes = non
- **⚠ vers couvert** `red-b06` idéal NC, lu C C C · **contredit** : evenement : bris lu vandalisme · manque : type_dommage = rayure_ou_ecaillement · retiré sans appui : auteur = tiers; effraction = non; intentionnel = oui; manque_entretien = non; sejour_temporaire = non
- **⚠ vers couvert** `g-p03` idéal ?, lu C C C · **contredit** : bien : objet_divers lu cles · manque : portes_fermees = oui · en trop : fermeture = cle · retiré sans appui : fermeture = cle; simple_disparition = non
- **⚠ vers couvert** `g-h02` idéal ?, lu C C ? · en trop : cause_perte_alimentaire = coupure_soudaine_reseau; chaleur_sans_feu = oui; proprietaire = assure; usage_professionnel = non · retiré sans appui : cause_perte_alimentaire = coupure_soudaine_reseau; embrasement = non; flammes = non
- **⚠ vers couvert** `g2-i08` idéal ?, lu NC C NC · **contredit** : lieu : autre_batiment lu voie_publique · en trop : auteur = tiers; laisse_sans_surveillance = oui; proprietaire = assure; sejour_temporaire = oui; simple_disparition = non; violence = non; violence = oui; vol_sur_personne = oui · retiré sans appui : effraction = non; fermeture = aucune; simple_disparition = non
- **⚠ vers couvert** `g2-i11` idéal ?, lu ? C ? · **contredit** : lieu : terrasse lu logement · en trop : travaux_batiment = aucun; travaux_vitres = aucun; type_dommage = bris · retiré sans appui : effraction = non; travaux_batiment = aucun; type_dommage = bris
- **⚠ vers couvert** `g2-p08` idéal NC, lu C C C · **contredit** : cause_eau : piscine_exterieure lu debordement_aquarium · en trop : travaux_batiment = aucun
- `velo-03` idéal NC, lu ? ? ? · **contredit** : fermeture : cadenas lu cle · manque : vol_sur_personne = non · en trop : proprietaire = assure; simple_disparition = non; violence = non · retiré sans appui : sejour_temporaire = non; serrure_surete = non; simple_disparition = non; vol_sur_personne = non
- `val-10` idéal NC, lu ? ? ? · manque : prevention_gel = non · en trop : periode_gel = oui; travaux_batiment = aucun · retiré sans appui : prevention_gel = non
- `val-11` idéal NC, lu ? ? ? · en trop : alea_tempete = vent; auteur = assure; intentionnel = non; periode_gel = non; travaux_batiment = aucun · retiré sans appui : alea_tempete = vent
- `val-13` idéal C, lu C ? ? · **contredit** : cause_eau : infiltration_toiture lu infiltration_exterieure · manque : cause_eau = infiltration_toiture · en trop : alea_tempete = vent; construction_close = oui; residence_principale = oui · retiré sans appui : construction_close = oui
- `red-t03` idéal NC, lu ? NC NC · manque : annexe_ancree_beton = non; construction_close = non · retiré sans appui : annexe_ancree_beton = non; construction_close = non
- `red-b01` idéal C, lu NC NC NC · en trop : auteur = famille; effraction = non; intentionnel = oui; manque_entretien = non; proprietaire = assure; travaux_batiment = aucun; travaux_vitres = aucun; type_dommage = bris; vitre_placee = oui · retiré sans appui : effraction = non
- `g-q01` idéal ?, lu NC NC NC · en trop : auteur = tiers; effraction = oui; fermeture = aucune; proprietaire = assure; simple_disparition = non; violence = non; vol_sur_personne = non · retiré sans appui : sejour_temporaire = non; simple_disparition = non; vol_sur_personne = non
- `g-q02` idéal ?, lu NC NC NC · en trop : evenement = vol; fermeture = aucune; proprietaire = assure; simple_disparition = oui; vol_sur_personne = non · retiré sans appui : fermeture = aucune; sejour_temporaire = non; vol_sur_personne = non
- `g-h03` idéal C, lu ? ? ? · en trop : bien_a_l_origine_sinistre = oui
- `g-h05` idéal C, lu ? ? ?
- `g2-i01` idéal ?, lu NC NC NC · en trop : auteur = tiers; effraction = oui; fermeture = aucune; lieu = parties_communes; occupation_partielle = oui; proprietaire = assure; simple_disparition = non; vol_sur_personne = non · retiré sans appui : fermeture = aucune; sejour_temporaire = non
- `g2-i02` idéal C, lu NC NC NC · **contredit** : effraction : non lu oui · manque : bien = objet_divers · en trop : auteur = tiers; fermeture = cle; proprietaire = assure; simple_disparition = non; type_dommage = rayure_ou_ecaillement; violence = non; vol_sur_personne = non · retiré sans appui : sejour_temporaire = non; serrure_surete = non; simple_disparition = non; vol_sur_personne = non
- `g2-i03` idéal C, lu NC NC NC · en trop : cause_eau = infiltration_exterieure
- `g2-i04` idéal ?, lu NC NC NC · en trop : auteur = tiers; effraction = non; evenement = vol; proprietaire = assure; sejour_temporaire = non; simple_disparition = oui; vol_sur_personne = non · retiré sans appui : fermeture = aucune
- `g2-i16` idéal ?, lu NC NC NC · en trop : auteur = assure; bien = element_batiment; cause_eau = infiltration_exterieure; intentionnel = non; travaux_batiment = aucun
- `g2-p04` idéal NC, lu ? ? ? · **contredit** : bien : mazout lu citerne; evenement : vol lu mazout · retiré sans appui : auteur = tiers; bien_a_l_origine_sinistre = non; intentionnel = oui
- `g2-l03` idéal C, lu NC NC NC · manque : absence = non; bien = objet_divers · en trop : auteur = tiers; fermeture = cle; portes_fermees = oui; proprietaire = assure; simple_disparition = non; violence = non; vol_sur_personne = non · retiré sans appui : absence = non; effraction = oui; fermeture = cle; sejour_temporaire = non; simple_disparition = non
- `g2-m02` idéal C, lu C C ? · en trop : alea_tempete = vent; cause_eau = infiltration_exterieure; type_dommage = bris · retiré sans appui : effraction = non

### Contradictions sans effet sur la décision

- `bougie-01` : evenement : autre lu degat_eaux
- `bougie-03` : evenement : autre lu fumee
- `g-l07` : evenement : autre lu bris
- `g2-p01` : bien : objet_divers lu element_batiment; effraction : non lu oui

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 86% (86% – 87%) | 74% (72% – 75%) | **4 (3 – 5)** | **2 (2 – 2)** | 21% (20% – 23%) |

Instables : **11** sur 97 · rappel des clauses : 66% · rappel des questions : 61% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 208.7 s · par cas, un à la fois (10 cas) : médiane 3.68 s, 95e centile 21.15 s (lecture 2.8 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.68 s, 95e centile 37.04 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 97 | 87% | 4 ⚠ | 2 |
| garantie : 1.4 | 2 | 100% | 0 | 0 |
| garantie : 2.1 | 13 | 92% | 1 ⚠ | 0 |
| garantie : 2.10 | 39 | 82% | 1 ⚠ | 1 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.12 | 1 | 100% | 0 | 0 |
| garantie : 2.2 | 6 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.5 | 1 | 0% | 0 | 1 |
| garantie : 2.6 | 4 | 100% | 0 | 0 |
| garantie : 2.7 | 16 | 88% | 1 ⚠ | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 7 | 71% | 1 ⚠ | 0 |
| garantie : 6.1 | 1 | 100% | 0 | 0 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 24 | 88% | 1 ⚠ | 1 |
| thème : info_manquante | 16 | 81% | 0 | 0 |
| thème : langue | 11 | 91% | 0 | 1 |
| thème : multi | 8 | 100% | 0 | 0 |
| thème : piege | 55 | 86% | 4 ⚠ | 0 |
| thème : variante | 13 | 92% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `bougie-04` attendu NC, obtenu NC NC C — Pendant mes vacances, une bougie laissée sur la table du jardin s'est enflammée et a brûlé la table et le salo… *(Vrai incendie, mais table et salon de jardin = contenu du jardin, exclu du contenu assuré (12/contenu). INCERTAIN défend)*
- **⚠ couvert à tort** `val-09` attendu NC, obtenu C NC C — Mon fer à repasser, laissé à plat sur la planche, a brûlé la housse et laissé une marque sur le tissu, sans fl… *(Définition de l'incendie : les brûlures et le contact d'une source de chaleur sans embrasement ne sont pas un incendie.)*
- **⚠ couvert à tort** `red-b06` attendu NC, obtenu C C C — La vitre de la fenêtre de la cuisine est rayée sur toute sa largeur. *(Exclusion 2.9 : les rayures et écaillements des vitres.)*
- **⚠ couvert à tort** `g-p03` attendu NC, obtenu C C C — Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune… *(Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct.)*
- **⚠ couvert à tort** `g2-p08` attendu NC, obtenu C C C — Le bain à bulles installé sur ma terrasse a fui et l'eau a abîmé le canapé du salon. *(Exclusion 2.7 : l'écoulement d'eau des piscines et des bains à bulles extérieurs.)*
- `velo-06` attendu NC, obtenu ? ? NC — Mon vélo était attaché à un arceau dans la rue avec un antivol. L'antivol a été coupé et le vélo volé. *(Vol dans la rue, sans violence : hors du bâtiment, et ce n'est pas un « vol commis sur l'assuré … suite à violences ».)*
- `val-11` attendu NC, obtenu ? ? ? — Pendant un orage, la pluie s'est infiltrée par la fenêtre mal jointée de ma chambre et a abîmé le mur et la mo… *(Exclusion 2.7 : une infiltration par les fenêtres, autre que celle due à une fuite des installations hydrauliques extéri)*
- `val-13` attendu C, obtenu C ? ? — La tempête a arraché des tuiles de l'immeuble et la pluie est entrée dans mon salon, abîmant le plafond et le … *(2.2 : les dommages matériels directement causés par la tempête. Garantie non écrite en règles : test de l'aveu de limite)*
- `red-t03` attendu NC, obtenu ? NC NC — Le poids de la neige a fait s'effondrer mon carport en bois, simplement posé sur des plots, sans ancrage en bé… *(Exclusion 2.2 : annexes faisant partie du bâtiment non fixées au sol par un ancrage en béton.)*
- `red-b01` attendu C, obtenu ? ? ? — Mon fils a cassé la vitre de la porte-fenêtre du salon avec un ballon. *(2.9 : le bris de vitres.)*
- `red-b05` attendu NC, obtenu ? ? NC — Le grand miroir que je venais d'acheter, encore dans son carton et pas encore accroché, s'est brisé quand je l… *(Exclusion 2.9 : les dommages aux vitres et biens assimilés non placés.)*
- `g-q01` attendu ?, obtenu NC NC NC — On m'a volé mon vélo dans ma cave. *(La cave n'est couverte que fermée par une serrure de sûreté : il faut le demander.)*
- `g-h02` attendu C, obtenu C C ? — Une panne de courant de dix heures a fait décongeler tout le contenu de mon congélateur. *(2.6 : denrées décongelées après 6 heures d'arrêt (limite 500 EUR). Non traduite.)*
- `g2-i01` attendu ?, obtenu NC NC NC — Mon vélo a été volé dans le local de mon immeuble. *(« Le local de mon immeuble » : local commun (vol exclu dans les parties communes) ou cave privative (couverte si serrure)*
- `g2-i02` attendu ?, obtenu NC NC NC — On a cambriolé mon appartement pendant le week-end où j'étais absent. La serrure porte des rayures, mais la po… *(Des traces sans réparation nécessaire ne sont pas une effraction (définition). Sans effraction, l'obligation de fermer à)*
- `g2-i03` attendu ?, obtenu ? NC NC — Une tache d'humidité est apparue au plafond de ma chambre, juste sous la salle de bain du voisin du dessus. *(2.7 couvre l'ensemble des dégâts des eaux, mais la condensation et certaines infiltrations sont exclues : la cause est à)*
- `g2-i04` attendu ?, obtenu ? NC NC — Mes bijoux ont disparu de ma chambre après le passage du plombier. *(Une disparition n'est pas un vol établi (simple disparition exclue) ; et un vol par une personne autorisée à se trouver )*
- `g2-i11` attendu ?, obtenu ? C ? — Après le gros coup de vent d'hier, des tuiles de l'immeuble sont tombées sur mon balcon et l'ont abîmé. *(La tempête suppose un vent d'au moins 80 km/h ou des dégâts aux biens voisins (définition) : non précisé. Garantie 2.2 n)*
- `g2-i16` attendu C, obtenu NC NC NC — De l'eau de mon appartement s'est infiltrée chez le voisin du dessous, qui me demande de payer ses réparations… *(2.5 : responsabilité civile du fait du bâtiment et du contenu envers les tiers. Garantie non traduite.)*
- `g2-p04` attendu NC, obtenu ? ? ? — On a siphonné le fioul de la cuve de chauffage, dans ma cave. *(Exclusion 2.10 : le vol de mazout de chauffage.)*
- `g2-l03` attendu C, obtenu NC NC NC — Je n'étais pas absente et la porte n'était pas ouverte : quelqu'un est entré pendant que je dormais et a pris … *(Vol du contenu dans le bâtiment ; l'obligation de fermer à clé ne vaut qu'en cas d'absence.)*
- `g2-m02` attendu C, obtenu C C ? — La tempête a cassé la fenêtre du salon et la pluie a abîmé le canapé. *(La vitre est couverte par le bris de vitrages (2.9) ; le canapé relève de la tempête (2.2), non traduite.)*
