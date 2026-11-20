% --- Art. 2.10 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(catastrophe_technologique).
garantie(catastrophe_technologique, "Catastrophes technologiques", '2.10-a',
    "La garantie couvre les conséquences pécuniaires des dommages à vos biens à usage d'habitation ou placés dans les locaux à usage d'habitation résultant de l'état de catastrophe technologique conformément à la loi n°2003-699 du 30 juillet 2003.").
perimetre(catastrophe_technologique, f(evenement, catastrophe_technologique)).
perimetre(catastrophe_technologique, concept(batiment)).
circonstance(catastrophe_technologique, f(publication_jo_catastrophe_technologique, oui), '2.10-a',
    "La garantie ne peut être mise en jeu qu'après publication au Journal officiel de la République Française de la décision de l'autorité administrative ayant constaté l'état de catastrophe technologique.").
