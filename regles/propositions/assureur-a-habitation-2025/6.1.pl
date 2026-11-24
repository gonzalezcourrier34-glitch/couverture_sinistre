% --- Art. 6.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
evenement_traduit(heurt).
evenement_traduit(bris).
evenement_traduit(vol).
definition(materiel_informatique, f(bien, appareil_informatique), '12/materiel-informatique',
    "Les ordinateurs de bureau et périphériques, laptops, notebook et tout appareil dont la taille de l’écran est supérieure à 7’’.").
garantie(pack_multimedia, "Pack multimédia", '6.1',
    "Pour autant que vos conditions particulières en fassent mention, vos garanties sont étendues au matériel informatique. Dans ce cadre, nous prenons en charge les dommages causés par : • la chute, le heurt et l’introduction d’un corps étrangers • le vol survenu à l’extérieur du bâtiment assuré, pour autant qu’une plainte soit déposée auprès des autorités judiciaires ou de polices compétentes. Il faut noter que ces couvertures sont acquises dans le monde entier.").
perimetre(pack_multimedia, concept(materiel_informatique)).
perimetre(pack_multimedia, ou([f(evenement, heurt), f(evenement, bris), f(evenement, vol)])).
circonstance(pack_multimedia, si(f(evenement, vol), et([non(concept(batiment)), f(plainte_deposee, oui)])), '6.1',
    "le vol survenu à l’extérieur du bâtiment assuré, pour autant qu’une plainte soit déposée auprès des autorités judiciaires ou de polices compétentes").
circonstance(pack_multimedia, f(option_materiel_multimedia, oui), '6.1',
    "Pour autant que vos conditions particulières en fassent mention, vos garanties sont étendues au matériel informatique. Dans ce cadre, nous prenons en charge les dommages causés par : • la chute, le heurt et l’introduction d’un corps étrangers • le vol survenu à l’extérieur du bâtiment assuré, pour autant qu’une plainte soit déposée auprès des autorités judiciaires ou de polices compétentes. Il faut noter que ces couvertures sont acquises dans le monde entier.").
exclusion(pack_multimedia, et([f(evenement, vol), f(laisse_sans_surveillance, oui)]), tout, oui, '6.1',
    "le vol d’objets ayant été laissé sans surveillance dans un lieu public").
exclusion(pack_multimedia, et([f(evenement, vol), f(lieu, vehicule), f(vehicule_voie_publique, oui), f(periode_horaire, nuit_22h_7h)]), tout, oui, '6.1',
    "le vol d’objets laissés dans un véhicule en stationnement sur la voie publique entre 22 heures et 7 heures").
exclusion(pack_multimedia, et([f(evenement, vol), f(lieu, vehicule), f(vehicule_voie_publique, oui), f(periode_horaire, jour_7h_22h), ou([f(materiel_laisse_en_vue, oui), f(vehicule_ferme_cle, non), f(habitacle_ferme, non)])]), tout, oui, '6.1',
    "le vol d’objets laissés dans un véhicule en stationnement sur la voie publique entre 7 heures et 22 heures et que les objets étaient visibles de l’extérieur ou que le véhicule n’était pas fermé à clé ou encore que l’habitacle n’était pas entièrement fermé").
exclusion(pack_multimedia, et([f(evenement, vol), f(simple_disparition, oui)]), tout, oui, '6.1',
    "la simple perte, disparition ou l’oubli d’un objet dans un lieu public").
limite(pack_multimedia, '6.1-a', "Limite par sinistre (à l’indice ABEX 775) 5.750 EUR", "5750 EUR à l'indice ABEX 775").
