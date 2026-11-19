:- encoding(utf8).
/*  Règles du contrat Assureur B « Habitation B » (conditions d'assurances, 06/2017).

    Deuxième contrat du projet (DEMARCHE 7.51, 7.52) : le même moteur (regles/moteur.pl) et le même
    vocabulaire de faits (regles/vocabulaire.json) que pour Assureur A. Les règles ne sont pas écrites à
    la main : chaque garantie est rédigée par Mistral Large (`couverture rediger --contrat
    assureur-b-habitation-2017 --article 3.1.6`), contrôlée par le code, relue, puis ajoutée ici par
    `couverture rediger --accepter`.

    Tant qu'aucune garantie n'est ajoutée, aucun événement n'est traduit : le moteur ne conclut
    jamais à un refus, il répond « à examiner par un gestionnaire ».
*/

:- discontiguous definition/4, precision/3, garantie/4, perimetre/2, circonstance/4,
                 obligation/6, exclusion/6, limite/4, evenement_traduit/1, accessoire/1.
% --- Art. 3.1.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
evenement_traduit(incendie).
evenement_traduit(explosion).
evenement_traduit(foudre).
evenement_traduit(electricite).
evenement_traduit(fumee).
evenement_traduit(heurt).
evenement_traduit(vol).
evenement_traduit(vandalisme).
evenement_traduit(attentat).
evenement_traduit(conflit_du_travail).
definition(incendie, et([f(flammes, oui), ou([f(embrasement, oui), f(chaleur_sans_feu, non)])]), '3.1.1.1',
    "L'incendie, c'est-à-dire la destruction par des flammes se propageant ou susceptibles de se propager en dehors de leur domaine normal ou d'objets dont la destination n'est pas, à ce moment, de brûler").
garantie(incendie_base, "Incendie et périls de base", '3.1.1.1',
    "La Compagnie assure les biens désignés, contre les périls suivants : 3.1.1.1.1 L'incendie, c'est-à-dire la destruction par des flammes se propageant ou susceptibles de se propager en dehors de leur domaine normal ou d'objets dont la destination n'est pas, à ce moment, de brûler ; 3.1.1.1.2 L'explosion ou l'implosion ; 3.1.1.1.3 La chute de la foudre ; 3.1.1.1.4 L'électrocution d'animaux ; 3.1.1.1.5 Les fumées et les suies ; 3.1.1.1.6 Les dégâts occasionnés au mobilier assuré et au bâtiment désigné par un événement soudain, résultant de l'action subite de la chaleur ou par le contact direct et immédiat avec un foyer ou une substance incandescente, même lorsqu'il n'y a pas eu embrasement, ni commencement d'incendie.").
perimetre(incendie_base, ou([f(evenement, incendie), f(evenement, explosion), f(evenement, foudre), et([f(evenement, electricite), f(bien, animal)]), f(evenement, fumee), et([ou([f(evenement, incendie), f(evenement, autre)]), f(chaleur_sans_feu, oui)])])).
perimetre(incendie_base, concept(batiment_designe)).
circonstance(incendie_base, si(f(evenement, incendie), concept(incendie)), '3.1.1.1',
    "L'incendie, c'est-à-dire la destruction par des flammes se propageant ou susceptibles de se propager en dehors de leur domaine normal ou d'objets dont la destination n'est pas, à ce moment, de brûler").
garantie(decongelation, "Décongélation denrées", '3.1.1.2',
    "à la décongélation de denrées alimentaires périssables contenues dans un surgélateur, congélateur ou réfrigérateur à usage domestique suite à un changement de température résultant d'un arrêt dans la production du froid imputable à la survenance d'un sinistre couvert par les présentes conditions spéciales ou par les conditions spéciales de la garantie \"dégâts électriques\"").
perimetre(decongelation, f(bien, denrees_alimentaires)).
circonstance(decongelation, ou([f(evenement, incendie), f(evenement, explosion), f(evenement, foudre), f(evenement, electricite)]), '3.1.1.2',
    "imputable à la survenance d'un sinistre couvert par les présentes conditions spéciales ou par les conditions spéciales de la garantie \"dégâts électriques\"").
garantie(linge, "Dégradation linge", '3.1.1.2',
    "à la dégradation du contenu des sèche-linge ou lave-linge à la suite d'un sinistre relevant de l'un des périls prévus aux présentes conditions spéciales de la garantie \"incendie et périls assimilés\" et aux conditions spéciales de la garantie \"dégâts électriques\"").
perimetre(linge, f(bien, objet_divers)).
perimetre(linge, f(lieu, logement)).
circonstance(linge, ou([f(evenement, incendie), f(evenement, explosion), f(evenement, foudre), f(evenement, electricite)]), '3.1.1.2',
    "à la suite d'un sinistre relevant de l'un des périls prévus aux présentes conditions spéciales de la garantie \"incendie et périls assimilés\" et aux conditions spéciales de la garantie \"dégâts électriques\"").
garantie(heurt, "Heurt", '3.1.1.2',
    "au heurt, sauf : n les dégâts causés au contenu par un Assuré ou par un animal lui appartenant ou lui ayant été confié ; n les dégâts causés au bâtiment désigné en cas de déménagement du mobilier ; n les dégâts au bien ou à l'animal ayant causé le heurt ; n les dégâts ne résultant pas directement d'un choc entre deux corps durs ; n les dégâts causés par la grêle.").
perimetre(heurt, f(evenement, heurt)).
perimetre(heurt, concept(batiment_designe)).
exclusion(heurt, ou([f(auteur, assure), f(bien, animal)]), tout, oui, '3.1.1.2',
    "les dégâts causés au contenu par un Assuré ou par un animal lui appartenant ou lui ayant été confié").
exclusion(heurt, et([f(bien, element_batiment), f(demenagement, oui)]), tout, non, '3.1.1.2',
    "les dégâts causés au bâtiment désigné en cas de déménagement du mobilier").
exclusion(heurt, f(bien_a_l_origine_sinistre, oui), tout, oui, '3.1.1.2',
    "les dégâts au bien ou à l'animal ayant causé le heurt").
exclusion(heurt, f(choc_deux_corps_durs, non), tout, non, '3.1.1.2',
    "les dégâts ne résultant pas directement d'un choc entre deux corps durs").
exclusion(heurt, f(alea_tempete, grele), tout, non, '3.1.1.2',
    "les dégâts causés par la grêle").
garantie(degradations_vol, "Dégradations lors de vol", '3.1.1.2',
    "aux dégradations immobilières causées à l'occasion d'un vol ou d'une tentative de vol dans les locaux à occupation régulière ainsi que le vol de parties de bâtiment sauf : n les dommages ou le vol des biens se trouvant à l'extérieur du bâtiment ; n lorsque le bâtiment est en cours de construction, transformation ou rénovation, à moins que l'Assuré démontre que cette circonstance n'a pas contribué à la survenance ou à l'aggravation des conséquences du sinistre.").
perimetre(degradations_vol, f(evenement, vol)).
perimetre(degradations_vol, f(bien, element_batiment)).
exclusion(degradations_vol, et([ou([f(lieu, jardin), f(lieu, terrasse)]), non(f(bien, element_batiment))]), tout, oui, '3.1.1.2',
    "les dommages ou le vol des biens se trouvant à l'extérieur du bâtiment").
exclusion(degradations_vol, et([f(travaux_construction, oui), non(f(lien_causal_travaux, non))]), tout, oui, '3.1.1.2',
    "lorsque le bâtiment est en cours de construction, transformation ou rénovation, à moins que l'Assuré démontre que cette circonstance n'a pas contribué à la survenance ou à l'aggravation des conséquences du sinistre").
exclusion(degradations_vol, f(occupation_irreguliere, oui), tout, oui, '3.1.1.2',
    "aux dégradations immobilières causées à l’occasion d’un vol ou d’une tentative de vol dans les locaux à occupation régulière").
garantie(vandalisme, "Vandalisme", '3.1.1.2',
    "aux dommages causés par un acte de vandalisme ou de malveillance au bâtiment désigné pour autant que les conditions suivantes soient remplies simultanément : n l'Assuré est propriétaire du bâtiment ; n le bâtiment fait l'objet d'une occupation régulière ; n le bâtiment n'est pas en cours de construction, ni de transformation, ni de rénovation. L'indemnisation des dégâts matériels causés par vandalisme ou malveillance est consentie sans application de la règle proportionnelle à concurrence de 2.500 € par sinistre.").
perimetre(vandalisme, f(evenement, vandalisme)).
perimetre(vandalisme, f(bien, element_batiment)).
perimetre(vandalisme, concept(batiment_designe)).
exclusion(vandalisme, f(statut_logement, locataire), tout, oui, '3.1.1.2',
    "l’Assuré est propriétaire du bâtiment").
exclusion(vandalisme, f(occupation_irreguliere, oui), tout, oui, '3.1.1.2',
    "le bâtiment fait l’objet d’une occupation régulière").
exclusion(vandalisme, f(travaux_construction, oui), tout, oui, '3.1.1.2',
    "le bâtiment n’est pas en cours de construction, ni de transformation, ni de rénovation").
limite(vandalisme, '3.1.1.2', "L'indemnisation des dégâts matériels causés par vandalisme ou malveillance est consentie sans application de la règle proportionnelle à concurrence de 2.500 € par sinistre.", "2500 EUR").
garantie(attentats, "Attentats et conflits du travail", '3.1.1.2',
    "aux attentats et conflits du travail : La Compagnie prend en charge à concurrence de 745.000 € par sinistre les dégâts causés directement aux biens désignés : n par des personnes tierces prenant part à de tels événements ; n qui résulteraient de mesures prises dans les cas précités par une autorité légalement constituée pour la sauvegarde et la protection des biens désignés. En cas de sinistre, l'Assuré s'engage à accomplir, dans les plus brefs délais, toutes les démarches en vue de l'indemnisation des dégâts matériels subis. L'Assuré s'engage à ne pas réclamer à la Compagnie, les indemnités relatives aux dégâts matériels à concurrence desquels il a été ou pourra être indemnisé par tout tiers. En cas de double paiement, l'Assuré doit rembourser à la Compagnie les indemnités que celle-ci lui a versées. Sur base de l'autorisation délivrée par les autorités publiques, la Compagnie se réserve le droit de suspendre cette garantie moyennant l'envoi d'une lettre recommandée. La suspension prend cours 7 jours après la notification faite au Preneur d'assurance.").
perimetre(attentats, ou([f(evenement, attentat), f(evenement, conflit_du_travail)])).
perimetre(attentats, concept(batiment_designe)).
obligation(attentats, f(plainte_deposee, oui), faux, non, '3.1.1.2',
    "En cas de sinistre, l'Assuré s'engage à accomplir, dans les plus brefs délais, toutes les démarches en vue de l'indemnisation des dégâts matériels subis.").
limite(attentats, '3.1.1.2', "La Compagnie prend en charge à concurrence de 745.000 € par sinistre les dégâts causés directement aux biens désignés", "745000 EUR").
exclusion([incendie_base, decongelation, linge, heurt, degradations_vol, vandalisme, attentats], f(option_incendie, non), tout, oui, '3.1.1',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ incendie et périls assimilés ” est accordée.").

% --- Art. 3.1.2 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
evenement_traduit(tempete).
definition(tempete, et([f(alea_tempete, vent), f(vent_80_kmh_irm, oui)]), '3.1.2.1',
    "la tempête (à partir de 80km/h)").
garantie(tempete_grele, "Tempête et grêle", '3.1.2.1',
    "La Compagnie assure les biens désignés contre la tempête (à partir de 80km/h), la grêle, le poids de la neige ou de la glace, y compris les dommages liés aux précipitations atmosphériques telles que pluie, neige ou grêle qui pénètrent à l'intérieur du bâtiment désigné par le fait que celui-ci a été préalablement endommagé par les événements précités.").
perimetre(tempete_grele, f(evenement, tempete)).
perimetre(tempete_grele, concept(batiment_designe)).
circonstance(tempete_grele, si(f(alea_tempete, vent), concept(tempete)), '3.1.2.1',
    "la tempête (à partir de 80km/h)").
exclusion(tempete_grele, f(manque_entretien, oui), tout, non, '3.1.2.2',
    "Ne sont toutefois pas couverts les dommages n résultant d'un défaut de réparation ou d'entretien du bâtiment désigné").
exclusion(tempete_grele, et([non(f(bien, element_batiment)), non(f(batiment_endommage_prealablement, oui))]), tout, oui, '3.1.2.2',
    "n causés au contenu se trouvant dans une construction non préalablement endommagée par le vent de tempête, la grêle, la pression de la neige ou de la glace").
exclusion(tempete_grele, et([ou([f(lieu, jardin), f(lieu, terrasse)]), non(f(bien, element_batiment))]), tout, oui, '3.1.2.2',
    "n causés à tout objet non fixé se trouvant à l'extérieur d'une construction, à l'exception du mobilier de jardin").
exclusion(tempete_grele, f(objet_fixe_exterieurement, oui), tout, non, '3.1.2.2',
    "n causés aux objets suivants fixés extérieurement alors même qu'ils seraient réputés immeubles par destination : mât, poteau, pylône, panneau publicitaire, lampadaire, enseigne, tente, bâche , décoration de toit (girouette, …)").
exclusion(tempete_grele, f(piscine, oui), tout, non, '3.1.2.2',
    "piscines, sauf si mention en est faite aux conditions particulières").
exclusion(tempete_grele, et([f(travaux_construction, oui), non(f(construction_close, oui))]), tout, oui, '3.1.2.2',
    "bâtiments en cours de construction, transformation, rénovation à moins que l'assuré ne démontre que cette circonstance n'a pas contribué à la survenance ou à l'aggravation des conséquences du sinistre. Cette exclusion est sans objet si cette construction est close et couverte définitivement avec portes et fenêtres posées à demeure").
exclusion(tempete_grele, f(construction_delabree, oui), tout, non, '3.1.2.2',
    "constructions en démolition ou délabrées, c'est-à-dire si le degré de vétusté de la partie sinistrée dépasse 40%").
exclusion(tempete_grele, f(materiaux_legers_murs, oui), tout, non, '3.1.2.2',
    "constructions dont les murs extérieurs composés de tôle, d'aggloméré de ciment et d'asbeste, de plaques ondulées ou de matériaux légers notamment bois, argile, matière plastique, panneaux agglomérés de bois et analogues représentent plus de 50% de la superficie totale de ces murs").
exclusion(tempete_grele, f(materiaux_legers_toiture, oui), tout, non, '3.1.2.2',
    "constructions dont la toiture composée de bois, d'aggloméré de bois ou analogues, de carton bitumé, de matières plastiques ou d'autres matériaux légers (ardoises et tuiles artificielles, chaume ou roofing non compris) représente plus de 20% de la superficie totale de cette toiture").
exclusion(tempete_grele, et([f(construction_close, non), non(f(abri_fixe_sol, oui))]), tout, non, '3.1.2.2',
    "constructions totalement ou partiellement ouvertes, à l'exception des auvents et marquises en matériaux durs, car-ports et pergolas, sous réserve que ces équipements soient solidement fixés au bâtiment ou qu'ils reposent sur des fondations").
exclusion(tempete_grele, f(deformation_sans_perte_etancheite, oui), tout, non, '3.1.2.2',
    "n causés par la pression de la neige ou de la glace et consistant en la déformation des tuyaux de descente ou du toit sans que cette déformation ait une influence sur l'étanchéité de ceux-ci").
exclusion(tempete_grele, f(choc_thermique, oui), tout, non, '3.1.2.2',
    "n causés par un choc thermique, c'est-à-dire une variation brutale de la température").
exclusion(tempete_grele, f(dommage_esthetique, oui), tout, non, '3.1.2.2',
    "n d'ordre purement esthétique").
limite(tempete_grele, '3.1.2.1', "Les dommages matériels occasionnés aux panneaux solaires et/ou installations photovoltaïques sont couverts à concurrence de 50.000 € par sinistre.", "50000").
limite(tempete_grele, '3.1.2.2', "Dans ce cas, la prise en charge des dommages se fait sans application de la règle proportionnelle à concurrence de 5.000 € par sinistre", "5000").
exclusion([tempete_grele], f(option_tempete, non), tout, oui, '3.1.2',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ tempête et grêle” est souscrite.").

% --- Art. 3.1.3 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
evenement_traduit(electricite).
garantie(degats_electriques, "Dégâts électriques", '3.1.3.1',
    "La Compagnie assure les biens désignés contre l'action de l'électricité.").
perimetre(degats_electriques, f(evenement, electricite)).
perimetre(degats_electriques, concept(batiment_designe)).
exclusion(degats_electriques, et([f(bien, appareil_informatique), f(usage_professionnel, oui)]), bien(appareil_informatique), non, '3.1.3.2',
    "les équipements informatiques et bureautiques à usage professionnel").
exclusion(degats_electriques, f(proprietaire, hote), tout, oui, '3.1.3.2',
    "les équipements dont l'Assuré n'est pas propriétaire").
exclusion(degats_electriques, f(support_donnees_ou_logiciel, oui), tout, non, '3.1.3.2',
    "les dégâts à tous supports de données et aux logiciels de traitement des données").
exclusion(degats_electriques, f(garantie_fabricant, oui), tout, non, '3.1.3.2',
    "les dégâts tombant sous la garantie du fabricant").
exclusion(degats_electriques, f(bien_marchandise, oui), tout, non, '3.1.3.2',
    "les dégâts aux appareils ou installations électriques constituant des marchandises").
exclusion(degats_electriques, et([f(travaux_construction, oui), non(f(lien_causal_travaux, non))]), tout, oui, '3.1.3.2',
    "les dégâts causés lorsque le bâtiment est en cours de construction, de transformation ou de rénovation à moins que l'Assuré démontre que cette circonstance n'a pas contribué à la survenance ou à l'aggravation des conséquences du sinistre").
exclusion(degats_electriques, f(bien, denrees_alimentaires), bien(denrees_alimentaires), non, '3.1.3.2',
    "les dégâts au contenu des appareils électroménagers").
exclusion(degats_electriques, f(appareil_plus_15_ans, oui), tout, oui, '3.1.3.2',
    "les dégâts aux appareils de plus de 15 ans d'âge").
exclusion(degats_electriques, ou([f(manque_entretien, oui), f(fonctionnement_defectueux, oui)]), tout, non, '3.1.3.2',
    "les pertes ou dommages qui sont la conséquence directe : – des effets continuels de l'exploitation (usure) ; – d'un fonctionnement défectueux").
limite(degats_electriques, '3.1.3.1', "Les dommages matériels occasionnés aux panneaux solaires et/ou installations photovoltaïques sont couverts à concurrence de 50.000 € par sinistre.", "50000").
exclusion([degats_electriques], f(option_degats_electriques, non), tout, oui, '3.1.3',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ dégâts électriques” est souscrite.").
% --- Art. 3.1.5 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
evenement_traduit(bris).
garantie(bris_vitrages, "Bris de vitrages", '3.1.5.1',
    "La Compagnie assure les biens désignés, contre les bris et fêlures accidentels des vitrages, des glaces et des miroirs.").
perimetre(bris_vitrages, f(evenement, bris)).
perimetre(bris_vitrages, ou([f(bien, vitre), f(bien, miroir), f(bien, panneau_solaire), f(bien, sanitaire), f(bien, serre), f(bien, table_cuisson_vitroceramique), f(bien, appareil_electromenager), f(bien, cadre), f(bien, chassis), f(bien, soubassement), f(cause_projection_debris, oui)])).
circonstance(bris_vitrages, si(f(type_dommage, opacification_ou_perte_etancheite), non(ou([f(garantie_fabricant, oui), f(statut_logement, locataire)]))), '3.1.5.1',
    "à la perte d’étanchéité des vitrages isolants sauf s’ils sont sous garantie ou si l’Assuré est locataire").
exclusion(bris_vitrages, f(type_dommage, rayure_ou_ecaillement), tout, non, '3.1.5.2',
    "Les rayures, égratignures et écaillements ne sont jamais assurés.").
exclusion(bris_vitrages, f(bien, appareil_audiovisuel), bien(appareil_audiovisuel), non, '3.1.5.2',
    "aux parties vitrées du matériel multimédia").
exclusion(bris_vitrages, et([f(travaux_construction, oui), non(f(lien_causal_travaux, non))]), tout, oui, '3.1.5.2',
    "au bâtiment désigné lorsqu’il est en cours de construction, de transformation ou de rénovation, à moins que l’Assuré ne démontre que cette circonstance n’a pas contribué à la survenance ou à l’aggravation des conséquences du sinistre").
exclusion(bris_vitrages, f(bien, verre_optique), bien(verre_optique), non, '3.1.5.2',
    "aux verres optiques et lunettes").
exclusion(bris_vitrages, f(bien, enseigne), bien(enseigne), non, '3.1.5.2',
    "aux châssis de couche et aux enseignes").
exclusion(bris_vitrages, ou([f(vitre_placee, non), f(vitrage_en_deplacement, oui)]), tout, oui, '3.1.5.2',
    "aux vitrages non encore placés ou pendant leur déplacement").
exclusion(bris_vitrages, et([f(lieu, parties_communes), f(occupation_partielle, oui)]), tout, oui, '3.1.5.2',
    "aux vitrages relevant des parties communes du bâtiment désigné lorsque l’Assuré est propriétaire, locataire ou occupant partiel").
exclusion(bris_vitrages, f(bien, objet_verre_non_vitre), bien(objet_verre_non_vitre), non, '3.1.5.2',
    "aux objets en verre, par exemple lustres, vases, vaisselle").
exclusion(bris_vitrages, f(manque_entretien, oui), tout, non, '3.1.5.2',
    "par un défaut de réparation ou d’entretien des châssis, soubassements et support de vitres, glaces et miroirs").
limite(bris_vitrages, '3.1.5.1', "Les dommages matériels occasionnés aux vitrages des panneaux solaires et/ou installations photovoltaïques sont couverts à concurrence de 50.000€ par sinistre.", "50000").
exclusion([bris_vitrages], f(option_bris_vitrages, non), tout, oui, '3.1.5',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ bris de vitrages ” est souscrite.").
% --- Art. 3.2.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
evenement_traduit(catastrophe_naturelle).
garantie(tremblement_terre, "Tremblement de terre", '3.2.1.1',
    "La Compagnie garantit, sous réserve des exclusions générales et des exclusions spécifiques, les dommages matériels causés aux biens désignés par un tremblement de terre.").
perimetre(tremblement_terre, f(evenement, catastrophe_naturelle)).
perimetre(tremblement_terre, f(catastrophe, tremblement_terre)).
perimetre(tremblement_terre, concept(batiment_designe)).
exclusion(tremblement_terre, et([f(travaux_construction, oui), f(lien_causal_travaux, oui)]), tout, oui, '3.2.1.2',
    "survenus alors que le bâtiment est en cours de construction, transformation ou rénovation dans la mesure où il existe un lien causal entre les dommages et les travaux en cours").
exclusion(tremblement_terre, et([et([ou([f(lieu, jardin), f(lieu, terrasse)]), non(f(bien, element_batiment))]), non(f(fixe_a_demeure, oui))]), tout, oui, '3.2.1.2',
    "survenus aux objets se trouvant à l’extérieur du bâtiment sauf s’ils sont fixés à demeure").
exclusion(tremblement_terre, ou([f(construction_facilement_deplacable, oui), f(construction_delabree, oui)]), tout, oui, '3.2.1.2',
    "aux constructions faciles à déplacer ou à démonter, délabrées ou en cours de démolition de même qu’à leur éventuel contenu").
exclusion(tremblement_terre, et([f(annexe_ancree_beton, non), ou([f(lieu, annexe), f(lieu, abri_jardin)])]), tout, oui, '3.2.1.2',
    "aux dépendances et abris de jardins qui ne reposent pas sur des fondations").
exclusion(tremblement_terre, f(bien, plantation), bien(plantation), non, '3.2.1.2',
    "aux jardins et plantations").
exclusion(tremblement_terre, f(bien, vehicule_moteur), bien(vehicule_moteur), non, '3.2.1.2',
    "aux véhicules terrestres à moteur, aériens, maritimes ou fluviaux").
limite(tremblement_terre, '3.2.1.3', "Lors du règlement de l’indemnité, l’Assuré conserve à sa charge un montant de 10% du dommage avec un minimum de 1.500 €.", "10% du dommage avec un minimum de 1.500 €").
exclusion([tremblement_terre], f(option_tremblement_terre, non), tout, oui, '3.2.1',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ tremblement de terre ” est accordée.").

% --- Art. 3.2.2 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
evenement_traduit(catastrophe_naturelle).
garantie(pluies_inondations, "Pluies & inondations", '3.2.2',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “Pluies & inondations” est accordée.").
perimetre(pluies_inondations, f(evenement, catastrophe_naturelle)).
perimetre(pluies_inondations, ou([f(catastrophe, inondation), f(catastrophe, ruissellement), f(catastrophe, glissement_terrain)])).
perimetre(pluies_inondations, concept(batiment_designe)).
exclusion(pluies_inondations, et([et([ou([f(lieu, jardin), f(lieu, terrasse)]), non(f(bien, element_batiment))]), non(f(bien, mobilier_jardin))]), tout, oui, '3.2.2.4',
    "au contenu se trouvant à l’extérieur des locaux, à l’exception du mobilier de jardin").
exclusion(pluies_inondations, et([f(travaux_construction, oui), f(lien_causal_travaux, oui)]), tout, oui, '3.2.2.4',
    "lorsque le bâtiment est en cours de construction, transformation ou rénovation et qu’il existe un lien causal entre les dommages et les travaux en cours").
exclusion(pluies_inondations, f(ouvertures_non_fermees, oui), tout, oui, '3.2.2.4',
    "par des entrées d’eaux pluviales, de neige ou de glace par des ouvertures non fermées, tels que portes, fenêtres, soupiraux, lucarnes").
exclusion(pluies_inondations, f(cause_eau, eau_souterraine), tout, oui, '3.2.2.4',
    "par les infiltrations d’eaux souterraines").
exclusion(pluies_inondations, f(cause_eau, condensation), tout, non, '3.2.2.4',
    "par l’hygrométrie ambiante, même consécutivement à un sinistre couvert").
exclusion(pluies_inondations, f(cause_eau, condensation), tout, non, '3.2.2.4',
    "par des champignons ou des moisissures, même consécutivement à un sinistre couvert").
exclusion(pluies_inondations, f(manque_entretien, oui), tout, non, '3.2.2.4',
    "par un défaut de réparation ou d’entretien, ou dus à une étanchéité absente, mal conçue ou mal réalisée").
exclusion(pluies_inondations, f(cause_eau, condensation), tout, non, '3.2.2.4',
    "par l’humidité, la porosité, la condensation, les phénomènes de capillarité").
exclusion(pluies_inondations, f(terrain_non_constructible, oui), tout, non, '3.2.2.4',
    "aux bâtiments situés sur un terrain non constructible").
exclusion(pluies_inondations, f(autorisation_gestion_eau_non_respectee, oui), tout, non, '3.2.2.4',
    "aux bâtiments soumis à l’autorisation de l’Administration de la gestion de l’eau et qui ne respectent pas les conditions afférentes à cette autorisation").
exclusion(pluies_inondations, f(dommages_dans_72h, non), tout, non, '3.2.2.1',
    "Les dommages qui résultent des événements climatiques cités ci-dessus seront pris en charge par la Compagnie à conditions qu’ils se soient réalisés dans les 72 heures suivant l’événement.").
limite(pluies_inondations, '3.2.2.2', "Lorsque les conditions particulières mentionnent que les biens désignés ne sont pas situés en zone inondable, l’Assuré bénéficie en cas de sinistre d’une intervention de la Compagnie à concurrence de 250.000€ maximum par sinistre.", "250000").
limite(pluies_inondations, '3.2.2.3', "Lorsque les conditions particulières mentionnent que les biens désignés sont situés en zone inondable, l’Assuré bénéficie en cas de sinistre d’une intervention de la Compagnie à concurrence de 20.000€ maximum par sinistre. En cas de sinistre, la garantie sera accordée dans la limite du plafond indiqué ci-avant soit 20.000€ et après déduction de la franchise de 1.500€ prévue dans le cadre de la présente garantie.", "20000").
limite(pluies_inondations, '3.2.2.4', "Dans ce cas, la prise en charge des dommages se fait sans application de la règle proportionnelle à concurrence de 5.000€ par sinistre", "5000").
exclusion([pluies_inondations], f(option_pluies_inondations, non), tout, oui, '3.2.2',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “Pluies & inondations” est accordée.").

% --- Art. 3.1.8 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
extension(batiment_designe, et([f(residence_principale_inhabitable, oui), f(lieu, autre_batiment), f(pays, luxembourg)]), '3.1.8.2',
    "Si le logement couvert par le présent contrat est devenu temporairement inhabitable en raison d'un sinistre couvert, les garanties sont automatiquement transférées sur le bâtiment pris en location au Grand-Duché de Luxembourg pour une période de 18 mois maximum").
extension(batiment_designe, et([f(sejour_temporaire, oui), f(lieu, autre_batiment)]), '3.1.8.3',
    "La Compagnie couvre également les dégâts causés aux objets personnels qu'un Assuré déplace à l'occasion d'un séjour temporaire privé ou professionnel dans un bâtiment situé n'importe où dans le monde").
extension(batiment_designe, et([f(lieu, chambre_etudiant), ou([f(pays, luxembourg), f(pays, allemagne), f(pays, belgique), f(pays, france), f(pays, autre_ue), f(pays, suisse), f(pays, norvege)])]), '3.1.8.4',
    "Les garanties sont étendues au contenu qui leur appartient et qui est entreposé dans ce logement").
extension(batiment_designe, f(lieu, maison_repos), '3.1.8.5',
    "La Compagnie couvre les dommages matériels accidentels causés au contenu appartenant au Preneur d'assurance, à son conjoint ou à leurs ascendants entreposé dans la chambre ou l'appartement occupé en maison de repos").
extension(batiment_designe, et([f(bien, sepulture), f(pays, luxembourg)]), '3.1.8.7',
    "La Compagnie couvre les dommages matériels accidentels causés aux sépultures dont un des assurés est propriétaire et situées au Grand-Duché de Luxembourg ou dans un rayon de maximum 50 km au-delà des frontières").
extension(batiment_designe, et([f(demenagement, oui), f(pays, luxembourg), f(duree_demenagement, moins_90_jours)]), '3.1.8.8',
    "En cas de déménagement au Grand-Duché de Luxembourg, les garanties souscrites sont acquises tant à l'ancienne qu'à la nouvelle adresse pendant 90 jours à compter du début du déménagement").
garantie(rc_sejour_temporaire, "Dégâts causés à l'hôtel ou à la villégiature (responsabilité)", '3.1.8.3',
    "Les dégâts matériels accidentels causés par un Assuré à l’occasion d’un séjour temporaire privé ou professionnel n’importe où dans le monde : n à un bâtiment de villégiature loué par un Assuré ; n à l’hôtel ou logement similaire occupé par un Assuré").
perimetre(rc_sejour_temporaire, f(sejour_temporaire, oui)).
perimetre(rc_sejour_temporaire, f(lieu, autre_batiment)).
garantie(rc_logement_etudiant, "Dégâts causés au logement d'étudiant (responsabilité)", '3.1.8.4',
    "La Compagnie couvre les dégâts matériels accidentels causés par les enfants assurés au logement –chambre ou studio– meublé ou non qu'ils louent pendant leurs études dans un des pays membre de l'Union Européenne, en Suisse ou en Norvège").
perimetre(rc_logement_etudiant, f(lieu, chambre_etudiant)).
perimetre(rc_logement_etudiant, ou([f(pays, luxembourg), f(pays, allemagne), f(pays, belgique), f(pays, france), f(pays, autre_ue), f(pays, suisse), f(pays, norvege)])).
garantie(rc_local_fete, "Dégâts causés au local de fête (responsabilité)", '3.1.8.6',
    "La Compagnie couvre les dommages matériels accidentels causés par un Assuré aux locaux situés au Grand-duché de Luxembourg, en Allemagne, en Belgique ou en France, pris en location à l'occasion d'une fête privée").
perimetre(rc_local_fete, f(lieu, local_fete_privee)).
perimetre(rc_local_fete, ou([f(pays, luxembourg), f(pays, allemagne), f(pays, belgique), f(pays, france)])).
accessoire(rc_sejour_temporaire).
accessoire(rc_logement_etudiant).
accessoire(rc_local_fete).

% --- Art. 3.1.9 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
garantie(frais_sauvetage, "Frais de sauvetage", '3.1.9.1',
    "La Compagnie prend en charge les frais engagés pour arrêter ou limiter le sinistre, mais aussi pour soustraire les biens désignés aux effets d'un péril assuré.").
exclusion(frais_sauvetage, non(f(option_incendie, oui)), tout, oui, '3.1.9',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ incendie et périls assimilés ” est souscrite.").
limite(frais_sauvetage, '3.1.9', "Les frais de sauvetage sont pris en charge à concurrence des frais exposés.", "frais exposés").
garantie(frais_deblai_demolition, "Frais de déblai et démolition", '3.1.9.2',
    "La Compagnie prend en charge les frais nécessaires à la reconstruction ou à la reconstitution des biens assurés et sinistrés.").
exclusion(frais_deblai_demolition, non(f(option_incendie, oui)), tout, oui, '3.1.9',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ incendie et périls assimilés ” est souscrite.").
limite(frais_deblai_demolition, '3.1.9', "Ces frais, à l'exception des frais de sauvetage, sont pris en charge à concurrence de 1.000.000 € maximum par sinistre", "1000000").
garantie(frais_conservation_entreposage, "Frais de conservation et d'entreposage", '3.1.9.3',
    "La Compagnie prend en charge les frais nécessaires à la conservation ou à l'entreposage des biens sauvés.").
exclusion(frais_conservation_entreposage, non(f(option_incendie, oui)), tout, oui, '3.1.9',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ incendie et périls assimilés ” est souscrite.").
limite(frais_conservation_entreposage, '3.1.9', "Ces frais, à l'exception des frais de sauvetage, sont pris en charge à concurrence de 1.000.000 € maximum par sinistre", "1000000").
garantie(frais_logement_provisoire, "Frais de logement provisoire", '3.1.9.4',
    "Lorsque les locaux à usage privé sont devenus inutilisables, la Compagnie prend en charge les frais nécessaires au logement provisoire dans un hôtel ou ailleurs pendant une durée maximale de quatre-vingt-dix jours à concurrence d'un montant maximum de 80 € par nuit par personne vivant habituellement au domicile de l'Assuré.").
perimetre(frais_logement_provisoire, f(residence_principale_inhabitable, oui)).
exclusion(frais_logement_provisoire, non(f(option_incendie, oui)), tout, oui, '3.1.9',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ incendie et périls assimilés ” est souscrite.").
limite(frais_logement_provisoire, '3.1.9.4', "pendant une durée maximale de quatre-vingt-dix jours à concurrence d'un montant maximum de 80 € par nuit par personne vivant habituellement au domicile de l'Assuré", "80€/nuit/personne, max 90 jours").
garantie(chomage_immobilier, "Chômage immobilier", '3.1.9.5',
    "L'intervention de la Compagnie est limitée à la durée normale de reconstruction du bâtiment, avec un maximum de 24 mois. Cette indemnisation ne peut se cumuler, pour une même période, avec les frais de logement précités.").
exclusion(chomage_immobilier, non(f(option_incendie, oui)), tout, oui, '3.1.9',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ incendie et périls assimilés ” est souscrite.").
limite(chomage_immobilier, '3.1.9.5', "avec un maximum de 24 mois", "24 mois").
garantie(frais_depollution, "Frais de dépollution", '3.1.9.6',
    "La Compagnie prend en charge les frais d'assainissement des terrains pollués par l'écoulement d'huile minérale et frais de transport et de déblaiement des terres polluées par l'écoulement d'huile minérale suite à un sinistre couvert à concurrence de 25.000 €").
perimetre(frais_depollution, f(cause_pollution, huile_minerale)).
circonstance(frais_depollution, f(reglementation_pollution_respectee, oui), '3.1.9.6',
    "que la règlementation en la matière ait été respectée").
exclusion(frais_depollution, et([f(travaux_construction, oui), non(f(lien_causal_travaux, oui))]), tout, oui, '3.1.9.6',
    "Si le bâtiment est en cours de transformation, construction ou reconstruction, l'extension de garantie est inopérante à moins que l'Assuré ne démontre que cette circonstance n'a pas contribué à la survenance ou à l'aggravation des conséquences du sinistre.").
exclusion(frais_depollution, non(f(option_incendie, oui)), tout, oui, '3.1.9',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ incendie et périls assimilés ” est souscrite.").
limite(frais_depollution, '3.1.9.6', "à concurrence de 25.000 €", "25000").
garantie(frais_remise_etat_jardins, "Frais de remise en état des jardins", '3.1.9.7',
    "La Compagnie prend en charge les frais nécessaires à la remise en état des jardins et des plantations endommagées par un péril couvert.").
exclusion(frais_remise_etat_jardins, non(f(option_incendie, oui)), tout, oui, '3.1.9',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ incendie et périls assimilés ” est souscrite.").
limite(frais_remise_etat_jardins, '3.1.9.7', "Si les biens désignés n'ont pas été endommagés, l'intervention de la Compagnie se limitera à 3.000€ sur base des justificatifs fournis par l'Assuré.", "3000").
garantie(frais_expertise, "Frais d'expertise", '3.1.9.8',
    "La Compagnie prend en charge le remboursement à l'Assuré des honoraires (toutes taxes éventuelles comprises) qu'il a effectivement payés à l'expert qu'il a désigné pour l'évaluation des dégâts aux biens désignés").
exclusion(frais_expertise, non(f(option_incendie, oui)), tout, oui, '3.1.9',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ incendie et périls assimilés ” est souscrite.").
limite(frais_expertise, '3.1.9.8', "sans que cette indemnisation ne puisse dépasser les montants résultant de l'application du barème repris ci-dessous", "selon barème (max 21.617 €)").
garantie(recours_locataires_occupants, "Recours des locataires ou occupants", '3.1.9.9',
    "La Compagnie couvre les frais que l'Assuré pourrait être amené à supporter en qualité soit de bailleur, en vertu de l'article 1721, deuxième alinéa du Code civil, à l'égard des locataires, soit de propriétaire à l'égard des occupants autres que locataires.").
exclusion(recours_locataires_occupants, non(f(option_incendie, oui)), tout, oui, '3.1.9',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ incendie et périls assimilés ” est souscrite.").
limite(recours_locataires_occupants, '3.1.9', "Ces frais, à l'exception des frais de sauvetage, sont pris en charge à concurrence de 1.000.000 € maximum par sinistre", "1000000").
garantie(recours_tiers, "Recours des tiers", '3.1.9.10',
    "La Compagnie couvre les frais que l'Assuré peut encourir en vertu des articles 1382 à 1386 du Code civil pour les dommages matériels causés par un sinistre garanti se communiquant à des biens qui sont la propriété de tiers.").
exclusion(recours_tiers, non(f(option_incendie, oui)), tout, oui, '3.1.9',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ incendie et périls assimilés ” est souscrite.").
limite(recours_tiers, '3.1.9', "Ces frais, à l'exception des frais de sauvetage, sont pris en charge à concurrence de 1.000.000 € maximum par sinistre", "1000000").
accessoire(frais_sauvetage).
accessoire(frais_deblai_demolition).
accessoire(frais_conservation_entreposage).
accessoire(frais_logement_provisoire).
accessoire(chomage_immobilier).
accessoire(frais_depollution).
accessoire(frais_remise_etat_jardins).
accessoire(frais_expertise).
accessoire(recours_locataires_occupants).
accessoire(recours_tiers).

% --- Art. 3.2.3 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
garantie(pertes_indirectes, "Pertes indirectes", '3.2.3',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ pertes indirectes ” est accordée. La Compagnie garantit la majoration de 10% des indemnités contractuellement dues, en vue de dédommager l’Assuré à la suite d’un sinistre couvert.").
exclusion(pertes_indirectes, non(f(option_pertes_indirectes, oui)), tout, oui, '3.2.3',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ pertes indirectes ” est accordée.").
limite(pertes_indirectes, '3.2.3', "La Compagnie garantit la majoration de 10% des indemnités contractuellement dues, en vue de dédommager l’Assuré à la suite d’un sinistre couvert.", "majoration de 10% des indemnités contractuellement dues").
accessoire(pertes_indirectes).
% --- Art. 3.1.7 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
evenement_traduit(bris).
evenement_traduit(vol).
garantie(materiel_multimedia_bris, "Bris du matériel multimédia", '3.1.7.1',
    "La Compagnie couvre tout bris ou destruction accidentel résultant d’une chute, d’un choc ou de la pénétration d’un corps étranger et qui rend nécessaire la réparation ou le remplacement du matériel multimédia. Sont également couverts au titre de cette garantie les équipements suivants : n équipement d’alarme et de surveillance, en activité ou au repos, pendant les opérations de démontage, de déplacement sur les lieux assurés ou de remontage nécessitées pour leur entretien ou leur révision, pour autant que la mise en exploitation desdits matériels ait donné entière satisfaction ; n équipement domotique").
perimetre(materiel_multimedia_bris, f(evenement, bris)).
perimetre(materiel_multimedia_bris, ou([f(bien, electronique), f(bien, equipement_alarme_surveillance), f(bien, equipement_domotique)])).
obligation(materiel_multimedia_bris, si(f(lieu, vehicule), et([f(vehicule_ferme_cle, oui), non(f(materiel_laisse_en_vue, oui))])), faux, non, '3.1.7.4',
    "Lorsque les biens assurés se trouvent à l’intérieur d’un véhicule inoccupé, la garantie intervient uniquement si les deux conditions suivantes sont remplies simultanément : n le véhicule a été fermé à clé ; n le matériel assuré n’a pas été laissé en vue à l’intérieur de l’habitacle du véhicule").
exclusion(materiel_multimedia_bris, et([f(bien, equipement_alarme_surveillance), f(mise_en_exploitation_satisfaction, non)]), bien(equipement_alarme_surveillance), non, '3.1.7.1',
    "pour autant que la mise en exploitation desdits matériels ait donné entière satisfaction").
limite(materiel_multimedia_bris, '3.1.7.1', "1 0.000 € par sinistre lorsque les conditions particulières mentionnent que la formule «Privilège» est souscrite", "10000").
limite(materiel_multimedia_bris, '3.1.7.1', "5.000 € par sinistre lorsque les conditions particulières mentionnent que la formule «Active» est souscrite", "5000").
garantie(materiel_multimedia_vol, "Vol du matériel multimédia", '3.1.7.1',
    "Sous réserve que la garantie vol ait été accordée, la Compagnie couvre également : n le vol du matériel multimédia lorsque le vol a eu lieu à l’extérieur du bâtiment désigné ; n le vol de ces équipements se trouvant à l’intérieur d’un véhicule terrestre automoteur à condition que ledit véhicule soit également volé ou qu’il y ait effraction caractérisée du véhicule ; n le vol de ces équipements qu’un Assuré déplace à l’occasion d’un séjour temporaire dans un bâtiment situé n’importe où dans le monde, pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes").
perimetre(materiel_multimedia_vol, f(evenement, vol)).
perimetre(materiel_multimedia_vol, ou([f(bien, electronique), f(bien, equipement_alarme_surveillance), f(bien, equipement_domotique)])).
circonstance(materiel_multimedia_vol, ou([non(concept(batiment_designe)), et([f(lieu, vehicule), ou([f(vehicule_vole, oui), f(effraction, oui)])]), et([f(sejour_temporaire, oui), f(plainte_deposee, oui)])]), '3.1.7.1',
    "le vol du matériel multimédia lorsque le vol a eu lieu à l’extérieur du bâtiment désigné ; n le vol de ces équipements se trouvant à l’intérieur d’un véhicule terrestre automoteur à condition que ledit véhicule soit également volé ou qu’il y ait effraction caractérisée du véhicule ; n le vol de ces équipements qu’un Assuré déplace à l’occasion d’un séjour temporaire dans un bâtiment situé n’importe où dans le monde, pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes").
obligation(materiel_multimedia_vol, si(f(lieu, vehicule), et([f(vehicule_ferme_cle, oui), non(f(materiel_laisse_en_vue, oui))])), faux, non, '3.1.7.4',
    "Lorsque les biens assurés se trouvent à l’intérieur d’un véhicule inoccupé, la garantie intervient uniquement si les deux conditions suivantes sont remplies simultanément : n le véhicule a été fermé à clé ; n le matériel assuré n’a pas été laissé en vue à l’intérieur de l’habitacle du véhicule").
exclusion(materiel_multimedia_vol, f(option_vol, non), tout, oui, '3.1.7.1',
    "Sous réserve que la garantie vol ait été accordée").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(proprietaire, hote), tout, oui, '3.1.7.2',
    "le matériel dont l'Assuré n'est pas propriétaire").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(cause_dommage, virus), tout, non, '3.1.7.2',
    "les pertes liées à l'action d'un virus et tous préjudices consécutifs").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(vice_defaut_connu, oui), tout, non, '3.1.7.2',
    "les pertes ou dommages dus à des vices ou défauts qui existaient à la date d'effet de la présente assurance et qui étaient connus de l'Assuré ou de ses mandataires").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], ou([f(manque_entretien, oui), f(fonctionnement_defectueux, oui)]), tout, non, '3.1.7.2',
    "les pertes ou dommages qui sont la conséquence directe : n des effets continuels de l’exploitation (usure) ; n d’un fonctionnement défectueux").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(garantie_fabricant, oui), tout, non, '3.1.7.2',
    "les pertes ou dommages dont le fabricant ou le fournisseur est légalement ou contractuellement responsable").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(bien, consommable), bien(consommable), non, '3.1.7.2',
    "les pertes ou dommages causés aux lampes,tubes, bandes transporteuses, fusibles, joints, courroies, chaînes").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(type_dommage, rayure_ou_ecaillement), tout, non, '3.1.7.2',
    "les défauts d'ordre esthétique, tels que les bosses, égratignures, rayures ou écaillements").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(evenement, electricite), tout, oui, '3.1.7.2',
    "les dommages d'origine électrique").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(bien, denrees_alimentaires), bien(denrees_alimentaires), non, '3.1.7.2',
    "les dommages causés au contenu des appareils").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], ou([f(auteur, assure), f(auteur, famille), et([f(auteur, personnel_prive), ou([f(heures_service, oui), non(ou([f(effraction, oui), f(violence, oui)]))])])]), tout, oui, '3.1.7.2',
    "les vols commis par ou avec la complicité de ou du : n Preneur d’assurance, son conjoint, leurs ascendants ou descendants ainsi que les conjoints de ces personnes ; n l’Assuré ; n toute personne au service de l’Assuré pendant les heures de service et, si ces vols ont été commis en dehors de celles-ci, autrement que par effraction ou avec violence. En ce qui concerne les pièces mentionnées aux points").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(option_materiel_multimedia, non), tout, oui, '3.1.7',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “matériel multimédia” est accordée.").

% --- Art. 3.1.4 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
evenement_traduit(degat_eaux).
garantie(degats_eaux_3_1_4, "Dégâts des eaux", '3.1.4',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ dégâts des eaux ” est souscrite.").
perimetre(degats_eaux_3_1_4, f(evenement, degat_eaux)).
perimetre(degats_eaux_3_1_4, concept(batiment_designe)).
circonstance(degats_eaux_3_1_4, ou([f(cause_eau, fuite_installation), f(cause_eau, infiltration_toiture), f(cause_eau, debordement_aquarium)]), '3.1.4.1',
    "La Compagnie assure les biens désignés contre les dégâts des eaux c’est-à-dire : n l’écoulement de l’eau des installations hydrauliques se trouvant à l’intérieur du bâtiment désigné et des bâtiments voisins, par suite de rupture, fissure ou débordement de ces installations ; n la pénétration ou l’infiltration dans le bâtiment désigné d’eau provenant de précipitations atmosphériques par suite de rupture, fissure ou débordement dans les tuyaux extérieurs destinés à l’évacuation de cette eau ; n l’infiltration accidentelle d’eau par les toitures, ciels vitrés, terrasses, balcons et balcons formant terrasse, loggias.").
exclusion(degats_eaux_3_1_4, f(bien, toiture), bien(toiture), non, '3.1.4.2',
    "à la toiture du bâtiment ainsi qu’aux revêtements qui en assurent l’étanchéité").
exclusion(degats_eaux_3_1_4, f(bien, canalisation), bien(canalisation), non, '3.1.4.2',
    "a ux conduites, aux installations et appareils hydrauliques, aux tuyaux d’évacuation, aux boilers, chaudières, citernes, aquariums et matelas d’eau à l’origine du sinistre ; toutefois, les dommages aux conduites encastrées sont pris en charge par la Compagnie").
exclusion(degats_eaux_3_1_4, f(cause_eau, condensation), tout, non, '3.1.4.2',
    "par la condensation").
exclusion(degats_eaux_3_1_4, et([f(cause_eau, infiltration_exterieure), non(ou([f(lieu, autre_batiment), f(installation_hydraulique_exterieure, oui)]))]), tout, oui, '3.1.4.2',
    "par la porosité des murs sauf si celle-ci trouve son origine dans un ou des bâtiments voisins ou dans une fuite ou un débordement des installations hydrauliques extérieures au bâtiment désigné").
exclusion(degats_eaux_3_1_4, f(evenement, tempete), tout, non, '3.1.4.2',
    "par tous les événements pouvant être pris en charge au titre de la garantie « tempête et grêle » ou de la garantie « pluies & inondations »").
exclusion(degats_eaux_3_1_4, f(cause_eau, infiltration_exterieure), tout, oui, '3.1.4.2',
    "par des entrées d’eaux pluviales, de neige ou de glace par des ouvertures fermées ou non, telles que portes, fenêtres, soupiraux, lucarne").
exclusion(degats_eaux_3_1_4, f(cause_eau, eau_souterraine), tout, oui, '3.1.4.2',
    "par les infiltrations d’eaux souterraines").
exclusion(degats_eaux_3_1_4, f(cause_eau, debordement_recipient), tout, oui, '3.1.4.2',
    "par les dommages causés par un objet non relié à l’installation hydraulique du bâtiment à l’exception des aquariums et matelas d’eau").
exclusion(degats_eaux_3_1_4, f(corrosion_visible, oui), tout, non, '3.1.4.2',
    "par des conduites, installations et appareils apparents présentant des points de corrosion visibles et non traités").
exclusion(degats_eaux_3_1_4, et([f(travaux_construction, oui), non(f(lien_causal_travaux, non))]), tout, oui, '3.1.4.2',
    "lorsque le bâtiment désigné est en cours de construction, de transformation ou de rénovation, à moins que l’Assuré ne démontre que cette circonstance n’a pas contribué à la survenance ou à l’aggravation des conséquences du sinistre").
exclusion(degats_eaux_3_1_4, f(cause_eau, condensation), tout, non, '3.1.4.2',
    "par l’hygrométrie ambiante, même consécutivement à un sinistre couvert").
exclusion(degats_eaux_3_1_4, f(cause_eau, condensation), tout, non, '3.1.4.2',
    "par des champignons ou des moisissures, même consécutivement à un sinistre couvert").
exclusion(degats_eaux_3_1_4, f(manque_entretien, oui), tout, non, '3.1.4.2',
    "par un défaut de réparation ou d’entretien, ou dus à une étanchéité absente, mal conçue ou mal réalisée").
exclusion(degats_eaux_3_1_4, f(travaux_batiment, entretien_reparation), tout, oui, '3.1.4.2',
    "lors du remplissage, de travaux de révision ou de réparation des installations et/ou citernes d’huiles minérales").
limite(degats_eaux_3_1_4, '3.1.4.1', "La perte d’eau subie à l’occasion d’un sinistre couvert est prise en charge à concurrence de 1.000 €.", "1000").
limite(degats_eaux_3_1_4, '3.1.4.3', "Si l’Assuré ne respecte pas ces prescriptions, sauf cas de force majeure, et si un sinistre survient ou est aggravé de ce fait, l’indemnité due sera réduite de moitié.", "indemnité réduite de moitié si les conduites n'ont pas été vidangées ou protégées").
exclusion([degats_eaux_3_1_4], f(option_degats_eaux, non), tout, oui, '3.1.4',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ dégâts des eaux ” est souscrite.").

% --- Art. 3.1.6 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-18 ---
evenement_traduit(vol).
evenement_traduit(vandalisme).
definition(vol_simple, et([f(effraction, non), f(violence, non)]), '3.1.6.2',
    "les vols simples").
definition(batiment_designe, ou([f(lieu, logement), f(lieu, cave), f(lieu, grenier), f(lieu, garage)]), '3.1.6.1',
    "le bâtiment désigné").
garantie(vol_batiment, "Vol bâtiment désigné", '3.1.6.1',
    "La Compagnie garantit, pour autant qu'une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes : n Le vol ou la tentative de vol du contenu ou des valeurs situés dans le bâtiment désigné.").
perimetre(vol_batiment, f(evenement, vol)).
perimetre(vol_batiment, concept(batiment_designe)).
circonstance(vol_batiment, f(plainte_deposee, oui), '3.1.6.1',
    "pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes").
limite(vol_batiment, '3.1.6.3', "à concurrence de 40% du montant indiqué aux conditions particulières au titre du contenu, pour les objets tels que meubles d’époque et objets de valeur", "40 % du contenu").
limite(vol_batiment, '3.1.6.3', "concernant les timbres de collection, l’indemnité par timbre ne pourra être supérieure à 500 €", "500 € par timbre").
limite(vol_batiment, '3.1.6.3', "à concurrence de 1500 € par sinistre pour l’ensemble constitué de l’argent comptant", "1 500 € (750 € hors clefs)").
limite(vol_batiment, '3.1.6.4', "En cas de sinistre dont la charge est aggravée en raison de la non-utilisation de ces systèmes de protection, la Compagnie se réserve le droit de réduire l’indemnité à concurrence de l’aggravation de son préjudice.", "indemnité réduite à concurrence de l'aggravation si les protections n'étaient pas utilisées").
garantie(vandalisme_vol, "Vandalisme lors vol", '3.1.6.1',
    "Les dégâts causés par vandalisme au contenu à l'occasion d'un vol ou d'une tentative de vol.").
perimetre(vandalisme_vol, f(evenement, vandalisme)).
perimetre(vandalisme_vol, f(evenement, vol)).
circonstance(vandalisme_vol, f(plainte_deposee, oui), '3.1.6.1',
    "pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes").
garantie(vol_annexes, "Vol annexes", '3.1.6.1',
    "Le vol ou la tentative de vol du contenu entreposé dans les annexes même non contiguës et équipées de serrures à cylindre. Cette intervention se fait sans application de la règle proportionnelle à concurrence de 2.500 € par sinistre.").
perimetre(vol_annexes, f(evenement, vol)).
perimetre(vol_annexes, f(lieu, annexe)).
perimetre(vol_annexes, f(serrure_cylindre, oui)).
circonstance(vol_annexes, f(plainte_deposee, oui), '3.1.6.1',
    "pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes").
limite(vol_annexes, '3.1.6.1', "Cette intervention se fait sans application de la règle proportionnelle à concurrence de 2.500 € par sinistre.", "2500").
garantie(remplacement_cles, "Remplacement clés", '3.1.6.1',
    "Les frais liés au remplacement des clés et serrures du bâtiment désigné suite à la perte ou au vol des clés, et moyennant le respect des obligations reprises au point 2.11.2.3 des conditions générales communes. Pour ce qui concerne les bâtiments dont l'Assuré est occupant partiel, cette intervention ne vise que les portes donnant directement accès à la partie occupée par lui.").
perimetre(remplacement_cles, f(evenement, vol)).
perimetre(remplacement_cles, f(bien, cles)).
circonstance(remplacement_cles, f(plainte_deposee, oui), '3.1.6.1',
    "pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes").
limite(remplacement_cles, '3.1.6.1', "Pour ce qui concerne les bâtiments dont l’Assuré est occupant partiel, cette intervention ne vise que les portes donnant directement accès à la partie occupée par lui.", "portes de la partie occupée").
garantie(vol_monde_sejour, "Vol monde séjour temporaire", '3.1.6.1',
    "au vol par effraction dans un bâtiment situé partout dans le monde, d'objets personnels appartenant à l'Assuré et déplacés dans le cadre d'un séjour temporaire avec un maximum de 2.500 € par sinistre.").
perimetre(vol_monde_sejour, f(evenement, vol)).
perimetre(vol_monde_sejour, f(effraction, oui)).
perimetre(vol_monde_sejour, f(sejour_temporaire, oui)).
perimetre(vol_monde_sejour, f(proprietaire, assure)).
circonstance(vol_monde_sejour, f(plainte_deposee, oui), '3.1.6.1',
    "pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes").
limite(vol_monde_sejour, '3.1.6.1', "avec un maximum de 2.500 € par sinistre.", "2500").
garantie(vol_privilege_concierge, "Vol Privilège concierge", '3.1.6.1',
    "au vol survenu au domicile des concierges ou de toute autre personne faisant fonction et désignée par l'assemblée des co-propriétaires- de biens qui leur ont été confiés par l'Assuré ou à l'attention de l'Assuré. Cette intervention se fait sans application de la règle proportionnelle à concurrence de 2.500 € par sinistre").
perimetre(vol_privilege_concierge, f(evenement, vol)).
perimetre(vol_privilege_concierge, f(formule, privilege)).
perimetre(vol_privilege_concierge, f(confiance_assure, oui)).
circonstance(vol_privilege_concierge, f(plainte_deposee, oui), '3.1.6.1',
    "pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes").
limite(vol_privilege_concierge, '3.1.6.1', "Cette intervention se fait sans application de la règle proportionnelle à concurrence de 2.500 € par sinistre", "2500").
garantie(vol_privilege_jardin, "Vol Privilège jardin", '3.1.6.1',
    "au vol ou la tentative de vol du mobilier de jardin, de l'outillage motorisé ou non, ou des plantations situés à l'adresse du risque, même en dehors du bâtiment désigné. Cette intervention se fait sans application de la règle proportionnelle à concurrence de 5.000 € par sinistre.").
perimetre(vol_privilege_jardin, f(evenement, vol)).
perimetre(vol_privilege_jardin, f(formule, privilege)).
perimetre(vol_privilege_jardin, ou([f(bien, mobilier_jardin), f(bien, plantation)])).
perimetre(vol_privilege_jardin, f(lieu, jardin)).
circonstance(vol_privilege_jardin, f(plainte_deposee, oui), '3.1.6.1',
    "pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes").
limite(vol_privilege_jardin, '3.1.6.1', "Cette intervention se fait sans application de la règle proportionnelle à concurrence de 5.000 € par sinistre.", "5000").
garantie(vol_agression, "Vol par agression", '3.1.6.1',
    "au vol par agression sur un Assuré partout dans le monde en ce compris par intrusion dans un véhicule en circulation. Cette intervention se fait sans application de la règle proportionnelle à concurrence de 6.000 € par sinistre ; les valeurs sont indemnisées à concurrence de 750 €. Lorsque les conditions particulières mentionnant que a formule \"Active\" est souscrite, la Compagnie étend sans supplément de prime la portée de la garantie au vol par agression sur un l'Assuré partout dans le monde en ce compris par intrusion dans un véhicule en circulation. Cette intervention se fait sans application de la règle proportionnelle à concurrence de 2.500 € par sinistre ; les valeurs sont indemnisées à concurrence de 750 €.").
perimetre(vol_agression, f(evenement, vol)).
perimetre(vol_agression, f(violence, oui)).
perimetre(vol_agression, f(vol_sur_personne, oui)).
perimetre(vol_agression, ou([f(formule, privilege), f(formule, active)])).
circonstance(vol_agression, f(plainte_deposee, oui), '3.1.6.1',
    "pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes").
limite(vol_agression, '3.1.6.1', "Cette intervention se fait sans application de la règle proportionnelle à concurrence de 6.000 € par sinistre", "6000").
limite(vol_agression, '3.1.6.1', "les valeurs sont indemnisées à concurrence de 750 €", "750").
limite(vol_agression, '3.1.6.1', "Cette intervention se fait sans application de la règle proportionnelle à concurrence de 2.500 € par sinistre", "2500").
exclusion([vol_batiment, vandalisme_vol, vol_annexes, remplacement_cles, vol_monde_sejour, vol_privilege_concierge, vol_privilege_jardin, vol_agression], concept(vol_simple), tout, oui, '3.1.6.2',
    "les vols simples").
exclusion([vol_batiment, vandalisme_vol, vol_annexes, remplacement_cles, vol_monde_sejour, vol_privilege_concierge, vol_privilege_jardin, vol_agression], et([f(vol_sur_personne, oui), f(lieu, voie_publique), non(f(violence, oui))]), tout, oui, '3.1.6.2',
    "les vols à la tire ou à la sauvette commis à l'extérieur du bâtiment désigné").
exclusion([vol_batiment, vandalisme_vol, vol_annexes, remplacement_cles, vol_monde_sejour, vol_privilege_concierge, vol_privilege_jardin, vol_agression], f(occupation_irreguliere, oui), tout, oui, '3.1.6.2',
    "les vols dans les locaux à occupation irrégulière").
exclusion([vol_batiment, vandalisme_vol, vol_annexes, remplacement_cles, vol_monde_sejour, vol_privilege_concierge, vol_privilege_jardin, vol_agression], ou([f(auteur, assure), f(auteur, famille), et([f(auteur, personnel_prive), ou([f(heures_service, oui), non(ou([f(effraction, oui), f(violence, oui)]))])])]), tout, oui, '3.1.6.2',
    "les vols commis par ou avec la complicité de ou du : n Preneur d'assurance, son conjoint, leurs ascendants ou descendants ainsi que les conjoints de ces personnes ; n l'Assuré ; n toute personne au service de l'Assuré pendant les heures de service et, si ces vols ont été commis en dehors de celles-ci, autrement que par effraction ou avec violence.").
exclusion([vol_batiment, vandalisme_vol, vol_annexes, remplacement_cles, vol_monde_sejour, vol_privilege_concierge, vol_privilege_jardin, vol_agression], f(bien, vehicule_moteur), bien(vehicule_moteur), non, '3.1.6.2',
    "les vols de véhicules automoteurs – à l'exception des engins de jardinage –, des remorques non enfermées dans le bâtiment désigné, ainsi que le vol de leurs accessoires et de leur contenu").
exclusion([vol_batiment, vandalisme_vol, vol_annexes, remplacement_cles, vol_monde_sejour, vol_privilege_concierge, vol_privilege_jardin, vol_agression], et([f(bien, remorque), non(ou([f(lieu, logement), f(lieu, cave), f(lieu, grenier), f(lieu, garage)]))]), bien(remorque), non, '3.1.6.2',
    "les vols de véhicules automoteurs – à l'exception des engins de jardinage –, des remorques non enfermées dans le bâtiment désigné, ainsi que le vol de leurs accessoires et de leur contenu").
exclusion([vol_batiment, vandalisme_vol, vol_annexes, remplacement_cles, vol_monde_sejour, vol_privilege_concierge, vol_privilege_jardin, vol_agression], et([ou([f(lieu, jardin), f(lieu, terrasse), f(lieu, parties_communes), et([ou([f(lieu, abri_jardin), f(lieu, annexe)]), f(serrure_cylindre, non)])]), non(ou([f(bien, mobilier_jardin), f(bien, plantation)])), non(f(lieu, logement))]), tout, oui, '3.1.6.2',
    "les vols des biens se trouvant à l'extérieur, dans les cours, les jardins -à l'exception du mobilier de jardin, de l'outillage motorisé ou non et des plantations situés à l'adresse du risque - dans les couloirs et passages d'accès, ainsi que dans les dépendances isolées ou contiguës avec ou sans communication intérieure avec la construction principale et non munies de serrure à cylindre").
exclusion([vol_batiment, vandalisme_vol, vol_annexes, remplacement_cles, vol_monde_sejour, vol_privilege_concierge, vol_privilege_jardin, vol_agression], et([f(occupation_partielle, oui), ou([f(lieu, parties_communes), f(lieu, garage), f(lieu, cave), f(lieu, grenier)]), f(serrure_surete, non)]), tout, oui, '3.1.6.2',
    "si l'Assuré n'occupe que partiellement le bâtiment désigné, le vol des biens se trouvant dans les parties communes et le contenu des garages, caves et greniers s'ils ne sont pas fermés par une serrure de sûreté").
exclusion([vol_batiment, vandalisme_vol, vol_annexes, remplacement_cles, vol_monde_sejour, vol_privilege_concierge, vol_privilege_jardin, vol_agression], f(bien, animal), bien(animal), oui, '3.1.6.2',
    "le vol des animaux").
exclusion([vol_batiment, vandalisme_vol, vol_annexes, remplacement_cles, vol_monde_sejour, vol_privilege_concierge, vol_privilege_jardin, vol_agression], et([f(travaux_construction, oui), non(f(lien_causal_travaux, non))]), tout, oui, '3.1.6.2',
    "les vols commis lorsque le bâtiment désigné est en cours de construction, de transformation ou de rénovation à moins que l'Assuré ne démontre que cette circonstance n'a pas contribué à la survenance ou à l'aggravation des conséquences du sinistre").
exclusion([vol_batiment, vandalisme_vol, vol_annexes, remplacement_cles, vol_monde_sejour, vol_privilege_concierge, vol_privilege_jardin, vol_agression], f(proprietaire, hote), tout, oui, '3.1.6.2',
    "le vol des biens dont l'Assuré n'est pas propriétaire").
exclusion([vol_batiment, vandalisme_vol, vol_annexes, remplacement_cles, vol_monde_sejour, vol_privilege_concierge, vol_privilege_jardin, vol_agression], f(abus_confiance, oui), tout, oui, '3.1.6.2',
    "l'abus de confiance").
