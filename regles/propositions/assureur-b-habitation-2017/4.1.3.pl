% --- Art. 4.1.3 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(litige).
garantie(protection_juridique, "Protection juridique (option)", '4.1.3.1',
    "La Compagnie s’engage : 4.1.3.1.1 à assurer la défense pénale de l’Assuré devant les tribunaux répressifs").
perimetre(protection_juridique, f(evenement, litige)).
perimetre(protection_juridique, ou([f(domaine_litige, defense_penale), f(domaine_litige, recours_dommage), f(domaine_litige, voisinage)])).
circonstance(protection_juridique, f(option_protection_juridique, oui), '4.1.3',
    "la garantie “ protection juridique ” est accordée").
limite(protection_juridique, '4.1.3.3', "Les frais énoncés au point 4.1.3.2 sont pris en charge par la Compagnie à concurrence de 8.658 € par sinistre", "8658").
