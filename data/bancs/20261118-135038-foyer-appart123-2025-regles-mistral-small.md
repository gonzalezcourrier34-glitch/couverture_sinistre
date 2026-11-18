# Banc d'essai — foyer-appart123-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (deux temps)

2026-11-18T13:43:42 · golden set v6 (97 cas, empreinte `0b83f83b91580639`) · cas validés par l'auteur : 0 sur 97


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 0.8 | ✓ |
| lecture | decisions_changees | ≤ 2 | 21.33 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 6 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 19 | ✗ |
| chaine | faux_couverts | ≤ 0 | 3.333 | ✗ |
| chaine | faux_refus | ≤ 1 | 2.667 | ✗ |
| chaine | exactitude | ≥ 0.85 | 0.849 | ✗ |
| chaine | instables | ≤ 3 | 9 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 0.394 | ✗ |

## Depuis le banc précédent (2026-11-18T13:30:00)

- lecture · rappel_faits : 0.914 → 0.895
- chaine · exactitude : 0.863 → 0.849
- chaine · exactitude_stricte : 0.643 → 0.636
- chaine · faux_couverts : 3 → 3.333
- chaine · faux_refus : 2 → 2.667

## Couche 1 — règles seules (faits idéaux, sans modèle)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 100% | 80% | **0** | **0** | 25% |

Rappel des questions attendues : 100% · questions posées par réponse « incertain » : 0.8

Raisonnement par hypothèses : incertains tranchés par une ou deux questions : 21% · questions inutiles retirées : 16

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

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **21.33** par exécution, dont **6** cas vers un couvert à tort.

Rappel des faits idéaux : 90% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 19 cas · faits vagues : 1 cas · faits en trop : 80 cas · faits retirés faute d'appui : 0 cas

### La lecture change la décision

- **⚠ vers couvert** `bougie-04` idéal NC, lu C NC C · manque : absence = oui · en trop : auteur = assure; chaleur_sans_feu = non; intentionnel = non
- **⚠ vers couvert** `val-03` idéal NC, lu C C C · manque : proprietaire = hote; vol_sur_personne = non · en trop : auteur = tiers; fermeture = aucune
- **⚠ vers couvert** `g-p03` idéal ?, lu C C C · **contredit** : bien : objet_divers lu cles · manque : portes_fermees = oui · en trop : fermeture = cle
- **⚠ vers couvert** `g2-i04` idéal ?, lu C C NC · en trop : auteur = tiers; evenement = vol; simple_disparition = non; simple_disparition = oui; vol_sur_personne = non
- **⚠ vers couvert** `g2-i11` idéal ?, lu C ? ? · **contredit** : lieu : terrasse lu logement · en trop : effraction = non; travaux_batiment = aucun; travaux_vitres = aucun; type_dommage = bris
- **⚠ vers couvert** `g2-i16` idéal ?, lu C C C · en trop : auteur = assure; bien = element_batiment; intentionnel = non
- `autre-01` idéal C, lu NC C C · **contredit** : violence : oui lu non · en trop : auteur = tiers; effraction = non; fermeture = aucune; simple_disparition = non
- `val-11` idéal NC, lu ? ? ?
- `val-12` idéal C, lu NC NC C · **contredit** : cause_eau : fuite_installation lu debordement_recipient · en trop : absence = oui
- `val-13` idéal C, lu ? ? ? · **contredit** : cause_eau : infiltration_toiture lu infiltration_exterieure
- `val-14` idéal NC, lu ? ? ? · en trop : auteur = tiers; fermeture = aucune
- `red-b01` idéal C, lu NC NC NC · en trop : auteur = famille; cause_dommage = autre; effraction = non; intentionnel = oui; manque_entretien = non; travaux_batiment = aucun; travaux_vitres = aucun; type_dommage = bris; vitre_placee = oui
- `red-b06` idéal NC, lu ? ? ? · **contredit** : evenement : bris lu vandalisme · manque : type_dommage = rayure_ou_ecaillement · en trop : auteur = tiers; intentionnel = oui
- `g-q01` idéal ?, lu NC NC NC · en trop : fermeture = aucune; proprietaire = assure; simple_disparition = non; vol_sur_personne = non
- `g-q02` idéal ?, lu NC NC NC · en trop : evenement = vol; fermeture = aucune; simple_disparition = oui; vol_sur_personne = non
- `g-q04` idéal C, lu NC C NC · en trop : cause_eau = infiltration_exterieure; cause_eau = infiltration_toiture
- `g2-i01` idéal ?, lu NC NC NC · en trop : fermeture = aucune; lieu = parties_communes; simple_disparition = non
- `g2-i03` idéal C, lu NC NC NC · en trop : cause_eau = infiltration_exterieure
- `g2-i06` idéal C, lu NC NC NC · en trop : prevention_gel = non
- `g2-i08` idéal ?, lu NC ? NC · **contredit** : lieu : autre_batiment lu voie_publique · en trop : auteur = tiers; effraction = non; fermeture = aucune; proprietaire = assure; simple_disparition = non; violence = non; vol_sur_personne = oui
- `g2-p01` idéal C, lu ? C C · **contredit** : bien : objet_divers lu cles; bien : objet_divers lu element_batiment; effraction : non lu oui · manque : portes_fermees = oui · en trop : fermeture = cle
- `g2-i07` idéal NC, lu NC ? ? · manque : lieu = voie_publique; vol_sur_personne = non · en trop : absence = oui; auteur = tiers; effraction = oui; fermeture = aucune; proprietaire = assure; simple_disparition = non
- `g2-p04` idéal NC, lu ? ? ? · **contredit** : evenement : vol lu mazout · en trop : auteur = tiers; intentionnel = oui
- `g2-l03` idéal C, lu ? ? ? · manque : bien = objet_divers · en trop : auteur = tiers; effraction = oui; fermeture = aucune; fermeture = cle; portes_fermees = oui; violence = non; vol_sur_personne = non
- `g2-m02` idéal C, lu ? ? ? · en trop : cause_eau = infiltration_exterieure

### Contradictions sans effet sur la décision

- `velo-06` : fermeture : cadenas lu aucune
- `bougie-01` : evenement : autre lu degat_eaux
- `bougie-03` : evenement : autre lu fumee
- `val-09` : bien : objet_divers lu mobilier; evenement : autre lu fumee
- `red-t03` : lieu : garage lu annexe; lieu : garage lu jardin
- `g-l03` : flammes : non lu oui
- `g-l07` : evenement : autre lu bris
- `g-h02` : bien : objet_divers lu electronique
- `g-h03` : bien : element_batiment lu mazout
- `g2-i02` : bien : objet_divers lu cles; effraction : non lu oui

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 85% (82% – 87%) | 64% (61% – 66%) | **3.333 (3 – 4)** | **2.667 (2 – 4)** | 26% (25% – 27%) |

Instables : **9** sur 97 · rappel des clauses : 61% · rappel des questions : 39% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 106.8 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 97 | 82% | 4 ⚠ | 4 |
| garantie : 1.4 | 2 | 100% | 0 | 0 |
| garantie : 2.1 | 13 | 92% | 1 ⚠ | 0 |
| garantie : 2.10 | 40 | 75% | 3 ⚠ | 1 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.12 | 1 | 100% | 0 | 0 |
| garantie : 2.2 | 6 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.5 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 4 | 100% | 0 | 0 |
| garantie : 2.7 | 16 | 69% | 0 | 2 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 7 | 86% | 0 | 1 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 24 | 96% | 0 | 1 |
| thème : info_manquante | 16 | 56% | 1 ⚠ | 1 |
| thème : langue | 11 | 100% | 0 | 0 |
| thème : multi | 8 | 100% | 0 | 0 |
| thème : piege | 55 | 82% | 4 ⚠ | 1 |
| thème : variante | 13 | 85% | 1 ⚠ | 1 |

### Erreurs et instabilités

- **⚠ couvert à tort** `bougie-04` attendu NC, obtenu C NC C — Pendant mes vacances, une bougie laissée sur la table du jardin s'est enflammée et a brûlé la table et le salo… *(Vrai incendie, mais table et salon de jardin = contenu du jardin, exclu du contenu assuré (12/contenu). INCERTAIN défend)*
- **⚠ couvert à tort** `val-03` attendu NC, obtenu C C C — Des amis que j'hébergeais pour le week-end se sont fait voler leur ordinateur lors d'un cambriolage de mon app… *(Exclusion 2.10 : le vol des biens appartenant à des hôtes (alors que la définition du contenu les inclut : piège).)*
- **⚠ couvert à tort** `g-p03` attendu NC, obtenu C C C — Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune… *(Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct.)*
- **⚠ couvert à tort** `g2-i04` attendu ?, obtenu C C NC — Mes bijoux ont disparu de ma chambre après le passage du plombier. *(Une disparition n'est pas un vol établi (simple disparition exclue) ; et un vol par une personne autorisée à se trouver )*
- `autre-01` attendu C, obtenu NC C C — Mon téléphone m'a été arraché des mains dans la rue. *(« Vol commis sur l'assuré, en dehors des biens assurés, suite à violences physiques et/ou menaces » (2.10), plafond 2 50)*
- `val-11` attendu NC, obtenu ? ? ? — Pendant un orage, la pluie s'est infiltrée par la fenêtre mal jointée de ma chambre et a abîmé le mur et la mo… *(Exclusion 2.7 : une infiltration par les fenêtres, autre que celle due à une fuite des installations hydrauliques extéri)*
- `val-12` attendu C, obtenu NC NC C — Ma baignoire a débordé pendant que j'étais au téléphone ; l'eau a abîmé mon parquet. *(2.7 couvre l'ensemble des dégâts des eaux ; l'exclusion du récipient vise un récipient NON relié à l'installation hydrau)*
- `val-14` attendu NC, obtenu ? ? ? — Lors d'un cambriolage avec la porte fracturée, on m'a volé mon chat de race. *(Exclusion 2.10 : le vol des animaux.)*
- `red-b01` attendu C, obtenu NC NC NC — Mon fils a cassé la vitre de la porte-fenêtre du salon avec un ballon. *(2.9 : le bris de vitres.)*
- `g-q01` attendu ?, obtenu NC NC NC — On m'a volé mon vélo dans ma cave. *(La cave n'est couverte que fermée par une serrure de sûreté : il faut le demander.)*
- `g-q04` attendu C, obtenu NC C NC — De l'eau coule du plafond de ma salle de bain et a abîmé le mur. *(2.7 couvre l'ensemble des dégâts des eaux ; la cause inconnue n'établit aucune exclusion (c'est à l'assureur de la prouv)*
- `g2-i01` attendu ?, obtenu NC NC NC — Mon vélo a été volé dans le local de mon immeuble. *(« Le local de mon immeuble » : local commun (vol exclu dans les parties communes) ou cave privative (couverte si serrure)*
- `g2-i03` attendu ?, obtenu NC NC NC — Une tache d'humidité est apparue au plafond de ma chambre, juste sous la salle de bain du voisin du dessus. *(2.7 couvre l'ensemble des dégâts des eaux, mais la condensation et certaines infiltrations sont exclues : la cause est à)*
- `g2-i06` attendu ?, obtenu NC NC NC — Pendant mon absence d'une semaine en février, une canalisation a gelé et a éclaté ; l'eau a abîmé le sol de la… *(Le gel est exclu, sauf si les mesures de prévention (chauffer, vidanger ou isoler) ont été respectées : à demander.)*
- `g2-i08` attendu ?, obtenu NC ? NC — On m'a volé mon sac au restaurant. *(Hors du bâtiment, seul le vol commis sur l'assuré avec violences ou menaces est couvert : à préciser.)*
- `g2-i11` attendu ?, obtenu C ? ? — Après le gros coup de vent d'hier, des tuiles de l'immeuble sont tombées sur mon balcon et l'ont abîmé. *(La tempête suppose un vent d'au moins 80 km/h ou des dégâts aux biens voisins (définition) : non précisé. Garantie 2.2 n)*
- `g2-p01` attendu C, obtenu ? C C — Pendant mes vacances, des cambrioleurs ont ouvert ma porte sans la casser : il n'y a que des traces de tournev… *(Pas d'effraction au sens du contrat, mais la porte était fermée à clé : l'obligation est respectée, le vol dans le bâtim)*
- `g2-i07` attendu NC, obtenu NC ? ? — Mon ordinateur portable a été volé dans ma voiture, garée devant chez moi. *(La voiture n'est pas le bâtiment, et ce n'est pas un vol commis sur l'assuré avec violences.)*
- `g2-p04` attendu NC, obtenu ? ? ? — On a siphonné le fioul de la cuve de chauffage, dans ma cave. *(Exclusion 2.10 : le vol de mazout de chauffage.)*
