# Comprendre le projet, sans rien connaître à l'assurance ni à l'intelligence artificielle

Ce texte raconte le projet du début à la fin, dans l'ordre où les questions se posent. Il ne demande aucune connaissance préalable. Les détails techniques sont ailleurs : [les explications](EXPLICATIONS.md) décrivent chaque fichier, [la démarche](DEMARCHE.md) garde chaque essai et sa mesure.

## 1. L'objectif

Quelqu'un rentre chez lui et trouve sa cave forcée, son vélo disparu. Il écrit à son assureur : « Mon vélo a été volé dans ma cave. » De l'autre côté, un gestionnaire doit répondre à une seule question : **le contrat couvre-t-il ce sinistre ?**

Pour répondre, il ouvre les « conditions générales », un document de 50 à 100 pages. Il y cherche la garantie vol, lit ce qu'elle couvre, puis la liste de ce qu'elle exclut, puis le lexique, parce que le contrat donne aux mots un sens précis (une « serrure de sûreté » n'est pas un cadenas). C'est long, et une erreur coûte cher dans les deux sens : promettre un remboursement que le contrat ne prévoit pas, ou refuser à tort.

Le projet fait ce travail avec lui. On lui donne une déclaration écrite comme on parle, il rend trois choses :

- **la réponse** : couvert, non couvert, ou « à préciser » ;
- **la preuve** : la phrase exacte du contrat sur laquelle la réponse s'appuie, avec son numéro d'article et sa page ;
- **la question à poser**, quand la déclaration ne dit pas tout ce qu'il faut savoir.

La troisième réponse est aussi importante que les deux autres. Un outil qui répond toujours quelque chose est dangereux ; un outil qui sait dire « je ne peux pas trancher, demandez-lui si la cave était fermée à clé » est utile.

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

**« Je ne sais pas » doit rester « je ne sais pas ».** Si la déclaration ne dit pas comment la cave était fermée, on ne peut ni couvrir ni refuser. Dans SortirIA, une information manquante peut être laissée de côté sans dommage. Ici, deviner est interdit.

## 3. La décision : qui fait quoi

La solution la plus simple serait de donner le contrat et la déclaration à un modèle de langage (ChatGPT, Mistral, Claude) et de lui demander la réponse. Je l'ai essayé au début. Le modèle répond avec assurance, souvent juste, et parfois faux sans que rien ne le signale. Surtout, on ne peut pas vérifier son raisonnement : il ne le montre pas, il le raconte après coup.

Le projet repose donc sur un partage des rôles, qui tient en une phrase : **le modèle lit, la logique décide, le code vérifie.**

- **Le modèle lit.** C'est ce qu'il fait bien : comprendre que « on m'a piqué mon vélo » veut dire un vol, et que « le local à vélos de la résidence » est une partie commune. Il ne fait que cela.
- **La logique décide.** Les règles du contrat sont écrites une fois, à l'avance, dans un langage fait pour le raisonnement (Prolog). Un programme les applique. Avec les mêmes faits, il rend toujours la même réponse, et il montre chaque étape.
- **Le code vérifie.** Chaque phrase citée est recherchée mot pour mot dans le contrat. Si elle n'y est pas, la réponse ne sort pas.

Deux garde-fous valent partout :

1. **Un doute ne fait jamais couvrir.** Tant qu'un fait décisif manque, la réponse est « à préciser », avec la question.
2. **Pas de réponse sans preuve.** Une décision qui ne peut pas citer le contrat est rétrogradée.

## 4. Préparer un contrat (une fois pour toutes)

Avant de pouvoir répondre sur un contrat, il faut le préparer. Cela se fait une seule fois par contrat, et c'est la partie la plus longue du travail.

**Première étape : découper.** Le programme lit le PDF, retire ce qui gêne (en-têtes, numéros de page, sommaire), et découpe le texte en clauses : une garantie, une exclusion, une définition du lexique. Chaque clause garde son numéro d'article et sa page. Pour le premier contrat, 48 pages deviennent 147 clauses. Un contrôle signale un découpage raté (trop peu de clauses, aucune exclusion trouvée) au lieu de continuer sur une base fausse.

**Deuxième étape : traduire en règles.** Chaque garantie est réécrite sous une forme que le programme peut appliquer :

- son **périmètre** : de quoi elle parle (un vol, dans le bâtiment, d'un bien qui vous appartient) ;
- ses **conditions** : « si ces locaux sont fermés avec une serrure de sûreté » ;
- ses **obligations** : ce que l'assuré devait faire (fermer la voiture à clé) ;
- ses **exclusions** : « le vol dans les parties communes du bâtiment » ;
- ses **limites** : plafonds et franchises.

Chaque règle porte la phrase du contrat qu'elle traduit. C'est cette phrase qui sera citée dans la réponse.

Ce n'est pas moi qui écris ces règles à la main, ou rarement. Un modèle de langage (Mistral Large) propose une traduction, article par article. Puis le code la contrôle : chaque phrase citée existe-t-elle dans le contrat ? Chaque exclusion du texte est-elle traduite ? Chaque mot employé est-il connu ? Une proposition qui échoue à un contrôle est bloquée. Ce qui passe est relu par un humain avant d'être accepté. Le modèle rédige, il ne valide pas.

**Troisième étape : le vocabulaire.** Pour que les règles et les déclarations se rencontrent, il faut une langue commune. C'est une liste fermée de faits possibles : l'événement (vol, incendie, dégât des eaux…), le bien (vélo, bijoux, ordinateur…), le lieu (cave, jardin, parties communes…), et les précisions qui comptent pour un contrat (y a-t-il eu effraction ? le local était-il fermé, et comment ?) : environ 250 faits en tout. Chaque fait a sa question en français, celle qu'on posera à l'assuré s'il manque. Une partie du vocabulaire est commune à tous les contrats, le reste est propre à chacun.

Quatre contrats de quatre assureurs sont préparés, rendus anonymes (A, B, C, D). A et B sont traduits en entier ; C et D en partie, et l'écran le montre par une couleur.

## 5. Les pièces de la machine

Une fois le contrat préparé, le système tient en cinq pièces.

```
le vocabulaire      la liste fermée des faits, avec leurs questions
les règles          un fichier par contrat : garanties, conditions, exclusions, chacune avec sa phrase
le moteur           le programme qui applique les règles aux faits ; le même pour tous les contrats
la lecture          le modèle qui traduit une déclaration en faits du vocabulaire
les bancs d'essai   des déclarations dont on connaît la bonne réponse, rejouées à chaque changement
```

**Le moteur** raisonne avec trois valeurs : oui, non, inconnu. C'est ce qui lui permet de ne pas confondre « la cave n'était pas fermée » avec « on ne sait pas si elle l'était ». Il suit le raisonnement d'un gestionnaire : une garantie dont le périmètre ne correspond pas est écartée ; une exclusion ne retire qu'une garantie qui s'appliquait ; c'est à l'assuré d'établir la garantie, à l'assureur d'établir l'exclusion. Quand il ne peut pas trancher, il essaie chaque réponse possible aux faits manquants et retient la question qui change la décision.

**Les bancs d'essai** sont ce qui permet de croire les chiffres. Une partie des cas sert à mettre au point ; une autre, jamais regardée pendant le réglage, sert à mesurer. Un troisième jeu, dit « fermé », a été écrit sans voir les règles. Chaque banc a des seuils fixés à l'avance.

## 6. Ce qui se passe quand on analyse un sinistre

Reprenons le vélo. L'assuré écrit : *« Mon vélo a été volé dans ma cave, fermée par un cadenas. »* L'analyse prend 4 à 5 secondes et passe par six étapes ; l'écran affiche les principales pendant qu'elles se font.

1. **Lire.** Un premier modèle (Mistral Medium) traduit la phrase en faits du vocabulaire : événement = vol, bien = vélo, lieu = cave, fermeture = cadenas.
2. **Vérifier chaque fait.** Un second modèle (Mistral Small), plus petit, relit la déclaration et contrôle chaque fait : est-il vraiment écrit ? Ce que la déclaration ne dit pas est retiré. Le premier modèle a tendance à compléter ; le second est là pour l'en empêcher.
3. **Décider.** Le moteur applique les règles du contrat A. La garantie « vol du contenu dans le bâtiment » concerne bien ce sinistre. Mais elle pose une condition : « si ces locaux sont fermés avec une serrure de sûreté ». Un cadenas n'en est pas une, d'après le lexique du contrat. La réponse est **non couvert**.
4. **Confirmer.** Une réponse ferme doit reposer sur des faits sûrs. Le fait qui a tout décidé (le cadenas) est confirmé une dernière fois dans le texte. S'il ne l'était pas, la réponse redeviendrait « à préciser ».
5. **Rédiger.** Le code, pas le modèle, écrit la réponse : la décision, la garantie en cause, la phrase du contrat.
6. **Vérifier les citations.** Chaque phrase citée est retrouvée mot pour mot dans la clause. Puis l'analyse est notée dans un journal, sans le texte de la déclaration.

Maintenant, retirons trois mots. L'assuré écrit seulement : *« Mon vélo a été volé dans ma cave. »* Le moteur trouve la même garantie et la même condition, mais il ne sait pas comment la cave était fermée. Il ne couvre pas, il ne refuse pas. La réponse est **à préciser**, avec la question : « Comment le local était-il fermé ? »

Et si le vélo était dans le hall de l'immeuble : une exclusion s'applique (« le vol ou le vandalisme dans les parties communes du bâtiment »), la réponse est **non couvert**, et c'est cette phrase qui est citée.

À côté de la réponse, l'écran montre l'« arbre de preuve » : chaque condition examinée, la phrase du contrat correspondante, et le fait de la déclaration qui l'a rendue vraie, fausse ou inconnue. Le gestionnaire peut refaire le raisonnement lui-même.

## 7. Les points forts

- **Le système ne promet pas à tort.** Sur les derniers passages des bancs (24 novembre 2026), aucun sinistre n'a été déclaré couvert à tort, sur les trois contrats mesurés. Les réponses sont justes à 94 % et 100 % pour A, 92 % pour B, 96 % pour D.
- **Chaque réponse se vérifie.** La phrase citée existe dans le contrat, le code le garantit. Le raisonnement est affiché, pas raconté.
- **Il sait ne pas savoir.** Les erreurs qui restent sont presque toutes des questions de trop : il demande une précision qu'il aurait pu lire. C'est le sens d'erreur le moins coûteux.
- **Les erreurs ont une adresse.** Avec des faits exacts, le moteur donne la bonne réponse sur tous les cas de test du contrat A. Les erreurs viennent de la lecture, c'est-à-dire de l'étape confiée au modèle. On sait donc où chercher.
- **Un nouveau contrat n'abîme pas les autres.** Le moteur est le même pour tous ; ajouter le quatrième contrat n'a pas fait baisser les trois premiers.
- **Tout est mesuré, y compris les échecs.** La démarche garde les essais qui n'ont pas marché et les fois où une mesure m'a donné tort.

## 8. Les points faibles

- **La lecture reste fragile.** Le modèle lit parfois plus que ce qui est écrit, ou lit différemment le même texte d'un passage à l'autre. Les garde-fous transforment ces erreurs en questions, pas en mauvaises décisions, mais ils ne les suppriment pas.
- **Préparer un contrat demande du travail humain.** Le modèle propose les règles, le code les contrôle, mais quelqu'un relit, et c'est la partie la plus longue du projet. Pour des centaines de contrats, cette relecture serait le coût principal.
- **Deux contrats sur quatre sont incomplets.** Chez C et D, certains sinistres reçoivent « à examiner par un gestionnaire » parce que leur garantie n'est pas encore traduite. C'est dit clairement, mais ce n'est pas une réponse.
- **Les jeux de test sont petits.** Vingt à trente cas par contrat : un écart de trois ou quatre points entre deux passages ne veut rien dire. Certaines parties (les voyages, la protection numérique du contrat B) sont vérifiées par des essais de règles, pas par un banc. Et trois cas des jeux « fermés » ont fini par servir à corriger une règle : ils sont signalés à côté des chiffres, et ne comptent plus comme des cas jamais vus.
- **Les bonnes réponses n'ont pas été relues par un juriste.** Elles ont été établies d'après le texte des contrats. Un professionnel pourrait en contester certaines.
- **Ce n'est pas un service en production.** Il n'a pas d'utilisateurs réels. Mon expérience d'un service en ligne vient de SortirIA, pas d'ici.
- **Il ne dit rien du montant.** Il répond à « est-ce couvert ? », pas à « combien ? ». Les plafonds et franchises sont cités, pas calculés.

## 9. En une phrase

Un modèle de langage est très bon pour comprendre ce qu'une personne a voulu dire, et peu fiable pour appliquer cent règles sans en oublier une. Ce projet lui confie la première tâche, confie la seconde à un programme qui montre son raisonnement, et fait vérifier le tout par du code. Ce qu'il ne sait pas, il le demande.
