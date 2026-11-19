# Banc d'essai — assureur-a-habitation-2025, méthode `regles`

2026-11-17T16:58:45 · golden set v4 (68 cas, empreinte `a6a056729cc7b00b`) · cas validés par l'auteur : 0 sur 68


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 0 | ✓ |
| regles | faux_refus | ≤ 0 | 0 | ✓ |
| regles | exactitude | ≥ 0.95 | 1 | ✓ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 0.9 | ✓ |
| lecture | decisions_changees | ≤ 2 | 15.67 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 6 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 13 | ✗ |
| chaine | faux_couverts | ≤ 0 | 3.667 | ✗ |
| chaine | faux_refus | ≤ 1 | 3.667 | ✗ |
| chaine | exactitude | ≥ 0.85 | 0.853 | ✓ |
| chaine | instables | ≤ 3 | 8 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 0.667 | ✗ |

## Depuis le banc précédent (2026-11-17T16:52:25)

- regles · exactitude : 0.956 → 1
- regles · exactitude_stricte : 0.765 → 0.809
- regles · faux_couverts : 2 → 0
- lecture · rappel_faits : 0.772 → 0.766
- chaine · exactitude : 0.863 → 0.853
- chaine · exactitude_stricte : 0.623 → 0.647
- chaine · faux_couverts : 6 → 3.667
- chaine · faux_refus : 0 → 3.667

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

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **15.67** par exécution, dont **6** cas vers un couvert à tort.

Rappel des faits idéaux : 77% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 13 cas · faits vagues : 0 cas · faits en trop : 19 cas

### La lecture change la décision

- **⚠ vers couvert** `bougie-04` idéal NC, lu NC NC C · **contredit** : lieu : jardin lu terrasse · manque : absence = oui
- **⚠ vers couvert** `val-01` idéal ?, lu C C C · manque : absence = oui; effraction = non; portes_fermees = oui; vol_sur_personne = non · en trop : fermeture = aucune; fermeture = cle
- **⚠ vers couvert** `val-03` idéal NC, lu C NC NC · manque : proprietaire = hote; vol_sur_personne = non · en trop : absence = oui; auteur = tiers; portes_fermees = non
- **⚠ vers couvert** `val-10` idéal NC, lu C C C · manque : absence = oui; prevention_gel = non
- **⚠ vers couvert** `val-13` idéal ?, lu C C C · manque : cause_eau = infiltration_exterieure
- **⚠ vers couvert** `g-q02` idéal ?, lu C C C · en trop : evenement = vol
- `velo-03` idéal NC, lu ? ? ? · **contredit** : fermeture : cadenas lu cle · manque : vol_sur_personne = non
- `velo-06` idéal NC, lu ? ? NC · **contredit** : fermeture : cadenas lu aucune; fermeture : cadenas lu cle · manque : fermeture = cadenas; violence = non; vol_sur_personne = non · en trop : effraction = oui
- `autre-01` idéal C, lu ? ? ? · manque : violence = oui
- `autre-02` idéal C, lu ? C C · manque : lieu = logement
- `val-06` idéal C, lu ? ? ? · manque : depot_moins_30j = oui; effraction = oui; vol_sur_personne = non
- `val-11` idéal NC, lu ? NC NC
- `red-b02` idéal C, lu NC NC NC · **contredit** : evenement : bris lu autre · manque : lieu = logement; type_dommage = felure
- `g-l05` idéal C, lu C ? C · manque : lieu = logement
- `g-l06` idéal C, lu ? ? C · manque : lieu = voie_publique; violence = oui; vol_sur_personne = oui · en trop : auteur = tiers
- `g-p04` idéal C, lu ? ? ? · manque : lieu = logement
- `g-p05` idéal C, lu NC NC NC · **contredit** : cause_eau : debordement_aquarium lu debordement_recipient
- `g-h04` idéal ?, lu ? NC NC · manque : bien = element_batiment/mobilier
- `g-h05` idéal ?, lu NC NC NC · manque : bien = element_batiment
- `g-h06` idéal C, lu ? ? ? · en trop : effraction = oui

### Contradictions sans effet sur la décision

- `val-09` : bien : objet_divers lu electronique
- `red-t03` : lieu : garage lu autre_batiment; lieu : garage lu logement
- `red-b03` : evenement : bris lu autre
- `red-b04` : evenement : bris lu autre
- `red-b05` : evenement : bris lu autre
- `g-l03` : bien : mobilier_jardin lu mobilier; lieu : jardin lu terrasse
- `g-p03` : bien : objet_divers lu velo
- `g-h02` : bien : objet_divers lu electronique

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 85% (84% – 87%) | 65% (62% – 68%) | **3.667 (3 – 4)** | **3.667 (3 – 4)** | 27% (24% – 31%) |

Instables : **8** sur 68 · rappel des clauses : 61% · rappel des questions : 67% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 37.7 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 68 | 84% | 4 ⚠ | 3 |
| garantie : 2.1 | 11 | 100% | 0 | 0 |
| garantie : 2.10 | 28 | 86% | 3 ⚠ | 0 |
| garantie : 2.2 | 5 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 50% | 0 | 1 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 3 | 100% | 0 | 0 |
| garantie : 2.7 | 9 | 44% | 1 ⚠ | 1 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 6 | 83% | 0 | 1 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 19 | 90% | 0 | 2 |
| thème : info_manquante | 6 | 83% | 1 ⚠ | 0 |
| thème : langue | 7 | 100% | 0 | 0 |
| thème : multi | 6 | 83% | 0 | 0 |
| thème : piege | 41 | 76% | 4 ⚠ | 3 |
| thème : variante | 13 | 92% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `bougie-04` attendu NC, obtenu NC NC C — Pendant mes vacances, une bougie laissée sur la table du jardin s'est enflammée et a brûlé la table et le salo… *(Vrai incendie, mais table et salon de jardin = contenu du jardin, exclu du contenu assuré (12/contenu). INCERTAIN défend)*
- **⚠ couvert à tort** `val-01` attendu NC, obtenu C C C — Pendant que j'étais au travail, quelqu'un est entré par la fenêtre de ma chambre, au rez-de-chaussée, que j'av… *(Obligation de prévention (2.10) : en cas d'absence, « fermer correctement les fenêtres […] facilement accessibles ». Lie)*
- **⚠ couvert à tort** `val-03` attendu NC, obtenu C NC NC — Des amis que j'hébergeais pour le week-end se sont fait voler leur ordinateur lors d'un cambriolage de mon app… *(Exclusion 2.10 : le vol des biens appartenant à des hôtes (alors que la définition du contenu les inclut : piège).)*
- **⚠ couvert à tort** `val-10` attendu NC, obtenu C C C — En janvier, je suis parti deux semaines en coupant le chauffage. Une canalisation a gelé puis éclaté ; l'eau a… *(2.7 : en période de gel, maintenir une température positive, vidanger ou isoler ; refus s'il y a un lien causal direct. )*
- **⚠ couvert à tort** `g-q02` attendu ?, obtenu C C C — Mon ordinateur portable a disparu de mon appartement. *(« Disparu » n'est pas « volé » : la simple disparition est exclue ; il faut établir le vol.)*
- `velo-06` attendu NC, obtenu ? ? NC — Mon vélo était attaché à un arceau dans la rue avec un antivol. L'antivol a été coupé et le vélo volé. *(Vol dans la rue, sans violence : hors du bâtiment, et ce n'est pas un « vol commis sur l'assuré … suite à violences ».)*
- `autre-02` attendu C, obtenu ? C C — Le tuyau du lave-linge a cédé et l'eau a abîmé le parquet et le canapé. *(Dégâts des eaux couverts (2.7) ; le tuyau à l'origine est exclu (2.7-b) mais sa réparation relève des garanties compléme)*
- `val-11` attendu NC, obtenu ? NC NC — Pendant un orage, la pluie s'est infiltrée par la fenêtre mal jointée de ma chambre et a abîmé le mur et la mo… *(Exclusion 2.7 : une infiltration par les fenêtres, autre que celle due à une fuite des installations hydrauliques extéri)*
- `red-b02` attendu C, obtenu NC NC NC — J'ai fait tomber une casserole sur ma table de cuisson vitrocéramique, qui s'est fendue. *(2.9 : les tables de cuisson en vitrocéramique sont assimilées aux vitres.)*
- `g-l05` attendu C, obtenu C ? C — Fuite d'eau sous l'évier : le meuble de cuisine a gonflé et le parquet est abîmé. *(2.7 : l'ensemble des dommages causés par l'eau.)*
- `g-l06` attendu C, obtenu ? ? C — Deux types m'ont bousculé à la sortie du bus et m'ont arraché mon sac avec mon portefeuille dedans. *(2.10 : vol commis sur l'assuré, en dehors des biens assurés, avec violences.)*
- `g-p04` attendu C, obtenu ? ? ? — Le chauffe-eau a fui ; le parquet est abîmé et le chauffe-eau lui-même est hors d'usage. *(2.7 : le parquet est couvert ; le chauffe-eau à l'origine du sinistre est exclu (exclusion partielle).)*
- `g-p05` attendu C, obtenu NC NC NC — L'aquarium du salon s'est brisé et l'eau a abîmé le parquet. *(2.7 : l'exclusion du récipient non relié excepte l'aquarium.)*
- `g-h04` attendu C, obtenu ? NC NC — Après des pluies exceptionnelles, la rivière a débordé et l'eau a envahi mon appartement au rez-de-chaussée. *(2.3 : l'inondation est couverte par les catastrophes naturelles, alors que 2.7 l'exclut. Non traduite.)*
- `g-h05` attendu C, obtenu NC NC NC — Les égouts publics ont refoulé pendant un gros orage et l'eau sale a envahi la salle de bain. *(2.3 : le refoulement d'égouts publics est une catastrophe naturelle couverte ; 2.7 l'exclut. Non traduite.)*
