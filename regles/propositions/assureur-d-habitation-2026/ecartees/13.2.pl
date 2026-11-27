% --- Art. 13.2 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(accident).
evenement_traduit(incendie).
evenement_traduit(explosion).
evenement_traduit(degat_eaux).
evenement_traduit(vol).
garantie(rc_fetes_familiales, "Responsabilité civile fêtes familiales", '13.2-a',
    "La garantie couvre les conséquences financières de la responsabilité civile que vous pouvez encourir à l’égard des tiers lorsque vous louez ou occupez un local en tant qu’organisateur à titre privé et sans but lucratif de manifestations familiales ou privées (fêtes, réceptions, mariage, communions…) d’un maximum de 150 personnes à la suite d’un accident, d’un incendie, d’une explosion ou d’un dégât des eaux causant des dommages corporels, matériels et immatériels à des tiers").
perimetre(rc_fetes_familiales, f(occasion_fete_familiale, oui)).
perimetre(rc_fetes_familiales, f(pays, france)).
perimetre(rc_fetes_familiales, ou([f(evenement, accident), f(evenement, incendie), f(evenement, explosion), f(evenement, degat_eaux)])).
circonstance(rc_fetes_familiales, f(nombre_personnes_manifestation, moins_150), '13.2-a',
    "d’un maximum de 150 personnes").
circonstance(rc_fetes_familiales, ou([f(defaut_organisation, oui), f(manque_precautions_amenagement, oui)]), '13.2-a',
    "provenant d’un défaut d’organisation ou d’un manque de précautions dans l’aménagement des lieux où doit se dérouler la manifestation").
circonstance(rc_fetes_familiales, f(auteur, assure), '13.2-a',
    "de votre fait ou du fait de toute personne dont vous devez répondre, salariée ou non, participant à l’organisation de cette manifestation").
circonstance(rc_fetes_familiales, f(cause_agencements, oui), '13.2-a',
    "du fait des agencements mobiliers ou immobiliers, aménagements ou installations nécessaires, y compris au cours des travaux de montage ou de démontage").
circonstance(rc_fetes_familiales, et([ou([f(evenement, incendie), f(evenement, explosion), f(evenement, degat_eaux)]), f(lieu_origine_sinistre, batiment_manifestation)]), '13.2-a',
    "causés par un incendie, une explosion, un dégât des eaux ayant pris naissance dans le bâtiment où se déroule la manifestation et dont vous êtes occupant ou locataire").
circonstance(rc_fetes_familiales, f(biens_confies_manifestation, oui), '13.2-a',
    "causés aux biens mobiliers qui vous sont confiés à l’occasion de la manifestation et pendant la durée de celle-ci").
circonstance(rc_fetes_familiales, f(intoxication_alimentaire, oui), '13.2-a',
    "dus à des intoxications causées par l’absorption de produits alimentaires offerts lors de la manifestation").
exclusion(rc_fetes_familiales, f(bien, vetements_objet_personnel), tout, oui, '13.2-b',
    "le vol ou la disparition des vêtements et objets personnels des participants").
exclusion(rc_fetes_familiales, f(bien, valeurs), tout, oui, '13.2-b',
    "des objets précieux, billets de banque, espèces et titres").
exclusion(rc_fetes_familiales, f(batiment_classe_monuments_historiques, oui), tout, oui, '13.2-b',
    "les manifestations ayant lieu dans un château ou dans un bâtiment faisant l’objet d’un classement ou d’une inscription auprès des monuments historiques").
exclusion(rc_fetes_familiales, ou([f(auteur, assure), f(auteur, famille)]), tout, oui, '13.2-b',
    "les dommages subis par toute personne ayant la qualité d’assuré, ses préposés et salariés dans l’exercice de leur fonction").
exclusion(rc_fetes_familiales, f(auteur, responsable_sinistre), tout, oui, '13.2-b',
    "les dommages subis par les personnes responsables du sinistre").
exclusion(rc_fetes_familiales, f(usage_professionnel, oui), tout, oui, '13.2-b',
    "les dommages résultant de l’exercice de votre profession, ou de toute fonction publique ou politique").
exclusion(rc_fetes_familiales, f(batiment_non_construit_dur, oui), tout, oui, '13.2-b',
    "les dommages causés aux bâtiments et locaux non construits et/ou non couverts en dur (tentes, chapiteaux, structures gonflables)").
limite(rc_fetes_familiales, '13.2-a', "La garantie prend effet au moment de la remise des clés du local et prend fin à la restitution des clés et ce pour une durée maximum de trois jours", "3 jours").
garantie(rc_chambres_hotes, "Responsabilité civile loueur de chambres d'hôtes", '13.2-c',
    "La garantie couvre les conséquences financières de la responsabilité civile que vous pouvez encourir du fait de l’exploitation de chambre(s) d’hôtes dans le local d’habitation assuré en raison : • de dommages corporels, matériels et immatériels consécutifs causés aux locataires de la chambre d’hôtes, y compris en cas d’intoxications alimentaires, • du vol avec effraction ou escalade du local d’habitation assuré des biens des locataires déposés dans la chambre").
perimetre(rc_chambres_hotes, f(lieu, logement)).
perimetre(rc_chambres_hotes, ou([f(evenement, accident), f(evenement, vol)])).
circonstance(rc_chambres_hotes, f(intoxication_alimentaire, oui), '13.2-c',
    "y compris en cas d’intoxications alimentaires").
circonstance(rc_chambres_hotes, si(f(evenement, vol), ou([f(effraction, oui), f(acces_voleur, escalade)])), '13.2-c',
    "du vol avec effraction ou escalade du local d’habitation assuré des biens des locataires déposés dans la chambre").
exclusion(rc_chambres_hotes, f(bien, vehicule_moteur), tout, oui, '13.2-d',
    "le vol ou la tentative de vol du véhicule des locataires").
exclusion(rc_chambres_hotes, f(bien, valeurs), tout, oui, '13.2-d',
    "le vol des espèces, titres et valeurs").
exclusion(rc_chambres_hotes, f(bien, animal), tout, oui, '13.2-d',
    "des animaux des locataires").
exclusion(rc_chambres_hotes, f(type_location, gite), tout, oui, '13.2-d',
    "la location de gîtes").
exclusion(rc_chambres_hotes, non(f(option_chambres_hotes, oui)), tout, oui, '13.2-c',
    "La garantie couvre les conséquences financières de la responsabilité civile que vous pouvez encourir du fait de l’exploitation de chambre(s) d’hôtes dans le local d’habitation assuré en raison : • de dommages corporels, matériels et immatériels consécutifs causés aux locataires de la chambre d’hôtes, y compris en cas d’intoxications alimentaires, • du vol avec effraction ou escalade du local d’habitation assuré des biens des locataires déposés dans la chambre").
limite(rc_chambres_hotes, '13.2-c', "Notre garantie est limitée à 1 chambre d’hôtes si votre habitation est un appartement et 3 chambres d’hôtes s’il s’agit d’une maison", "1 chambre (appartement) ou 3 chambres (maison)").
