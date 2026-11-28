# Document de conception

*Couverture sinistre : dire si un sinistre est couvert par un contrat d'assurance habitation, pourquoi, et sur quelles
clauses. Synthèse en dix minutes de lecture, au 28 novembre 2026. Le détail est dans le [README](../README.md), le
raisonnement pas à pas dans [la démarche](DEMARCHE.md), les mesures dans [la fiche métriques](METRIQUES.md).*

---

## 1. Le problème, et la contrainte qui commande tout

Un gestionnaire reçoit une déclaration en langage courant (« on m'a volé mon vélo dans le local commun ») et doit dire
si le contrat la couvre. Il relit pour cela cinquante à cent pages de conditions générales : la garantie, ses
conditions, ses exclusions, le lexique, les exceptions aux exclusions.

**Les erreurs ne coûtent pas la même chose.** Un « couvert » à tort est un paiement que le contrat ne prévoit pas ; un
refus à tort, un client lésé ; une réponse impossible à justifier ne vaut rien, même juste. J'ai donc fixé, avant de
construire quoi que ce soit, trois critères, dans cet ordre :

1. **ne pas couvrir à tort** ;
2. **pouvoir vérifier** : chaque réponse renvoie à la phrase du contrat, relisible en un clic ;
3. **savoir quoi demander** quand la déclaration ne suffit pas, plutôt que deviner.

La réponse a trois valeurs : *couvert*, *non couvert*, *à préciser* (avec la question à poser). Le système propose ;
le gestionnaire décide.

**Pourquoi pas « coller le contrat dans un assistant ».** C'est le premier essai, et il échoue sur les trois critères :
l'exclusion qui décide ne ressemble pas à la question (un vélo dans le hall relève des « parties communes du
bâtiment ») ; le sens des mots est au lexique (un cadenas n'est pas une « serrure de sûreté ») ; le raisonnement ne se
vérifie pas. Sur un banc public de cas d'assurance, un modèle seul tranchait 90 % des cas que des lecteurs humains
jugent ambigus.

## 2. L'architecture

Un principe : **le modèle juge des clauses, le code tranche.** On ne demande jamais au modèle « est-ce couvert ? ».

```
                      Une fois par contrat
   conditions générales ─► clauses découpées, anonymisées, contrôlées (base SQLite)
                         ─► pour chaque garantie, la liste des clauses qu'un gestionnaire doit relire
                         ─► règles Prolog traduites du contrat (rédigées par Mistral Large, contrôlées, relues)

                      À chaque déclaration : la lecture des clauses (méthode par défaut, 2 à 3 min)

   déclaration ─► 1. DÉSIGNATION   Mistral Large désigne les chapitres en jeu
               ─► 2. DOSSIER       le code ajoute exclusions générales, obligations, définitions,
                                   et la liste des clauses attendues
               ─► 3. JUGEMENT      Mistral Large juge chaque clause : couvre, exclut, limite,
                                   à vérifier (+ question), sans effet ; avec une phrase du contrat
                                   et une phrase de la déclaration
               ─► 4. CONTRÔLE      le code retrouve chaque citation mot pour mot, redemande une clause
                                   attendue restée sans jugement
               ─► 5. DÉCISION      une logique fixe : une exclusion citée l'emporte, un doute donne
                                   « à préciser »
               ─► 6. CONTRESIGNATURE  la chaîne de règles, lancée en parallèle, doit dire « couvert »
                                   elle aussi, ou voir chacun de ses obstacles écarté par une citation ;
                                   sinon « à préciser »

                      En parallèle : la chaîne de règles (seconde méthode, 4 à 5 s)

   déclaration ─► Mistral Medium la traduit en faits d'un vocabulaire fermé ─► Mistral Small vérifie
               chaque fait ─► le moteur Prolog (logique à trois valeurs) décide, avec un arbre de preuve
```

| Étape | Qui | Ce que le code garantit |
|---|---|---|
| Désignation | modèle | les garanties trouvées par les règles s'ajoutent aux chapitres désignés |
| Dossier | code | toutes les clauses attendues d'une garantie y sont, exclusions générales comprises |
| Jugement | modèle | une clause attendue sans jugement est redemandée ; sinon, pas de réponse franche |
| Contrôle | code | une citation introuvable dans le texte est écartée |
| Décision | code | reproductible : mêmes jugements, même décision |
| Contresignature | code + règles | aucun « couvert » sans l'accord des deux méthodes |

**Après les réponses du client**, seules les clauses en doute et leur garantie sont rejugées ; quand seules les règles
posaient la question, le moteur décide seul, en quelques secondes. Une déclaration à plusieurs sinistres reçoit une
décision par sinistre.

**Autour** : une API FastAPI (clé ou code d'accès, limite d'analyses par jour), un écran Angular qui suit l'analyse
étape par étape, une fiche PDF par réponse avec les articles cités en entier, un journal des analyses sans le texte du
sinistre, environ 350 tests, des consignes au modèle versionnées et archivées. En ligne sur Azure Container Apps.

## 3. Les choix, et ce qui a été écarté

| Option | Décision | Raison |
|---|---|---|
| Tout le contrat et la déclaration dans un seul appel | écartée | pas vérifiable, tranche l'ambigu (voir § 1) |
| Recherche par similarité des clauses (RAG classique) | écartée comme seule source du dossier | l'exclusion qui décide ne ressemble pas à la déclaration ; **une clause absente ne se trouve pas par une recherche**. D'où la liste écrite d'avance des clauses attendues par garantie |
| Règles traduites seules (ma première hypothèse) | gardée, mais plus seule | très bonne sur les cas qui ont servi à la régler, faible sur des cas neufs : 38 justes sur 60 et 7 couverts à tort sur un troisième jeu. Une règle peut mal traduire le contrat |
| Le modèle juge, le code décide (seconde hypothèse) | **méthode par défaut** | meilleure sur cas neufs (§ 4), lit le texte même ; plus lente et plus chère |
| Contresignature par les règles | gardée | elle coûte des « à préciser » là où les règles sont incomplètes (contrat D), mais elle empêche des couverts à tort |
| Deux consignes de lecture : cause seulement probable, condition non dite | gardées | sur un jeu neuf, trois couverts à tort évités pour deux réponses justes perdues |
| Ajouter les garanties trouvées par les règles au dossier | gardé, sans effet prouvé | mesuré : aucun gain de stabilité |
| Corriger la lecture de « personnel de maison » | retiré | la correction faisait couvrir à tort un cas, six fois sur six |

Chaque essai a eu son critère d'acceptation écrit avant la mesure ; les essais retirés restent dans la démarche.

## 4. Les chiffres clés, et ce qu'ils valent

Tous mesurés sur des **déclarations jamais vues** : écrites par des annotateurs (agents Claude) qui n'avaient lu que le
texte des contrats, jugées à l'aveugle par un second annotateur, code figé avant, chaque jeu passé une seule fois puis
déclaré « vu ». Contrats A, B et D, vingt cas chacun. Entre crochets, l'intervalle de confiance à 95 % (Wilson).

| Mesure | Lecture des clauses | Chaîne de règles |
|---|---|---|
| Jeu « cinq » (26 nov.), réponses justes | **53 / 60 = 88 %** [78–94] | 40,3 / 60 = 67 % [54–77] |
| Jeu « cinq », couverts à tort | **0** [0–6 %] | 4,7 en moyenne sur 3 passes |
| Stabilité : trois passes sur 30 cas de « cinq » | 74 / 90 = 82 % [73–89] ; 7 cas sur 30 changent, jamais de « couvert » à « non couvert » | plus stable |
| Jeu « six » (27 nov.), plus difficile, consigne actuelle | 46 / 60 = 77 % [65–86] ; **1 couvert à tort** | non mesurée |
| Durée d'une analyse | 2 à 3 minutes (médiane 177 s) | 4 à 5 secondes |
| Coût d'une analyse | 8 à 10 centimes | nettement moins : deux modèles plus petits, des appels courts |

**Ce que je lis.** La lecture des clauses fait moins d'erreurs coûteuses que la chaîne de règles, et l'écart sur
« cinq » (treize réponses, sur les mêmes cas) dépasse le hasard. Son niveau à attendre est plutôt **80 % que 88 %** :
la première passe avait eu de la chance. Elle varie d'une passe à l'autre, mais vers la prudence : une réponse franche devient
« à préciser » ou l'inverse, jamais « couvert » au lieu de « non couvert ».

**Ce qu'ils ne valent pas.**
- Les réponses attendues viennent d'**annotateurs automatiques** qui s'accordent, pas d'un gestionnaire ni d'un
  juriste. C'est la plus grosse faiblesse de la mesure.
- **Vingt cas par contrat** : les intervalles font vingt points de large ; un écart de deux ou trois réponses ne dit
  rien.
- **Une passe** pour la mesure de référence de la lecture des clauses, alors qu'elle varie.
- **Pas de comparaison avec une solution simple** (un seul appel avec tout le contrat) sur les mêmes jeux : je ne sais
  pas chiffrer ce que l'architecture apporte par rapport à elle.
- **Seulement de l'habitation**, quatre contrats, dont deux traduits en règles en partie, par choix.

## 5. Ce qu'il faudrait pour la production

**Un humain dans la boucle, clairement défini.** Le système prépare la décision ; le gestionnaire la prend. Vont
directement chez lui : tout « à préciser », tout désaccord entre les deux méthodes, toute déclaration sur une garantie
non traduite. Un « couvert » ou un refus arrive avec les clauses citées et la fiche PDF, pour une relecture rapide, pas
un clic d'approbation.

**Les données personnelles (RGPD).** Une déclaration en contient (noms, adresses, parfois des blessures, donc des
données de santé). Déjà fait : le texte du sinistre n'est jamais écrit au journal ; hébergement en France ;
assureurs anonymisés. À faire : un contrat de sous-traitance avec le fournisseur du modèle et l'hébergeur, une durée de
conservation, l'information des assurés, et une décision finale humaine (l'article 22 du RGPD encadre les décisions
entièrement automatisées qui affectent une personne).

**Le suivi.** Déjà fait : un journal par analyse (méthode, décision, durée, tokens, coût), une limite d'analyses par
jour, des tableaux Grafana en local. À faire en ligne : un tableau de bord sur ces journaux, des alertes (taux
d'erreurs du fournisseur, coût par jour, part de « à préciser »), et le repassage chaque semaine d'un jeu vu, pour voir
dériver le modèle du fournisseur.

**Le temps et le coût.** Deux à trois minutes conviennent à un gestionnaire, pas à un client en direct. Leviers : le
cache du fournisseur (déjà utilisé), la relecture partielle (faite), des modèles plus petits pour certaines étapes (à
mesurer), un traitement par lots pour les déclarations reçues la nuit.

**Ajouter un contrat.** Aujourd'hui : découper et anonymiser, écrire la liste des clauses attendues par garantie,
traduire en règles et relire. La traduction est l'étape lourde. La lecture des clauses fonctionne sans traduction
complète (contrats C et D) ; une piste serait de ne traduire que les garanties les plus fréquentes, en laissant la
contresignature passer la main au gestionnaire ailleurs.

## 6. La suite, dans l'ordre

1. **Faire relire les jeux de test par un gestionnaire.** Même une demi-heure sur dix cas par contrat dirait si mes
   « bonnes réponses » sont celles du métier. C'est la première chose à faire, avant tout nouveau réglage.
2. **Partir de vraies déclarations** : lesquelles reviennent le plus, où sont les vraies difficultés. Les jeux actuels
   sont écrits pour être variés, pas représentatifs.
3. **Des jeux plus grands** (100 à 200 cas par contrat), plusieurs passes systématiques, moyenne et dispersion.
4. **Comparer à des solutions simples**, sur les mêmes cas : un appel avec tout le contrat ; une recherche suivie d'un
   seul jugement. Si l'une fait aussi bien, simplifier.
5. **Comparer plusieurs modèles et tailles**, avec le coût et la durée comme contraintes, pas comme constats.
6. **Simplifier** ce que la mesure ne justifie pas, et traiter deux contrats en entier plutôt que quatre en partie.
7. Les éléments de production du § 5.

**Ce que je referais autrement.** Je partirais du métier et d'une solution simple mesurée, avant de construire la
traduction en règles ; et je tiendrais dès le début un document comme celui-ci, à côté du journal de bord.
