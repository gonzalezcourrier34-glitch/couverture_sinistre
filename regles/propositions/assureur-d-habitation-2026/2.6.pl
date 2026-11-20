% --- Art. 2.6 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(vandalisme).
evenement_traduit(vol).
garantie(deteriorations_immobilieres, "Détériorations immobilières", '2.6-a',
    "La garantie couvre la détérioration de : - vos biens immobiliers…à la suite d’un acte de vandalisme, d’une tentative de vol ou d’un vol").
perimetre(deteriorations_immobilieres, ou([f(evenement, vandalisme), f(evenement, vol)])).
perimetre(deteriorations_immobilieres, f(bien, element_batiment)).
perimetre(deteriorations_immobilieres, concept(batiment)).
circonstance(deteriorations_immobilieres, si(ou([f(lieu, logement), f(lieu, grenier), f(lieu, cave), f(lieu, garage), f(lieu, annexe), f(lieu, abri_jardin)]), ou([f(effraction, oui), f(acces_voleur, escalade), f(acces_voleur, menaces), f(acces_voleur, cles_volees), f(acces_voleur, fausse_qualite)])), '2.6-a',
    "Si les dommages sont commis à l’intérieur de votre habitation ou de ses dépendances, les détériorations doivent être commises à la suite : - de l’effraction ou de l’escalade des locaux assurés, ayant laissé des traces apparentes, - de menaces physiques ou violences physiques, - du vol des clés, - de l’introduction par fausse qualité").
exclusion(deteriorations_immobilieres, et([ou([f(auteur, famille), f(auteur, personnel_prive)]), non(f(plainte_deposee, oui))]), tout, oui, '2.6-b',
    "les vols, tentatives de vol ou actes de vandalisme dont seraient auteurs ou complices les membres de votre famille (article 311-12 du Code pénal) ou vos préposés pendant leur service, sauf si une plainte nominative est déposée à leur encontre").
exclusion(deteriorations_immobilieres, f(graffiti_mur_exterieur, oui), tout, oui, '2.6-b',
    "les graffitis, tags, pochoirs et inscriptions de toute nature, affichages, salissures, rayures commis à l’extérieur de votre local d’habitation et de ses dépendances").
