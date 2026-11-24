% --- Art. 3.3.1 : proposition rédigée par le modèle — mistral:mistral-large-4-0 (proposition écartée), 2026-11-24 ---
evenement_traduit(bris).
evenement_traduit(vol).
evenement_traduit(accident).
garantie(dommages_biens_bris, "Dommages aux biens : bris accidentel (option)", '3.3.1.1',
    "La Compagnie couvre tout bris ou destruction accidentel résultant d’une chute, d’un choc ou de la pénétration d’un corps étranger").
perimetre(dommages_biens_bris, f(evenement, bris)).
perimetre(dommages_biens_bris, ou([f(bien, instrument_musique), f(bien, materiel_sport), f(bien, velo), f(bien, materiel_medical), f(bien, materiel_photo), f(bien, bijoux)])).
circonstance(dommages_biens_bris, f(option_dommages_biens, oui), '3.3.1',
    "la garantie “dommages aux biens” est accordée").
exclusion(dommages_biens_bris, f(dommage_voile_seule, oui), tout, non, '3.3.1.3',
    "les dommages aux voiles des matériels utilisés dans le cadre de sports nautiques, aériens ou de glisse ; la Compagnie est tenue de payer une indemnité lorsque les voiles ne sont pas seules endommagées").
exclusion(dommages_biens_bris, f(usure_instrument, oui), tout, non, '3.3.1.3',
    "les vices de sonorité, la casse des cordes ainsi que les dommages aux peaux et aux anches des instruments de musique").
exclusion(dommages_biens_bris, f(emballage_inadapte, oui), tout, non, '3.3.1.3',
    "les dommages aux instruments de musique survenus en cours de transport et résultant d’une absence d’emballage ou d’un emballage inapproprié").
garantie(dommages_biens_vol, "Dommages aux biens : vol (option)", '3.3.1.1-a',
    "Sous réserve qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes, la Compagnie couvre également : 3.3.1.1.1 le vol de ces objets lorsqu’ils sont sous la surveillance directe et immédiate de l’Assuré ou des personnes qui l’accompagnent").
perimetre(dommages_biens_vol, f(evenement, vol)).
perimetre(dommages_biens_vol, ou([f(bien, instrument_musique), f(bien, materiel_sport), f(bien, velo), f(bien, materiel_medical), f(bien, materiel_photo), f(bien, bijoux)])).
circonstance(dommages_biens_vol, f(option_dommages_biens, oui), '3.3.1',
    "la garantie “dommages aux biens” est accordée").
circonstance(dommages_biens_vol, et([f(plainte_deposee, oui), ou([f(surveillance_directe, oui), f(lieu, autre_batiment), et([f(bien, velo), ou([f(lieu, cave), f(lieu, grenier), f(lieu, garage)]), f(local_ferme_cle, oui)]), et([f(local_ferme_cle, oui), ou([f(lieu, casier), f(lieu, chambre_etudiant), f(lieu, maison_repos), f(lieu, local_fete_privee)])]), et([f(lieu, vehicule), non(f(vol_de_nuit, oui)), ou([f(vehicule_vole, oui), f(effraction, oui)])]), et([f(bagage_enregistre, oui), non(ou([concept(batiment_designe), f(lieu, parties_communes), f(lieu, vehicule), f(lieu, annexe), f(lieu, jardin), f(lieu, terrasse), f(lieu, abri_jardin), f(lieu, autre_batiment), f(lieu, casier), f(lieu, veranda)]))])])]), '3.3.1.1-a',
    "Sous réserve qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes, la Compagnie couvre également : 3.3.1.1.1 le vol de ces objets lorsqu’ils sont sous la surveillance directe et immédiate de l’Assuré ou des personnes qui l’accompagnent ; 3.3.1.1.2 le vol de ces objets lorsqu’ils sont hors de la surveillance directe et immédiate de l’Assuré ou des personnes qui l’accompagnent : 3.3.1.1.2.1 dans la(les) résidence(s) secondaire(s) de l’Assuré ou dans ses locaux professionnels ; le vol des bicyclettes est également couvert dans les greniers, caves et garages fermés à clé et situés dans un immeuble collectif ; 3.3.1.1.2.2 occasionnellement, dans tous autres locaux clos, couverts et fermés à clé").
exclusion(dommages_biens_vol, ou([f(auteur, assure), f(auteur, famille), et([f(auteur, personnel_prive), ou([f(heures_service, oui), non(ou([f(effraction, oui), f(violence, oui)]))])])]), tout, oui, '3.3.1.3',
    "les vols commis par ou avec la complicité de ou du : n Preneur d’assurance, son conjoint, leurs ascendants ou descendants ainsi que les conjoints de ces personnes ; n l’Assuré ; n toute personne au service de l’Assuré pendant les heures de service et, si ces vols ont été commis en dehors de celles-ci, autrement que par effraction ou avec violence").
exclusion(dommages_biens_vol, et([f(lieu, vehicule), f(vehicule_ferme_cle, non)]), tout, non, '3.3.1.5',
    "La garantie est acquise dans ce second cas si : n la caravane ou la remorque est entièrement close et construite en bois, métal ou plastique rigide et vitrage").
exclusion(dommages_biens_vol, et([f(lieu, vehicule), f(vehicule_toit_souple, oui)]), tout, non, '3.3.1.5',
    "Par contre, la garantie n’est pas acquise si les objets assurés se trouvent dans l’habitacle d’un véhicule équipé d’un toit non rigide").
exclusion([dommages_biens_bris, dommages_biens_vol], f(proprietaire, hote), tout, oui, '3.3.1.3',
    "les objets et matériels dont l’Assuré n’est pas propriétaire").
exclusion([dommages_biens_bris, dommages_biens_vol], f(usage_professionnel, oui), tout, non, '3.3.1.3',
    "les objets et matériels utilisés à des fins professionnelles").
exclusion([dommages_biens_bris, dommages_biens_vol], f(bien, vehicule_moteur), bien(vehicule_moteur), non, '3.3.1.3',
    "les dommages aux véhicules automoteurs").
exclusion([dommages_biens_bris, dommages_biens_vol], f(bien, vetement_accessoire), bien(vetement_accessoire), non, '3.3.1.3',
    "les dommages aux vêtements et accessoires (casque, lunettes, gants, bottes, combinaison, …)").
exclusion([dommages_biens_bris, dommages_biens_vol], f(vice_defaut_connu, oui), tout, non, '3.3.1.3',
    "les dommages dus à des vices ou défauts qui existaient à la date d’effet de la présente assurance et qui étaient connus de l’Assuré ou de ses mandataires").
exclusion([dommages_biens_bris, dommages_biens_vol], ou([f(manque_entretien, oui), f(fonctionnement_defectueux, oui), f(evenement, tempete)]), tout, non, '3.3.1.3',
    "les dommages qui sont la conséquence directe : n de l’usure, de la détérioration lente, de la vétusté ou d’un défaut d’entretien ; n d’un fonctionnement défectueux ; n de la pluie, de la grêle et de toute autre manifestation atmosphérique").
exclusion([dommages_biens_bris, dommages_biens_vol], f(garantie_fabricant, oui), tout, non, '3.3.1.3',
    "les dommages dont le fabricant ou le fournisseur est légalement ou contractuellement responsable").
exclusion([dommages_biens_bris, dommages_biens_vol], f(type_dommage, rayure_ou_ecaillement), tout, non, '3.3.1.3',
    "les dommages d’ordre purement esthétique").
exclusion([dommages_biens_bris, dommages_biens_vol], f(evenement, electricite), tout, oui, '3.3.1.3',
    "les dommages d’origine électrique").
exclusion([dommages_biens_bris, dommages_biens_vol], f(evacuation_ordonnee, oui), tout, non, '3.3.1.6',
    "les effets du contrat sont suspendus de plein droit pendant la durée de l’évacuation des locaux renfermant les biens garantis lorsque celle-ci est ordonnée par les Autorités ou nécessitée par des faits de guerre ou des troubles civils").
