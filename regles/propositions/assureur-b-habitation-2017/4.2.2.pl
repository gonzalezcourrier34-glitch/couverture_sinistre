% --- Art. 4.2.2 : proposition rédigée par le modèle — mistral:mistral-large-4-0, 2026-11-24 ---
evenement_traduit(vol).
evenement_traduit(autre).
evenement_traduit(accident).
definition(bagage, ou([f(bien, objet_divers), et([f(bien, valeurs), f(vol_sur_personne, oui), f(plainte_deposee, oui)])]), '4.2.2.1',
    "On entend par bagage tout objet à usage personnel que l’Assuré emporte pendant un voyage ou qui, dûment enregistré, le précède ou le suit, ainsi que les biens personnels achetés au cours du voyage pour être ramenés au domicile habituel de l’Assuré. Les valeurs ne sont pas assimilées à des bagages. Pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes, la Compagnie garantit toutefois à l’Assuré le vol par agression des valeurs emportées en voyage.").
garantie(bagages_voyage, "Bagages en voyage", '4.2.2.1',
    "La Compagnie garantit à l’Assuré la couverture de ses bagages emportés dans le cadre d’un voyage contre : n le vol,pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes ; n la perte, n les dégâts dus à toute circonstance fortuite survenue pendant le voyage").
perimetre(bagages_voyage, concept(bagage)).
perimetre(bagages_voyage, f(sejour_temporaire, oui)).
circonstance(bagages_voyage, si(f(evenement, vol), f(plainte_deposee, oui)), '4.2.2.1',
    "pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes").
circonstance(bagages_voyage, si(f(lieu, vehicule), et([f(bagage_enregistre, non), f(periode_horaire, jour_7h_22h), ou([f(vehicule_vole, oui), f(effraction, oui)])])), '4.2.2.3',
    "Lorsque les bagages sont non enregistrés et se trouvent à l’intérieur d’un véhicule, d’une caravane, d’une remorque ou d’un bateau, le vol est couvert entre sept heures et vingt-deux heures et à condition qu’il soit accompagné : n du vol simultané du véhicule, de la caravane, de la remorque ou du bateau ; n de l’effraction caractérisée du véhicule, du coffre ou de la cabine du bateau").
exclusion(bagages_voyage, f(proprietaire, hote), tout, oui, '4.2.2.4',
    "les bagages dont l’Assuré n’est pas propriétaire").
exclusion(bagages_voyage, f(laisse_sans_surveillance, oui), tout, oui, '4.2.2.4',
    "les bagages laissés sans surveillance dans un lieu public").
exclusion(bagages_voyage, f(simple_disparition, oui), tout, oui, '4.2.2.4',
    "les bagages oubliés").
exclusion(bagages_voyage, f(saisie_autorites, oui), tout, oui, '4.2.2.4',
    "les pertes et dégâts causés à l’occasion d’une saisie par les autorités publiques (police, douane, …)").
exclusion(bagages_voyage, f(manque_entretien, oui), tout, oui, '4.2.2.4',
    "de l’usure, de la détérioration lente, de la vétusté ou d’un défaut d’entretien").
exclusion(bagages_voyage, f(cause_eau, infiltration_exterieure), tout, oui, '4.2.2.4',
    "de l’humidité, des mites, des vers ou des parasites").
exclusion(bagages_voyage, f(alea_tempete, grele), tout, oui, '4.2.2.4',
    "de la pluie, de la grêle et de toute autre manifestation atmosphérique").
exclusion(bagages_voyage, f(fonctionnement_defectueux, oui), tout, oui, '4.2.2.4',
    "les frais exposés pour réparer des défauts de fonctionnement, sauf si ces défauts sont la conséquence d’une perte ou d’un dommage indemnisable causé aux bagages").
exclusion(bagages_voyage, f(perte_indirecte, oui), tout, oui, '4.2.2.4',
    "les pertes indirectes de quelque nature que ce soit").
exclusion(bagages_voyage, f(dommage_esthetique, oui), tout, oui, '4.2.2.4',
    "les dommages d’ordre purement esthétique").
exclusion(bagages_voyage, et([f(type_dommage, bris), non(ou([f(evenement, incendie), f(evenement, vol), f(evenement, accident)]))]), tout, oui, '4.2.2.4',
    "la casse d’objets fragiles tels pendules, porcelaines, glaces, instruments de musique, à moins que celle-ci ne résulte d’un incendie, d’un vol ou d’un accident de la circulation impliquant le moyen de transport").
exclusion(bagages_voyage, f(auteur, assure), tout, oui, '4.2.2.4.10',
    "les vols commis par ou avec la complicité de ou du : Preneur d’assurance, son conjoint, leurs ascendants ou descendants ainsi que les conjoints de ces personnes ; l’Assuré").
exclusion(bagages_voyage, non(f(option_bagages, oui)), tout, oui, '4.2.2.1',
    "La Compagnie garantit à l’Assuré la couverture de ses bagages emportés dans le cadre d’un voyage contre : n le vol,pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes ; n la perte, n les dégâts dus à toute circonstance fortuite survenue pendant le voyage").
limite(bagages_voyage, '4.2.2.1', "La Compagnie garantit le remboursement sans application de règle proportionnelle à concurrence de 5.000 € par sinistre.", "5000").
