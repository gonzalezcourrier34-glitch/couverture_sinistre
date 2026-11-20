% --- Art. 22.2 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(litige).
garantie(protection_juridique, "Protection juridique (option)", '22.2',
    "Nous intervenons quand un litige survient dans votre vie privée ou salariée").
perimetre(protection_juridique, f(evenement, litige)).
perimetre(protection_juridique, ou([f(domaine_litige, travail), f(domaine_litige, logement), f(domaine_litige, travaux), f(domaine_litige, sante), f(domaine_litige, consommation), f(domaine_litige, administration), f(domaine_litige, voisinage), f(domaine_litige, employeur_domestique), f(domaine_litige, location_vacances), f(domaine_litige, bateau), f(domaine_litige, association), f(domaine_litige, famille)])).
circonstance(protection_juridique, f(option_protection_juridique, oui), '22.2',
    "(garantie optionnelle)").
