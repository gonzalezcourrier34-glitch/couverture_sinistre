# Banc d'essai — foyer-appart123-2025, méthode `regles`, lecture par `mistral:mistral-large-latest`

2026-11-17T17:37:28 · golden set v4 (68 cas, empreinte `a6a056729cc7b00b`) · cas validés par l'auteur : 0 sur 68


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 0.9 | ✓ |
| lecture | decisions_changees | ≤ 2 | 6.33 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 0 | ✓ |
| lecture | cas_avec_contradiction | ≤ 5 | 4 | ✓ |
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.961 | ✓ |
| chaine | instables | ≤ 3 | 4 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 1 | ✓ |

## Depuis le banc précédent (2026-11-17T17:29:31)

- lecture · rappel_faits : 0.596 → 0.903
- chaine · exactitude : 0.735 → 0.961
- chaine · exactitude_stricte : 0.387 → 0.716
- chaine · faux_couverts : 2.667 → 0
- chaine · faux_refus : 3 → 0

## Couche 1 — règles seules (faits idéaux, sans modèle)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 100% | 81% | **0** | **0** | 24% |

Rappel des questions attendues : 100% · questions posées par réponse « incertain » : 0.9

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 68 | 100% | 0 | 0 |
| garantie : 2.1 | 11 | 100% | 0 | 0 |
| garantie : 2.10 | 28 | 100% | 0 | 0 |
| garantie : 2.2 | 5 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 3 | 100% | 0 | 0 |
| garantie : 2.7 | 9 | 100% | 0 | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 6 | 100% | 0 | 0 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 19 | 100% | 0 | 0 |
| thème : info_manquante | 6 | 100% | 0 | 0 |
| thème : langue | 7 | 100% | 0 | 0 |
| thème : multi | 6 | 100% | 0 | 0 |
| thème : piege | 41 | 100% | 0 | 0 |
| thème : variante | 13 | 100% | 0 | 0 |

### Erreurs des règles

Aucune.

## Couche 2 — lecture des faits par le modèle

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **6.33** par exécution, dont **0** cas vers un couvert à tort.

Rappel des faits idéaux : 90% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 4 cas · faits vagues : 0 cas · faits en trop : 48 cas · faits retirés faute d'appui : 0 cas

### La lecture change la décision

- `velo-03` idéal NC, lu ? ? NC · **contredit** : fermeture : cadenas lu cle · manque : vol_sur_personne = non · en trop : portes_fermees = oui; proprietaire = assure; simple_disparition = non
- `velo-06` idéal NC, lu ? ? NC · manque : fermeture = cadenas; violence = non; vol_sur_personne = non · en trop : proprietaire = assure; simple_disparition = non
- `val-11` idéal NC, lu NC ? ?
- `val-14` idéal NC, lu NC NC ? · manque : lieu = logement; vol_sur_personne = non · en trop : auteur = tiers; proprietaire = assure; simple_disparition = non
- `red-t01` idéal C, lu ? ? ? · en trop : cause_eau = infiltration_exterieure
- `red-t04` idéal C, lu ? ? ? · en trop : cause_eau = infiltration_exterieure
- `g-q02` idéal ?, lu NC NC NC · en trop : evenement = autre; proprietaire = assure; simple_disparition = oui
- `g-p02` idéal C, lu ? ? ? · manque : lieu = logement · en trop : auteur = tiers; proprietaire = assure; simple_disparition = non; vol_sur_personne = non

### Contradictions sans effet sur la décision

- `val-05` : evenement : vol lu autre
- `red-t03` : bien : element_batiment lu objet_divers; lieu : garage lu jardin
- `red-b06` : evenement : bris lu autre

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 96% (96% – 97%) | 72% (71% – 72%) | **0 (0 – 0)** | **0 (0 – 0)** | 30% (29% – 31%) |

Instables : **4** sur 68 · rappel des clauses : 67% · rappel des questions : 100% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 544.7 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 68 | 97% | 0 | 0 |
| garantie : 2.1 | 11 | 100% | 0 | 0 |
| garantie : 2.10 | 28 | 93% | 0 | 0 |
| garantie : 2.2 | 5 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 3 | 100% | 0 | 0 |
| garantie : 2.7 | 9 | 100% | 0 | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 6 | 100% | 0 | 0 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 19 | 100% | 0 | 0 |
| thème : info_manquante | 6 | 100% | 0 | 0 |
| thème : langue | 7 | 100% | 0 | 0 |
| thème : multi | 6 | 100% | 0 | 0 |
| thème : piege | 41 | 98% | 0 | 0 |
| thème : variante | 13 | 92% | 0 | 0 |

### Erreurs et instabilités

- `velo-03` attendu NC, obtenu ? ? NC — Mon vélo a été volé dans ma cave privative, fermée à clé. Le cadenas de la porte a été forcé. *(Cave en immeuble à appartements : vol couvert à 1 000 EUR « si ces locaux sont fermés avec une serrure de sûreté » (2.10)*
- `velo-06` attendu NC, obtenu ? ? NC — Mon vélo était attaché à un arceau dans la rue avec un antivol. L'antivol a été coupé et le vélo volé. *(Vol dans la rue, sans violence : hors du bâtiment, et ce n'est pas un « vol commis sur l'assuré … suite à violences ».)*
- `val-11` attendu NC, obtenu NC ? ? — Pendant un orage, la pluie s'est infiltrée par la fenêtre mal jointée de ma chambre et a abîmé le mur et la mo… *(Exclusion 2.7 : une infiltration par les fenêtres, autre que celle due à une fuite des installations hydrauliques extéri)*
- `val-14` attendu NC, obtenu NC NC ? — Lors d'un cambriolage avec la porte fracturée, on m'a volé mon chat de race. *(Exclusion 2.10 : le vol des animaux.)*
- `g-p02` attendu C, obtenu ? ? ? — Lors d'un cambriolage avec la porte fracturée, on m'a volé des bijoux d'une valeur de 8 000 €. *(2.10 : couvert, mais limité à 3 500 EUR pour les bijoux (la limite n'est pas encore dans les règles).)*
