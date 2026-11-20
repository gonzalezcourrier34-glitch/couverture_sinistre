% --- Art. 1.2 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
definition(contenu, et([ou([f(lieu, logement), concept(dependances)]), ou([f(proprietaire, assure), f(auteur, famille)])]), '1.2-a',
    "Tous les objets d’usage courant et les vêtements vous appartenant ou qui vous sont confiés ou appartenant à toute personne résidant avec vous ou en simple visite, contenus à l’intérieur du local d’habitation et des dépendances assurés.").
exclusion(tous, et([concept(dependances), f(formule, eco)]), tout, oui, '1.2-b',
    "les biens mobiliers se trouvant dans les dépendances si vous avez souscrit la formule Eco").
exclusion(tous, ou([f(bien, bijoux), f(bien, valeurs)]), tout, non, '1.2-b',
    "les objets précieux, les espèces, titres et valeurs, les objets de valeur désignés").
exclusion(tous, f(bien, vehicule_moteur), tout, non, '1.2-b',
    "les véhicules terrestres à moteur (y compris les vélos électriques circulant à plus de 25 km/h et les engins de déplacement personnel motorisés), les remorques, les caravanes, les véhicules aériens").
exclusion(tous, ou([f(bien, animal), f(bien, plantation)]), tout, non, '1.2-b',
    "les animaux et les végétaux").
exclusion(tous, et([f(fauteuil_roulant, oui), f(evenement, vol), f(auteur, famille), non(f(plainte_deposee, oui))]), tout, oui, '1.2-b',
    "les vols, tentatives de vol ou actes de vandalisme dont seraient auteurs ou complices les membres de votre famille (article 311-12 du Code pénal) ou vos préposés pendant leur service, sauf si une plainte nominative est déposée à leur encontre").
