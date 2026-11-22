% --- Art. S2 : proposition rédigée par le modèle — mistral:mistral-large-4-0, 2026-11-22 ---
definition(batiment_assure, ou([et([f(formule, initiale), f(statut_logement, proprietaire)]), et([f(formule, initiale), f(statut_logement, coproprietaire)]), et([f(formule, confort), f(statut_logement, proprietaire)]), et([f(formule, confort), f(statut_logement, coproprietaire)]), et([f(formule, optimale), f(statut_logement, proprietaire)]), et([f(formule, optimale), f(statut_logement, coproprietaire)])]), 'S2-a',
    "Si vous êtes propriétaire, le bâtiment désigné dans vos Conditions Particulières au paragraphe « L’habitation assurée ». Si vous êtes copropriétaire, vous êtes également couvert pour votre quote-part dans les parties communes.").
definition(contenu_assure, et([f(formule, initiale), ou([f(statut_logement, locataire), f(statut_logement, proprietaire), f(statut_logement, coproprietaire)]), ou([concept(objets_usuels), concept(amenagements_immobiliers)]), f(lieu, logement), ou([f(proprietaire, assure), f(bien_confie, oui)])]), 'S2-a',
    "Si vous êtes locataire, propriétaire ou copropriétaire : les objets usuels pour les montants précisés dans vos Conditions Particulières, les aménagements immobiliers réalisés à vos frais. Ces biens doivent se trouver à l’intérieur du bâtiment assuré. Ils doivent appartenir aux personnes assurées ou leur avoir été confiés.").
definition(amenagements_immobiliers, f(bien, element_batiment), 'S1/amenagements-immobiliers',
    "Ils comprennent : - toutes les installations fixes de chauffage, de climatisation, d’alarme, les placards intégrés ainsi que les éléments fixes de cuisine et de salle de bains, - tous les revêtements de sols, de murs et de plafonds. Les appareils électroménagers, même encastrés, sont considérés comme des éléments mobiliers.").
extension(contenu_assure, et([ou([f(domaine_litige, defense_penale), f(domaine_litige, recours_dommage)]), non(f(pack_souscrit, oui))]), 'S2-a',
    "toutefois, pour la garantie Défense Pénale et Recours Suite à Accident, les biens de l’assuré situés à l’extérieur des bâtiments assurés seront garantis, à l’exception de ceux qui auraient pu être pris en charge au titre d’un pack").
exclusion(tous, f(bien, vehicule_moteur), tout, oui, 'S2-b',
    "Les véhicules terrestres à moteur soumis à l’obligation d’assurance de l’article L 211-1 du Code des assurances.").
exclusion(tous, f(bien, caravane), tout, oui, 'S2-b',
    "Les caravanes, les bateaux à voile ou à moteur, les jets ski.").
exclusion(tous, f(bien, bateau), tout, oui, 'S2-b',
    "Les caravanes, les bateaux à voile ou à moteur, les jets ski.").
exclusion(tous, f(bien, jet_ski), tout, oui, 'S2-b',
    "Les caravanes, les bateaux à voile ou à moteur, les jets ski.").
exclusion(tous, f(bien, mobil_home), tout, oui, 'S2-b',
    "Les mobil-homes, les manoirs, les châteaux, les monuments historiques ou inscrits à l’inventaire supplémentaire des monuments historiques.").
exclusion(tous, f(bien, manoir), tout, oui, 'S2-b',
    "Les mobil-homes, les manoirs, les châteaux, les monuments historiques ou inscrits à l’inventaire supplémentaire des monuments historiques.").
exclusion(tous, f(bien, chateau), tout, oui, 'S2-b',
    "Les mobil-homes, les manoirs, les châteaux, les monuments historiques ou inscrits à l’inventaire supplémentaire des monuments historiques.").
exclusion(tous, f(bien, monument_historique), tout, oui, 'S2-b',
    "Les mobil-homes, les manoirs, les châteaux, les monuments historiques ou inscrits à l’inventaire supplémentaire des monuments historiques.").
exclusion(tous, f(bien, valeurs), tout, oui, 'S2-b',
    "Les fonds et valeurs : il s’agit des billets de banque, pièces de monnaie, lingots d’or et d’argent, titres et valeurs mobilières, moyens de paiements.").
exclusion(tous, f(bien, animal), tout, oui, 'S2-b',
    "Les animaux.").
exclusion(tous, f(bien, collection), tout, oui, 'S2-b',
    "Les collections de timbres, de monnaie ou de médailles.").
exclusion(tous, f(terrain_non_constructible, oui), tout, oui, 'S2-b',
    "Les bâtiments et leur contenu construits dans une zone qui a été, préalablement à leur construction, déclarée inconstructible en vertu des règles légales ou administratives visant à prévenir les conséquences des catastrophes naturelles (Plan de Prévention des Risques, Plan d’Exposition aux Risques ou autres règles administratives en vigueur lors de la construction).").
exclusion(tous, f(batiment_inoccupe_10_ans_avant_souscription, oui), tout, oui, 'S2-b',
    "Les bâtiments inoccupés en permanence depuis plus de 10 ans avant la souscription.").
