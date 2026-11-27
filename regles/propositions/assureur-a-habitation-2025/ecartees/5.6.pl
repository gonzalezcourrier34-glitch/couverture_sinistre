% --- Art. 5.6 : proposition rédigée par le modèle — mistral:mistral-large-4-0, 2026-11-24 ---
evenement_traduit(responsabilite).
garantie(rc_garde_enfants_remuneree, "Garde rémunérée d'enfants", '5.6',
    "Nous assurons votre responsabilité contractuelle et extracontractuelle, lorsque vous assurez la garde, contre rémunération, de maximum 5 enfants de tiers. Nous vous assurons tant pour les dommages causés par les enfants gardés que pour ceux qui sont causés aux enfants gardés.").
perimetre(rc_garde_enfants_remuneree, f(evenement, responsabilite)).
perimetre(rc_garde_enfants_remuneree, f(garde_enfants_remuneree, oui)).
perimetre(rc_garde_enfants_remuneree, f(nombre_enfants_gardes, max_5)).
perimetre(rc_garde_enfants_remuneree, f(enfants_de_tiers, oui)).
