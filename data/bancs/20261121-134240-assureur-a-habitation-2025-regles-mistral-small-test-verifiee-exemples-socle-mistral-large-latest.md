# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee, exemples, socle mistral-large-latest)

2026-11-21T13:32:56 · golden set v12, partie « test » (31 cas, empreinte `0534a0545f66a07d`) · cas validés par l'auteur : 0 sur 31


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 1 | ✓ |
| lecture | decisions_changees | ≤ 2 | 9.33 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 1 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 4 | ✓ |
| chaine | faux_couverts | ≤ 0 | 0.667 | ✗ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.828 | ✗ |
| chaine | instables | ≤ 3 | 7 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 31.08 | ✗ |

## Couche 1 — règles seules (faits idéaux, sans modèle)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 100% | 94% | **0** | **0** | 10% |

Rappel des questions attendues : 100% · questions posées par réponse « incertain » : 1

Raisonnement par hypothèses : incertains tranchés par une ou deux questions : 33% · questions inutiles retirées : 7

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 31 | 100% | 0 | 0 |
| garantie : 2.1 | 3 | 100% | 0 | 0 |
| garantie : 2.10 | 13 | 100% | 0 | 0 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.6 | 2 | 100% | 0 | 0 |
| garantie : 2.7 | 5 | 100% | 0 | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 3 | 100% | 0 | 0 |
| garantie : aucune | 1 | 100% | 0 | 0 |
| thème : base | 1 | 100% | 0 | 0 |
| thème : hors_regles | 9 | 100% | 0 | 0 |
| thème : info_manquante | 3 | 100% | 0 | 0 |
| thème : langue | 4 | 100% | 0 | 0 |
| thème : multi | 2 | 100% | 0 | 0 |
| thème : piege | 16 | 100% | 0 | 0 |
| thème : variante | 4 | 100% | 0 | 0 |

### Erreurs des règles

Aucune.

## Couche 2 — lecture des faits par le modèle

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **9.33** par exécution, dont **1** cas vers un couvert à tort.

Rappel des faits idéaux : 73% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 4 cas · faits vagues : 0 cas · faits en trop : 27 cas · faits retirés (sans appui ou non dits) : 21 cas

### La lecture change la décision

- **⚠ vers couvert** `g2-p08` idéal NC, lu C C ? · **contredit** : cause_eau : piscine_exterieure lu debordement_aquarium · manque : bien = mobilier; cause_eau = piscine_exterieure; evenement = degat_eaux; lieu = logement/terrasse · en trop : type_dommage = moisissure · retiré sans appui : type_dommage = moisissure
- `velo-06` idéal NC, lu NC ? NC · manque : bien = velo; evenement = vol; fermeture = cadenas; lieu = voie_publique; violence = non; vol_sur_personne = non · en trop : acces_voleur = sans_effraction; effraction = oui; laisse_sans_surveillance = oui · retiré sans appui : fermeture = aucune; vol_sur_personne = non
- `bougie-05` idéal C, lu C ? C · manque : absence = oui; bien = element_batiment/mobilier; embrasement = oui; evenement = incendie; flammes = oui; lieu = logement/terrasse · en trop : intentionnel = non · retiré sans appui : bien_a_l_origine_sinistre = non; chaleur_sans_feu = non; manque_entretien = non
- `val-09` idéal NC, lu ? ? NC · **contredit** : evenement : autre lu accident · manque : bien = objet_divers; embrasement = non; evenement = autre; flammes = non; lieu = logement
- `red-b01` idéal C, lu NC NC NC · en trop : auteur = famille; effraction = non; intentionnel = oui; type_dommage = bris
- `g-l02` idéal C, lu C ? ? · manque : absence = oui; bien = electronique/velo; effraction = oui; evenement = vol; lieu = logement · en trop : auteur = tiers; fermeture = cle; plainte_deposee = oui; proprietaire = assure; serrure_surete = oui; vol_sur_personne = non · retiré sans appui : violence = non
- `g-h01` idéal C, lu ? ? ? · manque : lieu = logement · en trop : intentionnel = non; proprietaire = assure; usage_professionnel = non · retiré sans appui : cause_perte_alimentaire = coupure_soudaine_reseau; chaleur_sans_feu = non; embrasement = non; flammes = non; manque_entretien = non
- `g-h03` idéal C, lu ? ? ? · manque : bien = element_batiment; evenement = mazout; lieu = cave · en trop : bien_a_l_origine_sinistre = oui
- `g-h05` idéal C, lu ? C C · manque : bien = element_batiment; cause_eau = inondation; evenement = catastrophe_naturelle/degat_eaux; lieu = logement
- `g-h07` idéal C, lu ? ? ? · manque : lieu = logement · en trop : proprietaire = assure; usage_professionnel = non · retiré sans appui : chaleur_sans_feu = non; embrasement = non; flammes = non; intentionnel = non
- `g-m01` idéal C, lu ? ? C · manque : bien = electronique/vitre; effraction = oui; evenement = bris/vol; lieu = logement · en trop : auteur = tiers; fermeture = cle; proprietaire = assure; violence = non; vol_sur_personne = non · retiré sans appui : serrure_surete = non
- `g2-i06` idéal ?, lu ? ? NC · en trop : periode_gel = oui; prevention_gel = non; travaux_batiment = aucun · retiré sans appui : prevention_gel = non
- `g2-p01` idéal C, lu ? ? ? · **contredit** : effraction : non lu oui · manque : bien = objet_divers · en trop : acces_voleur = sans_effraction; fermeture = cle

### Contradictions sans effet sur la décision

- `g-l07` : evenement : autre lu accident

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 83% (74% – 90%) | 61% (55% – 68%) | **0.667 (0 – 1)** | **0 (0 – 0)** | 40% (36% – 45%) |

Instables : **7** sur 31 · rappel des clauses : 71% · rappel des questions : 100% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 129.4 s · par cas, un à la fois (10 cas) : médiane 16.68 s, 95e centile 31.08 s (lecture 15.81 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 10.69 s, 95e centile 30.6 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 31 | 84% | 1 ⚠ | 0 |
| garantie : 2.1 | 3 | 67% | 0 | 0 |
| garantie : 2.10 | 13 | 85% | 0 | 0 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.6 | 2 | 100% | 0 | 0 |
| garantie : 2.7 | 5 | 80% | 1 ⚠ | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 3 | 67% | 0 | 0 |
| garantie : aucune | 1 | 100% | 0 | 0 |
| thème : base | 1 | 100% | 0 | 0 |
| thème : hors_regles | 9 | 89% | 0 | 0 |
| thème : info_manquante | 3 | 100% | 0 | 0 |
| thème : langue | 4 | 100% | 0 | 0 |
| thème : multi | 2 | 50% | 0 | 0 |
| thème : piege | 16 | 81% | 1 ⚠ | 0 |
| thème : variante | 4 | 100% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `g2-p08` attendu NC, obtenu C C ? — Le bain à bulles installé sur ma terrasse a fui et l'eau a abîmé le canapé du salon. *(Exclusion 2.7 : l'écoulement d'eau des piscines et des bains à bulles extérieurs.)*
- `velo-06` attendu NC, obtenu NC ? NC — Mon vélo était attaché à un arceau dans la rue avec un antivol. L'antivol a été coupé et le vélo volé. *(Vol dans la rue, sans violence : hors du bâtiment, et ce n'est pas un « vol commis sur l'assuré … suite à violences ».)*
- `bougie-05` attendu C, obtenu C ? C — J'ai oublié une bougie allumée sur la terrasse avant de partir trois semaines. Le feu s'est propagé à la façad… *(Incendie qui atteint la façade et le séjour : couvert, même par imprudence. L'absence de trois semaines n'est pas une in)*
- `val-09` attendu NC, obtenu ? ? NC — Mon fer à repasser, laissé à plat sur la planche, a brûlé la housse et laissé une marque sur le tissu, sans fl… *(Définition de l'incendie : les brûlures et le contact d'une source de chaleur sans embrasement ne sont pas un incendie.)*
- `red-b01` attendu C, obtenu ? ? ? — Mon fils a cassé la vitre de la porte-fenêtre du salon avec un ballon. *(2.9 : le bris de vitres.)*
- `g-l02` attendu C, obtenu C ? ? — Bonjour, je vous écris parce que je suis vraiment embêté. Samedi soir nous étions chez ma belle-sœur pour son … *(Déclaration longue et bavarde. 2.10 : vol du contenu dans le bâtiment, avec effraction (l'obligation de fermer est alors)*
- `g-h05` attendu C, obtenu ? C C — Les égouts publics ont refoulé pendant un gros orage et l'eau sale a envahi la salle de bain. *(2.3 : le refoulement d'égouts publics est une catastrophe naturelle couverte ; 2.7 l'exclut. Non traduite.)*
- `g-m01` attendu C, obtenu ? ? C — Des cambrioleurs ont forcé la porte, volé mon ordinateur et cassé la vitre de la porte-fenêtre en partant. *(2.10 : vol avec effraction, et vandalisme au contenu à l'occasion du vol.)*
- `g2-p01` attendu C, obtenu ? ? ? — Pendant mes vacances, des cambrioleurs ont ouvert ma porte sans la casser : il n'y a que des traces de tournev… *(Pas d'effraction au sens du contrat, mais la porte était fermée à clé : l'obligation est respectée, le vol dans le bâtim)*
