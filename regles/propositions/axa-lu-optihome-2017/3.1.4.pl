% --- Art. 3.1.4 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
evenement_traduit(degat_eaux).
garantie(degats_eaux_3_1_4, "Dégâts des eaux", '3.1.4',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ dégâts des eaux ” est souscrite.").
perimetre(degats_eaux_3_1_4, f(evenement, degat_eaux)).
perimetre(degats_eaux_3_1_4, concept(batiment_designe)).
circonstance(degats_eaux_3_1_4, ou([f(cause_eau, fuite_installation), f(cause_eau, infiltration_toiture), f(cause_eau, debordement_aquarium)]), '3.1.4.1',
    "La Compagnie assure les biens désignés contre les dégâts des eaux c’est-à-dire : n l’écoulement de l’eau des installations hydrauliques se trouvant à l’intérieur du bâtiment désigné et des bâtiments voisins, par suite de rupture, fissure ou débordement de ces installations ; n la pénétration ou l’infiltration dans le bâtiment désigné d’eau provenant de précipitations atmosphériques par suite de rupture, fissure ou débordement dans les tuyaux extérieurs destinés à l’évacuation de cette eau ; n l’infiltration accidentelle d’eau par les toitures, ciels vitrés, terrasses, balcons et balcons formant terrasse, loggias.").
obligation(degats_eaux_3_1_4, si(f(periode_gel, oui), f(prevention_gel, oui)), faux, oui, '3.1.4.3',
    "Pendant la période de gel, l’Assuré doit, si les locaux ne sont pas chauffés ou si les installations se trouvent à l’extérieur, vidanger ou protéger les conduites et réservoirs ainsi que les installations de chauffage non pourvues d’antigel en quantité suffisante : n dans les résidences principales en cas d’inoccupation des locaux de plus de 15 jours consécutifs ; n dans les résidences secondaires, en cas d’inoccupation des locaux supérieure à 3 jours consécutifs. Si l’Assuré ne respecte pas ces prescriptions, sauf cas de force majeure, et si un sinistre survient ou est aggravé de ce fait, l’indemnité due sera réduite de moitié.").
exclusion(degats_eaux_3_1_4, f(bien, toiture), bien(toiture), non, '3.1.4.2',
    "à la toiture du bâtiment ainsi qu’aux revêtements qui en assurent l’étanchéité").
exclusion(degats_eaux_3_1_4, f(bien, canalisation), bien(canalisation), non, '3.1.4.2',
    "a ux conduites, aux installations et appareils hydrauliques, aux tuyaux d’évacuation, aux boilers, chaudières, citernes, aquariums et matelas d’eau à l’origine du sinistre ; toutefois, les dommages aux conduites encastrées sont pris en charge par la Compagnie").
exclusion(degats_eaux_3_1_4, f(cause_eau, condensation), tout, non, '3.1.4.2',
    "par la condensation").
exclusion(degats_eaux_3_1_4, et([f(cause_eau, infiltration_exterieure), non(ou([f(lieu, autre_batiment), f(installation_hydraulique_exterieure, oui)]))]), tout, oui, '3.1.4.2',
    "par la porosité des murs sauf si celle-ci trouve son origine dans un ou des bâtiments voisins ou dans une fuite ou un débordement des installations hydrauliques extérieures au bâtiment désigné").
exclusion(degats_eaux_3_1_4, f(evenement, tempete), tout, non, '3.1.4.2',
    "par tous les événements pouvant être pris en charge au titre de la garantie « tempête et grêle » ou de la garantie « pluies & inondations »").
exclusion(degats_eaux_3_1_4, f(cause_eau, infiltration_exterieure), tout, oui, '3.1.4.2',
    "par des entrées d’eaux pluviales, de neige ou de glace par des ouvertures fermées ou non, telles que portes, fenêtres, soupiraux, lucarne").
exclusion(degats_eaux_3_1_4, f(cause_eau, eau_souterraine), tout, oui, '3.1.4.2',
    "par les infiltrations d’eaux souterraines").
exclusion(degats_eaux_3_1_4, f(cause_eau, debordement_recipient), tout, oui, '3.1.4.2',
    "par les dommages causés par un objet non relié à l’installation hydraulique du bâtiment à l’exception des aquariums et matelas d’eau").
exclusion(degats_eaux_3_1_4, f(corrosion_visible, oui), tout, non, '3.1.4.2',
    "par des conduites, installations et appareils apparents présentant des points de corrosion visibles et non traités").
exclusion(degats_eaux_3_1_4, et([f(travaux_construction, oui), non(f(lien_causal_travaux, non))]), tout, oui, '3.1.4.2',
    "lorsque le bâtiment désigné est en cours de construction, de transformation ou de rénovation, à moins que l’Assuré ne démontre que cette circonstance n’a pas contribué à la survenance ou à l’aggravation des conséquences du sinistre").
exclusion(degats_eaux_3_1_4, f(cause_eau, condensation), tout, non, '3.1.4.2',
    "par l’hygrométrie ambiante, même consécutivement à un sinistre couvert").
exclusion(degats_eaux_3_1_4, f(cause_eau, condensation), tout, non, '3.1.4.2',
    "par des champignons ou des moisissures, même consécutivement à un sinistre couvert").
exclusion(degats_eaux_3_1_4, f(manque_entretien, oui), tout, non, '3.1.4.2',
    "par un défaut de réparation ou d’entretien, ou dus à une étanchéité absente, mal conçue ou mal réalisée").
exclusion(degats_eaux_3_1_4, f(travaux_batiment, entretien_reparation), tout, oui, '3.1.4.2',
    "lors du remplissage, de travaux de révision ou de réparation des installations et/ou citernes d’huiles minérales").
limite(degats_eaux_3_1_4, '3.1.4.1', "La perte d’eau subie à l’occasion d’un sinistre couvert est prise en charge à concurrence de 1.000 €.", "1000").
exclusion([degats_eaux_3_1_4], f(option_degats_eaux, non), tout, oui, '3.1.4',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ dégâts des eaux ” est souscrite.").
