% --- Art. 2.5 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-18 ---
evenement_traduit(vol).
evenement_traduit(incendie).
evenement_traduit(explosion).
evenement_traduit(foudre).
evenement_traduit(degat_eaux).
evenement_traduit(tempete).
evenement_traduit(bris).
evenement_traduit(autre).
evenement_traduit(electricite).
evenement_traduit(mazout).
evenement_traduit(catastrophe_naturelle).
evenement_traduit(attentat).
evenement_traduit(fumee).
evenement_traduit(vandalisme).
evenement_traduit(merule).
definition(trouble_de_voisinage, f(trouble_voisinage, oui), '2.5',
    "Notre garantie s'étend au trouble de voisinage au sens de l'article 3.101, à l'exclusion de l'article 3.102, du Code civil").
definition(terrain_attennant, et([concept(jardin), f(superficie_terrain, moins_5_hectares)]), '2.5',
    "du terrain attenant au bâtiment, sans dépasser au total 5 hectares, y compris l'ensemble des constructions répondant au champ d'application du contrat qui y sont situées").
garantie(rc_immeuble, "Responsabilité civile immeuble", '2.5',
    "Nous prenons en charge la responsabilité civile que vous pouvez encourir sur base : • du livre 6 du Code civil • de l'article 1721 du Code civil c'est-à-dire le recours des locataires pour les dommages causés aux tiers du fait : • du bâtiment, du contenu en ce compris le contenu destiné à l'usage du jardin, de la piscine, de l'étang de baignade ou du bain à bulles extérieur (eau comprise), à l'exception des animaux • des trottoirs, notamment suite au défaut d'enlèvement de la neige, de la glace ou du verglas • des ascenseurs et monte-charge pour autant qu'ils soient déclarés conformes à la réglementation en vigueur par un organisme de contrôle entretenus annuellement par une entreprise agréée • du terrain attenant au bâtiment, sans dépasser au total 5 hectares, y compris l'ensemble des constructions répondant au champ d'application du contrat qui y sont situées.").
perimetre(rc_immeuble, f(type_sinistre, responsabilite_civile)).
perimetre(rc_immeuble, f(tiers_victime, oui)).
perimetre(rc_immeuble, ou([f(source_responsabilite, batiment), et([ou([concept(contenu), f(bien, mobilier_jardin), f(bien, couverture_piscine), f(bien, plantation)]), non(f(bien, animal))]), f(source_responsabilite, trottoir), f(source_responsabilite, ascenseur), f(source_responsabilite, terrain_attennant), concept(trouble_de_voisinage)])).
circonstance(rc_immeuble, si(f(source_responsabilite, ascenseur), et([f(ascenseur_conforme, oui), f(ascenseur_entretien_annuel, oui)])), '2.5',
    "des ascenseurs et monte-charge pour autant qu'ils soient déclarés conformes à la réglementation en vigueur par un organisme de contrôle entretenus annuellement par une entreprise agréée").
circonstance(rc_immeuble, si(f(source_responsabilite, trottoir), f(defaut_enlevement_neige_glace, oui)), '2.5',
    "des trottoirs, notamment suite au défaut d'enlèvement de la neige, de la glace ou du verglas").
circonstance(rc_immeuble, si(concept(trouble_de_voisinage), et([f(evenement_soudain_imprevisible, oui), non(f(meme_immeuble_logements_multiples, oui))])), '2.5',
    "s'ils découlent d'un événement soudain, imprévisible pour vous, sauf s'il oppose les occupants d'un même immeuble à logements multiples").
exclusion(rc_immeuble, f(cause_amiante, oui), tout, oui, '2.5-a',
    "par l'amiante sous toutes ses formes").
exclusion(rc_immeuble, f(garde_biens, oui), tout, oui, '2.5-a',
    "à des biens dont vous avez la garde").
exclusion(rc_immeuble, f(conformite_controle_citerne, non), tout, oui, '2.5-a',
    "en cas de non-respect de la réglementation applicable au contrôle des citernes").
limite(rc_immeuble, '2.5', "Nous couvrons par fait dommageable : • 18.425.000 EUR pour l'indemnisation des dommages résultant de lésions corporelles", "18425000 EUR").
limite(rc_immeuble, '2.5', "Nous couvrons par fait dommageable : • 3.685.000 EUR pour l'indemnisation des dommages résultant de dégâts matériels", "3685000 EUR").
