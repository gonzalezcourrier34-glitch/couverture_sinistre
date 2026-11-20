% --- Art. 2.7 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(bris).
extension(bris_glaces, et([ou([f(formule, confort), f(formule, excellence)]), si(f(bien, veranda), f(option_veranda, oui))]), '2.7-a',
    "La garantie est étendue pour les formules Confort et Excellence aux : • plaques vitrocéramiques, plaques induction, • vérandas ou loggias (si l’option est souscrite), • vitraux, marquises, • appareils sanitaires.").
extension(bris_glaces, f(formule, excellence), '2.7-a',
    "La garantie est étendue pour la formule Excellence aux survitrages mobiles, vitres d'insert, vitres d'appareils électroménagers, ainsi que les panneaux solaires et photovoltaïques en toiture ou montés sur châssis scellés au sol.").
garantie(bris_glaces, "Bris de glaces", '2.7-a',
    "La garantie couvre, lorsqu’ils sont brisés accidentellement, les frais de remplacement : • des miroirs intérieurs, des glaces équipant les meubles et les aquariums, • des vitrages des portes, portes-fenêtres, baies et fenêtres, y compris en toiture, • des parois vitrées intérieures ainsi que celles équipant les balcons, situés dans les locaux que vous occupez à titre privatif, • des panneaux de signalisation, • des serres en verre et matériaux assimilés d’une superficie jusqu’à 5 m2. Les produits en matière plastique remplissant les mêmes fonctions que les produits verriers des biens définis ci-avant sont également pris en charge. La garantie couvre également : • les frais de clôture provisoire lorsque cette dernière est indispensable pour la sécurité des locaux, • les dommages matériels occasionnés par les éclats de verre, • le film occultant ou protecteur.").
perimetre(bris_glaces, f(evenement, bris)).
perimetre(bris_glaces, ou([f(bien, miroir), f(bien, verre_meuble), f(bien, vitre), f(bien, panneau_verre_plastique), f(bien, serre), f(bien, aquarium), f(bien, panneau_signalisation), f(bien, objet_verre_non_vitre)])).
perimetre(bris_glaces, concept(batiment)).
circonstance(bris_glaces, non(f(intentionnel, oui)), '2.7-a',
    "lorsqu’ils sont brisés accidentellement").
exclusion(bris_glaces, f(bien, appareil_electromenager), tout, oui, '2.7-b',
    "les appareils électroménagers, sauf ceux garantis dans le « Bris de glace renforcé » ci-dessus").
exclusion(bris_glaces, et([f(bien, serre), f(superficie_serre, plus_5m2), non(f(pack_jardin, oui))]), tout, oui, '2.7-b',
    "les serres d’une superficie de plus de 5 m2, sauf si le Pack Jardin est souscrit").
exclusion(bris_glaces, ou([f(type_dommage, rayure_ou_ecaillement), f(manque_entretien, oui), f(impropriete_support, oui)]), tout, oui, '2.7-b',
    "les ébréchures ainsi que tous dommages résultant de la vétusté ou de l’impropriété du support").
