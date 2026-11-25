# Jeu « quatre » : le quatrième jeu écrit sans voir les règles (DEMARCHE 7.187)

Le troisième jeu (`data/neuf`) a mesuré une fois, à l'aveugle, puis ses erreurs ont servi à corriger des règles
et le vocabulaire : il est « vu ». Celui-ci est gardé pour mesurer la refonte de la décision (DEMARCHE 7.188),
face à la chaîne actuelle ; aucun banc n'est lancé dessus avant. 60 déclarations (20 pour
A, 20 pour B, 20 pour D), écrites le 25 novembre 2026 vers 12 h 45 par trois agents Claude neufs, un par contrat,
qui n'ont lu que le texte des conditions générales. Mêmes consignes que pour le troisième jeu (chercher des
situations peu courantes ; celles des deux jeux précédents leur ont été nommées, pour qu'ils n'y retombent pas).

**Règle : ce jeu ne sert qu'à mesurer.** Aucun de ses cas ne sert à régler le vocabulaire, les règles ou les
exemples de lecture. Un cas n'est pas corrigé après avoir vu la réponse du système.

| Fichier | Contenu |
|---|---|
| `cas_agent.jsonl` | les 60 déclarations et la réponse du premier annotateur, avec l'article et la citation |
| `avis_second.jsonl` | la réponse du second annotateur (Mistral Large), sans voir la première |
| `avis_claude.jsonl` | un troisième avis, indépendant du modèle qui lit dans la nouvelle méthode : Claude (Opus 5.5), le 25 nov. 2026 vers 23 h, sans voir les deux autres ni aucune réponse du système, après le gel du code (DEMARCHE 7.206) |
| `arbitrage.csv` | les désaccords ; colonne `choix` : `agent`, `second` ou `ecarter` |
| `sinistres.jsonl`, `annotations/` | le jeu final (accords et arbitrages), au format du banc, sans faits idéaux |

Convention : les garanties de base sont souscrites ; les options, packs et formules sont inconnus (« incertain »
si la réponse en dépend).

```
uv run python -m couverture.mesure.ferme --jeu quatre annoter
uv run python -m couverture.mesure.ferme --jeu quatre comparer
# remplir la colonne « choix » d'arbitrage.csv, d'après les deux citations
uv run python -m couverture.mesure.ferme --jeu quatre exporter
uv run couverture banc --contrat assureur-a-habitation-2025 --jeu quatre
uv run couverture banc --contrat assureur-b-habitation-2017 --jeu quatre
uv run couverture banc --contrat assureur-d-habitation-2026 --jeu quatre
```

**Accord des annotateurs** : les trois avis donnent la même réponse sur les 60 cas (accord strict, 60 sur 60) ; aucun arbitrage n'a été nécessaire.
