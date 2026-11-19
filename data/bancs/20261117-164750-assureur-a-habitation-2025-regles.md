# Banc d'essai — assureur-a-habitation-2025, méthode `regles`

2026-11-17T16:45:10 · golden set v3 (68 cas, empreinte `6aa85917e50d9c68`) · cas validés par l'auteur : 0 sur 68


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 2 | ✗ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 0.956 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 0.9 | ✓ |
| lecture | decisions_changees | ≤ 2 | 19 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 6 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 12 | ✗ |
| chaine | faux_couverts | ≤ 0 | 4.667 | ✗ |
| chaine | faux_refus | ≤ 1 | 1.333 | ✗ |
| chaine | exactitude | ≥ 0.85 | 0.804 | ✗ |
| chaine | instables | ≤ 3 | 9 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 0.667 | ✗ |

## Depuis le banc précédent (2026-11-17T16:38:24)

- regles · exactitude : 0.853 → 0.956
- regles · faux_refus : 7 → 0
- lecture · rappel_faits : 0.824 → 0.732
- chaine · exactitude : 0.838 → 0.804
- chaine · exactitude_stricte : 0.671 → 0.569
- chaine · faux_refus : 4 → 1.333

## Couche 1 — règles seules (faits idéaux, sans modèle)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 96% | 76% | **2** | **0** | 25% |

Rappel des questions attendues : 100% · questions posées par réponse « incertain » : 0.9

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 68 | 96% | 2 ⚠ | 0 |
| garantie : 2.1 | 11 | 100% | 0 | 0 |
| garantie : 2.10 | 28 | 93% | 1 ⚠ | 0 |
| garantie : 2.2 | 5 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 100% | 0 | 0 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 3 | 100% | 0 | 0 |
| garantie : 2.7 | 9 | 89% | 1 ⚠ | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 6 | 100% | 0 | 0 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 19 | 100% | 0 | 0 |
| thème : info_manquante | 6 | 100% | 0 | 0 |
| thème : langue | 7 | 100% | 0 | 0 |
| thème : multi | 6 | 100% | 0 | 0 |
| thème : piege | 41 | 93% | 2 ⚠ | 0 |
| thème : variante | 13 | 100% | 0 | 0 |

### Erreurs des règles

- **⚠ couvert à tort** `g-p03` attendu NC, obtenu C — Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune… *(Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct.)*
- **⚠ couvert à tort** `g-p06` attendu NC, obtenu C — J'ai renversé le seau d'eau du ménage et l'eau a abîmé le parquet. *(Exclusion 2.7 : le renversement d'un récipient non relié à l'installation hydraulique.)*
- `g-p09` attendu NC, obtenu ? — Mon vélo a été volé dans mon casier du club de sport. *(Exclusion 2.10 : le vol du contenu entreposé dans un casier d'une association sportive (et hors du bâtiment).)*

## Couche 2 — lecture des faits par le modèle

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **19** par exécution, dont **6** cas vers un couvert à tort.

Rappel des faits idéaux : 73% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 12 cas · faits vagues : 1 cas · faits en trop : 20 cas

### La lecture change la décision

- **⚠ vers couvert** `val-01` idéal ?, lu ? C ? · manque : absence = oui; effraction = non; vol_sur_personne = non
- **⚠ vers couvert** `val-05` idéal NC, lu NC C NC · manque : absence = oui; effraction = non; simple_disparition = oui; vol_sur_personne = non
- **⚠ vers couvert** `val-10` idéal NC, lu C C C · manque : absence = oui; prevention_gel = non
- **⚠ vers couvert** `val-13` idéal ?, lu C C C · manque : cause_eau = infiltration_exterieure
- **⚠ vers couvert** `g-q02` idéal ?, lu C C C · en trop : evenement = vol
- **⚠ vers couvert** `g-q03` idéal ?, lu C C C · en trop : lieu = logement
- `velo-03` idéal NC, lu ? ? ? · **contredit** : fermeture : cadenas lu cle · manque : vol_sur_personne = non
- `velo-06` idéal NC, lu ? ? ? · manque : violence = non; vol_sur_personne = non · en trop : effraction = oui
- `bougie-01` idéal NC, lu NC ? NC · manque : absence = oui; embrasement = non; evenement = autre; flammes = non; lieu = jardin · en trop : chaleur_sans_feu = oui
- `autre-01` idéal C, lu ? ? ? · manque : violence = oui
- `autre-02` idéal C, lu ? C C · manque : lieu = logement
- `val-06` idéal C, lu C ? ? · manque : depot_moins_30j = oui; effraction = oui; vol_sur_personne = non
- `val-08` idéal C, lu ? ? ? · manque : lieu = logement
- `val-11` idéal NC, lu NC ? NC · manque : lieu = logement
- `val-12` idéal C, lu ? C ? · **contredit** : cause_eau : fuite_installation lu debordement_recipient · manque : lieu = logement
- `red-b02` idéal C, lu NC NC NC · **contredit** : evenement : bris lu autre · manque : lieu = logement; type_dommage = felure
- `g-l04` idéal C, lu C ? ? · manque : lieu = logement
- `g-l05` idéal C, lu ? ? ? · manque : lieu = logement
- `g-p04` idéal C, lu ? ? ? · manque : lieu = logement
- `g-p05` idéal C, lu ? ? ? · manque : lieu = logement
- `g-p06` idéal C, lu ? ? ? · manque : lieu = logement
- `g-p09` idéal ?, lu NC NC NC · **contredit** : lieu : autre_batiment lu parties_communes · en trop : fermeture = cle
- `g-h04` idéal ?, lu NC ? ? · manque : bien = element_batiment/mobilier
- `g-h06` idéal C, lu ? ? ? · en trop : effraction = oui

### Contradictions sans effet sur la décision

- `val-09` : bien : objet_divers lu electronique
- `red-t03` : lieu : garage lu annexe
- `red-b03` : evenement : bris lu autre
- `red-b04` : evenement : bris lu autre
- `red-b05` : evenement : bris lu autre
- `g-l03` : bien : mobilier_jardin lu mobilier; lieu : jardin lu terrasse
- `g-p03` : bien : objet_divers lu velo
- `g-h02` : bien : objet_divers lu electronique

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 80% (78% – 82%) | 57% (54% – 59%) | **4.667 (4 – 6)** | **1.333 (1 – 2)** | 36% (34% – 37%) |

Instables : **9** sur 68 · rappel des clauses : 60% · rappel des questions : 67% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 34.0 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 68 | 81% | 4 ⚠ | 2 |
| garantie : 2.1 | 11 | 91% | 0 | 0 |
| garantie : 2.10 | 28 | 86% | 3 ⚠ | 0 |
| garantie : 2.2 | 5 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 50% | 0 | 1 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 3 | 100% | 0 | 0 |
| garantie : 2.7 | 9 | 33% | 1 ⚠ | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 6 | 83% | 0 | 1 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 19 | 90% | 0 | 2 |
| thème : info_manquante | 6 | 67% | 2 ⚠ | 0 |
| thème : langue | 7 | 86% | 0 | 0 |
| thème : multi | 6 | 83% | 0 | 0 |
| thème : piege | 41 | 78% | 3 ⚠ | 2 |
| thème : variante | 13 | 85% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `val-01` attendu NC, obtenu ? C ? — Pendant que j'étais au travail, quelqu'un est entré par la fenêtre de ma chambre, au rez-de-chaussée, que j'av… *(Obligation de prévention (2.10) : en cas d'absence, « fermer correctement les fenêtres […] facilement accessibles ». Lie)*
- **⚠ couvert à tort** `val-05` attendu NC, obtenu NC C NC — Au retour de vacances, je ne retrouve plus ma montre de valeur. Aucune trace de passage ni d'effraction dans l… *(2.10 : « le vol du contenu situé dans le bâtiment sauf la simple disparition ».)*
- **⚠ couvert à tort** `val-10` attendu NC, obtenu C C C — En janvier, je suis parti deux semaines en coupant le chauffage. Une canalisation a gelé puis éclaté ; l'eau a… *(2.7 : en période de gel, maintenir une température positive, vidanger ou isoler ; refus s'il y a un lien causal direct. )*
- **⚠ couvert à tort** `g-q02` attendu ?, obtenu C C C — Mon ordinateur portable a disparu de mon appartement. *(« Disparu » n'est pas « volé » : la simple disparition est exclue ; il faut établir le vol.)*
- **⚠ couvert à tort** `g-q03` attendu ?, obtenu C C C — Mon vélo a été volé pendant que je faisais mes courses. *(Le lieu décide (dans le bâtiment ou dehors) : il faut le demander.)*
- **⚠ couvert à tort** `g-p03` attendu NC, obtenu C C C — Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune… *(Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct.)*
- `velo-06` attendu NC, obtenu ? ? ? — Mon vélo était attaché à un arceau dans la rue avec un antivol. L'antivol a été coupé et le vélo volé. *(Vol dans la rue, sans violence : hors du bâtiment, et ce n'est pas un « vol commis sur l'assuré … suite à violences ».)*
- `bougie-01` attendu NC, obtenu NC ? NC — J'ai laissé une bougie sur la table de mon jardin pendant mes vacances. Avec la chaleur, la bougie a fondu et … *(Pas d'embrasement : « l'excès de chaleur … sans qu'il y ait embrasement » n'est pas un incendie (12/incendie). Et le con)*
- `autre-02` attendu C, obtenu ? C C — Le tuyau du lave-linge a cédé et l'eau a abîmé le parquet et le canapé. *(Dégâts des eaux couverts (2.7) ; le tuyau à l'origine est exclu (2.7-b) mais sa réparation relève des garanties compléme)*
- `val-06` attendu C, obtenu C ? ? — J'ai déposé mon ordinateur chez un réparateur il y a deux semaines ; la boutique a été cambriolée et mon ordin… *(2.10 : le vol du contenu déposé chez un réparateur pendant max. 30 jours (limite 500 EUR).)*
- `val-08` attendu C, obtenu ? ? ? — Un court-circuit dans le grille-pain a mis le feu à la cuisine : les flammes ont détruit les placards et le ré… *(2.1 : l'incendie ; flammes et embrasement, c'est un incendie au sens de la définition.)*
- `val-11` attendu NC, obtenu NC ? NC — Pendant un orage, la pluie s'est infiltrée par la fenêtre mal jointée de ma chambre et a abîmé le mur et la mo… *(Exclusion 2.7 : une infiltration par les fenêtres, autre que celle due à une fuite des installations hydrauliques extéri)*
- `val-12` attendu C, obtenu ? C ? — Ma baignoire a débordé pendant que j'étais au téléphone ; l'eau a abîmé mon parquet. *(2.7 couvre l'ensemble des dégâts des eaux ; l'exclusion du récipient vise un récipient NON relié à l'installation hydrau)*
- `red-b02` attendu C, obtenu NC NC NC — J'ai fait tomber une casserole sur ma table de cuisson vitrocéramique, qui s'est fendue. *(2.9 : les tables de cuisson en vitrocéramique sont assimilées aux vitres.)*
- `g-l04` attendu C, obtenu C ? ? — La friteuse a pris feu ; les flammes sont montées jusqu'à la hotte et ont brûlé les placards de la cuisine. *(2.1 : incendie (flammes et embrasement).)*
- `g-l05` attendu C, obtenu ? ? ? — Fuite d'eau sous l'évier : le meuble de cuisine a gonflé et le parquet est abîmé. *(2.7 : l'ensemble des dommages causés par l'eau.)*
- `g-p04` attendu C, obtenu ? ? ? — Le chauffe-eau a fui ; le parquet est abîmé et le chauffe-eau lui-même est hors d'usage. *(2.7 : le parquet est couvert ; le chauffe-eau à l'origine du sinistre est exclu (exclusion partielle).)*
- `g-p05` attendu C, obtenu ? ? ? — L'aquarium du salon s'est brisé et l'eau a abîmé le parquet. *(2.7 : l'exclusion du récipient non relié excepte l'aquarium.)*
- `g-h04` attendu C, obtenu NC ? ? — Après des pluies exceptionnelles, la rivière a débordé et l'eau a envahi mon appartement au rez-de-chaussée. *(2.3 : l'inondation est couverte par les catastrophes naturelles, alors que 2.7 l'exclut. Non traduite.)*
