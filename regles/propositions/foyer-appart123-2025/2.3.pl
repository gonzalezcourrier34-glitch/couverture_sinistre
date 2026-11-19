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
