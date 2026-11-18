# Banc LegalBench · insurance_policy_interpretation · mistral:mistral-small-latest

2026-11-18T11:02:53 · 10 cas · données CC BY 4.0 (Guha et al., 2023 ; « Vague Contracts »)

| | Exactitude | Équilibrée | Couverts à tort | Refus à tort | Rappel « ambigu » | Précision « incertain » | Incertains |
|---|---|---|---|---|---|---|---|
| Réponse du modèle | 60 % | 67 % | 2 | 0 | 0 % | — | 0 % |
| Après contrôle des citations | 60 % | 67 % | 2 | 0 | 0 % | — | 0 % |

Réponses fermes du modèle : 10, dont **0 sans citation retrouvée dans la clause** ; 0 réponse(s) changée(s) par le contrôle.

## Confusion, après contrôle

| attendu \ obtenu | couvert | non couvert | ambigu / incertain | erreur |
|---|---|---|---|---|
| couvert | 3 | 0 | 0 | 0 |
| non couvert | 0 | 3 | 0 | 0 |
| ambigu / incertain | 2 | 2 | 0 | 0 |

## Confusion, réponse du modèle

| attendu \ obtenu | couvert | non couvert | ambigu / incertain | erreur |
|---|---|---|---|---|
| couvert | 3 | 0 | 0 | 0 |
| non couvert | 0 | 3 | 0 | 0 |
| ambigu / incertain | 2 | 2 | 0 | 0 |

## Les 4 écarts (après contrôle)

- `test-2` attendu ambigu / incertain, obtenu couvert (modèle : couvert) — « any work that requires, uses or produces any sources of heat that could ignite flammable materials ». L'utilisation d'un pistolet à chaleur pour sécher de la colle (source de chaleur) correspond à la définition de 'Hot Work' dans la clause, car cet outil pourrait enflammer des matériaux inflammables.
- `test-5` attendu ambigu / incertain, obtenu couvert (modèle : couvert) — « necessary and reasonable costs that you incur in locating and fixing accidental damage to cables or pipes in your home ». La clause couvre les coûts nécessaires et raisonnables engagés pour localiser et réparer des dommages accidentels causés aux canalisations dans la maison, ce qui inclut les travaux de démolition pour accéder à la canalisation.
- `test-8` attendu ambigu / incertain, obtenu non couvert (modèle : non couvert) — « loss or damage as a result of fire to the policy holder's car or audio equipment (while in or on the car) ». Le sinistre concerne un smartphone et un haut-parleur Bluetooth, qui ne sont pas des équipements audio intégrés au véhicule ou situés dans/on le véhicule au moment du sinistre.
- `test-9` attendu ambigu / incertain, obtenu non couvert (modèle : non couvert) — « damage to buildings and contents caused by a sudden, unforeseen flow of water from an internal source, such as a burst pipe or faulty applia ». Le sinistre implique un écoulement de jus de tomate, et non d'eau, même si le liquide provient d'une source interne.
