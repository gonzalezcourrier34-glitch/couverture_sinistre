% --- Art. 3.2.2 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
evenement_traduit(catastrophe_naturelle).
garantie(pluies_inondations, "Pluies & inondations", '3.2.2',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “Pluies & inondations” est accordée.").
perimetre(pluies_inondations, f(evenement, catastrophe_naturelle)).
perimetre(pluies_inondations, ou([f(catastrophe, inondation), f(catastrophe, ruissellement), f(catastrophe, glissement_terrain)])).
perimetre(pluies_inondations, concept(batiment_designe)).
exclusion(pluies_inondations, et([et([ou([f(lieu, jardin), f(lieu, terrasse)]), non(f(bien, element_batiment))]), non(f(bien, mobilier_jardin))]), tout, oui, '3.2.2.4',
    "au contenu se trouvant à l’extérieur des locaux, à l’exception du mobilier de jardin").
exclusion(pluies_inondations, et([f(travaux_construction, oui), f(lien_causal_travaux, oui)]), tout, oui, '3.2.2.4',
    "lorsque le bâtiment est en cours de construction, transformation ou rénovation et qu’il existe un lien causal entre les dommages et les travaux en cours").
exclusion(pluies_inondations, f(ouvertures_non_fermees, oui), tout, oui, '3.2.2.4',
    "par des entrées d’eaux pluviales, de neige ou de glace par des ouvertures non fermées, tels que portes, fenêtres, soupiraux, lucarnes").
exclusion(pluies_inondations, f(cause_eau, eau_souterraine), tout, oui, '3.2.2.4',
    "par les infiltrations d’eaux souterraines").
exclusion(pluies_inondations, f(cause_eau, condensation), tout, non, '3.2.2.4',
    "par l’hygrométrie ambiante, même consécutivement à un sinistre couvert").
exclusion(pluies_inondations, f(cause_eau, condensation), tout, non, '3.2.2.4',
    "par des champignons ou des moisissures, même consécutivement à un sinistre couvert").
exclusion(pluies_inondations, f(manque_entretien, oui), tout, non, '3.2.2.4',
    "par un défaut de réparation ou d’entretien, ou dus à une étanchéité absente, mal conçue ou mal réalisée").
exclusion(pluies_inondations, f(cause_eau, condensation), tout, non, '3.2.2.4',
    "par l’humidité, la porosité, la condensation, les phénomènes de capillarité").
exclusion(pluies_inondations, f(terrain_non_constructible, oui), tout, non, '3.2.2.4',
    "aux bâtiments situés sur un terrain non constructible").
exclusion(pluies_inondations, f(autorisation_gestion_eau_non_respectee, oui), tout, non, '3.2.2.4',
    "aux bâtiments soumis à l’autorisation de l’Administration de la gestion de l’eau et qui ne respectent pas les conditions afférentes à cette autorisation").
exclusion(pluies_inondations, f(dommages_dans_72h, non), tout, non, '3.2.2.1',
    "Les dommages qui résultent des événements climatiques cités ci-dessus seront pris en charge par la Compagnie à conditions qu’ils se soient réalisés dans les 72 heures suivant l’événement.").
limite(pluies_inondations, '3.2.2.2', "Lorsque les conditions particulières mentionnent que les biens désignés ne sont pas situés en zone inondable, l’Assuré bénéficie en cas de sinistre d’une intervention de la Compagnie à concurrence de 250.000€ maximum par sinistre.", "250000").
limite(pluies_inondations, '3.2.2.3', "Lorsque les conditions particulières mentionnent que les biens désignés sont situés en zone inondable, l’Assuré bénéficie en cas de sinistre d’une intervention de la Compagnie à concurrence de 20.000€ maximum par sinistre. En cas de sinistre, la garantie sera accordée dans la limite du plafond indiqué ci-avant soit 20.000€ et après déduction de la franchise de 1.500€ prévue dans le cadre de la présente garantie.", "20000").
limite(pluies_inondations, '3.2.2.4', "Dans ce cas, la prise en charge des dommages se fait sans application de la règle proportionnelle à concurrence de 5.000€ par sinistre", "5000").
exclusion([pluies_inondations], f(option_pluies_inondations, non), tout, oui, '3.2.2',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “Pluies & inondations” est accordée.").
