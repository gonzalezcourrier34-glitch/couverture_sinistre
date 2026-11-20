% --- Art. 12.2 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(responsabilite).
garantie(rc_locataire, "Responsabilité civile du locataire : incendie, explosion, eau", '12.2-a',
    "• Envers le propriétaire La garantie couvre les conséquences financières de votre responsabilité civile de locataire vis-à-vis de votre propriétaire…• Envers les voisins et les tiers La garantie couvre les conséquences financières de votre responsabilité civile à raison des dommages matériels et immatériels consécutifs subis par les voisins et les tiers à la suite d’un incendie, d’une explosion, d’une venue d’eau ayant pris naissance dans l’habitation assurée").
perimetre(rc_locataire, f(evenement, responsabilite)).
perimetre(rc_locataire, f(statut_logement, locataire)).
perimetre(rc_locataire, f(origine_rc, habitation)).
