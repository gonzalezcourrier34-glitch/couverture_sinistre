:- encoding(utf8).
/*  Règles du contrat Foyer « appart 123 » (2025) : vol (art. 2.10), incendie (art. 2.1),
    dégâts des eaux (art. 2.7), et les définitions de l'art. 12 qu'elles emploient.
    Les autres garanties (tempête, bris de vitrages…) ne sont pas encore traduites : voir evenement_traduit.

    Écrites à la main, pour servir de modèle avant de les faire écrire par un modèle de langage.
    Chaque règle garde, mot pour mot, la phrase du contrat qu'elle traduit : `couverture regles`
    vérifie que chaque citation figure dans la clause citée, et que chaque variable appartient
    au vocabulaire commun (regles/vocabulaire.json). Le moteur est dans regles/moteur.pl.

    Deux formes du contrat que les fiches ne savaient pas représenter (voir docs/DEMARCHE.md) :
      - une condition cachée dans le tableau des limites : la cave n'est couverte que « si ces
        locaux sont fermés avec une serrure de sûreté », et la serrure de sûreté exclut le cadenas ;
      - une exclusion cachée dans une définition : le contenu « ne comprend pas … le contenu du jardin ».
*/

:- discontiguous definition/4, precision/3, garantie/4, perimetre/2, circonstance/4,
                 obligation/6, exclusion/6, limite/4, evenement_traduit/1.

%  Les événements dont les garanties sont traduites ici. Un autre événement déclaré (tempête, bris de
%  vitrage…) relève d'une garantie qui n'est pas encore en règles : le moteur ne conclut alors pas
%  à un refus (au plus INCERTAIN). C'est ce qui garde vrai le « je ne sais pas » d'un contrat
%  partiellement traduit (docs/DEMARCHE.md, 7.17).
evenement_traduit(vol).
evenement_traduit(incendie).
evenement_traduit(explosion).
evenement_traduit(foudre).
evenement_traduit(degat_eaux).
evenement_traduit(fumee).

% --- Définitions (art. 12) -----------------------------------------------------------------------

definition(vol, f(evenement, vol), '12/vol',
    "Par vol, on entend le fait pour une personne de soustraire frauduleusement une chose qui ne lui appartient pas").

definition(contenu,
    et([ ou([f(bien, velo), f(bien, mobilier), f(bien, electronique), f(bien, bijoux),
             f(bien, valeurs), f(bien, objet_divers), f(bien, animal)]),
         non(f(bien, vehicule_moteur)),
         non(f(bien, mobilier_jardin)),
         non(f(lieu, jardin)) ]),
    '12/contenu',
    "Il s’agit des biens meubles qui se trouvent dans le bâtiment et qui vous appartiennent ou vous sont confiés").
precision(contenu, '12/contenu',
    "les véhicules automoteurs d'une cylindrée supérieure à 50 cc ou dont la vitesse excède 45 km/h").
precision(contenu, '12/contenu', "le contenu du jardin").

definition(batiment,
    ou([f(lieu, logement), f(lieu, cave), f(lieu, grenier), f(lieu, garage), f(lieu, annexe),
        f(lieu, terrasse), f(lieu, parties_communes)]),
    '12/batiment',
    "Il s’agit des constructions, séparées ou non, situées à l’adresse indiquée aux conditions particulières").
precision(batiment, '12/batiment', "les garages ou carports").
precision(batiment, '12/batiment', "les terrasses contigües").

definition(serrure_de_surete,
    et([f(serrure_surete, oui), non(f(fermeture, cadenas)), non(f(fermeture, aucune))]),
    '12/serrure-de-surete',
    "une serrure à double tour comportant un mécanisme à cylindre ou à pompe, sauf cadenas").

%  2.1 couvre aussi la suie et la fumée, sans incendie (la casserole qui noircit la cuisine).
definition(fumee, f(evenement, fumee), '2.1', "Le dégagement de suie et de fumée").

definition(incendie, et([f(flammes, oui), f(embrasement, oui)]), '12/incendie',
    "La destruction de biens par des flammes évoluant hors de leur domaine normal et créant de la sorte un embrasement susceptible de se propager à d’autres biens").
precision(incendie, '12/incendie', "sans qu’il y ait embrasement").

% --- Art. 2.10 Garantie vol ------------------------------------------------------------------------

garantie(vol_batiment, "Vol du contenu dans le bâtiment", '2.10',
    "le vol du contenu situé dans le bâtiment sauf la simple disparition").
perimetre(vol_batiment, concept(vol)).
perimetre(vol_batiment, concept(contenu)).
perimetre(vol_batiment, concept(batiment)).
%  Cachées dans le tableau des limites : des conditions, pas seulement des plafonds.
circonstance(vol_batiment, si(ou([f(lieu, cave), f(lieu, grenier)]), concept(serrure_de_surete)), '2.10',
    "si ces locaux sont fermés avec une serrure de sûreté").
circonstance(vol_batiment, si(ou([f(lieu, garage), f(lieu, annexe)]), concept(serrure_de_surete)), '2.10',
    "si ces locaux sont fermés par une serrure de sûreté").
obligation(vol_batiment, si(f(absence, oui), f(portes_fermees, oui)), f(effraction, oui), oui, '2.10',
    "en cas d’absence, fermer à clé ou au moyen d'un dispositif électronique toutes les portes extérieures du bâtiment").
obligation(vol_batiment, si(f(absence, oui), f(fenetres_fermees, oui)), f(effraction, oui), oui, '2.10',
    "Vous devez de même fermer correctement les fenêtres, oscillo-battants, soupiraux et autres ouvertures du bâtiment facilement accessibles").
obligation(vol_batiment, non(f(cles_a_proximite, oui)), f(effraction, oui), oui, '2.10',
    "ne pas laisser les clés d'accès aux locaux à proximité de ceux-ci").
exclusion(vol_batiment, f(simple_disparition, oui), tout, non, '2.10',
    "le vol du contenu situé dans le bâtiment sauf la simple disparition").
limite(vol_batiment, '2.10',
    "Les limites d’indemnisation pour le vol du contenu dépendent du nombre de chambres", "17 500 à 37 500 EUR").
limite(vol_batiment, '2.10', "si ces locaux sont fermés avec une serrure de sûreté", "caves et greniers : 1 000 EUR").

garantie(vol_personne, "Vol commis sur l’assuré avec violences", '2.10',
    "le vol commis sur l’assuré, en dehors des biens assurés, suite à violences physiques et/ou menaces").
perimetre(vol_personne, concept(vol)).
perimetre(vol_personne, f(vol_sur_personne, oui)).
%  « en dehors des biens assurés » : un vol au bâtiment (garage, terrasse…) n'est pas un vol sur la personne.
perimetre(vol_personne, non(concept(batiment))).
circonstance(vol_personne, f(violence, oui), '2.10', "suite à violences physiques et/ou menaces").
limite(vol_personne, '2.10',
    "Le vol commis sur l’assuré, avec violence et/ou menaces, en dehors des biens assurés", "2 500 EUR").

garantie(vol_reparateur, "Vol du contenu chez un réparateur", '2.10',
    "le vol du contenu déposé chez un réparateur pendant max. 30 jours").
perimetre(vol_reparateur, concept(vol)).
perimetre(vol_reparateur, f(lieu, chez_reparateur)).
circonstance(vol_reparateur, f(depot_moins_30j, oui), '2.10', "pendant max. 30 jours").
limite(vol_reparateur, '2.10', "Le vol du contenu déposé chez un réparateur pendant maximum 30 jours", "500 EUR").

%  Le tableau des limites cache une garantie : les clés volées, où que ce soit. La perte n'est pas
%  un événement du vocabulaire : « perdu » n'est pas « volé », la rattacher ici ferait de chaque
%  déclaration au bien inconnu un vol de clés possible.
garantie(vol_cles, "Vol ou perte des clés", '2.10', "Le vol ou la perte des clés").
perimetre(vol_cles, concept(vol)).
perimetre(vol_cles, f(bien, cles)).
limite(vol_cles, '2.10', "Le vol ou la perte des clés", "500 EUR").

% --- Art. 2.10-a Exclusions du vol (communes aux trois garanties vol) ---------------------------------

exclusion([vol_batiment, vol_personne, vol_reparateur, vol_cles], f(lieu, parties_communes), tout, oui, '2.10-a',
    "le vol ou le vandalisme dans les parties communes du bâtiment").
exclusion([vol_batiment, vol_personne, vol_reparateur, vol_cles], ou([f(auteur, assure), f(auteur, famille)]), tout, non, '2.10-a',
    "le vol et le vandalisme commis par ou avec votre complicité ou celle d’un descendant ou ascendant").
exclusion([vol_batiment, vol_personne, vol_reparateur, vol_cles], f(auteur, personnel_prive), tout, non, '2.10-a',
    "le vol commis par des personnes au service privé de l’assuré").
exclusion([vol_batiment, vol_personne, vol_reparateur, vol_cles], f(proprietaire, hote), tout, non, '2.10-a',
    "le vol des biens appartenant à des hôtes").
exclusion([vol_batiment, vol_personne, vol_reparateur, vol_cles], f(bien, animal), bien(animal), oui, '2.10-a',
    "le vol des animaux").
exclusion([vol_batiment, vol_personne, vol_reparateur, vol_cles], f(bien, mobilier_jardin), bien(mobilier_jardin), oui, '2.10-a',
    "le vol du mobilier extérieur").
exclusion([vol_batiment, vol_personne, vol_reparateur, vol_cles], f(bien, plantation), bien(plantation), oui, '2.10-a',
    "le vol des plantations du jardin").
exclusion([vol_batiment, vol_personne, vol_reparateur, vol_cles], f(bien, mazout), bien(mazout), oui, '2.10-a',
    "le vol de mazout de chauffage").
exclusion([vol_batiment, vol_personne, vol_reparateur, vol_cles], f(lieu, casier), tout, non, '2.10-a',
    "le vol du contenu entreposé dans un casier d’une association sportive ou d’agrément").

% --- Art. 2.1 Incendie et risques connexes -------------------------------------------------------------

garantie(incendie, "Incendie et risques connexes", '2.1',
    "Nous couvrons les dommages matériels directement causés par").
perimetre(incendie, ou([concept(incendie), f(evenement, explosion), f(evenement, foudre), concept(fumee)])).
%  La garantie ne se rattache qu'aux événements qu'elle couvre : pas de question sur les flammes pour une tempête.
perimetre(incendie, ou([f(evenement, incendie), f(evenement, explosion), f(evenement, foudre), f(evenement, fumee)])).
perimetre(incendie, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(incendie, concept(batiment)).
exclusion(incendie, f(chaleur_sans_feu, oui), tout, non, '2.1',
    "suite à l’action subite de la chaleur sans contact direct avec le feu").

% --- Art. 2.7 Dégâts causés par l'eau ----------------------------------------------------------------

garantie(degats_eaux, "Dégâts causés par l’eau", '2.7', "Nous couvrons l’ensemble des dommages causés par l’eau").
perimetre(degats_eaux, f(evenement, degat_eaux)).
perimetre(degats_eaux, ou([concept(contenu), f(bien, element_batiment), f(bien, canalisation)])).
perimetre(degats_eaux, concept(batiment)).
%  N'exclut que la canalisation à l'origine : le parquet et le canapé restent couverts.
exclusion(degats_eaux, f(bien, canalisation), bien(canalisation), oui, '2.7-b',
    "aux canalisations, radiateurs, robinets, citernes, chaudières et autres appareils chauffant de l'eau, qui sont à l'origine du sinistre").
exclusion(degats_eaux, f(cause_eau, infiltration_exterieure), tout, oui, '2.7-b',
    "par une infiltration par les terrasses, balcons, portes, fenêtres et porte-fenêtre ou par les murs extérieurs").
exclusion(degats_eaux, f(cause_eau, eau_souterraine), tout, oui, '2.7-b',
    "par une infiltration d’eau souterraine").
exclusion(degats_eaux, f(cause_eau, piscine_exterieure), tout, oui, '2.7-b',
    "par l'écoulement d'eau des piscines et des bains à bulles extérieurs").
%  Inconnue, la corrosion n'est pas une question à poser : c'est à l'assureur de la prouver.
exclusion(degats_eaux, f(corrosion_visible, oui), tout, non, '2.7-b',
    "par les canalisations apparentes présentant plusieurs points de corrosion visibles et non traités").
exclusion(degats_eaux, f(cause_eau, inondation), tout, oui, '2.7-b',
    "par une inondation ou un débordement ou refoulement d'égouts publics").
exclusion(degats_eaux, f(cause_eau, condensation), tout, non, '2.7-b', "par la condensation").
%  « infiltration_exterieure » ne vise que terrasses, balcons, portes, fenêtres et murs :
%  la pluie entrée par le toit (infiltration_toiture) reste couverte.
%  L'aquarium et le matelas d'eau sont exceptés : une autre valeur du vocabulaire (debordement_aquarium).
exclusion(degats_eaux, f(cause_eau, debordement_recipient), tout, oui, '2.7-b',
    "par le débordement ou le renversement d'un récipient non relié à l'installation hydraulique du bâtiment, autre qu’un aquarium ou un matelas d’eau").
%  Le gel est exclu sauf si les mesures de prévention ont été respectées ; inconnues, c'est une réserve.
exclusion(degats_eaux, et([f(cause_eau, gel), f(prevention_gel, non)]), tout, oui, '2.7-b',
    "par le gel, néanmoins, les dégâts qui résultent de l'écoulement d'eau consécutif au gel sont couverts lorsque les mesures de prévention reprises ci-dessous ont été respectées").

% --- Art. 2.9 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-17 ---
evenement_traduit(bris).
definition(vitrage_assure, ou([f(bien, vitre), f(bien, miroir), f(bien, coupole), f(bien, panneau_verre_plastique), f(bien, table_cuisson_vitroceramique), f(bien, panneau_solaire), f(bien, mur_rideau), f(bien, sanitaire), f(bien, verre_meuble)]), '2.9',
    "Nous assurons le bris et la fêlure de vitres, y compris le bris des biens suivants (assimilés aux vitres) : les miroirs, les coupoles, panneaux ou enseignes en verre ou en plastique, les tables de cuisson en vitrocéramique, les panneaux solaires fixés au bâtiment, les murs rideaux, les sanitaires et le verre intégré dans des meubles").
definition(sanitaire, f(bien, sanitaire), '12/sanitaires',
    "Les éviers, lavabos, baignoires, pédiluves, douches, toilettes et bidets, saunas, hammams et bains à bulles intérieurs").
garantie(bris_vitrages, "Bris et fêlure de vitrages", '2.9',
    "Nous assurons le bris et la fêlure de vitres, y compris le bris des biens suivants (assimilés aux vitres)").
perimetre(bris_vitrages, f(evenement, bris)).
perimetre(bris_vitrages, ou([concept(vitrage_assure), f(bien, cadre), f(bien, chassis), f(bien, soubassement)])).
exclusion(bris_vitrages, f(travaux_batiment, autres_que_entretien_reparation), tout, oui, '2.9-a',
    "les dommages causés par les travaux au bâtiment autres que d’entretien et de réparation").
exclusion(bris_vitrages, f(travaux_vitres, autres_que_nettoyage), tout, oui, '2.9-a',
    "les dommages causés par les travaux (nettoyage excepté) aux vitres, châssis et biens assimilés").
exclusion(bris_vitrages, f(bien, appareil_audiovisuel), bien(appareil_audiovisuel), oui, '2.9-a',
    "les parties vitrées des appareils audiovisuels y compris les écrans de télévision").
exclusion(bris_vitrages, f(bien, serre), bien(serre), oui, '2.9-a',
    "les parties vitrées des serres et des couvertures de piscine").
exclusion(bris_vitrages, f(vitre_placee, non), tout, oui, '2.9-a',
    "les dommages aux vitres et biens assimilés non placés").
exclusion(bris_vitrages, f(type_dommage, rayure_ou_ecaillement), tout, oui, '2.9-a',
    "les rayures et écaillements des vitres et biens assimilés").
exclusion(bris_vitrages, et([f(bien, sanitaire), f(cause_dommage, gel)]), tout, oui, '2.9-a',
    "les dommages causés aux sanitaires par le gel").
exclusion(bris_vitrages, f(bien, objet_verre_non_vitre), bien(objet_verre_non_vitre), oui, '2.9-a',
    "les dommages causés aux objets en verre autres que des vitres et biens assimilés").
exclusion(bris_vitrages, f(type_dommage, opacification_ou_perte_etancheite), tout, oui, '2.9-a',
    "l’opacification ou perte détanchéité des vitrages isolants").
exclusion(bris_vitrages, f(bien, couverture_piscine), bien(couverture_piscine), oui, '2.9-a',
    "les parties vitrées des serres et des couvertures de piscine").
limite(bris_vitrages, '2.9', "Dommages causés aux vitrages d’art, frais de reconstitution des inscriptions, peintures, 5.000 EUR décorations", "5000 EUR").

% --- Art. 1.4 Exclusions générales (toutes les garanties traduites) ---------------------------------
%  « Nous ne couvrons jamais » : elles visent toutes les garanties. Inconnues, ce ne sont pas des
%  questions à poser à chaque déclaration : l'assureur prouve l'exclusion (« non »).
exclusion([vol_batiment, vol_personne, vol_reparateur, vol_cles, incendie, degats_eaux, bris_vitrages],
    f(intentionnel, oui), tout, non, '1.4',
    "résultant d’un sinistre intentionnel dont vous êtes l’auteur ou le complice").
exclusion([vol_batiment, vol_personne, vol_reparateur, vol_cles, incendie, degats_eaux, bris_vitrages],
    f(manque_entretien, oui), tout, non, '1.4',
    "résultant d’un vice propre, de l’usure, d’un manque d’entretien, d’un usage inapproprié, ou de la détérioration lente et progressive des biens assurés").

% --- Art. 2.12 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-18 ---
evenement_traduit(merule).
garantie(degats_merule, "Dégâts dus à la mérule", '2.12',
    "Nous couvrons les dégâts dus à la mérule survenue postérieurement à la prise d’effet de la garantie.").
perimetre(degats_merule, f(evenement, merule)).
perimetre(degats_merule, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(degats_merule, concept(batiment)).
circonstance(degats_merule, f(merule_apres_prise_effet, oui), '2.12',
    "survenue postérieurement à la prise d’effet de la garantie").

% --- Art. 2.2 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-18 ---
evenement_traduit(tempete).
definition(tempete, ou([f(vent_80_kmh_irm, oui), f(vent_dommages_voisins, oui)]), '12/tempete',
    "• L’action du vent mesurée à une vitesse de pointe d’au moins 80 km/h par la station de l’I.R.M. la plus proche du bâtiment • L’action du vent qui endommage d’autres biens qui sont situés dans les 10 km du bâtiment et qui sont assurables contre le vent de tempête ou présentent une résistance au vent équivalente aux biens assurables.").
garantie(tempete, "Tempête, la grêle, la pression de la neige ou de la glace", '2.2',
    "Nous couvrons les dommages matériels directement causés par les aléas précisés.").
perimetre(tempete, f(evenement, tempete)).
circonstance(tempete, si(f(alea_tempete, vent), concept(tempete)), '12/tempete',
    "L’action du vent mesurée à une vitesse de pointe d’au moins 80 km/h par la station de l’I.R.M. la plus proche du bâtiment").
exclusion(tempete, et([f(construction_delabree, oui), non(f(residence_principale, oui))]), tout, oui, '2.2-a',
    "aux constructions délabrées ou en cours de démolition et à leur contenu éventuel, sauf si ces constructions constituent votre logement principal").
exclusion(tempete, et([ou([f(lieu, jardin), f(lieu, terrasse)]), non(f(bien, element_batiment))]), tout, oui, '2.2-a',
    "à tout objet situé à l'extérieur même ceux fixés à demeure").
exclusion(tempete, et([ou([f(lieu, annexe), f(lieu, abri_jardin)]), f(construction_close, non)]), tout, oui, '2.2-a',
    "à tout objet situé dans une annexe non entièrement close ou couverte").
exclusion(tempete, f(bien, materiaux_construction), bien(materiaux_construction), non, '2.2-a',
    "aux matériaux à pied d’œuvre").
exclusion(tempete, et([ou([f(lieu, annexe), f(lieu, abri_jardin)]), f(annexe_ancree_beton, non)]), tout, oui, '2.2-a',
    "aux annexes contiguës ou isolées faisant partie du bâtiment qui ne sont pas fixées au sol par un ancrage en béton, ansi qu’à leur contenu").
exclusion(tempete, f(construction_close, non), tout, oui, '2.2-a',
    "aux constructions non entièrement closes ou couvertes, à ce qui y est incorporé ainsi qu’à leur contenu").
limite(tempete, '2.2', "Abri de jardin et son éventuel contenu 1.000 EUR", "1000 EUR").

% --- Art. 2.3 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-18 ---
evenement_traduit(catastrophe_naturelle).
definition(inondation, f(cause_eau, inondation), '12/inondation',
    "Débordement de cours d’eau, canaux, lacs, étangs ou mers, suite à des précipitations atmosphériques, à une fonte des neiges ou de glace, à une rupture de digues ou à un raz-de- marée ainsi que l'inondation, le débordement ou le refoulement d'égouts publics, le glissement ou affaissement de terrain qui en résulte • Inondations résultant de mesures prises par une autorité légalement constituée pour la sauvegarde et la protection des biens et des personnes, à savoir par l'ouverture ou la destruction d'écluses, de barrages ou de digues dans le but d'éviter une inondation éventuelle ou l'extension de celle-ci • Ruissellement ou accumulation d'eaux occasionnées par des crues, des précipitations atmosphériques une tempête ou une fonte des neiges ou de glaces. Sont également considérés comme une seule et même inondation, le débordement initial d’un cours d’eau, d’un canal, d’un lac, d'un étang ou d’une mer et tout débordement survenu dans un délai de 168 heures après la décrue, c'est-à-dire le retour de ce cours d’eau, ce canal, ce lac, cet étang ou cette mer dans les limites habituelles, ainsi que les périls assurés qui en résultent directement.").
definition(tremblement_de_terre, f(evenement, catastrophe_naturelle), '12/tremblement-de-terre',
    "Tout séisme d’origine naturelle enregistré avec une magnitude minimale de quatre degrés sur l'échelle de Richter ou qui détruit, brise ou endommage des biens assurables contre ce péril dans les 10 km du bâtiment désigné ainsi que l’inondation, le débordement ou refoulement d’égouts publics, le glissement ou affaissement de terrain qui en résulte. Sont considérés comme un seul et même tremblement de terre, le séisme initial et ses répliques survenues dans les 72 heures, ainsi que les périls assurés qui en résultent directement.").
definition(debordement_ou_refoulement_egouts, f(cause_eau, inondation), '12/debordement-ou-refoulement-d-e',
    "Tout débordement ou refoulement d’égouts publics occasionné par des crues, des précipitations atmosphériques, une tempête, une fonte des neiges ou de glace ou une inondation.").
definition(glissement_ou_affaissement_terrain, f(evenement, catastrophe_naturelle), '12/glissement-ou-affaissement-de-',
    "Mouvement dû en tout ou en partie à un phénomène naturel, à l'exception du tremblement de terre et de l’inondation, d'une masse importante de terrain qui détruit ou endommage des biens.").
garantie(catastrophes_naturelles, "Catastrophes naturelles", '2.3',
    "Nous couvrons les dégâts qui découlent directement ou indirectement de : • l’inondation • le tremblement de terre • le débordement ou refoulement d'égouts publics • le glissement ou affaissement de terrain en ce compris les périls assurés par les autres garanties de base, dont la survenance résulte directement d’une catastrophe naturelle.").
perimetre(catastrophes_naturelles, f(evenement, catastrophe_naturelle)).
perimetre(catastrophes_naturelles, ou([concept(inondation), concept(tremblement_de_terre), concept(debordement_ou_refoulement_egouts), concept(glissement_ou_affaissement_terrain)])).
exclusion(catastrophes_naturelles, et([f(construction_delabree, oui), non(f(residence_principale, oui))]), tout, oui, '2.3-a',
    "aux constructions délabrées ou en cours de démolition et à leur contenu éventuel, sauf si ces constructions constituent votre logement principal").
exclusion(catastrophes_naturelles, f(reparation_loi_particuliere, oui), tout, oui, '2.3-a',
    "aux biens dont la réparation des dommages est organisée par des lois particulières ou par des conventions internationales.").
exclusion(catastrophes_naturelles, et([ou([f(lieu, jardin), f(lieu, terrasse)]), non(f(bien, element_batiment))]), tout, oui, '2.3-a',
    "à tout objet situé à l'extérieur même fixé à demeure").
exclusion(catastrophes_naturelles, et([ou([f(lieu, annexe), f(lieu, abri_jardin)]), f(construction_close, non)]), tout, oui, '2.3-a',
    "à tout objet situé dans une annexe non entièrement close ou couverte").
exclusion(catastrophes_naturelles, si(ou([concept(inondation), concept(debordement_ou_refoulement_egouts)]), f(batiment_construit_plus_18_mois_apres_classement, oui)), tout, oui, '2.3-a',
    "au bâtiment, à une partie de bâtiment ou au contenu d’un bâtiment qui a été construit plus de dix-huit mois après la date de publication au Moniteur belge de l'arrêté royal classant la zone où ce bâtiment est situé comme zone à risque").
exclusion(catastrophes_naturelles, si(ou([concept(inondation), concept(debordement_ou_refoulement_egouts)]), f(extension_sol_avant_classement, oui)), tout, oui, '2.3-a',
    "aux extensions au sol des biens existant avant la date de classement de la zone à risque.").
exclusion(catastrophes_naturelles, si(ou([concept(inondation), concept(debordement_ou_refoulement_egouts)]), et([f(lieu, cave), f(contenu_moins_10cm_sol, oui), f(occupation_partielle, oui)])), tout, oui, '2.3-a',
    "au contenu entreposé à moins de 10 cm du sol dans les caves d’immeubles à appartements multiples").
limite(catastrophes_naturelles, '2.3', "Le total des indemnités dues à nos assurés lors de la survenance d’une catastrophe naturelle est limité conformément à l’article 130, §2 et §3 de la loi du 4 avril 2014 relative aux assurances. Si les limites prévues par cet article devaient être dépassées, l’indemnité due en vertu de chaque contrat d’assurance sera réduite à due concurrence.", "limite légale article 130").
limite(catastrophes_naturelles, '2.3', "Abri de jardin et son éventuel contenu 1.000 EUR", "1000 EUR").

% --- Art. 2.4 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-18 ---
evenement_traduit(attentat).
evenement_traduit(conflit_du_travail).
definition(conflit_du_travail, f(evenement, conflit_du_travail), '12/conflit-du-travail',
    "Toute contestation collective sous quelque forme qu’elle se manifeste dans le cadre des relations du travail, en ce compris : • la grève : arrêt concerté du travail par un groupe de salariés, employés, fonctionnaires ou indépendants • le lock-out : fermeture provisoire décidée par une entreprise afin d’amener son personnel à composer dans un «conflit du travail».").
garantie(attentat_conflit_travail, "Attentat et conflit du travail", '2.4',
    "Nous prenons en charge exclusivement sous cette garantie : • la destruction des biens assurés ou leur détérioration par des personnes prenant part à un attentat ou à un conflit du travail • les conséquences des mesures prises par une autorité légalement constituée pour la sauvegarde et la protection de ces biens, lors de tels événements.").
perimetre(attentat_conflit_travail, ou([f(evenement, attentat), f(evenement, conflit_du_travail)])).
perimetre(attentat_conflit_travail, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(attentat_conflit_travail, concept(batiment)).
limite(attentat_conflit_travail, '2.4', "Notre garantie est limitée aux montants assurés et en tout état de cause à 1.497.671,24 EUR.", "1497671.24 EUR").
exclusion([attentat_conflit_travail], f(cause_nucleaire, oui), tout, oui, '2.4-a',
    "les dommages causés par des armes ou des engins destinés à exploser par une modification de structure du noyau atomique").
exclusion([attentat_conflit_travail], f(graffiti_mur_exterieur, oui), tout, oui, '2.4-a',
    "les graffitis et autres inscriptions sur les murs extérieurs").
exclusion([attentat_conflit_travail], et([f(evenement, vandalisme), ou([f(bien, mobilier_jardin), f(bien, serre), f(bien, plantation)])]), tout, non, '2.4-a',
    "le vandalisme au mobilier extérieur, serres, plantations").

% --- Art. 2.6 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-18 ---
evenement_traduit(electricite).
garantie(action_electricite, "Action de l'électricité", '2.6',
    "Nous couvrons les dommages matériels directement causés par l’action de l’électricité, y compris : • l’électrocution des animaux domestiques, • la décongélation ou détérioration des denrées alimentaires utilisées dans le cadre de votre vie privée, suite à l’arrêt d’une durée de 6 heures ou au dérangement d’une installation de réfrigération ou de congélation provoqué par l’action de l’électricité ou par une coupure de courant soudaine et imprévisible suite à un dysfonctionnement du réseau de distribution d’électricité. Nous prenons également en charge les frais liés à la recherche, la réparation ou le remplacement de la pièce défectueuse à l'origine du sinistre, ainsi que la remise en état consécutive.").
perimetre(action_electricite, f(evenement, electricite)).
perimetre(action_electricite, concept(batiment)).
circonstance(action_electricite, si(f(bien, denrees_alimentaires), ou([f(cause_perte_alimentaire, arret_6h), f(cause_perte_alimentaire, derangement_installation), f(cause_perte_alimentaire, coupure_soudaine_reseau)])), '2.6',
    "suite à l’arrêt d’une durée de 6 heures ou au dérangement d’une installation de réfrigération ou de congélation provoqué par l’action de l’électricité ou par une coupure de courant soudaine et imprévisible suite à un dysfonctionnement du réseau de distribution d’électricité").
limite(action_electricite, '2.6', "Perte de denrées alimentaires suite à une variation de température due à une panne 500 EUR de courant d’au moins 6 heures (y compris blackout", "500 EUR").
exclusion([action_electricite], et([ou([f(bien, electronique), f(bien, appareil_informatique)]), f(usage_professionnel, oui)]), bien(appareil_informatique), non, '2.6-a',
    "les dommages aux appareils électroniques et informatiques dont l’usage est professionnel").
exclusion([action_electricite], et([f(bien, appareil_informatique), non(concept(batiment)), non(f(usage_professionnel, oui))]), bien(appareil_informatique), non, '2.6-a',
    "ainsi que les dommages aux autres appareils informatiques en dehors du bâtiment assuré").
exclusion([action_electricite], f(garantie_fabricant, oui), tout, non, '2.6-a',
    "les dégâts tombant sous la garantie du fabriquant ou du fournisseur").

% --- Art. 2.8 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-18 ---
evenement_traduit(mazout).
garantie(degats_mazout, "Dégâts causés par le mazout", '2.8',
    "Nous couvrons les dégâts causés par tout combustible liquide de chauffage du bâtiment").
perimetre(degats_mazout, f(evenement, mazout)).
perimetre(degats_mazout, concept(batiment)).
obligation(degats_mazout, si(f(periode_gel, oui), f(prevention_gel, oui)), faux, oui, '2.8-a',
    "En période de gel, vous devez : • maintenir une température positive dans tous les locaux, ou • vidanger les installations hydrauliques et de chauffage, ou • isoler efficacement ces installations contre le gel. Nous refuserons notre intervention s’il existe un lien causal direct entre le non-respect de ces obligations et la survenance du sinistre.").
exclusion(degats_mazout, et([f(bien, canalisation), f(bien_a_l_origine_sinistre, oui)]), bien(canalisation), oui, '2.8-b',
    "les dégâts causés aux citernes ou canalisations qui sont à l'origine du sinistre").
exclusion(degats_mazout, et([f(bien, citerne), f(bien_a_l_origine_sinistre, oui)]), bien(citerne), oui, '2.8-b',
    "les dégâts causés aux citernes ou canalisations qui sont à l'origine du sinistre").
exclusion(degats_mazout, f(controle_citerne_conforme, non), tout, oui, '2.8-b',
    "les dégâts causés en cas de non-respect de la réglementation applicable au contrôle des citernes").
exclusion(degats_mazout, f(bien, mazout), bien(mazout), oui, '2.8-b',
    "la pertes de combustible liquide de chauffage subie à l’occasion d’un sinistre").

% --- Art. 2.11 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-18 ---
evenement_traduit(vol).
evenement_traduit(vandalisme).
garantie(degradations_vol_vandalisme, "Dégradations immobilières suite à des actes de vol, vandalisme et malveillance", '2.11',
    "Nous couvrons les dégradations immobilières sauf les dégâts causés : • au bâtiment libre de toute occupation depuis plus de 90 jours au moment du sinistre • aux matériaux à pied d'œuvre se trouvant à l’extérieur ou dans un bâtiment non fermé à clé • par ou avec la complicité d'un assuré, d'un descendant ou ascendant, du conjoint ou partenaire de chacun d'eux ou d'un locataire ou des personnes vivant à son foyer.").
perimetre(degradations_vol_vandalisme, ou([concept(vol), f(evenement, vandalisme)])).
perimetre(degradations_vol_vandalisme, f(bien, element_batiment)).
perimetre(degradations_vol_vandalisme, concept(batiment)).
obligation(degradations_vol_vandalisme, si(f(absence, oui), et([f(portes_fermees, oui), f(fenetres_fermees, oui)])), f(effraction, oui), oui, '2.11-a',
    "en cas d’absence, fermer à clé ou au moyen d'un dispositif électronique toutes les portes extérieures du bâtiment. Si seulement une partie du bâtiment est occupée par l’assuré, les portes donnant sur les parties communes doivent être fermées de la même manière. Vous devez de même fermer correctement les fenêtres, oscillo-battants, soupiraux et autres ouvertures du bâtiment facilement accessibles").
obligation(degradations_vol_vandalisme, non(f(cles_a_proximite, oui)), f(effraction, oui), oui, '2.11-a',
    "ne pas laisser les clés d'accès aux locaux à proximité de ceux-ci").
obligation(degradations_vol_vandalisme, si(f(lieu, abri_jardin), f(serrure_surete, oui)), f(effraction, oui), oui, '2.11-a',
    "fermer l’abri de jardin à l’aide d’une serrure de sûreté").
obligation(degradations_vol_vandalisme, si(f(bien, mobilier_jardin), f(materiel_jardin_range, oui)), f(effraction, oui), oui, '2.11-a',
    "ranger le matériel de jardin dans un local fermé à clé lorsqu’il n’est pas utilisé").
obligation(degradations_vol_vandalisme, f(dispositifs_antivol_installes, oui), faux, oui, '2.11-a',
    "installer les dispositifs de protection antivol que, le cas échéant, nous imposons et qui sont mentionnés en conditions particulières, les maintenir en bon état de fonctionnement et les utiliser en cas d’absence").
exclusion(degradations_vol_vandalisme, f(batiment_vacant_90j, oui), tout, oui, '2.11',
    "au bâtiment libre de toute occupation depuis plus de 90 jours au moment du sinistre").
exclusion(degradations_vol_vandalisme, et([f(bien, materiaux_construction), ou([ou([f(lieu, jardin), f(lieu, terrasse)]), f(fermeture, aucune)])]), bien(materiaux_construction), non, '2.11',
    "aux matériaux à pied d'œuvre se trouvant à l’extérieur ou dans un bâtiment non fermé à clé").
exclusion(degradations_vol_vandalisme, ou([f(auteur, assure), f(auteur, famille), f(auteur, locataire), f(auteur, personnel_prive)]), tout, oui, '2.11',
    "par ou avec la complicité d'un assuré, d'un descendant ou ascendant, du conjoint ou partenaire de chacun d'eux ou d'un locataire ou des personnes vivant à son foyer").
