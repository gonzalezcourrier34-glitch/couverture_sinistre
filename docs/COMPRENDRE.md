# Comprendre le projet : une expérience en deux hypothèses

J'ai mené ce projet comme une expérience. Je suis parti d'une question, j'ai posé une première hypothèse, je l'ai construite et mesurée. La mesure l'a en partie réfutée. J'en ai tiré une seconde hypothèse, que j'ai mesurée à son tour contre la première, sur des cas que ni l'une ni l'autre n'avait jamais vus. Ce texte raconte ce cheminement sans demander de connaissance préalable, ni en assurance ni en intelligence artificielle. Les détails techniques sont ailleurs : [les explications](EXPLICATIONS.md) décrivent chaque fichier, [la démarche](DEMARCHE.md) garde chaque essai et sa mesure, dans l'ordre où je les ai faits, y compris les fois où la mesure m'a donné tort.

## 1. La question

Quelqu'un rentre chez lui et trouve sa cave forcée, son vélo disparu. Il écrit à son assureur : « Mon vélo a été volé dans ma cave. » De l'autre côté, un gestionnaire doit répondre à une seule question : **le contrat couvre-t-il ce sinistre ?**

Pour répondre, il ouvre les « conditions générales », un document de 50 à 100 pages. Il y cherche la garantie vol, lit ce qu'elle couvre, puis ce qu'elle exclut, puis le lexique, parce que le contrat donne aux mots un sens précis (une « serrure de sûreté » n'est pas un cadenas). C'est long, et une erreur coûte cher dans les deux sens.

La question de recherche que je me suis posée : **un système peut-il faire ce travail avec le gestionnaire, de façon vérifiable ?** On lui donne une déclaration écrite comme on parle ; il doit rendre :

- **la réponse** : couvert, non couvert, ou « à préciser » ;
- **la preuve** : la phrase exacte du contrat sur laquelle la réponse s'appuie, avec son numéro d'article ;
- **la question à poser**, quand la déclaration ne dit pas tout ce qu'il faut savoir.

Avant d'écrire une ligne de code, j'ai fixé comment je jugerais les résultats, parce que les erreurs ne se valent pas. **« Couvert » à tort** est la plus grave : c'est une promesse faite au client, et un paiement que le contrat ne prévoit pas. **Le refus à tort** est grave aussi. **« À préciser » à la place d'une réponse** est l'erreur la moins chère : elle coûte une question de plus. Toutes les comparaisons qui suivent se lisent avec ce classement.

## 2. Pourquoi la question est difficile

Mon projet précédent, SortirIA, est un assistant de sorties pour Montpellier : on lui écrit « un concert gratuit ce week-end à Sète », il propose des sorties qui respectent la date, le lieu et le budget. Les deux projets se ressemblent en apparence : une phrase en entrée, une réponse en sortie, un modèle de langage au milieu. Ils diffèrent sur quatre points, et ce sont eux qui ont orienté toute ma conception.

| | SortirIA | Ce projet |
|---|---|---|
| Ce que fait le système | Il **recommande** | Il **décide** |
| Une réponse imparfaite | Reste utile : un concert un peu loin est encore une idée | Est une faute : « couvert » à tort est une promesse faite au client |
| Ce qu'il lit | Des fiches de sorties, courtes, ramenées à un même modèle | Des contrats de 50 à 100 pages, chacun écrit à sa façon |
| Ce qu'on attend de lui | Une bonne suggestion | Une réponse qu'on peut **vérifier** ligne à ligne |

J'ai identifié trois difficultés qui n'existaient pas dans SortirIA.

**La phrase qui décide ne ressemble pas à la question.** Pour un vélo volé dans le hall de l'immeuble, la réponse tient dans une exclusion qui parle de « parties communes du bâtiment ». Le mot « vélo » n'y est pas, le mot « hall » non plus. Chercher les passages qui ressemblent à la question ne suffit pas.

**Un contrat est fait d'exceptions d'exceptions.** Une garantie couvre le vol ; une exclusion retire le vol sans effraction ; une option rachète cette exclusion pour certains biens ; une obligation (fermer à clé) peut faire tout perdre. Il faut appliquer ces règles dans le bon ordre, sans en oublier une.

**« Je ne sais pas » doit rester « je ne sais pas ».** Si la déclaration ne dit pas comment la cave était fermée, on ne peut ni couvrir ni refuser. Deviner est interdit.

Le premier essai, le plus simple, a été de donner le contrat et la déclaration à un modèle de langage et de lui demander la réponse. Il répondait avec assurance, souvent juste, et parfois faux sans que rien ne le signale. Surtout, je ne pouvais pas vérifier son raisonnement : il ne le montre pas, il le raconte après coup. J'ai écarté cette voie, et posé trois garde-fous que mes deux hypothèses respectent :

1. **Pas de réponse sans preuve.** Chaque phrase citée est recherchée mot pour mot par le code ; une citation qui n'existe pas fait écarter ce qu'elle devait prouver.
2. **Un doute ne fait jamais couvrir.** Tant qu'un fait décisif manque, la réponse est « à préciser », avec la question.
3. **Le code tranche, pas le modèle.** La décision finale sort d'une logique écrite à l'avance, qui donne toujours la même réponse aux mêmes entrées.

## 3. Première hypothèse : « le modèle lit, la logique décide »

**L'hypothèse.** Si je traduis chaque contrat, une fois pour toutes, en règles qu'un programme sait appliquer, le modèle n'a plus qu'à transformer la déclaration en faits. La décision devient un calcul : reproductible, et traçable jusqu'à la phrase du contrat.

**Ce que j'ai construit.**

- *Découper.* Le programme lit le PDF, retire ce qui gêne (en-têtes, numéros de page, sommaire) et découpe le texte en clauses : une garantie, une exclusion, une définition du lexique, chacune avec son numéro d'article. Pour le premier contrat, 48 pages deviennent 147 clauses.
- *Traduire en règles.* Chaque garantie est réécrite dans un langage fait pour le raisonnement (Prolog) : son périmètre, ses conditions, ses obligations, ses exclusions, ses limites, chacune avec la phrase du contrat qu'elle traduit. Un modèle (Mistral Large) propose la traduction ; le code la contrôle ; je relis.
- *Un vocabulaire.* Pour que règles et déclarations se rencontrent, une liste fermée d'environ 250 faits possibles (l'événement, le bien, le lieu, la façon dont le local était fermé…), chacun avec la question à poser s'il manque.

Pour un sinistre, l'analyse prend quelques secondes. Sur le vélo dans la cave « fermée par un cadenas » : Mistral Medium traduit la phrase en faits (vol, vélo, cave, cadenas) ; Mistral Small vérifie chaque fait et retire ce que la déclaration ne dit pas ; le moteur applique les règles du contrat. La garantie vol pose une condition, « si ces locaux sont fermés avec une serrure de sûreté », et le lexique dit qu'un cadenas n'en est pas une : **non couvert**. Sans les mots « fermée par un cadenas », le moteur ne sait pas : **à préciser**, avec la question « Comment le local était-il fermé ? ». L'écran montre l'« arbre de preuve » : chaque condition examinée, sa phrase du contrat, et le fait qui l'a rendue vraie, fausse ou inconnue.

J'ai préparé quatre contrats de quatre assureurs, rendus anonymes (A, B, C, D). A et B sont traduits en entier ; C et D seulement en partie, volontairement : ils m'ont servi à mesurer ce que coûte un contrat de plus.

**Ce que la mesure a dit.** Sur les jeux de cas qui m'avaient servi à régler les règles, les résultats étaient excellents : 90 à 100 % de réponses justes, sans couvert à tort. Je m'en suis méfié, parce que je les avais sous les yeux en réglant. J'ai donc fait écrire des jeux de déclarations par des annotateurs qui n'avaient lu que le texte des contrats, sans voir mes règles, et je les ai mesurés une seule fois. Le premier de ces jeux a fait tomber les chiffres (95 % sur A, 58 % sur B, 78 % sur D, avec des couverts à tort). J'ai corrigé ce qu'il montrait, puis mesuré le suivant, « neuf », écrit après ces corrections : il a donné 38 réponses justes sur 60 et **7 couverts à tort**.

**Ce que j'en ai conclu.** L'hypothèse tenait sur un point : le système ne répondait jamais sans preuve. Elle échouait sur un autre : la preuve était celle de la règle, et une règle peut mal traduire le contrat. Une exclusion oubliée à la traduction, un mot que le vocabulaire ne connaît pas, et la décision est fausse, avec une citation exacte à l'appui. Des corrections qui ne font pas monter un jeu neuf désignent la méthode, pas une liste de règles.

## 4. Seconde hypothèse : « le modèle juge chaque clause, la logique tranche, les règles contresignent »

**L'hypothèse.** Si le modèle lit le texte même du contrat, une clause que la traduction a manquée peut encore être vue. Pour ne pas retomber dans le piège du début (un modèle qui décide sans qu'on puisse le vérifier), je ne lui pose jamais la question « est-ce couvert ? » : je lui fais juger les clauses une à une, je vérifie chaque citation, et je calcule la décision. Et je garde la première méthode comme contre-pouvoir : un « couvert » n'est rendu que si elle le dit aussi.

**Ce que j'ai construit.** Pour un sinistre, l'analyse prend deux à trois minutes, et l'écran en montre chaque étape.

1. **Désigner.** Mistral Large lit la table des chapitres du contrat et désigne ceux qui concernent le sinistre.
2. **Composer le dossier.** Le code, pas le modèle, y ajoute ce qui vaut pour tout le contrat : exclusions générales, obligations, définitions. De 70 à près de 300 clauses selon le contrat et le sinistre. J'ai écrit d'avance, pour chaque garantie, la liste des clauses qu'un gestionnaire doit relire : je peux ainsi constater qu'une clause n'a pas été jugée.
3. **Juger chaque clause.** Mistral Large rend pour chacune un effet (couvre, exclut, limite, à vérifier, sans effet), avec la phrase du contrat et celle de la déclaration. Une clause oubliée lui est redemandée une fois.
4. **Vérifier.** Le code retrouve chaque citation mot pour mot ; un jugement mal cité est écarté.
5. **Trancher.** Une exclusion citée l'emporte ; un point à vérifier donne « à préciser » ; une garantie qui couvre, sans exclusion, donne « couvert ».
6. **Contresigner.** Si la lecture conclut « couvert » et que les règles ne le disent pas, la réponse devient « à préciser ».

**Ce que cette hypothèse change, et que je dois assumer.** Dans la première, le modèle ne voyait que la déclaration et ne décidait de rien. Dans la seconde, il voit le contrat et porte un jugement sur chaque clause. C'est plus de pouvoir donné au modèle. Mes garde-fous le bornent, mais l'un d'eux a une faiblesse que je n'avais pas anticipée : le code vérifie qu'une citation existe, pas qu'elle a un rapport avec le sinistre.

**Une hypothèse annexe, non vérifiée.** Pour juger, la seconde méthode n'a besoin ni de règles ni de vocabulaire : en principe, elle s'appliquerait à un contrat nouveau sans le travail de traduction. Mais dans toutes mes mesures, les règles de la première méthode ont servi de contresignature. Sur un contrat sans règles traduites, ce mode-là n'a jamais été mesuré. Je le tiens pour une promesse, pas pour un résultat.

## 5. Le protocole de comparaison

Pour comparer honnêtement les deux hypothèses, il me fallait des cas qu'aucune des deux n'avait vus. J'ai fait écrire un quatrième jeu, « quatre » : soixante déclarations, vingt par contrat (A, B, D), par un annotateur qui n'avait lu que les contrats. Deux autres annotateurs ont donné leur réponse sans voir la sienne : Mistral Large, et Claude, l'assistant avec lequel j'ai construit le projet. Le second avis de Mistral ne suffisait pas : la seconde méthode lit avec Mistral Large, et un jeu annoté par le modèle qu'on mesure le favoriserait s'ils se trompaient de la même façon. Les trois avis concordent sur les soixante cas.

Les règles du protocole, fixées avant la mesure :

- le code des deux méthodes est figé et enregistré avant ;
- le jeu est passé une seule fois, la première méthode trois fois (elle est rapide, et sa lecture varie un peu), la seconde une fois (elle coûte environ 8 centimes par cas) ;
- les chiffres sont écrits tels quels, et rien n'est corrigé ensuite : un tour de corrections demanderait un cinquième jeu.

**Un cinquième jeu, pour le dernier tour.** Après cette mesure, j'ai fait un tour de corrections de la seconde méthode, en règles générales seulement, contrôlées sur les jeux déjà vus. Ces contrôles flattent forcément ce qu'on vient de corriger : il fallait un jeu neuf. Le jeu « cinq » a été monté de la même façon, soixante déclarations jamais vues, avec une différence : le second avis vient de trois autres instances de Claude, et plus du tout de Mistral Large. Les deux avis concordent sur cinquante-neuf cas ; le soixantième a été arbitré sur le texte par une septième instance. Code figé, une seule passe, chiffres tels quels.

Un incident, au jeu « quatre » : pendant la mesure, Mistral a répondu par une panne sur un cas, et mon outil de mesure s'est arrêté au lieu de passer au cas suivant. J'ai passé les deux cas restants le lendemain matin, avec le même code, sans avoir vu de réponse pour eux. Je l'ai noté, et corrigé l'outil après la mesure.

## 6. Les résultats

**La mesure finale, sur le jeu « cinq »** (26 novembre, après le dernier tour de corrections) :

| Jeu « cinq », 60 cas jamais vus | Première méthode (règles, 3 passages) | Seconde méthode (clauses, 1 passage) |
|---|---|---|
| A | 15,7 sur 20 | 20 sur 20 |
| B | 14,3 sur 20 | 19 sur 20 |
| D | 10,3 sur 20 | 14 sur 20 |
| **Réponses justes** | **40,3 sur 60** | **53 sur 60** |
| **Couverts à tort** | **4,7** | **0** |
| Refus à tort | 6 | 1 |
| « À préciser » au lieu d'une réponse | 9 | 6 |
| Durée d'une analyse | 3,5 à 5,2 s (médiane) | 177 s (médiane ; 71 à 366 s) |

Le seul refus à tort : des clés volées dans un sac au café ; on demandait le changement des serrures, la seconde méthode a appliqué l'exclusion des vols à la tire hors du domicile. Les six « à préciser » sont tous chez D : la lecture couvre à raison, les règles de D (traduites en partie) ne suivent pas, et la contresignature tire la réponse vers le doute.

**La première mesure, sur le jeu « quatre »** (25 novembre au soir) :

| Jeu « quatre », 60 cas jamais vus | Première méthode (règles) | Seconde méthode (clauses) |
|---|---|---|
| Réponses justes | 42 sur 60 (moyenne de trois passages) | 45 sur 60 (un passage) |
| — contrat A | 12,3 sur 20 | 16 sur 20 |
| — contrat B | 16,7 sur 20 | 16 sur 20 |
| — contrat D | 13 sur 20 | 13 sur 20 |
| **Couverts à tort** | **4,3** | **1** |
| Refus à tort | 2 | 4 |
| « À préciser » au lieu d'une réponse | 8,7 | 10 |
| Durée d'une analyse | 3 à 6 secondes | 2 à 3 minutes |
| Coût d'une analyse | bien moindre (petits modèles, peu de texte envoyé) | 8 à 10 centimes de dollar |

**Quatre cas où les deux méthodes divergent** (contrat A) :

- *Le casier du club de tennis forcé* (on attendait « non couvert »). La première méthode répond « à préciser » les trois fois. La seconde trouve l'exclusion et la cite : « le vol du contenu entreposé dans un casier d'une association sportive ou d'agrément ». **Non couvert, juste.** C'est exactement le gain que j'espérais : une clause lue dans le texte.
- *Le store banne arraché par la tempête* (on attendait « non couvert »). La première méthode le déclare couvert deux fois sur trois : l'erreur grave. La seconde trouve l'exclusion des objets situés à l'extérieur, mais pose aussi une question (propriétaire ou locataire ?) et répond « à préciser ». **Pas juste, mais l'erreur grave est évitée.**
- *L'eau d'une gouttière voisine entrée par une fenêtre* (on attendait « couvert »). La première méthode refuse les trois fois. La seconde trouve la garantie, mais la contresignature voit le refus des règles et rend « à préciser ». **Mon contre-pouvoir a un prix : l'erreur de la première méthode tire la seconde vers le doute.**
- *Un dégât des eaux après le gel* (on attendait « à préciser »). La première méthode répond juste. La seconde cite une clause d'obligations hors de propos et refuse. **Ici, c'est la seconde qui se trompe, dans un sens grave**, et ma contresignature ne l'arrête pas : je ne l'ai prévue que pour les « couvert ».

## 7. Discussion : ce que je retiens, ce que je ne peux pas affirmer

**Sur le jeu « quatre », je ne pouvais pas affirmer que la seconde méthode était plus juste.** Trois réponses de plus sur soixante, c'est un écart que ce jeu ne permet pas de distinguer du hasard. Sur le jeu « neuf », l'écart était de 48 contre 38 ; mais ce jeu m'avait servi à mettre la seconde méthode au point, et l'écart a fondu sur des cas neufs. C'est la leçon de méthode que je retiens le plus : un jeu qui a servi à corriger flatte toujours ce qu'on a corrigé.

**Sur le jeu « cinq », l'écart est net** : treize réponses justes de plus (53 contre 40), dans le même sens sur les trois contrats. Soixante cas restent peu, et deux jeux différents ne se comparent pas au point près ; mais la première méthode, à peu près inchangée entre les deux jeux, ne trouve pas celui-ci plus facile (40 contre 42). J'en conclus, avec cette prudence, que le dernier tour de corrections a servi.

**Je peux affirmer qu'elle se trompe moins gravement.** Un couvert à tort au lieu de plus de quatre au jeu « quatre », aucun au lieu de 4,7 au jeu « cinq », dans le sens qui coûte le plus. C'est cohérent avec l'hypothèse : la plupart des couverts à tort de la première méthode venaient d'une traduction incomplète, et la seconde lit le texte.

**Je dois reconnaître ce qu'elle coûte.** Deux à trois minutes d'attente et un coût nettement plus élevé. Au jeu « quatre », deux refus à tort de plus ; au jeu « cinq », un seul refus à tort, contre six pour la première méthode. Et dans les deux jeux, six écarts viennent de la contresignature elle-même : la lecture couvrait à raison, les règles se trompaient. Mon contre-pouvoir hérite des défauts de ce qu'il contresigne, surtout chez D, dont les règles ne sont traduites qu'en partie.

| | Première méthode (règles) | Seconde méthode (clauses) |
|---|---|---|
| Ce que voit le modèle | La déclaration seule | La déclaration et les clauses du contrat |
| Qui décide | Un moteur, sur des règles traduites | Une logique fixe, sur des jugements cités, contresignée par les règles |
| Travail par contrat | Découpage, traduction, vocabulaire, relecture humaine | Découpage ; les règles restent utiles pour la contresignature |
| Où elle se trompe | À la traduction : une règle fausse, un fait absent du vocabulaire | À la lecture : une clause mal jugée, une citation exacte mais hors de propos |
| Le raisonnement montré | Un arbre de preuve, condition par condition | Le jugement de chaque clause, avec ses deux citations |
| Même réponse deux fois ? | Presque : 2 à 3 cas sur 20 changent d'un passage à l'autre | Pas garanti : le modèle juge, et peut juger autrement |
| Durée, coût | Quelques secondes, très peu | 2 à 3 minutes, 8 à 10 centimes |

## 8. Ma décision, et ce qu'elle ne règle pas

**J'ai fait de la seconde méthode la méthode par défaut.** Le critère vient du §1 : à justesse comparable, je préfère le système qui promet le moins souvent à tort. La première reste dans le code, et l'écran dit laquelle a répondu. Avant de la mettre en ligne, j'ai vérifié que l'hébergeur laisse une requête durer plusieurs minutes (279 secondes ont tenu), et j'ai réduit le nombre d'analyses permises par jour, puisque chacune coûte maintenant 8 à 10 centimes.

**Ce qui reste vrai pour les deux méthodes.**

- **Les bonnes réponses n'ont pas été relues par un juriste.** Trois annotateurs automatiques concordent : cela dit que les cas ne sont pas ambigus pour qui lit le contrat, pas qu'un professionnel les validerait tous. C'est la prochaine étape avant tout usage réel.
- **Les jeux de test sont petits.** Vingt cas par contrat : un écart de deux ou trois réponses ne veut rien dire.
- **Ce n'est pas un service en production.** Il n'a pas d'utilisateurs réels.
- **Il ne dit rien du montant.** Il répond à « est-ce couvert ? », pas à « combien ? ».

**Les prochaines expériences, dans l'ordre.**

1. Mesurer la seconde méthode sans contresignature, sur un contrat sans règles traduites, avec un jeu neuf : c'est la condition pour dire qu'elle s'étend à un contrat nouveau. Le jeu « cinq » le suggère sans le prouver : chez D, les six réponses retenues par la contresignature étaient justes.
2. Faire contresigner seulement par des règles complètes : un contrat traduit en partie retient des « couvert » justes plus souvent qu'il n'arrête une erreur.
3. Réduire l'attente, en profitant davantage du cache du fournisseur.

J'ai essayé, puis retiré, de faire relire les refus par le modèle : il doutait de refus justes plus souvent qu'il ne corrigeait de refus à tort. Chacune de ces pistes demandera un jeu de cas neuf : « cinq » a servi.

## 9. En une phrase

J'ai d'abord traduit les contrats en règles et laissé un programme décider : c'était rapide et transparent, mais faux dès que la traduction l'était. J'ai alors fait lire au modèle les clauses mêmes, vérifié chacune de ses citations et fait contresigner ses « couvert » par la première méthode : sur des cas jamais vus, il promet à tort beaucoup moins souvent (aucune fois au dernier jeu), répond juste plus souvent après un dernier tour de corrections (53 sur 60 contre 40), au prix de deux à trois minutes d'attente.
