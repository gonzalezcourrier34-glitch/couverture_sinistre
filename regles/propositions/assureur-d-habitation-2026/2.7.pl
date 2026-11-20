% --- Art. 2.7 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(bris).
garantie(bris_glaces, "Bris de glaces", '2.7-a',
    "La garantie couvre, lorsqu’ils sont brisés accidentellement, les frais de remplacement : • des miroirs intérieurs, des glaces équipant les meubles et les aquariums, • des vitrages des portes, portes-fenêtres, baies et fenêtres, y compris en toiture").
perimetre(bris_glaces, f(evenement, bris)).
perimetre(bris_glaces, ou([f(bien, vitre), f(bien, miroir), f(bien, verre_meuble), f(bien, panneau_verre_plastique), f(bien, serre)])).
perimetre(bris_glaces, concept(batiment)).
garantie(bris_glace_plus, "Bris de glace + (Confort et Excellence)", '2.7-a',
    "La garantie est étendue pour les formules Confort et Excellence aux : • plaques vitrocéramiques, plaques induction, • vérandas ou loggias (si l’option est souscrite), • vitraux, marquises, • appareils sanitaires").
perimetre(bris_glace_plus, f(evenement, bris)).
perimetre(bris_glace_plus, ou([f(bien, table_cuisson_vitroceramique), f(bien, sanitaire), f(bien, veranda)])).
perimetre(bris_glace_plus, concept(batiment)).
circonstance(bris_glace_plus, ou([f(formule, confort), f(formule, excellence)]), '2.7-a',
    "La garantie est étendue pour les formules Confort et Excellence aux").
garantie(bris_glace_renforce, "Bris de glace renforcé (Excellence)", '2.7-a',
    "La garantie est étendue pour la formule Excellence aux survitrages mobiles, vitres d’insert, vitres d’appareils électroménagers, ainsi que les panneaux solaires et photovoltaïques").
perimetre(bris_glace_renforce, f(evenement, bris)).
perimetre(bris_glace_renforce, ou([f(bien, appareil_electromenager), f(bien, panneau_solaire)])).
perimetre(bris_glace_renforce, concept(batiment)).
circonstance(bris_glace_renforce, f(formule, excellence), '2.7-a',
    "La garantie est étendue pour la formule Excellence aux").
exclusion([bris_glaces, bris_glace_plus, bris_glace_renforce], et([f(bien, appareil_electromenager), non(f(formule, excellence))]), bien(appareil_electromenager), non, '2.7-b',
    "les appareils électroménagers, sauf ceux garantis dans le « Bris de glace renforcé » ci-dessus").
