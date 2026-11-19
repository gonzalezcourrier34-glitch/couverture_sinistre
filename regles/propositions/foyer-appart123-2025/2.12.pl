% --- Art. 2.12 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-18 ---
evenement_traduit(merule).
garantie(degats_merule, "Dégâts dus à la mérule", '2.12',
    "Nous couvrons les dégâts dus à la mérule survenue postérieurement à la prise d’effet de la garantie.").
perimetre(degats_merule, f(evenement, merule)).
perimetre(degats_merule, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(degats_merule, concept(batiment)).
circonstance(degats_merule, f(merule_apres_prise_effet, oui), '2.12',
    "survenue postérieurement à la prise d’effet de la garantie").
