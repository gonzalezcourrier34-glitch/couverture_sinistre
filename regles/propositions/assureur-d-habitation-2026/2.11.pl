% --- Art. 2.11 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(attentat).
garantie(attentats, "Attentats et actes de terrorisme", '2.11-a',
    "La garantie couvre les dommages matériels directs (y compris les frais de décontamination), subis sur le territoire national, causés aux biens assurés par un attentat ou un acte de terrorisme").
perimetre(attentats, f(evenement, attentat)).
perimetre(attentats, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(attentats, concept(batiment)).
exclusion([attentats], faux, tout, non, '2.11-b',
    "les frais de décontamination des déblais ainsi que leur confinement").
