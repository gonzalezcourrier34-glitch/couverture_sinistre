# Fiche métriques — comment on évalue le projet

Ce qu'on mesure, sur quels cas, avec quels seuils, et ce que valent les chiffres.
Deux méthodes, deux commandes : `uv run couverture banc --contrat …` pour la chaîne de règles (trois passages, rapports
dans `data/bancs/`), `uv run couverture juger --contrat … --jeu … --regles` pour la lecture des clauses (une passe,
bilan dans `data/debug/`). Le raisonnement qui a conduit à cette méthode d'évaluation est raconté dans
[COMPRENDRE, section 3](COMPRENDRE.md). Démarche et historique des mesures : [DEMARCHE.md](DEMARCHE.md), parties 7.21 et
suivantes. Mis à jour le 27 nov. 2026 après la mesure du jeu « six » ; les chiffres qui comptent sont en tête de la section 5.

---

## 1. Les jeux de cas

| Jeu | Où | Cas | Rôle | Limite |
|---|---|---|---|---|
| **Golden set** (référence) | `data/golden/` (v13, figé par empreinte, par contrat) | 97 (A) + 15 (B) | Rejoué à chaque changement ; toutes les métriques ci-dessous | Écrit par Claude en connaissant les règles, et il a servi à corriger le système : il mesure la **mise au point** |
| … dont la **partie test** | `data/lecture/partage.json` | 38 sur 112 (31 pour A, 7 pour B) | Mise de côté le 20 nov. (7.107) : ne sert jamais à corriger le vocabulaire, les règles ou les exemples | Tirée du même jeu : même auteur, même biais |
| **Jeu fermé** | `data/ferme/` | 20 (A) + 20 (B) + 25 (D) | La mesure de la **fidélité au contrat** : écrit à partir du seul texte des conditions générales, sans voir les règles (7.79) ; on ne corrige jamais en le regardant | Écrit par deux annotateurs automatiques et arbitré sur citations, pas par une personne du métier. C n'en a pas |
| **Jeux écrits à l'aveugle** | `data/aveugle/`, `data/neuf/`, `data/quatre/`, `data/cinq/`, `data/six/` | 60 chacun (20 par contrat : A, B, D) | Écrits de la même façon que le jeu fermé, chacun après un tour de corrections ; un second avis indépendant, un arbitrage sur le texte ; **mesurés une seule fois, code figé**, puis « vus » (7.185 à 7.187, 7.207, 7.215). « Quatre » et « cinq » comparent les deux méthodes | Mêmes limites que le jeu fermé. Pour « cinq », le second avis n'est plus Mistral Large, qui lit dans la méthode mesurée |
| Mise au point d'origine | `data/sinistres.jsonl` | 14 | Les 2 cas du recruteur et 12 variations | Inclus dans le golden set |
| Ancienne validation | `data/validation/` | 15 | Historique (7.17) | Inclus dans le golden set |
| Rédaction | `data/redaction/` | 10 | Tempête et bris, écrits avant les règles | Inclus dans le golden set |

**Composition du golden set (v13).** Assureur A, 97 cas : 44 couverts, 39 non couverts, 14 incertains. Assureur B, 15 cas : 5, 8 et 2.
Les cas où « je ne sais pas » est la bonne réponse restent sous-représentés dans le golden set ; le jeu fermé en a environ un tiers.

**Chaque cas porte** : la réponse attendue, les réponses tolérées (`acceptables`), les clauses et les
questions attendues, la garantie, des thèmes, l'origine, l'auteur, une note qui cite le contrat, et ses
**faits idéaux** (`regles/cas/golden/`) : ce qu'une lecture parfaite donnerait avec le vocabulaire.

---

## 2. Les trois couches

Le banc mesure séparément, pour savoir **où** naît une erreur :

1. **Règles** : les faits idéaux passent dans le moteur, sans modèle. Une erreur ici vient des règles ou du vocabulaire.
2. **Lecture** : les faits lus par le modèle passent dans les mêmes règles. On compare les deux décisions.
3. **Chaîne** : la méthode complète (le modèle lit, le moteur décide), 3 exécutions.

Le jeu fermé n'a pas de faits idéaux : seule la chaîne complète y est mesurée.

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

### Lecture des clauses (`couverture juger`)

Une passe par jeu (8 à 10 centimes par cas) ; le bilan est gardé dans `data/debug/`. Pas de portes : la comparaison se
fait jeu par jeu avec la chaîne de règles, passée sur les mêmes cas.

| Métrique | Définition |
|---|---|
| **Justes ou admises** | Réponse égale à l'attendu ou dans `acceptables` |
| **Couverts à tort**, **refus à tort** | Comme pour la chaîne de règles |
| « À préciser » ou erreur à la place d'une réponse | Une question, ou une panne du fournisseur, là où le texte suffisait |
| Désaccords avec les règles | La lecture conclut autrement que la chaîne de règles ; l'écran l'affiche |
| Clauses attendues sans jugement | Une clause à relire que le modèle n'a pas jugée, même après relance : pas de réponse franche |
| Jugements écartés | Une citation introuvable dans la clause ou dans la déclaration |
| Tokens envoyés, repris du cache, reçus ; durée par cas | Le coût et l'attente |

`juger --rejouer` rejoue les réponses gardées d'une passe précédente : il sert à vérifier une règle de décision sur un
jeu vu, presque sans frais, jamais à mesurer.

**La stabilité** (7.220), comme les trois passages du banc : `juger --passage 2`, `--passage 3` repassent un jeu en
gardant chaque passe à part ; `juger --stabilite --jeu … --contrat tous` compte, sur les cas communs aux passes, ceux
dont la décision change, ceux dont la décision tient sur d'autres clauses, et la justesse de chaque passe. Mesurée
le 26 novembre au soir : 7 cas instables sur 30, aucun entre « couvert » et « non couvert » (section 5).

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

Les plus récentes d'abord. Les deux premières sont les mesures qui comptent : les deux méthodes, sur des jeux jamais vus,
code figé, une seule fois. Dessous, l'historique complet de la chaîne de règles depuis le 17 novembre : il n'est pas à
lire d'un trait, il sert à retrouver ce qu'une modification a déplacé.

**27 nov. 2026, soir, jeu « six » : la consigne de jugement v2 contre la v1** (60 cas jamais vus, code figé et
commité avant, DEMARCHE 7.226 et 7.227). La v2 (deux règles de lecture : cause seulement probable, condition de la
garantie non dite) sur les 60 cas ; la v1 (`--consigne-jugement v1`) sur les 29 cas que la v2 laisse « à préciser »,
les seuls où ces règles peuvent changer la réponse.

| Contrat | Justes (v2) | Couverts à tort | Refus à tort | « À préciser » au lieu d'une réponse |
|---|---|---|---|---|
| A | 18 sur 20 | 0 | 1 | 1 |
| B | 14 sur 20 | 1 | 1 | 4 |
| D | 14 sur 20 | 0 | 0 | 6 |
| **Ensemble** | **46 sur 60** (77 %) | **1** | **2** | **11** |

Sur les 29 cas repassés en v1 : 23 réponses identiques ; la v1 fait trois couverts à tort que la v2 évite (`s-d03`,
`s-d08`, `s-d09`) et deux réponses justes que la v2 laisse « à préciser » (`s-d01`, `s-b06`) ; deux écarts sans
lien avec les règles (`s-b01`, `s-d11`). Estimation sur les 60 cas : v1 environ 48 justes et 4 couverts à tort, v2 46
et 1. La v2 reste. Tokens : 2,95 millions envoyés, 1,35 million reçus, environ 9 $.

**27 nov. 2026, après-midi, renfort des chapitres par les règles, jeu « cinq »** (DEMARCHE 7.224 et 7.225) : passes 4,
5 et 6 sur les vingt cas par contrat. Sur les dix cas des passes 1 à 3 : 24 / 24 / 26 justes sur 30 (82 %, comme
avant), 8 cas instables sur 30 (7 avant), aucun couvert à tort sur 180 analyses. Pas de gain ; 5 des 14 cas instables
sur 60 venaient d'une erreur 520 du fournisseur, relancée depuis. Environ 15 $ (`--echantillon 10` oublié).

**26 nov. 2026, soir, stabilité de la lecture des clauses sur le jeu « cinq »** (DEMARCHE 7.221) : passes 2 et 3 sur
dix cas par contrat (`--echantillon 10`), comparées à la passe 1 sur les mêmes trente cas.

| Contrat | Justes, passes 1 / 2 / 3 | Couverts à tort | Refus à tort | Cas instables | Même décision, autres clauses |
|---|---|---|---|---|---|
| A | 10 / 10 / 7 | 0 / 0 / 0 | 0 / 0 / 0 | 3 sur 10 | 1 sur 7 |
| B | 9 / 8 / 9 | 0 / 0 / 0 | 1 / 0 / 0 | 3 sur 10 | 0 sur 7 |
| D | 7 / 7 / 7 | 0 / 0 / 0 | 0 / 0 / 0 | 1 sur 10 | 3 sur 9 |
| **Ensemble** | **26 / 25 / 23 sur 30** (82 % en moyenne) | **0** | **1 sur 90** | **7 sur 30** | 4 sur 23 |

Les sept cas instables passent tous entre une réponse franche et « à préciser » ; aucun entre « couvert » et « non
couvert ». Causes lues dans les sorties : la contresignature (la lecture conclut « couvert », les règles ne suivent
pas), une citation jugée inexacte qui laisse une clause attendue sans jugement, une absence de couverture face à des
règles qui hésitent ; et en amont, des chapitres désignés très différents d'une passe à l'autre (de 92 à 290 clauses
au dossier pour un même cas). Tokens des passes 2 et 3 : 1,70 million envoyés, 0,84 million reçus, environ 5,8 $
(moins de 10 centimes par cas). Seuil de la chaîne de règles (≤ 3 instables) : non tenu.

**26 nov. 2026, 13 h 33 à 14 h 25, jeu « cinq »** (60 cas jamais vus, code figé au commit `de9ed60`, DEMARCHE 7.215) :

| | Chaîne de règles (3 passages) | Lecture des clauses (1 passe) |
|---|---|---|
| Justes, A / B / D | 15,7 / 14,3 / 10,3 sur 20 | 20 / 19 / 14 sur 20 |
| **Justes** | **40,3 sur 60** | **53 sur 60** |
| **Couverts à tort** | **4,7** | **0** |
| Refus à tort | 6 | 1 (`c-b08`) |
| « À préciser » au lieu d'une réponse | 9 | 6 (tous chez D, par la contresignature) |
| Durée d'une analyse | 3,5 à 5,2 s (médiane) | 177 s (médiane ; 71 à 366 s) |
| Tokens (lecture des clauses) | — | 1,87 million envoyés, 0,88 million reçus |

Portes de la chaîne de règles : échouent sur les trois contrats (couverts à tort, exactitude).

**25 nov. 2026, soir, jeu « quatre »** (60 cas jamais vus, code figé, DEMARCHE 7.207) : chaîne de règles 42 sur 60,
4,3 couverts à tort, 2 refus à tort, 8,7 « à préciser » de trop ; lecture des clauses 45 sur 60, 1 couvert à tort,
4 refus à tort, 10 « à préciser » de trop.

**25 nov. 2026, jeux « aveugle » et « neuf », chaîne de règles seule** (DEMARCHE 7.185 à 7.187) : « aveugle » A 95 %,
B 58 %, D 78 % ; « neuf » 38 sur 60 et 7 couverts à tort.

**24 nov. 2026, 10 h 40 à 10 h 47, état livré** (Mistral Medium lit, Mistral Small vérifie ; après quatre retouches de la phrase de réponse, qui ne changent aucune décision, 7.164 à 7.167) : partie test de A **94 %** (0 couvert à tort), jeu fermé de A **100 %** (0), de B **85 %** (1 couvert à tort, `f-b18`), de D **96 %** (0 ; 1 refus à tort). 4 à 4,8 s par cas en médiane, 7 s au plus au 95e centile. 231 tests passés.

**24 nov. 2026, 10 h 18 à 10 h 28, un essai retiré** (une définition pour chaque valeur de « auteur », 7.166) : jeu fermé de A **95 %**, `f-a02` couvert à tort **3 fois sur 3**, deux bancs de suite ; sans la définition, dans la minute, **0 sur 3**. Les trois autres bancs ne bougeaient pas. Retirée.

**24 nov. 2026, 9 h 17 à 9 h 54** (avant et après la première retouche) : partie test de A 94 %, jeu fermé de A 98 % puis 100 % (`f-a02` couvert à tort une fois sur trois, puis zéro), B 85 %, D 96 %.


**22 nov. 2026, 17 h 25 à 17 h 31** (28 exemples validés de plus dans la banque, 7.144) : partie test de A **90 %** (1 couvert à tort : `val-09`, aux trois passages), jeu fermé de A **100 %**, de B **85 %** (1 couvert à tort, `f-b18`), de D **96 %** (1 refus à tort, `f-d08`). Instables : 0 sur 96. Effet des exemples non mesurable (267 lectures justes sur 288, contre 265).

**22 nov. 2026, 16 h 20 à 16 h 26** (même configuration ; après 7.138 et 7.143, consignes et vocabulaire de lecture inchangés) : partie test de A **90 %** (0,3 couvert à tort : `val-09`, un passage sur trois), jeu fermé de A **100 %**, de B **85 %** (1 couvert à tort, `f-b18`), de D **93 %** (1 refus à tort, `f-d08`). Instables : 4 sur 96. Les écarts avec la série de 13 h 30 viennent tous de la lecture (DEMARCHE 7.143).

**22 nov. 2026, 13 h 30 à 13 h 36** (Mistral Medium lit, Mistral Small vérifie ; configuration retenue) : jeu fermé
de A **98 %** (0,3 couvert à tort), partie test de A **90 %** (0), B **82 %** (1), D **96 %** (0 ; 1 refus à tort).
4 à 4,8 s par cas en médiane, 7 s au plus au 95e centile. Référence actuelle (DEMARCHE 7.136).

**22 nov. 2026, 13 h 15 à 13 h 21** (toute l'analyse par Mistral Medium) : jeu fermé de A **92 %** (0 couvert à tort),
partie test de A **90 %** (0), B **80 %** (1), D **92 %** (0 ; 1 refus à tort). Lecture stable (63 déclarations sur 96
lues à l'identique trois fois). La confirmation refuse 17 fois sur 288 un lieu ou un bien que la déclaration implique
(DEMARCHE 7.136) : à remesurer avec Small pour vérifier.

**21 nov. 2026, 16 h 20 à 16 h 30** (graine fixe ; questions et réserves revues, 7.123 à 7.128) : jeu fermé de A
**87 %** (1 couvert à tort), partie test de A **85 %** (2), B **85 %** (0), D **100 %** (0). Par réponse, un « non
couvert » n'est jamais faux. Faits lus identiques aux trois passages : 35 déclarations sur 96 (30 sans graine).
Référence actuelle.

**21 nov. 2026, 15 h 18 à 15 h 26** (`lecture-details` v4, sans la phrase sur les flammes : **retirée**, retour à la
v3) : partie test de A 85 %, jeu fermé de A 90 %, B 90 %, D **95 %** (`f-d01`, la poêle en feu lue « chaleur sans
feu »). La référence reste celle de 14 h 41.

**21 nov. 2026, 14 h 41 à 14 h 49** (`lecture-details` v3 : la phrase sur le vol sur la personne retirée, 7.120) :
partie test de A **86 %**, jeu fermé de A **88 %**, B **88 %**, D **100 %**. Lecture de `vol_sur_personne` inchangée.

**21 nov. 2026, 14 h 26 à 14 h 32** (vocabulaire rangé en commun + un fichier par contrat, 7.119) : partie test de A
**85 %** (2 couverts à tort), jeu fermé de B **88 %** (0, 0), jeu fermé de D **100 %**. Référence actuelle.

**21 nov. 2026, 13 h 42 à 14 h 14** (temps 1 par Mistral Large, essai **non retenu**) : 17 à 31 s par cas, et 13 à 30 %
des analyses sans réponse dans le délai ; les taux (83 %, 65 %, 65 %, 64 %) ne mesurent donc pas la lecture
(DEMARCHE 7.118). L'état de référence reste celui de 12 h 51.

**21 nov. 2026, 13 h 18 à 13 h 26** (biens et événements vérifiés un par un, essai **retiré**) : partie test de A 82 %,
jeu fermé de A 93 %, B 88 %, D 96 %. Le juge retirait des biens justes (DEMARCHE 7.117). L'état de référence reste
celui de 12 h 51.

**21 nov. 2026, 12 h 51 à 12 h 58** (sans exemples au socle) : jeu fermé de B **82 %** (0, 0) ; jeu fermé de A **92 %**
(0,33 couvert à tort) ; partie test de A **87 %** (2 couverts à tort). Détail en DEMARCHE 7.116.

**21 nov. 2026, 12 h 42 et 12 h 45** : partie test de A avec exemples **90 %** (2 couverts à tort) ; jeu fermé de B sans
exemples **88 %** (0, 0, portes passées), contre 82 % et 78 % avec exemples : les exemples étaient recopiés au socle
(DEMARCHE 7.116).

**21 nov. 2026, 0 h 27 à 0 h 38, avec exemples, après 7.114** : jeu fermé **A 92 %** (0,33 couvert à tort, 0,33 refus
à tort), **B 78 %** (0, 0), **D 99 %** ; partie test de A **89 %**, 1,33 couvert à tort. **Latence d'un cas seul au 95e
centile : 3,8 à 6,1 s** (contre 20 à 70 s), porte passée partout. La vérification v4 est retirée (DEMARCHE 7.115).

**21 nov. 2026, 0 h 08 et 0 h 12, Assureur A, avec exemples, après 7.113** : jeu fermé **93 %** justes, 83 % exactes,
0,33 couvert à tort (le vase), 0 refus à tort ; partie test **89 %**, 83 % exactes, 2 couverts à tort (`g-p03`,
`g2-p08`), 0,33 refus à tort. Le vélo couvert 3 fois sur 3 ; le miroir « à préciser » au lieu de couvert.

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

**Les marges des résultats principaux** (28 nov., 7.234). Intervalle de confiance à 95 %, méthode de Wilson, qui reste
juste près de 0 et de 1. `couverture juger` l'affiche maintenant à la fin de chaque passe et de `--stabilite`
(`mesure.evaluation.intervalle`).

| Résultat | Taux | Intervalle à 95 % | Ce qu'on peut en dire |
|---|---|---|---|
| Jeu « cinq », lecture des clauses : 53 justes sur 60 | 88 % | 78–94 % | le niveau d'une passe heureuse |
| Jeu « cinq », chaîne de règles : 40,3 sur 60 (moyenne de 3) | 67 % | 54–77 % | les deux intervalles se touchent à peine ; sur les mêmes cas, treize réponses d'écart, dans le même sens sur les trois contrats : l'écart est réel |
| Stabilité, lecture des clauses : 74 justes sur 90 analyses (30 cas, 3 passes) | 82 % | 73–89 % | le niveau à attendre ; les passes portent sur les mêmes cas, la marge réelle est un peu plus large |
| Jeu « six », lecture des clauses (consigne v2) : 46 sur 60 | 77 % | 65–86 % | un jeu plus difficile ; ne se compare pas à « cinq » au point près |
| Couverts à tort, lecture des clauses : 0 sur 60 (« cinq ») | 0 % | 0–6 % | « aucun » veut dire « moins de 6 % », pas « jamais » |
| Couverts à tort, lecture des clauses : 1 sur 60 (« six ») | 2 % | 0–9 % | |
| Couverts à tort, chaîne de règles : 4,7 sur 60 (« cinq ») | 8 % | 3–17 % | |

Ce que les marges disent du projet : à vingt cas par contrat, un contrat seul ne se juge pas (19 sur 20, c'est entre
76 et 99 %) ; à soixante, on distingue la lecture des clauses de la chaîne de règles, pas deux versions de la lecture
des clauses. Pour régler une consigne au point près, il faudrait des jeux de 200 à 300 cas (une marge d'environ ± 5
points).

**Nos jeux ressemblent-ils aux sinistres réels ?** (28 nov., 7.235). Les 365 cas des six jeux, classés à la main
par catégorie de sinistre (`data/repartition/`), comparés à la répartition publiée par France Assureurs pour 2025 :

| Catégorie | Dans nos jeux | Dans la réalité | Lecture des clauses : justes (300 analyses de « cinq » et « six ») |
|---|---|---|---|
| Dégâts des eaux | 13 % | **40 %** | 77 % [60–89] |
| Dommages électriques | 5 % | 11 % | 84 % [62–94] |
| Tempête, grêle, neige | 8 % | 9 % | 100 % [84–100] |
| Responsabilité civile | 13 % | 9 % | 87 % [76–94] |
| Vol et vandalisme | 19 % | 8 % | 86 % [75–93] |
| Bris de glace | 7 % | 8 % | 56 % [33–77] |
| Incendie, explosion | 10 % | 4 % | 74 % [57–86] |
| Catastrophes naturelles | 6 % | 1 % | 90 % [60–98] |
| Autres (juridique, assistance, accidents, objets) | 20 % | 10 % | 85 % [73–92] |

- **Le sinistre le plus fréquent est le moins testé.** Les dégâts des eaux font 40 % des sinistres réels et 13 % de nos
  cas ; sur « cinq » et « six », 13 cas seulement, et une justesse plutôt plus basse que la moyenne. Les vols, les
  incendies et les catastrophes naturelles, plus faciles à imaginer, sont deux à six fois trop représentés.
- **Pondérée par la fréquence réelle**, la justesse de la lecture des clauses passe de 83 % à environ 81 % : peu
  d'écart, mais il repose sur les catégories où nos cas sont rares.
- Les marges par catégorie sont trop optimistes : elles comptent les passes d'un même cas comme des cas distincts.
- **Conséquence** : le prochain jeu doit suivre la répartition réelle, avec au moins 40 % de dégâts des eaux, et viser
  les bris de glace (la catégorie la plus faible).

**Que rapporte la traduction en règles ?** (28 nov., 7.236). Chaque ligne de sortie de `juger` dit ce que la lecture
des clauses avait conclu seule, avant la contresignature des règles (son motif). Sur les 360 analyses déjà payées
(« cinq » : passes 1 à 6 ; « six » : la consigne v2), sans aucun nouvel appel :

| | Avec la contresignature (en service) | Lecture des clauses seule |
|---|---|---|
| Réponses justes | 298 / 360 (83 % [79–86]) | 323 / 360 (90 % [86–93]) |
| **Couverts à tort** | **1** | **9** |
| Refus à tort | 6 | 12 |
| « À préciser » au lieu d'une réponse | 55 | 16 |

| Par contrat | Justes avec / seule | Couverts à tort avec / seule | Refus à tort avec / seule |
|---|---|---|---|
| A (traduit en entier) | 110 / 111 | 0 / 3 | 1 / 1 |
| B (traduit en entier) | 105 / 101 | 1 / 5 | 4 / 10 |
| D (traduit en partie, par choix) | 83 / 111 | 0 / 1 | 1 / 1 |

- **Là où le contrat est traduit en entier (A, B), la contresignature ne coûte rien et protège** : autant de réponses
  justes, sept couverts à tort et six refus à tort de moins sur 240 analyses.
- **Là où il ne l'est qu'en partie (D), elle coûte cher** : 28 réponses justes changées en « à préciser » pour un
  couvert à tort évité. Les règles ne connaissent pas la garantie, et leur silence bloque.
- **Ce que cela dit de la conception.** La version simple (la lecture des clauses seule) répond plus souvent juste, mais
  promet neuf fois à tort ; la traduction en règles vaut ce que vaut sa couverture du contrat. Pistes : ne
  contresigner que les garanties traduites, et laisser passer, avec un avertissement, une garantie que les règles
  ignorent ; ou traduire en premier les garanties les plus fréquentes. À mesurer sur un jeu neuf.
- Limite : l'avis « seule » est relu dans la sortie ; une contresignature absente aurait pu changer la suite de la
  lecture (la relecture ciblée des refus, appelée par un désaccord). L'écart est donc une estimation.

**Plusieurs passes du même jeu** (7.236). « Cinq » a été passé quatre fois en entier (passe 1, puis 4, 5 et 6 ; les
passes 2 et 3 ne portaient que sur dix cas par contrat) :

| Passe | Justes sur 60 | Erreurs du fournisseur | Couverts à tort |
|---|---|---|---|
| 1 (26 nov.) | 53 | 0 | 0 |
| 4 (27 nov.) | 51 | 0 | 0 |
| 5 | 48 | 4 | 0 |
| 6 | 52 | 1 | 0 |
| **Moyenne** | **51 (écart-type 2,2 ; 48 à 53)** | | **0 sur 240** |

Hors erreurs du fournisseur (relancées depuis, 7.225), la justesse va de 85 à 88 %. Sur les 60 cas : 45 justes à
chaque passe, 7 jamais (six de D, que la contresignature bloque, et `c-b08`), 8 parfois ; 11 changent de décision d'une
passe à l'autre, et un seul passe de « couvert » à « non couvert » (`c-a06`, une table basse en verre, où les deux
réponses sont admises par les annotateurs). La passe 1 était la meilleure des quatre : c'est la moyenne, 51, qu'il faut
retenir.

**Le coût et la durée réels** (7.236), relevés sur les 384 analyses de la lecture des clauses passées avec `juger`
(sans erreur du fournisseur), au tarif de Mistral Large (1,36 $ par million de tokens envoyés, 0,14 $ repris du cache,
4,18 $ reçus) :

| | Médiane | 90e centile | 95e centile | Extrêmes |
|---|---|---|---|---|
| Durée d'une analyse | 167 s | 268 s | 305 s | 71 à 446 s |
| Coût d'une analyse | 0,080 $ | | 0,132 $ | jusqu'à 0,211 $ ; moyenne 0,086 $ |

- **Ce qui coûte, c'est ce que le modèle écrit** : 69 % du coût vient des tokens reçus (sa réflexion et ses
  jugements), 13 000 en médiane ; on lui envoie 25 700 tokens en médiane, dont 35 % repris du cache.
- **Par contrat** : A, le plus court, 7,2 centimes ; B, le plus long (dossiers jusqu'à 290 clauses), 9,9 centimes.
- Deux appels au modèle dans 77 % des cas (désignation, jugement), trois quand une clause est redemandée.
- Non comptés : la chaîne de règles qui contresigne (deux petits modèles, des appels courts ; son coût n'est pas relevé),
  et la durée de l'écran.
- Pour un gestionnaire, trois minutes et neuf centimes ; pour mille déclarations par jour, environ 86 $ par jour. Le
  levier est la réflexion du modèle, pas le dossier envoyé.

- **Taille** : un cas pèse 1,5 point. Sur 68 cas, 85 % a une marge d'environ ± 8 points ; sur 97, d'environ ± 7. Les écarts de
  2 ou 3 points se lisent **cas par cas** (le rapport du banc les liste), pas en pourcentage.
- **Variance** : la lecture varie d'une exécution à l'autre même à température 0 ; on présente la
  moyenne avec le minimum et le maximum de 3 exécutions.
- **Tolérance** : « acceptable » couvre les cas ambigus ; l'exactitude stricte est toujours affichée à côté.
- **Biais** : le golden set est écrit par Claude et a servi à corriger le système. Le jeu fermé est la
  seule mesure de fidélité au contrat ; il reste écrit et arbitré par des modèles, pas par quelqu'un du métier.
- **Variation de la lecture** : le même modèle, à température 0 et graine fixe, ne lit pas toujours la même
  déclaration de la même façon. Un cas (`f-a02`) passe de « non couvert » à « couvert » d'une série à l'autre sans
  que rien ne change. Avant d'attribuer un écart à une modification, le banc se rejoue dans les deux états (7.166).
- **Comparabilité** : chaque rapport note la version du golden set, son empreinte et le modèle de lecture.
- **Annotateurs et méthode qui lisent de la même façon** : les réponses attendues des jeux à l'aveugle viennent de
  modèles qui lisent le contrat ; la lecture des clauses aussi. Si un modèle et un juriste comprennent une clause
  différemment, le jeu favorise la lecture des clauses. D'où, pour « cinq », un second avis qui n'est pas Mistral Large ;
  la limite reste tant qu'un jeu n'est pas relu par quelqu'un du métier.
- **Deux jeux ne se comparent pas au point près** : chacun a sa difficulté. La comparaison qui vaut est celle des deux
  méthodes sur le même jeu.

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

### Le second banc : LegalBench (passé le 18 nov., commande retirée depuis)

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

Résultat (18 nov., Mistral Small, 133 cas) : le modèle cite juste, mais tranche 90 % des cas que des lecteurs jugent ambigus (README, section 6). C'est ce que les règles évitent. La commande a été retirée avec la simplification du 20 nov. (7.110) ; les données restent dans `data/externes/legalbench/`, avec leur attribution (CC BY 4.0).

---

## 8. À faire

1. **Un jeu fermé écrit par une personne du métier**, pour chaque contrat ; et un jeu de mesure pour C, qui n'en a pas.
2. **Valider le golden set** (`couverture banc --fiche`, puis `--figer "validation"`) : ses réponses sont proposées, pas validées.
3. Plus de cas dont la bonne réponse est « incertain » dans le golden set.
4. Assureur B : les faits idéaux sans valeurs par défaut que la déclaration ne dit pas.
5. Relever les tokens de la chaîne de règles (`juger` les relève pour la lecture des clauses).
6. Resserrer la porte de latence (10 s ; mesuré à 7 s au plus).
7. Mesurer la lecture des clauses sans contresignature, sur un contrat jamais traduit, avec un jeu neuf.

Fait depuis la première version de cette liste : les jeux à l'aveugle mesurés une seule fois (7.185 à 7.215), le jeu fermé (7.79), le partage mise au point / test (7.107), la lecture par Mistral Large et par Medium mesurées (7.37, 7.118, 7.136), LegalBench passé (7.37).
