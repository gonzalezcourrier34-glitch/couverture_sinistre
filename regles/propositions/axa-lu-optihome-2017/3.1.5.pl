% --- Art. 3.1.5 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
evenement_traduit(bris).
garantie(bris_vitrages, "Bris de vitrages", '3.1.5.1',
    "La Compagnie assure les biens désignés, contre les bris et fêlures accidentels des vitrages, des glaces et des miroirs.").
perimetre(bris_vitrages, f(evenement, bris)).
perimetre(bris_vitrages, ou([f(bien, vitre), f(bien, miroir), f(bien, panneau_solaire), f(bien, sanitaire), f(bien, serre), f(bien, table_cuisson_vitroceramique), f(bien, appareil_electromenager), f(bien, cadre), f(bien, chassis), f(bien, soubassement), f(cause_projection_debris, oui)])).
circonstance(bris_vitrages, si(f(type_dommage, opacification_ou_perte_etancheite), non(ou([f(garantie_fabricant, oui), f(statut_assure_batiment, locataire)]))), '3.1.5.1',
    "à la perte d’étanchéité des vitrages isolants sauf s’ils sont sous garantie ou si l’Assuré est locataire").
exclusion(bris_vitrages, f(type_dommage, rayure_ou_ecaillement), tout, non, '3.1.5.2',
    "Les rayures, égratignures et écaillements ne sont jamais assurés.").
exclusion(bris_vitrages, f(bien, appareil_audiovisuel), tout, non, '3.1.5.2',
    "aux parties vitrées du matériel multimédia").
exclusion(bris_vitrages, et([concept(batiment_designe), f(travaux_construction, oui), non(f(lien_causal_travaux_sinistre, non))]), tout, oui, '3.1.5.2',
    "au bâtiment désigné lorsqu’il est en cours de construction, de transformation ou de rénovation, à moins que l’Assuré ne démontre que cette circonstance n’a pas contribué à la survenance ou à l’aggravation des conséquences du sinistre").
exclusion(bris_vitrages, f(bien, verre_optique), tout, non, '3.1.5.2',
    "aux verres optiques et lunettes").
exclusion(bris_vitrages, ou([f(bien, chassis_couche), f(bien, enseigne)]), tout, non, '3.1.5.2',
    "aux châssis de couche et aux enseignes").
exclusion(bris_vitrages, ou([f(vitre_placee, non), f(vitrage_en_deplacement, oui)]), tout, oui, '3.1.5.2',
    "aux vitrages non encore placés ou pendant leur déplacement").
exclusion(bris_vitrages, et([f(lieu, parties_communes), ou([f(statut_assure_batiment, proprietaire), f(statut_assure_batiment, locataire), f(occupation_partielle, oui)])]), tout, oui, '3.1.5.2',
    "aux vitrages relevant des parties communes du bâtiment désigné lorsque l’Assuré est propriétaire, locataire ou occupant partiel").
exclusion(bris_vitrages, f(bien, objet_verre_non_vitre), tout, non, '3.1.5.2',
    "aux objets en verre, par exemple lustres, vases, vaisselle").
exclusion(bris_vitrages, f(manque_entretien, oui), tout, oui, '3.1.5.2',
    "par un défaut de réparation ou d’entretien des châssis, soubassements et support de vitres, glaces et miroirs").
limite(bris_vitrages, '3.1.5.1', "Les dommages matériels occasionnés aux vitrages des panneaux solaires et/ou installations photovoltaïques sont couverts à concurrence de 50.000€ par sinistre.", "50000").
