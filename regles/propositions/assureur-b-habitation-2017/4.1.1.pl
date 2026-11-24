% --- Art. 4.1.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(responsabilite).
garantie(rc_vie_privee, "Responsabilité civile vie privée (option)", '4.1.1.5',
    "La garantie s’applique aux conséquences pécuniaires de la responsabilité civile pouvant incomber à l’Assuré en vertu des articles 1382 à 1386 du Code civil, en raison des dommages corporels, des dommages matériels et des dommages immatériels, causés accidentellement à des tiers au cours de sa vie familiale et privée").
perimetre(rc_vie_privee, f(evenement, responsabilite)).
circonstance(rc_vie_privee, f(option_rc_vie_privee, oui), '4.1.1',
    "la garantie “ responsabilité civile vie privée ” est accordée").
exclusion(rc_vie_privee, ou([f(victime, assure), f(victime, conjoint)]), tout, non, '4.1.1.2',
    "Toute personne autre que celle ayant la qualité d’Assuré.").
exclusion(rc_vie_privee, f(origine_rc, activite_professionnelle), tout, non, '4.1.1.8',
    "de l’exercice de l’activité professionnelle de l’Assuré").
exclusion(rc_vie_privee, f(origine_rc, contrat), tout, non, '4.1.1.8',
    "d’obligations contractuelles de l’Assuré, sauf s’il s’agit d’un contrat bénévole visé au point 4.1.1.5.4 ci-avant").
exclusion(rc_vie_privee, f(origine_rc, vehicule_moteur), tout, non, '4.1.1.8',
    "les véhicules ou appareils ci-après, si l’assuré ou les personnes dont il est civilement responsable en ont la propriété, la conduite, la garde ou l’usage").
exclusion(rc_vie_privee, f(bien_confie, oui), tout, non, '4.1.1.8',
    "les dommages survenant aux objets, immeubles ou animaux qui sont confiés à l’Assuré à un titre quelconque").
exclusion(rc_vie_privee, f(origine_rc, habitation), tout, non, '4.1.1.8',
    "les dommages matériels et immatériels d’incendie, d’explosion, ou d’eau, lorsque l’événement dommageable a son origine dans les locaux ou immeubles appartenant à l’Assuré ou occupés par lui à quelque titre que ce soit").
exclusion(rc_vie_privee, f(sport_aerien, oui), tout, non, '4.1.1.8',
    "de la pratique par l’Assuré de sports aériens").
exclusion(rc_vie_privee, f(concours_hippique, hors_calendrier_officiel), tout, non, '4.1.1.8',
    "de la participation de l’Assuré à des concours hippiques").
exclusion(rc_vie_privee, f(cause_amiante, oui), tout, non, '4.1.1.8',
    "de la présence ou de la dispersion d’amiante, de fibres d’amiante ou de produits contenant de l’amiante").
exclusion(rc_vie_privee, f(pari_ou_defi, oui), tout, non, '4.1.1.8',
    "de la participation à des paris ou défis").
exclusion(rc_vie_privee, ou([f(faute_lourde, ivresse), f(faute_lourde, activite_sans_qualification), f(faute_lourde, maladie_contagieuse)]), tout, non, '4.1.1.8',
    "d’une faute lourde de l’Assuré").
exclusion(rc_vie_privee, f(plus_de_5_chevaux, oui), tout, non, '4.1.1.8',
    "les chevaux propriété de l’Assuré ou gardés à titre gratuit par l’Assuré dès que leur nombre total est supérieur ou égal à six").
exclusion(rc_vie_privee, f(pratique_chasse, oui), tout, non, '4.1.1.8',
    "les dommages engageant une responsabilité civile soumise à une assurance rendue obligatoire au Grand-Duché du Luxembourg").
exclusion(rc_vie_privee, f(origine_rc, vehicule_moteur), tout, non, '4.1.1.8',
    "tous véhicules terrestres construits en vue d’être attelés à un véhicule terrestre à moteur").
exclusion(rc_vie_privee, f(aide_benevole_accident_travail, oui), tout, non, '4.1.1.8',
    "les dommages subis par une personne apportant une aide à titre gratuit à l’Assuré, lorsque ceux-ci relèvent de l’application de la législation sur les Accidents du Travail").
exclusion(rc_vie_privee, f(piece_eau_autre_adresse, oui), tout, non, '4.1.1.8',
    "les dommages causés par les étangs et autres pièces d’eau situés à une autre adresse que la résidence principale").
exclusion(rc_vie_privee, f(glissement_terrain, oui), tout, non, '4.1.1.8',
    "les dommages liés à un glissement, affaissement ou tassement de terrain").
limite(rc_vie_privee, '4.1.1.5', "8.658.260 € par sinistre au titre des dommages corporels", "8658260").
limite(rc_vie_privee, '4.1.1.5', "865.826 € par sinistre au titre des dommages matériels et des dommages immatériels", "865826").
