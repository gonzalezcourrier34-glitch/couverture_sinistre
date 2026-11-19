% --- Art. 3.1.7 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
evenement_traduit(bris).
evenement_traduit(vol).
garantie(materiel_multimedia_bris, "Bris du matériel multimédia", '3.1.7.1',
    "La Compagnie couvre tout bris ou destruction accidentel résultant d’une chute, d’un choc ou de la pénétration d’un corps étranger et qui rend nécessaire la réparation ou le remplacement du matériel multimédia. Sont également couverts au titre de cette garantie les équipements suivants : n équipement d’alarme et de surveillance, en activité ou au repos, pendant les opérations de démontage, de déplacement sur les lieux assurés ou de remontage nécessitées pour leur entretien ou leur révision, pour autant que la mise en exploitation desdits matériels ait donné entière satisfaction ; n équipement domotique").
perimetre(materiel_multimedia_bris, f(evenement, bris)).
perimetre(materiel_multimedia_bris, ou([f(bien, materiel_multimedia), f(bien, equipement_alarme_surveillance), f(bien, equipement_domotique)])).
circonstance(materiel_multimedia_bris, f(mise_en_exploitation_satisfaction, oui), '3.1.7.1',
    "pour autant que la mise en exploitation desdits matériels ait donné entière satisfaction").
obligation(materiel_multimedia_bris, et([f(lieu, vehicule_moteur), f(vehicule_inoccupe, oui), f(vehicule_ferme_cle, oui), non(f(materiel_laisse_en_vue, oui))]), faux, non, '3.1.7.4.2',
    "Lorsque les biens assurés se trouvent à l'intérieur d'un véhicule inoccupé, la garantie intervient uniquement si les deux conditions suivantes sont remplies simultanément : le véhicule a été fermé à clé ; le matériel assuré n'a pas été laissé en vue à l'intérieur de l'habitacle du véhicule.").
limite(materiel_multimedia_bris, '3.1.7.1', "1 0.000 € par sinistre lorsque les conditions particulières mentionnent que la formule «Privilège» est souscrite", "10000").
limite(materiel_multimedia_bris, '3.1.7.1', "5.000 € par sinistre lorsque les conditions particulières mentionnent que la formule «Active» est souscrite", "5000").
garantie(materiel_multimedia_vol, "Vol du matériel multimédia", '3.1.7.1',
    "Sous réserve que la garantie vol ait été accordée, la Compagnie couvre également : n le vol du matériel multimédia lorsque le vol a eu lieu à l’extérieur du bâtiment désigné ; n le vol de ces équipements se trouvant à l’intérieur d’un véhicule terrestre automoteur à condition que ledit véhicule soit également volé ou qu’il y ait effraction caractérisée du véhicule ; n le vol de ces équipements qu’un Assuré déplace à l’occasion d’un séjour temporaire dans un bâtiment situé n’importe où dans le monde, pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes").
perimetre(materiel_multimedia_vol, f(evenement, vol)).
perimetre(materiel_multimedia_vol, ou([f(bien, materiel_multimedia), f(bien, equipement_alarme_surveillance), f(bien, equipement_domotique)])).
circonstance(materiel_multimedia_vol, f(garantie_vol_accordee, oui), '3.1.7.1',
    "Sous réserve que la garantie vol ait été accordée").
circonstance(materiel_multimedia_vol, ou([f(lieu, voie_publique), si(f(lieu, vehicule_moteur), ou([f(vehicule_vole, oui), f(effraction, oui)])), si(f(sejour_temporaire, oui), f(plainte_deposee, oui))]), '3.1.7.1',
    "le vol du matériel multimédia lorsque le vol a eu lieu à l’extérieur du bâtiment désigné ; n le vol de ces équipements se trouvant à l’intérieur d’un véhicule terrestre automoteur à condition que ledit véhicule soit également volé ou qu’il y ait effraction caractérisée du véhicule ; n le vol de ces équipements qu’un Assuré déplace à l’occasion d’un séjour temporaire dans un bâtiment situé n’importe où dans le monde, pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(proprietaire, hote), tout, oui, '3.1.7.2',
    "le matériel dont l'Assuré n'est pas propriétaire").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(cause_dommage, virus), tout, oui, '3.1.7.2',
    "les pertes liées à l'action d'un virus et tous préjudices consécutifs").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(vice_defaut_connu, oui), tout, oui, '3.1.7.2',
    "les pertes ou dommages dus à des vices ou défauts qui existaient à la date d'effet de la présente assurance et qui étaient connus de l'Assuré ou de ses mandataires").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], ou([f(manque_entretien, oui), f(fonctionnement_defectueux, oui)]), tout, oui, '3.1.3.2',
    "les pertes ou dommages qui sont la conséquence directe : des effets continuels de l'exploitation (usure) ; d'un fonctionnement défectueux").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], et([f(defaut_fonctionnement, oui), non(f(bien_a_l_origine_sinistre, oui))]), tout, oui, '3.1.7.2',
    "les frais exposés pour réparer des défauts de fonctionnement, sauf si ces défauts sont la conséquence d'une perte ou d'un dommage indemnisable causé aux matériels assurés").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(entretien, oui), tout, oui, '3.1.7.2',
    "les frais d'entretien des matériels assurés, y compris le coût des pièces remplacées pendant les travaux d'entretien").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(garantie_fabricant, oui), tout, oui, '3.1.7.2',
    "les pertes ou dommages dont le fabricant ou le fournisseur est légalement ou contractuellement responsable").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(perte_indirecte, oui), tout, oui, '3.1.7.2',
    "les pertes indirectes de quelque nature que ce soit").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(bien, lampe_tube_bande_fusible_joint_courroie_chaine), tout, oui, '3.1.7.2',
    "les pertes ou dommages causés aux lampes,tubes, bandes transporteuses, fusibles, joints, courroies, chaînes").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(type_dommage, rayure_ou_ecaillement), tout, oui, '3.1.7.2',
    "les défauts d'ordre esthétique, tels que les bosses, égratignures, rayures ou écaillements").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(perte_donnees, oui), tout, oui, '3.1.7.2',
    "les pertes de données").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(cause_dommage, electricite), tout, oui, '3.1.7.2',
    "les dommages d'origine électrique").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(montant_dommage, inferieur_60), tout, oui, '3.1.7.2',
    "les dommages d'un montant inférieur à 60 €").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(contenu_appareil, oui), tout, oui, '3.1.7.2',
    "les dommages causés au contenu des appareils").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], ou([f(auteur, assure), f(auteur, famille), f(auteur, personnel_prive), f(auteur, preneur)]), tout, oui, '3.1.7.2.15',
    "les vols commis par ou avec la complicité de ou du : Preneur d'assurance, son conjoint, leurs ascendants ou descendants ainsi que les conjoints de ces personnes ; l'Assuré ; toute personne au service de l'Assuré pendant les heures de service et, si ces vols ont été commis en dehors de celles-ci, autrement que par effraction ou avec violence").
