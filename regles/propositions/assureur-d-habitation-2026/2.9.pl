% --- Art. 2.9 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(catastrophe_naturelle).
garantie(catastrophes_naturelles, "Catastrophes naturelles", '2.9-a',
    "La garantie couvre les dommages matériels directs non assurables ayant eu pour cause déterminante l’intensité anormale d’un agent naturel").
perimetre(catastrophes_naturelles, f(evenement, catastrophe_naturelle)).
perimetre(catastrophes_naturelles, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(catastrophes_naturelles, concept(batiment)).
circonstance(catastrophes_naturelles, f(arrete_catnat_30j, oui), '2.9-a',
    "La garantie est mise en jeu par une déclaration faite au plus tard trente jours après publication au Journal Officiel d’un arrêté interministériel constatant l’état de catastrophe naturelle").
exclusion(catastrophes_naturelles, f(terrain_non_constructible, oui), tout, non, '2.9-b',
    "les biens assurés construits sur des terrains classés inconstructibles par un plan de prévention des risques à l’exception toutefois des biens existants antérieurement à la publication de ce plan").
garantie(relogement_catnat, "Relogement d'urgence après une catastrophe naturelle", '2.9-a',
    "les frais de relogement d’urgence des personnes sinistrées dont la résidence principale est rendue impropre à l’habitation").
perimetre(relogement_catnat, f(evenement, catastrophe_naturelle)).
perimetre(relogement_catnat, f(residence_principale_inhabitable, oui)).
accessoire(relogement_catnat).
