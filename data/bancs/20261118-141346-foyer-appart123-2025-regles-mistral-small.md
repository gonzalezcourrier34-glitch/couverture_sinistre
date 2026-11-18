# Banc d'essai — foyer-appart123-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (en parallele)

2026-11-18T14:06:37 · golden set v6 (97 cas, empreinte `0b83f83b91580639`) · cas validés par l'auteur : 0 sur 97


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 0.8 | ✓ |
| lecture | decisions_changees | ≤ 2 | 25.33 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 17 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 18 | ✗ |
| chaine | faux_couverts | ≤ 0 | 11.667 | ✗ |
| chaine | faux_refus | ≤ 1 | 1.667 | ✗ |
| chaine | exactitude | ≥ 0.85 | 0.801 | ✗ |
| chaine | instables | ≤ 3 | 13 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 0.485 | ✗ |

## Depuis le banc précédent (2026-11-18T13:43:42)

- lecture · rappel_faits : 0.895 → 0.805
- chaine · exactitude : 0.849 → 0.801
- chaine · exactitude_stricte : 0.636 → 0.598
- chaine · faux_couverts : 3.333 → 11.667
- chaine · faux_refus : 2.667 → 1.667

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

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **25.33** par exécution, dont **17** cas vers un couvert à tort.

Rappel des faits idéaux : 80% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 18 cas · faits vagues : 1 cas · faits en trop : 22 cas · faits retirés faute d'appui : 0 cas

### La lecture change la décision

- **⚠ vers couvert** `bougie-03` idéal NC, lu NC NC C · **contredit** : evenement : autre lu fumee · manque : embrasement = non; flammes = non
- **⚠ vers couvert** `val-01` idéal ?, lu C C C · manque : absence = oui; effraction = non; portes_fermees = oui; vol_sur_personne = non · en trop : auteur = tiers; fermeture = aucune; fermeture = cle
- **⚠ vers couvert** `val-02` idéal NC, lu C C NC · **contredit** : auteur : personnel_prive lu tiers · manque : effraction = non; vol_sur_personne = non · en trop : proprietaire = assure
- **⚠ vers couvert** `val-03` idéal NC, lu NC C NC · manque : proprietaire = hote; vol_sur_personne = non · en trop : auteur = tiers; fermeture = cle
- **⚠ vers couvert** `val-05` idéal NC, lu NC C C · manque : absence = oui; effraction = non; simple_disparition = oui; vol_sur_personne = non
- **⚠ vers couvert** `val-09` idéal NC, lu C C C · **contredit** : bien : objet_divers lu mobilier; evenement : autre lu fumee · manque : embrasement = non; flammes = non
- **⚠ vers couvert** `val-10` idéal NC, lu C NC C · manque : absence = oui; prevention_gel = non
- **⚠ vers couvert** `val-11` idéal NC, lu C C C · manque : cause_eau = infiltration_exterieure
- **⚠ vers couvert** `red-b05` idéal NC, lu C NC C · manque : vitre_placee = non · en trop : cause_dommage = autre; type_dommage = bris
- **⚠ vers couvert** `g-q02` idéal ?, lu C C C · en trop : evenement = vol
- **⚠ vers couvert** `g-q03` idéal ?, lu C C C · en trop : lieu = logement
- **⚠ vers couvert** `g-p03` idéal ?, lu C C C · **contredit** : bien : objet_divers lu cles · manque : absence = oui; effraction = non; portes_fermees = oui · en trop : fermeture = cle
- **⚠ vers couvert** `g-h04` idéal ?, lu C ? C · manque : cause_eau = inondation
- **⚠ vers couvert** `g2-i04` idéal ?, lu C C C · en trop : auteur = tiers; evenement = vol
- **⚠ vers couvert** `g2-i16` idéal ?, lu NC C NC · en trop : bien = element_batiment; cause_eau = fuite_installation; cause_eau = infiltration_exterieure
- **⚠ vers couvert** `g2-i13` idéal NC, lu NC NC C · manque : manque_entretien = oui
- **⚠ vers couvert** `g2-p12` idéal NC, lu C C C · manque : auteur = assure; intentionnel = oui
- `velo-03` idéal NC, lu ? ? ? · **contredit** : fermeture : cadenas lu cle · manque : vol_sur_personne = non
- `velo-04` idéal NC, lu ? NC ? · manque : effraction = non; fermeture = aucune; vol_sur_personne = non
- `velo-06` idéal NC, lu ? ? ? · manque : fermeture = cadenas; violence = non; vol_sur_personne = non
- `bougie-04` idéal NC, lu NC NC ? · manque : absence = oui
- `autre-01` idéal C, lu ? ? ? · manque : violence = oui
- `val-12` idéal C, lu NC NC NC · **contredit** : cause_eau : fuite_installation lu debordement_recipient
- `val-14` idéal NC, lu ? ? ? · manque : vol_sur_personne = non
- `red-b06` idéal NC, lu ? ? ? · **contredit** : evenement : bris lu vandalisme · manque : type_dommage = rayure_ou_ecaillement
- `g2-i01` idéal ?, lu NC NC NC · en trop : lieu = parties_communes
- `g2-i03` idéal C, lu NC NC C · en trop : cause_eau = infiltration_exterieure
- `g2-p01` idéal C, lu C ? C · **contredit** : bien : objet_divers lu cles; bien : objet_divers lu element_batiment; effraction : non lu oui · manque : absence = oui; portes_fermees = oui · en trop : fermeture = cle
- `g2-i07` idéal NC, lu ? ? ? · manque : lieu = voie_publique; vol_sur_personne = non
- `g2-p04` idéal NC, lu ? ? ? · **contredit** : evenement : vol lu mazout
- `g2-l03` idéal C, lu ? ? ? · manque : bien = objet_divers · en trop : portes_fermees = oui

### Contradictions sans effet sur la décision

- `bougie-01` : evenement : autre lu degat_eaux
- `red-t03` : lieu : garage lu jardin
- `g-l07` : evenement : autre lu bris
- `g-p07` : flammes : oui lu non
- `g-h02` : bien : objet_divers lu electronique
- `g-h03` : bien : element_batiment lu mazout
- `g2-i02` : bien : objet_divers lu cles; effraction : non lu oui
- `g2-i08` : lieu : autre_batiment lu voie_publique
- `g2-i11` : lieu : terrasse lu logement

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 80% (79% – 80%) | 60% (58% – 61%) | **11.667 (11 – 13)** | **1.667 (1 – 2)** | 26% (26% – 27%) |

Instables : **13** sur 97 · rappel des clauses : 61% · rappel des questions : 48% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 114.3 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 97 | 80% | 11 ⚠ | 2 |
| garantie : 1.4 | 2 | 50% | 1 ⚠ | 0 |
| garantie : 2.1 | 13 | 92% | 1 ⚠ | 0 |
| garantie : 2.10 | 40 | 72% | 6 ⚠ | 0 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.12 | 1 | 100% | 0 | 0 |
| garantie : 2.2 | 6 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.5 | 1 | 0% | 0 | 1 |
| garantie : 2.6 | 4 | 100% | 0 | 0 |
| garantie : 2.7 | 16 | 75% | 2 ⚠ | 1 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 7 | 86% | 1 ⚠ | 0 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 24 | 92% | 1 ⚠ | 1 |
| thème : info_manquante | 16 | 69% | 3 ⚠ | 0 |
| thème : langue | 11 | 100% | 0 | 0 |
| thème : multi | 8 | 100% | 0 | 0 |
| thème : piege | 55 | 73% | 10 ⚠ | 1 |
| thème : variante | 13 | 92% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `bougie-03` attendu NC, obtenu NC NC C — Une bougie posée sur la table du salon a coulé et laissé une marque de brûlure superficielle, sans flammes. *(Brûlure sans flammes : « les brûlures » ne constituent pas un incendie (12/incendie).)*
- **⚠ couvert à tort** `val-01` attendu NC, obtenu C C C — Pendant que j'étais au travail, quelqu'un est entré par la fenêtre de ma chambre, au rez-de-chaussée, que j'av… *(Obligation de prévention (2.10) : en cas d'absence, « fermer correctement les fenêtres […] facilement accessibles ». Lie)*
- **⚠ couvert à tort** `val-02` attendu NC, obtenu C C NC — Ma femme de ménage, qui a les clés de l'appartement, m'a volé une bague en or estimée à 2 000 €. *(Exclusion 2.10 : le vol commis par des personnes au service privé de l'assuré.)*
- **⚠ couvert à tort** `val-03` attendu NC, obtenu NC C NC — Des amis que j'hébergeais pour le week-end se sont fait voler leur ordinateur lors d'un cambriolage de mon app… *(Exclusion 2.10 : le vol des biens appartenant à des hôtes (alors que la définition du contenu les inclut : piège).)*
- **⚠ couvert à tort** `val-05` attendu NC, obtenu NC C C — Au retour de vacances, je ne retrouve plus ma montre de valeur. Aucune trace de passage ni d'effraction dans l… *(2.10 : « le vol du contenu situé dans le bâtiment sauf la simple disparition ».)*
- **⚠ couvert à tort** `val-09` attendu NC, obtenu C C C — Mon fer à repasser, laissé à plat sur la planche, a brûlé la housse et laissé une marque sur le tissu, sans fl… *(Définition de l'incendie : les brûlures et le contact d'une source de chaleur sans embrasement ne sont pas un incendie.)*
- **⚠ couvert à tort** `val-10` attendu NC, obtenu C NC C — En janvier, je suis parti deux semaines en coupant le chauffage. Une canalisation a gelé puis éclaté ; l'eau a… *(2.7 : en période de gel, maintenir une température positive, vidanger ou isoler ; refus s'il y a un lien causal direct. )*
- **⚠ couvert à tort** `val-11` attendu NC, obtenu C C C — Pendant un orage, la pluie s'est infiltrée par la fenêtre mal jointée de ma chambre et a abîmé le mur et la mo… *(Exclusion 2.7 : une infiltration par les fenêtres, autre que celle due à une fuite des installations hydrauliques extéri)*
- **⚠ couvert à tort** `red-b05` attendu NC, obtenu C NC C — Le grand miroir que je venais d'acheter, encore dans son carton et pas encore accroché, s'est brisé quand je l… *(Exclusion 2.9 : les dommages aux vitres et biens assimilés non placés.)*
- **⚠ couvert à tort** `g-q02` attendu ?, obtenu C C C — Mon ordinateur portable a disparu de mon appartement. *(« Disparu » n'est pas « volé » : la simple disparition est exclue ; il faut établir le vol.)*
- **⚠ couvert à tort** `g-q03` attendu ?, obtenu C C C — Mon vélo a été volé pendant que je faisais mes courses. *(Le lieu décide (dans le bâtiment ou dehors) : il faut le demander.)*
- **⚠ couvert à tort** `g-p03` attendu NC, obtenu C C C — Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune… *(Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct.)*
- **⚠ couvert à tort** `g2-i04` attendu ?, obtenu C C C — Mes bijoux ont disparu de ma chambre après le passage du plombier. *(Une disparition n'est pas un vol établi (simple disparition exclue) ; et un vol par une personne autorisée à se trouver )*
- **⚠ couvert à tort** `g2-i13` attendu NC, obtenu NC NC C — Le joint de la douche fuyait depuis des mois ; l'eau a fini par abîmer le mur de la salle de bain. *(Exclusion générale 1.4 : manque d'entretien, détérioration lente et progressive.)*
- **⚠ couvert à tort** `g2-p12` attendu NC, obtenu C C C — Énervé, j'ai donné un coup de poing dans la vitre de la porte-fenêtre, qui s'est brisée. *(Exclusion générale 1.4 : un sinistre intentionnel dont l'assuré est l'auteur.)*
- `velo-04` attendu NC, obtenu ? NC ? — Mon vélo a été volé dans ma cave privative. J'avais oublié de la fermer à clé et il n'y a aucune trace d'effra… *(Cave non fermée : pas de serrure de sûreté (condition du plafond caves), et obligation de prévention non respectée avec )*
- `velo-06` attendu NC, obtenu ? ? ? — Mon vélo était attaché à un arceau dans la rue avec un antivol. L'antivol a été coupé et le vélo volé. *(Vol dans la rue, sans violence : hors du bâtiment, et ce n'est pas un « vol commis sur l'assuré … suite à violences ».)*
- `bougie-04` attendu NC, obtenu NC NC ? — Pendant mes vacances, une bougie laissée sur la table du jardin s'est enflammée et a brûlé la table et le salo… *(Vrai incendie, mais table et salon de jardin = contenu du jardin, exclu du contenu assuré (12/contenu). INCERTAIN défend)*
- `val-12` attendu C, obtenu NC NC NC — Ma baignoire a débordé pendant que j'étais au téléphone ; l'eau a abîmé mon parquet. *(2.7 couvre l'ensemble des dégâts des eaux ; l'exclusion du récipient vise un récipient NON relié à l'installation hydrau)*
- `val-14` attendu NC, obtenu ? ? ? — Lors d'un cambriolage avec la porte fracturée, on m'a volé mon chat de race. *(Exclusion 2.10 : le vol des animaux.)*
- `g-h04` attendu C, obtenu C ? C — Après des pluies exceptionnelles, la rivière a débordé et l'eau a envahi mon appartement au rez-de-chaussée. *(2.3 : l'inondation est couverte par les catastrophes naturelles, alors que 2.7 l'exclut. Non traduite.)*
- `g2-i01` attendu ?, obtenu NC NC NC — Mon vélo a été volé dans le local de mon immeuble. *(« Le local de mon immeuble » : local commun (vol exclu dans les parties communes) ou cave privative (couverte si serrure)*
- `g2-i03` attendu ?, obtenu NC NC C — Une tache d'humidité est apparue au plafond de ma chambre, juste sous la salle de bain du voisin du dessus. *(2.7 couvre l'ensemble des dégâts des eaux, mais la condensation et certaines infiltrations sont exclues : la cause est à)*
- `g2-i16` attendu C, obtenu NC C NC — De l'eau de mon appartement s'est infiltrée chez le voisin du dessous, qui me demande de payer ses réparations… *(2.5 : responsabilité civile du fait du bâtiment et du contenu envers les tiers. Garantie non traduite.)*
- `g2-p01` attendu C, obtenu C ? C — Pendant mes vacances, des cambrioleurs ont ouvert ma porte sans la casser : il n'y a que des traces de tournev… *(Pas d'effraction au sens du contrat, mais la porte était fermée à clé : l'obligation est respectée, le vol dans le bâtim)*
- `g2-i07` attendu NC, obtenu ? ? ? — Mon ordinateur portable a été volé dans ma voiture, garée devant chez moi. *(La voiture n'est pas le bâtiment, et ce n'est pas un vol commis sur l'assuré avec violences.)*
- `g2-p04` attendu NC, obtenu ? ? ? — On a siphonné le fioul de la cuve de chauffage, dans ma cave. *(Exclusion 2.10 : le vol de mazout de chauffage.)*
