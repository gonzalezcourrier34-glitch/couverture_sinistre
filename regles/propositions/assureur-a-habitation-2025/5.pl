% --- Art. 5 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(responsabilite).
garantie(rc_vie_privee, "Responsabilité civile vie privée", '5.1',
    "Nous vous assurons dans le monde entier lorsque votre responsabilité est mise en cause pour des dommages occasionnés à un tiers dans le cadre de votre vie privée et en dehors de tout contrat").
perimetre(rc_vie_privee, f(evenement, responsabilite)).
exclusion(rc_vie_privee, ou([f(victime, assure), f(victime, conjoint)]), tout, non, '12/tiers',
    "Toute personne qui n’est pas considérée comme assurée.").
exclusion(rc_vie_privee, f(origine_rc, activite_professionnelle), tout, non, '5.1',
    "dans le cadre de votre vie privée").
exclusion(rc_vie_privee, f(origine_rc, contrat), tout, non, '5.1',
    "en dehors de tout contrat").
exclusion(rc_vie_privee, f(bien_confie, oui), tout, non, '5.10',
    "les dommages causés aux biens mobiliers et immobiliers dont vous avez la garde").
exclusion(rc_vie_privee, f(origine_rc, vehicule_moteur), tout, non, '5.4-a',
    "des véhicules automoteurs ou équipés d’un moteur même non autonomes autres que ceux cités au point 2.4").
exclusion(rc_vie_privee, et([f(origine_rc, habitation), ou([f(evenement, incendie), f(evenement, explosion), f(evenement, fumee)])]), tout, non, '5.2-a',
    "les dommages matériels causés par le feu, par l’incendie, l’explosion ou la fumée consécutive à un feu ou à un incendie prenant naissance dans ou communiqué par un bâtiment assuré par le présent contrat").
exclusion(rc_vie_privee, f(intentionnel, oui), tout, non, '5.10',
    "pour les sinistres intentionnels").
limite(rc_vie_privee, '5.1', "les dommages résultant de lésions corporelles à concurrence de 24.763.874,96 EUR", "24763874.96").
limite(rc_vie_privee, '5.1', "les dommages matériels à concurrence de 7.131.995,99 EUR", "7131995.99").
limite(rc_vie_privee, '5.1', "Une franchise de 258,70 EUR est d’application pour les dommages matériels", "franchise 258.70").
