% --- Art. 2.8 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
garantie(contenu_congelateur_refrigerateur, "Contenu du congélateur et/ou réfrigérateur", '2.8',
    "Contenu du congélateur et/ou réfrigérateur").
perimetre(contenu_congelateur_refrigerateur, f(bien, denrees_alimentaires)).
perimetre(contenu_congelateur_refrigerateur, f(appareil_concerne, congelateur_ou_refrigerateur)).
circonstance(contenu_congelateur_refrigerateur, ou([et([f(evenement, electricite), f(option_degats_electriques, oui)]), f(option_panne_electromenager, oui), et([f(cause_perte_alimentaire, coupure_soudaine_reseau), f(justificatif_fournisseur_electricite, oui)])]), '2.8-b',
    "La garantie couvre les pertes ou détériorations causes aux denrées alimentaires contenues dans les congélateurs et/ou réfrigérateurs endommagés à l occasion d un sinistre dommages électrique indemnisé (ART 2-2), à la suite d un sinistre indemnisé au titre de la garantie panne électroménager (TITRE III) ou d une coupure électrique accidentelle avec justificatif de votre fournisseur d électricité.").
exclusion(contenu_congelateur_refrigerateur, ou([f(cause_arret_electrique, greve_fournisseur), f(cause_arret_electrique, ordres_autorites), f(cause_arret_electrique, fait_assure)]), tout, oui, '2.8-c',
    "provenant de l arrêt d un courant électrique, lorsqu il est dû : - à une grève du fournisseur, - à des ordres émanant d un service public ou des autorités civiles ou militaires, - au fait de l assuré").
exclusion(contenu_congelateur_refrigerateur, f(entretien_congelateur, non_conforme), tout, oui, '2.8-c',
    "dues à un mauvais entretien ou à une utilisation non conforme du congélateur et/ou réfrigérateur aux instructions du fabricant").
exclusion(contenu_congelateur_refrigerateur, f(fuite_liquide_frigorigene, oui), tout, oui, '2.8-c',
    "consécutives à une fuite du liquide frigorigène").
accessoire(contenu_congelateur_refrigerateur).
