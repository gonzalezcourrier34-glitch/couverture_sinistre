% --- Art. S2-b : proposition rédigée par le modèle — mistral:mistral-large-4-0, 2026-11-22 ---
exclusion(tous, f(bien, vehicule_moteur), bien(vehicule_moteur), non, 'S2-b',
    "Les véhicules terrestres à moteur soumis à l’obligation d’assurance de l’article L 211-1 du Code des assurances.").
exclusion(tous, f(bien, caravane), bien(caravane), non, 'S2-b',
    "Les caravanes, les bateaux à voile ou à moteur, les jets ski.").
exclusion(tous, f(bien, bateau), bien(bateau), non, 'S2-b',
    "Les caravanes, les bateaux à voile ou à moteur, les jets ski.").
exclusion(tous, f(habitation_non_assuree, oui), tout, non, 'S2-b',
    "Les mobil-homes, les manoirs, les châteaux, les monuments historiques ou inscrits à l’inventaire supplémentaire des monuments historiques.").
exclusion(tous, f(bien, valeurs), bien(valeurs), non, 'S2-b',
    "Les fonds et valeurs : il s’agit des billets de banque, pièces de monnaie, lingots d’or et d’argent, titres et valeurs mobilières, moyens de paiements.").
exclusion(tous, f(bien, animal), bien(animal), non, 'S2-b',
    "Les animaux.").
exclusion(tous, f(bien, collection_timbres_monnaies), bien(collection_timbres_monnaies), non, 'S2-b',
    "Les collections de timbres, de monnaie ou de médailles.").
exclusion(tous, f(terrain_non_constructible, oui), tout, non, 'S2-b',
    "Les bâtiments et leur contenu construits dans une zone qui a été, préalablement à leur construction, déclarée inconstructible en vertu des règles légales ou administratives visant à prévenir les conséquences des catastrophes naturelles (Plan de Prévention des Risques, Plan d’Exposition aux Risques ou autres règles administratives en vigueur lors de la construction).").
exclusion(tous, f(batiment_inoccupe_10_ans_avant_souscription, oui), tout, non, 'S2-b',
    "Les bâtiments inoccupés en permanence depuis plus de 10 ans avant la souscription.").
