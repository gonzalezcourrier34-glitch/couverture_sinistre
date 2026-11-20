# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee, exemples)

2026-11-20T16:50:06 · golden set v12, partie « test » (31 cas, empreinte `0534a0545f66a07d`) · cas validés par l'auteur : 0 sur 31


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| lecture | cas_avec_contradiction | ≤ 5 | 6 | ✗ |
| chaine | faux_couverts | ≤ 0 | 3 | ✗ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.871 | ✓ |
| chaine | instables | ≤ 3 | 0 | ✓ |
| chaine | rappel_questions | ≥ 0.8 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 10.55 | ✗ |

## Couche 2 — lecture des faits par le modèle

Rappel des faits idéaux : 88% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 6 cas · faits vagues : 1 cas · faits en trop : 27 cas · faits retirés (sans appui ou non dits) : 22 cas

### Contradictions sans effet sur la décision

- `val-09` : bien : objet_divers lu mobilier
- `g-l07` : evenement : autre lu accident
- `g-p03` : bien : objet_divers lu cles
- `g-h03` : bien : element_batiment lu canalisation/mazout; evenement : mazout lu degat_eaux
- `g2-p01` : bien : objet_divers lu mobilier; effraction : non lu oui
- `g2-p08` : cause_eau : piscine_exterieure lu debordement_aquarium

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 87% (87% – 87%) | 84% (84% – 84%) | **3 (3 – 3)** | **0 (0 – 0)** | 10% (10% – 10%) |

Instables : **0** sur 31 · rappel des clauses : 79% · rappel des questions : 100% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 64.2 s · par cas, un à la fois (10 cas) : médiane 4.04 s, 95e centile 10.55 s (lecture 2.91 s, décision 0.02 s) · en masse (quatre à la fois) : médiane 3.85 s, 95e centile 37.02 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 31 | 87% | 3 ⚠ | 0 |
| garantie : 2.1 | 3 | 100% | 0 | 0 |
| garantie : 2.10 | 13 | 92% | 1 ⚠ | 0 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.6 | 2 | 100% | 0 | 0 |
| garantie : 2.7 | 5 | 80% | 1 ⚠ | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 3 | 33% | 1 ⚠ | 0 |
| garantie : aucune | 1 | 100% | 0 | 0 |
| thème : base | 1 | 100% | 0 | 0 |
| thème : hors_regles | 9 | 78% | 1 ⚠ | 0 |
| thème : info_manquante | 3 | 100% | 0 | 0 |
| thème : langue | 4 | 100% | 0 | 0 |
| thème : multi | 2 | 100% | 0 | 0 |
| thème : piege | 16 | 81% | 3 ⚠ | 0 |
| thème : variante | 4 | 100% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `red-b05` attendu NC, obtenu C C C — Le grand miroir que je venais d'acheter, encore dans son carton et pas encore accroché, s'est brisé quand je l… *(Exclusion 2.9 : les dommages aux vitres et biens assimilés non placés.)*
- **⚠ couvert à tort** `g-p03` attendu NC, obtenu C C C — Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune… *(Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct.)*
- **⚠ couvert à tort** `g2-p08` attendu NC, obtenu C C C — Le bain à bulles installé sur ma terrasse a fui et l'eau a abîmé le canapé du salon. *(Exclusion 2.7 : l'écoulement d'eau des piscines et des bains à bulles extérieurs.)*
- `red-b01` attendu C, obtenu ? ? ? — Mon fils a cassé la vitre de la porte-fenêtre du salon avec un ballon. *(2.9 : le bris de vitres.)*
