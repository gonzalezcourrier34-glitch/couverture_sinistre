% --- Art. 5.8 : proposition rédigée par le modèle — mistral:mistral-large-4-0, 2026-11-24 ---
evenement_traduit(responsabilite).
garantie(rc_vie_privee_assistance_benevole, "Assistance bénévole de tiers", '5.8',
    "Nous vous assurons pour les dommages subis par un tiers qui aurait participé, dans le cadre de votre vie privée et en cas de danger imminent, à votre sauvetage à titre gratuit et non professionnel et/ou à celui de vos biens assurés.").
perimetre(rc_vie_privee_assistance_benevole, f(evenement, responsabilite)).
perimetre(rc_vie_privee_assistance_benevole, f(victime, tiers)).
perimetre(rc_vie_privee_assistance_benevole, f(dommage_tiers, corporel)).
perimetre(rc_vie_privee_assistance_benevole, f(danger_imminent, oui)).
perimetre(rc_vie_privee_assistance_benevole, f(assistance_benevole, oui)).
perimetre(rc_vie_privee_assistance_benevole, f(contexte_vie_privee, oui)).
perimetre(rc_vie_privee_assistance_benevole, ou([f(objet_sauvetage, assure), f(objet_sauvetage, biens_assures), f(objet_sauvetage, les_deux)])).
circonstance(rc_vie_privee_assistance_benevole, f(compensation_autre_organisme, non), '5.8',
    "Nous intervenons dans la mesure où la personne lésée ne peut obtenir de compensation à charge d'un autre organisme public ou privé.").
