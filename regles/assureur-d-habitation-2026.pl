:- encoding(utf8).
/*  Règles du contrat Assureur D « Multirisque Habitation » (conditions générales, 04/2026).

    Troisième contrat du projet (DEMARCHE 7.87) : le même moteur (regles/moteur.pl) et le même vocabulaire de
    faits (regles/vocabulaire.json) que pour les assureurs A et B. Contrat français, en trois formules (Eco,
    Confort, Excellence), avec des packs et des garanties optionnels. Aucune règle n'est écrite à la main :
    chaque garantie est rédigée par Mistral Large (`couverture rediger --contrat assureur-d-habitation-2026
    --article 2.5`), contrôlée par le code, relue, puis ajoutée ici par `couverture rediger --accepter`.

    Tant qu'aucune garantie n'est ajoutée, aucun événement n'est traduit : le moteur ne conclut jamais à un
    refus, il répond « à examiner par un gestionnaire ».
*/

:- discontiguous definition/4, precision/3, garantie/4, perimetre/2, circonstance/4,
                 obligation/6, exclusion/6, limite/4, evenement_traduit/1, accessoire/1.

% --- Art. 1.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
definition(batiment, ou([f(lieu, logement), f(lieu, grenier), f(lieu, parties_communes), f(lieu, cave), f(lieu, garage), f(lieu, annexe), f(lieu, abri_jardin)]), '1.1-a',
    "votre local d’habitation, c’est-à-dire les parties immobilières des bâtiments principaux d’habitation destinées à un usage privé").
exclusion(tous, et([f(bien, veranda), non(f(option_veranda, oui))]), bien(veranda), non, '1.1-b',
    "les vérandas, sauf mention aux conditions particulières").
exclusion(tous, f(bien, eolienne), bien(eolienne), non, '1.1-b',
    "les éoliennes").
exclusion(tous, et([f(bien, panneau_solaire), non(f(formule, excellence))]), bien(panneau_solaire), non, '1.1-b',
    "les panneaux solaires et photovoltaïques si vous avez souscrit les formules Eco et Confort").
exclusion(tous, et([f(bien, piscine), non(f(pack_piscine, oui))]), bien(piscine), non, '1.1-b',
    "les piscines, spas et jacuzzi").
exclusion(tous, et([f(bien, plantation), non(f(pack_jardin, oui))]), bien(plantation), non, '1.1-b',
    "les plantations").
exclusion(tous, f(local_inoccupe_12_mois, oui), tout, non, '1.1-b',
    "les locaux inoccupés ou inutilisés depuis plus de 12 mois consécutifs").
% --- Art. 1.5 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
extension(batiment, et([f(sejour_temporaire, oui), f(lieu, autre_batiment), ou([f(bien, mobilier), f(bien, electronique), f(bien, objet_divers), f(bien, velo), f(bien, mobilier_jardin)]), non(ou([f(bien, bijoux), f(bien, valeurs)])), ou([f(pays, france), f(pays, belgique), f(pays, luxembourg), f(pays, allemagne), f(pays, autre_ue), f(pays, royaume_uni), f(pays, andorre), f(pays, monaco)])]), '1.5-a',
    "Les objets que vous emportez avec vous dans les différents locaux d’habitation, y compris les chambres d’hôtel, que vous occupez lors de voyages ou de vacances dans les pays de l’Union européenne, au Royaume-Uni de Grande-Bretagne et d’Irlande du Nord, dans les principautés d’Andorre et de Monaco").
% --- Art. 1.2 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
definition(contenu, et([ou([f(bien, mobilier), f(bien, electronique), f(bien, objet_divers), f(bien, velo), f(bien, bijoux), f(bien, valeurs), f(bien, mobilier_jardin)]), concept(batiment)]), '1.2-a',
    "Tous les objets d’usage courant et les vêtements vous appartenant ou qui vous sont confiés ou appartenant à toute personne résidant avec vous ou en simple visite, contenus à l’intérieur du local d’habitation et des dépendances assurés").
exclusion(tous, et([ou([f(lieu, cave), f(lieu, garage), f(lieu, annexe), f(lieu, abri_jardin)]), f(formule, eco)]), tout, non, '1.2-b',
    "les biens mobiliers se trouvant dans les dépendances si vous avez souscrit la formule Eco").
exclusion(tous, et([f(bien, bijoux), non(f(option_objets_valeur, oui))]), bien(bijoux), non, '1.2-b',
    "les objets précieux, les espèces, titres et valeurs, les objets de valeur désignés").
exclusion(tous, et([f(bien, valeurs), non(f(option_objets_valeur, oui))]), bien(valeurs), non, '1.2-b',
    "les objets précieux, les espèces, titres et valeurs, les objets de valeur désignés").
exclusion(tous, f(bien, vehicule_moteur), bien(vehicule_moteur), non, '1.2-b',
    "les véhicules terrestres à moteur (y compris les vélos électriques circulant à plus de 25 km/h et les engins de déplacement personnel motorisés), les remorques, les caravanes, les véhicules aériens").
exclusion(tous, f(bien, remorque), bien(remorque), non, '1.2-b',
    "les véhicules terrestres à moteur (y compris les vélos électriques circulant à plus de 25 km/h et les engins de déplacement personnel motorisés), les remorques, les caravanes, les véhicules aériens").
exclusion(tous, f(bien, animal), bien(animal), non, '1.2-b',
    "les animaux et les végétaux").
exclusion(tous, f(bien, plantation), bien(plantation), non, '1.2-b',
    "les animaux et les végétaux").
% --- Art. 2.3 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(tempete).
garantie(tempete_grele_neige, "Tempête, grêle, neige sur les toitures", '2.3-a',
    "La garantie couvre les dommages matériels causés aux biens assurés par l’action directe : • du vent ou du choc d’un objet renversé ou projeté par le vent (garantie tempête)").
perimetre(tempete_grele_neige, f(evenement, tempete)).
perimetre(tempete_grele_neige, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(tempete_grele_neige, concept(batiment)).
circonstance(tempete_grele_neige, si(f(alea_tempete, vent), ou([f(vent_dommages_voisins, oui), f(vent_100_kmh, oui)])), '2.3-a',
    "lorsque ces phénomènes ont une intensité telle qu’ils détruisent ou endommagent d’autres bâtiments de bonne construction dans le voisinage ou que leur caractère exceptionnel est attesté par un certificat de la station météorologique la plus proche (vitesse supérieure à 100 km/h dans le cas du vent)").
circonstance(tempete_grele_neige, si(f(alea_tempete, neige_glace), ou([f(neige_dommages_voisins, oui), f(certificat_meteo, oui)])), '2.3-a',
    "lorsque ces phénomènes ont une intensité telle qu’ils détruisent ou endommagent d’autres bâtiments de bonne construction dans le voisinage ou que leur caractère exceptionnel est attesté par un certificat de la station météorologique la plus proche (vitesse supérieure à 100 km/h dans le cas du vent)").
exclusion(tempete_grele_neige, et([f(alea_tempete, vent), f(construction_close, non)]), tout, oui, '2.3-b',
    "les dommages occasionnés par le vent aux bâtiments dont les éléments porteurs ne sont pas ancrés, à ceux qui ne sont pas construits selon les règles de l’art ou qui ne sont pas entièrement clos et couverts, ainsi qu’à leur contenu").
exclusion(tempete_grele_neige, et([ou([f(lieu, jardin), f(lieu, terrasse)]), non(et([f(bien, mobilier_jardin), f(pack_jardin, oui)]))]), tout, oui, '2.3-b',
    "les objets en plein air, sauf pour le mobilier de jardin assuré dans le Pack Jardin s’il est souscrit").

% --- Art. 2.4 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(degat_eaux).
evenement_traduit(mazout).
garantie(venues_eau_gel, "Venues d'eau et gel", '2.4-a',
    "La garantie couvre les dommages résultant : • d’eaux de ruissellement à la surface du sol, • du refoulement des égouts, • d’infiltrations par les toitures").
perimetre(venues_eau_gel, f(evenement, degat_eaux)).
perimetre(venues_eau_gel, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(venues_eau_gel, concept(batiment)).
circonstance(venues_eau_gel, ou([f(cause_eau, inondation), f(cause_eau, infiltration_toiture), f(cause_eau, infiltration_exterieure), f(cause_eau, fuite_installation), f(cause_eau, gel), f(cause_eau, piscine_exterieure), f(cause_eau, debordement_recipient), f(cause_eau, debordement_aquarium)]), '2.4-a',
    "La garantie couvre les dommages résultant : • d’eaux de ruissellement à la surface du sol…• de débordements et renversements de récipients ou d’aquariums").
exclusion(venues_eau_gel, et([f(cause_eau, fuite_installation), f(canalisation_enterree, oui)]), tout, non, '2.4-c',
    "les dommages consécutifs à des fuites d’eau ou débordements provenant des canalisations enterrées").
exclusion(venues_eau_gel, et([f(bien, canalisation), f(canalisation_enterree, oui)]), bien(canalisation), non, '2.4-c',
    "les dommages sur les canalisations enterrées").
exclusion(venues_eau_gel, et([f(cause_eau, infiltration_exterieure), f(batiment_moins_10_ans, oui)]), tout, oui, '2.4-c',
    "les dommages résultant d’infiltrations à travers les murs et façades extérieurs lorsque la garantie décennale du constructeur doit s’appliquer").
exclusion(venues_eau_gel, f(evenement, catastrophe_naturelle), tout, non, '2.4-c',
    "les dommages relevant de la garantie Catastrophes naturelles").
exclusion(venues_eau_gel, f(cause_eau, condensation), tout, non, '2.4-c',
    "les dommages dus à l’humidité et/ou à la condensation").
garantie(recherche_fuite, "Recherche de fuite", '2.4-a',
    "Sont prises en charge au titre de la recherche de fuite").
perimetre(recherche_fuite, f(evenement, degat_eaux)).
perimetre(recherche_fuite, concept(batiment)).
garantie(debordement_cuves, "Débordement des cuves de combustible (Excellence)", '2.4-b',
    "les dommages résultant du débordement accidentel des cuves situées à l’intérieur des bâtiments principaux d’habitation et de leurs dépendances et contenant le combustible nécessaire à l’alimentation du chauffage").
perimetre(debordement_cuves, f(evenement, mazout)).
perimetre(debordement_cuves, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(debordement_cuves, concept(batiment)).
circonstance(debordement_cuves, f(formule, excellence), '2.4-b',
    "Sont également garantis : • les dommages résultant du débordement accidentel des cuves").
exclusion(debordement_cuves, f(bien, mazout), bien(mazout), non, '2.4-c',
    "le coût du combustible perdu, en cas de débordement accidentel des cuves").
accessoire(recherche_fuite).

% --- Art. 2.5 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(vol).
evenement_traduit(vandalisme).
garantie(vol_vandalisme, "Vol, tentative de vol, vandalisme", '2.5-a',
    "La garantie couvre la disparition, la destruction ou la détérioration des biens assurés résultant : • d’un vol, • d’une tentative de vol, • d ’un acte de vandalisme ou de sabotage").
perimetre(vol_vandalisme, ou([f(evenement, vol), f(evenement, vandalisme)])).
perimetre(vol_vandalisme, concept(contenu)).
perimetre(vol_vandalisme, concept(batiment)).
circonstance(vol_vandalisme, ou([f(effraction, oui), f(acces_voleur, escalade), f(acces_voleur, menaces), f(acces_voleur, cles_volees), f(acces_voleur, fausse_qualite)]), '2.5-a',
    "lorsque ces méfaits sont commis à l’intérieur des locaux assurés, par effraction ou escalade de ces locaux…au vol dans les locaux assurés par menaces physiques…au vol à la suite du vol des clés…au vol à la suite d’une introduction par fausse qualité").
exclusion(vol_vandalisme, et([ou([f(auteur, famille), f(auteur, personnel_prive)]), non(f(plainte_deposee, oui))]), tout, oui, '2.5-c',
    "les vols, tentatives de vol, actes de vandalisme ou actes de sabotage dont seraient auteurs ou complices les membres de votre famille (article 311-12 du Code pénal) ou vos préposés pendant leur service, sauf si une plainte nominative est déposée à leur encontre").
exclusion(vol_vandalisme, f(cles_deposees_exterieur, oui), tout, non, '2.5-c',
    "les vols des clés déposées, sans protection, à l’extérieur des locaux y compris dans une boîte à clé ou dans une boîte à lettres ainsi que toutes leurs conséquences").
exclusion(vol_vandalisme, et([f(bien, bijoux), ou([f(lieu, cave), f(lieu, garage), f(lieu, annexe), f(lieu, abri_jardin)])]), bien(bijoux), non, '2.5-c',
    "l es vols des objets précieux dans les dépendances").
exclusion(vol_vandalisme, et([f(bien, valeurs), ou([f(lieu, cave), f(lieu, garage), f(lieu, annexe), f(lieu, abri_jardin)])]), bien(valeurs), non, '2.5-c',
    "l es vols des objets précieux dans les dépendances").
exclusion(vol_vandalisme, et([ou([f(lieu, cave), f(lieu, garage), f(lieu, annexe), f(lieu, abri_jardin)]), f(formule, eco)]), tout, oui, '2.5-c',
    "les vols dans les dépendances, si vous avez souscrit la formule Eco").
exclusion(vol_vandalisme, f(construction_close, non), tout, non, '2.5-c',
    "les vols, tentatives de vol, actes de vandalisme ou actes de sabotage commis sur les terrasses, les balcons, dans les jardins et dans les locaux non entièrement clos ou couverts").
garantie(vol_cles, "Vol des clés (Confort et Excellence)", '2.5-a',
    "au vol des clés, en tous lieux de l’Union européenne, du Royaume-Uni de Grande-Bretagne et d’Irlande du Nord, de votre local d’habitation et/ou des dépendances assurés dès lors que le dépôt de plainte fait état d’un vol").
perimetre(vol_cles, f(evenement, vol)).
perimetre(vol_cles, f(bien, cles)).
circonstance(vol_cles, f(plainte_deposee, oui), '2.5-a',
    "dès lors que le dépôt de plainte fait état d’un vol").
circonstance(vol_cles, ou([f(formule, confort), f(formule, excellence)]), '2.5-a',
    "Extensions de garantie pour les formules Confort et Excellence").
exclusion(vol_cles, f(cles_deposees_exterieur, oui), tout, non, '2.5-c',
    "les vols des clés déposées, sans protection, à l’extérieur des locaux y compris dans une boîte à clé ou dans une boîte à lettres").

% --- Art. 2.6 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(vandalisme).
evenement_traduit(vol).
garantie(deteriorations_immobilieres, "Détériorations immobilières", '2.6-a',
    "La garantie couvre la détérioration de : - vos biens immobiliers…à la suite d’un acte de vandalisme, d’une tentative de vol ou d’un vol").
perimetre(deteriorations_immobilieres, ou([f(evenement, vandalisme), f(evenement, vol)])).
perimetre(deteriorations_immobilieres, f(bien, element_batiment)).
perimetre(deteriorations_immobilieres, concept(batiment)).
circonstance(deteriorations_immobilieres, si(ou([f(lieu, logement), f(lieu, grenier), f(lieu, cave), f(lieu, garage), f(lieu, annexe), f(lieu, abri_jardin)]), ou([f(effraction, oui), f(acces_voleur, escalade), f(acces_voleur, menaces), f(acces_voleur, cles_volees), f(acces_voleur, fausse_qualite)])), '2.6-a',
    "Si les dommages sont commis à l’intérieur de votre habitation ou de ses dépendances, les détériorations doivent être commises à la suite : - de l’effraction ou de l’escalade des locaux assurés, ayant laissé des traces apparentes, - de menaces physiques ou violences physiques, - du vol des clés, - de l’introduction par fausse qualité").
exclusion(deteriorations_immobilieres, et([ou([f(auteur, famille), f(auteur, personnel_prive)]), non(f(plainte_deposee, oui))]), tout, oui, '2.6-b',
    "les vols, tentatives de vol ou actes de vandalisme dont seraient auteurs ou complices les membres de votre famille (article 311-12 du Code pénal) ou vos préposés pendant leur service, sauf si une plainte nominative est déposée à leur encontre").
exclusion(deteriorations_immobilieres, f(graffiti_mur_exterieur, oui), tout, oui, '2.6-b',
    "les graffitis, tags, pochoirs et inscriptions de toute nature, affichages, salissures, rayures commis à l’extérieur de votre local d’habitation et de ses dépendances").

% --- Art. 2.7 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(bris).
garantie(bris_glaces, "Bris de glaces", '2.7-a',
    "La garantie couvre, lorsqu’ils sont brisés accidentellement, les frais de remplacement : • des miroirs intérieurs, des glaces équipant les meubles et les aquariums, • des vitrages des portes, portes-fenêtres, baies et fenêtres, y compris en toiture").
perimetre(bris_glaces, f(evenement, bris)).
perimetre(bris_glaces, ou([f(bien, vitre), f(bien, miroir), f(bien, verre_meuble), f(bien, panneau_verre_plastique), f(bien, serre)])).
perimetre(bris_glaces, concept(batiment)).
garantie(bris_glace_plus, "Bris de glace + (Confort et Excellence)", '2.7-a',
    "La garantie est étendue pour les formules Confort et Excellence aux : • plaques vitrocéramiques, plaques induction, • vérandas ou loggias (si l’option est souscrite), • vitraux, marquises, • appareils sanitaires").
perimetre(bris_glace_plus, f(evenement, bris)).
perimetre(bris_glace_plus, ou([f(bien, table_cuisson_vitroceramique), f(bien, sanitaire), f(bien, veranda)])).
perimetre(bris_glace_plus, concept(batiment)).
circonstance(bris_glace_plus, ou([f(formule, confort), f(formule, excellence)]), '2.7-a',
    "La garantie est étendue pour les formules Confort et Excellence aux").
garantie(bris_glace_renforce, "Bris de glace renforcé (Excellence)", '2.7-a',
    "La garantie est étendue pour la formule Excellence aux survitrages mobiles, vitres d’insert, vitres d’appareils électroménagers, ainsi que les panneaux solaires et photovoltaïques").
perimetre(bris_glace_renforce, f(evenement, bris)).
perimetre(bris_glace_renforce, ou([f(bien, appareil_electromenager), f(bien, panneau_solaire)])).
perimetre(bris_glace_renforce, concept(batiment)).
circonstance(bris_glace_renforce, f(formule, excellence), '2.7-a',
    "La garantie est étendue pour la formule Excellence aux").
exclusion([bris_glaces, bris_glace_plus, bris_glace_renforce], et([f(bien, appareil_electromenager), non(f(formule, excellence))]), bien(appareil_electromenager), non, '2.7-b',
    "les appareils électroménagers, sauf ceux garantis dans le « Bris de glace renforcé » ci-dessus").

% --- Art. 2.8 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(electricite).
garantie(contenu_congelateur, "Contenu du congélateur et/ou réfrigérateur", '2.8-b',
    "La garantie couvre les pertes ou détériorations causes aux denrées alimentaires contenues dans les congélateurs et/ou réfrigérateurs endommagés").
perimetre(contenu_congelateur, f(evenement, electricite)).
perimetre(contenu_congelateur, f(bien, denrees_alimentaires)).
perimetre(contenu_congelateur, concept(batiment)).
circonstance(contenu_congelateur, f(formule, excellence), '2.8-b',
    "La garantie couvre les pertes ou détériorations causes aux denrées alimentaires").
circonstance(contenu_congelateur, ou([f(cause_perte_alimentaire, coupure_soudaine_reseau), f(cause_perte_alimentaire, derangement_installation)]), '2.8-b',
    "à l’occasion d’un sinistre dommages électrique indemnisé (ART 2-2), à la suite d’un sinistre indemnisé au titre de la garantie panne électroménager (TITRE III) ou d’une coupure électrique accidentelle avec justificatif de votre fournisseur d’électricité").
exclusion(contenu_congelateur, f(manque_entretien, oui), tout, non, '2.8-c',
    "dues à un mauvais entretien ou à une utilisation non conforme du congélateur et/ou réfrigérateur aux instructions du fabricant").

% --- Art. 2.9 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(catastrophe_naturelle).
garantie(catastrophes_naturelles, "Catastrophes naturelles", '2.9-a',
    "La garantie couvre les dommages matériels directs non assurables ayant eu pour cause déterminante l’intensité anormale d’un agent naturel").
perimetre(catastrophes_naturelles, f(evenement, catastrophe_naturelle)).
perimetre(catastrophes_naturelles, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(catastrophes_naturelles, concept(batiment)).
circonstance(catastrophes_naturelles, f(arrete_catnat_30j, oui), '2.9-a',
    "La garantie est mise en jeu par une déclaration faite au plus tard trente jours après publication au Journal Officiel d’un arrêté interministériel constatant l’état de catastrophe naturelle").
exclusion(catastrophes_naturelles, f(terrain_non_constructible, oui), tout, non, '2.9-b',
    "les biens assurés construits sur des terrains classés inconstructibles par un plan de prévention des risques à l’exception toutefois des biens existants antérieurement à la publication de ce plan").
garantie(relogement_catnat, "Relogement d'urgence après une catastrophe naturelle", '2.9-a',
    "les frais de relogement d’urgence des personnes sinistrées dont la résidence principale est rendue impropre à l’habitation").
perimetre(relogement_catnat, f(evenement, catastrophe_naturelle)).
perimetre(relogement_catnat, f(residence_principale_inhabitable, oui)).
accessoire(relogement_catnat).

% --- Art. 2.11 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(attentat).
garantie(attentats, "Attentats et actes de terrorisme", '2.11-a',
    "La garantie couvre les dommages matériels directs (y compris les frais de décontamination), subis sur le territoire national, causés aux biens assurés par un attentat ou un acte de terrorisme").
perimetre(attentats, f(evenement, attentat)).
perimetre(attentats, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(attentats, concept(batiment)).
exclusion([attentats], faux, tout, non, '2.11-b',
    "les frais de décontamination des déblais ainsi que leur confinement").

% --- Art. 2.12 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(attentat).
garantie(emeutes, "Émeutes et mouvements populaires", '2.12-a',
    "La garantie couvre, dans les conditions et limites prévues pour chaque garantie si elle est souscrite, les dommages matériels causés aux biens assurés survenant lors d’émeutes ou de mouvements populaires").
perimetre(emeutes, f(evenement, attentat)).
perimetre(emeutes, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(emeutes, concept(batiment)).

% --- Art. 2.13 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
garantie(intervention_secours, "Intervention des moyens de secours", '2.13-a',
    "La garantie couvre les dommages matériels occasionnés par l’intervention des services de secours à proximité des locaux assurés").
perimetre(intervention_secours, concept(batiment)).
accessoire(intervention_secours).

% --- Art. 2.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(incendie).
evenement_traduit(explosion).
evenement_traduit(fumee).
evenement_traduit(foudre).
evenement_traduit(heurt).
garantie(incendie_evenements_annexes, "Incendie, explosion, enfumage, foudre, choc d'un véhicule", '2.1-a',
    "La garantie couvre les dommages matériels causés par : • l ’incendie, c’est-à-dire la combustion avec flammes en dehors d’un foyer normal…• l ’explosion…• l’enfumage accidentel…• la chute de la foudre…• le choc d’un véhicule").
perimetre(incendie_evenements_annexes, ou([f(evenement, incendie), f(evenement, explosion), f(evenement, fumee), f(evenement, foudre), f(evenement, heurt)])).
perimetre(incendie_evenements_annexes, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(incendie_evenements_annexes, concept(batiment)).
circonstance(incendie_evenements_annexes, si(f(evenement, heurt), ou([f(vehicule_identifie, oui), f(plainte_deposee, oui)])), '2.1-a',
    "Le véhicule doit être identifié, sinon vous devez déposer une plainte auprès des autorités.").
exclusion(incendie_evenements_annexes, et([f(evenement, incendie), f(chaleur_sans_feu, oui)]), tout, non, '2.1-a',
    "l ’incendie, c’est-à-dire la combustion avec flammes en dehors d’un foyer normal").
exclusion(incendie_evenements_annexes, et([f(evenement, heurt), ou([f(auteur, assure), f(auteur, famille)])]), tout, non, '2.1-a',
    "le choc d’un véhicule dont ni vous, ni votre conjoint ou concubin, ni vos enfants, n’avez la propriété, la conduite ou la garde").
exclusion(incendie_evenements_annexes, et([ou([f(evenement, incendie), f(evenement, explosion)]), f(bien_a_l_origine_sinistre, oui), ou([f(bien, electronique), f(bien, appareil_electromenager)])]), bien(electronique), non, '2.1-b',
    "les dommages aux appareils électriques ou électroniques qui ont pour origine l’incendie ou l’explosion prenant naissance dans l’appareil").
exclusion(incendie_evenements_annexes, et([f(evenement, foudre), f(evenement, electricite), ou([f(bien, electronique), f(bien, appareil_electromenager)])]), bien(electronique), non, '2.1-a',
    "la chute de la foudre, c’est-à-dire du fait de l’ébranlement ou de la calcination causés directement par l’impact de la foudre").
exclusion(incendie_evenements_annexes, et([f(evenement, fumee), f(cheminee_ouverte, oui)]), tout, non, '2.1-b',
    "la fumée provenant de cheminées à feu apparent (dits « à l’ouvert »)").
% --- Art. 2.2 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(electricite).
garantie(dommages_electriques, "Dommages électriques (Confort et Excellence)", '2.2-a',
    "La garantie couvre les dommages matériels causés par les effets d’une surtension, d’une sous-tension ou d’une surintensité accidentelle, y compris du fait de la foudre, aux installations ou aux appareils électriques").
perimetre(dommages_electriques, f(evenement, electricite)).
perimetre(dommages_electriques, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(dommages_electriques, concept(batiment)).
circonstance(dommages_electriques, ou([f(formule, confort), f(formule, excellence)]), '2.2',
    "Cette garantie est acquise uniquement pour les formules Confort et Excellence").
exclusion(dommages_electriques, f(bien, consommable), bien(consommable), non, '2.2-b',
    "les résistances chauffantes, les fusibles, les disjoncteurs, les lampes éclairantes, les transformateurs").
exclusion(dommages_electriques, f(bien, denrees_alimentaires), bien(denrees_alimentaires), non, '2.2-b',
    "le contenu des appareils endommagés").
exclusion(dommages_electriques, f(garantie_fabricant, oui), tout, oui, '2.2-b',
    "les dommages sous garantie ou faisant l’objet d’un contrat de maintenance").
limite(dommages_electriques, '2.2-a', "L’indemnisation est égale au coût de réparation ou de remplacement du sous-ensemble endommagé, dans la limite de la valeur de remplacement, vétusté déduite au taux de 1 % par mois, du bien mobilier endommagé, avec un maximum de 80 %", "vétusté 1 % par mois, au plus 80 %").

% --- Art. S25 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
exclusion(tous, ou([et([f(intentionnel, oui), non(f(auteur, tiers))]), et([f(participation_rixe, oui), non(f(legitime_defense, oui))])]), tout, non, 'S25',
    "les dommages causés intentionnellement ou frauduleusement par vous ou par un complice, ou résultant de votre ou de sa participation à une action violente ou à une rixe (sauf légitime défense)").
exclusion(tous, et([f(manque_entretien, oui), ou([non(f(evenement, degat_eaux)), non(f(cause_eau, gel))])]), tout, oui, 'S25',
    "ceux qui résultent directement d’un défaut de réparation ou d’entretien indispensables vous incombant et dont vous aviez connaissance").
exclusion(tous, et([ou([f(cause_guerre, oui), f(cause_nucleaire, oui)]), non(f(evenement, attentat))]), tout, non, 'S25',
    "de la guerre civile ou étrangère, - de tout combustible, produit ou déchet radioactif, de tout engin destiné à irradier ou à exploser par modification du noyau de l’atome ainsi que leur décontamination, sauf pour les dommages matériels directs causés par un attentat ou un acte de terrorisme").
