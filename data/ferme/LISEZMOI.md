# Jeu fermé : des cas écrits sans voir les règles (DEMARCHE 7.79)

Le golden set a été écrit par Claude après avoir lu les règles : il mesure si le moteur applique les règles, pas
si les règles disent le contrat. Ce jeu-ci est écrit **à partir du seul texte des conditions générales**, par deux
annotateurs qui n'ont vu ni les règles ni le golden set.

| Fichier | Contenu |
|---|---|
| `cas_agent.jsonl` | 40 déclarations (20 par assureur) et la réponse du premier annotateur (un agent Claude neuf, qui n'a lu que le texte des CG, noms anonymisés), avec l'article et la citation |
| `avis_second.jsonl` | la réponse du second annotateur (Mistral Large), sur les mêmes déclarations, sans voir la première |
| `arbitrage.csv` | les désaccords, avec les deux réponses et leurs citations ; colonne `choix` : `agent`, `second` ou `ecarter` |
| `sinistres.jsonl`, `annotations/` | le jeu final (accords + arbitrages), au format du banc, **sans faits idéaux** |

Convention : les garanties de base sont souscrites ; les options et formules sont inconnues (« incertain » si la
réponse en dépend).

```
uv run python -m couverture.mesure.ferme annoter      # second avis (Mistral Large ; reprend s'il est interrompu)
uv run python -m couverture.mesure.ferme comparer     # accords ; désaccords dans arbitrage.csv
# remplir la colonne « choix » d'arbitrage.csv, d'après les deux citations
uv run python -m couverture.mesure.ferme exporter
uv run couverture banc --contrat assureur-a-habitation-2025 --jeu ferme
uv run couverture banc --contrat assureur-b-habitation-2017 --jeu ferme
```

Règle : un cas n'est pas corrigé après avoir vu la réponse du système, sauf erreur sur le texte du contrat
(à noter dans DEMARCHE). `cas_fermes.csv`, le gabarit vide du 19 nov., n'est plus utilisé.
