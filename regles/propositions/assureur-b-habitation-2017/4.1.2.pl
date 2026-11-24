% --- Art. 4.1.2 : proposition rédigée par le modèle — mistral:mistral-large-4-0 (proposition écartée), 2026-11-24 ---
evenement_traduit(responsabilite).
garantie(rc_chasse, "Responsabilité civile chasse (option)", '4.1.2.1',
    "la Compagnie assure le Preneur d’assurance contre les conséquences pécuniaires de la responsabilité civile qu’il peut encourir aux termes des articles 1382 à 1384 du Code Civil ou par application de l’article 136 du Code de la Sécurité Sociale, à raison de dégâts corporels et matériels causés à des tiers par maladresse ou imprudence").
perimetre(rc_chasse, f(evenement, responsabilite)).
perimetre(rc_chasse, f(pratique_chasse, oui)).
circonstance(rc_chasse, f(option_rc_chasse, oui), '4.1.2',
    "la garantie “ responsabilité civile chasse ” est accordée").
exclusion(rc_chasse, f(victime, assure), tout, non, '4.1.2.4',
    "4.1.2.4.1 le Preneur d’assurance et tous ceux dont la responsabilité civile est couverte par le présent contrat").
exclusion(rc_chasse, et([ou([f(victime, conjoint), f(victime, famille)]), non(f(dommage_corporel_arme_chasse, oui))]), tout, non, '4.1.2.4',
    "4.1.2.4.2 le conjoint des personnes visées à l’alinéa qui précède, non séparé de corps ou de fait, les partenaires au sens de la loi modifiée du 9 juillet 2004 relative aux effets légaux de certains partenariats de ces mêmes personnes ainsi que les parents ou alliés en ligne directe des mêmes personnes, à la condition qu’ils habitent sous leur toit et soient entretenus de leurs deniers, étant précisé que sont cependant indemnisés les dommages corporels causés par un accident résultant, lors de l’activité de chasse, d’une arme de chasse").
exclusion(rc_chasse, f(victime, prepose), tout, non, '4.1.2.4',
    "4.1.2.4.3 les personnes bénéficiant de lois spéciales sur la réparation des dommages résultant d’accidents de travail").
exclusion(rc_chasse, f(produit_apres_livraison, oui), tout, non, '4.1.2.7',
    "4.1.2.7.1 les dommages causés par des produits ou marchandises après leur livraison").
exclusion(rc_chasse, f(produit_toxique_non_autorise, oui), tout, non, '4.1.2.7',
    "4.1.2.7.2 les dommages causés par l’emploi de produits toxiques non autorisé préalablement par les autorités compétentes").
exclusion(rc_chasse, f(degat_gibier_cultures, oui), tout, non, '4.1.2.7',
    "4.1.2.7.3 les dégâts causés par le gibier aux cultures et plantations").
exclusion(rc_chasse, f(abri_chasse_en_cause, oui), tout, non, '4.1.2.7',
    "4.1.2.7.4 la responsabilité civile du Preneur d’assurance comme propriétaire, locataire ou occupant à quelque titre que ce soit, de bâtiments et abris de chasse fixes ou mobiles, sauf convention contraire").
exclusion(rc_chasse, f(origine_rc, vehicule_moteur), tout, non, '4.1.2.7',
    "4.1.2.7.5 la responsabilité découlant de la propriété, de la garde ou de l’usage d’un véhicule à moteur de toute catégorie").
exclusion(rc_chasse, f(bien_confie, oui), tout, non, '4.1.2.7',
    "4.1.2.7.6 les dommages causés aux objets ou animaux confiés au Preneur d’assurance ou Assuré à quelque titre que ce soit").
exclusion(rc_chasse, f(pays, hors_europe), tout, non, '4.1.2.5',
    "L’assurance est valable en Europe à l’exception des pays suivants : Albanie, Turquie et tous les pays de l’ex-URSS et de l’ex-Yougoslavie non intégrés à l’Union Européenne").
limite(rc_chasse, '4.1.2.2', "12.000.000 f par sinistre au titre des dommages corporels", "12000000").
limite(rc_chasse, '4.1.2.2', "250.000 f par sinistre au titre des dommages matériels et des dommages immatériels", "250000").
