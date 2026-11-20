# Fiche métriques — comment on évalue le projet

Ce qu'on mesure, sur quels cas, avec quels seuils, et ce que valent les chiffres.
Commande unique : `uv run couverture banc --contrat assureur-a-habitation-2025` (rapports dans `data/bancs/`).
Démarche et historique des mesures : [DEMARCHE.md](DEMARCHE.md), parties 7.21 et suivantes.

---

## 1. Les jeux de cas

| Jeu | Où | Cas | Rôle | Limite |
|---|---|---|---|---|
| **Golden set** (référence) | `data/golden/` (v10, figé par empreinte, par contrat) | 97 (A) + 15 (B) | Rejoué à chaque changement ; toutes les métriques ci-dessous | Écrit par Claude, ayant servi à corriger le système : mesure la **mise au point** |
| Mise au point d'origine | `data/sinistres.jsonl` | 14 | Les 2 cas du recruteur et 12 variations | Inclus dans le golden set |
| Ancienne validation | `data/validation/` | 15 | Historique (7.17) | Inclus dans le golden set |
| Rédaction | `data/redaction/` | 10 | Tempête et bris, écrits avant les règles | Inclus dans le golden set |
| **Jeu fermé** (à créer) | `data/ferme/` | ≥ 20 | La **seule vraie mesure** : écrit par l'auteur ou un gestionnaire, sans voir les règles ; passé rarement ; on ne corrige jamais en le regardant | À écrire |

**Composition du golden set (v5)** : 58 nouveaux, 15 ex-validation, 12 mise au point, 10 rédaction, 2 recruteur.
Réponses attendues : 44 couvert, 40 non couvert, **13 incertain** (3 en v4).
Thèmes : piège (55), hors règles (24), information manquante (16), variante (13), langue (11), multiple (8).
Garanties : toutes celles du contrat, plus les exclusions générales (1.4).
Réponses attendues : 33 couverts, 32 non couverts, **3 incertains seulement** (déséquilibre à corriger :
les cas où « je ne sais pas » est la bonne réponse sont sous-représentés).

**Chaque cas porte** : la réponse attendue, les réponses tolérées (`acceptables`), les clauses et les
questions attendues, la garantie, des thèmes, l'origine, l'auteur, une note qui cite le contrat, et ses
**faits idéaux** (`regles/cas/golden/`) : ce qu'une lecture parfaite donnerait avec le vocabulaire.

---

## 2. Les trois couches

Le banc mesure séparément, pour savoir **où** naît une erreur :

1. **Règles** : les faits idéaux passent dans le moteur, sans modèle. Une erreur ici vient des règles ou du vocabulaire.
2. **Lecture** : les faits lus par le modèle passent dans les mêmes règles. On compare les deux décisions.
3. **Chaîne** : la méthode complète (le modèle lit, le moteur décide), 3 exécutions.

---

## 3. Les métriques, par ordre d'importance

### Décision (couches règles et chaîne)

| Métrique | Définition | Pourquoi | Seuil règles | Seuil chaîne |
|---|---|---|---|---|
| **Couverts à tort** | Réponse « couvert » quand l'attendu ne l'est pas et que l'annotation ne la tolère pas | Une promesse faite au client : l'erreur la plus coûteuse | 0 | 0 |
| **Refus à tort** | Réponse « non couvert » quand l'attendu est « couvert », non tolérée | Un client lésé | 0 | ≤ 1 |
| Justes ou acceptables | Réponse égale à l'attendu ou dans `acceptables` | Le score général | ≥ 95 % | ≥ 85 % |
| Exactes | Réponse égale à l'attendu, sans tolérance | Ce que la tolérance cache | — | — |
| Taux d'incertain | Part des réponses « incertain » | Le prix de la prudence : à 100 %, aucune erreur et aucune utilité | suivi | suivi |

### Lecture des faits

| Métrique | Définition | Seuil |
|---|---|---|
| **Décisions changées par la lecture** | Cas où les faits lus donnent une autre décision que les faits idéaux, par exécution | ≤ 2 |
| **… vers un couvert à tort** | Parmi elles, celles qui font couvrir à tort | 0 |
| Contradictions | Variable lue avec une valeur sans lien avec l'idéale (la hiérarchie du vocabulaire est prise en compte : « électronique » pour une télé est *vague*, pas faux) | ≤ 5 cas |
| Faits retirés | Faits hors sujet ou sans appui, retirés par le code | suivi |

Le rappel brut des faits idéaux est affiché mais pas jugé : il compte comme manquants des faits
négatifs que la déclaration ne dit pas (« pas de violence »), et la consigne interdit de les inventer.

### Justification

| Métrique | Définition | Seuil |
|---|---|---|
| **Citations introuvables** | Phrases des règles absentes du texte du contrat (`couverture regles`) | 0 |
| Rappel des clauses | Part des clauses attendues citées par la réponse | suivi |

### Questions (quand la réponse est « incertain »)

| Métrique | Définition | Seuil |
|---|---|---|
| Rappel des questions | Part des questions attendues effectivement posées | règles ≥ 90 %, chaîne ≥ 80 % |
| Questions par incertain | Nombre moyen de questions posées | ≤ 3 |
| **Incertains tranchables** | Part des incertains qu'une ou deux questions suffisent à trancher (raisonnement par hypothèses, Prolog) | suivi |
| Questions inutiles retirées | Questions dont aucune réponse ne change la décision, plus posées | suivi |

### Stabilité et coût

| Métrique | Définition | Seuil |
|---|---|---|
| **Cas instables** | Cas dont la réponse change d'une exécution à l'autre | ≤ 3 |
| **Temps par cas** | Médiane et 95e centile sur dix cas analysés **un à la fois** (ce que vit un gestionnaire), lecture et décision à part ; le temps en masse est affiché sans porte | 95e centile ≤ 10 s |
| Minimum et maximum | De chaque métrique sur les 3 exécutions | affichés |
| Durée | Par exécution des cas du golden set | suivi |
| Erreurs du fournisseur | Appels au modèle sans réponse | suivi |

### Passage à l'échelle (règles rédigées par le modèle, `couverture rediger`)

| Métrique | Définition |
|---|---|
| Contrôles passés sans retouche | Structure, vocabulaire, citations, couverture des exclusions, concepts, chargement, non-régression |
| Vocabulaire nouveau par garantie | Faits que le modèle déclare manquants (indicateur clé : doit baisser d'un contrat à l'autre) |
| Relecture humaine | Corrections nécessaires avant `--accepter` |
| Écarts au tableau des formules | Garanties qui jouent, dans les règles, pour une formule que le tableau du contrat ne leur donne pas (`couverture regles`, 7.92) |

---

## 4. Les portes

Les seuils sont dans `data/golden/seuils.json`. La commande `couverture banc` sort en erreur si une porte
échoue : branchable sur la CI. **Les seuils se resserrent ; ils ne se relâchent qu'en le notant dans
DEMARCHE**, avec la raison (le seul changement à ce jour, en 7.23, était un changement d'instrument).

---

## 5. Dernières mesures

**20 nov. 2026, 23 h 50 et 23 h 57, partie test du golden set, Assureur B (7 cas)** : sans exemples **81 %** justes,
71 % exactes ; avec exemples **81 %**, 76 % exactes ; 0 couvert à tort et 0 refus à tort dans les deux cas. Les exemples
deviennent la lecture par défaut (DEMARCHE 7.112).

**20 nov. 2026, 17 h 01 à 17 h 34, après la simplification (DEMARCHE 7.110, 7.111)** : jeu fermé sans exemples,
**A 88 %** (0 couvert à tort, 1 refus à tort), **B 90 %** (0, 0), **D 100 %** ; avec exemples, **A 95 %** (0, 1), B 82 %,
D 97 %. Partie test du golden set (A, 31 cas) : sans exemples 80 % justes, 3,3 couverts à tort, 8 instables ; **avec,
89 %, 2 couverts à tort, 2 instables**.

**20 nov. 2026, 16 h 19 à 16 h 25, après 7.106** : **Assureur A 85 % justes**, 75 % exactes, 0,67 couvert à tort
(`f-a02`, `f-a11`, une fois chacun), 0,67 refus à tort (`f-a18`), 4 instables ; **Assureur B 80 %**, 75 % exactes,
1,33 couvert à tort (`f-b15` et `f-b18`, couverts par une option en réserve), 5 instables ; **Assureur D 99 %**. Banque
d'exemples : 74 vecteurs ; seuil calibré à 0,85 (DEMARCHE 7.108).

**20 nov. 2026, 15 h 49 à 15 h 58, après les corrections des cent déclarations (DEMARCHE 7.105)** : **Assureur A
85 % justes**, 75 % exactes, 1,67 couvert à tort (`f-a11`, le vase lu verre de meuble ; `f-a17`, le déménagement non
traduit), 0,33 refus à tort, 2 instables ; **Assureur B 83 %**, 78 % exactes, 1 couvert à tort (`f-b18`), 0 refus à
tort ; **Assureur D 100 %**. Les trois couverts à tort sont corrigés en 7.106, sans nouvelle mesure encore. La porte
« rappel des questions » échouait à 0 % sur le jeu fermé : elle n'y était pas mesurable (7.106).

**20 nov. 2026, 14 h 40 à 14 h 43, après l'aide de la moisissure** : **Assureur A 85 % justes**, 77 % exactes,
1 couvert à tort, 0 refus à tort, 3 instables ; **Assureur B 82 %**, 77 % exactes, 1 couvert à tort (`f-b18`, la
voiture fermée à clé, en attente), 0 refus à tort, 2 instables. `f-b12` juste aux trois passages ; l'écart de B
(85 → 82 %) tient aux cas instables (`f-b03`, `f-b07`).

**20 nov. 2026, 14 h 30 à 14 h 36, après la relecture des erreurs de A et B (DEMARCHE 7.101)** : **Assureur A 85 %
justes**, 75 % exactes, 1 couvert à tort, 0,33 refus à tort, 2 instables ; **Assureur B 85 %**, 78 % exactes, 0,33
couvert à tort, 0 refus à tort, 5 instables ; **Assureur D 100 %**, 0 instable. Mesure de mise au point : les écarts
corrigés viennent de ce jeu.

**20 nov. 2026, 14 h 17, A après la relecture des contrats (typage de la section 5)** : **78 % justes**, 70 %
exactes, 2 couverts à tort, 0,33 refus à tort, 4 instables ; médiane 3,0 s. `f-a18` couvert 2 fois sur 3 (le vélo
encore lu véhicule à moteur une fois). DEMARCHE 7.100.

**20 nov. 2026, 14 h 10, A après la correction des aides** : **77 % justes**, 2 couverts à tort, 0 refus à tort,
2 instables. `f-a18` : le vélo lu `personne`, la règle couvre, la validation rétrograde en « incertain » (5.1 typée
« autre » par le découpage, DEMARCHE 7.100).

**20 nov. 2026, 14 h 02 à 14 h 05, A et B après leur responsabilité civile** (chaîne complète, jeu fermé) :
**Assureur A 78 % justes** (80 % avant), 2 couverts à tort, 1 refus à tort, 3 instables ; **Assureur B 63 %** (65 %),
1 couvert à tort, 0,67 refus à tort, 2 instables ; médiane 3,2 à 3,4 s. `f-b12`, `f-b16` et `f-a19` justes aux trois
passages ; `f-a18` (le piéton renversé à vélo) refusé aux trois : le vélo lu `vehicule_moteur` (DEMARCHE 7.99). Les
autres écarts avec le banc de 11 h 40 sont des cas instables hors responsabilité civile.

**20 nov. 2026, 12 h 33 à 12 h 38, les trois contrats après 7.97** : **Assureur D 100 % justes** (0 couvert à tort,
0 refus à tort, 0 instable) ; **A 80 %**, 1,67 couvert à tort ; **B 65 %**, 1 couvert à tort. Médiane 3,6 à 4,1 s ;
95e centile au-dessus de 20 s pour D et B (appels lents). Pour D, mesure optimiste : des écarts de ce jeu ont servi
à corriger les règles et la lecture (DEMARCHE 7.93 à 7.97) ; un second jeu fermé reste à écrire.

**20 nov. 2026, 12 h 23, assureur D, lot 3 accepté** (responsabilité civile, défense pénale, protection juridique) :
**92 % justes**, 0 couvert à tort, 0 refus à tort, 0 instable ; médiane 4,2 s, 95e centile 21,8 s (un appel lent).
Les deux écarts (`f-d09`, `f-d14`) : « accident » lu en trop, corrigé ensuite (DEMARCHE 7.97). Coût total de D :
3 lots, environ 50 min de rédaction, 417 contrôles bloquants, tout relu.

**20 nov. 2026, 11 h 36 à 11 h 42, jeu fermé, les trois contrats** (chaîne complète, Mistral Small, lecture
vérifiée) : **Assureur D 88 % justes**, 0 couvert à tort, 0 refus à tort, 0 instable (les 12 % restants : RC et
protection juridique, non traduites) ; **Assureur A 77 %**, 2 couverts à tort, 4 instables ; **Assureur B 63 %**,
1 couvert à tort, 2 instables. A et B : pas de régression due aux changements faits pour D (DEMARCHE 7.95).

**20 nov. 2026, 11 h 16, assureur D après 7.94** : **83 % justes**, 0 couvert à tort, 0,67 refus à tort (f-d04), 2 instables ; médiane 3,1 s. Les 3 cas de responsabilité civile et de protection juridique restent incertains (non traduits).

**20 nov. 2026, 10 h 57, assureur D après 7.93** : **71 % justes**, 0 couvert à tort, 0,33 refus à tort, 2 instables.

**20 nov. 2026, 10 h 51, troisième contrat (assureur D), jeu fermé** (25 cas, chaîne complète, Mistral Small,
lecture vérifiée) : **67 % justes**, 1 couvert à tort (f-d19, la foudre tombée sur un poteau), 0 refus à tort,
1 instable ; médiane 3,5 s. Première mesure d'un contrat traduit par le modèle puis relu, sans aucun cas de mise
au point. 3 des 8 erreurs sont la responsabilité civile et la protection juridique, pas encore traduites ; les
règles seules, sur des faits écrits à la main, donnent 23 sur 23 hors de ces garanties : le reste de l'écart est
dans la lecture (DEMARCHE 7.93). Coût de l'ajout : 2 lots, 25 min de rédaction, 179 contrôles bloquants, toutes
les garanties relues.

**19 nov. 2026, 17 h 58, jeu fermé après les corrections de 7.81** : **Assureur A 77 % justes** (70 %), 1,67 couvert
à tort (3), 0 refus à tort ; **Assureur B 62 % justes** (57 %), 1 couvert à tort (0), 1 refus à tort (1,33). Mesure
optimiste : cinq cas ont servi à corriger (DEMARCHE 7.82).

**19 nov. 2026, 17 h 45, jeu fermé** (40 cas écrits sans voir les règles, 7.79 ; chaîne complète, configuration
par défaut, sans Mistral Large) : **Assureur A 70 % justes**, 60 % exactes, 3 couverts à tort, 0,33 refus à tort,
5 instables ; **Assureur B 57 % justes**, 52 % exactes, 0 couvert à tort, 1,33 refus à tort ; médiane 4,1 à 4,2 s.
Première mesure de la fidélité des règles au contrat ; classement des erreurs : DEMARCHE 7.81.

**19 nov. 2026, 16 h 27 et 16 h 59, vérification v3 + confirmation et recours par Mistral Large** (golden v12) :
**Assureur B 100 % justes**, 82 % exactes, 0 couvert à tort, 0 refus à tort, médiane **22,6 s** (95e centile 38 s) ;
**Assureur A 89 % justes**, 75 % exactes, **1,33 couvert à tort**, 1,33 refus à tort, 15 instables, médiane 8,1 s
(95e centile 106 s, limites de débit de l'API). Meilleure justesse mesurée, au prix du temps. DEMARCHE 7.80.

**19 nov. 2026, 16 h 10, vérification v3** (souplesse limitée aux « non »), golden v12 : **Assureur A 90 % justes**,
76 % exactes, 4,33 couverts à tort, **0,67 refus à tort** (le plus bas mesuré), 11 instables ; un cas à la fois :
médiane 4,1 s, 95e centile 5,4 s. **Assureur B 76 % justes**, 49 % exactes, 0 couvert à tort, 0 refus à tort.
DEMARCHE 7.78.

**19 nov. 2026, 15 h 51, Assureur A, vérification v2 et aide de `cause_eau`** : chaîne 86 % justes, 74 % exactes,
4 couverts à tort, 2 refus à tort, 11 instables ; médiane 3,7 s, 95e centile 21 s (un appel lent). DEMARCHE 7.77.

**19 nov. 2026, 15 h 30, vérification v2 (les négations écrites) et exclusion du personnel corrigée**, golden
v12 : **Assureur B 78 % justes** (73 % avant), 51 % exactes, 0 couvert à tort, 0 refus à tort, 2 instables ;
**Assureur A 87 % justes**, 73 % exactes, **3,67 couverts à tort** (4 avant), **3 refus à tort** (1,67 avant),
14 instables ; un cas à la fois : médiane 4,1 à 4,7 s, 95e centile 5,5 à 6,2 s. DEMARCHE 7.76.

**19 nov. 2026, 14 h 50, Assureur B, golden v11, après le lot B** (extensions du lieu assuré, frais, pertes
indirectes) : règles seules 100 % justes, 87 % exactes ; **chaîne 73 % justes, 47 % exactes, 0 couvert à tort,
0 refus à tort**, 0 instable ; un cas à la fois : médiane 4,3 s, 95e centile 5,3 s. Mêmes décisions, cas par cas,
que le banc du 18 nov. sans confirmation : le lot B ne change rien au vol. Les quatre erreurs sont des
« incertain » là où le refus était attendu (faits négatifs non dits). La baisse affichée (82 % → 73 %) compare à un
banc avec confirmation par Mistral Large. DEMARCHE 7.74.

**19 nov. 2026, 14 h, Assureur A, golden v11, avec le pack multimédia (6.1)** : règles seules 100 % justes,
91 % exactes ; **chaîne 88 % justes, 75 % exactes, 4 couverts à tort**, 1,67 refus à tort, 12 instables ; un cas à
la fois : médiane 3,7 s, 95e centile 10,5 s. Toutes les erreurs restantes viennent de la lecture. DEMARCHE 7.71.

**19 nov. 2026, 13 h, Assureur A, golden v10, après le lot B et les corrections de lecture** (toutes les garanties
de dommages traduites, extensions et garanties accessoires) : règles seules 100 % justes, 91 % exactes ; **chaîne
88 % justes, 76 % exactes, 4,67 couverts à tort**, 0,67 refus à tort, 13 instables ; un cas à la fois : médiane
2,8 s (95e centile 68 s, un appel lent à l'API). DEMARCHE 7.70.

**19 nov. 2026, 10 h 30, confirmation des faits décisifs par Mistral Large (option)** : Assureur A 86 % justes,
**1,67 couvert à tort** (4 avec Small), médiane 8,6 s ; Assureur B 82 % justes, 0 couvert à tort. L'option reste
désactivée par défaut (DEMARCHE 7.67).

**19 nov. 2026, matin, lot A des deux contrats** (7 garanties pour A, 8 pour B, rédigées par Mistral Large en
une vingtaine de minutes, relues) : règles seules 100 % sur les deux contrats ; Assureur A 89 % justes et 4 à 5
couverts à tort selon les passages ; Assureur B 76 % justes, 0 couvert à tort (DEMARCHE 7.63 à 7.66).

**18 nov. 2026, 22 h 37, Assureur B Habitation, garantie vol (15 cas, golden v7), règles rédigées par
Mistral Large puis relues** : règles seules 100 % ; **chaîne 76 % justes, 0 couvert à tort, 0 refus à tort**,
1 instable ; rappel des faits 82 % ; un cas à la fois : médiane 3,3 s, 95e centile 4,7 s. Progression depuis le
premier banc (62 %) et détail : DEMARCHE 7.59 à 7.61. Cas écrits par Claude après relecture des règles : à
confirmer par un jeu indépendant.

**18 nov. 2026, 22 h 31, Assureur A, après les corrections générales de la soirée** (lecture limitée aux variables
du contrat, aides de lecture, moteur « exclusion entamée ») : **90 % justes, 1,33 couvert à tort** (meilleur
mesuré), 1 refus à tort, 12 instables ; 95e centile 4,1 s. DEMARCHE 7.57 à 7.61.

**18 nov. 2026, 17 h 10, lecture vérifiée + confirmation des faits décisifs (défaut)** : **90 % justes,
2,3 couverts à tort, 1,3 refus à tort**, questions attendues posées 70 % ; un cas à la fois : médiane 2,9 s,
95e centile 4,7 s (porte ≤ 10 s : passe). DEMARCHE 7.49, 7.50.

**18 nov. 2026, 16 h 30, moteur chargé une fois** : mêmes résultats (87 %, 2,7 couverts à tort, 5 instables) ;
temps par cas : médiane **2,4 s** (décision < 10 ms), 95e centile 68 s à cause des limites de débit de l'API
quand quatre cas tournent à la fois (DEMARCHE 7.47).

**18 nov. 2026, soir, golden v6, lecture Mistral Small vérifiée et arbitrée (défaut)** : **87 % justes,
2,7 couverts à tort, 2 refus à tort**, questions attendues posées 55 %, 2 à 3 minutes par passage
(DEMARCHE 7.38 à 7.45 : un temps 75 % et 9,3 couverts à tort le matin).

**18 nov. 2026, golden v6, lecture Mistral Large (3 exécutions)** : règles 100 % ; **chaîne 91 % justes,
0 couvert à tort, 0,3 refus à tort**, 9 instables ; 15 minutes par passage (Small : 20 secondes).

**18 nov. 2026, LegalBench, Mistral Small, 133 cas** : 55 % justes, exactitude équilibrée 64 %, 32 couverts à
tort, **ambigus reconnus 10 %** (précision des « incertain » 100 %) ; contrôle des citations sans effet
(toutes exactes). Détail : DEMARCHE 7.37.

**18 nov. 2026, golden v6, chaîne complète, lecture Mistral Small (SWI-Prolog, 3 exécutions)** :
règles seules 100 % ; **chaîne 75 % justes, 9,3 couverts à tort**, 14 cas instables. Sur les 68 cas
d'hier seulement : 76 % (85 % hier), la lecture s'est dégradée avec le vocabulaire plus long (DEMARCHE 7.32).
**Rappel, 17 nov., golden v4, lecture Mistral Large : 96 % sur ces 68 cas, aucun couvert à tort.**

**18 nov. 2026, golden v6, règles corrigées (oracle Python, à confirmer sur SWI-Prolog)** :
**100 % justes ou acceptables, 80 % exactes, 0 couvert et 0 refus à tort**, toutes les questions
attendues posées, 16 questions inutiles retirées (DEMARCHE 7.31).

**18 nov. 2026, golden v5 (97 cas), règles seules (oracle Python, à confirmer sur SWI-Prolog)** :
90 % justes ou acceptables, 70 % exactes, **4 couverts à tort, 3 refus à tort**. Les 29 cas ajoutés
ont fait ce qu'on attendait d'eux : trouver ce que les règles ne savent pas encore (détail : DEMARCHE 7.30).

**17 nov. 2026, golden v4 (68 cas), lecture par Mistral Small** :

| Couche | Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Instables |
|---|---|---|---|---|---|
| Règles seules (SWI-Prolog) | **100 %** | 81 % | **0** | **0** | — |
| Chaîne complète | 85 % | 65 % | 3,7 | 3,7 | 8 sur 68 |

Lecture : 15,7 décisions changées par exécution, dont 6 vers un couvert à tort. **Toutes les erreurs
restantes viennent de la lecture des faits.** Raisonnement par hypothèses (oracle, avant mesure sur le
poste) : 2 incertains sur 16 tranchables par une ou deux questions, 8 questions inutiles retirées.

---

## 6. Ce que valent les chiffres

- **Taille** : un cas pèse 1,5 point. Sur 68 cas, 85 % a une marge d'environ ± 8 points ; sur 97, d'environ ± 7. Les écarts de
  2 ou 3 points se lisent **cas par cas** (le rapport du banc les liste), pas en pourcentage.
- **Variance** : la lecture varie d'une exécution à l'autre même à température 0 ; on présente la
  moyenne avec le minimum et le maximum de 3 exécutions.
- **Tolérance** : « acceptable » couvre les cas ambigus ; l'exactitude stricte est toujours affichée à côté.
- **Biais** : le golden set est écrit par Claude et a servi à corriger le système. Le jeu fermé est la
  seule mesure de généralisation.
- **Comparabilité** : chaque rapport note la version du golden set, son empreinte et le modèle de lecture.

---

## 7. Sources externes possibles

Aucun jeu public ne donne la réponse selon les conditions générales d'Assureur A : la réponse dépend du contrat.
Sources utiles :

- **LegalBench, `insurance_policy_interpretation`** : 138 couples (déclaration, police), réponse
  couvert / non couvert / ambigu, licence CC BY 4.0, en anglais. Chaque cas a sa propre police : test de
  **généralisation** de la méthode (rédaction des règles comprise).
  https://hazyresearch.stanford.edu/legalbench/tasks/insurance_policy_interpretation.html
- **Décisions de médiateurs** (vrais sinistres habitation avec leur issue, en anglais) : FSPO irlandais
  (base filtrable par produit, motif et issue, https://fspo.ie/complaint-outcomes/decisions/) et Financial
  Ombudsman britannique (https://www.financial-ombudsman.org.uk). Réserve : ils jugent l'équité, pas
  seulement la lettre du contrat.
- **En français** : les cas présentés dans les rapports annuels de la Médiation de l'Assurance
  (https://www.mediation-assurance.org) ; la jurisprudence ouverte Judilibre (Cour de cassation, cours
  d'appel, tribunaux ; API gratuite, https://www.data.gouv.fr/fr/datasets/api-judilibre/).

Usage prévu : s'inspirer de situations réelles pour le **jeu fermé** (réécrites en déclarations et
annotées selon les CG d'Assureur A par l'auteur), et LegalBench comme **second banc** de généralisation.

### Le second banc : LegalBench (`couverture legalbench`)

Chaque cas a sa propre clause, en anglais, sans règles ni vocabulaire écrits pour elle. Le banc mesure
donc le **principe** du projet sans les règles : le modèle répond et **cite mot pour mot** la phrase de
la clause qui fonde sa réponse ; le code vérifie la citation ; une réponse ferme sans citation retrouvée
devient « incertain ». Deux colonnes : la réponse du modèle, et la réponse contrôlée.

| Métrique | Définition | Pourquoi |
|---|---|---|
| Exactitude | Réponse = réponse des lecteurs (3 classes) | Lisible |
| **Exactitude équilibrée** | Moyenne des rappels par classe (métrique de LegalBench) | Un modèle qui répond toujours « couvert » ne passe pas pour bon |
| **Rappel « ambigu »** | Part des cas ambigus reconnus comme tels | Le « je ne sais pas » sur des données que nous n'avons pas écrites |
| Précision « incertain » | Parmi les « incertain » répondus, part de vrais ambigus | Ne pas tout déclarer incertain pour bien paraître |
| Couverts / refus à tort | Comme le banc | Le coût métier |
| Citations introuvables | Réponses fermes dont la phrase citée n'est pas dans la clause | Ce que le contrôle attrape |

Données : `couverture legalbench --telecharger` (Hugging Face, sur le poste) dans `data/externes/legalbench/`,
avec leur attribution (CC BY 4.0). Rapports : `data/bancs/<date>-legalbench-<modèle>.md`.

---

## 8. À faire

0. Assureur B : un jeu de cas écrit par l'auteur sans voir les règles ; les faits idéaux sans valeurs par défaut.

1. Créer le jeu fermé (`data/ferme/`, ≥ 20 cas, auteur), avec plus de cas dont la bonne réponse est « incertain ».
2. Valider le golden set (`couverture banc --fiche`, puis `--figer "validation"`).
3. Mesurer la lecture par Mistral Large, puis la double lecture si elle aide.
4. Passer LegalBench (`couverture legalbench`), avec Mistral Small puis Large.
5. Suite possible : faire rédiger des règles pour chaque clause de LegalBench, pour tester aussi le moteur.
