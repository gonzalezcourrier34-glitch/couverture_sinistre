# Banc d'essai — foyer-appart123-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (deux temps)

2026-11-18T11:15:19 · golden set v6 (97 cas, empreinte `0b83f83b91580639`) · cas validés par l'auteur : 0 sur 97


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 0.8 | ✓ |
| lecture | decisions_changees | ≤ 2 | 23.67 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 5 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 19 | ✗ |
| chaine | faux_couverts | ≤ 0 | 2.667 | ✗ |
| chaine | faux_refus | ≤ 1 | 3.667 | ✗ |
| chaine | exactitude | ≥ 0.85 | 0.835 | ✗ |
| chaine | instables | ≤ 3 | 8 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 0.364 | ✗ |

## Depuis le banc précédent (2026-11-18T11:09:55)


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

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **23.67** par exécution, dont **5** cas vers un couvert à tort.

Rappel des faits idéaux : 90% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 19 cas · faits vagues : 2 cas · faits en trop : 78 cas · faits retirés faute d'appui : 0 cas

### La lecture change la décision

- **⚠ vers couvert** `bougie-04` idéal NC, lu C C C
- **⚠ vers couvert** `g-p03` idéal ?, lu C C C · **contredit** : bien : objet_divers lu cles · manque : portes_fermees = oui · en trop : auteur = tiers; fermeture = cle; proprietaire = assure; simple_disparition = non
- **⚠ vers couvert** `g2-i04` idéal ?, lu C NC C · en trop : auteur = tiers; evenement = vol; proprietaire = assure; simple_disparition = oui
- **⚠ vers couvert** `g2-i11` idéal ?, lu C C C · **contredit** : lieu : terrasse lu logement · en trop : cause_dommage = autre; type_dommage = bris
- **⚠ vers couvert** `g2-i16` idéal ?, lu C C C · en trop : bien = element_batiment; cause_eau = fuite_installation
- `velo-03` idéal NC, lu NC ? NC · **contredit** : fermeture : cadenas lu cle · manque : vol_sur_personne = non · en trop : auteur = tiers; proprietaire = assure
- `velo-06` idéal NC, lu ? ? ? · **contredit** : fermeture : cadenas lu aucune · manque : violence = non; vol_sur_personne = non · en trop : auteur = tiers; effraction = oui; proprietaire = assure; simple_disparition = non
- `autre-01` idéal C, lu ? ? C · manque : violence = oui · en trop : auteur = tiers
- `val-09` idéal NC, lu ? NC NC · **contredit** : bien : objet_divers lu mobilier; evenement : autre lu electricite; evenement : autre lu fumee · manque : embrasement = non; flammes = non · en trop : chaleur_sans_feu = oui; intentionnel = non
- `val-11` idéal NC, lu ? ? ?
- `val-12` idéal C, lu NC NC C · **contredit** : cause_eau : fuite_installation lu debordement_recipient · en trop : absence = oui
- `val-13` idéal C, lu ? ? ? · **contredit** : cause_eau : infiltration_toiture lu infiltration_exterieure
- `val-14` idéal NC, lu ? ? ? · manque : vol_sur_personne = non · en trop : auteur = tiers; fermeture = aucune; proprietaire = assure; simple_disparition = non
- `red-b01` idéal C, lu NC NC NC · en trop : auteur = famille; cause_dommage = autre; intentionnel = oui; type_dommage = bris
- `red-b06` idéal NC, lu ? ? ? · **contredit** : evenement : bris lu vandalisme · manque : type_dommage = rayure_ou_ecaillement · en trop : auteur = tiers; intentionnel = oui; manque_entretien = non
- `g-q01` idéal ?, lu NC NC NC · en trop : auteur = tiers; fermeture = aucune; proprietaire = assure; simple_disparition = non
- `g-q02` idéal ?, lu NC NC NC · en trop : evenement = vol; fermeture = aucune; simple_disparition = oui
- `g-q04` idéal C, lu NC NC NC · en trop : cause_eau = infiltration_exterieure
- `g-h06` idéal C, lu C C ? · en trop : auteur = tiers; cause_dommage = autre; effraction = oui; type_dommage = bris; vitre_placee = oui
- `g2-i01` idéal ?, lu NC NC NC · en trop : auteur = tiers; fermeture = aucune; lieu = parties_communes; proprietaire = assure; simple_disparition = non
- `g2-i03` idéal C, lu NC NC NC · en trop : cause_eau = infiltration_exterieure
- `g2-i05` idéal ?, lu NC NC NC · en trop : bien = element_batiment; embrasement = non
- `g2-i06` idéal C, lu NC NC NC · en trop : prevention_gel = non
- `g2-p01` idéal C, lu NC C ? · **contredit** : bien : objet_divers lu cles; bien : objet_divers lu element_batiment; effraction : non lu oui · manque : bien = objet_divers; portes_fermees = oui · en trop : auteur = tiers; fermeture = cle; proprietaire = assure
- `g2-p04` idéal NC, lu ? ? ? · **contredit** : evenement : vol lu mazout · en trop : auteur = tiers; intentionnel = oui
- `g2-l03` idéal C, lu NC C NC · **contredit** : bien : objet_divers lu soubassement · en trop : auteur = tiers; effraction = non; fermeture = cle; portes_fermees = oui; proprietaire = assure; simple_disparition = non; violence = non; vol_sur_personne = non
- `g2-m02` idéal C, lu ? ? ? · en trop : cause_eau = infiltration_exterieure

### Contradictions sans effet sur la décision

- `bougie-03` : evenement : autre lu fumee
- `red-t03` : lieu : garage lu jardin
- `g-l07` : evenement : autre lu bris
- `g-p07` : flammes : oui lu non
- `g-h02` : bien : objet_divers lu electronique
- `g-h03` : bien : element_batiment lu mazout
- `g2-i02` : effraction : non lu oui
- `g2-i08` : lieu : autre_batiment lu voie_publique

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 84% (81% – 86%) | 61% (60% – 62%) | **2.667 (2 – 3)** | **3.667 (3 – 5)** | 26% (26% – 26%) |

Instables : **8** sur 97 · rappel des clauses : 62% · rappel des questions : 36% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 95.7 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 97 | 81% | 3 ⚠ | 5 |
| garantie : 1.4 | 2 | 100% | 0 | 0 |
| garantie : 2.1 | 13 | 77% | 1 ⚠ | 0 |
| garantie : 2.10 | 40 | 78% | 2 ⚠ | 2 |
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
| thème : langue | 11 | 91% | 0 | 1 |
| thème : multi | 8 | 100% | 0 | 0 |
| thème : piege | 55 | 82% | 3 ⚠ | 2 |
| thème : variante | 13 | 85% | 1 ⚠ | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `bougie-04` attendu NC, obtenu C C C — Pendant mes vacances, une bougie laissée sur la table du jardin s'est enflammée et a brûlé la table et le salo… *(Vrai incendie, mais table et salon de jardin = contenu du jardin, exclu du contenu assuré (12/contenu). INCERTAIN défend)*
- **⚠ couvert à tort** `g-p03` attendu NC, obtenu C C C — Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune… *(Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct.)*
- **⚠ couvert à tort** `g2-i04` attendu ?, obtenu C NC C — Mes bijoux ont disparu de ma chambre après le passage du plombier. *(Une disparition n'est pas un vol établi (simple disparition exclue) ; et un vol par une personne autorisée à se trouver )*
- `velo-03` attendu NC, obtenu NC ? NC — Mon vélo a été volé dans ma cave privative, fermée à clé. Le cadenas de la porte a été forcé. *(Cave en immeuble à appartements : vol couvert à 1 000 EUR « si ces locaux sont fermés avec une serrure de sûreté » (2.10)*
- `velo-06` attendu NC, obtenu ? ? ? — Mon vélo était attaché à un arceau dans la rue avec un antivol. L'antivol a été coupé et le vélo volé. *(Vol dans la rue, sans violence : hors du bâtiment, et ce n'est pas un « vol commis sur l'assuré … suite à violences ».)*
- `autre-01` attendu C, obtenu ? ? C — Mon téléphone m'a été arraché des mains dans la rue. *(« Vol commis sur l'assuré, en dehors des biens assurés, suite à violences physiques et/ou menaces » (2.10), plafond 2 50)*
- `val-09` attendu NC, obtenu ? NC NC — Mon fer à repasser, laissé à plat sur la planche, a brûlé la housse et laissé une marque sur le tissu, sans fl… *(Définition de l'incendie : les brûlures et le contact d'une source de chaleur sans embrasement ne sont pas un incendie.)*
- `val-11` attendu NC, obtenu ? ? ? — Pendant un orage, la pluie s'est infiltrée par la fenêtre mal jointée de ma chambre et a abîmé le mur et la mo… *(Exclusion 2.7 : une infiltration par les fenêtres, autre que celle due à une fuite des installations hydrauliques extéri)*
- `val-12` attendu C, obtenu NC NC C — Ma baignoire a débordé pendant que j'étais au téléphone ; l'eau a abîmé mon parquet. *(2.7 couvre l'ensemble des dégâts des eaux ; l'exclusion du récipient vise un récipient NON relié à l'installation hydrau)*
- `val-14` attendu NC, obtenu ? ? ? — Lors d'un cambriolage avec la porte fracturée, on m'a volé mon chat de race. *(Exclusion 2.10 : le vol des animaux.)*
- `red-b01` attendu C, obtenu NC NC NC — Mon fils a cassé la vitre de la porte-fenêtre du salon avec un ballon. *(2.9 : le bris de vitres.)*
- `g-q01` attendu ?, obtenu NC NC NC — On m'a volé mon vélo dans ma cave. *(La cave n'est couverte que fermée par une serrure de sûreté : il faut le demander.)*
- `g-q04` attendu C, obtenu NC NC NC — De l'eau coule du plafond de ma salle de bain et a abîmé le mur. *(2.7 couvre l'ensemble des dégâts des eaux ; la cause inconnue n'établit aucune exclusion (c'est à l'assureur de la prouv)*
- `g-h06` attendu C, obtenu C C ? — Pendant une manifestation qui a dégénéré, des émeutiers ont brisé les fenêtres de mon appartement au rez-de-ch… *(2.4 : détérioration par des personnes prenant part à un attentat (émeutes) ; aussi 2.9. Non traduites.)*
- `g2-i01` attendu ?, obtenu NC NC NC — Mon vélo a été volé dans le local de mon immeuble. *(« Le local de mon immeuble » : local commun (vol exclu dans les parties communes) ou cave privative (couverte si serrure)*
- `g2-i03` attendu ?, obtenu NC NC NC — Une tache d'humidité est apparue au plafond de ma chambre, juste sous la salle de bain du voisin du dessus. *(2.7 couvre l'ensemble des dégâts des eaux, mais la condensation et certaines infiltrations sont exclues : la cause est à)*
- `g2-i05` attendu ?, obtenu NC NC NC — Il y a eu un début de feu dans la cuisine. *(L'incendie suppose flammes et embrasement ; les dégâts et l'embrasement sont à préciser.)*
- `g2-i06` attendu ?, obtenu NC NC NC — Pendant mon absence d'une semaine en février, une canalisation a gelé et a éclaté ; l'eau a abîmé le sol de la… *(Le gel est exclu, sauf si les mesures de prévention (chauffer, vidanger ou isoler) ont été respectées : à demander.)*
- `g2-p01` attendu C, obtenu NC C ? — Pendant mes vacances, des cambrioleurs ont ouvert ma porte sans la casser : il n'y a que des traces de tournev… *(Pas d'effraction au sens du contrat, mais la porte était fermée à clé : l'obligation est respectée, le vol dans le bâtim)*
- `g2-p04` attendu NC, obtenu ? ? ? — On a siphonné le fioul de la cuve de chauffage, dans ma cave. *(Exclusion 2.10 : le vol de mazout de chauffage.)*
- `g2-l03` attendu C, obtenu NC C NC — Je n'étais pas absente et la porte n'était pas ouverte : quelqu'un est entré pendant que je dormais et a pris … *(Vol du contenu dans le bâtiment ; l'obligation de fermer à clé ne vaut qu'en cas d'absence.)*
