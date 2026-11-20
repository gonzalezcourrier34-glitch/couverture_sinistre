% --- Art. 2.12 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(attentat).
garantie(emeutes, "Émeutes et mouvements populaires", '2.12-a',
    "La garantie couvre, dans les conditions et limites prévues pour chaque garantie si elle est souscrite, les dommages matériels causés aux biens assurés survenant lors d’émeutes ou de mouvements populaires").
perimetre(emeutes, f(evenement, attentat)).
perimetre(emeutes, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(emeutes, concept(batiment)).
