# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (deux temps)

2026-11-18T13:30:00 · golden set v6 (97 cas, empreinte `0b83f83b91580639`) · cas validés par l'auteur : 0 sur 97


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 0.8 | ✓ |
| lecture | decisions_changees | ≤ 2 | 20.67 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 6 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 18 | ✗ |
| chaine | faux_couverts | ≤ 0 | 3 | ✗ |
| chaine | faux_refus | ≤ 1 | 2 | ✗ |
| chaine | exactitude | ≥ 0.85 | 0.863 | ✓ |
| chaine | instables | ≤ 3 | 8 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 0.364 | ✗ |

## Depuis le banc précédent (2026-11-18T11:15:19)

- lecture · rappel_faits : 0.898 → 0.914
- chaine · exactitude : 0.835 → 0.863
- chaine · exactitude_stricte : 0.612 → 0.643
- chaine · faux_couverts : 2.667 → 3
- chaine · faux_refus : 3.667 → 2

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

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **20.67** par exécution, dont **6** cas vers un couvert à tort.

Rappel des faits idéaux : 91% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 18 cas · faits vagues : 1 cas · faits en trop : 81 cas · faits retirés faute d'appui : 0 cas

### La lecture change la décision

- **⚠ vers couvert** `bougie-04` idéal NC, lu C C NC · en trop : chaleur_sans_feu = non
- **⚠ vers couvert** `g-q03` idéal ?, lu C ? ? · en trop : absence = oui; fermeture = aucune; lieu = logement; proprietaire = assure; simple_disparition = non; vol_sur_personne = non
- **⚠ vers couvert** `g-p03` idéal ?, lu C C C · **contredit** : bien : objet_divers lu cles · manque : portes_fermees = oui · en trop : auteur = tiers; fermeture = cle; simple_disparition = non
- **⚠ vers couvert** `g2-i04` idéal ?, lu C C C · en trop : auteur = tiers; effraction = non; evenement = vol; simple_disparition = non; vol_sur_personne = non
- **⚠ vers couvert** `g2-i11` idéal ?, lu C C ? · **contredit** : lieu : terrasse lu logement · en trop : intentionnel = non
- **⚠ vers couvert** `g2-i16` idéal ?, lu C C C · en trop : bien = element_batiment
- `velo-03` idéal NC, lu NC ? ? · **contredit** : fermeture : cadenas lu cle · manque : vol_sur_personne = non
- `autre-01` idéal C, lu ? C ? · manque : violence = oui · en trop : auteur = tiers; fermeture = aucune; simple_disparition = non
- `val-03` idéal NC, lu NC ? ? · en trop : auteur = tiers; fermeture = aucune; simple_disparition = non
- `val-11` idéal NC, lu ? ? ?
- `val-12` idéal C, lu NC NC NC · **contredit** : cause_eau : fuite_installation lu debordement_recipient · en trop : absence = oui
- `val-13` idéal C, lu ? ? ? · **contredit** : cause_eau : infiltration_toiture lu infiltration_exterieure
- `val-14` idéal NC, lu ? ? ? · en trop : auteur = tiers; fermeture = aucune; proprietaire = assure; simple_disparition = non
- `red-b01` idéal C, lu NC NC NC · en trop : auteur = famille; cause_dommage = autre; effraction = non; intentionnel = oui; manque_entretien = non; travaux_batiment = aucun; travaux_vitres = aucun; type_dommage = bris; vitre_placee = oui
- `red-b06` idéal NC, lu ? ? ? · **contredit** : evenement : bris lu vandalisme · manque : type_dommage = rayure_ou_ecaillement · en trop : auteur = tiers; intentionnel = oui; manque_entretien = non
- `g-q01` idéal ?, lu NC NC NC · en trop : fermeture = aucune; proprietaire = assure; simple_disparition = non; vol_sur_personne = non
- `g-q02` idéal ?, lu NC NC NC · en trop : evenement = vol; fermeture = aucune; proprietaire = assure; simple_disparition = oui; vol_sur_personne = non
- `g-h06` idéal C, lu ? C C · en trop : auteur = tiers; effraction = oui; manque_entretien = non; travaux_batiment = aucun; travaux_vitres = aucun; type_dommage = bris; vitre_placee = oui
- `g2-i01` idéal ?, lu NC NC NC · en trop : fermeture = aucune; lieu = parties_communes; simple_disparition = non; vol_sur_personne = non
- `g2-i03` idéal C, lu NC NC NC · en trop : cause_eau = infiltration_exterieure
- `g2-i05` idéal ?, lu NC NC ? · en trop : bien = element_batiment; embrasement = non
- `g2-i06` idéal C, lu NC NC NC · en trop : prevention_gel = non
- `g2-p04` idéal NC, lu ? ? ? · **contredit** : evenement : vol lu mazout · en trop : auteur = tiers; intentionnel = oui; manque_entretien = non
- `g2-m02` idéal C, lu ? ? ? · en trop : cause_eau = infiltration_exterieure

### Contradictions sans effet sur la décision

- `velo-06` : fermeture : cadenas lu aucune
- `bougie-01` : evenement : autre lu degat_eaux
- `val-09` : bien : objet_divers lu mobilier; evenement : autre lu fumee
- `red-t03` : lieu : garage lu annexe; lieu : garage lu jardin
- `g-l07` : evenement : autre lu bris
- `g-h02` : bien : objet_divers lu electronique
- `g-h03` : bien : element_batiment lu mazout
- `g2-i02` : bien : objet_divers lu cles; effraction : non lu oui
- `g2-i08` : lieu : autre_batiment lu voie_publique
- `g2-p01` : bien : objet_divers lu cles; effraction : non lu oui
- `g2-l03` : bien : objet_divers lu cles/soubassement

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 86% (86% – 88%) | 64% (63% – 66%) | **3 (2 – 4)** | **2 (2 – 2)** | 25% (24% – 28%) |

Instables : **8** sur 97 · rappel des clauses : 61% · rappel des questions : 36% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 102.2 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 97 | 86% | 4 ⚠ | 2 |
| garantie : 1.4 | 2 | 100% | 0 | 0 |
| garantie : 2.1 | 13 | 85% | 1 ⚠ | 0 |
| garantie : 2.10 | 40 | 82% | 3 ⚠ | 0 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.12 | 1 | 100% | 0 | 0 |
| garantie : 2.2 | 6 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.5 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 4 | 100% | 0 | 0 |
| garantie : 2.7 | 16 | 75% | 0 | 1 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 7 | 86% | 0 | 1 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 24 | 96% | 0 | 1 |
| thème : info_manquante | 16 | 56% | 2 ⚠ | 0 |
| thème : langue | 11 | 100% | 0 | 0 |
| thème : multi | 8 | 100% | 0 | 0 |
| thème : piege | 55 | 86% | 3 ⚠ | 1 |
| thème : variante | 13 | 92% | 1 ⚠ | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `bougie-04` attendu NC, obtenu C C NC — Pendant mes vacances, une bougie laissée sur la table du jardin s'est enflammée et a brûlé la table et le salo… *(Vrai incendie, mais table et salon de jardin = contenu du jardin, exclu du contenu assuré (12/contenu). INCERTAIN défend)*
- **⚠ couvert à tort** `g-q03` attendu ?, obtenu C ? ? — Mon vélo a été volé pendant que je faisais mes courses. *(Le lieu décide (dans le bâtiment ou dehors) : il faut le demander.)*
- **⚠ couvert à tort** `g-p03` attendu NC, obtenu C C C — Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune… *(Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct.)*
- **⚠ couvert à tort** `g2-i04` attendu ?, obtenu C C C — Mes bijoux ont disparu de ma chambre après le passage du plombier. *(Une disparition n'est pas un vol établi (simple disparition exclue) ; et un vol par une personne autorisée à se trouver )*
- `velo-03` attendu NC, obtenu NC ? ? — Mon vélo a été volé dans ma cave privative, fermée à clé. Le cadenas de la porte a été forcé. *(Cave en immeuble à appartements : vol couvert à 1 000 EUR « si ces locaux sont fermés avec une serrure de sûreté » (2.10)*
- `autre-01` attendu C, obtenu ? C ? — Mon téléphone m'a été arraché des mains dans la rue. *(« Vol commis sur l'assuré, en dehors des biens assurés, suite à violences physiques et/ou menaces » (2.10), plafond 2 50)*
- `val-03` attendu NC, obtenu NC ? ? — Des amis que j'hébergeais pour le week-end se sont fait voler leur ordinateur lors d'un cambriolage de mon app… *(Exclusion 2.10 : le vol des biens appartenant à des hôtes (alors que la définition du contenu les inclut : piège).)*
- `val-11` attendu NC, obtenu ? ? ? — Pendant un orage, la pluie s'est infiltrée par la fenêtre mal jointée de ma chambre et a abîmé le mur et la mo… *(Exclusion 2.7 : une infiltration par les fenêtres, autre que celle due à une fuite des installations hydrauliques extéri)*
- `val-12` attendu C, obtenu NC NC NC — Ma baignoire a débordé pendant que j'étais au téléphone ; l'eau a abîmé mon parquet. *(2.7 couvre l'ensemble des dégâts des eaux ; l'exclusion du récipient vise un récipient NON relié à l'installation hydrau)*
- `val-14` attendu NC, obtenu ? ? ? — Lors d'un cambriolage avec la porte fracturée, on m'a volé mon chat de race. *(Exclusion 2.10 : le vol des animaux.)*
- `red-b01` attendu C, obtenu NC NC NC — Mon fils a cassé la vitre de la porte-fenêtre du salon avec un ballon. *(2.9 : le bris de vitres.)*
- `g-q01` attendu ?, obtenu NC NC NC — On m'a volé mon vélo dans ma cave. *(La cave n'est couverte que fermée par une serrure de sûreté : il faut le demander.)*
- `g-h06` attendu C, obtenu ? C C — Pendant une manifestation qui a dégénéré, des émeutiers ont brisé les fenêtres de mon appartement au rez-de-ch… *(2.4 : détérioration par des personnes prenant part à un attentat (émeutes) ; aussi 2.9. Non traduites.)*
- `g2-i01` attendu ?, obtenu NC NC NC — Mon vélo a été volé dans le local de mon immeuble. *(« Le local de mon immeuble » : local commun (vol exclu dans les parties communes) ou cave privative (couverte si serrure)*
- `g2-i03` attendu ?, obtenu NC NC NC — Une tache d'humidité est apparue au plafond de ma chambre, juste sous la salle de bain du voisin du dessus. *(2.7 couvre l'ensemble des dégâts des eaux, mais la condensation et certaines infiltrations sont exclues : la cause est à)*
- `g2-i05` attendu ?, obtenu NC NC ? — Il y a eu un début de feu dans la cuisine. *(L'incendie suppose flammes et embrasement ; les dégâts et l'embrasement sont à préciser.)*
- `g2-i06` attendu ?, obtenu NC NC NC — Pendant mon absence d'une semaine en février, une canalisation a gelé et a éclaté ; l'eau a abîmé le sol de la… *(Le gel est exclu, sauf si les mesures de prévention (chauffer, vidanger ou isoler) ont été respectées : à demander.)*
- `g2-i11` attendu ?, obtenu C C ? — Après le gros coup de vent d'hier, des tuiles de l'immeuble sont tombées sur mon balcon et l'ont abîmé. *(La tempête suppose un vent d'au moins 80 km/h ou des dégâts aux biens voisins (définition) : non précisé. Garantie 2.2 n)*
- `g2-p04` attendu NC, obtenu ? ? ? — On a siphonné le fioul de la cuve de chauffage, dans ma cave. *(Exclusion 2.10 : le vol de mazout de chauffage.)*
