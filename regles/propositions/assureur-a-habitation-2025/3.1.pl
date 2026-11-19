% --- Art. 3.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
extension(batiment, et([f(sejour_temporaire, oui), f(lieu, autre_batiment), concept(contenu)]), '3.1',
    "Le déplacement de votre contenu à l'occasion d'un séjour temporaire dans un bâtiment à concurrence de 5.000 EUR (à l’exception d’une caravane tractable ou d’un mobilhome pour lesquels la limite d’indemnisation est fixée à 500 EUR)").
extension(batiment, et([f(demenagement, oui), f(lieu, vehicule), f(detenteur_vehicule, oui), concept(contenu)]), '3.1',
    "Le contenu est également couvert lors de son transport dans un véhicule dont vous êtes le détenteur à concurrence de 5.000 EUR.").
garantie(extension_residence_remplacement, "Extension - Résidence de remplacement (RC locative)", '3.1',
    "La résidence de remplacement (meublée ou non) : si votre résidence principale est temporairement inhabitable à la suite d'un sinistre, nous couvrons pendant 18 mois votre responsabilité locative pour les dégâts causés à cette résidence de remplacement").
perimetre(extension_residence_remplacement, f(residence_principale, oui)).
perimetre(extension_residence_remplacement, f(residence_principale_inhabitable, oui)).
perimetre(extension_residence_remplacement, f(lieu, autre_batiment)).
exclusion(extension_residence_remplacement, non(f(couverture_rc_locative, oui)), tout, oui, '3.1',
    "Si nous couvrons votre résidence principale, et en fonction des couvertures (RC locative et/ou contenu) mentionnées dans vos conditions particulières").
limite(extension_residence_remplacement, '3.1', "jusqu'à concurrence de 1.000.000 EUR", "1000000 EUR").
limite(extension_residence_remplacement, '3.1', "pendant 18 mois", "18 mois").
garantie(extension_residence_villegiature, "Extension - Résidence de villégiature (RC contractuelle)", '3.1',
    "La résidence de villégiature (meublée ou non), à l'occasion d'un séjour temporaire nous couvrons votre responsabilité contractuelle pour les dégâts causés à cette résidence de villégiature, l'hôtel ou un logement similaire").
perimetre(extension_residence_villegiature, f(sejour_temporaire, oui)).
perimetre(extension_residence_villegiature, f(lieu, autre_batiment)).
exclusion(extension_residence_villegiature, non(f(couverture_rc_locative, oui)), tout, oui, '3.1',
    "Si nous couvrons votre résidence principale, et en fonction des couvertures (RC locative et/ou contenu) mentionnées dans vos conditions particulières").
limite(extension_residence_villegiature, '3.1', "jusqu'à concurrence de 1.000.000 EUR", "1000000 EUR").
garantie(extension_local_fete_familiale, "Extension - Local de fête de famille (RC locative)", '3.1',
    "Le local que vous occupez à l’occasion d’une fête de famille, c’est-à-dire une festivité privée à caractère familial. Nous couvrons votre responsabilité locative pour les dégâts que vous causez à ce local. Les tentes, chapiteaux et péniches à quai sont assimilés aux locaux de fête").
perimetre(extension_local_fete_familiale, f(occasion_fete_familiale, oui)).
perimetre(extension_local_fete_familiale, f(lieu, autre_batiment)).
exclusion(extension_local_fete_familiale, non(f(couverture_rc_locative, oui)), tout, oui, '3.1',
    "Si nous couvrons votre résidence principale, et en fonction des couvertures (RC locative et/ou contenu) mentionnées dans vos conditions particulières").
limite(extension_local_fete_familiale, '3.1', "jusqu'à concurrence de 1.000.000 EUR", "1000000 EUR").
garantie(extension_abandon_recours_famille, "Extension - Abandon de recours envers les parents ou alliés en ligne directe", '3.1',
    "L’abandon de recours : nous abandonnons tout recours envers les parents ou alliés en ligne directe auxquels vous prêtez ou louez votre habitation sauf en cas de malveillance ou dans la mesure où ces personnes disposent d’une assurance garantissant leur responsabilité").
perimetre(extension_abandon_recours_famille, f(auteur, famille)).
perimetre(extension_abandon_recours_famille, f(pret_ou_location_habitation, oui)).
exclusion(extension_abandon_recours_famille, f(malveillance_auteur, oui), tout, oui, '3.1',
    "sauf en cas de malveillance").
exclusion(extension_abandon_recours_famille, f(assurance_responsabilite_tiers, oui), tout, oui, '3.1',
    "ou dans la mesure où ces personnes disposent d’une assurance garantissant leur responsabilité").
exclusion(extension_abandon_recours_famille, non(f(couverture_rc_locative, oui)), tout, oui, '3.1',
    "Si nous couvrons votre résidence principale, et en fonction des couvertures (RC locative et/ou contenu) mentionnées dans vos conditions particulières").
accessoire(extension_residence_remplacement).
accessoire(extension_residence_villegiature).
accessoire(extension_local_fete_familiale).
accessoire(extension_abandon_recours_famille).
