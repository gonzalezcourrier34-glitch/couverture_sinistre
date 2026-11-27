% --- Art. 5.3 : proposition rédigée par le modèle — mistral:mistral-large-4-0, 2026-11-24 ---
evenement_traduit(responsabilite).
garantie(rc_vie_privee_animaux, "RC Vie Privée - Animaux et attelages", '5.3',
    "Nous vous assurons pour les dommages causés : • par les animaux dont vous avez la garde en dehors de toute activité professionnelle (les chiens de garde utilisés pour la garde de bâtiments à usage professionnel sont couverts) • aux animaux appartenant à des tiers et dont vous avez la garde en dehors de toute activité professionnelle • par les chevaux de selle, poneys et attelages dont vous êtes propriétaire, détenteur ou gardien. La garantie est acquise pour 5 chevaux de selle dont vous êtes propriétaire, ou plus si leur nombre est mentionné en conditions particulières. De plus, nous couvrons les dommages causés : • lorsque vous participez, à titre non professionnel, avec les chevaux ou attelages assurés, à des épreuves équestres (courses, jumpings, concours de dressage) ainsi que lors de leur préparation • lors du transport à titre gracieux dans les attelages assurés, étant entendu que le nombre de personnes transportées ne peut dépasser la capacité de transport de l’attelage concerné • par les objets transportés ou par leur chute").
perimetre(rc_vie_privee_animaux, f(evenement, responsabilite)).
perimetre(rc_vie_privee_animaux, ou([et([f(garde_animal, oui), non(f(activite_garde_professionnelle, oui)), non(f(type_animal, chien_garde_pro)), ou([f(origine_rc, animal_compagnie), f(origine_rc, animal_autre), f(type_animal, autre_animal)])]), f(type_animal, chien_garde_pro), et([f(type_animal, cheval_selle), f(proprietaire_detenteur_gardien, oui)]), et([f(type_animal, poney), f(proprietaire_detenteur_gardien, oui)]), et([f(type_animal, attelage), f(proprietaire_detenteur_gardien, oui)]), et([f(bien, animal), f(proprietaire, hote), f(garde_animal, oui), non(f(activite_garde_professionnelle, oui))]), et([f(auteur, personnel_prive), ou([f(utilisation_besoins_personnels, oui), f(garde_animal_prepose, oui)])])])).
circonstance(rc_vie_privee_animaux, f(epreuve_equestre, oui), '5.3',
    "lorsque vous participez, à titre non professionnel, avec les chevaux ou attelages assurés, à des épreuves équestres (courses, jumpings, concours de dressage) ainsi que lors de leur préparation").
circonstance(rc_vie_privee_animaux, et([f(transport_gracieux, oui), f(capacite_attelage_respectee, oui)]), '5.3',
    "lors du transport à titre gracieux dans les attelages assurés, étant entendu que le nombre de personnes transportées ne peut dépasser la capacité de transport de l’attelage concerné").
circonstance(rc_vie_privee_animaux, f(objet_transporte_cause_dommage, oui), '5.3',
    "par les objets transportés ou par leur chute").
exclusion(rc_vie_privee_animaux, ou([f(type_animal, gibier), f(type_animal, animal_sauvage)]), tout, oui, '5.3-a',
    "causés par le gibier ou les animaux sauvages, domptés ou non, à l’exception des cervidés").
exclusion(rc_vie_privee_animaux, et([f(auteur, personnel_prive), f(age_prepose, moins_14_ans), f(lieu, voie_publique), f(accompagnement_adulte, non)]), tout, oui, '5.3-a',
    "causés par un préposé de l’assuré, âgé de moins de 14 ans, quand il conduit des animaux ou des attelages sur la voie publique, sans être accompagné par un adulte").
exclusion(rc_vie_privee_animaux, et([f(lieu, voie_publique), f(dispositifs_securite_vehicule, non)]), tout, oui, '5.3-a',
    "résultant du fait que les véhicules, circulant sur la voie publique, ne sont pas munis des dispositifs de sécurité prévus par la règlementation sur la circulation routière").
exclusion(rc_vie_privee_animaux, f(dommage_objet_transporte, oui), tout, oui, '5.3-a',
    "aux objets et marchandises transportés").
limite(rc_vie_privee_animaux, '5.3', "La garantie est acquise pour 5 chevaux de selle dont vous êtes propriétaire, ou plus si leur nombre est mentionné en conditions particulières", "5 chevaux de selle (ou plus selon conditions particulières)").
