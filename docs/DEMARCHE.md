# La démarche, dans l'ordre où elle s'est construite

Ce document garde le raisonnement, pas seulement le résultat : ce qu'on a essayé, ce qui
a échoué, pourquoi, et ce qu'on en a tiré. Chaque version de consigne citée ici est
archivée en texte intégral dans [`docs/consignes/`](consignes/README.md).

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
- Les **CG réelles de Foyer** (appart 123, 48 pages). Elles ne sont pas versionnées : un
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

## 6. Brancher Mistral : les surprises de l'API

- `top_p` doit valoir 1 quand `temperature` vaut 0 → paramètre ajouté.
- La réponse peut être une **liste de morceaux**, dont des morceaux de réflexion
  (« thinking ») → lecture du seul texte (`texte_du_message`).
- Réponses **coupées** à la limite de longueur → erreur explicite (`ReponseTronquee`) au lieu
  de « aucun objet JSON ».

## 7. Le 17 novembre : du premier échec à la remise en question

### 7.1 Grille v1 : réponse coupée

Premiers essais sur Foyer : `INCERTAIN`, « réponse coupée à 8000 tokens », environ 4 minutes
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

### 7.8 Première compilation de Foyer : la réflexion du modèle, encore

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

Reste à améliorer à la compilation : chaque fiche devrait avoir une condition sur **l'objet**
(« le dommage porte-t-il sur le bâtiment ? » pour la 2.11), pour qu'une fiche hors sujet soit
écartée par une réponse « non » plutôt que par l'absence de réponse.

## 8. Ce qui reste à prouver

- Compiler Foyer, relire ses fiches, corriger ce qui doit l'être.
- Annoter les 14 sinistres sur Foyer, puis `couverture comparer` : exactitude, faux
  « couvert », taux d'incertain, durée.
- Choisir le modèle et le niveau de réflexion **sur ces mesures** (large/low, medium, small),
  pas sur une intuition.
- Limite connue : la responsabilité civile de Foyer (section 5) est typée « autre » par le
  découpage, donc pas encore compilée en fiche.

## 9. Les leçons, en une ligne chacune

1. Le modèle établit des faits ; le code décide et vérifie.
2. Ce qui appartient au contrat se calcule une fois, se contrôle une fois.
3. La longueur d'une sortie se règle par la consigne, pas par le plafond.
4. Lire la documentation du fournisseur avant de soupçonner son propre code (réflexion « high » par défaut).
7. Garder un fichier de diagnostic : c'est lui qui a montré la réflexion de 30 000 caractères.
8. Une exclusion retire une garantie qui s'applique ; elle ne sert pas à refuser une garantie qui ne s'applique pas.
5. Un garde-fou qui bloque une modification non versionnée vaut mieux qu'une bonne intention.
6. On choisit un réglage sur des mesures, et on garde l'ancienne méthode pour comparer.
