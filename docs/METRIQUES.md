# Fiche métriques — comment on évalue le projet

Ce qu'on mesure, sur quels cas, avec quels seuils, et ce que valent les chiffres.
Commande unique : `uv run couverture banc --contrat foyer-appart123-2025` (rapports dans `data/bancs/`).
Démarche et historique des mesures : [DEMARCHE.md](DEMARCHE.md), parties 7.21 et suivantes.

---

## 1. Les jeux de cas

| Jeu | Où | Cas | Rôle | Limite |
|---|---|---|---|---|
| **Golden set** (référence) | `data/golden/` (v6, figé par empreinte) | 97 | Rejoué à chaque changement ; toutes les métriques ci-dessous | Écrit par Claude, ayant servi à corriger le système : mesure la **mise au point** |
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

---

## 4. Les portes

Les seuils sont dans `data/golden/seuils.json`. La commande `couverture banc` sort en erreur si une porte
échoue : branchable sur la CI. **Les seuils se resserrent ; ils ne se relâchent qu'en le notant dans
DEMARCHE**, avec la raison (le seul changement à ce jour, en 7.23, était un changement d'instrument).

---

## 5. Dernières mesures

**18 nov. 2026, 22 h 37, AXA Luxembourg OptiHome, garantie vol (15 cas, golden v7), règles rédigées par
Mistral Large puis relues** : règles seules 100 % ; **chaîne 76 % justes, 0 couvert à tort, 0 refus à tort**,
1 instable ; rappel des faits 82 % ; un cas à la fois : médiane 3,3 s, 95e centile 4,7 s. Progression depuis le
premier banc (62 %) et détail : DEMARCHE 7.59 à 7.61. Cas écrits par Claude après relecture des règles : à
confirmer par un jeu indépendant.

**18 nov. 2026, 22 h 31, Foyer, après les corrections générales de la soirée** (lecture limitée aux variables
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

Aucun jeu public ne donne la réponse selon les conditions générales de Foyer : la réponse dépend du contrat.
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
annotées selon les CG de Foyer par l'auteur), et LegalBench comme **second banc** de généralisation.

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

0. AXA : un jeu de cas écrit par l'auteur sans voir les règles ; les faits idéaux sans valeurs par défaut.

1. Créer le jeu fermé (`data/ferme/`, ≥ 20 cas, auteur), avec plus de cas dont la bonne réponse est « incertain ».
2. Valider le golden set (`couverture banc --fiche`, puis `--figer "validation"`).
3. Mesurer la lecture par Mistral Large, puis la double lecture si elle aide.
4. Passer LegalBench (`couverture legalbench`), avec Mistral Small puis Large.
5. Suite possible : faire rédiger des règles pour chaque clause de LegalBench, pour tester aussi le moteur.
