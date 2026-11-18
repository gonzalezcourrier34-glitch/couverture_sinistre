# Banc d'essai — foyer-appart123-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-18T22:02:35 · golden set v6 (97 cas, empreinte `0b83f83b91580639`) · cas validés par l'auteur : 0 sur 97


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 0.8 | ✓ |
| lecture | decisions_changees | ≤ 2 | 20 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 5 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 15 | ✗ |
| chaine | faux_couverts | ≤ 0 | 2.333 | ✗ |
| chaine | faux_refus | ≤ 1 | 1 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.887 | ✓ |
| chaine | instables | ≤ 3 | 13 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 0.697 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 4.52 | ✓ |

## Depuis le banc précédent (2026-11-18T21:48:42)

- lecture · rappel_faits : 0.869 → 0.871
- chaine · exactitude : 0.894 → 0.887
- chaine · exactitude_stricte : 0.646 → 0.649
- chaine · faux_couverts : 3 → 2.333
- chaine · faux_refus : 0.667 → 1

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

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **20** par exécution, dont **5** cas vers un couvert à tort.

Rappel des faits idéaux : 87% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 15 cas · faits vagues : 1 cas · faits en trop : 66 cas · faits retirés (sans appui ou non dits) : 69 cas

### La lecture change la décision

- **⚠ vers couvert** `bougie-04` idéal NC, lu C C NC · manque : absence = oui · en trop : auteur = assure; cause_dommage = autre; intentionnel = non; type_dommage = bris · retiré sans appui : chaleur_sans_feu = non; effraction = non; intentionnel = non; manque_entretien = non; travaux_batiment = aucun; travaux_vitres = aucun
- **⚠ vers couvert** `val-03` idéal NC, lu C NC ? · manque : proprietaire = hote; vol_sur_personne = non · en trop : auteur = tiers · retiré sans appui : absence = oui; auteur = tiers; fermeture = aucune
- **⚠ vers couvert** `g-p03` idéal ?, lu C C C · **contredit** : bien : objet_divers lu cles · manque : portes_fermees = oui · retiré sans appui : fermeture = cle
- **⚠ vers couvert** `g2-i04` idéal ?, lu C NC NC · en trop : auteur = tiers; evenement = vol; proprietaire = assure; simple_disparition = oui; vol_sur_personne = non · retiré sans appui : simple_disparition = non; vol_sur_personne = non
- **⚠ vers couvert** `g2-i16` idéal ?, lu C C C · en trop : auteur = assure; bien = element_batiment · retiré sans appui : intentionnel = non
- `velo-04` idéal NC, lu NC ? NC · manque : fermeture = aucune; vol_sur_personne = non · retiré sans appui : absence = oui; fermeture = aucune
- `velo-06` idéal NC, lu NC NC ? · manque : fermeture = cadenas; violence = non; vol_sur_personne = non · en trop : auteur = tiers; effraction = oui · retiré sans appui : fermeture = aucune; fermeture = cle; vol_sur_personne = non
- `velo-07` idéal ?, lu ? NC ? · manque : vol_sur_personne = non · en trop : portes_fermees = oui · retiré sans appui : absence = oui; auteur = tiers
- `val-10` idéal NC, lu NC NC ? · manque : prevention_gel = non · retiré sans appui : prevention_gel = non
- `val-11` idéal NC, lu ? ? ?
- `val-12` idéal C, lu NC C NC · **contredit** : cause_eau : fuite_installation lu debordement_recipient · en trop : absence = oui
- `val-13` idéal C, lu ? ? ? · **contredit** : cause_eau : infiltration_toiture lu infiltration_exterieure
- `val-14` idéal NC, lu ? ? ? · en trop : auteur = tiers · retiré sans appui : fermeture = aucune
- `red-b01` idéal C, lu NC NC NC · en trop : auteur = famille; cause_dommage = autre; intentionnel = oui; type_dommage = bris; vitre_placee = oui · retiré sans appui : effraction = non; manque_entretien = non; travaux_batiment = aucun; travaux_vitres = aucun
- `red-b06` idéal NC, lu ? ? ? · **contredit** : evenement : bris lu vandalisme · manque : type_dommage = rayure_ou_ecaillement · retiré sans appui : auteur = tiers; intentionnel = oui
- `g-q02` idéal ?, lu NC NC NC · en trop : evenement = vol; proprietaire = assure; simple_disparition = oui · retiré sans appui : fermeture = aucune; vol_sur_personne = non
- `g-q04` idéal C, lu C C NC · en trop : cause_eau = infiltration_exterieure
- `g-h06` idéal C, lu C ? ? · en trop : auteur = tiers; effraction = oui; intentionnel = oui; manque_entretien = non; travaux_batiment = aucun; travaux_vitres = aucun; type_dommage = bris; vitre_placee = oui · retiré sans appui : travaux_batiment = aucun; travaux_vitres = aucun
- `g2-i01` idéal ?, lu NC NC NC · en trop : lieu = parties_communes; simple_disparition = non · retiré sans appui : fermeture = aucune; simple_disparition = non; vol_sur_personne = non
- `g2-i03` idéal C, lu NC NC NC · en trop : cause_eau = infiltration_exterieure
- `g2-i06` idéal ?, lu NC ? ? · en trop : prevention_gel = non · retiré sans appui : prevention_gel = non
- `g2-p01` idéal C, lu C ? C · **contredit** : bien : objet_divers lu cles; bien : objet_divers lu element_batiment; effraction : non lu oui · manque : portes_fermees = oui · en trop : fermeture = cle
- `g2-i07` idéal NC, lu ? ? ? · manque : lieu = voie_publique; vol_sur_personne = non · en trop : absence = oui; auteur = tiers; effraction = oui; proprietaire = assure; simple_disparition = non · retiré sans appui : fermeture = aucune; vol_sur_personne = non
- `g2-p04` idéal NC, lu ? ? ? · **contredit** : evenement : vol lu mazout · retiré sans appui : auteur = tiers; intentionnel = oui
- `g2-l03` idéal C, lu ? ? ? · manque : absence = non; bien = objet_divers · en trop : auteur = tiers; effraction = oui; fermeture = cle; portes_fermees = oui; violence = non; vol_sur_personne = non · retiré sans appui : absence = non; effraction = oui; fermeture = cle; vol_sur_personne = non
- `g2-m02` idéal C, lu ? ? ? · en trop : cause_eau = infiltration_exterieure

### Contradictions sans effet sur la décision

- `bougie-03` : evenement : autre lu fumee
- `val-09` : bien : objet_divers lu mobilier; evenement : autre lu fumee
- `red-t03` : lieu : garage lu jardin
- `g-l07` : evenement : autre lu bris
- `g-h02` : bien : objet_divers lu electronique
- `g-h03` : bien : element_batiment lu mazout
- `g2-i02` : bien : objet_divers lu cles; effraction : non lu oui
- `g2-i08` : lieu : autre_batiment lu voie_publique
- `g2-i11` : lieu : terrasse lu logement

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 89% (89% – 89%) | 65% (65% – 65%) | **2.333 (1 – 4)** | **1 (1 – 1)** | 37% (34% – 40%) |

Instables : **13** sur 97 · rappel des clauses : 65% · rappel des questions : 70% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 201.7 s · par cas, un à la fois (10 cas) : médiane 3.16 s, 95e centile 4.52 s (lecture 2.55 s, décision 0.0 s) · en masse (quatre à la fois) : médiane 2.89 s, 95e centile 68.21 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 97 | 89% | 4 ⚠ | 1 |
| garantie : 1.4 | 2 | 100% | 0 | 0 |
| garantie : 2.1 | 13 | 92% | 1 ⚠ | 0 |
| garantie : 2.10 | 40 | 82% | 3 ⚠ | 0 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.12 | 1 | 100% | 0 | 0 |
| garantie : 2.2 | 6 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.5 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 4 | 100% | 0 | 0 |
| garantie : 2.7 | 16 | 88% | 0 | 1 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 7 | 86% | 0 | 0 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 24 | 96% | 0 | 0 |
| thème : info_manquante | 16 | 88% | 1 ⚠ | 0 |
| thème : langue | 11 | 100% | 0 | 0 |
| thème : multi | 8 | 100% | 0 | 0 |
| thème : piege | 55 | 82% | 4 ⚠ | 1 |
| thème : variante | 13 | 92% | 1 ⚠ | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `bougie-04` attendu NC, obtenu C C NC — Pendant mes vacances, une bougie laissée sur la table du jardin s'est enflammée et a brûlé la table et le salo… *(Vrai incendie, mais table et salon de jardin = contenu du jardin, exclu du contenu assuré (12/contenu). INCERTAIN défend)*
- **⚠ couvert à tort** `val-03` attendu NC, obtenu C NC ? — Des amis que j'hébergeais pour le week-end se sont fait voler leur ordinateur lors d'un cambriolage de mon app… *(Exclusion 2.10 : le vol des biens appartenant à des hôtes (alors que la définition du contenu les inclut : piège).)*
- **⚠ couvert à tort** `g-p03` attendu NC, obtenu C C C — Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune… *(Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct.)*
- **⚠ couvert à tort** `g2-i04` attendu ?, obtenu C NC ? — Mes bijoux ont disparu de ma chambre après le passage du plombier. *(Une disparition n'est pas un vol établi (simple disparition exclue) ; et un vol par une personne autorisée à se trouver )*
- `velo-04` attendu NC, obtenu NC ? NC — Mon vélo a été volé dans ma cave privative. J'avais oublié de la fermer à clé et il n'y a aucune trace d'effra… *(Cave non fermée : pas de serrure de sûreté (condition du plafond caves), et obligation de prévention non respectée avec )*
- `velo-06` attendu NC, obtenu NC NC ? — Mon vélo était attaché à un arceau dans la rue avec un antivol. L'antivol a été coupé et le vélo volé. *(Vol dans la rue, sans violence : hors du bâtiment, et ce n'est pas un « vol commis sur l'assuré … suite à violences ».)*
- `velo-07` attendu C, obtenu ? NC ? — Mon vélo électrique acheté 3 500 € a été volé dans mon garage privatif fermé à clé. La porte du garage a été f… *(Garage privatif = bâtiment (12/batiment) ; effraction. Plafond 1 000 EUR si sans communication directe et serrure de sûr)*
- `autre-01` attendu C, obtenu ? C C — Mon téléphone m'a été arraché des mains dans la rue. *(« Vol commis sur l'assuré, en dehors des biens assurés, suite à violences physiques et/ou menaces » (2.10), plafond 2 50)*
- `val-11` attendu NC, obtenu ? ? ? — Pendant un orage, la pluie s'est infiltrée par la fenêtre mal jointée de ma chambre et a abîmé le mur et la mo… *(Exclusion 2.7 : une infiltration par les fenêtres, autre que celle due à une fuite des installations hydrauliques extéri)*
- `val-12` attendu C, obtenu NC C NC — Ma baignoire a débordé pendant que j'étais au téléphone ; l'eau a abîmé mon parquet. *(2.7 couvre l'ensemble des dégâts des eaux ; l'exclusion du récipient vise un récipient NON relié à l'installation hydrau)*
- `val-14` attendu NC, obtenu ? ? ? — Lors d'un cambriolage avec la porte fracturée, on m'a volé mon chat de race. *(Exclusion 2.10 : le vol des animaux.)*
- `red-b01` attendu C, obtenu ? ? ? — Mon fils a cassé la vitre de la porte-fenêtre du salon avec un ballon. *(2.9 : le bris de vitres.)*
- `g-q04` attendu C, obtenu C C ? — De l'eau coule du plafond de ma salle de bain et a abîmé le mur. *(2.7 couvre l'ensemble des dégâts des eaux ; la cause inconnue n'établit aucune exclusion (c'est à l'assureur de la prouv)*
- `g-h06` attendu C, obtenu C ? ? — Pendant une manifestation qui a dégénéré, des émeutiers ont brisé les fenêtres de mon appartement au rez-de-ch… *(2.4 : détérioration par des personnes prenant part à un attentat (émeutes) ; aussi 2.9. Non traduites.)*
- `g2-i01` attendu ?, obtenu NC NC NC — Mon vélo a été volé dans le local de mon immeuble. *(« Le local de mon immeuble » : local commun (vol exclu dans les parties communes) ou cave privative (couverte si serrure)*
- `g2-i02` attendu ?, obtenu C ? ? — On a cambriolé mon appartement pendant le week-end où j'étais absent. La serrure porte des rayures, mais la po… *(Des traces sans réparation nécessaire ne sont pas une effraction (définition). Sans effraction, l'obligation de fermer à)*
- `g2-p01` attendu C, obtenu C ? ? — Pendant mes vacances, des cambrioleurs ont ouvert ma porte sans la casser : il n'y a que des traces de tournev… *(Pas d'effraction au sens du contrat, mais la porte était fermée à clé : l'obligation est respectée, le vol dans le bâtim)*
- `g2-i07` attendu NC, obtenu ? ? ? — Mon ordinateur portable a été volé dans ma voiture, garée devant chez moi. *(La voiture n'est pas le bâtiment, et ce n'est pas un vol commis sur l'assuré avec violences.)*
- `g2-p04` attendu NC, obtenu ? ? ? — On a siphonné le fioul de la cuve de chauffage, dans ma cave. *(Exclusion 2.10 : le vol de mazout de chauffage.)*
- `g2-m01` attendu C, obtenu C ? C — Un court-circuit a provoqué un incendie dans le salon ; pour entrer, les pompiers ont dû casser la porte d'ent… *(2.1 : l'incendie, et les dégâts causés pour l'éteindre.)*
