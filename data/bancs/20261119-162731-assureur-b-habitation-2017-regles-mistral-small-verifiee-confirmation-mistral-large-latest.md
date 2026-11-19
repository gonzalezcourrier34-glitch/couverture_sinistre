# Banc d'essai — assureur-b-habitation-2017, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee, confirmation mistral-large-latest)

2026-11-19T16:17:54 · golden set v12 (15 cas, empreinte `60454afe2fa4e1ae`) · cas validés par l'auteur : 0 sur 15


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 1.5 | ✓ |
| lecture | decisions_changees | ≤ 2 | 1 | ✓ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 1 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 0 | ✓ |
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 1 | ✓ |
| chaine | instables | ≤ 3 | 2 | ✓ |
| chaine | rappel_questions | ≥ 0.8 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 37.84 | ✗ |

## Depuis le banc précédent de même configuration (2026-11-19T10:30:40, mistral:mistral-small-latest · verifiee, confirmation mistral-large-latest)

- lecture · rappel_faits : 0.754 → 0.835
- chaine · exactitude : 0.822 → 1
- chaine · exactitude_stricte : 0.622 → 0.822

## Couche 1 — règles seules (faits idéaux, sans modèle)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 100% | 87% | **0** | **0** | 13% |

Rappel des questions attendues : 100% · questions posées par réponse « incertain » : 1.5

Raisonnement par hypothèses : incertains tranchés par une ou deux questions : 50% · questions inutiles retirées : 16

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 15 | 100% | 0 | 0 |
| garantie : 3.1.6 | 15 | 100% | 0 | 0 |
| thème : base | 6 | 100% | 0 | 0 |
| thème : incertain | 2 | 100% | 0 | 0 |
| thème : piege | 7 | 100% | 0 | 0 |

### Erreurs des règles

Aucune.

## Couche 2 — lecture des faits par le modèle

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **1** par exécution, dont **1** cas vers un couvert à tort.

Rappel des faits idéaux : 84% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 0 cas · faits vagues : 0 cas · faits en trop : 8 cas · faits retirés (sans appui ou non dits) : 14 cas

### La lecture change la décision

- **⚠ vers couvert** `b-v03` idéal NC, lu C C C · manque : auteur = tiers; vol_sur_personne = non · en trop : sejour_temporaire = non; travaux_batiment = aucun; type_dommage = bris; vitre_placee = oui · retiré sans appui : sejour_temporaire = non; travaux_batiment = aucun; vol_sur_personne = non


## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 100% (100% – 100%) | 82% (73% – 87%) | **0 (0 – 0)** | **0 (0 – 0)** | 27% (27% – 27%) |

Instables : **2** sur 15 · rappel des clauses : 87% · rappel des questions : 100% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 117.4 s · par cas, un à la fois (10 cas) : médiane 22.62 s, 95e centile 37.84 s (lecture 4.54 s, décision 0.02 s) · en masse (quatre à la fois) : médiane 15.45 s, 95e centile 60.41 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 15 | 100% | 0 | 0 |
| garantie : 3.1.6 | 15 | 100% | 0 | 0 |
| thème : base | 6 | 100% | 0 | 0 |
| thème : incertain | 2 | 100% | 0 | 0 |
| thème : piege | 7 | 100% | 0 | 0 |

### Erreurs et instabilités

- `b-v07` attendu ?, obtenu ? C ? — J'ai été agressé en rentrant du travail, on m'a pris mon téléphone sous la menace d'un couteau. J'ai porté pla… *(Le vol par agression n'est couvert qu'en formule Privilège ou Active : à demander. Depuis la traduction de 3.1.7 (19 nov)*
- `b-v08` attendu NC, obtenu NC ? NC — Ma table et mes chaises de jardin ont été volées sur la pelouse derrière la maison. Le jardin n'est pas clôtur… *(Lettre du contrat : l'extension Privilège couvre le mobilier de jardin (3.1.6.1), mais les vols simples sont exclus (3.1)*
