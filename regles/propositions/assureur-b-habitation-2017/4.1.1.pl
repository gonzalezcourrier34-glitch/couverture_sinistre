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
limite(rc_vie_privee, '4.1.1.5', "8.658.260 € par sinistre au titre des dommages corporels", "8658260").
limite(rc_vie_privee, '4.1.1.5', "865.826 € par sinistre au titre des dommages matériels et des dommages immatériels", "865826").
