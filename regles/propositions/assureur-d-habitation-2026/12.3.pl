% --- Art. 12.3 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(responsabilite).
garantie(rc_villegiature, "Responsabilité civile villégiature", '12.3',
    "La garantie couvre les conséquences financières de votre responsabilité civile locative et le recours des voisins et des tiers en raison des dommages par incendie, explosion, venue d’eau, détériorations immobilières ou bris de glaces occasionnés à une habitation que vous occupez temporairement ou dont vous êtes occupant à titre gratuit pour des séjours d’agrément d’une durée inférieure à 3 mois").
perimetre(rc_villegiature, f(evenement, responsabilite)).
perimetre(rc_villegiature, f(origine_rc, habitation)).
perimetre(rc_villegiature, f(sejour_temporaire, oui)).
