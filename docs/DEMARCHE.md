# La démarche, dans l'ordre où elle s'est construite

Ce document garde le raisonnement, pas seulement le résultat : ce qu'on a essayé, ce qui
a échoué, pourquoi, et ce qu'on en a tiré. Chaque version de consigne citée ici est
archivée en texte intégral dans [`docs/consignes/`](consignes/README.md).

**Comment le lire.** Ce document est long : c'est un journal, tenu au fil du travail, jusqu'au 24 novembre 2026.
Pour le fil du raisonnement, la page qui suit suffit : onze tournants, chacun avec ce qu'on croyait, ce que la
mesure a dit, et ce qui a changé. Les sections 1 à 6 posent le point de départ. La section 7 est le journal
lui-même, en sept parties. La section 8 dit ce qui reste ouvert, la section 9 garde une leçon par ligne.

## Le cheminement, en onze tournants

Le principe n'a pas bougé du premier au dernier jour : **le modèle établit des faits, le code décide**. Tout le
reste a changé, et presque toujours pour la même raison : une mesure a contredit ce qu'on croyait.

| | Ce qu'on croyait | Ce que la mesure ou l'essai a montré | Ce qui a changé | Où |
|---|---|---|---|---|
| 1 | Le modèle peut, à chaque sinistre, trouver les clauses, en tirer les conditions et les confronter aux faits | Deux de ces trois tâches ne dépendent pas du sinistre : on les refaisait à chaque question, un peu différemment à chaque fois | Ce qui appartient au contrat se calcule une fois, et se contrôle une fois | 7.6 |
| 2 | Corriger jusqu'à ce que le vélo et la bougie sortent juste | Quatre règles ajoutées en une matinée, aucune mesurée ailleurs : du surapprentissage sur deux cas. Première mesure : 13 « incertain » sur 14, prudent mais inutile | Mesurer avant de corriger ; un jeu de cas, avec des sinistres qui doivent sortir « couvert » | 7.11, 7.12 |
| 3 | Des fiches de questions, compilées par le modèle, suffisent à représenter un contrat | Une seule clause réelle contient cinq garanties, des obligations, leur sanction et son exception. Fiches : 74 % de justes, 2 couverts à tort, une minute. Règles Prolog : 100 %, 0, 3 à 4 secondes, sur les mêmes 14 cas | La structure se tire du contrat, pas des sinistres ; le contrat devient des règles, un moteur logique décide | 7.15 à 7.16 bis |
| 4 | 100 % : les règles sont justes | Quinze cas nouveaux, annotés d'après l'article qui les tranche : deux couverts à tort. Le 100 % portait sur les cas qui avaient servi à écrire les règles | Un jeu de référence figé et un banc qui rejoue tout, avec des seuils fixés avant de mesurer | 7.17, 7.21 |
| 5 | Une meilleure consigne fera mieux lire les déclarations | Chaque phrase ajoutée en défaisait une autre. Avec des faits exacts le moteur ne se trompe pas : toutes les erreurs viennent de la lecture | On ne fait plus confiance à la lecture, on la vérifie : chaque fait cite les mots de la déclaration ; les faits qui portent la décision sont confirmés, sinon la réponse devient « à préciser ». Justesse 87 → 90 %, en 2,9 secondes | 7.26, 7.43 à 7.50 |
| 6 | Garder les quatre méthodes pour comparer | Elles coûtaient en code, en tests, en consignes, et les mesures avaient tranché | Une seule méthode ; plus d'un tiers du code retiré (7 400 → 4 700 lignes) | 7.36 |
| 7 | Ce qui marche sur un contrat écrit à la main marchera sur un autre | Sur un deuxième assureur, les règles rédigées par un modèle arrivent fausses par endroits, et les contrôles ne voient pas tout | Chaque erreur se corrige dans la méthode (consigne, contrôles, moteur), pas dans le contrat ; la rédaction propose, le code contrôle, une personne relit | 7.51 à 7.61 |
| 8 | Le jeu de référence mesure la fidélité au contrat | Il a été écrit en connaissant les règles. Sur un jeu fermé, écrit sans les voir : A 70 % au lieu de 90, B 57 % au lieu de 76 | Deux jeux : l'un pour mettre au point, l'autre, fermé, qui ne sert qu'à mesurer et jamais à corriger | 7.79 à 7.83 |
| 9 | Une erreur de lecture se corrige par une phrase de plus | Trois corrections en une heure pour la même déclaration, aucune mesurée, la deuxième sans effet | « Pas de rustine » : une consigne ne contient que des principes ; une lecture se corrige par des exemples validés, mesurés sur des cas qui n'ont pas servi à les choisir. Et celui qui lit n'est pas celui qui vérifie | 7.133, 7.136 |
| 10 | Un contrat de plus, c'est un fichier de plus | Le quatrième contrat, ajouté à froid : onze minutes de rédaction, 22 contrôles bloquants, et une erreur qu'aucun contrôle n'avait vue (les formules d'un autre contrat). Une de mes propres corrections a créé un couvert à tort | Le coût d'un contrat est mesuré et écrit ; ce qui est général et ce qui ne l'est pas, aussi : ce n'est pas un bouton | 7.148 à 7.159 |
| 11 | Une décision juste suffit | Les deux questions de l'énoncé, rejouées en ligne la veille de la livraison : décisions justes, phrases hors sujet. Et une correction raisonnable de la lecture, qui passait les tests et trois bancs sur quatre, faisait couvrir à tort un cas du jeu fermé six fois sur six | La réponse ne parle que de ce qui a un rapport avec le sinistre ; la correction de lecture est retirée | 7.164 à 7.167 |

**Où cela mène (24 novembre).** Quatre contrats d'assureurs différents. Décisions justes : 94 % et 100 % sur A
(partie test, jeu fermé), 85 % sur B, 96 % sur D ; un couvert à tort qui se répète chez B, un refus à tort chez D.
Le quatrième contrat est partiel et n'a pas de jeu de mesure. Les règles n'ont été relues par personne du métier.

---

## 1. Comprendre la consigne avant d'écrire du code

La demande : dire si un sinistre est couvert par des conditions générales (CG). Deux cas
donnés : un vélo volé dans le local commun d'un immeuble, non fermé à clé ; une bougie
laissée sur une table de jardin pendant les vacances, qui a fondu avec la chaleur.

Ce que le recruteur évalue, en le relisant attentivement :
- **citer ses sources** : chaque affirmation rattachée à une clause ;
- **admettre ses limites** : « un je ne sais pas étayé » vaut mieux qu'un oui inventé ;
- **ne pas faire « un PDF dans un chatbot »** ;
- **tenir des centaines de contrats** différents ;
- un petit projet qui marche, déployé, plutôt qu'une maquette.

Première conclusion : le verdict compte moins que la façon d'y arriver. Le projet doit
montrer un raisonnement vérifiable.

## 2. Pourquoi un RAG simple ne suffit pas

Un RAG simple découpe le document en morceaux, retrouve les plus ressemblants à la
question et demande au modèle de répondre. Sur un contrat d'assurance, il échoue pour
des raisons de fond :
- **l'exclusion ne ressemble pas à la question** : « vol de vélo » ressemble à « les vélos
  sont garantis », pas à « vols commis dans les parties communes » ;
- **le sens des mots est au lexique**, souvent à l'autre bout du document (« incendie » =
  « combustion avec flammes ») ;
- **chaque assureur rédige autrement** ;
- **rien n'est vérifiable** : le modèle peut citer une clause qui n'existe pas.

## 3. Les méthodes envisagées, et celle retenue au départ

| Méthode | Principe | Ce qu'on en a fait |
|---|---|---|
| Document brut | Tout le contrat dans le prompt | Gardée comme **référence** (méthode `brut`) : c'est le « chatbot » à battre |
| RAG simple | Top-k morceaux ressemblants | Écartée : rate l'exclusion qui décide |
| RAG structuré | Clauses typées + **enveloppe** (exclusions, définitions, renvois de la garantie trouvée) | Retenue pour la recherche |
| Verdict direct | Le modèle conclut en un coup | Gardée pour comparer (méthode `direct`) |
| **Grille de conditions** | Le modèle remplit condition par condition, **le code décide** par des règles | Retenue comme méthode principale |

L'idée centrale, qui reste vraie jusqu'au bout : **le modèle établit des faits, le code
décide**. Le « je ne sais pas » n'est alors pas une hésitation du modèle, c'est une
condition dont l'état est inconnu, et on sait laquelle.

## 4. Des données réelles

- Un **contrat fictif** (« Habitat Serein »), écrit pour couvrir les pièges de la consigne,
  avec **14 sinistres** et leurs réponses attendues (`data/annotations/`).
- Les **CG réelles d'Assureur A** (Habitation A, 48 pages). Elles ne sont pas versionnées : un
  document d'assureur ne se redistribue pas.

Le PDF réel a cassé le premier découpage : sommaire pris pour des clauses, lexique au
format « terme seul sur sa ligne », références de loi prises pour des renvois (« art. 58 de
la loi… »), puces en caractères privés. Chaque cas a donné une correction et un test. De
là sont nés les **profils d'assureur** et l'**agent de réparation** : le modèle propose un
réglage, le code le vérifie, un humain l'accepte.

## 5. Reprendre ce qui a marché dans SortirIA

SortirIA, le projet précédent, est en production. On en a repris les briques éprouvées :
recherche **hybride** (BM25 + embeddings, fusion RRF), **deux juges** (qualité du découpage
à l'ingestion, relecture des conditions décisives), **dérive** (PSI), **bilan**, suivi
**MLflow** avec consignes versionnées, tableaux **Grafana**.

C'était le point de départ. Presque tout a été retiré depuis, à mesure que la méthode changeait
(7.36, 7.110) : restent les consignes versionnées avec leur garde-fou, le journal des analyses
et Grafana. Reprendre ce qui a marché ailleurs a fait gagner du temps ; le garder sans le mesurer
en aurait fait perdre.

## 6. Brancher Mistral : les surprises de l'API

- `top_p` doit valoir 1 quand `temperature` vaut 0 → paramètre ajouté.
- La réponse peut être une **liste de morceaux**, dont des morceaux de réflexion
  (« thinking ») → lecture du seul texte (`texte_du_message`).
- Réponses **coupées** à la limite de longueur → erreur explicite (`ReponseTronquee`) au lieu
  de « aucun objet JSON ».

## 7. Le journal, du 17 au 26 novembre

Neuf parties, dans l'ordre. Chaque étape garde son numéro, cité ailleurs dans le projet.

| Partie | Étapes | La question du moment |
|---|---|---|
| I | 7.1 à 7.14 | Le modèle remplit une grille, puis le contrat est compilé en fiches : pourquoi ça ne tient pas |
| II | 7.15 à 7.23 | Repartir de la clause : des règles, un moteur logique, un jeu de référence et un banc |
| III | 7.24 à 7.50 | La lecture des déclarations, d'où viennent toutes les erreurs : la vérifier plutôt que la corriger |
| IV | 7.51 à 7.101 | D'autres contrats (B, puis D) : ce que coûte un contrat, et un jeu fermé pour mesurer la fidélité |
| V | 7.102 à 7.147 | Le produit : une API, un écran, des déclarations écrites comme les gens écrivent ; « pas de rustine » |
| VI | 7.148 à 7.159 | Un quatrième contrat ajouté à froid : ce qui est général, ce qui ne l'est pas |
| VII | 7.160 à 7.167 | Mettre en ligne, puis tout rejouer la veille de la livraison |
| VIII | 7.168 à 7.189 | Finir A et B, puis des jeux jamais vus qui montrent un défaut de fond |
| IX | 7.190 à 7.212 | La lecture des clauses : une seconde méthode, mesurée contre la première |

---

**Partie I — La grille, puis les fiches (17 novembre).** Le point de départ : à chaque sinistre, le modèle remplit
une grille de conditions et le code décide.

### 7.1 Grille v1 : réponse coupée

Premiers essais sur Assureur A : `INCERTAIN`, « réponse coupée à 8000 tokens », environ 4 minutes
par sinistre (2 tentatives de 2 minutes).

Diagnostic : la consigne v1 demandait de lister **toutes** les exclusions, « même si tu
penses qu'elle ne s'applique pas », avec extrait, justification et question pour chacune.
Sur 16 clauses d'un vrai contrat, la grille ne finissait jamais. Et la seconde tentative
disait seulement « pas un JSON valide » : le modèle recommençait aussi long.

Une erreur à reconnaître : la veille, la limite était passée de 3 000 à 8 000 tokens en
pensant que le modèle manquait de place. C'était traiter le symptôme : on lui a seulement
permis d'échouer plus lentement. **La longueur d'une sortie se règle par la consigne, pas
en repoussant le plafond.**

### 7.2 Grille v2 : bornée, mais toujours trop lente

v2 : au plus 3 garanties, 5 conditions par garantie, 5 exclusions pertinentes, justification
de 15 mots ; une réponse coupée relance une demande plus courte ; mode diagnostic
(`COUVERTURE_DEBUG=oui`).

Résultat : toujours `INCERTAIN`, puis « The read operation timed out ». La consigne n'était
donc pas la seule cause.

### 7.3 La vraie cause : la réflexion du modèle

Indice : dès le branchement, Mistral renvoyait une liste de morceaux, le format des modèles
qui réfléchissent avant de répondre. La documentation de Mistral le confirme :
**Mistral Large 4 réfléchit au niveau « high » si on ne précise rien** (valeurs acceptées :
`low`, `medium`, `high`). Des milliers de tokens de réflexion avant la première ligne de
la grille.

Correction : `reasoning_effort: low` par défaut (`COUVERTURE_REFLEXION` pour changer), retiré
automatiquement si un modèle le refuse ; délai dépassé affiché clairement et non relancé
quatre fois.

### 7.4 Premiers résultats sur le vrai contrat (grille v2, réflexion courte)

| Sinistre | Décision | Ce qui est juste | Ce qui cloche |
|---|---|---|---|
| Vélo, local commun | NON_COUVERT, 0,90 | Exclusion 2.10-a « vol… dans les parties communes du bâtiment », citée, page 12, relecture d'accord | Condition « portes donnant sur les parties communes fermées ? → non » : la clause vise les portes **du logement**, pas le local. Condition « véhicule automoteur exclu ? » posée **à l'envers** dans une garantie |
| Bougie, jardin | NON_COUVERT, 0,50 | Pas de flammes → pas d'incendie. Une citation inventée (art. 1.4) **écartée par le code**. La relecture conteste : la chaleur doit être « subite », la cire a fondu lentement | Lit « la chaleur » comme celle de la bougie (c'est l'été). Cite l'art. 2.1 au lieu de la **définition** d'incendie. Laisse « la table est-elle assurée ? » inconnu alors que la clause « mobilier de jardin » était fournie |

Les garde-fous ont fait leur travail : citation inventée rejetée, relecture critique,
confiance abaissée. Mais la grille elle-même avait cinq défauts de formulation.

### 7.5 Grille v3 : rafistoler par la consigne

v3 ajoute des « règles de lecture » : lire le sinistre tel qu'il est écrit ; un fait ne
s'applique qu'à l'objet ou au lieu exact de la clause ; OUI toujours favorable à l'assuré
dans une garantie ; citer la définition d'un terme défini ; trancher quand une clause
fournie le permet.

### 7.6 La remise en question

En reprenant la structure à froid : on demandait au modèle, **à chaque sinistre**, trois
métiers à la fois :
1. trouver quelles garanties et exclusions s'appliquent ;
2. en déduire les conditions et les formuler ;
3. confronter ces conditions aux faits.

Or 1 et 2 **ne dépendent pas du sinistre** : ce sont des propriétés du contrat. On les
refaisait à chaque question, un peu différemment à chaque fois. Les cinq défauts de 7.4
viennent tous de là, et la v3 les corrige par des consignes sans traiter la cause.

Un second risque, pas encore observé mais structurel : la recherche ne remonte qu'une
quinzaine de clauses. Si l'exclusion décisive n'y est pas, le modèle ne peut pas la voir,
et on répond COUVERT à tort, la pire erreur.

### 7.7 La stratégie retenue : compiler le contrat

**Une fois par contrat** (`couverture compiler`), chaque garantie devient une **fiche** :
événement visé, conditions formulées pour que OUI soit favorable, exclusions rattachées
(chacune marquée « à demander » ou « présumée absente »), limites. Chaque extrait est
vérifié dans sa clause par le code. Un humain peut relire et corriger
(`couverture fiches --exporter` puis `--importer` : il peut reformuler une question, pas
inventer une citation).

**À chaque sinistre** (`--methode fiches`) : les faits désignent les fiches de l'événement,
**complètes par construction** ; le modèle répond seulement oui / non / inconnu à des
questions déjà écrites ; le code décide **fiche par fiche** (une exclusion du vol ne fait pas
tomber la garantie incendie) ; la relecture contrôle les lignes décisives.

Ce que ça change :

| | Grille (`conditions`) | Fiches (`fiches`) |
|---|---|---|
| Qui formule les conditions | Le modèle, à chaque sinistre | Le modèle, une fois ; relu par un humain |
| Exclusion décisive manquée | Possible (recherche top-k) | Impossible pour l'événement reconnu |
| Citations | Vérifiées après coup, parfois écartées | Vérifiées à la compilation, toujours valides |
| Coût par sinistre | Un gros appel | Un petit appel |
| Nouveau contrat | Rien à faire, mais rien de contrôlé | Une compilation à relire |
| Risque | Erreurs variables d'une question à l'autre | Une fiche fausse se trompe pour tous les sinistres, d'où sa relecture |

Deux décisions de conception qui comptent :
- **Exclusions présumées absentes.** Sans elles, « le dommage est-il intentionnel ? » serait
  toujours inconnu, et toute réponse deviendrait INCERTAIN. Un gestionnaire présume la bonne
  foi : ces exclusions ne jouent que si la déclaration les évoque.
- **La relecture ne relit pas les exclusions présumées** : sa consigne dit « dans le doute,
  conteste », ce qui les rendrait inconnues et annulerait la présomption.

La méthode `conditions` est gardée : `couverture comparer` mesure l'écart entre les deux.

### 7.8 Première compilation d'Assureur A : la réflexion du modèle, encore

Résultat : 17 fiches, 126 questions, 7 citations écartées, 15 exclusions générales. Les fiches
réussies sont de bonne qualité (conditions dans le bon sens, définitions citées, exclusions
« présumées absentes » bien choisies). Mais quatre garanties ont échoué, dont **la garantie
vol (2.10)**, celle du premier cas de la consigne : trois délais dépassés (120 s), une réponse
coupée (« Défense et recours », 2.14).

Le fichier de diagnostic a donné la cause : **30 000 caractères de réflexion** (environ
7 500 tokens) avant la première ligne de la fiche. Le réglage « low » ne suffit pas à
empêcher une longue réflexion sur une clause complexe, et Mistral Large 4 n'accepte pas de
la couper complètement (`none` refusé).

Décision : ne pas lutter contre la réflexion **à la compilation**. Elle ne se fait qu'une fois,
et y réfléchir longuement est plutôt une qualité. On lui donne la marge nécessaire (16 000
tokens, 5 minutes par garantie), sans toucher aux réglages de l'analyse, qui doit rester
rapide. Trois améliorations en découlent :
- **reprise** : une seconde compilation ne refait que les garanties en échec ; les fiches
  réussies, peut-être déjà relues, sont gardées ;
- **progression** affichée garantie par garantie, pour qu'une attente de plusieurs minutes
  ne ressemble pas à un blocage ;
- **citation rattachée à la bonne clause** : le modèle citait parfois le bon texte sous le
  mauvais numéro (la définition du vol sous l'art. 2.11). Le code cherche le passage dans les
  clauses fournies avant de l'écarter. Un passage introuvable partout reste écarté.

`couverture modele` dit désormais si le niveau de réflexion demandé est accepté, et combien
le modèle a réfléchi : la question « le réglage est-il pris en compte ? » se tranche par une
mesure, pas par une supposition.

### 7.9 Relecture des fiches vol : des citations presque exactes

Avec la marge, tout compile : 32 fiches, 215 questions (le vol en 7 min 30, découpé en 4 fiches :
dans le bâtiment, contenu déplacé, sur la personne, chez le réparateur). La fiche « Vol du contenu
dans le bâtiment » contient bien l'exclusion « vol dans les parties communes » (2.10-a).

Deux conditions clés étaient pourtant écartées : « le bien se trouvait-il dans le bâtiment ? » et
« y a-t-il eu effraction ? ». Le modèle avait cité le bon texte en **sautant des mots sans le
signaler** (« l'accès a été endommagé » pour « l'accès (porte, fenêtre, chambranle, châssis) a été
endommagé »). Le contrôle avait raison de refuser une citation inexacte, mais tort de jeter la
condition.

Réparation (`validation.passage_exact`) : si tous les mots de l'extrait figurent dans la clause,
dans l'ordre, avec de petits trous, l'extrait est **remplacé par le passage littéral** du contrat.
Rien n'est inventé, la citation devient exacte. Appliquée à la compilation existante sans appel au
modèle : 6 questions récupérées sur 9. Les 3 restantes sont de vraies reformulations (dont un titre
d'article cité comme s'il était dans le texte) : elles restent écartées, pour la relecture humaine.

### 7.10 Premières analyses par fiches : trois règles de décision à revoir

| Sinistre | Résultat | Ce qui s'est passé |
|---|---|---|
| Vélo, local commun | INCERTAIN (attendu : NON_COUVERT) | La fiche « Vol du contenu » concluait bien NON_COUVERT par l'exclusion des parties communes. Mais la fiche « Dégradations immobilières » (2.11), retenue parce qu'elle parle de vol, couvre les dégâts **au bâtiment**. Sa condition d'entrée avait été écartée à la compilation : toutes ses questions restaient inconnues, et une seule fiche ouverte rendait tout incertain. |
| Bougie, jardin | NON_COUVERT, pour de mauvaises raisons | « Pas d'incendie » était établi, mais la décision citait deux exclusions : « dommage causé au contenu par vous » (qui vise les heurts) et « biens dont vous avez la garde » (art. 5.10, exclusions de la **responsabilité civile**, appliquées à tort à tout le contrat). |

La compilation n'était pas en cause : c'était la façon de décider. Trois règles corrigées
(`fiches.decider_fiche`, `JugeFiches._questions`) :
1. **Une exclusion ne compte que si la garantie s'applique.** Une condition de garantie non
   remplie écarte la fiche, sans consulter ses exclusions. Une exclusion retire une garantie
   qui s'applique ; elle ne sert pas à refuser une garantie qui ne s'applique pas.
2. **Une fiche dont aucune condition n'est établie n'est pas rattachée au sinistre.** Elle ne
   rend pas la réponse incertaine à elle seule. Si aucune fiche n'est rattachée, la réponse
   reste INCERTAIN (« aucune garantie rattachée »).
3. **Une exclusion « générale » ne vaut que pour sa partie du contrat** quand cette partie a ses
   propres garanties (art. 5.10 : responsabilité civile). Celles d'une partie sans garantie
   (art. 1.4, dispositions communes) valent pour tout.

Avec ces règles, les mêmes réponses du modèle donnent : vélo NON_COUVERT par l'exclusion 2.10-a ;
bougie NON_COUVERT parce qu'aucune garantie ne s'applique (pas d'incendie).

Ce que ça enseigne : la méthode par fiches déplace la difficulté. Le modèle ne se trompe plus sur
les questions, mais il faut encoder correctement **comment un gestionnaire combine les réponses**.
Ces règles sont du code, testées une par une, et non une consigne qu'on espère suivie.

Relance : la bougie donne NON_COUVERT pour la bonne raison (aucune garantie ne s'applique : pas
d'incendie). Le vélo reste INCERTAIN, cette fois à cause de la fiche « Vol sur la personne avec
violence » : sa première condition, « est-ce un vol ? », vaut oui pour **toutes** les fiches vol,
et suffisait à la rattacher alors que rien de propre à elle n'était établi. Quatrième règle :
**l'événement seul ne rattache pas une fiche** qui a d'autres conditions ; il faut qu'une de ses
conditions propres soit établie. Si aucune fiche ne l'est, la réponse reste INCERTAIN, en nommant
les garanties possibles et les questions qui trancheraient.

Ce qu'on n'a pas fait : changer la consigne pour que le modèle réponde « non » plus volontiers.
« Mon vélo a été volé dans ma cave » ne dit rien de l'effraction ; un « non » refuserait la
couverture au lieu de poser la question. La prudence du modèle est voulue, c'est la combinaison
des réponses qu'il fallait corriger.

Reste à améliorer à la compilation : chaque fiche devrait avoir une condition sur **l'objet**
(« le dommage porte-t-il sur le bâtiment ? » pour la 2.11), pour qu'une fiche hors sujet soit
écartée par une réponse « non » plutôt que par l'absence de réponse.

### 7.11 Deuxième remise en question : on ajustait sur deux exemples

En une matinée, quatre règles de décision avaient été ajoutées pour que le vélo et la bougie
sortent juste. Chacune était défendable ; aucune n'était mesurée ailleurs. Pire, toutes poussaient
vers NON_COUVERT, et la dernière pouvait produire un **refus à tort** (une garantie qui aurait
couvert, écartée faute de réponse). C'est la définition du surapprentissage, sur deux cas.

Deux décisions :

**1. Mesurer avant de corriger.** Un jeu d'évaluation sur Assureur A
(`data/annotations/assureur-a-habitation-2025.jsonl`) : 14 sinistres, dont 6 qui doivent sortir
COUVERT (vol avec effraction dans l'appartement, vrai incendie, dégât des eaux, vol à l'arraché),
pour voir les refus à tort. Chaque réponse attendue cite les clauses qui la fondent. Certains cas
sont réellement ambigus sans les conditions particulières (cave fermée par un cadenas, alors que
la « serrure de sûreté » exclut le cadenas ; mobilier de jardin, exclu du contenu sauf option) :
le champ `acceptables` admet alors un INCERTAIN honnête, jamais un COUVERT à tort. Deux nouveaux
indicateurs : `faux_refus` et `exactitude_stricte`. Les réponses sont proposées par Claude et
**à valider** par une personne : le statut le dit dans chaque ligne.

**2. Refaire la structure des fiches avec les rôles du droit des assurances.** Les quatre
règles étaient des approximations d'une distinction que le contrat fait lui-même. L'art. 2.10
d'Assureur A a une section « Obligation de prévention » séparée, avec « nous refuserons notre
intervention s'il existe un **lien causal direct** » et « en cas d'effraction, le non-respect
de ces obligations est **sans incidence** ». Une liste plate de « conditions » ne peut pas
exprimer ça.

| Rôle | Exemple (Assureur A, vol) | Effet sur la décision |
|---|---|---|
| Périmètre : événement, bien, lieu | vol ; contenu ; dans le bâtiment | « non » : la garantie est hors sujet ; tout « oui » : elle est rattachée au sinistre |
| Circonstance | avec violences ; avec effraction | « non » : elle ne joue pas ; « inconnu » : on pose la question |
| Obligation de prévention | portes fermées à clé en cas d'absence | « non » : déchéance possible, **si lien causal** : à apprécier par un gestionnaire |
| Exclusion | vol dans les parties communes | « oui » : refus, **seulement pour une garantie rattachée** |
| Limite | 1 000 EUR pour les caves | signalée |

Le modèle reçoit le rôle de chaque question, avec une consigne simple : **le périmètre est presque
toujours décrit** par une déclaration (quoi, où), donc un fait décrit et contraire vaut « non » (un
vol dans un local commun n'est pas un vol « sur la personne ») ; **les circonstances et obligations
ne le sont souvent pas**, donc leur silence vaut « inconnu ». C'est ce qui manquait : la fiche
« vol sur la personne » est maintenant écartée parce que son lieu est contraire, pas parce qu'on
n'a pas de réponse.

Combinaison : COUVERT si une fiche rattachée l'est ; sinon INCERTAIN si une fiche rattachée l'est ;
sinon NON_COUVERT si une fiche rattachée refuse. Une garantie seulement « possible » (périmètre
inconnu) n'empêche pas ce refus, mais **sa question est posée et la confiance baisse** : c'est la
protection contre le refus à tort. Sinon INCERTAIN si une fiche est possible ; sinon « aucune
garantie ne s'applique ».

Les faits (événement, bien, lieu) sont désormais extraits par un petit appel au modèle ; le
lexique écrit à la main ne sert qu'en secours. Il rattachait la bougie aux « dommages
accidentels » parce que la table était « abîmée ».

Consignes : `compilation` v2, `fiches` v2 (les v1 restent archivées). Une compilation faite avec
la v1 est refusée par l'analyse, avec le message qui dit de recompiler.

### 7.12 Première mesure : 93 % d'incertains, et pourquoi

Compilation v2 d'Assureur A : 36 fiches, 350 questions, 9 écartées. Évaluation `fiches` sur les
14 cas : **0 couvert à tort, 0 refus à tort**, mais 13 INCERTAIN sur 14 (exactitude 0,43 en
comptant les incertains acceptables, 0,07 en stricte). Prudent, donc, mais inutile.

La confiance a donné le diagnostic. **Sept cas à 0,0** : ce n'est pas une mauvaise réponse,
c'est une absence de réponse. Ce sont tous des vols : cinq fiches vol, les dégradations et les
exclusions générales, environ 80 questions dans un seul appel, coupé ou hors délai. Les autres :
- les deux vrais incendies restent INCERTAIN à cause d'exclusions « inconnues » (« vice de
  construction connu de vous ») ;
- la bougie au jardin ne trouve aucune garantie : le modèle a classé l'événement en « dommage
  accidentel », catégorie sans fiche chez Assureur A, alors que le lexique aurait reconnu « bougie ».

Trois corrections :
1. **Un appel par fiche, en parallèle**, plus un pour les exclusions générales. Chaque appel est
   petit, et un appel qui échoue ne rend inconnues que les questions de sa fiche.
2. **La charge de la preuve.** C'est à l'assuré d'établir les conditions de la garantie, et à
   l'assureur de prouver qu'une exclusion s'applique. Une exclusion dont rien n'indique qu'elle
   joue ne rend donc plus la réponse incertaine : elle devient une **réserve** (« couvert, sous
   réserve de vérifier… »), avec sa question et une confiance plafonnée à 0,7. Seuls un périmètre
   ou une circonstance inconnus (à la charge de l'assuré) laissent la réponse ouverte.
3. **Routage : modèle et lexique ensemble.** Une fiche de trop est écartée par son périmètre ;
   une fiche manquante, rien ne la rattrape.

Ce que la mesure a apporté : sans elle, on aurait continué à régler des règles sur le vélo et la
bougie, sans voir que la moitié des cas n'obtenaient tout simplement pas de réponse.

### 7.13 Un modèle par usage

L'évaluation `fiches` sur 14 cas prenait 30 à 60 minutes : 5 à 10 appels par cas, de 30 s à
2 min chacun, Mistral Large réfléchissant même au niveau « low ». Or les deux usages n'ont pas
les mêmes besoins :
- **le travail sur un contrat** (compilation, juge de qualité, réparation) se fait une fois et
  gagne à un modèle qui réfléchit : Mistral Large (`COUVERTURE_MODELE_CONTRAT`) ;
- **l'analyse d'un sinistre** se répète, et ne consiste plus qu'à répondre oui / non à des
  questions courtes : un modèle rapide sans réflexion suffit, Mistral Small (`COUVERTURE_MODELE`,
  réflexion `none`).
Et l'évaluation traite quatre cas à la fois. Ce choix sera vérifié sur les 14 cas : s'il coûte
des décisions justes, on le saura.

### 7.14 Nettoyage

- **Sorties courtes** : `analyser` donne la décision, le motif, les preuves décisives et les
  questions à poser, en une dizaine de lignes au lieu de 150 ; `--detail` garde tout.
  `evaluer` donne un tableau d'une ligne par cas ; `--detail` garde le JSON.
- **Méthode « direct » retirée** : elle ne servait qu'à comparer, et la référence « brut » suffit.
  Ses tests portaient en fait sur le contrôle des citations : ils sont gardés, avec un juge
  qui rend un verdict fixé d'avance. Sa consigne reste archivée.
- **Données produites supprimées** (base, diagnostics) : elles se reconstruisent avec
  `ingerer` et `compiler`. On garde le code et les données d'entrée.
- **README** ramené à l'essentiel ; le détail est dans `EXPLICATIONS.md` et ici.
- La méthode `conditions` est gardée jusqu'à la comparaison avec `fiches`.

### 7.14 bis Deuxième mesure : 79 %, zéro couvert à tort, en 27 secondes

Recompilation d'Assureur A (Mistral Large) : 38 fiches, 315 questions, **4 écartées seulement**
(contre 9 : la réparation des citations fait son effet), en 11 min 22 s. Évaluation `fiches`
avec Mistral Small sans réflexion, quatre cas à la fois :

| Indicateur | Première mesure (Large) | Deuxième mesure (Small) |
|---|---|---|
| Justes ou acceptables | 43 % | **79 %** |
| Exactes | 7 % | **50 %** |
| INCERTAIN | 93 % | 43 % |
| Couverts à tort | 0 | **0** |
| Refus à tort | 0 | **1** |
| Durée | ~1 h (interrompue) | **27 s** |

Le vélo de la consigne et la bougie au jardin sortent NON_COUVERT ; le vol avec effraction dans
l'appartement sort COUVERT. Trois erreurs, toutes sur des sinistres qui devraient être couverts :
un **refus à tort** (incendie qui atteint la façade et le séjour) et deux INCERTAIN (la nappe qui
prend feu au salon, le tuyau du lave-linge). Les deux incendies ratés désignent probablement la
fiche incendie elle-même ; à vérifier sur le détail avant toute correction.

Le modèle rapide n'a pas coûté de justesse, au contraire : sans réflexion, il ne se perd plus dans
80 questions, et chaque appel par fiche est court.

### 7.14 ter Les trois erreurs : deux formes du contrat que la structure ignorait

Le détail des trois cas ratés (deux incendies, un dégât des eaux) montre deux causes, et aucune
ne vient du modèle :
1. **Des alternatives lues comme des conditions cumulées.** La fiche incendie demande « le bien
   est-il un bâtiment ? » puis « un contenu ? » ; le contrat couvre l'un **ou** l'autre. La façade
   étant du bâtiment, « contenu ? » restait inconnu et la réponse devenait INCERTAIN.
2. **Des exclusions partielles traitées comme totales.** « Le dommage concerne-t-il la canalisation
   à l'origine du sinistre ? » est vrai pour le lave-linge, mais l'exclusion ne retire que le tuyau,
   pas le parquet ni le canapé. Corrigée la cause 1, elle aurait produit un refus à tort.
Et un détail de lecture : « dans le salon » ne suffisait pas au modèle pour dire « à l'adresse
assurée ».

Corrections, sans recompilation : les questions de rôle « bien » sont des alternatives (une seule
établie suffit) ; consigne `fiches` v3 : une énumération (« … ou … ») vaut oui si l'une est vraie,
une pièce du logement désigne le bâtiment assuré, et une exclusion qui ne vise qu'une partie des
dommages est « PARTIELLE » (la garantie joue pour le reste, la partie exclue est signalée).

Leçon pour la suite (Prolog) : un contrat combine des **ET** et des **OU**, et ses exclusions
portent soit sur tout le sinistre, soit sur **un bien** seulement. La représentation en règles devra
exprimer les trois explicitement.

### 7.14 quater La limite de débit

Troisième mesure interrompue au 13e cas, mais avec un premier signe : l'incendie de la façade
(bougie-05), refusé à tort avant le correctif, sort maintenant **COUVERT**. L'arrêt venait de
Mistral : « Rate limit exceeded » (429). Avec quatre cas en parallèle et un appel par fiche,
jusqu'à seize appels partaient ensemble ; quatre nouvelles tentatives en quinze secondes ne
suffisaient pas, et l'erreur arrêtait toute l'évaluation.

Corrections : au plus quatre appels simultanés pour tout le programme
(`COUVERTURE_APPELS_SIMULTANES`) ; jusqu'à six nouvelles tentatives, espacées jusqu'à une minute
avec un peu d'aléa ; un cas en erreur est compté « err » dans le tableau au lieu d'arrêter
l'évaluation. Seule une clé refusée arrête tout. Leçon : le parallélisme se règle avec les
limites du fournisseur, pas seulement avec celles de la machine.

### 7.14 quinquies Troisième mesure : 93 %, zéro erreur coûteuse

| Mesure | Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Durée |
|---|---|---|---|---|---|
| 1re (Large) | 43 % | 7 % | 0 | 0 | ~1 h |
| 2e (Small) | 79 % | 50 % | 0 | 1 | 27 s |
| **3e (alternatives, exclusions partielles, débit)** | **93 %** | **57 %** | **0** | **0** | **59 s** |

Les deux incendies et le dégât des eaux sortent COUVERT. Une seule erreur : velo-02 (local commun
fermé, serrure forcée) sort INCERTAIN au lieu de NON_COUVERT, alors qu'il était juste à la mesure
précédente : une régression à expliquer sur le détail. Les autres INCERTAIN sont les cas ambigus
attendus (cadenas, serrure du garage inconnue, option jardin, arrachage). Cette version sert de
**référence chiffrée** pour la suite en Prolog.

### 7.14 sexies La régression de velo-02 : une relecture qui « contestait » en étant d'accord

Le détail de velo-02 (local commun fermé, serrure forcée) : la première analyse concluait
**NON_COUVERT** par l'exclusion des parties communes, ce qui était juste. La relecture (Mistral
Small) a « contesté » trois lignes, mais ses propres raisons les **confirmaient** (« le local à vélos
est situé dans le bâtiment assuré », « le vélo n'est pas un contenu déplacé »). Sa consigne disant
« dans le doute, conteste », ces lignes sont redevenues inconnues, et la réponse INCERTAIN.

Le défaut était de conception : on faisait confiance à une **étiquette** au lieu de comparer des
**réponses**. Consigne `relecture` v2 : le relecteur ne voit plus ni la réponse ni la justification
de la première analyse ; il répond lui-même oui / non / inconnu, et **le code compare**. Il y a
contestation seulement si les deux réponses diffèrent. La relecture devient réellement
indépendante, et l'incohérence observée devient impossible. Valable pour les deux méthodes.

Leçon : ne jamais demander à un modèle un verdict sur le travail d'un autre quand on peut lui
demander le même travail et comparer.

### 7.14 septies Quatrième mesure : un recul, et deux leçons

Avec la relecture v2 : **64 %**, avec **un couvert à tort** (velo-03, cave fermée au cadenas) et
**un refus à tort** (lave-linge), et velo-01, le cas de la consigne, en INCERTAIN.

Deux causes :
1. **Deux règles qui se contredisent.** La relecture devait ne pouvoir que rendre la réponse plus
   prudente. Mais quand elle conteste une exclusion, celle-ci redevient inconnue, et la **charge de
   la preuve** transforme une exclusion inconnue en « couvert, sous réserve ». La relecture pouvait
   donc faire passer un refus à COUVERT. Chaque règle était juste isolément ; c'est leur combinaison
   qui violait le principe.
2. **Un relecteur indépendant doute davantage**, et chaque « inconnu » comptait comme contestation.

Et un constat de méthode : velo-02, bougie-02 et autre-02 changent d'une exécution à l'autre, à
réglages presque identiques. **Une seule exécution de 14 cas est bruitée** : on ne peut pas juger
une correction sur elle.

Corrections :
- **une règle garantie par le code** (`relecture.borner`) : après relecture, une décision ne peut
  devenir qu'INCERTAIN ; deux lectures qui mènent à deux décisions fermes différentes donnent
  INCERTAIN, « les deux lectures divergent » ;
- **seul un désaccord net conteste** (oui contre non) ; un « inconnu » du relecteur est un doute,
  noté, sans effet sur la réponse ;
- **`evaluer --repetitions N`** : rejoue l'évaluation N fois, montre la réponse de chaque cas à
  chaque fois, les cas instables, et chaque indicateur en moyenne (min – max).

Leçons : un principe (« la relecture ne fait que rendre prudent ») doit être **garanti par le
code**, pas espéré de la combinaison des règles ; et une mesure sans sa variance ne prouve rien.

### 7.14 octies Mesure sur trois exécutions : la référence des fiches

`evaluer --repetitions 3`, méthode `fiches`, Mistral Small, relecture v2 bornée :

| Indicateur | Moyenne (min – max) |
|---|---|
| Justes ou acceptables | 74 % (64 – 79 %) |
| Exactes | 60 % (50 – 64 %) |
| Couverts à tort | **2 (2 – 2)** |
| Refus à tort | 0 |
| Cas instables | 2 sur 14 (bougie-02, autre-02) |

Les deux couverts à tort sont **systématiques**, et ce sont exactement les deux pièges repérés en
analysant la clause vol (7.15) :
- **velo-03** (cave fermée au cadenas) → COUVERT : la condition « si fermée avec une serrure de
  sûreté » est cachée dans le **tableau des limites**, que les fiches affichent sans en tenir compte ;
  et la définition de la serrure de sûreté exclut le cadenas ;
- **bougie-04** (incendie du mobilier de jardin) → COUVERT : « le contenu… **ne comprend pas** le
  contenu du jardin » est une exclusion **cachée dans une définition**, et le modèle ne voit que la
  première phrase de la définition.

Décision : ne plus corriger les fiches. Ces deux formes (condition déguisée en limite, exclusion
dans une définition) sont ce qu'une représentation en règles exprime naturellement. Les fiches
restent la **référence chiffrée** ; Prolog devra faire au moins aussi bien et corriger ces deux cas.

---

**Partie II — Repartir de la clause (17 et 18 novembre).** Les fiches plafonnent. La question devient : qu'est-ce qu'une clause, et que faut-il en garder ?

### 7.15 Repartir de la clause : comment structurer des conditions générales

Après ces corrections successives, retour à la question de fond : comment se présente une clause,
et comment la traiter ? Une remarque de l'auteur a recadré la discussion : **la structure doit se
tirer du contrat lui-même, pas des sinistres**. Les sinistres ne servent qu'à tester.

**Anatomie d'une clause réelle** (Assureur A, art. 2.10 « Garantie vol » et 2.10-a, p. 11-12) :
- une seule clause numérotée contient **cinq garanties** (dans le bâtiment, chez le réparateur,
  sur la personne avec violence, contenu déplacé, vandalisme lors d'un vol) ;
- des **obligations de prévention**, leur **sanction** (« refus s'il existe un lien causal
  direct ») et une **exception à la sanction** (« en cas d'effraction, sans incidence ») ;
- un tableau de « **limites** » qui cache une **condition** (caves : 1 000 € « si fermées avec
  une serrure de sûreté », et la définition exclut le cadenas) ;
- des **exclusions** en sous-section, et des **définitions** à l'autre bout du document.

Trois constats : une clause porte plusieurs rôles ; un rôle est éclaté sur plusieurs clauses ;
les exceptions s'emboîtent (exception à une exclusion, exception à une sanction). D'où **deux
niveaux** : la **clause**, unité de citation (ce qu'on montre, avec sa page), et la
**proposition**, unité de raisonnement (une phrase, un rôle, ses exceptions).

**Ce que fait l'état de l'art.** Les travaux récents ne demandent plus au modèle de comprendre
le contrat à chaque question : ils lui font **traduire le contrat en règles logiques**, qu'un
moteur applique. Sur des polices santé, cette traduction n'améliore les résultats que si elle est
**guidée par un vocabulaire de faits fixé à l'avance** ; sans guide, elle fait moins bien que le
modèle seul (arXiv 2502.17638, sur peu de cas : 9 et 20). Pour les exceptions, la référence est la
logique « règle générale, puis exceptions par priorité », celle de Catala (Inria, Microsoft
Research). Partout, un expert relit les règles.

**Ce que ça révèle du projet.** Les fiches ont le bon squelette, mais pas de **vocabulaire de
faits commun** : chaque fiche pose ses propres questions en texte libre (350 pour Assureur A).

**Choix pour plusieurs contrats** : les contrats deviennent des **données**, pas du code.
- un **vocabulaire commun** de variables (événement, bien, lieu, effraction, violence, absence,
  fermé à clé, serrure de sûreté…), auquel chaque contrat rattache ses définitions ;
- **un fichier de règles par contrat et par version**, en JSON relisible : garanties, exceptions
  par priorité, obligations, limites, chacune avec sa clause et sa page ;
- **un seul moteur** en Python, à trois valeurs (oui, non, inconnu) ;
- une chaîne de production contrôlée : traduction par le modèle, vérification des citations par
  le code, relecture humaine, tests.

Pourquoi JSON et pas Prolog : relisible par un juriste, « je ne sais pas » natif, s'intègre à
l'existant, et reste convertible plus tard. Prolog (ou Catala) se justifie quand les règles
deviennent très nombreuses et s'enchaînent sur plusieurs niveaux.

Exemple de règle :
```json
{"garantie": "R1 Vol du contenu dans le bâtiment",
 "si": {"evenement": "vol", "bien": "contenu", "lieu": "batiment"},
 "sauf": [{"lieu": "parties_communes", "source": "2.10-a"},
          {"auteur": "famille", "source": "2.10-a"}]}
```

**Orientation retenue par l'auteur : Prolog.** Le point à régler est le « je ne sais pas ». En
Prolog, `\+` signifie « pas prouvé », pas « faux » (monde clos). Pour une **exclusion**, c'est
exactement la charge de la preuve : une exclusion non établie ne joue pas. Pour une **condition
de garantie**, c'est un refus à tort : un lieu inconnu ferait répondre « non couvert » au lieu
d'INCERTAIN. D'où trois issues explicites, `couvert/2`, `non_couvert/2`, `incertain/2`, des faits
`fait(S, variable, valeur)` et `inconnu(S, variable)`, et l'article cité dans chaque conclusion :

```prolog
couvert(S, '2.10')   :- vol(S), fait(S, bien, contenu), fait(S, lieu, batiment), \+ exclu(S, _).
non_couvert(S, Art)  :- exclu(S, Art).
incertain(S, lieu)   :- vol(S), inconnu(S, lieu).
exclu(S, '2.10-a')   :- fait(S, lieu, parties_communes).
```

À prévoir : SWI-Prolog (et `janus-swi` depuis Python) ; un vocabulaire de faits fixé à l'avance
(sans guide, la traduction en Prolog par un modèle fait moins bien que le modèle seul) ; chaque
fichier de règles chargé et testé automatiquement ; à côté de chaque règle, la phrase du contrat
qu'elle traduit, pour la relecture par un juriste.

Sur la question « quel taux de réussite ? » : aucun chiffre fiable tant que la méthode n'est pas
mesurée. Objectif raisonnable : 85 à 95 % de décisions justes sur les cas nets, un INCERTAIN
argumenté sur les cas ambigus, et **zéro couvert à tort**.

### 7.16 Prolog : le contrat en règles, un moteur qui décide

Mise en œuvre de l'orientation 7.15, sur le vol (2.10), l'incendie (2.1) et les dégâts des eaux
(2.7) d'Assureur A :

```
regles/vocabulaire.json        les variables communes à tous les contrats, et leurs valeurs
regles/moteur.pl               le moteur unique : logique à trois valeurs, règles de gestionnaire
regles/assureur-a-habitation-2025.pl les règles du contrat, chacune avec sa phrase du contrat
regles/cas/<contrat>.jsonl     les faits « idéaux » des 14 sinistres, pour tester les règles seules
```

Le contrat est **une suite de données** (définitions, garanties, périmètre, circonstances,
obligations, exclusions, limites) ; les conditions sont des termes `f(variable, valeur)`, `et`,
`ou`, `non`, `si`, `concept`. Le moteur évalue en **trois valeurs** (oui, non, inconnu), ce qui
règle le piège du monde clos de Prolog. Les formes que les fiches rataient s'écrivent directement :

```prolog
definition(contenu, et([ ..., non(f(bien, mobilier_jardin)), non(f(lieu, jardin)) ]), '12/contenu', "…").
circonstance(vol_batiment, si(ou([f(lieu, cave), f(lieu, grenier)]), concept(serrure_de_surete)), '2.10',
    "si ces locaux sont fermés avec une serrure de sûreté").
definition(serrure_de_surete, et([f(serrure_surete, oui), non(f(fermeture, cadenas)), …]), '12/serrure-de-surete', "…").
exclusion(degats_eaux, f(bien, canalisation), bien(canalisation), oui, '2.7-b', "…").   % partielle
obligation(vol_batiment, si(f(absence, oui), f(portes_fermees, oui)), f(effraction, oui), oui, '2.10', "…").
```

**Résultat des règles seules**, sur les faits idéaux des 14 cas : **13 exactes, 1 acceptable**
(le garage : le moteur demande si la serrure est de sûreté), **0 couvert à tort, 0 refus à tort**.
Les deux couverts à tort systématiques des fiches (cave au cadenas, mobilier de jardin) sont
corrigés. Les **36 citations** du fichier figurent mot pour mot dans leurs clauses.

**Vérification sans Prolog de mon côté.** L'environnement de développement n'avait ni SWI-Prolog
ni le droit de l'installer. D'où une **seconde implémentation du moteur en Python**, réservée aux
tests (`tests/moteur_reference.py`), qui lit le même fichier de règles : elle a permis de faire
tourner les cas, et, là où SWI-Prolog est installé, un **test différentiel** vérifie que les deux
moteurs donnent les mêmes réponses. `couverture regles` vérifie sur le poste : chargement sans
avertissement, vocabulaire, citations, cas.

**La méthode complète** (`--methode regles`) : Mistral Small lit la déclaration et la traduit dans
le vocabulaire (ce qu'elle ne dit pas reste inconnu), puis Prolog décide. Le modèle ne décide plus
rien et ne cite plus rien. Reste à mesurer cette lecture des faits : c'est maintenant elle, et
non plus le raisonnement, qui porte le risque.

Limite connue : une variable à plusieurs valeurs est évaluée globalement (« un des lieux est le
jardin »), pas bien par bien ; l'exclusion partielle couvre le cas utile (un bien exclu parmi
d'autres).

### 7.16 bis Première mesure des règles Prolog, sur le poste

Sur le poste de l'auteur (SWI-Prolog 10.0.2, Windows) :
- `couverture regles` : « Tout est en ordre » (chargement sans avertissement, vocabulaire, citations, cas) ;
- `tests/test_prolog.py` : 11 réussis, dont le **test différentiel** : SWI-Prolog et l'oracle Python
  donnent les mêmes réponses sur tous les cas ;
- chaîne complète (Mistral Small lit les faits, Prolog décide), **trois exécutions** :

| Méthode | Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Durée (14 cas) |
|---|---|---|---|---|---|
| Fiches (référence) | 74 % (64 – 79 %) | 60 % | 2 | 0 | ~1 min |
| **Règles Prolog** | **100 % (100 – 100 %)** | **90 % (86 – 93 %)** | **0** | **0** | **3 à 4 s** |

Un cas instable : velo-03 (cave au cadenas), une fois INCERTAIN au lieu de NON_COUVERT, réponse
acceptable ; l'écart vient de la lecture des faits, pas des règles. velo-07 (garage) reste
INCERTAIN, avec la bonne question : la serrure est-elle de sûreté ?

**Ce que ce résultat ne prouve pas encore**, à dire avant qu'on le découvre :
- les règles ont été écrites **en connaissant les 14 cas** : le score est optimiste. Ce qui le rend
  crédible : chaque règle cite mot pour mot une phrase du contrat, aucune n'est écrite pour un cas ;
- trois garanties seulement sont en règles (vol, incendie, dégâts des eaux) ;
- les réponses attendues ont été proposées par Claude et restent à valider.

La preuve suivante : de **nouveaux cas écrits sans regarder les règles**, puis des règles **écrites
par Mistral Large** pour les autres garanties, contrôlées de la même façon.

### 7.17 Le jeu de validation : quinze cas nouveaux, et deux couverts à tort

**Ce qui a été fait.** Quinze sinistres nouveaux (`data/validation/`), chacun annoté d'après
**l'article des CG qui le tranche**, cité dans la note : fenêtre laissée ouverte pendant l'absence,
vol par la femme de ménage, biens d'un hôte, mobilier de terrasse, simple disparition d'une montre,
dépôt chez un réparateur, vol avec menaces dans le métro, court-circuit et flammes, brûlure de fer
à repasser, canalisation gelée chauffage coupé, infiltration par une fenêtre, baignoire qui
déborde, tempête, chat volé, scooter de 125 cm³. Les cas visent des clauses que les 14 premiers
ne touchaient pas, et quelques pièges du texte (la définition du contenu inclut les biens des hôtes,
la garantie vol les exclut ; une baignoire est reliée à l'installation, l'exclusion du récipient ne
joue pas).

**Honnêteté sur la méthode.** Les cas ont été écrits par Claude, qui a aussi écrit les règles : ce
n'est pas un jeu « aveugle ». Ce qui limite le biais : les réponses attendues viennent du texte des
CG, relu pour l'occasion, pas des règles ; et la mesure a été **enregistrée avant toute correction**.
Un jeu écrit par l'auteur, ou par un gestionnaire, vaudrait mieux.

**La règle du jeu.** Le jeu de validation ne sert qu'à mesurer. Si l'on corrige les règles après
l'avoir vu, ses cas deviennent des cas de mise au point, et il en faut de nouveaux. D'où deux jeux
séparés, choisis par `--jeu mise_au_point|validation`, et un test qui vérifie la cohérence du jeu
mais **pas son score**.

**Première mesure, règles seules sur les faits idéaux** (oracle Python, à confirmer par
`couverture regles --jeu validation` sur le poste) :

| | Justes ou acceptables | Exactes | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| Mise au point (14 cas) | 100 % | 93 % | 0 | 0 |
| **Validation (15 cas)** | **87 % (13/15)** | **80 % (12/15)** | **2** | **0** |

La tempête (val-13), garantie non écrite en règles, donne INCERTAIN : le système avoue sa limite au
lieu de refuser, comme voulu.

**Les deux erreurs ont la même cause : des obligations de prévention que ni le vocabulaire ni les
règles n'expriment.**
- val-01, fenêtre ouverte pendant l'absence : l'obligation du 2.10 vise les portes **et** les
  fenêtres ; le vocabulaire ne connaît que `portes_fermees`. Les portes étaient fermées, la règle
  couvre.
- val-10, gel chauffage coupé : le 2.7 exclut le gel sauf si les mesures de prévention ont été
  respectées ; ni cette exclusion ni l'obligation (chauffer, vidanger ou isoler) ne sont en règles.

C'est la limite annoncée par l'architecture elle-même : **le moteur ne peut pas être plus juste que
le vocabulaire**. Un fait que personne n'a prévu de demander est un fait que le système ignore,
et l'ignorer ici veut dire couvrir. Deux pistes, à trancher avant de corriger :
1. compléter le vocabulaire et les règles (fenêtres, mesures contre le gel) : simple, mais c'est
   de la mise au point, et il faudra un nouveau jeu de validation ;
2. plus général : pour chaque obligation du contrat, faire de l'absence du fait un **inconnu qui
   empêche de conclure COUVERT** quand l'obligation est pertinente (absence, période de gel) :
   le système poserait la question au lieu de couvrir.

Confirmé sur le poste par SWI-Prolog (`couverture regles --jeu validation`) : mêmes 15 réponses.

**Chaîne complète sur le jeu de validation** (Mistral Small lit les faits, Prolog décide), trois exécutions :

| Jeu | Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains | Instables |
|---|---|---|---|---|---|---|
| Mise au point (14 cas) | 100 % | 90 % | 0 | 0 | | 1 |
| **Validation (15 cas)** | **67 %** | **60 %** | **2** | **1** | **20 %** | **0** |

Les réponses sont parfaitement stables d'une exécution à l'autre : les écarts ne sont pas du bruit,
ce sont des erreurs reproductibles.

**Les faits réellement lus** (`couverture analyser --methode regles` sur les quatre cas qui
diffèrent). Deux hypothèses sur quatre étaient fausses, et l'erreur était de mon côté :

| Cas | Faits lus par Mistral Small | Décision | Ce qui s'est passé |
|---|---|---|---|
| val-04 terrasse | vol ; mobilier_jardin ; terrasse ; absence=oui | INCERTAIN | **Lecture juste.** `vol_sur_personne` n'est pas dit ; la garantie « vol commis sur l'assuré » reste possible et l'emporte sur l'exclusion du mobilier extérieur |
| val-15 scooter | vol ; vehicule_moteur ; garage ; clé ; effraction | INCERTAIN | **Lecture juste.** Même mécanisme, avec la même question absurde : « le vol a-t-il été commis sur vous ? » |
| val-06 réparateur | vol ; electronique ; chez_reparateur ; effraction | INCERTAIN (acceptable) | « il y a deux semaines » n'est pas traduit en `depot_moins_30j=oui` ; la question posée est la bonne |
| val-13 tempête | **degat_eaux** ; infiltration_exterieure | **NON_COUVERT** | La tempête disparaît : la pluie entrée devient une infiltration, exclue par le 2.7 |

**Quatre constats, plus utiles que le score.**
1. **Mes faits « idéaux » étaient trop généreux.** J'avais écrit `vol_sur_personne: non` parce que
   le récit le laisse entendre ; une lecture fidèle ne l'invente pas. Les 87 % « règles seules »
   étaient donc optimistes, par le choix des faits et non par les règles.
2. **Le moteur ne suit pas la charge de la preuve pour les garanties « possibles ».** Une garantie
   dont l'assuré n'allègue aucun fait (des violences jamais mentionnées) l'emporte sur une exclusion
   établie, et produit INCERTAIN. La méthode par fiches avait tranché autrement (7.12) : NON_COUVERT
   pour la garantie concernée, avec les questions des garanties possibles « à vérifier ».
3. **Un seul événement ne suffit pas.** Une tempête qui fait entrer la pluie a une **cause** (la
   tempête) et un **dommage** (l'eau) ; le vocabulaire n'a qu'une variable `evenement`, la lecture a
   gardé le dommage et perdu la cause. Et un événement pour lequel aucune règle n'est écrite devrait
   rendre la décision au plus INCERTAIN, quoi que disent les autres garanties : c'est le seul moyen
   que « je ne sais pas » reste vrai quand le contrat n'est pas entièrement traduit.
4. **Des questions sans rapport** : pour la tempête, le système demande s'il y a eu des flammes. La
   garantie incendie est jugée « possible » parce que son périmètre est défini par les flammes, sans
   lien avec l'événement déclaré. Une question doit venir d'une garantie plausible.

**Ce que cela dit.** Le maillon faible n'est pas seulement la lecture : c'est **le contrat entre la
lecture et les règles**, ce qu'on attend de la lecture (cause et dommage, faits non allégués) et ce
que le moteur fait de ses silences. La lecture se trompe franchement une fois sur quatre (val-13),
et c'est la plus coûteuse : un refus ferme. Le cadre à trois valeurs protège contre un fait
**absent**, pas contre un fait **mal lu**.

**Corrections envisagées**, à faire en sachant qu'elles transforment ces 15 cas en mise au point (il
faudra un nouveau jeu de validation, idéalement écrit par l'auteur) :
1. vocabulaire : `cause` séparée de `dommage` (ou `evenement` à plusieurs valeurs) ; fenêtres ;
   mesures contre le gel ;
2. moteur : un événement sans règles → au plus INCERTAIN ; une garantie possible sans fait allégué
   ne masque plus une exclusion établie (NON_COUVERT, questions « à vérifier ») ; questions limitées
   aux garanties plausibles ;
3. seconde lecture des faits comparée par le code : un désaccord sur un fait décisif rend ce fait
   inconnu, donc la décision au plus INCERTAIN, jamais un refus.

### 7.17 bis Une dépendance hors de Python, et un test qui ne passait que sous Linux

**SWI-Prolog n'est pas dans `uv.lock`, et c'est normal.** Le verrou de uv ne connaît que des
paquets Python ; SWI-Prolog est un programme, appelé en sous-processus (`swipl`), comme git. Le
pont Python officiel (`janus-swi`) exigerait de toute façon le programme installé. La dépendance
est donc :
- décrite dans le README (winget sous Windows, apt sous Linux) ;
- vérifiée à l'exécution (`couverture regles` dit « SWI-Prolog introuvable » et donne la commande) ;
- installée dans l'image Docker (`swi-prolog-nox`). En le vérifiant, un second oubli est apparu :
  l'image ne copiait pas le dossier `regles/`. Reste à vérifier par `docker compose build` que
  le paquet installé (non éditable) retrouve bien `regles/` et `config/` ;
- à ajouter à la CI (`.github/workflows/ci.yml`, modifié par l'auteur) : sans elle, les tests
  Prolog y sont sautés.

**Un test qui échouait sous Windows** (`test_archive_des_consignes`) : l'archivage renvoyait des
chemins avec « \ », le test cherchait des « / ». Ce n'était pas un défaut de logique, mais un
défaut de portabilité que la CI sous Linux ne pouvait pas voir. Correction : chemins écrits avec
« / » sur tous les systèmes (`as_posix`). Leçon : faire tourner les tests aussi sur le système de
l'auteur.

### 7.18 Corrections après la validation : le contrat entre la lecture et les règles

Décision prise avec l'auteur : corriger maintenant, en sachant que **les 15 cas de validation
deviennent des cas de mise au point**. Un nouveau jeu, écrit par l'auteur sans Claude, mesurera
ces corrections.

**Ce qui a changé, et pourquoi chaque changement vient du contrat ou d'un principe, pas d'un cas :**

| Changement | Où | Justification |
|---|---|---|
| `evenement` prend plusieurs valeurs : la cause **et** le dommage | vocabulaire, consigne faits-regles v2 | Une tempête qui fait entrer la pluie a deux natures ; la lecture gardait le dommage et perdait la cause (val-13) |
| `evenement_traduit(...)` dans chaque contrat ; un événement déclaré non traduit plafonne la décision à INCERTAIN | moteur (règle 8), règles Assureur A | Un refus ne vaut que si toutes les garanties en jeu ont été examinées. Sans déclaration, tout événement est « non traduit » : le défaut est prudent |
| « vol commis sur l'assuré » : périmètre `non(concept(batiment))` | règles Assureur A | Le texte dit « en dehors des biens assurés » ; la règle l'avait omis, d'où la question absurde pour un scooter volé au garage (val-04, val-15) |
| incendie : périmètre lié aux événements incendie, explosion, foudre | règles Assureur A | Une garantie ne pose de questions que sur ce qu'elle couvre (pas de « flammes ? » pour une tempête) |
| obligation de fermer les fenêtres en cas d'absence | vocabulaire `fenetres_fermees`, règles Assureur A | Citée mot pour mot au 2.10 ; seules les portes étaient traduites (val-01) |
| exclusion du gel sauf mesures de prévention | vocabulaire `prevention_gel`, règles Assureur A | Citée mot pour mot au 2.7 ; absente des règles (val-10). Mesures inconnues : réserve, pas refus (l'assureur prouve l'exclusion) |
| durées traduites (« il y a deux semaines » → moins de 30 jours) | consigne faits-regles v2 | La lecture ne faisait pas la conversion (val-06) |

Ce qui n'a **pas** été changé, et pourquoi : la règle de combinaison. Elle donnait déjà la priorité
à une garantie rattachée sur une garantie seulement possible ; les deux INCERTAIN de val-04 et
val-15 venaient d'une garantie que le texte du contrat aurait dû écarter, pas du moteur.

**Mesure, règles seules (oracle Python), avec des faits idéaux réalistes** (pour val-04 et
val-15, `vol_sur_personne` n'est plus renseigné : c'est ce que donne la vraie lecture) :

| Jeu | Justes ou acceptables | Exactes | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| Mise au point d'origine (14 cas) | 100 % | 93 % | 0 | 0 |
| Ex-validation (15 cas, désormais mise au point) | 100 % | 87 % | 0 | 0 |

val-01 (fenêtre ouverte) donne INCERTAIN avec la question du lien causal : le contrat ne refuse
que s'il y a un lien causal direct, et c'est au gestionnaire de le constater. val-13 (tempête)
donne INCERTAIN avec « l'événement tempete relève d'une garantie pas encore traduite ».

**Ce que ces chiffres valent** : ce sont des chiffres de mise au point, optimistes par construction.
La preuve viendra d'un **nouveau jeu écrit par l'auteur**, puis de la chaîne complète (Mistral lit
les faits) sur ce jeu, trois exécutions.

### 7.19 Les règles écrites par le modèle : une rédaction contrôlée

**La question de l'auteur** : « les contrats ne seront pas structurés ». C'est vrai : des centaines
de contrats ne se traduisent pas à la main. La structure doit être **tirée du contrat par la
machine, une fois par version des conditions générales, puis contrôlée**. Le découpage en clauses
l'est déjà (147 clauses typées, sans intervention) ; restait la traduction en règles.

**Ce que dit la littérature** (arXiv 2502.17638, déjà cité en 7.15) : un modèle qui traduit un texte
juridique en Prolog **sans cadre** fait moins bien qu'un modèle qui répond directement ; avec un cadre
(schéma, vocabulaire, vérifications), il fait mieux. Tout le travail porte donc sur le cadre.

**La conception** (`src/couverture/redaction.py`, commande `couverture rediger`) :
- **Le modèle n'écrit pas de Prolog** : il remplit un schéma JSON (périmètre, circonstances,
  obligations, exclusions, limites), et le code écrit les règles. Un JSON se contrôle champ par
  champ ; une syntaxe inventée ne se contrôle qu'en la chargeant.
- **Il reçoit** le texte de l'article et de ses sous-sections, les définitions du contrat dont le
  terme y apparaît, le vocabulaire commun, et les concepts déjà traduits (bâtiment, contenu…).
- **Il ne doit rien approximer** : un fait absent du vocabulaire est **déclaré**
  (`vocabulaire_manquant`, avec la question à poser à l'assuré) ; une phrase qu'il ne sait pas
  traduire est **déclarée** (`non_traduit`). L'humain décide.
- **Six contrôles automatiques** : structure ; vocabulaire ; citations mot pour mot (réparées si
  les mots sont dans l'ordre) ; **couverture** (chaque élément des listes d'exclusions du contrat
  est traduit ou déclaré : une exclusion oubliée, c'est un couvert à tort) ; concepts et
  identifiants ; avec SWI-Prolog, chargement sans avertissement et **non-régression** sur les 29 cas
  déjà annotés (les décisions qui changent sont listées).
- **Rien n'entre dans le contrat sans un humain** : `--accepter-vocabulaire` pour les faits nouveaux,
  correction possible du JSON puis `--controler` (sans rappeler le modèle), et `--accepter`
  seulement si aucun contrôle ne bloque.

**Et la recherche (BM25 + embeddings, fusion RRF) ?** Elle sert la méthode `conditions` : trouver
le bon passage d'un document qu'on ne connaît pas. La méthode `regles` n'en fait pas : le moteur
examine **toutes** les garanties traduites, une exclusion ne peut pas être manquée parce qu'elle
était mal classée, et les citations sont écrites dans les règles puis vérifiées, pas retrouvées par
similarité. La recherche garde deux rôles dans ce schéma : à la rédaction, retrouver pour une
garantie les définitions et exclusions éloignées (aujourd'hui fait par les titres et les termes
définis, voir `definitions_utiles`) ; au moment du sinistre, montrer au gestionnaire les passages
à lire quand l'événement relève d'une garantie pas encore traduite.

**L'expérience** : tempête (2.2) et bris de vitrages (2.9), deux garanties que personne n'a
traduites. Les 10 cas de test (`data/redaction/`, jeu `redaction`) ont été écrits d'après le texte
des CG **avant** la rédaction : pour une fois, les cas ne connaissent pas les règles. Ce qu'on
mesurera :
1. combien de contrôles passent sans retouche, et lesquels échouent ;
2. ce que le modèle déclare de lui-même (vocabulaire, non traduit) plutôt que d'inventer ;
3. après relecture et acceptation, la chaîne complète sur les 10 cas, trois exécutions.

Le contrôle de couverture a été vérifié sur le vrai texte : une proposition simulée qui oubliait
trois des sept exclusions de l'art. 2.2 a été arrêtée, avec les trois phrases.

### 7.20 Deux mesures : la chaîne complète après corrections, et la première rédaction par Mistral Large

**1. Chaîne complète sur les 15 ex-cas de validation** (devenus mise au point en 7.18), Mistral Small
lit les faits avec la consigne faits-regles v2, trois exécutions. Les règles seules, avec SWI-Prolog,
confirment l'oracle : 100 % sur les deux jeux, « Tout est en ordre », 119 tests réussis sous Windows.

| | Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Instables |
|---|---|---|---|---|---|
| Avant les corrections (7.17) | 67 % | 60 % | 2 | 1 | 0 sur 15 |
| **Après (7.18)** | **87 % (73 – 93 %)** | **82 %** | **0,7 en moyenne (0 – 2)** | **0** | **4 sur 15** |

- Le refus à tort de la tempête a disparu, et les quatre lectures « justes mais mal exploitées »
  (val-04, val-06, val-10, val-15) sont désormais exactes.
- val-13 (tempête) donne COUVERT trois fois, mais par la garantie dégâts des eaux : la lecture n'a plus
  vu d'infiltration. Bonne réponse, raison discutable : la garantie tempête n'était pas encore traduite.
- **Le prix : la lecture est devenue instable.** Quatre cas changent d'une exécution à l'autre, et
  deux de ces écarts sont des couverts à tort : une fois la fenêtre ouverte n'est pas lue (val-01),
  une fois les biens de l'hôte non plus (val-03). La consigne v2 demande plus de choses ; à
  température 0, Mistral Small n'est pas pour autant déterministe.
- Conséquence : **la seconde lecture des faits comparée par le code** (8) devient la priorité. Un fait
  décisif sur lequel deux lectures divergent devient inconnu, ce qui empêche un couvert à tort.

**2. Première rédaction réelle : tempête (2.2) et bris de vitrages (2.9)**, consigne redaction-regles v1,
Mistral Large, environ 4 min 30 par article.

Ce que le modèle a bien fait, et c'est l'essentiel :
- 2.2 : **les 7 exclusions de la liste traduites**, **toutes les citations exactes**, et **9 faits
  nouveaux déclarés** (grêle, pression de la neige, construction délabrée, close et couverte, objet à
  l'extérieur, matériaux à pied d'œuvre, ancrage en béton…), aucun inventé en silence. Il a même
  recopié la coquille du contrat (« Ensembe des constructions ») : il cite, il ne réécrit pas ;
- 2.9 : **les 9 exclusions traduites**, avec un vocabulaire nouveau pour les vitres et biens assimilés.

Ce qui a échoué :
- 2.2 : **un écart au schéma** (une définition écrite avec « id, nom » au lieu de « concept,
  condition ») ; et **l'oubli de la définition de la tempête** : le contrat ne parle de tempête qu'avec
  un vent d'au moins 80 km/h, ou des dégâts aux biens voisins. Sans elle, la règle couvrirait tout
  coup de vent. Aucun contrôle ne l'aurait vu : la liste d'exclusions était complète ;
- 2.9 : un concept employé sans être défini (`sanitaires`), et un événement inventé (`felure`) ;
- **et un défaut de mon côté** : le concept inconnu a fait échouer SWI-Prolog pendant la
  non-régression, l'exception n'était pas attrapée, et **la réponse du modèle pour 2.9 a été perdue**
  (seules les règles générées sont restées).

Corrections (consigne redaction-regles v2, code) :
- la réponse du modèle est **enregistrée dès qu'elle arrive**, avant tout contrôle ;
- le schéma est contrôlé explicitement, avec des messages en clair, et **une seule reprise** renvoie
  au modèle ses écarts (« un élément de definitions n'a pas concept, condition ») ;
- un nouveau contrôle exige que **la définition de l'événement couvert** (« tempête ») soit employée
  ou déclarée non traduite ;
- Prolog n'est pas lancé tant qu'un concept est inconnu, et une erreur par cas devient un contrôle
  bloquant au lieu d'un plantage ;
- la consigne donne un exemple de définition et de limite, et la règle 6 sur l'événement défini.

La vraie réponse pour 2.2 est gardée comme jeu de test (`tests/fixtures/`) : les contrôles v2
l'arrêtent sur le schéma, puis, une fois l'écart corrigé, sur la définition de la tempête.

**Bilan provisoire de la rédaction** : sur le fond (exclusions, citations, faits déclarés), Mistral
Large fait le travail. Sur la forme et sur les conditions implicites (une définition qui restreint la
garantie), il faut le cadre. C'est ce que disait la littérature, mesuré ici sur le vrai contrat.

**Autre signal** : GitHub signale 43 vulnérabilités dans les dépendances verrouillées (5 critiques).
À traiter par une mise à jour du verrou (`uv lock --upgrade`) et une relecture des paquets
optionnels (MLflow en tire beaucoup).

### 7.21 Le golden set et le banc d'essai : tout vérifier d'un coup

**La demande de l'auteur** : « un golden set béton, en banc, pour qu'on vérifie tout ». Jusqu'ici,
chaque étape avait son jeu de cas (mise au point, validation, rédaction), mesuré à part, avec ses
propres commandes. Il manquait **une référence unique, figée, qu'on rejoue à chaque changement**.

**Le golden set** (`data/golden/`, version 1, 68 cas, voir son LISEZMOI) :
- les 39 cas existants, **étiquetés**, et 29 cas nouveaux qui comblent ce qu'aucun jeu ne testait :
  la **langue** (langage familier, fautes de frappe, déclaration longue et bavarde, négation),
  les **informations manquantes** (le système doit poser *la bonne* question), de nouveaux **pièges**
  du texte (clé sous le paillasson, seau renversé, aquarium, fumée sans incendie, casier du club),
  les **garanties non traduites** (électricité, mazout, catastrophes naturelles, attentat : jamais
  un refus), et les **sinistres multiples** (cambriolage et vitre cassée, incendie et eau d'extinction) ;
- chaque cas : réponse attendue et tolérée, clauses et questions attendues, garantie, thèmes,
  origine, auteur, une note qui cite le contrat, et ses faits idéaux ;
- **figé par une empreinte** : toute modification passe par `couverture banc --figer "raison"`, sinon
  un test échoue ;
- **à valider par l'auteur** : `--fiche` écrit une fiche de relecture par garantie (`A_VALIDER.md`),
  et le rapport compte les cas validés.

**Le banc** (`src/couverture/banc.py`, `couverture banc`) rejoue le golden set en **trois couches**,
pour savoir *où* naît une erreur, ce que les mesures précédentes ne disaient pas :
1. **règles** : faits idéaux → moteur, sans modèle ;
2. **lecture** : faits lus par le modèle comparés aux faits idéaux, fait par fait (rappel,
   **contradictions**, faits en trop) ;
3. **chaîne** : la méthode complète, trois exécutions, cas instables listés.
Il mesure aussi le rappel des clauses et des **questions**, et le nombre de questions posées par
réponse « incertain » (six questions pour un vélo volé, personne ne les lit). Des **portes**
(`seuils.json`) décident si le système est présentable, et la commande sort en erreur si l'une échoue :
on peut la brancher sur la CI. Chaque passage est gardé (`data/bancs/`) et comparé au précédent.

**Premier passage, couche règles (oracle Python ; à confirmer par SWI-Prolog sur le poste)** :

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 84 % | 66 % | **2** | **7** | 25 % |

Les portes échouent, et c'est le but : le banc voit ce que les jeux précédents ne voyaient pas.
- **2 couverts à tort**, deux phrases du contrat absentes des règles : l'obligation de ne pas laisser
  les clés à proximité (g-p03), l'exclusion du récipient non relié à l'installation (g-p06).
- **7 refus à tort**, deux causes :
  - les **garanties non traduites** déclarées avec l'événement « autre » (électricité, mazout) ou
    « dégât des eaux » (inondation, égouts) : le plafond « au plus INCERTAIN » de 7.18 ne joue que
    pour un événement nommé et non traduit. Le vocabulaire n'a pas de valeur pour ces périls, donc
    la lecture ne peut pas les nommer : **le vocabulaire doit connaître tous les périls du contrat**,
    même ceux dont les règles ne sont pas écrites ;
  - la **fumée sans incendie** (g-p07) : 2.1 couvre aussi « le dégagement de suie et de fumée »,
    absent des règles.
- Par thème : 100 % sur la langue, les informations manquantes, les variantes et les sinistres
  multiples ; 63 % sur les garanties non traduites. Par garantie : 2.3, 2.6 et 2.8 à 0 %.

**Ce que le banc ne vérifie pas encore** : les montants (limites d'indemnisation), et des cas écrits
sans Claude. Les 68 réponses attendues sont toutes de Claude : le golden set n'est « béton » qu'une
fois validé par l'auteur.

### 7.22 Deuxième rédaction (consigne v2) : 2.9 propre, 2.2 trop lente, et un vocabulaire qui doit devenir une hiérarchie

**Ce qui s'est passé** (Mistral Large, consigne redaction-regles v2, 18 min au total) :
- **2.2 (tempête)** : pas de réponse en 300 s, deux fois. La consigne v2 est plus longue et la
  garantie touche trois périls ; le délai est porté à 600 s pour la rédaction. La proposition v1
  reste en place, rien n'est perdu (la sauvegarde immédiate de 7.20 a joué son rôle).
- **2.9 (bris de vitrages)** : réponse conforme au schéma du premier coup (pas de reprise), les
  9 exclusions traduites, la définition des sanitaires ajoutée (l'oubli de la v1 est corrigé),
  aucun élément non traduit. Il ne reste que des **décisions humaines** :
  - 22 faits nouveaux déclarés (16 sortes de biens, travaux, vitre placée, type de dommage) ;
  - 3 exclusions qui ne visent qu'un bien mais excluraient tout le sinistre (signalées par un
    nouveau contrôle « portée », à relire) ;
  - une citation exacte mais rattachée à « 12 » au lieu de « 12/sanitaires » : désormais
    rattachée automatiquement à la seule clause qui contient le texte.

**Le problème de conception que 2.9 révèle : le vocabulaire est plat.** Le modèle propose `vitre`,
`miroir`, `chassis`… Mais une vitre est aussi un élément du bâtiment : si la lecture écrit
« vitre », les garanties incendie et dégâts des eaux, qui demandent `element_batiment`, ne la
reconnaissent plus. Ajouter des valeurs fines casse les règles écrites avec des valeurs larges.
Réponse : une **hiérarchie** dans le vocabulaire (`"parents": {"vitre": ["element_batiment"]}`) ;
avant la décision, le code ajoute les parents aux faits lus (`prolog.etendre_faits`, transitif,
idempotent). Une règle large reconnaît une valeur fine sans que la lecture ait à tout énumérer,
et une règle fine reste précise. Le banc et les contrôles de non-régression passent par la même
extension.

**Ce qui reste à décider par l'auteur** pour 2.9 : accepter le vocabulaire (en fusionnant au
besoin), donner ses parents à chaque valeur nouvelle, corriger les trois portées, puis
`--controler` et `--accepter`. Les faits idéaux des cas de bris du golden set devront être
réécrits dans le nouveau vocabulaire : c'est une nouvelle version du golden set, notée comme telle.

### 7.22 bis La hiérarchie, refaite à trois valeurs ; 2.9 relue ; golden set v2

**L'auteur a accepté le vocabulaire de 2.9** (`--accepter-vocabulaire 2.9`, 21 ajouts). La
non-régression a aussitôt signalé 7 cas de bris passés d'INCERTAIN à NON_COUVERT : leurs faits
idéaux disaient « élément du bâtiment » pour une vitre, et la nouvelle règle demande « vitre ».

**Ma première hiérarchie était fausse.** Elle ajoutait les parents aux faits avant la décision (une
vitre devient aussi « élément du bâtiment »). Deux défauts : un fait vague (« élément du bâtiment »)
restait un refus pour une règle précise, et une télévision devenait aussi « électronique », si bien
que l'exclusion qui ne vise que les appareils audiovisuels devenait partielle à tort.

**La version retenue est dans le moteur, à trois valeurs** (`moteur.pl`, et l'oracle) :
- un fait précis vaut pour sa catégorie : « vitre » répond **oui** à une règle sur « élément du bâtiment » ;
- un fait vague ne tranche pas : « élément du bâtiment » répond **inconnu** à une règle sur « vitre »,
  et le moteur demande « Quels biens sont endommagés ? » au lieu de refuser ;
- un fait sans rapport reste **non** ; une catégorie et sa sous-catégorie ne comptent pas comme
  deux biens pour une exclusion partielle.
La hiérarchie vient du vocabulaire (`"parents"`), et Python la pose en faits pour le moteur. C'est la
même idée que la logique à trois valeurs de 7.16 : ne jamais confondre « je ne sais pas » avec « non ».

**Relecture de 2.9** (à la demande de l'auteur, notée dans la proposition) : les trois exclusions qui
ne visent qu'un bien n'excluent plus que ce bien (appareils audiovisuels, objets en verre ; serres et
couvertures de piscine, scindées en deux).

**Golden set v2** : les faits idéaux des 8 cas de bris sont réécrits dans le nouveau vocabulaire
(vitre, table de cuisson, appareil audiovisuel, objet en verre, miroir non placé, rayure). Mesure,
règles seules (oracle), avant et après l'ajout des règles de 2.9 rédigées par Mistral Large et relues :

| | Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|---|
| Sans 2.9 | 84 % | 66 % | 2 | 7 | 25 % |
| **Avec 2.9** | **85 %** | **77 %** | **2** | **7** | **15 %** |

Les 8 cas de bris sont exacts, aucun couvert à tort n'apparaît, et les erreurs restantes sont
celles de 7.21 (clés, récipient, fumée, périls non nommés). **Première garantie rédigée par le modèle,
contrôlée, relue et mesurée** : il a fallu une relecture de trois portées et une décision de
vocabulaire, pas une réécriture.

**Deux fautes de ma part au premier passage sur le poste** : `banc.py` n'avait pas été déposé (il
appelait encore l'extension abandonnée), et les nouvelles règles `ancetre`/`vague` étaient insérées au
milieu des clauses de `eval`, ce que SWI-Prolog signale par un avertissement (traité comme une
erreur, à raison). L'oracle Python ne pouvait pas le voir. Un test vérifie désormais, sans
SWI-Prolog, que les clauses de chaque prédicat se suivent (moteur et règles du contrat), et la liste
des fichiers déposés est relue avant chaque dépôt.

### 7.23 Premier banc complet sur le poste : 2.9 acceptée, et ce que le banc dit vraiment

**2.9 est entrée dans le contrat** : `--controler` sans contrôle bloquant ; la non-régression
liste les 7 cas de bris qui passent d'INCERTAIN à leur réponse attendue ; `--accepter 2.9` ;
`couverture regles` : « Tout est en ordre », 52 citations vérifiées, 99 couples du vocabulaire.
150 tests réussis sous Windows, dont les tests SWI-Prolog. **Première garantie rédigée par le
modèle et en service.**

**Premier passage complet du banc** (golden v2, 68 cas, chaîne en trois exécutions, 40 s chacune) :

| Couche | Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Instables |
|---|---|---|---|---|---|
| Règles seules (SWI-Prolog) | 85 % | 76 % | 2 | 7 | — |
| Chaîne complète | 83 % (81 – 85 %) | 66 % | **5 (5 – 5)** | 4 (3 – 5) | 8 sur 68 |

Toutes les portes échouent. Les **5 couverts à tort de la chaîne** sont les mêmes à chaque exécution :
- 2 viennent des **règles** (déjà vus en 7.21) : la clé sous le paillasson, le seau renversé ;
- 3 viennent de la **lecture** :
  - g-l01 : « le local à vélos de la résidence » lu comme une annexe privée, au lieu des parties communes ;
  - red-b05 : « pas encore accroché » non lu comme une vitre non placée ;
  - g-q03 : « pendant mes courses » : un lieu dans le bâtiment est inventé, au lieu de rester inconnu.
Plus val-01 (la fenêtre ouverte), lue une fois sur trois.

**Le banc lui-même était mal calibré sur la lecture.** Il annonçait 82 % de faits retrouvés et
22 cas « contredits », mais :
- il comptait comme manquants les faits négatifs que la déclaration ne dit pas (« pas de
  violence ») : la consigne interdit justement de les inventer ;
- il comptait comme contradiction un mot plus vague ou plus précis (« électronique » pour une
  télévision), que la hiérarchie de 7.22 bis traite correctement.
**Correction de l'instrument** : la mesure qui compte est **« la lecture change-t-elle la
décision ? »**. Le banc passe désormais les faits lus dans les mêmes règles que les faits
idéaux, et compare les décisions : c'est la part d'erreur qui vient de la lecture et d'elle
seule. Les contradictions tiennent compte de la hiérarchie (un fait vague est signalé à part).
Les portes de la lecture changent en conséquence (décisions changées ≤ 2, vers un couvert à
tort : 0, contradictions ≤ 5), au lieu du rappel brut ≤ 90 % qui mesurait mal : c'est un
changement d'instrument, pas un relâchement.

**La suite, dans l'ordre** :
1. relancer le banc avec l'instrument corrigé : la mesure de référence propre ;
2. la lecture : donner au modèle le **sens** de chaque variable et de chaque valeur proche
   (parties communes ou annexe, débordement d'un récipient ou fuite, électronique ou audiovisuel),
   et la règle de ne jamais inventer un lieu ;
3. les règles : clés, récipient, fumée, casier, et les périls non traduits nommés dans le vocabulaire ;
4. la seconde lecture comparée par le code, contre les 8 cas instables.
Chaque étape repassée au banc, une à la fois, pour savoir ce qu'elle apporte.

---

**Partie III — La lecture (18 novembre).** Les règles sont justes quand les faits le sont. Reste à lire juste, ou à savoir quand on a mal lu.

### 7.24 La lecture : nommer tous les périls, donner le sens des mots, retirer ce qui est hors sujet

**Référence** (commit `0833fe0`, banc du 17 nov. 16 h 40, golden v2) : règles seules 85 %, 2 couverts
et 7 refus à tort ; chaîne 84 %, **4,7 couverts à tort** par exécution ; la lecture change **13,3
décisions** par exécution, dont 5 vers un couvert à tort.

**Ce que le rapport du banc montrait** : le modèle **invente** des faits dans 53 cas sur 68.
- « Vélo volé pendant mes courses » devient « dans le logement, absent, portes et fenêtres
  fermées » : couvert à tort.
- Le fioul et la panne de courant deviennent des « dégâts des eaux » avec une cause inventée
  (« fuite », « gel ») : le vocabulaire n'avait aucun mot pour ces périls, la lecture prenait le
  plus proche.
- Du bruit partout : une cause d'eau pour une bougie, « travaux : aucun » pour une tempête. Le
  vocabulaire de 2.9 a multiplié les occasions.
- Deux confusions de sens : « local à vélos de la résidence » lu « annexe » ; « pas encore
  accroché » non lu comme « non placé ».

**Trois changements, du plus robuste au plus fragile** :
1. **Le code retire les faits hors sujet** (`prolog.filtrer_faits`) : chaque variable déclare les
   événements auxquels elle s'applique (« pour » dans le vocabulaire : une cause d'eau pour un
   dégât des eaux, des travaux pour un bris…). Un fait lu hors sujet est retiré, quelle que soit la
   consigne ; c'est noté dans les avertissements. Sans événement lu, rien n'est retiré.
2. **Le vocabulaire nomme tous les périls du contrat** : électricité, mazout, catastrophe
   naturelle, attentat, fumée. Non traduits en règles, ils plafonnent la décision à INCERTAIN
   (7.18) : « à examiner », jamais un refus. C'est la leçon 36 appliquée.
3. **La consigne de lecture v3** donne au modèle, pour chaque variable, sa question et **le sens des
   valeurs proches** (« parties communes : local à vélos ou à poubelles commun… » ; « annexe :
   dépendance privée… » ; « récipient : seau, vase, aquarium » ; « fuite : appareil relié à
   l'eau, baignoire qui déborde »…), et une règle ferme : jamais un lieu, une absence, des portes
   fermées, un auteur ou une cause qui ne sont pas écrits. « Un fait inventé est plus grave qu'un
   fait manquant. »

**Golden v3** : les faits idéaux de 8 cas sont réécrits avec les nouveaux périls (électricité ×3,
mazout, catastrophe naturelle ×2, attentat, fumée). Tous les faits idéaux respectent le filtre
(un test le vérifie).

**Mesure, règles seules (oracle ; à confirmer sur le poste)** :

| | Justes ou acceptables | Exactes | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| Golden v2 | 85 % | 76 % | 2 | 7 |
| **Golden v3** | **96 %** | 76 % | 2 | **0** |

Les 7 refus à tort ont disparu : toutes les garanties non traduites répondent « à examiner ».
Restent les deux phrases du contrat absentes des règles (clé, récipient) et le casier. La porte
« exactitude des règles ≥ 95 % » passe pour la première fois. **L'effet sur la chaîne (lecture
v3 et filtre) reste à mesurer** : c'est le but de cette étape.

### 7.24 bis Le banc arrête une régression avant le commit

**Mesure sur le poste** (golden v3, lecture v3 et filtre) :

| | Règles seules | Chaîne : justes | Exactes | Couverts à tort | Refus à tort | Instables | Décisions changées par la lecture |
|---|---|---|---|---|---|---|---|
| Référence (v2) | 85 % | 84 % | 67 % | 4,7 | 4 | 5 | 13,3 |
| **Lecture v3** | **96 %** | **80 %** | **57 %** | 4,7 | **1,3** | 9 | **19** |

Les règles confirment le gain annoncé (96 %, aucun refus à tort, sur SWI-Prolog), mais **la chaîne
recule**. Le rapport du banc dit pourquoi, cas par cas :
- **en écrivant la v3, j'ai supprimé deux règles de la v2** : « une pièce du logement → lieu =
  logement » et « façade, murs, parquet → élément du bâtiment ». La nouvelle règle « n'ajoute
  jamais un lieu » a été obéie à la lettre : le modèle ne déduit plus le logement de « ma cuisine »
  ou « mon parquet », le bâtiment devient inconnu, et une dizaine de cas couverts passent à
  « incertain » (friteuse, fuite sous l'évier, chauffe-eau, aquarium…) ;
- deux inventions résistent : « pendant mes courses » lu « dans le logement », « disparu » lu
  « volé » ;
- l'aide du bris ne parlait que du verre : la table de cuisson fendue est lue « autre » (refus à tort).
Ce qui a marché : plus aucun fait hors sujet ne passe, les refus à tort tombent de 4 à 1,3.

**Consigne de lecture v4** : les deux règles rétablies ; « ce qui ne dit rien de l'endroit ne donne
pas de lieu » remplace l'interdiction trop large ; « disparu n'est pas volé » ; l'aide du bris
couvre la vitrocéramique et les sanitaires. **Avant de la livrer, la v4 a été comparée ligne à ligne
à la v2** (les archives `docs/consignes/` servent à cela) : c'est cette comparaison qui a trouvé la
deuxième règle perdue. Un test vérifie désormais que les règles qui ont fait leurs preuves restent
dans la consigne.

**Pas de commit sur une régression** : la v3 n'a pas été committée ; le banc l'a arrêtée.

### 7.25 Lecture v4 mesurée, et les quatre phrases du contrat qui manquaient

**Lecture v4 sur le poste** (golden v3) :

| | Chaîne : justes | Exactes | Couverts à tort | Refus à tort | Instables | Décisions changées par la lecture |
|---|---|---|---|---|---|---|
| Référence (v2) | 84 % | 67 % | 4,7 | 4 | 5 | 13,3 |
| Lecture v3 | 80 % | 57 % | 4,7 | 1,3 | 9 | 19 |
| **Lecture v4** | **86 %** | 62 % | **6** | **0** | 7 | 14,3 |

Gagné : aucun refus à tort ; le local à vélos est lu « parties communes » (g-l01 réglé) ; le
miroir non posé n'est plus couvert qu'une fois sur trois. Perdu :
- « disparu n'est pas volé » s'est **retourné** : le modèle garde « vol » et n'écrit plus
  « simple disparition », si bien que le vol est couvert trois fois sur trois (g-q02) ;
- les biens de l'hôte ne sont plus lus (val-03), trois fois sur trois ;
- « pendant mes courses » est toujours lu « dans le logement » (g-q03), malgré l'exemple mot pour
  mot dans la consigne.
**Leçon** : retoucher la formulation ne mène plus nulle part. Chaque règle ajoutée en déplace une
autre, et Mistral Small ignore même un exemple explicite. La suite doit être **structurelle** :
chaque fait décisif cite les mots de la déclaration qui le fondent, et le code vérifie qu'ils y sont
(comme les citations du contrat) ; puis une seconde lecture comparée par le code.

**Les quatre phrases du contrat qui manquaient aux règles** (vues par le banc dès 7.21) :
- la clé laissée à proximité (2.10) : obligation de prévention, excusée par l'effraction ; non
  respectée, le refus exige un lien causal, donc « incertain » avec la question ;
- le récipient non relié à l'installation (2.7) : exclusion ; l'aquarium et le matelas d'eau
  exceptés ont leur propre valeur dans le vocabulaire (`debordement_aquarium`) ;
- la suie et la fumée sans incendie (2.1) : dans le périmètre de la garantie incendie ;
- le casier d'une association sportive (2.10) : exclusion, avec un nouveau lieu `casier`.

**Et une règle du moteur** : une exclusion **certaine** écarte une garantie même si l'on ignore
encore si elle s'appliquerait. Sans elle, le vélo volé au casier restait « incertain » : il fallait
savoir s'il avait été volé « sur la personne », question absurde puisque l'exclusion règle tout.

**Mesure, règles seules (oracle ; golden v4)** : **100 % justes ou acceptables, 81 % exactes, aucun
couvert à tort, aucun refus à tort. Les portes des règles passent toutes, pour la première fois.**
Il ne reste d'erreurs que dans la lecture.

**Confirmé sur le poste** (SWI-Prolog, golden v4, 157 tests réussis) : règles seules 100 %, aucun
couvert ni refus à tort, porte des règles franchie. Chaîne complète :

| Chaîne | Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Instables |
|---|---|---|---|---|---|
| Référence (7.24) | 84 % | 67 % | 4,7 | 4 | 5 |
| **Lecture v4 + quatre règles** | **85 %** | 65 % | **3,7** | **3,7** | 8 |

Chaque indicateur coûteux fait au moins aussi bien que la référence : l'état est committé. Les
erreurs restantes sont toutes des erreurs de **lecture**. Couverts à tort : fenêtre ouverte non
lue (val-01), chauffage coupé non lu (val-10), « disparu » lu « volé » (g-q02). Refus à tort :
l'aquarium lu « récipient », si bien que la nouvelle exclusion s'applique (g-p05) ; la table de
cuisson non lue comme un bris ; l'inondation et les égouts non lus comme une catastrophe
naturelle. **Une règle plus juste rend plus coûteuse une lecture fausse** : c'est l'argument pour
le garde-fou structurel de la lecture (chaque fait décisif cite les mots de la déclaration).

### 7.26 Le garde-fou de la lecture : chaque fait cite les mots de la déclaration

État committé (`42b6b38`) : règles parfaites sur le golden set ; dans la chaîne, 3,7 couverts et 3,7
refus à tort par exécution, **tous dus à la lecture** : un fait inventé (« absent », « dans le
logement »), oublié (la fenêtre ouverte) ou mal choisi (l'aquarium lu « récipient »).

**Ce qui a été essayé avant** : retoucher la consigne (v3, v4). Chaque phrase ajoutée en a défait
une autre, et Mistral Small ignorait même un exemple écrit mot pour mot (7.25).

**Le garde-fou** reprend le principe des citations du contrat, appliqué à la déclaration : pour
chaque variable renseignée, le modèle recopie dans « appuis » **les mots exacts de la déclaration**
qui la fondent ; le code (`prolog.verifier_appuis`) vérifie que ces mots y figurent, à la ponctuation
et aux accents près, et **retire tout fait sans appui**. Le fait devient inconnu : le moteur pose la
question au lieu de couvrir ou de refuser sur un fait inventé. Si le modèle oublie complètement les
appuis, il est relancé une fois.

**Ce que le garde-fou ne fait pas, à dire avant de mesurer** : il vérifie que les mots *existent*,
pas qu'ils *prouvent* le fait. « Pendant que je faisais mes courses » est bien dans la déclaration ;
s'il est donné comme appui de « lieu = logement », le fait passe. Il arrête les inventions sans aucun
mot (« absent », « portes fermées » sortis de nulle part), pas un appui détourné. Un test documente
cette limite. Contre l'appui détourné, la piste suivante est une seconde lecture comparée par le
code.

Consigne de lecture **v5** : comparée ligne à ligne à la v4 avant livraison, elle ne fait
qu'**ajouter** la règle des appuis (aucune règle perdue, leçon 44).

**À mesurer au banc** : surtout les couverts à tort de la chaîne (3,7), et ce que le garde-fou coûte
en faits justes retirés (plus d'« incertain »).

**Premier passage sur le poste : trop strict.**

| Chaîne | Justes | Exactes | Couverts à tort | Refus à tort | Faits idéaux retrouvés |
|---|---|---|---|---|---|
| État committé | 85 % | 65 % | 3,7 | 3,7 | 77 % |
| Appuis, vérification stricte | 71 % | 35 % | **2** | 3 | **53 %** |

Les couverts à tort baissent (les inventions sont arrêtées), mais trop de faits justes sont retirés :
même le cambriolage avec la porte forcée devient « incertain ». **Le diagnostic, sur deux analyses
réelles** : pour un fait à plusieurs valeurs, le modèle colle les morceaux de la déclaration
(« forcé la porte volé mon ordinateur cassé la vitre », « meuble de cuisine parquet ») : tous les mots
y sont, dans l'ordre, mais pas d'un seul tenant, et la vérification les refusait. En revanche,
« violence : non » et « vol sur la personne : non » étaient retirés à raison : aucun mot ne les fonde.
**Correction** : un appui est accepté si ses mots figurent dans la déclaration dans le même ordre, avec
de petits écarts (le mécanisme qui répare déjà les citations du contrat) ; un mot absent suffit
toujours à refuser. Les appuis réels sont gardés en test. Le banc compte désormais les faits retirés
faute d'appui, pour mesurer le coût du garde-fou au lieu de le déduire.

**Second passage (appuis acceptés en morceaux ordonnés)** :

| Chaîne | Justes | Exactes | Couverts à tort | Refus à tort | Instables | Cas touchés par le garde-fou |
|---|---|---|---|---|---|---|
| État committé | 85 % | 65 % | 3,7 | 3,7 | 8 | — |
| Appuis stricts | 71 % | 35 % | 2 | 3 | 11 | — |
| Appuis assouplis | 74 % | 39 % | 2,7 | 3 | 14 | 20 sur 68 |

**Décision : le garde-fou est abandonné, retour à la lecture v4.** Il arrête bien des inventions
(couverts à tort 3,7 → 2,7), mais il retire surtout des faits **centraux et justes** : « vol » pour un
cambriolage avec la porte fracturée, « incendie » pour la friteuse en feu, « bris » pour la table de
cuisson fendue (l'événement et les biens comptent pour 15 des 30 faits retirés). Les inventions
visées (« dans le logement », « volé » pour « disparu ») sont rares. Deux essais, deux bilans
négatifs : on n'insiste pas. Ce qui reste : le banc compte désormais les faits retirés et note le
modèle de lecture. La consigne v5 reste archivée, marquée abandonnée.

### 7.27 Le modèle ou la méthode ?

L'auteur demande « le meilleur » plutôt qu'un compromis. Toutes les erreurs restantes sont des erreurs
de lecture, et Mistral Small a ignoré des consignes explicites (7.25). Avant de construire autre chose,
**une mesure qui ne demande aucun code** : la même chaîne, la même consigne (v4), avec **Mistral Large**
pour lire les faits (`COUVERTURE_MODELE=mistral-large-latest`). Elle dit si le plafond vient du modèle
ou de la méthode. Le banc note désormais le modèle dans le nom et l'en-tête de chaque rapport.

Ensuite, selon le résultat : si Large lit nettement mieux, **la double lecture comparée par le code**
(deux lectures ; un fait décisif sur lequel elles divergent devient inconnu) est la protection solide
contre les inventions, sans retirer les faits sur lesquels les lectures s'accordent.

### 7.28 Ce que Prolog apporte : le raisonnement par hypothèses

**La question de l'auteur** : « est-ce que Prolog apporte quelque chose ? » La réponse honnête, au
17 nov. : presque rien. Le moteur n'était qu'un évaluateur de conditions, et `moteur_reference.py`
le refaisait en Python à l'identique. L'auteur veut que Prolog apporte quelque chose : on lui donne
le travail pour lequel il est fait.

**Le défaut visé, mesuré par le banc** : quand la décision est « incertain », le moteur listait
toutes les questions possibles (jusqu'à six pour un vélo volé), sans dire lesquelles comptent ;
rappel des questions attendues : 67 %.

**Le raisonnement par hypothèses** (`explorer/2` dans `moteur.pl`) : pour chaque question, le moteur
**essaie chaque réponse possible** — il pose le fait (`assertz`), décide, le retire (`retract`) — et
classe la question :
- **décisive** : chaque réponse donne une décision ferme (« serrure de sûreté ? oui → couvert ; non →
  non couvert ») ;
- **utile** : une réponse au moins change la décision, sans toujours trancher seule ;
- **inutile** : la décision ne change pas, quelle que soit la réponse ; elle n'est plus posée.
Sans question décisive, il cherche **une paire de questions qui tranche toujours** (bornée à 400
essais). Les valeurs possibles viennent du vocabulaire (`vocabulaire.json`, lu par Prolog), et un
fait vague n'est essayé qu'avec ses précisions (hiérarchie de 7.22 bis).

**Ce que ça donne sur le golden set** (oracle ; à confirmer par SWI-Prolog) :
- le garage (velo-07) : une seule question tranche, et la réponse le dit (« oui → couvert ; non →
  non couvert ») ;
- la cave (g-q01) : aucune question seule ne suffit, mais « comment la cave était-elle fermée ? » et
  « serrure de sûreté ? » ensemble tranchent toujours ;
- **8 questions sur 29 étaient inutiles** (« y a-t-il eu des flammes ? » pour un ordinateur disparu) :
  elles ne sont plus posées ;
- **seuls 2 incertains sur 16 se tranchent par une ou deux questions** : les autres attendent une
  garantie non traduite ou une appréciation humaine (le lien de causalité). Le moteur le sait et le dit,
  au lieu de laisser croire qu'une question suffira.

**Ce que Prolog apporte, dit honnêtement** : le raisonnement hypothétique (poser un fait, décider,
le retirer) et la recherche d'un ensemble de questions sont naturels en Prolog, sur les mêmes règles,
en quelques dizaines de lignes. Python le fait aussi : l'oracle le refait pour le test différentiel,
et c'est la preuve qu'on contrôle ce que Prolog calcule. Mais c'est désormais un vrai usage,
mesurable au banc (incertains tranchés, questions inutiles retirées), pas une préférence de langage.
Prochain usage du même type : l'explication en arbre de preuve, et la comparaison de deux versions
d'un contrat (« quels sinistres changent de décision ? »).

### 7.29 La fiche métriques, et les jeux de cas externes

À la demande de l'auteur (« c'est la base pour démarrer »), les jeux de cas, les métriques, les seuils
et leurs limites sont réunis dans une fiche : [METRIQUES.md](METRIQUES.md). En la rédigeant, un
déséquilibre est apparu : le golden set ne compte que **3 cas dont la bonne réponse est « incertain »**
sur 68, alors que savoir dire « je ne sais pas » est au cœur de la demande du recruteur ; le jeu fermé
devra en contenir davantage.

**Recherche de jeux publics** : aucun ne donne la réponse selon les CG d'Assureur A (elle dépend du contrat).
Sources retenues : LegalBench `insurance_policy_interpretation` (138 couples déclaration-police, réponse
couvert / non couvert / ambigu, CC BY 4.0) comme second banc de généralisation ; les décisions des
médiateurs (FSPO irlandais, Financial Ombudsman britannique), la Médiation de l'Assurance et Judilibre
comme sources de situations réelles pour le jeu fermé, à réécrire et à annoter selon les CG d'Assureur A.

### 7.30 Le golden set complété (v5)

Trois manques relevés en 7.29 : trop peu de cas « incertain » (3 sur 68), des garanties jamais testées
(2.5 responsabilité immeuble, 2.11 dégradations, 2.12 mérule, exclusions générales 1.4), et peu de
situations comme les écrivent les clients. **29 cas ajoutés**, chacun avec une note qui cite les CG :
10 où la bonne réponse est « incertain » (le local de l'immeuble : commun ou privatif ? des rayures sur
la serrure sans réparation : ce n'est pas une effraction au sens du contrat, la porte était-elle fermée
à clé ? les bijoux disparus après le passage du plombier ; le gel sans savoir si l'on chauffait…),
les garanties manquantes, des pièges (traces de tournevis mais porte fermée à clé, rosiers volés, fioul
siphonné, clés volées, bain à bulles, infiltration par la toiture, coup de poing dans la vitre,
ordinateur professionnel), un courriel long et un message en style SMS, des sinistres multiples.
Golden **v5 : 97 cas, 13 « incertain »**, figé par empreinte.

Deux règles du banc corrigées en chemin : une réponse **tolérée par l'annotation** (« acceptables »)
n'est plus comptée comme couvert à tort ; un cas « incertain » sans question attendue n'est admis que
pour une garantie non traduite (la réponse est alors « à examiner par un gestionnaire »).

**Mesure, règles seules (oracle)** : 90 % justes, 70 % exactes, **4 couverts à tort, 3 refus à tort**
(v4 : 100 %, 0, 0). Les nouveaux cas trouvent des trous, et c'est leur rôle :

| Cas | Attendu | Obtenu | Cause |
|---|---|---|---|
| Joint de douche qui fuyait depuis des mois | non couvert | couvert | exclusions générales 1.4 (manque d'entretien) non traduites |
| Coup de poing dans la vitre | non couvert | couvert | 1.4 (sinistre intentionnel) non traduite |
| Tuyau apparent rouillé | non couvert | couvert | exclusion « corrosion visible » de 2.7 absente |
| Bain à bulles extérieur | non couvert | couvert | exclusion « piscines, bains à bulles » de 2.7 absente |
| Infiltration par la toiture | couvert | non couvert | la règle exclut toute infiltration extérieure, le contrat seulement terrasses, balcons, portes, fenêtres, murs |
| Clés volées dans le tram | couvert | non couvert | la limite « clés » de 2.10 n'est pas traduite |
| Portes taguées (2.11) | couvert | non couvert | « autre » est traité comme un événement traduit |
| Mérule (2.12) | incertain | non couvert | idem |
| Rosiers, fioul | non couvert | incertain | « plantations » et « mazout » manquent au vocabulaire (sans danger) |

Le plus grave est le dernier type d'erreur systémique : un événement « autre » donne « non couvert » au
lieu de « incertain, à examiner ». Deux réponses attendues restent discutables (toiture, clés) : la
fiche `A_VALIDER.md` les soumet à l'auteur.

### 7.31 Les sept trous corrigés

Chaque correction part d'une phrase du contrat (citations vérifiées contre le découpage des CG, 65 sur 65) :

- **« autre » n'était pas le problème** : il désigne aussi ce qu'aucune garantie ne couvre (la brûlure
  de bougie du recruteur, qui doit rester « non couvert »). Ce qui manquait, ce sont deux événements :
  `vandalisme` (2.11) et `merule` (2.12). Non traduits, ils plafonnent à « incertain, à examiner ».
- **Exclusions générales 1.4** : `intentionnel` et `manque_entretien` (usure, détérioration lente),
  sur toutes les garanties traduites. Elles sont « à prouver par l'assureur » : inconnues, elles ne
  deviennent pas une question posée à chaque déclaration (le test le vérifie).
- **2.7** : la valeur `infiltration_exterieure` ne vise plus que terrasses, balcons, portes, fenêtres et
  murs, comme le contrat ; `infiltration_toiture` reste couverte. Ajout de l'eau souterraine, des
  piscines et bains à bulles extérieurs, et de la corrosion visible (à prouver par l'assureur).
- **2.10** : une garantie cachée dans le tableau des limites, « le vol ou la perte des clés » (500 EUR) ;
  les exclusions « plantations du jardin » et « mazout de chauffage ».

**Une erreur évitée par le banc** : la première version de la garantie clés se rattachait aussi à la
« simple disparition ». Le rappel des questions est tombé de 100 % à 91 % : pour un début de feu, le
moteur ne demandait plus « y a-t-il eu embrasement ? » mais « quel bien ? », parce qu'un vol de clés
devenait possible. La perte n'est pas un événement du vocabulaire ; la garantie se limite au vol.

Les faits idéaux de 11 cas ont été précisés avec ces nouvelles valeurs (golden v6) ; les textes et les
réponses attendues n'ont pas changé. **Règles seules (oracle) : 100 % justes, 80 % exactes, 0 couvert et
0 refus à tort**, rappel des questions 100 %. La lecture doit maintenant reconnaître ces valeurs : le
vocabulaire lui fournit leurs définitions (« aide »), à mesurer au prochain banc complet.

### 7.32 Le banc complet sur le golden v6 : la lecture recule

**Mesure sur le poste** (Mistral Small, 3 exécutions) : règles seules 100 % ; **chaîne 75 % justes,
9,3 couverts à tort, 14 cas instables** ; la lecture change 31 décisions par exécution, dont 14 vers un
couvert à tort. Une partie vient des 29 cas nouveaux, faits pour être difficiles (72 % justes). Mais
**sur les 68 cas d'hier, la chaîne passe de 85 % à 76 %**, et des couverts à tort apparaissent sur des cas
qui passaient (le gel sans chauffage, la bougie, la fenêtre laissée ouverte). Les règles sont justes sur
les faits idéaux : c'est donc la lecture qui a reculé. Explication la plus probable : le vocabulaire
envoyé au modèle s'est allongé (intention, entretien, corrosion, clés, toiture…), et Mistral Small omet
davantage de faits (le lieu manque 19 fois, l'absence 9 fois). Un cas montre une confusion directe :
« la clé laissée sous le paillasson » lu comme « clés volées » ; le sens de cette valeur est précisé.

**Ce qui change la décision** : le banc d'hier soir avec **Mistral Large** pour lire les faits (golden
v4) donnait **96 % sur ces 68 cas, sans aucun couvert à tort** (85 % avec Small). La lecture par Large est
la mesure à refaire sur le golden v6 avant toute autre retouche.

### 7.33 L'arbre de preuve

Prolog n'apportait jusque-là que la décision et les questions qui tranchent. Il rend maintenant **la
trace de sa déduction** : pour chaque garantie retenue, chaque condition évaluée, avec sa phrase du
contrat et son état (oui, non, inconnu), jusqu'aux faits déclarés. Pour le vélo dans la cave fermée au
cadenas : « [non] Condition non remplie — art. 2.10 : « si ces locaux sont fermés avec une serrure de
sûreté » → serrure_de_surete (art. 12) → [oui] fermeture = cadenas (déclaré : cadenas) ». Ce n'est pas une
explication rédigée après coup par un modèle : chaque nœud est recalculé par le même `eval/2` que la
décision. L'affichage élague ce qui n'a pas compté (la branche vraie d'un « ou », les branches fausses
d'un « et », les exclusions qui ne jouent pas, comptées). L'arbre est dans la réponse (`analyser`, page
web, `regles --faits`), et l'oracle Python le reconstruit : le test différentiel compare les deux arbres
sur tous les cas.

### 7.34 Le second banc : LegalBench

Le golden set est écrit par Claude, pour un contrat. LegalBench (`insurance_policy_interpretation`,
Stanford, CC BY 4.0, 138 cas) apporte des clauses et des réponses que nous n'avons pas écrites, avec une
troisième réponse, « ambigu », quand les lecteurs ne s'accordent pas : une mesure externe du « je ne sais
pas ». Chaque cas ayant sa propre clause, sans règles ni vocabulaire, le banc mesure le principe du
projet **sans le moteur** : le modèle répond et cite mot pour mot la phrase de la clause ; le code vérifie
la citation ; une réponse ferme sans citation retrouvée devient « incertain ». On compare la réponse brute
et la réponse contrôlée (exactitude, exactitude équilibrée, rappel des ambigus, couverts à tort).
Les données se téléchargent sur le poste. Mesure à faire. Suite possible : faire rédiger des règles pour
chaque clause, pour tester aussi la rédaction et le moteur.

### 7.35 Le plan : une lecture fiable et rapide

Les règles sont justes ; toutes les erreurs viennent de la lecture des faits. Plan arrêté le 18 nov.,
une étape à la fois, chacune gardée seulement si le banc dit qu'elle améliore la justesse **et** le temps :

0. **Mesures de référence** : banc complet avec Small (fait : 75 %) et avec Large, sur le golden v6 ; temps par cas.
1. **Sortie contrainte par un schéma JSON** (valeurs du vocabulaire en listes fermées) et **lecture en deux
   temps** (événement, bien, lieu ; puis les seules questions de cet événement).
2. **Double lecture en parallèle**, comparée par le code, et **cascade** : Mistral Large ne relit que si les
   deux lectures divergent ou si la réponse est « couvert ».
3. **Prolog en processus permanent** (moteur et contrat chargés une fois).
4. **Le temps dans le banc** : médiane et p95 par étape, part des cas envoyés à Large, avec une porte.

### 7.36 La simplification : une seule méthode, et sa référence

Le projet portait encore quatre méthodes : la grille de conditions (le modèle remplit une grille à chaque
sinistre, avec relecture et recherche hybride), les fiches (le contrat compilé en questions, avec juge de
qualité et agent de réparation), les règles Prolog, et le document brut. Les mesures ont tranché
(7.17 à 7.31) : les règles sont justes sur 100 % du golden set quand les faits sont bien lus ; les fiches
plafonnaient à 74 %. Garder les anciennes méthodes coûtait en lecture du code, en tests et en consignes.

**Retiré** (environ 2 750 lignes, plus d'un tiers du code : de 7 400 à 4 700) : `conditions.py`, `relecture.py`, `recherche.py`
(embeddings, fusion RRF), `fiches.py`, `compilation.py`, `reparation.py`, `qualite.py`, `faits.py`, la
dérive et le bilan (`derive.py`, `bilan.py`) ; les commandes `compiler`, `fiches`, `evaluer`, `comparer`,
`reparer`, `propositions`, `derive`, `bilan` ; le mode hors ligne ; 10 consignes sur 14 (archivées dans
`docs/consignes/`, rien n'est réécrit) ; 66 tests. Le code reste dans l'historique git (tag
`avant-simplification`).

**Gardé** : la méthode `regles` (le système) et la méthode `brut` (le contrat dans le prompt : la
référence à battre, `couverture banc --methode brut`). Deux utilitaires de la compilation servent à la
rédaction des règles : ils sont passés dans `llm.py`. Le banc enregistre maintenant chaque passage dans
MLflow (il remplace `evaluer`), et les tableaux Grafana ne montrent plus que ce qui existe.

**Ce que les méthodes retirées ont appris** et qui reste dans le système : la décision calculée par le code
et non devinée par le modèle (grille), le rôle de chaque phrase du contrat (fiches : périmètre, conditions,
obligations, exclusions, limites), la charge de la preuve, le contrôle des citations, et le fait que le
modèle relise ne suffit pas quand il lit mal.

### 7.37 Mistral Large sur le golden v6, et LegalBench

**Lecture par Mistral Large** (golden v6, 3 exécutions) : **chaîne 91 % justes, aucun couvert à tort**,
0,3 refus à tort, 9 cas instables (Small : 75 %, 9,3 couverts à tort). 95 % sur les 68 cas d'origine,
80 % sur les 29 nouveaux. La lecture ne change plus que 13,7 décisions par exécution, **aucune vers un
couvert à tort**. Mais le prix est le temps : **15 minutes par passage**, contre 20 secondes avec Small.
Ce qui reste : des questions qui manquent (rappel 61 %) et des cas difficiles par construction (le vélo
volé avec violence, le local de l'immeuble, les traces de tournevis). Le plan de 7.35 en sort confirmé :
garder Small pour la vitesse, et n'appeler Large que sur les cas qui le demandent.

**LegalBench, Mistral Small, 133 cas** : 55 % justes (exactitude équilibrée 64 %), **32 couverts à tort**,
et surtout **10 % des cas ambigus reconnus** : sur 59 clauses que les lecteurs jugent ambiguës, le modèle
en tranche 53 (29 « couvert », 24 « non couvert »). Quand il répond « incertain », il a toujours raison
(précision 100 %), mais il le dit trop rarement. **Le contrôle des citations n'a rien changé** : les 127
citations étaient exactes. C'est la leçon du banc : vérifier qu'une phrase existe arrête une preuve
inventée, pas une interprétation trop sûre d'elle. Sur une vraie phrase (« any work that requires heat »),
le modèle tire une conclusion que la moitié des lecteurs ne tirent pas. C'est exactement ce que les règles
évitent : elles ne laissent au modèle que la lecture des faits, et la décision suit des conditions écrites.
Suites possibles : mesurer Mistral Large sur LegalBench, et faire rédiger des règles pour quelques clauses.

### 7.38 Étape 1 du plan : lecture en deux temps, sortie contrainte

**Lecture en deux temps** (`prolog.extraire_faits_regles`) : le temps 1 ne demande que l'événement, le bien
et le lieu ; le temps 2 ne demande que les variables qui concernent l'événement lu (« pour » dans le
vocabulaire) et celles qui valent pour tout (absence, auteur, intention…), en rappelant ce qui est déjà
établi. Pour un vol, la consigne du temps 2 ne parle plus de cause d'eau, de flammes ni de gel. La consigne
v4 a été coupée en deux (`lecture-socle` v1, `lecture-details` v1) ; un test vérifie que chacune de ses
règles se retrouve dans l'un des deux temps (la leçon de la v3, 7.24 bis). L'ancienne lecture reste
disponible pour comparer : `COUVERTURE_LECTURE=un_temps`. Le banc note le mode dans son rapport.

**Sortie contrainte par un schéma JSON** : chaque appel envoie un schéma où chaque variable n'admet que
les valeurs du vocabulaire, ou `null` (inconnu). Si le serveur refuse le schéma (erreur 400 ou 422), le
client revient au simple mode JSON et ne redemande plus le schéma.

**Mesure** (Small, golden v6, 3 exécutions ; schéma accepté par Mistral, aucune erreur du fournisseur) :

| Lecture | Justes | Couverts à tort | Refus à tort | Instables | Rappel des faits | Durée moyenne d'un passage |
|---|---|---|---|---|---|---|
| Un temps (v4) | 75 % | 9,3 | 5 | 14 | 78 % | 42 s |
| **Deux temps + schéma** | **84 %** | **2,7** | **3,7** | **8** | **90 %** | 96 s |

Le lieu, qui manquait 19 fois, ne manque plus. Les couverts à tort sont divisés par trois et demi. Le prix :
deux appels l'un après l'autre, donc un passage deux fois plus long, ce que la règle du plan refusait.
**Décision : on garde**, parce que le gain porte sur l'erreur la plus coûteuse, et que l'étape 3 (Prolog
chargé une fois) et la mesure de la latence par cas (étape 4) doivent venir avant d'ajouter des appels
(double lecture, étape 2). Restent : « la clé sous le paillasson » encore lue comme des clés volées (donc
couvert à tort), et le rappel des questions attendues tombé à 36 %, à comprendre.

### 7.39 Pourquoi les questions ne sont plus posées : le schéma pousse à remplir

En deux temps, les questions attendues n'étaient plus posées que dans 36 % des cas (52 % avant). Cas par
cas, la cause est la même : **le modèle remplit au lieu de laisser vide**. « On m'a volé mon vélo dans ma
cave » est lu avec `fermeture = aucune`, `auteur = tiers`, `simple_disparition = non` ; le début de feu avec
`embrasement = non` ; le gel avec `prevention_gel = non`. La décision devient ferme (souvent « non
couvert ») là où il fallait demander. Le schéma strict exige que chaque variable soit présente ; `null` était
permis, mais en fin de liste, et le modèle choisissait plutôt une vraie valeur.

**Correction** (`lecture-socle` v2, `lecture-details` v2) : chaque variable propose d'abord la valeur
« inconnu », retirée par le code avant toute décision ; la consigne dit que c'est la réponse normale, et qu'on
ne choisit pas « non », « aucune » ou « tiers » par défaut. Au passage, la règle des clés passe dans la
consigne du temps 1 (le vocabulaire seul n'avait pas suffi) : la clé dont le voleur s'est servi n'est pas
un bien volé. À mesurer.

### 7.40 Lecture v2 mesurée : la vraie cause est l'obligation de répondre

**Mesure** (Small, deux temps, consignes v2, 3 exécutions) : **86 % justes** (84 % en v1), 3 couverts à tort
(2,7), **2 refus à tort** (3,7), 8 instables, faits retrouvés 91 %, 1 à 2 minutes par passage. Mais les
**questions attendues restent posées dans 36 % des cas** : la correction de 7.39 n'a pas marché.

Cas par cas, le modèle remplit toujours : `simple_disparition = non` (39 fois), `fermeture = aucune` (29),
`auteur = tiers` (28), `intentionnel = non` (22)… alors que « inconnu » était proposé en premier et que la
consigne disait de ne pas choisir ces valeurs par défaut. La comparaison avec la lecture d'un seul coup
désigne la cause : sans schéma, « on m'a volé mon vélo dans ma cave » donnait bien la question sur la
fermeture (rappel 100 % sur ce cas), avec le schéma jamais. **Ce n'est pas la consigne, c'est la forme : un
schéma qui exige chaque variable oblige le modèle à écrire quelque chose pour chacune**, et il écrit une
valeur plausible plutôt que « inconnu ».

**Correction, un seul changement** : le schéma garde les listes fermées de valeurs, mais plus aucune
variable n'est obligatoire (forme non stricte). Les consignes ne changent pas (v2), pour mesurer l'effet
du schéma seul. On ne réessaie pas le garde-fou des appuis (7.26) : deux essais, deux bilans négatifs.

**La clé sous le paillasson** (g2-i02, g-p03) est toujours lue comme des clés volées malgré la règle : à
reprendre si la correction du schéma ne suffit pas (par exemple, ne pas demander `bien = cles` au temps 1
quand un autre bien est volé).

**Mesure : sans effet.** 85 % justes, 3,3 couverts à tort, 2,7 refus à tort, questions 39 % : dans le bruit
de la v2. Le schéma n'était donc pas la cause. Le compte des faits inventés, banc par banc, la donne :

| Lecture | Faits inventés (3 exécutions) | `g-q01` « volé dans ma cave » |
|---|---|---|
| Un temps, consigne v4 | 47 | rien d'inventé |
| Deux temps v1 (schéma strict, null) | 217 | fermeture = aucune, auteur = tiers… |
| Deux temps v2 (« inconnu » d'abord) | 268 | idem |
| Deux temps v2, schéma facultatif | 261 | idem |

**C'est le temps 2 lui-même** : on y présente au modèle une liste de questions ciblées (« tu réponds à
quelques questions précises »), et il y répond, question par question, même sans rien dans la déclaration.
Quand il traduisait la déclaration d'un seul coup, avec tout le vocabulaire, il ne gardait que ce qu'il
trouvait. Le schéma, strict ou non, n'y change rien.

### 7.41 Les deux lectures en parallèle : le socle court, le reste comme avant

Ce que chaque lecture fait bien : la lecture courte (événement, bien, lieu) ne perd plus le lieu ; la
lecture d'un seul coup (v4) n'invente presque rien. **On garde les deux, lancées en même temps** :
le socle vient de la lecture courte, le reste de la lecture complète (et si la lecture courte n'a pas trouvé
une variable du socle, la complète la donne). Comme les deux appels partent ensemble, la réponse attend la
plus lente, pas la somme : on revient vers le temps de la lecture d'un seul coup. Aucune consigne nouvelle :
`lecture-socle` v2 et la v4. Les deux autres modes restent disponibles pour comparer
(`COUVERTURE_LECTURE=deux_temps` ou `un_temps`). À mesurer.

### 7.42 Les deux lectures en parallèle : écartées

**Mesure** (Small, 3 exécutions) : 80 % justes, **11,7 couverts à tort**, 1,7 refus à tort, 13 instables ;
questions attendues 48 % (39 %), faits retrouvés 80 % (90 %) ; le temps d'un passage n'a pas baissé
(le banc sature déjà les appels simultanés). Les couverts à tort reviennent au niveau de la lecture d'un
seul coup (9,3).

**Pourquoi** : la lecture complète invente peu, mais elle **oublie les faits qui décident** : l'absence
(13 fois), l'effraction (9), les flammes et l'embrasement, la cause de l'eau, le gel sans chauffage,
l'intention. Or un fait qui fait refuser (une exclusion, une obligation non respectée) et qui manque,
c'est un « couvert » de trop. Les questions ciblées du temps 2 trouvent ces faits ; elles en inventent
aussi, mais ces inventions font surtout répondre « non couvert » ou « incertain » au lieu de poser une
question, rarement « couvert ».

| Lecture (Small) | Justes | Couverts à tort | Refus à tort | Questions posées | Faits inventés |
|---|---|---|---|---|---|
| Un temps (v4) | 75 % | 9,3 | 5 | 52 % | 47 |
| **Deux temps v2** | **86 %** | **3** | **2** | 36 % | 268 |
| En parallèle | 80 % | 11,7 | 1,7 | 48 % | — |

**Décision** : on revient à la lecture en deux temps (v2), qui reste la meilleure mesurée, par défaut ; le
mode en parallèle reste disponible (`COUVERTURE_LECTURE=en_parallele`) mais écarté. **Les faits inventés
du temps 2 relèvent de l'étape 2 du plan** : deux lectures indépendantes comparées par le code. Un fait
vrai est lu les deux fois ; une invention l'est rarement deux fois de la même façon. Un fait lu une seule
fois devient inconnu, et la question est posée.

### 7.43 Étape 2 revue : vérifier les faits plutôt que lire deux fois

Le plan prévoyait deux lectures indépendantes comparées par le code. **En regardant les bancs, l'idée ne
tient pas telle quelle** : les inventions du temps 2 sont **systématiques**. « On m'a volé mon vélo dans
ma cave » donne `fermeture = aucune` aux trois exécutions, avec la même décision chaque fois ; le modèle
répond à température 0, et deux lectures identiques inventeraient la même chose. Une seconde lecture plus
« aléatoire » (température plus haute, autre formulation) couperait surtout les faits instables, pas ceux-là.

**Ce qui est essayé à la place** (`COUVERTURE_LECTURE=verifiee`) : après les deux temps, **chaque fait du
temps 2 est soumis au modèle comme une affirmation** (« Comment le local était-il fermé ? → aucune »), et il
répond « dit » ou « non dit » au vu de la déclaration. Un fait « non dit » redevient inconnu : le moteur
pose la question. Juger une affirmation est une autre tâche que remplir une liste : le modèle n'a plus à
produire une valeur, seulement à dire si elle est écrite. Les faits du socle (événement, bien, lieu) ne sont
jamais soumis : les retirer rendait tout incertain (7.26). Une vérification illisible ne retire rien.
Consigne `verification-faits` v1. Un appel de plus, après les deux autres.

**À mesurer**, contre les deux temps (86 %, 3 couverts à tort, 2 refus à tort, questions 36 %) : les
questions posées doivent monter sans que les couverts à tort remontent (un fait vrai qui ferait refuser,
jugé « non dit » à tort, donnerait un couvert de trop). Le temps aussi : trois appels à la suite.

### 7.44 La lecture vérifiée mesurée, et le moteur comme arbitre

**Mesure** (Small, 3 exécutions) :

| Lecture | Justes | Couverts à tort | Refus à tort | Questions posées | Durée d'un passage |
|---|---|---|---|---|---|
| Deux temps v2 | 86 % | 3 | 2 | 36 % | 1 à 2 min |
| **Vérifiée** | 86 % | **6,7** | 1,7 | **73 %** | 2 à 3 min |

**Les questions attendues doublent** (36 % → 73 %) : la vérification retire bien les inventions
(`fermeture = aucune` 27 fois, `effraction = non` 18, `intentionnel = non` 18, `travaux = aucun` 13…).
**Mais le risque annoncé s'est produit** : elle retire aussi des faits **vrais qui faisaient refuser**, et
les couverts à tort doublent. « La fenêtre de ma chambre, que j'avais laissée grande ouverte » :
`fenetres_fermees = non` jugé « non dit » ; « je suis parti deux semaines en coupant le chauffage » :
`prevention_gel = non` jugé « non dit ». Sans eux, le moteur couvre.

**Correction : le moteur arbitre.** Un doute ne doit jamais faire couvrir. Après la vérification, Prolog
décide deux fois, avec les faits vérifiés et avec les faits lus. Si retirer les faits « non dits » fait
passer la décision à « couvert », la vérification est écartée pour ce cas et la lecture non vérifiée est
gardée (avec un avertissement). Dans tous les autres cas, la vérification s'applique : elle ne peut plus
que rendre une réponse plus prudente (une question au lieu d'un refus). C'est une asymétrie voulue, la
même que dans tout le projet : promettre à tort coûte plus que demander. Deux décisions de plus par
cas, sans appel au modèle. À mesurer : les questions doivent rester hautes et les couverts à tort revenir
au niveau des deux temps.

### 7.45 La lecture vérifiée et arbitrée : la meilleure, et désormais celle par défaut

**Mesure** (Small, 3 exécutions) :

| Lecture (Mistral Small) | Justes | Couverts à tort | Refus à tort | Questions posées | Instables | Durée d'un passage |
|---|---|---|---|---|---|---|
| Un temps (v4, ce matin) | 75 % | 9,3 | 5 | 52 % | 14 | 20 à 40 s |
| Deux temps v2 | 86 % | 3 | 2 | 36 % | 8 | 1 à 2 min |
| Vérifiée, sans arbitre | 86 % | 6,7 | 1,7 | 73 % | 8 | 2 à 3 min |
| **Vérifiée, arbitrée par le moteur** | **87 %** | **2,7** | **2** | **55 %** | 10 | 2 à 3 min |

L'arbitre a fait ce qu'on attendait : les couverts à tort reviennent à **2,7, le plus bas mesuré avec Small**,
et les questions posées restent bien au-dessus des deux temps (55 % contre 36 %). Une partie du gain de la
vérification est rendue (73 % → 55 %) : ce sont les cas où le moteur a jugé qu'enlever un fait aurait fait
couvrir. **Décision : la lecture vérifiée devient la lecture par défaut.** Le prix est le temps : trois
appels à la suite, et deux décisions de plus par cas (chacune lance aujourd'hui un SWI-Prolog). L'étape 3
du plan (Prolog chargé une fois) devient la suivante.

**Le chemin de la journée, en une ligne** : 75 % et 9,3 couverts à tort le matin (lecture d'un seul coup),
87 % et 2,7 le soir, sans changer de modèle : en découpant la lecture, en faisant vérifier les faits plutôt
que les relire, et en laissant le moteur décider quand un doute peut compter.

### 7.46 Étapes 3 et 4 : le moteur chargé une fois, et le temps dans le banc

**Le moteur chargé une fois** (`prolog.MoteurPermanent`). Chaque décision lançait un SWI-Prolog, qui
chargeait le moteur, les règles et le vocabulaire ; la lecture vérifiée décide jusqu'à trois fois par cas.
Désormais, un processus par contrat reste ouvert : Python lui envoie les faits sur une ligne
(`faits([evenement-vol, bien-velo]).`), il répond une ligne JSON (`servir` dans `moteur.pl`). Un verrou
fait passer les décisions une à une ; un processus arrêté, ou des règles modifiées sur le disque, le font
relancer ; une erreur donne une nouvelle tentative avec un processus neuf. Les avertissements au
chargement restent des erreurs, comme avant. `COUVERTURE_PROLOG_PERMANENT=non` revient à un processus par
décision. Deux tests : le protocole, avec un faux SWI-Prolog (sans Prolog installé) ; et, sur le poste,
**le moteur permanent rend exactement ce que rend un processus par décision, sur tous les cas**.

**Le temps dans le banc.** Chaque cas est chronométré, et la lecture est séparée de la décision. Le banc
donne la médiane et le 95e centile du temps par cas, et le temps médian de la lecture et de la décision.
Une porte : 95e centile au plus 30 s, à resserrer une fois mesuré. Attention : dans le banc, quatre cas
tournent à la fois et se partagent les appels au modèle ; un cas seul, comme dans l'interface, va plus vite.

À mesurer : le temps de la décision doit devenir négligeable, et le temps par cas baisser d'autant.

### 7.47 Mesure : la décision ne coûte plus rien, la lecture et le débit restent

**Tests** : 113 réussis, 1 sauté (le protocole avec un faux SWI-Prolog, prévu pour Linux) ; **le test qui
compare le moteur permanent à un processus par décision, sur tous les cas, passe sous Windows**. La suite
de tests passe de 30 à 10 secondes : c'était surtout le démarrage de SWI-Prolog.

**Banc** (lecture vérifiée, 3 exécutions) : 87 % justes, 2,7 couverts à tort, 2,3 refus à tort, **5 instables**
(le moins mesuré), questions posées 55 %. Les décisions n'ont pas bougé, comme attendu.

| Temps par cas (banc, quatre cas à la fois) | Médiane | 95e centile |
|---|---|---|
| Total | **2,4 s** | 68 s |
| Lecture (trois appels au modèle) | 2,4 s | — |
| Décision (Prolog, jusqu'à trois par cas) | **moins de 10 ms** | — |

**La décision est devenue négligeable.** Un cas typique prend 2,4 s, presque tout dans la lecture. Mais
le passage complet n'a pas raccourci (2 min 20 à 3 min 20) : **la queue est très longue** (5 % des cas
au-delà de 68 s). Ce n'est pas le système, c'est le débit : quatre cas à la fois, trois appels chacun,
et Mistral répond « trop de requêtes » (429) ; le client attend alors 2, 4, 8… jusqu'à 60 s avant de
réessayer. Un cas seul, comme dans l'interface, ne rencontre pas cette limite. La porte de latence échoue
(68 s pour 30) : elle mesure aujourd'hui le débit autorisé par la clé, pas le système. À trancher : la
garder telle quelle (elle dit vrai sur un traitement en masse), ou mesurer la latence avec un cas à la fois.

### 7.48 La latence mesurée comme la vit un gestionnaire

Décision de l'auteur : la porte de latence doit mesurer **ce que vit un gestionnaire qui pose une
question**, pas le débit d'un traitement en masse. Après la couche « chaîne », le banc analyse **dix cas
l'un après l'autre** (toujours les mêmes, répartis sur le golden set) et en tire la médiane et le 95e
centile du temps par cas, lecture et décision à part. La porte porte sur ce 95e centile : **10 s au
départ**, à resserrer une fois mesuré. Le temps « en masse » (quatre cas à la fois) reste affiché, sans
porte. Coût : une trentaine de secondes de plus par banc.

### 7.49 « Je ne sais pas » plutôt qu'une réponse fausse : confirmer les faits qui portent la décision

Demande de l'auteur : **le système doit dire « je ne sais pas » au lieu de donner une réponse fausse.** Les
2,7 couverts à tort et 2,3 refus à tort qui restent viennent tous d'un fait mal lu qui porte la décision :
« la clé sous le paillasson » lue comme des clés volées, « mes bijoux ont disparu » lu comme un vol, etc.

**Le principe : une réponse ferme doit reposer sur des faits confirmés.** Quand le moteur répond « couvert »
ou « non couvert », il désigne lui-même **les faits qui portent la décision** : ceux dont le retrait la
change (`faits_decisifs`, quelques décisions de quelques millisecondes). Ces faits seuls, socle compris,
sont soumis au modèle comme des affirmations (« Quel bien a été touché ? → cles (les clés elles-mêmes,
volées ou perdues…) : la déclaration le dit-elle ? »). **Un seul « non dit », et la réponse devient
« incertain »**, avec la question sur ce fait en premier, et la justification « Je ne peux pas trancher :
la déclaration ne dit pas clairement… ». L'arbre de preuve affiché est celui sans le fait douteux, précédé
d'une ligne qui le dit.

Ce n'est pas la vérification de 7.43 répétée : celle-là retirait des faits inventés pour **poser plus de
questions** ; celle-ci ne touche à aucun fait, elle **suspend une réponse ferme** dont l'appui n'est pas sûr.
Elle s'applique aux deux réponses fermes, couvert comme non couvert. Coût : un appel de plus, seulement
quand la réponse est ferme. À mesurer : les couverts et refus à tort doivent baisser ; l'exactitude peut
baisser aussi (des réponses justes deviendront « incertain ») : c'est le prix accepté.

### 7.50 La confirmation mesurée : plus juste, moins d'erreurs, et la latence passe

**Mesure** (Small, lecture vérifiée + confirmation des faits décisifs, 3 exécutions) :

| | Justes | Couverts à tort | Refus à tort | Questions posées | Instables |
|---|---|---|---|---|---|
| Vérifiée, arbitrée (7.45) | 87 % | 2,7 | 2,3 | 55 % | 5 |
| **+ confirmation des faits décisifs** | **90 %** | **2,3** | **1,3** | **70 %** | 10 |

Contre ce qu'on craignait, **l'exactitude monte** (87 → 90 %) : les réponses suspendues étaient surtout
des réponses fausses, et les cas « incertain » attendus le deviennent plus souvent (questions posées
55 → 70 %). **Latence, un cas à la fois : médiane 2,9 s, 95e centile 4,7 s : la porte (≤ 10 s) passe.**

**Ce qui reste, et pourquoi la confirmation ne l'attrape pas** :
- « la clé que j'avais laissée sous le paillasson » (`g-p03`) est toujours lue « clés volées », et le
  modèle **confirme** ce fait : la clé est bien dans la déclaration. Une confirmation juge qu'un fait est
  écrit, pas qu'il est bien rangé ;
- les autres erreurs sont des **oublis** : l'hôte qui a volé (`val-03`, exclusion des vols par les hôtes),
  l'absence pendant les vacances (`bougie-04`). Confirmer les faits lus ne peut pas retrouver un fait
  qui n'a pas été lu.

Pistes : une règle de cohérence (une clé laissée à proximité n'est pas une clé volée), et, avant de
couvrir, demander au modèle si la déclaration évoque l'une des exclusions que le moteur présume absentes.

---

**Partie IV — D'autres contrats (18 au 20 novembre).** La méthode tient-elle sur un contrat qu'on n'a pas écrit à la main, et que vaut la mesure ?

### 7.51 Trois contrats de plus : Assureur B, Assureur C, Assureur D

Pour montrer que la méthode se généralise, trois conditions générales réelles sont téléchargées par
l'auteur (liens dans `data/contrats/SOURCES.md` ; le lien Assureur D sert désormais la version d'avril 2026,
ajoutée au catalogue). Première ingestion, sans rien changer :

| Contrat | Clauses | Statut | Alertes |
|---|---|---|---|
| Assureur D Multirisque Habitation (2026) | 207 | OK | — |
| Assureur C Habitation (2025) | 157 | À vérifier | aucune définition reconnue |
| **Assureur B Habitation (2017)** | 292 | À vérifier | 118 clauses sans type ; 25 renvois introuvables |

**Assureur B, le second contrat visé** (luxembourgeois, comme le recruteur). Deux causes, deux corrections
générales, plus un profil d'assureur :
- **Le profil ne reconnaissait pas les titres numérotés.** Assureur B titre ses sections « 3.1.6.1 Etendue de la
  garantie », « 3.1.6.2 Vols exclus » ; le profil comparait le titre avec son numéro. Il le compare
  désormais sans. Profil `data/profils/assureur-b.json` : « étendue de la garantie », « objet de la
  garantie » → garantie ; « montant des garanties », « estimation des dommages » → limite ; « délai de
  carence », « étendue territoriale » → condition.
- **Les renvois vers des sous-points énumérés dans le texte** (« 3.1.7.2.9 les pertes… » écrit dans la clause
  3.1.7.2) n'avaient pas de clause à eux. Un tel renvoi mène maintenant à la clause qui le contient (au plus
  deux niveaux au-dessus).

Résultat : **Assureur B passe à OK** (293 clauses : 34 garanties, 25 exclusions, 51 conditions, 18 limites, 71
définitions ; 94 « autre », surtout les dispositions administratives : résiliation, prime, prescription).
Pour la garantie vol, par exemple : 3.1.6.1 étendue (garantie), 3.1.6.2 vols exclus (exclusion), 3.1.6.3
limites d'indemnité (limite), 3.1.6.4 mesures de sécurité (condition). Assureur A est inchangé.

**Assureur C** reste à vérifier : sa mise en page (numéros de page pris pour des numéros d'article,
titres aux lettres espacées) demanderait un profil plus lourd ; contrat français, il passe après Assureur B.

### 7.52 Assureur B : des règles qui partent de zéro

Pour Assureur A, les premières garanties ont été écrites à la main pour servir de modèle. **Pour Assureur B, aucune
règle n'est écrite à la main** : c'est le vrai test de la généralisation. Le fichier
`regles/assureur-b-habitation-2017.pl` part vide (en-tête seulement) ; tant qu'il l'est, aucun événement n'est
traduit et le moteur répond « à examiner par un gestionnaire », jamais « non couvert ». Chaque garantie
passe ensuite par la même chaîne que la 2.9 d'Assureur A : Mistral Large rédige à partir des clauses de
l'article et des définitions du lexique Assureur B qu'elles emploient, le code contrôle (citations mot pour mot,
vocabulaire, concepts, chargement Prolog), l'auteur relit, puis accepte. Première garantie : **le vol
(3.1.6)**, découpé en étendue (3.1.6.1), vols exclus (3.1.6.2), limites d'indemnité (3.1.6.3) et mesures de
sécurité (3.1.6.4). À mesurer : ce que la rédaction réussit seule, ce qu'il faut ajouter au vocabulaire
commun, et le temps humain de relecture.

### 7.53 Première rédaction Assureur B (vol, 3.1.6) : un plantage, puis ce que les contrôles voient et ne voient pas

**Le plantage.** Mistral Large a rendu « non_traduit » comme une liste de phrases au lieu d'objets
{"article", "texte", "pourquoi"}. Le contrôle des listes d'exclusions appelait `.get` sur une chaîne et
plantait, après six minutes de rédaction (la proposition brute était heureusement déjà sauvée). Correction :
le schéma signale désormais cet écart (ce qui déclenche la reprise par le modèle), et les contrôles mettent
la phrase en forme sans article ; elle reste bloquante. Un test reproduit le cas.

**Ce que les contrôles signalent (16 bloquants).** Treize faits nouveaux à accepter ou remplacer ; une
citation rattachée à un article qui n'existe pas (3.1.6.2.4) ; une partie de la liste d'exclusions oubliée
(les remorques non enfermées) ; le passage déclaré non traduit (objets volés retrouvés, 3.1.6.5).

**Ce qu'ils ne voient pas, et que la relecture a trouvé.**
- Des faits inventés alors que le vocabulaire commun les a déjà : `agression` pour `violence`,
  `vol_avec_complicite` pour `auteur`, `vol_simple` pour « ni effraction ni violence ». Le contrôle repère un
  fait nouveau, pas un fait nouveau *redondant*. Le vocabulaire commun est justement ce qui rend les règles
  comparables d'un assureur à l'autre : l'accepter tel quel l'aurait fragmenté.
- Les exclusions ne sont attachées qu'à la garantie de base. Les extensions « Privilège » et « Active »
  couvriraient un vol sans aucune exclusion : le genre d'erreur qui fait couvrir à tort.
- Des exceptions aux exclusions perdues : le vol au jardin est exclu en entier, alors que le mobilier de
  jardin, l'outillage et les plantations sont réservés ; l'exclusion des parties communes oublie sa
  condition (« si l'Assuré n'occupe que partiellement le bâtiment »).
- Des conditions cachées dans les limites (sous clefs, agression), contrairement à la règle 4 de la consigne.
- « Perte ou vol des clés » réduit au vol ; « biens dont l'Assuré n'est pas propriétaire » réduit à `hote`.

**Leçon 69.** Les contrôles mécaniques attrapaient la forme (citations, schéma, faits inconnus, exclusions
omises), pas une traduction plausible mais fausse. Corriger la proposition à la main aurait réglé Assureur B 3.1.6,
et rien d'autre : il aurait fallu recommencer pour chaque contrat. On a donc corrigé les causes, dans la
chaîne de rédaction elle-même (consigne `redaction-regles` v3) :

| Défaut observé | Cause | Correction générale |
|---|---|---|
| Extensions sans exclusions | le format n'avait pas d'endroit pour « les exclusions de l'article » | champ `exclusions_communes`, écrit `exclusion([g1, g2, …], …)` ; **bloquant** si une garantie n'a aucune exclusion alors que l'article en a |
| `agression` à côté de `violence` | le modèle ne voyait que les noms et les valeurs du vocabulaire | le vocabulaire lui est donné avec la question de chaque variable ; une variable nouvelle doit dire `plus_proche` (la variable existante la plus proche et pourquoi elle ne suffit pas), **à relire** sinon |
| Réserves perdues (« à l'exception du mobilier de jardin ») | rien ne le demandait | règle 3 bis de la consigne ; **à relire** si le texte cité a une réserve que la condition ne reprend pas |
| Conditions glissées dans les limites | idem | règle 4 précisée ; **à relire** si une limite porte « si », « s'ils », « lorsque » |
| `non_traduit` en phrases | format non vérifié | écart de schéma (reprise demandée au modèle) |

Rejoués sur la proposition Assureur B déjà rédigée, sans relancer le modèle, ces contrôles signalent seuls les cinq
extensions sans exclusions (bloquant), les deux réserves perdues et les quatre plafonds conditionnels (à
relire), et les quatorze variables nouvelles sans justification. La relecture humaine reste, mais elle part
d'une liste, pas d'une lecture ligne à ligne. Ce qui n'est pas automatisé : juger qu'une justification
`plus_proche` est bonne. La mesure suivante : relancer la rédaction avec la consigne v3 et compter ce qui
reste.

### 7.54 Deuxième rédaction Assureur B (consigne v3) : le fond suit, la forme casse, le code répare

**Mesure.** 27 minutes : la première réponse avait un défaut de forme, la reprise (une seconde rédaction
complète) l'a répété. Les neuf circonstances étaient rendues comme des conditions nues (`{"f": …}`) au lieu
de `{"condition", "article", "texte"}`. Ce défaut bloquait tous les autres contrôles.

**Le fond a suivi la consigne v3.**
- Les onze exclusions sont mises en commun : elles valent pour les huit garanties, extensions comprises.
- « Vol simple » est un concept écrit avec des faits existants (ni effraction ni violence), pas une variable.
- Les réserves sont gardées : le vol au jardin exclut tout sauf le mobilier de jardin et les plantations ;
  l'exclusion des parties communes garde « si l'Assuré n'occupe que partiellement le bâtiment ».
- Chaque variable nouvelle nomme sa voisine (`plus_proche`). Le modèle a pourtant gardé `agression` à côté
  de `violence` et `complicite_assure` à côté de `auteur` : nommer la voisine ne suffit pas à s'en servir.

**Corrections générales (consigne v4).**
- Une condition nue est enveloppée par le code avec l'article et la citation de sa garantie, et marquée
  `a_preciser` : l'avertissement revient à chaque contrôle tant que le relecteur ne l'a pas précisée. Cette
  remise en forme se fait aussi avant de décider d'une reprise : ce que le code sait réparer ne vaut pas dix
  minutes de modèle de plus. L'exemple de la consigne montre désormais une circonstance complète.
- Deux faux positifs du contrôle, présents dans les deux rédactions : une liste d'exclusions numérotée
  (« 3.1.6.2.4 les vols… ») n'était pas découpée par numéro, et un tiret d'incise (« automoteurs – à
  l'exception des engins de jardinage – ») était pris pour une puce. Et une citation présente mot pour mot
  dans trois articles (3.1.6.2, 3.1.7.2, 3.3.1.3) n'était rattachée à aucun ; on préfère maintenant la clause
  parente du sous-point cité.

**Résultat, sans relancer le modèle.** Sur la rédaction v3, il reste 20 points bloquants, tous de vraies
décisions humaines : 18 faits nouveaux à accepter ou à remplacer, et deux passages déclarés non traduits
(les plafonds par formule, la procédure des objets retrouvés). Plus aucun défaut de forme ni d'omission.
La relecture porte maintenant sur le vocabulaire, c'est-à-dire sur ce qu'aucun contrôle ne peut trancher.

### 7.55 La relecture humaine d'Assureur B 3.1.6 : ce qu'elle a changé, et combien de temps

La relecture a porté sur le JSON de la proposition, pas sur le PDF. Chaque modification est tracée dans
`meta.relecture` du fichier (`regles/propositions/assureur-b-habitation-2017/3.1.6.json`). Environ vingt minutes
à deux, pour une garantie de huit sous-garanties et onze exclusions.

**Vocabulaire : 18 faits proposés, 11 gardés.**
- Remplacés par l'existant : `agression` → `violence` ; `complicite_assure` → `auteur` ;
  `dispositifs_securite_conformes` → `serrure_surete` ; `vol_associe` → deux valeurs de `evenement` (vol et
  vandalisme, la variable en admet plusieurs) ; `remorque_non_fermee` → une valeur `remorque` de `bien`.
- Retirés : `aggravation_non_utilisation` (le lien causal de l'obligation le dit déjà),
  `acces_direct_partie_occupee` (c'est une limite de l'intervention : quelles portes), `sous_clefs` (un
  plafond, qui ne décide pas de la couverture).
- Gardés : plainte déposée, formule souscrite, occupation partielle, serrure à cylindre, séjour temporaire,
  occupation irrégulière, travaux, lien causal des travaux, abus de confiance, biens confiés au concierge.

**Deux conflits qu'aucun contrôle n'a vus.**
- *Le vol à la tire excluait le vol par agression.* Écrit « vol sur la personne, sur la voie publique », il
  frappait aussi l'extension agression, puisque les exclusions sont désormais communes. Ajouté : « sans
  violence ». C'est le revers de la mise en commun de 7.53 : une exclusion commune doit être compatible avec
  chaque extension.
- *Le vol simple vide l'extension « mobilier de jardin ».* Un vol au jardin se fait rarement par effraction.
  Laissé tel que le contrat l'écrit, et posé comme **question au métier** dans `meta.relecture` : c'est une
  lecture du contrat, pas une erreur de traduction.

**Autres corrections.** Le « bâtiment désigné » couvre cave, grenier et garage, pas le seul logement ; le
personnel de maison est exclu sauf effraction ou violence (les heures de service ne sont pas un fait du
vocabulaire : résidu connu) ; les plafonds de 3.1.6.3 sont cités en limites ; la procédure des objets
retrouvés (3.1.6.5) est classée **hors décision**, nouveau champ : cité et vérifié mot pour mot, mais non
bloquant.

**Leçon 70.** Un contrôle mécanique de plus en découle : pour chaque extension, vérifier qu'aucune
exclusion commune ne la rend impossible (une exclusion dont la condition est impliquée par le périmètre
de la garantie). C'est vérifiable par le moteur lui-même, en lui donnant le périmètre comme faits.

### 7.56 Le vocabulaire accepté, et un effet de bord évité

`--accepter-vocabulaire` a ajouté dix variables et une valeur (`bien = remorque`), puis `--controler`, avec
SWI-Prolog sur le poste, n'a plus rien trouvé de bloquant : les règles fusionnées se chargent sans
avertissement. Il n'y a pas encore de cas annotés Assureur B : la non-régression est vide, et c'est la prochaine
étape.

**L'effet de bord.** Les variables acceptées n'avaient pas de champ « pour ». Or la lecture ne filtre que les
variables qui le déclarent : une variable sans « pour » est lue pour tous les sinistres. La formule
« Privilège » ou la plainte déposée auraient été demandées pour un dégât des eaux chez Assureur A, et le banc
Assureur A aurait bougé pour une raison sans rapport. Correction générale : une variable acceptée vaut pour les
événements de la garantie qui l'a fait naître (ici vol et vandalisme). Les dix variables déjà ajoutées ont
été complétées, et cinq questions réécrites pour être posables à un assuré (« Serrure à cylindre ? » devient
« Les annexes ou dépendances étaient-elles fermées par une serrure à cylindre ? » ; le séjour temporaire n'est
pas « à l'étranger » : le contrat dit « partout dans le monde »).

**Leçon 71.** Ajouter des règles pour un assureur ne doit pas changer les réponses d'un autre. Le banc Assureur A
est le test de cette étanchéité : à relancer après chaque vocabulaire accepté.

### 7.57 Assureur B accepté ; le banc Assureur A bouge à peine, et on ferme quand même la porte

**Acceptation.** Les règles de l'art. 3.1.6 sont ajoutées à `regles/assureur-b-habitation-2017.pl` ; 125 tests
passent sur le poste.

**Banc Assureur A après l'ajout d'Assureur B** (même golden v6, Mistral Small, lecture vérifiée) :

| | Avant Assureur B (7.50) | Après Assureur B |
|---|---|---|
| Règles seules | 100 % | 100 % |
| Chaîne : justes | 90 % | 89 % |
| Couverts à tort | 2,33 | 3 |
| Refus à tort | 1,33 | 0,67 |
| Instables | 10 | 9 |
| Un cas à la fois, médiane / 95e centile | 2,9 s / 4,7 s | 2,9 s / 20,3 s |

Les règles Assureur A n'ont pas changé (règles seules : 100 %). L'écart de la chaîne est de l'ordre de la
variation entre deux exécutions de Mistral Small (deux cas-exécutions sur 291 pour les couverts à tort). Le
95e centile sur dix cas est une seule question lente : la médiane n'a pas bougé.

**Mais la cause possible était réelle.** Le vocabulaire est commun ; la lecture d'un vol chez Assureur A recevait
donc les dix variables d'Assureur B (plainte, formule « Privilège »…), qu'aucune règle Assureur A n'emploie : un prompt
plus long, et des faits à inventer en plus. Correction : chaque contrat ne lit que les variables que ses
règles emploient (`f(variable, …)` relevées dans son fichier, plus le socle événement / bien / lieu). Assureur A
lit 29 variables sur 39, Assureur B 19. C'est aussi ce qui rend le vocabulaire commun extensible sans limite : il
peut grossir avec chaque assureur sans alourdir la lecture des autres.

**Mesure après la correction** (chaque contrat ne lit que ses variables ; moteur encore sans la règle 7.58) :
89 % justes, couverts à tort 2,33 (le niveau d'avant Assureur B), refus à tort 1, instables 13 ; un cas à la fois,
médiane 3,2 s et 95e centile 4,5 s : la porte de latence passe de nouveau, le 20 s était bien une question lente
isolée. Rien de mesurable n'a donc été cassé par Assureur B ; la lecture reste la limite (20 décisions changées par
exécution, 13 cas instables), pas les règles.

**Leçon 72.** Un vocabulaire commun pour comparer, une lecture propre à chaque contrat pour décider.

### 7.58 Les cas de test Assureur B trouvent ce que la relecture n'a pas vu

**Quinze cas de vol Assureur B**, écrits d'après le texte du contrat (`data/golden/annotations/assureur-b-habitation-2017.jsonl`,
faits idéaux dans `regles/cas/golden/`) : cambriolage, vol simple, plainte absente ou inconnue, agression avec
et sans formule, vol à la tire, mobilier de jardin, cave à cadenas en immeuble, annexe à serrure à cylindre,
voiture, femme de ménage, clés, hôtel à l'étranger, travaux. Limite assumée : je les ai écrits après avoir relu
les règles ; ils ne sont pas indépendants, et restent « à valider par l'auteur » comme ceux d'Assureur A.

**Premier passage, règles seules : 11 sur 15.** Deux erreurs de traduction, qu'aucun contrôle ni la relecture
n'avaient vues :
- *« À l'extérieur » (3.1.6.2.6)* avait été traduit avec la voie publique et « un autre bâtiment ». L'exclusion
  tuait le vol par agression dans la rue (v05, v07) et le vol à l'hôtel (v14), que le contrat couvre
  expressément. Dans une liste d'exclusions d'un contrat habitation, « l'extérieur », ce sont les cours,
  jardins et couloirs à l'adresse du risque. Corrigé dans la proposition (seconde passe tracée dans
  `meta.relecture`), et règle 3 quater ajoutée à la consigne (v5).
- *Travaux en cours, lien causal inconnu (v15)* : le moteur répondait « couvert sous réserve ». Une exclusion
  inconnue était toujours une réserve, même quand la déclaration en établit une partie. **Règle générale
  ajoutée au moteur (6 bis)** : une exclusion « à demander » *entamée* (un de ses faits positifs est établi)
  fait poser la question ; une exclusion que rien n'évoque reste une réserve. Essayée d'abord autrement
  (une circonstance par garantie) : chaque cambriolage demandait alors « y a-t-il des travaux ? », pire.

**Effet sur Assureur A**, mesuré par l'oracle sur les 126 cas Assureur A (golden, mise au point, validation) : un seul
change, g2-i06 (gel pendant une absence), de « couvert sous réserve » à « incertain : les mesures contre le gel
étaient-elles prises ? », exactement la réponse attendue par son annotation. Un test unitaire qui figeait
l'ancien comportement est mis à jour, avec la raison.

**Second passage : 15 sur 15.** Un test vérifie désormais, pour chaque contrat du golden set, que les règles
seules donnent la réponse attendue sur les faits idéaux.

**Outils rendus génériques au passage.**
- `--accepter` remplace le bloc d'un article déjà accepté au lieu de l'ajouter une seconde fois ; les
  contrôles d'une proposition ignorent ce bloc (sinon « la garantie existe déjà »).
- L'empreinte du golden set est calculée par contrat, sur ses seules lignes du fichier de sinistres commun :
  ajouter Assureur B ne « modifie » pas le golden d'Assureur A, qui reste en v6.

**Leçon 73.** Trois filets, trois sortes d'erreurs : les contrôles attrapent la forme, la relecture attrape le
sens visible, les cas attrapent le sens en action, une exclusion qui en tue une autre. Aucun ne suffit seul.

### 7.59 Premier banc Assureur B : les règles sont justes, la lecture des nouvelles variables ne l'est pas encore

Golden Assureur B figé en v7 (15 cas). Banc, Mistral Small, lecture vérifiée, trois exécutions :

| | Assureur B (15 cas) | Assureur A (97 cas, 7.57) |
|---|---|---|
| Règles seules | 100 % justes | 100 % |
| Chaîne : justes | 62 % | 89 % |
| Couverts à tort | **0** | 2,33 |
| Refus à tort | 1,33 | 1 |
| Instables | 3 | 13 |
| Un cas à la fois, médiane / 95e centile | 3,5 s / 5,2 s | 3,2 s / 4,5 s |

Le test différentiel Prolog / oracle passe avec la règle « exclusion entamée » (128 tests sur le poste).

**Où la chaîne perd.** Pas dans les règles : dans la lecture des variables nouvelles, qui n'ont pas encore les
aides par valeur que celles d'Assureur A ont reçues en trente itérations.
- v14 (hôtel) : `proprietaire = hote` ; le modèle a lu « hôte » comme « hôtel ».
- v10 : « garage séparé de la maison » lu `garage` et non `annexe` ; la tondeuse lue comme véhicule à moteur.
- v09 : « j'habite un appartement » n'est pas compris comme une occupation partielle.
- v02, v03, v08 : la lecture donne la bonne décision, mais la confirmation des faits décisifs suspend la réponse
  (« je ne sais pas ») : c'est le prix, voulu, de zéro couvert à tort.

**Correction : des aides par valeur** pour `proprietaire` (« un hôte, pas un hôtel »), `occupation_partielle`,
`lieu` (garage attenant / annexe séparée), `bien = vehicule_moteur` (pas une tondeuse), `violence` (bousculade,
arrachage / pickpocket). Elles servent aussi à Assureur A, dont le banc est à relancer.

**Biais de mesure à corriger plus tard.** Les faits idéaux Assureur B contiennent des valeurs par défaut que la
déclaration ne dit pas (`auteur = tiers`, `proprietaire = assure`) : le rappel des faits (69 %) est sous-estimé.

**Leçon 74.** Le coût d'un nouvel assureur n'est pas seulement la rédaction des règles : chaque variable nouvelle
doit apprendre à être lue. La rédaction devrait proposer les aides par valeur en même temps que la variable.

### 7.60 Après les aides : Assureur A au meilleur niveau mesuré, Assureur B lit mieux mais suspend encore

| | Assureur B avant aides | Assureur B après | Assureur A (7.57) | Assureur A après |
|---|---|---|---|---|
| Rappel des faits | 69 % | **81 %** | 87 % | 87 % |
| Cas avec contradiction | 4 | 2 | 15 | 17 |
| Chaîne : justes | 62 % | 62 % | 89 % | **90 %** |
| Exactes | 42 % | 47 % | 65 % | 67 % |
| Couverts à tort | 0 | 0 | 2,33 | **1,33** |
| Refus à tort | 1,33 | 1 | 1 | 1 |
| 95e centile, un cas à la fois | 5,2 s | 5,3 s | 4,5 s | **4,1 s** |

Assureur A atteint son meilleur niveau de couverts à tort : les aides servent aux deux contrats.

**Ce qui reste sur Assureur B, cas par cas.**
- v10 : la tondeuse est encore lue comme véhicule à moteur, et l'exclusion « les vols de véhicules
  automoteurs » écartait **tout le sinistre**, vélos compris. Erreur de traduction : elle vise le bien, comme
  « le vol des animaux ». Scindée en deux exclusions de portée bien (véhicule ; remorque hors du bâtiment).
  Troisième passe tracée dans `meta.relecture`. Avec la même lecture, la réponse devient « couvert » (les vélos).
- v06 (pickpocket) : `vol_sur_personne` lu « non » ; v09 (cadenas) : `serrure_surete = non` non lu. Aides
  ajoutées (« pris dans une poche ou un sac que vous portiez » ; « cadenas, simple loquet »).
- v02, v08 : la lecture donne la bonne décision, la confirmation suspend (« je ne sais pas »). C'est le prix
  de zéro couvert à tort ; sur Assureur B, avec 15 cas, il pèse lourd (2 cas = 13 points).
- v12 : la femme de ménage lue comme `abus_confiance = oui`. Juridiquement défendable ; la réponse reste un
  refus.

**Mesure après la troisième passe** (128 tests sur le poste ; `--controler` avec SWI-Prolog : rien de
bloquant) : Assureur B **76 % justes** (62 % avant), 56 % exactes, **couverts à tort 0, refus à tort 0**, 1 cas
instable sur 15, une seule contradiction de lecture ; un cas à la fois, médiane 3,3 s et 95e centile 4,7 s.
Deux portes échouent encore : les décisions changées par la lecture (3,67 par exécution, seuil 2) et
l'exactitude de la chaîne (75,5 %, seuil 85 %), l'écart venant surtout des réponses suspendues par la
confirmation. Ces 15 cas ont été écrits par celui qui a relu les règles : la prochaine mesure honnête est
un jeu Assureur B écrit sans voir les règles.

**Leçon 75.** Sur un contrat neuf, le banc trouve d'abord des erreurs de traduction (portée d'une exclusion),
puis des erreurs de lecture ; les premières se corrigent une fois, les secondes demandent des aides qui
profitent à tous les contrats.

### 7.61 Synthèse du 18 novembre au soir : un deuxième assureur, de zéro règle à 76 %

Ce que la soirée devait montrer : que la méthode tient sur un contrat qu'on n'a pas écrit à la main. La garantie
vol d'Assureur B (art. 3.1.6 : 8 sous-garanties, 11 exclusions) a été rédigée par Mistral Large, contrôlée par
le code, relue, testée, mesurée. Chaque erreur trouvée a été corrigée **dans la méthode** (consigne, contrôles,
moteur, outils) et pas seulement dans le contrat : la question de l'auteur à mi-parcours, « il faut que ce soit
généralisable, non ? », a fixé la règle.

**La progression d'Assureur B 3.1.6, étape par étape**

| Étape | Section | Résultat | Correction générale qui en sort |
|---|---|---|---|
| Rédaction 1 (consigne v2) | 7.53 | plantage des contrôles ; puis 16 bloquants, extensions sans exclusions, faits en double | `non_traduit` en phrases toléré ; 4 contrôles nouveaux (exclusions communes, réserves, limites conditionnelles, `plus_proche`) ; vocabulaire donné avec son sens |
| Rédaction 2 (consigne v3), 27 min | 7.54 | fond juste (exclusions communes, vol simple en concept, réserves gardées) ; forme cassée : 9 bloquants | conditions nues remises en forme par le code (pas de reprise de 10 min) ; listes numérotées et citations en double |
| Contrôles rejoués (v4), sans modèle | 7.54 | 20 bloquants, tous des décisions humaines (18 faits nouveaux, 2 non traduits) | — |
| Relecture humaine, ~20 min à deux | 7.55 | 18 faits proposés → 11 gardés ; conflit tire / agression corrigé ; question métier posée (jardin) | champ `hors_decision` |
| Vocabulaire accepté | 7.56 | 0 bloquant ; règles chargées par SWI-Prolog | une variable acceptée ne vaut que pour les événements de sa garantie (« pour ») |
| Règles acceptées ; banc Assureur A | 7.57 | Assureur A inchangé dans la marge | chaque contrat ne lit que les variables de ses règles |
| 15 cas Assureur B, règles seules | 7.58 | **11 / 15**, puis **15 / 15** | consigne v5 (« à l'extérieur ») ; moteur : exclusion **entamée** = question (améliore aussi Assureur A, g2-i06) ; `--accepter` remplace ; golden par contrat |
| Premier banc Assureur B | 7.59 | 62 % justes, 0 couvert à tort | aides par valeur des variables nouvelles |
| Banc après les aides | 7.60 | 62 % (lecture 69 → 81 %) | exclusion « véhicules » limitée au bien ; aides vol sur la personne, serrure de sûreté |
| Banc final | 7.60 | **76 % justes, 0 couvert à tort, 0 refus à tort**, 1 instable ; 95e centile 4,7 s | — |

**Le banc Assureur B, dans le temps** (15 cas, Mistral Small, lecture vérifiée, 3 exécutions)

| | 22 h 17 | 22 h 20 | 22 h 37 |
|---|---|---|---|
| Règles seules | 100 % | 100 % | 100 % |
| Rappel des faits | 69 % | 81 % | 82 % |
| Contradictions de lecture | 4 | 2 | 1 |
| Décisions changées par la lecture | 5,33 | 6,33 | 3,67 |
| Chaîne : justes | 62 % | 62 % | **76 %** |
| Chaîne : exactes | 42 % | 47 % | 56 % |
| Couverts à tort | 0 | 0 | **0** |
| Refus à tort | 1,33 | 1 | **0** |
| Instables | 3 | 4 | 1 |
| 95e centile, un cas à la fois | 5,2 s | 5,3 s | 4,7 s |

**Assureur A pendant ce temps** (97 cas) : rien n'a été cassé, et les corrections générales l'ont amélioré.

| | Avant Assureur B (17 h 10) | Assureur B accepté (21 h 59) | Lecture par contrat (22 h 13) | Aides (22 h 31) |
|---|---|---|---|---|
| Règles seules | 100 % | 100 % | 100 % | 100 % (81 % exactes) |
| Chaîne : justes | 90 % | 89 % | 89 % | **90 %** |
| Couverts à tort | 2,33 | 3 | 2,33 | **1,33** (meilleur mesuré) |
| Refus à tort | 1,33 | 0,67 | 1 | 1 |
| Instables | 10 | 9 | 13 | 12 |
| 95e centile, un cas à la fois | 4,7 s | 20,3 s (une question lente) | 4,5 s | **4,1 s** |

**Ce que coûte un nouvel assureur, mesuré.** Pour une garantie de 8 sous-garanties : 2 rédactions par Mistral
Large (6 puis 27 minutes) ; environ 20 minutes de relecture à deux, puis deux passes plus courtes guidées par les
cas et le banc ; 11 variables et 1 valeur ajoutées au vocabulaire commun, avec leurs aides de lecture ; 15 cas
écrits. Le prochain assureur bénéficie de tout ce qui a été rendu générique ce soir.

**Ce que ces chiffres ne disent pas.** Les 15 cas Assureur B ont été écrits par Claude après avoir relu les règles :
ils mesurent la cohérence, pas la justesse face à un sinistre réel. Sur 15 cas, un cas pèse 6,7 points.

### 7.62 Toutes les garanties : Assureur A d'abord, Assureur B ensuite, et deux outils avant de commencer

Objectif fixé par l'auteur le 18 au soir : traduire **toutes** les garanties d'Assureur A, puis toutes celles d'Assureur B,
avec la chaîne mise au point sur Assureur B 3.1.6 (rédaction, contrôles, relecture, cas, banc).

**L'inventaire Assureur A.** Déjà traduits : incendie (2.1), dégâts des eaux (2.7), bris de vitrages (2.9, rédigé par
le modèle), vol (2.10), exclusions générales (1.4). Restent, en trois lots :
- **Lot A, dommages aux biens** : tempête (2.2), catastrophes naturelles (2.3), attentat et conflit du travail
  (2.4), électricité (2.6), mazout (2.8), dégradations immobilières (2.11), mérule (2.12).
- **Lot B** : responsabilité civile immeuble (2.5), extensions (3.1), garanties complémentaires (4), pack
  multimédia (6.1).
- **Lot C, d'une autre nature** : responsabilité civile vie privée (section 5), assistance (2.13), défense et
  recours (2.14). Ce ne sont pas des dommages aux biens : le vocabulaire actuel (événement, bien, lieu) n'y suffit
  pas, il faudra des faits de responsabilité (tiers lésé, faute, activité).

**Deux outils avant de lancer.**
- *Rédaction en parallèle* (`--paralleles`, 3 par défaut) : une rédaction attend surtout le modèle (6 à 27
  minutes) ; onze articles l'un après l'autre prendraient des heures. Un échec n'arrête pas les autres ; les
  doublons entre propositions (un concept défini deux fois) sont vus au contrôle qui suit chaque acceptation.
- *Les aides de lecture proposées par la rédaction* (consigne v6, leçon 74) : chaque variable nouvelle vient avec,
  pour chaque valeur, ce qu'un assuré dirait pour qu'on la retienne ; `--accepter-vocabulaire` les reprend. Sans
  elles, le premier banc Assureur B avait perdu 14 points de lecture. Une variable nouvelle sans aide est « à relire ».

### 7.63 Assureur A, lot A : sept garanties rédigées en 19 minutes, relues, acceptées

**La rédaction.** Onze articles (lots A et B) rédigés par Mistral Large, trois à la fois : **19 minutes** en tout
(une seule garantie Assureur B en avait pris 27 la veille, seule). Aucun plantage, aucune condition nue. La consigne v6
a tenu : chaque variable nouvelle est venue avec ses aides de lecture et sa voisine la plus proche.

**Le défaut de la rédaction en parallèle : le vocabulaire.** Chaque proposition ignore les autres. Le même fait
est arrivé sous plusieurs noms : « à l'extérieur » trois fois (`a_l_exterieur`, `situe_exterieur`,
`lieu = exterieur`), les constructions délabrées et le logement principal deux fois (2.2 et 2.3), le contrôle des
citernes deux fois (2.5 et 2.8), les matériaux à pied d'œuvre en variable (2.2) et en bien (2.11). Harmonisé à la
relecture (`relecture/assureur_a_lot_a.py`, tracé dans `meta.relecture` de chaque proposition) : 95 faits proposés pour
les onze articles ; pour les sept du lot A, 50 proposés, **24 gardés** sous un nom commun.

**Les corrections de fond, article par article.**
- *2.2 tempête* : la définition (vent ≥ 80 km/h ou dégâts dans les 10 km) ne vaut que pour le vent ; la garantie
  couvre aussi la grêle et la neige. Variable `alea_tempete` (vent, grêle, neige ou glace) et circonstance
  `si(vent, tempête)`. « Tout objet à l'extérieur » vise les objets, pas le bâtiment (un balcon abîmé par des
  tuiles, g2-i11, était refusé).
- *2.3 catastrophes naturelles* : le « risque aggravé » n'exclut pas, il change de régime (Bureau de
  Tarification) ; en circonstance, il faisait poser une question à chaque inondation : hors décision. La phrase
  sur les biens reconstruits, que le modèle avait ajoutée à chaque exclusion, concerne l'indemnisation : hors
  décision.
- *2.4 attentat* : la circonstance « détruits par des participants » est ce que l'événement désigne ; elle faisait
  poser la question à chaque fois : retirée.
- *2.6 électricité* : exclusion des appareils professionnels limitée au bien (un congélateur et un ordinateur
  grillés : le congélateur reste couvert) ; la garantie du fabricant est à l'assureur de l'établir.
- *2.8 mazout* : citerne en valeur de `bien` ; les frais d'assainissement des terres sont des frais exclus, pas un
  sinistre exclu : hors décision.
- *2.11 dégradations* : `malveillance` est du vandalisme ; les obligations « abri de jardin » et « matériel de
  jardin » s'appliquaient à tout sinistre : conditionnées.
- *2.12 mérule* : acceptée telle quelle.

**Trois corrections générales.**
- Une variable existante qu'un nouvel article emploie est désormais lue pour ses événements aussi :
  `prevention_gel` servait au mazout mais n'était lue que pour les dégâts des eaux (`etendre_pour`). Une variable
  proposée par deux articles prend les événements des deux.
- Le contrôle « la définition de l'événement couvert est employée » reconnaît un concept déjà défini dans les
  règles du contrat (`concept(vol)` → 12/vol).
- Les tests qui ont besoin d'une garantie non traduite la retirent eux-mêmes du contrat (`retirer_article`) au
  lieu de dépendre de l'avancement des traductions : quatre tests supposaient la tempête non traduite.

**Golden v8** : les faits idéaux de trois cas écrits quand ces garanties n'étaient pas traduites ont été complétés
(g2-p10 : l'usage professionnel ; g2-i11 : le vent ; red-t03 : neige, annexe sans ancrage, non close).

**Règles seules (oracle), Assureur A, 97 cas : 100 % justes, 0 couvert à tort, 0 refus à tort, 92 % exactes (87 %
avant le lot A)** : des « incertain » de cas hors règles deviennent des réponses fermes justes (denrées décongelées,
fioul, tags sur la porte). Assureur B inchangé (100 %).

**Le lot B attend.** Les extensions (3.1) et les garanties complémentaires (4) ne s'appliquent qu'**après** un
sinistre couvert (frais de sauvetage, logement provisoire, séjour temporaire) ; traduites comme des garanties
ordinaires, elles ont fait passer 25 refus justes à « incertain » au contrôle de non-régression. Il faut au moteur
la notion de **garantie accessoire** : évaluée seulement si une garantie de base couvre, et qui ne change jamais la
décision. La responsabilité civile immeuble (2.5) demande, comme la section 5, un vocabulaire de responsabilité
(tiers lésé, origine du dommage). Le pack multimédia (6.1) demande trois événements nouveaux (chute, heurt, corps
étranger) et une option des conditions particulières.

**Leçon 77.** Rédiger en parallèle va trois fois plus vite, mais chaque proposition invente son vocabulaire : la
relecture commence par harmoniser les noms, avant de juger le fond.

### 7.64 Le banc après le lot A : la chaîne recule, et la cause est dans le vocabulaire

Banc Assureur A, golden v8, Mistral Small (sur le poste, 128 tests et `--controler` sans rien de bloquant) :

| | Avant le lot A (7.60) | Après |
|---|---|---|
| Règles seules : justes / exactes | 100 % / 81 % | 100 % / **92 %** |
| Chaîne : justes / exactes | 90 % / 67 % | 89 % / **76 %** |
| Couverts à tort | 1,33 | **4,33** |
| Refus à tort | 1 | 0,33 |
| Contradictions de lecture | 17 cas | 26 cas |
| 95e centile, un cas à la fois | 4,1 s | 39 s (médiane 3,6 s : lenteur de l'API) |

L'exactitude monte (les garanties traduites répondent là où l'on disait « je ne sais pas »), mais trois cas
nouveaux deviennent couverts à tort. Lecture cas par cas :
- **val-03** (ordinateur d'amis hébergés, volé) : l'ordinateur est lu `appareil_informatique`, valeur ajoutée
  par 2.6. Elle n'était rattachée à rien : ce n'était plus de l'« électronique », donc plus du « contenu » pour la
  garantie vol écrite avant elle. **Défaut général** : une valeur plus fine d'une variable existante doit déclarer
  sa valeur parente (le vocabulaire sait l'exprimer, `parents` ; ni la consigne ni l'acceptation ne le
  demandaient). Corrigé : consigne v7 (`parent`), `--accepter-vocabulaire` le reprend, une valeur nouvelle sans
  parent est « à relire » ; rattachements ajoutés pour `appareil_informatique` (électronique),
  `denrees_alimentaires` (objet divers), `citerne` (élément du bâtiment).
- **red-b06** (vitre rayée) : lu `vandalisme` sans que personne soit nommé ; la garantie 2.11 couvre alors. Aide
  ajoutée : le vandalisme suppose que quelqu'un a abîmé exprès.
- **g2-i04** (bijoux disparus après le plombier) : `simple_disparition = non` inventé. Aide ajoutée.
- **bougie-04** : le jardin lu « terrasse », déjà vu (7.44).

**Leçon 78.** Chaque garantie traduite ouvre une route de plus vers « couvert » : une lecture approximative qui
ne menait nulle part peut désormais aboutir. Les aides de lecture et la hiérarchie des valeurs sont aussi
importantes que les règles.

### 7.65 Assureur B, lot A : huit garanties rédigées en 21 minutes, relues, acceptées

Incendie et périls assimilés (3.1.1, sept garanties : incendie, décongélation, linge, heurt, dégradations
immobilières à l'occasion d'un vol, vandalisme, attentats), tempête et grêle (3.1.2), dégâts électriques (3.1.3),
dégâts des eaux (3.1.4), bris de vitrages (3.1.5), matériel multimédia (3.1.7, bris et vol), tremblement de terre
(3.2.1), pluies et inondations (3.2.2). Relecture : `relecture/assureur_b_lot_a.py`, tracée dans chaque proposition.

**Trois défauts qui reviennent dans presque toutes les propositions, traités de la même façon partout.**
- *« Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent la garantie
  X »* : le modèle l'a mis dans le périmètre (`garantie_incendie_accordee = oui`), ce qui faisait poser la
  question à chaque déclaration. C'est une option du contrat : une **réserve** (`option_incendie`,
  `option_tempete`… ; exclusion « option = non », à demander) : « couvert, sous réserve que vos conditions
  particulières mentionnent la garantie ».
- *Des frais exclus* (reconstitution des données, entretien, pertes indirectes, franchise de 60 €, frais de
  recherche de fuite) : sans effet sur la question de couverture, **hors décision**.
- *Des exclusions de biens sans portée* (lunettes, toiture, véhicules, plantations) : portée limitée au bien. La
  toiture, sans cela, excluait tout le bâtiment des dégâts des eaux.

**Les erreurs de fond.**
- 3.1.1 : « dégradations immobilières à l'occasion d'un vol » couvrait **tout vol**, contenu compris ; limité aux
  éléments du bâtiment. La définition de l'incendie (flammes qui se propagent) s'appliquait à l'explosion et à
  la foudre. « Propriétaire du bâtiment » avait été traduit par `proprietaire = assure`, qui dit à qui sont les
  biens : variable `statut_logement`.
- 3.1.2 : deux circonstances contradictoires (la tempête à 80 km/h, et « grêle ou neige ») : un coup de vent ne
  pouvait jamais être couvert. Une seule : `si(vent, tempête)`.
- 3.1.4 : « infiltration extérieure » était à la fois condition de la garantie et exclusion.
- 3.1.7 : le matériel multimédia (1.25 : ordinateur, téléphone…) est `electronique` ; l'alarme et la domotique y
  sont rattachées. La condition propre à l'alarme s'appliquait à tout appareil ; l'obligation du véhicule à tout
  sinistre.
- 3.2.1 et 3.2.2 : `evenement = tremblement_terre`, `inondation`, `ruissellement`, `glissement_terrain` →
  `catastrophe_naturelle` (comme Assureur A) et une variable `catastrophe`. Les dommages dans les 72 heures : à
  l'assureur de l'établir.

**Deux corrections générales.**
- Les événements de lecture d'une variable sont calculés **garantie par garantie** (`evenements_par_variable`) :
  3.1.1 réunit sept garanties d'événements différents, et les flammes se retrouvaient à lire pour un vol.
- Une réserve d'option combinée à l'événement (« vol et option vol inconnue ») est *entamée* dès que l'événement
  est établi (règle 7.58) et pose la question : la réserve se pose sur la seule garantie concernée, sans
  l'événement.

**Vérifications.** Golden Assureur B (oracle) : 100 % justes, 0 couvert ni refus à tort. b-v07 (téléphone arraché
dans la rue, formule inconnue) devient « couvert » par 3.1.7 : conforme au contrat, sous réserve des options
multimédia et vol ; annotation complétée, golden **v9**. Seize cas de contrôle sur les nouvelles garanties
(incendie, explosion, tempête à 100 km/h, grêle, vent de force inconnue, fuite, pluie par une fenêtre ouverte,
vitre, lunettes, téléphone tombé ou volé dans une voiture, séisme, inondation, surtension, voiture contre le mur) :
réponses conformes au texte, les options en réserve.

**Leçon 79.** Un contrat qui découpe ses garanties en options (« si les conditions particulières le
mentionnent ») ne se lit pas comme un contrat tout compris : l'option est une réserve, jamais une question posée
au déclarant, qui ne la connaît pas.

### 7.66 Assureur A après les rattachements : 5 couverts à tort, tous des erreurs de lecture confirmées

Banc Assureur A (golden v8, sur le poste, 128 tests) : règles seules 100 % (91 % exactes) ; chaîne 89 % justes,
73 % exactes, **5 couverts à tort**, 0,67 refus à tort, 14 instables ; un cas à la fois, 95e centile 4,2 s.
(Le vocabulaire d'Assureur B a été déposé pendant ce banc : la mesure est à refaire, mais les cas parlent.)

Les sept cas couverts à tort, un par un : le jardin lu « terrasse » (bougie-04, 3 sur 3), la vitre rayée lue
« vandalisme » (red-b06, 3 sur 3 malgré l'aide de 7.64), les clés sous le paillasson lues « clés volées » (g-p03,
3 sur 3, connu depuis 7.50), le bain à bulles lu « aquarium » (g2-p08), le vase en cristal lu « verre de
meuble » (red-b04), et deux tirages isolés. **Aucune erreur de règle.**

Toutes ces lectures sont passées par la confirmation des faits décisifs (7.49) : le même petit modèle relit sa
propre lecture et la confirme. Plus il y a de garanties traduites, plus une lecture approximative trouve une
garantie qui couvre (leçon 78).

**Correction mise en place, à mesurer** : la confirmation peut être faite par un modèle plus fort que celui de la
lecture (`COUVERTURE_MODELE_CONFIRMATION`, par exemple `mistral-large-latest`). Elle ne porte que sur les quelques
faits dont dépend une réponse ferme (le moteur les désigne en quelques millisecondes) : un appel court, et
seulement quand la réponse est ferme. Le banc note le modèle de confirmation dans son résultat et le nom de son
rapport. Un test vérifie que c'est ce modèle, et non le lecteur, qui tranche.

### 7.67 Confirmer avec Mistral Large : moins de couverts à tort, plus de « je ne sais pas », trois fois plus lent

Même vocabulaire, même golden (v9), Mistral Small pour la lecture, trois exécutions :

| Assureur A, 97 cas | Confirmation par Small | Confirmation par Large |
|---|---|---|
| Chaîne : justes / exactes | 89 % / 75 % | 86 % / 67 % |
| **Couverts à tort** (par exécution) | **4** | **1,67** |
| Refus à tort | 0,67 | 0 |
| Réponses « couvert / non couvert / incertain » (sur 291) | 130 / 94 / 67 | 89 / 81 / 121 |
| Un cas à la fois, médiane / 95e centile | 3,2 s / 19 s | **8,6 s / 40 s** |

Assureur B (15 cas), confirmation par Large : 82 % justes (76 % avec Small), 0 couvert et 0 refus à tort, 1 instable ;
médiane 7,8 s.

**Ce que fait Large.** Il refuse la vitre rayée lue « vandalisme », le jardin lu « terrasse », les clés sous le
paillasson : bougie-04, red-b06 et g-p03 ne couvrent plus à tort. Il ne voit pas le bain à bulles lu
« aquarium » (g2-p08, 3 sur 3) : l'erreur n'est pas dans un fait décisif que l'on confirme, mais dans le choix de
la valeur. Et il est plus exigeant : dix cas justement couverts (la bougie qui brûle la table, un dégât des eaux
simple…) deviennent « incertains », parce qu'il juge « non dit » ce que la déclaration implique.

**Décision : l'option reste désactivée par défaut**, documentée et mesurée. Elle divise les couverts à tort par
2,4 au prix de 3 points de réponses justes et d'un temps de réponse multiplié par 2,7 (la porte « 95e centile
≤ 10 s » échoue). Pour un gestionnaire qui préfère un « je ne sais pas » à une erreur, elle se justifie ; pour un
traitement de masse, non. C'est un réglage d'exploitation (`COUVERTURE_MODELE_CONFIRMATION`), pas un choix de code.

**Deux réglages Assureur B au passage.** « L'action subite de la chaleur » (3.1.1.1.6) faisait poser la question pour un
cambriolage : limitée à l'incendie et aux autres événements. b-v07 n'attend plus la question de la formule
(la réponse couverte sous réserve des options ne la pose plus) : golden v10.

**Leçon 80.** Un juge plus fort corrige les erreurs de fait, pas les erreurs de choix ; et un juge plus strict
coûte des réponses justes. Le bon réglage dépend de qui lit la réponse.

### 7.68 Les garanties accessoires : ce qui s'ajoute à un sinistre couvert, sans décider s'il l'est

**Le problème.** Le lot B d'Assureur A (art. 3.1, extensions ; art. 4, garanties complémentaires) et celui d'Assureur B
(3.1.8, 3.1.9, 3.2.3) décrivent des garanties qui ne jouent qu'**après** un sinistre couvert : frais de sauvetage,
de déblai, de logement provisoire, extension à un séjour temporaire, pertes indirectes. Traduites comme des
garanties ordinaires, elles entraient dans la décision : leur périmètre (« tout sinistre couvert ») rattachait
chaque déclaration, leurs conditions inconnues (« le logement est-il inhabitable ? ») faisaient passer des refus
justes à « incertain », et leur seule présence marquait les événements comme « traduits ». Le contrôle de
non-régression du lot B d'Assureur A refusait les propositions pour cette raison (25 cas).

**Ce qui change, dans le moteur et non dans un contrat.**
- Un fait `accessoire(Garantie)`. Une garantie accessoire **n'entre pas dans la décision** : COUVERT, INCERTAIN
  ou NON_COUVERT se décident sur les garanties de base seules, exactement comme avant.
- Si la décision est COUVERT, le moteur évalue les accessoires et liste dans la réponse (`accessoires`) celles qui
  s'appliquent ou pourraient s'appliquer, avec leurs questions. Le motif ajoute : « Peuvent s'y ajouter :
  « Frais de logement provisoire » (4) sous réserve de précisions ». Elles ne changent jamais la décision.
- Un sinistre non couvert n'ouvre aucune accessoire, même si ses conditions sont remplies ; un sinistre incertain
  ne pose que les questions de la garantie de base.
- Une proposition faite seulement d'accessoires ne marque aucun événement comme « traduit » : des frais de déblai
  ne disent pas si une tempête est couverte.
- L'oracle Python (`tests/moteur_reference.py`) fait de même, pour le test différentiel avec SWI-Prolog.
- Rédaction : champ `"accessoire": true` sur la garantie, émis en `accessoire(id).` ; **consigne v8**, qui dit au
  modèle quand le mettre et de ne pas mettre tous les événements du contrat dans le périmètre.

**Tests.** 127 réussis (2 nouveaux) : décision inchangée et accessoire listée quand c'est couvert ; aucune accessoire
pour un refus ; seule la question de la garantie de base pour un doute ; pas d'`evenement_traduit` pour une
proposition d'accessoires.

**Leçon 81.** Une garantie n'est pas toujours une réponse à « est-ce couvert ? ». Certaines répondent à « et
qu'est-ce qui s'y ajoute ? ». Les mettre au même niveau dans le moteur dégrade les décisions qu'elles ne
concernent pas ; la distinction se fait une fois, dans le moteur, et vaut pour tous les contrats.

### 7.69 Le lot B d'Assureur A : trois façons d'« étendre » une garantie, et une seule était accessoire

**Rédaction (consigne v8, Mistral Large, 12 min).** Art. 3.1 : sept « extensions », toutes marquées accessoires
par le modèle ; art. 4 : une garantie complémentaire (frais de sauvetage, déblai, logement provisoire, expertise…),
accessoire aussi. Contrôles : 9 bloquants pour 3.1 (du vocabulaire nouveau à accepter), 3 pour 4 (un concept
« sinistre » inconnu et deux passages non traduits : le barème d'expertise et sa procédure).

**Ce que la relecture a montré, en simulant les 97 cas du golden avec l'oracle.** L'art. 4 ne change aucune
décision et s'ajoute aux 44 sinistres couverts : c'est bien une accessoire. Mais un incendie à l'hôtel restait
NON_COUVERT : « le contenu lors d'un séjour temporaire » n'ajoute rien à un sinistre couvert, il **élargit le lieu
assuré**, et toutes les garanties de base excluent un « autre bâtiment » par leur concept `batiment`. Accessoire,
l'extension ne jouait jamais.

**Trois corrections, dans le code et non dans le contrat.**
1. **Extension de définition** (moteur et oracle) : `extension(batiment, Condition, Art, Texte)` élargit la
   définition du bâtiment pour toutes les garanties qui l'emploient. Elle n'est jamais présumée : elle compte si
   elle est établie, ou entamée par ses propres faits (le séjour ou l'« autre bâtiment » sont déclarés), jamais par
   les concepts qu'elle emploie (« contenu » est établi par presque toute déclaration). Sinon ses questions
   seraient posées à chaque sinistre : c'est ce que la première simulation montrait (3 cas). La preuve cite
   l'extension quand elle joue. Rédaction : champ `extensions`, consigne v9, contrôle « extension d'un concept
   inconnu » ; à l'acceptation, une variable d'extension est lue pour tous les sinistres (plus de « pour »).
2. **Conditions particulières en réserve, pour tout contrat** : « en fonction des couvertures mentionnées dans vos
   conditions particulières » devient une exclusion « non condition » à demander, c'est-à-dire une réserve, et non
   une question posée à chaque sinistre. Le relecteur le faisait à la main pour huit garanties optionnelles d'Assureur B
   (7.62) ; le contrôle le fait désormais (`conditions_particulieres_en_reserve`), pour une condition oui/non
   seulement : une formule à plusieurs valeurs (Assureur A : Privilège, Active) reste demandée. Sur les propositions
   existantes, seules 3.1 et 6.1 (non acceptées) changent.
3. **Accessoires** : seules celles dont le périmètre est établi sont listées (sans cela, chaque incendie couvert
   énumérait les sept extensions) ; un passage non traduit d'un article fait seulement d'accessoires ne bloque
   plus (il ne peut pas changer une décision) ; le périmètre d'une accessoire ne dit pas « sinistre » (consigne v9).

**Relecture** (`relecture/assureur_a_lot_b.py`). 3.1 : séjour temporaire et transport pendant le déménagement deviennent
deux extensions du bâtiment (pour le contenu) ; la nouvelle adresse est hors décision (le logement est déjà le
bâtiment) ; les quatre extensions de responsabilité locative restent accessoires, à revoir avec la section 5.
4 : périmètre vidé. La question `sejour_temporaire`, écrite pour le vol d'Assureur B, devient générale (« hors de chez
vous, lors d'un séjour temporaire »).

**Simulation (oracle, 97 cas Assureur A).** Aucune décision ne change. Une question s'ajoute pour g2-i08 (« vol de mon
sac au restaurant ») : le séjour temporaire, que l'« autre bâtiment » entame ; la question attendue (violence)
reste posée. Incendie à l'hôtel en séjour : COUVERT par la garantie incendie, avec la citation de l'extension.
Tests : 131 réussis.

**Leçon 82.** « Étendre » recouvre trois choses : ajouter des frais à un sinistre couvert (accessoire), élargir un
lieu ou un bien assuré (extension de définition), et couvrir une autre responsabilité (une garantie à part). Le mot
du contrat ne dit pas laquelle ; la simulation sur le golden l'a montré en une minute.

### 7.70 Le lot B accepté, les noms anonymisés, et un tour du code

**Banc après le lot B** (golden v10, Mistral Small, trois exécutions, assureur A) :

| | Avant le lot B (7.67) | Après |
|---|---|---|
| Règles seules : justes / exactes | 100 % / 91 % | 100 % / 91 % |
| Chaîne : justes / exactes | 89 % / 75 % | 88 % / 76 % |
| Couverts à tort (par exécution) | 4 | 5,33 |
| Un cas à la fois : médiane / 95e centile | 3,2 s / 19 s | 3,4 s / 39 s |

Les couverts à tort sont les mêmes cas, tous des erreurs de lecture (lieu, clé, cause de l'eau), plus g2-i04 une
fois sur trois ; aucun ne passe par une extension ou une accessoire. L'écart de 4 à 5,33 est dans la variance déjà
vue (4 à 5). Deux effets de lecture à corriger : « pendant mes vacances » est lu `sejour_temporaire = oui`
(l'aide écrite en 7.69 le suggérait), et les variables des quatre extensions de responsabilité locative, sans
événement, sont lues pour tout sinistre.

**Les deux effets de lecture, corrigés dans la méthode.** Une variable que seules des garanties accessoires
emploient n'est plus lue (`"pour": ["accessoire"]`) : elle ne peut rien décider. Une variable d'extension est lue
pour ses événements d'origine, et aussi quand le temps 1 a lu le lieu qui entame l'extension (`"si": {"lieu":
["autre_batiment"]}`) ; `--accepter-vocabulaire` l'écrit seul. Le séjour temporaire n'est donc plus cherché dans
chaque incendie au logement, et son aide dit ce qui compte : les biens hors de chez soi, pas le déclarant en
vacances. Le test « la consigne du temps 2 est courte » l'avait signalé (8 193 caractères pour un vol) ; il
repasse.

**Un défaut du moteur, trouvé par l'oracle.** Avec les règles du lot B, Prolog et l'oracle Python donnaient la
même décision mais deux arbres de preuve différents pour velo-01 : Prolog montrait les deux extensions du bâtiment
comme actives. Cause : `extension_active` demandait `eval(X, oui)` avec la valeur déjà liée, et pour une condition
« et », la dernière clause de `et3` (`et3(_, oui)`) réussit toujours. La décision restait juste (la condition
élargie est réévaluée), mais les faits des extensions pouvaient devenir des questions. Corrigé : on évalue, puis
on compare. Le test différentiel a fait exactement son travail.

**Anonymisation.** Les assureurs deviennent Assureur A, B, C et D, partout dans le dépôt : identifiants
(`assureur-a-habitation-2025`…), fichiers, cas (`b-v07`), documentation. Un script hors dépôt (`perso/`) fait
la correspondance, renomme les PDF locaux et met à jour la base ; les liens de téléchargement restent dans
`data/contrats/SOURCES.prive.md`, non versionné. Les empreintes du golden suivent, sa version ne change pas (mêmes
cas). Le nom commun « foyer » (le foyer d'un incendie) reste. L'historique git n'est pas réécrit, et les
citations des conditions générales restent mot pour mot : elles ne contiennent pas les noms, mais un lecteur
pourrait retrouver le texte.

**Tour du code.** Retirés : trois fonctions jamais appelées (`charger_texte`, `ecrire_profil`, `segmenter`) et
la racinisation de `texte.py`, restes de la recherche retirée en 7.36 ; une fixture de test inutilisée.
`__version__` suit `pyproject.toml` (0.4.0). `EXPLICATIONS.md` décrivait encore la grille, les fiches, la recherche
hybride et l'agent de réparation comme en service : réécrit sur l'état actuel (lexique, données, tests, choix,
questions, limites). L'archive des consignes liste toutes les versions en service. La CI installe SWI-Prolog et
passe à uv : le test qui compare Prolog et l'oracle y tournait sauté. Gardés, et pourquoi : les consignes des
méthodes retirées (leur histoire), les scripts `relecture/` (la trace de chaque relecture humaine), les rapports de
`data/bancs/` (la progression), les colonnes héritées du journal (bases existantes et tableaux Grafana).

**Banc après les corrections de lecture** (même golden v10, 13 h) : règles seules inchangées (100 % / 91 %) ;
chaîne **88 % justes, 76 % exactes, 4,67 couverts à tort** (5,33 avant), 0,67 refus à tort, 13 instables. La
lecture d'un vol est plus courte : médiane un cas à la fois **2,8 s** (3,4 s avant). Le 95e centile (68 s) vient
d'un seul cas sur dix, ralenti par l'API (la lecture en masse a son 95e centile à 36 s) : à surveiller, ce n'est
pas un coût de la méthode. Les couverts à tort restent des erreurs de lecture du lieu, de la clé ou de la cause
(g2-p04, le fioul siphonné à la cave, s'ajoute une fois sur trois).

**Leçon 83.** Une documentation qui décrit un système retiré est pire qu'une absence : elle se relit à chaque
simplification, comme le code.

### 7.71 Le pack multimédia (6.1) : deux défauts de forme qui auraient refusé à tort, et une extension trop curieuse

**Rédaction** (consigne v9, Mistral Large, 4 min) : une garantie optionnelle (« pour autant que vos conditions
particulières en fassent mention », mise en réserve par le code), qui couvre le matériel informatique contre la
chute, le heurt, le corps étranger, et le vol hors du bâtiment avec plainte ; cinq exclusions (lieu public, véhicule
la nuit, véhicule le jour visible ou mal fermé, simple perte). Contrôles : le vocabulaire nouveau, et un cas changé
(g2-i07, l'ordinateur volé dans la voiture).

**Ce que la relecture a trouvé, en simulant le golden avec l'oracle.**
1. *La circonstance du vol valait pour tout.* « Vol et hors du bâtiment et plainte », écrit comme circonstance de la
   garantie, interdisait la chute et le heurt : un ordinateur tombé n'aurait jamais été couvert. **Dans le code**
   (`circonstances_par_evenement`, pour tout contrat) : une circonstance qui nomme un seul des événements de la
   garantie est réécrite « si vol, alors… ».
2. *Deux obligations écrites comme des situations.* « Véhicule, voie publique, entre 22 h et 7 h » à la place d'un
   devoir : le moteur les aurait jugées violées par tout heurt à la maison, donc refusé. **Contrôle bloquant**
   (`obligations_mal_formees`) : une obligation dont l'événement, le bien ou le lieu est hors d'un « si » décrit une
   situation, pas un devoir. Ici elles redisaient les exclusions du véhicule : retirées.
3. *Une extension entamée par un simple lieu.* Avec « hors du bâtiment » traduit par le concept du contrat, un vol
   dans une voiture demandait « étiez-vous en train de déménager ? », parce que l'extension « transport pendant un
   déménagement » était entamée par `lieu = vehicule`. **Moteur et oracle** : une extension n'est entamée que par ses
   propres faits (le séjour, le déménagement), jamais par l'événement, le bien ou le lieu ; la lecture va chercher
   ces faits quand le lieu s'y prête (le « si » de 7.70). Le vol au restaurant (g2-i08) ne demande plus le séjour.

**Relecture** (`relecture/assureur_a_6_1.py`) : « hors du bâtiment » devient `non(concept(batiment))` au lieu d'une
variable nouvelle ; le bris entre dans le périmètre (un ordinateur tombé se lit souvent « bris ») ; les exclusions
« dans un lieu public » ne sont plus limitées à la voie publique ; la simple perte ne vaut que pour le vol.

**Golden v11** : g2-i07 (ordinateur volé dans la voiture) passe de NON_COUVERT à **INCERTAIN** (NON_COUVERT
acceptable) : sans le pack multimédia, rien ne joue ; avec, tout dépend de la plainte, de l'heure et de la
fermeture. Faits idéaux précisés (`appareil_informatique`, `vehicule`, voie publique). C'était une réponse du
golden écrite avant que l'option soit traduite : le golden suit le contrat, et la fiche de validation le dit.

**Simulation** (oracle, 97 cas) : seule g2-i07 change. Ordinateur tombé à la maison : COUVERT sous réserve de
l'option ; volé dans la voiture la nuit, option et plainte connues : NON_COUVERT ; le jour : INCERTAIN, avec les
questions des exclusions du véhicule. Tests : 133.

**Acceptation : deux accrocs, deux corrections dans le code.** `periode_horaire` valait « 22h_7h » : une valeur
doit commencer par une lettre, et `--accepter-vocabulaire` la refusait **en silence** (elle restait « à
accepter »). Elle est maintenant refusée en clair, et renommée `nuit_22h_7h` / `jour_7h_22h`. Puis le test « la
consigne du temps 2 est courte » a de nouveau cassé (6 978 caractères pour un vol) : les variables du véhicule se
lisaient pour tout vol, et celles du vol pour toute chute. Désormais une variable posée dans un « et » ou un
« si » qui nomme l'événement ne se lit que pour lui, et une variable qu'on n'emploie que dans un lieu
(`habitacle_ferme` : dans un véhicule) porte `"seulement_si": {"lieu": ["vehicule"]}` et ne se lit pas quand le
lieu lu est une cave. Le vocabulaire déjà accepté est corrigé à la main pour les sept variables touchées.

**Banc après le 6.1** (golden v11, 14 h) : règles seules 100 % / 91 % ; chaîne **88 % justes, 75 % exactes,
4 couverts à tort** (4,67 avant), 1,67 refus à tort (0,67), 12 instables ; un cas à la fois : médiane 3,7 s,
**95e centile 10,5 s** (68 s au passage précédent, un appel lent). Les couverts à tort sont les quatre erreurs de
lecture connues (jardin lu logement, rayure lue vandalisme, clé sous le paillasson, bain à bulles lu aquarium).
Les refus à tort sont aussi des erreurs de lecture : la baignoire qui déborde lue « récipient » (val-12, 3 fois sur
3), et g2-l03 (« je n'étais pas absente », la nuit), où la vérification retire `absence = non` que la phrase dit
pourtant. Rien ne vient des règles du 6.1 ; la lecture reste le chantier.

**Leçon 85.** Une condition écrite au mauvais niveau (toute la garantie au lieu d'un de ses événements, une
situation au lieu d'un devoir) ne se voit pas à la lecture du texte ; elle se voit sur un cas que la garantie doit
couvrir. Le code la reconnaît désormais à sa forme.

### 7.72 Assureur B, lot B : des extensions sur les concepts d'un autre contrat, et des responsabilités déguisées

**Rédaction** (consigne v9, Mistral Large, trois articles en parallèle, 13 min). 3.1.8 : onze extensions et
24 contrôles bloquants ; 3.1.9 : dix frais, tous marqués accessoires (bien) ; 3.2.3 : les pertes indirectes
(une majoration de 10 % des indemnités), accessoire aussi.

**Ce que la relecture a trouvé.**
1. *Les concepts d'un autre contrat.* Les onze extensions portaient sur `batiment`, `contenu`, `bien` : les mots
   de l'assureur A, qui servaient d'exemple dans la consigne v9. Le lieu assuré de B s'appelle `batiment_designe`.
   **Consigne v10** : le concept vient des « Concepts déjà définis dans les règles du contrat », jamais d'un autre ;
   le **contrôle** donne la liste des concepts du contrat dans son message.
2. *Des responsabilités déguisées en extensions.* « Les dégâts causés par un assuré à l'hôtel, à la chambre
   d'étudiant, au local de fête » ne disent pas qu'un lieu de plus est assuré : ils couvrent la responsabilité de
   l'assuré envers le propriétaire. Responsabilité civile non traduite : **garanties accessoires**, comme les
   extensions de responsabilité de l'assureur A (7.69). Consigne v10 : la règle est dite au modèle.
3. *Des listes de pays en valeurs.* `zone_geographique = luxembourg_allemagne_belgique_france` : une valeur par
   liste. Remplacée par `pays`, une valeur par pays, et des conditions « ou ». Consigne v10.
4. *Pertes indirectes* : la liste des garanties dont l'indemnité n'est pas majorée est un calcul de montant, pas
   une condition de couverture : hors décision.

**Relecture** (`relecture/assureur_b_lot_b.py`) : six extensions de `batiment_designe` (logement de remplacement au
Luxembourg, séjour temporaire partout, chambre d'étudiant dans l'UE, en Suisse ou en Norvège, maison de repos,
sépultures au Luxembourg, nouvelle adresse pendant 90 jours), trois responsabilités accessoires, le garage à une
autre adresse hors décision (déjà un lieu assuré). Sépultures « au Luxembourg ou à 50 km des frontières » :
Luxembourg seulement, par prudence (au-delà, pas de « couvert »).

**Simulation** (oracle, 15 cas de l'assureur B) : aucune décision ne change. Un incendie dans la chambre de
maison de repos est couvert (sous réserve de l'option incendie), avec la citation de l'extension ; les frais
(sauvetage, déblai, logement provisoire…) et les pertes indirectes s'ajoutent aux sinistres couverts.

**Leçon 86.** Un exemple dans une consigne devient le vocabulaire du modèle : il faut l'écrire comme une place à
remplir (« un concept du contrat »), pas avec le nom d'un contrat.

### 7.73 Le contrôle du lot B : trois défauts de l'acceptation du vocabulaire

**Contrôle après relecture** (19 nov.) : 3.1.9 et 3.2.3 sans contrôle bloquant ; 3.1.8 en garde trois, tous du
même type : « garantie rc_… : aucune exclusion, alors que l'article en a ». Les tests passent (137).

**Ce que l'acceptation du vocabulaire a révélé.**
1. *Le contrôle des exclusions visait les accessoires.* Une garantie sans exclusion à côté d'exclusions de
   l'article est bloquante (7.53) ; mais une accessoire ne décide rien (7.68), ses exclusions ne changeraient
   aucune réponse. Le contrôle ne la vise plus.
2. *Des pseudo-événements dans les « pour ».* `option_incendie`, `sejour_temporaire`, `travaux_construction`,
   `lien_causal_travaux` ont reçu « accessoire » dans leur liste d'événements, parce qu'une garantie de frais les
   emploie. Sans effet sur la lecture (aucun sinistre ne s'appelle « accessoire »), mais le vocabulaire en devenait
   faux. « accessoire » et « extension » ne s'ajoutent plus à une variable déjà lue ; le vocabulaire est nettoyé.
3. *Une variable d'extension lue pour chaque sinistre.* `duree_demenagement` (« la nouvelle adresse pendant
   90 jours ») n'a ni lieu ni bien qui la déclenche : l'acceptation la laissait sans « pour », donc lue partout,
   ce qui allonge la lecture de toutes les déclarations (7.70). Une variable née d'une extension sans
   déclencheur est désormais `pour: ["extension"]` : l'extension, entamée par ses autres faits (un déménagement),
   la pose en question.
4. Le compte rendu répétait sept fois « pays : lue aussi si lieu = chambre_etudiant » (une fois par pays de la
   liste) : une ligne par fait.

**Leçon 87.** Une marque interne (« accessoire », « extension ») rangée dans le même champ que les vraies valeurs
finit par s'y mélanger : l'écrire en un seul endroit, et la filtrer partout où le champ se complète.

### 7.74 Le banc de l'assureur B après le lot B : rien ne bouge, et une comparaison trompeuse

**Acceptation** (19 nov., 14 h 45) : 3.1.8, 3.1.9 et 3.2.3 acceptés sans contrôle bloquant ; `couverture regles` :
352 couples du vocabulaire employés, 0 hors vocabulaire, 214 citations retrouvées ; 139 tests passent.

**Banc** (golden v11, 15 cas, lecture vérifiée par Mistral Small) : règles seules 100 % justes ; chaîne 73 % justes,
47 % exactes, **0 couvert à tort, 0 refus à tort**, 0 instable ; un cas à la fois : médiane 4,3 s, 95e centile
5,3 s (les variables de lieu et de pays ne sont lues que pour leur lieu : la lecture ne s'allonge pas).

**La comparaison trompeuse.** Le rapport annonce une baisse (82 % → 73 % justes) : il compare au dernier banc
de l'assureur B, qui avait la confirmation par Mistral Large (7.67). Comparé cas par cas au banc du 18 nov. dans
la même configuration, les décisions sont les mêmes, sauf deux :
- `b-v07` passe d'« incertain » à « couvert sous réserve » des conditions particulières (formules « vol » et
  « matériel multimédia ») : acceptable, et plus utile ;
- `b-v12` (la femme de ménage) était une fois sur trois refusé à juste titre ; il est « incertain » trois fois.

Les quatre erreurs (`b-v02`, `b-v06`, `b-v09`, `b-v12`) sont des « incertain » là où le refus était attendu : la
lecture ne pose pas les faits négatifs que la déclaration ne dit pas (« ni violence », « pas de serrure de
sûreté »), et la question suffit à trancher. Aucune erreur dangereuse. À surveiller : `b-v03`, que la lecture seule
mènerait à « couvert » (bris de vitre lu en trop) ; la chaîne s'arrête sur une question.

**Correction** : le rapport se compare désormais au dernier banc de **même modèle et même lecture**, et nomme
cette configuration dans son titre (`banc.dernier`, test `test_banc_precedent_de_meme_configuration`).

**Leçon 88.** Un écart entre deux bancs ne se lit qu'à configuration égale : le rapport doit nommer celle du banc
auquel il se compare.

### 7.75 Les faits négatifs : la vérification retirait des « non » écrits, et une exclusion mal traduite

**Le constat** (banc 7.74). Les quatre erreurs de l'assureur B sont des « incertain » là où le refus était attendu.
Cas par cas, ce n'est pas la lecture qui manque les faits négatifs : elle les lit, et la **vérification les
retire** comme « non dits » :
- `b-v09` : « une cave fermée par un simple cadenas » ; lu `serrure_surete = non` (l'aide du vocabulaire dit
  « non : cadenas »), retiré ;
- `b-v06` : « on m'a subtilisé mon portefeuille sans que je m'en rende compte » ; lu `violence = non`, retiré ;
- `b-v02` : « aucune effraction, personne n'a été menacé », écrit en toutes lettres, et pourtant perdu dans la
  chaîne (la question « y a-t-il eu effraction ? » est posée).
La consigne de vérification v1 disait seulement « une affirmation plausible mais non écrite est non dit » : le
modèle prenait toute négation pour une supposition.

**Consigne `verification-faits` v2.** Une négation compte comme le reste : « dit » quand elle est écrite en
toutes lettres, ou quand un détail écrit correspond au sens donné entre parenthèses pour la valeur (le
vocabulaire le donne déjà : « non : cadenas, simple loquet » ; « non : aucun contact ni menace, vol à la tire »).
Le contre-exemple de v1 reste : « le local n'était pas fermé » pour « volé dans ma cave » est non dit.

**Une exclusion mal traduite** (`b-v12`, la femme de ménage). Le texte exclut les vols d'une personne au service
de l'Assuré « pendant les heures de service et, si ces vols ont été commis en dehors de celles-ci, autrement que
par effraction ou avec violence ». Deux cas : pendant le service, toujours ; en dehors, sauf effraction ou
violence. La rédaction de 3.1.6 n'avait gardé que le second (il fallait savoir s'il y avait eu violence) ; celle de
3.1.7 excluait le personnel en toute circonstance (un cambriolage avec effraction un jour de congé aurait été
refusé à tort). Nouvelle variable `heures_service` ; les deux exclusions corrigées par
`relecture/assureur_b_personnel.py` ; faits idéaux de `b-v12` complétés (`heures_service = oui` : « pendant
qu'elle travaillait chez nous »). Simulation (oracle) : aucune autre décision du golden ne change ; sans
`heures_service` lue, la réponse reste « incertain » ; effraction hors service, couvert.

**Le risque.** Ces quinze cas ont été écrits par Claude après avoir lu les règles, et les corrections sont
tirées de leurs erreurs : la mesure qui suivra sera optimiste. Les deux corrections sont générales (une consigne
sur les négations, une clause relue contre son texte), mais seul un jeu écrit sans voir les règles dira si elles
tiennent. À vérifier aussi : l'assureur A exclut le personnel en toute circonstance (2.10-a) ; relire son texte.

**Leçon 89.** Un vérificateur trop strict ne fait pas d'erreur dangereuse, mais il ôte au système les « non »
qui permettent de refuser : sa consigne doit dire ce qu'est une négation écrite.

### 7.76 La mesure de la vérification v2 : mieux chez B, un refus à tort de plus chez A

**Assureur B** (golden v12) : chaîne **78 % justes** (73 %), 0 couvert à tort, 0 refus à tort. `b-v02` (« aucune
effraction, personne n'a été menacé ») et `b-v12` (la femme de ménage) sont refusés à juste titre une fois sur
trois, au lieu de jamais ; les autres exécutions restent « incertain » : la lecture de Mistral Small varie d'une
fois à l'autre (2 cas instables).

**Assureur A** : chaîne 87 % justes (88 %), **3,67 couverts à tort** (4), **3 refus à tort** (1,67). Cas par cas,
la plupart des écarts sont l'instabilité habituelle (14 cas instables). Un seul est systématique : `g2-i16`
(« de l'eau de mon appartement s'est infiltrée chez le voisin du dessous ») passe de « couvert » deux fois sur
trois à « refusé » trois fois. La lecture prend « infiltrée » pour `cause_eau = infiltration_exterieure` (la
pluie entrée par un mur, exclue en 2.7-b) ; l'erreur existait avant, mais la vérification v1 retirait parfois le
fait, et la v2, qui accepte un détail écrit correspondant au sens d'une valeur, le garde. L'oracle le confirme :
sans `cause_eau`, couvert ; avec, refusé.

**Correction** : l'aide de `infiltration_exterieure` précise « pas l'eau partie de chez l'assuré qui s'infiltre
chez un voisin ». La vérification v2 rend les erreurs de lecture plus durables, dans les deux sens : un « non »
juste survit, un fait mal lu aussi. Le rôle de la vérification, retirer ce qui n'est pas écrit, ne corrige pas
un fait mal compris ; c'est à l'aide du vocabulaire de le faire.

**Leçon 90.** Assouplir un vérificateur laisse passer les bons faits négatifs et les mauvaises lectures : chaque
assouplissement se mesure sur les refus à tort, pas seulement sur l'exactitude.

### 7.77 L'aide ne suffit pas : la vérification v3 limite la souplesse aux « non »

**Banc** (assureur A, 15 h 51, après l'aide de `cause_eau`) : chaîne 86 % justes, 74 % exactes, 4 couverts à tort,
2 refus à tort, 11 instables ; 95e centile de 21 s (un appel lent du fournisseur ; médiane 3,7 s). `g2-i16` reste
refusé trois fois sur trois : Mistral Small lit toujours `cause_eau = infiltration_exterieure` malgré l'aide, et la
vérification v2 le garde. Les couverts à tort sont ceux d'avant (`red-b06`, `g-p03`, `g2-p08` systématiques ;
`bougie-04`, `val-09` une fois). `val-09` (« sans flammes ») montre aussi que la vérification reste bruitée : le
« non » écrit en toutes lettres y a été retiré une fois.

**Diagnostic.** La v2 voulait garder les négations écrites ; sa seconde phrase (« un détail écrit correspond au
sens donné ») valait pour toutes les valeurs, et le vérificateur s'en est servi pour un fait positif sur un mot
commun (« infiltrée »). **Consigne `verification-faits` v3** : la souplesse ne vaut que pour « non » ; pour toute
autre valeur, le vérificateur doit confronter l'écrit au sens de la valeur et à ce qu'il écarte. L'exemple donné
n'est pas tiré du golden set (une machine à laver, pas l'eau qui passe chez le voisin), pour que `g2-i16` continue
de mesurer quelque chose.

**Le levier suivant**, si la v3 ne suffit pas : la confirmation des faits décisifs par Mistral Large (7.67), qui
ramenait les couverts à tort de 4 à 1,67 au prix d'une médiane de 8,6 s ; l'appliquer aussi aux refus.

**Leçon 91.** Un exemple de consigne tiré d'un cas du jeu d'essai rend ce cas inutile pour la mesure : prendre un
exemple voisin.

### 7.78 La v3 mesurée, et un recours pour les faits retirés à tort

**Banc** (16 h 10, golden v12). **Assureur A** : chaîne **90 % justes**, 76 % exactes, 4,33 couverts à tort,
**0,67 refus à tort** (le plus bas mesuré), 11 instables ; médiane 4,1 s, 95e centile 5,4 s. `g2-i16` revient à
« incertain » (acceptable) : le fait mal lu n'est plus gardé. Les couverts à tort restent les trois systématiques
(`red-b06`, `g-p03`, `g2-p08`) et deux occasionnels (`bougie-04`, `val-09`). **Assureur B** : 76 % justes
(78 % avec la v2, 73 % avec la v1), 0 couvert à tort, 0 refus à tort.

**Ce que la consigne ne règle pas.** Chez B, `b-v06` et `b-v09` restent « incertain » trois fois sur trois : le
rapport montre que la vérification par Mistral Small retire toujours `serrure_surete = non` (« un simple
cadenas »), `violence = non` (« sans que je m'en rende compte »), et même `auteur = personnel_prive` (« la femme de
ménage »), malgré la v3 qui les donne en exemple. Le petit modèle, en vérificateur, est prudent au-delà de ce
qu'on lui demande ; trois versions de consigne n'y changent plus grand-chose.

**Le recours** (`prolog.rappeler`). Après la vérification, les faits retirés qui, rétablis, **changeraient la
décision** (le moteur le dit en quelques millisecondes) sont soumis à un second avis, celui du modèle de
confirmation (Mistral Large, `COUVERTURE_MODELE_CONFIRMATION`) ; ceux qu'il trouve écrits sont rétablis. C'est le
pendant de la confirmation (7.49, 7.67) : la confirmation vérifie les faits qui portent une réponse ferme, le
recours ceux dont l'absence l'empêche. Il ne coûte qu'un appel, et seulement dans ces cas-là. Sans modèle de
confirmation distinct, pas de recours : le même petit modèle redirait la même chose. Test :
`test_recours_retablit_un_fait_retire_qui_tranche`.

**Leçon 92.** Quand trois versions d'une consigne ne changent plus le comportement d'un petit modèle, ce n'est
plus la consigne qu'il faut changer, c'est qui décide : un second avis plus fort, réservé aux faits qui comptent.

### 7.79 Un jeu fermé, écrit sans voir les règles, par deux annotateurs à l'aveugle

**Le problème.** Le golden set a été écrit par Claude après avoir lu les règles, et ses faits idéaux sont dans
le vocabulaire des règles : « règles seules 100 % » dit que le moteur applique les règles, pas que les règles
disent le contrat. L'exclusion du personnel mal traduite (7.75) passait à 100 %. Il faut des cas dont la réponse
vient du seul texte du contrat. L'auteur du projet n'est pas du métier : écrire ces cas lui-même n'aurait pas
donné une meilleure référence.

**La méthode** (`src/couverture/ferme.py`, `data/ferme/`).
1. *Premier annotateur* : un agent Claude neuf, qui n'a lu que le texte des deux CG (extrait des PDF, noms
   d'assureurs remplacés) ; ni règles, ni golden set, ni cette conversation. 40 cas (20 par assureur, environ
   7 couverts, 7 refusés, 6 incertains chacun), plusieurs garanties, des pièges, 6 cas de responsabilité civile,
   d'assistance ou de protection juridique (non traduites : le système doit dire « incertain »). Chaque réponse
   avec l'article et une citation mot pour mot, vérifiée.
2. *Second annotateur* : Mistral Large, les mêmes déclarations et le texte entier du contrat, sans la première
   réponse (`python -m couverture.mesure.ferme annoter`).
3. *Accords et arbitrage* : une réponse identique, ou acceptée par l'autre, entre dans le jeu ; un désaccord va
   dans `arbitrage.csv`, avec les deux citations, pour un arbitrage sur le texte (`comparer`, `exporter`).
4. *Banc* : `couverture banc --jeu ferme`, chaîne complète seule (pas de faits idéaux, qui remettraient le
   vocabulaire des règles dans le jeu) ; comparé aux bancs de même jeu.

**Convention** (posée par le premier annotateur, reprise dans la consigne du second) : garanties de base
souscrites, options et formules inconnues. Chez l'assureur B, chaque garantie n'existe que si les conditions
particulières la mentionnent : sans cette convention, presque tout serait « incertain ».

**Doutes signalés par l'annotateur** : le gel avec chauffage coupé (indemnité réduite ou refus ?), la fuite
chez le voisin (recours des tiers ou exclusion de l'eau en RC ?), quatre mois d'absence contre 110 nuits, le
serrurier (assistance supposée appelée ?). Le second avis dira lesquels sont vraiment ambigus. Un cas
(`f-b12`, la machine à laver qui abîme le plafond du voisin) ressemble à l'exemple de la consigne de
vérification v3 (7.77) : coïncidence (l'agent n'a pas vu la consigne), à garder en tête en lisant son résultat.

**Ce que ce jeu vaut** : deux lectures indépendantes du texte, désaccords arbitrés sur citations ; ce n'est pas
l'avis d'un gestionnaire de sinistres. Une relecture des cas litigieux par quelqu'un du métier le renforcerait.

**Leçon 93.** Pour mesurer la fidélité des règles au contrat, la référence ne doit rien devoir aux règles :
ni l'auteur des cas, ni leur vocabulaire.

### 7.80 Confirmation et recours par Mistral Large : la meilleure justesse, le temps en plus

**Banc** (golden v12, `COUVERTURE_MODELE_CONFIRMATION=mistral-large-latest`, vérification v3, recours 7.78).

| | sans Large (16 h 10) | confirmation seule (10 h 30, 7.67) | confirmation + recours |
|---|---|---|---|
| A : justes | 90 % | 86 % | 89 % |
| A : couverts à tort | 4,33 | 1,67 | **1,33** |
| A : refus à tort | 0,67 | — | 1,33 |
| A : médiane, 95e centile | 4,1 s, 5,4 s | 8,6 s | 8,1 s, 106 s |
| B : justes | 76 % | 82 % | **100 %** |
| B : médiane, 95e centile | 3,9 s, 5,9 s | — | 22,6 s, 38 s |

Chez B, le recours fait ce pour quoi il est fait : les « non » retirés par Mistral Small (le cadenas, le vol à
l'insu, la femme de ménage) sont rétablis par Mistral Large, et les quatre « incertain » deviennent des refus
justes. Chez A, la confirmation ramène les couverts à tort de 4,33 à 1,33 ; les refus à tort restent bas.

**Le prix** : un ou deux appels à Mistral Large par cas qui tranche, chacun de plusieurs secondes (le modèle
réfléchit) ; la médiane passe de 4 à 8 s (A) et à 23 s (B, où presque chaque cas appelle le recours puis la
confirmation, l'un après l'autre). Le 95e centile de A (106 s) vient des limites de débit de l'API quand quatre
cas tournent à la fois. La porte de latence (≤ 10 s) échoue.

**Lecture** : le petit modèle lit, le grand tranche sur les seuls faits qui comptent ; la justesse vient du grand.
Prochaines pistes, pour le temps : appeler le recours et la confirmation ensemble, en un seul appel, quand le
moteur peut dire d'avance quels faits seront décisifs ; un modèle intermédiaire (Mistral Medium) pour ce rôle.

### 7.81 Le jeu fermé : la première mesure de la fidélité au contrat

**Arbitrage** (7.79). 36 accords sur 40 entre les deux annotateurs ; les 4 désaccords ont la même forme :
Mistral Large lit la garantie et oublie la condition qui l'accompagne (une serrure de sûreté, un délai de 30 jours
après un déménagement, une assistance à appeler, une option). Arbitrés par Claude sur les citations, en faveur
de l'agent (« incertain »), validés par l'auteur.

**Banc** (chaîne complète, sans Mistral Large). **Assureur A : 70 % justes**, 3 couverts à tort, 0,33 refus à
tort. **Assureur B : 57 % justes**, 0 couvert à tort, 1,33 refus à tort. À comparer aux 90 % et 76 % du golden
set : l'écart est la mesure de ce que le golden set ne voyait pas.

**Les erreurs, classées** (les 6 et 13 cas en erreur au moins une fois sur trois) :

| Cause | Cas | Effet |
|---|---|---|
| **Garantie non traduite, répondue « refusé »** | f-a18 (vélo contre piéton), f-a20 (serrurier), f-b16 (morsure de chien), f-b19 (violon, option Confort) | refus au lieu d'« incertain » |
| **Règle fausse : une réduction traduite en refus** | f-b02 (gel, chauffage coupé : indemnité réduite de moitié) ; même forme en 3.1.6.4 (protections antivol) | refus à tort |
| **Règle incomplète : le gel n'est pas une fuite pour B** | f-b02 (« conduite gelée et éclatée » lue `cause_eau = gel`, absente de la garantie de B) | refus à tort |
| Clause de vie du contrat non traduite | f-a17 (déménagement non déclaré dans les 30 jours) | couvert au lieu d'« incertain » |
| Lecture | f-a11 (vase lu vitre), f-a13 (ordinateur de l'employeur non lu professionnel), f-a14 (store banne), f-b05, f-b17 (remise lue jardin) | couverts à tort (A), refus |
| Faits négatifs retirés (sans recours) | f-b06 (porte ouverte) | « incertain » |
| Garantie mal rattachée, à examiner | f-b01 (braise sur le tapis, « substance incandescente » 3.1.1.1.6), f-b03 (pluie par une fenêtre de toit), f-b04 (moisissure) | « incertain » au lieu d'une réponse |

**Le plus important** : quand un sinistre relève d'une garantie non traduite (responsabilité civile, assistance,
option), le moteur concluait « aucune garantie ne s'applique » et **refusait**. Le système n'était donc pas
honnête là où on le croyait ; le golden set ne le montrait pas, parce que ses cas de responsabilité civile y
étaient rares. Le mécanisme existait pourtant (règle 8 du moteur : un événement non traduit plafonne la réponse à
« incertain ») ; il manquait les événements. Deux valeurs ajoutées à `evenement` : `responsabilite` (un dommage
causé à quelqu'un d'autre, qui en demande réparation) et `assistance` (un dépannage, sans dommage à
indemniser). Aucun contrat ne les traduit encore : la réponse est « incertain », et deviendra une vraie réponse le
jour où la responsabilité civile sera traduite.

**Corrections générales** :
- *Rédaction v11* : une sanction qui réduit l'indemnité est une limite, pas une obligation ; contrôle bloquant
  quand la clause d'une obligation réduit sans refuser (`test_une_reduction_d_indemnite_n_est_pas_une_obligation`).
- *Assureur B* (`relecture/assureur_b_reductions.py`) : 3.1.4.3 (gel) et 3.1.6.4 (protections antivol) passent
  d'obligation à limite.
- *Vocabulaire* : `cause_eau = gel` a pour parent `fuite_installation` (une conduite qui gèle et éclate est une
  rupture d'installation), ce qui la fait entrer dans la garantie dégâts des eaux de B ; sans effet sur A, qui ne
  nomme le gel que pour l'exclure sans prévention.
- Oracle : aucune décision du golden set ne change (règles seules, A et B) ; le gel de f-b02 devient couvert.

**Règle de méthode.** Les cas f-b02, f-a18, f-a20, f-b16, f-b19 ont servi à corriger : ils deviennent des cas
de mise au point. La prochaine mesure honnête demandera un second jeu fermé, écrit de la même façon.

**Leçon 94.** Un jeu de cas écrit en voyant les règles ne trouve pas les trous des règles : le moteur refusait
la responsabilité civile, non traduite, depuis le début, et seul un jeu écrit sans les règles l'a montré.

### 7.82 Le jeu fermé après les corrections

**Banc** (17 h 58). **Assureur A : 77 % justes** (70 %), 1,67 couvert à tort (3), 0 refus à tort (0,33).
**Assureur B : 62 % justes** (57 %), 1 couvert à tort (0), 1 refus à tort (1,33). Mesure **optimiste** : f-a18,
f-a20, f-b02 et f-b16 ont servi à corriger et passent désormais (dix points sur vingt cas, à peu près).

**Ce qui a changé, cas par cas.**
- Garanties non traduites : le piéton renversé (f-a18), le serrurier (f-a20), la morsure du chien (f-b16) et la
  tondeuse empruntée (f-a19) répondent « incertain » ; ce dernier devient une erreur (le texte l'exclut, mais la
  responsabilité civile n'est pas traduite), une erreur prudente.
- Le gel (f-b02) est couvert, avec la réduction de moitié en limite.
- **Nouveau couvert à tort, f-b13** : « ma chaudière s'est mise à fuir ; j'ai appelé l'assistance » deux semaines
  après la souscription. La demande porte sur l'intervention (soumise à un délai d'attente de 30 jours), mais la
  lecture y voit aussi un dégât des eaux, que la garantie couvre ; et le moteur garde « couvert » quand une
  garantie traduite joue, même si un événement non traduit (l'assistance) est lu. Règle du moteur à rediscuter :
  « couvert » sur une partie du sinistre n'est pas « couvert » sur la demande.
- Restent : le déménagement non déclaré (f-a17, clause de vie du contrat), les lectures (vase, store, remise),
  le vol à la porte ouverte (faits négatifs, sans recours), la braise, la fenêtre de toit, la moisissure, le violon.

### 7.83 Trois trous des règles de l'assureur B, trouvés par le jeu fermé

- **La braise sur le tapis** (f-b01). 3.1.1.1.6 couvre les dégâts « par l'action subite de la chaleur ou par le
  contact direct et immédiat avec un foyer ou une substance incandescente, même lorsqu'il n'y a pas eu
  embrasement ». La règle ne connaissait que la chaleur seule, et exigeait, pour un événement lu « incendie », un
  incendie au sens de 3.1.1.1.1 (des flammes) : la braise n'était ni l'un ni l'autre. Nouvelle variable
  `contact_incandescent` ; la circonstance accepte désormais l'incendie, la chaleur seule ou le contact.
- **La moisissure** (f-b04). « Par des champignons ou des moisissures, même consécutivement à un sinistre
  couvert » (3.1.4.2.12, et 3.2.2.4) avait été traduit par `cause_eau = condensation`, la condition d'une autre
  exclusion : une moisissure après une fuite restait couverte. Nouvelle valeur `type_dommage = moisissure`.
  Même défaut que l'exclusion du personnel (7.75) : une exclusion rattachée à la condition de sa voisine.
- **La pluie par une fenêtre de toit** (f-b03). La règle était juste (3.1.4.2.6 exclut l'eau de pluie entrée par
  une ouverture, `infiltration_exterieure`) ; l'aide du vocabulaire ne disait pas qu'une fenêtre de toit est une
  ouverture, et la lecture pouvait choisir `infiltration_toiture`, couverte. Aides précisées.

Correction : `relecture/assureur_b_jeu_ferme.py` (3.1.1, 3.1.4, 3.2.2) ; vocabulaire. Oracle : aucune décision du
golden set ne change ; braise couverte, moisissure refusée, fuite simple couverte.

**Leçon 95.** Une exclusion peut citer le bon texte et porter la condition de sa voisine : le contrôle des
citations ne le voit pas ; seul un cas qui la met à l'épreuve le montre.

### 7.84 Deux décisions sur ce que le moteur ne sait pas (décidées avec l'auteur)

**Un événement non traduit plafonne aussi un « couvert ».** Jusqu'ici (règle 8 du moteur), un événement lu dont
la garantie n'est pas traduite empêchait un refus, mais laissait passer un « couvert » si une garantie traduite
jouait. f-b13 (« ma chaudière fuit, j'ai appelé l'assistance », deux semaines après la souscription) l'a montré :
le dégât des eaux était couvert, alors que la demande portait sur le dépannage, soumis à un délai d'attente.
Couvrir une partie du sinistre n'est pas couvrir la demande : la réponse est désormais « incertain », « à examiner
par un gestionnaire », avec ce que disent les garanties traduites. Choix de l'auteur, le plus prudent ; prix :
quelques « couvert » justes deviendront « incertain » quand la lecture ajoute un événement de trop. Moteur Prolog,
oracle et test (`test_evenement_non_traduit_jamais_refuse`) changés ensemble.

**La casse accidentelle.** f-b19 (un violon tombé de son pupitre) : chez l'assureur B, une casse accidentelle
relève d'une option non traduite (« dommages aux biens », formule Confort), et le moteur refusait. Nouvelle valeur
`evenement = accident` (chute, choc, objet renversé), de parent `heurt` : chez l'assureur A, le pack multimédia
(6.1, traduit sur le heurt) continue de couvrir l'ordinateur tombé, et le contrat ne garantit pas d'autre casse :
`evenement_traduit(accident)` y est déclaré (question examinée, le vase cassé reste refusé). Chez B, rien ne la
traduit : « incertain ».

Oracle : aucune décision du golden set ne change (A et B) ; violon « incertain » (B), ordinateur tombé couvert et
vase refusé (A), chaudière « incertain » (B).

### 7.85 Le banc après 7.83 et 7.84 : la valeur « accident » prenait la place de « bris »

**Banc** (18 h 10 à 18 h 25, sans Mistral Large). Jeu fermé : A 73 % justes (2 couverts à tort, 1 refus à
tort) ; B 60 % (0 couvert à tort, 0,67 refus à tort), sans la correction de 3.1.1, refusée par le contrôle (voir
plus bas). Golden set : **B 82 % justes** (76 %), 0 couvert à tort, 0 refus à tort ; **A 86 % justes, 4,33 refus
à tort** (0,67 à 16 h 10).

**Ce qui a fait monter les refus à tort chez A.** Cas par cas, trois bris de vitre accidentels (`red-b01`,
`red-b02`, `red-b05` : une vitre cassée par un enfant, par l'assuré) sont désormais lus `evenement = accident`
au lieu de `bris` : la garantie bris de vitrages ne se reconnaissait plus, et l'assureur A ayant déclaré la casse
accidentelle « examinée », la réponse devenait « refusé ». Les autres écarts sont l'instabilité habituelle de la
lecture. Correction : `accident` a pour parents `heurt` **et** `bris` (une vitre cassée par accident reste un bris
de vitrage pour les règles), et l'aide de la valeur renvoie les vitres, miroirs et verres à « bris ». Oracle : les
trois cas, lus « accident », redeviennent couverts ou refusés à juste titre ; aucune décision du golden set ne
change.

**Le contrôle de 7.81 trop large.** Il a refusé 3.1.1 : l'obligation de déclaration des attentats (3.1.1.2)
partage sa clause, longue, avec une réduction d'indemnité sans rapport. Il ne regarde plus que la sanction qui
suit le devoir (les 400 caractères après la phrase citée).

**`couverture regles`** échouait pour l'assureur A (`tableau` introuvable) : la fonction avait été retirée comme
code mort lors du tour du code (7.70), alors qu'elle servait encore. Rétablie.

**Leçon 96.** Une nouvelle valeur du vocabulaire peut voler les lectures d'une valeur existante : la rattacher à
celles dont elle peut prendre la place, et la mesurer sur le golden set avant le jeu fermé.

### 7.86 Après 7.85 : les refus à tort de A redescendent ; « accident » précisé en « bris » par le code

**Banc** (19 h 30, sans Mistral Large). Golden set A : 88 % justes, **1,33 refus à tort** (4,33 à 18 h 23),
5,33 couverts à tort (4,33 à 16 h 07 ; `red-b05`, le miroir pas encore accroché, couvert parce que la lecture
ne dit pas qu'il n'était pas posé ; le reste est l'instabilité connue). Jeu fermé B : 63 % justes (60 %),
1,33 couvert à tort ; la braise (f-b01) et la moisissure (f-b04, une fois sur trois) passent.

**Ce que la lecture fait encore de « accident ».** f-b08 (« j'ai cogné le miroir avec le manche de l'aspirateur »)
est lu `accident` malgré l'aide qui renvoie les vitres à `bris` ; chez l'assureur B, où la casse accidentelle
n'est pas traduite, la réponse tombe à « incertain » (7.84) au lieu de « couvert ». L'aide ne suffit pas : c'est
le code qui tranche. Nouvelle clé du vocabulaire, `preciser` : une valeur vague remplacée par la précise quand un
autre fait la désigne ; `evenement = accident` sur un bien en verre (vitre, miroir, vitrocéramique, sanitaire,
verre de meuble…) devient `bris` (`prolog.preciser`, appelé par `au_vocabulaire` ;
`test_accident_sur_une_vitre_est_un_bris`). Le violon tombé reste un accident.

Restent en erreur dans le jeu fermé B : la fenêtre de toit (la lecture voit une tempête), la porte ouverte (faits
négatifs, sans recours), la chaudière et l'assistance (« incertain », voulu), le congélateur de 18 ans, la remise
du jardin, la voiture à la gare (f-b18, couvert à tort : à examiner), le double vitrage embué.

### 7.87 Un troisième contrat (assureur D) : d'abord le lire correctement

**Pourquoi D et pas C.** Le plan prévoyait l'assureur C ; son PDF demande un profil lourd (7.51 : numéros de page
pris pour des numéros d'article, titres aux lettres espacées). D était noté « OK » à l'ingestion de 7.51 : c'est
lui qu'on traduit, pour mesurer ce que coûte un contrat de plus.

**« OK » ne voulait pas dire « bien lu ».** Les 207 clauses de D portaient des identifiants de section
(« S19 », « S20 ») et non les articles du contrat (« ART 2-5 Vol »), et leur texte mêlait deux colonnes :
pdfplumber lit la page ligne à ligne, d'un bord à l'autre (« ART 2.3 Tempête, grêle, avalanche, neige sur • de
débordements et renversements de récipients »). Impossible de rédiger ou de citer un article dans ces conditions.
Le contrôle d'ingestion ne vérifiait que la forme (types, renvois), pas que les clauses suivent les articles.

**Trois corrections générales**, activées par le profil d'assureur (`data/profils/assureur-d.json`), sans effet sur
A ni B (découpage comparé avant et après : identique, 147 et 293 clauses) :
- *Lecture en colonnes* (`"colonnes": 2`, `chargement._deux_colonnes`) : la gouttière est la verticale, entre 40 et
  60 % de la largeur, que le moins de mots traversent ; une page où plus de 3 % des mots la traversent est lue
  d'un bloc ; un titre sur toute la largeur coupe la page en bandes, chaque bande lue colonne gauche puis droite.
- *Articles « ART 2-7 »* : « ART » sans point et des numéros à tirets (ramenés à « 2.7 ») ; la lettrine détachée
  des titres (« C atastrophes » → « Catastrophes »). `"titres_numerotes": "articles"` : seuls les « ART n » ouvrent
  une clause, pas les « 1 Panne d'un appareil » des listes.
- *Lexique en capitales* : sous « Les définitions », un terme en capitales (« DOMMAGE CORPOREL », « FRANCHISE »)
  est un terme, pas un titre (41 définitions au lieu de 7).
- Le profil saute aussi les tableaux récapitulatifs (pages 11 à 23, numérotés « 1 », « 2.1 »… comme des articles)
  et les lignes de sommaire (« Pack Jardin p 34 »).

Résultat : 267 clauses, rangées par article (2.5-a « Ce que nous garantissons », 2.5-c « Ce qui est exclu »…).
Tests : `test_deux_colonnes_lues_colonne_par_colonne`, `test_articles_a_tirets_lettrine_et_lexique_en_capitales`,
`test_profil_colonnes_pages_et_articles`. Fichier de règles vide `regles/assureur-d-habitation-2026.pl`.

**Le jeu fermé d'abord.** Avant toute règle, un agent neuf écrit 25 cas à partir du seul texte de D (extrait en
colonnes, noms anonymisés), comme en 7.79 : cette fois, le jeu est écrit avant les règles, et aucun de ses cas ne
servira à les corriger avant la mesure.

**Leçon 97.** Un statut « OK » d'ingestion qui ne regarde que la forme laisse passer un contrat illisible : il faut
regarder, pour quelques articles, si le texte de la clause est bien celui de l'article.

### 7.88 Assureur D ingéré ; un incident ; les exclusions générales dans la rédaction

**Ingestion** (20 nov.) : D « OK », 267 clauses comme prévu (41 définitions, 47 garanties, 43 exclusions) ; A et B
inchangés (147 et 293 clauses).

**Incident.** `SOURCES.prive.md`, le fichier des vrais noms (7.70), rangé avec les contrats, a été ingéré comme
un contrat (« sources-prive », 1 clause). La base n'est pas versionnée (`.gitignore`) : rien n'est sorti du poste.
L'ingestion ignore désormais tout fichier `sources*` ; la base reflétant le dossier, la prochaine ingestion le
retire.

**Les exclusions générales.** Chez A, elles avaient été écrites à la main (1.4) ; chez B, elles ne sont pas
traduites. La rédaction ne savait pas les produire : un article sans garantie était refusé (« aucune garantie
proposée ») et ses exclusions communes n'auraient visé personne. Le moteur connaissait pourtant la cible `tous`.
*Rédaction v12* : un article d'exclusions générales (titre IX de D, « S25 ») se rédige sans garantie, et ses
exclusions visent `tous` (test `test_article_d_exclusions_generales_vise_toutes_les_garanties`). À faire ensuite
pour B, par la même voie.

**Plan de rédaction de D.** (1) les biens assurés (1.1 à 1.5 : les concepts du bâtiment et du contenu, dont les
garanties ont besoin) et les exclusions générales (S25) ; (2) les dommages (2.1 à 2.13) ; (3) les mesures de
sécurité (4, des réductions d'indemnité et non des refus, 7.81) et les frais (3, accessoires) ; les packs et les
responsabilités ensuite. Mesures à chaque lot : temps de rédaction, nombre de contrôles bloquants, corrections
à la main.

### 7.89 Assureur D, lot 1 : ce que coûte un contrat de plus (premières mesures)

**Second avis du jeu fermé de D** : 25 cas ; 24 accords (dont un souple), 1 désaccord. `f-d23` (l'eau traverse la
façade d'une maison « que nous avons fait construire ») : Mistral Large répond « refusé » (la garantie décennale du
constructeur) ; l'agent, « incertain » : la décennale ne joue que dix ans, et l'âge de la maison n'est pas dit.
Arbitré pour l'agent, sur la citation.

**Rédaction du lot 1** (biens assurés 1.1 à 1.5, exclusions générales « S25 » ; 6 articles, 3 à la fois) :
11 min 15 s, **80 contrôles bloquants**. La relecture (`relecture/assureur_d_lot_1.py`) a réécrit presque tout :
- *Les concepts* : le modèle inventait `bien_immobilier`, `dependances`, `depreciation_collection`, et étendait un
  concept `bien` qui n'existe pas. Comme chez A : `batiment` (les lieux : le logement, ses dépendances) et
  `contenu` (les biens mobiliers qui s'y trouvent).
- *Les exclusions de biens* (vérandas, éoliennes, piscines, véhicules, animaux…) excluaient tout le sinistre :
  elles n'excluent que le bien (portée `bien`). Leurs exceptions (option, pack, formule) restent en réserve.
- *Les exclusions générales* : celle du tremblement de terre excluait l'événement « catastrophe naturelle », donc
  la garantie qu'elle épargne expressément ; retirée (aucune autre garantie ne couvre ces phénomènes). Aucune
  n'est demandée à l'assuré.
- 1.3 et 1.4 (objets de valeur, véranda : des options) ne sont pas acceptés seuls ; leurs exceptions sont portées
  par les exclusions de 1.1 et 1.2.
Après relecture : 0 contrôle bloquant hors vocabulaire (16 valeurs nouvelles à accepter).

**Un contrôle trop bavard.** Le lexique de D définit « NOUS » et « VOUS » ; chaque garantie s'intitule « Ce que
nous garantissons » ; le contrôle « définition de l'événement couvert non traduite » se déclenchait à chaque
article. Les pronoms sont ignorés.

**Ce que le lot dit du coût.** Les articles de définition des biens sont les plus durs pour le modèle : ils
fixent les concepts que tout le reste emploie, et il les invente. C'est là que la relecture humaine compte le
plus ; les garanties (lot 2) devraient demander moins, si les concepts sont bons.

### 7.90 Lot 1 accepté en deux fois ; des variables qui ne doivent jamais être lues

**Acceptation.** 1.1 et S25 acceptés. 1.2 et 1.5 refusés : « concept inconnu : batiment / contenu ». Le contrôle
lit les concepts du contrat *avant* l'acceptation du lot : `batiment` naît en 1.1, `contenu` en 1.2. Pas un
défaut des règles, un ordre : accepter 1.2 (maintenant que 1.1 est écrit), puis 1.5.

**Le temps 2 de la lecture s'allongeait** (test `test_lecture_en_deux_temps` : 7 872 caractères pour moins de
7 706 permis). Les variables nées d'articles sans garantie (les biens assurés, les exclusions générales) n'ont pas
d'événement, donc pas de « pour » : l'option véranda, le pack piscine, la rixe, la guerre étaient demandées pour
chaque vol de vélo. Or elles ne servent qu'à des exclusions que l'assureur prouve (« à demander » faux) : la
réserve suffit, il n'y a rien à lire. Elles reçoivent `pour: ["jamais"]`, et la lecture les ignore ; la rédaction
le fait d'elle-même pour un article sans garantie.

Même cause, autre effet : l'extension de 1.5 (« sauf les objets précieux ») déclenchait la lecture du pays et du
séjour temporaire pour tout vol de bijoux. Un bien sous un « non » n'entame pas une extension ; seuls les faits
positifs la déclenchent.

**Lot 2 rédigé** (garanties 2.1 à 2.13) : 13 articles en 14 min 01 s, 99 contrôles bloquants (de 0 pour 2.13 à
18 pour 2.5) ; à relire avant toute acceptation.

### 7.91 Assureur D, lot 2 relu : les garanties, et un concept qui se mordait la queue

**Relecture** (`relecture/assureur_d_lot_2.py`) : 12 articles sur 13 réécrits ; 2.10 (catastrophes technologiques)
n'est pas traduit, l'événement manque au vocabulaire et reste « à examiner ». Ce que le modèle faisait mal, et que la
relecture a corrigé :
- *Les concepts* : `contenu` redéfini (« SUBIS PAR VOS BIENS »), un concept par événement, `dependances`,
  `objets_precieux`, `bris_glaces` inventés. Les garanties emploient `batiment` et `contenu` du lot 1.
- *Les formules* : « uniquement pour les formules Confort et Excellence » va dans le périmètre (formule inconnue :
  incertain, la convention du jeu fermé) ; « les vols dans les dépendances, si formule Eco » est à demander.
- *Le vol* : « effraction ou escalade, menaces, vol des clés, fausse qualité » était une disjonction de cinq faits
  oui/non ; un seul inconnu rendait incertain le vol sans effraction (porte non verrouillée), que le contrat refuse.
  Une variable `acces_voleur` à plusieurs valeurs, avec `effraction` qui existait : le refus redevient possible.
- *Les valeurs nouvelles* : le modèle en proposait six pour `cause_eau` ; elles auraient pris les lectures de A et
  B (leçon 96). Les causes de D sont rapportées aux valeurs existantes. Au total, 10 variables nouvelles, aucune
  valeur nouvelle d'une variable existante.
- *Ce qui excluait trop* : « les frais de réparation de l'élément à l'origine du dommage » refusaient tout le dégât
  des eaux (c'est le tuyau qui n'est pas payé) ; 2.13 (intervention des secours) déclarait traduits tous les
  événements, responsabilité civile comprise, qui aurait été refusée au lieu d'être incertaine.
- *Les renvois aux mesures de sécurité* (« voir ART. 4.1 ») ne bloquent plus : elles seront traduites avec le
  titre IV.

**Un concept défini par lui-même.** L'extension de 1.5 (les biens emportés en vacances) élargit le `batiment` pour
le `contenu` ; or le `contenu` est défini « dans le `batiment` ». Le premier cas de vol essayé a fait boucler
l'oracle sans fin (Prolog aurait fait de même). Aucun contrôle ne le voyait : chaque concept était connu. Un
contrôle bloquant cherche désormais les cycles entre définitions et extensions ; 1.5 écrit les biens en faits.

**Une option lue malgré « jamais »** : le Pack Jardin, employé par la tempête, recevait « lue pour la tempête ».
Une variable « jamais » le reste.

**Mesure, sans modèle** : les 25 cas du jeu fermé de D, avec des faits écrits à la main, passés à l'oracle : 22 sur
23 hors responsabilité civile et assistance (non traduites, incertaines comme attendu). L'écart, `f-d20`
(congélateur après une coupure) : les deux annotateurs le rangent dans les « + de la formule Excellence », le texte
ingéré ne le dit pas (la page du tableau des formules est parmi les pages ignorées). Laissé tel que le texte le dit.
Ce n'est pas le banc : la lecture des déclarations par Mistral reste à mesurer (`couverture banc --jeu ferme`).

**Coût du lot 2** : 14 min de rédaction, 99 contrôles bloquants ; relecture humaine (avec Claude) de tous les
articles. Comme au lot 1, le modèle écrit des règles plausibles mais presque toutes à reprendre : le gain est dans
la structure (articles découpés, citations vérifiées, exclusions toutes comptées), pas dans les conditions.

### 7.92 Un premier banc de D à moitié chargé ; le tableau des formules, lu comme un tableau

**L'acceptation s'est arrêtée à 1.2.** Sa proposition gardait les contrôles faits avant que 1.1 ne soit écrit
(« concept inconnu : batiment ») ; `--accepter` lit les contrôles enregistrés, il fallait d'abord `--controler`.
Faute de 1.2, le concept `contenu` manquait, et 8 des 12 garanties du lot 2 ont été refusées ; seules 2.6, 2.7, 2.8
et 2.13 sont entrées. Le banc lancé dans la foulée mesure donc un contrat à moitié traduit : **45 % justes** (chaîne
complète, jeu fermé, Mistral Small), 0 couvert à tort, 1 refus à tort. Il n'est pas retenu comme mesure de D.

**Le tableau des formules.** À l'ingestion, les pages 11 à 23 de D sont sautées : lues comme du texte, leurs
lignes numérotées « 2.1 », « 2.5 » se confondaient avec les articles (7.88). Mais la page 11, « Garanties selon les
formules », dit ce qu'aucun article ne dit : le contenu du congélateur n'est garanti qu'en formule Excellence
(`f-d20`, que les deux annotateurs avaient vu et pas le système). Elle est maintenant lue à part, comme un tableau :
- `couverture formules --contrat … --page 11` lit les mots avec leur position, trouve la ligne d'en-tête (Eco,
  Confort, Excellence) et rattache chaque « X » ou « option » à la colonne la plus proche (`tableaux.py`). 37 lignes,
  écrites dans `regles/formules/<contrat>.json` avec la page source.
- Le relecteur relie chaque ligne aux garanties des règles (« correspondance », conservée si on relit le tableau).
- `couverture regles` vérifie qu'aucune garantie ne joue, dans les règles, pour une formule que le tableau ne lui
  donne pas. La règle peut être plus étroite (le vol des clés n'est que pour Confort et Excellence, par l'article),
  jamais plus large. Sur les règles de D, le contrôle a trouvé le congélateur, et lui seul.

**La formule est une circonstance, pas un terme du périmètre.** Une fois la formule Excellence ajoutée au
périmètre du congélateur, l'oracle a refusé le cas au lieu de le dire incertain : une garantie au périmètre inconnu
n'est que « possible », et le refus d'une garantie retenue l'emporte (le contenu des appareils est exclu des
dommages électriques). C'est voulu par le moteur (une garantie hors sujet n'empêche pas de refuser), mais une
formule inconnue ne dit pas que la garantie est hors sujet. En circonstance, la garantie est retenue, incertaine
tant que la formule n'est pas dite. Les six garanties de D liées à une formule sont réécrites ainsi.

Oracle, faits écrits à la main : 23 sur 23 (hors responsabilité civile et assistance, non traduites).

### 7.93 Le premier vrai banc de D : 67 %, et ce qui reste à voir

Lot 1 et lot 2 acceptés (1.2 cette fois contrôlé avant), `couverture regles` en ordre, « Tableau des formules :
0 écart ». Banc sur le jeu fermé de D (25 cas, chaîne complète, Mistral Small, lecture vérifiée, 3 passages) :
**67 % justes**, 1 couvert à tort, 0 refus à tort, 1 instable, médiane 3,5 s par cas. C'est la première mesure d'un
contrat entièrement traduit par le modèle et relu, sans un seul cas de mise au point (A et B ont été réglés sur
leur jeu d'essai).

Les 8 erreurs :
- *Non traduit* (3) : `f-d09` et `f-d15` (responsabilité civile), `f-d16` (protection juridique) : « incertain »,
  comme prévu tant que le lot 3 n'est pas fait.
- *Couvert à tort* (1) : `f-d19`, la foudre tombée sur un poteau électrique de la rue. La garantie incendie couvre la
  foudre « y compris aux installations électriques », mais par l'impact direct ; ici c'est une surtension, qui
  relève des dommages électriques (Confort et Excellence). La relecture ajoute à 2.1 : foudre et électricité lues
  ensemble, l'appareil relève de 2.2. Oracle : foudre seule → couvert ; foudre et électricité → incertain.
- *Incertain au lieu d'une réponse* (3) : `f-d05` (porte forcée, rien volé), `f-d06` (vol avec effraction pendant les
  vacances), `f-d18` (porte non verrouillée). Les règles donnent la bonne réponse sur des faits écrits à la main :
  l'écart est dans la lecture ou dans la confirmation des faits décisifs (lecture « vérifiée »), et le banc ne
  gardait pas les faits lus. Il les garde désormais (`faits_lus` et `avertissements` par cas, dans le JSON du banc).
- *Refusé au lieu d'incertain* (1) : `f-d23`, l'infiltration dans une maison « que nous avons fait construire »,
  refusée trois fois : le modèle a lu « moins de dix ans » dans « fait construire ». L'aide de la variable dit
  désormais que « fait construire » ne dit pas quand.

### 7.94 Le banc garde les faits lus : trois erreurs de lecture, trois corrections

Second banc de D après 7.93 : **71 % justes**, 0 couvert à tort, 0,33 refus à tort, 2 instables. Le banc garde
maintenant ce que le modèle a lu ; les erreurs se lisent au lieu de se deviner :
- `f-d05` (porte forcée, rien volé) et `f-d06` (vol avec effraction) : le modèle lit **`intentionnel = oui`** pour
  tout vandalisme et tout vol : le voleur agit exprès. Mais l'exclusion générale vise les dommages causés
  intentionnellement « par vous ou par un complice ». Selon que la confirmation retenait ou non ce fait, la réponse
  était « incertain » ou un refus. L'exclusion de S25 ne joue plus quand l'auteur lu est un tiers.
- `f-d18` (porte non verrouillée, aucune trace) : le modèle lit `acces_voleur = sans_effraction`, la vérification
  retire `effraction = non` (« non dit »), et le vol reste incertain. Une clé nouvelle du vocabulaire, `implique` :
  « sans effraction » dit « effraction = non », sauf si l'effraction est déjà lue (`prolog.impliquer`).
- `f-d19` (foudre sur un poteau) : couvert à tort corrigé (incertain deux fois sur trois) ; la troisième fois, un
  refus : l'ordinateur lu « avec ses données » déclenchait « les frais de reconstitution des fichiers », écrits en
  exclusion de tout le sinistre. Ce sont des frais, pas l'appareil : hors décision.
- `f-d23` (la décennale) : malgré l'aide, le modèle lit encore « moins de dix ans » dans « fait construire ». La
  variable n'est plus lue (`pour: ["jamais"]`) : l'exclusion, à demander, est entamée par l'infiltration en façade,
  et la réponse est « incertain », avec la question de l'âge de la maison. C'est ce que le contrat demande :
  l'assureur vérifie la décennale, la déclaration ne la dit pas.

Oracle, sur les faits que le modèle a réellement lus : les cinq cas donnent la réponse attendue.

### 7.95 Assureur D à 83 % ; deux derniers écarts de lecture

Après 7.94 (S25 et 2.2 réacceptés), banc sur le jeu fermé de D : **83 % justes**, 0 couvert à tort, 0,67 refus à
tort, 2 instables, médiane 3,1 s. `f-d05`, `f-d06`, `f-d19` et `f-d23` donnent désormais la réponse attendue aux
trois passages. Restent, hors responsabilité civile et protection juridique (non traduites, 3 cas) :
- `f-d04` (conduite gelée dans une maison non chauffée, tuyaux non vidés) : le modèle lit `manque_entretien = oui`
  et l'exclusion générale du défaut d'entretien refuse (deux passages sur trois). Le contrat traite ce cas par ses
  mesures de prévention (4.2 : l'indemnité réduite de moitié), pas par l'exclusion. L'exclusion ne joue plus sur le
  gel ; sur une fuite lue sans précision (valeur parente du gel), elle est à demander.
- `f-d18` (porte non verrouillée) : refusé deux fois sur trois comme attendu ; la troisième, la confirmation des
  faits décisifs jugeait « non dit » le fait déduit `effraction = non`. On confirme désormais le fait lu qui le dit
  (`acces_voleur = sans_effraction`), pas sa conséquence (`prolog.sources_impliquees`).

Oracle, sur les faits réellement lus : `f-d04` couvert ; une fuite avec défaut d'entretien, incertain ; une tempête
sur un toit mal entretenu, toujours refusée.

**Résultat** (banc de 11 h 36) : **88 % justes, 0 couvert à tort, 0 refus à tort, 0 instable** ; médiane 2,9 s.
Tous les cas traduits sont justes aux trois passages ; les 12 % restants sont les 3 cas de responsabilité civile et
de protection juridique, incertains tant que le lot 3 n'est pas fait.

**A et B, après les changements du vocabulaire commun** (7.90 à 7.95) : A **77 %** (73 % au banc précédent,
70 % à la première mesure), 2 couverts à tort, 4 instables ; B **63 %** (65 %), 1 couvert à tort, 2 instables.
Cas par cas, les écarts avec les bancs précédents sont des changements d'un passage sur trois (instabilité de la
lecture), sauf `f-a10`, devenu juste aux trois passages ; aucun cas n'a basculé d'une réponse stable à une autre.
Les changements faits pour D n'ont pas dégradé A ni B.

### 7.96 Assureur D, lot 3 : la responsabilité civile et la protection juridique, les premières du projet

**Rédaction** : 13 articles (mesures de sécurité 4.1 à 4.3, responsabilité civile 12.1 à 13.3, défense pénale et
protection juridique 22.1 à 22.3) en 23 min 38 s, **238 contrôles bloquants**, près de **140 variables nouvelles**
proposées : une par condition du texte (le nombre de chiens adultes, la cylindrée d'un véhicule jouet, la longueur
d'un voilier, l'épandage de boues…). Accepté tel quel, ce vocabulaire aurait fait de la lecture d'une déclaration
de responsabilité civile une consigne de plusieurs pages pour un petit modèle.

**Relecture** (`relecture/assureur_d_lot_3.py`) :
- *Le vocabulaire* : sept variables au lieu de 140. `origine_rc` (ce qui a causé le dommage : une personne, un
  animal de compagnie, un autre animal, un chien dangereux, un véhicule à moteur, le logement, le bâtiment lui-même,
  la chasse ou un sport à risque, un contrat, l'activité professionnelle), `victime`, `dommage_tiers`,
  `bien_confie` ; pour la protection juridique, l'événement `litige` (nouveau), `domaine_litige` et l'option. Les
  exclusions que la déclaration ne dit jamais (épandage, phytosanitaires, ball-trap, statuts de société…) sont hors
  décision, chacune citée mot pour mot (le contrôle les compte toutes).
- *Les garanties* : la responsabilité « liée à l'habitation » selon le statut (propriétaire : le feu ou l'eau
  partis du logement, l'accident causé par le bâtiment ou le terrain ; locataire ; en vacances) ; la vie privée
  couvre le reste, sauf ce que 13.3 exclut ou renvoie à 12.x. La protection juridique, une option, en circonstance.
- *Des exclusions qui nomment leurs garanties* (`cibles`, nouveau champ des exclusions communes). Les articles
  d'exclusions sans garantie (12.4, 13.3, 22.3) s'écrivaient `tous`. Pire, les biens exclus de 1.1 et 1.2
  (véhicules, animaux…) visaient `tous` : la voiture rayée par le vélo de l'enfant (`f-d09`) aurait été refusée
  parce que « les véhicules à moteur » ne sont pas des biens assurés. Elles visent désormais les garanties qu'elles
  nomment ; un contrôle bloque une cible inconnue.
- *Les mesures de sécurité* (4.1 à 4.3) ne refusent jamais : elles réduisent l'indemnité de moitié. Le modèle en
  faisait des garanties (« protection_vol_4_1 ») ; ce sont des limites des garanties qu'elles touchent (vol,
  détériorations, eau, incendie), citées dans le titre IV. Les propositions 4.x ne sont pas acceptées.
- 13.2 (fêtes familiales, chambres d'hôtes en option) n'est pas traduit.

**Contrôle par le tableau des formules** : la responsabilité civile et la défense pénale, incluses dans les trois
formules, y sont reliées ; 0 écart. Oracle, faits écrits à la main : les 25 cas du jeu fermé de D donnent la réponse
attendue, et dix cas de responsabilité civile et de litige ajoutés (fuite chez le voisin, tuile qui tombe, chien qui
mord, scooter, objet du frère cassé, litige avec l'employeur…) aussi.

### 7.97 Assureur D à 92 % ; l'« accident » lu en trop

Lot 3 accepté (9 articles), les lots 1 et 2 réacceptés (exclusions qui nomment leurs garanties, réductions du
titre IV), `couverture regles` en ordre, 0 écart au tableau des formules. Banc sur le jeu fermé de D : **92 %
justes, 0 couvert à tort, 0 refus à tort, 0 instable**. `f-d15` (le cheval) et `f-d16` (le garagiste) sont refusés
aux trois passages, comme attendu. Le 95e centile de latence monte à 21,8 s (un appel lent au fournisseur) : la porte
de latence échoue sur ce passage.

Les deux écarts ont la même cause : le modèle lit **`accident`** en plus de l'événement qui dit déjà tout. `f-d09`
(le vélo raye une voiture) : `accident` et `responsabilite` ; `f-d14` (le trampoline emporté par le vent) :
`tempete` et `accident`. `accident` n'étant traduit par aucune garantie de D, la règle 8 du moteur (un événement
non traduit rend la décision incertaine) suspendait la réponse. L'aide de la valeur le disait pourtant (« pas un
vol, un incendie, l'eau, la tempête… »). Le vocabulaire retire désormais `accident` quand un autre événement est lu
(`preciser` accepte plusieurs règles, et une règle sans valeur de remplacement retire la valeur vague). Oracle, sur
les faits réellement lus : `f-d09` couvert, `f-d14` refusé.

**Résultat** (bancs de 12 h 33 à 12 h 38, chaîne complète, jeu fermé) : **Assureur D 100 % justes**, 0 couvert à
tort, 0 refus à tort, 0 instable (25 cas, dont 6 « incertain » attendus, l'assistance comprise) ; **A 80 %**
(77 %), **B 65 %** (63 %) : la règle sur « accident » ne les dégrade pas. Le 95e centile de latence reste
au-dessus de 20 s pour D et B : quelques appels lents au fournisseur, la médiane est de 4 s.

Limite de la mesure : 25 cas, écrits par un agent et un second avis, arbitrés par l'auteur. Plusieurs écarts du
banc ont été corrigés en regardant ces cas (7.93 à 7.97) : le 100 % est un résultat de mise au point, plus une
mesure à l'aveugle. Un second jeu fermé de D, écrit sans voir les règles, dirait ce qu'il vaut.

### 7.98 Les dépendances : 43 alertes Dependabot, et un verrou qui gardait le passé

GitHub signalait 43 alertes de sécurité sur `uv.lock`. Deux causes. Le verrou datait de quelques jours, et une
partie des paquets (MLflow et ce qu'il tire : Flask, SQLAlchemy, aiohttp, pyarrow…) avait été corrigée depuis.
Surtout, `pyproject.toml` acceptait Python 3.10 : `uv` gardait, pour 3.10 et 3.11, une seconde version plus ancienne
de 17 paquets (pillow, fastapi, starlette, python-multipart, numpy, pandas…), celles que les alertes visent. Or la
CI et l'image Docker sont en 3.12, le poste de développement en 3.14 : ces versions ne servaient à rien.

`requires-python = ">=3.12"`, puis `uv lock --upgrade` : **129 paquets → 104**, une seule version de chacun, toutes
à leur dernière version compatible ; 156 tests verts. Un fichier `.github/dependabot.yml` fait proposer chaque
semaine les mises à jour de `uv.lock`, chaque mois celles des actions de la CI. Le nombre d'alertes restantes se
lira sur GitHub après le push (Dependabot refait son analyse).

### 7.99 La responsabilité civile de A et B : le vocabulaire de D suffit

**Rédaction** (Mistral Large, consigne v12, 20 nov.) : A 2.5 (responsabilité de l'immeuble), 2.14 (défense et
recours), 5 (vie privée) ; B 3.1.9.10, 3.1.10 (immeuble), 4.1.1 (vie privée), 4.1.3 (protection juridique). **121
contrôles bloquants**, une soixantaine de variables nouvelles proposées (`soudain`, `imprevu`, `exterieur_victime`,
`age_assure`, `nombre_enfants_gardes`, `plateforme_agreee`…), et huit garanties pour la seule section 5 de A (biens
immeubles, animaux, déplacements, sports, garde d'enfants…), qui ne différaient que par ce qui a causé le dommage.

**Relecture** (`relecture/assureur_a_rc.py`, `relecture/assureur_b_rc.py`) :
- *Aucune variable nouvelle pour A, deux pour B* (les options). Le vocabulaire écrit pour D (`origine_rc`, `victime`,
  `bien_confie`, `litige`, `domaine_litige`) dit ce que les deux contrats distinguent. C'est la vérification qu'on
  attendait de 7.96 : sept variables tenaient pour un contrat français ; elles tiennent pour un contrat belge et un
  contrat luxembourgeois.
- *Une garantie de vie privée par contrat*, ses exclusions disent ce qui n'en relève pas : la profession, le contrat,
  les biens gardés ou confiés, les véhicules à moteur, le feu parti du bâtiment assuré (A 5.2), le feu, l'explosion
  ou l'eau partis des locaux de l'assuré (B 4.1.1.8.6), le sinistre intentionnel (A). La chasse reste hors décision
  chez A : le vocabulaire la range avec les sports en club et les compétitions, que A couvre.
- *Les options de B* (immeuble, vie privée, protection juridique : « si les conditions particulières mentionnent que
  la garantie … est accordée ») sont des circonstances dont la question ne cite pas les conditions particulières.
  Sinon le code en fait une réserve (7.62) : « couvert, sous réserve », comme pour les garanties de base de B. La
  convention du jeu fermé veut « incertain » pour une option inconnue (`f-b16`, le chien qui mord le facteur).
- 3.1.9.10 (le recours des tiers) était déjà traduit avec les frais annexes de l'incendie : la proposition n'est pas
  acceptée. `f-b12` (la fuite chez le voisin) reste couvert par lui, et la vie privée le refuserait (4.1.1.8.6).
- *Un contrôle assoupli* : la définition du contenu (12/contenu de A) bloquait la section 5, dont un titre dit « les
  biens immeubles et leur contenu ». Une définition citée « hors décision » par le relecteur compte désormais comme
  employée (le contrôle l'acceptait déjà déclarée non traduite) ; un test le vérifie.
- Hors décision, chaque élément cité : le trouble de voisinage, l'amiante, les seuils en euros, l'insolvabilité du
  tiers, le recours de l'assureur contre l'assuré (A 5.4), les engins lents que A couvre (fauteuils roulants, vélos
  électriques), les faits rares (paris, étangs, concours hippiques).

**Oracle**, faits écrits à la main : `f-a18` (le piéton renversé à vélo) couvert, `f-a19` (la tondeuse empruntée)
refusé, `f-b16` incertain, `f-b12` couvert ; le chien, la tuile, la voiture, le recours et le litige de consommation
donnent la réponse attendue sur les deux contrats ; les 25 cas de D inchangés ; 157 tests verts. Seul risque relevé :
si la lecture de `f-b12` ne donne que `responsabilite` (sans `degat_eaux`), la réponse devient un refus.

**Banc** (14 h 02 à 14 h 05, jeu fermé) : **A 78 %**, **B 63 %**, contre 80 % et 65 % avant ; pas de progrès. Le
risque relevé ne s'est pas réalisé : `f-b12`, `f-b16` et `f-a19` sont justes aux trois passages. Mais `f-a18`, le cas
que la responsabilité civile devait gagner, passe d'« incertain » à **refusé à tort** aux trois passages : le modèle
lit le vélo `origine_rc = vehicule_moteur`. L'aide de la valeur disait « une trottinette ou un vélo électriques
rapides » ; le petit modèle a retenu « vélo ». La vérification ne l'a pas retiré : le fait est vraisemblable, c'est sa
valeur qui est fausse. Les aides disent désormais « vélo ou trottinette sans moteur (à la force des jambes) » pour
`personne`, et « jamais un vélo ordinaire, qui est « personne » » pour `vehicule_moteur`. Les autres écarts entre les
deux bancs sont des cas instables hors responsabilité civile (`f-a13`, `f-a16`, `f-b05`, `f-b08`).

### 7.100 Le piéton renversé : la lecture était juste, la garantie n'était pas « une garantie »

Second banc de A après la correction des aides (14 h 10) : **77 %**. Le vélo est bien lu `origine_rc = personne`,
`victime = tiers`, aux trois passages, et le moteur répond « couvert »… que la validation rétrograde aussitôt :
« COUVERT rétrogradé en INCERTAIN : aucune garantie citée de façon vérifiable ». La règle de l'étape 5 (un
« couvert » doit citer une clause de type garantie) est juste ; le type ne l'était pas. Le découpage typait 5.1,
5.2, 5.5, 5.6 et 5.8 de A « autre » : la section 5 écrit « Nous vous assurons pour les dommages causés… », formule que
le classement ne connaissait pas (« nous garantissons », « nous couvrons », « nous prenons en charge »). La limite
était notée au chapitre 8 depuis le 18 nov. ; elle a coûté le seul cas que la responsabilité civile devait gagner.

« nous (vous) assurons » rejoint les formules de garantie. Simulé sur la base : seules ces cinq clauses de A changent
de type, aucune de B, C ou D ; un test le fixe. Le type est écrit dans la base au découpage : il faut relire les
contrats (`couverture ingerer --forcer`), puis vérifier que les citations des trois contrats tiennent.

Le reste du banc ne bouge pas : les écarts de A (`f-a13` l'ordinateur de l'employeur, `f-a15`, `f-a16` l'eau lue
tempête, `f-a17`) sont des erreurs de lecture connues ou des cas instables.

**Après relecture des contrats** (14 h 17) : base relue, 5.1, 5.2, 5.5, 5.6 et 5.8 de A typées « garantie », rien
d'autre ne bouge ; citations de A et D toutes retrouvées. Banc de A : **78 % justes**, 2 couverts à tort, 0,33 refus
à tort, 4 instables. `f-a18` est **couvert à deux passages sur trois** ; au troisième, le vélo est encore lu
`vehicule_moteur` malgré l'aide corrigée. La responsabilité civile est en place sur les trois contrats ; ce qui
reste en dessous de 85 % pour A et B, ce sont des erreurs de lecture hors responsabilité civile (l'ordinateur de
l'employeur, l'inondation lue tempête, l'incendie d'un appartement neuf), déjà relevées en 7.81.

### 7.101 Les erreurs du jeu fermé de A et B : cinq de lecture, trois de règles

Relecture de chaque écart des derniers bancs de A et B, faits lus en regard. Trois cas ne sont pas des erreurs
(`f-a15`, `f-a16`, `f-b14` : toute réponse y est acceptable). `f-b13` attend l'assistance (non traduite), `f-a17` le
délai de 30 jours après un déménagement (9.2, non traduit), `f-b18` la voiture fermée à clé (une obligation que le
moteur met en réserve, et la vitre de la voiture prise pour un vitrage assuré) : à reprendre plus tard. Le reste :

*Lecture, par l'aide des valeurs* (`regles/vocabulaire.json`) :
- `tempete` : « pas la pluie d'un orage ». L'orage faisait lire une tempête (`f-a15`, `f-a16`, `f-b03`), qui posait la
  question du vent à 80 km/h au lieu de refuser l'eau entrée par la fenêtre de toit.
- `degat_eaux` : « y compris les moisissures ». La moisissure était lue `autre` (`f-b04`), que B renvoie à l'incendie.
- `lieu` : « vol dans le logement entré par la terrasse » est `logement` (`f-b05`, lu `terrasse`, refusé) ; la remise
  au fond du jardin est une `annexe` (`f-b17`, lu `jardin`, refusé).
- `element_batiment` : pas un store banne (`f-a14`). `coupure_soudaine_reseau` : « panne de courant du quartier »
  (`f-a12`, jamais lue).

*Lecture, par le choix des variables* (`prolog.py`) : un contrat ne lit que les variables de ses règles (7.57). B
n'emploie pas `acces_voleur`, seulement `effraction` ; or « j'avais laissé ma porte ouverte » (`f-b06`) ne dit jamais
« sans effraction », et la vérification retirait `effraction = non` comme non dit. Une variable qui implique un fait
employé (`acces_voleur = sans_effraction` → `effraction = non`, 7.94) est désormais lue aussi.

*Règles* (`relecture/lecture_ab.py`) :
- A 2.6 : l'exclusion du matériel professionnel ne visait que l'ordinateur ; l'écran fourni par l'employeur restait
  couvert (`f-a13`). Elle vise chaque appareil électronique.
- B 3.1.5 : la perte d'étanchéité des vitrages était une circonstance « si… alors » ; le type de dommage inconnu la
  laissait inconnue, et le miroir fendu (`f-b08`) devenait incertain. Une exclusion à demander : le double vitrage embué
  (`f-b20`) reste incertain.
- B 3.1.1 : la décongélation rattachée à un vol, parce qu'un bien vague (`objet_divers`) pouvait être une denrée, et
  refusée faute d'incendie : ce refus l'emportait sur les garanties possibles du vol dans la remise. L'événement passe
  au périmètre. Le défaut est plus général (un périmètre fait d'un seul bien se rattache à tout bien vague) : à
  surveiller.

**Oracle**, faits attendus écrits à la main : les onze cas écrits donnent la réponse attendue ; les 25 cas de D et
les cas de responsabilité civile inchangés ; tests verts. Méthode : ces cas ont servi à corriger, le banc qui suit
mesure la mise au point, pas la généralisation.

**Banc** (14 h 30 à 14 h 36, jeu fermé) : **A 85 %** (78 %), 1 couvert à tort ; **B 85 %** (63 %), 0,33 couvert à
tort, 0 refus à tort, 5 instables ; **D 100 %**, inchangé. Les portes de justesse passent pour A et B pour la première
fois ; restent le rappel des questions et, selon les passages, la latence ou un couvert à tort.

Un effet de bord : l'aide de `degat_eaux` (« y compris les moisissures ») fait lire `type_dommage = moisissure` dans
des fuites qui n'en parlent pas (`f-b02`, `f-b03`, `f-b12`, `f-a15`) ; la confirmation le retient comme fait décisif
non confirmé, et `f-b12` devient incertain une fois sur trois. Les aides disent désormais : la moisissure « seulement
si la déclaration en parle ; l'eau seule ne suffit pas ». Restent, hors des cas en attente (assistance, déménagement,
voiture fermée à clé) : le store banne encore lu dans le logement (`f-a14`), le vélo lu véhicule à moteur une fois sur
trois (`f-a18`), le classement de la zone inondable (`f-a16`, couvert au lieu d'incertain).

Banc suivant (14 h 40) : **A 85 %**, **B 82 %** ; la fuite chez le voisin redevient juste aux trois passages. La porte
laissée ouverte (`f-b06`) est maintenant lue `acces_voleur = sans_effraction`, et l'absence d'effraction en découle ;
la réponse reste incertaine parce que la violence n'est pas lue (le vol simple exige l'une et l'autre absentes). Le
seul couvert à tort de B est `f-b18` (voiture fermée à clé, en attente).

---

**Partie V — Le produit (20 au 22 novembre).** Ce qu'un gestionnaire verrait : l'écran, les questions posées, la fiche ; et des déclarations que personne n'a écrites pour le système.

### 7.102 Une API qui englobe le produit

L'ancienne interface (`web.py`, Starlette) servait la page de démonstration : trois routes, ni clé, ni
documentation, et la seule analyse par le modèle. Le produit a maintenant son API, en FastAPI, sur le modèle de
celle de SortirIA : préfixe `/api/v1`, clé dans l'en-tête `x-api-key` (`COUVERTURE_API_KEY` ; sans clé configurée,
les routes protégées refusent tout plutôt que de rester ouvertes), **une route par fichier** (`api/routes/`), la
logique hors des routes (`api/service.py`, testée sans serveur), documentation interactive sur `/docs`.

Ce qu'elle ajoute au produit : **`POST /decisions`**, la décision sur des faits, sans modèle. Une analyse qui répond
« incertain » rend ses `faits` et, dans `a_preciser`, chaque variable à demander au client avec ses valeurs
possibles ; les réponses, ajoutées aux faits, se soumettent à `/decisions` : la décision tombe en quelques
millisecondes, gratuite et déterministe. C'est le circuit d'un gestionnaire (ou d'un formulaire) : le modèle ne lit
qu'une fois. Un fait décisif que la confirmation n'a pas retrouvé (7.49) est retiré des faits rendus et devient la
première question : renvoyés tels quels, ils ne redonneraient pas la réponse que la confirmation a suspendue.

Tests : la logique (6 tests, oracle Python, base temporaire) et les routes par HTTP (`TestClient`, dépendances
remplacées : clé, codes d'erreur, aller-retour « incertain » → réponse → décision, une route par fichier vérifiée).

### 7.103 Une interface Angular aux couleurs du système de design de foyer.lu

Sur le modèle de l'interface de SortirIA (Angular 21, composants autonomes, signaux, proxy `/api`), dans
`frontend/`. Un écran : à gauche le contrat et la déclaration (avec trois exemples), à droite la décision. La
décision en tête, en couleur (couvert, non couvert, à préciser), puis les faits retenus, les clauses citées (le texte
complet de la clause s'ouvre au clic), les limites, et, replié, l'arbre de preuve et les contrôles de la lecture.

Le circuit de l'API se voit : une réponse « à préciser » affiche les questions à poser au client, avec les réponses
possibles en boutons (le sens de chaque valeur au survol) ; « Décider » soumet les faits complétés à `/decisions`, et la
nouvelle décision s'ajoute sous la première, sans nouvel appel au modèle.

Couleurs et police : celles du système de design public de foyer.lu (variables `--fds-*` relevées sur le site,
police Barlow) : bleu principal `#2957C8`, gris « plume », vert, rouge et jaune d'état pour la décision. Seules les
couleurs sont reprises ; ni logo, ni nom, ni contenu de la marque : l'écran reste celui d'une démonstration.

La clé de l'API n'entre jamais dans le navigateur : le proxy de développement (`proxy.conf.mjs`) la lit dans le `.env`
et l'ajoute aux appels ; en production, ce serait le rôle du serveur placé devant l'API.

### 7.104 Cent déclarations écrites « comme les gens écrivent », par l'interface

Cent déclarations inventées, sans regarder les règles (`data/libre/declarations.jsonl`), écrites comme des clients :
fautes, style oral, détails inutiles, dix réduites à quelques mots (« jai une fuite », « court circuit »). Tous les
thèmes : eau, vol, incendie, électricité, tempête, catastrophes, bris, responsabilité civile, litiges, assistance, et
des cas hors contrat (la voiture, les termites, la panne du frigo). Réparties à tour de rôle sur A, B et D, envoyées
par la page (le proxy de l'interface, la clé côté serveur), trois à la fois. Pas de réponse attendue écrite à
l'avance : c'est un essai de robustesse, relu ensuite cas par cas par l'auteur et Claude, sans expert du métier.

**Robustesse** : 99 réponses, aucune erreur du serveur ; une seule refusée (« volé vélo », 9 caractères, sous le
minimum de 10 ; l'interface désactive déjà le bouton, mais l'API répond avec le message anglais de Pydantic). Médiane
3,7 s, 90e centile 9,9 s, maximum 39,5 s (quelques appels lents au fournisseur). Décisions : 29 couverts, 26 refus,
44 « à préciser », dont 10 renvoyés à un gestionnaire (assistance, mérule de B, casse accidentelle : non traduites)
et 9 suspendus par la confirmation d'un fait décisif.

**Relecture** : la grande majorité des réponses est défendable (le chien qui mord, la coupure de courant de 12 h,
l'ordinateur de l'employeur, la femme de ménage, les litiges hors garantie, le tremblement de terre qui demande
l'arrêté). Les erreurs se rangent en cinq familles :

1. *La responsabilité civile non reconnue* quand le dommage est décrit par l'objet d'autrui : « mon fils a cassé la
   vitre du voisin » est lu `bris` sur la voie publique, « une tuile est tombée sur la voiture du voisin » `heurt` :
   refusés, alors que la responsabilité civile (ou son option) répond. Le skieur percuté est lu `origine_rc =
   vehicule_moteur` et refusé. Quatre refus à tort.
2. *Un refus sur presque rien* : « jai une fuite » chez B est refusé (une garantie annexe rattachée par un bien vague,
   dont une condition est fausse, l'emporte ; le défaut relevé en 7.101). L'égout qui refoule, lu seulement `degat_eaux`
   avec `cause_eau = inondation`, est refusé par l'exclusion de l'inondation, sans que la catastrophe naturelle soit lue.
   L'explosion du barbecue sur la terrasse est refusée (aucune garantie rattachée).
3. *« accident » qui avale l'événement* : l'aquarium fendu, la tablette tombée, les clés perdues (lues `assistance`)
   partent chez le gestionnaire alors qu'une garantie traduite répond (eau, bris du multimédia, perte des clés de A).
4. *Des « couvert sous réserve » trop généreux* : « je crois que j'avais oublié de fermer à clé » est couvert sous
   réserve que les portes aient été fermées ; « degat des eaux cuisine », sans cause, couvert sous réserve de la cause.
   La réserve est juste en droit, mais la question est déjà répondue dans le premier cas, et décisive dans le second.
5. *L'orage lu tempête* (la fenêtre de toit restée ouverte) malgré l'aide de 7.101 ; des faits inventés sans effet
   (`type_dommage = moisissure` ou `opacification` sur de simples fuites).

Un défaut d'affichage : quand la validation rétrograde un « couvert » en « incertain » (le téléphone tombé dans les
toilettes, citation non vérifiable), la justification commence encore par « Couvert. ».

Ce que cela dit de la mesure : sur des textes libres, les erreurs ne viennent presque plus des règles, mais de la
lecture de ce qu'est le sinistre (qui est lésé, quel événement) ; le jeu fermé, écrit en phrases complètes, ne le
montrait pas.

### 7.105 Les refus à tort des cent déclarations, sur les trois contrats

Les deux familles d'erreurs qui coûtent le plus à un assuré (7.104, familles 1 et 2), corrigées pour A, B et D à la
fois, dans ce qui leur est commun : le moteur, la lecture et le vocabulaire. Aucune règle de contrat n'est touchée.

*Le moteur* (`moteur.pl` et l'oracle `moteur_reference.py`) : une garantie dont le périmètre est seulement inconnu
(un bien vague, ou pas de bien lu) et dont une condition est fausse ne joue pas, mais n'est plus « rattachée ». Son
refus l'emportait sur les garanties possibles : « jai une fuite » était refusé chez B par la dégradation du linge
(« à la suite d'un incendie »), faute de bien lu. C'était le défaut relevé en 7.101 (la décongélation) : corrigé une
fois pour toutes, au lieu de garantie par garantie. Règle 2 du moteur : « circonstance non → la garantie ne joue pas
(hors sujet si le périmètre est inconnu) ».

*La lecture* (`prolog.py`) : `implique` peut ajouter une valeur à une variable qui en a plusieurs. `cause_eau =
inondation` (débordement d'un cours d'eau, refoulement des égouts) ajoute `catastrophe_naturelle` aux événements, sans
retirer l'eau : l'égout qui refoule n'est plus refusé par l'exclusion de l'inondation du dégât des eaux (A), il relève
des catastrophes naturelles, qui demandent ce qui manque. Valable pour les trois contrats : B range l'inondation dans
« pluies & inondations », D dans les catastrophes naturelles (arrêté).

*Le vocabulaire* (les aides) : la responsabilité civile se reconnaît à l'objet d'autrui. `responsabilite` cite la vitre
ou la voiture d'un voisin, le skieur blessé ; `bris`, `heurt` et `accident` disent que le bien d'un autre, abîmé par
l'assuré, un proche ou sa maison, est une responsabilité civile ; `origine_rc` range le ski dans les sports de loisir
(`personne`) et précise que le véhicule à moteur est celui que conduisait l'assuré, pas la voiture abîmée de la victime ;
`lieu = terrasse` laisse au logement les murs, portes et baies de la maison (l'explosion du barbecue).

**Vérification sans modèle** : les faits des cent déclarations, rejoués par l'oracle avant et après : seuls changent
« jai une fuite » (refus → à préciser) et l'égout qui refoule (refus → à préciser, catastrophes naturelles) ; aucun
autre cas ne bouge. Les faits attendus après la nouvelle lecture (la vitre du voisin, la tuile sur la voiture, le
skieur, sur les trois contrats) donnent la responsabilité civile ou son option. Les 25 cas fermés de D et ceux de A et
B, inchangés ; deux tests ajoutés. Ce que les aides changent à la lecture, seul un nouveau passage des cent
déclarations le dira.

### 7.106 Après 7.105, les bancs fermés : trois couverts à tort, et une porte mal mesurée

Bancs fermés après 7.105 (Mistral Small, lecture vérifiée, 3 exécutions) : A **85 %** justes, 1,67 couvert à tort ;
B **83 %**, 1 couvert à tort ; D **100 %**. 175 tests passent. Les faits lus, gardés par le banc depuis 7.93, disent
chaque fois où l'erreur naît.

- *`f-b18`, l'ordinateur volé dans la voiture garée* (B, attendu incertain, obtenu couvert 3 fois sur 3). Deux
  causes. **Le moteur** : le pack multimédia oblige, dans un véhicule, à l'avoir fermé à clé et à ne rien laisser en
  vue ; non respectée, l'obligation fait refuser sans lien causal. Le lieu était établi, l'exigence inconnue : elle
  devenait une réserve, et la garantie couvrait. Une obligation « si A alors B », **sans lien causal**, dont A est
  établi et B inconnu est désormais **engagée** : la réponse est incertaine et on demande B (règle 6 ter, `moteur.pl`
  et l'oracle). Avec lien causal, elle reste une réserve : les fenêtres pendant l'absence ne se demandent pas quand le
  voleur est passé par la porte (`g2-p01`, qui l'a montré au premier essai). **La lecture** : la vitre de la voiture
  était lue `vitre` (un vitrage du bâtiment, couvert par le bris de vitrages) et la journée au parking un
  `sejour_temporaire` ; les aides disent maintenant que la vitre est celle du logement, celle d'une voiture étant
  `vehicule_moteur`, et qu'un séjour dure plusieurs nuits.
- *`f-a17`, l'incendie deux mois après avoir emménagé à Namur* (A, arbitré incertain). L'art. 9 n'était pas traduit :
  « Si vous déménagez en Belgique, vous disposez d'un délai de 30 jours pour nous en informer. Si vous ne le faites
  pas, l'assurance prend fin à l'expiration de ce délai. » Il devient une **exclusion commune, à demander**
  (`relecture/assureur_a_9.py`, proposition `9`) : l'assureur prouve que le déménagement n'a pas été signalé ; si la
  déclaration dit un emménagement de plus de 30 jours, l'exclusion est entamée, la réponse est incertaine, avec la
  question. Deux variables : `emmenagement` (non, moins de 30 jours, plus de 30 jours) et `demenagement_signale`. Le
  déménagement à l'étranger n'est pas traduit (il faudrait savoir où était le logement assuré).
- *`f-a11`, le vase brisé par le chat* (A, 2 couverts sur 3) : lu `verre_meuble` (couvert) au lieu de
  `objet_verre_non_vitre`. L'aide de `verre_meuble` dit maintenant ce qu'il est : le plateau ou la porte en verre d'un
  meuble, pas un objet posé dessus. C'est le genre de confusion que la banque d'exemples (7.107) devra régler sans aide.
- *La porte « rappel des questions » à 0 %* sur les trois bancs : le jeu fermé écrit la question attendue en phrase,
  le banc cherche une variable ; rien ne pouvait correspondre. Une question qui n'est pas une variable n'est plus
  mesurée (la porte n'est plus jugée sur le jeu fermé, au lieu d'échouer à tort).

Restent : `f-a18` (le vélo lu véhicule à moteur une fois sur trois), `f-a14` (le store banne, incertain au lieu de
refusé), et la latence de D au 95e centile (20 s pour un cas seul, un appel lent du fournisseur sur dix).

**Vérification sans modèle** : les faits lus de `f-b18` et `f-a17`, rejoués par l'oracle, donnent incertain avec les
bonnes questions ; lus correctement, ils l'auraient donné aussi. Les faits des cent déclarations (7.104), rejoués
avant et après : aucune décision ne change. Deux tests ajoutés.

### 7.107 La banque d'exemples et le partage mise au point / test

Première étape du plan proposé après 7.105 : remplacer, à terme, les exceptions écrites dans les aides du vocabulaire
(32 aides en ont) par des exemples choisis pour chaque déclaration. Rien n'est encore branché dans l'analyse.

**Le partage** (`data/lecture/partage.json`, figé) : les 112 cas du golden set qui ont des faits idéaux (A et B) sont
rangés en **74 de mise au point** et **38 de test**, d'après une empreinte de leur identifiant (le même cas tombe
toujours du même côté ; un cas ajouté plus tard ne déplace pas les autres). Règle : un cas de test ne sert jamais à
corriger le vocabulaire ou les règles, et n'entre jamais dans la banque. `couverture banc --partie test` (ou
`mise_au_point`) passe le golden set sur une seule partie ; ses rapports ne se comparent qu'à ceux de la même partie.
Honnêteté : ces 38 cas ont déjà servi à corriger avant aujourd'hui. Le partage protège la mesure à partir de
maintenant ; une mesure vraiment neuve demandera des déclarations neuves (un second lot de cent, écrit par Mistral
Large, puis validé).

**La banque** (`src/couverture/exemples.py`) : les cas de mise au point, avec leur déclaration et leurs faits idéaux.
`couverture exemples --indexer` calcule le vecteur de chaque déclaration avec `mistral-embed` (un texte → 1 024
nombres, pas un appel de lecture), dans la table `exemples` de la base ; seuls les exemples nouveaux ou changés sont
recalculés. `couverture exemples --proches "…"` donne les plus proches d'une déclaration avec leur score : similarité
cosinus, un **seuil** sous lequel on n'envoie rien (0,80, à calibrer sur ces scores), la **diversité** (MMR : le plus
proche, puis le suivant le plus proche qui ne ressemble pas trop aux exemples déjà pris), et, pour les détails, les
seuls exemples du **même événement**. Pas de base vectorielle : quelques centaines de vecteurs se comparent en Python.

Suite : calibrer le seuil, puis brancher les exemples dans les appels 1 et 2 derrière une option, et comparer sur la
partie test, avec et sans. S'ils n'améliorent que les cas déjà dans la banque, ils n'ont rien appris au modèle.

### 7.108 Bancs après 7.106, le seuil des exemples, et les exemples dans la lecture

Bancs fermés (16 h 19 à 16 h 25) : A **85 %** justes, 0,67 couvert à tort (contre 1,67), 0,67 refus à tort, 4
instables ; B **80 %**, 1,33 couvert à tort, 5 instables ; D **99 %**. 184 tests passent. Les faits lus disent :

- `f-b18` n'est plus couvert par la vitre ni par le séjour, mais la voiture garée devant la gare est lue
  `lieu = voie_publique` deux fois sur trois : l'obligation « dans un véhicule » n'est pas mise en jeu. Aides de
  `vehicule` et `voie_publique` : un objet volé dans une voiture garée, c'est `vehicule`.
- `f-a18`, le vélo, est lu `origine_rc = vehicule_moteur` deux fois sur trois. L'aide citait « vélo électrique » :
  la leçon 113, enfreinte par nous-mêmes. Elle dit maintenant « un engin à moteur, qui avance sans qu'on pédale »,
  sans le mot. Le vélo électrique rapide (un cyclomoteur) n'y est plus nommé.
- `f-b15` (le ruissellement) et `f-b18` restent couverts par **une option dont on ne sait pas si elle est
  souscrite** (pluies et inondations, matériel multimédia), mise en réserve depuis 7.62 (leçon 79). Le jeu fermé, lui,
  attend « incertain » quand la réponse dépend d'une option. Les deux conventions se contredisent : tranché en 7.109.
- Effet de bord de 7.106 : la réserve du déménagement (art. 9 de A) s'ajoute aux « à préciser » de chaque réponse
  couverte de A, comme celle du défaut d'entretien chez D.
- Le reste est de la variance de lecture (`f-a02`, `f-a11`, `f-a12`, `f-b03`, `f-b07`, `f-b13`) : c'est ce que les
  exemples doivent réduire.

**Le seuil**, calibré sur la banque (74 exemples, 2 701 paires, vecteurs `mistral-embed`) : deux déclarations du même
événement ont une similarité médiane de 0,84, deux d'événements différents de 0,80. À 0,85, 42 % des paires du même
événement passent, 4 % des autres ; à 0,88, 15 % et 0,5 %. Seuil retenu : **0,85** (avec le filtre par événement aux
détails). Le plus proche voisin de chaque exemple est du même événement 59 fois sur 74.

**Les exemples dans la lecture**, derrière l'option `COUVERTURE_EXEMPLES=oui` (lecture en deux temps ou vérifiée) :
un vecteur par déclaration, puis trois exemples au plus pour le socle (réduits à événement, bien, lieu) et trois du
même événement pour les détails (réduits aux variables de l'appel), avec la consigne qu'ils montrent la façon de lire
et ne sont pas les faits à reprendre. Une déclaration n'est jamais son propre exemple. Si l'appel au vecteur échoue,
la lecture se fait sans exemples. Le banc l'inscrit dans le mode de lecture (« verifiee, exemples ») : ses rapports ne
se comparent qu'entre eux. Deux tests ajoutés.

### 7.109 Une option seule à couvrir : « à préciser », plus « couvert sous réserve »

Décision de l'auteur, sur la question de 7.108. Depuis 7.62 (leçon 79), une garantie qui ne joue que si les
conditions particulières la mentionnent était une **réserve** : « couvert, sous réserve que vos conditions
particulières mentionnent la garantie ». Le jeu fermé, écrit sans voir les règles, attend « incertain » quand la réponse
dépend d'une option. Les deux conventions se contredisaient ; c'est la seconde qui est retenue : un « couvert » qui ne
l'est pas coûte plus cher qu'un « à préciser ». Ce que la leçon 79 disait reste vrai : le déclarant ne connaît pas ses
options, la question est un **point à vérifier dans les conditions particulières**, pas une question qu'il doit savoir.

Ce qui distingue une option d'une garantie de base est le contrat, pas le vocabulaire : `option_materiel_multimedia`
est une garantie de base chez B (3.1.7, « garanties de base ») et une garantie optionnelle chez A (6, « les
garanties optionnelles »). Chaque contrat déclare donc ses options, en tête de ses règles (`option/1`) :
- A : `option_materiel_multimedia` (le pack multimédia) ;
- B : `option_tremblement_terre`, `option_pluies_inondations`, `option_pertes_indirectes` (la section 3.2) ; les
  garanties de la section 3.1 (incendie, tempête, eaux, vol, bris de vitrages, multimédia…) restent présumées
  souscrites, comme le veut la convention du jeu fermé ;
- D : `option_veranda`, `option_objets_valeur`, `pack_jardin`, `pack_piscine` (les packs et garanties optionnels).

Le moteur (`moteur.pl` et l'oracle, règle 6 quater) : une garantie rattachée qui couvrirait sous la seule réserve d'une
option est « à préciser », avec la question de l'option. Une garantie de base qui couvre l'emporte toujours (le
combinateur prend d'abord un « couvert »).

**Vérification sans modèle**, oracle avant et après : les faits idéaux du golden set (A et B), les faits lus des neuf
derniers bancs fermés (195 lectures) et ceux des cent déclarations. Changent : `f-b15` (le ruissellement, chez B, 2
lectures sur 3 : couvert → à préciser, la réponse attendue), `f-a09` (A, 3 sur 3 : couvert → à préciser, la réponse
attendue ; le banc donnait déjà « incertain » par la confirmation) et, parmi les cent déclarations, le glissement de
terrain chez B (option pluies et inondations). Aucun cas du golden set ne change : ses réponses attendues n'ont pas à
être revues. Un test ajouté.

### 7.110 Simplifier : retirer ce qui n'est plus le produit, et une commande, un module par fichier

Décision de l'auteur : retirer tout ce qui servait des méthodes ou des réglages essayés puis écartés, et redécouper les
gros fichiers. Aucune réponse ne doit changer : les tests passent à l'identique (moins ceux du code retiré), et les
bancs sont à repasser pour le vérifier.

**Retiré** (le code reste dans l'historique git) :
- la méthode `brut` (le contrat entier dans le prompt, la référence « chatbot » : `pipeline.py`, `juges.py`) et
  LegalBench (`legalbench.py`, ses tests ; ses résultats restent dans METRIQUES) ;
- l'ancienne page web (`web.py`, `static/index.html`) et la commande `serveur`, remplacées par l'API et l'interface
  Angular (7.102, 7.103) ;
- MLflow (`suivi.py`, l'extra `suivi`, le service docker, `versions --enregistrer`) : les rapports de `data/bancs/`,
  comparés au précédent de même configuration, et le manifeste des consignes en tiennent lieu ;
- les fournisseurs Anthropic et « compatible OpenAI » (`COUVERTURE_FOURNISSEUR`, `COUVERTURE_LLM_URL`) : jamais
  employés ; Mistral reste derrière le protocole `LLM` ;
- les lectures en un temps et en parallèle (`COUVERTURE_LECTURE`, la consigne `faits-regles` v4), essayées et écartées
  en 7.38 à 7.42 ; la lecture est toujours en deux temps puis vérifiée (`verifier=False` sert aux tests) ;
- le second avis par un autre modèle (`COUVERTURE_MODELE_CONFIRMATION`, le recours de 7.78), jamais retenu : la
  confirmation des faits décisifs se fait par le modèle de la lecture ;
- les scripts `relecture/` (18 fichiers) : des corrections déjà appliquées, que chaque proposition trace dans
  `meta.relecture`.

**Redécoupé** :
- `prolog.py` (958 lignes) devient `prolog.py` (le moteur : SWI-Prolog, vocabulaire, décision, 266 lignes),
  `lecture.py` (le modèle lit, le code ramène au vocabulaire) et `chaine.py` (la chaîne et la réponse) ;
- `cli.py` (700 lignes) devient le paquet `cli/` : une commande par module, comme une route par fichier dans l'API ;
- `redaction.py` (1 140 lignes) devient le paquet `redaction/` : `consigne.py`, `ecriture.py` (JSON → Prolog),
  `controles.py`, `vocabulaire.py`, et les commandes dans `__init__.py`.

Bilan : 7 450 lignes de Python dans `src/` avant, 6 700 après, et 4 000 lignes de moins en tout (scripts de relecture et
page web compris). Le docker lance l'API et Grafana. Les consignes en service passent de sept à quatre ; leurs textes
archivés restent dans `docs/consignes/`.

### 7.111 Après la simplification, et les exemples mesurés

**La simplification ne change rien** (7.110) : 173 tests passent, `couverture regles` est en ordre pour les trois
contrats, et le jeu fermé donne, sans exemples, A **88 %** (0 couvert à tort, 1 refus à tort : le vélo), B **90 %** (0 et
0, portes passées), D **100 %**. Les 95e centiles de latence à 70 s viennent de deux séries de bancs lancées en même temps
(huit appels à la fois : limites de débit du fournisseur), pas du code.

**Les exemples** (`COUVERTURE_EXEMPLES=oui`, 7.108), mesurés le même après-midi :

| | A fermé | B fermé | D fermé | A, partie test du golden |
|---|---|---|---|---|
| Sans exemples (deux séries) | 85 % et 88 % | 83 % et 90 % | 99 % et 100 % | 80 % justes, 3,3 couverts à tort, 8 instables |
| Avec exemples | **95 %**, 0 couvert à tort, 0 instable | 82 % | 97 % | **89 %**, 2 couverts à tort, 2 instables |

Sur A, le gain est net, et il tient sur la partie test, que la banque ne contient pas : le jeu de clés lu comme un bien
volé (`g-p03`) et la fenêtre de `val-01` ne font plus couvrir, les instables passent de 8 à 2. Sur B et D, l'écart
reste dans la variance d'une série à l'autre. La banque ne contient que des cas de A et de B (le golden set) : D n'a pas
d'exemple à lui. Coût : une demi-seconde de plus par cas (un vecteur, des messages plus longs).

Restent dans les deux modes : `f-a18` (le vélo lu véhicule à moteur), `red-b05` (le miroir) et `g2-p08` (le bain à
bulles lu « débordement d'aquarium »).

### 7.112 Les exemples deviennent la lecture par défaut

La mesure demandée en 7.111, sur la partie test de B (7 cas, 3 exécutions), donne la même décision avec et sans
exemples : **81 % justes, 0 couvert à tort, 0 refus à tort**, 2 instables dans les deux cas ; 76 % d'exactes avec, 71 %
sans. Le rappel des faits baisse (73 % contre 81 %, un cas avec contradiction), sans effet sur les réponses. B ne recule
donc pas, et A gagne nettement (7.111) : les exemples deviennent la lecture par défaut.

- `COUVERTURE_EXEMPLES=non` les coupe (pour comparer) ;
- ils demandent la clé et la banque indexée (`couverture exemples --indexer`) ; sans l'une ou l'autre, la chaîne lit
  sans exemples, sans erreur. Le docker indexe la banque au démarrage ;
- le banc inscrit « exemples » dans le mode de lecture d'après la chaîne elle-même, plus d'après la variable : un
  rapport dit ce qui a vraiment tourné.

Un test ajouté. Suite : le vélo (`f-a18`), le miroir (`red-b05`) et le bain à bulles (`g2-p08`), puis des exemples pour D.

### 7.113 Les trois erreurs qui restaient, et la règle du partage

Les trois erreurs qui résistaient aux exemples (7.111), lues dans les faits gardés par les bancs :

- **`red-b05`, le miroir pas encore accroché** (couvert au lieu de refusé, 3 fois sur 3). Small lit « accident » ; le
  code le précise en « bris » sur un miroir (7.86), mais **après** la lecture. Le temps 2 avait donc posé les questions
  de l'« accident », qui n'en a presque pas, et jamais « la vitre était-elle placée ? ». Ce n'est pas une erreur de
  lecture mais de **la chaîne** : l'événement est maintenant précisé dès la fin du temps 1, avant de choisir les
  questions du temps 2 (`lecture.py`). Tout « accident » sur une vitre, un miroir ou un sanitaire en profite.
- **`f-a18`, le vélo** (refusé au lieu de couvert, 3 fois sur 3, malgré deux aides et les exemples). Le vélo était caché
  dans l'aide de `personne` (« maladresse, chute, jeu, sport… vélo ou trottinette sans moteur ») ; Small cherchait un
  engin, il prenait le seul qui existait : le véhicule à moteur. Le vélo a maintenant **sa valeur**,
  `velo_trottinette`, rangée sous `personne` (`parents`, comme le gel sous la fuite d'installation) : les règles des
  trois contrats qui visent « personne » s'y appliquent sans être touchées (vérifié par l'oracle : couvert chez A et D,
  à préciser chez B comme pour « personne »).
- **`g2-p08`, le bain à bulles lu « débordement d'aquarium »** : non corrigé, à dessein. Le cas est dans la **partie
  test** (7.107) ; l'aide de `piscine_exterieure` nomme déjà le bain à bulles, et la retoucher pour lui serait corriger
  sur un cas de test. La vérification aurait dû dire « non dit » (la déclaration ne parle d'aucun aquarium) : c'est elle
  qu'il faut renforcer, sur des cas de mise au point qui montrent la même confusion.

`red-b05` est aussi un cas de test. La correction n'y touche ni aux règles ni au vocabulaire : c'est un défaut de la
chaîne, que ce cas a montré et qui vaut pour tous. Il faut le dire : sur ce cas, la partie test ne mesure plus une
lecture neuve. Deux tests ajoutés.

**Mesure** (21 nov., 0 h 08 et 0 h 12, avec exemples) : 176 tests passent. Le vélo est couvert 3 fois sur 3. Le miroir
n'est plus couvert : `vitre_placee = non` est lu, mais la confirmation des faits décisifs ne le juge pas écrit (« encore
dans son carton et pas encore accroché ») et la réponse reste « à préciser », réponse acceptable, du côté prudent. Jeu
fermé de A : **93 %** justes, 0,33 couvert à tort (le vase, une fois sur trois). Partie test de A : **89 %**, 2 couverts
à tort : le bain à bulles, et le jeu de clés (`g-p03`) qui revient (corrigé par les exemples en 7.111, la lecture
d'une série à l'autre varie sur ce cas).

### 7.114 Ce qu'on montre au client, la vérification, la latence

**Les questions au client.** Le rapport de 7.113 montrait deux défauts visibles dans l'interface : la même question
deux fois (la question nue ajoutée par la confirmation, et la version classée par le moteur, « oui → couvert ; non →
non couvert ») ; et « avez-vous déménagé ? » ajouté à presque toutes les réponses d'Assureur A (7.106). Une seule
fonction choisit maintenant ce qu'on dit au client, pour le texte du verdict comme pour l'API
(`chaine.points_a_preciser`) :
- une **question** : sans la réponse, la garantie ne tranche pas (et, pour un refus, celles des garanties possibles) ;
- une **réserve** n'est montrée que pour une réponse couverte : pour « à préciser » ou un refus, elle ne change rien ;
- jamais une réserve qui vaut pour **tous les sinistres** (« pour » couvre tous les événements : le déménagement non
  signalé) : elle n'apprend rien sur celui-ci. Si la déclaration la met en jeu, le moteur en fait une question ;
- la confirmation n'ajoute plus une question que le moteur pose déjà.

**La vérification** (consigne `verification-faits` v4) : une valeur voisine n'est pas la bonne. Quand la déclaration
nomme une autre chose que ce que décrit le sens de la valeur, c'est « non dit », même si les deux se ressemblent ;
l'exemple de la consigne est un seau renversé lu comme un aquarium. C'est la confusion du bain à bulles (`g2-p08`),
traitée sans ce cas de test : ni son texte, ni l'aide de sa valeur ne changent.

**La latence.** Le 95e centile d'un cas seul montait à 20 s, et jusqu'à 70 s : un appel sur dix restait bloqué chez
le fournisseur jusqu'au délai de 120 s. Pour l'analyse, le délai passe à **15 s**, avec une relance : une lecture
répond en 2 ou 3 s, un appel sans réponse en 15 s est bloqué, relancé il répond. La rédaction (Mistral Large, des
minutes) garde son délai long, sans relance. Les deux séries de bancs lancées en même temps (7.111) restent à éviter.

**Pas fait** : des exemples pour D. La banque est faite des faits idéaux validés du golden set, qui n'a pas de cas de D ;
il faut d'abord écrire et valider des cas de D (avec l'auteur), comme pour un nouveau jeu de test. Les alertes de
sécurité de GitHub : à relire après le push, MLflow et ses dépendances retirées (7.110) devraient en faire disparaître
la plupart.

Trois tests ajoutés.

### 7.115 Mesure de 7.114 : la latence réglée, la vérification v4 retirée

Bancs du 21 nov. (0 h 27 à 0 h 38), avec exemples : 178 tests passent ; jeu fermé A **92 %** (0,33 couvert à tort, le
vase ; 0,33 refus à tort, le vélo une fois), B **78 %** (0 couvert à tort), D **99 %** ; partie test de A **89 %**,
1,33 couvert à tort.

- **La latence est réglée** : 95e centile d'un cas seul 3,75 s (A), 6,14 s (B), 4,55 s (D), 5,89 s (test), contre
  20 à 70 s avant. La porte de latence passe partout. Le délai de 15 s avec une relance (7.114) fait ce qu'on attendait.
- **La vérification v4 est retirée.** Elle ne corrige pas le cas visé (`g2-p08`, le bain à bulles, toujours couvert
  3 fois sur 3) et elle sert aussi à la confirmation des faits décisifs, devenue trop stricte : deux cas de test,
  justes jusque-là, passent à « à préciser » 3 fois sur 3 (`red-b01`, l'intention ; `g2-p01`, le bien volé). La
  consigne revient en v3 (même texte, même empreinte) ; v4 reste archivée, notée retirée. Une consigne partagée par
  deux étapes se mesure sur les deux.
- **Une réserve revenait par l'exploration** : sur `g2-p08`, couvert, le déménagement était encore demandé. Le moteur
  classe toutes les variables inconnues qui pourraient changer la réponse ; ses questions sont maintenant réduites à
  celles que `points_a_preciser` a retenues. Un test ajouté.
- B à 78 % : les refus de `f-b10` et `f-b13` sont « à préciser » 3 fois sur 3, comme dans la série avec exemples de
  7.111 (82 %), alors que la série sans exemples donnait 90 %. Les exemples pourraient coûter à B sur ces deux cas :
  à vérifier sur une série sans exemples, après ces corrections.

### 7.116 Les exemples recopiés au socle : plus d'exemples au temps 1

Bancs du 21 nov. (12 h 42 et 12 h 45) : 179 tests passent ; partie test de A, avec exemples, **90 %**, 2 couverts à
tort ; jeu fermé de B **sans** exemples **88 %**, 0 couvert à tort, portes passées. Avec exemples, B faisait 82 % puis
78 % : l'écart se répète.

Les faits lus disent pourquoi. Sans exemples, `f-b10` (« la surtension a grillé mon vieux congélateur ») est lu bien =
électroménager, et refusé 3 fois sur 3 ; avec exemples, bien = électroménager **et denrées alimentaires**. `f-b13` (« ma
chaudière s'est mise à fuir, j'ai appelé l'assistance ») gagne l'événement **assistance** et un appareil. Small
recopiait au **socle** les biens et les événements des exemples proches (un congélateur dont les aliments sont perdus,
une chaudière dépannée). Or le socle n'est pas vérifié : seuls les faits du temps 2 passent par la vérification, qui
retire un fait recopié que la déclaration ne dit pas.

Correction : **le socle ne reçoit plus d'exemples** ; le temps 2 garde les siens (ceux du même événement), et ses
copies passent par la vérification. Reste à mesurer que le gain de A (7.111) ne venait pas du socle.

**Mesure (21 nov., 12 h 51 à 12 h 58).** 179 tests passent. Jeu fermé de B avec exemples : **82 %**, comme avant, mais
pas pour les mêmes cas. `f-b10` (le congélateur) est juste 3 fois sur 3 : la correction fait ce qu'elle visait. L'écart
avec la lecture sans exemples (88 %) tient à deux cas qui n'en viennent plus :
- `f-b13` (la chaudière, « contrat signé il y a deux semaines ») est maintenant lu avec l'événement **assistance**,
  alors que le socle ne voit plus d'exemples. Cette lecture est la bonne : la réponse attendue repose sur le délai
  d'attente de 30 jours de l'assistance (art. 3.1.12.6), que les règles de B ne codent pas. Sans exemples, le refus
  venait d'une autre lecture, juste par chance. C'est une règle qui manque, pas une erreur de lecture.
- `f-b06` (la porte laissée ouverte) a les mêmes faits lus avec et sans exemples ; il oscille à la confirmation des
  faits décisifs (« violence » non confirmée).

Jeu fermé de A : **92 %**, inchangé. Un couvert à tort sur trois passages (`f-a11`, un vase lu « verre de meuble »)
et un refus à tort (`f-a18`, le vélo lu une fois « véhicule à moteur ») : variance de lecture.

Partie test de A : **87 %** (90 % avant). Deux cas ont bougé :
- `g2-p01` (cambriolage sans dire ce qui a été volé) passe de couvert à « à préciser », 3 fois sur 3. Le bien volé
  venait des exemples du socle (« objet divers », « élément du bâtiment ») : la déclaration ne le dit pas. La réponse
  est maintenant honnête, mais elle n'est plus celle qu'attend le golden set.
- `g-p03` (la clé sous le paillasson) est couvert à tort 3 fois sur 3, contre 1 avant : Small lit bien = clés (les clés
  ont servi à entrer, elles n'ont pas été volées). C'est une erreur de lecture du bien, qui ne vient pas des exemples.

Bilan : pas de gain net mesurable sur 20 et 31 cas. La correction reste, parce qu'un bien deviné d'après un exemple est
exactement la recopie qu'on veut éviter.

Restent sur la partie test de A, avec ou sans cette correction : `g2-p08` (le bain à bulles), `red-b01` (« mon fils a
cassé la vitre avec un ballon » lu intentionnel, gardé par la garde de 7.44 parce que le retirer ferait couvrir), et
`val-01`, `g-p03` d'une série à l'autre.

### 7.117 Les biens et les événements vérifiés un par un

Après 7.116, les couverts à tort qui restent viennent du **bien** lu au temps 1 : des clés lues comme le bien volé
alors qu'elles ont servi à entrer, un vase lu « verre de meuble ». Deux trous dans le contrôle :
- la **vérification** ne regardait aucun fait du temps 1 (7.26 : retirés, ils rendaient tout incertain) ;
- la **confirmation** des faits décisifs jugeait une liste en bloc (« bien → canalisation, électroménager »), avec la
  question du vocabulaire (« quels biens sont endommagés ou volés ? »). Un bien seulement cité passait.

Ce qui change, sans appel de plus et sans toucher à la consigne de vérification (v3) :
- un bien ou un événement se juge **valeur par valeur** (`bien=cles`), et pour un bien la phrase à vérifier devient
  « ce bien a lui-même été volé, perdu ou abîmé (il n'est pas seulement cité, utilisé, ou à l'origine du dommage) » ;
- à la **vérification**, les biens et les événements lus **à plusieurs** sont soumis : la valeur en trop est retirée,
  **jamais la dernière** (c'est ce qui rendait tout incertain). Un bien seul n'y passe pas ;
- à la **confirmation**, un bien ou un événement qui porte la décision est jugé de la même façon ; non confirmé, la
  réponse devient « à préciser », comme pour tout fait décisif.

À dire avant de mesurer : la phrase sur le bien « seulement cité » est générale, mais l'idée vient de `g-p03` (la clé
sous le paillasson), un cas de la partie test, et de `f-a11`, du jeu fermé. Ces deux cas ne sont plus une mesure
indépendante de ce changement (leçon 119). Rien ne dit non plus que Small jugera mieux avec cette phrase : à mesurer.

**Mesure (21 nov., 13 h 18 à 13 h 26) : essai retiré.** Partie test de A **82 %** (87 % avant), couverts à tort 1,67
(2 avant) mais 1 refus à tort nouveau ; jeu fermé de A 93 %, couverts à tort 0,67 (0,33 avant) ; B 88 % ; D **96 %**
(99 à 100 % avant). Les faits lus disent pourquoi : Small, comme juge, se trompe autant que Small, comme lecteur.
- `g-h03` (« le fioul a imprégné le sol de ma cave ») : le bien « élément du bâtiment » est jugé non dit et retiré, d'où
  un refus à tort 3 fois sur 3.
- `f-d05` (porte forcée au pied-de-biche) : l'événement « vandalisme » et le « châssis » sont retirés, faux 3 fois sur 3.
- `bougie-05`, `g-l05` : le bien n'est plus confirmé, la réponse juste devient « à préciser ».
- En face, le gain est mince : `g-p03` n'est rattrapé qu'une fois sur trois, et `f-a11` (le vase) pas du tout.

Le code de 7.117 est donc retiré, comme la vérification v4 (7.115) : la lecture revient à l'état de 7.116. Ce que
l'essai apprend : la vérification sait dire si un fait est **écrit** ; elle ne sait pas dire si une **catégorie** est
la bonne (le sol est-il un « élément du bâtiment » ?). Ce choix-là ne se corrige pas par un second avis du même
modèle : il faut un meilleur lecteur (Mistral Large au temps 1, à mesurer) ou des exemples.

### 7.118 Un meilleur lecteur pour le seul temps 1 (à mesurer)

7.117 a montré que Small ne se corrige pas lui-même sur un choix de catégorie. Or les couverts à tort qui restent
viennent du temps 1 (le bien : des clés, un « verre de meuble »). L'essai : donner **ce seul appel** à Mistral Large
(`COUVERTURE_MODELE_SOCLE=mistral-large-latest`), les détails, la vérification et la confirmation restant à Small.
Un appel sur quatre : le surcoût en temps est à mesurer (Large en entier prenait 15 minutes par passage du banc).

Rien ne change sans la variable. Le rapport du banc porte « socle mistral-large-latest » dans son nom, pour ne pas
être comparé aux rapports de Small seul.

**Mesure (21 nov., 13 h 42 à 14 h 14) : trop lent, non retenu.** Les chiffres bruts (A test 83 %, A fermé 65 %, B 65 %,
D 64 %) ne mesurent pas la lecture : Mistral Large ne répond pas dans les 15 s accordées, même relancé (« pas de
réponse après 15 s » : 12 analyses sur 93 sur la partie test de A, 18 sur 60 sur le jeu fermé), et l'analyse rend alors
« à préciser ». Un cas seul prend 17 à 31 s en médiane, contre 4 s : la porte des 10 s est hors d'atteinte, quel que
soit le délai accordé.

Sur les seules analyses où Large a répondu : partie test de A, 73 justes sur 81 (90 %) et `g-p03` (la clé sous le
paillasson) n'est plus couvert à tort ; jeu fermé de A, 35 sur 42 (83 %). Sous-ensembles biaisés, sans conclusion
sur la qualité. La variable `COUVERTURE_MODELE_SOCLE` reste, éteinte par défaut, pour essayer un modèle intermédiaire.

### 7.119 Le vocabulaire en deux étages : le commun, et un fichier par contrat

Mesuré sur les trois contrats : les questions de départ sont presque communes (16 à 18 événements sur 21, 29 à 34
biens sur 46), mais sur les 145 variables de détail employées, 17 servent aux trois assureurs, 30 à deux, et 98 à un
seul. Tout était pourtant dans un seul fichier, `regles/vocabulaire.json` : on ne voyait pas ce qui est général.

`regles/vocabulaire/` le montre maintenant :
- `commun.json` : le socle (événement, bien, lieu) et les variables que plusieurs contrats emploient (50) ;
- `assureur-a-….json` (32), `assureur-b-….json` (48), `assureur-d-….json` (19) : celles qu'un seul emploie.

La règle de rangement est calculée, pas choisie : `repartir` lit les règles de chaque contrat. Accepter du vocabulaire
ou des règles range tout seul ; après des règles écrites à la main, `couverture regles --contrat … --ranger`. Un test
échoue si une variable n'est pas dans son fichier. Le reste du code voit toujours un seul vocabulaire
(`prolog.vocabulaire()`), et le moteur Prolog n'a pas changé : il reçoit les valeurs dans un fichier fusionné.

Deux choses à savoir :
- le contenu est identique, mais **l'ordre des variables change** (le commun d'abord, puis celles du contrat), donc
  l'ordre des questions dans la consigne du temps 2 aussi : à vérifier par un banc ;
- les 98 variables « d'un seul contrat » sont sans doute trop nombreuses : Mistral Large les a proposées contrat par
  contrat, et deux assureurs peuvent dire la même chose sous deux noms. Les doublons restent à chercher.

**Mesure (21 nov., 14 h 26 à 14 h 32).** 181 tests passent, les règles de A se chargent (298 couples employés, 0 hors
vocabulaire). Partie test de A **85 %** (87 % avant), B **88 %** (82 à 88 %), D **100 %** (99 à 100 %) : dans la
variation habituelle, le nouvel ordre des questions ne se voit pas. (D : un appel lent du fournisseur porte le 95e
centile à 37 s ; la médiane reste à 3,5 s.)

### 7.120 Les cas particuliers quittent la consigne, un par un

La consigne du temps 2 porte cinq phrases écrites pour un cas (le vol sur la personne, les flammes, « fermé à clé »,
le gel, « il y a deux semaines »). C'est ce qui attache le plus la lecture à l'habitation, et la banque d'exemples a
été faite pour les remplacer. Elles sortent une par une, avec un banc à chaque fois ; seulement celles que la banque
montre déjà (le vol sur la personne : 6 exemples ; les flammes : 5 et 3 ; « fermé à clé » : 3). Le gel (1 exemple), la
fenêtre ouverte et le dépôt chez un réparateur (0) attendent des déclarations validées. Les phrases du temps 1 restent :
il ne reçoit plus d'exemples (7.116).

**Première phrase retirée** (`lecture-details` v3) : « vol_sur_personne = oui seulement si le bien a été pris sur la
personne ». L'aide du vocabulaire le dit déjà mot pour mot (« objet arraché, ou pris dans une poche ou un sac que
vous portiez »), et 6 exemples le montrent. À mesurer.

**Mesure (21 nov., 14 h 41 à 14 h 49) : retrait gardé.** Partie test de A **86 %** (85 % avant), jeu fermé de A 88 %
(92 %), B **88 %** (88 %), D **100 %** (100 %). La lecture de `vol_sur_personne` ne change pas : les mêmes cas, à une
lecture sur trois près dans les deux sens, et aucun « oui » perdu (`f-b07`, le sac pris dans le bus, en gagne un). Les
4 points du jeu fermé de A viennent d'autres cas (`f-a02`, le fer à repasser ; `f-a12`, le congélateur), sans vol :
variation de lecture.

**Deuxième phrase retirée** (`lecture-details` v4) : « des flammes qui brûlent ou se propagent : flammes = oui et
embrasement = oui ; avec la chaleur, sans flamme décrite : flammes = non ». Plus risquée que la première : le
vocabulaire n'a **pas d'aide** pour ces deux variables, seuls 8 exemples le montrent (5 avec flammes, 3 sans), et le
fer à repasser (`f-a02`) comme les bougies bougent déjà d'un passage à l'autre. Si la lecture se dégrade, le repli
est de porter ce sens dans l'aide du vocabulaire, pas de remettre la phrase. À mesurer.

**Mesure (21 nov., 15 h 18 à 15 h 26) : ce retrait-là est annulé**, retour à la v3. Partie test de A 85 %, jeu fermé de
A 90 %, B 90 % : inchangés, et la lecture de `flammes` et d'`embrasement` est la même cas par cas. Mais D passe de 100 %
à **95 %**, pour un seul cas faux 3 fois sur 3 : `f-d01` (« une poêle d'huile s'est enflammée, la hotte et les
placards ont brûlé ») est maintenant lu `chaleur_sans_feu = oui`, alors qu'avant le modèle lisait « non ».

La phrase faisait donc plus que ce qu'elle dit : elle ancrait la différence entre le feu et la chaleur pour une
variable qu'elle ne nomme pas. D n'emploie ni `flammes` ni `embrasement`, seulement `chaleur_sans_feu`, qui n'a aucune
aide dans le vocabulaire, et la banque n'a pas d'exemple de D. Les exemples ne remplacent une phrase que là où ils
existent.

Le repli prévu (porter le sens dans l'aide du vocabulaire) reste la bonne voie, mais pas en le réglant sur `f-d01`,
qui est un cas du jeu fermé (leçon 119) : une aide pour `chaleur_sans_feu`, puis la mesure sur des déclarations
nouvelles. D'ici là, la phrase reste. Bilan de 7.120 : une phrase retirée sur deux essayées ; « fermé à clé » attend
la même précaution (regarder d'abord quelles variables la phrase touche, chez les trois assureurs).

### 7.121 Le banc dit d'où vient son taux : justes et fausses par réponse

Un taux de 88 % ne dit pas s'il vient d'une chaîne qui tranche bien ou d'une chaîne qui répond « à préciser » partout.
Le banc affiche maintenant, pour chaque réponse donnée, combien sont justes et combien fausses (moyenne par
exécution), en console (« Par réponse ») et dans le rapport. Sur les bancs de 14 h 41 :

| Banc | Couvert (justes / faux) | Non couvert | À préciser |
|---|---|---|---|
| A, partie test (31) | 14 / 2 | 9 / 0 | 3,7 / 2,3 |
| A, jeu fermé (20) | 7,3 / 0,7 | 4,3 / 0 | 6 / 1,7 |
| B, jeu fermé (20) | 8 / 0 | 3,7 / 0 | 6 / 2,3 |
| D, jeu fermé (25) | 9 / 0 | 9 / 0 | 7 / 0 |

Un « non couvert » n'est jamais faux. Les erreurs sont des « couvert » de trop chez A (la clé sous le paillasson, le
bain à bulles) et des « à préciser » de trop ; la chaîne tranche dans deux tiers des cas environ.

### 7.122 L'écran tient dans la fenêtre

Sur un portable (fenêtre de 1366 × 650 ou 1536 × 730), la colonne de gauche débordait : le bouton « Analyser » était
sous le bas de l'écran, il fallait faire défiler pour le trouver. Mesuré sur une maquette statique de l'écran (le
gabarit et les styles, rendus par Chromium à trois tailles) : 1017 px de contenu pour 421 px de hauteur.

Ce qui change : la zone de saisie prend la hauteur qui reste au lieu d'une hauteur fixe ; les trois temps (lire,
décider, vérifier) passent dans l'accueil, à droite, où la place existe ; les exemples ont un titre court sur le
bouton (le texte complet va dans la saisie) ; le compteur rejoint la ligne des boutons ; les tailles de texte
descendent d'un cran (16 px de base). Fenêtre étroite ou très basse : une colonne, et la page défile. Après : la
colonne de gauche tient aux trois tailles, « Analyser » toujours visible. Non vérifié ici : la compilation Angular
(`npm run build`, `npm test`) et le rendu réel avec la police Barlow.

### 7.123 La même déclaration, des lectures différentes : une graine fixe (à mesurer)

Vu par l'auteur dans l'interface, et retrouvé dans le journal des analyses (21 nov., 15 h 31 à 15 h 35) : le premier
exemple proposé à l'écran (« en faisant du vélo dans le parc, j'ai renversé un piéton »), soumis cinq fois au contrat
A, a donné **non couvert** deux fois, **couvert** une fois et **à préciser** deux fois ; l'événement est lu tantôt
« responsabilité », tantôt « heurt ». Les bancs le disaient déjà pour le cas voisin `f-a18` : sur 15 lectures du jour,
4 lisent le vélo « véhicule à moteur » (d'où un refus à tort), alors que l'aide du vocabulaire dit l'inverse en
toutes lettres.

La température est à 0, mais les appels ne portaient pas de graine. Mistral documente `random_seed` : avec lui, des
appels identiques doivent donner des résultats reproductibles. Chaque appel porte maintenant `random_seed = 0`
(`COUVERTURE_GRAINE` pour changer la valeur ou s'en passer).

Ce que la graine peut et ne peut pas faire : elle peut rendre la réponse **stable** (la même déclaration, la même
lecture), pas **juste** : une lecture fausse deviendrait fausse à chaque fois. À regarder au banc : la ligne
« instables », et les cas qui se figent du mauvais côté. Si l'instabilité demeure, la piste suivante est de lire deux
fois et de répondre « à préciser » quand les deux lectures divergent sur un fait qui porte la décision.

**Mesure (21 nov., 16 h 20 à 16 h 30) : la graine ne stabilise pas la lecture.** Jeu fermé de A 87 %, partie test de
A 85 %, B 85 %, D 100 % : dans la variation habituelle. Instables : 2, 1, 3, 0 (avant : 3 à 4, 2, 1 à 5, 0 à 1). Et
la mesure directe, les faits lus aux trois passages d'un même banc : identiques pour 35 déclarations sur 96 avec la
graine, 30 sur 96 sans. Deux lectures sur trois de la même phrase diffèrent donc toujours, le plus souvent sur un
fait qui ne change pas la décision. `random_seed` reste envoyé (il ne coûte rien), mais il ne faut pas en attendre la
reproductibilité.

Ce que ces passages apprennent de plus utile : les erreurs qui restent ne sont **pas** de l'instabilité. `f-a11` (le
vase lu « verre de meuble »), `g-p03` (la clé), `g2-p08` (le bain à bulles), `red-b01`, `g2-p01`, `f-a14`, `f-b06`
sont faux **trois fois sur trois**, avec la même lecture. Lire deux fois et comparer ne les verrait pas : les deux
lectures seraient d'accord sur l'erreur. La piste de la double lecture est donc écartée sans être codée ; ce qu'il
faut, c'est un lecteur qui choisit mieux la catégorie, donc plus d'exemples validés.

### 7.124 « D'où venait l'eau ? » pour un piéton renversé à vélo

Vu par l'auteur à l'écran, contrat D : la déclaration du vélo et du piéton est couverte par la responsabilité civile
vie privée, mais « à demander au client » proposait deux réserves sans rapport : « d'où venait l'eau ? » et « le
dommage vient-il de l'usure ou d'un manque d'entretien ? ». Elles viennent d'exclusions que les règles rattachent à
la garantie ; le moteur les rend en réserves (l'assureur aurait à les prouver), et l'écran les montrait toutes.

Or le vocabulaire sait déjà qu'elles sont hors sujet : `cause_eau` ne vaut que pour un dégât des eaux ou une
catastrophe naturelle (« pour »), et la lecture retire un tel fait quand l'événement est autre
(`prolog.filtrer_faits`). La réponse du client aurait donc été jetée. La même règle s'applique maintenant aux
réserves : `points_a_preciser` reçoit les événements lus et ne pose pas une réserve hors sujet ; « une seule question
tranche » ne cite plus une question qu'on ne pose pas ; et quand il ne reste aucune réserve à montrer, la réponse ne
dit plus « sous réserve des vérifications à faire » et la confiance reste à 85 %.

La règle de D est juste : c'est une exclusion générale du contrat (le manque d'entretien, sauf pour un dégât des
eaux dû au gel), rattachée à toutes les garanties, d'où `cause_eau` dans ses conditions. C'est l'affichage qui
manquait de discernement, pas les règles.

### 7.125 Deux défauts vus à l'écran : la revue de tout ce qu'on demande au client

Deux défauts trouvés par l'auteur en dix minutes d'essais (7.123, 7.124) : les bancs ne les voyaient pas, parce
qu'ils notent la décision, pas ce que l'écran demande. La revue est donc faite par le code, et elle reste en test
(`tests/test_questions.py`) : pour chaque contrat, sur chaque événement seul, sur chaque événement avec un bien et un
lieu, et sur les faits idéaux de tous les cas (267 situations), l'oracle décide et on vérifie que chaque point demandé
peut servir. Trois défauts de plus :

- **Une réponse jetée** (6 situations, contrats B et D) : pour un « accident », la plainte déposée ou le véhicule
  identifié étaient demandés, mais ces questions ne valent que pour un « heurt », et la réponse du client était retirée
  comme hors sujet. Le vocabulaire dit pourtant qu'un accident compte comme un heurt ou un bris : `filtrer_faits`
  suit maintenant cette hiérarchie (`evenements_etendus`).
- **Une question déjà répondue** (8 situations, contrat A) : « d'où venait l'eau ? » en réserve, alors que la
  déclaration avait dit la cause. Une réserve sur un fait connu avec précision n'est plus posée.
- **Une question sans bouton** (3 situations, contrat A) : le lien de causalité d'une obligation de prévention
  arrivait dans les points à préciser sans réponses possibles. Il reste dans les questions en phrase, pour le
  gestionnaire ; il n'est plus proposé comme point à cliquer.

Ce que la revue ne corrige pas : sur un événement donné seul, certains contrats posent jusqu'à 12 questions (un vol
chez B). Une vraie déclaration en dit plus, et le moteur classe les questions décisives en tête ; à surveiller.

Ce que la revue ne couvre pas : la lecture par le modèle (c'est le rôle des bancs), et l'écran lui-même.

L'écran dit maintenant « Lire l'article entier » sur chaque clause citée : le texte complet était déjà en base et
s'ouvrait au clic, mais rien ne l'indiquait.

### 7.126 Les clauses citées : une ligne par article, l'article entier dans une fenêtre

À l'écran, la liste des clauses citées répétait le même article autant de fois qu'il avait d'extraits (trois lignes
« Art. 12/contenu », trois « Art. 12/batiment »), et le texte complet s'ouvrait dans la liste, qui s'allongeait encore.
Demande de l'auteur : un lien qui ouvre l'article entier dans une fenêtre.

- Les citations sont regroupées par article (`citationsParArticle`) : un article, une ligne, ses extraits dessous.
- Le numéro de l'article est un lien : il ouvre une fenêtre avec le chemin dans le contrat, les pages et le texte
  entier de la clause, tel qu'il est en base ; les extraits cités y sont surlignés (`surligner`). Échap, le bouton
  « Fermer » ou un clic hors de la fenêtre la referment.
- Si un extrait n'est pas retrouvé tel quel dans le texte (espaces ou retours à la ligne différents), l'article
  s'affiche sans surlignage pour cet extrait.

Les deux fonctions sont testées (vitest). Non vérifié ici : la compilation Angular et le rendu réel.

### 7.127 « Je ne peux pas trancher », dit dans les mots du client

Vu à l'écran, contrat A, le vélo et le piéton : le modèle a lu « véhicule à moteur », la confirmation ne l'a pas
retrouvé dans la déclaration, et la réponse est passée à « à préciser » avec la bonne question (qu'est-ce qui a causé
le dommage ?). Le garde-fou a donc fait son travail : sans lui, la réponse était un refus à tort. Mais la phrase
affichée était illisible : « la déclaration ne dit pas clairement « origine_rc : … → vehicule_moteur (une voiture…) ».
Couvert. … », soit un nom de variable, la valeur écartée, puis « Couvert. » juste après « je ne peux pas trancher ».

La phrase devient : « Je ne peux pas trancher : la déclaration ne répond pas clairement à « Qu'est-ce qui a causé le
dommage à l'autre personne ? » Selon la réponse, la décision change. Garantie en jeu : … ». La question, pas la
variable ; et plus de décision annoncée à contresens.

### 7.128 Une réponse « couvert » ne pose pas de question

Vu à l'écran, contrat A, « le tuyau de ma machine à laver a éclaté » : couvert, et pourtant un encadré « à demander
au client » avec « d'où venait l'eau ? » (déjà lu : une fuite d'installation) et « pendant le gel, le chauffage
était-il maintenu ? ». Et la question revenait après la réponse. Deux causes :

- une **réserve** n'est pas une question : la réponse est donnée, ce sont des points que l'assureur pourra vérifier
  (une exclusion qu'il aurait à prouver). L'écran les présentait pourtant comme des questions à cliquer ;
- « fuite d'installation » est une valeur large, qui regroupe « gel » : le moteur voulait la préciser, l'écran
  reproposait toutes les valeurs, le client recliquait « fuite d'installation », et rien n'avait changé.

Ce qui change :
- l'écran sépare les deux : « à demander au client » ne contient que les **questions** (sans elles, pas de décision) ;
  les réserves sont une liste à lire, « ce que l'assureur pourra vérifier », sans bouton ;
- une réserve sur un fait déjà connu, même en gros, n'est plus listée ;
- une question sur un fait connu en gros ne propose que ses précisions (`valeurs_proposees`), jamais la valeur déjà
  connue : la revue de 7.125 le vérifie maintenant sur toutes les situations ;
- une réponse « couvert » n'annonce plus « ces deux questions tranchent ».

Reste : « pendant le gel… » figure encore dans les réserves d'une fuite de machine à laver. C'est logique pour le
moteur (une fuite peut venir du gel), peu parlant pour un lecteur ; le vocabulaire ne sait pas dire « une fuite, mais
pas le gel ».

### 7.129 La note de conception en tête du README

L'énoncé attend surtout « vous l'avez déjà fait, et vous racontez ce que ça a donné ». Le récit existait, mais dans
ce fichier de plus de 4 000 lignes. Le README s'ouvre maintenant sur une note de deux pages : le besoin, le choix, les
deux questions de l'énoncé, les mesures du jour, un tableau des essais avec leur mesure et la décision prise (échecs
compris), ce que coûte un contrat de plus, les limites ; puis un déroulé de démonstration en 5 minutes. Les anciens
résultats (97 cas, 15 cas pour B) en sont retirés : ils dataient d'avant les jeux fermés.

### 7.130 La fiche d'analyse, en PDF

Le poste demande aussi de **produire** des documents, « avec notre charte graphique » ; le projet n'en produisait
aucun. Il en produit un, celui qu'un gestionnaire verserait au dossier : la fiche d'analyse d'un sinistre.

- `fiche.py` met en page une réponse de l'API, sans rien recalculer : la déclaration, la décision et son motif, les
  faits retenus, ce qu'il faut demander au client ou ce qui reste sous réserve, les clauses citées regroupées par
  article (numéro, pages, phrase exacte), les limites, les contrôles de la lecture, et la mention que la fiche ne
  remplace pas l'examen par un gestionnaire. Couleurs de l'écran ; ni logo, ni nom de marque.
- `POST /api/v1/fiches` la renvoie en PDF ; à l'écran, « Télécharger la fiche (PDF) » sous chaque décision.
- `reportlab`, déjà employé par les tests, devient une dépendance du projet (`uv lock`).

Vérifié ici : la fiche se produit, tient en une page sur un cas complet, et son texte porte la décision, les
articles et les questions (deux tests). Non vérifié ici : la route (FastAPI n'est pas installé dans cet
environnement ; un test l'attend chez l'auteur) et le bouton (compilation Angular).

### 7.131 Le piéton renversé lu « heurt » ; une question à 46 boutons

Vu à l'écran, contrat A, toujours le vélo et le piéton : cette fois l'événement est lu « heurt » seul, et non
« responsabilité ». La réponse part vers le pack multimédia (qui couvre le heurt du matériel informatique), et la
question « quels biens sont endommagés ? » s'affiche avec ses 46 valeurs en boutons.

- **La lecture.** L'aide de « heurt » disait « un véhicule, un arbre ou un objet a percuté le bâtiment ou les biens de
  l'assuré » ; elle ne disait rien d'une personne. Elle dit maintenant qu'une personne heurtée, renversée ou blessée
  par l'assuré relève de « responsabilite ». À dire : l'exemple de l'écran reprend presque mot pour mot `f-a18`, un
  cas du jeu fermé de A ; ce cas n'est donc plus une mesure indépendante de cette aide (leçon 119), et les exemples
  de l'écran ne devraient pas venir d'un jeu de mesure.
- **L'écran.** Au-delà de 10 réponses possibles, une question s'affiche en liste déroulante.

Non mesuré : l'effet de la nouvelle aide (un banc de A le dira), ni l'écran (compilation Angular).

### 7.132 L'aide ne suffit pas : une règle dans la consigne du temps 1 (à mesurer)

Après 7.131, même essai à l'écran : l'événement est encore lu « heurt ». La liste déroulante fonctionne ; l'aide du
vocabulaire, elle, n'a rien changé. Le temps 1 ne reçoit pas d'exemples (7.116) : il ne reste que sa consigne. Une
règle y est ajoutée (`lecture-socle` v3) : une personne blessée, ou le bien de quelqu'un d'autre abîmé, par l'assuré,
un proche ou son animal, c'est « responsabilite », même s'il y a eu un choc ; « heurt » ne vaut que pour ce qui a
percuté le bâtiment ou les biens de l'assuré.

C'est aller contre 7.120 (sortir les cas particuliers de la consigne), et c'est dit : la responsabilité civile n'est
pas un cas particulier de l'habitation mais une garantie de tout contrat, et aucun autre levier n'atteint le temps 1.
Small a déjà ignoré des règles écrites (7.25) : cinq essais à l'écran, puis un banc, diront si celle-ci tient. Même
réserve que 7.131 sur `f-a18`.

### 7.133 Pas de rustine : les deux corrections sont retirées, et la règle est posée

L'auteur, après 7.131 et 7.132 : « ce n'est pas généralisable ; je ne veux pas de rustine, je veux des règles claires,
pas du cas par cas ». Il a raison : trois corrections en une heure pour la même phrase (une aide, une autre aide, une
règle de consigne), dont aucune mesurée, et la deuxième n'avait rien changé. L'aide de « heurt » et la règle du temps 1
sont **retirées** (`lecture-socle` revient à la v2).

**La règle, désormais.** Une erreur de lecture ne se corrige plus en ajoutant une phrase pour ce cas :
1. une **consigne** ne contient que des principes de lecture valables pour tout contrat ;
2. le **vocabulaire** définit chaque valeur une fois, avec les règles du contrat ; on n'y ajoute pas une aide parce
   qu'une phrase a été mal lue ;
3. une lecture se corrige par des **exemples validés**, mesurés sur des cas qui n'ont pas servi à les choisir ;
4. quand l'erreur vient de la **structure** du vocabulaire, c'est la structure qu'on corrige ;
5. ce qui reste mal lu reste une **limite écrite**, que les garde-fous ramènent à « à préciser ».

**Le cas du piéton relève du point 4.** « Événement » mélange deux choses : ce qui s'est passé (un vol, un incendie, un
heurt) et la nature de la demande (« responsabilité », « assistance », « litige »). Un cycliste qui renverse un piéton,
c'est bien un heurt, **et** c'est une affaire de responsabilité : le modèle doit choisir entre deux réponses vraies. La
correction de structure : séparer les deux questions. « Qui a subi le dommage : l'assuré, ou quelqu'un d'autre ? »
existe déjà (`victime`), mais n'est posée que si l'événement est déjà « responsabilité ». Posée au temps 1, pour tout
sinistre, elle fait de la responsabilité une conséquence calculée par le code (un tiers a subi le dommage), plus un
mot à deviner. À faire, et à mesurer sur les trois contrats.

### 7.134 L'analyse racontée pendant qu'elle se fait

Demande de l'auteur : une fenêtre qui dit ce que le modèle fait au fur et à mesure, comme dans SortirIA. Pendant les
quelques secondes d'une analyse, l'écran ne montrait qu'un « analyse en cours ».

- La lecture et la chaîne acceptent un `suivi` : appelé au début de chaque étape, puis à sa fin avec ce qu'elle a
  donné, en une phrase (« evenement : vol ; bien : velo ; lieu : cave », « retiré, car non dit : fermeture »,
  « le moteur répond : non couvert »). Cinq étapes : la première lecture, les détails, la vérification, la décision
  du moteur, la confirmation des faits décisifs.
- `POST /api/v1/analyses/suivi` rend la même réponse que `/analyses`, précédée d'une ligne JSON par événement
  (`application/x-ndjson`). L'analyse tourne dans un fil ; une panne du modèle arrive dans le flux.
- À l'écran, « Analyser » ouvre une fenêtre avec les cinq étapes : en attente, en cours, faite, et ce que chacune a
  donné. Elle se referme seule une seconde après la fin, et la décision s'affiche.

Ce n'est pas un décor : chaque ligne vient de l'étape réelle, au moment où elle se termine. Vérifié ici : l'ordre et
le contenu des appels de suivi (un test) ; la fenêtre, sur une maquette. Non vérifié ici : la route en flux (FastAPI
absent de cet environnement ; un test l'attend chez l'auteur) et l'écran (compilation Angular, passage du flux par
le serveur de développement).

**Mistral Medium.** Essai de l'auteur à l'écran (`COUVERTURE_MODELE=mistral-medium-latest`) : la lecture lui paraît
meilleure et le temps de réponse acceptable. C'est une impression sur quelques essais ; les bancs restent à passer
avant d'en faire le modèle de l'analyse.

### 7.135 La fiche PDF joint les articles cités, en entier

Demande de l'auteur. Après la page de synthèse, la fiche ajoute « Les articles cités, en entier » : pour chaque article
cité, son chemin dans le contrat, ses pages et le texte complet de la clause, lu dans la base par la route, avec les
passages cités surlignés. Le lecteur de la fiche n'a plus à ouvrir le contrat. Un extrait qui ne se retrouve pas tel
quel n'est pas surligné ; un article absent de la base est simplement omis. Vérifié ici sur un PDF produit (un test).

### 7.136 Mistral Medium lit mieux, mais vérifie trop sévèrement : celui qui lit n'est pas celui qui vérifie

Bancs du 22 nov. (13 h 15 à 13 h 21), toute l'analyse par Mistral Medium (`COUVERTURE_MODELE=mistral-medium-latest`),
192 tests passés :

| Banc | Small (21 nov., 16 h 20) | Medium |
|---|---|---|
| A, jeu fermé | 87 %, 1 couvert à tort, 2 instables | **92 %**, **0**, 1 |
| A, partie test | 85 %, 2 couverts à tort, 1 instable | **90 %**, **0**, 0 |
| B, jeu fermé | 85 %, 0, 3 instables | 80 %, 1 couvert à tort, 0 |
| D, jeu fermé | 100 %, 0, 0 | 92 %, 1 refus à tort, 0 |

Ce que Medium apporte : **plus aucun couvert à tort chez A** (la clé sous le paillasson, le bain à bulles et le vase
sont bien lus), une lecture **stable** (faits identiques aux trois passages pour 63 déclarations sur 96, contre 35 avec
Small ; 1 cas instable sur 96 au lieu de 6), et un temps égal (3,5 à 3,9 s par cas, sans les appels bloqués de Small).

Ce qu'il coûte, et pourquoi : sur 288 analyses, la **confirmation** des faits décisifs a refusé 17 fois un fait du
temps 1 (11 fois le lieu, 5 fois le bien, 1 fois l'événement), toujours sur une réponse qui était juste, devenue « à
préciser ». Avec Small, ce refus n'arrive jamais sur ces faits. Medium, comme vérificateur, ne reconnaît pas ce que la
déclaration implique (« la chambre » : le logement). C'est la quasi-totalité de ce que B et D perdent.

La conséquence n'est pas une consigne de plus, c'est une séparation des rôles : **celui qui lit n'est pas celui qui
vérifie**. `COUVERTURE_MODELE_VERIFICATION` donne la vérification des faits lus et la confirmation des faits décisifs
à un autre modèle que la lecture. À mesurer : Medium qui lit, Small qui vérifie.

Restent, avec Medium, des erreurs de lecture propres : `f-b18` (un vol dans une voiture, couvert au lieu de « à
préciser », 3 fois sur 3) et `f-d08` (une crue avec arrêté de catastrophe naturelle, refusée 3 fois sur 3).

**Mesure (22 nov., 13 h 30 à 13 h 36) : gardé.** Medium lit, Small vérifie (`COUVERTURE_MODELE_VERIFICATION`), 193 tests
passés :

| Banc | Small seul | Medium seul | Medium lit, Small vérifie |
|---|---|---|---|
| A, jeu fermé | 87 %, 1 couvert à tort | 92 %, 0 | **98 %**, 0,3 |
| A, partie test | 85 %, 2 | 90 %, 0 | **90 %**, 0 |
| B, jeu fermé | 85 %, 0 | 80 %, 1 | 82 %, 1 |
| D, jeu fermé | 100 %, 0 | 92 %, 1 refus à tort | **96 %**, 1 refus à tort |

Les refus d'un fait du temps 1 par la confirmation tombent de 17 à 2 sur 288 analyses. Temps par cas : 4 à 4,8 s en
médiane, 5,7 à 7 s au 95e centile, sous la porte des 10 s. Instables : 2 cas sur 96.

Ce qui reste, à l'identique aux trois passages : `f-b18` (couvert à tort : un ordinateur volé dans une voiture, la
vitre brisée ; il fallait demander une précision), `f-d08` (refus à tort : une crue avec arrêté, lue sans bien touché),
et des « à préciser » de trop (`f-b06`, `f-b07`, `velo-06`, `val-09`, `g2-p01`). B est le seul contrat sous Small seul
(82 % contre 85 %) : trois points sur 20 cas, dans la variation, mais `f-b18` est un couvert à tort que Small n'avait
pas. C'est la configuration retenue pour la démonstration ; le README porte ces mesures.

### 7.137 Les faits s'affichent avec leurs libellés, écrits dans le vocabulaire

**Le constat (22 nov., sur la fiche PDF).** La fiche et l'écran montraient les identifiants du moteur : « evenement responsabilite », « origine rc velo trottinette ». Et la justification citait « (4~1) » : le numéro d'un morceau d'article dans la base, pas celui du contrat.

**La règle.** Ce qu'on montre d'un fait se définit là où le fait est défini, une fois :

- chaque variable du vocabulaire porte un `libelle` (« À l'origine du dommage ») ;
- une valeur porte un libellé (`libelles`) seulement quand l'identifiant sans tirets bas s'écrit mal (« velo_trottinette » → « vélo ou trottinette ») ; sinon l'identifiant suffit (« tiers », « cave ») ;
- `prolog.libelle` et `prolog.faits_affiches` sont le seul endroit qui les lit ; l'API rend `faits_affiches` à côté de `faits`, et `libelles` dans chaque point de `a_preciser` ; l'écran et la fiche n'affichent que cela ;
- un numéro d'article s'affiche comme dans le contrat (`chaine.numero` : « 4~1 » → « 4 »).

Les libellés ne sont pas envoyés au modèle : les consignes ne changent pas, les mesures non plus.

**Le contrôle.** `test_libelles_du_vocabulaire` : toute variable a un libellé, et aucun libellé ne vise une valeur qui n'existe pas. Une variable ajoutée par la rédaction sans libellé fait échouer ce test : il faut l'écrire en l'acceptant.

**Limite.** Les 149 libellés ont été écrits à la main d'après la question de chaque variable ; la rédaction par Mistral Large ne les propose pas encore.

### 7.138 Une variable sans événements n'est permise que si une règle vaut pour tout

**Le constat (22 nov., à l'écran).** Un piéton renversé à vélo, chez A : les faits retenus affichent « Assuré absent : non ». Le fait est hors sujet, et pourtant ni lu à part ni retiré.

**La cause.** Le vocabulaire dit, pour chaque variable, les événements où elle se lit (« pour ») ; la rédaction le calcule d'après les garanties qui l'emploient (7.56, 7.63). 144 variables sur 149 l'ont. « absence », écrite à la main avant ce mécanisme, ne l'avait pas : elle était donc lue pour tout sinistre, alors que les règles de A ne l'emploient que pour le vol et le vandalisme (2.10, 2.11), comme `portes_fermees` et `fenetres_fermees`.

**La règle.** Une variable hors du socle sans « pour » est lue partout : ce n'est permis que si une règle qui vise toutes les garanties (`tous`) l'emploie, comme `auteur` (l'exclusion du fait intentionnel chez D). `test_variable_sans_evenements_seulement_si_une_regle_vaut_pour_tout` le contrôle sur les règles de tous les contrats. « absence » reçoit les événements de ses voisines : vol, vandalisme.

**L'effet sur le golden set.** Six cas hors vol portaient « absence » dans leurs faits idéaux (les bougies, deux dégâts des eaux, un « autre ») : le filtre les retire désormais, et le test de conformité du golden au filtre l'exige. Retirés des faits idéaux, mécaniquement (aucune décision attendue ne change) ; golden set figé en **version 13**, avec la raison.

**La mesure (22 nov., 15 h).** Partie test de A : 90 % justes, aucun couvert ni refus à tort, les trois mêmes « à préciser » de trop (`velo-06`, `val-09`, `g2-p01`), rappel des faits 89 % (89,9 % avant). Jeu fermé de A : 100 % (98 % avant), aucune erreur. Rien ne bouge, comme attendu d'un changement qui ne retire qu'un fait hors sujet. La porte « décisions changées par la lecture ≤ 2 » échouait déjà à 4 avant ce changement : elle vient de ces trois cas, pas de celui-ci.

### 7.139 Piste écartée : demander la victime pour tout sinistre

**L'idée.** Poser « qui a subi le dommage ? » dès le temps 1, et laisser le code en déduire la responsabilité civile, au lieu de laisser le modèle choisir l'événement « responsabilité ».

**Ce que disent les mesures.** Relus un par un, les neuf cas en erreur des bancs du 22 nov. (partie test de A, jeux fermés de A, B et D) ne contiennent aucune erreur de responsabilité civile. Deux familles s'y voient : le bien n'est pas dit dans la déclaration (`g2-p01`, `val-09`, `f-b13`, `f-d08`), et un fait non dit est demandé là où l'annotateur a conclu « non » (`f-b06`, `f-b07`, `velo-06`). Restent `f-b18` (la vitre de la voiture lue comme un bris de vitrage) et `f-a02` (instable).

**La décision.** Écartée : elle change la première lecture des trois contrats, elle croise des faits existants (le propriétaire des biens, le bien confié) avec un risque de couvrir à tort (la vitre du voisin lue comme bris et comme responsabilité), et aucune mesure ne montre de gain. Les deux familles d'erreurs ne sont pas corrigées d'après ces cas (leçon 119) : elles relèvent d'exemples validés nouveaux (point 5 du plan).

### 7.140 Le vocabulaire en chiffres : ce qu'un contrat partage, ce qu'il est seul à employer

**La question.** « Comment tenir des centaines de contrats ? » dépend de ce que coûte un contrat de plus en vocabulaire. `couverture regles --contrat … --bilan` le calcule d'après les règles (`redaction.bilan`).

| Contrat | Variables employées | Partagées avec un autre | Propres |
|---|---|---|---|
| A | 76 | 44 (58 %) | 32 |
| B | 92 | 44 (48 %) | 48 |
| D | 48 | 29 (60 %) | 19 |

Sur 149 variables, 99 ne servent qu'à un contrat. Elles ne pèsent pas toutes sur la lecture :

- **16 sont des faits de souscription** (une option, un pack, une garantie mentionnée aux conditions particulières ; 19 avec les trois du commun). La déclaration ne les dit jamais : elles relèvent des conditions particulières (point 7 du plan), pas du vocabulaire de lecture.
- **13 autres ne sont jamais lues dans une déclaration** (réserve d'une exclusion, garantie accessoire, extension).
- **70 sont lues dans la déclaration.**

**Les doublons, relus à la main parmi ces 70** (questions comparées une à une, entre contrats et avec le commun). Rien n'est fusionné : fusionner change la lecture, donc se mesure.

| Groupe | Variables | Nature |
|---|---|---|
| Clés laissées dehors | `cles_a_proximite` (A), `cles_deposees_exterieur` (D) | même question |
| Travaux au bâtiment | `travaux_construction` (B), `travaux_batiment` (commun) | même question, valeurs à aligner |
| Fermeture du local | `fermeture` (A), `serrure_cylindre` (B), `serrure_surete` (commun) | une seule variable à plusieurs valeurs |
| Canalisation | `canalisation_enterree` (D), `canalisation_encastree` (commun, employée par aucune règle) | une seule variable à plusieurs valeurs |
| Vitesse du vent | `vent_80_kmh_irm` (commun), `vent_100_kmh` (D) | même grandeur, seuils différents |
| Durée d'inoccupation | `batiment_vacant_90j` (A), `local_inoccupe_12_mois` (D) | même grandeur, seuils différents |
| Depuis le déménagement | `emmenagement` (A), `duree_demenagement` (B) | même grandeur, seuils différents |
| Dégâts aux alentours | `vent_dommages_voisins` (commun), `neige_dommages_voisins` (D) | même question, phénomène différent |

Huit groupes, une dizaine de variables de moins si on les fusionnait : **environ une sur sept** des 70. Le reste est vraiment propre : « murs à plus de 50 % en matériaux légers », « construit plus de 18 mois après le classement de la zone ».

**Ce que cela dit pour cent contrats.**

- Un contrat réemploie la moitié de ses variables ou plus (48 à 60 %). Le troisième (D) n'en a ajouté que 19, dont 9 de souscription ou jamais lues.
- Trois contrats ne donnent pas une courbe. Ce qui se mesure : la part réemployée par contrat ; ce qui ne se mesure pas encore : si elle monte avec le nombre de contrats.
- Trois patrons reviennent et se prêtent à une règle : la souscription (hors de la lecture), les seuils (une grandeur, des valeurs graduées), la fermeture (une variable à valeurs). Les règles d'un contrat ne liraient alors que le seuil qui les concerne.

**Limite.** La relecture des doublons est manuelle. Pour cent contrats, il faudrait la proposer à la rédaction (comparer la question d'une variable nouvelle à celles qui existent, par mistral-embed, avant de l'accepter).

### 7.141 Les conditions particulières se donnent avec la déclaration

**Le constat (bilan 7.140).** 19 variables portent sur ce que le client a souscrit : la formule, une option, un pack. Le système les demandait au client ou les gardait en réserve (« sous réserve des conditions particulières »), alors qu'un gestionnaire a le contrat du client sous les yeux.

**La règle.** Un fait a une source. Elle s'écrit une fois, dans le vocabulaire : `source : conditions_particulieres`. Le reste en découle :

- `prolog.souscription(contrat)` : ce que les conditions particulières précisent pour ce contrat, c'est-à-dire les variables de cette source que ses règles emploient (2 chez A, 14 chez B, 6 chez D), avec ses valeurs à lui (`par_contrat` : les formules de B ne sont pas celles de D) ;
- l'analyse accepte une `souscription` facultative (`POST /analyses`, `/analyses/suivi`) ; ces faits s'ajoutent à ceux lus dans la déclaration et l'emportent sur eux, car le contrat fait foi ;
- un fait donné ainsi n'est pas soumis à la confirmation sur la déclaration : il n'en vient pas ;
- l'option d'un autre contrat ou une valeur inconnue est ignorée et signalée, jamais devinée ;
- `GET /contrats` publie la liste ; l'écran la propose sous le choix du contrat, repliée, chaque point « non renseigné » par défaut ;
- à l'affichage, ces faits viennent après ceux de la déclaration ; une question sur la formule ne propose que les formules du contrat.

Sans souscription donnée, rien ne change : la chaîne mesurée est la même, aucun banc à relancer.

**Ce qui n'a pas été fait : retirer ces variables de la lecture.** C'était l'étape suivante (« la déclaration ne les dit jamais »). Avant de la coder, le golden set a répondu : trois déclarations de B disent « j'ai la formule Privilège » (`b-v05`, `b-v06`, `b-v08`), et la formule figure dans leurs faits idéaux. Cesser de la lire aurait changé ces réponses en « à préciser ». La lecture reste donc inchangée, un test le garde (`test_la_declaration_peut_encore_dire_la_formule`), et le bilan dit « la déclaration ne les dit que parfois ». Les 16 variables de souscription propres à un contrat restent lues ; ce qui change, c'est qu'on n'a plus à les demander.

**Limites.** L'entrée est une saisie ou un objet JSON, pas le document des conditions particulières du client. La question de `formule` garde sa parenthèse « (Privilège, Active, standard) », fausse pour D : la corriger change la consigne de lecture, donc se mesure.

### 7.142 Sans événement lu, le moteur n'est pas interrogé

**Le constat (22 nov., à l'écran).** Un texte qui n'est pas une déclaration (une consigne collée par erreur dans la zone de saisie) : le modèle ne lit aucun événement, et la réponse était « à préciser », avec toutes les garanties du contrat citées (« pourrait s'appliquer, selon des faits non précisés ») et « Une seule question tranche : d'où venait l'eau ? ». Rien de faux dans la décision, mais une réponse qui ne veut rien dire.

**La cause.** Sans événement, le moteur ne peut écarter aucune garantie : il les rend toutes possibles, et l'exploration choisit une question parmi les leurs.

**La règle.** Les règles ne s'appliquent qu'à un sinistre. Sans événement lu, `PipelineRegles.analyser` ne les interroge pas : la réponse est « à préciser », dit « je n'ai pas reconnu de sinistre dans ce texte », ne cite aucune garantie et pose une seule question, « que s'est-il passé ? ». L'API la rend avec ses réponses possibles : en choisir une relance la décision sur les faits. La décision reste « à préciser », comme avant : les bancs ne changent pas.

### 7.143 Le rôle d'une citation est celui de la règle, pas le type de la clause

**Le constat (22 nov., à l'écran).** Un ordinateur cassé chez A, garantie matériel multimédia souscrite : la justification dit « Couvert. », la pastille dit « À préciser, confiance 85 % », et l'article 6.1 est étiqueté « exclusion ».

**La cause.** La validation exige, pour un « couvert », une citation vérifiable dont le rôle est « garantie ». Elle prenait ce rôle dans le type de la clause, fixé à l'ingestion par des indices de vocabulaire, pour la clause entière. La clause 6.1 de A commence par « Pour autant que vos conditions particulières en fassent mention… » et a été typée « exclusion » : tout « couvert » du pack multimédia était rétrogradé. Ce garde-fou date de la méthode où le modèle citait (« le rôle vient du contrat, pas du modèle ») ; dans la méthode « règles », c'est une règle rédigée, contrôlée et relue qui cite.

**L'ampleur.** Garanties dont la clause citée n'est pas typée « garantie » en base : 1 sur 24 chez A, 3 sur 26 chez D, **22 sur 40 chez B** (la clause 3.1.4 des dégâts des eaux est typée « autre », la 3.1.1.2 du heurt et du vandalisme « condition »).

**La règle.** Pour la méthode « règles », le rôle d'une citation est celui que la règle lui donne ; « garantie » est réservé à la phrase qui accorde la garantie (pas une définition ni une circonstance citée avec elle). Le garde-fou reste : un « couvert » exige cette phrase, retrouvée mot pour mot dans la clause. Quand un modèle cite (les autres méthodes), rien ne change. Et quand la validation rétrograde, la justification le dit, au lieu de garder « Couvert. ».

**La mesure (22 nov., 16 h 20).** A, partie test : 90 %, mais **0,3 couvert à tort** (un passage sur trois). A, jeu fermé : 100 %. B : 85 % (82 % à 13 h 30), 1 couvert à tort (`f-b18`, le même). D : 93 % (96 %), 1 refus à tort (`f-d08`, le même).

Comparées cas par cas à la série précédente, les réponses qui changent sont au nombre de quatre, et toutes par la lecture, avant toute validation : `val-09` (le fer à repasser, lu « accident » six fois sur six jusque-là, lu « électricité » deux fois sur trois, et couvert une fois par la garantie 2.6, dont la clause est bien typée « garantie » : l'ancien garde-fou ne l'aurait pas retenu), `f-d05` (un « cadre » lu « châssis », puis non confirmé), `f-b06` et `f-b13` (un passage de mieux chacun). Aucun passage, avant ou après, ne porte la trace d'une rétrogradation : **le changement de rôle n'a aucun effet mesuré sur ces jeux**, il corrige le cas vu à l'écran. Les consignes et le vocabulaire envoyés au modèle sont identiques entre les deux séries : l'écart est la variabilité du modèle.

**Ce que cela dit.** « Zéro couvert à tort » sur la partie test de A tenait à six lectures identiques ; la septième série en montre un. Le chiffre honnête est une fourchette (0 à 0,3), et le README le donne ainsi.

### 7.144 Des exemples écrits pour B et D, validés par une personne

**Le constat.** La banque d'exemples vient du golden set : 66 exemples de A, 8 de B, aucun de D, et aucun pour la responsabilité civile, le heurt, l'accident ou le vandalisme. Or la lecture se corrige par des exemples (7.133). À l'écran, « j'ai fait tomber mon ordinateur » a été lu « auteur : personnel de maison ».

**Le procédé.**

- Les exemples ajoutés sont dans `data/lecture/exemples.jsonl` : une déclaration, les faits qu'il fallait y lire, un statut. Ils sont **proposés** (ici par Claude, d'après le vocabulaire) puis **validés** par une personne, ligne par ligne ; seuls les validés entrent dans la banque (`couverture exemples --valider`, `--retirer`).
- Ils ne portent que ce que la déclaration dit : pas de valeur par défaut.
- **Aucun ne doit ressembler à un cas de mesure.** `exemples.controler_ajoutes` compare chaque exemple à la partie test du golden set et aux jeux fermés (part de mots communs, seuil 0,3) et refuse ce qui est trop proche : un exemple voisin d'un cas du banc lui soufflerait la réponse. Le contrôle est automatique, pour ne pas avoir à lire les cas de mesure en écrivant les exemples. Deux propositions ont été réécrites à l'aveugle et une retirée pour cette raison ; les sujets des neuf cas en erreur du 22 nov. ont été évités.
- Le même contrôle refuse un fait hors vocabulaire ou hors sujet pour son événement. Un test le rejoue.

**Ce qu'un exemple peut corriger, et ce qu'il ne peut pas.** Les exemples ne sont montrés qu'au temps 2 (7.116) : ils enseignent les détails (l'auteur, l'accès du voleur, le vent), pas l'événement ni le bien. La famille « le bien n'est pas dit » (7.139) n'en relève donc pas.

**État.** 28 exemples proposés (13 pour D, 15 pour B), validés tous les 28 par l'auteur le 22 nov. ; la banque passe de 74 à 102 exemples.

**La mesure (22 nov., 17 h 25).** A, partie test : 90 %, **1 couvert à tort** ; A, jeu fermé : 100 % ; B : 85 %, 1 couvert à tort ; D : 96 %, 1 refus à tort. Aucun cas instable sur les quatre bancs.

Comparée à la série de 16 h 20, sur les 288 lectures : 267 réponses justes contre 265 ; 2,29 détails lus par déclaration contre 2,34 ; les détails lus diffèrent pour 52 déclarations sur 96, quand ils différaient déjà pour 48 entre les deux séries précédentes, sans aucun changement. **L'effet des 28 exemples n'est pas mesurable sur ces jeux.** C'est attendu, et c'est le prix du contrôle : un exemple n'est montré que s'il ressemble à la déclaration (seuil 0,85), et ces exemples ont été écrits pour ne ressembler à aucun cas de mesure. Les bancs ne peuvent pas dire s'ils aident ; seules des déclarations nouvelles, proches d'eux, le diraient. Ils sont gardés : validés, sans effet négatif mesuré.

**Le couvert à tort de A n'en vient pas.** `val-09` (le fer à repasser) est lu « électricité » aux trois passages, dès le temps 1, qui ne reçoit pas d'exemples et dont la consigne et le vocabulaire sont identiques, au caractère près, à ceux de 13 h 30. Lu « accident » six fois sur six avant 16 h, « électricité » deux fois sur trois à 16 h 20, trois fois sur trois à 17 h 25 : la lecture du même texte par `mistral-medium-latest` a changé dans la journée. L'hypothèse d'un alias « latest » qui aurait changé de modèle dans la journée est examinée, et écartée, en 7.145.

### 7.145 Le modèle se désigne par sa version, et la variation ne vient pas d'un changement de version

**La question.** Le même texte, lu autrement à quelques heures d'écart avec la même consigne (7.144) : `mistral-medium-latest` a-t-il changé de modèle dans la journée ?

**La vérification.** `couverture modele` demande maintenant au fournisseur tous les noms du modèle configuré (`GET /models`, `llm.noms_du_modele`). Réponse du 22 nov., 17 h 54 : « mistral-medium-latest » désigne le même modèle que `mistral-medium-2604` (Mistral Medium 3.5) ; « mistral-small-latest », le même que `mistral-small-2603` (Mistral Small 4). La documentation de Mistral ne signale aucun changement de Medium ce jour-là, et classe Medium 3.5 comme déprécié depuis le 31 octobre 2026, retiré le 30 avril 2027.

**La conclusion.** L'hypothèse est écartée : la version n'a pas changé. À température 0, avec une graine fixe, la même version ne lit pas toujours le même texte de la même façon, et l'écart peut durer (six lectures « accident », puis cinq « électricité » sur six). C'est une propriété du service, pas un réglage qu'on aurait manqué : 7.123 l'avait déjà mesuré sur la graine.

**Ce qui change.** La configuration nomme les versions datées (`mistral-medium-2604`, `mistral-small-2603`) : ce sont les mêmes modèles que ceux mesurés, donc les mesures restent valables, et le jour où « latest » changera, le projet ne changera pas avec lui. Deux choses à savoir pour une mise en service : le modèle de lecture est déprécié (à remplacer avant avril 2027, bancs à rejouer), et un zéro mesuré un jour ne garantit pas le lendemain : les bancs se rejouent à intervalle régulier, pas seulement quand on change quelque chose.

### 7.146 La rédaction propose les libellés

**Le manque (7.137).** Les 149 libellés ont été écrits à la main. Un contrat de plus aurait demandé de recommencer, et une variable acceptée sans libellé aurait montré son identifiant à l'écran.

**La règle.** Le libellé naît avec la variable, là où elle est proposée :

- la consigne de rédaction (v13) demande, pour chaque variable nouvelle, son `libelle` (le nom court à montrer) et, pour les seules valeurs dont l'identifiant s'écrit mal, leurs `libelles` ;
- `accepter_vocabulaire` les range avec la variable ; un libellé de valeur qui ne vise aucune valeur est ignoré ;
- sans libellé, la proposition est notée « à relire » par le contrôle, l'acceptation le signale (« sans libellé ; à écrire »), et le test des libellés du vocabulaire échoue tant qu'il n'est pas écrit : trois filets pour un oubli.

**Ce qui n'est pas mesuré.** La consigne v13 n'a pas été rejouée sur les trois contrats : leurs règles sont déjà rédigées et relues. Elle servira au prochain contrat (point 6 du plan), qui dira si Mistral Large propose des libellés utilisables.

### 7.147 Fusionner un doublon : un outil, et une limite

**L'outil.** `couverture regles --contrat … --fusionner ancienne:nouvelle` (`redaction.fusionner_variables`) : l'ancienne variable est renommée partout où elle sert (les règles de chaque contrat, octet pour octet ; le vocabulaire ; les faits idéaux des cas ; les exemples de lecture), la variable gardée conserve sa question et son aide, et le rangement la fait passer au commun si deux contrats l'emploient. Les contrats qui employaient déjà la variable gardée lisent exactement la même chose : seul celui dont la variable disparaît est à mesurer.

**Ce que l'outil vérifie, et ce qu'il ne vérifie pas.** Il refuse deux variables qui n'ont pas les mêmes valeurs. Il ne sait pas si deux questions veulent dire la même chose : « vent d'au moins 80 km/h » et « vent de plus de 100 km/h » ont les mêmes valeurs (oui, non) et ne sont pas un doublon. Le jugement reste celui d'une personne.

**Ce qui est fusionné.** Un seul des huit groupes de 7.140 est un vrai doublon, à valeurs et à sens identiques : les clés laissées dehors (`cles_deposees_exterieur` de D devient `cles_a_proximite` de A). Le vocabulaire passe de 149 à 148 variables, les propres lues dans la déclaration de 70 à 68 (la variable gardée devient commune).

**Ce qui ne l'est pas, et pourquoi.** Les sept autres groupes ne se renomment pas : ce sont des refontes.

- Trois sont des seuils (le vent, l'inoccupation, le déménagement) : une variable graduée à la place de deux oui/non, et chaque règle réécrite pour dire son seuil.
- Deux sont des variables à valeurs (la fermeture, la canalisation) : trois questions à réunir en une, avec des valeurs à définir.
- Deux demandent un avis de métier (les travaux « autres que d'entretien » sont-ils un bâtiment « en construction » ? les dégâts du vent et ceux de la neige aux alentours sont-ils la même condition ?).

Chacune changerait la lecture de deux contrats, pour un gain d'une variable. Or les trois séries du 22 nov. montrent qu'à consigne identique un banc varie de trois points et d'un couvert à tort : l'effet d'une refonte serait sous le bruit, donc impossible à valider. Elles restent décrites, pas faites.

**La mesure (22 nov., 18 h 11).** Jeu fermé de D : 96 %, aucun couvert à tort, 1 refus à tort (`f-d08`, le même), aucun cas instable : dans la fourchette du jour (93 à 96 %). Les règles de D se chargent dans SWI-Prolog, 117 citations retrouvées, aucun fait hors vocabulaire.

---

**Partie VI — Un contrat ajouté à froid (22 novembre).** Répondre, par l'essai, à la question des centaines de contrats.

### 7.148 Le quatrième contrat : un PDF sans numéros d'article (Assureur C)

**D'où l'on part.** Assureur C avait été ingéré le 18 nov. (7.51) et laissé « à vérifier » : 157 clauses, aucune définition reconnue, presque tout rangé sous un article « 2 » qui n'existe pas. C'est le contrat ajouté à froid du plan (point 6), repris le 22 nov. à 18 h 20.

**Ce que le document a de particulier.** Trois choses, toutes de mise en page :

- **aucun numéro d'article** : 53 pages structurées par des titres (« Vol », « Bris de glaces »), avec sous chacun les mêmes sous-titres (« Ce qui est garanti », « Mesures de prévention », « Ce qui est exclu ») ;
- **un lexique à puces** : une puce seule sur sa ligne, le terme sur la ligne suivante, la définition dessous ;
- **sept pages aux lettres espacées** (« L e s di s p o siti o n s ») : la police n'a pas ses largeurs dans le PDF, l'extraction coupe un mot à chaque lettre.

**Ce qui a été ajouté, au découpage et non au contrat.**

- `titres` dans un profil : les titres de section, recopiés du sommaire. Chacun ouvre une section, une seule fois (le tableau des montants répète les titres des garanties). Dans ce mode, une ligne en capitales est un sous-titre de la section en cours, un intertitre commence par une majuscule (« les exclusions communes figurant page 30 : » est la suite d'une phrase), et seul un titre du sommaire ferme le lexique (« Franchise » y est un terme) ;
- `lexique : "puce"` ;
- dans la lecture du PDF, une page où plus de 60 % des « mots » font une ou deux lettres est relue avec un écart proportionnel à la taille des caractères.

Le profil d'Assureur C tient en un fichier (`data/profils/assureur-c.json`) : 45 titres, 9 intertitres, 3 intervalles de pages ignorées (couvertures, sommaire, contacts, déclaration de confidentialité).

**Le résultat.** 218 clauses, statut OK, aucune alerte : 51 définitions, 32 garanties, 32 exclusions, 47 conditions, 33 limites. Chaque garantie a sa section, avec ses clauses dans l'ordre (« Vol » : ce qui est garanti, mesures de protection, en cas d'inhabitation, montants, exclusions).

**La non-régression.** Les trois autres contrats ont été redécoupés avec le code d'avant et celui d'après : mêmes clauses, au caractère près (147, 293 et 267 ; empreintes identiques). Sans `titres` dans le profil, rien ne change.

**Ce que cela a coûté.** Environ une heure, sans appel à un modèle : lire la sortie du découpage, trouver les trois causes, écrire deux options de profil et une règle de lecture, recopier le sommaire. C'est le coût d'un PDF dont la mise en page sort de ce que les trois premiers avaient montré ; un cinquième contrat sans numéros ne demandera plus que son profil.

**Ce qui reste.** Les règles d'Assureur C ne sont pas rédigées : c'est l'étape suivante (Mistral Large, consigne v13), et la première mesure des libellés proposés (7.146).

### 7.149 Un contrat de plus ne commence pas par un fichier écrit à la main

**Le constat (22 nov., 18 h 32).** Première rédaction pour Assureur C : la commande s'arrête sur « fichier introuvable ». Les règles de B et de D avaient commencé par un fichier vide créé à la main, avec son en-tête ; rien ne le créait.

**La règle.** La première rédaction crée le fichier de règles du contrat (`redaction.ouvrir_regles` : un en-tête, aucune règle). Et un contrat n'est compté parmi ceux qu'on peut interroger que si ses règles traduisent au moins une garantie (`prolog.a_des_garanties`) : tant que le fichier est vide, il n'apparaît ni à l'écran, ni dans le rangement du vocabulaire, ni dans le bilan.

### 7.150 La première rédaction du quatrième contrat : ce qu'elle a coûté, ce qu'elle a montré

**La mesure (22 nov., 18 h 39 à 18 h 51).** Deux sections d'Assureur C, le vol (S8) et le bris de glaces (S10), rédigées par `mistral-large-latest` avec la consigne v13 : 11 min 23 s en tout, le bris de glaces en moins de quatre minutes, le vol en onze. 5 garanties, 13 exclusions, 8 circonstances, 1 limite. 22 contrôles bloquants : aucune règle n'est entrée dans le contrat sans relecture, ce qui est le but.

**Ce qui marche sans rien changer.** Les citations sont toutes retrouvées dans le texte. Les neuf variables et valeurs nouvelles arrivent avec leur libellé, leur question et leur aide (7.146). Le vocabulaire existant est réutilisé là où il dit la même chose : les clés laissées à proximité, l'auteur du vol, les parties communes, les travaux sur les vitres, les rayures. Le modèle déclare ce qu'il ne traduit pas au lieu de l'inventer.

**Ce qui est faux, et qu'aucun contrôle n'avait vu.** Le texte du vol dit « formule Initiale avec option Vol, formule Confort ou formule Optimale ». Le modèle a écrit `standard`, `confort`, `excellence` : les formules de B et de D, parce que le vocabulaire qu'on lui donnait les montrait toutes. Dans le bris de glaces, pour la même formule, il a déclaré `optimale`. Deux sections, deux noms, et le premier aurait décidé un sinistre de C avec le nom d'une formule de D.

**La règle.** Une variable dont chaque contrat a ses noms (`par_contrat`, 7.141) ne montre à la rédaction que ceux du contrat traduit ; s'il n'en a pas encore, elle le dit et demande les noms du texte. Le contrôle refuse le nom d'un autre contrat. L'acceptation range les noms déclarés sous le contrat, y compris celui qu'un autre porte déjà (« confort » chez C et chez D). Aucune hiérarchie entre formules n'est retenue : le « parent » proposé par le modèle est ignoré pour ces variables.

**Au passage.** Les propositions portaient « consigne v12 » : la version était écrite deux fois dans le code, et une seule avait été changée. Un test les compare.

**Ce qui reste ouvert.** Ce contrat renvoie à ses pages (« reportez-vous à la page 19 », « les exclusions communes figurant page 30 »), pas à des articles. La rédaction ne suit pas ces renvois : elle les déclare non traduits, ce qui est honnête et bloquant. Les exclusions communes (S35) se rédigent à part et visent toutes les garanties ; les exclusions relatives aux biens (page 14) et les montants (page 19) restent à relier.

### 7.151 La relecture du vol et du bris de glaces d'Assureur C

**Deux rédactions du même texte ne se ressemblent pas (22 nov., 19 h 02).** Relancée après la règle des formules (7.150), la rédaction des deux mêmes sections a pris 2 min 28 s au lieu de 11 min 23 s, et elle a fait moins : le vol sur le lieu de vacances rangé en extension d'un concept qui n'existe pas, les dépendances réduites au garage, la suspension pour inhabitation déclarée non traduite, des citations coupées par « … », la formule et son option fondues en une valeur (`initiale_option_vol`). Les formules, elles, portent bien les noms du texte. Même modèle, même consigne, vingt minutes d'écart : relancer jusqu'à obtenir une bonne rédaction n'est pas une méthode. Les deux brouillons sont gardés (`regles/propositions/assureur-c-habitation-2025/brouillons/`).

**Ce que les contrôles ont vu, et ce qu'ils n'ont pas vu.** 22 puis 26 points bloquants : le vocabulaire nouveau, les renvois non traduits, l'extension sans concept, une citation absente, une garantie sans exclusion. Ils n'ont pas vu les « objets de valeur » réduits aux bijoux dans les deux rédactions, ni les dépendances réduites au garage : une définition plus étroite que le texte est une règle bien formée.

**La relecture (19 h 27).** Les deux brouillons réunis à la main dans le JSON de la proposition, comme le prévoit la méthode (« la source, corrigible à la main ») :
- la formule et l'option sont deux faits (`formule = initiale` et `option_vol = oui`), comme chez B ;
- les objets de valeur suivent la définition du contrat : bijoux, objets d'art, tapis et fourrures au-dessus de 200 €, collections, tout objet au-dessus de 5 000 € ; d'où une variable `valeur_unitaire` et trois biens nouveaux ;
- les « locaux sans communication intérieure » se disent avec le lieu existant (`annexe` : « dépendance privée sans communication avec le logement ») ; la variable proposée pour cela n'est pas créée ;
- l'inhabitation est une durée (trois jours, quarante-cinq jours) : une variable à trois valeurs, et la suspension de la garantie des objets de valeur est traduite ;
- les exclusions du vol valent pour ses deux garanties ; « les vitraux, les marquises, les serres » n'excluent que ces biens ;
- les renvois par page sont rangés : « reportez-vous à la page 19 » est une limite qui cite la section des montants ; « outre les exclusions […] page 14 et […] page 30 » est classé hors décision, avec la raison.
Après cela : aucun contrôle bloquant, toutes les citations retrouvées mot pour mot.

**Ce que la relecture ne règle pas.**
- Les biens non assurés (S2-b) et les exclusions communes (S35) ne sont pas encore rédigés : tant qu'ils ne le sont pas, une décision « couvert » de C les ignore.
- Un garage est une dépendance dans les règles, alors que le contrat en fait une pièce annexe quand il communique avec le logement : on demandera la porte pleine pour un garage attenant.
- Une exclusion des objets de valeur écarte tout le sinistre, même si d'autres biens ont été volés avec eux.
- Le relecteur ne connaît pas l'assurance : la relecture vérifie que la règle dit ce que dit le texte, pas qu'un gestionnaire la lirait ainsi.

**Vérifié sur quelques faits, avec le moteur de référence.** Le vélo de l'énoncé, dans le local commun : non couvert, par l'exclusion des locaux à usage commun (S8-f). La bougie : à examiner, l'incendie n'étant pas traduit. Un cambriolage par effraction en formule Confort : couvert ; en formule Initiale sans option Vol : non couvert ; formule inconnue : à préciser. Une fenêtre brisée : couverte en Confort, pas en Initiale. Un aquarium : couvert en Optimale seulement.

**Un effet sur les autres contrats, à mesurer.** L'acceptation ajoute huit valeurs à `bien` et une à `lieu`, que la lecture propose à tous les contrats. Chacune a un parent (`objet_divers`, `logement`), donc les règles existantes les reconnaissent ; mais les bancs de A, B et D sont à repasser. Et un test mesurait la longueur de la consigne de lecture sur tout le vocabulaire : elle grandissait avec chaque contrat ; il la mesure maintenant pour un contrat, comme en service.

**Le coût, à ce stade.** Pour deux sections sur une trentaine : deux rédactions (14 minutes de modèle), trois corrections du code (7.148 à 7.150), une relecture qui a réécrit six définitions ou règles sur une vingtaine et créé sept variables. La relecture a été faite par l'assistant qui a écrit le code, en quelques minutes : ce n'est pas le temps d'un relecteur humain, qui reste à mesurer.

### 7.152 Le premier essai à l'écran : la bonne réponse sous le mauvais nom

**Le constat (22 nov., 19 h 40).** La question du vélo de l'énoncé, posée au contrat C à l'écran : « Non couvert », avec la clause S8-f sur les locaux à usage commun. La réponse et la citation sont justes. La phrase ne l'est pas : « Vol sur le lieu de vacances (S8-a) : une exclusion s'applique ». Personne n'était en vacances.

**La cause.** Le périmètre du vol dans l'habitation, tel que je l'avais relu, n'admettait que le logement et les dépendances : le local commun en sortait, et la garantie était « hors sujet ». L'exclusion des locaux communs ne tenait plus qu'à l'autre garantie, celle des vacances, dont le périmètre restait inconnu. Chez A et chez D, le bâtiment comprend les parties communes, et c'est l'exclusion qui décide.

**La règle (restreinte depuis, voir 7.156 : elle ne vaut que pour une exclusion de tout le sinistre).** Un lieu ou un bien que le contrat exclut en toutes lettres appartient au périmètre de la garantie : c'est l'exclusion qui décide, et c'est elle qu'on cite. Un contrôle le vérifie (`exclusions_hors_perimetre`) : une exclusion qui vise un lieu ou un bien qu'aucune de ses garanties n'admet est signalée à la relecture. Il a trouvé aussitôt le même défaut dans le bris de glaces : un vitrail brisé aurait été écarté sans la clause qui l'exclut.

**Les corrections.** Les parties communes entrent dans le périmètre du vol dans l'habitation ; les vitraux, marquises et serres dans celui du bris de glaces. Le lieu de vacances suit sa définition jusqu'au bout (« dans un bâtiment n'appartenant pas à l'assuré ») : un séjour temporaire, dans un autre bâtiment.

**Ce que ça dit de la relecture.** L'erreur était la mienne, pas celle du modèle, et les faits écrits à la main ne l'avaient pas montrée : la décision était juste. Il a fallu l'écran, c'est-à-dire lire la phrase qu'un gestionnaire lirait.

### 7.153 Tout revérifier avant de continuer

**La demande (22 nov., 19 h 45).** Après quatre corrections en une soirée sur le quatrième contrat, revérifier l'ensemble : le code, les règles, le vocabulaire, la logique. Fait sur une copie de l'état réel du dépôt (règles et vocabulaire de C acceptés compris).

**Ce qui a été vérifié, et le résultat.**
- Le code de `src/` est identique à la copie de travail, fichier par fichier ; les tests passent (203 ici, 215 sur le poste avec SWI-Prolog) ; l'analyse statique ne signale aucune erreur réelle.
- Le vocabulaire, 155 variables : chacune a un libellé et une question ; aucune valeur en double ; les aides, libellés, parents, « si », « implique » et noms par contrat ne visent que des variables et des valeurs qui existent. Une variable n'est employée par aucune règle (`canalisation_encastree`, déjà connue).
- Les règles des quatre contrats : chaque fait employé est dans le vocabulaire, chaque formule est un nom du contrat, chaque concept employé est défini, aucune garantie en double. 567 citations comparées au texte des clauses : 567 retrouvées.
- Tous les contrôles d'aujourd'hui repassés sur toutes les propositions déjà acceptées.

**Ce que la revue a trouvé.**
1. *La fusion de variables oubliait les propositions.* Après la fusion de 7.147, la proposition 2.5 de D gardait l'ancien nom : les règles étaient justes, mais leur source ne pouvait plus être recontrôlée. La fusion renomme maintenant aussi les propositions ; celle de D est corrigée.
2. *Le défaut de 7.152 existe aussi chez A et chez B.* Dix exclusions du bris de vitrages et du matériel multimédia visent un bien que le périmètre n'admet pas (un vase, une serre, des lunettes) : la décision est juste (« non couvert »), mais la clause qui le dit n'est pas citée. Non corrigé ce soir : cela change des règles mesurées, et demande de repasser les bancs.
3. *Un contrôle se trompe sur une règle juste.* L'obligation du matériel dans un véhicule (B, 3.1.7.4) est signalée comme une simple réduction, alors que le texte dit « la garantie intervient uniquement si » : la clause réunit plusieurs alinéas, et le contrôle lit l'ensemble.
4. *Des brouillons jamais acceptés restent dans les propositions de D* (objets de valeur, véranda, catastrophe technologique, mesures de protection contre le vol, manifestations) : ces articles ne sont pas dans les règles. Pour le vol de D, les mesures de protection exigées ne sont donc pas vérifiées.
5. *L'en-tête des règles de A est périmé* : il dit que la tempête et le bris de vitrages ne sont pas traduits. Il dit aussi, et c'est toujours vrai, que le vol, l'incendie, les dégâts des eaux et les exclusions générales de A ont été écrits à la main, comme modèle.
6. *L'anonymisation fuit à trois endroits* : un nom de fichier et un commentaire dans `tests/test_pipeline.py`, et le nom d'un service d'assistance dans le texte d'une clause recopiée dans deux fichiers de `data/ferme/`. Deux dossiers de propositions portent encore un ancien nom sur le poste.

**Ce qui n'a pas pu être vérifié ici.** L'accord entre le moteur Prolog et le moteur de référence (les tests qui le font tournent sur le poste, pas ici) ; la lecture des déclarations par le modèle (les bancs) ; l'écran (pas de construction du frontend ici).

### 7.154 Ce qui est général, ce qui ne l'est pas, et une dernière fuite entre contrats

**La demande (22 nov., 19 h 58).** Dire ce qui est généralisable, et chercher les bogues restants.

**Ce qui est général, vérifié dans le code.**
- Aucun identifiant de contrat, aucun numéro d'article, aucune valeur métier (vol, logement, formule…) n'est écrit dans la logique de `src/` : seulement dans les exemples de la documentation de l'API, dans l'aide de la ligne de commande, et dans la liste des contrats du jeu fermé (`ferme.py`).
- Le moteur, la validation des citations, l'API, l'écran et la fiche n'ont pas changé d'une ligne pour le quatrième contrat.
- Ce qui est propre à un contrat tient dans quatre fichiers de données : son profil de découpage, ses règles, ses variables propres, sa ligne au catalogue.

**Ce qui n'est pas général.**
- Les deux consignes (rédaction et lecture) disent « assurance habitation », et leurs exemples en viennent.
- Le socle de la lecture est « événement, bien, lieu » : il convient à un contrat de dommages aux biens ; pour une responsabilité civile seule, une assurance auto ou une prévoyance, il serait à revoir. Aucun contrat hors habitation n'a été essayé.
- Le « pour » d'une variable (les sinistres pour lesquels on la lit) est commun à tous les contrats : accepter le vol de C fait lire la résidence principale pour un vol chez A. Sans effet sur une décision, mais la lecture d'un contrat dépend encore un peu des autres.
- Le découpage : chaque mise en page nouvelle a demandé un profil, et une fois sur quatre du code.
- La relecture des règles reste humaine (7.151).

**Une fuite de plus entre contrats, corrigée.** La rédaction ne voyait plus que les formules du contrat (7.150), mais la lecture d'une déclaration les voyait encore toutes : interrogé sur C, le modèle pouvait répondre « excellence », une formule de D. La chaîne lit maintenant avec le vocabulaire tel que le contrat le voit (`prolog.vocabulaire_du_contrat`) ; une formule d'un autre contrat est écartée et signalée. Et la question posée pour la formule ne cite plus les noms d'un seul assureur.

**La recherche de bogues.** 1 800 jeux de faits tirés au hasard dans le vocabulaire, plus des entrées mal formées (valeur inconnue, liste là où on attend un mot, valeur vide), soumis à la décision des quatre contrats et, pour une partie, à la fiche PDF : aucune erreur, aucun « couvert » sans clause citée, et chaque « à examiner » sans question vient d'un événement que le contrat ne traduit pas, ce que la réponse dit. Ce n'est pas une preuve d'absence de bogue : les routes HTTP, l'écran et le moteur Prolog ne tournent pas dans l'environnement où cette revue a été faite ; ils sont couverts par les tests du poste.

### 7.155 Les bancs de A, B et D après l'arrivée du quatrième contrat

**La question.** L'acceptation du vol et du bris de glaces de C a ajouté huit biens et un lieu au vocabulaire commun, que la lecture propose à tous les contrats (7.151) ; et la lecture ne voit plus que les formules du contrat interrogé (7.154). Les trois autres contrats en sont-ils changés ?

**La mesure (22 nov., 20 h 22 à 20 h 30), trois répétitions par banc.**

| Banc | Avant (séries du 22 nov.) | Après |
|---|---|---|
| A, partie test (31 cas) | 90 %, 0 à 1 couvert à tort | 94 %, 0 couvert à tort, 0 refus à tort |
| A, jeu fermé (20 cas) | 98 à 100 % | 100 % |
| B, jeu fermé (20 cas) | 82 à 85 %, 1 couvert à tort | 82 %, 1 couvert à tort (`f-b18`, le même) |
| D, jeu fermé (25 cas) | 93 à 96 %, 1 refus à tort | 96 %, 1 refus à tort |

**Ce qu'on peut en dire.** Aucun chiffre ne sort de sa fourchette : ajouter un contrat n'a pas dégradé les trois autres, à la précision de ces jeux (un cas pèse 3 à 5 points). Le 94 % de A n'est pas un progrès démontré : il est dans le bruit mesuré le même jour (trois séries à consigne identique variaient de 3 points). Les erreurs qui restent sont celles d'avant, laissées telles quelles parce qu'elles sont des cas de mesure.

**Les portes.** Trois bancs sur quatre « échouent » : B sur l'exactitude et le couvert à tort, comme avant ; A sur le 95e centile du temps de réponse (15 s et 11 s pour un seuil à 10 s, médiane 3,6 à 4,3 s : un appel lent au modèle sur dix suffit) et sur les décisions changées par la lecture (3 pour un seuil à 2). Les seuils ne sont pas relevés pour faire passer.

### 7.156 La règle de 7.152 était trop large : un couvert à tort introduit, puis retiré

**Le constat (22 nov., 20 h 50).** Avant d'appliquer à A et à B la règle de 7.152 (« un bien exclu en toutes lettres entre dans le périmètre »), comparaison des décisions avant et après sur 600 jeux de faits par contrat : chez A, 40 « non couvert » ou « à préciser » devenaient « couvert » ; chez B, 29. Un vase et un meuble, une serre et une couverture de piscine : couverts.

**La cause.** Le périmètre d'une garantie est établi dès qu'un des biens déclarés y entre. Une exclusion qui ne vise qu'un bien (« les vitraux ») n'en retire qu'un. Faire entrer dans le périmètre un bien qui n'y est que pour être exclu, c'est ouvrir la garantie à tout ce qui est déclaré avec lui. La règle de 7.152 est juste pour une exclusion qui écarte tout le sinistre (les locaux à usage commun) ; elle est fausse pour une exclusion d'un seul bien.

**Le défaut était déjà dans le contrat C**, accepté une heure plus tôt : un vitrail et une marquise brisés ensemble, ou un vitrail et une télévision, étaient « couverts ». Les bancs ne pouvaient pas le voir, C n'a pas de jeu de mesure. La comparaison avant-après l'a vu avant que A et B ne soient touchés.

**Les corrections.**
- Les vitraux, marquises et serres sortent du périmètre du bris de glaces de C ; leurs exclusions restent, chacune pour son bien. Un test garde le cas : deux biens exclus déclarés ensemble ne sont pas couverts.
- Le contrôle de 7.152 ne signale plus que les exclusions de tout le sinistre.
- Rien n'est changé chez A ni chez B. Les règles en place des quatre contrats ont été cherchées pour le même défaut (deux biens exclus d'une même garantie, déclarés ensemble) : aucun.
- Le contrôle qui prenait pour une réduction d'indemnité l'obligation « la garantie intervient uniquement si » (B, 3.1.7.4) reconnaît maintenant cette formule comme un refus.

**Ce qui restait, et qui ne se réglait pas dans les règles.** Un vase brisé seul chez A, un vitrail chez C : « non couvert », à raison, mais sans la clause qui l'exclut, parce qu'aucune garantie ne s'y rattache. C'est le moteur qu'il fallait changer : fait le soir même (7.157).

**Une limite du moteur que ce défaut a rappelée.** Pour plusieurs biens déclarés ensemble, le moteur répond « couvert » dès qu'un bien entre dans une garantie, même si l'autre n'entre dans aucune (une vitre et une télévision chez C). La réponse ne dit pas lequel.

### 7.157 Quand aucune garantie ne s'applique, citer la clause qui exclut

**Le défaut, et pourquoi il ne se réglait pas dans les règles.** Un vase brisé chez A, un vitrail chez C : « non couvert », à raison, mais avec la phrase « aucune garantie ne s'applique » et, pour citations, le texte des trois premières garanties du contrat, sans rapport avec le sinistre. La clause qui exclut « les objets en verre » existe, mais elle est attachée à une garantie dont le vase ne franchit pas le périmètre : le moteur ne l'examinait jamais. Faire entrer le vase dans le périmètre créait des couverts à tort (7.156).

**La règle, dans le moteur.** Quand aucune garantie ne s'applique, le moteur cherche les exclusions que les faits établissent, parmi celles des garanties qui couvrent l'événement déclaré (un bris pour le bris de vitrages), et les rend à part (`exclusions_etablies`). La décision ne change pas : elle était déjà « non couvert ». La chaîne cite alors ces clauses, avec le rôle « exclusion », et la phrase le dit : « aucune garantie ne s'applique, et le contrat l'exclut expressément ».

**Écrite deux fois, comme le reste du moteur** : en Prolog (`regles/moteur.pl`) et dans le moteur de référence des tests ; le test de concordance compare ce champ sur tous les cas, et un test le vérifie sur quatre cas de A et de C.

**Ce que ça donne (moteur de référence).** Vase brisé chez A : clause 2.9-a, « les dommages causés aux objets en verre autres que des vitres ». Serre brisée chez A : 2.9-a, « les parties vitrées des serres ». Vitrail chez C, seul ou avec une marquise : S10-c. Une vitre brisée, un vélo dans le local commun : rien de changé.

**Vérifié sur le poste (22 nov., 21 h 17 à 21 h 27).** Les tests passent avec SWI-Prolog (221), dont la concordance des deux moteurs sur ce champ. À l'écran, sur A : « J'ai fait tomber un vase en cristal dans mon salon, il est cassé » donne « Non couvert », la clause 2.9-a sur les objets en verre, et des faits tous lus dans la déclaration. Les bancs, repassés parce que le moteur a changé, et pour la première fois sous la version datée `mistral-medium-2604` : A partie test 94 %, A jeu fermé 100 %, B 85 %, D 96 % ; les mêmes erreurs qu'à 20 h 30 (un couvert à tort chez B, un refus à tort chez D), aucune nouvelle.

**Ce qui reste.** Quand aucune garantie ne s'applique et qu'aucune clause n'exclut le cas en toutes lettres (un vase brisé chez D), la réponse cite encore les premières garanties du contrat, faute de mieux. Et la « confiance » affichée (85 % pour un couvert ou un refus, 40 % pour un « à préciser ») est une valeur fixe par type de réponse, pas une probabilité mesurée.

### 7.158 Le README dit ce que le quatrième contrat a coûté

La section « Tenir des centaines de contrats » est réécrite d'après ce qui a été mesuré le 22 novembre (7.148 à 7.157) : ce qui est général (le moteur, l'API, l'écran, quatre fichiers de données par contrat), ce que C a coûté étape par étape, l'erreur de relecture et ce qui l'a montrée, ce qui n'est pas général. Elle conclut qu'il faut des relecteurs du métier, un outil de relecture et un jeu de mesure par contrat. Les chiffres du vocabulaire sont recalculés avec C (56 questions communes, 70 variables lues propres à un seul contrat). Quatre limites sont ajoutées : plusieurs biens déclarés ensemble, le cas sans garantie ni exclusion écrite, le contrat C partiel, les mesures de protection de D. Le README dit aussi que quatre articles de A ont été écrits à la main, et que la confiance affichée est une valeur fixe.

### 7.159 Les exclusions communes et les biens non assurés de C ; et un défaut du moteur trouvé en les relisant

**La rédaction (22 nov., 21 h 44).** Deux sections en 3 min 56 s : les biens assurés et non assurés (S2), les exclusions communes (S35). 24 contrôles bloquants, presque tous du vocabulaire nouveau.

**La relecture.**
- *Les exclusions communes* : le modèle les avait toutes marquées « à demander ». Chaque vol aurait reçu une douzaine de questions (une guerre ? une maladie transmissible ?). Elles ne sont jamais demandées, comme chez A et D : c'est à l'assureur de prouver l'exclusion. Dix exclusions gardées, cinq variables nouvelles qui ne sont jamais lues dans une déclaration. Trois alinéas sont des postes de frais que le contrat ne rembourse pas (honoraires d'expert, dépollution, pertes dues à une franchise) : classés hors décision, ils ne disent pas si le sinistre est couvert. Une valeur d'événement et deux variables proposées pour eux ne sont pas créées.
- *Les biens non assurés* (S2-b) : neuf exclusions, chacune pour son bien (un véhicule, des espèces, un animal), au lieu d'écarter tout le sinistre comme le proposait le modèle : un téléviseur volé avec des espèces reste couvert. Les collections de timbres et de monnaies deviennent un bien à part, rattaché à « collection » : le contrat assure les autres collections comme objets de valeur. Sept biens proposés (manoir, château…) sont ramenés à deux biens et une variable.
- *Les biens assurés* (S2-a), qui dépendent de la formule et de la qualité d'occupant, ne sont pas repris : aucune garantie traduite ne les emploie, et la rédaction y inventait trois concepts.

**Le défaut du moteur.** En vérifiant ces exclusions par bien : des espèces et un animal volés ensemble étaient « couverts ». Chaque exclusion voyait « un autre bien déclaré » et ne retirait que le sien ; aucune ne voyait que l'autre était exclu aussi. C'est la cause profonde du couvert à tort de 7.156, et elle est dans le moteur depuis le début. La règle : si chaque bien déclaré est exclu, il ne reste rien à couvrir, et les exclusions partielles valent une exclusion totale (`consolider_partielles`, en Prolog et dans la référence).

**Vérifié avant de déposer.** 450 jeux de faits par contrat, avec plusieurs biens : aucune décision de A, B, C ou D ne change avec la correction du moteur (le cas est rare, et il était faux). Puis, sur C, 700 jeux de faits avant et après les deux sections : 81 décisions changent, toutes vers « non couvert », aucune vers « couvert ». Des espèces volées : non couvert ; des espèces et un téléviseur : couvert, sauf les espèces ; un vol simulé par l'assuré : non couvert ; une voiture volée dans le garage : non couvert.

**Vérifié sur le poste (22 h 05 à 22 h 17).** Les deux sections sont acceptées sans contrôle bloquant ; 223 tests passent avec SWI-Prolog, dont la concordance des deux moteurs sur les biens tous exclus. Les quatre bancs, repassés après ce second changement du moteur et l'ajout de trois biens au vocabulaire commun, rendent exactement les chiffres de 21 h 27 : A partie test 94 %, A jeu fermé 100 %, B 85 % (un couvert à tort, le même), D 96 % (un refus à tort, le même).

---

**Partie VII — En ligne, et la veille (23 et 24 novembre).** Ce qu'il faut pour qu'un inconnu l'essaie, puis une dernière relecture par l'usage.

### 7.160 Masquer les noms dans le texte des contrats

**Le constat (23 nov.).** Le dépôt est anonyme depuis 7.70 : les assureurs s'y appellent A, B, C, D. Mais la base, elle, contient le texte des conditions générales tel qu'il est : l'assureur, son assisteur, son siège, ses numéros d'immatriculation, ses courriels. C'est ce texte que l'écran et la fiche citent. Une capture, une vidéo ou une mise en ligne montrerait ces noms.

**La règle.** À l'ingestion, après le découpage (pour ne pas le changer), les clauses et le texte brut passent par une liste de remplacements propre à chaque contrat : le nom devient « Assureur A », l'assisteur « Assureur A Assistance », une adresse « [adresse] », un numéro « [numéro] ». Les courriels, les sites et les téléphones sont masqués d'office. La liste contient les vrais noms : elle est hors du dépôt (`data/contrats/noms.prive.json`, que git ignore) ; un modèle sans nom réel est versionné (`noms.exemple.json`). Sans liste, rien ne change. La liste entre dans l'empreinte du contrat : la modifier relance son ingestion.

**Vérifié avant de déposer, sur une copie de la base.** 84, 206, 92 et 136 remplacements pour A, B, C, D. Une recherche des noms, adresses et numéros connus ne trouve plus que des restes sans nom (un médiateur public, le mot « Appartement »). Les 567 citations des règles se retrouvent toutes mot pour mot dans le texte masqué : aucune règle ne cite un nom.

**Ce que ça ne fait pas.** Le texte reste celui de l'assureur : une phrase suffit à le retrouver, et les noms de formules sont des signatures. Masquer le nom de l'auteur ne donne pas le droit de republier son texte. L'anonymisation protège une capture ou une vidéo ; elle ne rend pas le contrat publiable.

### 7.161 Une image pour mettre la démonstration en ligne

**Le besoin (23 nov.).** Le projet sera jugé sans moi : il faut une adresse où l'essayer. Trois choses manquaient, et aucune n'est une question d'hébergeur.

**1. La clé.** En local, l'écran passe par le proxy de développement, qui ajoute la clé de l'API : elle n'entre jamais dans le navigateur. En ligne il n'y a plus de proxy, et une page ouverte dépenserait le crédit Mistral pour n'importe qui. La règle (`api/acces.py`) : quand `COUVERTURE_CODE_ACCES` est défini, toute requête demande ce code par l'authentification « Basic » du navigateur (sa propre fenêtre, une fois ; l'écran n'a pas changé), le code dispense de la clé, et `/health` seul reste ouvert pour l'hébergeur. Les analyses, qui appellent le modèle, sont comptées : `COUVERTURE_LIMITE_JOUR` par jour, puis 429. Le compte est en mémoire, il repart de zéro au redémarrage : c'est un frein, pas une garantie, et le vrai plafond se règle chez le fournisseur du modèle.

**2. Le texte des contrats.** L'écran, pour afficher un article cité, téléchargeait toutes les clauses du contrat. En ligne, cela revenait à publier les conditions générales de quatre assureurs derrière un code. La règle : une route pour une seule clause ; en ligne, la liste complète est fermée (403) et une clause n'est servie que si les règles du contrat la citent (`prolog.clauses_citees` : 175 clauses sur 925). La fiche PDF suit la même règle pour les articles qu'elle joint. Hors ligne, rien ne change.

**3. Un seul conteneur.** L'API sert l'écran construit (`COUVERTURE_FRONT`) : une adresse, un service à payer ou à ne pas payer. `deploiement/Dockerfile` construit l'écran, puis prépare la base du poste (`nettoyer_base.py` retire le journal des analyses locales et le texte brut des contrats), et n'emporte ni les PDF, ni la liste des noms, ni les propositions de rédaction. L'image contient encore le texte des clauses : elle va dans un registre privé.

**Trouvé en l'écrivant.** L'image d'origine installe le paquet par `pip install .` : le code est alors copié dans les bibliothèques de Python, et il cherche `regles/` et `config/` à côté de lui, où ils ne sont pas. La nouvelle image installe en mode éditable. L'ancienne n'a pas été corrigée ni réessayée : à vérifier avant de s'en resservir.

**Ce qui n'est pas vérifié ici.** Les routes HTTP et l'écran ne s'exécutent pas dans l'environnement de l'assistant : les tests ajoutés (code d'accès, clause seule, limite) et la construction de l'image se lancent sur le poste.

### 7.162 La démonstration est en ligne

**Fait le 23 nov.** L'image de 7.161, construite sur le poste, envoyée dans un registre privé (GHCR), tourne sur Azure Container Apps, dans l'environnement qui héberge déjà SortirIA. Zéro instance au repos, une au plus : rien ne tourne sans visiteur, et le compteur d'analyses reste unique. L'adresse et le code d'accès se donnent avec le message d'accompagnement ; ils ne sont pas dans le dépôt.

**Ce que l'essai sur le poste a montré avant l'envoi.**
- Un test du projet (« une route par fichier ») a refusé ma route d'une clause, ajoutée dans le fichier de la liste : elle a son fichier (`routes/clause.py`). La règle existait, je ne l'avais pas relue.
- Le premier lancement affichait « la clé API du serveur n'est pas configurée » : le fichier d'environnement était vide. Sans code d'accès, l'image retombe en mode local et réclame une clé qu'elle n'a pas. Rien n'est exposé dans ce cas, mais le message ne dit pas la cause.
- L'image doit rester privée alors que le code est public : le dépôt montre le code, l'image contient en plus le texte des clauses.

**Vérifié en ligne.** L'en-tête (modèle daté), les quatre contrats, une analyse complète avec ses citations. Sur le poste, avant l'envoi : le code d'accès, l'article cité, la fiche. 227 tests passent.

**Ce qui n'est pas mesuré.** Le temps du premier chargement quand le service dort ; ce que l'application coûte à côté de SortirIA ; la tenue de la limite d'analyses, dont le compte repart de zéro à chaque réveil. Le jeton qui laisse Azure lire l'image expire : passé sa date, le service ne redémarre plus.

**Retouche de l'écran.** Les contrats sur une seule ligne, à parts égales ; sous 110 px par carte la ligne défile.

### 7.163 Après la mise en ligne : le journal, l'ancienne image, la documentation

**Le journal était perdu en ligne.** Il s'écrit dans la base, et la base du conteneur repart de l'image à chaque réveil : aucune trace de ce que font les visiteurs, alors que le suivi est ce que je raconte de SortirIA. La règle : quand `COUVERTURE_JOURNAL_SORTIE` est défini (l'image en ligne le fait), chaque ligne du journal est aussi écrite sur la sortie standard, en JSON, que l'hébergeur collecte. C'est la même ligne : toujours sans le texte du sinistre. Un test le vérifie, et vérifie qu'hors ligne rien n'est écrit. Ce n'est pas un tableau de bord : les lignes se relisent avec `az containerapp logs show`, sans requête ni alerte. Vérifié en ligne sur une analyse : la ligne porte le contrat, la décision, les faits, les questions, la durée, les versions des consignes, et la longueur de la déclaration (55 caractères), pas son texte.

**L'ancienne image.** Le `Dockerfile` de `docker compose` installait le paquet par `pip install .` : même défaut que celui trouvé en 7.161. Corrigé de la même façon (installation éditable), puis vérifié sur le poste par `docker compose up -d --build` : l'image se construit, l'ingestion masque les noms, et `/api/v1/sante` liste les quatre contrats décidables. Je n'ai pas essayé l'image d'avant la correction : qu'elle ait été en panne reste une déduction.

**La documentation relue.** Le README, `EXPLICATIONS.md` et le guide du suivi décrivaient le projet d'avant la mise en ligne : routes, clé et code d'accès, arborescence, nombre de tests, « déployer pour avoir une URL » parmi les suites. Corrigés. `EXPLICATIONS.md` n'a été relu en entier nulle part ailleurs que sur ces passages : son en-tête le dit, et renvoie au README en cas d'écart.

### 7.164 La réponse ne nomme que les garanties établies

**Trouvé le 24 nov., veille de la livraison**, en rejouant en ligne la première question de l'énoncé sur les quatre contrats. Les quatre décisions sont justes. Chez B, la phrase disait : « Vol Privilège concierge : une exclusion s'applique ; Vol par agression : une exclusion s'applique ». Pour un vélo volé dans un local commun, ces deux garanties n'ont rien à faire là.

**La cause.** Une règle voulue du moteur : une exclusion certaine écarte une garantie même quand on ne sait pas si elle s'appliquerait (inutile de demander si le vol a été commis sur la personne quand le lieu est exclu). Les garanties de vol ordinaires de B étaient hors périmètre ; restaient ces deux-là, au périmètre inconnu, écartées par l'exclusion, et donc nommées.

**La règle, de présentation.** Une garantie n'est nommée que si le sinistre s'y rattache de façon établie. Le moteur donne un motif propre aux garanties écartées sans être établies ; la chaîne ne les nomme pas. Si toutes le sont : « Non couvert : le contrat exclut ce cas (3.1.6.2) », et la clause d'exclusion reste citée. Rien ne dépend d'un contrat, d'une garantie ou d'un sinistre.

**Vérifié avant de déposer.** La logique du moteur n'est pas touchée : une chaîne de caractères change dans une clause, le double Python est inchangé, donc aucune décision ne peut changer. Sur 480 jeux de faits tirés au hasard (120 par contrat), la nouvelle phrase remplace une garantie sans rapport dans 36 cas (un vol de bijoux dans un casier ne nomme plus « Vol commis sur l'assuré avec violences ») ; dans 2 cas mélangés, seules les garanties établies restent nommées. Le vélo : A et C inchangés, B corrigé.

**Ce que la règle coûte.** Quand la garantie écartée était la bonne mais que son périmètre n'était pas établi faute d'un fait, la phrase ne la nomme plus : elle dit que le contrat exclut le cas, et cite la clause.

**À vérifier sur le poste** : les tests avec SWI-Prolog, puis les quatre bancs, dont les décisions ne doivent pas bouger.

### 7.165 Une garantie sans rapport avec l'événement n'est ni nommée ni citée

**Trouvé le même matin**, sur la seconde question de l'énoncé. La bougie fondue est lue « accident ». Chez A, aucune garantie ne s'applique : réponse juste, mais accompagnée des articles du vol, les trois premières garanties du fichier. Chez C et D, « à examiner par un gestionnaire », suivi de « Vol… hors de son périmètre ; Tempête… hors de son périmètre ». Le README annonçait pour A « art. 12 : l'excès de chaleur sans embrasement n'est pas un incendie » : la réponse ne l'a jamais cité sous cette forme. Je l'avais écrit d'après la note du cas, pas d'après l'écran.

**La règle.** Le moteur dit quelles garanties portent sur l'événement déclaré (`visent_evenement`, le même critère que 7.157). Une garantie écartée dès son périmètre n'est nommée et citée que si elle en fait partie. Si aucune : « aucune garantie de ce contrat ne porte sur cet événement », sans citation. Aucune décision ne change : le calcul est ajouté à la sortie, après la décision.

**Mesuré sur le double Python.** Bougie : A cite « Bris et fêlure de vitrages » et « Pack multimédia » (17 garanties écartées de la phrase), C le bris de glaces, D le bris de glaces et l'incendie. Vélo : rien ne change sur les quatre contrats.

**Ce que la règle ne fait pas.** Elle retire le hors-sujet, elle n'apporte pas la bonne citation : pour la bougie, la phrase du lexique sur l'embrasement reste absente. Et la lecture « auteur : personnel de maison », vue sur B, C et D pour cette déclaration, n'est pas expliquée. Les deux sont écrits dans les limites du README, et la ligne du tableau est corrigée.

### 7.166 Définir les valeurs de « auteur » : essayé, mesuré, retiré

**Le constat.** Pour la bougie, sur B, C et D, la lecture donnait « auteur : personnel de maison ». Le modèle ne voit de cette valeur que son identifiant, `personnel_prive`, sans définition : pour « j'ai laissé une bougie », « personnel, privé » peut se lire « moi-même ».

**L'essai.** Une définition pour chaque valeur de « auteur » dans le vocabulaire commun (tiers, assuré, famille, personnel de maison). Sur la bougie, l'effet attendu : `auteur = assure`.

**La mesure.** Partie test de A, B et D : inchangés. Jeu fermé de A : le fer à repasser (`f-a02`), couvert à tort 0 à 1 fois sur 3 jusque-là, l'est 3 fois sur 3. Rejoué pour séparer le hasard de la cause : avec les définitions, 3 sur 3 une seconde fois ; sans elles, dans la minute, 0 sur 3. Six contre zéro : la modification est en cause.

**La décision.** Retirée. Une lecture plus juste sur un fait (qui a agi) fait couvrir à tort un sinistre qui ne l'était pas : ce fait, une fois lu, rencontre une règle ou une autre lecture que je n'ai pas le droit d'aller régler sur ce cas, puisqu'il vient du jeu fermé. Le « personnel de maison » reste donc une erreur de lecture connue, sans effet sur les décisions observées, écrite dans les limites.

**Ce que ça montre.** Le jeu fermé a fait son travail la veille de la livraison : il a arrêté une correction raisonnable, qui passait les tests et trois bancs sur quatre.

### 7.167 Deux retouches de la phrase, une de l'écran

Toujours le 24 nov., toujours sans toucher à une décision.

- **Une phrase par article.** Pour la bougie chez D, la réponse nommait trois fois « Bris de glace… (2.7-a) : hors de son périmètre ». Les garanties d'un même article écartées pour le même motif se disent une fois.
- **Quand le dossier part chez un gestionnaire**, la réponse ne dit plus des garanties traduites qu'elles ne jouent pas, et ne cite plus leurs clauses. Restent celles qui s'appliquent ou pourraient s'appliquer.
- **Les cartes de contrat** : la date et le nombre de clauses sur deux lignes, sans coupure.

Avec 7.164 et 7.165, c'est la même idée sous quatre formes : la réponse ne parle que de ce qui a un rapport avec le sinistre.

**Partie VIII — Finir, puis des cas jamais vus (24 et 25 novembre).** Les contrats A et B sont traduits en entier ; des jeux écrits sans voir les règles disent ce que vaut la méthode sur des cas neufs, et le défaut qu'ils montrent n'est pas un défaut de règle.

### 7.168 Quatre sinistres, quatre lignes

Le 24 nov., en fin de matinée. Un essai sur une déclaration longue (un retour de vacances : garage forcé, vélo et tondeuse disparus, congélateur débranché, parquet gondolé, vitre fêlée) rend « couvert, confiance 70 % », au titre des dégâts des eaux. Rien sur le vol, rien sur la vitre.

**La cause.** La réponse est « couvert » dès qu'un bien entre dans une garantie, et la lecture rend des listes (événements, biens, lieux) sans dire quel bien va avec quel événement. Le moteur ne peut donc pas répondre sinistre par sinistre : on ne lui donne pas les sinistres.

**Le choix.** Ne pas toucher au moteur ni aux règles, mesurés depuis une semaine. Découper avant lui :

- la déclaration est d'abord analysée d'un bloc, comme toujours ; si la lecture y trouve un seul événement, rien d'autre ne se passe ;
- à partir de deux événements, une consigne nouvelle (`decoupage-sinistres` v1) demande au modèle s'ils font un seul sinistre ou plusieurs. Un sinistre, c'est un fait générateur et ce qu'il entraîne : une tempête et la pluie qui entre, un incendie et l'eau des pompiers restent un sinistre. Dans le doute, un seul ;
- le modèle recopie les phrases de chaque sinistre, et le code ne garde que celles qui figurent mot pour mot dans la déclaration : le même garde-fou que pour les citations du contrat ;
- la chaîne entière (lecture, vérification, moteur, confirmation) est rejouée sur chaque sinistre ;
- la réponse liste les sinistres, une ligne chacun, avec sa décision et ses articles. La décision d'ensemble n'est ferme que si toutes sont les mêmes.

Une variable (`COUVERTURE_DECOUPAGE=non`) coupe le tout sans reconstruire l'image.

**Les essais à la main, sur A.** Garage forcé, congélateur et vitre fêlée : deux sinistres, « à préciser » pour le vol (la serrure de sûreté du garage, qui est bien la question de ce contrat), « couvert » pour la vitre (2.9). La tempête et l'incendie, avec leurs suites : pas de découpage, la réponse d'avant. Une réserve : le congélateur est rangé avec le vol, ce que la déclaration ne dit pas.

**Les bancs.** A 94 % et 100 %, D 96 % : inchangés. B : 78 %, contre 85 % le matin. Avant de conclure, lecture du rapport puis rejeu sur le code d'avant (`git stash`), comme le veut la leçon 162 :

- le cas qui bascule (une chaudière qui fuit deux semaines après la signature) ne contient qu'un événement : le découpage n'y est pas appelé ;
- ses faits lus sont ceux du matin ; ce qui change, c'est la confirmation, qui ne retrouve plus le bien dans la déclaration ;
- avec l'ancien code, B donne 82 %, et le même cas échoue deux fois sur trois.

La baisse ne vient donc pas du découpage : le modèle de confirmation ne répond plus comme le matin sur ce cas. La fourchette publiée de B passe de 82–85 % à 78–85 %.

**Ce qui n'est pas fait.** Aucun jeu ne mesure le découpage lui-même : les cas existants ont une à trois phrases. L'écran affiche les lignes mais ne propose pas de répondre aux questions d'un sinistre en particulier. La réponse coûte une lecture de plus par sinistre.

### 7.169 Dire à l'écran ce qui est traduit

Le 24 nov., 13 h. Une question simple, posée tard : pourquoi des garanties manquent-elles ? Parce que la traduction s'est faite garantie par garantie, les plus courantes d'abord, et que rien ne le disait à qui regarde l'écran.

- **Un inventaire.** Les articles de garantie de chaque jeu de conditions, comparés aux règles. Le premier comptage, automatique, s'appuyait sur l'étiquette « garantie » des clauses : il a manqué l'assistance de B, étiquetée autrement, et il a déclaré A complet à tort. L'état est donc **déclaré à la main**, dans `regles/traduction.json`, et non calculé.
- **À l'écran.** « 1. Les conditions générales » (et non « le contrat ») ; un contour vert pour des conditions traduites en entier, orange pour des conditions traduites en partie ; la légende en petit sous les cartes ; au survol, ce qui est traduit et ce qui reste. La carte choisie garde son fond et prend un anneau bleu.
- **Aujourd'hui, quatre contours orange.** C'est l'état réel.

Ce que « en entier » veut dire : chaque garantie a ses règles, et chaque exclusion qu'une déclaration peut énoncer est une règle. La définition plus souple (tout passage est traduit ou classé « sans effet ») aurait donné un vert à A alors qu'un accident de chasse, que le contrat exclut, y est couvert : l'exclusion est classée « rare » depuis le 20 nov.

### 7.170 Neuf articles d'un coup, et deux assistances à la main

Le même après-midi. Objectif fixé : A et B en vert ; C et D restent en partie, et c'est assumé. La livraison est repoussée d'un jour, au 26 au matin, avec un gel du code le 25 à 18 h.

**Neuf articles de B donnés au modèle d'un coup.** Un quart d'heure de rédaction. Résultat : l'assistance d'urgence échoue (réponse coupée à 16 000 jetons), et les huit autres sortent avec 6 à 43 contrôles bloquants chacune. Des citations d'articles qui n'existent pas, des exclusions du contrat absentes des règles, un événement « maladie » inventé, une centaine de faits nouveaux. Une proposition range parmi les garanties un service qui met seulement en relation avec un artisan, sans jamais payer la facture. Aucune n'est acceptée. Les contrôles ont fait ce pour quoi ils existent.

**L'assistance d'urgence de B (3.1.12), écrite à la main** à partir du texte : la garantie en situation d'urgence dans l'habitation, le délai de carence de trente jours (fuites, chauffage, ouvertures), onze exclusions, l'option, le plafond. Six faits nouveaux, propres à B. Les citations passent mot pour mot.

**L'assistance de A (2.13).** La proposition du modèle : quatorze garanties sans événement. Le contrôle de non-régression annonce une soixantaine de cas de test qui passeraient à « couvert ». Réécrite : les prestations « mises en place après un sinistre couvert » forment une garantie accessoire, qui ne décide rien ; le dépannage serrurier, seul dû sans sinistre, est une garantie sur l'événement « assistance ».

**Trois erreurs à moi, dans l'ordre où elles sont apparues.**

- J'ai cru que le fait `depot_moins_30j`, que le modèle lisait chez B, était un délai d'attente. C'est « chez le réparateur depuis trente jours au plus », une règle de vol de A. Lire un nom n'est pas lire une définition.
- Ma première version de l'assistance de A déclarait « traduits » dix-sept événements pour la garantie accessoire. Deux tests ont échoué, à raison : une tempête sans règle n'aurait plus été signalée « à examiner par un gestionnaire » (7.84).
- J'ai écrit l'intervention non demandée à l'assistance comme une exclusion que l'assureur prouve et que le système ne demande pas. Le jeu fermé de A a rendu un couvert à tort, trois fois sur trois : une porte claquée, un serrurier, une facture, et rien sur qui a appelé. C'est la condition même de la prestation, et seul l'assuré le sait : c'est une question. Corrigé chez A et chez B.

**Ce que cette correction coûte.** Elle vient du texte du contrat, mais c'est un cas du jeu fermé (`f-a20`) qui l'a montrée. Pour l'assistance de A, ce cas n'est plus un cas jamais vu. Le README le dit à côté du chiffre.

**Bancs après les deux assistances.** A 94 % (partie test) et 100 % (jeu fermé) ; B 83 % ; D 96 % ; 233 tests. Aucun gain sur B : le cas de la chaudière dépend de la lecture, qui ne retient pas toujours l'événement « assistance » quand une panne est racontée avec lui. Essai écrit pour l'occasion : un chauffage en panne et un appel à l'assistance sont lus « dégât électrique ». C'est le prochain point, et il touche le vocabulaire commun.

### 7.171 A traduit en entier

Le 24 nov., 14 h. Il restait à A, après l'assistance, les exclusions de la responsabilité civile que la relecture du 20 nov. avait classées « rares ; le vocabulaire ne les distingue pas ». Aucune des seize variables proposées alors n'avait été retenue, pour protéger la lecture. Conséquence, vue en dressant l'inventaire : un accident de chasse était couvert chez A, que le contrat exclut en une ligne (5.5-a).

Six exclusions deviennent des règles : la chasse, le gibier et les animaux sauvages (sauf les cervidés), l'ivresse et la violence de l'assuré majeur, le terrorisme, le nucléaire, la pollution graduelle. Cinq faits nouveaux ; les deux autres existaient.

**Demander ou non.** Une heure plus tôt, la leçon du serrurier disait : ce que seul l'assuré sait se demande. Appliquée ici, elle ferait demander « était-ce à la chasse ? » après chaque accident de sport. La différence : sans appel à l'assistance, le dépannage n'est jamais dû, la question porte sur la condition de la prestation ; un accident de sport est couvert, sauf chasse, et l'exclusion ne joue que si la déclaration la dit. La leçon 165 est précisée en conséquence.

**Ce qui reste classé sans effet** dans l'article 5 : quinze passages, dont aucun n'est une exclusion à lire dans une déclaration. Des extensions que la garantie couvre déjà, et le recours de l'assureur contre l'auteur. Un point faible : la garde d'enfants rémunérée, couverte (5.6), peut être lue « activité professionnelle » et refusée à tort.

**Mesure.** À l'acceptation, aucun cas de test ne change de décision. Un accident de chasse : non couvert, 5.5-a cité. Des lunettes cassées au foot : couvert. L'outil a rangé les cinq faits dans le vocabulaire commun : ils sont lus pour les quatre contrats, donc les quatre bancs sont repassés. A 94 % et 100 %, B 83 %, D 96 % : rien ne bouge. `regles/traduction.json` déclare A traduit en entier ; sa carte passe au vert.

### 7.172 Finir A pour de bon, avancer B

Le 24 nov., 14 h 30 à 15 h 45.

**Un recensement que j'aurais dû faire avant de déclarer A vert.** En ouvrant un article de B, dix exclusions classées « rares » dans sa responsabilité civile. Compté partout : dix-huit passages chez A, vingt-deux chez B. Chez A, seul l'article 5 avait été repris ; les articles 2.5 et 2.14 avaient les mêmes classements. Le vert de 7.171 était prématuré, et il a été dit comme tel.

**A, la fin.** Neuf exclusions deviennent des règles : l'amiante, le contrôle des citernes, l'ascenseur non conforme, le terrain de plus de cinq hectares (2.5) ; la procédure à l'étranger sans accord, le recours entre assurés (2.14) ; les actes collectifs de violence, les jet-skis et engins aériens, plus de cinq chevaux (5). Sept faits nouveaux. Vérifié par un comptage, pas à l'œil : plus aucun « rare » dans les propositions de A. Ce qui reste hors décision : des extensions de garantie, de la procédure et des frais, le recours de l'assureur. Aucun cas de test ne change de décision ; A 94 % et 100 %.

**B, trois articles.**

- *Assistance pour petits travaux (3.3.2).* Le contrat organise la venue d'un artisan et ne paie jamais sa facture. Une garantie qui « couvre » aurait répondu couvert à une demande que le délai de carence de l'assistance d'urgence refuse. C'est donc un service qui ne décide rien, et la facture à la charge de l'assuré est dans son nom.
- *Protection juridique de l'immeuble (3.1.11).* Calquée sur la protection juridique déjà traduite (4.1.3) : une garantie, trois exclusions lues par des faits existants, un seul fait nouveau, l'option.
- *Option « dommages aux biens » (3.3.1).* Le bris accidentel et le vol d'instruments, de matériel de sport, de vélos, de matériel médical, de bijoux. Construite sur le matériel multimédia (3.1.7), dont l'article reprend la rédaction. Cinq valeurs de bien nouvelles, rattachées à « objet divers » pour les règles déjà écrites.

**Ce que 3.3.1 change à la question de l'énoncé.** Un vélo volé dans un hall : toujours non couvert chez B si la lecture comprend qu'il n'était pas surveillé ; « à préciser », avec la question de la surveillance, sinon. Un vélo volé dans une cave fermée à clé, plainte déposée : couvert, sous réserve de l'option. Avant, le premier était un refus ferme et le second une question.

**Trois écritures du vol, deux retirées.**

- La plainte et le lieu en deux conditions : pour le vélo du hall, seule la plainte était demandée.
- La plainte en formalité à vérifier : la bonne question était posée, mais un vol sans plainte n'était plus refusé.
- La plainte et le lieu en une seule condition : retenue.

**Un essai retiré : ouvrir le bris à l'événement « accident ».** Une guitare tombée est lue « accident », que rien ne traduit chez B. Déclarer cet événement traduit suffit à faire couvrir un vase tombé par la garantie « heurt » (3.1.1.2), dont l'exclusion des dégâts causés par l'assuré n'est pas demandée. La mention « à examiner par un gestionnaire » masquait ce défaut depuis le début. Retiré avant dépôt ; B ne sera pas déclaré complet tant que cette garantie n'est pas reprise.

**Une erreur de dépôt.** Le poste a reçu une version intermédiaire de 3.3.1 : j'avais réutilisé le dossier de dépôt, contre la règle. Vu en lisant la sortie de l'utilisateur, qui annonçait une obligation que ma version n'avait pas. Redéposé d'un dossier neuf, relu après dépôt, banc repassé.

**Mesure.** Sur 900 jeux de faits tirés au hasard, avant et après 3.3.1, aucune décision ne change hors des vélos, des bijoux et des nouveaux biens. Bancs : A 94 % et 100 % ; B 87 puis 88 % ; D 95 % (un cas juste deux fois sur trois, la confirmation écartant une fois un bien lu comme avant) ; 233 tests. `regles/traduction.json` : A traduit en entier, B dix-neuf articles sur vingt-quatre avec ses deux réserves.

### 7.173 Les exclusions rares de B, la chasse, l'accident, et une option mal rangée

Le 24 nov., 15 h 45 à 17 h.

**Les exclusions « rares » de B.** Même recensement que pour A (7.172) : vingt-deux passages classés plutôt que traduits, dans la responsabilité civile vie privée (4.1.1), les catastrophes naturelles (3.1.10), les deux protections juridiques (4.1.3, 3.1.11) et l'option « dommages aux biens » (3.3.1). Ils deviennent des règles : sports aériens, concours hippiques, paris et défis, faute lourde, aide bénévole relevant d'un accident du travail, terrain de plus d'un hectare ou non attenant, glissement de terrain, litige d'environnement, et les autres. Recompté après coup : il ne reste dans les propositions de B qu'un passage qui réponde au mot « rare », et c'est une extension (des garages à une autre adresse), pas un refus.

**La chasse (4.1.2).** Vingtième article de B. Une garantie de responsabilité civile, portée par un fait, « pratique de la chasse », que A lisait déjà pour l'exclure. Dix exclusions. Une limite assumée : le contrat exclut deux pays d'Europe que le vocabulaire des lieux ne distingue pas.

**Mesure du premier lot.** A 94 % et 100 %, B 85 %, D 95 %.

**L'accident, et la garantie « heurt ».** Le garde-fou de 7.172 tenait à une garantie : le « heurt » (3.1.1.2) couvrait un vase tombé dès que l'événement « accident » était déclaré traduit, parce qu'un accident satisfait une règle écrite sur le heurt. Première écriture, une exclusion jointe à l'exclusion des dégâts causés par l'assuré : elle rendait incertain un heurt par un tiers. Retenue : une exclusion à part, « l'événement est un accident », qui ne se demande pas. Puis l'accident est déclaré traduit dans le bris du matériel multimédia (3.1.7) et dans l'option (3.3.1), sans toucher à leur périmètre. Trois essais conformes à ce que j'attendais : la bougie « à préciser », le vase « non couvert », la guitare « couvert sous réserve de l'option ».

**B à 77 %, deux couverts à tort.** Le troisième essai était le défaut. Le jeu fermé contient un violon tombé de son pupitre, attendu « à préciser » : l'option n'est peut-être pas souscrite. Mon critère d'arrêt était atteint.

**La cause : une option rangée avec les garanties de base.** Les règles de B connaissent deux cas. Les garanties de base, « applicables si les conditions particulières les mentionnent », répondent « couvert sous réserve ». Les options (responsabilité civile, protection juridique) se demandent : « avez-vous souscrit l'option ? ». J'avais écrit les dommages aux biens et la chasse dans le premier cas, alors que le contrat les place lui-même sous un titre « Option ». Dire « couvert » pour une option que l'assuré n'a peut-être pas, c'est trop dire. Le défaut datait de l'après-midi ; la mention « à examiner par un gestionnaire » le masquait pour les objets cassés, pas pour le vélo volé dans une cave fermée, qui répondait déjà « couvert sous réserve » (7.172).

**La correction.** Pour ces deux articles, l'option est une condition de la garantie, avec sa question. Un violon tombé, un accident de chasse, un vélo volé dans une cave fermée avec plainte : « à préciser », une seule question. Le vélo du hall et le vase restent des refus. B repassé : 85 %, un couvert à tort (le vol dans la voiture, connu), deux cas instables ; 233 tests.

**Ce que ce chiffre vaut.** `f-b19` a servi à corriger une règle. La règle vient du titre de l'article, pas du cas ; mais ce cas n'est plus un cas jamais vu, comme `f-a20` pour A (7.170), et c'est écrit à côté du chiffre dans le README.

**Un point que je croyais ouvert, et qui ne l'était pas.** J'ai écrit ici, puis dit à l'utilisateur, que la section 3.2 du contrat (« Option » : tremblement de terre, pluies et inondations, pertes indirectes) était restée en réserve. C'était faux. Vérifié une heure plus tard avec le moteur : ces trois options sont déclarées comme telles depuis 7.109, et un tremblement de terre répond « à préciser », avec la question de l'option. Le mécanisme existait ; je ne l'ai pas relu avant d'écrire 3.3.1 et 4.1.2, ni avant d'annoncer un écart.

**Une image sans son fichier.** L'image mise en ligne à 15 h 50 montrait quatre cartes orange : le fichier de construction ne copiait pas `regles/traduction.json`. Une ligne ajoutée ; l'image suivante reste à construire.

**Reste à B** : la protection numérique (4.1.4), l'annulation de voyage (4.2.1), les bagages (4.2.2), l'assistance voyage (4.2.3).

### 7.174 Les bagages et la protection numérique de B

Le 24 nov., 17 h à 21 h.

**Deux articles écrits à la main.** Les propositions du modèle avaient plus de vingt contrôles bloquants chacune. Les deux articles sont propres à B : vingt-quatre faits nouveaux, aucun dans le vocabulaire commun, donc seul le banc de B à passer.

**Les bagages (4.2.2).** Quatre garanties : le vol, le vol par agression des valeurs, la casse, et l'incendie, l'explosion ou le dégât des eaux. « En voyage » est un fait du périmètre, avec un lieu où l'on voyage (voie publique, véhicule, autre bâtiment) ; les faits nouveaux ne sont lus que dans ces lieux. La perte d'un bagage n'est pas traduite : le vocabulaire n'a pas d'événement « perte ».

**Ce que la comparaison a attrapé avant le banc.** Sur 2 500 jeux de faits tirés au hasard, avant et après (leçon 155), trois écritures successives produisaient des refus nouveaux. Un véhicule et une remorque écrits en exclusion, puis les valeurs, puis l'objet laissé sans surveillance : chaque fois, le moteur refusait par une exclusion des bagages un sinistre dont on ne savait pas s'il était survenu en voyage, alors qu'une autre garantie restait possible. C'est une règle du moteur (un périmètre seulement inconnu, une exclusion établie : refus) qui convient quand le périmètre inconnu est un lieu, pas quand il est le fait même qui définit la garantie. Retenu : véhicule et remorque dans le périmètre ; les exclusions qui ne se demandent pas ne jouent que si le voyage est établi. Reste un coût mesuré : un incendie ou un dégât des eaux hors de chez soi, sans mention de voyage, passe de « non couvert » à « à préciser » (86 jeux sur 2 500).

**Une tentative qui aurait touché les quatre contrats.** Exclure le bagage prêté pour l'incendie faisait lire « propriétaire des biens » sur trois événements de plus, dans le vocabulaire commun. Vu dans le diff du vocabulaire après l'acceptation, retiré : le bagage prêté qui brûle n'est pas exclu, et c'est écrit dans la proposition.

**Mesure.** B 83 % (85 % au passage précédent), un couvert à tort. Les trois cas qui bougent se passent dans le logement, où ces garanties ne se rattachent pas et où leurs faits ne sont pas lus. Je n'ai pas rejoué le banc sur les règles d'avant (leçon 162) : c'est un raisonnement, pas une mesure.

**La protection numérique (4.1.4).** Une garantie de protection juridique sur l'événement « litige », déjà traduit chez B, avec un fait « litige lié à Internet » à cinq valeurs. Les conditions d'un achat (vendeur de quatre pays, bien neuf entre 150 et 5 000 €) sont des circonstances : la prestation en dépend et seul l'assuré les connaît. Deux faits communs (« usage professionnel », « pays ») avaient été étendus au litige par l'acceptation : remplacés par le domaine du litige et par un fait propre à B.

**L'employeur.** La comparaison montrait un seul changement : un litige avec l'employeur passait de « non couvert » à « à préciser », avec la question « est-ce lié à Internet ? ». J'avais essayé d'écarter du périmètre les domaines sans rapport avec Internet, puis retiré l'essai parce qu'il faisait demander le domaine à une usurpation d'identité. J'ai déposé en l'annonçant comme le point à regarder, avec son critère de retrait. L'essai chez l'utilisateur l'a confirmé. L'essai retiré est revenu : entre une question de trop pour un litige du travail, cas courant, et une question de domaine pour une usurpation dont la lecture ne donne pas le domaine, la seconde coûte moins, et la protection juridique 4.1.3 pose déjà cette question pour le même litige.

**Mesure.** B 85 % avant la correction, 90 % après, un couvert à tort (`f-b18`), aucun cas instable, 233 tests. Le 90 % est le haut de la fourchette, pas un progrès : aucun des cas du banc n'est un litige sur Internet.

**Vu à l'essai, non corrigé.** « Quelqu'un a ouvert un compte en ligne à mon nom et a commandé pour 900 euros » est lu « vol de valeurs », pas « litige ». La garantie n'est pas atteinte. La correction est dans la lecture de l'événement, donc dans le vocabulaire commun : avec les événements de voyage, quatre bancs.

### 7.175 Le voyage : le seul lot de la soirée dans le vocabulaire commun, et B en vert

Le 24 nov., 21 h à 21 h 45.

**Un événement, pas trois.** Les propositions du modèle demandaient un événement par article (« annulation de voyage », « maladie »). Retenu : un seul événement commun, « voyage », et un fait propre à B, « objet de la demande de voyage », à quatorze valeurs. Les trois articles s'y rattachent : l'annulation (4.2.1), l'assistance voyage (4.2.3) et la perte d'un bagage, cinquième garantie de 4.2.2. Un bagage volé ou cassé reste « vol » ou « bris ».

**L'annulation.** Onze motifs couverts, un motif « autre » qui refuse, treize exclusions, chacune avec sa phrase : le contrôle des exclusions les compte une à une, et ma première écriture en citait trois pour dix.

**L'assistance voyage.** Une seule garantie pour quinze prestations : toutes répondent à la même question de couverture. L'appel à l'assistance au moment des faits est une circonstance, donc une question, sauf pour les trois cas que le contrat en dispense. Je l'avais d'abord écrit en exclusion à demander : le moteur de référence ne posait pas la question et couvrait. Les quinze prestations et les dispositions juridiques, que le découpage du contrat avait typées « exclusion », sont classées hors décision avec leur raison.

**« Litige » nomme la fraude en ligne.** L'essai de 21 h (« un compte ouvert à mon nom ») avait été lu « vol de valeurs ». L'aide de l'événement « litige » cite maintenant l'usurpation d'identité, la fraude à la carte et l'atteinte à la réputation.

**Deux effets sur les autres contrats, vus avant le dépôt.** Un test a échoué : une réserve « qui vaut pour tous les sinistres » est reconnue à ce que son fait est lu pour tous les événements ; avec un événement de plus, le déménagement de A ne valait plus « pour tous » et serait réapparu sur chaque réponse couverte de A. Les deux faits de A sont étendus au nouvel événement. Et la réserve de légitime défense, écrite comme un fait, portait le nom d'un fait de D : l'acceptation le déplaçait dans le vocabulaire commun. Elle est passée dans l'aide de la valeur ; le fichier de D n'a pas bougé.

**Mesure, quatre bancs.** A 94 % et 100 %, D 96 % (le refus à tort connu), B 87 %, un seul couvert à tort (`f-b18`), 233 tests. Je n'avais pas de banc « avant » du soir pour A et D : les références sont celles de l'après-midi, et aucun chiffre n'a baissé. Trois essais : le voyage annulé chez B, « à préciser » avec la question de l'option ; la fraude en ligne, lue « litige » et rattachée à la protection numérique, mais avec une question de trop sur le domaine du litige, que la lecture donne et que la confirmation ne retrouve pas ; le voyage annulé chez A, « à examiner par un gestionnaire ».

**Cette dernière réponse est fausse dans sa phrase.** Elle dit « relève d'une garantie qui n'est pas encore traduite ». A est en vert : il n'a pas de garantie de voyage, et la réponse juste est « non couvert ». La phrase date du temps où aucun contrat n'était complet. Non corrigé ce soir : c'est du code de la chaîne, pas une règle.

**B en vert, et ce que cela veut dire.** Tous les articles de B ont leurs règles, et aucune proposition n'a de passage non traduit. Recompté : trois passages restent « laissés au gestionnaire » ou « non distingués », tous dans la protection numérique (l'antivirus, la grève du transporteur, le domicile des membres du ménage) ; ce sont des faits qu'une déclaration ne peut pas établir. Les limites : l'assistance voyage ne vérifie pas l'étranger ; la gravité d'une maladie n'est pas jugée ; et le banc de B ne contient aucun cas de voyage ni de litige sur Internet. Le vert de B dit que le texte est traduit, pas que ces garanties sont mesurées.

### 7.176 Finir B : l'étranger, seize essais, le vélo du hall et la voiture devant la gare

Le 24 nov., 21 h 35 à 22 h.

**À la question « B est-il terminé ? »**, la réponse était oui pour la traduction et cinq points ouverts pour le reste. Les voici.

**L'étranger.** Sept prestations de l'assistance voyage ne valent qu'à l'étranger : une circonstance, avec un fait propre à B. Un médecin payé au Luxembourg : non couvert.

**Seize essais de règles.** Les articles de la soirée n'ont aucun cas dans le jeu fermé, et je ne peux pas en écrire : je connais les règles. Seize jeux de faits exacts, avec la réponse attendue, sont entrés dans les tests ; le moteur Prolog et le moteur de référence doivent concorder. Ils ne mesurent pas la chaîne, la lecture n'y est pas : ils empêchent une régression des règles.

**Le vélo du hall : je visais la mauvaise réponse.** J'ai réécrit l'aide du fait « sous votre surveillance » pour retrouver le refus d'avant. Les deux essais sont restés « à préciser », et c'est la réponse exacte : l'option « dommages aux biens » couvre un vélo volé sous la surveillance directe de l'assuré, où qu'il soit, et « volé dans le hall » ne dit pas s'il l'était. Le refus net datait d'avant la traduction de l'option. C'est le README qui était faux, corrigé : le vélo est refusé chez A, C et D, « à préciser » chez B.

**La voiture devant la gare (`f-b18`).** Couvert à tort depuis le 20 novembre, attribué à la lecture, et laissé. L'essai montre ce que la lecture rend : la voiture comme bien touché, avec l'ordinateur, et le lieu « voie publique ». Les règles étaient justes sur des faits exacts (« dans un véhicule » : la question est posée), mais ces faits-là n'arrivaient jamais. Trois corrections de l'aide du lieu, les 20 et 21 novembre, n'y avaient rien changé.

**La règle.** L'obligation de 3.1.7.4 (véhicule fermé à clé, matériel non visible) se déclenche aussi quand un véhicule figure parmi les biens touchés et que le lieu lu est la voie publique. Elle ne conclut rien : elle pose la question du contrat. Comparé sur 700 jeux de faits ciblés : seuls changent les cas « véhicule touché, voie publique », de « couvert » à « à préciser ». Un cambriolage où la voiture du garage est abîmée n'est pas concerné : le lieu n'est pas la voie publique.

**Ce que c'est, dit sans détour.** Une règle écrite pour rattraper une lecture, en regardant un cas du jeu fermé. Je l'ai proposée à l'utilisateur comme un choix, avec ce que chaque branche coûte : un couvert à tort connu et un jeu fermé intact, ou un produit qui pose la question et un cas de moins jamais vu. Il a accepté. Ma recommandation allait dans ce sens : un « couvert » donné à tort est l'erreur la plus chère.

**Mesure.** B 90 %, zéro couvert à tort, aucun cas instable, portes passées, 249 tests. Ce zéro compte deux cas vus sur vingt (`f-b19`, `f-b18`) ; c'est écrit dans le tableau du README.

### 7.177 Relire le code après une journée de travail à la main

Le 24 nov., 22 h 10 à 22 h 40.

**La question de l'utilisateur** : jeter un œil au code, voir ce qui peut être généralisé. Je n'ai pas relu les 8 500 lignes : j'ai cherché ce que j'avais fait à la main dans la journée, parce que c'est là qu'une règle du code manque. Aucun nom de contrat ne décide de rien dans `src/` ; six points restaient manuels ou en double.

**Fait ce soir, trois points.**

*Un contrat complet refuse ce qu'il ne garantit pas.* « Relève d'une garantie qui n'est pas encore traduite » était écrit en dur dans la chaîne, alors que `regles/traduction.json` dit quels contrats sont traduits en entier. Pour ceux-là, un événement sans garantie est un refus quand la déclaration ne porte que sur lui (« aucune garantie de ce contrat ne porte sur cet événement », phrase qui existait). Si elle porte aussi sur autre chose, le dossier reste à examiner, et la phrase dit ce qui manque. L'événement « autre » n'est pas concerné : le moteur ne le compte pas parmi les non traduits. Le moteur n'est pas modifié ; la règle est dans la chaîne, là où la phrase se construit. Les tests ne dépendent plus de l'état déclaré : par défaut aucun contrat n'y est complet, et le test qui porte sur un contrat complet le dit.

*L'acceptation du vocabulaire recopie ce que le relecteur écrit.* La mention « fait des conditions particulières » et une restriction de lecture se rajoutaient à la main après chaque acceptation : sept fois dans la journée, et un oubli à midi. Elles sont recopiées, si la source est celle que le code connaît et si la restriction porte sur des valeurs du vocabulaire.

*Deux listes en dur.* La table des contrats du jeu fermé (A, B, D) se lit dans les cas et dans le dossier des règles ; l'export rejoué donne les mêmes fichiers, octet pour octet. Le fichier de construction de l'image copie le dossier des règles entier, moins ce qui ne sert qu'à rédiger : c'est la copie fichier par fichier qui avait oublié l'état de traduction (7.173).

**Laissé, puis repris.** Les options (7.178) et l'exclusion qui refuse avant qu'on sache si sa garantie est en jeu (7.179) : les deux ont été faits dans l'heure, à la demande de l'utilisateur. Ce qui suit est ce que j'en disais avant de les regarder. C'est un changement du moteur : une demi-journée, avec les quatre bancs. La veille d'une livraison, l'écrire ici vaut mieux que le faire mal. Un troisième point, plus petit, reste aussi : étendre de lui-même les faits « pour tous les sinistres » quand un événement est ajouté (leçon 177).

**Mesure, et un défaut que le test n'avait pas vu.** 255 tests chez l'utilisateur ; A 94 % et 100 %, B 88 %, D 96 %, zéro couvert à tort sur A et B. Mais l'essai du voyage annulé chez A affichait « Décision : INCERTAIN » sous la phrase « Non couvert », avec « faire examiner par un gestionnaire ». La validation des citations ramène à « à préciser » toute réponse ferme sans citation vérifiable, et ce refus n'a rien à citer. Mon test s'arrêtait à la construction du verdict, une étape avant. Corrigé : c'est la seule exception admise à la validation, pour un contrat traduit en entier et cette phrase-là ; le test va maintenant jusqu'au bout de la chaîne.

### 7.178 Une seule façon d'écrire une option

Le 24 nov., 22 h 20 à 22 h 50.

**La demande.** J'avais classé ce point « non, la veille du gel » : trois écritures d'une option coexistent, et les unifier me semblait demander de réécrire les règles de A, B et D. L'utilisateur l'a demandé quand même. En regardant de plus près, le risque que je décrivais n'était pas dans ce qu'il fallait faire.

**Ce qui se décide pareil, et ce qui ne se décide pas pareil.** La déclaration en tête de fichier (`option(…)`, 7.109) et la circonstance « option = oui » donnent la même réponse : « à préciser » tant que l'option est inconnue, refus si elle n'est pas souscrite. La troisième écriture, elle, décide autre chose : la mise en réserve automatique d'une phrase qui cite les conditions particulières répond « couvert, sous réserve ». L'erreur de 17 h n'était pas d'avoir deux écritures équivalentes, mais que rien ne dise au relecteur laquelle des deux décisions il était en train de choisir : je la choisissais sans le voir, par les mots de la phrase que je citais.

**La règle.** Une circonstance peut porter la marque « option ». Marquée, elle reste une question, quel que soit le texte cité. Non marquée et citant les conditions particulières, elle devient une réserve, et la note de contrôle rappelle la marque. Un contrôle bloquant refuse une marque sur autre chose que « fait = oui », ou sur un fait qui n'est pas un fait des conditions particulières. Le code ne devine pas si un article est une option : les titres « Option » de B ne sont pas tous dans la base (3.2 et 3.3 manquent, 4.1 est lu « O ption »). C'est le relecteur qui le dit, une fois, à un endroit que le contrôle vérifie.

**Dix propositions marquées, zéro règle changée.** Neuf articles de B et un de D portent maintenant la marque. Pour chacun, les règles générées avant et après sont identiques au caractère près : rien à réaccepter, aucun banc à repasser pour ce point.

**Ce qui reste double.** Huit options plus anciennes (trois chez B, une chez A, quatre chez D) sont déclarées en tête de leur fichier de règles. Elles décident comme les autres. Les convertir changerait le texte de règles mesurées, pour aucun changement de réponse : pas ce soir. La consigne de rédaction donnée au modèle ne parle pas encore de la marque.

**Ce que j'avais mal estimé.** J'ai annoncé « une demi-journée, risque élevé » pour un travail que j'imaginais comme une réécriture. Posé comme « où le relecteur dit-il que c'est une option, et qui le vérifie ? », c'était un champ, un contrôle et deux tests : 236 tests ici, sans Prolog.

### 7.179 Une garantie écartée ne refuse pas à la place d'une garantie possible

Le 24 nov., 22 h 25 à 23 h.

**Le défaut.** Quand le périmètre d'une garantie est inconnu et qu'une de ses exclusions est établie, le moteur la tient pour « exclue, que la garantie s'applique ou non » (7.164). C'est juste : elle ne peut pas couvrir. Mais la combinaison la comptait comme une garantie qui refuse, et un refus l'emporte sur les garanties seulement possibles. De l'argent volé dans la rue était refusé par l'exclusion des bagages (« les valeurs ne sont pas des bagages ») sans qu'on sache si le vol avait eu lieu en voyage, alors que le vol par agression pouvait encore s'appliquer. Je l'avais contourné à la main le soir même : « et en voyage » dans dix-huit exclusions des bagages, « et l'un des cinq risques » dans cinq de la protection numérique (leçon 174).

**La règle.** Une garantie écartée ne peut pas couvrir, et rien ne lui rattache le sinistre : elle n'a pas à refuser pour les autres. Quand toutes les garanties qui refusent sont seulement écartées et qu'une autre reste possible, la réponse est « à préciser », avec les questions de celle-ci. Si aucune n'est possible, le refus demeure, et sa phrase cite l'exclusion comme avant. Si le sinistre est rattaché à la garantie (périmètre établi), rien ne change. Quatre lignes dans le moteur Prolog, autant dans le moteur de référence.

**Mesuré avant de déposer, avec le moteur de référence.** Les 141 cas à faits exacts du dépôt (97 du golden set de A, 15 de B, les cas de validation et de non-régression) : une seule réponse changeait, un portefeuille volé à la tire dans le tram chez B, de « non couvert » à « à préciser ». C'était ma précaution manuelle qui parlait : en cachant l'exclusion des valeurs tant que le voyage n'était pas dit, elle laissait la garantie des bagages « possible ». La règle du moteur rend la précaution inutile ; retirée, le cas redevient un refus. Les deux se tenaient : on ne pouvait pas garder l'une avec l'autre.

**Sur des faits tirés au hasard**, 400 par contrat : une réponse change chez A, une chez D, aucune chez C ; chez B, 12 sur 500 avec les précautions retirées. Toutes passent de « non couvert » à « à préciser », et celles que j'ai lues sont des corrections : une catastrophe naturelle refusée parce que l'option « tremblement de terre » n'est pas souscrite, alors que rien ne dit que ce n'est pas une inondation, que l'autre option couvre.

**Ce que cela coûte.** Des refus deviennent des questions : c'est le sens du changement, et un banc peut y perdre un « non couvert » juste. Seul le banc le dira ; 237 tests ici, sans Prolog, et le moteur Prolog modifié n'a pas tourné sur ma machine.

**Ce que j'avais mal estimé, une seconde fois.** « Une demi-journée, risque élevé. » La règle tenait en quatre lignes ; ce qui demandait du temps était de savoir ce qu'elle changeait, et les cas à faits exacts l'ont dit en une minute.

**Mesuré le soir même, 22 h 40 à 22 h 53, sur le poste où tourne SWI-Prolog.** Les deux articles réacceptés sans contrôle bloquant. 257 tests passés, un ignoré : le moteur Prolog modifié et le moteur de référence concordent. L'annulation d'un voyage chez A : « non couvert », et cette fois la décision affichée le dit aussi (7.177). A : 94 % (partie test) et 100 % (jeu fermé) ; B : 90 %, deux cas instables ; D : 96 %. Aucun couvert à tort, aucun refus à tort, sur les quatre bancs. Rien n'a baissé.

Deux choses à dire à côté de ces chiffres. *Le portefeuille volé dans le tram*, redevenu un refus avec des faits exacts, sort « à préciser » dans la chaîne complète : la lecture donne bien « pas de violence », mais la déclaration ne le dit pas en toutes lettres (« subtilisé sans que je m'en rende compte »), le fait porte la décision, il n'est pas confirmé, et la chaîne pose la question au lieu de refuser (7.43 à 7.50). C'est une question dont la réponse se devine ; ce n'est pas le changement du moteur, et je ne l'ai pas corrigé. *La porte de A sur les décisions changées par la lecture* échoue toujours, à 3 pour un seuil de 2, avec les trois mêmes cas qu'à 21 h 28 et 22 h 29 (`velo-06`, `g-h03`, `g2-p01`) : elle échouait avant ce soir, et le seuil n'est pas relevé.

### 7.180 Un événement nouveau n'enlève plus à un fait qu'il vaut pour tous les sinistres

Le 24 nov., 22 h 40 à 23 h 10.

**Le défaut.** Certains faits sont lus pour tous les événements : « avez-vous signalé votre déménagement ? » chez A. Parce qu'ils valent pour tous les sinistres, leur réserve n'est pas répétée sous chaque réponse. « Pour tous » se calcule : la liste des événements où le fait est lu couvre toute la liste des événements. Le jour où « voyage » est entré dans le vocabulaire, ces faits n'étaient plus lus « pour tous », et la réserve du déménagement serait revenue sous chaque réponse couverte de A. Un test l'a rattrapé ; j'ai étendu les deux faits à la main.

**La règle.** Quand l'acceptation ajoute un événement, elle étend elle-même la liste de tout fait qui couvrait jusque-là tous les événements, et le dit dans son compte rendu (« vaut pour tous les sinistres, lue aussi pour… »). Un fait lu pour quelques événements seulement n'est pas touché : rien ne dit qu'il concerne le nouveau.

**Mesure.** Un test : un événement inventé est accepté, les faits généraux le reçoivent, un fait partiel ne le reçoit pas. Aucune réponse actuelle ne peut changer : la règle ne joue qu'à l'ajout d'un événement, et les bancs ne sont pas rejoués pour elle.

### 7.181 Les options qui ouvrent une garantie : une seule écriture, et une neuvième option trouvée

Le 24 nov., 23 h 05 à 23 h 40.

**La question.** Après 7.178, huit options plus anciennes restaient déclarées en tête des fichiers de règles (`option(...)`), en plus d'une exclusion « option non souscrite » dans leur article. J'avais écrit qu'elles « décidaient pareil » et que les convertir demanderait de réécrire des règles mesurées. Je ne les avais pas lues une par une.

**Lues, elles sont de deux sortes.** Quatre ouvrent une garantie entière : le matériel multimédia chez A, le tremblement de terre, les pluies et inondations et les pertes indirectes chez B. Les quatre de D lèvent une exclusion pour un bien : la véranda, les objets de valeur, le jardin, la piscine. Le pack jardin n'ouvre pas une garantie, il fait qu'un meuble de jardin n'est plus exclu de la tempête. Une circonstance sur la garantie ne dit pas cela : chez D, la déclaration en tête n'est pas un doublon, et elle reste.

**Mesuré avant de rien déposer**, avec le moteur de référence : les quatre premières converties en circonstances marquées « option », comparées aux règles d'avant sur les 141 cas à faits exacts, sur 3 000 jeux de faits tirés au hasard par contrat, et sur 3 000 autres ciblés sur ces options (souscrite, non souscrite, non dite). Aucune décision ne change. Ce qui change est l'ordre des questions : écrite en circonstance, l'option se demande avant les autres points de sa garantie, au lieu de se demander après.

**Ce que la comparaison a trouvé sans le chercher.** Le « matériel multimédia » de B (3.1.7) est une option, écrite comme les autres en exclusion « option non souscrite », mais déclarée nulle part : une neuvième, que ma liste de huit ne contenait pas. Sans la déclaration, le moteur la traitait en garantie de base : un ordinateur cassé était « couvert », l'option devenant une réserve. C'est le défaut de 7.173, sur un article que je croyais réglé. Convertie, la garantie répond « à préciser » et demande si l'option est souscrite ; 15 jeux de faits au hasard sur 3 000 passent de « couvert » à « à préciser », 73 sur 3 000 en ciblé, aucun dans un autre sens.

**Ce qui est fait.** Cinq propositions (A 6.1 ; B 3.1.7, 3.2.1, 3.2.2, 3.2.3) : l'exclusion « option non souscrite » devient une circonstance marquée « option ». Les quatre déclarations en tête des règles de A et de B sont retirées. Le contrôle de couverture compte la phrase d'une circonstance « option » comme traduite : il la réclamait une seconde fois, puisqu'elle n'était plus dans une exclusion. Les règles obtenues par l'acceptation sont, fait pour fait, celles qui ont été mesurées.

**Un test a dû changer, et il faut le dire.** Le vol dans la voiture garée (7.106, `f-b18`, un cas vu) attendait la question « le véhicule était-il fermé à clé ? ». Elle vient maintenant après « l'option est-elle souscrite ? » : le test vérifie les deux temps. C'est une question de plus avant la bonne, sur un cas du jeu fermé ; le banc de B dira ce que cela coûte.

**Ce que je n'ai pas fait.** « Sous réserve que la garantie vol ait été accordée » (3.1.7.1) reste une réserve : le vol est une garantie de base de B que le contrat laisse retirer, pas une option rangée sous un titre « Option ». Le moteur Prolog n'a pas tourné sur ma machine.

**Ce que j'avais mal estimé, une troisième fois.** J'avais écrit « elles décident pareil » sans les lire : c'était vrai des huit, et la neuvième, que je ne voyais pas, couvrait à tort. Une liste qu'on n'a pas relue cache ce qui n'y est pas.

**Mesuré à 23 h 40, avec SWI-Prolog et le modèle.** Les cinq articles sans contrôle bloquant ; 261 tests passés, un ignoré. A : 94 % (partie test) et 100 % (jeu fermé). B : 93 % (90 % une heure plus tôt), un cas instable. Aucun couvert ni refus à tort. Deux portes échouent, aucune sur une décision : celle de A sur les décisions changées par la lecture (3 pour un seuil de 2, comme avant), celle de B sur le temps de réponse (11,3 s au 95e centile pour un seuil de 10, un appel lent ; médiane 4,3 s).

### 7.182 Une exclusion du vol qui refusait le bris

Le 24 nov., 23 h 40 à minuit.

**Comment c'est apparu.** Pour vérifier 7.181, une phrase que j'avais écrite moi-même, hors de tout jeu de cas : « Mon ordinateur portable est tombé de la table du salon, l'écran est cassé. » J'annonçais « à préciser ». La réponse a été « non couvert », avec pour preuve « les vols commis par ou avec la complicité de l'Assuré ».

**Trois causes, une seule corrigée.** La lecture a ajouté « causé par l'assuré », que la phrase ne dit pas. Une question hors sujet est restée (« des débris de vitrages ? »). Et une règle était fausse depuis le 19 novembre : l'exclusion des vols commis par l'assuré ou sa famille (3.1.7.2) était commune aux deux garanties du matériel multimédia, le vol et le bris. Dès que l'auteur était lu « assuré », le bris était refusé pour complicité de vol. Seule cette règle est corrigée ici : l'exclusion appartient à la garantie vol.

**Une première écriture, retirée avant dépôt.** J'avais d'abord gardé l'exclusion commune en lui ajoutant « et l'événement est un vol ». Un test l'a refusée : établie à moitié par l'événement, l'exclusion faisait demander « qui est l'auteur ? » à chaque vol, avant « le véhicule était-il fermé ? ». C'est le piège déjà noté dans la relecture de cet article pour la garantie vol. Rangée dans la garantie vol, la condition reste celle d'avant, et rien ne change pour un vol.

**Mesuré avant de déposer, avec le moteur de référence.** L'ordinateur tombé : « à préciser » (l'option est-elle souscrite ?), « couvert » si elle l'est, « non couvert » si elle ne l'est pas. Les 15 cas à faits exacts de B et 700 jeux de faits au hasard : aucune décision ne change. 700 jeux ciblés (bris, accident, vol ou heurt, auteur connu) : 74 décisions changent, toutes sur un bris ou un accident, vers « couvert » ou « à préciser » ; aucune sur un vol. Cela ajoute des « couvert » : un bris accidentel causé par l'assuré ou un proche, option souscrite. C'est ce que dit l'article (« tout bris ou destruction accidentel résultant d'une chute, d'un choc ») ; le banc de B dira si l'un d'eux est à tort.

**Mesuré à 23 h 53, avec SWI-Prolog et le modèle.** L'article sans contrôle bloquant ; 261 tests passés, un ignoré. L'ordinateur tombé de la table : « à préciser », une seule question, « vos conditions particulières mentionnent-elles la garantie matériel multimédia ? », et plus aucune citation sur le vol. La lecture donne toujours « causé par l'assuré » : elle ne refuse plus rien. Jeu fermé de B : 92 % (93 % dix minutes plus tôt, le même cas instable faisant l'écart), aucun couvert ni refus à tort, portes passées. Aucun « couvert » à tort n'est apparu ; mais ce banc mesure peu le matériel multimédia (je n'y connais qu'un cas, `f-b18`, un vol) : la limite de 7.176 vaut ici aussi.

**Ce qui n'est pas corrigé.** La lecture qui nomme un auteur que la déclaration ne nomme pas, et la question sur les vitrages. La seconde ne change pas la décision ; la première se mesurerait sur toute la lecture, pas la veille du gel.

### 7.183 Le code rangé par métier, et une description pour chaque fonction

La nuit du 24 au 25 nov.

**La demande.** Un code clair, commenté, et des fichiers rangés de façon logique, avant le gel. Quatre étapes, dans cet ordre : nettoyer, décrire, ranger, nettoyer encore.

**Nettoyer.** Peu à retirer : aucun import inutile, aucun code en commentaire, aucune note « à faire ». Deux membres morts depuis le retrait des anciennes méthodes sont supprimés (`Base.maj_rapport`, `Clause.reference`).

**Décrire.** 137 fonctions, classes et méthodes publiques n'avaient pas de description : chacune en a une, en une ou deux phrases, qui dit ce qu'elle rend et dans quel cas elle échoue. Une quinzaine de commentaires là où le code ne s'explique pas seul (la gouttière d'une page en deux colonnes, l'élagage de l'arbre de preuve, l'ordre des questions et des réserves). Vérifié par le code, pas à l'œil : l'arbre syntaxique de chaque fichier, descriptions retirées, est identique avant et après. Aucune ligne exécutée n'a changé.

**Ranger.** Vingt-cinq fichiers à plat dans un seul dossier faisaient quatre métiers. Ils sont en quatre sous-dossiers : `contrat/` (lire un contrat), `analyse/` (analyser un sinistre), `redaction/` (rédiger les règles, déjà rangé), `mesure/` (les jeux de cas et les bancs). Restent à la racine ce que tous partagent : les modèles de données, le client du modèle, les consignes, la configuration. Les contrôles du découpage s'appelaient `controles.py`, comme ceux de la rédaction : ils deviennent `controle_decoupage.py`. Chaque sous-dossier s'ouvre sur une page qui dit ce qu'il contient.

**Ce que le rangement a changé dans le code exécuté**, et rien d'autre : les imports ; un chemin (le moteur cherchait `regles/` deux dossiers au-dessus de lui, il est un dossier plus bas) ; le nom du module des consignes de lecture, donc le manifeste des versions (les empreintes des consignes, elles, n'ont pas bougé : aucun texte envoyé au modèle n'a changé) ; le nom de la commande du jeu fermé (`python -m couverture.mesure.ferme`). Vérifié de trois façons : l'arbre syntaxique de chaque fichier déplacé, imports mis à part, est identique ; les 267 imports du projet sont résolus un par un (le module existe, le nom y est défini) ; les tests.

**Ce que je n'ai pas pu vérifier sur ma machine.** Les tests de l'API (FastAPI n'y est pas installé) et ceux qui appellent SWI-Prolog : 241 tests passent ici, 8 sont ignorés. Ils tournent sur le poste et en intégration continue ; c'est là que le rangement est jugé, avec un banc.

**Ce que je n'ai pas fait.** Supprimer des fichiers de données ou d'anciennes propositions : la liste est donnée, la décision n'est pas la mienne. J'avais aussi écrit ici que je ne découperais pas les fonctions de plus de 80 lignes, parce que ce serait réécrire du code mesuré : c'est fait en 7.184, avec la mesure qui manquait à mon refus.

### 7.184 Les huit longues fonctions, découpées et comparées à elles-mêmes

La nuit du 24 au 25 nov., vers 2 h.

**La demande.** Les fonctions de plus de 80 lignes, réécrites pour qu'elles se lisent. J'en annonçais sept ; avec leurs descriptions, elles sont huit : le contrôle d'une proposition (240 lignes), l'acceptation du vocabulaire (134), le découpage d'un contrat en clauses (131), la commande `regles` (119), la réponse (114), la fiche PDF (112), le rapport du banc (98), le rejeu d'un jeu de cas (83).

**La méthode.** Sept d'entre elles sont une suite d'étapes : chaque étape devient une fonction nommée, avec sa description, et la fonction d'origine n'est plus que leur enchaînement. Les lignes sont déplacées telles quelles, par un script qui les coupe et les recolle, pas retapées. La huitième, le découpage en clauses, était une boucle qui partageait six variables avec deux fonctions internes : elle devient un petit objet (`_Decoupage`) qui porte cet état, avec une méthode par cas (une ligne ordinaire, un titre numéroté, un titre sans numéro). Plus aucune fonction du code ne dépasse 80 lignes.

**La preuve, fonction par fonction.** L'arbre syntaxique ne suffit plus : le code a changé de forme. Chaque fonction est donc comparée à sa version d'avant, sur beaucoup d'entrées, et la sortie doit être identique.

| Fonction | Comparée sur | Résultat |
|---|---|---|
| Contrôle d'une proposition | les 81 propositions des quatre contrats, trois variantes chacune : 1 376 problèmes relevés | identique |
| Acceptation du vocabulaire | les mêmes 81 propositions, sur un vocabulaire appauvri : 502 lignes d'ajout, et les fichiers écrits | identique |
| Réponse (`verdict`) | 9 246 décisions du moteur de référence (cas à faits exacts, faits au hasard, événements non traduits, contrat complet ou non) | identique |
| Découpage en clauses | le texte des cinq contrats de la base et le PDF de test, sous quatre profils : 24 découpages, 3 102 clauses | identique |
| Rapport du banc | les 332 rapports de `data/bancs`, seuls puis comparés au précédent : 1,9 million de caractères | identique |
| Fiche PDF | 14 réponses de formes différentes : texte, position de chaque mot, tracés | identique |
| Rejeu d'un jeu de cas | 4 jeux simulés (pannes du fournisseur comprises), un cas à la fois puis quatre | identique |
| Commande `regles` | 25 appels (cinq contrats, cinq jeux, un cas seul, le bilan, un refus), SWI-Prolog simulé | identique |

**Ce que la comparaison a montré en passant.** Deux passages de l'ancien contrôle sur la même proposition ne rendaient pas toujours les problèmes dans le même ordre : une boucle parcourait un ensemble. Les comparaisons sont donc faites à graine fixe. L'ordre ne change aucune gravité ; je ne l'ai pas corrigé, pour ne rien changer d'autre que la forme.

**Ce qui n'est pas prouvé.** La commande `regles` n'a tourné qu'avec un SWI-Prolog simulé, et les tests de l'API ne tournent pas sur ma machine. 241 tests passent ici, comme avant ; les 261 du poste, puis un banc, jugent le reste.

**Ce que j'avais mal estimé.** J'avais refusé ce découpage deux fois, comme « du code mesuré qu'on ne réécrit pas la veille du gel ». L'objection était juste tant qu'il n'y avait pas de mesure ; elle tombait dès qu'on pouvait comparer chaque fonction à elle-même. Je n'avais pas pensé à le faire.

### 7.185 Un second jeu écrit sans voir les règles, et C dit pour ce qu'il est

*25 novembre, 11 h.*

**Après le rangement, les mêmes chiffres.** Quatre bancs relancés sur le code rangé et découpé (7.183, 7.184) :
A 93,5 % sur la partie test (la porte de lecture échoue toujours, 3 décisions changées pour 2 admises, comme
avant le rangement), A 100 % sur le jeu fermé, B 90 % (91,7 % la veille : un passage sur soixante, dans le
bruit), D 96 %. Aucun couvert à tort, aucun refus à tort.

**Le contrat C.** Le README le rangeait parmi les limites. Ce n'en est pas une : C a été intégré pour mesurer
ce que coûte un contrat de plus, étape par étape, et deux garanties suffisaient à cette mesure. Le README et
`COMPRENDRE.md` le disent maintenant ainsi.

**Le jeu « aveugle ».** Trois cas du jeu fermé (`f-a20`, `f-b19`, `f-b18`) ont servi à corriger une règle : ce
jeu n'est plus tout à fait fermé. Un second est monté de la même façon (7.79), dans `data/aveugle` : 60
déclarations, 20 pour A, 20 pour B, 20 pour D, écrites par trois agents neufs, un par contrat, qui n'ont reçu
que le texte des conditions générales. Je ne les ai pas écrites : je connais les règles. Chaque citation a été
retrouvée mot pour mot dans le texte et chaque article existe. Par contrat : 7 couverts, 7 non couverts, 6
incertains. Les annotateurs ont signalé leurs propres doutes (la responsabilité locative de A, la formule des
dommages électriques de D) : je n'y ai pas touché, le second avis et l'arbitrage sont là pour cela.

Dans le code, peu de chose : `evaluation.JEUX_FERMES = ("ferme", "aveugle")`, l'option `--jeu` de
`couverture.mesure.ferme` et du banc, et la banque d'exemples qui tient ses exemples loin des déclarations des
deux jeux. Un test monte un jeu « aveugle » de bout en bout.

**Le second avis et l'arbitrage (11 h 25).** Mistral Large a répondu aux 60 déclarations sans voir la première
réponse : 54 accords stricts, 5 souples, 1 désaccord (`av-a09`, de l'eau de pluie passée par le bas d'une
fenêtre : non couvert pour l'agent, couvert pour Mistral au titre de l'inondation). Un troisième agent, neuf, qui
n'a reçu que le texte et les deux avis, a retenu le premier : le contrat exclut les infiltrations par les
fenêtres, et de fortes pluies ne font pas une inondation au sens du lexique. Aucun cas écarté.

**La mesure (11 h 37), une seule fois, trois passages par banc.**

| Contrat | Justes | Exactes | Couverts à tort | Refus à tort | Instables | Portes |
|---|---|---|---|---|---|---|
| A | 95 % | 75 % | 0 | 0 | 0 | passe |
| B | 58 % | 58 % | 1,3 | 2,7 | 4 | échoue |
| D | 78 % | 73 % | 2 | 1 | 2 | échoue |

Sur les jeux fermés, une heure plus tôt : A 100 %, B 90 %, D 96 %. L'écart est donc de 5 points pour A, de 32
pour B, de 18 pour D. Les couverts à tort : chez B, `av-b13` (un rocher tombé d'un talus, exclusion commune des
chutes de pierres) à chaque passage et `av-b11` (une tablette volée dans une voiture) une fois sur trois ; chez
D, `av-d11` (des bijoux volés, qui relèvent de l'option objets de valeur) et `av-d16` (une trottinette
électrique) à chaque passage. Chez B, dix cas sur vingt se trompent ou varient ; les thèmes « base » (33 %) et
« définition » (0 %) tombent, les thèmes « option » et « manque » tiennent (100 %).

**Une ressemblance trouvée par le contrôle.** Une fois le jeu exporté, le test qui tient les exemples de lecture
loin des cas de mesure a échoué : `ex-d14`, un exemple de la banque (des tags sur un mur, plainte déposée),
ressemble à `av-d13` (indice 0,40). L'exemple est antérieur, l'annotateur ne l'a pas vu : c'est un hasard, sur un
sinistre banal. Retirer l'exemple changerait la lecture qu'on vient de mesurer ; retirer le cas retoucherait le
jeu après la mesure. Les deux restent, et le couple est déclaré dans `data/lecture/proches_declares.json`, que
le contrôle lit : toute autre ressemblance reste refusée. Ce cas était juste aux trois passages ; sans lui, D
serait à 77 % au lieu de 78 %.

**Ce que je n'ai pas fait.** Je n'ai ouvert ni les faits lus ni les règles pour ces cas : chercher la cause,
c'est déjà commencer à régler, et ce jeu perdrait ce qui le rend utile. Les chiffres sont dans le README, à côté
des autres, avec la phrase qui convient : A est le contrat le plus travaillé et il tient ; B et D ont été
réglés sur des jeux que je regardais, et ces jeux les flattaient de vingt à trente points.

**Ce que cela change.** Rien dans le code avant la livraison. Dans le discours : la promesse « jamais couvert à
tort » n'est tenue que sur les cas qui ont servi à régler ; sur des cas neufs, B et D couvrent à tort une à
deux fois sur vingt. La suite logique, après la livraison : corriger d'après ces cas en les déclarant vus,
puis écrire un troisième jeu, et recommencer jusqu'à ce que l'écart entre jeu vu et jeu neuf se ferme.

### 7.186 Corriger d'après le jeu aveugle, et en écrire un troisième pour mesurer

*25 novembre, midi.* 58 % sur B : « ce n'est pas bon du tout », et il reste six heures. Le commit de 7.185 fixe la
mesure à l'aveugle ; à partir de là, les 60 cas du jeu « aveugle » sont des cas **vus**, et ce qui suit ne peut
plus se mesurer sur eux.

**Ce que les faits lus disaient.** Les rapports du banc gardent, pour chaque passage, les faits retenus par la
lecture. Rejoués sur les règles sans modèle (les mêmes faits, le moteur de référence), ils redonnent les chiffres
du banc à un cas près : de quoi séparer ce qui vient des règles de ce qui vient de la lecture, et voir l'effet
d'une correction en une seconde.

| Défaut | Cas | D'où il vient | Correction, écrite comme une règle |
|---|---|---|---|
| Les exclusions communes de B (2.10) n'étaient pas traduites | un rocher tombé d'un talus, couvert comme un heurt | règles | l'article 2.10 traduit pour toutes les garanties (`exclusion(tous, …)`) : chute de pierres et mouvement de terrain, faute intentionnelle, guerre, nucléaire ; jamais demandés |
| Deux garanties de base de B traitées en options | un téléviseur tombé, un facteur qui glisse sur le verglas : « à préciser » | règles (ma décision de 7.181) | le contrat range 3.1.7 et 3.1.10 sous « 3.1 Garanties de base », avec la phrase de l'incendie et du vol : présumées souscrites, avec la réserve. Un test interdit une circonstance « option » dans un article 3.1.x |
| La vitre d'une voiture comptait comme un vitrage du bâtiment | une tablette volée dans une voiture, couverte une fois sur trois | règles | bris de vitrages et dégradations lors d'un vol : pas dans un véhicule (exclusion jamais demandée, pour ne pas demander le lieu à chaque vitre) |
| Chez D, les bijoux volés étaient couverts sans l'option | une bague et une chaîne volées | règles | l'exclusion « sauf option objets de valeur » se demande |
| Une trottinette électrique lue comme un vélo | un piéton renversé, couvert chez D | vocabulaire | une valeur `engin_motorise_personnel`, enfant de `vehicule_moteur` : les règles écrites pour les véhicules à moteur s'appliquent, dans les quatre contrats |
| Le trampoline lu « matériel de sport » | refusé chez B, dont le lexique le range dans le mobilier de jardin | vocabulaire | l'aide du mobilier de jardin nomme les jeux d'extérieur, le barbecue, le parasol |
| Un parquet gonflé lu « moisissure » | une conduite rompue dans une cloison, refusée | vocabulaire | l'aide dit ce qui n'est pas une moisissure |
| Une victime qui demande réparation lue « responsabilité » | un piéton renversé par un cycliste, refusé chez D | vocabulaire | l'aide de « litige » et de « responsabilité » dit de quel côté se trouve l'assuré |
| Le serrurier demandé à l'assistance, ou appelé soi-même | « à préciser » chez A et B | vocabulaire | l'aide d'`intervention_mandatee` donne les deux situations |

**Ce que je n'ai pas corrigé.** La salle des fêtes louée (B, 3.1.8.6) : j'ai essayé d'en faire une garantie qui
décide seule ; elle posait alors ses questions (le pays, le séjour) à chaque incendie, et le test des questions
hors sujet l'a refusé. Elle reste accessoire, et ce cas reste faux. Les « à préciser » instables (une porte non
fermée à clé sans violence dite, un congélateur débranché, une tempête suivie de pluie) : ils tiennent à la
lecture d'un passage à l'autre, pas à une règle.

**Ce qui change ailleurs.** L'ordinateur tombé de la table (7.182) redevient « couvert », avec la réserve des
conditions particulières : c'est la conséquence de la règle sur les garanties de base, et c'est ce que répondent
deux lecteurs du texte. Un cas du golden set de B (`b-v07`, un téléphone volé sous la menace) passe pour la même
raison de « à préciser » à « couvert » ; son annotation est corrigée et datée. Sur les 112 cas à faits exacts des
trois contrats, c'est la seule décision qui bouge.

**Sur les faits lus à 11 h 37, sans relire** : B passe de 58 % à 70 %, D de 73 % à 78 %, et les couverts à tort
de 4 à 3 et de 6 à 3 passages. Le reste dépend de ce que la lecture fera du vocabulaire corrigé : cela ne se
voit que sur un banc.

**Le troisième jeu.** Mesurer ces corrections sur le jeu qui les a inspirées serait se flatter une seconde
fois. Trois agents neufs écrivent `data/neuf` : 60 déclarations, mêmes consignes, avec une demande de plus,
éviter les situations rebattues (je leur ai nommé celles du second jeu, pour qu'ils n'y retombent pas). Second
avis, arbitrage, puis une mesure, qui ira dans le README à côté des deux autres.

**La mesure sur le troisième jeu (12 h 37).** Second avis : 55 accords stricts, 2 souples, 3 désaccords, arbitrés
par un agent neuf sur le seul texte, tous en faveur du premier annotateur (une coupure de courant dont la durée
n'est pas dite, une responsabilité civile rangée sous un titre d'option, la télévision d'un frère). Puis une
mesure, trois passages :

| Contrat | Justes | Exactes | Couverts à tort | Refus à tort | Instables |
|---|---|---|---|---|---|
| A | 60 % | 55 % | 4 | 1 | 0 |
| B | 50 % | 47 % | 2 | 0 | 4 |
| D | 80 % | 58 % | 1 | 1 | 1 |

C'est moins bon que le second jeu pour A (95 %) et pour B (58 %), un peu mieux pour D (78 %). Deux lectures
possibles, et les deux sont vraies en partie : le troisième jeu est plus dur (j'ai demandé des situations
inhabituelles), et mes neuf corrections ne valaient que pour les cas qui les avaient inspirées. Ce que je
retiens : A n'était pas « bon à 95 % », il l'était sur vingt situations courantes ; et un contrat réglé pendant
une semaine sur des jeux que je voyais ne répond juste, sur l'inconnu, qu'une fois sur deux à quatre fois sur
cinq. Les chiffres vont tels quels dans le README, enregistrés avant que j'ouvre ces cas.

### 7.187 Un second tour, sur les couverts à tort du troisième jeu

*25 novembre, 12 h 45.* « Encore un tour de corrections », en commençant par les couverts à tort, et une mesure
sur un quatrième jeu. Le commit de 7.186 fixe les chiffres du troisième ; ses 60 cas deviennent des cas vus.

Rejoués sans modèle, les faits lus au banc redonnent 60 %, 50 % et 90 % (A, B, D) : les règles expliquent
presque tout pour A et B ; pour D, la différence avec les 80 % du banc tient à l'étape qui confirme les faits
décisifs.

| Défaut | Cas | Correction |
|---|---|---|
| A : la faute lourde d'un majeur (ivresse) n'excluait que si la lecture disait l'âge | un téléviseur cassé après un pot de départ, couvert | l'exclusion se demande : la faute dite, on demande si l'auteur est mineur ; sans faute dite, aucune question de plus |
| A et D : pas de seuil pour les recours | un manteau déchiré (140 €), des lunettes (180 €), couverts | le seuil du contrat (250 EUR, 300 €) en exclusion jamais demandée, avec une variable par contrat |
| B : un vol en location de vacances passait par la garantie vol du bâtiment désigné | des clubs de golf volés au Portugal, couverts | l'extension 3.1.8 vaut « à l'exception du vol » : la condition manquait |
| B : tout bien volé en séjour était un « objet personnel » | les mêmes clubs | le lexique (1.30) retire les bijoux, les valeurs, les instruments de musique et le matériel de sport |
| Vocabulaire : un appareil photo n'avait pas de mot | « à préciser » pour un appareil tombé en randonnée | nommé dans l'aide de l'électronique |

**Laissés tels quels**, parce que je n'ai pas de règle générale sûre en deux heures : une coupure de courant
dont le contrat A dit à la fois « soudaine » et « six heures » ; un coup de vent suivi de pluie, que la garantie
dégâts des eaux couvre avant que la tempête ait posé sa question ; une maison où l'on ne séjourne plus que de
temps en temps (B) ; un bateau loué dont la puissance décide (A) ; un chat confié (A). Ce sont des erreurs qui
restent dans le produit livré.

**Sur les faits lus à 12 h 37, sans relire** : les passages couverts à tort tombent de 12 à 9 pour A et de 9 à 6
pour B ; D ne bouge pas (ses corrections attendent que la lecture produise le fait du seuil). Les 112 cas à faits
exacts des trois contrats ne changent pas de décision.

**Le quatrième jeu** (`data/quatre`) : 60 déclarations écrites par trois agents neufs, mêmes consignes que le
troisième. C'est lui qui dira si ce tour a servi.

### 7.188 Le défaut est de fond : on refond la décision, et on livre lundi

*25 novembre, 13 h 30.* Les commandes du second tour n'étaient pas lancées quand la question est venue :
« au vu des scores, peut-il y avoir un problème de logique de fond ? » Oui.

**Le défaut.** La chaîne couvre par défaut et ne refuse que pour les raisons qu'on lui a apprises. Dès qu'un
sinistre entre dans le périmètre d'une garantie, la réponse est « couvert », sauf si une exclusion traduite
s'applique *et* si la lecture a produit le fait qui la déclenche. Or un contrat d'assurance est fait surtout
d'exclusions, de seuils et de définitions. Une clause non traduite (les exclusions communes de B), un mot
absent du vocabulaire (la trottinette électrique), un fait non lu (l'ivresse sans l'âge) : tout ce qui manque
joue dans le même sens, vers un couvert à tort. Les quinze corrections des deux tours sont toutes de cette
famille, et il en reste autant que de situations auxquelles je n'ai pas pensé. Le moteur n'est pas en cause :
sur des faits exacts il applique les règles sans erreur. Ce qui n'était pas vérifié, c'est que les règles
disent tout le contrat ; je le vérifiais sur des cas que j'avais sous les yeux.

**L'indice.** Le second annotateur des jeux fermés, Mistral Large avec le texte entier du contrat et aucune
règle, s'accorde avec le premier sur 57 à 59 cas sur 60. J'ai simulé, sur les deux jeux mesurés, une réponse
qui serait la sienne, avec « couvert » seulement si la chaîne le dit aussi :

| Jeu | Contrat | Chaîne seule | Lecture directe, « couvert » si la chaîne aussi |
|---|---|---|---|
| aveugle | A | 95 % (0 couvert à tort) | 95 % (0) |
| aveugle | B | 58 % (1,3) | 75 % (0) |
| aveugle | D | 78 % (2) | 97 % (0) |
| neuf | A | 60 % (4) | 85 % (1) |
| neuf | B | 50 % (2) | 92 % (0) |
| neuf | D | 80 % (1) | 90 % (0) |

Ces chiffres sont flatteurs : la bonne réponse de ces jeux a été établie en partie avec l'avis du même modèle,
qui se juge donc un peu lui-même. C'est une simulation encourageante, pas une mesure.

**Ce qui a été discuté, et écarté.**
- *Faire refuser le moteur par défaut* tant que chaque exclusion n'est pas écartée : une question par
  exclusion, presque tout deviendrait « à préciser ».
- *Tout miser sur le modèle* : on perdrait ce que les règles donnent et que lui n'a pas (la même réponse à
  chaque fois sur des faits donnés, des questions précises, une preuve rejouable, une relecture humaine faite
  une fois).
- *La lecture du contrat entier à chaque analyse*, faisable en une après-midi : c'est la variante la plus
  chère (40 000 à 100 000 tokens par analyse, quelques centimes de plus, dix à trente secondes d'attente), et
  elle rend un avis global dont on ne sait pas quelles clauses il a regardées. Une étape possible, pas la cible.

**Ce qui est retenu.** Le modèle juge chaque clause, la logique additionne, les règles contresignent, le code
vérifie :
1. choisir les chapitres : les garanties qui peuvent jouer, largement, puis le code ajoute toutes leurs
   exclusions, les exclusions générales et le lexique ;
2. un jugement par clause (« s'applique », « ne s'applique pas », « la déclaration ne le dit pas »), avec la
   phrase de la déclaration qui le fonde ;
3. la décision par une logique fixe, en code ;
4. les contrôles : citations mot pour mot, aucune exclusion du dossier sans jugement ;
5. « couvert » seulement si la chaîne de règles le dit aussi ; chaque désaccord enregistré, comme la liste des
   règles et des mots qui manquent.

Rien de ce qui existe n'est jeté : le découpage, la base, le vocabulaire, les règles, le moteur, la validation
des citations, les bancs et les jeux servent tous. Ce qui change est le rôle des règles (elles contresignent,
elles ne décident plus seules) et la phrase du projet.

**Le calendrier.** Aucune date n'avait été imposée : celle du 26 était la mienne. Je ne livre pas une méthode
dont je viens de mesurer qu'elle répond juste une fois sur deux à quatre fois sur cinq, quand je sais comment
faire mieux. Livraison lundi 30 novembre, le week-end compris, en avançant le plus loin possible à chaque
séance. Le gel de 18 h est levé. La chaîne actuelle reste en place et en ligne : elle est livrable à tout
moment, avec ses chiffres. Le quatrième jeu (`data/quatre`), jamais ouvert, est gardé pour la mesure de la
nouvelle méthode : aucun banc n'est lancé dessus avant.

**Les frais.** Les appels au modèle ne se font plus qu'à des moments annoncés, avec leur coût estimé : un
essai de fumée de cinq à dix cas après chaque étape, un point d'étape d'un contrat et d'un passage, une mesure
finale. Le banc recevra une option d'échantillon et affichera les tokens envoyés, repris du cache et reçus.

Le plan détaillé, étape par étape avec son critère, est dans `perso/FEUILLE_DE_ROUTE.md`.

### 7.189 En tables d'abord : le principe d'un article, appliqué au contrat

*25 novembre, 14 h 30.*

**Le dossier de clauses, sans modèle.** Première pièce de la refonte : `analyse/dossier.py` compose ce que le
modèle devra juger. Le modèle désigne des chapitres dans la table des matières ; le code ajoute, sans rien
laisser à son choix, la garantie entière quand on n'en a désigné qu'un sous-article, les chapeaux au-dessus,
les exclusions générales, les articles auxquels ces clauses renvoient, et les définitions du lexique dont le
terme paraît. Sur les 120 cas déjà vus : les bons chapitres une fois désignés, le dossier contient tous les
articles cités dans 119 cas. Avec des chapitres désignés par un lecteur qui ne voit que la table des matières
(pas Mistral : un essai gratuit de la consigne), il est complet dans 114 cas ; les six manques tiennent à une
garantie cachée sous un titre (le « heurt » sous « Incendie »), d'où les premiers mots de chaque garantie
ajoutés à la table. Le dossier pèse 6 500 à 10 000 mots, un quart à un tiers du contrat : plus que ce que
j'annonçais (« quelques milliers de tokens »), parce que la désignation est large. Je préfère cela à une
exclusion oubliée.

**L'article.** « Parse the Folder, Not Just the PDFs » (Towards Data Science) traite un dossier de sinistre :
ses deux vraies questions, une pièce manque-t-elle, deux valeurs se contredisent-elles, ne sont pas des
recherches. L'absence d'un document ne rend qu'un résultat vide ; on ne la constate que si l'on a écrit
d'avance ce qui était attendu. D'où des tables : les pièces attendues par type de dossier, les pièces arrivées,
une jointure (présente, manquante, non rattachée), et pour réponse l'état du dossier, chaque entrée avec sa
source. Je n'en ai lu qu'un résumé fidèle, et c'est un billet, pas une étude mesurée : une idée voisine, pas
une preuve.

**Le lien.** C'est notre défaut du matin, vu de l'autre côté : la chaîne ne savait pas qu'une exclusion manquait
à son examen, parce que rien ne lui disait ce qu'elle aurait dû examiner.

**Ce qui est décidé.** La refonte se fait en tables d'abord, dans la base SQLite du projet : les *clauses
attendues* par garantie, écrites une fois par contrat (le rôle de chacune, et si elle bloque la couverture) ;
les *jugements*, une ligne par clause et par sinistre avec ses deux citations ; une *jointure*, où une clause
attendue sans jugement fait refuser la réponse et où un jugement sur une clause non attendue est signalé ; et
l'*état du sinistre* pour réponse. La décision devient une requête, plus un appel au modèle. C'est la même
étape 2 de la feuille de route, construite en tables plutôt qu'en mémoire.

**Ce qui n'est pas pour cette livraison.** Le système de l'article lui-même, la complétude et la cohérence d'un
dossier de sinistre (formulaire, devis, factures, rapports), est une évolution future : il prolonge le projet
(nos « à préciser » en sont l'amorce : la plainte, l'arrêté de catastrophe naturelle sont des pièces
attendues), mais il n'y a ni dossiers ni jeu de référence pour le mesurer aujourd'hui.

**Partie IX — La lecture des clauses (25 et 26 novembre).** Le modèle lit les clauses mêmes du contrat et juge chacune ; la logique tranche, les règles contresignent. Une mesure unique, sur un jeu jamais vu, la compare à la première méthode.

### 7.190 Deux essais sans frais, trois défauts trouvés, et une commande pour le premier essai payant

**Le fait.** Avant de payer un seul appel, le jugement clause par clause a été essayé deux fois sur des cas déjà
vus, avec un autre lecteur que Mistral et les chapitres désignés à l'étape 1. Premier essai, 12 cas : aucune
clause oubliée, aucune citation fausse, 9 réponses justes. Second essai, 24 cas, après corrections : 22 réponses
justes, aucun couvert à tort, aucun refus à tort ; les deux écarts sont des « à préciser » (une mesure de
sécurité lue comme une exclusion, et un « couvre » tiré du chapitre qui liste les biens assurés). Ce ne sont pas
des mesures : les cas sont vus, et le lecteur n'est pas celui de la démonstration.

**Les trois défauts, et leur règle.** Aucun n'a été réglé par un cas particulier.

- *Le chapeau d'un grand titre attendait tout le titre* : plus rien n'était jamais couvert, puisqu'une clause
  attendue manquait toujours. Le chapeau n'attend plus que ses clauses propres (`attendu.py`, un test).
- *Un « couvre » emprunté* : une clause citée dans une garantie par renvoi, en chapeau, en exclusion générale ou
  en définition faisait couvrir cette garantie. Un « couvre » ne compte que dans la garantie propre de la clause
  (`jugement.EMPRUNTS`, un test).
- *La portée d'un refus* : des bijoux que le contrat n'assure que par option étaient lus « exclus pour cette
  garantie », et une autre garantie couvrait. Quand une garantie couvre et qu'un refus vient d'une partie du
  contrat qui n'est pas sa voisine (même chapitre parent), la décision est « à préciser » avec le motif « sa
  portée est à examiner » (un test). La consigne dit aussi qu'une clause qui liste les biens assurés ne
  « couvre » pas, et qu'un bien assuré seulement par option est « à vérifier » pour tout le contrat.

**Ce qui reste prudent.** Les deux écarts vont dans le sens sûr (on demande au lieu d'affirmer). La consigne a
été retouchée pour eux et n'a pas été réessayée : ce sera vu à l'essai chez Mistral.

**La commande.** `couverture juger --contrat … "déclaration"`, ou `--jeu aveugle --cas av-d07` : la décision,
l'attendu en regard, les clauses qui couvrent, excluent ou restent à vérifier avec leur extrait, les clauses
attendues sans jugement et les jugements écartés. Deux appels à Mistral Large par cas, sur un dossier de 7 500 à
16 000 mots : c'est une commande payante, lancée seulement aux moments annoncés. La chaîne de règles n'y est
appelée qu'avec `--regles`. Suite : 273 tests passés.

### 7.191 Le premier appel payant : une réponse coupée à 8 000 tokens

**Le fait.** Premier essai chez Mistral Large (25 nov., 16 h 07), contrat D, premier cas : la désignation passe,
le jugement échoue, « réponse coupée à 8 000 tokens ». La consigne demandait un élément par clause à juger, et
une garantie de D en attend une centaine : cent lignes, chacune avec son motif, ne tiennent pas dans la limite.
L'autre lecteur, aux essais gratuits, n'avait pas cette limite : l'essai gratuit ne pouvait pas le voir.

**La correction.** La réponse détaille seulement ce qui couvre, exclut ou reste à vérifier ; tout le reste tient
dans une liste d'identifiants, `"sans_effet": ["2.7-b", "2.8"]`. La jointure ne change pas : chaque clause
attendue doit toujours figurer, dans l'une ou dans l'autre. La réponse est plus courte, donc moins chère et plus
rapide. La limite passe à 16 000 tokens pour cette commande, et un cas qui échoue n'arrête plus les suivants.
Un test de plus ; suite : 274 passés.

### 7.192 Le premier cas lu par Mistral : une indemnité réduite n'est pas un refus

**Le fait.** La réponse courte passe (25 nov., 16 h 21, av-d07, l'eau non coupée pendant trois semaines) :
75 clauses au dossier, la venue d'eau jugée « couvre » avec ses deux citations. Mais la réponse est « à
préciser » pour un « couvert » attendu : le jugement sur la clause 4.2 (fermer l'eau au-delà de quinze jours)
est écarté, sa citation de la déclaration n'y étant pas mot pour mot, et la clause reste sans jugement. Le
contrôle a fait son travail : sans lui, on ne sait pas ce que ce jugement aurait fait de la réponse. Durée :
148 secondes, Mistral Large réfléchissant avant de répondre ; c'est trop pour un écran, à mesurer avec les
tokens.

**Ce que le texte dit.** La clause 4.2 ne refuse rien : « l'indemnité sera réduite de 50 % ». Les quatre effets
ne savaient pas le dire : entre « exclut » et « sans effet », aucun n'était juste. Un cinquième effet,
`limite` : la clause réduit ce qui sera payé (indemnité réduite, franchise, plafond) sans refuser le sinistre.
Elle ne pèse pas sur la décision et s'affiche avec elle. La consigne demande de lire la sanction écrite ; une
obligation sans sanction écrite, ou dont la sanction est la perte de la garantie, reste « exclut ».

**Deux réglages du contrôle.** Une citation de la déclaration abrégée par « … » ou « [...] » est admise si
chacun de ses morceaux (trois mots au moins) y figure : le modèle abrège, il n'invente pas ; une phrase
réécrite reste écartée. Et un jugement écarté affiche maintenant l'effet et la phrase citée, pour qu'on voie ce
qui a été refusé. La commande affiche aussi les tokens envoyés et reçus. Suite : 276 tests passés.

### 7.193 Le second passage : la limite est lue, un identifiant est mal recopié, et c'est lent

**Le fait.** Même cas (25 nov., 16 h 42). La clause 4.2 est jugée « limite », avec la phrase du contrat et celle
de la déclaration : l'effet ajouté dit ce que le texte dit. La réponse reste « à préciser » pour une autre
raison : le modèle a écrit « 25 » pour la clause « S25 » (les exclusions générales, un titre sans numéro que
le découpage a nommé ainsi). Le jugement est écarté comme « hors du dossier », la clause reste sans jugement,
pas de réponse franche. Une vérification sans frais avait précédé cet appel (120 cas avec un modèle factice,
aucun plantage, aucune clause attendue cachée au modèle) : elle ne pouvait pas voir une faute de recopie.

**La règle.** Un identifiant rendu qui n'est pas au dossier est rétabli quand une seule clause du dossier lui
correspond au signe de tête près (« S », « § », crochets) ; à deux candidates, on ne devine pas et le jugement
reste écarté. Un test.

**Le temps et le prix.** 17 941 tokens envoyés, 7 695 reçus, 210 secondes : le modèle réfléchit longuement avant
d'écrire une réponse courte. C'est trop lent pour un écran et la réflexion coûte plus que la lecture. À essayer
au prochain moment payant : le même cas avec le modèle moyen (`--modele`), et comparer justesse, durée et
tokens. La commande affiche maintenant la longueur de la réflexion. Suite : 277 tests passés.

### 7.194 Le modèle moyen : dix fois plus rapide, moins soigneux, et ce que le code rattrape

**Le fait.** Même cas avec `mistral-medium-2604` (25 nov., 17 h 15) : 22 secondes au lieu de 210, aucune
réflexion, 18 022 tokens envoyés et 4 192 reçus. Un premier essai avait rendu un JSON illisible, et la réponse
n'avait pas été gardée ; la commande écrit maintenant les réponses brutes dans `data/debug/`, et c'est ce
fichier qui a été lu ici. La réponse reste « à préciser », pour quatre raisons que le fichier montre :

- la citation du contrat pour la fuite d'eau saute des mots sans le dire (« des conduites non enterrées, des
  appareils à effet d'eau », la clause intercale « des piscines, de tous ») : jugement écarté ;
- la clause qui renvoie aux mesures de sécurité est jugée « limite » avec la phrase de l'article 4.2, qui n'est
  pas la sienne : jugement écarté ;
- le chapeau du titre n'est jugé nulle part : oubli ;
- la garantie des dommages électriques, réservée à deux formules, est jugée « à vérifier pour tout le contrat »
  pour une fuite d'eau.

S'y ajoute un « couvre » donné à la clause qui liste les biens assurés, que la consigne interdit. Et chaque
clause sans effet est écrite deux fois, en détail puis en liste.

**Ce que le code rattrape désormais.**

- *Une citation qui saute des mots* devient le passage exact de la clause, quand tous ses mots y sont, dans
  l'ordre et à peu d'écart (`validation.passage_exact`, déjà employé par la chaîne de règles). Ce qui s'affiche
  est toujours le texte du contrat.
- *Une limite mal citée* ne coûte plus la réponse : une limite ne pèse pas sur la décision, la clause compte
  pour lue et la limite n'est pas affichée. Un refus ou une couverture mal cités restent écartés.
- *Ce qui manque est redemandé une fois* : la jointure dit quelles clauses n'ont pas de jugement, un second
  appel les soumet seules (avec les définitions et la déclaration). C'est la logique des tables : on ne
  redemande pas tout, on redemande le trou. Si le trou reste, pas de réponse franche, comme avant.
- *La consigne* : la formule qu'exige une garantie n'est à vérifier que si cette garantie est celle de
  l'événement déclaré ; le schéma n'admet plus « sans effet » dans la liste détaillée.

Rejouée sans frais sur ces règles, la réponse du modèle moyen n'a plus qu'un oubli à redemander et retrouve la
citation exacte de la fuite d'eau ; il lui reste la question hors sujet sur la formule, que seule la consigne
peut corriger : à voir au prochain appel.

**Ce que je n'ai pas fait, et pourquoi.** J'avais écrit une règle qui ramenait à sa garantie la portée « tout »
d'une clause voisine de celle qui couvre. Elle aurait fait passer ce cas, et elle contredisait un test existant
(un bien que le contrat n'assure pas, dit dans une garantie voisine) : elle pouvait donner un couvert à tort.
Retirée. Entre un « à préciser » de trop et un couvert à tort, la règle choisit le premier.

**Ce qui reste ouvert.** Le « couvre » sur la clause des biens assurés : aucune règle de structure ne le
distingue aujourd'hui (le type que le découpage donne aux clauses est trop peu sûr), et c'est la
contresignature des règles qui l'arrête. Et le choix du modèle : Large juge mieux et met trois minutes et
demie ; le moyen répond en vingt secondes et demande plus de rattrapage. Il se décidera sur plusieurs cas, pas
sur un seul.

**Les jugements en table.** `jugement.garder` écrit chaque analyse (`analyses_clauses`) et ses jugements
(`jugements`, une ligne par clause avec ses deux citations) ; la commande `juger` le fait à chaque passage.

**La commande devient l'outil de mesure de la nouvelle méthode.** `juger --jeu …` compte en fin de passage les
réponses justes et sépare les deux erreurs qui ne se valent pas (couvert à tort, refus à tort) des « à
préciser » donnés à la place d'une réponse ; elle additionne les tokens de tous les appels et le temps, et garde
ce bilan en fichier. `--echantillon N` limite le passage aux N premiers cas : un essai se paie à sa taille. Et
`--jeu quatre` s'arrête avant tout appel, et avant même d'ouvrir les fichiers, sans `--mesure-finale` : le jeu
jamais regardé ne se lance pas par mégarde. Suite : 282 tests passés.

### 7.195 Le tarif vérifié : le modèle moyen n'est pas le moins cher

**Le fait.** Depuis le début des essais, les coûts étaient estimés sur un tarif supposé (2 € par million de
tokens envoyés) et sur l'idée que le modèle moyen coûtait moins que le grand. La page des tarifs de Mistral
(docs.mistral.ai, lue le 25 nov. 2026) dit autre chose, par million de tokens : Mistral Large 4, 1,36 $ envoyés
(0,14 $ repris du cache) et 4,18 $ reçus ; Mistral Medium 3.5, 1,50 $ envoyés et 7,50 $ reçus ; Mistral Small 4,
0,15 $ et 0,60 $.

**Ce que cela donne sur le cas essayé.** Avec Large : environ 24 000 tokens envoyés sur les deux appels et
7 700 reçus, soit 6 à 7 centimes de dollar. Avec le moyen : autant d'envoyés, 4 200 reçus, soit 6 à 7 centimes
aussi. Le moyen est dix fois plus rapide, pas moins cher : ce qu'il écrit coûte presque le double, et il en
écrit trop. Le choix entre les deux se fera sur la justesse et sur le temps, pas sur le prix. Le cache, lui,
divise par dix le prix des tokens envoyés : mettre en tête de l'appel ce qui ne change pas reste à faire.

### 7.196 Le cache : ce qu'il peut rendre, mesuré avant de l'annoncer

**Le fait.** Mistral reprend à 10 % du prix le début d'un envoi qu'il a déjà vu (documentation « prompt
caching », lue le 25 nov. 2026 : le cache est automatique, il porte sur le préfixe, et la réponse dit combien
de tokens en viennent, `usage.prompt_tokens_details.cached_tokens`). Encore faut-il que deux sinistres du même
contrat commencent pareil.

**Ce qui est fait.** La désignation commençait déjà par la table des matières, la déclaration à la fin. Le
jugement est réordonné : d'abord les exclusions générales, qui reviennent à chaque sinistre d'un contrat, puis
les garanties désignées, puis les définitions appelées par les mots de la déclaration, puis la déclaration.
L'ordre du contrat est gardé à l'intérieur de chaque groupe. La commande affiche les tokens repris du cache.

**Ce que cela peut rendre, mesuré sans frais** sur les 120 cas déjà vus (début commun entre deux envois
successifs du même contrat) : 98 à 99 % de la désignation ; 13 à 27 % du jugement, puisque les garanties
désignées changent d'un sinistre à l'autre. Sur l'ensemble des tokens envoyés, 30 à 43 % selon le contrat, soit
12 à 18 % de la facture d'un cas si le cache répond à chaque fois, ce que Mistral ne garantit pas. C'est une
économie réelle et modeste : l'essentiel du prix est dans ce que le modèle écrit, pas dans ce qu'il lit.
Suite : 283 tests passés.

### 7.197 Le modèle moyen après rattrapages : 14 secondes, et une exclusion qui n'écarte qu'un poste

**Le fait.** Même cas, modèle moyen (25 nov., 18 h 55) : 14 secondes, trois appels, 31 746 tokens envoyés et
1 115 reçus, soit environ 6 centimes de dollar. La réponse courte est respectée (1 115 tokens au lieu de
4 192), la citation à trous de la fuite d'eau est écartée puis rattrapée par la relance, la clause oubliée
aussi, la limite de l'article 4.2 est lue, la question hors sujet sur la formule a disparu. Le cache n'a repris
que 996 tokens : c'était le premier envoi dans le nouvel ordre.

**Ce qui empêche encore « couvert ».** La clause des exclusions de la garantie est jugée « exclut » sur cette
phrase : « les frais de réparation ou de remplacement de l'élément à l'origine du dommage couvert par le
contrat ». La lecture est exacte et l'effet est faux : la clause écarte un poste (le raccord), pas le sinistre
(la cuisine inondée, le parquet), et elle le dit elle-même en parlant du « dommage couvert ». C'est la même
famille que l'indemnité réduite : ce qui sera payé diminue, la garantie joue.

**La règle.** L'effet « limite » couvre désormais trois cas, écrits dans la consigne : la sanction d'une
obligation quand elle est une indemnité réduite, un plafond que le montant déclaré dépasse, et une exclusion
qui n'écarte qu'un poste du dommage quand le reste demeure garanti. Reste « exclut » ce qui écarte tout ce que
la déclaration réclame. Aucune règle de code ne peut le vérifier : c'est une lecture, confiée au modèle, et
c'est à l'essai suivant de dire s'il la fait.

**Toujours ouvert.** Le modèle moyen donne encore « couvre » à la clause qui liste les biens assurés. Sur ce
cas cela ne change rien ; sur un autre, cela pourrait couvrir à tort, et seule la contresignature des règles
l'arrête aujourd'hui.

### 7.198 L'essai de fumée complet : cinq sur cinq pour A et D, zéro sur trois pour B

**Le fait.** Après un dernier réglage de consigne, le cas av-d07 rend « couvert » en 13 secondes, avec ses deux
limites et 9 004 tokens repris du cache. Puis les sept autres cas (25 nov., 19 h 02), modèle moyen, avec la
contresignature des règles. Ce sont des cas déjà vus : un essai de fumée, pas une mesure.

| Contrat | Cas | Justes | Ce qui s'est passé |
|---|---|---|---|
| A | n-a07, av-a05 | 2 sur 2 | 14 et 18 s |
| D | av-d07, av-d01, av-d10 | 3 sur 3 | 12 à 16 s ; jusqu'à 25 544 tokens sur 26 050 repris du cache |
| B | av-b05, av-b14, n-b06 | 0 sur 3 | deux refus à tort, un « à préciser » |

Aucun couvert à tort. Huit cas pour environ 250 000 tokens envoyés et 13 000 reçus, de l'ordre de 45 centimes de
dollar, 13 à 29 secondes par cas.

**Les trois échecs de B, lus dans les réponses brutes.**

- *av-b05, le trampoline emporté par la tempête* : la clause exclut les objets non fixés « à l'exception du
  mobilier de jardin », et le lexique range le trampoline dans le mobilier de jardin. La définition était dans
  l'envoi ; le modèle écrit lui-même « mobilier de jardin » dans son motif, et exclut quand même.
- *n-b06, le vol avec les clés perdues* : le contrat exclut les vols simples, et le lexique dit qu'un vol commis
  avec des clés perdues n'en est pas un. La définition était dans l'envoi ; le modèle exclut. Il juge aussi
  « exclut » la phrase qui accorde la garantie vol, et cite pour les exclusions générales un alinéa sur les
  changements de température : les deux citations sont exactes, leur rapport est nul, et aucun contrôle de code
  ne voit cela.
- *av-b14, le facteur qui glisse sur le verglas* : la garantie couvre, mais le modèle demande si elle est
  souscrite et si le sinistre a été déclaré dans les huit jours, deux questions que la consigne écarte en toutes
  lettres.

Dans deux de ces cas, la chaîne de règles répondait « couvert », à raison, et la lecture des clauses l'a
emporté, à tort : la contresignature est écrite pour arrêter un couvert, pas un refus.

**Ce que le code rattrape de plus.** Le modèle juge des alinéas numérotés dans le texte d'une clause
(« 3.1.6.2.1 les vols simples ») au lieu de la clause : ces jugements étaient écartés comme « hors du
dossier ». Ils reviennent à la clause qui les contient, le plus lourd d'abord, et la citation se vérifie dans
cette clause. La consigne dit maintenant que la définition du contrat l'emporte sur le sens courant, et qu'on
juge sous l'identifiant entre crochets. Rejouées sur ce code, les trois réponses de B restent fausses : ce ne
sont pas des défauts de contrôle, ce sont des lectures fausses.

**Ce que cela dit.** La méthode tient sur A et D. Sur B, dont les dossiers sont plus gros (jusqu'à 123 clauses)
et qui renvoie davantage à son lexique, le modèle moyen n'applique pas les définitions qu'on lui donne. Deux
questions restent, dans cet ordre : est-ce le modèle (les mêmes trois cas avec Large le diront, pour une
vingtaine de centimes) ; et que faire d'un désaccord où les règles couvrent et la lecture refuse (le rendre « à
préciser » au lieu de laisser la lecture l'emporter). Ni l'une ni l'autre ne se décide sur trois cas vus.
Suite : 284 tests passés.

### 7.199 Les trois cas de B avec Mistral Large : c'était le modèle

**Le fait.** Les trois cas de B manqués par le modèle moyen, rejoués avec Mistral Large et la contresignature
des règles (25 nov., 19 h 16) :

| Cas | Modèle moyen | Mistral Large | Ce que Large a lu |
|---|---|---|---|
| av-b05, le trampoline | refus à tort | « à préciser » | la tempête couvre ; les règles disent « non couvert » |
| av-b14, le verglas | « à préciser » | **couvert, juste** | la responsabilité pour défaut d'enlèvement du verglas |
| n-b06, les clés perdues | refus à tort | **couvert, juste** | la garantie vol, plainte déposée |

La lecture seule de Large donne les trois réponses attendues ; sur le trampoline, la chaîne de règles répond
« non couvert » (son erreur connue, 7.186), et la contresignature fait ce pour quoi elle est écrite : un couvert
que les règles ne signent pas devient « à préciser ». Aucun couvert à tort, aucun refus à tort.

**Le prix et le temps.** 81 000 tokens envoyés et 32 000 reçus pour trois cas, soit environ 25 centimes de
dollar, 8 centimes par cas ; 100 à 163 secondes par cas. Large réfléchit avant de répondre (18 000 à
30 000 caractères de réflexion par jugement), au niveau le plus bas qu'il accepte (« low » ; « none » est
refusé, 7.112). C'est la réflexion qui coûte et qui dure, et c'est sans doute elle qui applique les définitions
du lexique que le modèle moyen lisait sans s'en servir.

**Ce que cela décide, et ce que cela ne décide pas.** Les échecs de B venaient du modèle, pas de la méthode :
les mêmes dossiers, la même consigne, le même code donnent juste avec un lecteur qui réfléchit. Reste un choix
qui n'est pas technique : un lecteur rapide (15 s, juste sur A et D, faux sur B) ou un lecteur lent (2 min, juste
sur les trois contrats essayés). Choisir un modèle par contrat serait régler sur les cas vus ; il en faut un
pour tous. Le choix se fera sur un échantillon plus large des jeux déjà vus, puis la mesure sur le jeu
« quatre », une seule fois, avec le modèle choisi.

### 7.200 Trente cas avec Mistral Large : aucune erreur grave, et 84 minutes

**Le fait.** Les dix premiers cas du jeu « aveugle » pour chaque contrat, Mistral Large, contresignature des
règles (25 nov., de 19 h 20 à 20 h 40). Ce sont des cas déjà vus : un essai, pas une mesure.

| Contrat | Justes | Couverts à tort | Refus à tort | « À préciser » au lieu d'une réponse |
|---|---|---|---|---|
| A | 9 sur 10 | 0 | 0 | 1 (av-a06) |
| B | 7 sur 10 | 0 | 0 | 3 (av-b05, av-b06, av-b10) |
| D | 7 sur 10 | 0 | 0 | 3 (av-d04, av-d06, av-d07) |

23 justes sur 30, et les sept écarts vont tous dans le sens prudent. Pour mémoire, la chaîne actuelle avait sur ce
jeu entier 1 à 2 couverts à tort pour B et 2 pour D (7.186) ; les chiffres ne se comparent pas autrement, les
échantillons n'étant pas les mêmes.

**Les sept écarts.**

- *Des questions sur les formalités* (av-a06, av-d07) : le délai de déclaration du sinistre, le plafond. Ce sont
  des conditions de règlement, pas de couverture ; la consigne le dit, Large les pose quand même. Dans les deux
  cas, les règles disaient « couvert ».
- *Une question sur le calcul de l'indemnité* (av-b06) : l'âge de la plaque de cuisson, qui joue sur la vétusté,
  pas sur la garantie.
- *Une clause citée de travers* (av-b10) : une exclusion jugée « exclut » avec, pour citation, la phrase qui
  accorde la garantie. La citation existe ; son rapport est nul (même défaut qu'en 7.198).
- *La contresignature* (av-d04) : la lecture couvre, les règles disent « à préciser », la réponse est « à
  préciser ». C'est la règle voulue ; c'est ici la chaîne de règles qui se trompe.
- *Une prudence défendable* (av-d06) : des moisissures que le contrat exclut ; Large demande si l'assuré
  connaissait le défaut d'aération. On attendait « non couvert ».
- *Une réponse coupée* (av-b05) : la réflexion de Large compte dans la limite de 16 000 tokens. Portée à 32 000.

**Le temps.** 84 minutes pour 30 cas, deux minutes et demie à trois minutes par cas, les cas l'un après l'autre.
Environ 900 000 tokens envoyés et 400 000 reçus, de l'ordre de 2,50 à 3 $ ; c'est la réflexion de Large qui fait
l'essentiel du prix et du temps. La commande lance maintenant 4 cas à la fois (`--paralleles`, comme le banc,
chaque cas avec son propre client pour que les comptes de tokens ne se mélangent pas) : un passage de 30 cas
devrait prendre une vingtaine de minutes. Cela ne change rien au temps d'une analyse : à l'écran, une
déclaration attendrait toujours deux à trois minutes. C'est la question qui reste avant le branchement.

### 7.201 Le branchement : la lecture des clauses dans l'API et à l'écran, derrière un réglage

**Le choix.** Avec Mistral Large, une analyse par la lecture des clauses prend deux à trois minutes (7.200). On ne
le cache pas : on le dit avant l'attente et on montre chaque étape pendant. Ni cascade de modèles ni double
bouton : la cascade demanderait une mesure de plus, et un bouton « rapide » montrerait par défaut la méthode qui
couvre à tort (choix du 25 nov., 20 h 48).

**Ce qui est branché.**

- *Le réglage* : `COUVERTURE_METHODE` (`regles` par défaut, `clauses`) et `COUVERTURE_MODELE_CLAUSES`
  (`mistral-large-latest`). Une requête peut choisir sa méthode (`methode` dans `POST /analyses` et
  `/analyses/suivi`). Par défaut, rien ne change : la décision entre les deux méthodes se prend après la mesure
  sur le jeu « quatre ».
- *La contresignature en même temps* : la chaîne de règles tourne dans un fil pendant que le modèle lit les
  clauses ; elle ne rallonge pas l'attente. Si elle ne répond pas, un « couvert » n'est pas contresigné et devient
  « à préciser » : la garde contre un couvert à tort ne se saute pas en silence.
- *Le suivi* : la première ligne du flux annonce les étapes de cette méthode et le temps à prévoir ; puis
  « trouver les chapitres », « juger chaque clause » (avec le compte : tant couvrent, tant excluent), « faire
  contresigner », « décider ».
- *La réponse* : le même format que la chaîne de règles, pour l'écran, la fiche PDF et le journal. Les citations
  sont les phrases du contrat jugées ; le raisonnement donne, pour chaque clause qui pèse, la phrase du contrat et
  celle de la déclaration ; les questions sont en phrases (pas de boutons : il n'y a pas de variable à renvoyer au
  moteur, on complète la déclaration et on relance). Il n'y a pas de « confiance » chiffrée : l'écran dit si les
  règles concordent.
- *Les conditions particulières* choisies à l'écran (la formule, les options) sont ajoutées à la déclaration, en
  mots, pour que le modèle les lise.

**Ce qui reste à vérifier.** Une requête de trois à cinq minutes sur le site en ligne : la limite de durée d'une
requête chez l'hébergeur est à vérifier avant d'y activer la méthode (étape 7). Suite : 287 tests passés.

### 7.202 Le suivi dans l'ordre

**Le fait.** Premier essai à l'écran (25 nov., 21 h) : « faire contresigner » se cochait avant « trouver les
chapitres ». La chaîne de règles tourne pendant la lecture et finissait la première ; l'écran racontait donc
l'analyse dans le désordre.

**La correction.** La chaîne tourne toujours en même temps, sans rallonger l'attente, mais en silence : son
étape ne s'ouvre et ne se ferme qu'au moment de contresigner, après le jugement des clauses et avant la décision.
L'écran suit l'ordre annoncé : chapitres, jugement, contresignature, décision. Un test vérifie cet ordre.

### 7.203 Les questions du règlement du sinistre ne retiennent plus la réponse

**Le fait.** Premier résultat à l'écran (25 nov., 21 h 03) : le piéton renversé à vélo, contrat A. La garantie de
responsabilité civile couvre, citée ; la réponse est pourtant « à préciser », pour une seule question : « avez-vous
déclaré ce sinistre dans les huit jours ? ». C'est le défaut le plus fréquent des trente cas de 7.200 : trois des
sept écarts (le délai de déclaration, un plafond, l'âge d'un appareil pour la vétusté). La consigne écarte ces
questions ; Mistral Large les pose quand même.

**Ce que dit le texte.** Ces clauses sont rangées, dans les quatre contrats, sous des titres qui disent ce
qu'elles sont : « Sinistres », « En cas de sinistre », « Obligations et formalités à respecter en cas de
sinistre », « Estimation des biens », « Fixation de l'indemnité », « Limites d'indemnisation », « Franchise ».
Elles disent ce qui sera payé et comment, une fois la couverture acquise ; pas si le sinistre est couvert.

**La règle.** Une clause rangée sous un tel titre (hors lexique) est une clause du règlement du sinistre
(`dossier.est_reglement`). Une question qu'elle pose devient un rappel : la clause compte pour lue, la question
s'affiche avec la réponse (« sous réserve · ce que l'assureur pourra vérifier »), et ne fait plus de la réponse un
« à préciser ». Un refus venu d'une telle clause, lui, compte toujours. Les titres ont été relus dans les quatre
contrats : une garantie d'assistance « en cas de sinistre affectant le domicile » et des « frais d'expertise »
assurés n'y sont pas pris, et un test le vérifie.

**Rejouées sans frais.** Les réponses de Mistral Large aux trente cas de 7.200, gardées, ont été rejouées sur ce
code : 26 justes sur 30 au lieu de 23, toujours aucun couvert à tort ni refus à tort. Le rejeu est exact (les
réponses du modèle sont les mêmes, seul le code qui les lit a changé) ; ce sont des cas vus, ce n'est pas une
mesure. Restent : une réponse coupée, une citation sans rapport, un couvert que les règles ne contresignent pas,
une prudence sur des moisissures. Suite : 289 tests passés.

### 7.204 Un réglage du poste qui fuyait dans les tests, et des appels payés pour rien

**Le fait.** Le 25 nov. vers 21 h 15, la suite de tests a échoué sur trois tests de l'API, puis s'est bloquée
(arrêtée à la main). Cause : `COUVERTURE_METHODE=clauses`, ajouté au `.env` pour essayer l'écran, est lu par la
configuration de l'API, et les tests ne fixaient pas la méthode. Leurs analyses sont donc parties vers la lecture
des clauses, avec le vrai Mistral Large : quelques appels payés pour rien, et des tests qui attendaient des
minutes. Les tests tournaient chez moi sans ce `.env` : je ne pouvais pas le voir.

**Deux corrections.** Les tests de l'API fixent leur méthode (`regles`). Et une garde commune à tous les tests :
aucun test ne peut ouvrir une connexion vers un fournisseur ; s'il essaie, il échoue tout de suite avec un message
qui le dit. Les tests qui simulent le fournisseur le font eux-mêmes, après la garde. Suite : 289 tests passés.

### 7.205 Le jeu « neuf » entier avec Mistral Large : le critère de l'étape 4 est atteint

**Le fait.** Les 60 cas du jeu « neuf », déjà vus, avec Mistral Large et la contresignature des règles (25 nov.,
de 21 h 35 à 22 h 20 ; environ 1,9 million de tokens envoyés et 870 000 reçus, de l'ordre de 6 $ ; 85 à 360 s par
cas, quatre à la fois). En regard, la chaîne de règles seule sur le même jeu (7.186).

| Contrat | Chaîne de règles : justes | couverts à tort | Lecture des clauses : justes | couverts à tort | refus à tort |
|---|---|---|---|---|---|
| A | 12 sur 20 | 4 | 14 sur 20 | 1 | 0 |
| B | 10 sur 20 | 2 | 17 sur 20 | 0 | 1 |
| D | 16 sur 20 | 1 | 17 sur 20 | 0 | 0 |
| Ensemble | 38 sur 60 | 7 | 48 sur 60 | 1 | 1 |

Le critère de l'étape 4 (plus de réponses justes, pas plus de couverts à tort) est atteint. Ce sont des cas vus :
la mesure reste à faire sur le jeu « quatre ».

**Les douze écarts, lus dans les réponses brutes.**

- *Quatre « à préciser » par la contresignature* (n-a08, n-a15, n-b13, n-d16) : la lecture couvre, à raison ; les
  règles hésitent ou refusent. C'est le prix voulu de la garde.
- *Deux couverts à tort évités par la contresignature* (n-a16 : l'assuré avait trop bu ; n-a17 : la pension de
  furets, que l'assistance limite aux chiens et chats) : la lecture couvrait, les règles non. Sans la garde, ce
  seraient deux couverts à tort de plus.
- *Un couvert à tort* (n-a04, une fenêtre de toit arrachée par le vent, la pluie entrée) : la lecture et les règles
  couvrent toutes deux ; le cas attendait « à préciser ». Rien ne l'arrête aujourd'hui.
- *Un refus à tort* (n-b06, le vol avec les clés perdues) : Large aussi applique « vols simples » sans la définition
  du lexique, comme le modèle moyen en 7.198.
- *Une citation trop abrégée* (n-a20) : le modèle saute une ligne entière d'une liste en citant ; le contrôle la
  refuse, la clause reste sans jugement. Le contrôle a raison ; on ne l'assouplit pas.
- *Une portée* (n-b09) : une clause qui énumère les biens assurés par une garantie est jugée « exclut » pour un bien
  qu'elle ne nomme pas. Une phrase de consigne de plus, à vérifier à la mesure.
- *Le délai de déclaration de D* (n-d07, n-d11) : rangé sous un titre coupé par le découpage, « DÉCLARATION ? » ;
  les titres du règlement du sinistre comprennent maintenant « déclaration » seule et « déclaration du sinistre ».

**Une règle de contresignature de plus.** Ce dernier changement a fait passer n-d07 de « à préciser » à « non
couvert » : la désignation avait manqué la garantie vol, et rien ne couvrait. « Aucune garantie examinée ne
couvre » ne cite aucune clause : c'est une absence, pas un refus. Elle ne l'emporte plus sur des règles qui
couvrent ; la réponse est « à préciser ». Un refus qui cite son exclusion tient toujours seul. Un test.

**Rejoué sans frais** sur ce code (les réponses du modèle sont les mêmes) : jeu « neuf » 49 sur 60, un couvert à
tort, un refus à tort ; les trente cas de 7.200, 26 sur 30, aucun. Suite : 290 tests passés.

### 7.206 Le jeu « quatre » : un troisième avis, et les trois annotateurs d'accord sur les 60 cas

**Pourquoi un troisième avis.** Le second avis du jeu « quatre » venait de Mistral Large, et la nouvelle méthode
lit avec Mistral Large : un jeu annoté par le même modèle que celui qu'on mesure le favoriserait, s'ils se
trompaient de la même façon. L'utilisateur a choisi que l'avis indépendant soit le mien (Claude, Opus 5.5).

**Comment.** Après le gel du code, pour que rien de ce que je lisais ne puisse régler le système. Un script ne
m'a montré que l'identifiant, le contrat et la déclaration de chaque cas, sans la réponse du premier annotateur ni
celle de Mistral. J'ai lu dans chaque contrat les chapitres en jeu et le lexique, et rendu pour chaque cas la
réponse, les articles, une citation (vérifiée mot pour mot dans le texte par le code) et la question à poser
quand la réponse dépend d'une option ou d'un fait non dit. Convention du jeu : garanties de base souscrites,
options et formules inconnues. Fichier : `data/quatre/avis_claude.jsonl`.

**Le résultat.** Les trois avis (l'agent qui a écrit les cas, Mistral Large, moi) donnent la même réponse sur les
60 cas. Aucun arbitrage n'est nécessaire : le jeu se compose des 60 cas, tels qu'annotés.

**La limite, dite telle quelle.** Le premier annotateur et moi sommes deux modèles Claude ; Mistral Large est le
troisième. Aucun n'est un gestionnaire de sinistres. L'accord de trois lectures ne prouve pas qu'elles sont justes,
il dit que les cas ne sont pas ambigus pour qui lit le contrat. Et j'ai construit le système que ce jeu mesure : je
l'ai annoté sans voir aucune de ses réponses sur ces cas, mais je connais ses règles.

### 7.207 La mesure unique sur le jeu « quatre » : autant de réponses justes, quatre fois moins de couverts à tort

**Le déroulé.** Le code est figé et poussé (commit `4410d43`), puis le jeu est fermé et exporté : 60 cas, 20 par
contrat. Un faux pas avant : le fichier du second avis avait été renommé, et `ferme` ne trouvait plus rien (0 cas) ;
il a repris son nom, sans toucher au code. Le soir du 25 novembre : la chaîne de règles seule passe trois fois sur
chaque contrat (`banc`, Mistral Medium et Small, de 22 h 44 à 22 h 50) ; puis la lecture des clauses une fois
(`juger --mesure-finale --regles`, Mistral Large, contresignature des règles, de 22 h 50 à 23 h 28, environ 2 millions
de tokens envoyés dont la moitié repris du cache, 830 000 reçus, de l'ordre de 5 $).

**Un incident.** Sur A, Mistral a répondu par une erreur 520 (son serveur) au cas q-a20. `juger` rattrapait une
réponse coupée, pas une panne du fournisseur : tout le passage de A s'est arrêté, sans bilan, q-a19 fini sans être
affiché, q-a20 jamais traité. Ces deux cas ont été passés le lendemain matin, avec le même code, et personne n'avait vu
de réponse pour eux auparavant. Le défaut est corrigé après la mesure : une panne du fournisseur compte comme une
erreur du cas, et le passage continue ; une clé refusée arrête toujours tout.

**Les chiffres, tels quels.**

| Jeu « quatre » | Chaîne de règles (moyenne de 3 passages) | Lecture des clauses (1 passage) |
|---|---|---|
| A | 12,3 sur 20 | 16 sur 20 |
| B | 16,7 sur 20 | 16 sur 20 |
| D | 13 sur 20 | 13 sur 20 |
| **Ensemble** | **42 sur 60** | **45 sur 60** |
| Couverts à tort | 4,3 (A 0,7 ; B 1,3 ; D 2,3) | **1** (q-b15) |
| Refus à tort | 2 | 4 (q-a04, q-b17, q-d03, q-d13) |
| « À préciser » au lieu d'une réponse | 8,7 | 10 |
| Durée d'une analyse | 3,6 s (médiane) | 100 à 260 s |

Trois réponses justes de plus sur soixante : ce jeu ne permet pas de l'affirmer. L'écart du jeu « neuf » (48 contre
38, 7.205) tenait en partie au réglage. Ce qui tient, c'est le sens des erreurs : un couvert à tort au lieu de plus de
quatre, au prix de deux refus à tort de plus et d'une attente de deux à trois minutes.

**Les quinze écarts de la lecture des clauses, lus dans la sortie.** Rien n'en est corrigé : ce jeu a servi, il ne
sert plus à mesurer.

- *La contresignature hérite des erreurs des règles* (six cas : q-a02, q-a17, q-b04, q-d01, q-d04, q-d19). La lecture
  couvre, à raison ; les règles refusent ou hésitent ; la réponse devient « à préciser ». C'est le prix voulu de la garde,
  et le plus gros poste.
- *Une absence l'emporte sur des règles qui hésitent* (q-b17, q-d13 : deux refus à tort). « Aucune garantie examinée
  ne couvre » ne cite rien ; la règle de 7.205 ne la retient que contre des règles qui couvrent, pas contre des règles
  qui disent « à préciser ».
- *Un refus qui cite une clause hors de propos* (q-a04 : une clause d'obligations, pour un dégât des eaux après le gel ;
  q-d03 : l'exclusion des cataclysmes naturels). Un refus cité n'est pas contresigné : il tient seul.
- *Une question à côté d'une exclusion trouvée* (q-a05 : propriétaire ou locataire ; q-d05 : la formule souscrite).
  L'exclusion est lue et citée, mais un point « à vérifier » l'emporte sur elle.
- *Une question de règlement passée au travers* (q-d10 : réunir les preuves du vol). Le titre de la clause n'est pas
  parmi ceux du règlement du sinistre (7.203).
- *Une garantie optionnelle* (q-b07 : les bagages) : l'option n'est pas dans la déclaration ; on attendait « couvert ».
- *Le couvert à tort* (q-b15, un dégât des eaux) : la lecture et les règles couvrent. La clause des exclusions du
  dégât des eaux (3.1.4.2), oubliée au premier appel puis redemandée au modèle, n'a pas été retenue.

**Le choix.** L'utilisateur fait de la lecture des clauses la méthode par défaut : à justesse comparable, elle promet
moins souvent à tort, et elle lit le texte du contrat au lieu d'une traduction. `COUVERTURE_METHODE` vaut maintenant
`clauses` par défaut ; la chaîne de règles reste disponible (`methode: "regles"`). Une limite est écrite avec le choix :
toutes les mesures de la lecture des clauses ont été faites avec la contresignature des règles ; le mode sans règles
traduites, celui d'un contrat nouveau, n'est pas mesuré. `docs/COMPRENDRE.md` est réécrit en comparaison des deux
méthodes.

### 7.208 Deux à trois minutes derrière l'hébergeur : un battement dans le suivi

**La question.** Avant de mettre la lecture des clauses en ligne : l'hébergeur laisse-t-il une requête durer deux à
trois minutes, et jusqu'à 260 secondes au jeu « quatre » ? Azure Container Apps passe les requêtes par un proxy
(Envoy) dont le délai par défaut est de 240 secondes ; la documentation de Microsoft le décrit comme un délai
d'inactivité (« idle request timeout », 4 minutes), que seul le mode d'entrée « premium » permet d'allonger.

**Ce qui est fait.** Le suivi (`/analyses/suivi`, celui qu'emploie l'écran) envoie déjà une ligne à chaque étape,
mais un seul appel au modèle peut rester muet plus de deux minutes. Il envoie maintenant une ligne vide toutes les
15 secondes tant qu'aucune étape n'arrive ; l'écran ignorait déjà les lignes vides. Un test. L'analyse en un seul
appel (`/analyses`, sans suivi) n'en profite pas : elle reste exposée au délai.

**Vérifié en ligne** (26 nov., image v10, méthode `regles` gardée pour les visiteurs, `methode: clauses` demandée
par la requête). Les lignes vides arrivent au fil de l'eau : le proxy ne les retient pas. Un premier cas (q-b17) a fini
en 95 s, sous la limite : il ne prouvait rien. Un second (q-b08, 290 clauses au dossier, 213 jugées) a fini en
**279 s**, la décision reçue en entier : la requête dépasse les 240 s sans être coupée. La méthode par défaut passe
à `clauses` en ligne. Deux défauts vus au passage, pour les finitions : une question posée deux fois dans la même
réponse ; une garantie optionnelle qui ne donne lieu à aucune question. **Corrigés** le même jour : la réponse reprend
les questions de la décision, chacune une fois (la liste les comparait à elle-même avant d'être remplie, et la même
question pouvait y entrer deux fois) ; une option qui couvre seule fait demander si elle est souscrite, avec son
article. Deux tests.

**Le coût en ligne.** Une analyse coûte maintenant 8 à 10 centimes au lieu de moins d'un ; la limite de 300 analyses
par jour, pensée pour l'ancienne méthode, est à baisser.

### 7.209 L'en-tête de l'écran dit la méthode qui répond, et l'état du service ne déborde plus

**Ce que j'ai vu à l'écran**, le 26 au matin, sur la première analyse en ligne par la lecture des clauses (un piéton
renversé à vélo, assureur A : « couvert », les règles concordent, trois articles de responsabilité civile cités). La
réponse était juste, mais l'en-tête disait encore « le modèle lit la déclaration, la logique décide » et nommait
Mistral Medium, alors que la réponse venait de Mistral Large, clause par clause. Et la pastille « Service
disponible » débordait sur la page.

**Les deux causes.** L'en-tête ne connaissait pas la méthode du serveur : `/api/v1/sante` donne maintenant la méthode
par défaut et, pour la lecture des clauses, son modèle ; l'en-tête et la fenêtre de suivi en tirent leur phrase, et
l'état du service nomme les deux modèles (la lecture, et la contresignature). Le débordement venait d'un nom de classe
employé deux fois : la petite case de couleur de la légende des conditions (`.pastille`, 10 pixels de côté)
s'appliquait aussi à l'état du service. Elle s'appelle maintenant `.repere-couleur`. Un test pour la santé.

**Puis la place de l'état du service.** Une fois la pastille rendue à sa taille, la ligne d'état, plus longue, est passée sous le titre : l'en-tête a grandi, et la zone de la déclaration a rétréci d'autant. Le titre cède maintenant la place (il peut passer à la ligne), l'état reste à droite sur une ligne, en plus court (« clauses : … · règles : … ») ; le détail complet est dans l'infobulle.
La légende des cadres de couleur (conditions traduites en entier, en partie) passe aussi sur la ligne du titre « Les conditions générales », à droite et en plus petit : une ligne de moins au-dessus de la déclaration.
Et la page d'accueil décrivait encore la première méthode (« Lire : un modèle traduit la déclaration en faits d'un vocabulaire fermé », « ses réponses donnent la décision tout de suite ») : elle décrit maintenant celle qui répond (juger, trancher, vérifier ; deux à trois minutes).

**Puis la place de la saisie**, à la demande de l'utilisateur : la zone de la déclaration faisait 240 pixels sur un écran de 850. Trois gains, sans rien retirer de l'écran (ce qui sort de la vue passe dans les infobulles) : des cartes de contrat sur deux lignes (l'assureur ; le produit et la date, coupés si besoin), le reste au survol ; les exemples et le bouton « Analyser » sur une seule ligne, le compteur de caractères dans le coin de la zone de saisie ; des marges un peu plus serrées. La zone prend toute la hauteur qui reste.

### 7.210 Un dernier tour sur la justesse : deux règles générales, rejouées sur les jeux vus

**Le cadre.** L'utilisateur décide un dernier tour sur la justesse de la lecture des clauses, à condition que chaque
correction soit une règle générale, puis un cinquième jeu pour le mesurer. Je pars des quinze écarts du jeu
« quatre » (7.207), rangés en cinq familles. Ce jeu est vu désormais : le rejouer ne mesure rien, il vérifie qu'une
règle fait ce qu'elle dit. Les réponses brutes du modèle étant gardées, les rejeux ne coûtent rien.

**Deux règles, les plus sûres.**

- *Un doute qui ne peut pas faire couvrir ne retient pas la réponse.* Un store banne arraché par la tempête : la
  garantie tempête est exclue (les objets extérieurs, clause citée), mais une question restait sur la qualité
  d'occupant, posée dans un chapitre qui ne porte aucune garantie ; la réponse était « à préciser ». De même, une
  question de formule empruntée par renvoi à une garantie déjà exclue. La règle : un chapitre qui ne porte ni
  garantie ni option, ou une garantie dont le seul doute est emprunté et qui ne couvre rien elle-même, ne tient pas
  la réponse en suspens ; si toutes les garanties qui pouvaient couvrir sont exclues, la réponse suit les
  exclusions. Un premier essai, qui écartait aussi les chapitres d'options sans garantie propre, faisait refuser un
  vol à la terrasse d'un café que seule une option pouvait couvrir : le chapeau des options garde son doute.
- *Une absence de couverture ne l'emporte pas sur des règles qui hésitent.* La garde de 7.205 (une absence, sans
  clause citée, face à des règles qui couvrent : « à préciser ») vaut aussi face à des règles qui répondent « à
  préciser ».

**Rejoué** (sans frais, sur les réponses gardées ; ces jeux sont tous vus) :

| Jeu | Avant | Après | Ce qui change |
|---|---|---|---|
| « quatre » | 45 sur 60 | 49 sur 60 | deux refus à tort deviennent « à préciser » (justes) ; deux « à préciser » deviennent « non couvert » (justes) |
| « neuf » | 49 sur 60 | 48 sur 60 | un refus juste devient « à préciser » (n-b17) ; aucun couvert à tort de plus |
| « aveugle », 30 cas | 26 sur 30 | 27 sur 30 | un « à préciser » devient « non couvert » (juste) |

Le prix de la seconde règle se voit sur « neuf » : une absence qui avait raison devient une question. C'est le sens
d'erreur le moins coûteux, et il est voulu. Aucun couvert à tort n'est ajouté nulle part. Deux tests.

**Restent**, inscrits à la feuille de route : l'arbitrage ciblé quand la contresignature tire vers le doute (le plus
gros poste, six écarts, qui demande un appel de plus au modèle) ; les refus cités hors de propos ; trois petits
restes. Puis le jeu « cinq ».

### 7.211 L'arbitrage ciblé : relire les seuls obstacles des règles, avant de renoncer à un « couvert »

**Le constat.** Six des quinze écarts du jeu « quatre » viennent de la contresignature : la lecture couvre à raison,
les règles non, et un simple désaccord suffisait à rendre « à préciser ». La garde est voulue (elle a arrêté deux
couverts à tort au jeu « neuf », 7.205) ; elle était aveugle à la raison du désaccord.

**La règle.** Les règles disent pourquoi elles ne couvrent pas : leurs conditions examinées portent chacune une
clause, la question posée aux faits et la réponse (une exclusion établie ou possible ; une condition de garantie ou
une obligation non remplie ou inconnue). Quand la lecture couvre et que les règles non, on repose au modèle une seule
question par obstacle (six au plus) : la déclaration l'écarte-t-elle ? Il répond « écarte », « confirme » ou
« inconnu » ; « écarte » exige la phrase de la déclaration qui le montre, retrouvée mot pour mot par le code. Le
« couvert » ne tient que si chaque obstacle est écarté ainsi ; sinon la réponse reste « à préciser », comme avant.
Sans obstacle dit par les règles, aucune relecture. Un appel de plus au modèle, dans ces cas seulement. La consigne
interdit d'écarter sur ce qui est probable ou habituel : dans le doute, « inconnu ».

**Ce qu'il faut pour l'essayer à petit prix.** `couverture juger --rejouer` reprend les réponses gardées d'un passage
précédent, dans l'ordre des appels ; seul ce qui est nouveau (la relecture ciblée, et la chaîne de règles, qui ne
coûte presque rien) est demandé. Le rejeu s'écrit à part (`juger_<cas>_rejeu.txt`), l'original reste intact. Quatre
tests : le couvert qui tient ; la garde qui ne s'affaiblit pas (citation inexacte, obstacle confirmé, inconnu) ;
aucune relecture sans obstacle ; le rejeu sans appel.

**Rejoué chez Mistral** (26 nov., `juger --rejouer` sur les trois jeux vus : seules la chaîne de règles et la
relecture sont payées, quelques centimes ; ce n'est pas une mesure). Onze relectures en tout :

- *La garde tient* : n-a16 (l'assuré avait trop bu), l'obstacle est « confirmé » et la réponse reste « à
  préciser » ; n-a17 (les furets) ne déclenche pas de relecture, les règles n'y nomment pas d'obstacle. Aucun couvert
  à tort n'apparaît, sur aucun jeu.
- *Trois « couvert » justes retrouvés* au jeu « quatre » : la gouttière voisine (q-a02, l'exclusion des infiltrations
  par les fenêtres écartée : l'eau venait d'un tuyau rompu), la tonnelle et les chaises de jardin (q-b04), le drone
  sur la fenêtre de toit (q-d01).
- *La prudence ailleurs* : cinq obstacles « confirmés » ou « inconnus » (n-a08, n-a15 deux fois, q-a13, q-d04,
  av-d04) laissent la réponse à préciser, à raison pour q-a13, à tort pour les autres. Le modèle ne lâche un
  obstacle que sur une phrase de la déclaration, ce qui est voulu.

| Jeu (vu) | Avant 7.211 | Après |
|---|---|---|
| « quatre » | 49 sur 60 | 51 sur 60 |
| « neuf » | 48 sur 60 | 48 sur 60 |
| « aveugle », 30 cas | 27 sur 30 | 27 sur 30 |

**Une limite vue en relisant** : pour le drone (q-d01), le modèle a cité la déclaration entière comme preuve. Le code
vérifie que la citation existe, pas qu'elle dit précisément ce qui écarte l'obstacle. C'est la même limite que pour
les jugements (leçon 209), et elle reste.

### 7.212 La relecture d'un refus que les règles ne suivent pas

**Le constat.** Deux refus à tort du jeu « quatre » viennent d'une clause citée mot pour mot mais hors de propos :
une clause d'obligations pour un dégât des eaux après le gel (q-a04), l'exclusion des cataclysmes naturels pour un
sinistre qui n'en est pas un (q-d03). Un refus fondé sur une clause citée n'était pas contresigné : il tenait seul.

**La règle, symétrique de 7.211 et plus prudente.** Quand la lecture refuse en citant ses exclusions (six au plus) et
que les règles ne refusent pas, on relit ces seules clauses, une à une : chacune « joue » (le fait déclencheur cité
mot pour mot dans la déclaration), « ne joue pas » ou « inconnu ». La consigne rappelle qu'une clause d'obligations
ne refuse que si la déclaration dit le manquement et son lien avec le sinistre. Le refus tient si l'une des clauses
joue ainsi ; sinon la réponse devient « à préciser ». **Elle ne devient jamais « couvert »** : cette relecture ne peut
que confirmer un refus ou en faire une question, et ne touche pas à la garde contre les couverts à tort. Quand les
règles refusent aussi, rien n'est relu. Deux tests.

**Le prix attendu** : les refus justes que les règles ne suivaient pas (une dizaine par jeu, la lecture des clauses
y ayant raison contre des règles incomplètes) passent par cette relecture ; si le modèle répond « inconnu » trop
souvent, des refus justes deviendront des questions. À vérifier par le même rejeu, avant de garder la règle.

## 8. Ce qui reste à faire

Tenu à jour le 26 nov. 2026. Dans l'ordre où je le ferais.

**0. La lecture des clauses, après sa mesure (7.207).** Rien de ceci n'est mesurable sur le jeu « quatre », qui a servi :
chaque point demande un jeu neuf.
- Mesurer le mode sans contresignature, sur un contrat sans règles traduites : la condition pour dire qu'elle s'étend à
  un contrat nouveau.
- Une absence de couverture face à des règles qui disent « à préciser » : la même garde qu'en 7.205.
- Une exclusion citée face à un point « à vérifier » : laquelle doit l'emporter.
- Les refus cités hors de propos : les soumettre aux règles quand elles répondent « à préciser ».
- Le temps d'attente : deux à trois minutes, surtout la réflexion de Mistral Large.

**1. La validation par le métier.** C'est la première limite du projet.
- Faire relire les règles d'un contrat par un juriste ou un gestionnaire de sinistres, et mesurer sur ses propres cas.
- Un jeu fermé écrit par une personne : celui de `data/ferme/` l'a été par deux annotateurs automatiques (7.79).
- Valider le golden set (`data/golden/A_VALIDER.md`), en particulier la toiture et les clés.

**2. La lecture.** Elle reste la source de toutes les erreurs mesurées.
- Les identifiants montrés au modèle sans définition. Celui de « auteur » a été défini, mesuré et retiré (7.166) : la piste est générale, mais elle demande un jour de mesures, pas une matinée.
- La bougie fondue lue « accident » : la réponse est juste, sans la citation qui l'expliquerait (7.165).
- Des déclarations nouvelles, validées, pour mesurer les exemples de B et de D (7.144), et un second lot que rien n'a encore corrigé.
- Les erreurs qui se répètent : le vol dans une voiture chez B, la crue chez D (README, section 4).

**3. Les contrats.**
- Assureur C : les biens assurés, qui dépendent de la formule et de la qualité d'occupant, et un jeu de mesure (7.159).
- Assureur B : traduit en entier (7.175) ; à mesurer : des cas de voyage et de litige sur Internet dans son jeu fermé. Assureur D : les options, les assistances, les mesures de protection contre le vol.
- Un contrat hors habitation : le socle de la lecture (événement, bien, lieu) et les deux consignes sont à revoir pour lui (7.154). Aucun n'a été essayé.
- Les conditions particulières lues dans le document du client : aujourd'hui elles se saisissent (7.141).
- La loi applicable : écrite comme limite, non traitée.

**4. En ligne.**
- Un tableau de bord et une alerte sur le journal, qui part aujourd'hui dans les journaux de l'hébergeur (7.163).
- Le coût par analyse : les tokens ne sont pas relevés.
- Le temps du premier chargement quand le service dort.

**5. Le reste.**
- Contrôle mécanique à écrire : aucune exclusion commune ne doit rendre une extension impossible (leçon 70).
- Plusieurs biens déclarés ensemble : « couvert » dès qu'un seul entre dans une garantie (README, section 7).
- L'alerte de dépendance signalée par GitHub.

**Fait depuis le plan du 22 novembre** : le contrôle des variables sans événements (7.138), le doublon du vocabulaire (7.147), les libellés proposés par la rédaction (7.146), les exemples de B et D (7.144), le quatrième contrat à froid et son coût (7.148 à 7.159), la saisie des conditions particulières (7.141), la mise en ligne (7.160 à 7.163). Écartée : demander la victime pour tout sinistre (7.139).

## 9. Les leçons, en une ligne chacune

1. Le modèle établit des faits ; le code décide et vérifie.
2. Ce qui appartient au contrat se calcule une fois, se contrôle une fois.
3. La longueur d'une sortie se règle par la consigne, pas par le plafond.
4. Lire la documentation du fournisseur avant de soupçonner son propre code (réflexion « high » par défaut).
5. Garder un fichier de diagnostic : c'est lui qui a montré la réflexion de 30 000 caractères.
6. Une exclusion retire une garantie qui s'applique ; elle ne sert pas à refuser une garantie qui ne s'applique pas.
7. Quand on corrige des règles pour faire passer deux exemples, il est temps de construire le jeu d'évaluation.
8. Les bonnes catégories sont souvent déjà dans le métier (et dans le contrat) : périmètre, conditions, obligations, exclusions, limites.
9. Une confiance à 0,0 n'est pas une erreur de jugement mais une absence de réponse : lire les indicateurs avant de corriger le raisonnement.
10. La charge de la preuve est une règle de décision : l'assuré prouve la garantie, l'assureur l'exclusion.
11. Un garde-fou qui bloque une modification non versionnée vaut mieux qu'une bonne intention.
12. On choisit un réglage sur des mesures, et on garde l'ancienne méthode pour comparer.
13. Un modèle par usage : celui qui réfléchit pour le contrat (une fois), un rapide pour les sinistres (souvent).
14. Un écran d'abord : la décision, la preuve, la question à poser. Le détail est sur demande.
15. La structure se tire du contrat, pas des sinistres : les sinistres servent à tester.
16. Un principe doit être garanti par le code, pas espéré de la combinaison des règles.
17. Une mesure sans sa variance ne prouve rien : rejouer plusieurs fois avant de conclure.
18. Ne pas demander à un modèle de juger le travail d'un autre quand on peut lui faire refaire le travail et comparer.
19. Un score obtenu en connaissant les cas est optimiste : il faut un jeu de cas écrit sans regarder les règles.
20. Quand on ne peut pas exécuter un langage, une seconde implémentation et un test différentiel valent mieux qu'un pari.
21. Le moteur ne peut pas être plus juste que le vocabulaire : un fait jamais demandé est un fait ignoré, et l'ignorer peut vouloir dire couvrir.
22. Un jeu de validation se mesure une fois, avant correction ; corrigé, il devient de la mise au point.
23. Trois valeurs protègent contre un fait absent, pas contre un fait mal lu : une lecture fausse peut produire un refus ferme.
24. Lire les faits obtenus avant de corriger : deux hypothèses sur quatre étaient fausses.
25. Des faits « idéaux » écrits par celui qui connaît la réponse sont trop généreux ; la vraie mesure passe par la vraie lecture.
26. Un refus ne vaut que si toutes les garanties en jeu ont été examinées : un contrat partiellement traduit doit le savoir de lui-même.
27. Avant de toucher au moteur, relire le texte : deux erreurs « du moteur » étaient une phrase du contrat oubliée dans une règle.
28. Le modèle remplit un schéma, le code écrit les règles : ce qui se contrôle champ par champ ne s'invente pas.
29. Pour traduire un contrat, le contrôle le plus utile est celui de la couverture : ce que le modèle a omis, pas ce qu'il a écrit.
30. Une dépendance hors de Python (un programme) se déclare, se vérifie à l'exécution et s'installe dans l'image : le verrou de uv ne la voit pas.
31. Faire tourner les tests sur le système de l'auteur : la CI sous Linux ne voit pas les « \ » de Windows.
32. Enregistrer la réponse d'un modèle avant de la contrôler : une rédaction coûte des minutes, un contrôle qui plante ne doit pas la perdre.
33. Un contrôle de couverture sur les listes ne voit pas les conditions implicites : la définition d'un terme peut restreindre une garantie autant qu'une exclusion.
34. Une consigne qui demande plus rend la lecture moins stable : mesurer la variance à chaque version.
35. Un banc qui ne mesure qu'une réponse finale dit qu'il y a une erreur ; un banc en couches dit où elle naît.
36. Le vocabulaire doit nommer tous les périls du contrat, même non traduits : on ne peut pas dire « je ne sais pas » de ce qu'on ne sait pas nommer.
37. Un vocabulaire commun à plusieurs contrats doit être une hiérarchie : une valeur fine ne doit pas casser les règles écrites avec des valeurs larges.
38. Une hiérarchie de valeurs se raisonne à trois valeurs aussi : un fait vague ne vaut ni oui ni non pour une valeur précise.
39. Un oracle vérifie la logique, pas la forme : ce que l'outil réel refuse (un avertissement de chargement) mérite son propre test.
40. Mesurer la lecture par son effet sur la décision : un fait manqué qui ne change rien n'est pas une erreur, un fait inventé qui fait couvrir en est une grave.
41. Corriger l'instrument avant de corriger le système : un banc mal calibré fait chercher au mauvais endroit.
42. Contre un modèle qui invente, une consigne aide, un filtre dans le code protège.
43. Donner au modèle le sens des mots, pas seulement les mots : « parties communes » ne dit pas « local à vélos ».
44. Une consigne se réécrit en comparant à la précédente, ligne à ligne : ajouter une règle peut en effacer une autre.
45. Une interdiction large est obéie à la lettre : « n'ajoute pas de lieu » a fait oublier « une cuisine est dans le logement ».
46. Le banc sert d'abord à refuser un commit : une amélioration annoncée se mesure avant d'être gardée.
47. Quand chaque retouche de consigne en défait une autre, il faut un garde-fou dans le code, pas une phrase de plus.
48. Une exclusion certaine dispense de toute question : le « je ne sais pas » ne doit pas porter sur ce qui ne changera rien.
49. Un fait lu se cite comme une clause du contrat : les mots d'abord, la vérification par le code ensuite.
50. Un garde-fou se règle sur ce que le modèle produit vraiment : regarder ses sorties avant d'assouplir ou de durcir.
51. Un garde-fou qui retire plus de faits justes qu'il n'arrête d'inventions se retire : deux essais négatifs suffisent.
52. Avant d'ajouter de la méthode, mesurer ce que donne un meilleur modèle : c'est la question la moins chère.
53. Un outil se justifie par ce qu'on lui fait faire : Prolog n'apporte rien comme évaluateur, il apporte comme raisonneur par hypothèses.
54. Une question qui ne change aucune décision ne se pose pas ; une question qui tranche se pose en premier, avec ce qu'elle entraîne.
55. Un banc qui ne trouve plus rien n'est pas la preuve que tout va bien : on l'agrandit jusqu'à ce qu'il retrouve des erreurs.
56. Une exclusion que l'assureur doit prouver ne se pose pas en question à chaque client : inconnue, elle ne joue pas.
57. Allonger ce que lit un petit modèle a un prix : chaque valeur ajoutée au vocabulaire se paie en faits oubliés ailleurs.
58. Une explication qui sort du moteur vaut preuve ; une explication rédigée par le modèle après la décision n'en est qu'un récit.
59. Le code qu'on garde pour mémoire se paie à chaque lecture : la mémoire est dans git et dans ce document.
60. Une citation exacte ne prouve pas une lecture juste : la vérification arrête l'invention, pas l'excès de confiance.
61. Un schéma qui oblige à répondre pousse à remplir : la case « inconnu » doit être la première offerte, pas la dernière tolérée.
62. Quand un modèle remplit au lieu de laisser vide, chercher ce qui l'oblige à répondre (un schéma, une liste de questions) avant de réécrire la consigne : ici, c'était la liste de questions.
63. Un fait oublié qui ferait refuser coûte plus cher qu'un fait inventé qui fait demander : on choisit la lecture qui oublie le moins ce qui décide.
64. Comparer deux lectures ne sert à rien si les erreurs se répètent à l'identique : il faut changer de question, pas la reposer.
65. Un contrôle qui retire des faits doit être asymétrique : il peut rendre une réponse plus prudente, jamais plus généreuse, et c'est le moteur qui dit laquelle des deux il produit.
66. Avant de répondre ferme, demander au moteur sur quels faits la réponse repose, et les faire confirmer : c'est là que se décide un « je ne sais pas » honnête.
67. Confirmer qu'un fait est écrit n'attrape ni un fait mal rangé ni un fait oublié : chaque erreur de lecture a son contrôle.
68. Un « à vérifier » se lit avant de se corriger : la moitié des alertes d'Assureur B venaient de deux limites générales du découpage, pas du contrat.
69. Les contrôles mécaniques attrapent la forme, pas une traduction plausible mais fausse : corriger la chaîne, pas le contrat.
70. Une exclusion commune doit être compatible avec chaque extension : le vol à la tire excluait le vol par agression.
71. Ajouter des règles pour un assureur ne doit pas changer les réponses d'un autre : le banc du premier est le test d'étanchéité.
72. Un vocabulaire commun pour comparer, une lecture propre à chaque contrat pour décider.
73. Trois filets, trois sortes d'erreurs : les contrôles la forme, la relecture le sens visible, les cas le sens en action.
74. Chaque variable nouvelle doit apprendre à être lue : la rédaction devrait proposer ses aides en même temps qu'elle.
75. Sur un contrat neuf, le banc trouve d'abord des erreurs de traduction, puis des erreurs de lecture.
76. Une exclusion que rien n'évoque reste une réserve ; une exclusion que la déclaration entame devient une question (précise la leçon 56).
77. Rédiger en parallèle va trois fois plus vite, mais chaque proposition invente son vocabulaire : la relecture commence par harmoniser les noms.
78. Chaque garantie traduite ouvre une route de plus vers « couvert » : une valeur nouvelle doit être rattachée à celles que les règles connaissent déjà.
79. Une garantie optionnelle (« si les conditions particulières le mentionnent ») est une réserve, jamais une question au déclarant (7.109 : seule à couvrir, elle donne « à préciser », le point à vérifier dans les conditions particulières).
80. Un juge plus fort corrige les erreurs de fait, pas les erreurs de choix ; un juge plus strict coûte des réponses justes.
81. Une garantie ne répond pas toujours à « est-ce couvert ? » : certaines disent ce qui s'y ajoute, et ne doivent pas entrer dans la décision.
82. « Étendre » recouvre trois choses (ajouter des frais, élargir un lieu, couvrir une autre responsabilité) ; la simulation sur le golden les distingue en une minute.
83. Une documentation qui décrit un système retiré est pire qu'une absence : elle se relit à chaque simplification, comme le code.
84. En Prolog, une relation pensée pour calculer une valeur ne sert pas forcément à la vérifier : on calcule, puis on compare.
85. Une condition écrite au mauvais niveau ne se voit pas à la lecture du texte ; elle se voit sur un cas que la garantie doit couvrir.
86. Un exemple dans une consigne devient le vocabulaire du modèle : l'écrire comme une place à remplir, pas avec le nom d'un contrat.
87. Une marque interne rangée parmi les vraies valeurs d'un champ s'y mélange : la filtrer partout où le champ se complète.
88. Deux bancs ne se comparent qu'à configuration égale : le rapport doit nommer celle de son point de comparaison.
89. Un vérificateur trop strict ôte au système les « non » qui permettent de refuser : dire ce qu'est une négation écrite.
90. Assouplir un vérificateur laisse passer les bons « non » et les mauvaises lectures : mesurer les refus à tort.
91. Un exemple de consigne tiré du jeu d'essai rend ce cas inutile pour la mesure : prendre un exemple voisin.
92. Quand une consigne ne change plus un petit modèle, changer qui décide : un second avis plus fort, sur les seuls faits qui comptent.
93. Pour mesurer la fidélité des règles au contrat, la référence ne doit rien devoir aux règles : ni l'auteur des cas, ni leur vocabulaire.
94. Un jeu écrit en voyant les règles ne trouve pas leurs trous : seul un jeu écrit sans elles a montré la responsabilité civile refusée.
95. Une exclusion peut citer le bon texte et porter la condition de sa voisine : seul un cas qui la met à l'épreuve le montre.
96. Une nouvelle valeur du vocabulaire peut voler les lectures d'une valeur existante : la rattacher à celles dont elle prend la place.
97. Un statut « OK » d'ingestion qui ne regarde que la forme laisse passer un contrat illisible : vérifier le texte de quelques articles.
98. Une variable qui ne sert qu'à une exception prouvée par l'assureur n'a pas à être lue : la lire allonge chaque consigne pour rien.
99. Un concept peut se définir par lui-même à travers une extension : chercher les cycles, aucun contrôle de nom ne les voit.
100. Une disjonction de faits oui/non n'est fausse que si tous sont lus « non » : une variable à plusieurs valeurs rend le refus possible.
101. Une page sautée à l'ingestion peut être la seule à dire une condition : la lire autrement, pas l'oublier.
102. Ce qui dépend des conditions particulières (la formule) se met en circonstance : au périmètre, un refus voisin l'emporte.
103. `--accepter` lit les contrôles enregistrés : après un changement du contrat, `--controler` d'abord.
104. Un banc qui ne garde pas les faits lus oblige à deviner : garder, pour chaque cas, ce que le modèle a lu.
105. Un fait lu peut en dire un autre : l'écrire dans le vocabulaire (« implique »), au lieu d'espérer que le modèle écrive les deux.
106. Un fait que le petit modèle infère malgré l'aide (« fait construire » → moins de dix ans) : ne plus le lire, et le demander.
107. Confirmer un fait déduit, c'est confirmer le fait qui le dit : la conséquence n'est jamais écrite telle quelle.
108. Le modèle traduit une condition par une variable : relu, le vocabulaire se resserre en quelques variables à plusieurs valeurs.
109. « Tous » est dangereux pour une exclusion de biens : une exclusion nomme les garanties qu'elle vise.
110. Une valeur fourre-tout lue à côté d'une valeur précise doit s'effacer : sinon elle suspend toute décision.
111. Accepter une version de Python qu'on ne teste pas, c'est garder dans le verrou des dépendances qu'on ne met jamais à jour.
112. Un vocabulaire juste se vérifie sur le contrat suivant : celui de D a suffi pour A et B sans une variable de plus.
113. Une aide qui cite le mot à exclure (« vélo électrique ») l'attire : dire aussi, en clair, ce que la valeur n'est jamais.
114. Une limite notée « connue » finit par coûter un cas : celle du typage a annulé une garantie juste.
115. Un contrat ne lit que ses variables ; il doit lire aussi celles qui les impliquent, sinon un fait dit autrement se perd.
116. Des déclarations écrites comme les gens écrivent montrent d'autres erreurs que des cas rédigés : l'objet d'autrui cache la responsabilité civile.
117. Un défaut vu deux fois dans les règles se corrige dans le moteur : une garantie qu'on ne sait pas rattacher ne doit pas refuser.
118. Une obligation qui fait refuser sans lien causal, mise en jeu par la déclaration, se demande : en faire une réserve couvre à tort.
119. Un cas de test qui a servi à corriger ne mesure plus rien : partager avant de corriger, et figer le partage.
120. Une règle qu'on a écrite se relit dans ses propres aides : « vélo électrique » dans l'aide du véhicule à moteur attirait le vélo.
121. Une garantie optionnelle se déclare dans le contrat, pas dans le vocabulaire : la même variable est une option chez l'un, une garantie de base chez l'autre.
122. Ce qu'on a essayé et écarté se retire du code : un réglage qu'on ne mesure plus est une branche qu'on ne teste plus.
123. Deux séries de bancs lancées en même temps se gênent : la latence mesurée devient celle du fournisseur saturé.
124. Quand le modèle s'obstine sur une valeur fausse, lui donner la valeur qu'il cherche (le vélo), plutôt qu'une aide de plus.
125. Une précision du code faite après la lecture arrive trop tard si elle décide des questions suivantes.
126. Ce qu'on demande au client se choisit en un seul endroit : deux listes construites séparément finissent par se répéter.
127. Une consigne qui sert à deux étapes (la vérification et la confirmation) se mesure sur les deux : la rendre plus stricte pour l'une a fait douter l'autre.
128. Un exemple montré à une étape qu'on ne vérifie pas est recopié sans contrôle : n'en montrer qu'aux étapes vérifiées.
129. Le même modèle ne se corrige pas lui-même sur un choix de catégorie : sa vérification vaut pour « est-ce écrit ? », pas pour « est-ce le bon mot ? ».
130. Avant de comparer deux lectures, compter les appels sans réponse : un délai dépassé se lit comme une mauvaise lecture.
131. Avant de retirer une phrase d'une consigne, chercher les variables qu'elle influence sans les nommer, chez chaque contrat.
132. Une question n'est posée que si sa réponse peut servir : la règle qui retire un fait hors sujet vaut aussi pour les questions.
133. Un banc note la décision, pas ce que l'écran demande : tester à part que chaque question posée peut servir.
134. Une réserve n'est pas une question : ce que l'assureur vérifiera s'affiche, ce que le client doit dire se demande.
135. Distinguer l'erreur instable de l'erreur répétée avant de choisir le remède : relire ne corrige que la première.
136. Trois corrections pour une même phrase : arrêter, et chercher la règle ou la structure qui manque.
137. Un bon lecteur n'est pas forcément un bon vérificateur : mesurer chaque rôle à part, et pouvoir les confier à deux modèles.
138. Un identifiant sert au moteur, un libellé au lecteur : écrire le second à côté du premier, pas dans l'écran.
139. Une exception tolérée (une variable « lue partout ») se justifie par une règle qu'un test peut vérifier ; sinon elle cache un oubli.
140. Avant de corriger une structure, relire les erreurs mesurées une par une : la piste la plus élégante ne corrigeait aucune d'elles.
141. Compter avant de généraliser : sur 99 variables « propres », 29 ne sont pas lues dans la déclaration, et les doublons n'en retirent qu'une dizaine.
142. Une évidence sur les données se vérifie dans les données : « la déclaration ne dit jamais la formule » était faux pour trois cas du golden set.
143. Une erreur de manipulation est un cas de test gratuit : le texte collé par erreur a montré ce que répond le système quand il n'y a pas de sinistre.
144. Un garde-fou écrit pour une méthode se relit quand la méthode change : « le rôle vient du contrat » protégeait d'un modèle qui cite, et rétrogradait des règles qui citent juste.
145. Un zéro mesuré sur trois passages n'est pas un zéro : donner la fourchette de plusieurs séries, surtout pour l'erreur qui coûte.
146. Pour écrire des exemples sans copier les cas de mesure, ne pas les relire : laisser un contrôle automatique refuser ce qui leur ressemble.
147. Un exemple écrit loin des cas de mesure ne peut pas améliorer la mesure : choisir d'avance entre protéger le banc et le voir bouger.
148. Une hypothèse sur le fournisseur se vérifie auprès du fournisseur : « latest » n'avait pas changé de version ; c'est la même version qui lit le même texte autrement d'une heure à l'autre.
149. Nommer la version datée du modèle : les mesures restent attachées à ce qu'on a mesuré, et les bancs se rejouent à date fixe, pas seulement après un changement.
150. Ne pas entreprendre un changement dont l'effet attendu est plus petit que le bruit de la mesure : on ne saurait pas dire s'il a marché.
151. Avant d'aller chercher un contrat de plus, finir celui qui attend : il était déjà la mesure qu'on cherchait.
152. Ce qu'on montre au modèle, il s'en sert : lui montrer les formules de tous les contrats, c'est lui proposer d'écrire celles d'un autre.
153. Une définition plus étroite que le texte est une règle bien formée : aucun contrôle de forme ne la voit, seule la relecture.
154. Une décision juste ne prouve pas une règle juste : lire aussi la phrase et la clause qui l'accompagnent.
156. Un défaut corrigé par ses effets revient : chercher pourquoi le moteur a laissé passer, pas seulement quelle règle l'a déclenché.
155. Avant d'étendre une règle à d'autres contrats, comparer les décisions avant et après sur des faits tirés au hasard : c'est ce qui a montré qu'elle était fausse.
157. Mettre en ligne change qui peut appeler quoi : relire chaque route en se demandant ce qu'elle donne à un inconnu, avant de choisir l'hébergeur.
158. Un message d'erreur exact sur l'effet peut tromper sur la cause : « clé non configurée » voulait dire « fichier d'environnement vide ».
159. Ce qu'on écrit dans un fichier du conteneur disparaît avec lui : en ligne, ce qui doit rester sort par la sortie standard ou par un service.
160. Rejouer la question de l'énoncé sur chaque contrat, et lire la phrase comme quelqu'un du métier : une décision juste peut être mal dite.
161. Ce qu'un document annonce de l'écran se vérifie à l'écran, pas dans les notes d'un cas de test.
162. Une correction qui améliore le cas qu'on regarde se juge sur ceux qu'on ne regarde pas ; et un écart se rejoue dans les deux états avant d'être attribué au hasard.
163. Rejouer dans les deux états sert aussi à innocenter : la baisse de B est apparue juste après un changement, et ne venait pas de lui. Un modèle appelé par une API n'est pas un point fixe ; une fourchette publiée doit dire sur combien de passages elle repose.
164. Ce qu'un écran ne dit pas, on finit par le croire complet : l'état de la traduction se montre, et se déclare à la main quand le comptage automatique se trompe.
165. Quand la prestation n'est due que sous une condition que seul l'assuré connaît, cette condition se demande. Une exclusion qui retire un cas d'une garantie par ailleurs acquise ne se demande pas : elle joue quand la déclaration la dit.
166. Un jeu fermé qui révèle une erreur de règle a fait son travail une fois ; après la correction, ce cas est vu, et il faut l'écrire à côté du chiffre.
167. Avant d'écrire « complet », compter ce qui a été classé plutôt que traduit, dans tous les articles et pas seulement celui qu'on vient d'ouvrir.
168. Un garde-fou peut masquer un défaut : « à examiner par un gestionnaire » cachait une garantie qui couvrait trop. Lever un garde-fou se vérifie comme un changement de règle.
169. Un dépôt se relit après coup, sur le poste : « écrit » ne dit pas quelle version.
170. Une garantie que le contrat range sous un titre « Option » se demande ; « couvert sous réserve » est pour ce que le contrat donne par défaut. Le titre de l'article décide, pas l'habitude prise sur l'article d'à côté.
171. Un essai conforme à ce qu'on attendait ne prouve que l'attente : la guitare « couverte sous réserve » était le résultat prévu, et le défaut.
172. Ce qu'une image embarque se lit dans son fichier de construction, pas dans le dépôt : un fichier ajouté au projet n'y entre que si une ligne le copie.
173. Avant d'annoncer un écart, le vérifier avec le moteur : la section que je disais mal traitée l'était correctement depuis des jours, par un mécanisme que j'avais écrit et oublié.
174. Une exclusion d'une garantie définie par un fait (« en voyage », « lié à Internet ») ne doit jouer que si ce fait est établi : sinon elle refuse un sinistre qui relève peut-être d'une autre garantie.
175. Après une acceptation, lire le diff du vocabulaire commun : une règle propre à un contrat peut y étendre la lecture d'un fait pour les quatre.
176. Un risque vu avant le dépôt s'annonce avec son essai et son critère de retrait ; l'essai l'a confirmé en une commande.
177. Ajouter une valeur au socle commun (un événement) change ce que « pour tous » veut dire : chercher qui raisonne sur l'ensemble des valeurs avant de l'étendre.
178. « Traduit en entier » et « mesuré » sont deux affirmations : le vert dit la première, le banc la seconde, et il faut écrire laquelle manque.
179. Avant de corriger un écart avec une réponse attendue, vérifier que l'attente tient encore : le refus du vélo chez B datait d'avant l'option, et j'ai réglé une aide pour retrouver une réponse devenue fausse.
180. Quand la lecture rend les mêmes faits « à côté » à chaque passage, la règle peut les accueillir, à condition de seulement poser la question du contrat, et de dire que le cas a été vu.
181. Ce qu'on a refait à la main plusieurs fois dans la journée désigne la règle qui manque au code : c'est par là que commence une relecture.
182. Un test qui lit l'état déclaré du projet change de résultat quand le projet avance : il fixe lui-même l'état dont il parle.
183. Avant de refuser un chantier pour son risque, séparer ce qui change une réponse de ce qui change une écriture : unifier les options ne demandait de toucher à aucune règle mesurée.
184. Quand deux écritures voisines donnent deux décisions, le choix doit être un mot que le relecteur écrit et que le contrôle vérifie, pas un effet des mots de la citation.
185. Une précaution écrite dans les règles pour pallier le moteur doit sortir le jour où le moteur est corrigé : gardée, elle a transformé un refus juste en question.
186. Le coût d'un changement du moteur se mesure d'abord sur les cas à faits exacts, sans modèle : c'est rapide, et cela dit quelles réponses bougent avant tout banc.
187. Un test qui s'arrête à l'étape modifiée ne voit pas ce que l'étape suivante en fait : la décision se vérifie là où l'utilisateur la lit.
188. Ce qu'un test a rattrapé une fois et qu'on a réparé à la main reviendra au prochain ajout : la réparation va dans le code qui fait l'ajout.
189. Avant d'écrire « ces cas décident pareil », les convertir et comparer : la comparaison a trouvé celui qui manquait à la liste, et il décidait autrement.
190. Essayer une phrase qu'aucun jeu de cas ne contient, et lire la preuve citée, pas seulement la décision : un refus juste en apparence citait une exclusion du vol pour un objet tombé.
191. Un rangement se prouve comme un calcul : même arbre syntaxique hors imports, chaque import résolu, puis les tests ; « ça a l'air pareil » n'est pas une preuve.
192. « On ne réécrit pas du code mesuré » vaut tant qu'on ne peut pas comparer l'ancien et le nouveau ; quand on le peut, le refus n'est plus de la prudence, c'est une mesure qu'on n'a pas faite.
193. Un jeu de test dont on a regardé trois cas pour corriger une règle n'est plus fermé : on le dit à côté des chiffres, et on en écrit un autre, par quelqu'un qui n'a pas vu les règles.
194. Le chiffre d'un jeu qu'on a regardé pendant les réglages mesure les réglages : B passe de 90 % à 58 % sur vingt cas neufs. Le seul chiffre qui parle d'un contrat est celui du jeu qu'on n'a jamais ouvert.
195. Quand un banc garde les faits lus, les rejouer sur les règles sans modèle sépare en une seconde ce qui vient des règles de ce qui vient de la lecture, et dit ce qu'une correction change avant de payer un passage.
196. Corriger d'après un jeu neuf le brûle : la mesure d'après se fait sur un autre, écrit de la même façon, sinon on a seulement appris les réponses.
197. Neuf corrections tirées d'un jeu n'ont pas fait monter le suivant : ce qu'on corrige d'après vingt cas vaut pour ces vingt cas. Le chiffre honnête d'un système est celui du dernier jeu qu'il n'a pas vu, et il faut l'écrire même quand il baisse.
198. Quand deux tours de corrections ne font pas monter le chiffre d'un jeu neuf, ce n'est plus une liste de défauts, c'est la méthode : s'arrêter de corriger, nommer le défaut de fond, et changer ce qui décide.
199. Une date qu'on s'est fixée soi-même ne justifie pas de livrer ce qu'on sait insuffisant : on la déplace, on le dit, et on garde livrable ce qui marche.
200. On ne constate un manque que si l'on a écrit d'avance ce qui devait être là : une liste de ce qui est attendu, puis une jointure, valent mieux qu'un lecteur à qui l'on demande de ne rien oublier.
201. Un essai gratuit sur des cas déjà vus ne mesure rien, mais il trouve les défauts de construction avant qu'on paie pour les voir : trois ici, dont un qui empêchait toute réponse « couvert ».
202. La taille de la réponse se compte avant d'appeler : cent clauses à une ligne chacune dépassent la limite du modèle. On ne fait écrire en détail que ce qui décide, et le reste en liste.
203. Quand le modèle hésite entre deux cases, regarder si la bonne case existe : « l'indemnité sera réduite de moitié » n'était ni une exclusion ni rien, et la liste des effets n'avait pas de mot pour le dire.
204. Un modèle recopie mal un identifiant qu'on a fabriqué (« 25 » pour « S25 ») : le contrôle doit le rétablir quand il n'y a qu'une lecture possible, et refuser quand il y en a deux.
205. Garder la réponse brute du modèle avant de la lire : une réponse illisible qu'on n'a pas gardée se paie une seconde fois pour être comprise.
206. Une règle qui fait passer le cas du jour mais contredit un test écrit pour éviter un couvert à tort se retire : le test disait déjà pourquoi.
207. Un coût annoncé sur un tarif supposé se vérifie à la source avant de servir à choisir : le modèle « moyen » facturait ses réponses presque deux fois plus cher que le « grand ».
208. Une exclusion peut n'écarter qu'un poste du dommage (« les frais de réparation de l'élément à l'origine du dommage couvert ») : la lire comme un refus du sinistre, c'est lire juste et conclure faux.
209. Deux citations exactes ne font pas un jugement juste : le contrôle prouve que les phrases existent, pas qu'elles ont un rapport. Ce que le code ne peut pas vérifier se mesure, sur des cas.
210. Avant de corriger une méthode qui échoue, changer seulement le lecteur sur les mêmes cas : si un meilleur modèle réussit avec le même dossier et la même consigne, le défaut n'était pas dans la méthode.
211. Lancer les cas en parallèle raccourcit un passage, pas une analyse : le temps qu'attend l'utilisateur devant l'écran ne se règle qu'en changeant ce que fait le modèle.
212. Quand un modèle n'obéit pas à une consigne, chercher dans le contrat ce qui distingue les cas : ici, les titres des chapitres disaient déjà quelles clauses ne décident pas de la couverture.
213. Les tests ne doivent dépendre ni du `.env` du poste ni du réseau : une garde qui refuse tout appel au fournisseur coûte trois lignes, un réglage qui fuit coûte des appels payés.
214. Une absence de couverture n'est pas un refus : seul un refus qui cite sa clause peut l'emporter sur une autre lecture qui couvre.
215. Sur un jeu jamais vu, l'écart d'un jeu vu fond : 48 contre 38 sur « neuf », 45 contre 42 sur « quatre ». Ce qui tient est souvent le sens des erreurs, pas leur nombre.
216. Une garde qui contresigne hérite des erreurs de celui qui contresigne : six des quinze écarts de la nouvelle méthode viennent des règles de l'ancienne.
217. Un outil de mesure ne s'arrête pas sur la panne d'un cas : une erreur du fournisseur se compte comme une erreur de ce cas, et le passage continue.
218. Une réponse longue derrière un proxy se protège par le flux : une ligne vide régulière coûte trois lignes de code, une requête coupée coûte l'analyse.
219. Un doute n'a de poids que s'il peut changer la réponse : une question qui ne peut ouvrir aucune garantie ne doit pas retenir un refus fondé sur une clause citée.
220. Une garde gagne à savoir pourquoi elle bloque : relire le seul obstacle que les règles nomment garde la prudence et rend les réponses justes que le simple désaccord sacrifiait.
