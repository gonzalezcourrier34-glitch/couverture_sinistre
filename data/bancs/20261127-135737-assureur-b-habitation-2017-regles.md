# Banc d'essai — assureur-b-habitation-2017, méthode `regles`

2026-11-27T13:57:37 · golden set v14 (15 cas, empreinte `b2148e39ad12cab0`) · cas validés par l'auteur : 0 sur 15


## Portes : **PASSE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 1.5 | ✓ |

## Depuis le banc précédent de même configuration (2026-11-27T13:51:02)


## Couche 1 — règles seules (faits idéaux, sans modèle)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 100% | 93% | **0** | **0** | 13% |

Rappel des questions attendues : 100% · questions posées par réponse « incertain » : 1.5

Raisonnement par hypothèses : incertains tranchés par une ou deux questions : 50% · questions inutiles retirées : 19

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 15 | 100% | 0 | 0 |
| garantie : 3.1.6 | 15 | 100% | 0 | 0 |
| thème : base | 7 | 100% | 0 | 0 |
| thème : incertain | 1 | 100% | 0 | 0 |
| thème : piege | 7 | 100% | 0 | 0 |

### Erreurs des règles

Aucune.
