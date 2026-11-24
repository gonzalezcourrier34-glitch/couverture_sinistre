% --- Art. 4.2.1 : proposition rédigée par le modèle — mistral:mistral-large-4-0, 2026-11-24 ---
evenement_traduit(annulation_voyage).
definition(maladie_grave, f(maladie_grave, oui), '4.2.1.2',
    "Par maladie grave, on entend : une altération de la santé constatée par une autorité médicale notoirement compétente interdisant de quitter la chambre (sortie non autorisée) et impliquant la cessation de toute activité professionnelle ou autre.").
definition(accident_grave, f(accident_grave, oui), '4.2.1.2',
    "Par accident grave, on entend : une atteinte corporelle non intentionnelle de la part de la victime provenant de l'action soudaine d'une cause extérieure et lui interdisant tous déplacements par ses propres moyens.").
garantie(annulation_voyage, "Annulation de voyage", '4.2.1',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ annulation” est souscrite.").
perimetre(annulation_voyage, f(evenement, annulation_voyage)).
perimetre(annulation_voyage, f(option_annulation, oui)).
circonstance(annulation_voyage, et([ou([f(motif_annulation, maladie_grave_assure_famille), f(motif_annulation, deces_assure_famille), f(motif_annulation, retard_transport_public), f(motif_annulation, greve_sauvage_transport), f(motif_annulation, accident_circulation_trajet), f(motif_annulation, force_majeure_trajet), f(motif_annulation, licenciement_economique), f(motif_annulation, convocation_greffe), f(motif_annulation, convocation_adoption), f(motif_annulation, vaccination_impossible), f(motif_annulation, vol_papiers_48h), f(motif_annulation, divorce), f(motif_annulation, separation), f(motif_annulation, hote_indisponible), f(motif_annulation, degats_materiels_residence), f(motif_annulation, complications_grossesse), f(motif_annulation, grossesse_3_mois)]), f(maladie_accident_apres_inscription, oui)]), '4.2.1.2',
    "La garantie est d’application : 4.2.1.2.1 dans le cas d’une maladie grave, d’un accident corporel grave ou du décès... 4.2.1.2.14 en cas de grossesse de l’Assurée pour autant que le voyage était prévu pendant les 3 derniers mois de la grossesse et que cette dernière n’était pas connue au moment de la réservation du voyage ou de la location. La Compagnie garantit l’Assuré seulement contre les conséquences des maladies et accidents survenus après la date de l’inscription au voyage.").
obligation(annulation_voyage, f(declaration_ecrite_5j, oui), faux, non, '4.2.1.5',
    "La déclaration d’annulation doit être signifiée par écrit à la Compagnie dans les 5 jours suivant la communication de l’annulation, et sera accompagnée des pièces justificatives.").
obligation(annulation_voyage, f(transmission_infos_30j, oui), faux, non, '4.2.1.5',
    "L’Assuré doit transmettre sans délai à la Compagnie, et dans tous les cas dans les 30 jours, toutes les informations utiles.").
exclusion(annulation_voyage, f(voyage_professionnel, oui), tout, oui, '4.2.1.4',
    "les voyages à caractère professionnel").
exclusion(annulation_voyage, f(voyage_reserve_avant_souscription, oui), tout, oui, '4.2.1.4',
    "les voyages réservés par l’Assuré avant la date de souscription de la garantie et dont la date de départ est prévue moins d’un mois après sa date de prise d’effet").
exclusion(annulation_voyage, f(abus_substances, oui), tout, oui, '4.2.1.4',
    "l’usage abusif de l’alcool (ivresse, alcoolisme), de médicaments, de drogues ou de stupéfiants").
exclusion(annulation_voyage, f(maladie_mentale_sans_hospitalisation, oui), tout, oui, '4.2.1.4',
    "les maladies psychotiques, mentales ou nerveuses qui n’entraînent pas d’hospitalisation de plus de 7 jours").
exclusion(annulation_voyage, f(intentionnel, oui), tout, non, '4.2.1.4',
    "les actes intentionnels").
exclusion(annulation_voyage, f(participation_rixe, oui), tout, non, '4.2.1.4',
    "les accidents et troubles résultant de participation à des paris, crimes, rixes (sauf cas de légitime défense)").
exclusion(annulation_voyage, f(sport_professionnel, oui), tout, oui, '4.2.1.4',
    "les accidents et troubles résultant de participation, à titre professionnel ou sous contrat avec rémunération, à tout sport ou compétition ainsi qu’aux entrainements préparatoires").
exclusion(annulation_voyage, f(sport_dangereux, oui), tout, oui, '4.2.1.4',
    "les accidents résultant de la pratique en tant qu’amateur et n’importe quel niveau, des sports suivants : sports mécaniques (auto, moto, tout véhicule motorisé), sports aériens, alpinisme, sports de glisse donnant lieu à un classement international, national ou régional, skeleton, sports de combat, spéléologie").
exclusion(annulation_voyage, f(cause_epidemie_pollution_catnat, oui), tout, oui, '4.2.1.4',
    "les épidémies, la pollution du milieu naturel et les catastrophes naturelles").
exclusion(annulation_voyage, f(cause_greve_guerre_terrorisme, oui), tout, oui, '4.2.1.4',
    "les grèves, les guerres et les guerres civiles, les émeutes, les mouvements populaires, les actes de terrorisme").
exclusion(annulation_voyage, f(cause_nucleaire, oui), tout, non, '4.2.1.4',
    "tout effet de rayonnement radioactif ainsi que l’inobservation consciente d’interdictions officielles").
exclusion(annulation_voyage, f(interruption_volontaire_grossesse, oui), tout, oui, '4.2.1.4',
    "les annulations et modifications consécutives à une interruption volontaire de grossesse").
limite(annulation_voyage, '4.2.1.1', "La prise en charge totale de ces frais se fait à concurrence de 15.000 E maximum par sinistre et par année d’assurance.", "15000 EUR").
