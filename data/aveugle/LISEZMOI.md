# Jeu « aveugle » : un second jeu écrit sans voir les règles (DEMARCHE 7.185)

Le premier jeu fermé (`data/ferme`, 7.79) a servi depuis le 19 novembre, et trois de ses cas ont fini par être
regardés pour corriger une règle. Celui-ci est neuf : 60 déclarations (20 pour A, 20 pour B, 20 pour D), écrites
le 25 novembre 2026 par trois agents Claude neufs, un par contrat, qui n'ont lu que le texte des conditions
générales (noms anonymisés) : ni les règles, ni le vocabulaire, ni les autres jeux.

**Ce jeu a mesuré une fois, à l'aveugle, le 25 novembre à 11 h 37** (chiffres ci-dessous). Ensuite ses erreurs ont
été lues et neuf corrections en ont été tirées (DEMARCHE 7.186) : depuis, ses 60 cas sont des cas **vus**, et un
banc relancé sur lui ne mesure plus que ces corrections. Le jeu jamais regardé est `data/neuf`.

| Fichier | Contenu |
|---|---|
| `cas_agent.jsonl` | les 60 déclarations et la réponse du premier annotateur, avec l'article et la citation |
| `avis_second.jsonl` | la réponse du second annotateur (Mistral Large), sans voir la première |
| `arbitrage.csv` | les désaccords ; colonne `choix` : `agent`, `second` ou `ecarter` |
| `sinistres.jsonl`, `annotations/` | le jeu final (accords et arbitrages), au format du banc, sans faits idéaux |

Mesure du 25 novembre, 11 h 37, la seule : A 95 % de réponses justes (0 couvert à tort), B 58 % (1 à 2), D 78 % (2).
Second avis : 59 accords sur 60 ; le désaccord (`av-a09`) arbitré par un troisième lecteur du texte.
Un cas, `av-d13`, ressemble par hasard à un exemple de lecture antérieur (`ex-d14`) : déclaré dans
`data/lecture/proches_declares.json`.

Convention : les garanties de base sont souscrites ; les options, packs et formules sont inconnus (« incertain »
si la réponse en dépend).

```
uv run python -m couverture.mesure.ferme --jeu aveugle annoter
uv run python -m couverture.mesure.ferme --jeu aveugle comparer
# remplir la colonne « choix » d'arbitrage.csv, d'après les deux citations
uv run python -m couverture.mesure.ferme --jeu aveugle exporter
uv run couverture banc --contrat assureur-a-habitation-2025 --jeu aveugle
uv run couverture banc --contrat assureur-b-habitation-2017 --jeu aveugle
uv run couverture banc --contrat assureur-d-habitation-2026 --jeu aveugle
```
