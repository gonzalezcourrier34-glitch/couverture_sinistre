% --- Art. 2.5 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(vol).
evenement_traduit(vandalisme).
garantie(vol_vandalisme, "Vol, tentative de vol, vandalisme", '2.5-a',
    "La garantie couvre la disparition, la destruction ou la détérioration des biens assurés résultant : • d’un vol, • d’une tentative de vol, • d ’un acte de vandalisme ou de sabotage").
perimetre(vol_vandalisme, ou([f(evenement, vol), f(evenement, vandalisme)])).
perimetre(vol_vandalisme, concept(contenu)).
perimetre(vol_vandalisme, concept(batiment)).
circonstance(vol_vandalisme, ou([f(effraction, oui), f(acces_voleur, escalade), f(acces_voleur, menaces), f(acces_voleur, cles_volees), f(acces_voleur, fausse_qualite)]), '2.5-a',
    "lorsque ces méfaits sont commis à l’intérieur des locaux assurés, par effraction ou escalade de ces locaux…au vol dans les locaux assurés par menaces physiques…au vol à la suite du vol des clés…au vol à la suite d’une introduction par fausse qualité").
exclusion(vol_vandalisme, et([ou([f(auteur, famille), f(auteur, personnel_prive)]), non(f(plainte_deposee, oui))]), tout, oui, '2.5-c',
    "les vols, tentatives de vol, actes de vandalisme ou actes de sabotage dont seraient auteurs ou complices les membres de votre famille (article 311-12 du Code pénal) ou vos préposés pendant leur service, sauf si une plainte nominative est déposée à leur encontre").
exclusion(vol_vandalisme, f(cles_deposees_exterieur, oui), tout, non, '2.5-c',
    "les vols des clés déposées, sans protection, à l’extérieur des locaux y compris dans une boîte à clé ou dans une boîte à lettres ainsi que toutes leurs conséquences").
exclusion(vol_vandalisme, et([f(bien, bijoux), ou([f(lieu, cave), f(lieu, garage), f(lieu, annexe), f(lieu, abri_jardin)])]), bien(bijoux), non, '2.5-c',
    "l es vols des objets précieux dans les dépendances").
exclusion(vol_vandalisme, et([f(bien, valeurs), ou([f(lieu, cave), f(lieu, garage), f(lieu, annexe), f(lieu, abri_jardin)])]), bien(valeurs), non, '2.5-c',
    "l es vols des objets précieux dans les dépendances").
exclusion(vol_vandalisme, et([ou([f(lieu, cave), f(lieu, garage), f(lieu, annexe), f(lieu, abri_jardin)]), f(formule, eco)]), tout, oui, '2.5-c',
    "les vols dans les dépendances, si vous avez souscrit la formule Eco").
exclusion(vol_vandalisme, f(construction_close, non), tout, non, '2.5-c',
    "les vols, tentatives de vol, actes de vandalisme ou actes de sabotage commis sur les terrasses, les balcons, dans les jardins et dans les locaux non entièrement clos ou couverts").
limite(vol_vandalisme, '4.1', "Si l’introduction a été facilitée ou aggravée par la nonconformité ou l’absence de mise en œuvre des moyens de protection et/ou de fermeture exigés aux conditions particulières, l’indemnité sera réduite de 50 %", "indemnité réduite de 50 %").
garantie(vol_cles, "Vol des clés (Confort et Excellence)", '2.5-a',
    "au vol des clés, en tous lieux de l’Union européenne, du Royaume-Uni de Grande-Bretagne et d’Irlande du Nord, de votre local d’habitation et/ou des dépendances assurés dès lors que le dépôt de plainte fait état d’un vol").
perimetre(vol_cles, f(evenement, vol)).
perimetre(vol_cles, f(bien, cles)).
circonstance(vol_cles, f(plainte_deposee, oui), '2.5-a',
    "dès lors que le dépôt de plainte fait état d’un vol").
circonstance(vol_cles, ou([f(formule, confort), f(formule, excellence)]), '2.5-a',
    "Extensions de garantie pour les formules Confort et Excellence").
exclusion(vol_cles, f(cles_deposees_exterieur, oui), tout, non, '2.5-c',
    "les vols des clés déposées, sans protection, à l’extérieur des locaux y compris dans une boîte à clé ou dans une boîte à lettres").
