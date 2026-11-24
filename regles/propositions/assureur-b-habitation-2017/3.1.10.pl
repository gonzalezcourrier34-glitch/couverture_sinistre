% --- Art. 3.1.10 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(responsabilite).
garantie(rc_immeuble, "Responsabilité civile immeuble (option)", '3.1.10.1',
    "La Compagnie garantit la responsabilité civile qu’un Assuré pourrait encourir sur la base des articles 1382 à 1386 du Code civil, à l’égard d’un tiers, en raison de dommages causés par le fait").
perimetre(rc_immeuble, f(evenement, responsabilite)).
perimetre(rc_immeuble, f(origine_rc, immeuble)).
circonstance(rc_immeuble, f(option_rc_immeuble, oui), '3.1.10',
    "la garantie “ responsabilité civile immeuble ” est accordée").
exclusion(rc_immeuble, ou([f(victime, assure), f(victime, conjoint)]), tout, non, '3.1.10.2',
    "Toute personne autre que celle ayant la qualité d’Assuré.").
exclusion(rc_immeuble, f(bien_confie, oui), tout, non, '3.1.10.3',
    "à des biens dont l’assuré est locataire ou occupant à titre gratuit, ainsi qu’à ceux qui lui ont été confiés").
exclusion(rc_immeuble, f(origine_rc, activite_professionnelle), tout, non, '3.1.10.3',
    "par le fait de l’exercice d’une profession").
exclusion(rc_immeuble, f(ascenseur_non_conforme, oui), tout, non, '3.1.10.1',
    "d ’ascenseurs et d’appareils élévateurs à moteur du bâtiment désigné pour autant qu’ils soient conformes à la réglementation en vigueur et fassent l’objet d’un entretien annuel").
exclusion(rc_immeuble, f(terrain_plus_1_hectare, oui), tout, non, '3.1.10.1',
    "d es terrains y attenant pour autant qu’ils ne dépassent pas un hectare").
exclusion(rc_immeuble, f(cause_amiante, oui), tout, non, '3.1.10.3',
    "par la présence ou la dispersion d’amiante, de fibres d’amiante ou de produits contenant de l’amiante").
exclusion(rc_immeuble, f(terrain_non_attenant, oui), tout, non, '3.1.10.3',
    "par le fait des terrains non attenant dont l’Assuré est propriétaire").
limite(rc_immeuble, '3.1.10.1', "15.554.864 € par sinistre au titre des dommages corporels", "15554864").
limite(rc_immeuble, '3.1.10.1', "896.823 € par sinistre au titre des dommages matériels et des dommages immatériels", "896823").
