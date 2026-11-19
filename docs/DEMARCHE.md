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

**1. Mesurer avant de corriger.** Un jeu d'évaluation sur Foyer
(`data/annotations/foyer-appart123-2025.jsonl`) : 14 sinistres, dont 6 qui doivent sortir
COUVERT (vol avec effraction dans l'appartement, vrai incendie, dégât des eaux, vol à l'arraché),
pour voir les refus à tort. Chaque réponse attendue cite les clauses qui la fondent. Certains cas
sont réellement ambigus sans les conditions particulières (cave fermée par un cadenas, alors que
la « serrure de sûreté » exclut le cadenas ; mobilier de jardin, exclu du contenu sauf option) :
le champ `acceptables` admet alors un INCERTAIN honnête, jamais un COUVERT à tort. Deux nouveaux
indicateurs : `faux_refus` et `exactitude_stricte`. Les réponses sont proposées par Claude et
**à valider** par une personne : le statut le dit dans chaque ligne.

**2. Refaire la structure des fiches avec les rôles du droit des assurances.** Les quatre
règles étaient des approximations d'une distinction que le contrat fait lui-même. L'art. 2.10
de Foyer a une section « Obligation de prévention » séparée, avec « nous refuserons notre
intervention s'il existe un **lien causal direct** » et « en cas d'effraction, le non-respect
de ces obligations est **sans incidence** ». Une liste plate de « conditions » ne peut pas
exprimer ça.

| Rôle | Exemple (Foyer, vol) | Effet sur la décision |
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

Compilation v2 de Foyer : 36 fiches, 350 questions, 9 écartées. Évaluation `fiches` sur les
14 cas : **0 couvert à tort, 0 refus à tort**, mais 13 INCERTAIN sur 14 (exactitude 0,43 en
comptant les incertains acceptables, 0,07 en stricte). Prudent, donc, mais inutile.

La confiance a donné le diagnostic. **Sept cas à 0,0** : ce n'est pas une mauvaise réponse,
c'est une absence de réponse. Ce sont tous des vols : cinq fiches vol, les dégradations et les
exclusions générales, environ 80 questions dans un seul appel, coupé ou hors délai. Les autres :
- les deux vrais incendies restent INCERTAIN à cause d'exclusions « inconnues » (« vice de
  construction connu de vous ») ;
- la bougie au jardin ne trouve aucune garantie : le modèle a classé l'événement en « dommage
  accidentel », catégorie sans fiche chez Foyer, alors que le lexique aurait reconnu « bougie ».

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

Recompilation de Foyer (Mistral Large) : 38 fiches, 315 questions, **4 écartées seulement**
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

### 7.15 Repartir de la clause : comment structurer des conditions générales

Après ces corrections successives, retour à la question de fond : comment se présente une clause,
et comment la traiter ? Une remarque de l'auteur a recadré la discussion : **la structure doit se
tirer du contrat lui-même, pas des sinistres**. Les sinistres ne servent qu'à tester.

**Anatomie d'une clause réelle** (Foyer, art. 2.10 « Garantie vol » et 2.10-a, p. 11-12) :
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
faits commun** : chaque fiche pose ses propres questions en texte libre (350 pour Foyer).

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
(2.7) de Foyer :

```
regles/vocabulaire.json        les variables communes à tous les contrats, et leurs valeurs
regles/moteur.pl               le moteur unique : logique à trois valeurs, règles de gestionnaire
regles/foyer-appart123-2025.pl les règles du contrat, chacune avec sa phrase du contrat
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
| `evenement_traduit(...)` dans chaque contrat ; un événement déclaré non traduit plafonne la décision à INCERTAIN | moteur (règle 8), règles Foyer | Un refus ne vaut que si toutes les garanties en jeu ont été examinées. Sans déclaration, tout événement est « non traduit » : le défaut est prudent |
| « vol commis sur l'assuré » : périmètre `non(concept(batiment))` | règles Foyer | Le texte dit « en dehors des biens assurés » ; la règle l'avait omis, d'où la question absurde pour un scooter volé au garage (val-04, val-15) |
| incendie : périmètre lié aux événements incendie, explosion, foudre | règles Foyer | Une garantie ne pose de questions que sur ce qu'elle couvre (pas de « flammes ? » pour une tempête) |
| obligation de fermer les fenêtres en cas d'absence | vocabulaire `fenetres_fermees`, règles Foyer | Citée mot pour mot au 2.10 ; seules les portes étaient traduites (val-01) |
| exclusion du gel sauf mesures de prévention | vocabulaire `prevention_gel`, règles Foyer | Citée mot pour mot au 2.7 ; absente des règles (val-10). Mesures inconnues : réserve, pas refus (l'assureur prouve l'exclusion) |
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

**Recherche de jeux publics** : aucun ne donne la réponse selon les CG de Foyer (elle dépend du contrat).
Sources retenues : LegalBench `insurance_policy_interpretation` (138 couples déclaration-police, réponse
couvert / non couvert / ambigu, CC BY 4.0) comme second banc de généralisation ; les décisions des
médiateurs (FSPO irlandais, Financial Ombudsman britannique), la Médiation de l'Assurance et Judilibre
comme sources de situations réelles pour le jeu fermé, à réécrire et à annoter selon les CG de Foyer.

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

### 7.51 Trois contrats de plus : AXA Luxembourg, Société Générale, MACSF

Pour montrer que la méthode se généralise, trois conditions générales réelles sont téléchargées par
l'auteur (liens dans `data/contrats/SOURCES.md` ; le lien MACSF sert désormais la version d'avril 2026,
ajoutée au catalogue). Première ingestion, sans rien changer :

| Contrat | Clauses | Statut | Alertes |
|---|---|---|---|
| MACSF Multirisque Habitation (2026) | 207 | OK | — |
| Société Générale Habitation (2025) | 157 | À vérifier | aucune définition reconnue |
| **AXA Luxembourg OptiHome (2017)** | 292 | À vérifier | 118 clauses sans type ; 25 renvois introuvables |

**AXA, le second contrat visé** (luxembourgeois, comme le recruteur). Deux causes, deux corrections
générales, plus un profil d'assureur :
- **Le profil ne reconnaissait pas les titres numérotés.** AXA titre ses sections « 3.1.6.1 Etendue de la
  garantie », « 3.1.6.2 Vols exclus » ; le profil comparait le titre avec son numéro. Il le compare
  désormais sans. Profil `data/profils/axa-lu.json` : « étendue de la garantie », « objet de la
  garantie » → garantie ; « montant des garanties », « estimation des dommages » → limite ; « délai de
  carence », « étendue territoriale » → condition.
- **Les renvois vers des sous-points énumérés dans le texte** (« 3.1.7.2.9 les pertes… » écrit dans la clause
  3.1.7.2) n'avaient pas de clause à eux. Un tel renvoi mène maintenant à la clause qui le contient (au plus
  deux niveaux au-dessus).

Résultat : **AXA passe à OK** (293 clauses : 34 garanties, 25 exclusions, 51 conditions, 18 limites, 71
définitions ; 94 « autre », surtout les dispositions administratives : résiliation, prime, prescription).
Pour la garantie vol, par exemple : 3.1.6.1 étendue (garantie), 3.1.6.2 vols exclus (exclusion), 3.1.6.3
limites d'indemnité (limite), 3.1.6.4 mesures de sécurité (condition). Foyer est inchangé.

**Société Générale** reste à vérifier : sa mise en page (numéros de page pris pour des numéros d'article,
titres aux lettres espacées) demanderait un profil plus lourd ; contrat français, il passe après AXA.

### 7.52 AXA : des règles qui partent de zéro

Pour Foyer, les premières garanties ont été écrites à la main pour servir de modèle. **Pour AXA, aucune
règle n'est écrite à la main** : c'est le vrai test de la généralisation. Le fichier
`regles/axa-lu-optihome-2017.pl` part vide (en-tête seulement) ; tant qu'il l'est, aucun événement n'est
traduit et le moteur répond « à examiner par un gestionnaire », jamais « non couvert ». Chaque garantie
passe ensuite par la même chaîne que la 2.9 de Foyer : Mistral Large rédige à partir des clauses de
l'article et des définitions du lexique AXA qu'elles emploient, le code contrôle (citations mot pour mot,
vocabulaire, concepts, chargement Prolog), l'auteur relit, puis accepte. Première garantie : **le vol
(3.1.6)**, découpé en étendue (3.1.6.1), vols exclus (3.1.6.2), limites d'indemnité (3.1.6.3) et mesures de
sécurité (3.1.6.4). À mesurer : ce que la rédaction réussit seule, ce qu'il faut ajouter au vocabulaire
commun, et le temps humain de relecture.

### 7.53 Première rédaction AXA (vol, 3.1.6) : un plantage, puis ce que les contrôles voient et ne voient pas

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
omises), pas une traduction plausible mais fausse. Corriger la proposition à la main aurait réglé AXA 3.1.6,
et rien d'autre : il aurait fallu recommencer pour chaque contrat. On a donc corrigé les causes, dans la
chaîne de rédaction elle-même (consigne `redaction-regles` v3) :

| Défaut observé | Cause | Correction générale |
|---|---|---|
| Extensions sans exclusions | le format n'avait pas d'endroit pour « les exclusions de l'article » | champ `exclusions_communes`, écrit `exclusion([g1, g2, …], …)` ; **bloquant** si une garantie n'a aucune exclusion alors que l'article en a |
| `agression` à côté de `violence` | le modèle ne voyait que les noms et les valeurs du vocabulaire | le vocabulaire lui est donné avec la question de chaque variable ; une variable nouvelle doit dire `plus_proche` (la variable existante la plus proche et pourquoi elle ne suffit pas), **à relire** sinon |
| Réserves perdues (« à l'exception du mobilier de jardin ») | rien ne le demandait | règle 3 bis de la consigne ; **à relire** si le texte cité a une réserve que la condition ne reprend pas |
| Conditions glissées dans les limites | idem | règle 4 précisée ; **à relire** si une limite porte « si », « s'ils », « lorsque » |
| `non_traduit` en phrases | format non vérifié | écart de schéma (reprise demandée au modèle) |

Rejoués sur la proposition AXA déjà rédigée, sans relancer le modèle, ces contrôles signalent seuls les cinq
extensions sans exclusions (bloquant), les deux réserves perdues et les quatre plafonds conditionnels (à
relire), et les quatorze variables nouvelles sans justification. La relecture humaine reste, mais elle part
d'une liste, pas d'une lecture ligne à ligne. Ce qui n'est pas automatisé : juger qu'une justification
`plus_proche` est bonne. La mesure suivante : relancer la rédaction avec la consigne v3 et compter ce qui
reste.

### 7.54 Deuxième rédaction AXA (consigne v3) : le fond suit, la forme casse, le code répare

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

### 7.55 La relecture humaine d'AXA 3.1.6 : ce qu'elle a changé, et combien de temps

La relecture a porté sur le JSON de la proposition, pas sur le PDF. Chaque modification est tracée dans
`meta.relecture` du fichier (`regles/propositions/axa-lu-optihome-2017/3.1.6.json`). Environ vingt minutes
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
avertissement. Il n'y a pas encore de cas annotés AXA : la non-régression est vide, et c'est la prochaine
étape.

**L'effet de bord.** Les variables acceptées n'avaient pas de champ « pour ». Or la lecture ne filtre que les
variables qui le déclarent : une variable sans « pour » est lue pour tous les sinistres. La formule
« Privilège » ou la plainte déposée auraient été demandées pour un dégât des eaux chez Foyer, et le banc
Foyer aurait bougé pour une raison sans rapport. Correction générale : une variable acceptée vaut pour les
événements de la garantie qui l'a fait naître (ici vol et vandalisme). Les dix variables déjà ajoutées ont
été complétées, et cinq questions réécrites pour être posables à un assuré (« Serrure à cylindre ? » devient
« Les annexes ou dépendances étaient-elles fermées par une serrure à cylindre ? » ; le séjour temporaire n'est
pas « à l'étranger » : le contrat dit « partout dans le monde »).

**Leçon 71.** Ajouter des règles pour un assureur ne doit pas changer les réponses d'un autre. Le banc Foyer
est le test de cette étanchéité : à relancer après chaque vocabulaire accepté.

### 7.57 AXA accepté ; le banc Foyer bouge à peine, et on ferme quand même la porte

**Acceptation.** Les règles de l'art. 3.1.6 sont ajoutées à `regles/axa-lu-optihome-2017.pl` ; 125 tests
passent sur le poste.

**Banc Foyer après l'ajout d'AXA** (même golden v6, Mistral Small, lecture vérifiée) :

| | Avant AXA (7.50) | Après AXA |
|---|---|---|
| Règles seules | 100 % | 100 % |
| Chaîne : justes | 90 % | 89 % |
| Couverts à tort | 2,33 | 3 |
| Refus à tort | 1,33 | 0,67 |
| Instables | 10 | 9 |
| Un cas à la fois, médiane / 95e centile | 2,9 s / 4,7 s | 2,9 s / 20,3 s |

Les règles Foyer n'ont pas changé (règles seules : 100 %). L'écart de la chaîne est de l'ordre de la
variation entre deux exécutions de Mistral Small (deux cas-exécutions sur 291 pour les couverts à tort). Le
95e centile sur dix cas est une seule question lente : la médiane n'a pas bougé.

**Mais la cause possible était réelle.** Le vocabulaire est commun ; la lecture d'un vol chez Foyer recevait
donc les dix variables d'AXA (plainte, formule « Privilège »…), qu'aucune règle Foyer n'emploie : un prompt
plus long, et des faits à inventer en plus. Correction : chaque contrat ne lit que les variables que ses
règles emploient (`f(variable, …)` relevées dans son fichier, plus le socle événement / bien / lieu). Foyer
lit 29 variables sur 39, AXA 19. C'est aussi ce qui rend le vocabulaire commun extensible sans limite : il
peut grossir avec chaque assureur sans alourdir la lecture des autres.

**Mesure après la correction** (chaque contrat ne lit que ses variables ; moteur encore sans la règle 7.58) :
89 % justes, couverts à tort 2,33 (le niveau d'avant AXA), refus à tort 1, instables 13 ; un cas à la fois,
médiane 3,2 s et 95e centile 4,5 s : la porte de latence passe de nouveau, le 20 s était bien une question lente
isolée. Rien de mesurable n'a donc été cassé par AXA ; la lecture reste la limite (20 décisions changées par
exécution, 13 cas instables), pas les règles.

**Leçon 72.** Un vocabulaire commun pour comparer, une lecture propre à chaque contrat pour décider.

### 7.58 Les cas de test AXA trouvent ce que la relecture n'a pas vu

**Quinze cas de vol AXA**, écrits d'après le texte du contrat (`data/golden/annotations/axa-lu-optihome-2017.jsonl`,
faits idéaux dans `regles/cas/golden/`) : cambriolage, vol simple, plainte absente ou inconnue, agression avec
et sans formule, vol à la tire, mobilier de jardin, cave à cadenas en immeuble, annexe à serrure à cylindre,
voiture, femme de ménage, clés, hôtel à l'étranger, travaux. Limite assumée : je les ai écrits après avoir relu
les règles ; ils ne sont pas indépendants, et restent « à valider par l'auteur » comme ceux de Foyer.

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

**Effet sur Foyer**, mesuré par l'oracle sur les 126 cas Foyer (golden, mise au point, validation) : un seul
change, g2-i06 (gel pendant une absence), de « couvert sous réserve » à « incertain : les mesures contre le gel
étaient-elles prises ? », exactement la réponse attendue par son annotation. Un test unitaire qui figeait
l'ancien comportement est mis à jour, avec la raison.

**Second passage : 15 sur 15.** Un test vérifie désormais, pour chaque contrat du golden set, que les règles
seules donnent la réponse attendue sur les faits idéaux.

**Outils rendus génériques au passage.**
- `--accepter` remplace le bloc d'un article déjà accepté au lieu de l'ajouter une seconde fois ; les
  contrôles d'une proposition ignorent ce bloc (sinon « la garantie existe déjà »).
- L'empreinte du golden set est calculée par contrat, sur ses seules lignes du fichier de sinistres commun :
  ajouter AXA ne « modifie » pas le golden de Foyer, qui reste en v6.

**Leçon 73.** Trois filets, trois sortes d'erreurs : les contrôles attrapent la forme, la relecture attrape le
sens visible, les cas attrapent le sens en action, une exclusion qui en tue une autre. Aucun ne suffit seul.

### 7.59 Premier banc AXA : les règles sont justes, la lecture des nouvelles variables ne l'est pas encore

Golden AXA figé en v7 (15 cas). Banc, Mistral Small, lecture vérifiée, trois exécutions :

| | AXA (15 cas) | Foyer (97 cas, 7.57) |
|---|---|---|
| Règles seules | 100 % justes | 100 % |
| Chaîne : justes | 62 % | 89 % |
| Couverts à tort | **0** | 2,33 |
| Refus à tort | 1,33 | 1 |
| Instables | 3 | 13 |
| Un cas à la fois, médiane / 95e centile | 3,5 s / 5,2 s | 3,2 s / 4,5 s |

Le test différentiel Prolog / oracle passe avec la règle « exclusion entamée » (128 tests sur le poste).

**Où la chaîne perd.** Pas dans les règles : dans la lecture des variables nouvelles, qui n'ont pas encore les
aides par valeur que celles de Foyer ont reçues en trente itérations.
- v14 (hôtel) : `proprietaire = hote` ; le modèle a lu « hôte » comme « hôtel ».
- v10 : « garage séparé de la maison » lu `garage` et non `annexe` ; la tondeuse lue comme véhicule à moteur.
- v09 : « j'habite un appartement » n'est pas compris comme une occupation partielle.
- v02, v03, v08 : la lecture donne la bonne décision, mais la confirmation des faits décisifs suspend la réponse
  (« je ne sais pas ») : c'est le prix, voulu, de zéro couvert à tort.

**Correction : des aides par valeur** pour `proprietaire` (« un hôte, pas un hôtel »), `occupation_partielle`,
`lieu` (garage attenant / annexe séparée), `bien = vehicule_moteur` (pas une tondeuse), `violence` (bousculade,
arrachage / pickpocket). Elles servent aussi à Foyer, dont le banc est à relancer.

**Biais de mesure à corriger plus tard.** Les faits idéaux AXA contiennent des valeurs par défaut que la
déclaration ne dit pas (`auteur = tiers`, `proprietaire = assure`) : le rappel des faits (69 %) est sous-estimé.

**Leçon 74.** Le coût d'un nouvel assureur n'est pas seulement la rédaction des règles : chaque variable nouvelle
doit apprendre à être lue. La rédaction devrait proposer les aides par valeur en même temps que la variable.

### 7.60 Après les aides : Foyer au meilleur niveau mesuré, AXA lit mieux mais suspend encore

| | AXA avant aides | AXA après | Foyer (7.57) | Foyer après |
|---|---|---|---|---|
| Rappel des faits | 69 % | **81 %** | 87 % | 87 % |
| Cas avec contradiction | 4 | 2 | 15 | 17 |
| Chaîne : justes | 62 % | 62 % | 89 % | **90 %** |
| Exactes | 42 % | 47 % | 65 % | 67 % |
| Couverts à tort | 0 | 0 | 2,33 | **1,33** |
| Refus à tort | 1,33 | 1 | 1 | 1 |
| 95e centile, un cas à la fois | 5,2 s | 5,3 s | 4,5 s | **4,1 s** |

Foyer atteint son meilleur niveau de couverts à tort : les aides servent aux deux contrats.

**Ce qui reste sur AXA, cas par cas.**
- v10 : la tondeuse est encore lue comme véhicule à moteur, et l'exclusion « les vols de véhicules
  automoteurs » écartait **tout le sinistre**, vélos compris. Erreur de traduction : elle vise le bien, comme
  « le vol des animaux ». Scindée en deux exclusions de portée bien (véhicule ; remorque hors du bâtiment).
  Troisième passe tracée dans `meta.relecture`. Avec la même lecture, la réponse devient « couvert » (les vélos).
- v06 (pickpocket) : `vol_sur_personne` lu « non » ; v09 (cadenas) : `serrure_surete = non` non lu. Aides
  ajoutées (« pris dans une poche ou un sac que vous portiez » ; « cadenas, simple loquet »).
- v02, v08 : la lecture donne la bonne décision, la confirmation suspend (« je ne sais pas »). C'est le prix
  de zéro couvert à tort ; sur AXA, avec 15 cas, il pèse lourd (2 cas = 13 points).
- v12 : la femme de ménage lue comme `abus_confiance = oui`. Juridiquement défendable ; la réponse reste un
  refus.

**Mesure après la troisième passe** (128 tests sur le poste ; `--controler` avec SWI-Prolog : rien de
bloquant) : AXA **76 % justes** (62 % avant), 56 % exactes, **couverts à tort 0, refus à tort 0**, 1 cas
instable sur 15, une seule contradiction de lecture ; un cas à la fois, médiane 3,3 s et 95e centile 4,7 s.
Deux portes échouent encore : les décisions changées par la lecture (3,67 par exécution, seuil 2) et
l'exactitude de la chaîne (75,5 %, seuil 85 %), l'écart venant surtout des réponses suspendues par la
confirmation. Ces 15 cas ont été écrits par celui qui a relu les règles : la prochaine mesure honnête est
un jeu AXA écrit sans voir les règles.

**Leçon 75.** Sur un contrat neuf, le banc trouve d'abord des erreurs de traduction (portée d'une exclusion),
puis des erreurs de lecture ; les premières se corrigent une fois, les secondes demandent des aides qui
profitent à tous les contrats.

### 7.61 Synthèse du 18 novembre au soir : un deuxième assureur, de zéro règle à 76 %

Ce que la soirée devait montrer : que la méthode tient sur un contrat qu'on n'a pas écrit à la main. La garantie
vol d'AXA Luxembourg (art. 3.1.6 : 8 sous-garanties, 11 exclusions) a été rédigée par Mistral Large, contrôlée par
le code, relue, testée, mesurée. Chaque erreur trouvée a été corrigée **dans la méthode** (consigne, contrôles,
moteur, outils) et pas seulement dans le contrat : la question de l'auteur à mi-parcours, « il faut que ce soit
généralisable, non ? », a fixé la règle.

**La progression d'AXA 3.1.6, étape par étape**

| Étape | Section | Résultat | Correction générale qui en sort |
|---|---|---|---|
| Rédaction 1 (consigne v2) | 7.53 | plantage des contrôles ; puis 16 bloquants, extensions sans exclusions, faits en double | `non_traduit` en phrases toléré ; 4 contrôles nouveaux (exclusions communes, réserves, limites conditionnelles, `plus_proche`) ; vocabulaire donné avec son sens |
| Rédaction 2 (consigne v3), 27 min | 7.54 | fond juste (exclusions communes, vol simple en concept, réserves gardées) ; forme cassée : 9 bloquants | conditions nues remises en forme par le code (pas de reprise de 10 min) ; listes numérotées et citations en double |
| Contrôles rejoués (v4), sans modèle | 7.54 | 20 bloquants, tous des décisions humaines (18 faits nouveaux, 2 non traduits) | — |
| Relecture humaine, ~20 min à deux | 7.55 | 18 faits proposés → 11 gardés ; conflit tire / agression corrigé ; question métier posée (jardin) | champ `hors_decision` |
| Vocabulaire accepté | 7.56 | 0 bloquant ; règles chargées par SWI-Prolog | une variable acceptée ne vaut que pour les événements de sa garantie (« pour ») |
| Règles acceptées ; banc Foyer | 7.57 | Foyer inchangé dans la marge | chaque contrat ne lit que les variables de ses règles |
| 15 cas AXA, règles seules | 7.58 | **11 / 15**, puis **15 / 15** | consigne v5 (« à l'extérieur ») ; moteur : exclusion **entamée** = question (améliore aussi Foyer, g2-i06) ; `--accepter` remplace ; golden par contrat |
| Premier banc AXA | 7.59 | 62 % justes, 0 couvert à tort | aides par valeur des variables nouvelles |
| Banc après les aides | 7.60 | 62 % (lecture 69 → 81 %) | exclusion « véhicules » limitée au bien ; aides vol sur la personne, serrure de sûreté |
| Banc final | 7.60 | **76 % justes, 0 couvert à tort, 0 refus à tort**, 1 instable ; 95e centile 4,7 s | — |

**Le banc AXA, dans le temps** (15 cas, Mistral Small, lecture vérifiée, 3 exécutions)

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

**Foyer pendant ce temps** (97 cas) : rien n'a été cassé, et les corrections générales l'ont amélioré.

| | Avant AXA (17 h 10) | AXA accepté (21 h 59) | Lecture par contrat (22 h 13) | Aides (22 h 31) |
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

**Ce que ces chiffres ne disent pas.** Les 15 cas AXA ont été écrits par Claude après avoir relu les règles :
ils mesurent la cohérence, pas la justesse face à un sinistre réel. Sur 15 cas, un cas pèse 6,7 points.

### 7.62 Toutes les garanties : Foyer d'abord, AXA ensuite, et deux outils avant de commencer

Objectif fixé par l'auteur le 18 au soir : traduire **toutes** les garanties de Foyer, puis toutes celles d'AXA,
avec la chaîne mise au point sur AXA 3.1.6 (rédaction, contrôles, relecture, cas, banc).

**L'inventaire Foyer.** Déjà traduits : incendie (2.1), dégâts des eaux (2.7), bris de vitrages (2.9, rédigé par
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
  elles, le premier banc AXA avait perdu 14 points de lecture. Une variable nouvelle sans aide est « à relire ».

### 7.63 Foyer, lot A : sept garanties rédigées en 19 minutes, relues, acceptées

**La rédaction.** Onze articles (lots A et B) rédigés par Mistral Large, trois à la fois : **19 minutes** en tout
(une seule garantie AXA en avait pris 27 la veille, seule). Aucun plantage, aucune condition nue. La consigne v6
a tenu : chaque variable nouvelle est venue avec ses aides de lecture et sa voisine la plus proche.

**Le défaut de la rédaction en parallèle : le vocabulaire.** Chaque proposition ignore les autres. Le même fait
est arrivé sous plusieurs noms : « à l'extérieur » trois fois (`a_l_exterieur`, `situe_exterieur`,
`lieu = exterieur`), les constructions délabrées et le logement principal deux fois (2.2 et 2.3), le contrôle des
citernes deux fois (2.5 et 2.8), les matériaux à pied d'œuvre en variable (2.2) et en bien (2.11). Harmonisé à la
relecture (`relecture/foyer_lot_a.py`, tracé dans `meta.relecture` de chaque proposition) : 95 faits proposés pour
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

**Règles seules (oracle), Foyer, 97 cas : 100 % justes, 0 couvert à tort, 0 refus à tort, 92 % exactes (87 %
avant le lot A)** : des « incertain » de cas hors règles deviennent des réponses fermes justes (denrées décongelées,
fioul, tags sur la porte). AXA inchangé (100 %).

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

Banc Foyer, golden v8, Mistral Small (sur le poste, 128 tests et `--controler` sans rien de bloquant) :

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

### 7.65 AXA, lot A : huit garanties rédigées en 21 minutes, relues, acceptées

Incendie et périls assimilés (3.1.1, sept garanties : incendie, décongélation, linge, heurt, dégradations
immobilières à l'occasion d'un vol, vandalisme, attentats), tempête et grêle (3.1.2), dégâts électriques (3.1.3),
dégâts des eaux (3.1.4), bris de vitrages (3.1.5), matériel multimédia (3.1.7, bris et vol), tremblement de terre
(3.2.1), pluies et inondations (3.2.2). Relecture : `relecture/axa_lot_a.py`, tracée dans chaque proposition.

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
  `catastrophe_naturelle` (comme Foyer) et une variable `catastrophe`. Les dommages dans les 72 heures : à
  l'assureur de l'établir.

**Deux corrections générales.**
- Les événements de lecture d'une variable sont calculés **garantie par garantie** (`evenements_par_variable`) :
  3.1.1 réunit sept garanties d'événements différents, et les flammes se retrouvaient à lire pour un vol.
- Une réserve d'option combinée à l'événement (« vol et option vol inconnue ») est *entamée* dès que l'événement
  est établi (règle 7.58) et pose la question : la réserve se pose sur la seule garantie concernée, sans
  l'événement.

**Vérifications.** Golden AXA (oracle) : 100 % justes, 0 couvert ni refus à tort. axa-v07 (téléphone arraché
dans la rue, formule inconnue) devient « couvert » par 3.1.7 : conforme au contrat, sous réserve des options
multimédia et vol ; annotation complétée, golden **v9**. Seize cas de contrôle sur les nouvelles garanties
(incendie, explosion, tempête à 100 km/h, grêle, vent de force inconnue, fuite, pluie par une fenêtre ouverte,
vitre, lunettes, téléphone tombé ou volé dans une voiture, séisme, inondation, surtension, voiture contre le mur) :
réponses conformes au texte, les options en réserve.

**Leçon 79.** Un contrat qui découpe ses garanties en options (« si les conditions particulières le
mentionnent ») ne se lit pas comme un contrat tout compris : l'option est une réserve, jamais une question posée
au déclarant, qui ne la connaît pas.

### 7.66 Foyer après les rattachements : 5 couverts à tort, tous des erreurs de lecture confirmées

Banc Foyer (golden v8, sur le poste, 128 tests) : règles seules 100 % (91 % exactes) ; chaîne 89 % justes,
73 % exactes, **5 couverts à tort**, 0,67 refus à tort, 14 instables ; un cas à la fois, 95e centile 4,2 s.
(Le vocabulaire d'AXA a été déposé pendant ce banc : la mesure est à refaire, mais les cas parlent.)

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

## 8. Ce qui reste à faire

Tenu à jour le 18 nov. 2026, 22 h 40 ; ce qui est fait est dans les sections 7.

**Le plan de lecture (7.35)**
- La lecture vérifiée est la lecture par défaut (7.45). Mesurer Mistral Large avec elle, pour le recours dans la cascade.
- Le recours à Mistral Large pour les seuls cas douteux (faits retirés par la vérification, ou « couvert » sur un fait vérifié de justesse).
- La porte de latence passe (4,7 s pour 10) : la resserrer, par exemple à 8 s.
- Les erreurs restantes (7.50) : la clé sous le paillasson (cohérence), les oublis (demander, avant de couvrir, si une exclusion présumée absente est évoquée).
- Étape 2 : double lecture en parallèle comparée par le code, et recours à Mistral Large quand elles divergent ou que la réponse est « couvert ».

**La mesure honnête**
- Le **jeu fermé**, écrit par l'auteur sans voir les règles (`data/ferme/`, au moins 20 cas, avec des « incertain »).
- **Valider le golden set** (`data/golden/A_VALIDER.md`), en particulier la toiture et les clés.
- LegalBench avec Mistral Large ; et, plus tard, des règles rédigées pour quelques clauses.

**Le passage à l'échelle**
- Traduire les garanties restantes de Foyer (tempête 2.2, électricité 2.6, mazout 2.8, responsabilité de l'immeuble 2.5, dégradations 2.11, mérule 2.12) avec la rédaction par Mistral Large, consigne v5.
- AXA : la garantie vol est faite (7.53 à 7.61). Suite : un **jeu AXA écrit par l'auteur sans voir les règles** ; puis les autres garanties (incendie, dégâts des eaux…) ; la **question métier** du vol simple au jardin (7.55) à poser à un souscripteur.
- Faire **proposer les aides par valeur** par la rédaction, en même temps que chaque variable nouvelle (leçon 74).
- Contrôle mécanique à écrire : aucune exclusion commune ne doit rendre une extension impossible (leçon 70) ; le moteur peut le vérifier en prenant le périmètre de chaque garantie comme faits.
- Le coût de la confirmation sur AXA (deux réponses justes suspendues sur 15) : mesurer si la confirmation peut épargner les faits que la lecture et la vérification donnent tous deux.
- Faits idéaux AXA : retirer les valeurs par défaut que la déclaration ne dit pas (`auteur = tiers`, `proprietaire = assure`), qui sous-estiment le rappel.

**Le reste**
- Les 43 vulnérabilités signalées par GitHub (la mise à jour du verrou n'en a pas réduit le nombre : lire la liste).
- Limites connues : la perte de clés (sans vol) n'est pas traduite ; la responsabilité civile (section 5) est typée « autre » par le découpage ; les conditions particulières ne sont pas lues.

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
68. Un « à vérifier » se lit avant de se corriger : la moitié des alertes d'AXA venaient de deux limites générales du découpage, pas du contrat.
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
79. Une garantie optionnelle (« si les conditions particulières le mentionnent ») est une réserve, jamais une question au déclarant.
