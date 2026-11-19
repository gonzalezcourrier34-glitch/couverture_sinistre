% --- Art. 3.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-18 ---
evenement_traduit(vol).
evenement_traduit(incendie).
evenement_traduit(degat_eaux).
evenement_traduit(tempete).
evenement_traduit(bris).
evenement_traduit(autre).
evenement_traduit(electricite).
evenement_traduit(mazout).
evenement_traduit(catastrophe_naturelle).
evenement_traduit(attentat).
evenement_traduit(fumee).
evenement_traduit(vandalisme).
evenement_traduit(merule).
evenement_traduit(explosion).
evenement_traduit(foudre).
garantie(sejour_temporaire_contenu, "Contenu en séjour temporaire", '3.1',
    "Le déplacement de votre contenu à l'occasion d'un séjour temporaire dans un bâtiment à concurrence de 5.000 EUR (à l'exception d'une caravane tractable ou d'un mobilhome pour lesquels la limite d'indemnisation est fixée à 500 EUR)").
perimetre(sejour_temporaire_contenu, concept(contenu)).
perimetre(sejour_temporaire_contenu, f(sejour_temporaire, oui)).
perimetre(sejour_temporaire_contenu, f(lieu, autre_batiment)).
exclusion(sejour_temporaire_contenu, f(type_logement_temporaire, caravane_mobilhome), tout, oui, '3.1',
    "à l'exception d'une caravane tractable ou d'un mobilhome pour lesquels la limite d'indemnisation est fixée à 500 EUR").
limite(sejour_temporaire_contenu, '3.1', "à concurrence de 5.000 EUR", "5000 EUR").
limite(sejour_temporaire_contenu, '3.1', "la limite d'indemnisation est fixée à 500 EUR", "500 EUR").
garantie(demenagement_transport, "Déménagement et transport", '3.1',
    "Votre nouvelle adresse en Belgique à partir du début de votre déménagement. Après 30 jours, l'assurance n'est acquise qu'à la nouvelle situation du risque. Le contenu est également couvert lors de son transport dans un véhicule dont vous êtes le détenteur à concurrence de 5.000 EUR.").
perimetre(demenagement_transport, concept(contenu)).
perimetre(demenagement_transport, ou([f(lieu, logement), f(lieu, vehicule_moteur)])).
circonstance(demenagement_transport, f(demenagement_en_cours, oui), '3.1',
    "à partir du début de votre déménagement").
limite(demenagement_transport, '3.1', "à concurrence de 5.000 EUR", "5000 EUR").
garantie(residence_remplacement, "Résidence de remplacement", '3.1',
    "La résidence de remplacement (meublée ou non) : si votre résidence principale est temporairement inhabitable à la suite d'un sinistre, nous couvrons pendant 18 mois votre responsabilité locative pour les dégâts causés à cette résidence de remplacement").
perimetre(residence_remplacement, f(lieu, autre_batiment)).
perimetre(residence_remplacement, f(auteur, assure)).
circonstance(residence_remplacement, f(residence_principale_inhabitable, oui), '3.1',
    "si votre résidence principale est temporairement inhabitable à la suite d'un sinistre").
circonstance(residence_remplacement, f(couverture_rc_locative, oui), '3.1',
    "Si nous couvrons votre résidence principale, et en fonction des couvertures (RC locative et/ou contenu) mentionnées dans vos conditions particulières").
limite(residence_remplacement, '3.1', "jusqu'à concurrence de 1.000.000 EUR", "1000000 EUR").
limite(residence_remplacement, '3.1', "pendant 18 mois", "18 mois").
garantie(villegiature, "Résidence de villégiature", '3.1',
    "La résidence de villégiature (meublée ou non), à l'occasion d'un séjour temporaire nous couvrons votre responsabilité contractuelle pour les dégâts causés à cette résidence de villégiature, l'hôtel ou un logement similaire").
perimetre(villegiature, f(lieu, autre_batiment)).
perimetre(villegiature, f(sejour_temporaire, oui)).
perimetre(villegiature, f(auteur, assure)).
circonstance(villegiature, f(couverture_rc_locative, oui), '3.1',
    "Si nous couvrons votre résidence principale, et en fonction des couvertures (RC locative et/ou contenu) mentionnées dans vos conditions particulières").
limite(villegiature, '3.1', "jusqu'à concurrence de 1.000.000 EUR", "1000000 EUR").
garantie(fete_famille, "Local de fête de famille", '3.1',
    "Le local que vous occupez à l'occasion d'une fête de famille, c'est-à-dire une festivité privée à caractère familial. Nous couvrons votre responsabilité locative pour les dégâts que vous causez à ce local. Les tentes, chapiteaux et péniches à quai sont assimilés aux locaux de fête").
perimetre(fete_famille, f(lieu, autre_batiment)).
perimetre(fete_famille, f(auteur, assure)).
circonstance(fete_famille, f(fete_famille, oui), '3.1',
    "à l'occasion d'une fête de famille, c'est-à-dire une festivité privée à caractère familial").
circonstance(fete_famille, f(couverture_rc_locative, oui), '3.1',
    "Si nous couvrons votre résidence principale, et en fonction des couvertures (RC locative et/ou contenu) mentionnées dans vos conditions particulières").
limite(fete_famille, '3.1', "jusqu'à concurrence de 1.000.000 EUR", "1000000 EUR").
garantie(abandon_recours, "Abandon de recours", '3.1',
    "L'abandon de recours : nous abandonnons tout recours envers les parents ou alliés en ligne directe auxquels vous prêtez ou louez votre habitation sauf en cas de malveillance ou dans la mesure où ces personnes disposent d'une assurance garantissant leur responsabilité").
perimetre(abandon_recours, f(auteur, famille)).
circonstance(abandon_recours, f(couverture_rc_locative, oui), '3.1',
    "Si nous couvrons votre résidence principale, et en fonction des couvertures (RC locative et/ou contenu) mentionnées dans vos conditions particulières").
exclusion(abandon_recours, f(malveillance, oui), tout, oui, '3.1',
    "sauf en cas de malveillance").
exclusion(abandon_recours, f(assurance_rc_tiers, oui), tout, oui, '3.1',
    "ou dans la mesure où ces personnes disposent d'une assurance garantissant leur responsabilité").
