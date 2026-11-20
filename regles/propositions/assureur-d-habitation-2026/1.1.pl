% --- Art. 1.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
definition(bien_immobilier, ou([f(bien, element_batiment), concept(dependances), f(bien, serre), f(bien, borne_recharge), f(bien, cloture), f(bien, panneau_solaire)]), '1.1-a',
    "votre local d'habitation... les clôtures, murs d'enceinte... les panneaux solaires et photovoltaïques (formule Excellence)").
definition(dependances, f(lieu, annexe), 'S10-a/dependances',
    "Ce sont les locaux destinés à un usage autre que le local d'habitation... situés en dehors de la « verticalité » du local d'habitation. Sont également considérés comme dépendances les caves et les garages situés dans les immeubles collectifs.").
exclusion(tous, ou([f(bien, chemin), f(bien, court_tennis), f(bien, veranda), f(bien, eolienne)]), tout, oui, '1.1-b',
    "les chemins, les courts de tennis, les vérandas, sauf mention aux conditions particulières, les éoliennes").
exclusion(tous, f(bien, local_inoccupe_12_mois), tout, oui, '1.1-b',
    "les locaux inoccupés ou inutilisés depuis plus de 12 mois consécutifs").
exclusion(tous, et([f(bien, panneau_solaire), f(formule, eco_ou_confort)]), tout, non, '1.1-b',
    "les panneaux solaires et photovoltaïques si vous avez souscrit les formules Eco et Confort").
exclusion(tous, et([ou([f(bien, piscine), f(bien, spa), f(bien, jacuzzi), f(bien, abri_piscine)]), non(f(pack_piscine, oui))]), tout, oui, '1.1-b',
    "les piscines, spas et jacuzzi, les abris de piscine, spas et jacuzzi (sauf Pack Piscine)").
exclusion(tous, et([ou([f(bien, aire_cimentee), f(bien, plantation), f(bien, cloture_vegetale), f(bien, serre_plus_5m2)]), non(f(pack_jardin, oui))]), tout, oui, '1.1-b',
    "les aires cimentées, goudronnées, dallées ou gravillonnées, les plantations, les clôtures végétales, les serres d'une superficie de plus de 5 m2 (sauf Pack Jardin)").
