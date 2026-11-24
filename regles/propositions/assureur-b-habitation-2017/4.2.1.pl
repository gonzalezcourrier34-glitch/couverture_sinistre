% --- Art. 4.2.1 : proposition rédigée par le modèle — mistral:mistral-large-4-0 (proposition écartée), 2026-11-24 ---
evenement_traduit(voyage).
garantie(annulation_voyage, "Annulation ou interruption de voyage (option)", '4.2.1.1',
    "La Compagnie garantit le remboursement : n des frais d’annulation contractuellement dus lorsque le voyage est annulé avant le départ ou lorsque la location est annulée avant l’entrée en jouissance des locaux").
perimetre(annulation_voyage, f(evenement, voyage)).
perimetre(annulation_voyage, ou([f(objet_voyage, annulation), f(objet_voyage, interruption)])).
circonstance(annulation_voyage, f(option_annulation, oui), '4.2.1',
    "la garantie “ annulation” est souscrite").
circonstance(annulation_voyage, ou([f(motif_annulation, sante_ou_deces_proche), f(motif_annulation, transport_greve_sauvage), f(motif_annulation, accident_trajet_depart), f(motif_annulation, licenciement_economique), f(motif_annulation, greffe_ou_adoption), f(motif_annulation, vaccination_impossible), f(motif_annulation, vol_papiers_48h), f(motif_annulation, divorce_ou_separation), f(motif_annulation, hote_empeche), f(motif_annulation, degats_domicile), f(motif_annulation, grossesse)]), '4.2.1.2',
    "La garantie est d’application : 4.2.1.2.1 dans le cas d’une maladie grave, d’un accident corporel grave ou du décès").
exclusion(annulation_voyage, f(voyage_professionnel, oui), tout, non, '4.2.1.4',
    "les voyages à caractère professionnel").
exclusion(annulation_voyage, f(reservation_avant_souscription, oui), tout, non, '4.2.1.4',
    "les voyages réservés par l’Assuré avant la date de souscription de la garantie et dont la date de départ est prévue moins d’un mois après sa date de prise d’effet").
exclusion(annulation_voyage, f(motif_anterieur_inscription, oui), tout, non, '4.2.1.2',
    "La Compagnie garantit l’Assuré seulement contre les conséquences des maladies et accidents survenus après la date de l’inscription au voyage").
exclusion(annulation_voyage, et([f(motif_annulation, accident_trajet_depart), f(immobilisation_moins_1h, oui)]), tout, non, '4.2.1.2',
    "les embarras de circulation ainsi que tout événement à l’origine de l’immobilisation survenus moins d’une heure avant l’heure d’embarquement prévue ne sont pas pris en compte par cette garantie").
exclusion(annulation_voyage, f(cause_annulation_exclue, alcool_drogue), tout, non, '4.2.1.4',
    "l’usage abusif de l’alcool (ivresse, alcoolisme), de médicaments, de drogues ou de stupéfiants").
exclusion(annulation_voyage, f(cause_annulation_exclue, trouble_psychique_sans_hospitalisation), tout, non, '4.2.1.4',
    "les maladies psychotiques, mentales ou nerveuses qui n’entraînent pas d’hospitalisation de plus de 7 jours").
exclusion(annulation_voyage, f(cause_annulation_exclue, acte_intentionnel), tout, non, '4.2.1.4',
    "les actes intentionnels").
exclusion(annulation_voyage, f(cause_annulation_exclue, pari_crime_rixe), tout, non, '4.2.1.4',
    "les accidents et troubles résultant de participation à des paris, crimes, rixes (sauf cas de légitime défense)").
exclusion(annulation_voyage, f(cause_annulation_exclue, sport_professionnel), tout, non, '4.2.1.4',
    "les accidents et troubles résultant de participation, à titre professionnel ou sous contrat avec rémunération, à tout sport ou compétition ainsi qu’aux entrainements préparatoires").
exclusion(annulation_voyage, f(cause_annulation_exclue, sport_a_risque), tout, non, '4.2.1.4',
    "les accidents résultant de la pratique en tant qu’amateur et n’importe quel niveau, des sports suivants : sports mécaniques (auto, moto, tout véhicule motorisé), sports aériens, alpinisme").
exclusion(annulation_voyage, f(cause_annulation_exclue, epidemie_pollution_catastrophe), tout, non, '4.2.1.4',
    "les épidémies, la pollution du milieu naturel et les catastrophes naturelles").
exclusion(annulation_voyage, f(cause_annulation_exclue, greve_guerre_terrorisme), tout, non, '4.2.1.4',
    "les grèves, les guerres et les guerres civiles, les émeutes, les mouvements populaires, les actes de terrorisme").
exclusion(annulation_voyage, f(cause_annulation_exclue, radioactivite_ou_interdiction), tout, non, '4.2.1.4',
    "tout effet de rayonnement radioactif ainsi que l’inobservation consciente d’interdictions officielles").
exclusion(annulation_voyage, f(cause_annulation_exclue, ivg), tout, non, '4.2.1.4',
    "les annulations et modifications consécutives à une interruption volontaire de grossesse").
limite(annulation_voyage, '4.2.1.1', "La prise en charge totale de ces frais se fait à concurrence de 15.000 E maximum par sinistre et par année d’assurance", "15000").
