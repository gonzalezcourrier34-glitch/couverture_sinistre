% --- Art. 2.5 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(vol).
evenement_traduit(vandalisme).
definition(dependances, ou([f(lieu, garage), f(lieu, cave), f(lieu, grenier), f(lieu, annexe)]), 'S10-a/dependances',
    "Ce sont les locaux destinés à un usage autre que le local d’habitation ou l’exercice d’une profession situés en dehors de la « verticalité » du local d’habitation. Sont également considérés comme dépendances les caves et les garages situés dans les immeubles collectifs.").
definition(objets_precieux, ou([f(bien, bijoux), f(bien, valeurs)]), 'S10-a/objets-de-valeur',
    "Objets précieux (bijoux, pierreries, les perles non montées, argenterie massive, articles d’orfèvrerie et autres ouvrages en métaux précieux), espèces, titres et valeurs, objets d’art et fourrures d’un montant unitaire supérieur à 2 000 € (tapis noués à la main, tapisseries, tableaux, statues et statuettes, sculptures, vases, ménagères en métal argenté, fourrures, vêtements de haute couture), le mobilier précieux, les timbres et les collections de timbres dès lors que vous souhaitez le(s) désigner spécifiquement dans vos conditions particulières, soit en valeur expertisée, soit en valeur déclarée.").
extension(papiers_identite, ou([f(pays, royaume_uni), f(pays, allemagne), f(pays, france), f(pays, luxembourg), f(pays, autre_ue), et([f(lieu, logement), f(effraction, oui)])]), '2.5-a',
    "au vol des papiers d’identité, du permis de conduire, du certificat d’immatriculation (ex. carte grise) et de la carte de crédit, dans l’une des circonstances suivantes : - survenu à l’intérieur des locaux assurés par effraction ou escalade des locaux, menaces physiques, usage des clés du sociétaire dès lors qu’elles ont fait l’objet d’un vol ou introduction par fausse qualité, - en tous lieux de l’Union européenne, du Royaume-Uni de Grande-Bretagne et d’Irlande du Nord.").
extension(cles, et([f(plainte_deposee, oui), ou([f(pays, royaume_uni), f(pays, allemagne), f(pays, france), f(pays, luxembourg), f(pays, autre_ue)])]), '2.5-a',
    "au vol des clés, en tous lieux de l’Union européenne, du Royaume-Uni de Grande-Bretagne et d’Irlande du Nord, de votre local d’habitation et/ou des dépendances assurés dès lors que le dépôt de plainte fait état d’un vol, pour les frais de remplacement à l’identique des canons de serrure, des verrous équipant les locaux assurés ou des télécommandes permettant d’ouvrir ces derniers et leurs portails d’accès.").
extension(objets_precieux, et([f(formule, excellence), f(option_objets_valeur, oui), f(lieu, residence_secondaire)]), '2.5-b',
    "si l’option « objets de valeur » est souscrite, le vol des objets précieux vous appartenant de la résidence principale dans votre résidence secondaire lorsque vous y séjournez.").
extension(cles_vehicule, et([f(plainte_deposee, oui), ou([f(pays, royaume_uni), f(pays, allemagne), f(pays, france), f(pays, luxembourg), f(pays, autre_ue)])]), '2.5-b',
    "les frais de remplacement des clés, barillets, système de télécommande de véhicule en cas de vol des clés de celui-ci en tous lieux de l’Union européenne, du Royaume-Uni de Grande-Bretagne et d’Irlande du Nord, dès lors que le dépôt de plainte fait état d’un vol").
extension(plaque_signaletique, f(lieu, autre_batiment), '2.5-b',
    "le vol de votre plaque signalétique professionnelle située à l’extérieur de votre local d’habitation").
garantie(vol_vandalisme, "Vol, tentative de vol, vandalisme et sabotage", '2.5-a',
    "La garantie couvre la disparition, la destruction ou la détérioration des biens assurés résultant : • d’un vol, • d’une tentative de vol, • d ’un acte de vandalisme ou de sabotage, lorsque ces méfaits sont commis à l’intérieur des locaux assurés, par effraction ou escalade de ces locaux et ayant laissé des traces apparentes.").
perimetre(vol_vandalisme, ou([f(evenement, vol), f(evenement, vandalisme)])).
perimetre(vol_vandalisme, ou([concept(batiment), concept(dependances)])).
circonstance(vol_vandalisme, ou([et([f(effraction, oui), f(traces_apparentes, oui)]), f(violence, oui), et([f(vol_cles, oui), f(dans_48h, oui)]), f(introduction_fausse_qualite, oui)]), '2.5-a',
    "La garantie est étendue, pour autant que vous puissiez en apporter la preuve : • au vol dans les locaux assurés par menaces physiques ou violences physiques sur vous, • au vol à la suite du vol des clés, exclusivement dans les 48 h qui suivent l’heure à laquelle vous avez eu connaissance du vol des clés, • au vol à la suite d’une introduction par fausse qualité dans les locaux assurés.").
exclusion(vol_vandalisme, et([ou([f(auteur, famille), f(auteur, personnel_prive)]), non(f(plainte_nominative, oui))]), tout, oui, '2.5-c',
    "les vols, tentatives de vol, actes de vandalisme ou actes de sabotage dont seraient auteurs ou complices les membres de votre famille (article 311-12 du Code pénal) ou vos préposés pendant leur service, sauf si une plainte nominative est déposée à leur encontre").
exclusion(vol_vandalisme, f(cles_deposees_exterieur, oui), tout, oui, '2.5-c',
    "les vols des clés déposées, sans protection, à l’extérieur des locaux y compris dans une boîte à clé ou dans une boîte à lettres ainsi que toutes leurs conséquences").
exclusion(vol_vandalisme, et([concept(objets_precieux), concept(dependances)]), tout, oui, '2.5-c',
    "les vols des objets précieux dans les dépendances").
exclusion(vol_vandalisme, et([concept(dependances), f(formule, eco)]), tout, oui, '2.5-c',
    "les vols dans les dépendances, si vous avez souscrit la formule Eco").
exclusion(vol_vandalisme, et([f(objet_art_fourrure, oui), f(valeur_superieure_2000, oui), ou([concept(dependances), f(lieu, residence_secondaire)])]), tout, oui, '2.5-c',
    "les vols des objets d’art et de fourrures - lorsque leur valeur excède 2 000 € - dans les dépendances et les résidences secondaires").
exclusion(vol_vandalisme, et([ou([f(lieu, terrasse), f(lieu, jardin), non(f(construction_close, oui))]), non(f(pack_jardin, oui))]), tout, oui, '2.5-c',
    "les vols, tentatives de vol, actes de vandalisme ou actes de sabotage commis sur les terrasses, les balcons, dans les jardins et dans les locaux non entièrement clos ou couverts, sauf si le Pack Jardin est souscrit").
exclusion(vol_vandalisme, f(bien, rampe_pmr), tout, oui, '2.5-c',
    "le vol des rampes amovibles d’accès pour personne à mobilité réduite").
