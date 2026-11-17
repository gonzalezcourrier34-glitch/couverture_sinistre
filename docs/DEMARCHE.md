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

## 8. Ce qui reste à faire

- Expliquer la régression de velo-02, puis comparer avec `conditions`.
- Valider les 14 réponses attendues sur Foyer (proposées, pas encore validées).
- Construire le **vocabulaire de faits commun** à partir des conditions de Foyer, puis traduire les
  garanties en **règles Prolog** à trois issues (couvert, non couvert, incertain), en commençant par
  la garantie vol.
- Limite connue : la responsabilité civile de Foyer (section 5) est typée « autre » par le découpage.

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
