% --- Art. 2.14 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(litige).
garantie(defense_penale, "Défense pénale", '2.14~1',
    "que vous et toutes les personnes assurées auront exposés pour leur défense devant une juridiction pénale où ils sont cités à la suite d’un événement garanti par la présente assurance").
perimetre(defense_penale, f(evenement, litige)).
perimetre(defense_penale, f(domaine_litige, defense_penale)).
exclusion(defense_penale, f(procedure_etranger_sans_accord, oui), tout, non, '2.14~2',
    "une action ou procédure menée à l’étranger sans notre accord écrit préalable").
limite(defense_penale, '2.14~2', "Défense et recours 6.500 EUR", "6500").
garantie(recours, "Recours contre les tiers responsables", '2.14~1',
    "que les assurés, à l’exception du personnel même occasionnel à leur service privé auront exposés pour l’exercice de recours contre les tiers responsables de dommages").
perimetre(recours, f(evenement, litige)).
perimetre(recours, f(domaine_litige, recours_dommage)).
exclusion(recours, f(procedure_etranger_sans_accord, oui), tout, non, '2.14~2',
    "une action ou procédure menée à l’étranger sans notre accord écrit préalable").
exclusion(recours, f(adversaire_assure, oui), tout, non, '2.14~2',
    "les recours entre assurés").
exclusion(recours, f(enjeu_moins_250, oui), tout, non, '2.14~2',
    "ainsi que pour les dommages inférieurs à 250 EUR").
limite(recours, '2.14~2', "Défense et recours 6.500 EUR", "6500").
