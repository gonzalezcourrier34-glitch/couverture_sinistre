% --- Art. 6.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-18 ---
evenement_traduit(chute).
evenement_traduit(heurt).
evenement_traduit(introduction_corps_etranger).
evenement_traduit(vol).
definition(materiel_informatique, f(bien, materiel_informatique), '12/materiel-informatique',
    "Les ordinateurs de bureau et périphériques, laptops, notebook et tout appareil dont la taille de l’écran est supérieure à 7’’.").
garantie(pack_multimedia, "Pack multimédia", '6.1',
    "Pour autant que vos conditions particulières en fassent mention, vos garanties sont étendues au matériel informatique.").
perimetre(pack_multimedia, f(pack_multimedia_souscrit, oui)).
perimetre(pack_multimedia, concept(materiel_informatique)).
perimetre(pack_multimedia, ou([f(evenement, chute), f(evenement, heurt), f(evenement, introduction_corps_etranger), f(evenement, vol)])).
circonstance(pack_multimedia, si(f(evenement, vol), et([non(ou([f(lieu, logement), f(lieu, cave), f(lieu, grenier), f(lieu, garage), f(lieu, annexe), f(lieu, parties_communes), f(lieu, casier)])), f(plainte_deposee, oui)])), '6.1',
    "le vol survenu à l’extérieur du bâtiment assuré, pour autant qu’une plainte soit déposée auprès des autorités judiciaires ou de polices compétentes").
obligation(pack_multimedia, et([f(transport_vehicule, oui), f(lieu, voie_publique), f(heure_sinistre, entre_22h_7h), f(absence, oui)]), faux, oui, '6.1-a',
    "les retirer et les mettre en lieu sûr, lorsque le véhicule, en l’absence des occupants, stationne entre 22 heures et 7 heures sur la voie publique").
obligation(pack_multimedia, et([f(transport_vehicule, oui), f(lieu, voie_publique), f(heure_sinistre, entre_7h_22h)]), faux, oui, '6.1-a',
    "veiller à ce que le véhicule, en stationnement sur la voie public entre 7 heures et 22 heures, soit fermé à clé, que l’habitacle soit fermé et que les objets ne soient pas visibles de l’extérieur").
exclusion(pack_multimedia, et([f(evenement, vol), f(lieu_public, oui), f(surveillance, non)]), tout, oui, '6.1',
    "le vol d’objets ayant été laissé sans surveillance dans un lieu public").
exclusion(pack_multimedia, et([f(evenement, vol), f(transport_vehicule, oui), f(lieu, voie_publique), f(heure_sinistre, entre_22h_7h)]), tout, oui, '6.1',
    "le vol d’objets laissés dans un véhicule en stationnement sur la voie publique entre 22 heures et 7 heures").
exclusion(pack_multimedia, et([f(evenement, vol), f(transport_vehicule, oui), f(lieu, voie_publique), f(heure_sinistre, entre_7h_22h), ou([f(objets_visibles_exterieur, oui), f(vehicule_ferme_cle, non), f(habitacle_ferme, non)])]), tout, oui, '6.1',
    "le vol d’objets laissés dans un véhicule en stationnement sur la voie publique entre 7 heures et 22 heures et que les objets étaient visibles de l’extérieur ou que le véhicule n’était pas fermé à clé ou encore que l’habitacle n’était pas entièrement fermé").
exclusion(pack_multimedia, et([f(lieu_public, oui), ou([f(nature_perte, perte), f(nature_perte, disparition), f(nature_perte, oubli)])]), tout, oui, '6.1',
    "la simple perte, disparition ou l’oubli d’un objet dans un lieu public").
limite(pack_multimedia, '6.1-a', "Limite par sinistre (à l’indice ABEX 775) 5.750 EUR", "5750 EUR").
