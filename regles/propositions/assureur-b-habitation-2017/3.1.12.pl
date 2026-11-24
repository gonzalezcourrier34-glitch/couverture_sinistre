% --- Art. 3.1.12 : proposition rédigée par le modèle — aucun : la réponse du modèle a été coupée (16000 tokens), 2026-11-24 ---
evenement_traduit(assistance).
garantie(assistance_urgence, "Assistance d’urgence", '3.1.12.2',
    "Assureur B Assistance intervient dans les frais en cas de situation d’urgence afin de prévenir ou de limiter les dommages, ou pour effectuer une réparation urgente et provisoire à l’habitation de l’Assuré ou à une installation fixe").
perimetre(assistance_urgence, f(evenement, assistance)).
perimetre(assistance_urgence, concept(batiment_designe)).
circonstance(assistance_urgence, f(urgence_habitation, oui), '3.1.12.1',
    "Urgent ou urgence : Des conditions où un dommage soudain et imprévisible : n rend l’habitation du bénéficiaire dangereuse ou peu sûre, n entraîne un risque de dommage supplémentaire à l’habitation du bénéficiaire et/ou aux biens immeubles qu’elle contient, et/ou n rend l’habitation de l’Assuré inhabitable").
exclusion(assistance_urgence, et([f(anciennete_garantie, moins_30_jours), ou([f(objet_assistance, fuite_eau), f(objet_assistance, chauffage_central), f(objet_assistance, ouverture)])]), tout, non, '3.1.12.6',
    "Un délai d’attente de trente jours calendaires s’applique à compter de la prise d’effet de la garantie pour les sinistres liés : n aux fuites et évacuation d’eaux ; n au chauffage central ; n aux ouvertures de la maison (porte, fenêtre, serrure)").
exclusion(assistance_urgence, f(intervention_mandatee, non), tout, oui, '3.1.12.3',
    "Une intervention qui n’a pas été demandée au moment des faits ou qui a été organisée sans l’accord d’Assureur B Assistance, ne relève pas de la garantie").
exclusion(assistance_urgence, f(manque_entretien, oui), tout, non, '3.1.12.5',
    "les frais consécutifs à des signes de vétusté normale, d’usure ou d’altération").
exclusion(assistance_urgence, f(vice_defaut_connu, oui), tout, non, '3.1.12.5',
    "les frais pour un problème connu avant la conclusion du contrat").
exclusion(assistance_urgence, f(evenement, catastrophe_naturelle), tout, non, '3.1.12.5',
    "d’un glissement de terrain, d’une inondation ou de toute autre catastrophe naturelle").
exclusion(assistance_urgence, f(cause_guerre, oui), tout, non, '3.1.12.5',
    "les événements résultant d’une guerre, d’une mobilisation générale, d’une mobilisation de personnes ou de matériel par les pouvoirs publics, de terrorisme ou de sabotage, ou de conflits sociaux").
exclusion(assistance_urgence, ou([f(manque_entretien, oui), f(intentionnel, oui)]), tout, non, '3.1.12.5',
    "les conséquences nuisibles normalement prévisibles imputables à un fait ou à une négligence (par exemple le manque d’entretien prévu pour l’habitation ou l’installation fixe concernée) dans le chef de l’occupant de l’habitation de l’Assuré ou à sa faute intentionnelle").
exclusion(assistance_urgence, f(manque_entretien, oui), tout, non, '3.1.12.5',
    "frais en cas de manque d’entretien évident de l’installation fixe ou de l’habitation de l’Assuré").
exclusion(assistance_urgence, f(coupure_reseau, oui), tout, non, '3.1.12.5',
    "l’interruption ou la coupure de l’alimentation en gaz, en électricité ou en eau imputable au réseau de distribution").
exclusion(assistance_urgence, ou([f(cause_pollution, huile_minerale), f(cause_pollution, autre)]), tout, non, '3.1.12.5',
    "les dommages causés directement ou indirectement par une pollution").
exclusion(assistance_urgence, f(objet_assistance, panne_electrique), tout, non, '3.1.12.5',
    "les dommages causés directement ou indirectement par ou consistant en un dysfonctionnement ou une panne du circuit électrique, d’une connexion intégrée, d’un circuit intégré, d’un microprocesseur, de matériel informatique, d’un logiciel, d’un ordinateur, d’un appareil de télécommunication ou d’un système similaire").
limite(assistance_urgence, '3.1.12.2', "L’intervention d’Assureur B Assistance se limite à deux interventions/an et à concurrence de 400 € maximum par intervention à l’habitation de l’Assuré", "400").
exclusion([assistance_urgence], f(option_assistance_urgence, non), tout, oui, '3.1.12',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie ” Assistance d’urgence ” est accordée.").
