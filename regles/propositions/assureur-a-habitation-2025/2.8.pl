% --- Art. 2.8 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-18 ---
evenement_traduit(mazout).
garantie(degats_mazout, "Dégâts causés par le mazout", '2.8',
    "Nous couvrons les dégâts causés par tout combustible liquide de chauffage du bâtiment").
perimetre(degats_mazout, f(evenement, mazout)).
perimetre(degats_mazout, concept(batiment)).
obligation(degats_mazout, si(f(periode_gel, oui), f(prevention_gel, oui)), faux, oui, '2.8-a',
    "En période de gel, vous devez : • maintenir une température positive dans tous les locaux, ou • vidanger les installations hydrauliques et de chauffage, ou • isoler efficacement ces installations contre le gel. Nous refuserons notre intervention s’il existe un lien causal direct entre le non-respect de ces obligations et la survenance du sinistre.").
exclusion(degats_mazout, et([f(bien, canalisation), f(bien_a_l_origine_sinistre, oui)]), bien(canalisation), oui, '2.8-b',
    "les dégâts causés aux citernes ou canalisations qui sont à l'origine du sinistre").
exclusion(degats_mazout, et([f(bien, citerne), f(bien_a_l_origine_sinistre, oui)]), bien(citerne), oui, '2.8-b',
    "les dégâts causés aux citernes ou canalisations qui sont à l'origine du sinistre").
exclusion(degats_mazout, f(controle_citerne_conforme, non), tout, oui, '2.8-b',
    "les dégâts causés en cas de non-respect de la réglementation applicable au contrôle des citernes").
exclusion(degats_mazout, f(bien, mazout), bien(mazout), oui, '2.8-b',
    "la pertes de combustible liquide de chauffage subie à l’occasion d’un sinistre").
