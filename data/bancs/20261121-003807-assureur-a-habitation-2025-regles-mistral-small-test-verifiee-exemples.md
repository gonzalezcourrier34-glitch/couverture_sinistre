# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee, exemples)

2026-11-21T00:33:39 · golden set v12, partie « test » (31 cas, empreinte `0534a0545f66a07d`) · cas validés par l'auteur : 0 sur 31


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| lecture | cas_avec_contradiction | ≤ 5 | 5 | ✓ |
| chaine | faux_couverts | ≤ 0 | 1.333 | ✗ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.892 | ✓ |
| chaine | instables | ≤ 3 | 2 | ✓ |
| chaine | rappel_questions | ≥ 0.8 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 5.89 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-21T00:08:40, mistral:mistral-small-latest · verifiee, exemples)

- lecture · rappel_faits : 0.89 → 0.885
- chaine · faux_couverts : 2 → 1.333
- chaine · faux_refus : 0.333 → 0

## Couche 2 — lecture des faits par le modèle

Rappel des faits idéaux : 88% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 5 cas · faits vagues : 1 cas · faits en trop : 26 cas · faits retirés (sans appui ou non dits) : 25 cas

### Contradictions sans effet sur la décision

- `val-09` : bien : objet_divers lu mobilier
- `g-l07` : evenement : autre lu accident
- `g-h03` : bien : element_batiment lu canalisation/mazout; evenement : mazout lu degat_eaux; evenement : mazout lu degat_eaux/vol
- `g2-p01` : effraction : non lu oui
- `g2-p08` : cause_eau : piscine_exterieure lu debordement_aquarium

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 89% (87% – 90%) | 83% (81% – 84%) | **1.333 (1 – 2)** | **0 (0 – 0)** | 16% (13% – 19%) |

Instables : **2** sur 31 · rappel des clauses : 83% · rappel des questions : 100% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 76.5 s · par cas, un à la fois (10 cas) : médiane 3.48 s, 95e centile 5.89 s (lecture 2.71 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.56 s, 95e centile 11.74 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 31 | 90% | 1 ⚠ | 0 |
| garantie : 2.1 | 3 | 100% | 0 | 0 |
| garantie : 2.10 | 13 | 92% | 0 | 0 |
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
| thème : multi | 2 | 100% | 0 | 0 |
| thème : piege | 16 | 88% | 1 ⚠ | 0 |
| thème : variante | 4 | 100% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `val-01` attendu NC, obtenu ? C ? — Pendant que j'étais au travail, quelqu'un est entré par la fenêtre de ma chambre, au rez-de-chaussée, que j'av… *(Obligation de prévention (2.10) : en cas d'absence, « fermer correctement les fenêtres […] facilement accessibles ». Lie)*
- **⚠ couvert à tort** `g2-p08` attendu NC, obtenu C C C — Le bain à bulles installé sur ma terrasse a fui et l'eau a abîmé le canapé du salon. *(Exclusion 2.7 : l'écoulement d'eau des piscines et des bains à bulles extérieurs.)*
- `red-b01` attendu C, obtenu ? ? ? — Mon fils a cassé la vitre de la porte-fenêtre du salon avec un ballon. *(2.9 : le bris de vitres.)*
- `red-b05` attendu NC, obtenu ? NC NC — Le grand miroir que je venais d'acheter, encore dans son carton et pas encore accroché, s'est brisé quand je l… *(Exclusion 2.9 : les dommages aux vitres et biens assimilés non placés.)*
- `g2-p01` attendu C, obtenu ? ? ? — Pendant mes vacances, des cambrioleurs ont ouvert ma porte sans la casser : il n'y a que des traces de tournev… *(Pas d'effraction au sens du contrat, mais la porte était fermée à clé : l'obligation est respectée, le vol dans le bâtim)*
