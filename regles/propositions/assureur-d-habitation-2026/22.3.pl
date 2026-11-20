% --- Art. 22.3 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(litige).
exclusion([recours_accident, defense_penale, protection_juridique], f(domaine_litige, activite_professionnelle), tout, non, '22.3-a~1',
    "d’une activité professionnelle non salariée ou de l’administration d’une entreprise, d’une collectivité ou d’une association lorsque cette dernière emploie un ou des salariés,").
exclusion([recours_accident, defense_penale, protection_juridique], f(domaine_litige, vehicule_moteur), tout, non, '22.3-a~2',
    "de l’achat, la vente, la propriété, la location (sauf pour la location de courte durée n’excédant pas deux mois), l’entretien, la réparation, la conduite ou l’assurance d’un véhicule terrestre à moteur (sauf les engins de jardinage et les jouets télécommandés),").
exclusion([recours_accident, defense_penale, protection_juridique], f(domaine_litige, divorce_succession), tout, non, '22.3-a~2',
    "de l’application du Livre I du Code civil, excepté les litiges découlant des incapacités (sauvegarde de justice, tutelle, curatelle) et de la filiation (légitime, naturelle, adoptive),").
exclusion([recours_accident, defense_penale, protection_juridique], f(domaine_litige, divorce_succession), tout, non, '22.3-a~2',
    "des régimes matrimoniaux, des successions (excepté les litiges découlant des successions en ligne directe), des donations entre vifs et legs (excepté les litiges découlant des donations entre vifs et legs en ligne directe),").
