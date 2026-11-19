% --- Art. 3.2.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
evenement_traduit(tremblement_terre).
garantie(tremblement_terre, "Tremblement de terre", '3.2.1.1',
    "La Compagnie garantit, sous réserve des exclusions générales et des exclusions spécifiques, les dommages matériels causés aux biens désignés par un tremblement de terre.").
perimetre(tremblement_terre, f(evenement, tremblement_terre)).
perimetre(tremblement_terre, f(formule, serenite_plus)).
perimetre(tremblement_terre, concept(batiment_designe)).
circonstance(tremblement_terre, f(evenement, tremblement_terre), '3.2.1.1',
    "Sont considérés comme un seul sinistre le séisme initial et les éventuelles répliques survenues dans les 72h, de même que les dommages tombant sous le coup d’un péril assuré qui en sont la conséquence directe.").
exclusion(tremblement_terre, et([f(travaux_construction, oui), f(lien_causal_travaux, oui)]), tout, oui, '3.2.1.2',
    "survenus alors que le bâtiment est en cours de construction, transformation ou rénovation dans la mesure où il existe un lien causal entre les dommages et les travaux en cours").
exclusion(tremblement_terre, et([ou([f(lieu, jardin), f(lieu, terrasse), f(lieu, abri_jardin), f(lieu, parties_communes)]), non(f(fixe_a_demeure, oui))]), tout, oui, '3.2.1.2',
    "survenus aux objets se trouvant à l’extérieur du bâtiment sauf s’ils sont fixés à demeure").
exclusion(tremblement_terre, ou([f(construction_facilement_deplacable, oui), f(construction_delabree, oui), f(contenu_construction_delabree_ou_deplacable, oui)]), tout, oui, '3.2.1.2',
    "aux constructions faciles à déplacer ou à démonter, délabrées ou en cours de démolition de même qu’à leur éventuel contenu").
exclusion(tremblement_terre, et([f(annexe_ancree_beton, non), ou([f(lieu, annexe), f(lieu, abri_jardin)])]), tout, oui, '3.2.1.2',
    "aux dépendances et abris de jardins qui ne reposent pas sur des fondations").
exclusion(tremblement_terre, ou([f(bien, plantation), f(bien, terrain_jardin)]), tout, oui, '3.2.1.2',
    "aux jardins et plantations").
exclusion(tremblement_terre, f(bien, terrain_golf_tennis), tout, oui, '3.2.1.2',
    "aux terrains de golf ou de tennis").
exclusion(tremblement_terre, ou([f(bien, vehicule_moteur), f(bien, vehicule_aerien), f(bien, vehicule_maritime), f(bien, vehicule_fluvial)]), tout, oui, '3.2.1.2',
    "aux véhicules terrestres à moteur, aériens, maritimes ou fluviaux").
limite(tremblement_terre, '3.2.1.3', "Lors du règlement de l’indemnité, l’Assuré conserve à sa charge un montant de 10% du dommage avec un minimum de 1.500 €.", "10% du dommage avec un minimum de 1.500 €").
