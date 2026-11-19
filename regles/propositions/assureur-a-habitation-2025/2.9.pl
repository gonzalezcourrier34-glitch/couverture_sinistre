% --- Art. 2.9 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-17 ---
evenement_traduit(bris).
definition(vitrage_assure, ou([f(bien, vitre), f(bien, miroir), f(bien, coupole), f(bien, panneau_verre_plastique), f(bien, table_cuisson_vitroceramique), f(bien, panneau_solaire), f(bien, mur_rideau), f(bien, sanitaire), f(bien, verre_meuble)]), '2.9',
    "Nous assurons le bris et la fêlure de vitres, y compris le bris des biens suivants (assimilés aux vitres) : les miroirs, les coupoles, panneaux ou enseignes en verre ou en plastique, les tables de cuisson en vitrocéramique, les panneaux solaires fixés au bâtiment, les murs rideaux, les sanitaires et le verre intégré dans des meubles").
definition(sanitaire, f(bien, sanitaire), '12/sanitaires',
    "Les éviers, lavabos, baignoires, pédiluves, douches, toilettes et bidets, saunas, hammams et bains à bulles intérieurs").
garantie(bris_vitrages, "Bris et fêlure de vitrages", '2.9',
    "Nous assurons le bris et la fêlure de vitres, y compris le bris des biens suivants (assimilés aux vitres)").
perimetre(bris_vitrages, f(evenement, bris)).
perimetre(bris_vitrages, ou([concept(vitrage_assure), f(bien, cadre), f(bien, chassis), f(bien, soubassement)])).
exclusion(bris_vitrages, f(travaux_batiment, autres_que_entretien_reparation), tout, oui, '2.9-a',
    "les dommages causés par les travaux au bâtiment autres que d’entretien et de réparation").
exclusion(bris_vitrages, f(travaux_vitres, autres_que_nettoyage), tout, oui, '2.9-a',
    "les dommages causés par les travaux (nettoyage excepté) aux vitres, châssis et biens assimilés").
exclusion(bris_vitrages, f(bien, appareil_audiovisuel), bien(appareil_audiovisuel), oui, '2.9-a',
    "les parties vitrées des appareils audiovisuels y compris les écrans de télévision").
exclusion(bris_vitrages, f(bien, serre), bien(serre), oui, '2.9-a',
    "les parties vitrées des serres et des couvertures de piscine").
exclusion(bris_vitrages, f(vitre_placee, non), tout, oui, '2.9-a',
    "les dommages aux vitres et biens assimilés non placés").
exclusion(bris_vitrages, f(type_dommage, rayure_ou_ecaillement), tout, oui, '2.9-a',
    "les rayures et écaillements des vitres et biens assimilés").
exclusion(bris_vitrages, et([f(bien, sanitaire), f(cause_dommage, gel)]), tout, oui, '2.9-a',
    "les dommages causés aux sanitaires par le gel").
exclusion(bris_vitrages, f(bien, objet_verre_non_vitre), bien(objet_verre_non_vitre), oui, '2.9-a',
    "les dommages causés aux objets en verre autres que des vitres et biens assimilés").
exclusion(bris_vitrages, f(type_dommage, opacification_ou_perte_etancheite), tout, oui, '2.9-a',
    "l’opacification ou perte détanchéité des vitrages isolants").
exclusion(bris_vitrages, f(bien, couverture_piscine), bien(couverture_piscine), oui, '2.9-a',
    "les parties vitrées des serres et des couvertures de piscine").
limite(bris_vitrages, '2.9', "Dommages causés aux vitrages d’art, frais de reconstitution des inscriptions, peintures, 5.000 EUR décorations", "5000 EUR").
