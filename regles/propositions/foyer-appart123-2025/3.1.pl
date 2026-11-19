% --- Art. 3.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
garantie(extension_sejour_temporaire_contenu, "Extension - Contenu lors d'un séjour temporaire", '3.1',
    "Le déplacement de votre contenu à l'occasion d'un séjour temporaire dans un bâtiment à concurrence de 5.000 EUR (à l’exception d’une caravane tractable ou d’un mobilhome pour lesquels la limite d’indemnisation est fixée à 500 EUR)").
perimetre(extension_sejour_temporaire_contenu, f(sejour_temporaire, oui)).
perimetre(extension_sejour_temporaire_contenu, concept(contenu)).
perimetre(extension_sejour_temporaire_contenu, f(lieu, autre_batiment)).
circonstance(extension_sejour_temporaire_contenu, f(couverture_contenu, oui), '3.1',
    "En fonction des couvertures (RC locative et/ou contenu) mentionnées dans vos conditions particulières").
limite(extension_sejour_temporaire_contenu, '3.1', "à concurrence de 5.000 EUR", "5000 EUR").
limite(extension_sejour_temporaire_contenu, '3.1', "à l’exception d’une caravane tractable ou d’un mobilhome pour lesquels la limite d’indemnisation est fixée à 500 EUR", "500 EUR").
garantie(extension_demenagement_nouvelle_adresse, "Extension - Nouvelle adresse en Belgique lors d'un déménagement", '3.1',
    "Votre nouvelle adresse en Belgique à partir du début de votre déménagement. Après 30 jours, l'assurance n'est acquise qu'à la nouvelle situation du risque.").
perimetre(extension_demenagement_nouvelle_adresse, f(demenagement, oui)).
perimetre(extension_demenagement_nouvelle_adresse, f(lieu, logement)).
circonstance(extension_demenagement_nouvelle_adresse, f(couverture_contenu, oui), '3.1',
    "En fonction des couvertures (RC locative et/ou contenu) mentionnées dans vos conditions particulières").
circonstance(extension_demenagement_nouvelle_adresse, non(f(demenagement_depuis_plus_30j, oui)), '3.1',
    "Après 30 jours, l'assurance n'est acquise qu'à la nouvelle situation du risque").
garantie(extension_transport_contenu_vehicule_demenagement, "Extension - Transport du contenu dans un véhicule pendant le déménagement", '3.1',
    "Le contenu est également couvert lors de son transport dans un véhicule dont vous êtes le détenteur à concurrence de 5.000 EUR.").
perimetre(extension_transport_contenu_vehicule_demenagement, f(demenagement, oui)).
perimetre(extension_transport_contenu_vehicule_demenagement, concept(contenu)).
perimetre(extension_transport_contenu_vehicule_demenagement, f(lieu, vehicule)).
perimetre(extension_transport_contenu_vehicule_demenagement, f(detenteur_vehicule, oui)).
circonstance(extension_transport_contenu_vehicule_demenagement, f(couverture_contenu, oui), '3.1',
    "En fonction des couvertures (RC locative et/ou contenu) mentionnées dans vos conditions particulières").
limite(extension_transport_contenu_vehicule_demenagement, '3.1', "à concurrence de 5.000 EUR", "5000 EUR").
garantie(extension_residence_remplacement, "Extension - Résidence de remplacement (RC locative)", '3.1',
    "La résidence de remplacement (meublée ou non) : si votre résidence principale est temporairement inhabitable à la suite d'un sinistre, nous couvrons pendant 18 mois votre responsabilité locative pour les dégâts causés à cette résidence de remplacement").
perimetre(extension_residence_remplacement, f(residence_principale, oui)).
perimetre(extension_residence_remplacement, f(residence_principale_inhabitable, oui)).
perimetre(extension_residence_remplacement, f(lieu, autre_batiment)).
circonstance(extension_residence_remplacement, f(couverture_rc_locative, oui), '3.1',
    "Si nous couvrons votre résidence principale, et en fonction des couvertures (RC locative et/ou contenu) mentionnées dans vos conditions particulières").
limite(extension_residence_remplacement, '3.1', "jusqu'à concurrence de 1.000.000 EUR", "1000000 EUR").
limite(extension_residence_remplacement, '3.1', "pendant 18 mois", "18 mois").
garantie(extension_residence_villegiature, "Extension - Résidence de villégiature (RC contractuelle)", '3.1',
    "La résidence de villégiature (meublée ou non), à l'occasion d'un séjour temporaire nous couvrons votre responsabilité contractuelle pour les dégâts causés à cette résidence de villégiature, l'hôtel ou un logement similaire").
perimetre(extension_residence_villegiature, f(sejour_temporaire, oui)).
perimetre(extension_residence_villegiature, f(lieu, autre_batiment)).
circonstance(extension_residence_villegiature, f(couverture_rc_locative, oui), '3.1',
    "Si nous couvrons votre résidence principale, et en fonction des couvertures (RC locative et/ou contenu) mentionnées dans vos conditions particulières").
limite(extension_residence_villegiature, '3.1', "jusqu'à concurrence de 1.000.000 EUR", "1000000 EUR").
garantie(extension_local_fete_familiale, "Extension - Local de fête de famille (RC locative)", '3.1',
    "Le local que vous occupez à l’occasion d’une fête de famille, c’est-à-dire une festivité privée à caractère familial. Nous couvrons votre responsabilité locative pour les dégâts que vous causez à ce local. Les tentes, chapiteaux et péniches à quai sont assimilés aux locaux de fête").
perimetre(extension_local_fete_familiale, f(occasion_fete_familiale, oui)).
perimetre(extension_local_fete_familiale, f(lieu, autre_batiment)).
circonstance(extension_local_fete_familiale, f(couverture_rc_locative, oui), '3.1',
    "Si nous couvrons votre résidence principale, et en fonction des couvertures (RC locative et/ou contenu) mentionnées dans vos conditions particulières").
limite(extension_local_fete_familiale, '3.1', "jusqu'à concurrence de 1.000.000 EUR", "1000000 EUR").
garantie(extension_abandon_recours_famille, "Extension - Abandon de recours envers les parents ou alliés en ligne directe", '3.1',
    "L’abandon de recours : nous abandonnons tout recours envers les parents ou alliés en ligne directe auxquels vous prêtez ou louez votre habitation sauf en cas de malveillance ou dans la mesure où ces personnes disposent d’une assurance garantissant leur responsabilité").
perimetre(extension_abandon_recours_famille, f(auteur, famille)).
perimetre(extension_abandon_recours_famille, f(pret_ou_location_habitation, oui)).
circonstance(extension_abandon_recours_famille, f(couverture_rc_locative, oui), '3.1',
    "Si nous couvrons votre résidence principale, et en fonction des couvertures (RC locative et/ou contenu) mentionnées dans vos conditions particulières").
exclusion(extension_abandon_recours_famille, f(malveillance_auteur, oui), tout, oui, '3.1',
    "sauf en cas de malveillance").
exclusion(extension_abandon_recours_famille, f(assurance_responsabilite_tiers, oui), tout, oui, '3.1',
    "ou dans la mesure où ces personnes disposent d’une assurance garantissant leur responsabilité").
accessoire(extension_sejour_temporaire_contenu).
accessoire(extension_demenagement_nouvelle_adresse).
accessoire(extension_transport_contenu_vehicule_demenagement).
accessoire(extension_residence_remplacement).
accessoire(extension_residence_villegiature).
accessoire(extension_local_fete_familiale).
accessoire(extension_abandon_recours_famille).
