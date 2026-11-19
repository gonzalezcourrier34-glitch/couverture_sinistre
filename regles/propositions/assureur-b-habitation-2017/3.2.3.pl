% --- Art. 3.2.3 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
garantie(pertes_indirectes, "Pertes indirectes", '3.2.3',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ pertes indirectes ” est accordée. La Compagnie garantit la majoration de 10% des indemnités contractuellement dues, en vue de dédommager l’Assuré à la suite d’un sinistre couvert.").
exclusion(pertes_indirectes, non(f(option_pertes_indirectes, oui)), tout, oui, '3.2.3',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie “ pertes indirectes ” est accordée.").
limite(pertes_indirectes, '3.2.3', "La Compagnie garantit la majoration de 10% des indemnités contractuellement dues, en vue de dédommager l’Assuré à la suite d’un sinistre couvert.", "majoration de 10% des indemnités contractuellement dues").
accessoire(pertes_indirectes).
