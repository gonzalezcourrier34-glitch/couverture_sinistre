% --- Art. 2.13 : proposition rédigée par le modèle — mistral:mistral-large-4-0 (proposition écartée), 2026-11-24 ---
evenement_traduit(assistance).
garantie(assistance_apres_sinistre, "Assistance après un sinistre couvert", '2.13~1',
    "vous trouverez ci-dessous, de manière exhaustive, les prestations comprises dans votre contrat d’assurance et qui sont mises en place après un sinistre couvert").
limite(assistance_apres_sinistre, '2.13~3', "de l’organisation et de la prise en charge d’un véhicule de remplacement (voiture de tourisme de la catégorie B au maximum) durant 7 jours au maximum à partir de la date du sinistre couvert", "7 jours max").
limite(assistance_apres_sinistre, '2.13~4', "Assureur A Assistance organise cette surveillance et en assume les frais pendant 72 heures au maximum", "72 heures max").
limite(assistance_apres_sinistre, '2.13~4', "de la mise à disposition pendant 16 heures maximum d’un agent de nettoyage pour le nettoyage des locaux endommagés à concurrence de 40 EUR/heure", "16 heures, 40 EUR/heure").
limite(assistance_apres_sinistre, '2.13~4', "Assureur A Assistance indemnise à concurrence de 120 EUR par jour (toutes taxes et frais compris) au cours de 7 jours au maximum", "120 EUR/jour, 7 jours max").
garantie(depannage_serrurier, "Dépannage serrurier", '2.13~6',
    "Si l’assuré ne peut plus pénétrer dans le bâtiment assuré à la suite de la perte des clés, de l’oubli des clés à l’intérieur, ou du vol des clés ou parce que la serrure du bâtiment ou de l’appartement (lorsque l’assuré n’occupe qu’une partie du bâtiment) a été endommagée, Assureur A Assistance organisera et paiera les frais d’ouverture de la porte et, le cas échéant, le remplacement de la serrure par un serrurier").
perimetre(depannage_serrurier, f(evenement, assistance)).
perimetre(depannage_serrurier, f(objet_assistance, ouverture)).
exclusion(depannage_serrurier, et([f(intervention_mandatee, non), non(f(contact_assistance_impossible, oui))]), tout, oui, '2.13-a',
    "Les prestations qui ne peuvent être demandées au moment du sinistre et qui ne sont pas exécutées en accord avec Assureur A Assistance ne sont pas garanties. Néanmoins, lorsque l’assuré n’a matériellement pas été en mesure de prendre contact avec la centrale de Assureur A Assistance, la couverture continuera à s’appliquer").
limite(depannage_serrurier, '2.13~6', "Assureur A Assistance prend ces frais en charge à concurrence de 300 EUR au maximum par sinistre et par année assurée", "300").
accessoire(assistance_apres_sinistre).
