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

%  Les garanties optionnelles (DEMARCHE 7.109) : elles ne jouent que si les conditions particulières les mentionnent,
%  ce que la déclaration ne dit pas. Seule à couvrir, une option ne donne pas « couvert sous réserve » mais « à
%  préciser », avec le point à vérifier dans les conditions particulières. Les garanties de base sont présumées souscrites.
option(option_veranda).
option(option_objets_valeur).
option(pack_jardin).
option(pack_piscine).
% --- Art. 1.5 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
extension(batiment, et([f(sejour_temporaire, oui), f(lieu, autre_batiment), ou([f(bien, mobilier), f(bien, electronique), f(bien, objet_divers), f(bien, velo), f(bien, mobilier_jardin)]), non(ou([f(bien, bijoux), f(bien, valeurs)])), ou([f(pays, france), f(pays, belgique), f(pays, luxembourg), f(pays, allemagne), f(pays, autre_ue), f(pays, royaume_uni), f(pays, andorre), f(pays, monaco)])]), '1.5-a',
    "Les objets que vous emportez avec vous dans les différents locaux d’habitation, y compris les chambres d’hôtel, que vous occupez lors de voyages ou de vacances dans les pays de l’Union européenne, au Royaume-Uni de Grande-Bretagne et d’Irlande du Nord, dans les principautés d’Andorre et de Monaco").
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

% --- Art. 1.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
definition(batiment, ou([f(lieu, logement), f(lieu, grenier), f(lieu, parties_communes), f(lieu, cave), f(lieu, garage), f(lieu, annexe), f(lieu, abri_jardin)]), '1.1-a',
    "votre local d’habitation, c’est-à-dire les parties immobilières des bâtiments principaux d’habitation destinées à un usage privé").
exclusion([incendie_evenements_annexes, dommages_electriques, tempete_grele_neige, venues_eau_gel, recherche_fuite, debordement_cuves, vol_vandalisme, vol_cles, deteriorations_immobilieres, bris_glaces, bris_glace_plus, bris_glace_renforce, contenu_congelateur, catastrophes_naturelles, relogement_catnat, attentats, emeutes, intervention_secours], et([f(bien, veranda), non(f(option_veranda, oui))]), bien(veranda), non, '1.1-b',
    "les vérandas, sauf mention aux conditions particulières").
exclusion([incendie_evenements_annexes, dommages_electriques, tempete_grele_neige, venues_eau_gel, recherche_fuite, debordement_cuves, vol_vandalisme, vol_cles, deteriorations_immobilieres, bris_glaces, bris_glace_plus, bris_glace_renforce, contenu_congelateur, catastrophes_naturelles, relogement_catnat, attentats, emeutes, intervention_secours], f(bien, eolienne), bien(eolienne), non, '1.1-b',
    "les éoliennes").
exclusion([incendie_evenements_annexes, dommages_electriques, tempete_grele_neige, venues_eau_gel, recherche_fuite, debordement_cuves, vol_vandalisme, vol_cles, deteriorations_immobilieres, bris_glaces, bris_glace_plus, bris_glace_renforce, contenu_congelateur, catastrophes_naturelles, relogement_catnat, attentats, emeutes, intervention_secours], et([f(bien, panneau_solaire), non(f(formule, excellence))]), bien(panneau_solaire), non, '1.1-b',
    "les panneaux solaires et photovoltaïques si vous avez souscrit les formules Eco et Confort").
exclusion([incendie_evenements_annexes, dommages_electriques, tempete_grele_neige, venues_eau_gel, recherche_fuite, debordement_cuves, vol_vandalisme, vol_cles, deteriorations_immobilieres, bris_glaces, bris_glace_plus, bris_glace_renforce, contenu_congelateur, catastrophes_naturelles, relogement_catnat, attentats, emeutes, intervention_secours], et([f(bien, piscine), non(f(pack_piscine, oui))]), bien(piscine), non, '1.1-b',
    "les piscines, spas et jacuzzi").
exclusion([incendie_evenements_annexes, dommages_electriques, tempete_grele_neige, venues_eau_gel, recherche_fuite, debordement_cuves, vol_vandalisme, vol_cles, deteriorations_immobilieres, bris_glaces, bris_glace_plus, bris_glace_renforce, contenu_congelateur, catastrophes_naturelles, relogement_catnat, attentats, emeutes, intervention_secours], et([f(bien, plantation), non(f(pack_jardin, oui))]), bien(plantation), non, '1.1-b',
    "les plantations").
exclusion([incendie_evenements_annexes, dommages_electriques, tempete_grele_neige, venues_eau_gel, recherche_fuite, debordement_cuves, vol_vandalisme, vol_cles, deteriorations_immobilieres, bris_glaces, bris_glace_plus, bris_glace_renforce, contenu_congelateur, catastrophes_naturelles, relogement_catnat, attentats, emeutes, intervention_secours], f(local_inoccupe_12_mois, oui), tout, non, '1.1-b',
    "les locaux inoccupés ou inutilisés depuis plus de 12 mois consécutifs").

% --- Art. 1.2 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
definition(contenu, et([ou([f(bien, mobilier), f(bien, electronique), f(bien, objet_divers), f(bien, velo), f(bien, bijoux), f(bien, valeurs), f(bien, mobilier_jardin)]), concept(batiment)]), '1.2-a',
    "Tous les objets d’usage courant et les vêtements vous appartenant ou qui vous sont confiés ou appartenant à toute personne résidant avec vous ou en simple visite, contenus à l’intérieur du local d’habitation et des dépendances assurés").
exclusion([incendie_evenements_annexes, dommages_electriques, tempete_grele_neige, venues_eau_gel, recherche_fuite, debordement_cuves, vol_vandalisme, vol_cles, deteriorations_immobilieres, bris_glaces, bris_glace_plus, bris_glace_renforce, contenu_congelateur, catastrophes_naturelles, relogement_catnat, attentats, emeutes, intervention_secours], et([ou([f(lieu, cave), f(lieu, garage), f(lieu, annexe), f(lieu, abri_jardin)]), f(formule, eco)]), tout, non, '1.2-b',
    "les biens mobiliers se trouvant dans les dépendances si vous avez souscrit la formule Eco").
exclusion([incendie_evenements_annexes, dommages_electriques, tempete_grele_neige, venues_eau_gel, recherche_fuite, debordement_cuves, vol_vandalisme, vol_cles, deteriorations_immobilieres, bris_glaces, bris_glace_plus, bris_glace_renforce, contenu_congelateur, catastrophes_naturelles, relogement_catnat, attentats, emeutes, intervention_secours], et([f(bien, bijoux), non(f(option_objets_valeur, oui))]), bien(bijoux), non, '1.2-b',
    "les objets précieux, les espèces, titres et valeurs, les objets de valeur désignés").
exclusion([incendie_evenements_annexes, dommages_electriques, tempete_grele_neige, venues_eau_gel, recherche_fuite, debordement_cuves, vol_vandalisme, vol_cles, deteriorations_immobilieres, bris_glaces, bris_glace_plus, bris_glace_renforce, contenu_congelateur, catastrophes_naturelles, relogement_catnat, attentats, emeutes, intervention_secours], et([f(bien, valeurs), non(f(option_objets_valeur, oui))]), bien(valeurs), non, '1.2-b',
    "les objets précieux, les espèces, titres et valeurs, les objets de valeur désignés").
exclusion([incendie_evenements_annexes, dommages_electriques, tempete_grele_neige, venues_eau_gel, recherche_fuite, debordement_cuves, vol_vandalisme, vol_cles, deteriorations_immobilieres, bris_glaces, bris_glace_plus, bris_glace_renforce, contenu_congelateur, catastrophes_naturelles, relogement_catnat, attentats, emeutes, intervention_secours], f(bien, vehicule_moteur), bien(vehicule_moteur), non, '1.2-b',
    "les véhicules terrestres à moteur (y compris les vélos électriques circulant à plus de 25 km/h et les engins de déplacement personnel motorisés), les remorques, les caravanes, les véhicules aériens").
exclusion([incendie_evenements_annexes, dommages_electriques, tempete_grele_neige, venues_eau_gel, recherche_fuite, debordement_cuves, vol_vandalisme, vol_cles, deteriorations_immobilieres, bris_glaces, bris_glace_plus, bris_glace_renforce, contenu_congelateur, catastrophes_naturelles, relogement_catnat, attentats, emeutes, intervention_secours], f(bien, remorque), bien(remorque), non, '1.2-b',
    "les véhicules terrestres à moteur (y compris les vélos électriques circulant à plus de 25 km/h et les engins de déplacement personnel motorisés), les remorques, les caravanes, les véhicules aériens").
exclusion([incendie_evenements_annexes, dommages_electriques, tempete_grele_neige, venues_eau_gel, recherche_fuite, debordement_cuves, vol_vandalisme, vol_cles, deteriorations_immobilieres, bris_glaces, bris_glace_plus, bris_glace_renforce, contenu_congelateur, catastrophes_naturelles, relogement_catnat, attentats, emeutes, intervention_secours], f(bien, animal), bien(animal), non, '1.2-b',
    "les animaux et les végétaux").
exclusion([incendie_evenements_annexes, dommages_electriques, tempete_grele_neige, venues_eau_gel, recherche_fuite, debordement_cuves, vol_vandalisme, vol_cles, deteriorations_immobilieres, bris_glaces, bris_glace_plus, bris_glace_renforce, contenu_congelateur, catastrophes_naturelles, relogement_catnat, attentats, emeutes, intervention_secours], f(bien, plantation), bien(plantation), non, '1.2-b',
    "les animaux et les végétaux").

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
limite(incendie_evenements_annexes, '4.3', "Si vous ne pouvez produire de justificatif établi par ce professionnel datant de moins de deux ans au jour du sinistre, l’indemnisation des dommages subis par le seul conduit de fumée sera réduite de 50 %", "indemnité réduite de 50 %").
limite(incendie_evenements_annexes, '4.3', "Vous devez également vous conformer aux instructions du service public concernant le débroussaillage, à défaut de quoi l’indemnisation sera réduite de 50 %", "indemnité réduite de 50 %").

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
limite(venues_eau_gel, '4.2', "L’indemnité sera réduite de 50 % si vous ne respectez pas ces prescriptions et qu’un sinistre survient ou est aggravé de ce fait", "indemnité réduite de 50 %").
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
limite(vol_vandalisme, '4.1', "Si l’introduction a été facilitée ou aggravée par la nonconformité ou l’absence de mise en œuvre des moyens de protection et/ou de fermeture exigés aux conditions particulières, l’indemnité sera réduite de 50 %", "indemnité réduite de 50 %").
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
limite(deteriorations_immobilieres, '4.1', "Si l’introduction a été facilitée ou aggravée par la nonconformité ou l’absence de mise en œuvre des moyens de protection et/ou de fermeture exigés aux conditions particulières, l’indemnité sera réduite de 50 %", "indemnité réduite de 50 %").

% --- Art. 12.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(responsabilite).
garantie(rc_proprietaire_voisins, "Responsabilité civile du propriétaire : incendie, explosion, eau", '12.1-a~1',
    "• Envers les voisins et les tiers La garantie couvre les conséquences financières de votre responsabilité civile à raison : - des dommages matériels et immatériels consécutifs subis par les voisins et les tiers à la suite d’un incendie, d’une explosion, d’une venue d’eau ayant pris naissance dans le local d’habitation et/ou des dépendances assurés").
perimetre(rc_proprietaire_voisins, f(evenement, responsabilite)).
perimetre(rc_proprietaire_voisins, f(statut_logement, proprietaire)).
perimetre(rc_proprietaire_voisins, f(origine_rc, habitation)).
exclusion(rc_proprietaire_voisins, ou([f(victime, assure), f(victime, conjoint), f(victime, famille), f(victime, prepose)]), tout, non, '12.1-a~2',
    "Toute personne autre que : • vous-même, votre conjoint ou concubin (signataire ou non d’un PACS) non séparé, vos ascendants et descendants, • le personnel de garde ou d’entretien pendant son service").
garantie(rc_proprietaire_immeuble, "Responsabilité civile du propriétaire : accident causé par l'habitation", '12.1-a~2',
    "des dommages corporels, matériels et immatériels consécutifs causés aux tiers à la suite d’un accident occasionné pendant la période de validité du contrat par : • l’habitation désignée aux conditions particulières, y compris le terrain, les plantations, les clôtures et leurs aménagements").
perimetre(rc_proprietaire_immeuble, f(evenement, responsabilite)).
perimetre(rc_proprietaire_immeuble, f(statut_logement, proprietaire)).
perimetre(rc_proprietaire_immeuble, f(origine_rc, immeuble)).
exclusion(rc_proprietaire_immeuble, ou([f(victime, assure), f(victime, conjoint), f(victime, famille), f(victime, prepose)]), tout, non, '12.1-a~2',
    "Toute personne autre que : • vous-même, votre conjoint ou concubin (signataire ou non d’un PACS) non séparé, vos ascendants et descendants, • le personnel de garde ou d’entretien pendant son service").

% --- Art. 12.2 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(responsabilite).
garantie(rc_locataire, "Responsabilité civile du locataire : incendie, explosion, eau", '12.2-a',
    "• Envers le propriétaire La garantie couvre les conséquences financières de votre responsabilité civile de locataire vis-à-vis de votre propriétaire…• Envers les voisins et les tiers La garantie couvre les conséquences financières de votre responsabilité civile à raison des dommages matériels et immatériels consécutifs subis par les voisins et les tiers à la suite d’un incendie, d’une explosion, d’une venue d’eau ayant pris naissance dans l’habitation assurée").
perimetre(rc_locataire, f(evenement, responsabilite)).
perimetre(rc_locataire, f(statut_logement, locataire)).
perimetre(rc_locataire, f(origine_rc, habitation)).

% --- Art. 12.3 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(responsabilite).
garantie(rc_villegiature, "Responsabilité civile villégiature", '12.3',
    "La garantie couvre les conséquences financières de votre responsabilité civile locative et le recours des voisins et des tiers en raison des dommages par incendie, explosion, venue d’eau, détériorations immobilières ou bris de glaces occasionnés à une habitation que vous occupez temporairement ou dont vous êtes occupant à titre gratuit pour des séjours d’agrément d’une durée inférieure à 3 mois").
perimetre(rc_villegiature, f(evenement, responsabilite)).
perimetre(rc_villegiature, f(origine_rc, habitation)).
perimetre(rc_villegiature, f(sejour_temporaire, oui)).

% --- Art. 13.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(responsabilite).
garantie(rc_vie_privee, "Responsabilité civile vie privée", '13.1-a~1',
    "La garantie couvre les conséquences financières de la responsabilité civile que les assurés peuvent encourir dans le cadre de leur vie privée, en raison de dommages corporels, matériels et immatériels consécutifs causés aux tiers").
perimetre(rc_vie_privee, f(evenement, responsabilite)).
exclusion(rc_vie_privee, f(origine_rc, activite_professionnelle), tout, non, '13.1-a~1',
    "dans le cadre de leur vie privée").
exclusion(rc_vie_privee, ou([f(victime, assure), f(victime, conjoint)]), tout, non, '13.1-a~3',
    "le responsable du sinistre et son conjoint ou concubin (signataire ou non d’un PACS)").
exclusion(rc_vie_privee, et([f(victime, famille), f(dommage_tiers, materiel)]), tout, oui, '13.1-a~3',
    "leurs ascendants et descendants, frères et sœurs et leurs conjoints pour les dommages matériels").
exclusion(rc_vie_privee, f(victime, prepose), tout, non, '13.1-a~3',
    "les préposés attachés à votre service privé pendant la durée de leur service").

% --- Art. 22.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(litige).
definition(accident, f(domaine_litige, recours_dommage), 'S10-a/accident',
    "Tout événement soudain, imprévu et extérieur à la victime à la chose endommagée").
garantie(recours_accident, "Recours suite à accident", '22.1',
    "pour réclamer amiablement et au besoin judiciairement la réparation pécuniaire des dommages subis par vous, ou causés aux biens assurés par le contrat, lorsque ces dommages résultent d’un accident survenu au cours de votre vie privée, engagent la responsabilité d’une personne n’ayant pas la qualité d’assuré au titre du contrat, et ne peuvent être indemnisés au titre d’une garantie du présent contrat").
perimetre(recours_accident, f(evenement, litige)).
perimetre(recours_accident, concept(accident)).
garantie(defense_penale, "Défense pénale", '22.1',
    "pour vous défendre devant les juridictions répressives et les commissions administratives, si vous êtes poursuivi pour contravention ou délit à la suite d’un événement dont les conséquences pécuniaires à l’égard du tiers sont couvertes par la garantie responsabilité civile du contrat").
perimetre(defense_penale, f(evenement, litige)).
perimetre(defense_penale, f(domaine_litige, defense_penale)).

% --- Art. 22.2 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(litige).
garantie(protection_juridique, "Protection juridique (option)", '22.2',
    "Nous intervenons quand un litige survient dans votre vie privée ou salariée").
perimetre(protection_juridique, f(evenement, litige)).
perimetre(protection_juridique, ou([f(domaine_litige, travail), f(domaine_litige, logement), f(domaine_litige, travaux), f(domaine_litige, sante), f(domaine_litige, consommation), f(domaine_litige, administration), f(domaine_litige, voisinage), f(domaine_litige, employeur_domestique), f(domaine_litige, location_vacances), f(domaine_litige, bateau), f(domaine_litige, association), f(domaine_litige, famille)])).
circonstance(protection_juridique, f(option_protection_juridique, oui), '22.2',
    "(garantie optionnelle)").

% --- Art. 12.4 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(responsabilite).
exclusion([rc_proprietaire_voisins, rc_proprietaire_immeuble, rc_locataire, rc_villegiature], f(origine_rc, vehicule_moteur), tout, non, '12.4-a',
    "les dommages de toute nature causés par des véhicules à moteur (y compris les vélos électriques circulant à plus de 25 km/h et les engins de déplacement personnel motorisés) soumis à la législation sur l’assurance automobile obligatoire, ou qui y seraient soumis en France,").
exclusion([rc_proprietaire_voisins, rc_proprietaire_immeuble, rc_locataire, rc_villegiature], f(bien_confie, oui), tout, non, '12.4-a',
    "les dommages subis par les biens dont vous avez la propriété, la conduite ou la garde,").

% --- Art. 13.3 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(responsabilite).
exclusion([rc_vie_privee], f(origine_rc, habitation), tout, non, '13.3-a~1',
    "les dommages matériels et immatériels consécutifs à un incendie, une explosion, une venue d’eau ayant pris naissance dans un local dont vous êtes propriétaire, locataire ou occupant à titre gratuit, sauf pour la garantie « Responsa bilité civile fêtes familiales » lorsque la garantie est acquise,").
exclusion([rc_vie_privee], f(origine_rc, animal_autre), tout, non, '13.3-a~1',
    "les dommages causés par tous les animaux (y compris les chevaux) autres que les animaux de compagnie. Pour les animaux ayant mordu une personne ou un autre animal, la garantie couvre le coût de leurs visites sanitaires obligatoires,").
exclusion([rc_vie_privee], f(origine_rc, contrat), tout, non, '13.3-a~1',
    "les conséquences pécuniaires des responsabilités résultant de l’exécution, de la mauvaise exécution et de l’inexécution d’un contrat, sauf lors de vos activités bénévoles,").
exclusion([rc_vie_privee], f(origine_rc, vehicule_moteur), tout, non, '13.3-a~2',
    "tous véhicules terrestres à moteur (y compris les vélos électriques circulant à plus de 25 km/h et les engins de déplacement personnel motorisés) soumis à l’obligation d’assurance et leurs remorques ou matériels attelés, ou qui y seraient soumis en France, à l’exception des cas décrits ci-avant,").
exclusion([rc_vie_privee], f(origine_rc, chien_dangereux), tout, non, '13.3-a~2',
    "les dommages causés par les chiens de première catégorie (chiens d’attaque) et deuxième catégorie (chiens de garde et de défense) tels que définis dans la loi n°99-5 du 6 janvier 1999 modifiée par la loi n°2008-582 du 20 juin 2008 et soumis à l’obligation d’assurance,").
exclusion([rc_vie_privee], f(origine_rc, chasse_sport), tout, non, '13.3-a~2',
    "la pratique du ball-trap, de la chasse, y compris les faits des chiens en action de chasse, des sports aériens, de tout sport à titre professionnel,").
exclusion([rc_vie_privee], f(origine_rc, chasse_sport), tout, non, '13.3-a~2',
    "votre participation à toutes épreuves, courses ou compétitions sportives, soumises à une obligation d’assurance légale, ainsi qu’à leurs essais préparatoires,").
exclusion([rc_vie_privee], f(origine_rc, chasse_sport), tout, non, '13.3-a~2',
    "toute activité physique ou sportive que vous exercez en tant que membre d’un club ou d’un groupement sportif agréé conformément à la loi du 29 octobre 1975. Toutefois, la garantie reste acquise en cas d’absence ou d’insuffisance d’assurance du club").
exclusion([rc_vie_privee], f(origine_rc, immeuble), tout, non, '13.3-a~2',
    "tout bien immobilier dont vous êtes propriétaire ou copropriétaire,").

% --- Art. 22.3 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(litige).
exclusion([recours_accident, defense_penale, protection_juridique], f(domaine_litige, activite_professionnelle), tout, non, '22.3-a~1',
    "d’une activité professionnelle non salariée ou de l’administration d’une entreprise, d’une collectivité ou d’une association lorsque cette dernière emploie un ou des salariés,").
exclusion([recours_accident, defense_penale, protection_juridique], f(domaine_litige, vehicule_moteur), tout, non, '22.3-a~2',
    "de l’achat, la vente, la propriété, la location (sauf pour la location de courte durée n’excédant pas deux mois), l’entretien, la réparation, la conduite ou l’assurance d’un véhicule terrestre à moteur (sauf les engins de jardinage et les jouets télécommandés),").
exclusion([recours_accident, defense_penale, protection_juridique], f(domaine_litige, divorce_succession), tout, non, '22.3-a~2',
    "de l’application du Livre I du Code civil, excepté les litiges découlant des incapacités (sauvegarde de justice, tutelle, curatelle) et de la filiation (légitime, naturelle, adoptive),").
exclusion([recours_accident, defense_penale, protection_juridique], f(domaine_litige, divorce_succession), tout, non, '22.3-a~2',
    "des régimes matrimoniaux, des successions (excepté les litiges découlant des successions en ligne directe), des donations entre vifs et legs (excepté les litiges découlant des donations entre vifs et legs en ligne directe),").
