% --- Art. 3.1.3 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
evenement_traduit(electricite).
garantie(degats_electriques, "Dégâts électriques", '3.1.3.1',
    "La Compagnie assure les biens désignés contre l'action de l'électricité.").
perimetre(degats_electriques, f(evenement, electricite)).
perimetre(degats_electriques, concept(batiment_designe)).
exclusion(degats_electriques, et([f(bien, appareil_informatique), f(usage_professionnel, oui)]), bien(appareil_informatique), non, '3.1.3.2',
    "les équipements informatiques et bureautiques à usage professionnel").
exclusion(degats_electriques, f(proprietaire, hote), tout, oui, '3.1.3.2',
    "les équipements dont l'Assuré n'est pas propriétaire").
exclusion(degats_electriques, f(support_donnees_ou_logiciel, oui), tout, non, '3.1.3.2',
    "les dégâts à tous supports de données et aux logiciels de traitement des données").
exclusion(degats_electriques, f(garantie_fabricant, oui), tout, non, '3.1.3.2',
    "les dégâts tombant sous la garantie du fabricant").
exclusion(degats_electriques, f(bien_marchandise, oui), tout, non, '3.1.3.2',
    "les dégâts aux appareils ou installations électriques constituant des marchandises").
exclusion(degats_electriques, et([f(travaux_construction, oui), non(f(lien_causal_travaux, non))]), tout, oui, '3.1.3.2',
    "les dégâts causés lorsque le bâtiment est en cours de construction, de transformation ou de rénovation à moins que l'Assuré démontre que cette circonstance n'a pas contribué à la survenance ou à l'aggravation des conséquences du sinistre").
exclusion(degats_electriques, f(bien, denrees_alimentaires), bien(denrees_alimentaires), non, '3.1.3.2',
    "les dégâts au contenu des appareils électroménagers").
exclusion(degats_electriques, f(appareil_plus_15_ans, oui), tout, oui, '3.1.3.2',
    "les dégâts aux appareils de plus de 15 ans d'âge").
exclusion(degats_electriques, ou([f(manque_entretien, oui), f(fonctionnement_defectueux, oui)]), tout, non, '3.1.3.2',
    "les pertes ou dommages qui sont la conséquence directe : – des effets continuels de l'exploitation (usure) ; – d'un fonctionnement défectueux").
limite(degats_electriques, '3.1.3.1', "Les dommages matériels occasionnés aux panneaux solaires et/ou installations photovoltaïques sont couverts à concurrence de 50.000 € par sinistre.", "50000").
exclusion([degats_electriques], f(option_degats_electriques, non), tout, oui, '3.1.3',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ dégâts électriques” est souscrite.").
