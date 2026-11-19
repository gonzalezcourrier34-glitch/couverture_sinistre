# Comprendre le projet, fichier par fichier

> **Une seule méthode depuis le 18 nov. 2026.** Les premières méthodes (grille remplie par le modèle et relue, recherche hybride, fiches compilées, juge de qualité, agent de réparation, dérive et bilan) ont été retirées : les règles Prolog les ont remplacées. Pourquoi, et ce qu'elles ont appris : [DEMARCHE.md](DEMARCHE.md), 7.36. Leurs consignes restent archivées dans `docs/consignes/`, et leur code dans l'historique git (tag `avant-simplification`). Ce document décrit le projet tel qu'il est.
>
> **Noms anonymisés (19 nov. 2026).** Les assureurs s'appellent ici Assureur A, B, C et D (DEMARCHE 7.70).

Ce document explique **ce que fait chaque partie du projet, et pourquoi elle est faite ainsi**. Il sert à préparer l'entretien : pour chaque choix, il donne la raison et ce qui a été écarté.

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
| **Conditions particulières (CP)** | Le document propre à chaque client : son adresse, les garanties et options qu'il a souscrites, ses capitaux, ses franchises. Non publiques ; pas encore lues par le système. |
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
| **Starlette / Uvicorn** | Un petit framework web Python et le serveur qui le fait tourner. |
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
| **Vocabulaire** | `regles/vocabulaire.json` : les variables communes à tous les contrats (événement, bien, lieu, fermeture…), leurs valeurs, la question à poser quand elles manquent, une aide de lecture par valeur, et la hiérarchie des valeurs (un vélo est un bien du contenu). |
| **Faits** | Ce que la lecture tire de la déclaration, dans le vocabulaire : `evenement = vol`, `lieu = cave`. Ce qu'elle ne dit pas reste inconnu. |
| **Règles d'un contrat** | `regles/<contrat>.pl` : pour chaque garantie, son périmètre, ses circonstances, ses obligations, ses exclusions et ses limites, chacune avec la phrase du contrat qu'elle traduit. |
| **Périmètre** | Ce qui fait qu'une garantie concerne le sinistre (événement, bien, lieu). Hors du périmètre, la garantie ne dit rien. |
| **Réserve** | Une exclusion inconnue que la déclaration n'évoque pas : la réponse est « couvert, sous réserve de… », sans question. Les options des conditions particulières sont des réserves. |
| **Exclusion entamée** | Une exclusion inconnue dont un fait est établi (des travaux sont mentionnés) : la question est posée. |
| **Garantie accessoire** | Une garantie qui ne joue qu'après un sinistre couvert (frais de sauvetage, logement provisoire). Elle ne change jamais la décision ; si c'est couvert, elle est listée. |
| **Extension de définition** | Une clause qui élargit un lieu ou un bien assuré (le contenu en séjour temporaire) : elle élargit la définition du contrat, pour toutes les garanties. |
| **Événement non traduit** | Un événement dont aucune garantie n'est encore en règles : le moteur ne refuse jamais, il répond « à examiner ». |
| **Rédaction** | Mistral Large traduit une garantie en règles (un JSON, que le code écrit en Prolog) ; le code contrôle, un humain relit, puis accepte. |
| **Proposition** | Une rédaction en attente dans `regles/propositions/<contrat>/`, avec ses contrôles. |
| **Relecture** | Les corrections de l'auteur sur une proposition, écrites dans un script versionné (`relecture/`) et tracées dans la proposition. |
| **Arbre de preuve** | La trace de la déduction : chaque condition évaluée, sa phrase du contrat, son état, jusqu'aux faits déclarés. |
| **Question décisive** | Une question dont la réponse tranche (« oui → couvert ; non → non couvert »), trouvée par le moteur en essayant chaque réponse. |
| **Verdict** | La réponse : décision, justification, citations, ce qu'il faut vérifier, confiance. |
| **COUVERT / NON_COUVERT / INCERTAIN** | Les trois décisions possibles. INCERTAIN est une vraie réponse, accompagnée de ce qu'il faut vérifier. |
| **Faux « couvert »** | Le système dit « couvert » alors que ce n'est pas le cas. L'erreur la plus grave : c'est une promesse faite au client. |
| **Document brut** | La méthode de référence : le contrat entier collé dans le prompt, comme dans un chatbot. |
| **Profil d'assureur** | Les règles de lecture propres à un assureur (ses intertitres et leur type, ses lignes de bruit, le format de son lexique), dans un fichier JSON. |
| **Golden set** | 112 cas étiquetés (97 pour l'assureur A, 15 pour l'assureur B), figés et versionnés, sur lesquels le banc rejoue tout le système. |
| **Banc, couches, portes** | Le banc rejoue le golden set en trois couches (règles seules, lecture, chaîne) ; les portes (`data/golden/seuils.json`) disent si c'est présentable. |
| **Confirmation** | Avant une réponse ferme, le modèle confirme que les faits qui la portent sont bien écrits dans la déclaration ; sinon, la réponse devient INCERTAIN. |
| **Journal** | La table `analyses` : chaque question posée au système et sa réponse, sans le texte du sinistre. |
| **MLflow** | Un outil pour suivre des expériences : chaque exécution garde ses paramètres, ses métriques et ses fichiers. Son **Prompt Registry** garde les versions des consignes. |
| **Exécution** (*run*) | Une ingestion ou un banc enregistré dans MLflow. |
| **Consigne** (*prompt*) | Le texte d'instructions envoyé au modèle. Le projet n'entraîne pas de modèle : ce qui change d'une version à l'autre, ce sont les consignes. |
| **Manifeste des consignes** | `config/versions_consignes.json` : la version et l'empreinte de chaque consigne. Sert de garde-fou en CI. |
| **Grafana** | Un outil de tableaux de bord qui lit une base et affiche des graphiques. Ici, il lit la base SQLite du projet. |
| **CI** (intégration continue) | Les tests lancés automatiquement à chaque envoi du code (GitHub Actions). |
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

---

## 3. Le parcours complet d'un sinistre

### A. Une fois par contrat

```
PDF ─► chargement.py ─► segmentation.py ─► controles.py ─► base.py (SQLite)
       pages, nettoyage   clauses typées     OK / A_VERIFIER   contrats, clauses, renvois
                          (+ profil d'assureur)

garanties ─► règles Prolog (regles/<contrat>.pl) : à la main, ou `couverture rediger` (Mistral Large)
          ─► contrôles : citations dans le contrat, mots dans le vocabulaire, chargement, banc
```

Sur le contrat Assureur A Habitation A : 48 pages deviennent 147 clauses, dont 63 définitions. Statut `OK`.

### B. À chaque sinistre (`couverture analyser` ou l'interface)

Exemple : « Mon vélo a été volé dans ma cave, fermée par un cadenas. »

1. **Lecture** (`prolog.py`) : Mistral traduit la déclaration en faits du vocabulaire : `evenement = vol`, `bien = velo`, `lieu = cave`, `fermeture = cadenas`. Les valeurs hors vocabulaire et les faits hors sujet sont retirés.
2. **Décision** (`regles/moteur.pl`) : la garantie « vol du contenu dans le bâtiment » a son périmètre établi, mais sa condition « si ces locaux sont fermés avec une serrure de sûreté » est fausse : un cadenas n'est pas une serrure de sûreté (définition, art. 12). → **NON_COUVERT**.
3. **Hypothèses** : si la réponse avait été incertaine (fermeture inconnue), le moteur aurait essayé chaque réponse et dit « serrure de sûreté ? oui → couvert ; non → non couvert ».
4. **Arbre de preuve** : chaque condition évaluée, sa phrase du contrat, son état, jusqu'au fait déclaré `fermeture = cadenas`.
5. **Vérification** : chaque citation est recherchée dans la clause du contrat.
6. **Journal** : l'analyse est notée (décision, faits, questions), sans le texte du sinistre.

---

## 4. Les fichiers, un par un

L'ordre suit le parcours des données.

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

### `src/couverture/chargement.py` — lire et nettoyer le PDF

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

### `src/couverture/segmentation.py` — découper en clauses typées

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

### `src/couverture/controles.py` — repérer les contrats mal lus

**Rôle** : `controler` produit un rapport et un statut, `OK` ou `A_VERIFIER`. Alertes :
- moins de 15 clauses (le découpage a probablement échoué) ;
- plus de 40 % de clauses sans type (titres non reconnus) ;
- aucune garantie, aucune exclusion ou aucune définition détectée ;
- pas d'exclusions générales repérées ;
- trop de renvois vers des clauses introuvables (plus de 3, ou plus de 5 % des clauses).

Le rapport liste aussi les garanties sans exclusion voisine et les clauses très longues.

**Pourquoi** : avec des centaines de contrats, personne ne relit chaque découpage. Un contrat mal lu doit être signalé, pas servi en silence. Exemple : « un contrat sans exclusion n'existe pas » ; si on n'en trouve aucune, c'est la lecture qui a échoué.

### `src/couverture/profils.py` — les règles propres à un assureur

**Rôle** : un profil est un fichier JSON dans `data/profils/<nom>.json`, désigné dans le catalogue (`"profil": "assureur-a"`). Il contient :
- `intertitres` : des titres propres à l'assureur et leur type (« Les situations hors contrat » → exclusion). La segmentation les reconnaît comme intertitres, et `classer` leur donne ce type en priorité ;
- `lignes_ignorees` : des expressions régulières pour les lignes de bruit que le nettoyage n'a pas vues (une référence de document répétée…) ;
- `lexique` : le format des définitions (`deux_points`, `terme_seul`, ou `auto`).

`valider_profil` refuse un type inconnu, une expression invalide, un nom mal formé. `charger_profil` le lit.

**Pourquoi** : les règles générales couvrent la plupart des contrats. Quand un assureur rédige autrement, on n'ajoute pas un cas particulier dans le code : on écrit un profil, réutilisé pour toutes les versions de ses contrats. C'est ce qui rend l'approche tenable sur des centaines de contrats, comme `sources.yaml` dans SortirIA pour les agendas.

### `src/couverture/base.py` — le stockage multi-contrats

**Rôle** : une base SQLite avec trois tables.
- `contrats` : identifiant, assureur, produit, version, fichier, empreinte, statut, rapport des contrôles, texte brut, date d'ingestion.
- `clauses` : toutes les clauses de tous les contrats, avec le contrat auquel elles appartiennent, leur ordre, leur groupe, leur type, leurs pages.
- `renvois` : les liens d'une clause vers une autre.

Méthodes : `enregistrer` (remplace entièrement un contrat), `contrats`, `contrat`, `clauses(contrat_id)`, `texte_brut`, `empreinte`.

**Pourquoi** : chaque contrat est lu une fois, et chaque question ne charge **que les clauses du contrat concerné**. On ne mélange jamais deux contrats. SQLite suffit pour des centaines de contrats et ne demande aucun serveur. En production, ce serait PostgreSQL, avec le même schéma.

### `src/couverture/ingestion.py` — de fichier à base

**Rôle** :
- `ingerer_fichier` : calcule l'empreinte du fichier ; s'il n'a pas changé depuis la dernière fois, ne fait rien (idempotence) ; sinon lit, découpe, contrôle et enregistre.
- `ingerer_dossier` : fait de même pour tous les fichiers de `data/contrats`, avec les métadonnées de `catalogue.json` (identifiant, assureur, produit, version, et le **profil d'assureur** s'il y en a un). Sans entrée au catalogue, l'identifiant est tiré du nom du fichier.
- **L'empreinte** couvre le fichier **et** son profil : modifier le profil relance le découpage.

**Pourquoi** : ajouter un contrat se résume à déposer un fichier et relancer `couverture ingerer`. La version du contrat compte : un client garde les CG en vigueur au moment de sa souscription.

### `src/couverture/llm.py` — parler au modèle

**Rôle** : trois clients, sans bibliothèque externe (de simples appels HTTP), qui respectent tous le même protocole `LLM` : une méthode `completer(systeme, message)`.
- `MistralLLM` (par défaut) : l'API de Mistral, `https://api.mistral.ai/v1`. Clé dans `MISTRAL_API_KEY`, modèle `mistral-large-latest` sauf si `COUVERTURE_MODELE` dit autre chose. Le **mode JSON** de Mistral est activé (`response_format`) : le serveur garantit une réponse JSON valide, ce qui évite les réponses illisibles.
- `AnthropicLLM` : l'API d'Anthropic, clé dans `ANTHROPIC_API_KEY`.
- `OpenAICompatibleLLM` : toute API compatible OpenAI (Ollama en local, vLLM, Azure…), adresse dans `COUVERTURE_LLM_URL`. `MistralLLM` en est une variante, puisque l'API de Mistral est compatible OpenAI.

`configurer()` choisit le fournisseur : celui forcé par `COUVERTURE_FOURNISSEUR`, sinon le premier dont la clé est renseignée, dans l'ordre Mistral, Anthropic, compatible OpenAI. Une valeur d'exemple laissée telle quelle (« colle-ta-cle-ici ») est ignorée. Sans rien, il renvoie `None`, et l'analyse demande de configurer une clé.

`_poster` envoie les requêtes avec **de nouvelles tentatives** sur les erreurs passagères : 429 (limite de débit atteinte) et erreurs serveur 5xx, en attendant de plus en plus longtemps (ou le délai indiqué par le serveur). Une clé refusée (401, 403) donne un message clair : « Clé API refusée, vérifier la clé dans le fichier .env ». Ces erreurs (`ErreurLLM`) remontent jusqu'à l'utilisateur au lieu d'être confondues avec une réponse illisible du modèle.

Température 0 partout, pour des réponses stables d'une exécution à l'autre.

**Réponses JSON** : `extraire_json` récupère l'objet JSON même entouré de texte ; `appeler_json` redemande une fois une réponse coupée ou illisible ; `pour_travail_long` donne plus de temps et de tokens au travail fait une fois par contrat (rédaction des règles).

**Pourquoi Mistral par défaut** : fournisseur européen, données hébergées dans l'UE, ce qui compte pour un assureur luxembourgeois qui traite des données clients. Contexte long (suffisant pour la méthode « document brut »), prix faible, API compatible OpenAI. **Pourquoi plusieurs fournisseurs** : changer de modèle ne doit rien changer au reste, et un assureur voudra souvent un modèle hébergé chez lui.

### `src/couverture/config.py` — les clés hors du code

**Rôle** : `charger_env` lit le fichier `.env` à la racine du projet et place ses valeurs dans l'environnement, **sans écraser** une variable déjà définie. Il gère les commentaires, les guillemets et le préfixe `export`. Appelé au démarrage de chaque commande.

**Pourquoi** : une clé API ne doit jamais être écrite dans le code ni versionnée. `.env` est dans le `.gitignore`. Son contenu minimal :

```
MISTRAL_API_KEY=colle-ta-cle-ici
COUVERTURE_MODELE=mistral-large-latest
```

`mistral-small-latest` coûte moins cher. Pour un autre fournisseur : `ANTHROPIC_API_KEY=…`, ou `COUVERTURE_LLM_URL=http://localhost:11434/v1` pour Ollama, et `COUVERTURE_FOURNISSEUR=…` pour forcer le choix si plusieurs sont renseignés. En déploiement, les mêmes variables sont passées au conteneur (`docker run --env-file .env`).

### `src/couverture/juges.py` et `pipeline.py` — la référence « document brut »

**Rôle** : `JugeDocumentBrut` met le contrat entier dans le prompt, comme un chatbot ; `PipelineDocumentBrut` contrôle ses citations de la même façon que pour les règles, pour que la comparaison soit juste (`verdict.decision_initiale` garde la réponse non contrôlée). `pipeline.llm_configure` choisit le modèle selon l'environnement.

**Pourquoi** : c'est la méthode à battre ; `couverture banc --methode brut` la mesure sur le même golden set.

### `regles/` et `src/couverture/prolog.py` — le contrat en règles Prolog (méthode `regles`)

**Rôle** : le contrat est écrit en **règles**, un moteur logique décide, et le modèle ne fait que lire les faits de la déclaration.
- `regles/vocabulaire.json` : les variables communes à tous les contrats (événement, bien, lieu, fermeture, serrure de sûreté, effraction, violence, flammes, embrasement…), leurs valeurs permises et la question à poser quand elles manquent ;
- `regles/moteur.pl` : le moteur, commun à tous les contrats. Logique à **trois valeurs** (oui, non, inconnu), pour ne pas confondre « je ne sais pas » avec « faux » (le monde clos de Prolog). Il applique les règles de gestionnaire (périmètre, circonstances, exclusions, obligations avec lien causal, charge de la preuve, exclusions partielles) et combine les garanties ;
- `regles/<contrat>.pl` : les règles d'un contrat, sous forme de données (`definition`, `garantie`, `perimetre`, `circonstance`, `obligation`, `exclusion`, `limite`), chacune avec la phrase du contrat qu'elle traduit ;
- `regles/cas/<contrat>.jsonl` : les faits « idéaux » de chaque sinistre de test, pour éprouver les règles sans modèle ;
- `prolog.py` : trouve SWI-Prolog, lui fait charger le moteur et les règles, pose les faits (vérifiés : rien ne peut être injecté), lit la décision en JSON ; `extraire_faits_regles` fait lire la déclaration par le modèle, dans le vocabulaire, en laissant inconnu ce qu'elle ne dit pas ; `PipelineRegles` assemble et met en forme ;
- `couverture regles --contrat <id>` : vérifie le chargement sans avertissement, le vocabulaire, les citations (mot pour mot dans les clauses), et les cas.
- **Raisonnement par hypothèses** (`explorer/2` dans `moteur.pl`) : quand la décision dépend de faits inconnus, le moteur essaie chaque réponse possible (assertz, décision, retract) et classe chaque question : décisive (« oui → couvert ; non → non couvert »), utile, ou inutile (plus posée) ; sans question décisive, il cherche une paire qui tranche. Les valeurs possibles viennent de `vocabulaire.json`. L'oracle Python (`Explorateur`) refait le même calcul pour le test différentiel ;
- **Arbre de preuve** (`arbres_de_preuve/2` dans `moteur.pl`) : pour chaque garantie retenue, l'arbre de ce que le moteur a évalué — périmètre, conditions, obligations, exclusions —, chaque nœud avec sa phrase du contrat et son état (oui, non, inconnu), jusqu'aux faits déclarés. Il est recalculé avec le même `eval/2` que la décision : c'est la trace de la déduction, pas une explication écrite après coup. `arbre_lisible` (prolog.py) l'élague pour la lecture (la branche vraie d'un « ou », les branches fausses d'un « et », les exclusions qui ne jouent pas sont comptées) ; l'oracle Python refait le même arbre pour le test différentiel ;
- `regles/<contrat>.pl` déclare aussi `evenement_traduit(...)` : un événement déclaré dont la garantie n'est pas encore traduite (la tempête, par exemple) empêche le moteur de refuser, il répond « à examiner » ;
- `src/couverture/redaction.py` (`couverture rediger --article 2.2`, plusieurs articles en parallèle) : **Mistral Large rédige les règles d'une garantie**. Il remplit un schéma JSON (le code écrit le Prolog), déclare les faits qui manquent au vocabulaire (avec leur question, leur aide de lecture et la valeur dont ils précisent le sens), ce qu'il ne sait pas traduire (`non_traduit`, bloquant) et ce qui ne change pas la décision (`hors_decision`, cité). Le code remet en forme ce qu'il sait corriger (une condition rendue sans citation, une condition des conditions particulières mise en réserve), puis contrôle : structure, vocabulaire, citations (mot pour mot, rattachées à la bonne clause), couverture de chaque exclusion du contrat, réserves (« à l'exception de »), limites qui posent une condition, portée des exclusions, définition de l'événement couvert, concepts et identifiants, chargement par SWI-Prolog et non-régression sur les cas. Les propositions restent dans `regles/propositions/` jusqu'à `--accepter`, refusé tant qu'un contrôle bloque ; `--accepter-vocabulaire` ajoute les faits nouveaux après lecture ;
- **trois façons d'étendre une garantie**, distinguées par le moteur : une garantie **accessoire** (`accessoire/1` : frais après un sinistre couvert, jamais dans la décision), une **extension de définition** (`extension/4` : le contenu en séjour temporaire élargit le bâtiment, pour toutes les garanties), et une **réserve** (une option des conditions particulières : « couvert, sous réserve que… »). DEMARCHE 7.68 et 7.69.

**Pourquoi** : la première méthode (des fiches de questions) ne savait pas représenter une condition cachée dans un tableau de limites ni une exclusion cachée dans une définition ; une règle les exprime directement. La décision devient un calcul reproductible. Les tests utilisent aussi `tests/moteur_reference.py`, une seconde implémentation du moteur en Python : là où SWI-Prolog est installé, un test vérifie que les deux concordent.

**La lecture** (`extraire_faits_regles`, mode `verifiee` par défaut) : en deux temps, puis vérifiée. Les deux temps : d'abord l'événement, le bien et le lieu ; puis seulement les questions qui concernent cet événement, avec ce qui est déjà établi. Chaque appel envoie un **schéma JSON** qui n'admet que les valeurs du vocabulaire (`schema_faits`), sans rendre aucune variable obligatoire. `COUVERTURE_LECTURE=un_temps` ou `en_parallele` donnent les lectures essayées et écartées, pour comparer (DEMARCHE 7.38 à 7.42). `COUVERTURE_LECTURE=verifiee` ajoute une vérification : chaque fait du temps 2 est soumis au modèle comme une affirmation, et un fait « non dit » redevient inconnu (7.43) ; si retirer ces faits ferait passer la décision à « couvert », le moteur garde la lecture non vérifiée : un doute ne fait jamais couvrir (7.44). Enfin, avant toute réponse ferme, le moteur désigne les faits qui la portent (`faits_decisifs`) et le modèle confirme qu'ils sont écrits ; un seul « non dit » et la réponse devient « incertain », avec la question (`PipelineRegles.confirmer`, 7.49).

**Le moteur chargé une fois** (`MoteurPermanent`) : un SWI-Prolog par contrat reste ouvert ; Python lui envoie les faits sur une ligne, il répond une ligne JSON (`servir` dans `moteur.pl`). Il est relancé s'il s'arrête ou si les règles changent sur le disque. `COUVERTURE_PROLOG_PERMANENT=non` revient à un processus par décision (DEMARCHE 7.46).

### `src/couverture/banc.py` et `data/golden/` — le banc d'essai

**Rôle** : rejouer tout le système sur un jeu de référence figé (le *golden set* : 112 cas sur deux contrats, étiquetés par garantie, thème, origine et auteur), en trois couches : les **règles** seules sur les faits idéaux, la **lecture** des faits par le modèle comparée aux faits idéaux, la **chaîne** complète sur plusieurs exécutions. Des **portes** (`data/golden/seuils.json`) disent si c'est présentable ; la commande `couverture banc` sort en erreur si une porte échoue. Chaque passage est gardé dans `data/bancs/` et comparé au précédent. `--figer` versionne le golden set ; `--fiche` écrit la fiche de validation des réponses attendues.

**Pourquoi** : un score unique dit qu'il y a une erreur ; trois couches disent si elle vient des règles, de la lecture ou de leur combinaison. Et une référence qui change sans le dire ne mesure plus rien.

### `src/couverture/legalbench.py` — le second banc, externe

**Rôle** : LegalBench (`insurance_policy_interpretation`, Stanford, CC BY 4.0) : une clause en anglais, un sinistre, et la réponse de lecteurs (couvert, non couvert, ambigu). Le modèle répond et cite la phrase de la clause ; le code vérifie la citation ; une réponse ferme sans citation retrouvée devient « incertain ». Le rapport compare la réponse brute et la réponse contrôlée (exactitude, exactitude équilibrée, rappel des ambigus, couverts à tort).

**Pourquoi** : des cas que nous n'avons pas écrits, avec une réponse « ambigu » : une mesure externe du « je ne sais pas ».

### `src/couverture/journal.py` — le journal des analyses

**Rôle** : chaque analyse faite par l'interface ou par `couverture analyser` est notée dans la table `analyses` : date, contrat, méthode, décision (avant contrôle et finale), confiance, faits repérés (événement, bien, lieu), citations rejetées, questions à poser, durée, versions des consignes. Les erreurs du modèle sont notées aussi. Les colonnes `decision_avant_relecture`, `conditions_ecartees` et `contestations` viennent des méthodes retirées ; elles restent dans le schéma pour les bases existantes et les tableaux Grafana.

**Ce qui n'est pas noté** : le texte du sinistre, seulement sa longueur. Une déclaration de sinistre peut contenir des données personnelles ; le journal n'en a pas besoin.

**Pourquoi** : le banc mesure le système sur des cas écrits à l'avance ; le journal mesure ce qui se passe vraiment (comme `search_log.py` dans SortirIA).

### `src/couverture/consignes.py` — le versionnage des consignes

**Rôle** : `CONSIGNES` liste les sept consignes en service (lecture des faits en un temps, lecture en deux temps : socle puis détails, vérification des faits, rédaction des règles, document brut, LegalBench), le texte qui porte chacune dans le code, et sa version.
- **archive** : `ecrire_manifeste` écrit aussi le texte intégral de chaque nouvelle version dans `docs/consignes/<consigne>/<version>.txt`, sans jamais réécrire une version archivée. `verifier` échoue si le texte d'une version en service ne correspond plus à son archive. L'histoire des consignes (rédaction des règles v1 à v9, et celles des méthodes retirées) reste ainsi lisible, avec le pourquoi de chaque changement dans `docs/DEMARCHE.md` ;
- `etat_actuel` calcule la version et l'empreinte de chaque texte ; `ecrire_manifeste` les écrit dans `config/versions_consignes.json` ;
- `verifier` compare le code au manifeste et signale un texte modifié **sans nouvelle version**, ou un manifeste pas à jour. Un test l'appelle : la CI échoue ;
- `versions_courtes` (« faits-regles:v4,redaction-regles:v9… ») est notée dans le journal à chaque analyse et dans chaque exécution MLflow ;
- `enregistrer_dans_mlflow` crée une version au **Prompt Registry** de MLflow pour chaque texte différent, et pose l'alias `production` sur celle en service. Relancé sans changement, il ne crée rien.

**Pourquoi** : une consigne modifiée change les réponses. Pour comparer deux versions, ou comprendre une réponse passée, il faut savoir quelle consigne l'a produite. C'est la même règle que SortirIA (`scripts/versionnage.py`).

### `src/couverture/suivi.py` — le suivi MLflow

**Rôle** :
- **une ingestion = une exécution** (expérience `couverture-ingestion`) : par contrat, le nombre de clauses par type, les alertes, le statut ; artefact : les rapports de contrôle ;
- **un banc = une exécution** (expérience `couverture-evaluation`) : contrat, méthode, modèle de lecture, versions des consignes, version du golden set ; les métriques de chaque couche (`regles/exactitude`, `chaine/faux_couverts`…).

Les fonctions qui calculent paramètres et métriques sont pures et testées sans MLflow. `execution` ouvre une exécution et renvoie un objet dont les méthodes **ne lèvent jamais** : sans MLflow, avec `MLFLOW_ACTIF=false`, avec un serveur qui ne répond pas en 3 s, ou en cas d'erreur, le travail continue sans suivi.

**Pourquoi** : c'est ce qui rend les comparaisons sérieuses. Deux exécutions avec la même empreinte de jeu de test et deux versions de consigne différentes se comparent directement ; deux modèles aussi. Et l'empreinte du jeu de test empêche de comparer des chiffres obtenus sur des cas différents.

### `monitoring/grafana/` — les tableaux de bord

**Rôle** : `construire_tableaux.py` écrit les deux tableaux en JSON, dans `provisioning/dashboards/`, chargés automatiquement par Grafana avec la source SQLite (`provisioning/datasources/sqlite.yml`).
- **Réponses** : usage, décisions par jour, part d'INCERTAIN, rattrapages par jour (réponses corrigées par le contrôle des citations, preuves écartées), temps de réponse, INCERTAIN par contrat, sinistres déclarés, questions à poser les plus fréquentes, versions des consignes en service avec leurs résultats, dernières erreurs ;
- **Contrats** : lecture de chaque contrat, clauses par type, alertes.

Les requêtes utilisent les macros de période du plugin (`$__unixEpochFrom()`, `$__unixEpochTo()`) et les fonctions JSON de SQLite (`json_each`, `json_extract`) pour lire les rapports et les questions.

**Pourquoi un générateur** : un tableau Grafana est un JSON illisible ; ici les requêtes sont écrites en clair, et un test les exécute toutes sur une vraie base et vérifie que le JSON est à jour (même méthode que `construire_tableau_modeles.py` dans SortirIA). **Pourquoi SQLite** : garder le projet petit ; avec PostgreSQL, comme dans SortirIA, seules la source et quelques fonctions changeraient.

### `docker-compose.yml` et `.github/workflows/ci.yml`

- **docker compose** lance l'application (ports 8020), MLflow (5010) et Grafana (3011). L'application lit les contrats au démarrage puis sert l'interface ; la base `data/base.sqlite` est partagée avec Grafana, en lecture seule. Les ports évitent ceux de SortirIA.
- **La CI** installe SWI-Prolog et le projet (avec uv), vérifie les versions des consignes, puis lance les tests : le moteur Prolog y est comparé à l'oracle Python.

Le détail est dans `monitoring/README.md`.

### `src/couverture/validation.py` — aucune décision sans preuve

**Rôle** :
- `extrait_present` : vérifie qu'un extrait figure dans une clause, à la ponctuation, aux accents et à la casse près. Les coupures « … » sont acceptées : chaque morceau doit être présent.
- `valider` : appliqué à tous les verdicts.
  - une citation d'une clause non fournie, ou introuvable, est marquée rejetée ;
  - le **rôle** d'une citation (garantie, exclusion…) est repris du contrat, pas de ce que dit le modèle ;
  - COUVERT sans aucune garantie citée correctement devient INCERTAIN ;
  - une décision ferme sans aucune citation valide devient INCERTAIN ;
  - INCERTAIN doit toujours dire quoi vérifier ;
  - la décision d'origine est gardée dans `decision_initiale`.
  - Option `relocaliser` (pour le document brut) : le modèle ne connaît pas nos identifiants, on cherche donc son extrait dans toutes les clauses.

**Pourquoi** : c'est le garde-fou contre les hallucinations, fait par du code, donc fiable. En gardant la décision d'origine, on peut mesurer combien de fois le contrôle a rattrapé le modèle.

### `src/couverture/evaluation.py` — les jeux de cas

**Rôle** : `charger_cas` croise les sinistres et les réponses attendues ; `evaluer` rejoue une chaîne sur un jeu (le banc s'en sert pour sa couche « chaîne »). Une clause attendue « 4.4 » est considérée comme citée si la clause 4.4 ou l'un de ses morceaux l'est.

### `src/couverture/cli.py` — la ligne de commande

| Commande | Effet |
|---|---|
| `couverture ingerer [--forcer]` | Lit `data/contrats`, remplit la base ; affiche statuts et alertes. |
| `couverture contrats` / `clauses --contrat ID` | Liste les contrats ; affiche le découpage d'un contrat. |
| `couverture regles --contrat ID [--faits JSON] [--jeu …]` | Vérifie les règles (chargement, vocabulaire, citations, cas) ; avec `--faits`, décide un cas et montre l'arbre de preuve. Sans modèle. |
| `couverture rediger --contrat ID --article 2.2` | Mistral Large rédige les règles d'une garantie ; le code les contrôle ; `--accepter` les ajoute. |
| `couverture analyser --contrat ID "…" [--methode regles\|brut] [--detail] [--json]` | Analyse un sinistre : décision, motif, preuves, questions, arbre de preuve. |
| `couverture banc --contrat ID [--methode brut] [--couches …]` | Le golden set rejoué : règles, lecture, chaîne ; portes ; rapport dans `data/bancs/` et exécution MLflow. |
| `couverture legalbench [--telecharger] [--limite N]` | Le second banc, externe (LegalBench). |
| `couverture serveur [--port 8000]` | Lance l'interface web. |
| `couverture versions [--manifeste \| --enregistrer]` | Vérifie les versions des consignes ; réécrit le manifeste ; les enregistre dans MLflow. |
| `couverture modele` | Affiche le modèle configuré et teste la connexion. |

### `src/couverture/web.py` et `static/index.html` — l'interface

**L'API** (Starlette) :
- `GET /` : la page ;
- `GET /api/contrats` : contrats, statut, alertes, et le modèle configuré ;
- `GET /api/contrats/{id}/clauses` : toutes les clauses, pour afficher leur texte complet ;
- `POST /api/analyser` : `{contrat_id, sinistre, methode}` → le résultat complet. Chaque analyse est notée dans le journal. La description doit faire entre 10 et 2 000 caractères. Les pipelines sont gardés en mémoire par contrat et par méthode.

**La page** (HTML et JavaScript sans framework) :
- choix du contrat (avec un avertissement s'il est `A_VERIFIER`), de la méthode (règles Prolog ou document brut), description du sinistre, boutons d'exemple avec les deux cas du recruteur ;
- résultat : la décision en grand avec la confiance, la justification, et un message si le contrôle a corrigé le modèle ;
- **les vérifications qui ont compté** : chaque garantie, condition, exclusion ou limite, avec un état coloré (« Remplie », « Non remplie », « Inconnu » ; pour une exclusion, « S'applique » ou « Ne s'applique pas »), l'extrait avec l'article et la page, et le texte complet de la clause avec le passage surligné ;
- « Ce que le contrat ne permet pas de trancher » : les questions à poser et les réserves ;
- l'arbre de preuve du moteur Prolog, dans un bloc dépliable ;
- « Comment la réponse a été construite » : chaque clause lue, et les avertissements.

Le contenu est inséré comme du texte, jamais comme du HTML, pour éviter qu'un contenu malveillant s'exécute dans la page.

**Pourquoi** : le recruteur demande une restitution claire et déconseille Streamlit. L'interface montre exactement ce qu'il veut voir : les sources, et les limites.

### `src/couverture/__init__.py`

Expose `Resultat`, `Verdict`, `Decision` pour un usage en Python, et la version du paquet.

### Fichiers à la racine

| Fichier | Rôle |
|---|---|
| `pyproject.toml`, `uv.lock` | Le paquet Python : dépendances (pydantic, pdfplumber, starlette, uvicorn), la commande `couverture`, la configuration de pytest ; les versions exactes, installées avec `uv sync`. |
| `relecture/` | Les scripts de relecture humaine de chaque lot de propositions : la trace de ce que l'auteur a changé, et pourquoi. Ils ont servi une fois. |
| `perso/` | Les fichiers de l'auteur, non versionnés. |
| `Dockerfile` | Construit une image qui installe le paquet, ingère les contrats et lance le serveur. La clé du modèle est passée au lancement, jamais écrite dans l'image. |
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
| `data/externes/legalbench/` | Le jeu LegalBench `insurance_policy_interpretation` (CC BY 4.0), avec son attribution. |
| `data/profils/<nom>.json` | Les profils d'assureur. Un seul aujourd'hui (assureur B) : les autres contrats sont lus correctement par les règles générales. |
| `tests/fixtures/cg_style_reel.pdf` | Un PDF fictif mis en page comme un vrai contrat (sommaire, en-têtes, lexique, intertitres sans numéro, mots coupés), produit par `generer_pdf.py`. |

**Pourquoi des variations à un seul fait** : si la réponse change quand on passe du local commun à la cave privative fermée à clé, c'est que le système raisonne vraiment sur le contrat, et pas qu'il répète une réponse apprise.

---

## 6. Les tests

`uv run pytest` lance 134 tests, sans appel réel à un modèle (les réponses sont préparées ou la connexion simulée) :
- **`test_pipeline.py` (37)** — lecture et découpage d'un PDF (sommaire, en-têtes, mots coupés, intertitres, lexique éclaté, renvois), contrôles d'ingestion, base, contrôle des citations (une citation inventée fait passer COUVERT à INCERTAIN), document brut, configuration du modèle (`.env`, nouvelles tentatives, clé refusée, réponses coupées), profils, journal sans le texte du sinistre, versions des consignes et MLflow, tableaux Grafana exécutés sur une vraie base ; le contrat réel A si son PDF est présent.
- **`test_prolog.py` (44)** — le moteur : trois valeurs et questions, exclusions partielles, extensions de définition, garanties accessoires, événement non traduit jamais refusé, obligations, questions décisives et paires, arbre de preuve, faits sans injection possible ; la lecture (vocabulaire, deux temps, vérification, un doute ne fait jamais couvrir, confirmation) ; le moteur permanent ; et, si SWI-Prolog est installé, **Prolog et l'oracle Python concordent** sur tous les cas.
- **`test_redaction.py` (32)** — la rédaction : Prolog généré et évalué par l'oracle, chaque contrôle (vocabulaire déclaré, fait inventé, citation réparée ou refusée, exclusion oubliée, réserves, conditions des conditions particulières mises en réserve, accessoires, extensions…), la reprise unique sur un écart au schéma, l'acceptation, la hiérarchie des valeurs.
- **`test_banc.py` (16)** — le golden set (complet, cohérent, figé), les règles seules justes pour chaque contrat, les trois couches, les portes, la latence, la fiche de validation.
- **`test_legalbench.py` (5)** — lecture du jeu, contrôle des citations, métriques, rapport.

---

## 7. L'évaluation et ses indicateurs

Le banc (`couverture banc`) mesure trois couches sur le golden set, avec des portes (`data/golden/seuils.json`) :

| Couche | Ce qu'elle mesure | Portes |
|---|---|---|
| **Règles** | Les règles seules, sur les faits idéaux : exactitude, couverts à tort, refus à tort, rappel des questions attendues, questions par réponse incertaine. | 0 couvert à tort, 0 refus à tort, exactitude ≥ 95 % |
| **Lecture** | Les faits lus par le modèle comparés aux faits idéaux : rappel des faits, contradictions, décisions changées par la lecture (et vers un couvert à tort). | ≤ 2 décisions changées, aucune vers un couvert à tort |
| **Chaîne** | Le système complet, trois exécutions : justes, exactes, couverts à tort, refus à tort, cas instables, rappel des questions, latence (un cas à la fois, au 95e centile). | 0 couvert à tort, exactitude ≥ 85 %, 95e centile ≤ 10 s |

**Couverts à tort** : l'indicateur le plus important, car c'est une promesse faite au client. **Justes** compte aussi les réponses acceptables (un « incertain » défendable) ; **exactes**, seulement la réponse attendue.

**Où on en est** (19 nov. 2026, détail et progression dans `docs/METRIQUES.md` et `docs/DEMARCHE.md`) : les règles seules sont justes à 100 % sur les deux contrats, sans couvert à tort ; la chaîne complète en est à 88 % de réponses justes pour l'assureur A, avec 4 à 5 couverts à tort par exécution, tous dus à la lecture (un lieu, une clé, une cause d'eau mal lus). La lecture est la marge de progrès.

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
| Confirmation par un modèle plus fort : option | Moins de couverts à tort, mais plus de « je ne sais pas » et trois fois plus lent : un réglage d'exploitation | L'imposer, ou l'ignorer |
| Golden set figé, banc en trois couches, portes | Savoir si une erreur vient des règles, de la lecture ou de leur combinaison ; une référence qui change le dit | Une exactitude unique, des cas qui bougent |
| Profils d'assureur en JSON | Un assureur différent = un fichier, pas du code | Des cas particuliers dans `segmentation.py` |
| Contrôle des citations par du code | Bloque les hallucinations de façon fiable | Faire confiance au modèle |
| Archiver le texte de chaque version de consigne, garde-fou en CI | Savoir quelle consigne a produit une réponse ; impossible de changer un texte en silence | Prompts modifiés sans trace |
| MLflow : une ingestion, un banc = une exécution | Comparer versions et modèles sur un même jeu (même empreinte) | Comparer des chiffres notés à la main |
| Journal sans le texte du sinistre | Mesurer en production sans stocker de données personnelles | Garder les déclarations |
| Grafana sur SQLite, tableaux générés et testés | Pas de base de plus à faire tourner ; requêtes lisibles et vérifiées | PostgreSQL pour une démonstration ; JSON édité à la main |
| Pas de LangGraph | La chaîne est linéaire | Un graphe par habitude |
| Mistral par défaut, modèle interchangeable | Fournisseur européen ; un assureur voudra souvent un modèle chez lui | Dépendre d'un seul fournisseur |
| Interface HTML simple | Restitution claire ; Streamlit déconseillé par le recruteur | Streamlit |

---

## 9. Les questions qu'on peut vous poser

**Pourquoi ne pas tout confier au modèle ?**
Parce qu'en assurance, une réponse non vérifiable ne vaut rien. Le modèle fait ce qu'il fait bien (lire une déclaration, rédiger une première traduction d'une garantie) ; les règles et les contrôles font ce que le code fait bien (appliquer une logique, vérifier qu'un texte existe).

**Pourquoi pas un RAG ?**
L'exclusion qui décide ne ressemble pas à la question (« vol de vélo » ressemble à « les vélos sont garantis », pas à « vols commis dans les parties communes »). Une recherche par ressemblance la rate. Les règles, elles, rattachent chaque exclusion à sa garantie une fois pour toutes. Une recherche hybride a été essayée, puis retirée (DEMARCHE 7.36).

**Comment tenir des centaines de contrats ?**
Chaque contrat est lu une fois, contrôlé et stocké dans le même schéma. Ses garanties sont rédigées par Mistral Large (une vingtaine de minutes pour huit garanties, en parallèle), contrôlées par le code, relues, puis acceptées. Le moteur et le vocabulaire sont communs. Le deuxième assureur est passé de zéro règle à 76 % de réponses justes en une journée (82 % avec la confirmation par Mistral Large), et chaque erreur trouvée a amélioré la méthode pour tous.

**Que fait le système quand il ne sait pas ?**
Il répond INCERTAIN, avec la question qui tranche (« la cave était-elle fermée par une serrure de sûreté ? oui → couvert ; non → non couvert »). Quand une option des conditions particulières manque, il répond « couvert, sous réserve de… ». Et un événement dont la garantie n'est pas encore traduite n'est jamais refusé : il est envoyé à un gestionnaire.

**Comment savez-vous que les règles sont justes ?**
Trois filets : les contrôles du code (citations mot pour mot, chaque exclusion du contrat traduite, vocabulaire, chargement), la relecture humaine (tracée dans `relecture/`), et le banc (les règles seules doivent être justes à 100 % sur les cas). Les cas de l'assureur B ont trouvé deux erreurs que la relecture n'avait pas vues.

**Et si la lecture se trompe ?**
C'est la principale source d'erreurs restantes, et elle est mesurée à part (couche « lecture » du banc). Trois défenses : un schéma qui n'admet que les valeurs du vocabulaire, une vérification des faits, et la confirmation des faits qui portent une réponse ferme. Un doute ne fait jamais couvrir.

**Comment comparez-vous deux versions d'une consigne, ou deux modèles ?**
Chaque banc est une exécution MLflow qui porte les versions des consignes, les modèles et l'empreinte du golden set. Deux exécutions avec la même empreinte se comparent directement, sur les couverts à tort d'abord. Une consigne ne peut pas changer sans nouvelle version : la CI échoue.

**Pourquoi INCERTAIN est-il une bonne réponse ?**
Parce que c'est la consigne : un « je ne sais pas » étayé vaut mieux qu'une réponse assurée sans justification. Et ici, INCERTAIN dit précisément quoi demander à l'assuré.

**Quel lien avec SortirIA ?**
Le même problème de fond : des sources hétérogènes à ramener dans un schéma commun et fiable. Ce projet en reprend le versionnage des consignes avec garde-fou en CI, le suivi MLflow, le journal et les tableaux Grafana générés et testés. La différence : SortirIA recommande, une approximation reste utile ; ici le système décide, une erreur est une promesse faite au client, d'où la décision calculée, le contrôle des citations et le droit de répondre INCERTAIN.

**Comment avez-vous utilisé l'IA ?**
Pour écrire le code plus vite, comme le recruteur l'encourage, et dans le système lui-même pour lire les déclarations et rédiger les règles. Les choix d'architecture, l'évaluation et la relecture des règles restent les vôtres : vous devez pouvoir expliquer chaque fichier de ce document.

---

## 10. Limites et suites

**Limites actuelles**
- Les conditions particulières ne sont pas lues : les options deviennent des réserves (« couvert, sous réserve que… »).
- La lecture des déclarations reste la principale source d'erreurs (4 à 5 couverts à tort par exécution sur 97 cas pour l'assureur A).
- Le golden set a été écrit par Claude et reste à valider par l'auteur (`data/golden/A_VALIDER.md`) ; les cas de l'assureur B ont été écrits par celui qui a relu ses règles.
- La responsabilité civile, l'assistance et la protection juridique ne sont pas encore traduites : ces sinistres vont à un gestionnaire.
- Le découpage repose sur des règles et des profils ; un format très inhabituel dépassera ce qu'un profil peut décrire.
- Les tableaux de plafonds sont lus comme du texte : les montants sont cités, pas calculés.

**Suites, dans l'ordre**
1. Un jeu de cas écrit par l'auteur sans voir les règles, pour chaque contrat.
2. Les garanties restantes des deux contrats (responsabilité civile, assistance, pack multimédia).
3. La lecture : les erreurs restantes, une par une, comme pour les règles.
4. Lire les conditions particulières pour lever les réserves.
5. Déployer l'interface avec le `Dockerfile` pour avoir une URL à envoyer.
