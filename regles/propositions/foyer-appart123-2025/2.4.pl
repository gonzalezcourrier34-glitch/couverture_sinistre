% --- Art. 2.4 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-18 ---
evenement_traduit(attentat).
evenement_traduit(conflit_du_travail).
definition(conflit_du_travail, f(evenement, conflit_du_travail), '12/conflit-du-travail',
    "Toute contestation collective sous quelque forme qu’elle se manifeste dans le cadre des relations du travail, en ce compris : • la grève : arrêt concerté du travail par un groupe de salariés, employés, fonctionnaires ou indépendants • le lock-out : fermeture provisoire décidée par une entreprise afin d’amener son personnel à composer dans un «conflit du travail».").
garantie(attentat_conflit_travail, "Attentat et conflit du travail", '2.4',
    "Nous prenons en charge exclusivement sous cette garantie : • la destruction des biens assurés ou leur détérioration par des personnes prenant part à un attentat ou à un conflit du travail • les conséquences des mesures prises par une autorité légalement constituée pour la sauvegarde et la protection de ces biens, lors de tels événements.").
perimetre(attentat_conflit_travail, ou([f(evenement, attentat), f(evenement, conflit_du_travail)])).
perimetre(attentat_conflit_travail, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(attentat_conflit_travail, concept(batiment)).
limite(attentat_conflit_travail, '2.4', "Notre garantie est limitée aux montants assurés et en tout état de cause à 1.497.671,24 EUR.", "1497671.24 EUR").
exclusion([attentat_conflit_travail], f(cause_nucleaire, oui), tout, oui, '2.4-a',
    "les dommages causés par des armes ou des engins destinés à exploser par une modification de structure du noyau atomique").
exclusion([attentat_conflit_travail], f(graffiti_mur_exterieur, oui), tout, oui, '2.4-a',
    "les graffitis et autres inscriptions sur les murs extérieurs").
exclusion([attentat_conflit_travail], et([f(evenement, vandalisme), ou([f(bien, mobilier_jardin), f(bien, serre), f(bien, plantation)])]), tout, non, '2.4-a',
    "le vandalisme au mobilier extérieur, serres, plantations").
