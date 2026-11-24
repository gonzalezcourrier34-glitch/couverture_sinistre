% --- Art. 5.5 : proposition rédigée par le modèle — mistral:mistral-large-4-0, 2026-11-24 ---
evenement_traduit(responsabilite).
garantie(rc_vie_privee_activites_sportives_loisirs, "RC Vie Privée - Activités sportives et de loisirs", '5.5',
    "Nous vous assurons pour les dommages causés par : • la pratique d'activités sportives ou d'agrément • l'utilisation à des fins exclusivement sportives ou récréatives d'aéromodèles (y compris les drones dont la masse maximale au décollage est inferieure à 150 kg), pour autant qu'ils ne volent pas dans un rayon de 3 km autour des aéroports ou des aérodromes civils et militaires et qu'ils ne volent pas au-dessus des complexes industriels, des prisons, des terminaux LNG, des centrales nucléaires, ou d'un rassemblement public de personnes en plein air • les enfants assurés à l'occasion de services même rémunérés").
perimetre(rc_vie_privee_activites_sportives_loisirs, f(evenement, responsabilite)).
perimetre(rc_vie_privee_activites_sportives_loisirs, ou([f(origine_rc, activite_sportive_loisir), f(origine_rc, aeromodele), f(origine_rc, enfant_service_remunere)])).
circonstance(rc_vie_privee_activites_sportives_loisirs, si(f(origine_rc, aeromodele), et([f(aeromodele_rayon_3km_aeroport, non), f(aeromodele_au_dessus_zone_interdite, non)])), '5.5',
    "pour autant qu'ils ne volent pas dans un rayon de 3 km autour des aéroports ou des aérodromes civils et militaires et qu'ils ne volent pas au-dessus des complexes industriels, des prisons, des terminaux LNG, des centrales nucléaires, ou d'un rassemblement public de personnes en plein air").
circonstance(rc_vie_privee_activites_sportives_loisirs, si(et([f(origine_rc, aeromodele), f(est_drone, oui)]), f(masse_aeromodele, moins_150kg)), '5.5',
    "y compris les drones dont la masse maximale au décollage est inferieure à 150 kg").
exclusion(rc_vie_privee_activites_sportives_loisirs, f(origine_rc, chasse_sport), tout, oui, '5.5-a',
    "Nous n'indemnisons pas les dommages causés par la pratique de la chasse.").
