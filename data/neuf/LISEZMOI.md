# Jeu « neuf » : le troisième jeu écrit sans voir les règles (DEMARCHE 7.186)

Le second jeu (`data/aveugle`) a mesuré une fois, à l'aveugle, puis ses erreurs ont servi à corriger des règles
et le vocabulaire : il est « vu ». Celui-ci mesure ce que valent ces corrections sur des cas qu'elles n'ont pas
regardés : 60 déclarations (20 pour A, 20 pour B, 20 pour D), écrites le 25 novembre 2026 à midi par trois
agents Claude neufs, un par contrat, qui n'ont lu que le texte des conditions générales. Mêmes consignes que
pour le second jeu, avec une demande de plus : éviter les situations rebattues (celles du second jeu leur ont
été nommées, pour qu'ils n'y retombent pas).

**Règle : ce jeu ne sert qu'à mesurer.** Aucun de ses cas ne sert à régler le vocabulaire, les règles ou les
exemples de lecture. Un cas n'est pas corrigé après avoir vu la réponse du système.

| Fichier | Contenu |
|---|---|
| `cas_agent.jsonl` | les 60 déclarations et la réponse du premier annotateur, avec l'article et la citation |
| `avis_second.jsonl` | la réponse du second annotateur (Mistral Large), sans voir la première |
| `arbitrage.csv` | les désaccords ; colonne `choix` : `agent`, `second` ou `ecarter` |
| `sinistres.jsonl`, `annotations/` | le jeu final (accords et arbitrages), au format du banc, sans faits idéaux |

Mesure du 25 novembre, 12 h 37, la seule à l'aveugle : A 60 % de réponses justes (4 couverts à tort), B 50 % (2),
D 80 % (1). Second avis : 57 accords sur 60 ; trois désaccords arbitrés par un troisième lecteur du texte.

Convention : les garanties de base sont souscrites ; les options, packs et formules sont inconnus (« incertain »
si la réponse en dépend).

```
uv run python -m couverture.mesure.ferme --jeu neuf annoter
uv run python -m couverture.mesure.ferme --jeu neuf comparer
# remplir la colonne « choix » d'arbitrage.csv, d'après les deux citations
uv run python -m couverture.mesure.ferme --jeu neuf exporter
uv run couverture banc --contrat assureur-a-habitation-2025 --jeu neuf
uv run couverture banc --contrat assureur-b-habitation-2017 --jeu neuf
uv run couverture banc --contrat assureur-d-habitation-2026 --jeu neuf
```
