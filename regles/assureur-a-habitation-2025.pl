:- encoding(utf8).
/*  Règles du contrat Assureur A « Habitation A » (2025).

    Quatre blocs ont été écrits à la main, pour servir de modèle avant que la rédaction par un modèle de langage
    existe : le vol (art. 2.10 et ses exclusions, 2.10-a), l'incendie (art. 2.1), les dégâts des eaux (art. 2.7) et
    les exclusions générales (art. 1.4), avec les définitions de l'art. 12 qu'ils emploient.
    Tous les autres articles ont été rédigés par Mistral Large (`couverture rediger`), contrôlés par le code, relus,
    puis ajoutés ici : chacun porte l'en-tête « proposition rédigée par le modèle ». Ce que le contrat traduit
    aujourd'hui se lit dans les faits evenement_traduit.

    Chaque règle garde, mot pour mot, la phrase du contrat qu'elle traduit : `couverture regles`
    vérifie que chaque citation figure dans la clause citée, et que chaque variable appartient
    au vocabulaire (regles/vocabulaire/). Le moteur est dans regles/moteur.pl.

    Deux formes du contrat que les fiches ne savaient pas représenter (voir docs/DEMARCHE.md) :
      - une condition cachée dans le tableau des limites : la cave n'est couverte que « si ces
        locaux sont fermés avec une serrure de sûreté », et la serrure de sûreté exclut le cadenas ;
      - une exclusion cachée dans une définition : le contenu « ne comprend pas … le contenu du jardin ».
*/

:- discontiguous definition/4, precision/3, garantie/4, perimetre/2, circonstance/4,
                 obligation/6, exclusion/6, limite/4, evenement_traduit/1, accessoire/1.

%  Les garanties optionnelles (DEMARCHE 7.109) : elles ne jouent que si les conditions particulières les mentionnent,
%  ce que la déclaration ne dit pas. Seule à couvrir, une option ne donne pas « couvert sous réserve » mais « à
%  préciser », avec le point à vérifier dans les conditions particulières. Les garanties de base sont présumées souscrites.
option(option_materiel_multimedia).

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
%  La casse accidentelle (7.84) : le contrat ne la garantit que pour le matériel informatique (pack multimédia,
%  art. 6.1, où « accident » compte comme un heurt) ; ailleurs, aucune garantie. La question est examinée :
%  pas de plafond à « incertain ».
evenement_traduit(accident).

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

% --- Art. 3.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
extension(batiment, et([f(sejour_temporaire, oui), f(lieu, autre_batiment), concept(contenu)]), '3.1',
    "Le déplacement de votre contenu à l'occasion d'un séjour temporaire dans un bâtiment à concurrence de 5.000 EUR (à l’exception d’une caravane tractable ou d’un mobilhome pour lesquels la limite d’indemnisation est fixée à 500 EUR)").
extension(batiment, et([f(demenagement, oui), f(lieu, vehicule), f(detenteur_vehicule, oui), concept(contenu)]), '3.1',
    "Le contenu est également couvert lors de son transport dans un véhicule dont vous êtes le détenteur à concurrence de 5.000 EUR.").
garantie(extension_residence_remplacement, "Extension - Résidence de remplacement (RC locative)", '3.1',
    "La résidence de remplacement (meublée ou non) : si votre résidence principale est temporairement inhabitable à la suite d'un sinistre, nous couvrons pendant 18 mois votre responsabilité locative pour les dégâts causés à cette résidence de remplacement").
perimetre(extension_residence_remplacement, f(residence_principale, oui)).
perimetre(extension_residence_remplacement, f(residence_principale_inhabitable, oui)).
perimetre(extension_residence_remplacement, f(lieu, autre_batiment)).
exclusion(extension_residence_remplacement, non(f(couverture_rc_locative, oui)), tout, oui, '3.1',
    "Si nous couvrons votre résidence principale, et en fonction des couvertures (RC locative et/ou contenu) mentionnées dans vos conditions particulières").
limite(extension_residence_remplacement, '3.1', "jusqu'à concurrence de 1.000.000 EUR", "1000000 EUR").
limite(extension_residence_remplacement, '3.1', "pendant 18 mois", "18 mois").
garantie(extension_residence_villegiature, "Extension - Résidence de villégiature (RC contractuelle)", '3.1',
    "La résidence de villégiature (meublée ou non), à l'occasion d'un séjour temporaire nous couvrons votre responsabilité contractuelle pour les dégâts causés à cette résidence de villégiature, l'hôtel ou un logement similaire").
perimetre(extension_residence_villegiature, f(sejour_temporaire, oui)).
perimetre(extension_residence_villegiature, f(lieu, autre_batiment)).
exclusion(extension_residence_villegiature, non(f(couverture_rc_locative, oui)), tout, oui, '3.1',
    "Si nous couvrons votre résidence principale, et en fonction des couvertures (RC locative et/ou contenu) mentionnées dans vos conditions particulières").
limite(extension_residence_villegiature, '3.1', "jusqu'à concurrence de 1.000.000 EUR", "1000000 EUR").
garantie(extension_local_fete_familiale, "Extension - Local de fête de famille (RC locative)", '3.1',
    "Le local que vous occupez à l’occasion d’une fête de famille, c’est-à-dire une festivité privée à caractère familial. Nous couvrons votre responsabilité locative pour les dégâts que vous causez à ce local. Les tentes, chapiteaux et péniches à quai sont assimilés aux locaux de fête").
perimetre(extension_local_fete_familiale, f(occasion_fete_familiale, oui)).
perimetre(extension_local_fete_familiale, f(lieu, autre_batiment)).
exclusion(extension_local_fete_familiale, non(f(couverture_rc_locative, oui)), tout, oui, '3.1',
    "Si nous couvrons votre résidence principale, et en fonction des couvertures (RC locative et/ou contenu) mentionnées dans vos conditions particulières").
limite(extension_local_fete_familiale, '3.1', "jusqu'à concurrence de 1.000.000 EUR", "1000000 EUR").
garantie(extension_abandon_recours_famille, "Extension - Abandon de recours envers les parents ou alliés en ligne directe", '3.1',
    "L’abandon de recours : nous abandonnons tout recours envers les parents ou alliés en ligne directe auxquels vous prêtez ou louez votre habitation sauf en cas de malveillance ou dans la mesure où ces personnes disposent d’une assurance garantissant leur responsabilité").
perimetre(extension_abandon_recours_famille, f(auteur, famille)).
perimetre(extension_abandon_recours_famille, f(pret_ou_location_habitation, oui)).
exclusion(extension_abandon_recours_famille, f(malveillance_auteur, oui), tout, oui, '3.1',
    "sauf en cas de malveillance").
exclusion(extension_abandon_recours_famille, f(assurance_responsabilite_tiers, oui), tout, oui, '3.1',
    "ou dans la mesure où ces personnes disposent d’une assurance garantissant leur responsabilité").
exclusion(extension_abandon_recours_famille, non(f(couverture_rc_locative, oui)), tout, oui, '3.1',
    "Si nous couvrons votre résidence principale, et en fonction des couvertures (RC locative et/ou contenu) mentionnées dans vos conditions particulières").
accessoire(extension_residence_remplacement).
accessoire(extension_residence_villegiature).
accessoire(extension_local_fete_familiale).
accessoire(extension_abandon_recours_famille).

% --- Art. 4 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
garantie(garanties_complementaires, "Garanties complémentaires (frais, pertes)", '4~1',
    "Vous bénéficiez des garanties complémentaires en cas de sinistre assuré par une garantie de base ou par une garantie facultative que vous avez souscrite et ce compris les événements survenant en dehors de l’habitation mentionnée en conditions particulières.").
limite(garanties_complementaires, '4~1', "• frais de sauvetage • frais de déblai et de démolition des biens assurés, en ce compris les frais d'abattage, d'élagage et d'enlèvement de l'arbre ou du pylône qui a causé les dégâts • frais de nettoyage des locaux endommagés après travaux • frais de conservation et d’entreposage des biens sauvés", "sans plafond").
limite(garanties_complementaires, '4~1', "• frais de logement provisoire pendant la durée normale de non habitabilité de votre bâtiment • le chômage immobilier pendant la durée normale de reconstruction de votre bâtiment. Cette indemnité ne peut se cumuler pour une même période et un même logement sinistré avec la garantie des frais de logement provisoire et ce pour une période maximale de 18 mois.", "18 mois max").
limite(garanties_complementaires, '4~1', "• frais liés aux garanties dégâts causés par l'eau et le mazout c'est-à-dire les frais liés à la recherche, la réparation ou le remplacement de la partie de canalisation à l'origine du sinistre y compris les radiateurs, ainsi que la remise en état consécutive. Nous prenons en charge ces frais jusqu'à concurrence de maximum 1.100 EUR lorsque les biens assurés n'ont pas été endommagés. Nous couvrons également la moins-value du bâtiment pouvant en résulter et fixée par l'expert, jusqu'à concurrence de maximum 2.200 EUR par sinistre", "1100 EUR / 2200 EUR").
limite(garanties_complementaires, '4~2', "• l’avance de fonds jusqu'à 7.700 EUR, pour couvrir les frais de première nécessité et les réparations en cas de non habitabilité du bâtiment. Cette avance n'implique aucune reconnaissance de la prise en charge du sinistre et est déduite de l'indemnité définitive éventuelle", "7700 EUR").
limite(garanties_complementaires, '4~2', "• frais médicaux et pharmaceutiques à concurrence de 2.000 EUR.", "2000 EUR").
limite(garanties_complementaires, '4~2', "• frais d’expertise c'est-à-dire les frais et honoraires de votre expert et le cas échéant ceux d’un tiersexpert, calculés en pourcentage des indemnités dues hors TVA, conformément au barème repris ciaprès, à l'exclusion de celles relatives aux assurances de responsabilité et des pertes indirectes.", "barème % max 25000 EUR").
accessoire(garanties_complementaires).

% --- Art. 6.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
evenement_traduit(heurt).
evenement_traduit(bris).
evenement_traduit(vol).
definition(materiel_informatique, f(bien, appareil_informatique), '12/materiel-informatique',
    "Les ordinateurs de bureau et périphériques, laptops, notebook et tout appareil dont la taille de l’écran est supérieure à 7’’.").
garantie(pack_multimedia, "Pack multimédia", '6.1',
    "Pour autant que vos conditions particulières en fassent mention, vos garanties sont étendues au matériel informatique. Dans ce cadre, nous prenons en charge les dommages causés par : • la chute, le heurt et l’introduction d’un corps étrangers • le vol survenu à l’extérieur du bâtiment assuré, pour autant qu’une plainte soit déposée auprès des autorités judiciaires ou de polices compétentes. Il faut noter que ces couvertures sont acquises dans le monde entier.").
perimetre(pack_multimedia, concept(materiel_informatique)).
perimetre(pack_multimedia, ou([f(evenement, heurt), f(evenement, bris), f(evenement, vol)])).
circonstance(pack_multimedia, si(f(evenement, vol), et([non(concept(batiment)), f(plainte_deposee, oui)])), '6.1',
    "le vol survenu à l’extérieur du bâtiment assuré, pour autant qu’une plainte soit déposée auprès des autorités judiciaires ou de polices compétentes").
exclusion(pack_multimedia, et([f(evenement, vol), f(laisse_sans_surveillance, oui)]), tout, oui, '6.1',
    "le vol d’objets ayant été laissé sans surveillance dans un lieu public").
exclusion(pack_multimedia, et([f(evenement, vol), f(lieu, vehicule), f(vehicule_voie_publique, oui), f(periode_horaire, nuit_22h_7h)]), tout, oui, '6.1',
    "le vol d’objets laissés dans un véhicule en stationnement sur la voie publique entre 22 heures et 7 heures").
exclusion(pack_multimedia, et([f(evenement, vol), f(lieu, vehicule), f(vehicule_voie_publique, oui), f(periode_horaire, jour_7h_22h), ou([f(materiel_laisse_en_vue, oui), f(vehicule_ferme_cle, non), f(habitacle_ferme, non)])]), tout, oui, '6.1',
    "le vol d’objets laissés dans un véhicule en stationnement sur la voie publique entre 7 heures et 22 heures et que les objets étaient visibles de l’extérieur ou que le véhicule n’était pas fermé à clé ou encore que l’habitacle n’était pas entièrement fermé").
exclusion(pack_multimedia, et([f(evenement, vol), f(simple_disparition, oui)]), tout, oui, '6.1',
    "la simple perte, disparition ou l’oubli d’un objet dans un lieu public").
exclusion(pack_multimedia, non(f(option_materiel_multimedia, oui)), tout, oui, '6.1',
    "Pour autant que vos conditions particulières en fassent mention, vos garanties sont étendues au matériel informatique. Dans ce cadre, nous prenons en charge les dommages causés par : • la chute, le heurt et l’introduction d’un corps étrangers • le vol survenu à l’extérieur du bâtiment assuré, pour autant qu’une plainte soit déposée auprès des autorités judiciaires ou de polices compétentes. Il faut noter que ces couvertures sont acquises dans le monde entier.").
limite(pack_multimedia, '6.1-a', "Limite par sinistre (à l’indice ABEX 775) 5.750 EUR", "5750 EUR à l'indice ABEX 775").
% --- Art. 2.6 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-18 ---
evenement_traduit(electricite).
garantie(action_electricite, "Action de l'électricité", '2.6',
    "Nous couvrons les dommages matériels directement causés par l’action de l’électricité, y compris : • l’électrocution des animaux domestiques, • la décongélation ou détérioration des denrées alimentaires utilisées dans le cadre de votre vie privée, suite à l’arrêt d’une durée de 6 heures ou au dérangement d’une installation de réfrigération ou de congélation provoqué par l’action de l’électricité ou par une coupure de courant soudaine et imprévisible suite à un dysfonctionnement du réseau de distribution d’électricité. Nous prenons également en charge les frais liés à la recherche, la réparation ou le remplacement de la pièce défectueuse à l'origine du sinistre, ainsi que la remise en état consécutive.").
perimetre(action_electricite, f(evenement, electricite)).
perimetre(action_electricite, concept(batiment)).
circonstance(action_electricite, si(f(bien, denrees_alimentaires), ou([f(cause_perte_alimentaire, arret_6h), f(cause_perte_alimentaire, derangement_installation), f(cause_perte_alimentaire, coupure_soudaine_reseau)])), '2.6',
    "suite à l’arrêt d’une durée de 6 heures ou au dérangement d’une installation de réfrigération ou de congélation provoqué par l’action de l’électricité ou par une coupure de courant soudaine et imprévisible suite à un dysfonctionnement du réseau de distribution d’électricité").
limite(action_electricite, '2.6', "Perte de denrées alimentaires suite à une variation de température due à une panne 500 EUR de courant d’au moins 6 heures (y compris blackout", "500 EUR").
exclusion([action_electricite], et([f(bien, appareil_informatique), f(usage_professionnel, oui)]), bien(appareil_informatique), non, '2.6-a',
    "les dommages aux appareils électroniques et informatiques dont l’usage est professionnel").
exclusion([action_electricite], et([f(bien, electronique), f(usage_professionnel, oui)]), bien(electronique), non, '2.6-a',
    "les dommages aux appareils électroniques et informatiques dont l’usage est professionnel").
exclusion([action_electricite], et([f(bien, appareil_audiovisuel), f(usage_professionnel, oui)]), bien(appareil_audiovisuel), non, '2.6-a',
    "les dommages aux appareils électroniques et informatiques dont l’usage est professionnel").
exclusion([action_electricite], et([f(bien, appareil_informatique), non(concept(batiment)), non(f(usage_professionnel, oui))]), bien(appareil_informatique), non, '2.6-a',
    "ainsi que les dommages aux autres appareils informatiques en dehors du bâtiment assuré").
exclusion([action_electricite], f(garantie_fabricant, oui), tout, non, '2.6-a',
    "les dégâts tombant sous la garantie du fabriquant ou du fournisseur").

% --- Art. 9 : proposition rédigée par le modèle — aucun, 2026-11-20 ---
exclusion(tous, et([f(emmenagement, plus_30_jours), f(demenagement_signale, non)]), tout, oui, '9.2~8',
    "Si vous déménagez en Belgique, vous disposez d’un délai de 30 jours pour nous en informer. Si vous ne le faites pas, l’assurance prend fin à l’expiration de ce délai.").

% --- Art. 2.13 : proposition rédigée par le modèle — mistral:mistral-large-4-0 (proposition écartée), 2026-11-24 ---
evenement_traduit(assistance).
garantie(assistance_apres_sinistre, "Assistance après un sinistre couvert", '2.13~1',
    "vous trouverez ci-dessous, de manière exhaustive, les prestations comprises dans votre contrat d’assurance et qui sont mises en place après un sinistre couvert").
limite(assistance_apres_sinistre, '2.13~3', "de l’organisation et de la prise en charge d’un véhicule de remplacement (voiture de tourisme de la catégorie B au maximum) durant 7 jours au maximum à partir de la date du sinistre couvert", "7 jours max").
limite(assistance_apres_sinistre, '2.13~4', "Assureur A Assistance organise cette surveillance et en assume les frais pendant 72 heures au maximum", "72 heures max").
limite(assistance_apres_sinistre, '2.13~4', "de la mise à disposition pendant 16 heures maximum d’un agent de nettoyage pour le nettoyage des locaux endommagés à concurrence de 40 EUR/heure", "16 heures, 40 EUR/heure").
limite(assistance_apres_sinistre, '2.13~4', "Assureur A Assistance indemnise à concurrence de 120 EUR par jour (toutes taxes et frais compris) au cours de 7 jours au maximum", "120 EUR/jour, 7 jours max").
garantie(depannage_serrurier, "Dépannage serrurier", '2.13~6',
    "Si l’assuré ne peut plus pénétrer dans le bâtiment assuré à la suite de la perte des clés, de l’oubli des clés à l’intérieur, ou du vol des clés ou parce que la serrure du bâtiment ou de l’appartement (lorsque l’assuré n’occupe qu’une partie du bâtiment) a été endommagée, Assureur A Assistance organisera et paiera les frais d’ouverture de la porte et, le cas échéant, le remplacement de la serrure par un serrurier").
perimetre(depannage_serrurier, f(evenement, assistance)).
perimetre(depannage_serrurier, f(objet_assistance, ouverture)).
exclusion(depannage_serrurier, et([f(intervention_mandatee, non), non(f(contact_assistance_impossible, oui))]), tout, oui, '2.13-a',
    "Les prestations qui ne peuvent être demandées au moment du sinistre et qui ne sont pas exécutées en accord avec Assureur A Assistance ne sont pas garanties. Néanmoins, lorsque l’assuré n’a matériellement pas été en mesure de prendre contact avec la centrale de Assureur A Assistance, la couverture continuera à s’appliquer").
limite(depannage_serrurier, '2.13~6', "Assureur A Assistance prend ces frais en charge à concurrence de 300 EUR au maximum par sinistre et par année assurée", "300").
accessoire(assistance_apres_sinistre).
% --- Art. 2.5 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(responsabilite).
garantie(rc_immeuble, "Responsabilité civile immeuble", '2.5',
    "Nous prenons en charge la responsabilité civile que vous pouvez encourir sur base : • du livre 6 du Code civil • de l’article 1721 du Code civil c'est-à-dire le recours des locataires pour les dommages causés aux tiers du fait : • du bâtiment, du contenu").
perimetre(rc_immeuble, f(evenement, responsabilite)).
perimetre(rc_immeuble, ou([f(origine_rc, immeuble), f(origine_rc, habitation)])).
exclusion(rc_immeuble, ou([f(victime, assure), f(victime, conjoint)]), tout, non, '12/tiers',
    "Toute personne qui n’est pas considérée comme assurée.").
exclusion(rc_immeuble, f(bien_confie, oui), tout, non, '2.5-a',
    "à des biens dont vous avez la garde").
exclusion(rc_immeuble, f(cause_amiante, oui), tout, non, '2.5-a',
    "par l’amiante sous toutes ses formes").
exclusion(rc_immeuble, f(controle_citerne_respecte, non), tout, non, '2.5-a',
    "en cas de non-respect de la réglementation applicable au contrôle des citernes").
exclusion(rc_immeuble, f(ascenseur_non_conforme, oui), tout, non, '2.5',
    "des ascenseurs et monte-charge pour autant qu’ils soient déclarés conformes à la réglementation en vigueur par un organisme de contrôle entretenus annuellement par une entreprise agréée").
exclusion(rc_immeuble, f(terrain_plus_5_hectares, oui), tout, non, '2.5',
    "du terrain attenant au bâtiment, sans dépasser au total 5 hectares").
limite(rc_immeuble, '2.5', "18.425.000 EUR pour l’indemnisation des dommages résultant de lésions corporelles", "18425000").
limite(rc_immeuble, '2.5', "3.685.000 EUR pour l’indemnisation des dommages résultant de dégâts matériels", "3685000").

% --- Art. 2.14 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(litige).
garantie(defense_penale, "Défense pénale", '2.14~1',
    "que vous et toutes les personnes assurées auront exposés pour leur défense devant une juridiction pénale où ils sont cités à la suite d’un événement garanti par la présente assurance").
perimetre(defense_penale, f(evenement, litige)).
perimetre(defense_penale, f(domaine_litige, defense_penale)).
exclusion(defense_penale, f(procedure_etranger_sans_accord, oui), tout, non, '2.14~2',
    "une action ou procédure menée à l’étranger sans notre accord écrit préalable").
limite(defense_penale, '2.14~2', "Défense et recours 6.500 EUR", "6500").
garantie(recours, "Recours contre les tiers responsables", '2.14~1',
    "que les assurés, à l’exception du personnel même occasionnel à leur service privé auront exposés pour l’exercice de recours contre les tiers responsables de dommages").
perimetre(recours, f(evenement, litige)).
perimetre(recours, f(domaine_litige, recours_dommage)).
exclusion(recours, f(procedure_etranger_sans_accord, oui), tout, non, '2.14~2',
    "une action ou procédure menée à l’étranger sans notre accord écrit préalable").
exclusion(recours, f(adversaire_assure, oui), tout, non, '2.14~2',
    "les recours entre assurés").
limite(recours, '2.14~2', "Défense et recours 6.500 EUR", "6500").

% --- Art. 5 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(responsabilite).
garantie(rc_vie_privee, "Responsabilité civile vie privée", '5.1',
    "Nous vous assurons dans le monde entier lorsque votre responsabilité est mise en cause pour des dommages occasionnés à un tiers dans le cadre de votre vie privée et en dehors de tout contrat").
perimetre(rc_vie_privee, f(evenement, responsabilite)).
exclusion(rc_vie_privee, ou([f(victime, assure), f(victime, conjoint)]), tout, non, '12/tiers',
    "Toute personne qui n’est pas considérée comme assurée.").
exclusion(rc_vie_privee, f(origine_rc, activite_professionnelle), tout, non, '5.1',
    "dans le cadre de votre vie privée").
exclusion(rc_vie_privee, f(origine_rc, contrat), tout, non, '5.1',
    "en dehors de tout contrat").
exclusion(rc_vie_privee, f(bien_confie, oui), tout, non, '5.10',
    "les dommages causés aux biens mobiliers et immobiliers dont vous avez la garde").
exclusion(rc_vie_privee, f(origine_rc, vehicule_moteur), tout, non, '5.4-a',
    "des véhicules automoteurs ou équipés d’un moteur même non autonomes autres que ceux cités au point 2.4").
exclusion(rc_vie_privee, et([f(origine_rc, habitation), ou([f(evenement, incendie), f(evenement, explosion), f(evenement, fumee)])]), tout, non, '5.2-a',
    "les dommages matériels causés par le feu, par l’incendie, l’explosion ou la fumée consécutive à un feu ou à un incendie prenant naissance dans ou communiqué par un bâtiment assuré par le présent contrat").
exclusion(rc_vie_privee, f(intentionnel, oui), tout, non, '5.10',
    "pour les sinistres intentionnels").
exclusion(rc_vie_privee, f(pratique_chasse, oui), tout, non, '5.5-a',
    "Nous n’indemnisons pas les dommages causés par la pratique de la chasse.").
exclusion(rc_vie_privee, f(animal_sauvage, gibier_ou_sauvage), tout, non, '5.3-a',
    "causés par le gibier ou les animaux sauvages, domptés ou non, à l’exception des cervidés").
exclusion(rc_vie_privee, et([ou([f(faute_lourde, ivresse), f(faute_lourde, violence)]), non(f(auteur_mineur, oui))]), tout, non, '5.10',
    "la responsabilité civile personnelle de l’assuré qui a atteint l’âge de 18 ans pour les sinistres causés en raison d’une des fautes lourdes suivantes : ivresse ou état analogue résultant de l’utilisation de produits autres que des boissons alcoolisées, actes de violence commis sur les personnes").
exclusion(rc_vie_privee, f(evenement, attentat), tout, non, '5.10',
    "pour les actes de terrorisme").
exclusion(rc_vie_privee, f(cause_nucleaire, oui), tout, non, '5.10',
    "les dommages ou l’aggravation des dommages causés par la modification de la structure du noyau de l’atome").
exclusion(rc_vie_privee, f(pollution_graduelle, oui), tout, non, '5.10',
    "les dommages découlant de la pollution graduelle").
exclusion(rc_vie_privee, ou([f(evenement, attentat), f(evenement, conflit_du_travail)]), tout, non, '5.10',
    "Les dommages résultant d’actes collectifs de violence, d’émeute, de sabotage, de mouvement populaire, de conflit de travail ou de terrorisme.").
exclusion(rc_vie_privee, f(origine_rc, vehicule_moteur), tout, non, '5.4-a',
    "l’emploi de jet-skis ainsi que l’emploi de véhicules aériens").
exclusion(rc_vie_privee, f(plus_de_5_chevaux, oui), tout, non, '5.3',
    "La garantie est acquise pour 5 chevaux de selle dont vous êtes propriétaire, ou plus si leur nombre est mentionné en conditions particulières").
limite(rc_vie_privee, '5.1', "les dommages résultant de lésions corporelles à concurrence de 24.763.874,96 EUR", "24763874.96").
limite(rc_vie_privee, '5.1', "les dommages matériels à concurrence de 7.131.995,99 EUR", "7131995.99").
limite(rc_vie_privee, '5.1', "Une franchise de 258,70 EUR est d’application pour les dommages matériels", "franchise 258.70").
