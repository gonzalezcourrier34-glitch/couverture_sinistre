% --- Art. S25 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
exclusion(tous, ou([f(intentionnel, oui), et([f(participation_rixe, oui), non(f(legitime_defense, oui))])]), tout, oui, 'S25',
    "les dommages causés intentionnellement ou frauduleusement par vous ou par un complice, ou résultant de votre ou de sa participation à une action violente ou à une rixe (sauf légitime défense) et sous réserves des dispositions de l'article L. 121-2 du Code").
exclusion(tous, f(amende, oui), tout, oui, 'S25',
    "les paiements des amendes auxquelles vous pourriez être condamné").
exclusion(tous, f(manque_entretien, oui), tout, oui, 'S25',
    "de la garantie des dommages subis par vos biens, ceux qui résultent directement d'un défaut de réparation ou d'entretien indispensables vous incombant et dont vous aviez connaissance").
exclusion(tous, f(armes_illegales, oui), tout, oui, 'S25',
    "les dommages causés par les armes détenues illégalement").
exclusion(tous, ou([f(catastrophe, tremblement_terre), f(catastrophe, eruption_volcanique), f(catastrophe, raz_de_maree), f(evenement, catastrophe_naturelle)]), tout, oui, 'S25',
    "les dommages occasionnés par un tremblement de terre, une éruption volcanique, un raz-de-marée ou cataclysme naturel. Cette exclusion ne s'applique pas à la garantie « Catastrophes naturelles »").
exclusion(tous, et([ou([f(cause_guerre, oui), f(cause_nucleaire, oui)]), non(f(evenement, attentat))]), tout, oui, 'S25',
    "les dommages résultant : - de la guerre civile ou étrangère, - de tout combustible, produit ou déchet radioactif, de tout engin destiné à irradier ou à exploser par modification du noyau de l'atome ainsi que leur décontamination, sauf pour les dommages matériels directs causés par un attentat ou un acte de terrorisme.").
