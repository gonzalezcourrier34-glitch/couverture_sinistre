:- encoding(utf8).
/*  Règles du contrat Foyer « appart 123 » (2025) : vol (art. 2.10), incendie (art. 2.1),
    dégâts des eaux (art. 2.7), et les définitions de l'art. 12 qu'elles emploient.

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
                 obligation/6, exclusion/6, limite/4.

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
exclusion(vol_batiment, f(simple_disparition, oui), tout, non, '2.10',
    "le vol du contenu situé dans le bâtiment sauf la simple disparition").
limite(vol_batiment, '2.10',
    "Les limites d’indemnisation pour le vol du contenu dépendent du nombre de chambres", "17 500 à 37 500 EUR").
limite(vol_batiment, '2.10', "si ces locaux sont fermés avec une serrure de sûreté", "caves et greniers : 1 000 EUR").

garantie(vol_personne, "Vol commis sur l’assuré avec violences", '2.10',
    "le vol commis sur l’assuré, en dehors des biens assurés, suite à violences physiques et/ou menaces").
perimetre(vol_personne, concept(vol)).
perimetre(vol_personne, f(vol_sur_personne, oui)).
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
