% --- Art. 4.1.4 : proposition rédigée par le modèle — mistral:mistral-large-4-0, 2026-11-24 ---
definition(e_protection, f(option_e_protection, oui), '4.1.4',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ E-protection ” est accordée.").
garantie(e_protection, "E-protection", '4.1.4.3~1',
    "Le Prestataire s’engage aux conditions telles que prévues ci-dessous, à fournir des services et à prendre en charge si nécessaire des frais afin de permettre à l’Assuré de faire valoir ses droits en tant que demandeur ou défendeur, soit dans une procédure judiciaire, administrative ou autre, soit en dehors de toute procédure.").
perimetre(e_protection, concept(e_protection)).
perimetre(e_protection, f(type_sinistre_e_protection, usurpation_identite)).
perimetre(e_protection, ou([f(type_sinistre_e_protection, utilisation_frauduleuse_moyens_paiement), f(type_sinistre_e_protection, atteinte_e_reputation), f(type_sinistre_e_protection, achat_bien_mobilier_e_commercant), f(type_sinistre_e_protection, achat_service_e_commercant), f(type_sinistre_e_protection, objet_connecte)])).
circonstance(e_protection, f(fait_generateur_connu_souscription, non), '4.1.4.4',
    "le fait générateur du sinistre ne doit pas être connu de l’Assuré à la date de prise d’effet de la présente garantie").
circonstance(e_protection, f(declaration_sinistre, oui), '4.1.4.4',
    "l’Assuré doit déclarer son sinistre à la Compagnie").
circonstance(e_protection, f(delai_attente_1_mois, oui), '4.1.4.4',
    "Pour tous les sinistres, le délai d’attente est d’1 mois à partir de la prise d’effet du contrat").
circonstance(e_protection, f(domicile_luxembourg, oui), '4.1.4.1',
    "sont considérés comme assurés, pour autant qu’ils soient domiciliés au Grand-Duché de Luxembourg et y résident habituellement").
exclusion(e_protection, f(domaine_litige, propriete_intellectuelle), tout, oui, '4.1.4.3~1',
    "de litiges liés à la propriété intellectuelle ou autres droits similaires (marques, copyright, droit d’auteur, etc…)").
exclusion(e_protection, f(activite_professionnelle, oui), tout, oui, '4.1.4.3~1',
    "d’une activité rémunérée ou professionnelle").
exclusion(e_protection, f(complicite_assure, oui), tout, oui, '4.1.4.3~1',
    "de la complicité de l’Assuré à savoir coopérer directement ou prêter pour l’exécution une aide telle que, sans son assistance l’événement dont découle le sinistre n’aurait pu avoir lieu").
exclusion(e_protection, f(faute_lourde, oui), tout, oui, '4.1.4.3.8',
    "d’une faute lourde").
exclusion(e_protection, f(crime, oui), tout, oui, '4.1.4.3~2',
    "pour les crimes ou les crimes correctionnalisés ainsi que leurs conséquences").
exclusion(e_protection, f(auteur_sinistre, assure), tout, oui, '4.1.4.3~2',
    "Le Prestataire ne prend pas en charge les sinistres résultant d’une usurpation d’identité ou d’une utilisation frauduleuse des moyens de paiement ou d’une atteinte à l’e-réputation par une personne assurée au titre des présentes garanties").
limite(e_protection, '4.1.4.4.9', "Indemnisation du préjudice subi en cas d’usurpation d’identité", "5000 EUR par sinistre et par année d’assurance").
limite(e_protection, '4.1.4.4.9', "Défense des intérêts de l’Assuré (défense amiable et judiciaire) par sinistre et par année d’assurance", "5750 EUR (1er instance), 5750 EUR (appel), 5750 EUR (cassation)").
limite(e_protection, '4.1.4.4.9', "Mise en relation en cas d’atteinte à l’e-réputation des frais de nettoyage ou de noyage des informations par sinistre et par année d’assurance", "5000 EUR").
accessoire(e_protection).
