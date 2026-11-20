% --- Art. 3.1.9.10 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
garantie(recours_tiers, "Recours des tiers", '3.1.9.10',
    "La Compagnie couvre les frais que l’Assuré peut encourir en vertu des articles 1382 à 1386 du Code civil pour les dommages matériels causés par un sinistre garanti se communiquant à des biens qui sont la propriété de tiers.").
perimetre(recours_tiers, f(victime, tiers)).
perimetre(recours_tiers, f(dommage_tiers, materiel)).
accessoire(recours_tiers).
