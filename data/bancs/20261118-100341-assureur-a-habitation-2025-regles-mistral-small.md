# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest`

2026-11-18T09:59:59 · golden set v6 (97 cas, empreinte `0b83f83b91580639`) · cas validés par l'auteur : 0 sur 97


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 0.8 | ✓ |
| lecture | decisions_changees | ≤ 2 | 31.33 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 14 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 20 | ✗ |
| chaine | faux_couverts | ≤ 0 | 9.333 | ✗ |
| chaine | faux_refus | ≤ 1 | 5 | ✗ |
| chaine | exactitude | ≥ 0.85 | 0.753 | ✗ |
| chaine | instables | ≤ 3 | 14 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 0.515 | ✗ |

## Depuis le banc précédent (2026-11-18T09:56:57)


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

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **31.33** par exécution, dont **14** cas vers un couvert à tort.

Rappel des faits idéaux : 78% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 20 cas · faits vagues : 3 cas · faits en trop : 32 cas · faits retirés faute d'appui : 0 cas

### La lecture change la décision

- **⚠ vers couvert** `bougie-03` idéal NC, lu C C ? · **contredit** : bien : mobilier lu element_batiment; evenement : autre lu fumee · manque : embrasement = non; flammes = non; lieu = logement
- **⚠ vers couvert** `bougie-04` idéal NC, lu C NC C · manque : absence = oui
- **⚠ vers couvert** `val-01` idéal ?, lu C C C · manque : absence = oui; effraction = non; portes_fermees = oui; vol_sur_personne = non · en trop : fermeture = aucune; fermeture = cle
- **⚠ vers couvert** `val-03` idéal NC, lu C NC NC · manque : proprietaire = hote; vol_sur_personne = non · en trop : auteur = tiers
- **⚠ vers couvert** `val-10` idéal NC, lu C C C · manque : absence = oui; prevention_gel = non
- **⚠ vers couvert** `red-b05` idéal NC, lu NC NC C · **contredit** : evenement : bris lu autre · manque : lieu = logement; vitre_placee = non
- **⚠ vers couvert** `g-q02` idéal ?, lu C C C · en trop : evenement = vol
- **⚠ vers couvert** `g-q03` idéal ?, lu C C C · en trop : lieu = logement
- **⚠ vers couvert** `g-p03` idéal ?, lu C C C · **contredit** : bien : objet_divers lu cles · manque : absence = oui; portes_fermees = oui · en trop : fermeture = cle
- **⚠ vers couvert** `g2-i04` idéal ?, lu C C C · en trop : absence = oui; evenement = vol
- **⚠ vers couvert** `g2-i11` idéal ?, lu C ? C
- **⚠ vers couvert** `g2-i16` idéal ?, lu ? ? C · en trop : bien = element_batiment; cause_eau = fuite_installation
- **⚠ vers couvert** `g2-i13` idéal NC, lu NC C C · manque : manque_entretien = oui
- **⚠ vers couvert** `g2-p12` idéal NC, lu NC C C · manque : auteur = assure; intentionnel = oui
- `velo-03` idéal NC, lu ? ? ? · **contredit** : fermeture : cadenas lu cle · manque : vol_sur_personne = non
- `velo-06` idéal NC, lu ? ? ? · **contredit** : fermeture : cadenas lu cle · manque : fermeture = cadenas; violence = non; vol_sur_personne = non · en trop : effraction = oui
- `autre-01` idéal C, lu ? ? ? · manque : violence = oui
- `autre-02` idéal C, lu ? ? ? · manque : lieu = logement
- `val-06` idéal C, lu ? ? ? · manque : depot_moins_30j = oui; effraction = oui; vol_sur_personne = non
- `val-09` idéal NC, lu ? ? ? · **contredit** : bien : objet_divers lu electronique; evenement : autre lu fumee · manque : embrasement = non; flammes = non; lieu = logement
- `val-12` idéal C, lu NC NC NC · **contredit** : cause_eau : fuite_installation lu debordement_recipient · manque : lieu = logement
- `red-b01` idéal C, lu NC NC NC · en trop : intentionnel = oui
- `red-b06` idéal NC, lu ? ? ? · **contredit** : evenement : bris lu vandalisme · manque : type_dommage = rayure_ou_ecaillement
- `g-l05` idéal C, lu ? C C · manque : lieu = logement
- `g-l06` idéal C, lu C ? C · manque : violence = oui; vol_sur_personne = oui · en trop : auteur = tiers
- `g-p04` idéal C, lu ? ? ? · manque : lieu = logement
- `g-p05` idéal C, lu NC NC NC · **contredit** : cause_eau : debordement_aquarium lu debordement_recipient
- `g-h05` idéal ?, lu NC NC NC · manque : bien = element_batiment
- `g-h06` idéal C, lu ? ? ?
- `g-m02` idéal C, lu C NC C · manque : embrasement = oui; flammes = oui · en trop : cause_eau = inondation
- `g2-i01` idéal ?, lu NC NC NC · en trop : lieu = parties_communes
- `g2-i02` idéal C, lu NC NC NC · **contredit** : bien : objet_divers lu element_batiment; effraction : non lu oui · en trop : fermeture = cle
- `g2-i03` idéal C, lu NC NC NC · en trop : cause_eau = infiltration_exterieure
- `g2-i12` idéal C, lu ? C C · vague : bien : appareil_audiovisuel lu electronique · en trop : fenetres_fermees = non; portes_fermees = non
- `g2-p01` idéal C, lu NC NC C · **contredit** : bien : objet_divers lu cles; bien : objet_divers lu element_batiment; effraction : non lu oui · manque : absence = oui; portes_fermees = oui · en trop : auteur = tiers; fermeture = cle
- `g2-i07` idéal NC, lu ? ? ? · manque : lieu = voie_publique; vol_sur_personne = non · en trop : absence = oui
- `g2-p04` idéal NC, lu ? ? ? · **contredit** : evenement : vol lu mazout
- `g2-m02` idéal C, lu C ? ? · en trop : cause_eau = infiltration_exterieure

### Contradictions sans effet sur la décision

- `val-02` : auteur : personnel_prive lu famille
- `red-t03` : lieu : garage lu annexe; lieu : garage lu autre_batiment
- `red-b03` : evenement : bris lu autre
- `g-l03` : bien : mobilier_jardin lu mobilier; lieu : jardin lu terrasse
- `g-h02` : bien : objet_divers lu electronique
- `g-h03` : bien : element_batiment lu mazout
- `g2-i08` : lieu : autre_batiment lu voie_publique
- `g2-l03` : bien : objet_divers lu valeurs

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 75% (75% – 75%) | 55% (54% – 56%) | **9.333 (9 – 10)** | **5 (4 – 6)** | 30% (29% – 31%) |

Instables : **14** sur 97 · rappel des clauses : 59% · rappel des questions : 52% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 41.9 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 97 | 75% | 9 ⚠ | 5 |
| garantie : 1.4 | 2 | 100% | 0 | 0 |
| garantie : 2.1 | 13 | 77% | 2 ⚠ | 0 |
| garantie : 2.10 | 40 | 70% | 6 ⚠ | 1 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.12 | 1 | 100% | 0 | 0 |
| garantie : 2.2 | 6 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 50% | 0 | 1 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.5 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 4 | 100% | 0 | 0 |
| garantie : 2.7 | 16 | 56% | 1 ⚠ | 2 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 7 | 86% | 0 | 1 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 24 | 92% | 0 | 2 |
| thème : info_manquante | 16 | 62% | 3 ⚠ | 0 |
| thème : langue | 11 | 91% | 0 | 0 |
| thème : multi | 8 | 88% | 0 | 0 |
| thème : piege | 55 | 66% | 8 ⚠ | 4 |
| thème : variante | 13 | 77% | 2 ⚠ | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `bougie-03` attendu NC, obtenu C C ? — Une bougie posée sur la table du salon a coulé et laissé une marque de brûlure superficielle, sans flammes. *(Brûlure sans flammes : « les brûlures » ne constituent pas un incendie (12/incendie).)*
- **⚠ couvert à tort** `bougie-04` attendu NC, obtenu C NC C — Pendant mes vacances, une bougie laissée sur la table du jardin s'est enflammée et a brûlé la table et le salo… *(Vrai incendie, mais table et salon de jardin = contenu du jardin, exclu du contenu assuré (12/contenu). INCERTAIN défend)*
- **⚠ couvert à tort** `val-01` attendu NC, obtenu C C C — Pendant que j'étais au travail, quelqu'un est entré par la fenêtre de ma chambre, au rez-de-chaussée, que j'av… *(Obligation de prévention (2.10) : en cas d'absence, « fermer correctement les fenêtres […] facilement accessibles ». Lie)*
- **⚠ couvert à tort** `val-03` attendu NC, obtenu C NC NC — Des amis que j'hébergeais pour le week-end se sont fait voler leur ordinateur lors d'un cambriolage de mon app… *(Exclusion 2.10 : le vol des biens appartenant à des hôtes (alors que la définition du contenu les inclut : piège).)*
- **⚠ couvert à tort** `val-10` attendu NC, obtenu C C C — En janvier, je suis parti deux semaines en coupant le chauffage. Une canalisation a gelé puis éclaté ; l'eau a… *(2.7 : en période de gel, maintenir une température positive, vidanger ou isoler ; refus s'il y a un lien causal direct. )*
- **⚠ couvert à tort** `red-b05` attendu NC, obtenu NC NC C — Le grand miroir que je venais d'acheter, encore dans son carton et pas encore accroché, s'est brisé quand je l… *(Exclusion 2.9 : les dommages aux vitres et biens assimilés non placés.)*
- **⚠ couvert à tort** `g-q02` attendu ?, obtenu C C C — Mon ordinateur portable a disparu de mon appartement. *(« Disparu » n'est pas « volé » : la simple disparition est exclue ; il faut établir le vol.)*
- **⚠ couvert à tort** `g-q03` attendu ?, obtenu C C C — Mon vélo a été volé pendant que je faisais mes courses. *(Le lieu décide (dans le bâtiment ou dehors) : il faut le demander.)*
- **⚠ couvert à tort** `g-p03` attendu NC, obtenu C C C — Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune… *(Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct.)*
- **⚠ couvert à tort** `g2-i04` attendu ?, obtenu C C C — Mes bijoux ont disparu de ma chambre après le passage du plombier. *(Une disparition n'est pas un vol établi (simple disparition exclue) ; et un vol par une personne autorisée à se trouver )*
- **⚠ couvert à tort** `g2-i13` attendu NC, obtenu NC C C — Le joint de la douche fuyait depuis des mois ; l'eau a fini par abîmer le mur de la salle de bain. *(Exclusion générale 1.4 : manque d'entretien, détérioration lente et progressive.)*
- **⚠ couvert à tort** `g2-p12` attendu NC, obtenu NC C C — Énervé, j'ai donné un coup de poing dans la vitre de la porte-fenêtre, qui s'est brisée. *(Exclusion générale 1.4 : un sinistre intentionnel dont l'assuré est l'auteur.)*
- `velo-06` attendu NC, obtenu ? ? ? — Mon vélo était attaché à un arceau dans la rue avec un antivol. L'antivol a été coupé et le vélo volé. *(Vol dans la rue, sans violence : hors du bâtiment, et ce n'est pas un « vol commis sur l'assuré … suite à violences ».)*
- `autre-02` attendu C, obtenu ? ? ? — Le tuyau du lave-linge a cédé et l'eau a abîmé le parquet et le canapé. *(Dégâts des eaux couverts (2.7) ; le tuyau à l'origine est exclu (2.7-b) mais sa réparation relève des garanties compléme)*
- `val-09` attendu NC, obtenu ? ? ? — Mon fer à repasser, laissé à plat sur la planche, a brûlé la housse et laissé une marque sur le tissu, sans fl… *(Définition de l'incendie : les brûlures et le contact d'une source de chaleur sans embrasement ne sont pas un incendie.)*
- `val-12` attendu C, obtenu NC NC NC — Ma baignoire a débordé pendant que j'étais au téléphone ; l'eau a abîmé mon parquet. *(2.7 couvre l'ensemble des dégâts des eaux ; l'exclusion du récipient vise un récipient NON relié à l'installation hydrau)*
- `red-b01` attendu C, obtenu NC NC NC — Mon fils a cassé la vitre de la porte-fenêtre du salon avec un ballon. *(2.9 : le bris de vitres.)*
- `g-l05` attendu C, obtenu ? C C — Fuite d'eau sous l'évier : le meuble de cuisine a gonflé et le parquet est abîmé. *(2.7 : l'ensemble des dommages causés par l'eau.)*
- `g-l06` attendu C, obtenu C ? C — Deux types m'ont bousculé à la sortie du bus et m'ont arraché mon sac avec mon portefeuille dedans. *(2.10 : vol commis sur l'assuré, en dehors des biens assurés, avec violences.)*
- `g-p04` attendu C, obtenu ? ? ? — Le chauffe-eau a fui ; le parquet est abîmé et le chauffe-eau lui-même est hors d'usage. *(2.7 : le parquet est couvert ; le chauffe-eau à l'origine du sinistre est exclu (exclusion partielle).)*
- `g-p05` attendu C, obtenu NC NC NC — L'aquarium du salon s'est brisé et l'eau a abîmé le parquet. *(2.7 : l'exclusion du récipient non relié excepte l'aquarium.)*
- `g-h05` attendu C, obtenu NC NC NC — Les égouts publics ont refoulé pendant un gros orage et l'eau sale a envahi la salle de bain. *(2.3 : le refoulement d'égouts publics est une catastrophe naturelle couverte ; 2.7 l'exclut. Non traduite.)*
- `g-m02` attendu C, obtenu C NC C — Un incendie chez le voisin s'est propagé à mon appartement ; les pompiers ont inondé le salon en l'éteignant. *(2.1 : incendie ; l'eau d'extinction en est la conséquence.)*
- `g2-i01` attendu ?, obtenu NC NC NC — Mon vélo a été volé dans le local de mon immeuble. *(« Le local de mon immeuble » : local commun (vol exclu dans les parties communes) ou cave privative (couverte si serrure)*
- `g2-i02` attendu ?, obtenu NC NC NC — On a cambriolé mon appartement pendant le week-end où j'étais absent. La serrure porte des rayures, mais la po… *(Des traces sans réparation nécessaire ne sont pas une effraction (définition). Sans effraction, l'obligation de fermer à)*
- `g2-i03` attendu ?, obtenu NC NC NC — Une tache d'humidité est apparue au plafond de ma chambre, juste sous la salle de bain du voisin du dessus. *(2.7 couvre l'ensemble des dégâts des eaux, mais la condensation et certaines infiltrations sont exclues : la cause est à)*
- `g2-i11` attendu ?, obtenu C ? C — Après le gros coup de vent d'hier, des tuiles de l'immeuble sont tombées sur mon balcon et l'ont abîmé. *(La tempête suppose un vent d'au moins 80 km/h ou des dégâts aux biens voisins (définition) : non précisé. Garantie 2.2 n)*
- `g2-i12` attendu ?, obtenu ? C C — Pendant mes vacances, quelqu'un est entré chez moi et a volé ma télévision ; je ne sais pas comment il est ent… *(Vol dans le bâtiment couvert ; sans effraction connue, l'obligation de fermer à clé pendant l'absence est à vérifier.)*
- `g2-i16` attendu C, obtenu ? ? C — De l'eau de mon appartement s'est infiltrée chez le voisin du dessous, qui me demande de payer ses réparations… *(2.5 : responsabilité civile du fait du bâtiment et du contenu envers les tiers. Garantie non traduite.)*
- `g2-p01` attendu C, obtenu NC NC C — Pendant mes vacances, des cambrioleurs ont ouvert ma porte sans la casser : il n'y a que des traces de tournev… *(Pas d'effraction au sens du contrat, mais la porte était fermée à clé : l'obligation est respectée, le vol dans le bâtim)*
- `g2-i07` attendu NC, obtenu ? ? ? — Mon ordinateur portable a été volé dans ma voiture, garée devant chez moi. *(La voiture n'est pas le bâtiment, et ce n'est pas un vol commis sur l'assuré avec violences.)*
- `g2-p04` attendu NC, obtenu ? ? ? — On a siphonné le fioul de la cuve de chauffage, dans ma cave. *(Exclusion 2.10 : le vol de mazout de chauffage.)*
- `g2-m02` attendu C, obtenu C ? ? — La tempête a cassé la fenêtre du salon et la pluie a abîmé le canapé. *(La vitre est couverte par le bris de vitrages (2.9) ; le canapé relève de la tempête (2.2), non traduite.)*
