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
obligation(vol_batiment, f(serrure_surete, oui), faux, oui, '3.1.6.4',
    "portes donnant sur l’extérieur ou sur les parties communes de l’immeuble : au moins une serrure de sûreté ou un verrou de sûreté").
limite(vol_batiment, '3.1.6.3', "à concurrence de 40% du montant indiqué aux conditions particulières au titre du contenu, pour les objets tels que meubles d’époque et objets de valeur", "40 % du contenu").
limite(vol_batiment, '3.1.6.3', "concernant les timbres de collection, l’indemnité par timbre ne pourra être supérieure à 500 €", "500 € par timbre").
limite(vol_batiment, '3.1.6.3', "à concurrence de 1500 € par sinistre pour l’ensemble constitué de l’argent comptant", "1 500 € (750 € hors clefs)").
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
exclusion([vol_batiment, vandalisme_vol, vol_annexes, remplacement_cles, vol_monde_sejour, vol_privilege_concierge, vol_privilege_jardin, vol_agression], ou([f(auteur, assure), f(auteur, famille), et([f(auteur, personnel_prive), non(ou([f(effraction, oui), f(violence, oui)]))])]), tout, oui, '3.1.6.2',
    "les vols commis par ou avec la complicité de ou du : n Preneur d'assurance, son conjoint, leurs ascendants ou descendants ainsi que les conjoints de ces personnes ; n l'Assuré ; n toute personne au service de l'Assuré pendant les heures de service et, si ces vols ont été commis en dehors de celles-ci, autrement que par effraction ou avec violence.").
exclusion([vol_batiment, vandalisme_vol, vol_annexes, remplacement_cles, vol_monde_sejour, vol_privilege_concierge, vol_privilege_jardin, vol_agression], ou([f(bien, vehicule_moteur), et([f(bien, remorque), non(ou([f(lieu, logement), f(lieu, cave), f(lieu, grenier), f(lieu, garage)]))])]), tout, oui, '3.1.6.2',
    "les vols de véhicules automoteurs – à l'exception des engins de jardinage –, des remorques non enfermées dans le bâtiment désigné, ainsi que le vol de leurs accessoires et de leur contenu").
exclusion([vol_batiment, vandalisme_vol, vol_annexes, remplacement_cles, vol_monde_sejour, vol_privilege_concierge, vol_privilege_jardin, vol_agression], et([ou([f(lieu, jardin), f(lieu, voie_publique), f(lieu, parties_communes), f(lieu, autre_batiment)]), non(ou([f(bien, mobilier_jardin), f(bien, plantation)])), non(f(lieu, logement))]), tout, oui, '3.1.6.2',
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
