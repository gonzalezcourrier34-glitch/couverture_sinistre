% --- Art. 2.11 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(attentat).
garantie(attentat_biens, "Attentats et actes de terrorisme", '2.11-a',
    "La garantie couvre les dommages matériels directs (y compris les frais de décontamination), subis sur le territoire national, causés aux biens assurés par un attentat ou un acte de terrorisme tels que définis aux articles 421-1 et 421-2 du Code pénal.").
perimetre(attentat_biens, f(evenement, attentat)).
perimetre(attentat_biens, f(pays, france)).
exclusion(attentat_biens, f(nature_frais, decontamination_deblais_confinement), tout, oui, '2.11-b',
    "les frais de décontamination des déblais ainsi que leur confinement").
