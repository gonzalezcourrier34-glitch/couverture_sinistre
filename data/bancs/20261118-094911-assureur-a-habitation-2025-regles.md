# Banc d'essai — assureur-a-habitation-2025, méthode `regles`

2026-11-18T09:48:53 · golden set v5 (97 cas, empreinte `40144a4cdc4f1540`) · cas validés par l'auteur : 0 sur 97


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 4 | ✗ |
| regles | faux_refus | ≤ 0 | 3 | ✗ |
| regles | exactitude | ≥ 0.95 | 0.897 | ✗ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 0.9 | ✓ |

## Depuis le banc précédent (2026-11-17T17:37:28)

- regles · exactitude : 1 → 0.897
- regles · exactitude_stricte : 0.809 → 0.701
- regles · faux_couverts : 0 → 4
- regles · faux_refus : 0 → 3

## Couche 1 — règles seules (faits idéaux, sans modèle)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 90% | 70% | **4** | **3** | 26% |

Rappel des questions attendues : 100% · questions posées par réponse « incertain » : 0.9

Raisonnement par hypothèses : incertains tranchés par une ou deux questions : 28% · questions inutiles retirées : 17

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 97 | 90% | 4 ⚠ | 3 |
| garantie : 1.4 | 2 | 0% | 2 ⚠ | 0 |
| garantie : 2.1 | 13 | 100% | 0 | 0 |
| garantie : 2.10 | 40 | 92% | 0 | 1 |
| garantie : 2.11 | 1 | 0% | 0 | 1 |
| garantie : 2.12 | 1 | 0% | 0 | 0 |
| garantie : 2.2 | 6 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.5 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 4 | 100% | 0 | 0 |
| garantie : 2.7 | 16 | 81% | 2 ⚠ | 1 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 7 | 100% | 0 | 0 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 24 | 92% | 0 | 1 |
| thème : info_manquante | 16 | 94% | 0 | 0 |
| thème : langue | 11 | 100% | 0 | 0 |
| thème : multi | 8 | 100% | 0 | 0 |
| thème : piege | 55 | 86% | 4 ⚠ | 2 |
| thème : variante | 13 | 100% | 0 | 0 |

### Erreurs des règles

- **⚠ couvert à tort** `g2-i13` attendu NC, obtenu C — Le joint de la douche fuyait depuis des mois ; l'eau a fini par abîmer le mur de la salle de bain. *(Exclusion générale 1.4 : manque d'entretien, détérioration lente et progressive.)*
- **⚠ couvert à tort** `g2-i14` attendu NC, obtenu C — Le tuyau apparent de ma cave, très rouillé depuis longtemps, a cédé et l'eau a abîmé les cartons que j'y stock… *(Exclusion 2.7 : les canalisations apparentes présentant plusieurs points de corrosion visibles et non traités.)*
- **⚠ couvert à tort** `g2-p12` attendu NC, obtenu C — Énervé, j'ai donné un coup de poing dans la vitre de la porte-fenêtre, qui s'est brisée. *(Exclusion générale 1.4 : un sinistre intentionnel dont l'assuré est l'auteur.)*
- **⚠ couvert à tort** `g2-p08` attendu NC, obtenu C — Le bain à bulles installé sur ma terrasse a fui et l'eau a abîmé le canapé du salon. *(Exclusion 2.7 : l'écoulement d'eau des piscines et des bains à bulles extérieurs.)*
- `g2-i15` attendu ?, obtenu NC — Un champignon s'est développé derrière les plinthes et a attaqué le parquet ; l'expert parle de mérule. *(2.12 couvre la mérule survenue après la prise d'effet de la garantie : la date est à établir. Garantie non traduite.)*
- `g2-i17` attendu C, obtenu NC — Des inconnus ont tagué et rayé la porte d'entrée de mon appartement. *(2.11 : dégradations immobilières suite à des actes de vandalisme. Garantie non traduite.)*
- `g2-p03` attendu NC, obtenu ? — On a arraché et volé les rosiers de mon jardin. *(Exclusion 2.10 : le vol des plantations du jardin.)*
- `g2-p04` attendu NC, obtenu ? — On a siphonné le fioul de la cuve de chauffage, dans ma cave. *(Exclusion 2.10 : le vol de mazout de chauffage.)*
- `g2-p06` attendu C, obtenu NC — On m'a volé mes clés d'appartement dans la poche, dans le tram, sans violence. *(Limites de la garantie vol : le vol ou la perte des clés (500 EUR) et le remplacement des serrures.)*
- `g2-p09` attendu C, obtenu NC — Des infiltrations par la toiture de l'immeuble ont taché le plafond de mon salon. *(L'exclusion vise les infiltrations par terrasses, balcons, portes, fenêtres ou murs, et les dégâts à la partie extérieur)*
