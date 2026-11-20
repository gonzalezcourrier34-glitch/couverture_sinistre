% --- Art. 2.4 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(degat_eaux).
garantie(venues_eau_gel_base_2_4_a, "Venues d'eau et gel - garantie de base", '2.4-a',
    "La garantie couvre les dommages résultant : • d’eaux de ruissellement à la surface du sol, • du refoulement des égouts, • d’infiltrations par les toitures, ciels vitrés, terrasses formant toiture, • de fuites d’eau ou débordements provenant des conduites non enterrées, des piscines, de tous appareils à effet d’eau et d’installations de chauffage ou de sécurité, • d’infiltrations au travers des murs non enterrés et façades extérieurs. Dès la constatation de l’origine du sinistre et pour ce type d’événement, la garantie sera suspendue de plein droit et ne sera remise en vigueur que lorsque les travaux nécessaires à l’étanchéité des murs extérieurs et façades auront été effectués, • du gel des conduites et des appareils à effet d’eau à l’intérieur de vos locaux isolés, • d’infiltrations par les gaines d’aération ou de ventilation, • de débordements et renversements de récipients ou d’aquariums.").
perimetre(venues_eau_gel_base_2_4_a, f(evenement, degat_eaux)).
perimetre(venues_eau_gel_base_2_4_a, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(venues_eau_gel_base_2_4_a, concept(batiment)).
circonstance(venues_eau_gel_base_2_4_a, ou([f(cause_eau, ruissellement), f(cause_eau, refoulement_egouts), f(cause_eau, infiltration_toiture), et([f(cause_eau, fuite_installation), f(canalisation_encastree, non)]), f(cause_eau, piscine), f(cause_eau, fuite_appareil_eau), f(cause_eau, infiltration_exterieure), f(cause_eau, gel), f(cause_eau, infiltration_gaines_aeration), f(cause_eau, debordement_recipient), f(cause_eau, debordement_aquarium)]), '2.4-a',
    "La garantie couvre les dommages résultant : • d’eaux de ruissellement à la surface du sol, • du refoulement des égouts, • d’infiltrations par les toitures, ciels vitrés, terrasses formant toiture, • de fuites d’eau ou débordements provenant des conduites non enterrées, des piscines, de tous appareils à effet d’eau et d’installations de chauffage ou de sécurité, • d’infiltrations au travers des murs non enterrés et façades extérieurs, • du gel des conduites et des appareils à effet d’eau à l’intérieur de vos locaux isolés, • d’infiltrations par les gaines d’aération ou de ventilation, • de débordements et renversements de récipients ou d’aquariums.").
exclusion(venues_eau_gel_base_2_4_a, et([f(cause_eau, fuite_installation), f(canalisation_encastree, oui)]), tout, oui, '2.4-c',
    "les dommages consécutifs à des fuites d’eau ou débordements provenant des canalisations enterrées").
exclusion(venues_eau_gel_base_2_4_a, et([f(bien, canalisation), f(canalisation_encastree, oui)]), bien(canalisation), oui, '2.4-c',
    "les dommages sur les canalisations enterrées").
exclusion(venues_eau_gel_base_2_4_a, et([f(cause_eau, infiltration_exterieure), f(garantie_decennale_constructeur, oui)]), tout, oui, '2.4-c',
    "les dommages résultant d’infiltrations à travers les murs et façades extérieurs lorsque la garantie décennale du constructeur doit s’appliquer").
exclusion(venues_eau_gel_base_2_4_a, f(releve_garantie_catastrophes_naturelles, oui), tout, oui, '2.4-c',
    "les dommages relevant de la garantie Catastrophes naturelles").
exclusion(venues_eau_gel_base_2_4_a, f(cause_eau, condensation), tout, oui, '2.4-c',
    "les dommages dus à l’humidité et/ou à la condensation").
exclusion(venues_eau_gel_base_2_4_a, et([f(bien_a_l_origine_sinistre, oui), non(f(cause_eau, gel))]), tout, oui, '2.4-c',
    "les frais de réparation ou de remplacement de l’élément à l’origine du dommage couvert par le contrat. Cette exclusion ne s’applique pas lorsque le dommage résulte du gel").
garantie(recherche_fuite_2_4_a, "Recherche de fuite", '2.4-a',
    "Sont prises en charge au titre de la recherche de fuite : • la recherche de fuite destructrice ou non destructrice à l’intérieur dans des locaux assurés, • les détériorations immobilières nécessitées par la recherche de la fuite dans les locaux assurés en cas de dommages consécutifs à une origine garantie définie ci-dessus.").
perimetre(recherche_fuite_2_4_a, concept(batiment)).
garantie(debordement_cuve_combustible_excellence_2_4_b, "Débordement accidentel des cuves de combustible - Formule Excellence", '2.4-b',
    "les dommages résultant du débordement accidentel des cuves situées à l’intérieur des bâtiments principaux d’habitation et de leurs dépendances et contenant le combustible nécessaire à l’alimentation du chauffage").
perimetre(debordement_cuve_combustible_excellence_2_4_b, f(evenement, degat_eaux)).
perimetre(debordement_cuve_combustible_excellence_2_4_b, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(debordement_cuve_combustible_excellence_2_4_b, concept(batiment)).
circonstance(debordement_cuve_combustible_excellence_2_4_b, et([f(cause_eau, debordement_cuve_combustible), f(formule, excellence)]), '2.4-b',
    "les dommages résultant du débordement accidentel des cuves situées à l’intérieur des bâtiments principaux d’habitation et de leurs dépendances et contenant le combustible nécessaire à l’alimentation du chauffage").
exclusion(debordement_cuve_combustible_excellence_2_4_b, et([f(bien, mazout), f(cause_eau, debordement_cuve_combustible)]), bien(mazout), oui, '2.4-c',
    "le coût du combustible perdu, en cas de débordement accidentel des cuves").
garantie(surconsommation_eau_excellence_2_4_b, "Frais de surconsommation d'eau - Formule Excellence", '2.4-b',
    "les frais de surconsommation d’eau consécutifs à une venue d’eaux ayant causé des dommages mobiliers ou immobiliers indemnisés au titre du présent contrat. Ces frais devront être justifiés par la production de factures attestant de la surconsommation d’eau.").
circonstance(surconsommation_eau_excellence_2_4_b, f(formule, excellence), '2.4-b',
    "les frais de surconsommation d’eau consécutifs à une venue d’eaux ayant causé des dommages mobiliers ou immobiliers indemnisés au titre du présent contrat").
accessoire(recherche_fuite_2_4_a).
accessoire(surconsommation_eau_excellence_2_4_b).
