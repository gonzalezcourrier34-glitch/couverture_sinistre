% --- Art. 4.1.4 : proposition rédigée par le modèle — mistral:mistral-large-4-0 (proposition écartée), 2026-11-24 ---
evenement_traduit(litige).
garantie(e_protection, "E-protection : litiges liés à Internet (option)", '4.1.4.3~1',
    "La présente protection juridique a pour vocation de protéger l’Assuré contre les risques liés à Internet dans le cadre de sa vie privée aux conditions telles que prévues ci-dessous").
perimetre(e_protection, f(evenement, litige)).
perimetre(e_protection, ou([f(litige_internet, usurpation_identite), f(litige_internet, fraude_paiement), f(litige_internet, e_reputation), f(litige_internet, achat_bien_internet), f(litige_internet, achat_service_internet)])).
perimetre(e_protection, non(ou([f(domaine_litige, travail), f(domaine_litige, logement), f(domaine_litige, travaux), f(domaine_litige, sante), f(domaine_litige, voisinage), f(domaine_litige, employeur_domestique), f(domaine_litige, location_vacances), f(domaine_litige, bateau), f(domaine_litige, association), f(domaine_litige, famille), f(domaine_litige, vehicule_moteur), f(domaine_litige, activite_professionnelle), f(domaine_litige, divorce_succession)]))).
circonstance(e_protection, f(option_e_protection, oui), '4.1.4',
    "la garantie “ E-protection ” est accordée").
circonstance(e_protection, si(ou([f(litige_internet, achat_bien_internet), f(litige_internet, achat_service_internet)]), f(vendeur_lu_be_fr_nl, oui)), '4.1.4.3~1',
    "être acquis auprès d’un professionnel domicilié au Luxembourg, en Belgique, en France, ou aux Pays-Bas").
circonstance(e_protection, si(f(litige_internet, achat_bien_internet), f(achat_bien_conditions, oui)), '4.1.4.3~1',
    "être neuf, n être d’une valeur comprise entre 150 E et 5000 E TTC").
exclusion(e_protection, f(anciennete_garantie, moins_30_jours), tout, non, '4.1.4.4',
    "Pour tous les sinistres, le délai d’attente est d’1 mois à partir de la prise d’effet du contrat").
exclusion(e_protection, f(litige_connu_avant_souscription, oui), tout, non, '4.1.4.4',
    "le fait générateur du sinistre ne doit pas être connu de l’Assuré à la date de prise d’effet de la présente garantie").
exclusion(e_protection, f(domaine_litige, activite_professionnelle), tout, non, '4.1.4.3~1',
    "d’une activité rémunérée ou professionnelle").
exclusion(e_protection, ou([f(litige_nature_exclue, propriete_intellectuelle), f(litige_nature_exclue, douane_fiscalite), f(litige_nature_exclue, gestion_societe), f(litige_nature_exclue, delai_paiement), f(litige_nature_exclue, politique_syndical), f(litige_nature_exclue, droits_tiers_ou_cedes), f(litige_nature_exclue, action_collective), f(litige_nature_exclue, caution_mandat)]), tout, non, '4.1.4.3~1',
    "de litiges liés à la propriété intellectuelle ou autres droits similaires (marques, copyright, droit d’auteur, etc…) ; n de litiges liés à des questions douanières ou fiscales ; n de la participation à l’administration ou à la gestion d’une association ou d’une société civile ou commerciale").
exclusion(e_protection, f(enjeu_moins_150, oui), tout, non, '4.1.4.4',
    "les sinistres dont l’enjeu en principal ne dépasse pas 150 R").
exclusion(e_protection, et([ou([f(litige_internet, usurpation_identite), f(litige_internet, fraude_paiement), f(litige_internet, e_reputation)]), ou([f(auteur, assure), f(auteur, famille)])]), tout, non, '4.1.4.3~2',
    "Le Prestataire ne prend pas en charge les sinistres résultant d’une usurpation d’identité ou d’une utilisation frauduleuse des moyens de paiement ou d’une atteinte à l’e-réputation par une personne assurée au titre des présentes garanties").
exclusion(e_protection, et([f(litige_internet, fraude_paiement), f(code_secret_divulgue, oui)]), tout, non, '4.1.4.3~2',
    "donner la possibilité à un tiers (y compris le (la) conjoint(e), un membre de la famille et des amis) de prendre connaissance du code secret et/ou d’utiliser la carte de crédit ou de débit ; indiquer son code secret sur un support de quelle que forme qu’il soit").
exclusion(e_protection, et([f(litige_internet, fraude_paiement), f(banque_prevenue, non)]), tout, non, '4.1.4.3~2',
    "ne pas notifier immédiatement à sa banque, dès que l’Assuré a connaissance de la perte, du vol ou de l’usage abusif de sa carte de crédit ou de débit, ou de toute utilisation non autorisée de sa carte de crédit ou de débit").
exclusion(e_protection, et([f(litige_internet, e_reputation), f(diffusion_volontaire, oui)]), tout, non, '4.1.4.3~2',
    "une e-réputation que l’Assuré s’est lui-même constituée au travers des réseaux sociaux, commentaires sur les sites Internet ou encore utilisation de son courrier électronique ; n une diffusion volontaire d’informations de données personnelles de la part de l’Assuré").
exclusion(e_protection, et([f(litige_internet, e_reputation), f(auteur_presse, oui)]), tout, non, '4.1.4.3~2',
    "une atteinte à l’e-réputation par une société de presse ou un journaliste").
exclusion(e_protection, et([f(litige_internet, achat_bien_internet), ou([f(bien, animal), f(bien, plantation), f(bien, bijoux), f(bien, objet_art), f(bien, tapis_fourrure), f(bien, valeurs), f(bien, collection), f(bien, collection_timbres_monnaies), f(bien, denrees_alimentaires), f(bien, vehicule_moteur)])]), tout, non, '4.1.4.3~2',
    "d’animaux et de végétaux ; n de bijoux, d’orfèvrerie, de pierres précieuses, de peintures, de sculptures, de tapis, d’espèces").
exclusion(e_protection, et([f(litige_internet, achat_bien_internet), f(achat_bien_exclu, oui)]), tout, non, '4.1.4.3~2',
    "de biens et denrées périssables ; n de médicaments au sens du droit luxembourgeois ; n d’armes de toutes catégories au sens du droit luxembourgeois ; n de véhicules terrestres à moteur ; n de données numériques à visualiser ou à télécharger en ligne").
exclusion(e_protection, et([ou([f(litige_internet, achat_bien_internet), f(litige_internet, achat_service_internet)]), f(achat_enchere, oui)]), tout, non, '4.1.4.3~2',
    "s ur un site de vente aux enchères").
exclusion(e_protection, et([ou([f(litige_internet, achat_bien_internet), f(litige_internet, achat_service_internet)]), f(prix_conteste, oui)]), tout, non, '4.1.4.3~2',
    "dont le prix d’achat est contesté").
exclusion(e_protection, et([ou([f(litige_internet, usurpation_identite), f(litige_internet, fraude_paiement)]), f(litige_hors_europe, oui)]), tout, non, '4.1.4.5',
    "dans un pays membre de l’Union européenne, en ce compris la Suisse, Monaco, Andorre, Saint-Marin, le Vatican, le Liechtenstein et la Norvège pour la garantie en cas d’usurpation d’identité et la garantie en cas d’utilisation frauduleuse des moyens de paiement").
limite(e_protection, '4.1.4.3~1', "l’indemnisation du préjudice s’effectue dans la limite globale de 5000 E toutes taxes comprises (TTC) par année d’assurance", "5000").
