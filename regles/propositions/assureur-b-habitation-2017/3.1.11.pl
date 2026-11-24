% --- Art. 3.1.11 : proposition rédigée par le modèle — mistral:mistral-large-4-0, 2026-11-24 ---
evenement_traduit(litige).
garantie(protection_juridique_immeuble_defense_penale, "Défense pénale immeuble", '3.1.11.1',
    "La Compagnie assume sur le plan pénal la défense de l’Assuré lorsque, à l’occasion d’un sinistre couvert par les présentes conditions spéciales, il est poursuivi du chef : n d’infractions aux lois et règlements relatifs au bâtiment désigné ; n d’homicide ou de blessures involontaires du fait du bâtiment désigné.").
perimetre(protection_juridique_immeuble_defense_penale, f(evenement, litige)).
perimetre(protection_juridique_immeuble_defense_penale, f(option_protection_juridique, oui)).
perimetre(protection_juridique_immeuble_defense_penale, concept(batiment_designe)).
circonstance(protection_juridique_immeuble_defense_penale, ou([f(motif_poursuite_penale, infraction_batiment), f(motif_poursuite_penale, homicide_blessures_involontaires)]), '3.1.11.1',
    "il est poursuivi du chef : n d’infractions aux lois et règlements relatifs au bâtiment désigné ; n d’homicide ou de blessures involontaires du fait du bâtiment désigné").
limite(protection_juridique_immeuble_defense_penale, '3.1.11.3', "Les frais énoncés au point 3.1.11.2 sont pris en charge par la Compagnie à concurrence de 8.658 € par sinistre.", "8658").
garantie(protection_juridique_immeuble_recours_tiers, "Recours contre tiers immeuble", '3.1.11.1',
    "La Compagnie exerce également le recours contre un tiers dont la responsabilité civile extracontractuelle est engagée, pour obtenir l’indemnisation : n des dommages corporels encourus par un Assuré au titre de la garantie responsabilité civile immeuble ; n des dommages matériels causés aux biens de l’Assuré, ainsi qu’aux dommages immatériels qui en sont la conséquence.").
perimetre(protection_juridique_immeuble_recours_tiers, f(evenement, litige)).
perimetre(protection_juridique_immeuble_recours_tiers, f(option_protection_juridique, oui)).
perimetre(protection_juridique_immeuble_recours_tiers, f(auteur, tiers)).
circonstance(protection_juridique_immeuble_recours_tiers, ou([f(dommage_tiers, corporel), f(dommage_tiers, materiel)]), '3.1.11.1',
    "pour obtenir l’indemnisation : n des dommages corporels encourus par un Assuré au titre de la garantie responsabilité civile immeuble ; n des dommages matériels causés aux biens de l’Assuré, ainsi qu’aux dommages immatériels qui en sont la conséquence").
limite(protection_juridique_immeuble_recours_tiers, '3.1.11.3', "Les frais énoncés au point 3.1.11.2 sont pris en charge par la Compagnie à concurrence de 8.658 € par sinistre.", "8658").
garantie(protection_juridique_immeuble_insolvabilite_tiers, "Insolvabilité des tiers", '3.1.11.4',
    "La Compagnie accorde sa garantie lorsqu’il résulte des renseignements obtenus que le tiers considéré comme responsable est insolvable. L’intervention de la Compagnie se fera à concurrence de 8.658 € par sinistre, pour les dommages et intérêts alloués par les Tribunaux en réparation des dommages corporels et/ ou des dommages matériels subis par les Assurés lorsque le tiers responsable de l’accident est déclaré insolvable après exécution de toutes voies de recours.").
perimetre(protection_juridique_immeuble_insolvabilite_tiers, f(evenement, litige)).
perimetre(protection_juridique_immeuble_insolvabilite_tiers, f(option_protection_juridique, oui)).
perimetre(protection_juridique_immeuble_insolvabilite_tiers, f(auteur, tiers)).
circonstance(protection_juridique_immeuble_insolvabilite_tiers, f(tiers_insolvable, oui), '3.1.11.4',
    "lorsqu’il résulte des renseignements obtenus que le tiers considéré comme responsable est insolvable").
circonstance(protection_juridique_immeuble_insolvabilite_tiers, ou([f(dommage_tiers, corporel), f(dommage_tiers, materiel)]), '3.1.11.4',
    "pour les dommages et intérêts alloués par les Tribunaux en réparation des dommages corporels et/ ou des dommages matériels subis par les Assurés lorsque le tiers responsable de l’accident est déclaré insolvable après exécution de toutes voies de recours").
limite(protection_juridique_immeuble_insolvabilite_tiers, '3.1.11.4', "L’intervention de la Compagnie se fera à concurrence de 8.658 € par sinistre", "8658").
accessoire(protection_juridique_immeuble_insolvabilite_tiers).
exclusion([protection_juridique_immeuble_defense_penale, protection_juridique_immeuble_recours_tiers, protection_juridique_immeuble_insolvabilite_tiers], ou([f(victime, prepose), f(victime_mise_a_disposition, oui)]), tout, oui, '3.1.11.1',
    "en cas de dommages subis par les préposés et par les personnes occasionnellement mises à la disposition de l’Assuré").
exclusion([protection_juridique_immeuble_defense_penale, protection_juridique_immeuble_recours_tiers, protection_juridique_immeuble_insolvabilite_tiers], et([f(auteur, assure), f(victime, assure)]), tout, oui, '3.1.11.1',
    "en cas de litige entre personnes dont la responsabilité civile est couverte par la présente assurance").
exclusion([protection_juridique_immeuble_defense_penale, protection_juridique_immeuble_recours_tiers, protection_juridique_immeuble_insolvabilite_tiers], ou([f(type_responsabilite_exclue, apres_livraison_produits), f(type_responsabilite_exclue, apres_execution_travaux), f(type_responsabilite_exclue, professionnelle)]), tout, oui, '3.1.11.1',
    "en cas de dommages relevant de la responsabilité civile après livraison de produits, après exécution des travaux ou professionnelle").
