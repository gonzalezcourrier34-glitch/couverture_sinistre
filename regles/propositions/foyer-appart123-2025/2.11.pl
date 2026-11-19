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
