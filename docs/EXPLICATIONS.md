# Comprendre le projet, fichier par fichier

> **Deux méthodes depuis le 25 nov. 2026, la seconde par défaut depuis le 26.** La **chaîne de règles** (le contrat traduit en règles Prolog, le modèle ne fait que lire la déclaration) et la **lecture des clauses** (le modèle lit et juge chaque clause du contrat, la logique tranche, les règles contresignent). Elles sont comparées, chiffres à l'appui, dans [COMPRENDRE.md](COMPRENDRE.md) ; ce document décrit les deux, fichier par fichier. La seconde est choisie par `COUVERTURE_METHODE` (défaut `clauses`) ou par requête (`methode`).
>
> **Avant le 18 nov. 2026.** Les premières méthodes (grille remplie par le modèle et relue, recherche hybride, fiches compilées, juge de qualité, agent de réparation, dérive et bilan) ont été retirées : les règles Prolog les ont remplacées. Pourquoi, et ce qu'elles ont appris : [DEMARCHE.md](DEMARCHE.md), 7.36. Leurs consignes restent archivées dans `docs/consignes/`, et leur code dans l'historique git (tag `avant-simplification`). Ce document décrit le projet tel qu'il est.
>
> **Noms anonymisés (19 nov. 2026).** Les assureurs s'appellent ici Assureur A, B, C et D (DEMARCHE 7.70). Depuis le 23 nov., leurs noms sont aussi masqués dans le texte des clauses, à l'ingestion (7.160).
>
> **En ligne (23 nov. 2026).** La démonstration tourne sur Azure, derrière un code d'accès (7.161, 7.162). Le document a été relu en entier le 24 nov., contre le code, et complété le 26 pour la lecture des clauses. Les chiffres de mesure, qui bougent, sont tenus à jour dans le README (section 4) : en cas d'écart, il fait foi.

Pour une première lecture, sans vocabulaire technique : [le projet raconté](COMPRENDRE.md). Ce document-ci explique **ce que fait chaque partie du projet, et pourquoi elle est faite ainsi**. Il sert à préparer l'entretien : pour chaque choix, il donne la raison et ce qui a été écarté.

Sommaire :
1. [Lexique](#1-lexique)
2. [Le problème et l'idée générale](#2-le-problème-et-lidée-générale)
3. [Le parcours complet d'un sinistre](#3-le-parcours-complet-dun-sinistre)
4. [Les fichiers, un par un](#4-les-fichiers-un-par-un)
5. [Les données](#5-les-données)
6. [Les tests](#6-les-tests)
7. [L'évaluation et ses indicateurs](#7-lévaluation-et-ses-indicateurs)
8. [Les choix, résumés](#8-les-choix-résumés)
9. [Les questions qu'on peut vous poser](#9-les-questions-quon-peut-vous-poser)
10. [Limites et suites](#10-limites-et-suites)

---

## 1. Lexique

### Assurance

| Terme | Définition |
|---|---|
| **Conditions générales (CG)** | Le texte commun à tous les clients d'un produit d'assurance (par exemple « Habitation A, version 2025 »). Il décrit les garanties, les exclusions, les définitions, les plafonds. C'est ce que le système lit. |
| **Conditions particulières (CP)** | Le document propre à chaque client : son adresse, les garanties et options qu'il a souscrites, ses capitaux, ses franchises. Non publiques. Le système ne lit pas ce document : la formule et les options se saisissent avec la déclaration (DEMARCHE 7.141). |
| **Contrat** | Ici, une version des conditions générales d'un assureur. Un contrat client = CG + CP. |
| **Sinistre** | L'événement qui cause un dommage (vol, incendie, fuite d'eau…) et que l'assuré déclare. |
| **Garantie** | Ce que l'assureur prend en charge : « Nous garantissons le vol des biens… ». |
| **Exclusion** | Ce qui n'est pas pris en charge, même si une garantie semble s'appliquer : « Ne sont pas garantis les vols commis dans les parties communes ». Une exclusion l'emporte sur une garantie. |
| **Exclusion générale** | Une exclusion qui vaut pour toutes les garanties (dommages intentionnels, guerre, usure…). |
| **Condition de garantie** | Ce qui doit être vrai pour que la garantie joue : fermeture à clé, effraction, option souscrite… |
| **Franchise** | Montant qui reste à la charge de l'assuré (par exemple 150 € par sinistre). |
| **Plafond** | Montant maximal remboursé (par exemple 1 000 € pour le contenu d'une cave). |
| **Vétusté** | La dépréciation d'un bien avec le temps, déduite de l'indemnité. |
| **Dépendance** | Local privatif non habitable, clos et couvert : cave, garage, box, grenier. |
| **Parties communes** | Locaux partagés par les occupants d'un immeuble : hall, couloirs, local à vélos collectif. |
| **Effraction** | Forcement ou destruction d'un dispositif de fermeture. Chaque contrat en donne sa propre définition. |
| **Lexique (d'un contrat)** | La partie du contrat qui définit ses termes. Le sens d'un mot dans un contrat est celui de son lexique, pas le sens courant. |
| **Renvoi** | Une clause qui en cite une autre : « au sens de l'article 1.5 », « dans les conditions de l'article 4.2 ». |
| **Gestionnaire sinistres** | La personne qui, chez l'assureur, décide si un sinistre est couvert. Le système reproduit sa façon de raisonner. |

### Technique

| Terme | Définition |
|---|---|
| **LLM** (grand modèle de langage) | Un modèle comme Claude, GPT ou Mistral, qui lit et produit du texte. |
| **Prompt** | Le texte envoyé au modèle : des instructions (le « système ») et un message. |
| **RAG** (*Retrieval-Augmented Generation*) | Chercher des passages dans des documents, puis les donner au modèle pour qu'il réponde. Le RAG « simple » prend les passages les plus proches de la question. |
| **Chunk / découpage** | Le morceau de document qu'on indexe. Ici, un chunk = une clause du contrat, pas un nombre fixe de mots. |
| **Clause** | Dans ce projet, la plus petite unité du contrat : un article numéroté (`4.3`), une sous-section (`2.10-a`) ou un terme du lexique (`12/effraction`). |
| **Ingestion** | Le traitement fait une seule fois par contrat : lecture du PDF, nettoyage, découpage, contrôles, stockage. |
| **Segmentation** | Le découpage du texte en clauses. |
| **Typage** | Le fait de donner une nature à chaque clause : garantie, exclusion, condition, limite, définition, autre. |
| **Normalisation** | Mettre le texte sous une forme comparable : minuscules, sans accents. |
| **Prolog** (SWI-Prolog) | Un langage de programmation logique : on écrit des faits et des règles, le moteur en déduit des conclusions. Ici, il décide de la couverture. |
| **Logique à trois valeurs** (Kleene) | Oui, non, inconnu. « Je ne sais pas » n'est pas confondu avec « faux », contrairement au monde clos de Prolog. |
| **Oracle** | Une seconde implémentation du moteur, en Python (`tests/moteur_reference.py`), comparée à Prolog dans les tests. |
| **Expression régulière** (regex) | Un motif pour reconnaître du texte, par exemple « une ligne qui commence par Article suivi d'un numéro ». |
| **JSON** | Un format de données structuré. Le modèle répond en JSON pour que le code puisse lire sa réponse sans ambiguïté. |
| **Pydantic** | Une bibliothèque Python qui définit des modèles de données et vérifie qu'une donnée a la bonne forme. |
| **SQLite** | Une base de données dans un simple fichier, sans serveur. |
| **Idempotent** | Qu'on peut relancer sans effet de bord : ré-ingérer un contrat inchangé ne refait rien. |
| **Empreinte (hash)** | Un code calculé à partir du contenu d'un fichier. Si le fichier change, l'empreinte change. |
| **Heuristique** | Une règle simple et approximative, sans modèle. |
| **Hallucination** | Quand un modèle affirme quelque chose de faux avec assurance, par exemple une clause qui n'existe pas. |
| **FastAPI / Uvicorn** | Un framework web Python pour écrire une API, et le serveur qui la fait tourner. |
| **API** | Une adresse web qui renvoie des données (ici en JSON) au lieu d'une page. |
| **Docker** | Un outil pour emballer l'application et ses dépendances, et la déployer à l'identique ailleurs. |
| **Clé API** | Le mot de passe qui autorise un programme à utiliser un service payant (ici le modèle de Mistral). Elle se garde dans `.env`, jamais dans le code. |
| **Fichier `.env`** | Un fichier de variables d'environnement à la racine du projet, lu au démarrage. Il contient les secrets et n'est pas versionné. |
| **Limite de débit (429)** | Le fournisseur refuse temporairement les requêtes trop rapprochées. Le système attend et réessaie. |
| **Mode JSON** | Une option de l'API qui oblige le modèle à répondre par un JSON valide. |
| **Protocole** (*Protocol*) | En Python, une interface : « tout objet qui a une méthode `juger` est un juge ». Permet de changer de juge ou de modèle sans toucher au reste. |

### Propres au projet

| Terme | Définition |
|---|---|
| **Groupe** | La section dont dépend une clause. `2.10-a` (exclusions) appartient au groupe `2.10` (garantie vol). |
| **Vocabulaire** | `regles/vocabulaire/` : `commun.json` (le socle et les variables que plusieurs contrats emploient) et un fichier par contrat (celles que lui seul emploie) ; pour chaque variable, son libellé (le nom montré à l'écran et sur la fiche), sa source quand ce sont les conditions particulières du client qui font foi (la formule, une option), ses valeurs, la question à poser quand elles manquent, une aide de lecture par valeur, et la hiérarchie des valeurs (un vélo est un bien du contenu). |
| **Faits** | Ce que la lecture tire de la déclaration, dans le vocabulaire : `evenement = vol`, `lieu = cave`. Ce qu'elle ne dit pas reste inconnu. |
| **Règles d'un contrat** | `regles/<contrat>.pl` : pour chaque garantie, son périmètre, ses circonstances, ses obligations, ses exclusions et ses limites, chacune avec la phrase du contrat qu'elle traduit. |
| **Périmètre** | Ce qui fait qu'une garantie concerne le sinistre (événement, bien, lieu). Hors du périmètre, la garantie ne dit rien. |
| **Réserve** | Une exclusion inconnue que la déclaration n'évoque pas : la réponse est « couvert, sous réserve de… », sans question. Une option des conditions particulières que personne n'a renseignée reste une réserve, ou une question si elle seule peut couvrir. |
| **Exclusion entamée** | Une exclusion inconnue dont un fait est établi (des travaux sont mentionnés) : la question est posée. |
| **Garantie accessoire** | Une garantie qui ne joue qu'après un sinistre couvert (frais de sauvetage, logement provisoire). Elle ne change jamais la décision ; si c'est couvert, elle est listée. |
| **Extension de définition** | Une clause qui élargit un lieu ou un bien assuré (le contenu en séjour temporaire) : elle élargit la définition du contrat, pour toutes les garanties. |
| **Événement non traduit** | Un événement dont aucune garantie n'est encore en règles : le moteur ne refuse jamais, il répond « à examiner ». |
| **Rédaction** | Mistral Large traduit une garantie en règles (un JSON, que le code écrit en Prolog) ; le code contrôle, un humain relit, puis accepte. |
| **Proposition** | Une rédaction en attente dans `regles/propositions/<contrat>/`, avec ses contrôles. |
| **Relecture** | Les corrections de l'auteur sur une proposition, tracées dans la proposition elle-même (`meta.relecture`). |
| **Arbre de preuve** | La trace de la déduction : chaque condition évaluée, sa phrase du contrat, son état, jusqu'aux faits déclarés. |
| **Question décisive** | Une question dont la réponse tranche (« oui → couvert ; non → non couvert »), trouvée par le moteur en essayant chaque réponse. |
| **Verdict** | La réponse : décision, justification, citations, ce qu'il faut vérifier, confiance. |
| **COUVERT / NON_COUVERT / INCERTAIN** | Les trois décisions possibles. INCERTAIN est une vraie réponse, accompagnée de ce qu'il faut vérifier. |
| **Faux « couvert »** | Le système dit « couvert » alors que ce n'est pas le cas. L'erreur la plus grave : c'est une promesse faite au client. |
| **Profil d'assureur** | Les règles de lecture propres à un assureur (ses intertitres et leur type, ses lignes de bruit, le format de son lexique), dans un fichier JSON. |
| **Golden set** | 112 cas étiquetés (97 pour l'assureur A, 15 pour l'assureur B), figés et versionnés, sur lesquels le banc rejoue tout le système. |
| **Banc, couches, portes** | Le banc rejoue le golden set en trois couches (règles seules, lecture, chaîne) ; les portes (`data/golden/seuils.json`) disent si c'est présentable. |
| **Confirmation** | Avant une réponse ferme, le modèle confirme que les faits qui la portent sont bien écrits dans la déclaration ; sinon, la réponse devient INCERTAIN. |
| **Journal** | La table `analyses` : chaque question posée au système et sa réponse, sans le texte du sinistre. |
| **Consigne** (*prompt*) | Le texte d'instructions envoyé au modèle. Le projet n'entraîne pas de modèle : ce qui change d'une version à l'autre, ce sont les consignes. |
| **Manifeste des consignes** | `config/versions_consignes.json` : la version et l'empreinte de chaque consigne. Sert de garde-fou en CI. |
| **Grafana** | Un outil de tableaux de bord qui lit une base et affiche des graphiques. Ici, il lit la base SQLite du projet. |
| **CI** (intégration continue) | Les tests lancés automatiquement à chaque envoi du code (GitHub Actions). |
| **Lecture des clauses** | La seconde méthode, par défaut depuis le 26 nov. : le modèle (Mistral Large) lit les clauses du contrat qui concernent le sinistre et juge chacune ; une logique fixe tranche ; les règles contresignent. |
| **Désignation** | Première étape de la lecture des clauses : dans la table des matières du contrat, le modèle désigne les chapitres à relire. |
| **Dossier** | Les clauses qu'on fait juger pour un sinistre : les chapitres désignés en entier, leurs chapeaux, les exclusions générales, les articles cités, les définitions employées. Le code le compose, pas le modèle. |
| **Clauses attendues** | Pour chaque garantie, la liste, écrite avant tout sinistre, des clauses qu'un gestionnaire doit relire avant de répondre (tables `garanties` et `clauses_attendues`). Une clause attendue sans jugement empêche une réponse franche. |
| **Jugement** | L'effet d'une clause sur la déclaration, rendu par le modèle avec deux citations (le contrat, la déclaration) : `couvre`, `exclut`, `limite` (réduit l'indemnité sans refuser), `a_verifier` (avec la question), `sans_effet`. |
| **Contresignature** | Un « couvert » de la lecture des clauses n'est rendu que si la chaîne de règles dit « couvert » aussi ; sinon, « à préciser ». Un refus fondé sur une clause citée tient seul. |
| **Rappel** | Une question du règlement du sinistre (délai de déclaration, preuves, plafond) : elle ne dit pas si c'est couvert ; elle s'affiche comme une réserve, sans retenir la réponse. |
| **Statut OK / A_VERIFIER** | Le résultat des contrôles d'ingestion : un contrat `A_VERIFIER` a probablement été mal lu. |

---

## 2. Le problème et l'idée générale

**La demande** : dire si un sinistre est couvert par un contrat, pourquoi, et sur quelles clauses. Le recruteur précise que le verdict compte moins que la capacité à **citer ses sources** et à **admettre ses limites**, et il pose la question de l'échelle : **des centaines de contrats différents**.

**Pourquoi l'approche naïve échoue** (coller le PDF dans un chatbot) :
- **L'exclusion ne ressemble pas à la question.** « Vol de vélo » ressemble à « les vélos sont garantis », pas à « vols commis dans les parties communes ». Une recherche par ressemblance rate la clause qui décide.
- **Le sens des mots est dans le lexique**, souvent à l'autre bout du document.
- **Chaque assureur rédige autrement.** Un prompt réglé sur un contrat casse sur le suivant.
- **Rien n'est vérifiable.** Le modèle peut citer une clause inexistante, et personne ne le voit.

**L'idée** : traiter le problème comme un **raisonnement juridique**, pas comme une recherche.
1. **Une fois par contrat** : le découper en clauses contrôlées, puis traduire ses garanties en **règles Prolog** (périmètre, conditions, obligations, exclusions, limites), chacune avec la phrase du contrat qu'elle traduit, mot pour mot. Les règles sont écrites à la main ou par Mistral Large, et **toujours contrôlées par le code**.
2. **À chaque sinistre** : le modèle ne fait que **lire** la déclaration et la traduire en faits d'un vocabulaire commun.
3. **Prolog décide**, en logique à trois valeurs (oui, non, inconnu) : couvert, non couvert, ou incertain avec la question qui tranche.
4. **Chaque réponse se rattache à une phrase du contrat**, et l'arbre de preuve montre la déduction jusqu'aux faits déclarés.

**Ma seconde hypothèse (25 nov.)**, née d'une mesure : sur des cas jamais vus, la chaîne de règles se trompait surtout parce qu'un contrat était mal ou incomplètement traduit, et elle couvrait alors à tort (7 fois sur 60 au jeu « neuf »). La **lecture des clauses** repart du texte même : le modèle juge chaque clause en jeu, citations à l'appui ; le code vérifie les citations et décide selon une logique fixe ; la chaîne de règles contresigne les « couvert ». Je l'ai mesurée une seule fois contre la première, sur un jeu jamais vu (« quatre ») : autant de réponses justes (45 sur 60 contre 42), un couvert à tort au lieu de 4,3, mais quatre refus à tort au lieu de deux, et deux à trois minutes par analyse au lieu de quelques secondes (DEMARCHE 7.207).

---

## 3. Le parcours complet d'un sinistre

### A. Une fois par contrat

```
PDF ─► chargement.py ─► segmentation.py ─► anonymisation.py ─► controle_decoupage.py ─► base.py (SQLite)
       pages, nettoyage   clauses typées     noms masqués        OK / A_VERIFIER            contrats, clauses, renvois
                          (+ profil d'assureur)

garanties ─► règles Prolog (regles/<contrat>.pl) : à la main, ou `couverture rediger` (Mistral Large)
          ─► contrôles : citations dans le contrat, mots dans le vocabulaire, chargement, banc
```

Sur le contrat Assureur A Habitation A : 48 pages deviennent 147 clauses, dont 63 définitions. Statut `OK`.

### B. À chaque sinistre (`couverture analyser` ou l'interface)

Exemple : « Mon vélo a été volé dans ma cave, fermée par un cadenas. »

1. **Lecture** (`lecture.py`) : Mistral traduit la déclaration en faits du vocabulaire : `evenement = vol`, `bien = velo`, `lieu = cave`, `fermeture = cadenas`. Les valeurs hors vocabulaire et les faits hors sujet sont retirés.
2. **Décision** (`regles/moteur.pl`) : la garantie « vol du contenu dans le bâtiment » a son périmètre établi, mais sa condition « si ces locaux sont fermés avec une serrure de sûreté » est fausse : un cadenas n'est pas une serrure de sûreté (définition, art. 12). → **NON_COUVERT**.
3. **Hypothèses** : si la réponse avait été incertaine (fermeture inconnue), le moteur aurait essayé chaque réponse et dit « serrure de sûreté ? oui → couvert ; non → non couvert ».
4. **Arbre de preuve** : chaque condition évaluée, sa phrase du contrat, son état, jusqu'au fait déclaré `fermeture = cadenas`.
5. **Vérification** : chaque citation est recherchée dans la clause du contrat.
6. **Journal** : l'analyse est notée (décision, faits, questions), sans le texte du sinistre. En ligne, la même ligne part aussi sur la sortie standard.

### C. À chaque sinistre, par la lecture des clauses (la méthode par défaut)

Même déclaration, même contrat. Deux à trois minutes ; l'écran affiche chaque étape.

1. **Désigner** (`clauses.py`) : Mistral Large reçoit la table des matières du contrat et la déclaration, et désigne les chapitres à relire (ici, la garantie vol).
2. **Composer le dossier** (`dossier.py`, `attendu.py`) : le code ajoute à ces chapitres leurs chapeaux, les exclusions générales, les articles qu'ils citent et les définitions employées (« serrure de sûreté »). Il sait d'avance quelles clauses doivent recevoir un jugement.
3. **Juger** (`clauses.py`) : Mistral Large rend un jugement par clause, avec la phrase du contrat et celle de la déclaration. Ce qui ne joue pas tient dans une simple liste (`sans_effet`), pour garder la réponse courte. Une clause attendue restée sans jugement est redemandée une fois.
4. **Contrôler** (`jugement.py`) : chaque citation est retrouvée mot pour mot (un mot sauté se répare sur le passage exact) ; un identifiant mal recopié est rétabli ; un jugement mal cité est écarté.
5. **Décider** (`jugement.py`) : une exclusion qui vaut pour tout le contrat refuse ; sinon garantie par garantie, une exclusion l'emporte, un point à vérifier donne « à préciser », une garantie qui couvre sans exclusion donne « couvert » ; une option qui couvre seule donne « à préciser », avec la question de sa souscription.
6. **Contresigner** (`jugement.arbitrer`) : la chaîne de règles a tourné en parallèle ; un « couvert » qu'elle ne confirme pas devient « à préciser », et le désaccord est affiché.
7. **Garder** : les jugements de l'analyse vont dans les tables `analyses_clauses` et `jugements`.

---

## 4. Les fichiers, un par un

L'ordre suit le parcours des données.

Le code est rangé par métier (25 novembre 2026) : quatre sous-dossiers, et à la racine ce que tous partagent.

```
src/couverture/
  contrat/     lire un contrat : chargement, segmentation, profils, anonymisation, controle_decoupage, ingestion,
               tableaux (les formules), base (SQLite)
  analyse/     analyser un sinistre : lecture, exemples, prolog (le moteur), chaine, validation, journal, fiche (le PDF) ;
               et la lecture des clauses : attendu, dossier, jugement, clauses
  redaction/   rédiger les règles d'un contrat : consigne, controles, ecriture, vocabulaire
  mesure/      mesurer : evaluation (les jeux de cas), banc, ferme (le jeu fermé)
  cli/  api/   une commande, une route par fichier
  models.py  texte.py  config.py  llm.py  consignes.py  progression.py     ce que tous partagent
```

Le sens des dépendances : `contrat` ne connaît personne ; `analyse` lit `contrat` ; `redaction` et `mesure` lisent
`analyse` ; `cli` et `api` appellent le tout. Une exception : la banque d'exemples (`analyse/exemples.py`) lit les
jeux de cas de `mesure`, pour tenir ses exemples loin des déclarations qui servent à mesurer. Chaque sous-dossier s'ouvre sur un `__init__.py` qui dit ce qu'il contient.

### `src/couverture/models.py` — les structures de données

**Rôle** : définir la forme de tout ce qui circule entre les étapes, avec Pydantic.

| Modèle | Contenu |
|---|---|
| `TypeClause` | garantie, exclusion, condition, limite, définition, autre. |
| `Clause` | `id` (« 4.3 », « 2.10-a », « 12/effraction »), `article`, `groupe`, `titre`, `chemin` (les titres parents), `texte`, `type`, `pages`, `renvois`. |
| `ClauseRetenue` | Une clause consultée pour la réponse, et pourquoi (« règle », « document complet »). |
| `Faits` | L'événement, le bien, le lieu et les autres faits lus, résumés pour l'affichage et le journal. |
| `Decision` | COUVERT, NON_COUVERT, INCERTAIN. |
| `Citation` | Identifiant de clause, extrait, rôle, validité, pages. |
| `EtatCondition` / `Condition` | Une vérification affichée : une garantie, condition, exclusion ou limite qui a compté, avec sa phrase du contrat et son état. |
| `Verdict` | La décision et tout ce qui la justifie, dont `decision_initiale` (la décision du juge avant contrôle, pour mesurer ce que le contrôle corrige). |
| `Resultat` | La sortie complète : sinistre, contrat, méthode, faits, clauses consultées, verdict. |

**Pourquoi** : des structures explicites rendent chaque étape testable séparément et la sortie entièrement traçable. Pydantic refuse une réponse du modèle mal formée au lieu de la laisser passer.

### `src/couverture/texte.py` — normaliser le français

**Rôle** : `normaliser` met un texte en minuscules, sans accents, « œ » → « oe », apostrophes harmonisées, espaces compactés.

**Pourquoi** : « Garantie » et « garantie », « dégât » et « degat » doivent se rejoindre quand le code compare une citation au contrat, un intertitre à un profil, ou une phrase à une règle.

### `src/couverture/contrat/chargement.py` — lire et nettoyer le PDF

**Rôle** : obtenir des lignes de texte propres, chacune avec son numéro de page.
- `lire_pages` : PDF via pdfplumber (ou pypdf en secours), Word via python-docx, Markdown et texte directement.
- `nettoyer` :
  1. **Puces** : les caractères privés des polices (Wingdings, Symbol) deviennent « • ».
  2. **En-têtes et pieds de page** : une ligne du haut ou du bas présente sur au moins 40 % des pages est retirée. On compare des « signatures » où les chiffres sont remplacés, pour que « Page 12 » et « Page 13 » se reconnaissent.
  3. **Sommaire** : une page titrée « Sommaire » ou « Table des matières », ou une page du début où presque toutes les lignes finissent par un numéro, est retirée. Les lignes avec des points de conduite (« ...... 12 ») aussi.
  4. **Numéros de page seuls** : retirés.
  5. **Mots coupés** : « garan- » + « tie » → « garantie », seulement si la ligne précédente est pleine, pour ne pas recoller « lave- » dans une liste.
- `charger_lignes` : lire, puis nettoyer.

**Pourquoi** : sur un vrai contrat, ce bruit casse le découpage. Le sommaire du contrat Assureur A créait des clauses fantômes (« 10.2 Non-paiement 38 ») avant cette correction. Garder la page de chaque ligne permet de citer « art. 2.10-a, p. 12 ».

### `src/couverture/contrat/segmentation.py` — découper en clauses typées

**Rôle** : c'est le cœur de l'ingestion. Il transforme les lignes en clauses, avec leurs titres, leur type, leur groupe et leurs renvois.

**Ce qui est reconnu comme un titre** :
- **Article** : « Article 4 — Vol », « Art. 4 ».
- **Numéro** : « 4.3 Vélos », « 3.5 - Vol et vandalisme ». Un numéro seul (« 3 Vol ») n'est accepté que s'il ressemble à un titre (majuscule, court, sans point final, numéro ≤ 40), pour ne pas prendre « 1. Les dommages intentionnels ; » pour un titre. Un numéro suivi d'une unité (« 10 % », « 2 ans ») est du texte.
- **Intertitre sans numéro** : une liste de formules qui portent le sens juridique, comme « Ce que nous garantissons », « Ce qui n'est pas garanti », « Exclusions », « Lexique », « Franchise »… Ils deviennent des sous-clauses : `2.2-a`, `2.2-b`.
- **Titre en capitales** : « VOL ET VANDALISME », « MESURES DE PRÉVENTION ».

**Comment les clauses sont construites** :
- Une **pile** de sections suit la hiérarchie. Quand un nouveau titre arrive, on ferme la section en cours et on remonte la pile jusqu'au bon niveau.
- **Identifiants** : le numéro (`4.3`), le numéro du parent plus une lettre pour un intertitre (`2.10-a`), `S1`, `S2`… pour un titre sans numéro. Un numéro répété reçoit un suffixe (`4.3'2`).
- **Groupe** : pour un intertitre, son parent (`2.10-a` → `2.10`) ; pour une clause numérotée, le numéro du parent (`4.3` → `4`). Le groupe sert à rattacher les exclusions à leur garantie.
- **Lexique éclaté** : une section de définitions est coupée en une clause par terme. Deux formats sont gérés : « Terme : définition » sur une ligne, et le terme seul sur sa ligne avec la définition dessous (le format d'Assureur A). Chaque terme devient `12/effraction`, `12/parties-communes`…
- **Clauses trop longues** (plus de 2 500 caractères, souvent des listes d'exclusions) : coupées aux puces en morceaux (`2.13~1`, `2.13~2`) pour que les citations restent précises.

**`classer` : le typage**, dans cet ordre :
1. le titre propre de la clause (« Ce qui n'est pas garanti » → exclusion ; « Franchise » → limite ; « Lexique » → définition…) ;
2. sa formulation (« ne sont pas garantis » → exclusion, testé avant « sont garantis » qui est contenu dedans ; « nous garantissons » → garantie ; « sous réserve » → condition) ;
3. les titres de ses parents ;
4. sinon : autre.

**Renvois** : `extraire_renvois` repère « article 4.2 », « art. 1.5 », « articles 4.1 et 4.2 ». Il écarte les références à des lois (« art. 58 de la loi du 4 avril 2014 », « article 1302 du Code civil ») : un mot comme loi, code, arrêté ou RGPD juste après, ou un numéro trop long (« 1302 »). `resoudre` relie chaque renvoi à la clause visée, ou à ses premières sous-clauses.

**Pourquoi** : une citation précise exige une clause entière et typée. Le type permet ensuite à la recherche de ramener les exclusions et au contrôle de vérifier qu'un « couvert » s'appuie sur une garantie. Les règles ont été ajustées sur un PDF de test mis en page comme un vrai contrat, puis sur le vrai contrat Assureur A.

### `src/couverture/contrat/controle_decoupage.py` — repérer les contrats mal lus

**Rôle** : `controler` produit un rapport et un statut, `OK` ou `A_VERIFIER`. Alertes :
- moins de 15 clauses (le découpage a probablement échoué) ;
- plus de 40 % de clauses sans type (titres non reconnus) ;
- aucune garantie, aucune exclusion ou aucune définition détectée ;
- pas d'exclusions générales repérées ;
- trop de renvois vers des clauses introuvables (plus de 3, ou plus de 5 % des clauses).

Le rapport liste aussi les garanties sans exclusion voisine et les clauses très longues.

**Pourquoi** : avec des centaines de contrats, personne ne relit chaque découpage. Un contrat mal lu doit être signalé, pas servi en silence. Exemple : « un contrat sans exclusion n'existe pas » ; si on n'en trouve aucune, c'est la lecture qui a échoué.

### `src/couverture/contrat/profils.py` — les règles propres à un assureur

**Rôle** : un profil est un fichier JSON dans `data/profils/<nom>.json`, désigné dans le catalogue (`"profil": "assureur-a"`). Il contient :
- `intertitres` : des titres propres à l'assureur et leur type (« Les situations hors contrat » → exclusion). La segmentation les reconnaît comme intertitres, et `classer` leur donne ce type en priorité ;
- `lignes_ignorees` : des expressions régulières pour les lignes de bruit que le nettoyage n'a pas vues (une référence de document répétée…) ;
- `lexique` : le format des définitions (`deux_points`, `terme_seul`, ou `auto`).

`valider_profil` refuse un type inconnu, une expression invalide, un nom mal formé. `charger_profil` le lit.

**Pourquoi** : les règles générales couvrent la plupart des contrats. Quand un assureur rédige autrement, on n'ajoute pas un cas particulier dans le code : on écrit un profil, réutilisé pour toutes les versions de ses contrats. C'est ce qui rend l'approche tenable sur des centaines de contrats, comme `sources.yaml` dans SortirIA pour les agendas.

### `src/couverture/contrat/base.py` — le stockage multi-contrats

**Rôle** : une base SQLite avec trois tables.
- `contrats` : identifiant, assureur, produit, version, fichier, empreinte, statut, rapport des contrôles, texte brut, date d'ingestion.
- `clauses` : toutes les clauses de tous les contrats, avec le contrat auquel elles appartiennent, leur ordre, leur groupe, leur type, leurs pages.
- `renvois` : les liens d'une clause vers une autre.

Méthodes : `enregistrer` (remplace entièrement un contrat), `contrats`, `contrat`, `clauses(contrat_id)`, `texte_brut`, `empreinte`.

**Pourquoi** : chaque contrat est lu une fois, et chaque question ne charge **que les clauses du contrat concerné**. On ne mélange jamais deux contrats. SQLite suffit pour des centaines de contrats et ne demande aucun serveur. En production, ce serait PostgreSQL, avec le même schéma.

### `src/couverture/contrat/ingestion.py` — de fichier à base

**Rôle** :
- `ingerer_fichier` : calcule l'empreinte du fichier ; s'il n'a pas changé depuis la dernière fois, ne fait rien (idempotence) ; sinon lit, découpe, contrôle et enregistre.
- `ingerer_dossier` : fait de même pour tous les fichiers de `data/contrats`, avec les métadonnées de `catalogue.json` (identifiant, assureur, produit, version, et le **profil d'assureur** s'il y en a un). Sans entrée au catalogue, l'identifiant est tiré du nom du fichier.
- **L'empreinte** couvre le fichier, son profil **et** la liste des noms à masquer : modifier l'un des trois relance le découpage.

**Pourquoi** : ajouter un contrat se résume à déposer un fichier et relancer `couverture ingerer`. La version du contrat compte : un client garde les CG en vigueur au moment de sa souscription.

### `src/couverture/contrat/anonymisation.py` — masquer les noms dans le texte

**Rôle** : après le découpage, remplacer dans chaque clause et dans le texte brut le nom de l'assureur (« Assureur A »), de son assisteur, ses adresses, ses numéros. Les courriels, les sites et les téléphones sont masqués pour tout contrat ; le reste vient d'une liste propre à chaque contrat, `data/contrats/noms.prive.json`, qui n'est pas versionnée (la versionner publierait les noms). `ingerer` affiche le nombre de remplacements.

**Pourquoi après le découpage** : masquer avant aurait pu changer les titres et les numéros que le découpage reconnaît. Les citations des règles restent exactes : elles ne portaient pas sur ces passages (vérifié, 567 sur 567).

**Ce que ça ne fait pas** : le texte reste celui de l'assureur, reconnaissable par qui le connaît. C'est pourquoi les conditions générales ne sont pas redistribuées, et pourquoi, en ligne, on ne lit que les clauses citées.

### `src/couverture/llm.py` — parler au modèle

**Rôle** : le client de Mistral, sans bibliothèque externe (de simples appels HTTP), derrière un protocole `LLM` : une méthode `completer(systeme, message)` (les tests branchent des modèles factices).
- `MistralLLM` : l'API de Mistral, `https://api.mistral.ai/v1`, au format OpenAI (`OpenAICompatibleLLM`). Clé dans `MISTRAL_API_KEY`, modèle `mistral-large-latest` sauf si `COUVERTURE_MODELE` dit autre chose. Le **mode JSON** de Mistral est activé (`response_format`) : le serveur garantit une réponse JSON valide, ce qui évite les réponses illisibles.

`configurer()` renvoie le modèle des analyses, ou celui de la rédaction des règles (`configurer("contrat")`, `COUVERTURE_MODELE_CONTRAT`). Une valeur d'exemple laissée telle quelle (« colle-ta-cle-ici ») est ignorée. Sans clé, il renvoie `None`, et l'analyse demande de configurer une clé. Anthropic et les API compatibles OpenAI ont été retirés le 20 nov. 2026 : jamais employés ni testés sur le projet.

`_poster` envoie les requêtes avec **de nouvelles tentatives** sur les erreurs passagères : 429 (limite de débit atteinte) et erreurs serveur 5xx, en attendant de plus en plus longtemps (ou le délai indiqué par le serveur). Une clé refusée (401, 403) donne un message clair : « Clé API refusée, vérifier la clé dans le fichier .env ». Ces erreurs (`ErreurLLM`) remontent jusqu'à l'utilisateur au lieu d'être confondues avec une réponse illisible du modèle.

Température 0 partout, pour des réponses stables d'une exécution à l'autre.

**Réponses JSON** : `extraire_json` récupère l'objet JSON même entouré de texte ; `appeler_json` redemande une fois une réponse coupée ou illisible ; `pour_travail_long` donne plus de temps et de tokens au travail fait une fois par contrat (rédaction des règles).

**Pourquoi Mistral par défaut** : fournisseur européen, données hébergées dans l'UE, ce qui compte pour un assureur luxembourgeois qui traite des données clients. Prix faible, API au format OpenAI. **Un autre modèle** (hébergé chez l'assureur, par exemple) se brancherait en une classe qui respecte le protocole `LLM` : rien d'autre ne change.

### `src/couverture/config.py` — les clés hors du code

**Rôle** : `charger_env` lit le fichier `.env` à la racine du projet et place ses valeurs dans l'environnement, **sans écraser** une variable déjà définie. Il gère les commentaires, les guillemets et le préfixe `export`. Appelé au démarrage de chaque commande.

**Pourquoi** : une clé API ne doit jamais être écrite dans le code ni versionnée. `.env` est dans le `.gitignore`. Son contenu minimal :

```
MISTRAL_API_KEY=colle-ta-cle-ici
COUVERTURE_MODELE=mistral-medium-2604                 # lit les déclarations
COUVERTURE_MODELE_VERIFICATION=mistral-small-2603     # vérifie et confirme les faits
COUVERTURE_MODELE_CONTRAT=mistral-large-4-0           # rédige les règles, une fois par contrat
```

Trois rôles, trois modèles, désignés par leur version datée : celui qui lit le mieux n'est pas celui qui vérifie le mieux (DEMARCHE 7.136), et un nom en « latest » change sans prévenir (7.145). Sans ces variables, le code prend `mistral-large-latest`. En déploiement, les mêmes variables sont passées au conteneur (`docker run --env-file .env`).

### `regles/` et `src/couverture/analyse/` (`prolog.py`, `lecture.py`, `chaine.py`) — le contrat en règles Prolog

**Rôle** : le contrat est écrit en **règles**, un moteur logique décide, et le modèle ne fait que lire les faits de la déclaration.
- `regles/vocabulaire/` : `commun.json` (événement, bien, lieu, et les variables que plusieurs contrats emploient : effraction, auteur, cause de l'eau…) et un fichier par contrat pour les variables que lui seul emploie ; pour chacune, ses valeurs permises et la question à poser quand elle manque. `couverture regles --contrat … --ranger` remet chaque variable dans son fichier (7.119) ;
- `regles/moteur.pl` : le moteur, commun à tous les contrats. Logique à **trois valeurs** (oui, non, inconnu), pour ne pas confondre « je ne sais pas » avec « faux » (le monde clos de Prolog). Il applique les règles de gestionnaire (périmètre, circonstances, exclusions, obligations avec lien causal, charge de la preuve, exclusions partielles) et combine les garanties ;
- `regles/<contrat>.pl` : les règles d'un contrat, sous forme de données (`definition`, `garantie`, `perimetre`, `circonstance`, `obligation`, `exclusion`, `limite`), chacune avec la phrase du contrat qu'elle traduit ;
- `regles/cas/<contrat>.jsonl` : les faits « idéaux » de chaque sinistre de test, pour éprouver les règles sans modèle ;
- `prolog.py` : trouve SWI-Prolog, lui fait charger le moteur et les règles, pose les faits (vérifiés : rien ne peut être injecté), lit la décision en JSON ;
- `lecture.py` : `extraire_faits_regles` fait lire la déclaration par le modèle, dans le vocabulaire, en laissant inconnu ce qu'elle ne dit pas, puis ramène les faits au vocabulaire (préciser, impliquer, filtrer) ;
- `chaine.py` : `PipelineRegles` assemble la lecture, la décision et la confirmation, puis met en forme la réponse et l'arbre de preuve ;
- `couverture regles --contrat <id>` : vérifie le chargement sans avertissement, le vocabulaire, les citations (mot pour mot dans les clauses), et les cas.
- **Raisonnement par hypothèses** (`explorer/2` dans `moteur.pl`) : quand la décision dépend de faits inconnus, le moteur essaie chaque réponse possible (assertz, décision, retract) et classe chaque question : décisive (« oui → couvert ; non → non couvert »), utile, ou inutile (plus posée) ; sans question décisive, il cherche une paire qui tranche. Les valeurs possibles viennent du vocabulaire. L'oracle Python (`Explorateur`) refait le même calcul pour le test différentiel ;
- **Arbre de preuve** (`arbres_de_preuve/2` dans `moteur.pl`) : pour chaque garantie retenue, l'arbre de ce que le moteur a évalué — périmètre, conditions, obligations, exclusions —, chaque nœud avec sa phrase du contrat et son état (oui, non, inconnu), jusqu'aux faits déclarés. Il est recalculé avec le même `eval/2` que la décision : c'est la trace de la déduction, pas une explication écrite après coup. `arbre_lisible` (chaine.py) l'élague pour la lecture (la branche vraie d'un « ou », les branches fausses d'un « et », les exclusions qui ne jouent pas sont comptées) ; l'oracle Python refait le même arbre pour le test différentiel ;
- `regles/<contrat>.pl` déclare aussi `evenement_traduit(...)` : un événement déclaré dont la garantie n'est pas encore traduite (la tempête, par exemple) empêche le moteur de refuser, il répond « à examiner » ;
- `src/couverture/redaction/` (`couverture rediger --article 2.2`, plusieurs articles en parallèle) : **Mistral Large rédige les règles d'une garantie**. Il remplit un schéma JSON (le code écrit le Prolog), déclare les faits qui manquent au vocabulaire (avec leur question, leur aide de lecture et la valeur dont ils précisent le sens), ce qu'il ne sait pas traduire (`non_traduit`, bloquant) et ce qui ne change pas la décision (`hors_decision`, cité). Le code remet en forme ce qu'il sait corriger (une condition rendue sans citation, une condition des conditions particulières mise en réserve), puis contrôle : structure, vocabulaire, citations (mot pour mot, rattachées à la bonne clause), couverture de chaque exclusion du contrat, réserves (« à l'exception de »), limites qui posent une condition, portée des exclusions, définition de l'événement couvert, concepts et identifiants, chargement par SWI-Prolog et non-régression sur les cas. Les propositions restent dans `regles/propositions/` jusqu'à `--accepter`, refusé tant qu'un contrôle bloque ; `--accepter-vocabulaire` ajoute les faits nouveaux après lecture. Le paquet : `consigne.py` (la consigne et le contexte), `ecriture.py` (JSON → Prolog), `controles.py`, `vocabulaire.py`, et les commandes dans `__init__.py` ;
- **trois façons d'étendre une garantie**, distinguées par le moteur : une garantie **accessoire** (`accessoire/1` : frais après un sinistre couvert, jamais dans la décision), une **extension de définition** (`extension/4` : le contenu en séjour temporaire élargit le bâtiment, pour toutes les garanties), et une **réserve** (ce que l'assureur aurait à prouver). Une **garantie optionnelle** (`option/1`) dont on ne sait pas si elle est souscrite donne « à préciser » si elle est seule à couvrir. DEMARCHE 7.68, 7.69 et 7.109.

**Pourquoi** : la première méthode (des fiches de questions) ne savait pas représenter une condition cachée dans un tableau de limites ni une exclusion cachée dans une définition ; une règle les exprime directement. La décision devient un calcul reproductible. Les tests utilisent aussi `tests/moteur_reference.py`, une seconde implémentation du moteur en Python : là où SWI-Prolog est installé, un test vérifie que les deux concordent.

**La lecture** (`extraire_faits_regles`) : en deux temps, puis vérifiée. Les deux temps : d'abord l'événement, le bien et le lieu ; puis seulement les questions qui concernent cet événement, avec ce qui est déjà établi. Chaque appel envoie un **schéma JSON** qui n'admet que les valeurs du vocabulaire (`schema_faits`), sans rendre aucune variable obligatoire. Les lectures en un temps et en parallèle, essayées et écartées (DEMARCHE 7.38 à 7.42), ont été retirées. Puis une vérification : chaque fait du temps 2 est soumis au modèle comme une affirmation, et un fait « non dit » redevient inconnu (7.43) ; si retirer ces faits ferait passer la décision à « couvert », le moteur garde la lecture non vérifiée : un doute ne fait jamais couvrir (7.44). Enfin, avant toute réponse ferme, le moteur désigne les faits qui la portent (`faits_decisifs`) et le modèle confirme qu'ils sont écrits ; un seul « non dit » et la réponse devient « incertain », avec la question (`PipelineRegles.confirmer`, 7.49). Le temps 2 reçoit aussi des déclarations proches du même événement et leurs faits (`exemples.py`, 7.107, 7.108, 7.116 ; par défaut depuis 7.112, `COUVERTURE_EXEMPLES=non` pour s'en passer). Il faut la banque indexée (`couverture exemples --indexer`) : sans elle, la lecture se fait sans exemples.

**Le moteur chargé une fois** (`MoteurPermanent`) : un SWI-Prolog par contrat reste ouvert ; Python lui envoie les faits sur une ligne, il répond une ligne JSON (`servir` dans `moteur.pl`). Il est relancé s'il s'arrête ou si les règles changent sur le disque. `COUVERTURE_PROLOG_PERMANENT=non` revient à un processus par décision (DEMARCHE 7.46).

### `src/couverture/analyse/attendu.py`, `dossier.py`, `jugement.py`, `clauses.py` — la lecture des clauses

La seconde méthode, en quatre fichiers, du plus mécanique au seul qui appelle le modèle.

- **`attendu.py`** calcule, du seul découpage et une fois par contrat, les tables `garanties` (repère, titre, chemin, optionnelle ou non) et `clauses_attendues` (pour chaque garantie, chaque clause à relire, son rôle, et si elle peut bloquer). *Pourquoi* : on ne constate un manque que si l'on a écrit d'avance ce qui devait être là ; la complétude d'une analyse devient une jointure SQL.
- **`dossier.py`** compose le dossier d'un sinistre à partir des chapitres désignés, sans laisser de choix au modèle ; dans le doute, il élargit (une clause de trop coûte des tokens, une exclusion oubliée coûte un couvert à tort). Il reconnaît aussi, à leur titre, les clauses du règlement du sinistre (délai, estimation, franchise) : leurs questions deviennent des rappels.
- **`jugement.py`** : les contrôles d'un jugement (clause au dossier, citations exactes, question présente), les rattrapages en code (identifiant rétabli, alinéa ramené à sa clause, citation de la déclaration abrégée par « … » acceptée quand chaque morceau y figure), la jointure, la décision (`decider`), la contresignature (`arbitrer`), et l'enregistrement des jugements. Rien n'y appelle le modèle.
- **`clauses.py`** : les deux consignes (désigner, juger), les deux appels à Mistral Large, la relance des clauses oubliées, et l'analyse de bout en bout (`lire`), qui annonce ses étapes au suivi de l'écran. L'ordre de l'envoi est choisi pour le cache du fournisseur : ce qui ne change pas d'un sinistre à l'autre d'abord, la déclaration à la fin.

*Ce qui a été écarté* : demander au modèle « ce sinistre est-il couvert ? ». Il ne voit jamais cette question : il désigne des chapitres, puis juge des clauses une à une ; la réponse est calculée.

### `src/couverture/mesure/banc.py` et `data/golden/` — le banc d'essai

**Rôle** : rejouer tout le système sur un jeu de référence figé (le *golden set* : 112 cas sur deux contrats, étiquetés par garantie, thème, origine et auteur), en trois couches : les **règles** seules sur les faits idéaux, la **lecture** des faits par le modèle comparée aux faits idéaux, la **chaîne** complète sur plusieurs exécutions. Des **portes** (`data/golden/seuils.json`) disent si c'est présentable ; la commande `couverture banc` sort en erreur si une porte échoue. Chaque passage est gardé dans `data/bancs/` et comparé au précédent. `--figer` versionne le golden set ; `--fiche` écrit la fiche de validation des réponses attendues.

**Pourquoi** : un score unique dit qu'il y a une erreur ; trois couches disent si elle vient des règles, de la lecture ou de leur combinaison. Et une référence qui change sans le dire ne mesure plus rien.

### `src/couverture/analyse/journal.py` — le journal des analyses

**Rôle** : chaque analyse faite par l'interface ou par `couverture analyser` est notée dans la table `analyses` : date, contrat, méthode, décision (avant contrôle et finale), confiance, faits repérés (événement, bien, lieu), citations rejetées, questions à poser, durée, versions des consignes. Les erreurs du modèle sont notées aussi. Les colonnes `decision_avant_relecture`, `conditions_ecartees` et `contestations` viennent des méthodes retirées ; elles restent dans le schéma pour les bases existantes et les tableaux Grafana.

**Ce qui n'est pas noté** : le texte du sinistre, seulement sa longueur. Une déclaration de sinistre peut contenir des données personnelles ; le journal n'en a pas besoin.

**Pourquoi** : le banc mesure le système sur des cas écrits à l'avance ; le journal mesure ce qui se passe vraiment (comme `search_log.py` dans SortirIA).

**En ligne** : la base vit dans le conteneur et repart de l'image à chaque réveil. L'image définit `COUVERTURE_JOURNAL_SORTIE` : chaque ligne est alors aussi écrite sur la sortie standard, en JSON, que l'hébergeur collecte (`az containerapp logs show`). Grafana, lui, reste un outil du poste.

### `src/couverture/consignes.py` — le versionnage des consignes

**Rôle** : `CONSIGNES` liste les quatre consignes en service (lecture en deux temps : socle puis détails, vérification des faits, rédaction des règles), le texte qui porte chacune dans le code, et sa version.
- **archive** : `ecrire_manifeste` écrit aussi le texte intégral de chaque nouvelle version dans `docs/consignes/<consigne>/<version>.txt`, sans jamais réécrire une version archivée. `verifier` échoue si le texte d'une version en service ne correspond plus à son archive. L'histoire des consignes (rédaction des règles v1 à v9, et celles des méthodes retirées) reste ainsi lisible, avec le pourquoi de chaque changement dans `docs/DEMARCHE.md` ;
- `etat_actuel` calcule la version et l'empreinte de chaque texte ; `ecrire_manifeste` les écrit dans `config/versions_consignes.json` ;
- `verifier` compare le code au manifeste et signale un texte modifié **sans nouvelle version**, ou un manifeste pas à jour. Un test l'appelle : la CI échoue ;
- `versions_courtes` (« lecture-socle:v2,redaction-regles:v13… ») est notée dans le journal à chaque analyse.

**Pourquoi** : une consigne modifiée change les réponses. Pour comparer deux versions, ou comprendre une réponse passée, il faut savoir quelle consigne l'a produite. C'est la même règle que SortirIA (`scripts/versionnage.py`).

### `monitoring/grafana/` — les tableaux de bord

**Rôle** : `construire_tableaux.py` écrit les deux tableaux en JSON, dans `provisioning/dashboards/`, chargés automatiquement par Grafana avec la source SQLite (`provisioning/datasources/sqlite.yml`).
- **Réponses** : usage, décisions par jour, part d'INCERTAIN, rattrapages par jour (réponses corrigées par le contrôle des citations, preuves écartées), temps de réponse, INCERTAIN par contrat, sinistres déclarés, questions à poser les plus fréquentes, versions des consignes en service avec leurs résultats, dernières erreurs ;
- **Contrats** : lecture de chaque contrat, clauses par type, alertes.

Les requêtes utilisent les macros de période du plugin (`$__unixEpochFrom()`, `$__unixEpochTo()`) et les fonctions JSON de SQLite (`json_each`, `json_extract`) pour lire les rapports et les questions.

**Pourquoi un générateur** : un tableau Grafana est un JSON illisible ; ici les requêtes sont écrites en clair, et un test les exécute toutes sur une vraie base et vérifie que le JSON est à jour (même méthode que `construire_tableau_modeles.py` dans SortirIA). **Pourquoi SQLite** : garder le projet petit ; avec PostgreSQL, comme dans SortirIA, seules la source et quelques fonctions changeraient.

### `docker-compose.yml` et `.github/workflows/ci.yml`

- **docker compose** lance l'API (port 8021) et Grafana (3011). L'API lit les contrats au démarrage ; la base `data/base.sqlite` est partagée avec Grafana, en lecture seule. Les ports évitent ceux de SortirIA.
- **La CI** installe SWI-Prolog et le projet (avec uv), vérifie les versions des consignes, puis lance les tests : le moteur Prolog y est comparé à l'oracle Python.

- **L'image en ligne** (`deploiement/Dockerfile`) est une autre image : elle construit l'écran, embarque la base du poste nettoyée (`nettoyer_base.py` retire le journal local et le texte brut), et ne contient ni les PDF, ni la liste des noms. Un seul conteneur sert l'écran et l'API.

Le détail est dans `monitoring/README.md`.

### `src/couverture/analyse/validation.py` — aucune décision sans preuve

**Rôle** :
- `extrait_present` : vérifie qu'un extrait figure dans une clause, à la ponctuation, aux accents et à la casse près. Les coupures « … » sont acceptées : chaque morceau doit être présent.
- `valider` : appliqué à tous les verdicts.
  - une citation d'une clause non fournie, ou introuvable, est marquée rejetée ;
  - le **rôle** d'une citation (garantie, exclusion…) est repris du contrat, pas de ce que dit le modèle ;
  - COUVERT sans aucune garantie citée correctement devient INCERTAIN ;
  - une décision ferme sans aucune citation valide devient INCERTAIN ;
  - INCERTAIN doit toujours dire quoi vérifier ;
  - la décision d'origine est gardée dans `decision_initiale`.

**Pourquoi** : c'est le garde-fou contre les hallucinations, fait par du code, donc fiable. En gardant la décision d'origine, on peut mesurer combien de fois le contrôle a rattrapé le modèle.

### `src/couverture/mesure/evaluation.py` — les jeux de cas

**Rôle** : `charger_cas` croise les sinistres et les réponses attendues ; `evaluer` rejoue une chaîne sur un jeu (le banc s'en sert pour sa couche « chaîne »). Une clause attendue « 4.4 » est considérée comme citée si la clause 4.4 ou l'un de ses morceaux l'est.

### `src/couverture/cli/` — la ligne de commande

Une commande par module (`cli/regles.py`, `cli/banc.py`…), comme une route par fichier dans l'API ; `cli/__init__.py` les assemble, `cli/affichage.py` met en forme une analyse.

| Commande | Effet |
|---|---|
| `couverture ingerer [--forcer]` | Lit `data/contrats`, remplit la base ; affiche statuts et alertes. |
| `couverture contrats` / `clauses --contrat ID` | Liste les contrats ; affiche le découpage d'un contrat. |
| `couverture regles --contrat ID [--faits JSON] [--jeu …]` | Vérifie les règles (chargement, vocabulaire, citations, cas) ; avec `--faits`, décide un cas et montre l'arbre de preuve. Sans modèle. |
| `couverture formules --contrat ID --page N` | Lit le tableau des garanties par formule d'un contrat. |
| `couverture rediger --contrat ID --article 2.2` | Mistral Large rédige les règles d'une garantie ; le code les contrôle ; `--accepter` les ajoute. |
| `couverture analyser --contrat ID "…" [--detail] [--json]` | Analyse un sinistre : décision, motif, preuves, questions, arbre de preuve. |
| `couverture juger --contrat ID "…" \| --jeu J [--cas …] [--regles] [--paralleles 4]` | La lecture des clauses sur une déclaration ou sur les cas d'un jeu : décision, clauses jugées, tokens et cache ; un bilan par jeu dans `data/debug/`. Le jeu « quatre » demande `--mesure-finale`. |
| `couverture banc --contrat ID [--jeu ferme] [--partie test] [--couches …]` | Le golden set ou le jeu fermé rejoué : règles, lecture, chaîne ; portes ; rapport dans `data/bancs/`. |
| `couverture exemples [--partager] [--indexer] [--proches "…"]` | La banque d'exemples de lecture et le partage mise au point / test. |
| `couverture api [--port 8001]` | Lance l'API FastAPI (documentation sur `/docs`). |
| `couverture versions [--manifeste]` | Vérifie les versions des consignes ; réécrit le manifeste. |
| `couverture modele` | Affiche le modèle configuré et teste la connexion. |

### L'API (`src/couverture/api/`) et l'interface (`frontend/`)

L'API FastAPI (une route par fichier, la logique dans `service.py`, la clé dans l'en-tête `x-api-key`) et l'interface Angular aux couleurs du système de design de foyer.lu : voir `README.md`.

**La méthode** se choisit par `COUVERTURE_METHODE` (défaut `clauses`) ou par requête (`methode`). Avec `clauses`, `service.analyser_clauses` fait tourner la chaîne de règles en parallèle pour la contresignature, et `resultat_clauses` met la réponse au format de l'API : citations, limites, questions, rappels, raisonnement clause par clause. Le **suivi** (`routes/analyse_suivie.py`, un flux de lignes JSON) annonce d'abord les étapes de la méthode ; pendant une étape longue, il envoie une ligne vide toutes les 15 secondes, pour que l'hébergeur ne coupe pas une requête de plusieurs minutes (7.208 : 279 s tenues en ligne).

**En ligne** (`api/acces.py`, actif quand `COUVERTURE_CODE_ACCES` est défini) : le navigateur demande un code d'accès, qui tient lieu de clé (en local, c'est le proxy de développement qui ajoute la clé ; en ligne il n'y a pas de proxy) ; les analyses sont comptées par jour ; la liste des clauses est fermée et `routes/clause.py` ne sert une clause que si les règles la citent ; l'API sert l'écran construit (`COUVERTURE_FRONT`). Pourquoi : une page ouverte dépenserait le crédit du modèle pour n'importe qui, et donnerait à télécharger le texte de quatre assureurs. L'ancienne page (`web.py`, HTML sans framework) a été retirée le 20 nov. 2026.

### `src/couverture/__init__.py`

Expose `Resultat`, `Verdict`, `Decision` pour un usage en Python, et la version du paquet.

### Fichiers à la racine

| Fichier | Rôle |
|---|---|
| `pyproject.toml`, `uv.lock` | Le paquet Python : dépendances (pydantic, pdfplumber, fastapi, uvicorn), la commande `couverture`, la configuration de pytest ; les versions exactes, installées avec `uv sync`. |
| `perso/` | Les fichiers de l'auteur, non versionnés. |
| `Dockerfile` | Construit l'image de `docker compose` : installe le paquet, ingère les contrats et lance l'API. La clé du modèle est passée au lancement, jamais écrite dans l'image. |
| `deploiement/` | L'image de la démonstration en ligne, le nettoyage de la base qu'elle embarque, le modèle du fichier de secrets. |
| `.dockerignore` | Ce que la construction d'une image ne lit pas : `.env`, `perso/`, la liste des noms, les secrets de l'image en ligne. |
| `.gitignore` | Exclut la base générée, les caches, le fichier `.env` (les clés) et **les PDF des assureurs** (on ne redistribue pas leurs documents). |
| `README.md` | La présentation du projet. |

---

## 5. Les données

| Fichier | Contenu |
|---|---|
| `data/contrats/catalogue.json` | Nom de fichier → identifiant, assureur, produit, version, profil. |
| `data/contrats/SOURCES.md` | Les contrats utilisés, anonymisés ; les liens de téléchargement restent chez l'auteur (`SOURCES.prive.md`, non versionné). Les PDF ne sont pas versionnés. |
| `data/contrats/fictif_habitat_serein.md` | Un contrat **inventé**, écrit pour contenir les pièges classiques (local collectif, cave privative, bougie avec ou sans flammes, options). Il sert aux tests. |
| `data/golden/` | Le golden set : `sinistres.jsonl` (les déclarations), `annotations/<contrat>.jsonl` (décision attendue, réponses acceptables, clauses et questions attendues, note), `version.json` (version et empreinte par contrat), `seuils.json` (les portes), `A_VALIDER.md` (la fiche de validation par l'auteur). |
| `regles/cas/golden/<contrat>.jsonl` | Les faits idéaux de chaque cas du golden : ce qu'une lecture parfaite donnerait. La couche « règles » du banc les utilise. |
| `data/sinistres.jsonl`, `data/annotations/` | Le premier jeu (mise au point), écrit avant le code : les deux cas du recruteur et des variations qui changent **un seul fait**. |
| `data/validation/`, `data/redaction/` | Deux jeux plus petits : des cas écrits après coup pour vérifier une correction, et des cas des garanties rédigées par le modèle. |
| `data/bancs/` | Chaque passage du banc : un rapport lisible (`.md`) et ses chiffres (`.json`), comparés au passage précédent. |
| `data/profils/<nom>.json` | Les profils d'assureur : B, C et D en ont un ; A est lu par les règles générales. |
| `data/ferme/` | Le jeu fermé (65 cas pour A, B et D) : écrit à partir du seul texte des contrats par deux annotateurs indépendants, arbitré sur citations. Il mesure, il ne sert jamais à corriger (DEMARCHE 7.79). |
| `data/lecture/` | La banque d'exemples de lecture, et le partage du golden set : 74 cas pour mettre au point, 38 pour tester. |
| `tests/fixtures/cg_style_reel.pdf` | Un PDF fictif mis en page comme un vrai contrat (sommaire, en-têtes, lexique, intertitres sans numéro, mots coupés), produit par `generer_pdf.py`. |

**Pourquoi des variations à un seul fait** : si la réponse change quand on passe du local commun à la cave privative fermée à clé, c'est que le système raisonne vraiment sur le contrat, et pas qu'il répète une réponse apprise.

---

## 6. Les tests

`uv run pytest` lance 312 tests (26 nov. 2026, dont un ignoré sous Windows ; le nombre entre parenthèses compte les fonctions de test, dont certaines jouent plusieurs cas), sans appel réel à un modèle : les réponses sont préparées, et une garde commune (`tests/conftest.py`) fait échouer tout appel réseau au fournisseur, pour qu'un réglage du poste ne déclenche jamais d'appel payé (7.204) :
- **`test_pipeline.py` (47)** — lecture et découpage d'un PDF (sommaire, en-têtes, mots coupés, intertitres, lexique éclaté, renvois), contrôles d'ingestion, base, contrôle des citations (une citation inventée fait passer COUVERT à INCERTAIN), configuration du modèle (`.env`, nouvelles tentatives, clé refusée, réponses coupées), profils, journal sans le texte du sinistre, versions des consignes, tableaux Grafana exécutés sur une vraie base ; le contrat réel A si son PDF est présent.
- **`test_prolog.py` (83)** — le moteur : trois valeurs et questions, exclusions partielles, extensions de définition, garanties accessoires, événement non traduit jamais refusé, obligations, questions décisives et paires, arbre de preuve, faits sans injection possible ; la lecture (vocabulaire, deux temps, vérification, un doute ne fait jamais couvrir, confirmation) ; le moteur permanent ; et, si SWI-Prolog est installé, **Prolog et l'oracle Python concordent** sur tous les cas.
- **`test_redaction.py` (57)** — la rédaction : Prolog généré et évalué par l'oracle, chaque contrôle (vocabulaire déclaré, fait inventé, citation réparée ou refusée, exclusion oubliée, réserves, conditions des conditions particulières mises en réserve, accessoires, extensions…), la reprise unique sur un écart au schéma, l'acceptation, la hiérarchie des valeurs.
- **`test_jugement.py` (21)**, **`test_clauses.py` (15)**, **`test_dossier.py` (5)**, **`test_attendu.py` (4)** — la lecture des clauses, avec un modèle factice : les clauses attendues, la composition du dossier, les contrôles et rattrapages d'un jugement, la décision et la contresignature, la relance, les rappels du règlement, une question une seule fois, l'analyse de bout en bout.
- **`test_banc.py` (18)** — le golden set (complet, cohérent, figé), les règles seules justes pour chaque contrat, les trois couches, les portes, la latence, la fiche de validation.
- **`test_api_routes.py` (16)** et **`test_api_service.py` (8)** — les routes par HTTP, dépendances remplacées ; une route par fichier ; le mode en ligne : le code d'accès remplace la clé, le contrat ne se télécharge pas, les analyses sont comptées ; la méthode choisie par requête ; le suivi qui bat pendant une longue étape.
- **`test_exemples.py` (13)**, **`test_fiche.py`**, **`test_tableaux.py`**, **`test_questions.py`**, **`test_ferme.py`** — la banque d'exemples, la fiche PDF, les tableaux Grafana exécutés, les questions posées, le jeu fermé.

---

## 7. L'évaluation et ses indicateurs

Le banc (`couverture banc`) mesure trois couches sur le golden set, avec des portes (`data/golden/seuils.json`) :

| Couche | Ce qu'elle mesure | Portes |
|---|---|---|
| **Règles** | Les règles seules, sur les faits idéaux : exactitude, couverts à tort, refus à tort, rappel des questions attendues, questions par réponse incertaine. | 0 couvert à tort, 0 refus à tort, exactitude ≥ 95 % |
| **Lecture** | Les faits lus par le modèle comparés aux faits idéaux : rappel des faits, contradictions, décisions changées par la lecture (et vers un couvert à tort). | ≤ 2 décisions changées, aucune vers un couvert à tort |
| **Chaîne** | Le système complet, trois exécutions : justes, exactes, couverts à tort, refus à tort, cas instables, rappel des questions, latence (un cas à la fois, au 95e centile). | 0 couvert à tort, exactitude ≥ 85 %, 95e centile ≤ 10 s |

**Couverts à tort** : l'indicateur le plus important, car c'est une promesse faite au client. **Justes** compte aussi les réponses acceptables (un « incertain » défendable) ; **exactes**, seulement la réponse attendue.

**Deux jeux, deux usages.** Le golden set a été écrit en connaissant les règles : il dit que le moteur applique les règles, pas que les règles disent le contrat. Le **jeu fermé** (`data/ferme/`, `couverture banc --jeu ferme`) a été écrit sans les voir : c'est lui qui mesure la fidélité au contrat. À sa première mesure, A est tombé de 90 à 70 % et B de 76 à 57 % (DEMARCHE 7.81). Ses cas ne servent jamais à corriger le vocabulaire, les règles ou les exemples.

**La lecture des clauses se mesure autrement** : `couverture juger --jeu …` rejoue un jeu une fois (le modèle coûte 8 à 10 centimes par cas), et compte justes, couverts à tort, refus à tort et « à préciser » au lieu d'une réponse. **La comparaison qui compte** est celle du jeu « quatre », jamais vu, passé une seule fois par les deux méthodes après le gel du code (26 nov., DEMARCHE 7.207) : chaîne de règles 42 sur 60, 4,3 couverts à tort, 2 refus à tort ; lecture des clauses 45 sur 60, 1 couvert à tort, 4 refus à tort.

**La chaîne de règles, sur ses anciens jeux** (24 nov. 2026 ; détail dans le README, section 4) : avec des faits exacts, les règles sont justes à 100 %. La chaîne complète donne 94 % de réponses justes sur la partie test de A, 98 à 100 % sur son jeu fermé, 85 % sur celui de B, 96 % sur celui de D. Un couvert à tort se répète chez B, un refus à tort chez D, et un cas de A est couvert à tort une fois sur trois certains jours. Toutes ces erreurs viennent de la lecture.

---

## 8. Les choix, résumés

| Choix | Raison | Écarté |
|---|---|---|
| Structurer chaque contrat une fois | Vérifiable, réutilisable, tient à l'échelle | Coller le PDF dans le prompt à chaque question |
| Une clause = une unité du contrat | Citations précises, type connu | Morceaux de taille fixe |
| Lexique éclaté terme par terme | Le sens d'un mot est celui du contrat | Le laisser en un seul bloc |
| Le contrat en règles Prolog, le modèle ne fait que lire | La décision devient un calcul reproductible, traçable jusqu'à la phrase du contrat | Faire décider le modèle (grille, fiches : essayé, retiré) |
| Logique à trois valeurs | « Je ne sais pas » n'est pas « faux » | Le monde clos de Prolog |
| Règles rédigées par Mistral Large, contrôlées par le code, relues par un humain | Tient sur des dizaines de garanties ; aucune règle n'entre sans contrôle | Tout écrire à la main, ou tout laisser au modèle |
| Corriger la méthode, pas le contrat | Une erreur trouvée sur un contrat est corrigée dans la consigne, les contrôles ou le moteur, et sert à tous | Retoucher les règles d'un seul contrat |
| Vocabulaire commun, lu contrat par contrat | Un même fait se lit pareil partout ; un contrat ne lit que ses variables | Un vocabulaire par contrat |
| Accessoires, extensions, réserves distinguées | Trois sens d'« étendre » ; mélangés, ils dégradent des décisions qu'ils ne concernent pas | Tout traduire en garanties ordinaires |
| Un doute ne fait jamais couvrir | Une vérification qui retire un fait ne peut pas rendre la réponse plus favorable | Retirer les faits sans regarder l'effet |
| Un jeu fermé, écrit sans voir les règles | Mesurer la fidélité au contrat, pas l'accord du moteur avec ses propres règles ; il a arrêté une correction la veille de la livraison (7.166) | Corriger sur les cas qui mesurent |
| Un modèle lit, un autre vérifie | Celui qui lit le mieux refuse trop quand il vérifie | Un seul modèle pour tout |
| Golden set figé, banc en trois couches, portes | Savoir si une erreur vient des règles, de la lecture ou de leur combinaison ; une référence qui change le dit | Une exactitude unique, des cas qui bougent |
| Profils d'assureur en JSON | Un assureur différent = un fichier, pas du code | Des cas particuliers dans `segmentation.py` |
| Contrôle des citations par du code | Bloque les hallucinations de façon fiable | Faire confiance au modèle |
| Archiver le texte de chaque version de consigne, garde-fou en CI | Savoir quelle consigne a produit une réponse ; impossible de changer un texte en silence | Prompts modifiés sans trace |
| Un rapport par banc, comparé au précédent de même configuration | Comparer versions et modèles sur un même jeu (même empreinte), sans service de plus | Comparer des chiffres notés à la main |
| Journal sans le texte du sinistre | Mesurer en production sans stocker de données personnelles | Garder les déclarations |
| Grafana sur SQLite, tableaux générés et testés | Pas de base de plus à faire tourner ; requêtes lisibles et vérifiées | PostgreSQL pour une démonstration ; JSON édité à la main |
| Pas de LangGraph | La chaîne est linéaire | Un graphe par habitude |
| Mistral seul, derrière une interface `LLM` | Fournisseur européen ; un autre modèle se branche en une classe | Garder des fournisseurs qu'on ne teste pas |
| En ligne : un code d'accès, le contrat non téléchargeable | Une page ouverte dépenserait le crédit du modèle et publierait le texte de quatre assureurs | Une démonstration publique |
| Lire les clauses du contrat plutôt que seulement ses règles, et faire contresigner par les règles | Une clause que la traduction a manquée peut encore être vue ; sur un jeu jamais vu, quatre fois moins de couverts à tort, à justesse comparable | La chaîne de règles seule (gardée, choisissable) ; laisser le modèle décider du sinistre |
| La décision de la lecture des clauses calculée par le code | Le modèle juge une clause à la fois ; la réponse se recalcule à partir des jugements gardés | Demander au modèle sa conclusion |
| Une mesure unique sur un jeu jamais vu, code figé avant | Un jeu qui a servi à corriger flatte la méthode : l'écart de 48 contre 38 sur « neuf » est devenu 45 contre 42 sur « quatre » | Comparer sur les jeux de mise au point |
| API FastAPI et interface Angular | Restitution claire, sur le modèle de SortirIA ; Streamlit déconseillé par le recruteur | Streamlit |

---

## 9. Les questions qu'on peut vous poser

**Pourquoi ne pas tout confier au modèle ?**
Parce qu'en assurance, une réponse non vérifiable ne vaut rien. Le modèle fait ce qu'il fait bien (lire une déclaration, rédiger une première traduction d'une garantie) ; les règles et les contrôles font ce que le code fait bien (appliquer une logique, vérifier qu'un texte existe).

**Pourquoi pas un RAG ?**
L'exclusion qui décide ne ressemble pas à la question (« vol de vélo » ressemble à « les vélos sont garantis », pas à « vols commis dans les parties communes »). Une recherche par ressemblance la rate. Les règles, elles, rattachent chaque exclusion à sa garantie une fois pour toutes. Une recherche hybride a été essayée, puis retirée (DEMARCHE 7.36).

**Comment tenir des centaines de contrats ?**
Par une méthode, pas par un bouton. Ce qui est commun ne change pas d'un contrat à l'autre : le moteur, la validation des citations, l'API, l'écran. Ce qui est propre à un contrat tient dans quatre fichiers de données. Ses garanties sont rédigées par Mistral Large, contrôlées par le code, relues, puis acceptées. Le quatrième contrat, ajouté à froid, a donné le coût réel : une heure de découpage, onze minutes de rédaction pour deux garanties, 22 contrôles bloquants, et une relecture qui ne se réduit pas (README, section 6). Pour des centaines de contrats, il faut des relecteurs du métier, un outil de relecture et un jeu de mesure par contrat.

**Que fait le système quand il ne sait pas ?**
Il répond INCERTAIN, avec la question qui tranche (« la cave était-elle fermée par une serrure de sûreté ? oui → couvert ; non → non couvert »). Quand seule une option des conditions particulières couvrirait, il répond « à préciser », avec le point à vérifier. Et un événement dont la garantie n'est pas encore traduite n'est jamais refusé : il est envoyé à un gestionnaire.

**Comment savez-vous que les règles sont justes ?**
Je ne le sais pas entièrement, et il faut le dire. Quatre filets existent : les contrôles du code (citations mot pour mot, chaque exclusion du contrat traduite, vocabulaire, chargement), une relecture tracée dans chaque proposition, le banc (les règles seules doivent être justes à 100 % sur les cas), et le jeu fermé, écrit sans voir les règles. Mais la relecture a été faite par l'assistant qui a écrit le code, pas par quelqu'un du métier, et elle s'est trompée au moins une fois. Les règles n'ont été validées ni par un juriste ni par un gestionnaire de sinistres : c'est la première chose à faire.

**Et si la lecture se trompe ?**
C'est la principale source d'erreurs restantes, et elle est mesurée à part (couche « lecture » du banc). Trois défenses : un schéma qui n'admet que les valeurs du vocabulaire, une vérification des faits, et la confirmation des faits qui portent une réponse ferme. Un doute ne fait jamais couvrir.

**Comment comparez-vous deux versions d'une consigne, ou deux modèles ?**
Chaque banc écrit un rapport qui porte le modèle, le mode de lecture et l'empreinte du jeu de cas, et se compare au précédent de même configuration ; le journal note les versions des consignes. Deux bancs avec la même empreinte se comparent directement, sur les couverts à tort d'abord. Une consigne ne peut pas changer sans nouvelle version : la CI échoue.

**Pourquoi deux méthodes, et pourquoi la seconde par défaut ?**
J'ai mené le projet comme une expérience. Ma première hypothèse traduisait chaque contrat en règles : rapide, transparente, mais fausse dès que la traduction l'était, et sur des cas jamais vus elle couvrait parfois à tort. La seconde fait lire au modèle les clauses mêmes, une à une ; je vérifie chaque citation, je calcule la décision et je fais contresigner les « couvert » par la première. Je les ai comparées une seule fois, code figé, sur soixante cas jamais vus : 45 réponses justes contre 42 (un écart que soixante cas ne permettent pas d'affirmer), un couvert à tort contre 4,3. Mon choix tient à l'erreur qui coûte le plus. Ce qu'il coûte, je le dis aussi : deux refus à tort de plus, deux à trois minutes et 8 à 10 centimes par analyse.

**La seconde méthode généralise-t-elle à un nouveau contrat ?**
En principe : elle n'a besoin, pour juger, que du contrat découpé. Mais j'ai fait toutes mes mesures avec la contresignature des règles traduites ; sans elles, sur un contrat nouveau, je n'ai rien mesuré. C'est ma prochaine expérience, pas un résultat que j'annonce.

**Le modèle ne décide-t-il pas, finalement, dans la seconde méthode ?**
Il porte un jugement par clause, oui : c'est plus de pouvoir qu'une simple lecture des faits. Je l'encadre de trois façons : chaque jugement cite deux phrases retrouvées mot pour mot ; la décision se calcule à partir des jugements par une logique fixe ; un « couvert » doit être contresigné. Ce que mon code ne vérifie pas, c'est que la clause citée a un rapport avec le sinistre : deux refus à tort du jeu « quatre » en viennent, et je ne l'avais pas anticipé.

**Pourquoi INCERTAIN est-il une bonne réponse ?**
Parce que c'est la consigne : un « je ne sais pas » étayé vaut mieux qu'une réponse assurée sans justification. Et ici, INCERTAIN dit précisément quoi demander à l'assuré.

**Quel lien avec SortirIA ?**
Le même problème de fond : des sources hétérogènes à ramener dans un schéma commun et fiable. Ce projet en reprend le versionnage des consignes avec garde-fou en CI, le journal et les tableaux Grafana générés et testés. La différence : SortirIA recommande, une approximation reste utile ; ici le système décide, une erreur est une promesse faite au client, d'où la décision calculée, le contrôle des citations et le droit de répondre INCERTAIN.

**Comment avez-vous utilisé l'IA ?**
Pour écrire le code plus vite, comme le recruteur l'encourage, et dans le système lui-même pour lire les déclarations et rédiger les règles. Sa part dans le code est grande, et visible dans chaque commit ; il a aussi relu les règles, ce qui est une limite (voir la question précédente sur leur justesse). Le cadrage, les arbitrages et les décisions restent les vôtres : mesurer avant de corriger, « pas de rustine », ne jamais corriger sur le jeu fermé. Vous devez pouvoir expliquer chaque fichier de ce document, et raconter les onze tournants de la démarche sans notes.

---

## 10. Limites et suites

**Limites actuelles** (23 nov. 2026, complétées le 26 ; la liste complète et tenue à jour est dans le README, section 7)
- La lecture des clauses : deux à trois minutes et 8 à 10 centimes par analyse ; plus de refus à tort que la chaîne de règles ; une même déclaration ne reçoit pas toujours deux fois la même réponse ; jamais mesurée sans la contresignature des règles (DEMARCHE 7.207, 7.208).
- Les règles n'ont pas été relues par un juriste ou un gestionnaire de sinistres, et les jeux de cas viennent de ceux qui ont écrit ou relu les règles.
- La lecture des déclarations reste la principale source d'erreurs, et elle varie d'un appel à l'autre ; les chiffres du jour sont dans le README, section 4.
- Chaque nouveau contrat demande une rédaction, non reproductible d'un essai à l'autre, puis une relecture humaine (README, section 6).
- Les conditions particulières ne sont pas lues dans le document du client : la formule et les options se saisissent avec la déclaration.
- Le contrat C est partiel et n'a pas de jeu de mesure.
- Le découpage repose sur des règles et des profils ; un format très inhabituel dépassera ce qu'un profil peut décrire.
- Les tableaux de plafonds sont lus comme du texte : les montants sont cités, pas calculés.
- En ligne : pas d'utilisateurs réels, un compteur d'analyses qui repart de zéro à chaque réveil, et un journal lisible dans les journaux de l'hébergeur, sans tableau de bord.

**Suites, dans l'ordre**
0. Mesurer la lecture des clauses sans contresignature, sur un contrat sans règles traduites, avec un jeu neuf ; puis réduire ses refus à tort et son temps.
1. Faire relire les règles d'un contrat par quelqu'un du métier, et mesurer sur ses propres cas.
2. Un jeu de cas écrit sans voir les règles, pour chaque contrat ; un jeu de mesure pour C.
3. La lecture : les erreurs restantes, une par une, comme pour les règles.
4. Lire les conditions particulières dans le document du client.
5. En ligne : relever les journaux dans un tableau de bord, et le coût par analyse.
