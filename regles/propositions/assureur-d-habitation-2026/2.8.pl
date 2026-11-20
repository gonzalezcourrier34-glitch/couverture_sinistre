% --- Art. 2.8 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(electricite).
garantie(contenu_congelateur, "Contenu du congélateur et/ou réfrigérateur", '2.8-b',
    "La garantie couvre les pertes ou détériorations causes aux denrées alimentaires contenues dans les congélateurs et/ou réfrigérateurs endommagés").
perimetre(contenu_congelateur, f(evenement, electricite)).
perimetre(contenu_congelateur, f(bien, denrees_alimentaires)).
perimetre(contenu_congelateur, concept(batiment)).
circonstance(contenu_congelateur, f(formule, excellence), '2.8-b',
    "La garantie couvre les pertes ou détériorations causes aux denrées alimentaires").
circonstance(contenu_congelateur, ou([f(cause_perte_alimentaire, coupure_soudaine_reseau), f(cause_perte_alimentaire, derangement_installation)]), '2.8-b',
    "à l’occasion d’un sinistre dommages électrique indemnisé (ART 2-2), à la suite d’un sinistre indemnisé au titre de la garantie panne électroménager (TITRE III) ou d’une coupure électrique accidentelle avec justificatif de votre fournisseur d’électricité").
exclusion(contenu_congelateur, f(manque_entretien, oui), tout, non, '2.8-c',
    "dues à un mauvais entretien ou à une utilisation non conforme du congélateur et/ou réfrigérateur aux instructions du fabricant").
