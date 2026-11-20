% --- Art. 2.2 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(electricite).
evenement_traduit(foudre).
definition(appareil_electrique, ou([f(bien, appareil_electromenager), f(bien, appareil_audiovisuel), f(bien, appareil_informatique), f(bien, equipement_alarme_surveillance), f(bien, equipement_domotique), f(bien, element_batiment)]), '2.2-a',
    "aux installations ou aux appareils électriques").
garantie(dommages_electriques, "Dommages électriques", '2.2-a',
    "La garantie couvre les dommages matériels causés par les effets d'une surtension, d'une sous-tension ou d'une surintensité accidentelle, y compris du fait de la foudre, aux installations ou aux appareils électriques.").
perimetre(dommages_electriques, f(evenement, electricite)).
perimetre(dommages_electriques, f(evenement, foudre)).
perimetre(dommages_electriques, concept(appareil_electrique)).
perimetre(dommages_electriques, ou([f(formule, confort), f(formule, excellence)])).
circonstance(dommages_electriques, ou([f(cause_electrique, surtension), f(cause_electrique, sous_tension), f(cause_electrique, surintensite), f(cause_electrique, foudre)]), '2.2-a',
    "causés par les effets d'une surtension, d'une sous-tension ou d'une surintensité accidentelle, y compris du fait de la foudre").
exclusion(dommages_electriques, ou([f(bien, resistance_chauffante), f(bien, fusible), f(bien, disjoncteur), f(bien, lampe_eclairante), f(bien, transformateur)]), tout, oui, '2.2-b',
    "les résistances chauffantes, les fusibles, les disjoncteurs, les lampes éclairantes, les transformateurs").
exclusion(dommages_electriques, f(bien, contenu_appareil), tout, oui, '2.2-b',
    "le contenu des appareils endommagés").
exclusion(dommages_electriques, f(frais_reconstitution_fichiers, oui), tout, oui, '2.2-b',
    "les frais de reconstitution des fichiers informatiques").
exclusion(dommages_electriques, f(frais_reconstitution_donnees, oui), tout, oui, '2.2-b',
    "les frais de reconstitution de données").
exclusion(dommages_electriques, ou([f(garantie_fabricant, oui), f(contrat_maintenance, oui)]), tout, oui, '2.2-b',
    "les dommages sous garantie ou faisant l'objet d'un contrat de maintenance").
limite(dommages_electriques, '2.2-a', "L'indemnisation est égale au coût de réparation ou de remplacement du sous-ensemble endommagé, dans la limite de la valeur de remplacement, vétusté déduite au taux de 1 % par mois, du bien mobilier endommagé, avec un maximum de 80 % (si l'âge de l'appareil ne peut être justifié, le maximum de vétusté est appliqué).", "valeur de remplacement, vétusté déduite au taux de 1 % par mois, maximum 80 %").
