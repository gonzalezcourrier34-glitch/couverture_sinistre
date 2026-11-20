% --- Art. 1.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
definition(batiment, ou([f(lieu, logement), f(lieu, grenier), f(lieu, parties_communes), f(lieu, cave), f(lieu, garage), f(lieu, annexe), f(lieu, abri_jardin)]), '1.1-a',
    "votre local d’habitation, c’est-à-dire les parties immobilières des bâtiments principaux d’habitation destinées à un usage privé").
exclusion(tous, et([f(bien, veranda), non(f(option_veranda, oui))]), bien(veranda), non, '1.1-b',
    "les vérandas, sauf mention aux conditions particulières").
exclusion(tous, f(bien, eolienne), bien(eolienne), non, '1.1-b',
    "les éoliennes").
exclusion(tous, et([f(bien, panneau_solaire), non(f(formule, excellence))]), bien(panneau_solaire), non, '1.1-b',
    "les panneaux solaires et photovoltaïques si vous avez souscrit les formules Eco et Confort").
exclusion(tous, et([f(bien, piscine), non(f(pack_piscine, oui))]), bien(piscine), non, '1.1-b',
    "les piscines, spas et jacuzzi").
exclusion(tous, et([f(bien, plantation), non(f(pack_jardin, oui))]), bien(plantation), non, '1.1-b',
    "les plantations").
exclusion(tous, f(local_inoccupe_12_mois, oui), tout, non, '1.1-b',
    "les locaux inoccupés ou inutilisés depuis plus de 12 mois consécutifs").
