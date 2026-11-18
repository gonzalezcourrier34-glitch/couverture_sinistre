# Comprendre le projet, fichier par fichier

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
| **Conditions générales (CG)** | Le texte commun à tous les clients d'un produit d'assurance (par exemple « appart 123, version 2025 »). Il décrit les garanties, les exclusions, les définitions, les plafonds. C'est ce que le système lit. |
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
| **BM25** | Un algorithme classique de recherche par mots-clés. Il donne un score à chaque document selon les mots qu'il partage avec la requête, en favorisant les mots rares. |
| **Embeddings** | Une représentation d'un texte en vecteur de nombres, telle que deux textes de sens proche ont des vecteurs proches. Ici `mistral-embed`, calculé une fois par clause à l'ingestion. |
| **Similarité cosinus** | La mesure de proximité entre deux vecteurs (1 = même direction, 0 = sans rapport). |
| **Recherche hybride** | Chercher à la fois par les mots (BM25) et par le sens (embeddings), puis fusionner les deux classements. |
| **RRF** (*Reciprocal Rank Fusion*) | Une façon simple de fusionner deux classements : score = 1/(60 + rang dans le premier) + 1/(60 + rang dans le second). Un élément bien classé par les deux passe devant. Elle n'a pas besoin que les deux scores soient comparables. |
| **Normalisation** | Mettre le texte sous une forme comparable : minuscules, sans accents. |
| **Racinisation** (*stemming*) | Réduire un mot à sa racine pour que « garantis », « garantie » et « garanties » se rejoignent. |
| **Mots vides** | Les mots trop fréquents pour être utiles à la recherche : « le », « de », « et »… |
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
| **Enveloppe d'une garantie** | Les clauses qui l'entourent et la limitent : ses exclusions, ses conditions, ses plafonds, ses définitions, ses renvois. |
| **Groupe** | La section dont dépend une clause. `2.10-a` (exclusions) appartient au groupe `2.10` (garantie vol). Sert à rattacher les exclusions à leur garantie. |
| **Juge** | Le composant qui produit la décision. Il y en a quatre (voir `juges.py` et `conditions.py`). |
| **Grille** | La liste des conditions et exclusions, chacune avec un état, que remplit le juge par conditions. |
| **État d'une condition** | `REMPLIE`, `NON_REMPLIE` ou `INCONNUE`. Pour une exclusion, `REMPLIE` veut dire qu'elle s'applique. |
| **Condition décisive** | Celle qui a fait basculer la décision. |
| **Verdict** | La réponse : décision, justification, citations, ce qu'il faut vérifier, confiance. |
| **COUVERT / NON_COUVERT / INCERTAIN** | Les trois décisions possibles. INCERTAIN est une vraie réponse, accompagnée de ce qu'il faut vérifier. |
| **Faux « couvert »** | Le système dit « couvert » alors que ce n'est pas le cas. C'est l'erreur la plus grave, car c'est une promesse faite au client. |
| **Document brut** | La méthode de référence : le contrat entier collé dans le prompt, comme dans un chatbot. Elle sert de point de comparaison. |
| **Profil d'assureur** | Les règles de lecture propres à un assureur (ses intertitres et leur type, ses lignes de bruit, le format de son lexique), dans un fichier JSON. L'équivalent de `sources.yaml` dans SortirIA. |
| **Proposition de réparation** | Un profil proposé par Mistral pour un contrat mal lu, vérifié par le code, en attente de validation humaine. Statuts : `a_valider`, `acceptee`, `refusee`, `refusee_par_la_verification`. |
| **Juge de qualité** | Un appel au modèle, à l'ingestion, qui vérifie le type d'un échantillon de clauses. Son score est la part de types confirmés. |
| **Juge de la grille (relecteur)** | Un second appel, indépendant, qui relit les conditions décisives et confirme ou conteste chacune. |
| **Contestation** | Le relecteur estime que le passage cité ne justifie pas l'état proposé. La condition redevient INCONNUE. |
| **Journal** | La table `analyses` : chaque question posée au système et sa réponse, sans le texte du sinistre. |
| **Dérive** | Un changement dans ce que le système reçoit ou répond, d'une période à l'autre. |
| **PSI** (*Population Stability Index*) | La mesure de dérive : Σ (part récente − part de référence) × ln(part récente / part de référence). Moins de 0,1 : stable ; de 0,1 à 0,25 : modérée ; plus de 0,25 : forte. |
| **Bilan** | Le rapport de la semaine : ce qui demande une intervention d'abord, puis les chiffres. |
| **MLflow** | Un outil pour suivre des expériences : chaque exécution garde ses paramètres, ses métriques et ses fichiers. Son **Prompt Registry** garde les versions des consignes. |
| **Exécution** (*run*) | Une ingestion ou une évaluation enregistrée dans MLflow. |
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
1. **Une fois par contrat** : le transformer en clauses structurées et typées, contrôlées, stockées.
2. **À chaque sinistre** : retrouver la garantie concernée **et tout ce qui l'entoure** (exclusions, définitions, renvois).
3. **Décider comme un gestionnaire** : une grille de conditions, chacune vérifiée sur les faits et justifiée par une citation. La décision est **calculée par des règles** à partir de cette grille, pas devinée par le modèle.
4. **Vérifier par du code** que chaque citation existe vraiment dans le contrat.

---

## 3. Le parcours complet d'un sinistre

### A. Une fois par contrat : l'ingestion (`couverture ingerer`)

```
PDF ─► chargement.py ─► segmentation.py ─► controles.py ─► base.py (SQLite) ─► embeddings (mistral-embed)
       pages, nettoyage   clauses typées     OK / A_VERIFIER   contrats, clauses,   un vecteur par clause
                          (+ profil d'assureur)                renvois, vecteurs

                                         └─► qualite.py : Mistral vérifie le type d'un échantillon ─► score, A_VERIFIER si < 80 %

contrat A_VERIFIER ─► reparation.py : Mistral propose un profil ─► vérifié par le code ─► validé par vous ─► relu

chaque semaine : journal des analyses ─► derive.py (PSI) ─► bilan.py ─► Markdown, et mail si configuré
```

Sur le contrat Foyer appart 123 : 48 pages deviennent 147 clauses, dont 63 définitions. Statut `OK`.

### B. À chaque question : l'analyse (`couverture analyser` ou l'interface)

Exemple : « Je me fais voler mon vélo dans le local commun de l'immeuble, qui n'était pas fermé à clé. »

1. **Faits** (`faits.py`) : événement = vol ; bien = vélo ; lieu = parties communes ; la requête est enrichie avec le vocabulaire du contrat (« parties communes », « local à vélos collectif »).
2. **Recherche** (`recherche.py`) : les mots (BM25) et le sens (embeddings) trouvent la garantie vol (`2.10`), fusionnés par RRF. L'enveloppe ajoute ses exclusions (`2.10-a`), les définitions utiles (`12/effraction`…), les renvois.
3. **Grille** (`conditions.py`) : le modèle remplit les conditions :
   - garantie « Vol du contenu » : *le vélo était-il dans le bâtiment assuré ?* → INCONNUE ;
   - exclusion : *le vol a-t-il eu lieu dans les parties communes ?* → REMPLIE (art. 2.10-a, p. 12) ;
   - exclusion : *complicité d'un proche ?* → NON_REMPLIE.
4. **Vérification** : chaque passage cité est recherché dans la clause. Une condition sans preuve est écartée.
5. **Décision calculée** : une exclusion est remplie → **NON_COUVERT**, confiance 0,9, condition décisive = 2.10-a.
6. **Relecture** (`relecture.py`) : un second appel relit la condition décisive, avec le texte complet de l'art. 2.10-a et le sinistre. S'il confirme, la décision reste. S'il conteste (« le local n'est pas décrit comme une partie commune »), la condition redevient inconnue, la décision est recalculée, et la question à poser à l'assuré est ajoutée.
7. **Affichage** : la décision, puis la grille, chaque ligne avec son état, sa citation, sa page et le texte complet de la clause.
8. **Journal** : l'analyse est notée (décision, confiance, contestations, questions à poser), sans le texte du sinistre.

---

## 4. Les fichiers, un par un

L'ordre suit le parcours des données.

### `src/couverture/models.py` — les structures de données

**Rôle** : définir la forme de tout ce qui circule entre les étapes, avec Pydantic.

| Modèle | Contenu |
|---|---|
| `TypeClause` | garantie, exclusion, condition, limite, définition, autre. |
| `Clause` | `id` (« 4.3 », « 2.10-a », « 12/effraction »), `article`, `groupe`, `titre`, `chemin` (les titres parents), `texte`, `type`, `pages`, `renvois`. |
| `ClauseRetenue` | Une clause sélectionnée par la recherche, avec son score et **la raison** de sa sélection. |
| `Faits` | Événements, biens, lieux, circonstances repérés dans la description. |
| `Decision` | COUVERT, NON_COUVERT, INCERTAIN. |
| `Citation` | Identifiant de clause, extrait, rôle, validité, pages. |
| `EtatCondition` / `Condition` | Une ligne de la grille : nature (garantie, exclusion, limite), énoncé, état, extrait, justification, question à poser, validité, caractère décisif. |
| `Verdict` | La décision et tout ce qui la justifie, dont `decision_initiale` (la décision du juge avant contrôle, pour mesurer ce que le contrôle corrige). |
| `Resultat` | La sortie complète : sinistre, contrat, méthode, faits, clauses consultées, verdict. |

**Pourquoi** : des structures explicites rendent chaque étape testable séparément et la sortie entièrement traçable. Pydantic refuse une réponse du modèle mal formée au lieu de la laisser passer.

### `src/couverture/texte.py` — normaliser le français

**Rôle** : rendre les textes comparables pour la recherche.
- `normaliser` : minuscules, sans accents, « œ » → « oe », apostrophes harmonisées.
- `mots` : découpe en mots et retire les mots vides.
- `raciniser` : retire des suffixes courants (« -ement », « -ation », « -es », « -s »…) si le mot reste assez long.
- `jetons` : `mots` puis `raciniser`. C'est ce qu'utilise BM25.

**Pourquoi** : « garantis », « Garantie » et « GARANTIES » doivent se rejoindre. Le raciniseur est volontairement léger, écrit à la main pour éviter une dépendance. Un essai d'ajouter le suffixe « -er » a dégradé les résultats, il a donc été retiré : les tests l'ont montré.

### `src/couverture/chargement.py` — lire et nettoyer le PDF

**Rôle** : obtenir des lignes de texte propres, chacune avec son numéro de page.
- `lire_pages` : PDF via pdfplumber (ou pypdf en secours), Word via python-docx, Markdown et texte directement.
- `nettoyer` :
  1. **Puces** : les caractères privés des polices (Wingdings, Symbol) deviennent « • ».
  2. **En-têtes et pieds de page** : une ligne du haut ou du bas présente sur au moins 40 % des pages est retirée. On compare des « signatures » où les chiffres sont remplacés, pour que « Page 12 » et « Page 13 » se reconnaissent.
  3. **Sommaire** : une page titrée « Sommaire » ou « Table des matières », ou une page du début où presque toutes les lignes finissent par un numéro, est retirée. Les lignes avec des points de conduite (« ...... 12 ») aussi.
  4. **Numéros de page seuls** : retirés.
  5. **Mots coupés** : « garan- » + « tie » → « garantie », seulement si la ligne précédente est pleine, pour ne pas recoller « lave- » dans une liste.
- `charger_lignes` : lire, puis nettoyer. `charger_texte` : le même texte d'un seul tenant, pour la méthode « document brut ».

**Pourquoi** : sur un vrai contrat, ce bruit casse le découpage. Le sommaire du contrat Foyer créait des clauses fantômes (« 10.2 Non-paiement 38 ») avant cette correction. Garder la page de chaque ligne permet de citer « art. 2.10-a, p. 12 ».

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
- **Lexique éclaté** : une section de définitions est coupée en une clause par terme. Deux formats sont gérés : « Terme : définition » sur une ligne, et le terme seul sur sa ligne avec la définition dessous (le format de Foyer). Chaque terme devient `12/effraction`, `12/parties-communes`…
- **Clauses trop longues** (plus de 2 500 caractères, souvent des listes d'exclusions) : coupées aux puces en morceaux (`2.13~1`, `2.13~2`) pour que les citations restent précises.

**`classer` : le typage**, dans cet ordre :
1. le titre propre de la clause (« Ce qui n'est pas garanti » → exclusion ; « Franchise » → limite ; « Lexique » → définition…) ;
2. sa formulation (« ne sont pas garantis » → exclusion, testé avant « sont garantis » qui est contenu dedans ; « nous garantissons » → garantie ; « sous réserve » → condition) ;
3. les titres de ses parents ;
4. sinon : autre.

**Renvois** : `extraire_renvois` repère « article 4.2 », « art. 1.5 », « articles 4.1 et 4.2 ». Il écarte les références à des lois (« art. 58 de la loi du 4 avril 2014 », « article 1302 du Code civil ») : un mot comme loi, code, arrêté ou RGPD juste après, ou un numéro trop long (« 1302 »). `resoudre` relie chaque renvoi à la clause visée, ou à ses premières sous-clauses.

**Pourquoi** : une citation précise exige une clause entière et typée. Le type permet ensuite à la recherche de ramener les exclusions et au contrôle de vérifier qu'un « couvert » s'appuie sur une garantie. Les règles ont été ajustées sur un PDF de test mis en page comme un vrai contrat, puis sur le vrai contrat Foyer.

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

**Rôle** : un profil est un fichier JSON dans `data/profils/<nom>.json`, désigné dans le catalogue (`"profil": "foyer"`). Il contient :
- `intertitres` : des titres propres à l'assureur et leur type (« Les situations hors contrat » → exclusion). La segmentation les reconnaît comme intertitres, et `classer` leur donne ce type en priorité ;
- `lignes_ignorees` : des expressions régulières pour les lignes de bruit que le nettoyage n'a pas vues (une référence de document répétée…) ;
- `lexique` : le format des définitions (`deux_points`, `terme_seul`, ou `auto`).

`valider_profil` refuse un type inconnu, une expression invalide, un nom mal formé. `charger_profil` et `ecrire_profil` le lisent et l'écrivent.

**Pourquoi** : les règles générales couvrent la plupart des contrats. Quand un assureur rédige autrement, on n'ajoute pas un cas particulier dans le code : on écrit un profil, réutilisé pour toutes les versions de ses contrats. C'est ce qui rend l'approche tenable sur des centaines de contrats, comme `sources.yaml` dans SortirIA pour les agendas.

### `src/couverture/reparation.py` — l'agent de réparation : il propose, un humain décide

**Rôle** : pour un contrat `A_VERIFIER`, la commande `couverture reparer` :
1. **classe** chaque alerte des contrôles en famille de problème (`diagnostiquer`) : découpage échoué, titres non reconnus, aucune exclusion, aucune garantie, lexique non reconnu, pas d'exclusions générales, renvois cassés, chacune avec un conseil ;
2. **réunit** les lignes qui ressemblent à des titres (`candidats_titres`) : courtes, sans ponctuation finale, avec une majuscule, les plus fréquentes d'abord (un intertitre revient dans chaque section) ;
3. **demande** à Mistral un profil : quels titres sont des intertitres et de quel type, quelles lignes sont du bruit, quel format de lexique. Consigne : recopier chaque ligne exactement, n'en inventer aucune ;
4. **vérifie** la proposition par du code (`verifier`) :
   - chaque intertitre doit exister mot pour mot dans le contrat, sinon il est écarté ;
   - chaque motif de ligne à ignorer doit reconnaître son exemple, qui doit exister dans le contrat, ne pas effacer plus de 8 % des lignes, et **ne jamais effacer une ligne longue ou qui parle de garantie ou d'exclusion** ;
   - le contrat est redécoupé avec le profil, et les contrôles sont relancés : la proposition n'est retenue que s'il y a **moins d'alertes** (ou nettement moins de clauses sans type) **et aucune nouvelle alerte** ;
5. **enregistre** la proposition dans `data/propositions/NNN-<contrat>.json`, avec le diagnostic, la réponse du modèle, le profil, l'avant/après et ce qui a été écarté. Statut `a_valider`, ou `refusee_par_la_verification`.

**Rien n'est appliqué** avant que vous lanciez `couverture propositions --accepter N`. L'acceptation écrit le profil, le rattache au contrat dans le catalogue, puis relit le contrat. `--refuser N` la classe sans effet.

**Exemple** (un test le reproduit) : un assureur titre ses exclusions « Les situations hors contrat ». Le contrat sort `A_VERIFIER` (« aucune exclusion détectée »). Mistral propose cet intertitre comme exclusion, plus un intertitre inventé et un motif qui effacerait les lignes « Nous garantissons… ». La vérification garde le premier et écarte les deux autres. Après acceptation : 4 exclusions trouvées, une alerte de moins.

**Pourquoi** : c'est le principe de l'agent de SortirIA (`agent/diagnosis.py`) : classer, chercher une réparation, la vérifier, la proposer sans l'appliquer. Ici, la règle est encore plus importante : un profil faux pourrait faire passer une exclusion pour une garantie, donc dire « couvert » à tort. L'IA travaille là où elle est forte (comprendre une rédaction nouvelle), une seule fois par assureur, et sous le contrôle du code puis d'un humain.

### `src/couverture/base.py` — le stockage multi-contrats

**Rôle** : une base SQLite avec trois tables.
- `contrats` : identifiant, assureur, produit, version, fichier, empreinte, statut, rapport des contrôles, texte brut, date d'ingestion.
- `clauses` : toutes les clauses de tous les contrats, avec le contrat auquel elles appartiennent, leur ordre, leur groupe, leur type, leurs pages.
- `renvois` : les liens d'une clause vers une autre.
- `vecteurs` : l'embedding de chaque clause, rangé par modèle (changer de modèle d'embeddings ne mélange pas les vecteurs).

Méthodes : `enregistrer` (remplace entièrement un contrat), `contrats`, `contrat`, `clauses(contrat_id)`, `texte_brut`, `empreinte`.

**Pourquoi** : chaque contrat est lu une fois, et chaque question ne charge **que les clauses du contrat concerné**. On ne mélange jamais deux contrats. SQLite suffit pour des centaines de contrats et ne demande aucun serveur. Les vecteurs y sont stockés en JSON et comparés en Python (quelques centaines de clauses par contrat). En production, ce serait PostgreSQL + pgvector, comme dans SortirIA, avec le même schéma.

### `src/couverture/ingestion.py` — de fichier à base

**Rôle** :
- `ingerer_fichier` : calcule l'empreinte du fichier ; s'il n'a pas changé depuis la dernière fois, ne fait rien (idempotence) ; sinon lit, découpe, contrôle et enregistre.
- `ingerer_dossier` : fait de même pour tous les fichiers de `data/contrats`, avec les métadonnées de `catalogue.json` (identifiant, assureur, produit, version, et le **profil d'assureur** s'il y en a un). Sans entrée au catalogue, l'identifiant est tiré du nom du fichier.
- **L'empreinte** couvre le fichier **et** son profil : modifier le profil relance le découpage.
- `calculer_vecteurs` : avec une clé Mistral, calcule un embedding par clause (son chemin de titres et son texte) et l'enregistre. Si la clé est ajoutée après une première ingestion, seuls les vecteurs manquants sont calculés. **Une panne des embeddings ne bloque jamais l'ingestion** (comme le juge de qualité de SortirIA) : la recherche se fait alors par les mots seuls, et le rapport le dit.

**Pourquoi** : ajouter un contrat se résume à déposer un fichier et relancer `couverture ingerer`. La version du contrat compte : un client garde les CG en vigueur au moment de sa souscription.

### `src/couverture/faits.py` — traduire la langue du client en langue du contrat

**Rôle** :
- `extraire_faits` repère, avec des listes de déclencheurs, les **événements** (vol, incendie, dégât des eaux, bris, dommage accidentel, responsabilité), les **biens** (vélo, mobilier, électronique, objet de valeur), les **lieux** (habitation, dépendance, parties communes, extérieur) et les **circonstances** (effraction, fermé à clé, sans flammes, antivol, violence, badge). Un déclencheur doit commencer un mot : « eau » ne doit pas trouver « bureau ».
- `enrichir_requete` ajoute à la description les termes du contrat qui correspondent : « local commun » → « parties communes », « local à vélos collectif » ; « bougie » → « incendie », « flamme », « objet incandescent ».

**Pourquoi** : le client dit « on m'a piqué mon vélo dans le local commun » ; le contrat dit « vol », « biens mobiliers », « parties communes ». Sans ce pont, la recherche par mots-clés rate les bonnes clauses. Limite : ce lexique est écrit à la main pour l'habitation.

### `src/couverture/recherche.py` — retrouver la garantie et son enveloppe

**Rôle** : sélectionner au plus 16 clauses à donner au juge.
1. **La recherche hybride**, reprise de SortirIA (`build_search_query`) :
   - **par les mots** : BM25 (écrit dans le fichier, sans dépendance), sur la description enrichie par `faits.py`. Les titres comptent double, car « 2.10 Garantie vol » dit beaucoup. Il retrouve les termes juridiques précis ;
   - **par le sens** : la description d'origine est vectorisée par `mistral-embed` et comparée aux vecteurs des clauses (similarité cosinus). Il rapproche « on m'a chouravé ma bicyclette » de « vol », sans aucun mot commun ;
   - **la fusion RRF** : score = 1/(60 + rang mots) + 1/(60 + rang sens), sur les 30 premiers de chaque classement. Les 5 meilleures clauses sont retenues, avec leur origine : « par les mots », « par le sens » ou les deux.
   - Sans clé Mistral, ou si les vecteurs n'ont pas été calculés, la recherche se fait par les mots seuls, comme avant.
2. **L'enveloppe**, pour chaque garantie ou exclusion retenue :
   - ses **sous-sections** (`2.10` → `2.10-a`) ;
   - ses **voisines** du même groupe qui sont des exclusions, conditions ou limites.
3. **Les exclusions générales** qui partagent au moins un mot avec le sinistre, ou qui sont proches par le sens.
4. **Les renvois** des clauses retenues.
5. **Les définitions** des termes qui apparaissent dans la requête ou dans les clauses retenues.

Chaque clause retenue garde **la raison** de sa sélection, affichée dans l'interface (« sous-section de 2.10 », « définition d'un terme employé »…). Le résultat est remis dans l'ordre du contrat.

**Pourquoi** : c'est la différence principale avec un RAG simple. La clause qui décide, l'exclusion, ne ressemble pas à la question ; elle est retrouvée **par la structure du contrat**, pas par ressemblance. Sur Foyer, le vélo dans le local commun ramène bien la garantie vol 2.10 et l'exclusion 2.10-a. Un test le vérifie.

**Pourquoi l'hybride** : les deux classements se complètent, comme dans SortirIA où « le sens rate les noms propres, les mots les retrouvent ». Ici, les mots retrouvent les termes du contrat, et le sens retrouve ce que le client dit avec ses propres mots. Le sens réduit aussi la dépendance au lexique écrit à la main dans `faits.py`, le point le plus fragile du projet. La fusion RRF est choisie parce qu'elle ne demande pas de régler des poids entre deux scores qui n'ont pas la même échelle.

### `src/couverture/llm.py` — parler au modèle

**Rôle** : trois clients, sans bibliothèque externe (de simples appels HTTP), qui respectent tous le même protocole `LLM` : une méthode `completer(systeme, message)`.
- `MistralLLM` (par défaut) : l'API de Mistral, `https://api.mistral.ai/v1`. Clé dans `MISTRAL_API_KEY`, modèle `mistral-large-latest` sauf si `COUVERTURE_MODELE` dit autre chose. Le **mode JSON** de Mistral est activé (`response_format`) : le serveur garantit une réponse JSON valide, ce qui évite les grilles illisibles.
- `AnthropicLLM` : l'API d'Anthropic, clé dans `ANTHROPIC_API_KEY`.
- `OpenAICompatibleLLM` : toute API compatible OpenAI (Ollama en local, vLLM, Azure…), adresse dans `COUVERTURE_LLM_URL`. `MistralLLM` en est une variante, puisque l'API de Mistral est compatible OpenAI.

`configurer()` choisit le fournisseur : celui forcé par `COUVERTURE_FOURNISSEUR`, sinon le premier dont la clé est renseignée, dans l'ordre Mistral, Anthropic, compatible OpenAI. Une valeur d'exemple laissée telle quelle (« colle-ta-cle-ici ») est ignorée. Sans rien, il renvoie `None`, et la pipeline utilise le juge heuristique.

`_poster` envoie les requêtes avec **de nouvelles tentatives** sur les erreurs passagères : 429 (limite de débit atteinte) et erreurs serveur 5xx, en attendant de plus en plus longtemps (ou le délai indiqué par le serveur). Une clé refusée (401, 403) donne un message clair : « Clé API refusée, vérifier la clé dans le fichier .env ». Ces erreurs (`ErreurLLM`) remontent jusqu'à l'utilisateur au lieu d'être confondues avec une réponse illisible du modèle.

Température 0 partout, pour des réponses stables d'une exécution à l'autre.

**Embeddings** : `MistralEmbeddings` appelle `mistral-embed` par lots de 32 textes (tronqués à 6 000 caractères). `configurer_embeddings()` l'active dès que `MISTRAL_API_KEY` est renseignée ; `COUVERTURE_EMBEDDINGS=aucun` le coupe.

**Pourquoi Mistral par défaut** : fournisseur européen, données hébergées dans l'UE, ce qui compte pour un assureur luxembourgeois qui traite des données clients. Contexte long (suffisant pour la méthode « document brut »), prix faible, API compatible OpenAI. **Pourquoi plusieurs fournisseurs** : changer de modèle ne doit rien changer au reste, et un assureur voudra souvent un modèle hébergé chez lui.

### `src/couverture/config.py` — les clés hors du code

**Rôle** : `charger_env` lit le fichier `.env` à la racine du projet et place ses valeurs dans l'environnement, **sans écraser** une variable déjà définie. Il gère les commentaires, les guillemets et le préfixe `export`. Appelé au démarrage de chaque commande.

**Pourquoi** : une clé API ne doit jamais être écrite dans le code ni versionnée. `.env` est dans le `.gitignore`. Son contenu minimal :

```
MISTRAL_API_KEY=colle-ta-cle-ici
COUVERTURE_MODELE=mistral-large-latest
```

`mistral-small-latest` coûte moins cher. Pour un autre fournisseur : `ANTHROPIC_API_KEY=…`, ou `COUVERTURE_LLM_URL=http://localhost:11434/v1` pour Ollama, et `COUVERTURE_FOURNISSEUR=…` pour forcer le choix si plusieurs sont renseignés. En déploiement, les mêmes variables sont passées au conteneur (`docker run --env-file .env`).

### `src/couverture/juges.py` — le juge sans modèle et la référence « brut »

**Rôle** : produire un verdict à partir du sinistre et des clauses. Tous respectent le protocole `Juge` (une méthode `juger`).
- La méthode « direct » (le modèle conclut en un coup sur les clauses retenues) a été **retirée** le 17 novembre : elle ne servait que de point de comparaison, et la référence « brut » suffit. Sa consigne reste archivée dans `docs/consignes/verdict-direct/`.
- **`JugeHeuristique`**, sans modèle : compte les mots communs entre le sinistre et les clauses. Il ne dit « couvert » que si aucune exclusion ne recoupe le sinistre ; il dit « non couvert » si aucune garantie ne correspond, ou si une exclusion recoupe nettement plus qu'une garantie ; sinon INCERTAIN. Il cite le passage le plus pertinent de chaque clause, en donnant plus de poids aux mots du lieu (« parties communes »), qui décident souvent.
- **`JugeDocumentBrut`**, la référence « chatbot » : le contrat entier dans le prompt, sans recherche ni structure.
- Outils partagés : `formater_clauses` (présente les clauses au modèle avec leur identifiant, leur type et leur chemin), `extraire_json` (récupère le JSON même entouré de texte ou de balises Markdown).

**Pourquoi** : `brut` sert de point de comparaison pour prouver l'intérêt des méthodes structurées. L'heuristique fait tourner le système sans clé et sert de filet de sécurité : volontairement prudente, elle n'a jamais dit « couvert » à tort sur les cas de test.

### `src/couverture/conditions.py` — le juge par conditions (méthode par défaut)

**Rôle** : c'est le cœur de la décision.

1. **Le modèle remplit une grille, sans conclure.** Le prompt (`SYSTEME_CONDITIONS`) lui demande :
   - les garanties qui pourraient viser le sinistre, et pour chacune ses conditions, **une condition = un seul fait vérifiable** ;
   - toutes les exclusions qui pourraient le concerner, même s'il pense qu'elles ne s'appliquent pas ;
   - les limites à signaler ;
   - pour chaque ligne : un état, l'extrait exact, la justification tirée de la description, et la question à poser si l'état est inconnu. Consigne clé : « N'invente aucun fait : dans le doute, INCONNUE ».
2. **`lire_grille`** transforme le JSON en objets `Condition`. Un état non reconnu devient INCONNUE.
3. **`verifier_conditions`** écarte toute condition dont la clause n'a pas été fournie ou dont l'extrait est introuvable.
4. **`decider`** applique des règles explicites, sur les seules conditions prouvées :

| Situation | Décision | Confiance |
|---|---|---|
| Une exclusion est remplie | NON_COUVERT | 0,9 |
| Une garantie a toutes ses conditions remplies, aucune exclusion inconnue | COUVERT | 0,85 |
| Une garantie a toutes ses conditions remplies, mais une exclusion est inconnue | INCERTAIN (on dit laquelle) | 0,6 |
| Une garantie possible a des conditions inconnues et aucune non remplie | INCERTAIN (avec les questions) | 0,5 |
| Toutes les garanties ont une condition non remplie | NON_COUVERT | 0,75 |
| Aucune garantie prouvée | INCERTAIN | 0,2 |

   Si une condition (hors limites) a été écartée faute de preuve, la confiance est plafonnée à 0,5.
5. **Les conditions décisives** sont marquées et leurs citations placées en tête. Les questions des conditions inconnues deviennent « ce qu'il faut vérifier ».
6. **Si un relecteur est configuré** (par défaut, oui), les conditions décisives sont relues et la décision recalculée en cas de contestation (voir `relecture.py`).

**Pourquoi** :
- **« Je ne sais pas » sort de la logique** : c'est une condition à l'état inconnu, et on sait laquelle. Ce n'est pas une hésitation du modèle.
- **Des petites questions plutôt qu'une grande.** Un modèle se trompe beaucoup moins sur « ce fait remplit-il cette condition ? » que sur « ce sinistre est-il couvert par ce contrat de 48 pages ? ».
- **Une exclusion inventée ne peut pas faire basculer la décision**, puisqu'elle est écartée avant le calcul. Un test le vérifie.
- **C'est ainsi que travaille un gestionnaire**, et le raisonnement est lisible ligne par ligne.
- **Les conditions particulières s'y brancheront naturellement** : « l'option est-elle souscrite ? » est une condition comme une autre.

### `src/couverture/compilation.py` — compiler le contrat en fiches

**Rôle** : une fois par contrat (`couverture compiler`), traduire chaque garantie en **fiche** de questions fermées, réutilisables pour tous les sinistres.
- `unites` : pour chaque garantie (ses morceaux « 2.14~1 », « 2.14~2 » réunis), les clauses à montrer au modèle. Ses sous-sections (« 2.10-a Exclusions ») si le contrat en a ; sinon les exclusions et conditions rangées en fin de section (contrat fictif : 4.4 et 4.5 pour 4.1, 4.2, 4.3). Plus les renvois et les définitions des termes employés. Les exclusions générales sont à part ;
- `compiler_garantie` : un appel par garantie (quatre en parallèle). Le modèle rend une ou plusieurs fiches : événements visés, conditions (OUI favorable à l'assuré), exclusions (OUI = elle s'applique, avec `a_demander`), limites ;
- `_points` : **chaque extrait est vérifié dans la clause citée** ; une question à la citation introuvable est écartée et signalée ;
- `compiler_exclusions_generales` : un appel pour les exclusions communes, chacune « à demander » ou « présumée absente » ;
- `verifier_import` : après relecture humaine (`couverture fiches --exporter` puis `--importer`), revérifie tout. Un humain peut reformuler une question, pas inventer une citation.

**Pourquoi** : les conditions sont des propriétés du contrat. Les faire reformuler par le modèle à chaque sinistre (méthode `conditions`) produit des grilles un peu différentes à chaque fois et répète les mêmes erreurs. Compilées une fois, elles se contrôlent une fois. Le raisonnement complet est dans `docs/DEMARCHE.md`.

**Stockage** : table `compilations` de `base.py`. Une ré-ingestion ne l'efface pas (elle a coûté des appels et a pu être relue) ; son empreinte dit à quelle version du contrat elle correspond, et une compilation périmée est ignorée à l'analyse.

### `src/couverture/fiches.py` — analyser avec le contrat compilé (méthode `fiches`)

**Rôle** : à chaque sinistre, le modèle n'a plus qu'un métier : répondre oui / non / inconnu à des questions déjà écrites. Chaque question a un **rôle** (consigne de compilation v2) : périmètre (événement, bien, lieu), circonstance, obligation de prévention, exclusion, limite. Le modèle voit ce rôle : un périmètre décrit et contraire vaut « non », une circonstance passée sous silence vaut « inconnu ». `decider_fiche` applique, dans l'ordre : périmètre contraire → hors sujet ; circonstance non remplie → ne joue pas ; périmètre incomplet → « possible » ; exclusion qui s'applique → refus ; circonstance inconnue → incertain ; obligation non respectée → incertain (déchéance seulement s'il y a un lien causal) ; sinon couvert, **sous réserve** des exclusions et obligations inconnues (charge de la preuve : l'assuré établit la garantie, l'assureur l'exclusion). Les questions sont posées par fiche, un appel par fiche en parallèle. Les faits (événement, bien, lieu) sont extraits par un petit appel (`extraire_faits_modele`), le lexique de `faits.py` servant de secours. Les points ci-dessous décrivent la première version et restent vrais dans leur principe.
1. `router` : les fiches dont l'événement correspond aux faits de `faits.py`. Si aucun événement n'est reconnu, `router_par_le_modele` choisit dans la liste des fiches ;
2. `JugeFiches.juger` : un appel pour toutes les questions des fiches retenues et des exclusions générales. Une exclusion « présumée absente » restée inconnue devient « ne s'applique pas » ;
3. `decider_fiche`, pour chaque fiche, lit comme un gestionnaire : une condition de garantie non remplie écarte la fiche **sans consulter ses exclusions** ; une fiche dont aucune condition n'est établie n'est **pas rattachée** au sinistre ; sinon, les règles de `conditions.decider`. Puis `decider_fiches` : COUVERT si une fiche l'est, sinon INCERTAIN si une fiche l'est, sinon NON_COUVERT si une fiche rattachée refuse, sinon INCERTAIN (aucune garantie rattachée). Une exclusion du vol ne fait pas tomber la garantie incendie ;
   les exclusions générales d'une partie qui a ses propres garanties (art. 5.10, responsabilité civile) ne valent que pour cette partie ;
4. relecture des lignes décisives (`relecture.py`), limitée aux exclusions de la fiche retenue et **sans les présumées absentes** : la consigne du relecteur dit « dans le doute, conteste », ce qui les rendrait inconnues et annulerait la présomption.

**Pourquoi** : plus d'exclusion décisive oubliée par la recherche, des citations toujours valides, un appel plus petit. La méthode `conditions` reste pour comparer (`couverture comparer`).

### `regles/` et `src/couverture/prolog.py` — le contrat en règles Prolog (méthode `regles`)

**Rôle** : le contrat est écrit en **règles**, un moteur logique décide, et le modèle ne fait que lire les faits de la déclaration.
- `regles/vocabulaire.json` : les variables communes à tous les contrats (événement, bien, lieu, fermeture, serrure de sûreté, effraction, violence, flammes, embrasement…), leurs valeurs permises et la question à poser quand elles manquent ;
- `regles/moteur.pl` : le moteur, commun à tous les contrats. Logique à **trois valeurs** (oui, non, inconnu), pour ne pas confondre « je ne sais pas » avec « faux » (le monde clos de Prolog). Il applique les règles de gestionnaire (périmètre, circonstances, exclusions, obligations avec lien causal, charge de la preuve, exclusions partielles) et combine les garanties ;
- `regles/<contrat>.pl` : les règles d'un contrat, sous forme de données (`definition`, `garantie`, `perimetre`, `circonstance`, `obligation`, `exclusion`, `limite`), chacune avec la phrase du contrat qu'elle traduit ;
- `regles/cas/<contrat>.jsonl` : les faits « idéaux » de chaque sinistre de test, pour éprouver les règles sans modèle ;
- `prolog.py` : trouve SWI-Prolog, lui fait charger le moteur et les règles, pose les faits (vérifiés : rien ne peut être injecté), lit la décision en JSON ; `extraire_faits_regles` fait lire la déclaration par le modèle, dans le vocabulaire, en laissant inconnu ce qu'elle ne dit pas ; `PipelineRegles` assemble et met en forme ;
- `couverture regles --contrat <id>` : vérifie le chargement sans avertissement, le vocabulaire, les citations (mot pour mot dans les clauses), et les cas.
- **Raisonnement par hypothèses** (`explorer/2` dans `moteur.pl`) : quand la décision dépend de faits inconnus, le moteur essaie chaque réponse possible (assertz, décision, retract) et classe chaque question : décisive (« oui → couvert ; non → non couvert »), utile, ou inutile (plus posée) ; sans question décisive, il cherche une paire qui tranche. Les valeurs possibles viennent de `vocabulaire.json`. L'oracle Python (`Explorateur`) refait le même calcul pour le test différentiel ;
- `regles/<contrat>.pl` déclare aussi `evenement_traduit(...)` : un événement déclaré dont la garantie n'est pas encore traduite (la tempête, par exemple) empêche le moteur de refuser, il répond « à examiner » ;
- `src/couverture/redaction.py` (`couverture rediger --article 2.2`) : **Mistral Large rédige les règles d'une garantie**. Il remplit un schéma JSON (le code écrit le Prolog), déclare les faits qui manquent au vocabulaire et ce qu'il ne sait pas traduire ; six contrôles (structure, vocabulaire, citations, couverture de chaque exclusion du contrat, concepts et identifiants, chargement et non-régression) ; les propositions restent dans `regles/propositions/` jusqu'à `--accepter`, refusé tant qu'un contrôle bloque.

**Pourquoi** : les fiches ne savaient pas représenter une condition cachée dans un tableau de limites ni une exclusion cachée dans une définition ; une règle les exprime directement. La décision devient un calcul reproductible. Les tests utilisent aussi `tests/moteur_reference.py`, une seconde implémentation du moteur en Python : là où SWI-Prolog est installé, un test vérifie que les deux concordent.

### `src/couverture/banc.py` et `data/golden/` — le banc d'essai

**Rôle** : rejouer tout le système sur un jeu de référence figé (le *golden set*, 68 cas étiquetés par garantie, thème, origine et auteur), en trois couches : les **règles** seules sur les faits idéaux, la **lecture** des faits par le modèle comparée aux faits idéaux, la **chaîne** complète sur plusieurs exécutions. Des **portes** (`data/golden/seuils.json`) disent si c'est présentable ; la commande `couverture banc` sort en erreur si une porte échoue. Chaque passage est gardé dans `data/bancs/` et comparé au précédent. `--figer` versionne le golden set ; `--fiche` écrit la fiche de validation des réponses attendues.

**Pourquoi** : un score unique dit qu'il y a une erreur ; trois couches disent si elle vient des règles, de la lecture ou de leur combinaison. Et une référence qui change sans le dire ne mesure plus rien.

### `src/couverture/relecture.py` — le juge de la grille


**Depuis la consigne v2** : le relecteur répond lui-même aux questions décisives, sans voir la réponse de la première analyse ; le code compare et ne conteste que si les deux réponses diffèrent (voir `docs/DEMARCHE.md`, 7.14 sexies).
**Le problème qu'il règle** : le contrôle des citations vérifie qu'un passage **existe** dans le contrat. Il ne vérifie pas qu'il **justifie** l'état donné. Le modèle peut citer la bonne exclusion et se tromper sur son application aux faits.

**Rôle** : après le calcul de la décision, un second appel au modèle reçoit, pour chaque condition qui pèse sur la décision, le sinistre, le texte complet de la clause (pas seulement l'extrait), la question, l'état proposé et la justification du premier appel. Il **ne voit pas la décision**. Consigne : vérifier la justification au lieu de s'y fier, et contester dans le doute.

**Ce qui est relu** (`a_relire`), selon la décision :
- NON_COUVERT : les conditions décisives (l'exclusion qui s'applique, ou les conditions non remplies) ;
- COUVERT : les conditions de la garantie retenue, **et les exclusions jugées non applicables**. C'est là que se cache l'erreur la plus coûteuse : une exclusion écartée à tort donne un « couvert » à tort ;
- INCERTAIN : rien, la réponse admet déjà sa limite (et on économise un appel).

**Ce qui se passe** (`relire`) : une condition confirmée garde son état. Une condition contestée redevient INCONNUE ; son état d'origine est gardé (`etat_propose`), avec la raison et la question à poser. Une condition sur laquelle le relecteur ne se prononce pas est considérée comme contestée. Puis la décision est **recalculée par les mêmes règles**. Comme une contestation ne fait que remplacer un état certain par INCONNUE, la relecture **ne peut que rendre la réponse plus prudente**, jamais l'inverse. La décision d'avant est gardée (`decision_avant_relecture`) pour mesurer l'effet de la relecture.

**Si la relecture est en panne** : la décision reste, avec un avertissement et une confiance plafonnée à 0,6. C'est un contrôle, pas une étape indispensable (même principe que le juge de SortirIA).

**Configuration** : par défaut, le même modèle que le juge principal, dans un appel séparé. `COUVERTURE_MODELE_RELECTURE` permet un autre modèle (par exemple `mistral-small-latest`, moins cher, ou un autre modèle pour une relecture plus indépendante). `COUVERTURE_RELECTURE=non` la désactive.

**Pourquoi** : c'est le cœur de la consigne, « citer ses sources et admettre ses limites ». Une citation qui existe mais ne prouve rien ne doit pas suffire. Et l'indicateur `faux_couverts_evites_par_relecture` mesure directement ce que la relecture apporte.

### `src/couverture/qualite.py` — le juge de qualité à l'ingestion

**Le problème qu'il règle** : les contrôles vérifient qu'un contrat a des garanties et des exclusions, pas que ce **sont** les bonnes. Une exclusion typée « garantie » passe les contrôles, et peut faire dire « couvert » à tort.

**Rôle** :
- `echantillon` : 16 clauses, **stratifiées par type** (chaque type est représenté) et **reproductibles** (tirées avec l'empreinte du contrat comme graine : même contrat, même échantillon) ;
- `juger_qualite` : Mistral dit, pour chaque clause, si son type est juste et lequel il proposerait. Score = part de types confirmés ;
- `appliquer` : sous le seuil de 80 %, une alerte « Typage douteux » est ajoutée et le contrat passe `A_VERIFIER`. Les erreurs relevées (titre, type actuel, type proposé) sont transmises à l'agent de réparation, qui les reçoit dans son prompt, et sa vérification compte combien de ces types le profil corrige.

Lancé à l'ingestion quand un modèle est configuré ; un contrat déjà ingéré sans score est jugé à la prochaine ingestion. **Une panne du juge ne bloque jamais l'ingestion** : le rapport note l'erreur, le statut ne change pas.

**Pourquoi un échantillon** : juger toutes les clauses coûterait un appel long par contrat pour peu d'information en plus ; 16 clauses suffisent à repérer un contrat dont le typage est faux de façon systématique. C'est la même logique que `judge_quality` dans SortirIA.

### `src/couverture/journal.py` — le journal des analyses

**Rôle** : chaque analyse faite par l'interface ou par `couverture analyser` est notée dans la table `analyses` : date, contrat, méthode, juge, décision (avant contrôle, avant relecture, finale), confiance, faits repérés (événement, bien, lieu), citations rejetées, conditions écartées, contestations, questions à poser, durée. Les erreurs du modèle sont notées aussi.

**Ce qui n'est pas noté** : le texte du sinistre, seulement sa longueur. Une déclaration de sinistre peut contenir des données personnelles ; le journal n'en a pas besoin.

**Pourquoi** : l'évaluation mesure le système sur 14 cas écrits à l'avance. Le journal mesure ce qui se passe vraiment, et alimente la dérive et le bilan (comme `search_log.py` dans SortirIA).

### `src/couverture/derive.py` — la dérive

**Rôle** : `calculer` compare les 7 derniers jours aux 28 précédents, avec le PSI, sur trois familles de variables :
- **les questions** (type d'événement, bien, lieu) : les sinistres déclarés changent (saison, nouveau produit) ; le jeu de test n'est peut-être plus représentatif ;
- **les réponses** (décision, niveau de confiance) : le système répond autrement ; un contrat mal lu, ou un modèle changé par le fournisseur ;
- **la fiabilité** (contestations, citations rejetées) : le modèle se trompe plus souvent.

Et **par contrat** : un taux d'INCERTAIN d'au moins 60 %, en hausse de 20 points, sur au moins 10 analyses, déclenche une alerte : c'est souvent un contrat mal lu.

En dessous de 30 analyses dans chaque période, la dérive n'est pas calculée : elle n'aurait pas de sens. Les petites parts sont lissées (0,0001) pour que le logarithme reste défini.

**Pourquoi le PSI** : simple, lisible, avec des seuils connus ; c'est la méthode déjà utilisée dans SortirIA (et dans le projet de scoring crédit avant lui).

### `src/couverture/bilan.py` — le bilan

**Rôle** : `construire_bilan` écrit un rapport Markdown, dans cet ordre :
1. **À faire** : contrats à vérifier (avec la commande à lancer), propositions de réparation en attente, dérives fortes, erreurs du modèle ;
2. **Contrats** : statut de lecture, score du juge de qualité, nombre d'alertes ;
3. **Activité** : nombre d'analyses, répartition des décisions, réponses corrigées par le contrôle des citations, contestations de la relecture et décisions changées, citations écartées, temps de réponse médian ;
4. **Ce qui manque** : les questions à poser à l'assuré qui reviennent le plus. C'est la liste des informations à aller chercher ailleurs ; si « l'option vélo est-elle souscrite ? » revient 50 fois, il est temps de lire les conditions particulières ;
5. **Dérive**.

`couverture bilan` l'enregistre dans `data/bilans/` et l'affiche ; `--envoyer` l'envoie par mail si un serveur SMTP est configuré dans `.env` (`SMTP_HOTE`, `SMTP_PORT`, `SMTP_UTILISATEUR`, `SMTP_MOT_DE_PASSE`, `BILAN_DESTINATAIRE`).

**Pourquoi** : comme le mail du lundi de SortirIA, il ne raconte pas tout ; il dit d'abord ce qui demande une intervention humaine.

### `src/couverture/consignes.py` — le versionnage des consignes

**Rôle** : `CONSIGNES` liste les dix consignes en service (grille de conditions, relecture, document brut, juge de qualité, réparation, compilation, exclusions générales, fiches, routage, faits), le texte qui porte chacune dans le code, et sa version.
- **archive** : `ecrire_manifeste` écrit aussi le texte intégral de chaque nouvelle version dans `docs/consignes/<consigne>/<version>.txt`, sans jamais réécrire une version archivée. `verifier` échoue si le texte d'une version en service ne correspond plus à son archive. L'histoire des consignes (grille v1, v2, v3) reste ainsi lisible, avec le pourquoi de chaque changement dans `docs/DEMARCHE.md` ;
- `etat_actuel` calcule la version et l'empreinte de chaque texte ; `ecrire_manifeste` les écrit dans `config/versions_consignes.json` ;
- `verifier` compare le code au manifeste et signale un texte modifié **sans nouvelle version**, ou un manifeste pas à jour. Un test l'appelle : la CI échoue ;
- `versions_courtes` (« grille-conditions:v1,relecture:v1… ») est notée dans le journal à chaque analyse et dans chaque exécution MLflow ;
- `enregistrer_dans_mlflow` crée une version au **Prompt Registry** de MLflow pour chaque texte différent, et pose l'alias `production` sur celle en service. Relancé sans changement, il ne crée rien.

**Pourquoi** : une consigne modifiée change les réponses. Pour comparer deux versions, ou comprendre une réponse passée, il faut savoir quelle consigne l'a produite. C'est la même règle que SortirIA (`scripts/versionnage.py`).

### `src/couverture/suivi.py` — le suivi MLflow

**Rôle** :
- **une ingestion = une exécution** (expérience `couverture-ingestion`) : versions des consignes, modèles, et par contrat le nombre de clauses par type, les alertes, le statut, le score du juge de qualité ; artefact : les rapports de contrôle ;
- **une évaluation = une exécution** (expérience `couverture-evaluation`, une par méthode avec `couverture comparer`) : contrat et son empreinte, méthode, modèles du juge, du relecteur et des embeddings, versions des consignes, **empreinte du jeu de test** ; toutes les métriques de l'évaluation ; artefact : le rapport cas par cas.

Les fonctions qui calculent paramètres et métriques sont pures et testées sans MLflow. `execution` ouvre une exécution et renvoie un objet dont les méthodes **ne lèvent jamais** : sans MLflow, avec `MLFLOW_ACTIF=false`, avec un serveur qui ne répond pas en 3 s, ou en cas d'erreur, le travail continue sans suivi.

**Pourquoi** : c'est ce qui rend les comparaisons sérieuses. Deux exécutions avec la même empreinte de jeu de test et deux versions de consigne différentes se comparent directement ; deux modèles aussi. Et l'empreinte du jeu de test empêche de comparer des chiffres obtenus sur des cas différents.

### `monitoring/grafana/` — les tableaux de bord

**Rôle** : `construire_tableaux.py` écrit les deux tableaux en JSON, dans `provisioning/dashboards/`, chargés automatiquement par Grafana avec la source SQLite (`provisioning/datasources/sqlite.yml`).
- **Réponses** : usage, décisions par jour, part d'INCERTAIN, rattrapages par jour (contestations, décisions changées par la relecture, réponses corrigées par le contrôle, preuves écartées), temps de réponse, INCERTAIN par contrat, sinistres déclarés, questions à poser les plus fréquentes, versions des consignes en service avec leurs résultats, dernières erreurs ;
- **Contrats** : lecture de chaque contrat, qualité du typage, clauses par type, alertes, types contestés par le juge de qualité.

Les requêtes utilisent les macros de période du plugin (`$__unixEpochFrom()`, `$__unixEpochTo()`) et les fonctions JSON de SQLite (`json_each`, `json_extract`) pour lire les rapports et les questions.

**Pourquoi un générateur** : un tableau Grafana est un JSON illisible ; ici les requêtes sont écrites en clair, et un test les exécute toutes sur une vraie base et vérifie que le JSON est à jour (même méthode que `construire_tableau_modeles.py` dans SortirIA). **Pourquoi SQLite** : garder le projet petit ; avec PostgreSQL, comme dans SortirIA, seules la source et quelques fonctions changeraient.

### `docker-compose.yml` et `.github/workflows/ci.yml`

- **docker compose** lance l'application (ports 8020), MLflow (5010) et Grafana (3011). L'application lit les contrats au démarrage puis sert l'interface ; la base `data/base.sqlite` est partagée avec Grafana, en lecture seule. Les ports évitent ceux de SortirIA.
- **La CI** installe le projet, vérifie les versions des consignes, puis lance les tests.

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

### `src/couverture/pipeline.py` — l'assemblage

**Rôle** :
- `llm_configure` : choisit le modèle selon les variables d'environnement, ou aucun.
- `juge_par_defaut` : conditions avec un modèle ; heuristique sans modèle. La méthode `fiches` a son propre assemblage (`fiches.PipelineFiches`).
- `Pipeline.analyser` : faits → requête enrichie → recherche → juge → validation → `Resultat`. Construit depuis la base (`depuis_base`) ou depuis un fichier (`depuis_fichier`).
- `PipelineDocumentBrut` : la référence, avec le même contrôle des citations pour que la comparaison soit juste.

### `src/couverture/evaluation.py` — mesurer

**Rôle** :
- `charger_cas` : croise `data/sinistres.jsonl` (les sinistres) et `data/annotations/<contrat>.jsonl` (la réponse attendue pour ce contrat).
- `evaluer` : rejoue chaque cas et calcule les indicateurs (voir la section 7). Une clause attendue « 4.4 » est considérée comme citée si la clause 4.4 ou l'un de ses morceaux (`4.4~2`, `4.4/terme`) l'est.

**Pourquoi** : on ne peut pas dire qu'une méthode est meilleure sans la mesurer. Séparer sinistres et annotations permet de rejouer les mêmes sinistres sur chaque nouveau contrat.

### `src/couverture/cli.py` — la ligne de commande

| Commande | Effet |
|---|---|
| `couverture ingerer [--forcer]` | Lit `data/contrats`, remplit la base ; avec une clé Mistral, calcule les embeddings et fait juger le typage ; affiche statuts, scores et alertes. |
| `couverture contrats` | Liste les contrats, leur statut, leur version. |
| `couverture clauses --contrat ID` | Affiche le découpage : identifiant, type, pages, titre. |
| `couverture analyser --contrat ID "…" [--methode conditions\|fiches\|brut] [--detail] [--json] [--hors-ligne]` | Analyse un sinistre : décision, motif, preuves décisives, questions à poser. `--detail` montre toutes les fiches ; `--json` la sortie complète, pour la traçabilité. |
| `couverture evaluer --contrat ID [--methode …] [--detail]` | Indicateurs sur les cas annotés de ce contrat. |
| `couverture comparer --contrat ID` | Les trois méthodes côte à côte (modèle requis). |
| `couverture serveur [--port 8000]` | Lance l'interface web. |
| `couverture derive [--jours 7] [--reference 28]` | Le PSI de chaque variable, les taux d'INCERTAIN par contrat et les alertes. |
| `couverture bilan [--jours 7] [--sortie F] [--envoyer]` | Le bilan de la période, écrit dans `data/bilans/`, et envoyé par mail si demandé. |
| `couverture versions [--manifeste \| --enregistrer]` | Vérifie les versions des consignes ; réécrit le manifeste ; les enregistre dans MLflow. |
| `couverture modele` | Affiche le modèle configuré et teste la connexion (génération et embeddings). |
| `couverture reparer [--contrat ID]` | Propose un profil d'assureur pour les contrats à vérifier. N'applique rien. |
| `couverture propositions [--accepter N \| --refuser N]` | Liste les propositions, avec leur avant/après ; en accepte (et relit le contrat) ou en refuse une. |

### `src/couverture/web.py` et `static/index.html` — l'interface

**L'API** (Starlette) :
- `GET /` : la page ;
- `GET /api/contrats` : contrats, statut, alertes, et le modèle configuré ;
- `GET /api/contrats/{id}/clauses` : toutes les clauses, pour afficher leur texte complet ;
- `POST /api/analyser` : `{contrat_id, sinistre, methode}` → le résultat complet. Chaque analyse est notée dans le journal. La description doit faire entre 10 et 2 000 caractères. Les pipelines sont gardés en mémoire par contrat et par méthode.

**La page** (HTML et JavaScript sans framework) :
- choix du contrat (avec un avertissement s'il est `A_VERIFIER`), de la méthode (si un modèle est configuré), description du sinistre, boutons d'exemple avec les deux cas du recruteur ;
- résultat : la décision en grand avec la confiance, la justification, et un message si le contrôle a corrigé le modèle ;
- **la grille, condition par condition** : pour chaque ligne, un état coloré (« Remplie », « Non remplie », « Inconnu » ; pour une exclusion, « S'applique » ou « Ne s'applique pas »), l'énoncé, la justification, l'extrait avec l'article et la page, le badge « décisif », et le texte complet de la clause avec le passage surligné ;
- pour chaque condition relue : « ✓ Confirmée par la relecture » ou « ⚠ Contestée par la relecture », avec l'état d'origine et la raison ; un message en haut si la relecture a changé la décision ;
- « Comment la réponse a été construite » : chaque clause lue et la raison de sa sélection.

Le contenu est inséré comme du texte, jamais comme du HTML, pour éviter qu'un contenu malveillant s'exécute dans la page.

**Pourquoi** : le recruteur demande une restitution claire et déconseille Streamlit. L'interface montre exactement ce qu'il veut voir : les sources, et les limites.

### `src/couverture/__init__.py`

Expose `Pipeline`, `Resultat`, `Verdict`, `Decision` pour un usage en Python, et la version du paquet.

### Fichiers à la racine

| Fichier | Rôle |
|---|---|
| `pyproject.toml` | Le paquet Python : dépendances (pydantic, pdfplumber, starlette, uvicorn), la commande `couverture`, la configuration de pytest. |
| `Dockerfile` | Construit une image qui installe le paquet, ingère les contrats et lance le serveur. La clé du modèle est passée au lancement, jamais écrite dans l'image. |
| `.gitignore` | Exclut la base générée, les caches, le fichier `.env` (les clés) et **les PDF des assureurs** (on ne redistribue pas leurs documents). |
| `README.md` | La présentation du projet. |

---

## 5. Les données

| Fichier | Contenu |
|---|---|
| `data/contrats/catalogue.json` | Nom de fichier → identifiant, assureur, produit, version. |
| `data/contrats/SOURCES.md` | Les liens de téléchargement des CG réelles : Foyer appart 123 (2025), AXA Luxembourg OptiHome (2017), Société Générale (2025), MACSF. Les CG de Foyer Mozaïk ne sont pas publiques. |
| `data/contrats/fictif_habitat_serein.md` | Un contrat **inventé**, écrit pour contenir les pièges classiques (local collectif, cave privative, bougie avec ou sans flammes, options). |
| `data/sinistres.jsonl` | 14 sinistres indépendants des contrats : les deux du recruteur, des variations qui changent **un seul fait**, et deux cas de contrôle (téléphone arraché, fuite du lave-linge). Le champ `pieges` dit ce que le système ne doit pas manquer. |
| `data/annotations/<contrat>.jsonl` | Pour un contrat : la décision attendue, les clauses qui doivent être citées, et une note qui explique. Fait pour le contrat fictif ; à faire pour Foyer. |
| `data/profils/<nom>.json` | Les profils d'assureur acceptés. Vide au départ : le contrat Foyer est lu correctement par les règles générales. |
| `data/bilans/` | Les bilans écrits par `couverture bilan` (non versionnés). |
| `data/propositions/` | Les propositions de réparation, avec leur statut : la trace de chaque décision humaine. |
| `tests/fixtures/cg_style_reel.pdf` | Un PDF fictif mis en page comme un vrai contrat (sommaire, en-têtes, lexique, intertitres sans numéro, mots coupés), produit par `generer_pdf.py`. |

**Pourquoi des variations à un seul fait** : si la réponse change quand on passe du local commun à la cave privative fermée à clé, c'est que le système raisonne vraiment sur le contrat, et pas qu'il répète une réponse apprise.

---

## 6. Les tests

`pytest` lance 62 tests dans `tests/test_pipeline.py` :
- **Lecture et découpage** : types des clauses, retrait du sommaire et des en-têtes, mots recollés, intertitres sans numéro, lexique éclaté, renvois.
- **Base** : ingestion de deux contrats sans mélange, renvois relus depuis la base, ré-ingestion d'un fichier inchangé sans traitement.
- **Recherche** : la garantie, son exclusion et la définition utile sont ramenées ; les renvois sont suivis.
- **Contrôle des citations** : une citation inventée fait passer COUVERT à INCERTAIN ; une clause non fournie est rejetée ; le rôle vient du contrat ; une réponse illisible donne INCERTAIN.
- **Juge par conditions** : exclusion remplie → non couvert ; tout rempli → couvert ; inconnu → incertain avec la question ; exclusion inconnue → incertain ; exclusion inventée → écartée et sans effet.
- **Document brut** : les citations sont retrouvées dans les clauses.
- **Évaluation** : le jeu de test est cohérent ; l'heuristique ne dit jamais « couvert » à tort.
- **Configuration du modèle** : lecture du `.env`, choix de Mistral, valeur d'exemple ignorée, requête envoyée à Mistral (adresse, clé, mode JSON, température 0), nouvelle tentative après une limite de débit, message clair si la clé est refusée. Aucun appel réel : la connexion est simulée.
- **Recherche hybride** : une question sans aucun mot commun avec le contrat (« chouravé ») retrouve la garantie vol par le sens, et l'enveloppe ramène son exclusion ; sans vecteurs, la recherche reste lexicale ; les vecteurs sont calculés une seule fois, y compris si la clé arrive après ; une panne des embeddings ne bloque pas l'ingestion. Les embeddings sont simulés.
- **Profils** : un intertitre propre à l'assureur change le typage ; un profil mal formé est refusé.
- **Agent de réparation** : la vérification garde l'intertitre réel et écarte l'intertitre inventé et le motif qui effacerait une garantie ; la proposition n'est pas appliquée avant acceptation ; l'acceptation écrit le profil et le catalogue ; une proposition sans amélioration est refusée par la vérification.
- **Juge de la grille** : une relecture qui confirme ne change rien ; une relecture qui conteste l'exclusion fait passer NON_COUVERT à INCERTAIN avec la question à poser ; une exclusion écartée à tort et contestée **évite un faux « couvert »** ; une relecture en panne laisse la décision avec un avertissement ; rien n'est relu quand la réponse est déjà INCERTAIN.
- **Juge de qualité** : l'échantillon est stratifié et reproductible ; un type contesté fait baisser le score, ajoute l'alerte et la famille « typage douteux » ; une panne ne bloque pas l'ingestion ; la vérification d'une réparation compte les types qu'elle corrige.
- **Journal, dérive, bilan** : le PSI vaut 0 sur deux distributions identiques et dépasse 0,25 sur deux distributions inversées ; la dérive est « stable » puis « forte » quand les sinistres changent, avec une alerte sur le contrat dont l'INCERTAIN explose ; le bilan compte les analyses et les erreurs et liste la question qui revient ; le journal ne garde pas le texte du sinistre.
- **Versionnage et MLflow** : le manifeste est à jour ; un texte changé sans version est détecté ; l'enregistrement au Prompt Registry pose l'alias `production` et ne recrée rien la seconde fois ; les métriques d'ingestion et d'évaluation sont justes ; une exécution enregistre paramètres, métriques et artefact dans l'ordre, et une erreur du suivi ne remonte jamais. MLflow est simulé.
- **Grafana** : le JSON est à jour ; chaque requête s'exécute sur une vraie base remplie, avec les bons comptes ; chaque série temporelle a sa colonne `time`.
- **Ligne de commande** : ingestion, évaluation, bilan et versions de bout en bout.
- **Contrat réel** (si le PDF Foyer est présent) : statut OK, exclusion des parties communes trouvée en 2.10-a, plus de 40 définitions, et la recherche du vélo ramène 2.10 et 2.10-a.

Les tests du juge utilisent un **faux modèle** qui renvoie une réponse préparée : on teste les règles et les contrôles sans dépendre d'un modèle réel.

---

## 7. L'évaluation et ses indicateurs

| Indicateur | Ce qu'il mesure |
|---|---|
| `exactitude` | Part des décisions identiques à la décision attendue. |
| `exactitude_avant_controle` | La même chose, avant le contrôle des citations. L'écart montre ce que le contrôle corrige. |
| `faux_couverts` | Nombre de « couvert » à tort. **L'indicateur le plus important** : c'est une promesse faite au client. |
| `faux_couverts_avant_controle` | La même chose avant contrôle. |
| `taux_incertain` | Part d'INCERTAIN. Trop haut : le système ne sert à rien. Trop bas sur des cas ambigus : il tranche au hasard. |
| `rappel_clauses_moyen` | Part des clauses attendues effectivement citées : la qualité de la justification. |
| `citations_rejetees` | Nombre de citations introuvables : la fréquence des hallucinations. |
| `conditions_contestees` | Nombre de conditions contestées par la relecture. |
| `decisions_changees_par_relecture` | Nombre de décisions que la relecture a fait changer. |
| `faux_couverts_evites_par_relecture` | « Couvert » que la relecture a fait tomber, alors que la bonne réponse n'était pas « couvert ». **Ce que la relecture apporte, en un chiffre.** |
| `confusion` | Pour chaque décision attendue, les décisions obtenues. |

**Où on en est** : sur le contrat fictif, le juge heuristique donne 7 décisions exactes sur 14, aucun faux « couvert », aucune citation rejetée, et 63 % des clauses attendues citées. Les trois méthodes avec un vrai modèle restent à mesurer (`couverture comparer`).

---

## 8. Les choix, résumés

| Choix | Raison | Écarté |
|---|---|---|
| Structurer chaque contrat une fois, à l'ingestion | Vérifiable, réutilisable, tient à l'échelle | Coller le PDF dans le prompt à chaque question |
| Une clause = une unité du contrat | Citations précises, type connu | Morceaux de taille fixe |
| Lexique éclaté terme par terme | Le sens d'un mot est celui du contrat | Le laisser en un seul bloc |
| Recherche + enveloppe structurelle | L'exclusion ne ressemble pas à la question | Les k passages les plus proches |
| Recherche hybride mots + sens, fusion RRF | Les mots retrouvent les termes du contrat, le sens retrouve la langue du client ; RRF sans poids à régler (repris de SortirIA) | Embeddings seuls, ou BM25 seul |
| Embeddings calculés une fois, à l'ingestion | Coût payé une fois par contrat ; panne non bloquante | Vectoriser à chaque question |
| Profils d'assureur en JSON | Un assureur différent = un fichier, pas du code | Ajouter des cas particuliers dans `segmentation.py` |
| Juge de la grille, indépendant, qui ne voit pas la décision | Une citation qui existe ne prouve pas l'état ; la relecture ne peut que rendre plus prudent | Faire confiance au premier appel, ou demander au même appel de « vérifier son travail » |
| Compiler chaque garantie en fiche, une fois | Les conditions appartiennent au contrat ; contrôlées une fois par le code et par un humain ; aucune exclusion oubliée par la recherche | Les faire reformuler par le modèle à chaque sinistre (gardé : méthode `conditions`, pour comparer) |
| Exclusions « présumées absentes » | Un gestionnaire présume la bonne foi ; sinon toute réponse serait INCERTAIN | Traiter toutes les exclusions inconnues comme bloquantes |
| Décision fiche par fiche | Une exclusion du vol ne doit pas faire tomber la garantie incendie | Une seule grille où toute exclusion vaut pour tout |
| Réflexion du modèle courte (`low`) | Mistral Large 4 réfléchit au maximum par défaut : minutes et milliers de tokens avant de répondre | Repousser la limite de tokens (essayé, voir `DEMARCHE.md`) |
| Archiver le texte de chaque version de consigne | Comprendre une réponse passée, raconter la démarche | Garder seulement l'empreinte |
| Juge de qualité sur un échantillon | Les contrôles comptent les exclusions, pas leur justesse ; un échantillon suffit et coûte peu | Juger toutes les clauses, ou ne rien juger |
| Journal sans le texte du sinistre | Mesurer en production sans stocker de données personnelles | Garder les déclarations |
| Dérive par PSI, bilan « à faire d'abord » | Méthode simple et éprouvée (SortirIA) ; un humain ne lit que ce qui le concerne | Tableaux de bord exhaustifs |
| Consignes versionnées, garde-fou en CI | Savoir quelle consigne a produit une réponse ; impossible de changer un texte en silence | Prompts modifiés sans trace |
| MLflow : une ingestion, une évaluation = une exécution | Comparer versions et modèles sur un même jeu de test (même empreinte) | Comparer des chiffres notés à la main |
| Grafana sur SQLite, tableaux générés et testés | Pas de base de plus à faire tourner ; requêtes lisibles et vérifiées | PostgreSQL pour un projet de démonstration ; JSON édité à la main |
| Pas de LangGraph | La chaîne est linéaire ; un graphe n'apporterait que de la complexité | Reprendre le graphe de SortirIA par habitude |
| Agent de réparation : propose, le code vérifie, un humain décide | Un profil faux ferait dire « couvert » à tort ; même règle que SortirIA | Laisser l'IA corriger seule, ou tout corriger à la main |
| Grille de conditions, décision par règles | Petites étapes vérifiables, incertitude précise | Verdict du modèle en un coup |
| Contrôle des citations par du code | Bloque les hallucinations de façon fiable | Faire confiance au modèle |
| Rôle des citations repris du contrat | Le modèle ne peut pas présenter une exclusion comme une garantie | Rôle déclaré par le modèle |
| Contrôles d'ingestion, statut A_VERIFIER | Personne ne relit des centaines de découpages | Servir tous les contrats sans contrôle |
| SQLite, recherche filtrée par contrat | Jamais de mélange entre contrats ; simple | Un index unique pour tous les contrats |
| Modèle interchangeable | Données sensibles : modèle interne possible | Dépendre d'un seul fournisseur |
| Jeu de test écrit avant le code, avec variations | Mesurer, et prouver le raisonnement | Juger « à l'œil » |
| Faux « couvert » comptés à part | L'erreur la plus coûteuse | Une seule exactitude globale |
| Interface HTML simple | Restitution claire, déconseil de Streamlit | Streamlit |

---

## 9. Les questions qu'on peut vous poser

**Pourquoi une recherche hybride ?**
Les termes d'un contrat sont précis (« effraction », « dépendance ») : les mots les retrouvent bien. Mais le client parle avec ses mots (« on m'a piqué mon vélo ») : le sens fait le pont. La fusion RRF combine les deux sans poids à régler ; c'est la méthode de SortirIA, en production. Et dans tous les cas, la clause qui décide, l'exclusion, est ramenée par la structure du contrat (l'enveloppe), pas par la ressemblance.

**Pourquoi SQLite et pas pgvector ?**
Pour garder un projet petit qui tourne partout. Quelques centaines de clauses par contrat se comparent en Python sans problème. En production : PostgreSQL + pgvector, comme dans SortirIA, avec le même schéma.

**Pourquoi ne pas tout confier au modèle ?**
Parce qu'en assurance, une réponse non vérifiable ne vaut rien. Le modèle fait ce qu'il fait bien (lire une clause, la confronter à un fait) ; les règles et les contrôles font ce que le code fait bien (appliquer une logique, vérifier qu'un texte existe).

**Que se passe-t-il avec un contrat au format inhabituel ?**
Les contrôles le signalent `A_VERIFIER` : peu de clauses, pas d'exclusion trouvée, etc. Il n'est pas servi en silence. L'agent de réparation propose alors un profil d'assureur ; le code le vérifie (lignes réelles, avant/après, aucune garantie effacée) ; vous l'acceptez ou le refusez. Le profil sert ensuite à toutes les versions de cet assureur.

**Pourquoi l'agent n'applique-t-il pas lui-même sa réparation ?**
Parce qu'un profil faux pourrait faire passer une exclusion pour une garantie, donc dire « couvert » à tort. C'est la même règle que dans SortirIA, où une adresse « trouvée » pourrait être le mauvais document : l'agent propose, un humain décide, et chaque décision est tracée dans `data/propositions/`.

**Comment tenir des centaines de contrats ?**
Chaque contrat est lu une fois, contrôlé, stocké dans le même schéma, avec ses embeddings. Les contrats mal lus sont signalés et réparés par un profil d'assureur, proposé par l'IA et validé par un humain, une fois par assureur. Chaque question ne porte que sur un contrat. Les sinistres de test sont réutilisés ; un nouveau contrat ne demande qu'un fichier d'annotations. La version compte, et les conditions particulières viendront remplir les conditions de la grille.

**Et si le modèle se trompe sur l'état d'une condition ?**
L'erreur est visible ligne par ligne, avec sa justification, au lieu d'être cachée dans un verdict global. On peut la mesurer, l'annoter, et ajuster le prompt sur cette condition précise.

**Pourquoi un second juge ? Le premier ne suffit pas ?**
Le premier appel remplit la grille ; s'il se trompe sur l'application d'une clause, sa citation existe quand même et passe le contrôle. Le relecteur reçoit le texte complet de la clause, ne voit pas la décision, et doit vérifier la justification. Il ne peut que rendre la réponse plus prudente : au pire, il coûte un INCERTAIN de trop ; au mieux, il évite un « couvert » à tort. On mesure les deux.

**Le relecteur n'est-il pas le même modèle, avec les mêmes biais ?**
Par défaut, oui, mais dans un appel séparé, avec une autre consigne et sans voir la conclusion. Pour plus d'indépendance, `COUVERTURE_MODELE_RELECTURE` permet un autre modèle. C'est un compromis coût / indépendance, à régler avec les mesures.

**Comment savez-vous que le système se dégrade en production ?**
Grafana montre, jour par jour, la part d'INCERTAIN, ce que la relecture et le contrôle des citations rattrapent, et les erreurs du modèle. Le journal note chaque analyse avec les versions des consignes qui l'ont produite ; la dérive compare la semaine aux quatre précédentes sur les questions, les réponses et la fiabilité ; un contrat dont le taux d'INCERTAIN explose est signalé. Le bilan hebdomadaire dit d'abord ce qui demande une intervention. C'est le dispositif de SortirIA, en production.

**Pourquoi un juge sans modèle ?**
Pour faire tourner et tester le système sans clé, et comme filet de sécurité. Il est volontairement prudent.

**Pourquoi INCERTAIN est-il une bonne réponse ?**
Parce que c'est la consigne : un « je ne sais pas » étayé vaut mieux qu'une réponse assurée sans justification. Et ici, INCERTAIN dit précisément quoi demander à l'assuré.

**Quel lien avec SortirIA ?**
Le même problème de fond : des sources hétérogènes à ramener dans un schéma commun et fiable. SortirIA le fait pour des dizaines d'agendas, en production sur Azure. Ce projet en reprend la recherche hybride (mots + sens, RRF), l'agent qui propose des réparations validées par un humain, le juge de qualité, la dérive par PSI, le bilan, le suivi MLflow avec les consignes versionnées et le garde-fou en CI, et les tableaux Grafana générés et testés. Il n’en reprend pas le graphe LangGraph, qui n'aurait pas d'utilité ici. La différence : SortirIA recommande, une approximation reste utile ; ici le système décide, une erreur est une promesse faite au client, d'où le contrôle des citations, la décision calculée et le droit de répondre INCERTAIN.

**Comment comparez-vous deux versions d'une consigne, ou deux modèles ?**
Chaque évaluation est une exécution MLflow qui porte les versions des consignes, les modèles et l'empreinte du jeu de test. Deux exécutions avec la même empreinte se comparent directement, sur les faux « couvert » d'abord. Et une consigne ne peut pas changer sans nouvelle version : la CI échoue.

**Comment avez-vous utilisé l'IA ?**
Pour écrire le code et l'interface plus vite, comme le recruteur l'encourage. Les choix d'architecture, l'évaluation et la vérification sur un vrai contrat restent les vôtres : vous devez pouvoir expliquer chaque fichier de ce document.

---

## 10. Limites et suites

**Limites actuelles**
- Les conditions particulières ne sont pas lues : beaucoup d'INCERTAIN viennent de là (« l'option est-elle souscrite ? »).
- Le pont entre la langue du client et celle du contrat (`faits.py`) est écrit à la main pour l'habitation ; la recherche par le sens le complète, mais l'extraction des faits reste à confier au modèle.
- Le découpage repose sur des règles et des profils ; un format très inhabituel (sans aucun titre reconnaissable) dépassera ce qu'un profil peut décrire.
- Les tableaux de plafonds sont lus comme du texte, sans leur structure.
- Les méthodes avec un vrai modèle, les vrais embeddings, les deux juges et l'agent de réparation ne sont pas encore mesurés avec Mistral ; la dérive n'aura de sens qu'avec des semaines d'utilisation réelle.
- Le relecteur est, par défaut, le même modèle que le juge principal.

**Suites, dans l'ordre**
1. Coller la clé Mistral dans `.env`, vérifier avec `couverture modele`, puis lancer `couverture comparer` : le tableau brut / conditions / fiches.
2. Écrire les annotations du contrat Foyer, puis d'un ou deux autres contrats.
3. Lire les conditions particulières pour remplir les conditions « option souscrite ».
4. Ajouter un contrat que les règles générales lisent mal (AXA Luxembourg, par exemple) et faire tourner l'agent de réparation dessus : c'est la démonstration la plus parlante pour « des centaines de contrats ».
5. Déployer l'interface avec le `Dockerfile` pour avoir une URL à envoyer, et planifier `couverture bilan --envoyer` chaque lundi.
6. Tracer chaque appel au modèle dans MLflow (prompt, réponse, tokens, durée) et suivre le coût, comme dans SortirIA.
