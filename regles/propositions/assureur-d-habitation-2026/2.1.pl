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
