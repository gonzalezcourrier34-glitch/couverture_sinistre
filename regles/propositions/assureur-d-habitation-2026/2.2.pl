% --- Art. 2.2 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(electricite).
garantie(dommages_electriques, "Dommages électriques (Confort et Excellence)", '2.2-a',
    "La garantie couvre les dommages matériels causés par les effets d’une surtension, d’une sous-tension ou d’une surintensité accidentelle, y compris du fait de la foudre, aux installations ou aux appareils électriques").
perimetre(dommages_electriques, f(evenement, electricite)).
perimetre(dommages_electriques, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(dommages_electriques, concept(batiment)).
circonstance(dommages_electriques, ou([f(formule, confort), f(formule, excellence)]), '2.2',
    "Cette garantie est acquise uniquement pour les formules Confort et Excellence").
exclusion(dommages_electriques, f(bien, consommable), bien(consommable), non, '2.2-b',
    "les résistances chauffantes, les fusibles, les disjoncteurs, les lampes éclairantes, les transformateurs").
exclusion(dommages_electriques, f(bien, denrees_alimentaires), bien(denrees_alimentaires), non, '2.2-b',
    "le contenu des appareils endommagés").
exclusion(dommages_electriques, f(garantie_fabricant, oui), tout, oui, '2.2-b',
    "les dommages sous garantie ou faisant l’objet d’un contrat de maintenance").
limite(dommages_electriques, '2.2-a', "L’indemnisation est égale au coût de réparation ou de remplacement du sous-ensemble endommagé, dans la limite de la valeur de remplacement, vétusté déduite au taux de 1 % par mois, du bien mobilier endommagé, avec un maximum de 80 %", "vétusté 1 % par mois, au plus 80 %").
