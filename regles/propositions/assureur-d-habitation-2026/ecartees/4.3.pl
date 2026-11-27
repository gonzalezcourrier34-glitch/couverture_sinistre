% --- Art. 4.3 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(incendie).
garantie(incendie_mesures_securite_4_3, "Incendie - Mesures de sécurité", '4.3',
    "Vous devez faire ramoner chaque année les conduits de fumée par un professionnel.").
perimetre(incendie_mesures_securite_4_3, f(evenement, incendie)).
perimetre(incendie_mesures_securite_4_3, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(incendie_mesures_securite_4_3, concept(batiment)).
limite(incendie_mesures_securite_4_3, '4.3', "Vous devez faire ramoner chaque année les conduits de fumée par un professionnel. Si vous ne pouvez produire de justificatif établi par ce professionnel datant de moins de deux ans au jour du sinistre, l’indemnisation des dommages subis par le seul conduit de fumée sera réduite de 50 %.", "réduction de 50 %").
limite(incendie_mesures_securite_4_3, '4.3', "Vous devez également vous conformer aux instructions du service public concernant le débroussaillage, à défaut de quoi l’indemnisation sera réduite de 50 %.", "réduction de 50 %").
