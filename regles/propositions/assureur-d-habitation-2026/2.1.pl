% --- Art. 2.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(incendie).
evenement_traduit(explosion).
evenement_traduit(fumee).
evenement_traduit(foudre).
evenement_traduit(heurt).
evenement_traduit(autre).
definition(contenu, non(f(bien, element_batiment)), '2.1-a',
    "SUBIS PAR VOS BIENS").
definition(incendie, f(flammes, oui), '2.1-a',
    "l ’incendie, c’est-à-dire la combustion avec flammes en dehors d’un foyer normal, y compris ceux occasionnés par la fumée et les émanations qui s’en dégagent, ainsi que par l’intervention des services de secours à cette occasion").
definition(explosion, f(evenement, explosion), '2.1-a',
    "l ’explosion, c’est-à-dire l’action subite et violente d’une surpression ou d’une dépression").
definition(enfumage_accidentel, f(evenement, fumee), '2.1-a',
    "l ’enfumage accidentel, c’est-à-dire l’émission accidentelle de fumées ou de vapeurs corrosives à l’intérieur des locaux assurés").
definition(foudre, f(evenement, foudre), '2.1-a',
    "la chute de la foudre, c’est-à-dire du fait de l’ébranlement ou de la calcination causés directement par l’impact de la foudre ou encore du fait de la chute d’un objet causée par la foudre, y compris aux installations électriques équipant les locaux").
definition(choc_vehicule, f(evenement, heurt), '2.1-a',
    "le choc d’un véhicule, c’est-à-dire le choc d’un véhicule dont ni vous, ni votre conjoint ou concubin, ni vos enfants, n’avez la propriété, la conduite ou la garde").
definition(chute_engins_volants, f(evenement, autre), '2.1-a',
    "la chute d’engins volants ou d’objets provenant de ces derniers").
definition(mur_du_son, f(evenement, autre), '2.1-a',
    "le mur du son, c’est-à-dire l’ébranlement consécutif au franchissement du mur du son").
garantie(incendie_evenements_annexes, "Incendie et événements annexes", '2.1-a',
    "La garantie couvre les dommages matériels causés par : • l ’incendie, c’est-à-dire la combustion avec flammes en dehors d’un foyer normal, y compris ceux occasionnés par la fumée et les émanations qui s’en dégagent, ainsi que par l’intervention des services de secours à cette occasion, • l ’explosion, c’est-à-dire l’action subite et violente d’une surpression ou d’une dépression, • l ’enfumage accidentel, c’est-à-dire l’émission accidentelle de fumées ou de vapeurs corrosives à l’intérieur des locaux assurés, • la chute de la foudre, c’est-à-dire du fait de l’ébranlement ou de la calcination causés directement par l’impact de la foudre ou encore du fait de la chute d’un objet causée par la foudre, y compris aux installations électriques équipant les locaux, • le choc d’un véhicule, c’est-à-dire le choc d’un véhicule dont ni vous, ni votre conjoint ou concubin, ni vos enfants, n’avez la propriété, la conduite ou la garde. Le véhicule doit être identifié, sinon vous devez déposer une plainte auprès des autorités.La garantie couvre également les dommages matériels causés par la chute d’engins volants ou d’objets provenant de ces derniers, • le mur du son, c’est-à-dire l’ébranlement consécutif au franchissement du mur du son.").
perimetre(incendie_evenements_annexes, ou([f(evenement, incendie), f(evenement, explosion), f(evenement, fumee), f(evenement, foudre), f(evenement, heurt), f(evenement, autre)])).
perimetre(incendie_evenements_annexes, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(incendie_evenements_annexes, concept(batiment)).
circonstance(incendie_evenements_annexes, si(f(evenement, heurt), et([f(auteur, tiers), ou([f(vehicule_identifie, oui), f(plainte_deposee, oui)])])), '2.1-a',
    "le choc d’un véhicule, c’est-à-dire le choc d’un véhicule dont ni vous, ni votre conjoint ou concubin, ni vos enfants, n’avez la propriété, la conduite ou la garde. Le véhicule doit être identifié, sinon vous devez déposer une plainte auprès des autorités.").
exclusion(incendie_evenements_annexes, et([ou([f(evenement, incendie), f(evenement, explosion)]), ou([f(bien, electronique), f(bien, appareil_electromenager), f(bien, appareil_audiovisuel), f(bien, appareil_informatique)]), f(bien_a_l_origine_sinistre, oui)]), tout, oui, '2.1-b',
    "les dommages aux appareils électriques ou électroniques qui ont pour origine l’incendie ou l’explosion prenant naissance dans l’appareil. Ces dommages sont indemnisés au titre de la garantie dommages électriques.").
exclusion(incendie_evenements_annexes, et([f(evenement, fumee), f(cheminee_ouverte, oui)]), tout, oui, '2.1-b',
    "la fumée provenant de cheminées à feu apparent (dits « à l’ouvert »).").
