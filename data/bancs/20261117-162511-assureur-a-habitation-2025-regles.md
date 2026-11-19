# Banc d'essai — assureur-a-habitation-2025, méthode `regles`

2026-11-17T16:22:58 · golden set v2 (68 cas, empreinte `c4ba1d6cdf5a889f`) · cas validés par l'auteur : 0 sur 68


## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| regles | faux_couverts | ≤ 0 | 2 | ✗ |
| regles | faux_refus | ≤ 0 | 7 | ✗ |
| regles | exactitude | ≥ 0.95 | 0.853 | ✗ |
| regles | rappel_questions | ≥ 0.9 | 1 | ✓ |
| regles | questions_par_incertain | ≤ 3 | 1.5 | ✓ |
| lecture | rappel_faits | ≥ 0.9 | 0.82 | ✗ |
| lecture | cas_avec_contradiction | ≤ 2 | 22 | ✗ |
| chaine | faux_couverts | ≤ 0 | 5 | ✗ |
| chaine | faux_refus | ≤ 1 | 4 | ✗ |
| chaine | exactitude | ≥ 0.85 | 0.829 | ✗ |
| chaine | instables | ≤ 3 | 8 | ✗ |
| chaine | rappel_questions | ≥ 0.8 | 0.667 | ✗ |

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

Rappel des faits idéaux : **82%** · cas avec une contradiction : **22** · cas avec des faits en trop : 51

- `velo-01` rappel 89% · manque : effraction = non
- `velo-02` rappel 83% · manque : vol_sur_personne = non
- `velo-03` rappel 72% · **contredit** : fermeture : cadenas lu cle · manque : vol_sur_personne = non
- `velo-04` rappel 89% · **contredit** : fermeture : aucune lu cle · manque : vol_sur_personne = non
- `velo-05` rappel 87% · manque : vol_sur_personne = non
- `velo-06` rappel 78% · **contredit** : fermeture : cadenas lu aucune · manque : violence = non
- `velo-07` rappel 83% · manque : vol_sur_personne = non
- `bougie-01` rappel 17% · **contredit** : bien : mobilier_jardin lu mobilier · manque : absence = oui; embrasement = non; evenement = autre; flammes = non
- `bougie-03` rappel 60% · manque : embrasement = non; flammes = non
- `bougie-04` rappel 83% · manque : absence = oui
- `bougie-05` rappel 71% · manque : absence = oui
- `autre-01` rappel 73% · **contredit** : bien : electronique lu appareil_audiovisuel · manque : violence = oui
- `autre-02` rappel 94%
- `val-01` rappel 88% · manque : absence = oui; effraction = non; portes_fermees = oui
- `val-02` rappel 89% · **contredit** : auteur : personnel_prive lu famille
- `val-03` rappel 83% · manque : vol_sur_personne = non
- `val-05` rappel 81% · manque : effraction = non; vol_sur_personne = non
- `val-06` rappel 61% · **contredit** : bien : electronique lu appareil_audiovisuel · manque : effraction = oui; vol_sur_personne = non
- `val-08` rappel 89%
- `val-09` rappel 27% · **contredit** : bien : objet_divers lu electronique; evenement : autre lu incendie · manque : embrasement = non; flammes = non
- `val-10` rappel 76% · manque : absence = oui
- `val-12` rappel 75% · **contredit** : cause_eau : fuite_installation lu debordement_recipient
- `val-14` rappel 80% · manque : vol_sur_personne = non
- `red-t03` rappel 67% · **contredit** : lieu : garage lu annexe
- `red-b02` rappel 83% · manque : lieu = logement
- `red-b03` rappel 67% · **contredit** : bien : appareil_audiovisuel lu electronique
- `red-b04` rappel 89% · **contredit** : bien : objet_verre_non_vitre lu objet_divers
- `red-b05` rappel 75% · manque : vitre_placee = non
- `g-l01` rappel 67% · **contredit** : lieu : parties_communes lu annexe; lieu : parties_communes lu logement · manque : fermeture = aucune
- `g-l02` rappel 83% · manque : absence = oui
- `g-l03` rappel 22% · **contredit** : bien : mobilier_jardin lu mobilier; flammes : non lu oui; lieu : jardin lu terrasse · manque : absence = oui; bien = mobilier_jardin; embrasement = non; flammes = non
- `g-l04` rappel 83%
- `g-l06` rappel 83%
- `g-l07` rappel 33% · **contredit** : evenement : autre lu bris · manque : auteur = famille
- `g-p03` rappel 67% · **contredit** : bien : objet_divers lu velo · manque : portes_fermees = oui
- `g-p04` rappel 93% · manque : lieu = logement
- `g-p05` rappel 75% · **contredit** : cause_eau : debordement_recipient lu fuite_installation
- `g-p06` rappel 75% · **contredit** : cause_eau : debordement_recipient lu fuite_installation
- `g-p07` rappel 93% · manque : bien = element_batiment
- `g-h02` rappel 33% · **contredit** : bien : objet_divers lu electronique; evenement : autre lu degat_eaux
- `g-h03` rappel 67% · **contredit** : evenement : autre lu degat_eaux
- `g-h04` rappel 47% · manque : bien = element_batiment/mobilier; lieu = logement
- `g-h05` rappel 75% · **contredit** : bien : element_batiment lu sanitaire
- `g-h07` rappel 78% · **contredit** : bien : animal lu electronique
- `g-m02` rappel 95%

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 83% (81% – 85%) | 66% (65% – 69%) | **5 (5 – 5)** | **4 (3 – 5)** | 21% (18% – 24%) |

Instables : **8** sur 68 · rappel des clauses : 61% · rappel des questions : 67% · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 40.5 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : claude | 68 | 82% | 5 ⚠ | 3 |
| garantie : 2.1 | 11 | 73% | 0 | 1 |
| garantie : 2.10 | 28 | 86% | 3 ⚠ | 0 |
| garantie : 2.2 | 5 | 100% | 0 | 0 |
| garantie : 2.3 | 2 | 50% | 0 | 1 |
| garantie : 2.4 | 1 | 100% | 0 | 0 |
| garantie : 2.6 | 3 | 67% | 0 | 1 |
| garantie : 2.7 | 9 | 78% | 1 ⚠ | 0 |
| garantie : 2.8 | 1 | 100% | 0 | 0 |
| garantie : 2.9 | 6 | 83% | 1 ⚠ | 0 |
| garantie : aucune | 2 | 100% | 0 | 0 |
| thème : base | 2 | 50% | 0 | 0 |
| thème : hors_regles | 19 | 84% | 1 ⚠ | 2 |
| thème : info_manquante | 6 | 83% | 1 ⚠ | 0 |
| thème : langue | 7 | 86% | 0 | 0 |
| thème : multi | 6 | 83% | 0 | 0 |
| thème : piege | 41 | 76% | 4 ⚠ | 2 |
| thème : variante | 13 | 100% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `val-01` attendu NC, obtenu C ? ? — Pendant que j'étais au travail, quelqu'un est entré par la fenêtre de ma chambre, au rez-de-chaussée, que j'av… *(Obligation de prévention (2.10) : en cas d'absence, « fermer correctement les fenêtres […] facilement accessibles ». Lie)*
- **⚠ couvert à tort** `red-b05` attendu NC, obtenu C C C — Le grand miroir que je venais d'acheter, encore dans son carton et pas encore accroché, s'est brisé quand je l… *(Exclusion 2.9 : les dommages aux vitres et biens assimilés non placés.)*
- **⚠ couvert à tort** `g-l01` attendu NC, obtenu ? C C — on m'a piqué mon vélo dans le local à vélos de la résidence, la porte était même pas fermée *(Langue familière. Exclusion 2.10 : le vol dans les parties communes du bâtiment.)*
- **⚠ couvert à tort** `g-q03` attendu ?, obtenu C C C — Mon vélo a été volé pendant que je faisais mes courses. *(Le lieu décide (dans le bâtiment ou dehors) : il faut le demander.)*
- **⚠ couvert à tort** `g-p03` attendu NC, obtenu C C C — Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune… *(Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct.)*
- **⚠ couvert à tort** `g-p06` attendu NC, obtenu C C C — J'ai renversé le seau d'eau du ménage et l'eau a abîmé le parquet. *(Exclusion 2.7 : le renversement d'un récipient non relié à l'installation hydraulique.)*
- `velo-04` attendu NC, obtenu ? NC NC — Mon vélo a été volé dans ma cave privative. J'avais oublié de la fermer à clé et il n'y a aucune trace d'effra… *(Cave non fermée : pas de serrure de sûreté (condition du plafond caves), et obligation de prévention non respectée avec )*
- `bougie-01` attendu NC, obtenu ? ? ? — J'ai laissé une bougie sur la table de mon jardin pendant mes vacances. Avec la chaleur, la bougie a fondu et … *(Pas d'embrasement : « l'excès de chaleur … sans qu'il y ait embrasement » n'est pas un incendie (12/incendie). Et le con)*
- `val-09` attendu NC, obtenu ? ? NC — Mon fer à repasser, laissé à plat sur la planche, a brûlé la housse et laissé une marque sur le tissu, sans fl… *(Définition de l'incendie : les brûlures et le contact d'une source de chaleur sans embrasement ne sont pas un incendie.)*
- `red-b01` attendu C, obtenu C NC C — Mon fils a cassé la vitre de la porte-fenêtre du salon avec un ballon. *(2.9 : le bris de vitres.)*
- `g-p04` attendu C, obtenu ? C C — Le chauffe-eau a fui ; le parquet est abîmé et le chauffe-eau lui-même est hors d'usage. *(2.7 : le parquet est couvert ; le chauffe-eau à l'origine du sinistre est exclu (exclusion partielle).)*
- `g-p07` attendu C, obtenu NC NC NC — Une casserole oubliée sur le feu a dégagé une épaisse fumée qui a noirci les murs et le plafond de la cuisine … *(2.1 couvre aussi « le dégagement de suie et de fumée », sans incendie.)*
- `g-p09` attendu NC, obtenu NC ? NC — Mon vélo a été volé dans mon casier du club de sport. *(Exclusion 2.10 : le vol du contenu entreposé dans un casier d'une association sportive (et hors du bâtiment).)*
- `g-h01` attendu C, obtenu ? NC NC — Un orage a provoqué une surtension : le réfrigérateur et la box internet ne fonctionnent plus. *(2.6 : action de l'électricité. Garantie non traduite : jamais un refus.)*
- `g-h05` attendu C, obtenu NC NC NC — Les égouts publics ont refoulé pendant un gros orage et l'eau sale a envahi la salle de bain. *(2.3 : le refoulement d'égouts publics est une catastrophe naturelle couverte ; 2.7 l'exclut. Non traduite.)*
- `g-h07` attendu C, obtenu NC NC NC — Mon chat s'est électrocuté en mordant un câble électrique. *(2.6 : l'électrocution des animaux domestiques. Non traduite.)*
