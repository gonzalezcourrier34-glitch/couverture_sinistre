# Banc d'essai — assureur-b-habitation-2017, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee)

2026-11-20T23:49:02 · golden set v12, partie « test » (7 cas, empreinte `60454afe2fa4e1ae`) · cas validés par l'auteur : 0 sur 7


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| lecture | cas_avec_contradiction | ≤ 5 | 0 | ✓ |
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.809 | ✗ |
| chaine | instables | ≤ 3 | 2 | ✓ |
| chaine | rappel_questions | ≥ 0.8 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 12.21 | ✗ |

## Couche 2 — lecture des faits par le modèle

Rappel des faits idéaux : 81% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 0 cas · faits vagues : 0 cas · faits en trop : 5 cas · faits retirés (sans appui ou non dits) : 6 cas


## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 81% (71% – 86%) | 71% (57% – 86%) | **0 (0 – 0)** | **0 (0 – 0)** | 43% (29% – 57%) |

Instables : **2** sur 7 · rappel des clauses : 86% · rappel des questions : 100% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 9.6 s · par cas, un à la fois (7 cas) : médiane 4.49 s, 95e centile 12.21 s (lecture 3.42 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 4.81 s, 95e centile 6.28 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 7 | 86% | 0 | 0 |
| garantie : 3.1.6 | 7 | 86% | 0 | 0 |
| thème : base | 3 | 100% | 0 | 0 |
| thème : incertain | 1 | 100% | 0 | 0 |
| thème : piege | 3 | 67% | 0 | 0 |

### Erreurs et instabilités

- `b-v02` attendu NC, obtenu NC ? NC — J'avais laissé la porte de l'appartement ouverte pour descendre les poubelles. En remontant, mon portefeuille … *(Vol simple : ni effraction ni violence (3.1.6.2.1).)*
- `b-v06` attendu NC, obtenu ? ? ? — Dans le tram, on m'a subtilisé mon portefeuille dans la poche sans que je m'en rende compte. J'ai la formule P… *(Vol à la tire hors du bâtiment désigné (3.1.6.2.2), et vol simple.)*
- `b-v08` attendu NC, obtenu NC ? ? — Ma table et mes chaises de jardin ont été volées sur la pelouse derrière la maison. Le jardin n'est pas clôtur… *(Lettre du contrat : l'extension Privilège couvre le mobilier de jardin (3.1.6.1), mais les vols simples sont exclus (3.1)*
