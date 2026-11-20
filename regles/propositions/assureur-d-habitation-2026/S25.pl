% --- Art. S25 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
exclusion(tous, ou([et([f(intentionnel, oui), non(f(auteur, tiers))]), et([f(participation_rixe, oui), non(f(legitime_defense, oui))])]), tout, non, 'S25',
    "les dommages causés intentionnellement ou frauduleusement par vous ou par un complice, ou résultant de votre ou de sa participation à une action violente ou à une rixe (sauf légitime défense)").
exclusion(tous, et([f(manque_entretien, oui), ou([non(f(evenement, degat_eaux)), non(f(cause_eau, gel))])]), tout, oui, 'S25',
    "ceux qui résultent directement d’un défaut de réparation ou d’entretien indispensables vous incombant et dont vous aviez connaissance").
exclusion(tous, et([ou([f(cause_guerre, oui), f(cause_nucleaire, oui)]), non(f(evenement, attentat))]), tout, non, 'S25',
    "de la guerre civile ou étrangère, - de tout combustible, produit ou déchet radioactif, de tout engin destiné à irradier ou à exploser par modification du noyau de l’atome ainsi que leur décontamination, sauf pour les dommages matériels directs causés par un attentat ou un acte de terrorisme").
