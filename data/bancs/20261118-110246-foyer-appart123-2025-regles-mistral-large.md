# Banc d'essai — foyer-appart123-2025, méthode `regles`, lecture par `mistral:mistral-large-latest`

2026-11-18T10:14:39 · golden set v6 (97 cas, empreinte `0b83f83b91580639`) · cas validés par l'auteur : 0 sur 97


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 0.8 | ✓ |
| lecture | decisions_changees | ≤ 2 | 13.67 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 0 | ✓ |
| lecture | cas_avec_contradiction | ≤ 5 | 7 | ✗ |
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0.333 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.907 | ✓ |
| chaine | instables | ≤ 3 | 9 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 0.606 | ✗ |

## Depuis le banc précédent (2026-11-18T09:59:59)

- lecture · rappel_faits : 0.778 → 0.894
- chaine · exactitude : 0.753 → 0.907
- chaine · exactitude_stricte : 0.546 → 0.681
- chaine · faux_couverts : 9.333 → 0
- chaine · faux_refus : 5 → 0.333

## Couche 1 — règles seules (faits idéaux, sans modèle)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 100% | 80% | **0** | **0** | 25% |

Rappel des questions attendues : 100% · questions posées par réponse « incertain » : 0.8

Raisonnement par hypothèses : incertains tranchés par une ou deux questions : 21% · questions inutiles retirées : 16

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 97 | 100% | 0 | 0 |
| garantie : 1.4 | 2 | 100% | 0 | 0 |
| garantie : 2.1 | 13 | 100% | 0 | 0 |
| garantie : 2.10 | 40 | 100% | 0 | 0 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.12 | 1 | 100% | 0 | 0 |
| garantie : 2.2 | 6 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.5 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 4 | 100% | 0 | 0 |
| garantie : 2.7 | 16 | 100% | 0 | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 7 | 100% | 0 | 0 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 24 | 100% | 0 | 0 |
| thème : info_manquante | 16 | 100% | 0 | 0 |
| thème : langue | 11 | 100% | 0 | 0 |
| thème : multi | 8 | 100% | 0 | 0 |
| thème : piege | 55 | 100% | 0 | 0 |
| thème : variante | 13 | 100% | 0 | 0 |

### Erreurs des règles

Aucune.

## Couche 2 — lecture des faits par le modèle

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **13.67** par exécution, dont **0** cas vers un couvert à tort.

Rappel des faits idéaux : 89% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 7 cas · faits vagues : 0 cas · faits en trop : 69 cas · faits retirés faute d'appui : 0 cas

### La lecture change la décision

- `velo-04` idéal NC, lu NC ? NC · manque : fermeture = aucune; vol_sur_personne = non · en trop : portes_fermees = non; proprietaire = assure; simple_disparition = non
- `velo-06` idéal NC, lu ? ? ? · manque : fermeture = cadenas; violence = non; vol_sur_personne = non · en trop : effraction = oui; proprietaire = assure
- `bougie-05` idéal C, lu ? C ? · manque : absence = oui; bien = element_batiment/mobilier; embrasement = oui; evenement = incendie; flammes = oui; lieu = logement/terrasse · en trop : auteur = assure; intentionnel = non
- `autre-01` idéal C, lu C ? ? · manque : violence = oui · en trop : proprietaire = assure; simple_disparition = non
- `val-11` idéal NC, lu NC ? NC
- `val-14` idéal NC, lu NC ? NC · manque : lieu = logement; vol_sur_personne = non · en trop : auteur = tiers; proprietaire = assure; simple_disparition = non
- `red-t04` idéal C, lu ? ? ? · en trop : cause_eau = infiltration_exterieure
- `red-b04` idéal NC, lu NC NC ? · manque : bien = objet_verre_non_vitre; evenement = bris; lieu = logement · en trop : type_dommage = bris
- `g-q02` idéal ?, lu NC NC NC · en trop : proprietaire = assure; simple_disparition = oui
- `g-p02` idéal C, lu ? ? ? · manque : lieu = logement · en trop : auteur = tiers; proprietaire = assure; simple_disparition = non; vol_sur_personne = non
- `g2-i01` idéal ?, lu NC NC NC · en trop : lieu = parties_communes; proprietaire = assure
- `g2-i02` idéal C, lu NC NC ? · **contredit** : bien : objet_divers lu element_batiment; effraction : non lu oui · manque : bien = objet_divers · en trop : auteur = tiers; proprietaire = assure; simple_disparition = non; vol_sur_personne = non
- `g2-i04` idéal ?, lu NC NC NC · en trop : evenement = autre; proprietaire = assure; simple_disparition = oui
- `g2-i05` idéal ?, lu NC NC ? · en trop : embrasement = non
- `g2-i16` idéal ?, lu ? ? NC · **contredit** : lieu : logement lu autre_batiment · manque : lieu = logement · en trop : bien = element_batiment; cause_eau = fuite_installation
- `g2-p01` idéal C, lu ? ? ? · **contredit** : effraction : non lu oui · manque : bien = objet_divers · en trop : auteur = tiers; fermeture = cle; vol_sur_personne = non
- `g2-i07` idéal NC, lu ? ? ? · manque : lieu = voie_publique; vol_sur_personne = non · en trop : proprietaire = assure
- `g2-m01` idéal C, lu ? ? ? · manque : embrasement = oui

### Contradictions sans effet sur la décision

- `val-05` : evenement : vol lu autre
- `red-t03` : bien : element_batiment lu objet_divers; lieu : garage lu annexe
- `red-b06` : evenement : bris lu autre
- `g2-i08` : lieu : autre_batiment lu voie_publique

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 91% (90% – 92%) | 68% (66% – 69%) | **0 (0 – 0)** | **0.333 (0 – 1)** | 30% (28% – 31%) |

Instables : **9** sur 97 · rappel des clauses : 67% · rappel des questions : 61% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 933.9 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 97 | 91% | 0 | 0 |
| garantie : 1.4 | 2 | 100% | 0 | 0 |
| garantie : 2.1 | 13 | 77% | 0 | 0 |
| garantie : 2.10 | 40 | 85% | 0 | 0 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.12 | 1 | 100% | 0 | 0 |
| garantie : 2.2 | 6 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.5 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 4 | 100% | 0 | 0 |
| garantie : 2.7 | 16 | 100% | 0 | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 7 | 100% | 0 | 0 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 24 | 100% | 0 | 0 |
| thème : info_manquante | 16 | 81% | 0 | 0 |
| thème : langue | 11 | 100% | 0 | 0 |
| thème : multi | 8 | 75% | 0 | 0 |
| thème : piege | 55 | 91% | 0 | 0 |
| thème : variante | 13 | 85% | 0 | 0 |

### Erreurs et instabilités

- `velo-04` attendu NC, obtenu NC ? NC — Mon vélo a été volé dans ma cave privative. J'avais oublié de la fermer à clé et il n'y a aucune trace d'effra… *(Cave non fermée : pas de serrure de sûreté (condition du plafond caves), et obligation de prévention non respectée avec )*
- `velo-06` attendu NC, obtenu ? ? ? — Mon vélo était attaché à un arceau dans la rue avec un antivol. L'antivol a été coupé et le vélo volé. *(Vol dans la rue, sans violence : hors du bâtiment, et ce n'est pas un « vol commis sur l'assuré … suite à violences ».)*
- `bougie-05` attendu C, obtenu ? C ? — J'ai oublié une bougie allumée sur la terrasse avant de partir trois semaines. Le feu s'est propagé à la façad… *(Incendie qui atteint la façade et le séjour : couvert, même par imprudence. L'absence de trois semaines n'est pas une in)*
- `autre-01` attendu C, obtenu C ? ? — Mon téléphone m'a été arraché des mains dans la rue. *(« Vol commis sur l'assuré, en dehors des biens assurés, suite à violences physiques et/ou menaces » (2.10), plafond 2 50)*
- `val-11` attendu NC, obtenu NC ? NC — Pendant un orage, la pluie s'est infiltrée par la fenêtre mal jointée de ma chambre et a abîmé le mur et la mo… *(Exclusion 2.7 : une infiltration par les fenêtres, autre que celle due à une fuite des installations hydrauliques extéri)*
- `val-14` attendu NC, obtenu NC ? NC — Lors d'un cambriolage avec la porte fracturée, on m'a volé mon chat de race. *(Exclusion 2.10 : le vol des animaux.)*
- `red-b04` attendu NC, obtenu NC NC ? — Un vase en cristal est tombé de l'étagère et s'est brisé. *(Exclusion 2.9 : les objets en verre autres que des vitres et biens assimilés.)*
- `g-p02` attendu C, obtenu ? ? ? — Lors d'un cambriolage avec la porte fracturée, on m'a volé des bijoux d'une valeur de 8 000 €. *(2.10 : couvert, mais limité à 3 500 EUR pour les bijoux (la limite n'est pas encore dans les règles).)*
- `g2-i01` attendu ?, obtenu NC NC NC — Mon vélo a été volé dans le local de mon immeuble. *(« Le local de mon immeuble » : local commun (vol exclu dans les parties communes) ou cave privative (couverte si serrure)*
- `g2-i02` attendu ?, obtenu NC NC ? — On a cambriolé mon appartement pendant le week-end où j'étais absent. La serrure porte des rayures, mais la po… *(Des traces sans réparation nécessaire ne sont pas une effraction (définition). Sans effraction, l'obligation de fermer à)*
- `g2-i05` attendu ?, obtenu NC NC ? — Il y a eu un début de feu dans la cuisine. *(L'incendie suppose flammes et embrasement ; les dégâts et l'embrasement sont à préciser.)*
- `g2-i16` attendu C, obtenu ? ? NC — De l'eau de mon appartement s'est infiltrée chez le voisin du dessous, qui me demande de payer ses réparations… *(2.5 : responsabilité civile du fait du bâtiment et du contenu envers les tiers. Garantie non traduite.)*
- `g2-p01` attendu C, obtenu ? ? ? — Pendant mes vacances, des cambrioleurs ont ouvert ma porte sans la casser : il n'y a que des traces de tournev… *(Pas d'effraction au sens du contrat, mais la porte était fermée à clé : l'obligation est respectée, le vol dans le bâtim)*
- `g2-i07` attendu NC, obtenu ? ? ? — Mon ordinateur portable a été volé dans ma voiture, garée devant chez moi. *(La voiture n'est pas le bâtiment, et ce n'est pas un vol commis sur l'assuré avec violences.)*
- `g2-m01` attendu C, obtenu ? ? ? — Un court-circuit a provoqué un incendie dans le salon ; pour entrer, les pompiers ont dû casser la porte d'ent… *(2.1 : l'incendie, et les dégâts causés pour l'éteindre.)*
