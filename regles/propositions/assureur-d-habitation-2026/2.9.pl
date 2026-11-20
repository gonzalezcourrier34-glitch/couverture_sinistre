% --- Art. 2.9 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(catastrophe_naturelle).
garantie(catastrophe_naturelle_dommages_materiels, "Dommages matériels directs par catastrophe naturelle", '2.9-a',
    "La garantie couvre les dommages matériels directs non assurables ayant eu pour cause déterminante l’intensité anormale d’un agent naturel, lorsque les mesures habituelles à prendre pour prévenir ces dommages n’ont pu empêcher leur survenance ou n’ont pu être prises.").
perimetre(catastrophe_naturelle_dommages_materiels, f(evenement, catastrophe_naturelle)).
perimetre(catastrophe_naturelle_dommages_materiels, concept(batiment)).
circonstance(catastrophe_naturelle_dommages_materiels, f(dommage_non_assurable_ailleurs, oui), '2.9-a',
    "dommages matériels directs non assurables").
circonstance(catastrophe_naturelle_dommages_materiels, f(mesures_prevention_habituelles_non_efficaces, oui), '2.9-a',
    "lorsque les mesures habituelles à prendre pour prévenir ces dommages n’ont pu empêcher leur survenance ou n’ont pu être prises").
circonstance(catastrophe_naturelle_dommages_materiels, f(declaration_dans_30j_apres_arrete, oui), '2.9-a',
    "La garantie est mise en jeu par une déclaration faite au plus tard trente jours après publication au Journal Officiel d’un arrêté interministériel constatant l’état de catastrophe naturelle").
circonstance(catastrophe_naturelle_dommages_materiels, si(f(catastrophe, secheresse_rehydratation), ou([ou([f(affecte_solidite_bati, oui), f(entrave_usage_normal, oui)]), f(evolution_defavorable_probable, oui)])), '2.9-a',
    "pour les dommages ayant eu pour cause déterminante les mouvements de terrain différentiels consécutifs à la sécheresse et à la réhydratation des sols, la garantie prévue à l’article L. 125-1 du Code couvre l’ensemble des dommages qui affectent la solidité du bâti ou entravent l’usage normal des bâtiments. Les dommages ne présentant pas ces caractéristiques au moment du constat des désordres sont également couverts par la garantie dès lors qu’ils sont de nature à évoluer défavorablement et à affecter la solidité du bâti ou à entraver l’usage normal des bâtiments (Article R. 125-7 du Code)").
exclusion(catastrophe_naturelle_dommages_materiels, et([f(terrain_non_constructible, oui), non(f(bien_existant_avant_publication_plan, oui))]), tout, oui, '2.9-b',
    "les biens assurés construits sur des terrains classés inconstructibles par un plan de prévention des risques à l’exception toutefois des biens existants antérieurement à la publication de ce plan (article L. 125-6 du Code)").
exclusion(catastrophe_naturelle_dommages_materiels, f(construction_violation_regles_administratives, oui), tout, oui, '2.9-b',
    "les biens immobiliers construits en violation des règles administratives en vigueur lors de leur mise en place et tendant à prévenir les dommages causés par une catastrophe naturelle (article L. 125-6 du Code)").
exclusion(catastrophe_naturelle_dommages_materiels, et([f(catastrophe, secheresse_rehydratation), f(bien_annexe_habitation, oui), non(f(element_indissociable_ouvrages_principaux, oui))]), tout, oui, '2.9-b',
    "en cas de dommages ayant eu pour cause déterminante les mouvements de terrain différentiels consécutifs à la sécheresse et à la réhydratation des sols, les dommages survenus sur les constructions constitutives d’éléments annexes aux parties à usage d’habitation, tels que notamment les remises, les garages et parkings, les terrasses, les murs de clôture extérieurs, les serres, les terrains de jeux ou les piscines et leurs éléments architecturaux connexes, sauf lorsque ces éléments font indissociablement corps avec les ouvrages de viabilité, de fondation, d’ossature, de clos ou de couvert (Article R. 125-7 du Code)").
garantie(catastrophe_naturelle_relogement_urgence, "Frais de relogement d'urgence", '2.9-a',
    "Sont également considérés comme les effets des catastrophes naturelles les frais de relogement d’urgence des personnes sinistrées dont la résidence principale est rendue impropre à l’habitation pour des raisons de sécurité, de salubrité ou d’hygiène qui résultent de ces dommages matériels directs non assurables ayant eu pour cause déterminante l’intensité anormale d’un agent naturel.").
circonstance(catastrophe_naturelle_relogement_urgence, et([f(residence_principale_inhabitable, oui), ou([f(raison_inhabitabilite, securite), f(raison_inhabitabilite, salubrite), f(raison_inhabitabilite, hygiene)])]), '2.9-a',
    "dont la résidence principale est rendue impropre à l’habitation pour des raisons de sécurité, de salubrité ou d’hygiène qui résultent de ces dommages matériels directs non assurables ayant eu pour cause déterminante l’intensité anormale d’un agent naturel").
accessoire(catastrophe_naturelle_relogement_urgence).
