% --- Art. 4.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(vol).
definition(residence_secondaire, non(f(residence_principale, oui)), 'S10-a/residence-secondaire',
    "Habitation à usage privé qui n'est pas votre résidence principale telle qu'elle est définie ci-avant.").
definition(dependances, ou([f(lieu, annexe), f(lieu, garage), f(lieu, cave)]), 'S10-a/dependances',
    "Ce sont les locaux destinés à un usage autre que le local d'habitation ou l'exercice d'une profession situés en dehors de la « verticalité » du local d'habitation. Sont également considérés comme dépendances les caves et les garages situés dans les immeubles collectifs.").
garantie(protection_vol_4_1, "Mesures de sécurité contre le vol et détériorations immobilières", '4.1',
    "Si vous vous absentez : • moins de 24 heures : les portes doivent être fermées à clé, les fenêtres, portes-fenêtres et autres issues bloquées, • plus de 24 heures : tous les moyens de fermeture et de protection décrits aux conditions particulières doivent être mis en action.").
perimetre(protection_vol_4_1, f(evenement, vol)).
perimetre(protection_vol_4_1, concept(batiment)).
obligation(protection_vol_4_1, f(duree_absence, moins_24h), faux, oui, '4.1',
    "moins de 24 heures : les portes doivent être fermées à clé, les fenêtres, portes-fenêtres et autres issues bloquées").
obligation(protection_vol_4_1, f(duree_absence, plus_24h), faux, oui, '4.1',
    "plus de 24 heures : tous les moyens de fermeture et de protection décrits aux conditions particulières doivent être mis en action").
obligation(protection_vol_4_1, concept(dependances), faux, oui, '4.1',
    "Les portes d'accès aux dépendances doivent être en bois plein ou en métal munies d'une ou plusieurs serrures de sûreté (cadenas exclu)").
obligation(protection_vol_4_1, et([concept(dependances), f(lieu, cave), f(immeuble_collectif, oui)]), faux, oui, '4.1',
    "Dans les ensembles collectifs, les portes de cave doivent être renforcées, pleines et munies de deux serrures de sûreté").
exclusion(protection_vol_4_1, et([f(duree_inoccupation, '46_jours_et_plus'), f(residence_principale, oui)]), tout, oui, '4.1',
    "La garantie Vol des objets de valeur et du contenu est suspendue dès le 46ème jour d'inoccupation jusqu'au retour des occupants autorisés.").
exclusion(protection_vol_4_1, et([f(duree_inoccupation_secondaire, '2_jours_et_plus'), concept(residence_secondaire)]), tout, oui, '4.1',
    "Cas particulier du vol des objets précieux de la résidence principale dans votre résidence secondaire : la garantie Vol des objets précieux est suspendue dès le 2ème jour d'inoccupation de la résidence secondaire.").
limite(protection_vol_4_1, '4.1', "Si l'introduction a été facilitée ou aggravée par la non-conformité ou l'absence de mise en œuvre des moyens de protection et/ou de fermeture exigés aux conditions particulières, l'indemnité sera réduite de 50 %.", "réduction de 50 % de l'indemnité").
limite(protection_vol_4_1, '4.1', "Pour la garantie Vol des objets précieux, des espèces, titres et valeurs, une franchise de 30 % du montant du sinistre est appliquée dès le 11ème jour d'une période d'inoccupation qui excède 10 jours consécutifs et jusqu'au retour des occupants autorisés, sauf si ces objets sont enfermés dans un coffre-fort ou dans des caches spécialement aménagées dans les murs ou dans le sol.", "franchise de 30 % du montant du sinistre").
