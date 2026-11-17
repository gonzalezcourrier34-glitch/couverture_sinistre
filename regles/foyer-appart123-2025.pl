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

% --- Art. 2.10-a Exclusions du vol (communes aux trois garanties vol) ---------------------------------

exclusion([vol_batiment, vol_personne, vol_reparateur], f(lieu, parties_communes), tout, oui, '2.10-a',
    "le vol ou le vandalisme dans les parties communes du bâtiment").
exclusion([vol_batiment, vol_personne, vol_reparateur], ou([f(auteur, assure), f(auteur, famille)]), tout, non, '2.10-a',
    "le vol et le vandalisme commis par ou avec votre complicité ou celle d’un descendant ou ascendant").
exclusion([vol_batiment, vol_personne, vol_reparateur], f(auteur, personnel_prive), tout, non, '2.10-a',
    "le vol commis par des personnes au service privé de l’assuré").
exclusion([vol_batiment, vol_personne, vol_reparateur], f(proprietaire, hote), tout, non, '2.10-a',
    "le vol des biens appartenant à des hôtes").
exclusion([vol_batiment, vol_personne, vol_reparateur], f(bien, animal), bien(animal), oui, '2.10-a',
    "le vol des animaux").
exclusion([vol_batiment, vol_personne, vol_reparateur], f(bien, mobilier_jardin), bien(mobilier_jardin), oui, '2.10-a',
    "le vol du mobilier extérieur").

% --- Art. 2.1 Incendie et risques connexes -------------------------------------------------------------

garantie(incendie, "Incendie et risques connexes", '2.1',
    "Nous couvrons les dommages matériels directement causés par").
perimetre(incendie, ou([concept(incendie), f(evenement, explosion), f(evenement, foudre)])).
%  La garantie ne se rattache qu'aux événements qu'elle couvre : pas de question sur les flammes pour une tempête.
perimetre(incendie, ou([f(evenement, incendie), f(evenement, explosion), f(evenement, foudre)])).
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
exclusion(degats_eaux, f(cause_eau, inondation), tout, oui, '2.7-b',
    "par une inondation ou un débordement ou refoulement d'égouts publics").
exclusion(degats_eaux, f(cause_eau, condensation), tout, non, '2.7-b', "par la condensation").
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
