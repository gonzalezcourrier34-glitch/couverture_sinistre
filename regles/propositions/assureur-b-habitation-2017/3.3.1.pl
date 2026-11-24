% --- Art. 3.3.1 : proposition rédigée par le modèle — mistral:mistral-large-4-0, 2026-11-24 ---
evenement_traduit(bris).
extension(lieu_assure, f(pays, monde), '3.3.1.2',
    "La garantie ainsi définie s'exerce dans le monde entier").
garantie(dommages_biens_confort, "Dommages aux biens (Option Confort)", '3.3.1.1',
    "La Compagnie couvre tout bris ou destruction accidentel résultant d'une chute, d'un choc ou de la pénétration d'un corps étranger et qui rend nécessaire la réparation ou le remplacement des").
perimetre(dommages_biens_confort, f(evenement, bris)).
obligation(dommages_biens_confort, f(plainte_deposee, oui), faux, non, '3.3.1.7',
    "déposer une plainte auprès du Parquet").
exclusion(dommages_biens_confort, f(proprietaire, hote), tout, oui, '3.3.1.3',
    "les objets et matériels dont l'Assuré n'est pas propriétaire").
exclusion(dommages_biens_confort, f(usage_professionnel, oui), tout, oui, '3.3.1.3',
    "les objets et matériels utilisés à des fins professionnelles").
exclusion(dommages_biens_confort, f(bien, vehicule_moteur), tout, non, '3.3.1.3',
    "les dommages aux véhicules automoteurs").
exclusion(dommages_biens_confort, f(vice_defaut_connu, oui), tout, oui, '3.3.1.3',
    "les dommages dus à des vices ou défauts qui existaient à la date d'effet de la présente assurance et qui étaient connus de l'Assuré ou de ses mandataires").
exclusion(dommages_biens_confort, f(manque_entretien, oui), tout, oui, '3.3.1.3.7',
    "les dommages qui sont la conséquence directe de l'usure, de la détérioration lente, de la vétusté ou d'un défaut d'entretien").
exclusion(dommages_biens_confort, f(fonctionnement_defectueux, oui), tout, oui, '3.3.1.3',
    "d'un fonctionnement défectueux").
exclusion(dommages_biens_confort, f(garantie_fabricant, oui), tout, oui, '3.3.1.3',
    "les dommages dont le fabricant ou le fournisseur est légalement ou contractuellement responsable").
exclusion(dommages_biens_confort, f(dommage_esthetique, oui), tout, oui, '3.3.1.3',
    "les dommages d'ordre purement esthétique").
exclusion(dommages_biens_confort, f(auteur, assure), tout, oui, '3.3.1.3.17',
    "les vols commis par ou avec la complicité de l'Assuré").
limite(dommages_biens_confort, '3.3.1.4.1', "Le calcul de l'indemnité tient compte d'une vétusté de 10% par année d'ancienneté révolue, sans que cette vétusté ne puisse dépasser 80%", "vétusté 10%/an max 80%").
limite(dommages_biens_confort, '3.3.1.4', "Pour le matériel d'assistance médicale de type pompe à oxygène ou à insuline, et prothèse auditive, le calcul de l'indemnité tient compte d'une vétusté de 20% par année d'ancienneté révolue", "vétusté 20%/an").
