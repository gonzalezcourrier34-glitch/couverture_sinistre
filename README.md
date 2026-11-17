# Couverture sinistre

Un système qui dit si un sinistre est couvert par un contrat d'assurance habitation, **pourquoi**, et **sur quelles clauses** il s'appuie. Quand le contrat ne permet pas de trancher, il répond **INCERTAIN** et dit ce qu'il faut vérifier.

> Une réponse assurée sans justification vaut moins qu'un « je ne sais pas » étayé.

Explication détaillée de chaque fichier, lexique et choix : [docs/EXPLICATIONS.md](docs/EXPLICATIONS.md).

## Pourquoi pas « le PDF dans un chatbot »

Coller le contrat dans un prompt marche sur un contrat, puis s'effondre :
- **L'exclusion ne ressemble pas à la question.** « Vol de vélo » ramène « les vélos sont garantis ». L'exclusion des parties communes est dans une autre clause, et la définition de « parties communes » est au lexique.
- **Chaque assureur rédige autrement** (numérotation, intertitres, place des exclusions), et un prompt réglé sur un contrat casse sur le suivant.
- **Rien n'est vérifiable** : le modèle peut citer une clause qui n'existe pas, et on ne s'en aperçoit pas.

Le système fait donc le travail difficile **une fois par contrat**, à l'ingestion, puis raisonne sur des clauses structurées et contrôle chaque citation.

## Les étapes

```
PDF ──► nettoyage ──► découpage en clauses ──► contrôles ──► base SQLite        (une fois par contrat)

sinistre ──► faits ──► recherche + enveloppe du contrat ──► juge ──► contrôle des citations ──► réponse
```

| Étape | Module | Ce qu'elle fait |
|---|---|---|
| Lecture | `chargement.py` | PDF, Word ou Markdown → lignes avec leur page. Retire le sommaire, les en-têtes et pieds de page répétés, recolle les mots coupés. |
| Découpage | `segmentation.py` | Une clause = une unité du contrat : articles numérotés (`4.3`), intertitres sans numéro (« Ce que nous ne garantissons pas » → `2.2-b`), titres en capitales. Le lexique est éclaté en une clause par terme. Chaque clause est typée (garantie, exclusion, condition, limite, définition) et garde ses renvois (« au sens de l'article 1.5 »). |
| Profils | `profils.py` | Les règles de lecture propres à un assureur (ses intertitres, ses lignes de bruit, son format de lexique), dans un fichier JSON, sans toucher au code. |
| Réparation | `reparation.py` | Pour un contrat mal lu : diagnostic, profil proposé par Mistral, vérifié par le code (avant/après), **appliqué seulement après validation humaine**. |
| Qualité | `qualite.py` | **Le juge de qualité** à l'ingestion : Mistral relit un échantillon de clauses et dit si leur type est juste. Sous 80 %, le contrat passe « à vérifier » et les erreurs guident l'agent de réparation. |
| MLflow | `suivi.py`, `consignes.py` | Une exécution par ingestion et par évaluation (paramètres, versions des consignes, métriques, rapport). Les consignes sont versionnées : un texte modifié sans nouvelle version fait échouer la CI ; `couverture versions --enregistrer` les inscrit au Prompt Registry avec l'alias `production`. Jamais bloquant. |
| Grafana | `monitoring/grafana/` | Deux tableaux (Réponses, Contrats) lus directement dans la base SQLite, générés par un script dont chaque requête est testée. |
| Suivi | `journal.py`, `derive.py`, `bilan.py` | Chaque analyse est journalisée (sans le texte du sinistre). La dérive compare la semaine aux 4 précédentes (PSI). Le bilan dit ce qui demande une intervention, puis les chiffres, et peut partir par mail. |
| Contrôles | `controles.py` | Repère les contrats mal lus : trop peu de clauses, aucune exclusion, titres non reconnus, renvois cassés. Statut `OK` ou `A_VERIFIER`. |
| Stockage | `base.py`, `ingestion.py` | Tables `contrats`, `clauses`, `renvois`. Un contrat inchangé n'est pas relu. Les questions sont toujours filtrées sur un contrat. |
| Faits | `faits.py` | Événement, bien, lieu, circonstances, traduits en vocabulaire du contrat (« local commun » → parties communes). |
| Recherche | `recherche.py` | **Hybride** : BM25 (les mots) et embeddings `mistral-embed` (le sens), fusionnés par RRF, comme dans SortirIA. Puis **l'enveloppe du contrat** : exclusions et conditions de la même section que la garantie trouvée, exclusions générales, clauses visées par un renvoi, définitions des termes employés. |
| Grille | `conditions.py` | Le modèle ne dit pas « couvert ou non ». Il remplit une grille : pour chaque garantie possible, ses conditions, et chaque exclusion possible, avec pour chacune un état (`REMPLIE`, `NON_REMPLIE`, `INCONNUE`), le passage exact du contrat et le fait du sinistre qui le fonde. |
| Décision | `conditions.py` | **Calculée par des règles**, pas devinée (voir ci-dessous). Sans modèle, `JugeHeuristique` prend le relais et ne tranche que les cas nets. |
| Relecture | `relecture.py` | **Le juge de la grille** : un second appel, indépendant, relit les conditions qui décident et vérifie que chaque passage cité **justifie** l'état donné (pas seulement qu'il existe). Une condition contestée redevient inconnue et la décision est recalculée : la relecture ne peut que rendre la réponse plus prudente. |
| Contrôle | `validation.py` | Chaque citation doit exister mot pour mot dans une clause fournie. Le type de clause vient du contrat, pas du modèle. COUVERT sans garantie citée correctement devient INCERTAIN. La décision d'origine est conservée (`decision_initiale`) pour mesurer ce que le contrôle corrige. |
| Référence | `PipelineDocumentBrut` | Le contrat entier dans le prompt, sans recherche : la méthode à battre. |

## La décision : condition par condition

Un gestionnaire ne se demande pas « est-ce couvert ? » d'un bloc. Il vérifie une grille. Le système fait pareil :

1. Le modèle confronte chaque condition au sinistre. Exemple sur Foyer appart 123, vélo volé dans le local commun :
   - garantie « Vol du contenu » : *le vélo était-il dans le bâtiment assuré ?* → **inconnu** (art. 2.10, p. 11) ;
   - exclusion : *le vol a-t-il eu lieu dans les parties communes ?* → **s'applique** (art. 2.10-a, p. 12) ;
   - exclusion : *complicité d'un proche ?* → **ne s'applique pas**.
2. Les citations sont vérifiées : une condition dont le passage est introuvable est écartée.
3. La décision est calculée :
   - une exclusion qui s'applique → **non couvert** ;
   - une garantie dont toutes les conditions sont remplies, sans exclusion → **couvert** ;
   - si une exclusion reste inconnue → **incertain**, en disant laquelle ;
   - une garantie possible avec des conditions inconnues → **incertain**, avec les questions à poser à l'assuré ;
   - toutes les garanties écartées → **non couvert**.

Résultat : « je ne sais pas » n'est pas une hésitation du modèle. C'est une condition dont l'état est inconnu, et on sait laquelle. Chaque étape est petite et vérifiable, et un modèle se trompe bien moins sur « ce fait remplit-il cette condition ? » que sur « ce sinistre est-il couvert par ce contrat de 48 pages ? ».

Trois méthodes sont comparables sur les mêmes cas (`couverture comparer`) :
- `brut` : le contrat entier collé dans le prompt (le chatbot) ;
- `direct` : les clauses retenues, puis un verdict du modèle en un coup ;
- `conditions` : la grille et la décision calculée (méthode par défaut).

## Les agents et les juges

Repris de l'organisation de SortirIA, chacun à un endroit précis et contrôlé :

| Rôle | Quand | Ce qu'il fait | Garde-fou |
|---|---|---|---|
| Juge de qualité | ingestion, une fois par contrat | vérifie le type d'un échantillon de clauses | ne bloque jamais ; sous le seuil, le contrat passe « à vérifier » |
| Agent de réparation | contrat « à vérifier » | propose un profil d'assureur | vérifié par le code, appliqué seulement par un humain |
| Juge des conditions | chaque sinistre | remplit la grille, sans conclure | citations vérifiées, décision calculée par des règles |
| Juge de la grille (relecture) | chaque sinistre, sauf INCERTAIN | relit les conditions décisives | ne peut que rendre la réponse plus prudente |
| MLflow et Grafana | en continu | suivent chaque ingestion, évaluation et réponse, avec les versions qui les ont produites | lecture seule ; le suivi ne bloque jamais |
| Dérive et bilan | chaque semaine | signale ce qui change et ce qui demande une intervention | lecture seule |

Pas de LangGraph ici : la chaîne est linéaire. Le graphe de SortirIA se justifiait par la collecte nocturne (nouvelles tentatives, branches, pannes de sources).

## Tenir des centaines de contrats

La vraie difficulté n'est pas la réponse, c'est la lecture de contrats tous rédigés différemment. Le système la traite comme SortirIA traitait des dizaines d'agendas hétérogènes : des règles générales, un profil par source quand il le faut, et un agent qui **propose** les réparations sans jamais les appliquer seul.

```
contrat ─► règles générales ─► contrôles ─► OK ─────────────────────────────► servi
                                    └─► A_VERIFIER ─► couverture reparer
                                                       Mistral propose un profil d'assureur
                                                       le code vérifie (lignes réelles, avant/après)
                                                    ─► couverture propositions --accepter N  (humain)
                                                    ─► relu avec le profil, réutilisé pour toutes ses versions
```

- **Chaque contrat est lu une fois**, découpé selon sa propre structure, puis rangé dans un schéma commun. Une question ne charge que les clauses du contrat concerné.
- **Les contrats mal lus sont signalés automatiquement** (`couverture ingerer` affiche les alertes) au lieu d'être servis en silence.
- **Les sinistres de test sont indépendants des contrats** (`data/sinistres.jsonl`). Ajouter un contrat, c'est ajouter un fichier d'annotations (`data/annotations/<contrat>.jsonl`) et rejouer les mêmes cas.
- **Les métadonnées** (assureur, produit, version) sont dans `data/contrats/catalogue.json`. La version compte : un client garde les CG en vigueur à sa souscription.
- **Le modèle est interchangeable** : Mistral par défaut (hébergement européen), Anthropic, ou un modèle hébergé en interne derrière une API compatible OpenAI (vLLM, Ollama…).
- **Les conditions particulières se brancheront naturellement** : « l'option est-elle souscrite ? » est une condition comme une autre, qu'on remplira depuis le contrat du client au lieu de la poser.

## Utilisation

Avec [uv](https://docs.astral.sh/uv/) (ou `pip install -e ".[dev]"`) :

```bash
uv sync --extra dev                      # environnement .venv, projet installé en mode éditable
                                         # (--extra suivi en plus pour MLflow)
# ensuite, chaque commande se lance avec « uv run » : uv run couverture modele, uv run pytest…

couverture modele                        # modèle configuré et test de connexion
couverture ingerer                       # lit data/contrats/, remplit data/base.sqlite
couverture contrats                      # contrats et statut de lecture
couverture clauses  --contrat fictif-habitat-serein
couverture analyser --contrat fictif-habitat-serein "Je me fais voler mon vélo dans le local commun de l'immeuble, qui n'était pas fermé à clé."
couverture evaluer  --contrat fictif-habitat-serein
couverture analyser --contrat foyer-appart123-2025 --methode direct "..."   # conditions (défaut), direct ou brut
couverture comparer --contrat fictif-habitat-serein    # brut, direct et conditions sur les mêmes cas (modèle requis)
couverture reparer                       # propose un profil pour les contrats à vérifier (modèle requis)
couverture versions [--manifeste | --enregistrer]   # consignes versionnées
couverture derive                        # dérive des questions et des réponses (PSI, 7 jours contre 28)
couverture bilan [--envoyer]             # à faire, contrats, activité, ce qui manque, dérive
couverture propositions [--accepter N | --refuser N]
couverture serveur                       # interface sur http://127.0.0.1:8000
pytest
```

**Modèle** : Mistral par défaut. Créer à la racine du projet un fichier `.env` contenant la clé créée sur console.mistral.ai, puis vérifier avec `couverture modele` :

```
MISTRAL_API_KEY=colle-ta-cle-ici
COUVERTURE_MODELE=mistral-large-latest
```

 Mistral est un fournisseur européen : les données restent dans l'UE. Anthropic (`ANTHROPIC_API_KEY`) et tout modèle compatible OpenAI, comme Ollama en local (`COUVERTURE_LLM_URL`), sont aussi pris en charge. Sans modèle, c'est le juge heuristique qui répond (`--hors-ligne` pour le forcer).

Déploiement : `docker compose up -d --build` lance l'application (http://localhost:8020), MLflow (http://localhost:5010) et Grafana (http://localhost:3011). Détails : [monitoring/README.md](monitoring/README.md).

## Données

- `data/contrats/` : les conditions générales. `fictif_habitat_serein.md` est un contrat **inventé** pour les tests. Les CG réelles ne sont pas versionnées : leurs liens de téléchargement sont dans `data/contrats/SOURCES.md`, et elles sont déjà référencées dans `catalogue.json`.
- `data/sinistres.jsonl` : 14 sinistres, dont les deux de l'énoncé, et des variations qui changent **un seul fait** (local fermé ou non, cave privative, flammes ou non, intérieur ou jardin). Si la réponse bascule quand le fait change, le système raisonne vraiment sur le contrat.
- `data/annotations/` : pour chaque contrat, la décision attendue et les clauses qui doivent être citées.
- `tests/fixtures/cg_style_reel.pdf` : un PDF fictif mis en page comme un vrai contrat (sommaire, en-têtes, lexique, intertitres sans numéro), pour tester la lecture.

## Résultats à ce stade

**Lecture d'un contrat réel** : Foyer appart 123 (48 pages) est découpé en 147 clauses, avec le statut `OK`. Le lexique est éclaté en 63 définitions, et les exclusions sont rattachées à leur garantie (`2.10 Garantie vol` → `2.10-a Exclusions`). Pour le vélo dans le local commun, la recherche ramène la garantie vol et l'exclusion « le vol ou le vandalisme dans les parties communes du bâtiment » (art. 2.10-a, p. 12).

**Contrat fictif, juge heuristique (sans modèle), 14 cas** : 7 décisions exactes, **0 faux « couvert »**, 0 citation rejetée, 63 % des clauses attendues citées. Le juge heuristique est volontairement prudent : il répond INCERTAIN plutôt que de se tromper.

**Recherche hybride et agent de réparation** : testés avec un faux modèle (une question sans aucun mot commun avec le contrat retrouve la garantie par le sens ; une proposition qui invente un intertitre ou effacerait une garantie est corrigée par la vérification ; rien n'est appliqué sans acceptation). Les vrais embeddings Mistral restent à mesurer.

**Juges et suivi** : testés avec de faux modèles (une relecture qui conteste une exclusion écartée évite un « couvert » à tort ; une relecture en panne laisse la décision avec un avertissement ; le juge de qualité fait passer un contrat mal typé « à vérifier » et guide la réparation ; une dérive forte sur le type d'événement et un contrat à 67 % d'INCERTAIN sont signalés ; le bilan liste les questions qui reviennent).

**Juge par conditions** : les règles de décision et le contrôle des citations sont couverts par les tests, avec un faux modèle (exclusion inventée écartée, exclusion inconnue → incertain, etc.).

**Pas encore mesuré** : les trois méthodes avec un vrai modèle, et les annotations des contrats réels. Commandes : `couverture evaluer` et `couverture comparer`.

## Limites connues

- Les conditions particulières du client (options souscrites, capitaux) ne sont pas lues. Les brancher transformerait beaucoup d'INCERTAIN en décisions fermes (« l'option vélo est-elle souscrite ? »).
- Le lexique client → contrat de `faits.py` est écrit à la main pour l'habitation.
- Le découpage repose sur des règles. Un contrat au format inhabituel sera signalé `A_VERIFIER` ; il faudra alors ajouter une règle ou un découpage assisté par le modèle.
- Les tableaux de garanties et de plafonds dans les PDF sont lus comme du texte, sans leur structure.
