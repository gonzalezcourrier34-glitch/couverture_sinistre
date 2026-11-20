# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-20T16:54:08 · golden set v12, partie « test » (31 cas, empreinte `0534a0545f66a07d`) · cas validés par l'auteur : 0 sur 31


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| lecture | cas_avec_contradiction | ≤ 5 | 5 | ✓ |
| chaine | faux_couverts | ≤ 0 | 3 | ✗ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.86 | ✓ |
| chaine | instables | ≤ 3 | 4 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 6.46 | ✓ |

## Couche 2 — lecture des faits par le modèle

Rappel des faits idéaux : 86% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 5 cas · faits vagues : 1 cas · faits en trop : 28 cas · faits retirés (sans appui ou non dits) : 23 cas

### Contradictions sans effet sur la décision

- `val-09` : evenement : autre lu fumee
- `g-l07` : evenement : autre lu accident
- `g-p03` : bien : objet_divers lu cles
- `g2-p01` : effraction : non lu oui
- `g2-p08` : cause_eau : piscine_exterieure lu debordement_aquarium

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 86% (84% – 87%) | 78% (77% – 81%) | **3 (3 – 3)** | **0 (0 – 0)** | 15% (13% – 16%) |

Instables : **4** sur 31 · rappel des clauses : 77% · rappel des questions : 100% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 67.0 s · par cas, un à la fois (10 cas) : médiane 3.65 s, 95e centile 6.46 s (lecture 2.71 s, décision 0.04 s) · en masse (quatre à la fois) : médiane 4.18 s, 95e centile 37.12 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 31 | 87% | 3 ⚠ | 0 |
| garantie : 2.1 | 3 | 100% | 0 | 0 |
| garantie : 2.10 | 13 | 77% | 2 ⚠ | 0 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.6 | 2 | 100% | 0 | 0 |
| garantie : 2.7 | 5 | 100% | 0 | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 3 | 67% | 1 ⚠ | 0 |
| garantie : aucune | 1 | 100% | 0 | 0 |
| thème : base | 1 | 100% | 0 | 0 |
| thème : hors_regles | 9 | 89% | 1 ⚠ | 0 |
| thème : info_manquante | 3 | 100% | 0 | 0 |
| thème : langue | 4 | 100% | 0 | 0 |
| thème : multi | 2 | 100% | 0 | 0 |
| thème : piege | 16 | 75% | 3 ⚠ | 0 |
| thème : variante | 4 | 100% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `val-01` attendu NC, obtenu C ? ? — Pendant que j'étais au travail, quelqu'un est entré par la fenêtre de ma chambre, au rez-de-chaussée, que j'av… *(Obligation de prévention (2.10) : en cas d'absence, « fermer correctement les fenêtres […] facilement accessibles ». Lie)*
- **⚠ couvert à tort** `red-b05` attendu NC, obtenu C C C — Le grand miroir que je venais d'acheter, encore dans son carton et pas encore accroché, s'est brisé quand je l… *(Exclusion 2.9 : les dommages aux vitres et biens assimilés non placés.)*
- **⚠ couvert à tort** `g-p03` attendu NC, obtenu C C C — Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune… *(Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct.)*
- **⚠ couvert à tort** `g2-p08` attendu NC, obtenu NC C C — Le bain à bulles installé sur ma terrasse a fui et l'eau a abîmé le canapé du salon. *(Exclusion 2.7 : l'écoulement d'eau des piscines et des bains à bulles extérieurs.)*
- `red-b01` attendu C, obtenu C C ? — Mon fils a cassé la vitre de la porte-fenêtre du salon avec un ballon. *(2.9 : le bris de vitres.)*
- `g-q04` attendu C, obtenu ? ? C — De l'eau coule du plafond de ma salle de bain et a abîmé le mur. *(2.7 couvre l'ensemble des dégâts des eaux ; la cause inconnue n'établit aucune exclusion (c'est à l'assureur de la prouv)*
- `g2-p01` attendu C, obtenu ? ? ? — Pendant mes vacances, des cambrioleurs ont ouvert ma porte sans la casser : il n'y a que des traces de tournev… *(Pas d'effraction au sens du contrat, mais la porte était fermée à clé : l'obligation est respectée, le vol dans le bâtim)*
