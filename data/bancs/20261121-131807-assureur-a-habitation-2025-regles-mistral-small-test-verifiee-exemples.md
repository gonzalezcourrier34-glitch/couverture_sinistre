# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee, exemples)

2026-11-21T13:14:17 · golden set v12, partie « test » (31 cas, empreinte `0534a0545f66a07d`) · cas validés par l'auteur : 0 sur 31


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 1 | ✓ |
| lecture | decisions_changees | ≤ 2 | 5.67 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 2 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 5 | ✓ |
| chaine | faux_couverts | ≤ 0 | 1.667 | ✗ |
| chaine | faux_refus | ≤ 1 | 1 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.817 | ✗ |
| chaine | instables | ≤ 3 | 3 | ✓ |
| chaine | rappel_questions | ≥ 0.8 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 5.74 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-21T12:53:51, mistral:mistral-small-latest · verifiee, exemples)

- lecture · rappel_faits : 0.893 → 0.87
- chaine · exactitude : 0.871 → 0.817
- chaine · exactitude_stricte : 0.774 → 0.742
- chaine · faux_couverts : 2 → 1.667
- chaine · faux_refus : 0 → 1

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

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **5.67** par exécution, dont **2** cas vers un couvert à tort.

Rappel des faits idéaux : 87% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 5 cas · faits vagues : 1 cas · faits en trop : 26 cas · faits retirés (sans appui ou non dits) : 25 cas

### La lecture change la décision

- **⚠ vers couvert** `g-p03` idéal ?, lu C C C · **contredit** : bien : objet_divers lu cles · manque : effraction = non; portes_fermees = oui · en trop : acces_voleur = cles_volees · retiré sans appui : fermeture = aucune
- **⚠ vers couvert** `g2-p08` idéal NC, lu C C C · manque : cause_eau = piscine_exterieure · retiré sans appui : bien = appareil_electromenager; cause_eau = debordement_aquarium; type_dommage = moisissure
- `red-b01` idéal C, lu NC NC NC · en trop : auteur = famille; effraction = non; intentionnel = oui; proprietaire = assure; travaux_batiment = aucun; travaux_vitres = aucun; type_dommage = bris; vitre_placee = oui
- `g-h03` idéal C, lu NC NC NC · **contredit** : bien : element_batiment lu mazout · en trop : bien_a_l_origine_sinistre = oui · retiré sans appui : bien = element_batiment
- `g2-i06` idéal ?, lu NC NC ? · en trop : periode_gel = oui; prevention_gel = non · retiré sans appui : prevention_gel = non; type_dommage = opacification_ou_perte_etancheite
- `g2-p01` idéal C, lu ? ? ? · **contredit** : effraction : non lu oui · manque : bien = objet_divers · en trop : acces_voleur = sans_effraction; fermeture = cle

### Contradictions sans effet sur la décision

- `val-09` : bien : objet_divers lu mobilier; evenement : autre lu fumee
- `g-l07` : evenement : autre lu accident

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 82% (81% – 84%) | 74% (74% – 74%) | **1.667 (1 – 2)** | **1 (1 – 1)** | 20% (19% – 23%) |

Instables : **3** sur 31 · rappel des clauses : 80% · rappel des questions : 100% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 62.1 s · par cas, un à la fois (10 cas) : médiane 3.88 s, 95e centile 5.74 s (lecture 2.95 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.59 s, 95e centile 36.54 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 31 | 81% | 2 ⚠ | 1 |
| garantie : 2.1 | 3 | 67% | 0 | 0 |
| garantie : 2.10 | 13 | 85% | 1 ⚠ | 0 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.6 | 2 | 100% | 0 | 0 |
| garantie : 2.7 | 5 | 80% | 1 ⚠ | 0 |
| garantie : 2.8 | 1 | 0% | 0 | 1 |
| garantie : 2.9 | 3 | 67% | 0 | 0 |
| garantie : aucune | 1 | 100% | 0 | 0 |
| thème : base | 1 | 100% | 0 | 0 |
| thème : hors_regles | 9 | 78% | 0 | 1 |
| thème : info_manquante | 3 | 100% | 0 | 0 |
| thème : langue | 4 | 100% | 0 | 0 |
| thème : multi | 2 | 50% | 0 | 0 |
| thème : piege | 16 | 81% | 2 ⚠ | 0 |
| thème : variante | 4 | 75% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `g-p03` attendu NC, obtenu C ? C — Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune… *(Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct.)*
- **⚠ couvert à tort** `g2-p08` attendu NC, obtenu C C C — Le bain à bulles installé sur ma terrasse a fui et l'eau a abîmé le canapé du salon. *(Exclusion 2.7 : l'écoulement d'eau des piscines et des bains à bulles extérieurs.)*
- `bougie-05` attendu C, obtenu ? C ? — J'ai oublié une bougie allumée sur la terrasse avant de partir trois semaines. Le feu s'est propagé à la façad… *(Incendie qui atteint la façade et le séjour : couvert, même par imprudence. L'absence de trois semaines n'est pas une in)*
- `red-b01` attendu C, obtenu ? ? ? — Mon fils a cassé la vitre de la porte-fenêtre du salon avec un ballon. *(2.9 : le bris de vitres.)*
- `g-l05` attendu C, obtenu C ? C — Fuite d'eau sous l'évier : le meuble de cuisine a gonflé et le parquet est abîmé. *(2.7 : l'ensemble des dommages causés par l'eau.)*
- `g-h03` attendu C, obtenu NC NC NC — La cuve de fioul de l'immeuble a fui et le fioul a imprégné le sol de ma cave. *(2.8 : dégâts causés par le mazout. Non traduite.)*
- `g2-p01` attendu C, obtenu ? ? ? — Pendant mes vacances, des cambrioleurs ont ouvert ma porte sans la casser : il n'y a que des traces de tournev… *(Pas d'effraction au sens du contrat, mais la porte était fermée à clé : l'obligation est respectée, le vol dans le bâtim)*
