% --- Art. 12.4 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(responsabilite).
exclusion([rc_proprietaire_voisins, rc_proprietaire_immeuble, rc_locataire, rc_villegiature], f(origine_rc, vehicule_moteur), tout, non, '12.4-a',
    "les dommages de toute nature causés par des véhicules à moteur (y compris les vélos électriques circulant à plus de 25 km/h et les engins de déplacement personnel motorisés) soumis à la législation sur l’assurance automobile obligatoire, ou qui y seraient soumis en France,").
exclusion([rc_proprietaire_voisins, rc_proprietaire_immeuble, rc_locataire, rc_villegiature], f(bien_confie, oui), tout, non, '12.4-a',
    "les dommages subis par les biens dont vous avez la propriété, la conduite ou la garde,").
