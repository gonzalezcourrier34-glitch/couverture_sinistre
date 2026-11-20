% --- Art. 2.4 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(degat_eaux).
evenement_traduit(mazout).
garantie(venues_eau_gel, "Venues d'eau et gel", '2.4-a',
    "La garantie couvre les dommages résultant : • d’eaux de ruissellement à la surface du sol, • du refoulement des égouts, • d’infiltrations par les toitures").
perimetre(venues_eau_gel, f(evenement, degat_eaux)).
perimetre(venues_eau_gel, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(venues_eau_gel, concept(batiment)).
circonstance(venues_eau_gel, ou([f(cause_eau, inondation), f(cause_eau, infiltration_toiture), f(cause_eau, infiltration_exterieure), f(cause_eau, fuite_installation), f(cause_eau, gel), f(cause_eau, piscine_exterieure), f(cause_eau, debordement_recipient), f(cause_eau, debordement_aquarium)]), '2.4-a',
    "La garantie couvre les dommages résultant : • d’eaux de ruissellement à la surface du sol…• de débordements et renversements de récipients ou d’aquariums").
exclusion(venues_eau_gel, et([f(cause_eau, fuite_installation), f(canalisation_enterree, oui)]), tout, non, '2.4-c',
    "les dommages consécutifs à des fuites d’eau ou débordements provenant des canalisations enterrées").
exclusion(venues_eau_gel, et([f(bien, canalisation), f(canalisation_enterree, oui)]), bien(canalisation), non, '2.4-c',
    "les dommages sur les canalisations enterrées").
exclusion(venues_eau_gel, et([f(cause_eau, infiltration_exterieure), f(batiment_moins_10_ans, oui)]), tout, oui, '2.4-c',
    "les dommages résultant d’infiltrations à travers les murs et façades extérieurs lorsque la garantie décennale du constructeur doit s’appliquer").
exclusion(venues_eau_gel, f(evenement, catastrophe_naturelle), tout, non, '2.4-c',
    "les dommages relevant de la garantie Catastrophes naturelles").
exclusion(venues_eau_gel, f(cause_eau, condensation), tout, non, '2.4-c',
    "les dommages dus à l’humidité et/ou à la condensation").
garantie(recherche_fuite, "Recherche de fuite", '2.4-a',
    "Sont prises en charge au titre de la recherche de fuite").
perimetre(recherche_fuite, f(evenement, degat_eaux)).
perimetre(recherche_fuite, concept(batiment)).
garantie(debordement_cuves, "Débordement des cuves de combustible (Excellence)", '2.4-b',
    "les dommages résultant du débordement accidentel des cuves situées à l’intérieur des bâtiments principaux d’habitation et de leurs dépendances et contenant le combustible nécessaire à l’alimentation du chauffage").
perimetre(debordement_cuves, f(evenement, mazout)).
perimetre(debordement_cuves, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(debordement_cuves, concept(batiment)).
circonstance(debordement_cuves, f(formule, excellence), '2.4-b',
    "Sont également garantis : • les dommages résultant du débordement accidentel des cuves").
exclusion(debordement_cuves, f(bien, mazout), bien(mazout), non, '2.4-c',
    "le coût du combustible perdu, en cas de débordement accidentel des cuves").
accessoire(recherche_fuite).
