% --- Art. 3.1.2 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
evenement_traduit(tempete).
definition(tempete, et([f(alea_tempete, vent), f(vent_80_kmh_irm, oui)]), '3.1.2.1',
    "la tempête (à partir de 80km/h)").
garantie(tempete_grele, "Tempête et grêle", '3.1.2.1',
    "La Compagnie assure les biens désignés contre la tempête (à partir de 80km/h), la grêle, le poids de la neige ou de la glace, y compris les dommages liés aux précipitations atmosphériques telles que pluie, neige ou grêle qui pénètrent à l'intérieur du bâtiment désigné par le fait que celui-ci a été préalablement endommagé par les événements précités.").
perimetre(tempete_grele, f(evenement, tempete)).
perimetre(tempete_grele, concept(batiment_designe)).
circonstance(tempete_grele, concept(tempete), '3.1.2.1',
    "la tempête (à partir de 80km/h)").
circonstance(tempete_grele, ou([f(alea_tempete, grele), f(alea_tempete, neige_glace)]), '3.1.2.1',
    "la grêle, le poids de la neige ou de la glace").
exclusion(tempete_grele, f(manque_entretien, oui), tout, oui, '3.1.2.2',
    "Ne sont toutefois pas couverts les dommages n résultant d'un défaut de réparation ou d'entretien du bâtiment désigné").
exclusion(tempete_grele, et([non(f(bien, element_batiment)), non(f(batiment_endommage_prealablement, oui))]), tout, oui, '3.1.2.2',
    "n causés au contenu se trouvant dans une construction non préalablement endommagée par le vent de tempête, la grêle, la pression de la neige ou de la glace").
exclusion(tempete_grele, et([ou([f(lieu, jardin), f(lieu, terrasse), f(lieu, abri_jardin)]), non(f(bien, mobilier_jardin))]), tout, oui, '3.1.2.2',
    "n causés à tout objet non fixé se trouvant à l'extérieur d'une construction, à l'exception du mobilier de jardin").
exclusion(tempete_grele, f(objet_fixe_exterieurement, oui), tout, oui, '3.1.2.2',
    "n causés aux objets suivants fixés extérieurement alors même qu'ils seraient réputés immeubles par destination : mât, poteau, pylône, panneau publicitaire, lampadaire, enseigne, tente, bâche , décoration de toit (girouette, …)").
exclusion(tempete_grele, f(piscine, oui), tout, oui, '3.1.2.2',
    "piscines, sauf si mention en est faite aux conditions particulières").
exclusion(tempete_grele, et([f(travaux_construction, oui), non(f(construction_close, oui))]), tout, oui, '3.1.2.2',
    "bâtiments en cours de construction, transformation, rénovation à moins que l'assuré ne démontre que cette circonstance n'a pas contribué à la survenance ou à l'aggravation des conséquences du sinistre. Cette exclusion est sans objet si cette construction est close et couverte définitivement avec portes et fenêtres posées à demeure").
exclusion(tempete_grele, f(construction_delabree, oui), tout, oui, '3.1.2.2',
    "constructions en démolition ou délabrées, c'est-à-dire si le degré de vétusté de la partie sinistrée dépasse 40%").
exclusion(tempete_grele, f(materiaux_legers_murs, oui), tout, oui, '3.1.2.2',
    "constructions dont les murs extérieurs composés de tôle, d'aggloméré de ciment et d'asbeste, de plaques ondulées ou de matériaux légers notamment bois, argile, matière plastique, panneaux agglomérés de bois et analogues représentent plus de 50% de la superficie totale de ces murs").
exclusion(tempete_grele, f(materiaux_legers_toiture, oui), tout, oui, '3.1.2.2',
    "constructions dont la toiture composée de bois, d'aggloméré de bois ou analogues, de carton bitumé, de matières plastiques ou d'autres matériaux légers (ardoises et tuiles artificielles, chaume ou roofing non compris) représente plus de 20% de la superficie totale de cette toiture").
exclusion(tempete_grele, et([f(construction_close, non), non(f(abri_fixe_sol, oui))]), tout, oui, '3.1.2.2',
    "constructions totalement ou partiellement ouvertes, à l'exception des auvents et marquises en matériaux durs, car-ports et pergolas, sous réserve que ces équipements soient solidement fixés au bâtiment ou qu'ils reposent sur des fondations").
exclusion(tempete_grele, f(deformation_sans_perte_etancheite, oui), tout, oui, '3.1.2.2',
    "n causés par la pression de la neige ou de la glace et consistant en la déformation des tuyaux de descente ou du toit sans que cette déformation ait une influence sur l'étanchéité de ceux-ci").
exclusion(tempete_grele, f(choc_thermique, oui), tout, oui, '3.1.2.2',
    "n causés par un choc thermique, c'est-à-dire une variation brutale de la température").
exclusion(tempete_grele, f(dommage_esthetique, oui), tout, oui, '3.1.2.2',
    "n d'ordre purement esthétique").
limite(tempete_grele, '3.1.2.1', "Les dommages matériels occasionnés aux panneaux solaires et/ou installations photovoltaïques sont couverts à concurrence de 50.000 € par sinistre.", "50000").
limite(tempete_grele, '3.1.2.2', "Dans ce cas, la prise en charge des dommages se fait sans application de la règle proportionnelle à concurrence de 5.000 € par sinistre", "5000").
