% --- Art. 3.1.11 : proposition rédigée par le modèle — mistral:mistral-large-4-0 (proposition écartée), 2026-11-24 ---
evenement_traduit(litige).
garantie(protection_juridique_immeuble, "Protection juridique immeuble (option)", '3.1.11.1',
    "La Compagnie assume sur le plan pénal la défense de l’Assuré lorsque, à l’occasion d’un sinistre couvert par les présentes conditions spéciales, il est poursuivi du chef : n d’infractions aux lois et règlements relatifs au bâtiment désigné ; n d’homicide ou de blessures involontaires du fait du bâtiment désigné. 3.1.11.1.2 Recours La Compagnie exerce également le recours contre un tiers dont la responsabilité civile extracontractuelle est engagée").
perimetre(protection_juridique_immeuble, f(evenement, litige)).
perimetre(protection_juridique_immeuble, ou([f(domaine_litige, defense_penale), f(domaine_litige, recours_dommage)])).
exclusion(protection_juridique_immeuble, f(victime, prepose), tout, non, '3.1.11.1',
    "en cas de dommages subis par les préposés et par les personnes occasionnellement mises à la disposition de l’Assuré").
exclusion(protection_juridique_immeuble, ou([f(victime, assure), f(victime, conjoint)]), tout, non, '3.1.11.1',
    "en cas de litige entre personnes dont la responsabilité civile est couverte par la présente assurance").
exclusion(protection_juridique_immeuble, ou([f(domaine_litige, activite_professionnelle), f(origine_rc, activite_professionnelle)]), tout, non, '3.1.11.1',
    "en cas de dommages relevant de la responsabilité civile après livraison de produits, après exécution des travaux ou professionnelle").
exclusion(protection_juridique_immeuble, non(f(option_pj_immeuble, oui)), tout, oui, '3.1.11',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ protection juridique immeuble ” est accordée").
limite(protection_juridique_immeuble, '3.1.11.3', "Les frais énoncés au point 3.1.11.2 sont pris en charge par la Compagnie à concurrence de 8.658 € par sinistre", "8658").
