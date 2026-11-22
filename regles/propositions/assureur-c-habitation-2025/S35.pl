% --- Art. S35 : proposition rédigée par le modèle — mistral:mistral-large-4-0, 2026-11-22 ---
exclusion(tous, f(intentionnel, oui), tout, non, 'S35',
    "Intentionnellement causés ou provoqués par l’assuré ou avec sa complicité").
exclusion(tous, f(dommage_legislation_construction, oui), tout, non, 'S35',
    "Relevant de la législation sur la construction ou la rénovation des bâtiments").
exclusion(tous, f(assurance_dommages_ouvrage, oui), tout, non, 'S35',
    "Relevant de l’assurance Dommages ouvrage").
exclusion(tous, f(cause_guerre, oui), tout, non, 'S35',
    "Causés par une guerre étrangère, ou une guerre civile").
exclusion(tous, et([ou([f(catastrophe, tremblement_terre), f(catastrophe, eruption_volcanique), f(catastrophe, action_mer), f(catastrophe, glissement_terrain)]), non(f(evenement, catastrophe_naturelle))]), tout, non, 'S35',
    "Causés par les tremblements de terre, les éruptions volcaniques, l’action de la mer, les glissements de terrain ou autres événements à caractère catastrophique, sauf si ces événements sont déclarés « Catastrophes naturelles »").
exclusion(tous, et([f(cause_nucleaire, oui), non(f(evenement, attentat))]), tout, non, 'S35',
    "Causés par la désintégration du noyau atomique, la radioactivité, la transmutation d’atome, à l’exception des dommages causés aux biens par un attentat ou un acte de terrorisme").
exclusion(tous, f(maladie_transmissible, oui), tout, non, 'S35',
    "Causés ou aggravés ou en relation, de manière directe ou indirecte, avec une maladie transmissible ou la crainte d’une maladie transmissible. On entend par maladie transmissible, toute maladie qui peut être transmise d’un organisme à un autre organisme par le vecteur de toute substance ou agent.").
exclusion(tous, f(defaut_reparation_connu, oui), tout, non, 'S35',
    "Résultant d’un défaut de réparation vous incombant, connu de vous sauf cas de force majeure, étant entendu que les causes non supprimées d’un précédent sinistre sont considérées automatiquement comme un défaut de réparation").
exclusion(tous, f(defaut_installation_electronique, oui), tout, non, 'S35',
    "Les dommages résultant d’un défaut d’installation sur les matériels électroniques, HI-FI, vidéo et Informatique").
exclusion(tous, f(support_donnees_ou_logiciel, oui), tout, non, 'S35',
    "Les dommages de toute nature aux données sur tous supports informatiques (y compris en cours de transmission et de traitement), ainsi que les atteintes à l’authenticité, l’intégrité ou la confidentialité de ces informations et/ou données ainsi que leurs conséquences immatérielles et financières.").
