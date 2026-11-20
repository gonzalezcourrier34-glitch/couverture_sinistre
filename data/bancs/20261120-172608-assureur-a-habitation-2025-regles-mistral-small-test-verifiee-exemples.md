# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee, exemples)

2026-11-20T17:18:06 · golden set v12, partie « test » (31 cas, empreinte `0534a0545f66a07d`) · cas validés par l'auteur : 0 sur 31


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| lecture | cas_avec_contradiction | ≤ 5 | 5 | ✓ |
| chaine | faux_couverts | ≤ 0 | 2 | ✗ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.892 | ✓ |
| chaine | instables | ≤ 3 | 2 | ✓ |
| chaine | rappel_questions | ≥ 0.8 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 4.86 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-20T16:50:06, mistral:mistral-small-latest · verifiee, exemples)

- lecture · rappel_faits : 0.879 → 0.866
- chaine · exactitude : 0.871 → 0.892
- chaine · exactitude_stricte : 0.839 → 0.828
- chaine · faux_couverts : 3 → 2

## Couche 2 — lecture des faits par le modèle

Rappel des faits idéaux : 87% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 5 cas · faits vagues : 1 cas · faits en trop : 27 cas · faits retirés (sans appui ou non dits) : 20 cas

### Contradictions sans effet sur la décision

- `val-09` : bien : objet_divers lu mobilier
- `g-l07` : evenement : autre lu accident
- `g-h03` : bien : element_batiment lu canalisation/mazout; evenement : mazout lu degat_eaux
- `g2-p01` : bien : objet_divers lu element_batiment; effraction : non lu oui
- `g2-p08` : cause_eau : piscine_exterieure lu debordement_aquarium

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 89% (87% – 90%) | 83% (81% – 84%) | **2 (2 – 2)** | **0 (0 – 0)** | 14% (13% – 16%) |

Instables : **2** sur 31 · rappel des clauses : 77% · rappel des questions : 100% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 147.9 s · par cas, un à la fois (10 cas) : médiane 3.6 s, 95e centile 4.86 s (lecture 2.69 s, décision 0.02 s) · en masse (quatre à la fois) : médiane 4.21 s, 95e centile 70.31 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 31 | 90% | 2 ⚠ | 0 |
| garantie : 2.1 | 3 | 100% | 0 | 0 |
| garantie : 2.10 | 13 | 92% | 0 | 0 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.6 | 2 | 100% | 0 | 0 |
| garantie : 2.7 | 5 | 80% | 1 ⚠ | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 3 | 67% | 1 ⚠ | 0 |
| garantie : aucune | 1 | 100% | 0 | 0 |
| thème : base | 1 | 100% | 0 | 0 |
| thème : hors_regles | 9 | 89% | 1 ⚠ | 0 |
| thème : info_manquante | 3 | 100% | 0 | 0 |
| thème : langue | 4 | 100% | 0 | 0 |
| thème : multi | 2 | 100% | 0 | 0 |
| thème : piege | 16 | 88% | 2 ⚠ | 0 |
| thème : variante | 4 | 75% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `red-b05` attendu NC, obtenu C C C — Le grand miroir que je venais d'acheter, encore dans son carton et pas encore accroché, s'est brisé quand je l… *(Exclusion 2.9 : les dommages aux vitres et biens assimilés non placés.)*
- **⚠ couvert à tort** `g2-p08` attendu NC, obtenu C C C — Le bain à bulles installé sur ma terrasse a fui et l'eau a abîmé le canapé du salon. *(Exclusion 2.7 : l'écoulement d'eau des piscines et des bains à bulles extérieurs.)*
- `velo-06` attendu NC, obtenu ? ? NC — Mon vélo était attaché à un arceau dans la rue avec un antivol. L'antivol a été coupé et le vélo volé. *(Vol dans la rue, sans violence : hors du bâtiment, et ce n'est pas un « vol commis sur l'assuré … suite à violences ».)*
- `red-b01` attendu C, obtenu C ? ? — Mon fils a cassé la vitre de la porte-fenêtre du salon avec un ballon. *(2.9 : le bris de vitres.)*
