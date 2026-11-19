% --- Art. 2.2 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-18 ---
evenement_traduit(tempete).
definition(tempete, ou([f(vent_80_kmh_irm, oui), f(vent_dommages_voisins, oui)]), '12/tempete',
    "• L’action du vent mesurée à une vitesse de pointe d’au moins 80 km/h par la station de l’I.R.M. la plus proche du bâtiment • L’action du vent qui endommage d’autres biens qui sont situés dans les 10 km du bâtiment et qui sont assurables contre le vent de tempête ou présentent une résistance au vent équivalente aux biens assurables.").
garantie(tempete, "Tempête, la grêle, la pression de la neige ou de la glace", '2.2',
    "Nous couvrons les dommages matériels directement causés par les aléas précisés.").
perimetre(tempete, f(evenement, tempete)).
circonstance(tempete, si(f(alea_tempete, vent), concept(tempete)), '12/tempete',
    "L’action du vent mesurée à une vitesse de pointe d’au moins 80 km/h par la station de l’I.R.M. la plus proche du bâtiment").
exclusion(tempete, et([f(construction_delabree, oui), non(f(residence_principale, oui))]), tout, oui, '2.2-a',
    "aux constructions délabrées ou en cours de démolition et à leur contenu éventuel, sauf si ces constructions constituent votre logement principal").
exclusion(tempete, et([ou([f(lieu, jardin), f(lieu, terrasse)]), non(f(bien, element_batiment))]), tout, oui, '2.2-a',
    "à tout objet situé à l'extérieur même ceux fixés à demeure").
exclusion(tempete, et([ou([f(lieu, annexe), f(lieu, abri_jardin)]), f(construction_close, non)]), tout, oui, '2.2-a',
    "à tout objet situé dans une annexe non entièrement close ou couverte").
exclusion(tempete, f(bien, materiaux_construction), bien(materiaux_construction), non, '2.2-a',
    "aux matériaux à pied d’œuvre").
exclusion(tempete, et([ou([f(lieu, annexe), f(lieu, abri_jardin)]), f(annexe_ancree_beton, non)]), tout, oui, '2.2-a',
    "aux annexes contiguës ou isolées faisant partie du bâtiment qui ne sont pas fixées au sol par un ancrage en béton, ansi qu’à leur contenu").
exclusion(tempete, f(construction_close, non), tout, oui, '2.2-a',
    "aux constructions non entièrement closes ou couvertes, à ce qui y est incorporé ainsi qu’à leur contenu").
limite(tempete, '2.2', "Abri de jardin et son éventuel contenu 1.000 EUR", "1000 EUR").
