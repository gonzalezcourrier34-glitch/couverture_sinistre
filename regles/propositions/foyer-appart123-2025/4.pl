% --- Art. 4 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-18 ---
evenement_traduit(vol).
evenement_traduit(incendie).
evenement_traduit(explosion).
evenement_traduit(foudre).
evenement_traduit(degat_eaux).
evenement_traduit(tempete).
evenement_traduit(bris).
evenement_traduit(autre).
evenement_traduit(electricite).
evenement_traduit(mazout).
evenement_traduit(catastrophe_naturelle).
evenement_traduit(attentat).
evenement_traduit(fumee).
evenement_traduit(vandalisme).
evenement_traduit(merule).
garantie(frais_sauvetage, "Frais de sauvetage", '4~1',
    "• frais de sauvetage").
perimetre(frais_sauvetage, f(sinistre_assure, oui)).
perimetre(frais_sauvetage, ou([f(couverture_rc_locative, oui), f(couverture_contenu, oui)])).
garantie(frais_deblai_demolition, "Frais de déblai et de démolition", '4~1',
    "• frais de déblai et de démolition des biens assurés, en ce compris les frais d'abattage, d'élagage et d'enlèvement de l'arbre ou du pylône qui a causé les dégâts").
perimetre(frais_deblai_demolition, f(sinistre_assure, oui)).
perimetre(frais_deblai_demolition, ou([f(couverture_rc_locative, oui), f(couverture_contenu, oui)])).
garantie(frais_nettoyage, "Frais de nettoyage des locaux endommagés", '4~1',
    "• frais de nettoyage des locaux endommagés après travaux").
perimetre(frais_nettoyage, f(sinistre_assure, oui)).
perimetre(frais_nettoyage, ou([f(couverture_rc_locative, oui), f(couverture_contenu, oui)])).
garantie(frais_conservation_entreposage, "Frais de conservation et d'entreposage", '4~1',
    "• frais de conservation et d'entreposage des biens sauvés").
perimetre(frais_conservation_entreposage, f(sinistre_assure, oui)).
perimetre(frais_conservation_entreposage, ou([f(couverture_rc_locative, oui), f(couverture_contenu, oui)])).
garantie(frais_logement_provisoire, "Frais de logement provisoire", '4~1',
    "• frais de logement provisoire pendant la durée normale de non habitabilité de votre bâtiment").
perimetre(frais_logement_provisoire, f(sinistre_assure, oui)).
perimetre(frais_logement_provisoire, ou([f(couverture_rc_locative, oui), f(couverture_contenu, oui)])).
garantie(chomage_immobilier, "Chômage immobilier", '4~1',
    "• le chômage immobilier pendant la durée normale de reconstruction de votre bâtiment.").
perimetre(chomage_immobilier, f(sinistre_assure, oui)).
perimetre(chomage_immobilier, ou([f(couverture_rc_locative, oui), f(couverture_contenu, oui)])).
circonstance(chomage_immobilier, non(f(cumul_chomage_logement, oui)), '4~1',
    "Cette indemnité ne peut se cumuler pour une même période et un même logement sinistré avec la garantie des frais de logement provisoire").
limite(chomage_immobilier, '4~1', "et ce pour une période maximale de 18 mois", "18 mois").
garantie(frais_eau_mazout_canalisation, "Frais liés aux dégâts causés par l'eau et le mazout (canalisation)", '4~1',
    "• frais liés aux garanties dégâts causés par l'eau et le mazout c'est-à-dire les frais liés à la recherche, la réparation ou le remplacement de la partie de canalisation à l'origine du sinistre y compris les radiateurs, ainsi que la remise en état consécutive.").
perimetre(frais_eau_mazout_canalisation, f(sinistre_assure, oui)).
perimetre(frais_eau_mazout_canalisation, ou([f(couverture_rc_locative, oui), f(couverture_contenu, oui)])).
perimetre(frais_eau_mazout_canalisation, ou([f(evenement, degat_eaux), f(evenement, mazout)])).
limite(frais_eau_mazout_canalisation, '4~1', "Nous prenons en charge ces frais jusqu'à concurrence de maximum 1.100 EUR lorsque les biens assurés n'ont pas été endommagés", "1.100 EUR").
garantie(moins_value_batiment, "Moins-value du bâtiment", '4~1',
    "Nous couvrons également la moins-value du bâtiment pouvant en résulter et fixée par l'expert, jusqu'à concurrence de maximum 2.200 EUR par sinistre").
perimetre(moins_value_batiment, f(sinistre_assure, oui)).
perimetre(moins_value_batiment, ou([f(couverture_rc_locative, oui), f(couverture_contenu, oui)])).
perimetre(moins_value_batiment, ou([f(evenement, degat_eaux), f(evenement, mazout)])).
limite(moins_value_batiment, '4~1', "jusqu'à concurrence de maximum 2.200 EUR par sinistre", "2.200 EUR").
garantie(avance_fonds, "Avance de fonds", '4~2',
    "• l'avance de fonds jusqu'à 7.700 EUR, pour couvrir les frais de première nécessité et les réparations en cas de non habitabilité du bâtiment. Cette avance n'implique aucune reconnaissance de la prise en charge du sinistre et est déduite de l'indemnité définitive éventuelle").
perimetre(avance_fonds, f(sinistre_assure, oui)).
perimetre(avance_fonds, ou([f(couverture_rc_locative, oui), f(couverture_contenu, oui)])).
circonstance(avance_fonds, f(non_habitabilite, oui), '4~2',
    "en cas de non habitabilité du bâtiment").
limite(avance_fonds, '4~2', "jusqu'à 7.700 EUR", "7.700 EUR").
garantie(frais_medicaux, "Frais médicaux et pharmaceutiques", '4~2',
    "• frais médicaux et pharmaceutiques à concurrence de 2.000 EUR.").
perimetre(frais_medicaux, f(sinistre_assure, oui)).
perimetre(frais_medicaux, ou([f(couverture_rc_locative, oui), f(couverture_contenu, oui)])).
limite(frais_medicaux, '4~2', "à concurrence de 2.000 EUR", "2.000 EUR").
garantie(frais_expertise, "Frais d'expertise", '4~2',
    "• frais d'expertise c'est-à-dire les frais et honoraires de votre expert et le cas échéant ceux d'un tiers-expert, calculés en pourcentage des indemnités dues hors TVA, conformément au barème repris ci-après, à l'exclusion de celles relatives aux assurances de responsabilité et des pertes indirectes.").
perimetre(frais_expertise, f(sinistre_assure, oui)).
perimetre(frais_expertise, ou([f(couverture_rc_locative, oui), f(couverture_contenu, oui)])).
exclusion(frais_expertise, f(assurance_responsabilite, oui), tout, oui, '4~2',
    "à l'exclusion de celles relatives aux assurances de responsabilité").
exclusion(frais_expertise, f(pertes_indirectes, oui), tout, oui, '4~2',
    "et des pertes indirectes").
garantie(frais_expertise_contestation, "Frais d'expertise en cas de contestation", '4~2',
    "Uniquement pour les frais d'expertise dépassant le barème prévu ci-dessus : en cas de contestation sur l'évaluation des dommages suite à un sinistre, vous désignez un expert qui fixera l'indemnité en concertation avec notre expert. Nous avançons les frais de cet expert, et le cas échéant ceux du tiers-expert. Toutefois, si vous n'obtenez pas raison, ces frais restent définitivement à votre charge et doivent nous être remboursés.").
perimetre(frais_expertise_contestation, f(sinistre_assure, oui)).
perimetre(frais_expertise_contestation, ou([f(couverture_rc_locative, oui), f(couverture_contenu, oui)])).
circonstance(frais_expertise_contestation, f(frais_expertise_depassent_bareme, oui), '4~2',
    "Uniquement pour les frais d'expertise dépassant le barème prévu ci-dessus").
circonstance(frais_expertise_contestation, f(contestation_evaluation, oui), '4~2',
    "en cas de contestation sur l'évaluation des dommages suite à un sinistre").
obligation(frais_expertise_contestation, non(f(obtenu_raison, oui)), faux, non, '4~2',
    "si vous n'obtenez pas raison, ces frais restent définitivement à votre charge et doivent nous être remboursés").
