% --- Art. 22.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(litige).
definition(accident, f(domaine_litige, recours_dommage), 'S10-a/accident',
    "Tout événement soudain, imprévu et extérieur à la victime à la chose endommagée").
garantie(recours_accident, "Recours suite à accident", '22.1',
    "pour réclamer amiablement et au besoin judiciairement la réparation pécuniaire des dommages subis par vous, ou causés aux biens assurés par le contrat, lorsque ces dommages résultent d’un accident survenu au cours de votre vie privée, engagent la responsabilité d’une personne n’ayant pas la qualité d’assuré au titre du contrat, et ne peuvent être indemnisés au titre d’une garantie du présent contrat").
perimetre(recours_accident, f(evenement, litige)).
perimetre(recours_accident, concept(accident)).
exclusion(recours_accident, f(enjeu_moins_300, oui), tout, non, '27',
    "enjeu financier du litige en principal en dessous duquel nous n’intervenons pas et dont le montant est fixé à 300 €").
garantie(defense_penale, "Défense pénale", '22.1',
    "pour vous défendre devant les juridictions répressives et les commissions administratives, si vous êtes poursuivi pour contravention ou délit à la suite d’un événement dont les conséquences pécuniaires à l’égard du tiers sont couvertes par la garantie responsabilité civile du contrat").
perimetre(defense_penale, f(evenement, litige)).
perimetre(defense_penale, f(domaine_litige, defense_penale)).
