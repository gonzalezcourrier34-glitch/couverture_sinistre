% --- Art. 3.1.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
evenement_traduit(incendie).
evenement_traduit(explosion).
evenement_traduit(foudre).
evenement_traduit(electricite).
evenement_traduit(fumee).
evenement_traduit(heurt).
evenement_traduit(vol).
evenement_traduit(vandalisme).
evenement_traduit(attentat).
evenement_traduit(conflit_du_travail).
definition(incendie, et([f(flammes, oui), ou([f(embrasement, oui), f(chaleur_sans_feu, non)])]), '3.1.1.1',
    "L'incendie, c'est-à-dire la destruction par des flammes se propageant ou susceptibles de se propager en dehors de leur domaine normal ou d'objets dont la destination n'est pas, à ce moment, de brûler").
garantie(incendie_base, "Incendie et périls de base", '3.1.1.1',
    "La Compagnie assure les biens désignés, contre les périls suivants : 3.1.1.1.1 L'incendie, c'est-à-dire la destruction par des flammes se propageant ou susceptibles de se propager en dehors de leur domaine normal ou d'objets dont la destination n'est pas, à ce moment, de brûler ; 3.1.1.1.2 L'explosion ou l'implosion ; 3.1.1.1.3 La chute de la foudre ; 3.1.1.1.4 L'électrocution d'animaux ; 3.1.1.1.5 Les fumées et les suies ; 3.1.1.1.6 Les dégâts occasionnés au mobilier assuré et au bâtiment désigné par un événement soudain, résultant de l'action subite de la chaleur ou par le contact direct et immédiat avec un foyer ou une substance incandescente, même lorsqu'il n'y a pas eu embrasement, ni commencement d'incendie.").
perimetre(incendie_base, ou([f(evenement, incendie), f(evenement, explosion), f(evenement, foudre), et([f(evenement, electricite), f(bien, animal)]), f(evenement, fumee), et([ou([f(evenement, incendie), f(evenement, autre)]), f(chaleur_sans_feu, oui)])])).
perimetre(incendie_base, concept(batiment_designe)).
circonstance(incendie_base, si(f(evenement, incendie), concept(incendie)), '3.1.1.1',
    "L'incendie, c'est-à-dire la destruction par des flammes se propageant ou susceptibles de se propager en dehors de leur domaine normal ou d'objets dont la destination n'est pas, à ce moment, de brûler").
garantie(decongelation, "Décongélation denrées", '3.1.1.2',
    "à la décongélation de denrées alimentaires périssables contenues dans un surgélateur, congélateur ou réfrigérateur à usage domestique suite à un changement de température résultant d'un arrêt dans la production du froid imputable à la survenance d'un sinistre couvert par les présentes conditions spéciales ou par les conditions spéciales de la garantie \"dégâts électriques\"").
perimetre(decongelation, f(bien, denrees_alimentaires)).
circonstance(decongelation, ou([f(evenement, incendie), f(evenement, explosion), f(evenement, foudre), f(evenement, electricite)]), '3.1.1.2',
    "imputable à la survenance d'un sinistre couvert par les présentes conditions spéciales ou par les conditions spéciales de la garantie \"dégâts électriques\"").
garantie(linge, "Dégradation linge", '3.1.1.2',
    "à la dégradation du contenu des sèche-linge ou lave-linge à la suite d'un sinistre relevant de l'un des périls prévus aux présentes conditions spéciales de la garantie \"incendie et périls assimilés\" et aux conditions spéciales de la garantie \"dégâts électriques\"").
perimetre(linge, f(bien, objet_divers)).
perimetre(linge, f(lieu, logement)).
circonstance(linge, ou([f(evenement, incendie), f(evenement, explosion), f(evenement, foudre), f(evenement, electricite)]), '3.1.1.2',
    "à la suite d'un sinistre relevant de l'un des périls prévus aux présentes conditions spéciales de la garantie \"incendie et périls assimilés\" et aux conditions spéciales de la garantie \"dégâts électriques\"").
garantie(heurt, "Heurt", '3.1.1.2',
    "au heurt, sauf : n les dégâts causés au contenu par un Assuré ou par un animal lui appartenant ou lui ayant été confié ; n les dégâts causés au bâtiment désigné en cas de déménagement du mobilier ; n les dégâts au bien ou à l'animal ayant causé le heurt ; n les dégâts ne résultant pas directement d'un choc entre deux corps durs ; n les dégâts causés par la grêle.").
perimetre(heurt, f(evenement, heurt)).
perimetre(heurt, concept(batiment_designe)).
exclusion(heurt, ou([f(auteur, assure), f(bien, animal)]), tout, oui, '3.1.1.2',
    "les dégâts causés au contenu par un Assuré ou par un animal lui appartenant ou lui ayant été confié").
exclusion(heurt, et([f(bien, element_batiment), f(demenagement, oui)]), tout, non, '3.1.1.2',
    "les dégâts causés au bâtiment désigné en cas de déménagement du mobilier").
exclusion(heurt, f(bien_a_l_origine_sinistre, oui), tout, oui, '3.1.1.2',
    "les dégâts au bien ou à l'animal ayant causé le heurt").
exclusion(heurt, f(choc_deux_corps_durs, non), tout, non, '3.1.1.2',
    "les dégâts ne résultant pas directement d'un choc entre deux corps durs").
exclusion(heurt, f(alea_tempete, grele), tout, non, '3.1.1.2',
    "les dégâts causés par la grêle").
garantie(degradations_vol, "Dégradations lors de vol", '3.1.1.2',
    "aux dégradations immobilières causées à l'occasion d'un vol ou d'une tentative de vol dans les locaux à occupation régulière ainsi que le vol de parties de bâtiment sauf : n les dommages ou le vol des biens se trouvant à l'extérieur du bâtiment ; n lorsque le bâtiment est en cours de construction, transformation ou rénovation, à moins que l'Assuré démontre que cette circonstance n'a pas contribué à la survenance ou à l'aggravation des conséquences du sinistre.").
perimetre(degradations_vol, f(evenement, vol)).
perimetre(degradations_vol, f(bien, element_batiment)).
exclusion(degradations_vol, et([ou([f(lieu, jardin), f(lieu, terrasse)]), non(f(bien, element_batiment))]), tout, oui, '3.1.1.2',
    "les dommages ou le vol des biens se trouvant à l'extérieur du bâtiment").
exclusion(degradations_vol, et([f(travaux_construction, oui), non(f(lien_causal_travaux, non))]), tout, oui, '3.1.1.2',
    "lorsque le bâtiment est en cours de construction, transformation ou rénovation, à moins que l'Assuré démontre que cette circonstance n'a pas contribué à la survenance ou à l'aggravation des conséquences du sinistre").
exclusion(degradations_vol, f(occupation_irreguliere, oui), tout, oui, '3.1.1.2',
    "aux dégradations immobilières causées à l’occasion d’un vol ou d’une tentative de vol dans les locaux à occupation régulière").
garantie(vandalisme, "Vandalisme", '3.1.1.2',
    "aux dommages causés par un acte de vandalisme ou de malveillance au bâtiment désigné pour autant que les conditions suivantes soient remplies simultanément : n l'Assuré est propriétaire du bâtiment ; n le bâtiment fait l'objet d'une occupation régulière ; n le bâtiment n'est pas en cours de construction, ni de transformation, ni de rénovation. L'indemnisation des dégâts matériels causés par vandalisme ou malveillance est consentie sans application de la règle proportionnelle à concurrence de 2.500 € par sinistre.").
perimetre(vandalisme, f(evenement, vandalisme)).
perimetre(vandalisme, f(bien, element_batiment)).
perimetre(vandalisme, concept(batiment_designe)).
exclusion(vandalisme, f(statut_logement, locataire), tout, oui, '3.1.1.2',
    "l’Assuré est propriétaire du bâtiment").
exclusion(vandalisme, f(occupation_irreguliere, oui), tout, oui, '3.1.1.2',
    "le bâtiment fait l’objet d’une occupation régulière").
exclusion(vandalisme, f(travaux_construction, oui), tout, oui, '3.1.1.2',
    "le bâtiment n’est pas en cours de construction, ni de transformation, ni de rénovation").
limite(vandalisme, '3.1.1.2', "L'indemnisation des dégâts matériels causés par vandalisme ou malveillance est consentie sans application de la règle proportionnelle à concurrence de 2.500 € par sinistre.", "2500 EUR").
garantie(attentats, "Attentats et conflits du travail", '3.1.1.2',
    "aux attentats et conflits du travail : La Compagnie prend en charge à concurrence de 745.000 € par sinistre les dégâts causés directement aux biens désignés : n par des personnes tierces prenant part à de tels événements ; n qui résulteraient de mesures prises dans les cas précités par une autorité légalement constituée pour la sauvegarde et la protection des biens désignés. En cas de sinistre, l'Assuré s'engage à accomplir, dans les plus brefs délais, toutes les démarches en vue de l'indemnisation des dégâts matériels subis. L'Assuré s'engage à ne pas réclamer à la Compagnie, les indemnités relatives aux dégâts matériels à concurrence desquels il a été ou pourra être indemnisé par tout tiers. En cas de double paiement, l'Assuré doit rembourser à la Compagnie les indemnités que celle-ci lui a versées. Sur base de l'autorisation délivrée par les autorités publiques, la Compagnie se réserve le droit de suspendre cette garantie moyennant l'envoi d'une lettre recommandée. La suspension prend cours 7 jours après la notification faite au Preneur d'assurance.").
perimetre(attentats, ou([f(evenement, attentat), f(evenement, conflit_du_travail)])).
perimetre(attentats, concept(batiment_designe)).
obligation(attentats, f(plainte_deposee, oui), faux, non, '3.1.1.2',
    "En cas de sinistre, l'Assuré s'engage à accomplir, dans les plus brefs délais, toutes les démarches en vue de l'indemnisation des dégâts matériels subis.").
limite(attentats, '3.1.1.2', "La Compagnie prend en charge à concurrence de 745.000 € par sinistre les dégâts causés directement aux biens désignés", "745000 EUR").
exclusion([incendie_base, decongelation, linge, heurt, degradations_vol, vandalisme, attentats], f(option_incendie, non), tout, oui, '3.1.1',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ incendie et périls assimilés ” est accordée.").
