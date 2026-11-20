% --- Art. 1.2 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
definition(contenu, et([ou([f(bien, mobilier), f(bien, electronique), f(bien, objet_divers), f(bien, velo), f(bien, bijoux), f(bien, valeurs), f(bien, mobilier_jardin)]), concept(batiment)]), '1.2-a',
    "Tous les objets d’usage courant et les vêtements vous appartenant ou qui vous sont confiés ou appartenant à toute personne résidant avec vous ou en simple visite, contenus à l’intérieur du local d’habitation et des dépendances assurés").
exclusion(tous, et([ou([f(lieu, cave), f(lieu, garage), f(lieu, annexe), f(lieu, abri_jardin)]), f(formule, eco)]), tout, non, '1.2-b',
    "les biens mobiliers se trouvant dans les dépendances si vous avez souscrit la formule Eco").
exclusion(tous, et([f(bien, bijoux), non(f(option_objets_valeur, oui))]), bien(bijoux), non, '1.2-b',
    "les objets précieux, les espèces, titres et valeurs, les objets de valeur désignés").
exclusion(tous, et([f(bien, valeurs), non(f(option_objets_valeur, oui))]), bien(valeurs), non, '1.2-b',
    "les objets précieux, les espèces, titres et valeurs, les objets de valeur désignés").
exclusion(tous, f(bien, vehicule_moteur), bien(vehicule_moteur), non, '1.2-b',
    "les véhicules terrestres à moteur (y compris les vélos électriques circulant à plus de 25 km/h et les engins de déplacement personnel motorisés), les remorques, les caravanes, les véhicules aériens").
exclusion(tous, f(bien, remorque), bien(remorque), non, '1.2-b',
    "les véhicules terrestres à moteur (y compris les vélos électriques circulant à plus de 25 km/h et les engins de déplacement personnel motorisés), les remorques, les caravanes, les véhicules aériens").
exclusion(tous, f(bien, animal), bien(animal), non, '1.2-b',
    "les animaux et les végétaux").
exclusion(tous, f(bien, plantation), bien(plantation), non, '1.2-b',
    "les animaux et les végétaux").
