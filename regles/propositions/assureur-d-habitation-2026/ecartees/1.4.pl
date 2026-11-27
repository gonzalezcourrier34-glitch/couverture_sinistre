% --- Art. 1.4 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
definition(veranda, et([f(construction_vitree, oui), f(construction_close, oui), f(adjacente_habitation, oui)]), '1.4',
    "Il s'agit d'une construction totalement ou partiellement vitrée entièrement close et couverte, adjacente au local d'habitation ou à ses dépendances.").
extension(bien, et([concept(veranda), f(option_veranda, oui)]), '1.4',
    "Cette garantie doit être spécialement mentionnée aux conditions particulières. Il s'agit d'une construction totalement ou partiellement vitrée entièrement close et couverte, adjacente au local d'habitation ou à ses dépendances.").
exclusion(tous, et([concept(veranda), f(bien, serre)]), tout, oui, '1.4-a',
    "les serres").
exclusion(tous, et([concept(veranda), f(manque_entretien, oui)]), tout, oui, '1.4-a',
    "les dommages résultant de la vétusté de la véranda").
