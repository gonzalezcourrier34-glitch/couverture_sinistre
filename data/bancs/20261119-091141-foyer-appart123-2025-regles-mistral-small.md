# Banc d'essai — foyer-appart123-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-19T09:00:31 · golden set v8 (97 cas, empreinte `68cb3c13ea714708`) · cas validés par l'auteur : 0 sur 97


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 1.9 | ✓ |
| lecture | decisions_changees | ≤ 2 | 22 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 8 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 26 | ✗ |
| chaine | faux_couverts | ≤ 0 | 4.333 | ✗ |
| chaine | faux_refus | ≤ 1 | 0.333 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.893 | ✓ |
| chaine | instables | ≤ 3 | 10 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 0.727 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 39.01 | ✗ |

## Depuis le banc précédent (2026-11-18T22:20:56)

- regles · exactitude_stricte : 0.814 → 0.918
- lecture · rappel_faits : 0.868 → 0.855
- chaine · exactitude : 0.897 → 0.893
- chaine · exactitude_stricte : 0.67 → 0.763
- chaine · faux_couverts : 1.333 → 4.333
- chaine · faux_refus : 1 → 0.333

## Couche 1 — règles seules (faits idéaux, sans modèle)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 100% | 92% | **0** | **0** | 16% |

Rappel des questions attendues : 100% · questions posées par réponse « incertain » : 1.9

Raisonnement par hypothèses : incertains tranchés par une ou deux questions : 67% · questions inutiles retirées : 29

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

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **22** par exécution, dont **8** cas vers un couvert à tort.

Rappel des faits idéaux : 86% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 26 cas · faits vagues : 0 cas · faits en trop : 74 cas · faits retirés (sans appui ou non dits) : 73 cas

### La lecture change la décision

- **⚠ vers couvert** `bougie-04` idéal NC, lu NC C C · **contredit** : lieu : jardin lu logement/terrasse · manque : absence = oui · en trop : auteur = assure; cause_dommage = autre; intentionnel = non; type_dommage = bris · retiré sans appui : chaleur_sans_feu = non; effraction = non; intentionnel = non; manque_entretien = non; travaux_batiment = aucun; travaux_vitres = aucun
- **⚠ vers couvert** `val-03` idéal NC, lu C NC C · **contredit** : bien : electronique lu appareil_informatique; bien : electronique lu appareil_informatique/chassis · manque : vol_sur_personne = non · en trop : auteur = tiers; violence = non · retiré sans appui : auteur = tiers; fermeture = aucune; portes_fermees = non
- **⚠ vers couvert** `red-b06` idéal NC, lu C C C · **contredit** : evenement : bris lu vandalisme · manque : type_dommage = rayure_ou_ecaillement · en trop : effraction = non · retiré sans appui : auteur = tiers; effraction = non; fenetres_fermees = non; fermeture = aucune; intentionnel = oui; manque_entretien = non
- **⚠ vers couvert** `g-p03` idéal ?, lu C C C · **contredit** : bien : objet_divers lu cles · manque : absence = oui; portes_fermees = oui · en trop : fermeture = cle · retiré sans appui : fermeture = cle
- **⚠ vers couvert** `g2-i04` idéal ?, lu C C C · en trop : auteur = tiers; evenement = vol; proprietaire = assure; simple_disparition = non · retiré sans appui : auteur = tiers; fermeture = aucune; simple_disparition = non; vol_sur_personne = non
- **⚠ vers couvert** `g2-i11` idéal ?, lu C C C · **contredit** : lieu : terrasse lu logement · retiré sans appui : vent_dommages_voisins = oui
- **⚠ vers couvert** `g2-i16` idéal ?, lu NC NC C · en trop : auteur = assure; bien = element_batiment; cause_eau = infiltration_exterieure · retiré sans appui : intentionnel = non
- **⚠ vers couvert** `g2-p04` idéal NC, lu ? ? C · **contredit** : bien : mazout lu citerne; evenement : vol lu mazout · en trop : auteur = tiers; bien_a_l_origine_sinistre = non · retiré sans appui : auteur = tiers; bien_a_l_origine_sinistre = non; intentionnel = oui
- `velo-03` idéal NC, lu ? NC NC · **contredit** : fermeture : cadenas lu cle · manque : vol_sur_personne = non · en trop : portes_fermees = oui; proprietaire = assure · retiré sans appui : auteur = tiers; serrure_surete = non; simple_disparition = non; violence = non; vol_sur_personne = non
- `velo-06` idéal NC, lu NC NC ? · manque : fermeture = cadenas; violence = non; vol_sur_personne = non · en trop : auteur = tiers; effraction = oui; proprietaire = assure · retiré sans appui : auteur = tiers; fermeture = aucune; simple_disparition = non; violence = non; vol_sur_personne = non
- `val-01` idéal ?, lu NC NC NC · **contredit** : bien : electronique lu appareil_informatique · manque : fenetres_fermees = non · en trop : violence = non · retiré sans appui : fenetres_fermees = non; fermeture = aucune
- `val-10` idéal NC, lu ? ? ? · manque : prevention_gel = non · retiré sans appui : chaleur_sans_feu = non; embrasement = non; flammes = non; prevention_gel = non
- `val-11` idéal NC, lu ? ? ? · en trop : alea_tempete = vent
- `val-12` idéal C, lu C NC C · **contredit** : cause_eau : fuite_installation lu debordement_recipient · en trop : absence = non; auteur = assure; intentionnel = non
- `val-13` idéal C, lu C C ? · **contredit** : cause_eau : infiltration_toiture lu infiltration_exterieure · manque : cause_eau = infiltration_toiture · en trop : alea_tempete = vent; construction_close = oui
- `red-t03` idéal NC, lu NC ? ? · manque : annexe_ancree_beton = non; construction_close = non · retiré sans appui : annexe_ancree_beton = non; construction_close = non
- `red-b01` idéal C, lu NC NC NC · en trop : auteur = famille; intentionnel = oui; type_dommage = bris; vitre_placee = oui · retiré sans appui : effraction = non; manque_entretien = non; travaux_batiment = aucun; travaux_vitres = aucun
- `red-b02` idéal C, lu NC C NC · **contredit** : type_dommage : felure lu bris · en trop : auteur = assure; cause_dommage = autre; effraction = non; intentionnel = non; intentionnel = oui; manque_entretien = non; travaux_batiment = aucun; travaux_vitres = aucun · retiré sans appui : auteur = assure; effraction = non; travaux_batiment = aucun; travaux_vitres = aucun
- `g-q02` idéal ?, lu NC NC NC · **contredit** : bien : electronique lu appareil_informatique · en trop : evenement = vol; proprietaire = assure; simple_disparition = oui; vol_sur_personne = non · retiré sans appui : fermeture = aucune
- `g-h01` idéal C, lu ? ? ? · **contredit** : bien : electronique lu appareil_informatique/denrees_alimentaires · retiré sans appui : cause_perte_alimentaire = coupure_soudaine_reseau
- `g2-i01` idéal ?, lu NC NC NC · en trop : lieu = parties_communes; occupation_partielle = oui; proprietaire = assure; simple_disparition = non · retiré sans appui : auteur = tiers; fermeture = aucune; simple_disparition = non; vol_sur_personne = non
- `g2-i02` idéal C, lu ? C ? · **contredit** : bien : objet_divers lu cles; effraction : non lu oui · manque : bien = objet_divers · en trop : auteur = tiers; fermeture = cle; occupation_partielle = oui; portes_fermees = oui; proprietaire = assure; serrure_surete = non · retiré sans appui : batiment_vacant_90j = non; manque_entretien = non; serrure_surete = non; simple_disparition = non; violence = non; vol_sur_personne = non
- `g2-i03` idéal C, lu NC NC NC · en trop : cause_eau = infiltration_exterieure
- `g2-p01` idéal C, lu C C ? · **contredit** : bien : objet_divers lu cles; effraction : non lu oui · manque : absence = oui; bien = objet_divers; portes_fermees = oui · en trop : fermeture = cle
- `g2-i07` idéal NC, lu ? ? ? · **contredit** : bien : electronique lu appareil_informatique · manque : lieu = voie_publique; vol_sur_personne = non · en trop : auteur = tiers; effraction = oui; proprietaire = assure; simple_disparition = non; violence = non · retiré sans appui : auteur = tiers; fermeture = aucune; vol_sur_personne = non
- `g2-l03` idéal C, lu ? ? ? · manque : absence = non; bien = objet_divers · en trop : auteur = tiers; effraction = oui; fermeture = cle; portes_fermees = oui; proprietaire = assure; vol_sur_personne = non · retiré sans appui : absence = non; fermeture = cle; simple_disparition = non; violence = non
- `g2-m02` idéal C, lu ? ? ? · en trop : alea_tempete = vent; cause_eau = infiltration_exterieure

### Contradictions sans effet sur la décision

- `bougie-01` : evenement : autre lu degat_eaux
- `bougie-03` : evenement : autre lu fumee
- `autre-01` : bien : electronique lu appareil_informatique
- `val-06` : bien : electronique lu appareil_informatique
- `val-07` : bien : electronique/valeurs lu appareil_informatique
- `val-09` : bien : objet_divers lu mobilier; evenement : autre lu fumee
- `g-l03` : lieu : jardin lu terrasse
- `g-l07` : evenement : autre lu bris
- `g-h02` : bien : objet_divers lu appareil_informatique/denrees_alimentaires; bien : objet_divers lu denrees_alimentaires
- `g2-i08` : lieu : autre_batiment lu voie_publique

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 89% (88% – 91%) | 76% (74% – 77%) | **4.333 (4 – 5)** | **0.333 (0 – 1)** | 23% (22% – 25%) |

Instables : **10** sur 97 · rappel des clauses : 71% · rappel des questions : 73% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 196.7 s · par cas, un à la fois (10 cas) : médiane 3.58 s, 95e centile 39.01 s (lecture 3.04 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.23 s, 95e centile 37.8 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 97 | 91% | 4 ⚠ | 0 |
| garantie : 1.4 | 2 | 100% | 0 | 0 |
| garantie : 2.1 | 13 | 100% | 0 | 0 |
| garantie : 2.10 | 40 | 85% | 3 ⚠ | 0 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.12 | 1 | 100% | 0 | 0 |
| garantie : 2.2 | 6 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.5 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 4 | 100% | 0 | 0 |
| garantie : 2.7 | 16 | 94% | 0 | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 7 | 71% | 1 ⚠ | 0 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 24 | 92% | 1 ⚠ | 0 |
| thème : info_manquante | 16 | 88% | 1 ⚠ | 0 |
| thème : langue | 11 | 100% | 0 | 0 |
| thème : multi | 8 | 100% | 0 | 0 |
| thème : piege | 55 | 86% | 4 ⚠ | 0 |
| thème : variante | 13 | 100% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `bougie-04` attendu NC, obtenu NC C C — Pendant mes vacances, une bougie laissée sur la table du jardin s'est enflammée et a brûlé la table et le salo… *(Vrai incendie, mais table et salon de jardin = contenu du jardin, exclu du contenu assuré (12/contenu). INCERTAIN défend)*
- **⚠ couvert à tort** `val-03` attendu NC, obtenu C NC C — Des amis que j'hébergeais pour le week-end se sont fait voler leur ordinateur lors d'un cambriolage de mon app… *(Exclusion 2.10 : le vol des biens appartenant à des hôtes (alors que la définition du contenu les inclut : piège).)*
- **⚠ couvert à tort** `red-b06` attendu NC, obtenu C C C — La vitre de la fenêtre de la cuisine est rayée sur toute sa largeur. *(Exclusion 2.9 : les rayures et écaillements des vitres.)*
- **⚠ couvert à tort** `g-p03` attendu NC, obtenu C C C — Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune… *(Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct.)*
- **⚠ couvert à tort** `g2-i04` attendu ?, obtenu C C C — Mes bijoux ont disparu de ma chambre après le passage du plombier. *(Une disparition n'est pas un vol établi (simple disparition exclue) ; et un vol par une personne autorisée à se trouver )*
- `velo-03` attendu NC, obtenu ? NC NC — Mon vélo a été volé dans ma cave privative, fermée à clé. Le cadenas de la porte a été forcé. *(Cave en immeuble à appartements : vol couvert à 1 000 EUR « si ces locaux sont fermés avec une serrure de sûreté » (2.10)*
- `velo-06` attendu NC, obtenu NC NC ? — Mon vélo était attaché à un arceau dans la rue avec un antivol. L'antivol a été coupé et le vélo volé. *(Vol dans la rue, sans violence : hors du bâtiment, et ce n'est pas un « vol commis sur l'assuré … suite à violences ».)*
- `val-11` attendu NC, obtenu ? ? ? — Pendant un orage, la pluie s'est infiltrée par la fenêtre mal jointée de ma chambre et a abîmé le mur et la mo… *(Exclusion 2.7 : une infiltration par les fenêtres, autre que celle due à une fuite des installations hydrauliques extéri)*
- `val-12` attendu C, obtenu C NC C — Ma baignoire a débordé pendant que j'étais au téléphone ; l'eau a abîmé mon parquet. *(2.7 couvre l'ensemble des dégâts des eaux ; l'exclusion du récipient vise un récipient NON relié à l'installation hydrau)*
- `val-13` attendu C, obtenu C C ? — La tempête a arraché des tuiles de l'immeuble et la pluie est entrée dans mon salon, abîmant le plafond et le … *(2.2 : les dommages matériels directement causés par la tempête. Garantie non écrite en règles : test de l'aveu de limite)*
- `red-t03` attendu NC, obtenu NC ? ? — Le poids de la neige a fait s'effondrer mon carport en bois, simplement posé sur des plots, sans ancrage en bé… *(Exclusion 2.2 : annexes faisant partie du bâtiment non fixées au sol par un ancrage en béton.)*
- `red-b01` attendu C, obtenu ? ? ? — Mon fils a cassé la vitre de la porte-fenêtre du salon avec un ballon. *(2.9 : le bris de vitres.)*
- `red-b02` attendu C, obtenu ? C ? — J'ai fait tomber une casserole sur ma table de cuisson vitrocéramique, qui s'est fendue. *(2.9 : les tables de cuisson en vitrocéramique sont assimilées aux vitres.)*
- `g2-i01` attendu ?, obtenu NC NC NC — Mon vélo a été volé dans le local de mon immeuble. *(« Le local de mon immeuble » : local commun (vol exclu dans les parties communes) ou cave privative (couverte si serrure)*
- `g2-i16` attendu C, obtenu ? ? C — De l'eau de mon appartement s'est infiltrée chez le voisin du dessous, qui me demande de payer ses réparations… *(2.5 : responsabilité civile du fait du bâtiment et du contenu envers les tiers. Garantie non traduite.)*
- `g2-p01` attendu C, obtenu C C ? — Pendant mes vacances, des cambrioleurs ont ouvert ma porte sans la casser : il n'y a que des traces de tournev… *(Pas d'effraction au sens du contrat, mais la porte était fermée à clé : l'obligation est respectée, le vol dans le bâtim)*
- `g2-i07` attendu NC, obtenu ? ? ? — Mon ordinateur portable a été volé dans ma voiture, garée devant chez moi. *(La voiture n'est pas le bâtiment, et ce n'est pas un vol commis sur l'assuré avec violences.)*
- `g2-p04` attendu NC, obtenu ? ? ? — On a siphonné le fioul de la cuve de chauffage, dans ma cave. *(Exclusion 2.10 : le vol de mazout de chauffage.)*
