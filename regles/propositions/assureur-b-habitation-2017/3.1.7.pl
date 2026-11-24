% --- Art. 3.1.7 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
evenement_traduit(bris).
evenement_traduit(vol).
evenement_traduit(accident).
garantie(materiel_multimedia_bris, "Bris du matériel multimédia", '3.1.7.1',
    "La Compagnie couvre tout bris ou destruction accidentel résultant d’une chute, d’un choc ou de la pénétration d’un corps étranger et qui rend nécessaire la réparation ou le remplacement du matériel multimédia. Sont également couverts au titre de cette garantie les équipements suivants : n équipement d’alarme et de surveillance, en activité ou au repos, pendant les opérations de démontage, de déplacement sur les lieux assurés ou de remontage nécessitées pour leur entretien ou leur révision, pour autant que la mise en exploitation desdits matériels ait donné entière satisfaction ; n équipement domotique").
perimetre(materiel_multimedia_bris, f(evenement, bris)).
perimetre(materiel_multimedia_bris, ou([f(bien, electronique), f(bien, equipement_alarme_surveillance), f(bien, equipement_domotique)])).
circonstance(materiel_multimedia_bris, f(option_materiel_multimedia, oui), '3.1.7',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “matériel multimédia” est accordée.").
obligation(materiel_multimedia_bris, si(ou([f(lieu, vehicule), et([f(bien, vehicule_moteur), f(lieu, voie_publique)])]), et([f(vehicule_ferme_cle, oui), non(f(materiel_laisse_en_vue, oui))])), faux, non, '3.1.7.4',
    "Lorsque les biens assurés se trouvent à l’intérieur d’un véhicule inoccupé, la garantie intervient uniquement si les deux conditions suivantes sont remplies simultanément : n le véhicule a été fermé à clé ; n le matériel assuré n’a pas été laissé en vue à l’intérieur de l’habitacle du véhicule").
exclusion(materiel_multimedia_bris, et([f(bien, equipement_alarme_surveillance), f(mise_en_exploitation_satisfaction, non)]), bien(equipement_alarme_surveillance), non, '3.1.7.1',
    "pour autant que la mise en exploitation desdits matériels ait donné entière satisfaction").
limite(materiel_multimedia_bris, '3.1.7.1', "1 0.000 € par sinistre lorsque les conditions particulières mentionnent que la formule «Privilège» est souscrite", "10000").
limite(materiel_multimedia_bris, '3.1.7.1', "5.000 € par sinistre lorsque les conditions particulières mentionnent que la formule «Active» est souscrite", "5000").
garantie(materiel_multimedia_vol, "Vol du matériel multimédia", '3.1.7.1',
    "Sous réserve que la garantie vol ait été accordée, la Compagnie couvre également : n le vol du matériel multimédia lorsque le vol a eu lieu à l’extérieur du bâtiment désigné ; n le vol de ces équipements se trouvant à l’intérieur d’un véhicule terrestre automoteur à condition que ledit véhicule soit également volé ou qu’il y ait effraction caractérisée du véhicule ; n le vol de ces équipements qu’un Assuré déplace à l’occasion d’un séjour temporaire dans un bâtiment situé n’importe où dans le monde, pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes").
perimetre(materiel_multimedia_vol, f(evenement, vol)).
perimetre(materiel_multimedia_vol, ou([f(bien, electronique), f(bien, equipement_alarme_surveillance), f(bien, equipement_domotique)])).
circonstance(materiel_multimedia_vol, ou([non(concept(batiment_designe)), et([f(lieu, vehicule), ou([f(vehicule_vole, oui), f(effraction, oui)])]), et([f(sejour_temporaire, oui), f(plainte_deposee, oui)])]), '3.1.7.1',
    "le vol du matériel multimédia lorsque le vol a eu lieu à l’extérieur du bâtiment désigné ; n le vol de ces équipements se trouvant à l’intérieur d’un véhicule terrestre automoteur à condition que ledit véhicule soit également volé ou qu’il y ait effraction caractérisée du véhicule ; n le vol de ces équipements qu’un Assuré déplace à l’occasion d’un séjour temporaire dans un bâtiment situé n’importe où dans le monde, pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes").
circonstance(materiel_multimedia_vol, f(option_materiel_multimedia, oui), '3.1.7',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “matériel multimédia” est accordée.").
obligation(materiel_multimedia_vol, si(ou([f(lieu, vehicule), et([f(bien, vehicule_moteur), f(lieu, voie_publique)])]), et([f(vehicule_ferme_cle, oui), non(f(materiel_laisse_en_vue, oui))])), faux, non, '3.1.7.4',
    "Lorsque les biens assurés se trouvent à l’intérieur d’un véhicule inoccupé, la garantie intervient uniquement si les deux conditions suivantes sont remplies simultanément : n le véhicule a été fermé à clé ; n le matériel assuré n’a pas été laissé en vue à l’intérieur de l’habitacle du véhicule").
exclusion(materiel_multimedia_vol, f(option_vol, non), tout, oui, '3.1.7.1',
    "Sous réserve que la garantie vol ait été accordée").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(proprietaire, hote), tout, oui, '3.1.7.2',
    "le matériel dont l'Assuré n'est pas propriétaire").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(cause_dommage, virus), tout, non, '3.1.7.2',
    "les pertes liées à l'action d'un virus et tous préjudices consécutifs").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(vice_defaut_connu, oui), tout, non, '3.1.7.2',
    "les pertes ou dommages dus à des vices ou défauts qui existaient à la date d'effet de la présente assurance et qui étaient connus de l'Assuré ou de ses mandataires").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], ou([f(manque_entretien, oui), f(fonctionnement_defectueux, oui)]), tout, non, '3.1.7.2',
    "les pertes ou dommages qui sont la conséquence directe : n des effets continuels de l’exploitation (usure) ; n d’un fonctionnement défectueux").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(garantie_fabricant, oui), tout, non, '3.1.7.2',
    "les pertes ou dommages dont le fabricant ou le fournisseur est légalement ou contractuellement responsable").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(bien, consommable), bien(consommable), non, '3.1.7.2',
    "les pertes ou dommages causés aux lampes,tubes, bandes transporteuses, fusibles, joints, courroies, chaînes").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(type_dommage, rayure_ou_ecaillement), tout, non, '3.1.7.2',
    "les défauts d'ordre esthétique, tels que les bosses, égratignures, rayures ou écaillements").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(evenement, electricite), tout, oui, '3.1.7.2',
    "les dommages d'origine électrique").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], f(bien, denrees_alimentaires), bien(denrees_alimentaires), non, '3.1.7.2',
    "les dommages causés au contenu des appareils").
exclusion([materiel_multimedia_bris, materiel_multimedia_vol], ou([f(auteur, assure), f(auteur, famille), et([f(auteur, personnel_prive), ou([f(heures_service, oui), non(ou([f(effraction, oui), f(violence, oui)]))])])]), tout, oui, '3.1.7.2',
    "les vols commis par ou avec la complicité de ou du : n Preneur d’assurance, son conjoint, leurs ascendants ou descendants ainsi que les conjoints de ces personnes ; n l’Assuré ; n toute personne au service de l’Assuré pendant les heures de service et, si ces vols ont été commis en dehors de celles-ci, autrement que par effraction ou avec violence. En ce qui concerne les pièces mentionnées aux points").
