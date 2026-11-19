% --- Art. 3.1.9 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
garantie(frais_sauvetage, "Frais de sauvetage", '3.1.9.1',
    "La Compagnie prend en charge les frais engagés pour arrêter ou limiter le sinistre, mais aussi pour soustraire les biens désignés aux effets d'un péril assuré.").
exclusion(frais_sauvetage, non(f(option_incendie, oui)), tout, oui, '3.1.9',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ incendie et périls assimilés ” est souscrite.").
limite(frais_sauvetage, '3.1.9', "Les frais de sauvetage sont pris en charge à concurrence des frais exposés.", "frais exposés").
garantie(frais_deblai_demolition, "Frais de déblai et démolition", '3.1.9.2',
    "La Compagnie prend en charge les frais nécessaires à la reconstruction ou à la reconstitution des biens assurés et sinistrés.").
exclusion(frais_deblai_demolition, non(f(option_incendie, oui)), tout, oui, '3.1.9',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ incendie et périls assimilés ” est souscrite.").
limite(frais_deblai_demolition, '3.1.9', "Ces frais, à l'exception des frais de sauvetage, sont pris en charge à concurrence de 1.000.000 € maximum par sinistre", "1000000").
garantie(frais_conservation_entreposage, "Frais de conservation et d'entreposage", '3.1.9.3',
    "La Compagnie prend en charge les frais nécessaires à la conservation ou à l'entreposage des biens sauvés.").
exclusion(frais_conservation_entreposage, non(f(option_incendie, oui)), tout, oui, '3.1.9',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ incendie et périls assimilés ” est souscrite.").
limite(frais_conservation_entreposage, '3.1.9', "Ces frais, à l'exception des frais de sauvetage, sont pris en charge à concurrence de 1.000.000 € maximum par sinistre", "1000000").
garantie(frais_logement_provisoire, "Frais de logement provisoire", '3.1.9.4',
    "Lorsque les locaux à usage privé sont devenus inutilisables, la Compagnie prend en charge les frais nécessaires au logement provisoire dans un hôtel ou ailleurs pendant une durée maximale de quatre-vingt-dix jours à concurrence d'un montant maximum de 80 € par nuit par personne vivant habituellement au domicile de l'Assuré.").
perimetre(frais_logement_provisoire, f(residence_principale_inhabitable, oui)).
exclusion(frais_logement_provisoire, non(f(option_incendie, oui)), tout, oui, '3.1.9',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ incendie et périls assimilés ” est souscrite.").
limite(frais_logement_provisoire, '3.1.9.4', "pendant une durée maximale de quatre-vingt-dix jours à concurrence d'un montant maximum de 80 € par nuit par personne vivant habituellement au domicile de l'Assuré", "80€/nuit/personne, max 90 jours").
garantie(chomage_immobilier, "Chômage immobilier", '3.1.9.5',
    "L'intervention de la Compagnie est limitée à la durée normale de reconstruction du bâtiment, avec un maximum de 24 mois. Cette indemnisation ne peut se cumuler, pour une même période, avec les frais de logement précités.").
exclusion(chomage_immobilier, non(f(option_incendie, oui)), tout, oui, '3.1.9',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ incendie et périls assimilés ” est souscrite.").
limite(chomage_immobilier, '3.1.9.5', "avec un maximum de 24 mois", "24 mois").
garantie(frais_depollution, "Frais de dépollution", '3.1.9.6',
    "La Compagnie prend en charge les frais d'assainissement des terrains pollués par l'écoulement d'huile minérale et frais de transport et de déblaiement des terres polluées par l'écoulement d'huile minérale suite à un sinistre couvert à concurrence de 25.000 €").
perimetre(frais_depollution, f(cause_pollution, huile_minerale)).
circonstance(frais_depollution, f(reglementation_pollution_respectee, oui), '3.1.9.6',
    "que la règlementation en la matière ait été respectée").
exclusion(frais_depollution, et([f(travaux_construction, oui), non(f(lien_causal_travaux, oui))]), tout, oui, '3.1.9.6',
    "Si le bâtiment est en cours de transformation, construction ou reconstruction, l'extension de garantie est inopérante à moins que l'Assuré ne démontre que cette circonstance n'a pas contribué à la survenance ou à l'aggravation des conséquences du sinistre.").
exclusion(frais_depollution, non(f(option_incendie, oui)), tout, oui, '3.1.9',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ incendie et périls assimilés ” est souscrite.").
limite(frais_depollution, '3.1.9.6', "à concurrence de 25.000 €", "25000").
garantie(frais_remise_etat_jardins, "Frais de remise en état des jardins", '3.1.9.7',
    "La Compagnie prend en charge les frais nécessaires à la remise en état des jardins et des plantations endommagées par un péril couvert.").
exclusion(frais_remise_etat_jardins, non(f(option_incendie, oui)), tout, oui, '3.1.9',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ incendie et périls assimilés ” est souscrite.").
limite(frais_remise_etat_jardins, '3.1.9.7', "Si les biens désignés n'ont pas été endommagés, l'intervention de la Compagnie se limitera à 3.000€ sur base des justificatifs fournis par l'Assuré.", "3000").
garantie(frais_expertise, "Frais d'expertise", '3.1.9.8',
    "La Compagnie prend en charge le remboursement à l'Assuré des honoraires (toutes taxes éventuelles comprises) qu'il a effectivement payés à l'expert qu'il a désigné pour l'évaluation des dégâts aux biens désignés").
exclusion(frais_expertise, non(f(option_incendie, oui)), tout, oui, '3.1.9',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ incendie et périls assimilés ” est souscrite.").
limite(frais_expertise, '3.1.9.8', "sans que cette indemnisation ne puisse dépasser les montants résultant de l'application du barème repris ci-dessous", "selon barème (max 21.617 €)").
garantie(recours_locataires_occupants, "Recours des locataires ou occupants", '3.1.9.9',
    "La Compagnie couvre les frais que l'Assuré pourrait être amené à supporter en qualité soit de bailleur, en vertu de l'article 1721, deuxième alinéa du Code civil, à l'égard des locataires, soit de propriétaire à l'égard des occupants autres que locataires.").
exclusion(recours_locataires_occupants, non(f(option_incendie, oui)), tout, oui, '3.1.9',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ incendie et périls assimilés ” est souscrite.").
limite(recours_locataires_occupants, '3.1.9', "Ces frais, à l'exception des frais de sauvetage, sont pris en charge à concurrence de 1.000.000 € maximum par sinistre", "1000000").
garantie(recours_tiers, "Recours des tiers", '3.1.9.10',
    "La Compagnie couvre les frais que l'Assuré peut encourir en vertu des articles 1382 à 1386 du Code civil pour les dommages matériels causés par un sinistre garanti se communiquant à des biens qui sont la propriété de tiers.").
exclusion(recours_tiers, non(f(option_incendie, oui)), tout, oui, '3.1.9',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ incendie et périls assimilés ” est souscrite.").
limite(recours_tiers, '3.1.9', "Ces frais, à l'exception des frais de sauvetage, sont pris en charge à concurrence de 1.000.000 € maximum par sinistre", "1000000").
accessoire(frais_sauvetage).
accessoire(frais_deblai_demolition).
accessoire(frais_conservation_entreposage).
accessoire(frais_logement_provisoire).
accessoire(chomage_immobilier).
accessoire(frais_depollution).
accessoire(frais_remise_etat_jardins).
accessoire(frais_expertise).
accessoire(recours_locataires_occupants).
accessoire(recours_tiers).
