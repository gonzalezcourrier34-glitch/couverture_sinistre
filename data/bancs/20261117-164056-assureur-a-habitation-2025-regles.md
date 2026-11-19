# Banc d'essai — assureur-a-habitation-2025, méthode `regles`

2026-11-17T16:38:24 · golden set v2 (68 cas, empreinte `c4ba1d6cdf5a889f`) · cas validés par l'auteur : 0 sur 68


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 2 | ✗ |
| regles | faux_refus | ≤ 0 | 7 | ✗ |
| regles | exactitude | ≥ 0.95 | 0.853 | ✗ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 1.5 | ✓ |
| lecture | decisions_changees | ≤ 2 | 13.33 | ✗ |
| lecture | decisions_changees_vers_couvert | ≤ 0 | 5 | ✗ |
| lecture | cas_avec_contradiction | ≤ 5 | 16 | ✗ |
| chaine | faux_couverts | ≤ 0 | 4.667 | ✗ |
| chaine | faux_refus | ≤ 1 | 4 | ✗ |
| chaine | exactitude | ≥ 0.85 | 0.838 | ✗ |
| chaine | instables | ≤ 3 | 5 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 0.667 | ✗ |

## Depuis le banc précédent (2026-11-17T16:32:49)

- lecture · rappel_faits : 0.825 → 0.824
- chaine · exactitude : 0.853 → 0.838
- chaine · exactitude_stricte : 0.681 → 0.671
- chaine · faux_refus : 3.667 → 4

## Couche 1 — règles seules (faits idéaux, sans modèle)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 85% | 76% | **2** | **7** | 15% |

Rappel des questions attendues : 100% · questions posées par réponse « incertain » : 1.5

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 68 | 85% | 2 ⚠ | 7 |
| garantie : 2.1 | 11 | 91% | 0 | 1 |
| garantie : 2.10 | 28 | 93% | 1 ⚠ | 0 |
| garantie : 2.2 | 5 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 0% | 0 | 2 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 3 | 0% | 0 | 3 |
| garantie : 2.7 | 9 | 89% | 1 ⚠ | 0 |
| garantie : 2.8 | 1 | 0% | 0 | 1 |
| garantie : 2.9 | 6 | 100% | 0 | 0 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 100% | 0 | 0 |
| thème : hors_regles | 19 | 68% | 0 | 6 |
| thème : info_manquante | 6 | 100% | 0 | 0 |
| thème : langue | 7 | 100% | 0 | 0 |
| thème : multi | 6 | 100% | 0 | 0 |
| thème : piege | 41 | 85% | 2 ⚠ | 3 |
| thème : variante | 13 | 100% | 0 | 0 |

### Erreurs des règles

- **⚠ couvert à tort** `g-p03` attendu NC, obtenu C — Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune… *(Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct.)*
- **⚠ couvert à tort** `g-p06` attendu NC, obtenu C — J'ai renversé le seau d'eau du ménage et l'eau a abîmé le parquet. *(Exclusion 2.7 : le renversement d'un récipient non relié à l'installation hydraulique.)*
- `g-p07` attendu C, obtenu NC — Une casserole oubliée sur le feu a dégagé une épaisse fumée qui a noirci les murs et le plafond de la cuisine … *(2.1 couvre aussi « le dégagement de suie et de fumée », sans incendie.)*
- `g-p09` attendu NC, obtenu ? — Mon vélo a été volé dans mon casier du club de sport. *(Exclusion 2.10 : le vol du contenu entreposé dans un casier d'une association sportive (et hors du bâtiment).)*
- `g-h01` attendu C, obtenu NC — Un orage a provoqué une surtension : le réfrigérateur et la box internet ne fonctionnent plus. *(2.6 : action de l'électricité. Garantie non traduite : jamais un refus.)*
- `g-h02` attendu C, obtenu NC — Une panne de courant de dix heures a fait décongeler tout le contenu de mon congélateur. *(2.6 : denrées décongelées après 6 heures d'arrêt (limite 500 EUR). Non traduite.)*
- `g-h03` attendu C, obtenu NC — La cuve de fioul de l'immeuble a fui et le fioul a imprégné le sol de ma cave. *(2.8 : dégâts causés par le mazout. Non traduite.)*
- `g-h04` attendu C, obtenu NC — Après des pluies exceptionnelles, la rivière a débordé et l'eau a envahi mon appartement au rez-de-chaussée. *(2.3 : l'inondation est couverte par les catastrophes naturelles, alors que 2.7 l'exclut. Non traduite.)*
- `g-h05` attendu C, obtenu NC — Les égouts publics ont refoulé pendant un gros orage et l'eau sale a envahi la salle de bain. *(2.3 : le refoulement d'égouts publics est une catastrophe naturelle couverte ; 2.7 l'exclut. Non traduite.)*
- `g-h07` attendu C, obtenu NC — Mon chat s'est électrocuté en mordant un câble électrique. *(2.6 : l'électrocution des animaux domestiques. Non traduite.)*

## Couche 2 — lecture des faits par le modèle

**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : **13.33** par exécution, dont **5** cas vers un couvert à tort.

Rappel des faits idéaux : 82% (les faits négatifs non dits, comme « pas de violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : 16 cas · faits vagues : 2 cas · faits en trop : 52 cas

### La lecture change la décision

- **⚠ vers couvert** `red-b05` idéal NC, lu C C C · manque : vitre_placee = non · en trop : cause_dommage = autre; type_dommage = bris
- **⚠ vers couvert** `g-l01` idéal NC, lu C C ? · **contredit** : lieu : parties_communes lu annexe; lieu : parties_communes lu logement · manque : fermeture = aucune · en trop : auteur = tiers; effraction = non; portes_fermees = non; proprietaire = assure; vol_sur_personne = non
- **⚠ vers couvert** `g-q03` idéal ?, lu C C C · en trop : absence = oui; fenetres_fermees = oui; lieu = logement; portes_fermees = oui; vol_sur_personne = non
- **⚠ vers couvert** `g-h02` idéal NC, lu C C C · **contredit** : bien : objet_divers lu electronique; evenement : autre lu degat_eaux · en trop : cause_eau = gel
- **⚠ vers couvert** `g-h03` idéal NC, lu C C C · **contredit** : evenement : autre lu degat_eaux · en trop : cause_eau = fuite_installation
- `velo-03` idéal NC, lu ? ? ? · **contredit** : fermeture : cadenas lu cle · manque : vol_sur_personne = non · en trop : absence = oui; proprietaire = assure
- `velo-04` idéal NC, lu NC NC ? · **contredit** : fermeture : aucune lu cle · manque : vol_sur_personne = non · en trop : absence = oui; simple_disparition = oui
- `bougie-01` idéal NC, lu ? ? ? · **contredit** : bien : mobilier_jardin lu mobilier · manque : absence = oui; embrasement = non; evenement = autre; flammes = non · en trop : cause_dommage = autre; type_dommage = rayure_ou_ecaillement
- `autre-01` idéal C, lu ? ? ? · manque : violence = oui
- `val-09` idéal NC, lu NC ? NC · **contredit** : bien : objet_divers lu electronique; evenement : autre lu incendie · manque : embrasement = non; evenement = autre; flammes = non · en trop : chaleur_sans_feu = oui
- `val-11` idéal NC, lu ? NC NC · manque : bien = element_batiment · en trop : fenetres_fermees = non
- `red-t01` idéal C, lu ? ? ? · en trop : cause_eau = infiltration_exterieure; chaleur_sans_feu = non; embrasement = non; flammes = non; travaux_batiment = aucun; travaux_vitres = aucun
- `g-q02` idéal ?, lu NC NC NC · en trop : evenement = vol; simple_disparition = oui
- `g-p04` idéal C, lu C ? C · manque : lieu = logement
- `g-p09` idéal ?, lu NC NC NC · en trop : absence = oui; effraction = non; effraction = oui; fenetres_fermees = oui; fermeture = cle; portes_fermees = oui; proprietaire = hote; vol_sur_personne = non
- `g-h04` idéal NC, lu ? ? ? · manque : bien = element_batiment/mobilier

### Contradictions sans effet sur la décision

- `val-02` : auteur : personnel_prive lu famille
- `val-12` : cause_eau : fuite_installation lu debordement_recipient
- `red-t03` : lieu : garage lu annexe
- `g-l03` : bien : mobilier_jardin lu mobilier; evenement : autre lu degat_eaux; flammes : non lu oui; lieu : jardin lu terrasse
- `g-l07` : evenement : autre lu bris
- `g-p03` : bien : objet_divers lu velo
- `g-p05` : cause_eau : debordement_recipient lu fuite_installation
- `g-p06` : cause_eau : debordement_recipient lu fuite_installation
- `g-h07` : bien : animal lu electronique

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 84% (82% – 85%) | 67% (66% – 68%) | **4.667 (4 – 5)** | **4 (4 – 4)** | 20% (19% – 21%) |

Instables : **5** sur 68 · rappel des clauses : 60% · rappel des questions : 67% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 29.7 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 68 | 84% | 5 ⚠ | 4 |
| garantie : 2.1 | 11 | 82% | 0 | 1 |
| garantie : 2.10 | 28 | 89% | 3 ⚠ | 0 |
| garantie : 2.2 | 5 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 50% | 0 | 1 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 3 | 33% | 0 | 2 |
| garantie : 2.7 | 9 | 78% | 1 ⚠ | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 6 | 83% | 1 ⚠ | 0 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 50% | 0 | 0 |
| thème : hors_regles | 19 | 79% | 1 ⚠ | 3 |
| thème : info_manquante | 6 | 83% | 1 ⚠ | 0 |
| thème : langue | 7 | 86% | 1 ⚠ | 0 |
| thème : multi | 6 | 100% | 0 | 0 |
| thème : piege | 41 | 80% | 4 ⚠ | 2 |
| thème : variante | 13 | 100% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `red-b05` attendu NC, obtenu C C C — Le grand miroir que je venais d'acheter, encore dans son carton et pas encore accroché, s'est brisé quand je l… *(Exclusion 2.9 : les dommages aux vitres et biens assimilés non placés.)*
- **⚠ couvert à tort** `g-l01` attendu NC, obtenu C C ? — on m'a piqué mon vélo dans le local à vélos de la résidence, la porte était même pas fermée *(Langue familière. Exclusion 2.10 : le vol dans les parties communes du bâtiment.)*
- **⚠ couvert à tort** `g-q03` attendu ?, obtenu C C C — Mon vélo a été volé pendant que je faisais mes courses. *(Le lieu décide (dans le bâtiment ou dehors) : il faut le demander.)*
- **⚠ couvert à tort** `g-p03` attendu NC, obtenu C C C — Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune… *(Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct.)*
- **⚠ couvert à tort** `g-p06` attendu NC, obtenu C C C — J'ai renversé le seau d'eau du ménage et l'eau a abîmé le parquet. *(Exclusion 2.7 : le renversement d'un récipient non relié à l'installation hydraulique.)*
- `velo-04` attendu NC, obtenu NC NC ? — Mon vélo a été volé dans ma cave privative. J'avais oublié de la fermer à clé et il n'y a aucune trace d'effra… *(Cave non fermée : pas de serrure de sûreté (condition du plafond caves), et obligation de prévention non respectée avec )*
- `bougie-01` attendu NC, obtenu ? ? ? — J'ai laissé une bougie sur la table de mon jardin pendant mes vacances. Avec la chaleur, la bougie a fondu et … *(Pas d'embrasement : « l'excès de chaleur … sans qu'il y ait embrasement » n'est pas un incendie (12/incendie). Et le con)*
- `val-09` attendu NC, obtenu NC ? NC — Mon fer à repasser, laissé à plat sur la planche, a brûlé la housse et laissé une marque sur le tissu, sans fl… *(Définition de l'incendie : les brûlures et le contact d'une source de chaleur sans embrasement ne sont pas un incendie.)*
- `val-11` attendu NC, obtenu ? NC NC — Pendant un orage, la pluie s'est infiltrée par la fenêtre mal jointée de ma chambre et a abîmé le mur et la mo… *(Exclusion 2.7 : une infiltration par les fenêtres, autre que celle due à une fuite des installations hydrauliques extéri)*
- `g-p04` attendu C, obtenu C ? C — Le chauffe-eau a fui ; le parquet est abîmé et le chauffe-eau lui-même est hors d'usage. *(2.7 : le parquet est couvert ; le chauffe-eau à l'origine du sinistre est exclu (exclusion partielle).)*
- `g-p07` attendu C, obtenu NC NC NC — Une casserole oubliée sur le feu a dégagé une épaisse fumée qui a noirci les murs et le plafond de la cuisine … *(2.1 couvre aussi « le dégagement de suie et de fumée », sans incendie.)*
- `g-h01` attendu C, obtenu NC NC NC — Un orage a provoqué une surtension : le réfrigérateur et la box internet ne fonctionnent plus. *(2.6 : action de l'électricité. Garantie non traduite : jamais un refus.)*
- `g-h05` attendu C, obtenu NC NC NC — Les égouts publics ont refoulé pendant un gros orage et l'eau sale a envahi la salle de bain. *(2.3 : le refoulement d'égouts publics est une catastrophe naturelle couverte ; 2.7 l'exclut. Non traduite.)*
- `g-h07` attendu C, obtenu NC NC NC — Mon chat s'est électrocuté en mordant un câble électrique. *(2.6 : l'électrocution des animaux domestiques. Non traduite.)*
