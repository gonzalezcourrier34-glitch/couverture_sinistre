# Comprendre le projet : deux façons de lire un contrat, comparées

Ce texte raconte le projet sans demander aucune connaissance préalable, ni en assurance ni en intelligence artificielle. Le projet a connu deux méthodes. La première traduit chaque contrat en règles et laisse un programme décider. La seconde fait lire au modèle les clauses mêmes du contrat, une par une. Ce texte les compare, chiffres à l'appui, et dit pourquoi la seconde est devenue la méthode par défaut et ce qu'elle ne règle pas. Les détails techniques sont ailleurs : [les explications](EXPLICATIONS.md) décrivent chaque fichier, [la démarche](DEMARCHE.md) garde chaque essai et sa mesure.

## 1. L'objectif

Quelqu'un rentre chez lui et trouve sa cave forcée, son vélo disparu. Il écrit à son assureur : « Mon vélo a été volé dans ma cave. » De l'autre côté, un gestionnaire doit répondre à une seule question : **le contrat couvre-t-il ce sinistre ?**

Pour répondre, il ouvre les « conditions générales », un document de 50 à 100 pages. Il y cherche la garantie vol, lit ce qu'elle couvre, puis ce qu'elle exclut, puis le lexique, parce que le contrat donne aux mots un sens précis (une « serrure de sûreté » n'est pas un cadenas). C'est long, et une erreur coûte cher dans les deux sens : promettre un remboursement que le contrat ne prévoit pas, ou refuser à tort.

Le projet fait ce travail avec lui. On lui donne une déclaration écrite comme on parle, il rend trois choses :

- **la réponse** : couvert, non couvert, ou « à préciser » ;
- **la preuve** : la phrase exacte du contrat sur laquelle la réponse s'appuie, avec son numéro d'article ;
- **la question à poser**, quand la déclaration ne dit pas tout ce qu'il faut savoir.

La troisième réponse est aussi importante que les deux autres. Un outil qui répond toujours quelque chose est dangereux ; un outil qui sait dire « je ne peux pas trancher, demandez-lui si la cave était fermée à clé » est utile.

Les erreurs ne se valent pas. **« Couvert » à tort** est la plus grave : c'est une promesse faite au client, et un paiement que le contrat ne prévoit pas. **Le refus à tort** est grave aussi. **« À préciser » à la place d'une réponse** est l'erreur la moins chère : elle coûte une question de plus. Toute la comparaison qui suit se lit avec ce classement en tête.

## 2. Pourquoi c'est plus difficile que SortirIA

Mon projet précédent, SortirIA, est un assistant de sorties pour Montpellier : on lui écrit « un concert gratuit ce week-end à Sète », il propose des sorties qui respectent la date, le lieu et le budget. Les deux projets se ressemblent en apparence : une phrase en entrée, une réponse en sortie, un modèle de langage au milieu. Ils diffèrent sur quatre points, et ce sont eux qui ont décidé de toute la conception.

| | SortirIA | Ce projet |
|---|---|---|
| Ce que fait le système | Il **recommande** | Il **décide** |
| Une réponse imparfaite | Reste utile : un concert un peu loin est encore une idée | Est une faute : « couvert » à tort est une promesse faite au client |
| Ce qu'il lit | Des fiches de sorties, courtes, ramenées à un même modèle | Des contrats de 50 à 100 pages, chacun écrit à sa façon |
| Ce qu'on attend de lui | Une bonne suggestion | Une réponse qu'on peut **vérifier** ligne à ligne |

Trois difficultés n'existaient pas dans SortirIA.

**La phrase qui décide ne ressemble pas à la question.** Pour un vélo volé dans le hall de l'immeuble, la réponse tient dans une exclusion qui parle de « parties communes du bâtiment ». Le mot « vélo » n'y est pas, le mot « hall » non plus. Chercher les passages qui ressemblent à la question ne suffit pas.

**Un contrat est fait d'exceptions d'exceptions.** Une garantie couvre le vol ; une exclusion retire le vol sans effraction ; une option rachète cette exclusion pour certains biens ; une obligation (fermer à clé) peut faire tout perdre. Il faut appliquer ces règles dans le bon ordre, sans en oublier une.

**« Je ne sais pas » doit rester « je ne sais pas ».** Si la déclaration ne dit pas comment la cave était fermée, on ne peut ni couvrir ni refuser. Deviner est interdit.

## 3. Deux réponses au même problème

La solution la plus simple serait de donner le contrat et la déclaration à un modèle de langage et de lui demander la réponse. Je l'ai essayé au début. Le modèle répond avec assurance, souvent juste, et parfois faux sans que rien ne le signale. Surtout, on ne peut pas vérifier son raisonnement : il ne le montre pas, il le raconte après coup. Les deux méthodes du projet sont deux manières d'éviter ce piège.

**Première méthode : « le modèle lit, la logique décide ».** Chaque contrat est traduit à l'avance en règles, dans un langage fait pour le raisonnement (Prolog). Pour un sinistre, le modèle ne fait que transformer la déclaration en faits (« vol », « vélo », « cave », « cadenas ») ; un programme applique les règles à ces faits. Le modèle ne voit jamais le contrat, et il ne décide de rien.

**Seconde méthode : « le modèle juge chaque clause, la logique tranche, les règles contresignent ».** Pour un sinistre, le modèle lit les clauses du contrat qui le concernent et rend, clause par clause, un jugement cité : cette garantie couvre, cette exclusion exclut, cette clause demande une précision. Un programme tranche à partir de ces jugements, selon une logique fixe. Puis la première méthode, qui tourne en parallèle, contresigne : un « couvert » n'est rendu que si elle dit « couvert » aussi.

Ce qui change au fond tient en une phrase : **dans la première méthode, le modèle ne voit que la déclaration ; dans la seconde, il voit aussi le texte du contrat, et il porte un jugement sur chaque clause.** C'est plus de pouvoir donné au modèle. Il est encadré par trois garde-fous, communs aux deux méthodes :

1. **Pas de réponse sans preuve.** Chaque phrase citée est recherchée mot pour mot par le code. Une citation qui n'existe pas fait écarter ce qu'elle devait prouver.
2. **Un doute ne fait jamais couvrir.** Tant qu'un fait décisif manque, la réponse est « à préciser », avec la question.
3. **Le code tranche, pas le modèle.** Dans les deux méthodes, la décision finale sort d'une logique écrite à l'avance, qui donne toujours la même réponse aux mêmes entrées.

## 4. Ce qu'il faut préparer pour un contrat

**Commun aux deux : découper.** Le programme lit le PDF, retire ce qui gêne (en-têtes, numéros de page, sommaire) et découpe le texte en clauses : une garantie, une exclusion, une définition du lexique. Chaque clause garde son numéro d'article. Pour le premier contrat, 48 pages deviennent 147 clauses. Un contrôle signale un découpage raté au lieu de continuer sur une base fausse.

**Propre à la première méthode : traduire en règles, et un vocabulaire.** Chaque garantie est réécrite sous une forme que le programme peut appliquer : son périmètre, ses conditions, ses obligations, ses exclusions, ses limites. Chaque règle porte la phrase du contrat qu'elle traduit. Un modèle (Mistral Large) propose la traduction, article par article ; le code la contrôle ; ce qui passe est relu par un humain. Il faut aussi une langue commune entre les règles et les déclarations : une liste fermée d'environ 250 faits possibles (l'événement, le bien, le lieu, la façon dont le local était fermé…), chacun avec la question à poser s'il manque. C'est la partie la plus longue du projet, et c'est là que la première méthode se trompe le plus : une règle mal traduite, ou un fait absent du vocabulaire, mène tout droit à une mauvaise décision.

**Propre à la seconde méthode : rien de plus, en principe.** Le modèle lit les clauses découpées ; il n'a besoin ni de règles ni de vocabulaire pour juger. **Mais dans toutes les mesures de ce projet, les règles de la première méthode ont servi de contresignature.** Sur un contrat sans règles traduites, la seconde méthode fonctionne (un « couvert » n'est alors plus contresigné), mais ce mode-là n'a jamais été mesuré. La promesse « un nouveau contrat sans travail de traduction » est donc réelle dans la conception, et pas encore prouvée.

Quatre contrats de quatre assureurs sont préparés, rendus anonymes (A, B, C, D). A et B sont traduits en entier, D en grande partie, C seulement en partie : ils ont servi à mesurer le travail que demande un contrat de plus.

## 5. Un sinistre, vu par les deux méthodes

**La première méthode, sur le vélo.** L'assuré écrit : *« Mon vélo a été volé dans ma cave, fermée par un cadenas. »* L'analyse prend quelques secondes.

1. **Lire.** Un modèle (Mistral Medium) traduit la phrase en faits : événement = vol, bien = vélo, lieu = cave, fermeture = cadenas.
2. **Vérifier chaque fait.** Un second modèle, plus petit (Mistral Small), relit la déclaration et retire ce qu'elle ne dit pas.
3. **Décider.** Le moteur applique les règles du contrat A. La garantie « vol du contenu dans le bâtiment » pose une condition : « si ces locaux sont fermés avec une serrure de sûreté ». Un cadenas n'en est pas une, d'après le lexique. La réponse est **non couvert**.
4. **Confirmer, rédiger, vérifier.** Le fait décisif est confirmé une dernière fois ; le code rédige la réponse et vérifie chaque citation. À côté, l'écran montre l'« arbre de preuve » : chaque condition examinée, sa phrase du contrat, et le fait qui l'a rendue vraie, fausse ou inconnue.

Sans les mots « fermée par un cadenas », le moteur ne sait pas comment la cave était fermée : **à préciser**, avec la question « Comment le local était-il fermé ? ».

**La seconde méthode.** L'analyse prend 2 à 3 minutes ; l'écran affiche chaque étape pendant qu'elle se fait.

1. **Désigner.** Mistral Large lit la table des chapitres et désigne ceux qui concernent le sinistre.
2. **Composer le dossier.** Le code y ajoute ce qui vaut pour tout le contrat : exclusions générales, obligations, définitions. De 70 à près de 300 clauses selon le contrat et le sinistre.
3. **Juger chaque clause.** Mistral Large rend pour chacune un effet (couvre, exclut, limite, à vérifier, sans effet), avec la phrase du contrat et celle de la déclaration. Une clause oubliée lui est redemandée une fois.
4. **Vérifier.** Le code retrouve chaque citation mot pour mot ; un jugement mal cité est écarté.
5. **Trancher.** Une exclusion citée l'emporte ; un point à vérifier donne « à préciser » ; une garantie qui couvre, sans exclusion, donne « couvert ».
6. **Contresigner.** Si la lecture conclut « couvert » et que les règles ne le disent pas, la réponse devient « à préciser ».

**Quatre cas réels du jeu de mesure final**, pour voir où les deux méthodes divergent (contrat A ; la première méthode a été passée trois fois, la seconde une fois) :

- *Le casier du club de tennis forcé* (on attendait « non couvert »). La première méthode répond « à préciser » les trois fois. La seconde trouve l'exclusion et la cite : « le vol du contenu entreposé dans un casier d'une association sportive ou d'agrément ». **Non couvert, juste.**
- *Le store banne arraché par la tempête* (on attendait « non couvert »). La première méthode le déclare couvert deux fois sur trois : c'est l'erreur grave. La seconde trouve l'exclusion des objets situés à l'extérieur, mais pose aussi une question (propriétaire ou locataire ?) et répond « à préciser ». **Pas juste, mais l'erreur grave est évitée.**
- *L'eau d'une gouttière voisine entrée par une fenêtre* (on attendait « couvert »). La première méthode refuse les trois fois. La seconde trouve la garantie dégâts des eaux, mais la contresignature voit le refus des règles et rend « à préciser ». **La garde a son prix : l'erreur de la première méthode tire la seconde vers le doute.**
- *Un dégât des eaux après le gel* (on attendait « à préciser »). La première méthode répond juste, « à préciser ». La seconde cite une clause d'obligations et refuse. **Ici, c'est la seconde qui se trompe, et dans un sens grave** : un refus fondé sur une clause citée n'est pas contresigné, il tient seul.

## 6. La mesure

Un chiffre ne vaut que si les cas n'ont pas servi à régler le système. Le projet a eu plusieurs jeux de test, et il faut les lire dans l'ordre.

**Les jeux qui ont servi à régler.** Sur ses premiers jeux, la première méthode atteignait 90 à 100 % de réponses justes, sans couvert à tort. Un jeu écrit sans voir les règles a fait tomber ces chiffres (95 % sur A, 58 % sur B, 78 % sur D, avec des couverts à tort). Après corrections, un troisième jeu, « neuf », a donné 38 justes sur 60 et **7 couverts à tort**. Autrement dit, la première méthode empêchait de répondre sans preuve, mais pas de mal traduire un contrat. C'est ce constat qui a fait naître la seconde. Sur ce même jeu « neuf », la seconde méthode a donné 48 justes sur 60, 1 couvert à tort et 1 refus à tort. Mais ce jeu a servi à la mettre au point : ce n'est pas une mesure.

**Le jeu « quatre » : la seule comparaison honnête.** Soixante déclarations, vingt par contrat (A, B, D), écrites par un premier annotateur qui n'a lu que les contrats, puis jugées sans voir sa réponse par deux autres : Mistral Large, et Claude, le modèle qui m'a aidé à construire le projet. Les trois avis concordent sur les soixante cas. Le code des deux méthodes a été figé avant, et le jeu a été passé une seule fois, sans rien corriger ensuite.

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

Trois choses à en retenir :

- **Sur des cas jamais vus, les deux méthodes ont à peu près autant de réponses justes** : 45 contre 42, un écart de trois réponses que soixante cas ne permettent pas d'affirmer. L'écart du jeu « neuf » (48 contre 38) était gonflé par le réglage. Il faut le dire : la seconde méthode n'est pas nettement « plus juste ».
- **Elle se trompe beaucoup moins dans le sens qui coûte le plus.** Un couvert à tort au lieu de plus de quatre.
- **Elle refuse plus souvent à tort.** Quatre fois au lieu de deux : un refus qui cite son exclusion n'est pas contresigné, et le modèle cite parfois une clause qui ne s'applique pas.

## 7. Les deux méthodes face à face

| | Première méthode (règles) | Seconde méthode (clauses) |
|---|---|---|
| Ce que voit le modèle | La déclaration seule | La déclaration et les clauses du contrat |
| Qui décide | Un moteur, sur des règles traduites | Une logique fixe, sur des jugements cités, contresignée par les règles |
| Travail par contrat | Découpage, traduction, vocabulaire, relecture humaine | Découpage ; les règles restent utiles pour la contresignature |
| Où elle se trompe | À la traduction : une règle fausse, un fait absent du vocabulaire | À la lecture : une clause mal jugée, une définition du lexique oubliée |
| La preuve | La phrase attachée à la règle | La phrase citée par le modèle, vérifiée mot pour mot |
| La question à poser | Tirée du vocabulaire | Rédigée par le modèle sur la clause en doute |
| Le raisonnement montré | Un arbre de preuve, condition par condition | Le jugement de chaque clause, avec ses deux citations |
| Même réponse deux fois ? | Presque : 2 à 3 cas sur 20 changent d'un passage à l'autre | Pas mesuré ; le modèle juge, et peut juger autrement |
| Durée, coût | Quelques secondes, très peu | 2 à 3 minutes, 8 à 10 centimes |
| Couverts à tort (jeu « quatre ») | 4,3 sur 60 | 1 sur 60 |

**Ce que la première méthode fait mieux.** Elle est rapide, peu coûteuse, et son raisonnement se refait à la main : chaque condition, chaque fait, chaque phrase. Elle refuse moins souvent à tort. Ses erreurs ont une adresse : la lecture de la déclaration ou la traduction du contrat.

**Ce que la seconde fait mieux.** Elle lit le contrat lui-même : une clause que la traduction avait manquée peut encore être vue (le casier du club de tennis). Elle se trompe beaucoup moins souvent dans le sens grave. Et, en principe, elle peut s'appliquer à un nouveau contrat sans le travail de traduction.

**Ce que la seconde fait moins bien.** Deux à trois minutes par analyse, et un modèle plus cher. Elle refuse plus souvent à tort. Elle confie davantage au modèle : ses jugements sont vérifiés dans leurs citations, pas dans leur bon sens, et une citation exacte peut être hors sujet. Elle applique encore mal certaines définitions du lexique. Et sa meilleure garde, la contresignature, dépend des règles de la première méthode : quand celles-ci se trompent, elle tire vers le doute une bonne réponse.

## 8. Le choix, et ce qui reste à faire

**La seconde méthode est la méthode par défaut.** Le choix tient au classement des erreurs du §1 : à justesse comparable, on préfère le système qui promet le moins souvent à tort, et qui peut s'étendre à d'autres contrats. Les deux méthodes restent dans le code, et l'écran dit laquelle a répondu.

**Ce qui reste vrai pour les deux.**

- **Les bonnes réponses n'ont pas été relues par un juriste.** Elles ont été établies d'après le texte des contrats par trois annotateurs automatiques qui concordent. Leur accord dit que les cas ne sont pas ambigus pour qui lit le contrat, pas qu'un professionnel les validerait tous. C'est la prochaine étape avant tout usage réel.
- **Les jeux de test sont petits.** Vingt cas par contrat : un écart de deux ou trois réponses ne veut rien dire. Chaque contrat demande son propre jeu jamais vu, renouvelé après chaque série de corrections.
- **Ce n'est pas un service en production.** Il n'a pas d'utilisateurs réels. Mon expérience d'un service en ligne vient de SortirIA.
- **Il ne dit rien du montant.** Il répond à « est-ce couvert ? », pas à « combien ? ». Les plafonds et franchises sont cités, pas calculés.

**Ce qui reste à faire pour la seconde.**

- Mesurer le mode sans contresignature, sur un contrat sans règles traduites : c'est la condition pour dire qu'elle généralise.
- Faire baisser les refus à tort, par exemple en soumettant aussi un refus au regard des règles quand elles répondent « à préciser ».
- Réduire l'attente, en profitant davantage du cache du fournisseur.

## 9. En une phrase

La première méthode traduit le contrat une fois pour toutes et laisse un programme décider : elle est rapide et transparente, mais elle se trompe dès que la traduction est fausse. La seconde fait lire au modèle les clauses mêmes du contrat, vérifie chacune de ses citations et fait contresigner ses « couvert » par la première : elle est lente, mais sur des cas jamais vus, elle promet à tort quatre fois moins souvent, pour autant de réponses justes.
