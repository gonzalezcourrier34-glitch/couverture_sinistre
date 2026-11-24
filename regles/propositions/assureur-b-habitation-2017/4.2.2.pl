% --- Art. 4.2.2 : proposition rédigée par le modèle — mistral:mistral-large-4-0 (proposition écartée), 2026-11-24 ---
evenement_traduit(vol).
evenement_traduit(bris).
evenement_traduit(accident).
evenement_traduit(incendie).
evenement_traduit(explosion).
evenement_traduit(degat_eaux).
evenement_traduit(voyage).
garantie(bagages_vol, "Bagages en voyage : vol (option)", '4.2.2.1',
    "La Compagnie garantit à l’Assuré la couverture de ses bagages emportés dans le cadre d’un voyage contre : n le vol,pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes ; n la perte, n les dégâts dus à toute circonstance fortuite survenue pendant le voyage").
perimetre(bagages_vol, f(evenement, vol)).
perimetre(bagages_vol, ou([f(lieu, voie_publique), f(lieu, vehicule), f(lieu, autre_batiment)])).
perimetre(bagages_vol, f(en_voyage, oui)).
perimetre(bagages_vol, non(ou([f(bien, vehicule_moteur), f(bien, remorque)]))).
circonstance(bagages_vol, f(option_bagages, oui), '4.2.2',
    "la garantie “ bagages” est souscrite").
circonstance(bagages_vol, et([f(plainte_deposee, oui), ou([non(f(lieu, vehicule)), f(bagage_enregistre, oui), et([non(f(vol_de_nuit, oui)), ou([f(vehicule_vole, oui), f(effraction, oui)])])])]), '4.2.2.3',
    "Lorsque les bagages sont non enregistrés et se trouvent à l’intérieur d’un véhicule, d’une caravane, d’une remorque ou d’un bateau, le vol est couvert entre sept heures et vingt-deux heures et à condition qu’il soit accompagné : n du vol simultané du véhicule, de la caravane, de la remorque ou du bateau ; n de l’effraction caractérisée du véhicule, du coffre ou de la cabine du bateau").
exclusion(bagages_vol, et([f(en_voyage, oui), ou([f(auteur, assure), f(auteur, famille)])]), tout, non, '4.2.2.4',
    "les vols commis par ou avec la complicité de ou du : n Preneur d’assurance, son conjoint, leurs ascendants ou descendants ainsi que les conjoints de ces personnes ; n l’Assuré").
exclusion(bagages_vol, et([f(en_voyage, oui), f(lieu, vehicule), f(vehicule_ferme_cle, non)]), tout, non, '4.2.2.3',
    "toutes les portes du véhicule ou de la cabine de bateau où se trouvent les objets garantis y compris le volet ou la porte fermant le coffre aménagé dans la carrosserie de la voiture ou de la caravane ou encore dans la coque du bateau, sont bloqués en position de fermeture ; n les vitrages sont fermés et le “toit ouvrant” est bloqué en position de fermeture").
exclusion(bagages_vol, et([f(en_voyage, oui), f(lieu, vehicule), f(vehicule_toit_souple, oui)]), tout, non, '4.2.2.3',
    "La garantie n’est pas acquise si les bagages se trouvent dans l’habitacle d’un véhicule équipé d’un toit non rigide").
exclusion(bagages_vol, et([f(en_voyage, oui), f(surveillance_directe, non), f(lieu, voie_publique)]), tout, non, '4.2.2.4',
    "les bagages laissés sans surveillance dans un lieu public").
exclusion(bagages_vol, et([f(bien, valeurs), f(en_voyage, oui)]), bien(valeurs), non, '4.2.2.1',
    "Les valeurs ne sont pas assimilées à des bagages").
exclusion(bagages_vol, et([f(en_voyage, oui), f(proprietaire, hote)]), tout, non, '4.2.2.4',
    "les bagages dont l’Assuré n’est pas propriétaire").
limite(bagages_vol, '4.2.2.1', "à concurrence de 5.000 € par sinistre", "5000").
garantie(bagages_valeurs_agression, "Valeurs emportées en voyage : vol par agression (option)", '4.2.2.1',
    "Pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes, la Compagnie garantit toutefois à l’Assuré le vol par agression des valeurs emportées en voyage").
perimetre(bagages_valeurs_agression, f(evenement, vol)).
perimetre(bagages_valeurs_agression, f(bien, valeurs)).
perimetre(bagages_valeurs_agression, ou([f(lieu, voie_publique), f(lieu, vehicule), f(lieu, autre_batiment)])).
perimetre(bagages_valeurs_agression, f(en_voyage, oui)).
perimetre(bagages_valeurs_agression, non(ou([f(bien, vehicule_moteur), f(bien, remorque)]))).
circonstance(bagages_valeurs_agression, f(option_bagages, oui), '4.2.2',
    "la garantie “ bagages” est souscrite").
circonstance(bagages_valeurs_agression, et([f(plainte_deposee, oui), f(violence, oui)]), '4.2.2.1',
    "Pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes, la Compagnie garantit toutefois à l’Assuré le vol par agression des valeurs emportées en voyage").
exclusion(bagages_valeurs_agression, et([f(en_voyage, oui), ou([f(auteur, assure), f(auteur, famille)])]), tout, non, '4.2.2.4',
    "les vols commis par ou avec la complicité de ou du : n Preneur d’assurance, son conjoint, leurs ascendants ou descendants ainsi que les conjoints de ces personnes ; n l’Assuré").
exclusion(bagages_valeurs_agression, et([f(en_voyage, oui), f(proprietaire, hote)]), tout, non, '4.2.2.4',
    "les bagages dont l’Assuré n’est pas propriétaire").
limite(bagages_valeurs_agression, '4.2.2.1', "à concurrence de 5.000 € par sinistre", "5000").
garantie(bagages_bris, "Bagages en voyage : casse accidentelle (option)", '4.2.2.1',
    "La Compagnie garantit à l’Assuré la couverture de ses bagages emportés dans le cadre d’un voyage contre : n le vol,pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes ; n la perte, n les dégâts dus à toute circonstance fortuite survenue pendant le voyage").
perimetre(bagages_bris, f(evenement, bris)).
perimetre(bagages_bris, ou([f(lieu, voie_publique), f(lieu, vehicule), f(lieu, autre_batiment)])).
perimetre(bagages_bris, f(en_voyage, oui)).
perimetre(bagages_bris, non(ou([f(bien, vehicule_moteur), f(bien, remorque)]))).
circonstance(bagages_bris, f(option_bagages, oui), '4.2.2',
    "la garantie “ bagages” est souscrite").
exclusion(bagages_bris, et([ou([f(bien, instrument_musique), f(bien, miroir), f(bien, objet_verre_non_vitre)]), non(f(accident_circulation, oui))]), tout, oui, '4.2.2.4',
    "la casse d’objets fragiles tels pendules, porcelaines, glaces, instruments de musique, à moins que celle-ci ne résulte d’un incendie, d’un vol ou d’un accident de la circulation impliquant le moyen de transport").
exclusion(bagages_bris, et([f(en_voyage, oui), f(bagage_dommage_esthetique, oui)]), tout, non, '4.2.2.4',
    "les dommages d’ordre purement esthétique").
exclusion(bagages_bris, et([f(en_voyage, oui), f(deterioration_lente_ou_parasites, oui)]), tout, non, '4.2.2.4',
    "de l’usure, de la détérioration lente, de la vétusté ou d’un défaut d’entretien ; n de l’humidité, des mites, des vers ou des parasites").
exclusion(bagages_bris, et([f(en_voyage, oui), f(cause_intemperie, oui)]), tout, non, '4.2.2.4',
    "de la pluie, de la grêle et de toute autre manifestation atmosphérique").
exclusion(bagages_bris, et([f(bien, valeurs), f(en_voyage, oui)]), bien(valeurs), non, '4.2.2.1',
    "Les valeurs ne sont pas assimilées à des bagages").
exclusion(bagages_bris, et([f(en_voyage, oui), f(proprietaire, hote)]), tout, non, '4.2.2.4',
    "les bagages dont l’Assuré n’est pas propriétaire").
limite(bagages_bris, '4.2.2.1', "à concurrence de 5.000 € par sinistre", "5000").
garantie(bagages_sinistre, "Bagages en voyage : incendie, explosion, dégât des eaux (option)", '4.2.2.1',
    "La Compagnie garantit à l’Assuré la couverture de ses bagages emportés dans le cadre d’un voyage contre : n le vol,pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes ; n la perte, n les dégâts dus à toute circonstance fortuite survenue pendant le voyage").
perimetre(bagages_sinistre, ou([f(evenement, incendie), f(evenement, explosion), f(evenement, degat_eaux)])).
perimetre(bagages_sinistre, ou([f(lieu, voie_publique), f(lieu, vehicule), f(lieu, autre_batiment)])).
perimetre(bagages_sinistre, f(en_voyage, oui)).
perimetre(bagages_sinistre, non(ou([f(bien, vehicule_moteur), f(bien, remorque)]))).
circonstance(bagages_sinistre, f(option_bagages, oui), '4.2.2',
    "la garantie “ bagages” est souscrite").
exclusion(bagages_sinistre, et([f(en_voyage, oui), f(deterioration_lente_ou_parasites, oui)]), tout, non, '4.2.2.4',
    "de l’usure, de la détérioration lente, de la vétusté ou d’un défaut d’entretien ; n de l’humidité, des mites, des vers ou des parasites").
exclusion(bagages_sinistre, et([f(en_voyage, oui), f(cause_intemperie, oui)]), tout, non, '4.2.2.4',
    "de la pluie, de la grêle et de toute autre manifestation atmosphérique").
exclusion(bagages_sinistre, et([f(bien, valeurs), f(en_voyage, oui)]), bien(valeurs), non, '4.2.2.1',
    "Les valeurs ne sont pas assimilées à des bagages").
limite(bagages_sinistre, '4.2.2.1', "à concurrence de 5.000 € par sinistre", "5000").
garantie(bagages_perte, "Bagages en voyage : perte (option)", '4.2.2.1',
    "La Compagnie garantit à l’Assuré la couverture de ses bagages emportés dans le cadre d’un voyage contre : n le vol,pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes ; n la perte, n les dégâts dus à toute circonstance fortuite survenue pendant le voyage").
perimetre(bagages_perte, f(evenement, voyage)).
perimetre(bagages_perte, f(objet_voyage, perte_bagage)).
circonstance(bagages_perte, f(option_bagages, oui), '4.2.2',
    "la garantie “ bagages” est souscrite").
exclusion(bagages_perte, f(bagage_oublie, oui), tout, non, '4.2.2.4',
    "les bagages oubliés").
exclusion(bagages_perte, f(saisie_autorites, oui), tout, non, '4.2.2.4',
    "les pertes et dégâts causés à l’occasion d’une saisie par les autorités publiques (police, douane, …)").
exclusion(bagages_perte, f(bien, valeurs), bien(valeurs), non, '4.2.2.1',
    "Les valeurs ne sont pas assimilées à des bagages").
limite(bagages_perte, '4.2.2.1', "à concurrence de 5.000 € par sinistre", "5000").
exclusion([bagages_vol, bagages_valeurs_agression, bagages_bris, bagages_sinistre, bagages_perte], et([f(en_voyage, oui), f(bagage_oublie, oui)]), tout, non, '4.2.2.4',
    "les bagages oubliés").
exclusion([bagages_vol, bagages_valeurs_agression, bagages_bris, bagages_sinistre, bagages_perte], et([f(en_voyage, oui), f(saisie_autorites, oui)]), tout, non, '4.2.2.4',
    "les pertes et dégâts causés à l’occasion d’une saisie par les autorités publiques (police, douane, …)").
exclusion([bagages_vol, bagages_valeurs_agression, bagages_bris, bagages_sinistre, bagages_perte], et([f(bagage_exterieur_vehicule, oui), non(f(accident_circulation, oui))]), tout, oui, '4.2.2.1',
    "Les bagages transportés à l’extérieur d’un véhicule sont uniquement couverts contre les conséquences d’un accident de la circulation impliquant le moyen de transport").
