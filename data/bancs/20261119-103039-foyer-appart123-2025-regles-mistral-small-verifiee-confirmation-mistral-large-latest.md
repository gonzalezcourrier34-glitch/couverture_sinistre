# Banc d'essai — foyer-appart123-2025, méthode `regles`, lecture par `mistral:mistral-small-latest` (verifiee, confirmation mistral-large-latest)

2026-11-19T10:05:33 · golden set v9 (97 cas, empreinte `68cb3c13ea714708`) · cas validés par l'auteur : 0 sur 97


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 1.9 | ✓ |
| lecture | decisions_changees | ≤ 2 | 22.33 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 9 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 17 | ✗ |
| chaine | faux_couverts | ≤ 0 | 1.667 | ✗ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.862 | ✓ |
| chaine | instables | ≤ 3 | 13 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 0.788 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 40.33 | ✗ |

## Depuis le banc précédent (2026-11-19T09:54:33)

- lecture · rappel_faits : 0.877 → 0.871
- chaine · exactitude : 0.89 → 0.862
- chaine · exactitude_stricte : 0.753 → 0.673
- chaine · faux_couverts : 4 → 1.667
- chaine · faux_refus : 0.667 → 0

## Couche 1 — règles seules (faits idéaux, sans modèle)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 100% | 91% | **0** | **0** | 16% |

Rappel des questions attendues : 100% · questions posées par réponse « incertain » : 1.9

Raisonnement par hypothèses : incertains tranchés par une ou deux questions : 69% · questions inutiles retirées : 29

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

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **22.33** par exécution, dont **9** cas vers un couvert à tort.

Rappel des faits idéaux : 87% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 17 cas · faits vagues : 0 cas · faits en trop : 82 cas · faits retirés (sans appui ou non dits) : 81 cas

### La lecture change la décision

- **⚠ vers couvert** `bougie-04` idéal NC, lu C NC C · **contredit** : lieu : jardin lu logement/terrasse · manque : absence = oui · en trop : auteur = assure; cause_dommage = autre; intentionnel = non; manque_entretien = non; proprietaire = assure; travaux_batiment = aucun; travaux_vitres = aucun; type_dommage = bris · retiré sans appui : chaleur_sans_feu = non; effraction = non; intentionnel = non; travaux_batiment = aucun
- **⚠ vers couvert** `val-03` idéal NC, lu NC C C · manque : vol_sur_personne = non · en trop : auteur = tiers; simple_disparition = non · retiré sans appui : auteur = tiers; fermeture = aucune; portes_fermees = non
- **⚠ vers couvert** `red-b06` idéal NC, lu C C C · **contredit** : evenement : bris lu vandalisme · manque : type_dommage = rayure_ou_ecaillement · en trop : auteur = tiers; effraction = non · retiré sans appui : effraction = non; fenetres_fermees = non; fermeture = aucune; intentionnel = oui
- **⚠ vers couvert** `g-p03` idéal ?, lu C C C · **contredit** : bien : objet_divers lu cles · manque : absence = oui; portes_fermees = oui · en trop : auteur = tiers; fermeture = cle · retiré sans appui : fermeture = aucune
- **⚠ vers couvert** `g-h02` idéal ?, lu C C C · en trop : cause_perte_alimentaire = coupure_soudaine_reseau; chaleur_sans_feu = oui; proprietaire = assure; usage_professionnel = non · retiré sans appui : embrasement = non; flammes = non
- **⚠ vers couvert** `g2-i11` idéal ?, lu ? C C · **contredit** : lieu : terrasse lu logement · en trop : occupation_partielle = oui; type_dommage = bris · retiré sans appui : travaux_batiment = aucun; travaux_vitres = aucun; vent_dommages_voisins = oui
- **⚠ vers couvert** `g2-i16` idéal ?, lu C C NC · en trop : auteur = assure; bien = element_batiment; cause_eau = infiltration_exterieure · retiré sans appui : intentionnel = non
- **⚠ vers couvert** `g2-p04` idéal NC, lu ? C ? · **contredit** : evenement : vol lu mazout · en trop : auteur = tiers; bien_a_l_origine_sinistre = non · retiré sans appui : auteur = tiers; bien_a_l_origine_sinistre = non; intentionnel = oui
- **⚠ vers couvert** `g2-p08` idéal NC, lu C C C · **contredit** : cause_eau : piscine_exterieure lu debordement_aquarium · retiré sans appui : travaux_batiment = aucun
- `velo-03` idéal NC, lu ? NC ? · **contredit** : fermeture : cadenas lu cle · en trop : auteur = tiers; proprietaire = assure; serrure_surete = non; simple_disparition = non; violence = non · retiré sans appui : serrure_surete = non; simple_disparition = non; violence = non
- `velo-04` idéal NC, lu ? ? NC · manque : effraction = non; fermeture = aucune; vol_sur_personne = non · en trop : proprietaire = assure · retiré sans appui : effraction = non; fermeture = aucune; simple_disparition = non; vol_sur_personne = non
- `val-10` idéal NC, lu ? ? ? · manque : prevention_gel = non · en trop : periode_gel = oui; travaux_batiment = aucun · retiré sans appui : prevention_gel = non
- `val-11` idéal NC, lu ? ? ? · en trop : alea_tempete = vent; auteur = assure; construction_close = oui; intentionnel = non; periode_gel = non; travaux_batiment = aucun · retiré sans appui : travaux_batiment = aucun
- `val-12` idéal C, lu NC NC NC · **contredit** : cause_eau : fuite_installation lu debordement_recipient · en trop : absence = non; auteur = assure; intentionnel = non; travaux_batiment = aucun
- `val-13` idéal C, lu ? ? ? · **contredit** : cause_eau : infiltration_toiture lu infiltration_exterieure · en trop : alea_tempete = vent; travaux_batiment = aucun
- `red-t03` idéal NC, lu ? NC ? · manque : annexe_ancree_beton = non; construction_close = non · retiré sans appui : annexe_ancree_beton = non; construction_close = non
- `red-b01` idéal C, lu NC NC C · en trop : auteur = famille; intentionnel = oui; manque_entretien = non; proprietaire = assure; travaux_batiment = aucun; travaux_vitres = aucun; type_dommage = bris; vitre_placee = oui · retiré sans appui : absence = non; effraction = non; manque_entretien = non; travaux_batiment = aucun; travaux_vitres = aucun
- `g-q02` idéal ?, lu NC NC NC · en trop : evenement = vol; proprietaire = assure; simple_disparition = oui; vol_sur_personne = non · retiré sans appui : fermeture = aucune; vol_sur_personne = non
- `g-h03` idéal C, lu ? ? ? · en trop : bien_a_l_origine_sinistre = oui
- `g2-i01` idéal ?, lu NC NC NC · en trop : auteur = tiers; lieu = parties_communes; occupation_partielle = oui; proprietaire = assure; simple_disparition = non · retiré sans appui : auteur = tiers; fermeture = aucune; vol_sur_personne = non
- `g2-i03` idéal C, lu NC NC NC · en trop : cause_eau = infiltration_exterieure
- `g2-i04` idéal ?, lu NC NC NC · en trop : auteur = tiers; evenement = vol; proprietaire = assure; simple_disparition = oui; vol_sur_personne = non · retiré sans appui : fermeture = aucune; vol_sur_personne = non
- `g2-i07` idéal NC, lu ? ? ? · **contredit** : lieu : voie_publique lu vehicule · manque : vol_sur_personne = non · en trop : proprietaire = assure; simple_disparition = non · retiré sans appui : fermeture = aucune; vol_sur_personne = non
- `g2-l03` idéal C, lu ? ? ? · manque : absence = non; bien = objet_divers · en trop : effraction = oui; fermeture = cle; portes_fermees = oui; violence = non; vol_sur_personne = non · retiré sans appui : absence = non; effraction = oui; violence = non; vol_sur_personne = non
- `g2-m02` idéal C, lu ? ? C · en trop : alea_tempete = vent; cause_eau = infiltration_exterieure · retiré sans appui : construction_close = oui

### Contradictions sans effet sur la décision

- `bougie-01` : evenement : autre lu degat_eaux
- `bougie-03` : evenement : autre lu fumee
- `val-09` : bien : objet_divers lu mobilier; evenement : autre lu fumee
- `g-l07` : evenement : autre lu bris
- `g2-i02` : bien : objet_divers lu bijoux; effraction : non lu oui
- `g2-i08` : lieu : autre_batiment lu voie_publique
- `g2-p01` : bien : objet_divers lu cles; bien : objet_divers lu element_batiment; effraction : non lu oui

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 86% (84% – 88%) | 67% (65% – 69%) | **1.667 (1 – 2)** | **0 (0 – 0)** | 42% (40% – 42%) |

Instables : **13** sur 97 · rappel des clauses : 68% · rappel des questions : 79% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 448.1 s · par cas, un à la fois (10 cas) : médiane 8.58 s, 95e centile 40.33 s (lecture 2.76 s, décision 0.0 s) · en masse (quatre à la fois) : médiane 9.37 s, 95e centile 72.72 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 97 | 88% | 1 ⚠ | 0 |
| garantie : 1.4 | 2 | 100% | 0 | 0 |
| garantie : 2.1 | 13 | 62% | 0 | 0 |
| garantie : 2.10 | 40 | 95% | 0 | 0 |
| garantie : 2.11 | 1 | 100% | 0 | 0 |
| garantie : 2.12 | 1 | 100% | 0 | 0 |
| garantie : 2.2 | 6 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.5 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 4 | 100% | 0 | 0 |
| garantie : 2.7 | 16 | 75% | 1 ⚠ | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 7 | 86% | 0 | 0 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 24 | 96% | 0 | 0 |
| thème : info_manquante | 16 | 100% | 0 | 0 |
| thème : langue | 11 | 91% | 0 | 0 |
| thème : multi | 8 | 62% | 0 | 0 |
| thème : piege | 55 | 89% | 1 ⚠ | 0 |
| thème : variante | 13 | 85% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `val-03` attendu NC, obtenu NC C C — Des amis que j'hébergeais pour le week-end se sont fait voler leur ordinateur lors d'un cambriolage de mon app… *(Exclusion 2.10 : le vol des biens appartenant à des hôtes (alors que la définition du contenu les inclut : piège).)*
- **⚠ couvert à tort** `g2-p08` attendu NC, obtenu C C C — Le bain à bulles installé sur ma terrasse a fui et l'eau a abîmé le canapé du salon. *(Exclusion 2.7 : l'écoulement d'eau des piscines et des bains à bulles extérieurs.)*
- `velo-04` attendu NC, obtenu ? ? NC — Mon vélo a été volé dans ma cave privative. J'avais oublié de la fermer à clé et il n'y a aucune trace d'effra… *(Cave non fermée : pas de serrure de sûreté (condition du plafond caves), et obligation de prévention non respectée avec )*
- `bougie-02` attendu C, obtenu ? ? ? — Une bougie allumée est tombée dans le salon, la nappe a pris feu et les flammes ont brûlé la table. *(Flammes, embrasement de la nappe : incendie au sens du contrat (2.1, 12/incendie).)*
- `bougie-04` attendu NC, obtenu ? NC ? — Pendant mes vacances, une bougie laissée sur la table du jardin s'est enflammée et a brûlé la table et le salo… *(Vrai incendie, mais table et salon de jardin = contenu du jardin, exclu du contenu assuré (12/contenu). INCERTAIN défend)*
- `bougie-05` attendu C, obtenu ? C ? — J'ai oublié une bougie allumée sur la terrasse avant de partir trois semaines. Le feu s'est propagé à la façad… *(Incendie qui atteint la façade et le séjour : couvert, même par imprudence. L'absence de trois semaines n'est pas une in)*
- `autre-02` attendu C, obtenu ? ? ? — Le tuyau du lave-linge a cédé et l'eau a abîmé le parquet et le canapé. *(Dégâts des eaux couverts (2.7) ; le tuyau à l'origine est exclu (2.7-b) mais sa réparation relève des garanties compléme)*
- `val-05` attendu NC, obtenu NC NC ? — Au retour de vacances, je ne retrouve plus ma montre de valeur. Aucune trace de passage ni d'effraction dans l… *(2.10 : « le vol du contenu situé dans le bâtiment sauf la simple disparition ».)*
- `val-11` attendu NC, obtenu ? ? ? — Pendant un orage, la pluie s'est infiltrée par la fenêtre mal jointée de ma chambre et a abîmé le mur et la mo… *(Exclusion 2.7 : une infiltration par les fenêtres, autre que celle due à une fuite des installations hydrauliques extéri)*
- `val-12` attendu C, obtenu ? ? ? — Ma baignoire a débordé pendant que j'étais au téléphone ; l'eau a abîmé mon parquet. *(2.7 couvre l'ensemble des dégâts des eaux ; l'exclusion du récipient vise un récipient NON relié à l'installation hydrau)*
- `red-b01` attendu C, obtenu ? ? C — Mon fils a cassé la vitre de la porte-fenêtre du salon avec un ballon. *(2.9 : le bris de vitres.)*
- `g-l04` attendu C, obtenu ? C ? — La friteuse a pris feu ; les flammes sont montées jusqu'à la hotte et ont brûlé les placards de la cuisine. *(2.1 : incendie (flammes et embrasement).)*
- `g-p02` attendu C, obtenu C ? ? — Lors d'un cambriolage avec la porte fracturée, on m'a volé des bijoux d'une valeur de 8 000 €. *(2.10 : couvert, mais limité à 3 500 EUR pour les bijoux (la limite n'est pas encore dans les règles).)*
- `g-p04` attendu C, obtenu C ? ? — Le chauffe-eau a fui ; le parquet est abîmé et le chauffe-eau lui-même est hors d'usage. *(2.7 : le parquet est couvert ; le chauffe-eau à l'origine du sinistre est exclu (exclusion partielle).)*
- `g-m02` attendu C, obtenu ? ? ? — Un incendie chez le voisin s'est propagé à mon appartement ; les pompiers ont inondé le salon en l'éteignant. *(2.1 : incendie ; l'eau d'extinction en est la conséquence.)*
- `g2-i01` attendu ?, obtenu ? ? NC — Mon vélo a été volé dans le local de mon immeuble. *(« Le local de mon immeuble » : local commun (vol exclu dans les parties communes) ou cave privative (couverte si serrure)*
- `g2-p01` attendu C, obtenu C C ? — Pendant mes vacances, des cambrioleurs ont ouvert ma porte sans la casser : il n'y a que des traces de tournev… *(Pas d'effraction au sens du contrat, mais la porte était fermée à clé : l'obligation est respectée, le vol dans le bâtim)*
- `g2-i07` attendu NC, obtenu ? ? ? — Mon ordinateur portable a été volé dans ma voiture, garée devant chez moi. *(La voiture n'est pas le bâtiment, et ce n'est pas un vol commis sur l'assuré avec violences.)*
- `g2-p04` attendu NC, obtenu ? ? ? — On a siphonné le fioul de la cuve de chauffage, dans ma cave. *(Exclusion 2.10 : le vol de mazout de chauffage.)*
- `g2-m01` attendu C, obtenu ? C ? — Un court-circuit a provoqué un incendie dans le salon ; pour entrer, les pompiers ont dû casser la porte d'ent… *(2.1 : l'incendie, et les dégâts causés pour l'éteindre.)*
- `g2-m02` attendu C, obtenu ? ? C — La tempête a cassé la fenêtre du salon et la pluie a abîmé le canapé. *(La vitre est couverte par le bris de vitrages (2.9) ; le canapé relève de la tempête (2.2), non traduite.)*
