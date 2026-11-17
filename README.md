# Couverture sinistre

Un système qui dit si un sinistre est couvert par un contrat d'assurance habitation, **pourquoi**, et **sur quelles clauses** il s'appuie. Quand le contrat ne permet pas de trancher, il répond **INCERTAIN** et dit ce qu'il faut vérifier.

> Une réponse assurée sans justification vaut moins qu'un « je ne sais pas » étayé.

Explication détaillée de chaque fichier, lexique et choix : [docs/EXPLICATIONS.md](docs/EXPLICATIONS.md). Suivi en production : [monitoring/README.md](monitoring/README.md).

## Pourquoi pas « le PDF dans un chatbot »

Coller le contrat dans un prompt marche sur un contrat, puis s'effondre :
- **L'exclusion ne ressemble pas à la question.** « Vol de vélo » ramène « les vélos sont garantis ». L'exclusion des parties communes est dans une autre clause, et la définition de « parties communes » est au lexique.
- **Chaque assureur rédige autrement** (numérotation, intertitres, place des exclusions), et un prompt réglé sur un contrat casse sur le suivant.
- **Rien n'est vérifiable** : le modèle peut citer une clause qui n'existe pas, ou une clause qui existe mais ne dit pas ce qu'il prétend, et on ne s'en aperçoit pas.

Le système fait donc le travail difficile **une fois par contrat**, à l'ingestion, puis raisonne sur des clauses structurées, et vérifie chaque preuve par du code et par une seconde lecture.

## Les étapes

```
Une fois par contrat
  PDF ─► nettoyage ─► découpage en clauses typées ─► contrôles ─► juge de qualité ─► base SQLite + embeddings
                      (+ profil d'assureur)            └─ mal lu ? ─► agent de réparation ─► validation humaine

À chaque sinistre
  description ─► faits ─► recherche hybride + enveloppe du contrat ─► grille de conditions (modèle)
              ─► citations vérifiées ─► décision calculée ─► relecture des conditions décisives ─► réponse ─► journal

Chaque semaine
  journal ─► dérive (PSI) ─► bilan            en continu : MLflow (exécutions, consignes) et Grafana
```

| Étape | Module | Ce qu'elle fait |
|---|---|---|
| Lecture | `chargement.py` | PDF, Word ou Markdown → lignes avec leur page. Retire le sommaire, les en-têtes et pieds de page répétés, recolle les mots coupés. |
| Découpage | `segmentation.py` | Une clause = une unité du contrat : articles numérotés (`4.3`), intertitres sans numéro (« Ce que nous ne garantissons pas » → `2.2-b`), titres en capitales. Le lexique est éclaté en une clause par terme. Chaque clause est typée (garantie, exclusion, condition, limite, définition) et garde ses renvois (« au sens de l'article 1.5 »). |
| Profils | `profils.py` | Les règles de lecture propres à un assureur (ses intertitres, ses lignes de bruit, son format de lexique), dans un fichier JSON, sans toucher au code. |
| Contrôles | `controles.py` | Repère les contrats mal lus : trop peu de clauses, aucune exclusion, titres non reconnus, renvois cassés. Statut `OK` ou `A_VERIFIER`. |
| Qualité | `qualite.py` | **Juge de qualité** : Mistral relit un échantillon de clauses et dit si leur type est juste. Sous 80 %, le contrat passe « à vérifier ». |
| Réparation | `reparation.py` | Pour un contrat mal lu : diagnostic, profil proposé par Mistral, vérifié par le code (lignes réelles, avant/après), **appliqué seulement après validation humaine**. |
| Stockage | `base.py`, `ingestion.py` | Tables `contrats`, `clauses`, `renvois`, `vecteurs`. Un contrat inchangé n'est pas relu ; les embeddings sont calculés une seule fois. Les questions sont toujours filtrées sur un contrat. |
| Faits | `faits.py` | Événement, bien, lieu, circonstances, traduits en vocabulaire du contrat (« local commun » → parties communes). |
| Recherche | `recherche.py` | **Hybride** : BM25 (les mots) et `mistral-embed` (le sens), fusionnés par RRF, comme dans SortirIA. Puis **l'enveloppe du contrat** : exclusions et conditions de la garantie trouvée, exclusions générales, clauses visées par un renvoi, définitions des termes employés. |
| Grille | `conditions.py` | Le modèle ne dit pas « couvert ou non ». Il remplit une grille : pour chaque garantie possible, ses conditions, et chaque exclusion possible, avec un état (`REMPLIE`, `NON_REMPLIE`, `INCONNUE`), le passage exact du contrat et le fait du sinistre qui le fonde. |
| Contrôle des citations | `validation.py`, `conditions.py` | Chaque passage cité doit exister mot pour mot dans une clause fournie, sinon la condition est écartée. Le type de clause vient du contrat, pas du modèle. |
| Décision | `conditions.py` | **Calculée par des règles**, pas devinée (voir ci-dessous). Sans modèle, `JugeHeuristique` prend le relais et ne tranche que les cas nets. |
| Relecture | `relecture.py` | **Juge de la grille** : un second appel, qui ne voit pas la décision, vérifie que chaque passage décisif **justifie** l'état donné. Une condition contestée redevient inconnue et la décision est recalculée : la relecture ne peut que rendre la réponse plus prudente. |
| Journal, dérive, bilan | `journal.py`, `derive.py`, `bilan.py` | Chaque analyse est journalisée (sans le texte du sinistre). La dérive compare la semaine aux 4 précédentes (PSI). Le bilan dit d'abord ce qui demande une intervention. |
| MLflow | `suivi.py`, `consignes.py` | Une exécution par ingestion et par évaluation. Les consignes sont versionnées : un texte modifié sans nouvelle version fait échouer la CI ; `couverture versions --enregistrer` les inscrit au Prompt Registry. Jamais bloquant. |
| Grafana | `monitoring/grafana/` | Deux tableaux (Réponses, Contrats) lus dans la base SQLite, générés par un script dont chaque requête est testée. |
| Référence | `pipeline.py` (`PipelineDocumentBrut`) | Le contrat entier dans le prompt, sans recherche : la méthode à battre. |

## La décision : condition par condition

Un gestionnaire ne se demande pas « est-ce couvert ? » d'un bloc. Il vérifie une grille. Le système fait pareil.

1. Le modèle confronte chaque condition au sinistre. Par exemple, pour le vélo volé dans le local commun, sur le contrat Foyer appart 123 (illustration de la forme de la grille, pas encore un résultat mesuré) :
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
4. La relecture contrôle les conditions qui ont décidé. Pour un « couvert », elle relit aussi les exclusions écartées : c'est là que se cache le « couvert » à tort, l'erreur la plus coûteuse.

« Je ne sais pas » n'est donc pas une hésitation du modèle : c'est une condition dont l'état est inconnu, et on sait laquelle. Chaque étape est petite et vérifiable ; un modèle se trompe bien moins sur « ce fait remplit-il cette condition ? » que sur « ce sinistre est-il couvert par ce contrat de 48 pages ? ».

Trois méthodes sont comparables sur les mêmes cas (`couverture comparer`) :
- `brut` : le contrat entier collé dans le prompt (le chatbot) ;
- `direct` : les clauses retenues, puis un verdict du modèle en un coup ;
- `conditions` : la grille, la décision calculée et la relecture (méthode par défaut).

## Les agents et les juges

Repris de l'organisation de SortirIA, chacun à un endroit précis et contrôlé :

| Rôle | Quand | Ce qu'il fait | Garde-fou |
|---|---|---|---|
| Juge de qualité | ingestion, une fois par contrat | vérifie le type d'un échantillon de clauses | ne bloque jamais ; sous le seuil, le contrat passe « à vérifier » |
| Agent de réparation | contrat « à vérifier » | propose un profil d'assureur | vérifié par le code, appliqué seulement par un humain |
| Juge des conditions | chaque sinistre | remplit la grille, sans conclure | citations vérifiées, décision calculée par des règles |
| Juge de la grille (relecture) | chaque sinistre, sauf INCERTAIN | relit les conditions décisives | ne peut que rendre la réponse plus prudente |
| MLflow et Grafana | en continu | suivent chaque ingestion, évaluation et réponse, avec les versions qui les ont produites | lecture seule ; le suivi ne bloque jamais |
| Dérive et bilan | chaque semaine | signalent ce qui change et ce qui demande une intervention | lecture seule |

Pas de LangGraph : la chaîne est linéaire. Le graphe de SortirIA se justifiait par la collecte nocturne (nouvelles tentatives, branches, pannes de sources).

## Tenir des centaines de contrats

La vraie difficulté n'est pas la réponse, c'est la lecture de contrats tous rédigés différemment. Le système la traite comme SortirIA traitait des dizaines d'agendas hétérogènes : des règles générales, un profil par source quand il le faut, et un agent qui **propose** les réparations sans jamais les appliquer seul.

```
contrat ─► règles générales ─► contrôles + juge de qualité ─► OK ──────────────────────────► servi
                                         └─► A_VERIFIER ─► couverture reparer
                                                            Mistral propose un profil d'assureur
                                                            le code vérifie (lignes réelles, avant/après)
                                                         ─► couverture propositions --accepter N  (humain)
                                                         ─► relu avec le profil, réutilisé pour toutes ses versions
```

- **Chaque contrat est lu une fois**, découpé selon sa propre structure, puis rangé dans un schéma commun. Une question ne charge que les clauses du contrat concerné.
- **Les contrats mal lus sont signalés automatiquement** au lieu d'être servis en silence.
- **Les sinistres de test sont indépendants des contrats** (`data/sinistres.jsonl`). Ajouter un contrat, c'est ajouter un fichier d'annotations (`data/annotations/<contrat>.jsonl`) et rejouer les mêmes cas.
- **Les métadonnées** (assureur, produit, version, profil) sont dans `data/contrats/catalogue.json`. La version compte : un client garde les CG en vigueur à sa souscription.
- **Le modèle est interchangeable** : Mistral par défaut (hébergement européen), Anthropic, ou un modèle hébergé en interne derrière une API compatible OpenAI (vLLM, Ollama…).
- **Les conditions particulières se brancheront naturellement** : « l'option est-elle souscrite ? » est une condition comme une autre, qu'on remplira depuis le contrat du client au lieu de la poser.

## Installation et utilisation

Avec [uv](https://docs.astral.sh/uv/) :

```bash
uv sync --extra dev                  # crée .venv ; ajouter --extra suivi pour MLflow
cp .env.example .env                 # puis y mettre la clé Mistral (console.mistral.ai)
uv run pytest -q
```

Le fichier `.env` (jamais versionné) contient au minimum :

```
MISTRAL_API_KEY=votre-clé
COUVERTURE_MODELE=mistral-large-latest
```

Mistral est un fournisseur européen : les données restent dans l'UE. Anthropic (`ANTHROPIC_API_KEY`) et tout modèle compatible OpenAI, comme Ollama en local (`COUVERTURE_LLM_URL`), sont aussi pris en charge. Sans modèle, c'est le juge heuristique qui répond (`--hors-ligne` pour le forcer).

```bash
uv run couverture modele                  # modèle configuré, test de connexion (génération et embeddings)
uv run couverture ingerer                 # lit data/contrats/, remplit data/base.sqlite
uv run couverture contrats                # contrats et statut de lecture
uv run couverture clauses  --contrat foyer-appart123-2025
uv run couverture analyser --contrat foyer-appart123-2025 "Je me fais voler mon vélo dans le local commun de l'immeuble, qui n'était pas fermé à clé."
uv run couverture analyser --contrat foyer-appart123-2025 --methode direct "..."   # conditions (défaut), direct ou brut
uv run couverture evaluer  --contrat fictif-habitat-serein
uv run couverture comparer --contrat fictif-habitat-serein   # brut, direct et conditions sur les mêmes cas
uv run couverture reparer                 # propose un profil pour les contrats à vérifier
uv run couverture propositions [--accepter N | --refuser N]
uv run couverture versions [--manifeste | --enregistrer]     # consignes versionnées
uv run couverture derive                  # dérive (PSI, 7 jours contre 28)
uv run couverture bilan [--envoyer]       # à faire, contrats, activité, ce qui manque, dérive
uv run couverture serveur                 # interface sur http://127.0.0.1:8000
```

Avec docker : `docker compose up -d --build` lance l'application (http://localhost:8020), MLflow (http://localhost:5010) et Grafana (http://localhost:3011). Détails : [monitoring/README.md](monitoring/README.md).

## Arborescence

```
src/couverture/        le code (un module par étape, voir le tableau ci-dessus)
  static/index.html    l'interface
data/
  contrats/            conditions générales, catalogue.json, SOURCES.md (liens des CG réelles)
  sinistres.jsonl      les 14 sinistres de test
  annotations/         la réponse attendue, contrat par contrat
config/                manifeste des versions des consignes
monitoring/            Grafana (tableaux générés et testés) et guide du suivi
docs/EXPLICATIONS.md   chaque fichier, chaque choix, lexique, questions d'entretien
tests/                 tests (pytest) et un PDF de contrat fictif mis en page comme un vrai
```

## Données

- `data/contrats/` : les conditions générales. `fictif_habitat_serein.md` est un contrat **inventé** pour les tests. Les CG réelles ne sont pas versionnées (documents des assureurs) : leurs liens sont dans `data/contrats/SOURCES.md`, et elles sont déjà référencées dans `catalogue.json`. Les CG de Foyer Mozaïk (Luxembourg) ne sont pas publiques ; le projet utilise les CG publiques de Foyer « appart 123 ».
- `data/sinistres.jsonl` : 14 sinistres, dont les deux de l'énoncé, et des variations qui changent **un seul fait** (local fermé ou non, cave privative, flammes ou non, intérieur ou jardin). Si la réponse bascule quand le fait change, le système raisonne vraiment sur le contrat.
- `data/annotations/` : pour chaque contrat, la décision attendue et les clauses qui doivent être citées.

## Résultats à ce stade

**Tests** : 62 tests passent, sous Linux et sous Windows. La CI les relance à chaque envoi, avec deux garde-fous : une consigne modifiée sans nouvelle version, ou un tableau Grafana non régénéré, la font échouer.

**Lecture d'un contrat réel** : Foyer appart 123 (48 pages) est découpé en 147 clauses, avec le statut `OK`. Le lexique est éclaté en 63 définitions, et les exclusions sont rattachées à leur garantie (`2.10 Garantie vol` → `2.10-a Exclusions`). Pour le vélo dans le local commun, la recherche ramène la garantie vol et l'exclusion « le vol ou le vandalisme dans les parties communes du bâtiment » (art. 2.10-a, p. 12).

**Contrat fictif, juge heuristique (sans modèle), 14 cas** : 7 décisions exactes, **0 faux « couvert »**, 0 citation rejetée, 63 % des clauses attendues citées. Le juge heuristique est volontairement prudent : il répond INCERTAIN plutôt que de se tromper.

**Juges, recherche hybride, réparation, suivi** : testés avec de faux modèles. Une relecture qui conteste une exclusion écartée évite un « couvert » à tort ; une question sans aucun mot commun avec le contrat retrouve la garantie par le sens ; une proposition de réparation qui invente un intertitre ou effacerait une garantie est corrigée par la vérification ; un contrat mal typé passe « à vérifier » ; une dérive forte est signalée.

**Pas encore mesuré** : les trois méthodes avec Mistral (`couverture comparer`), les vrais embeddings, les deux juges et l'agent de réparation sur de vrais contrats, et les annotations du contrat Foyer.

## Limites connues

- Les conditions particulières du client (options souscrites, capitaux) ne sont pas lues. Les brancher transformerait beaucoup d'INCERTAIN en décisions fermes.
- Le lexique client → contrat de `faits.py` est écrit à la main pour l'habitation ; la recherche par le sens le complète, mais l'extraction des faits reste à confier au modèle.
- Le découpage repose sur des règles et des profils d'assureur ; un format sans aucun titre reconnaissable dépassera ce qu'un profil peut décrire.
- Les tableaux de garanties et de plafonds dans les PDF sont lus comme du texte, sans leur structure.
- Le relecteur est, par défaut, le même modèle que le juge principal (un autre modèle se configure avec `COUVERTURE_MODELE_RELECTURE`).
- La dérive n'a de sens qu'après plusieurs semaines d'utilisation réelle.
