# Jeu « cinq » : le cinquième jeu écrit sans voir les règles (DEMARCHE 7.215)

Le quatrième jeu (`data/quatre`) a mesuré une fois les deux méthodes (7.207), puis ses écarts ont servi au dernier
tour de justesse (7.210 à 7.214) : il est « vu ». Celui-ci mesure ce tour, une seule fois, les deux méthodes côte à
côte. 60 déclarations (20 pour A, 20 pour B, 20 pour D), écrites le 26 novembre 2026 vers 13 h 20 par trois agents
Claude neufs, un par contrat, qui n'ont lu que le texte des conditions générales et la liste des déclarations des
jeux précédents (pour ne pas y retomber). Par contrat : 7 couverts, 7 non couverts, 6 incertains.

**Règle : ce jeu ne sert qu'à mesurer.** Aucun de ses cas ne sert à régler le vocabulaire, les règles, les
consignes ou les exemples de lecture. Un cas n'est pas corrigé après avoir vu la réponse du système.
`juger --jeu cinq` refuse de partir sans `--mesure-finale`.

| Fichier | Contenu |
|---|---|
| `cas_agent.jsonl` | les 60 déclarations et la réponse du premier annotateur, avec l'article et la citation |
| `avis_second.jsonl` | la réponse du second annotateur, sans voir la première : trois autres agents Claude neufs, un par contrat. Pas Mistral Large cette fois : c'est le modèle qui lit dans la méthode mesurée |
| `arbitrage.csv` | le désaccord ; colonne `choix` : `agent`, `second` ou `ecarter` |
| `sinistres.jsonl`, `annotations/` | le jeu final (accords et arbitrage), au format du banc, sans faits idéaux |

Convention : les garanties de base sont souscrites ; les options, packs et formules sont inconnus (« incertain »
si la réponse en dépend). Chaque citation des deux avis a été retrouvée mot pour mot dans le texte.

**Accord des annotateurs** : 56 accords stricts, 3 souples, 1 désaccord (`c-a20`, un locataire qui perce un tuyau
encastré : « incertain » pour le premier, la responsabilité locative pouvant ne pas être souscrite ; « couvert »
pour le second). Un septième agent neuf, qui n'a reçu que le texte et les deux avis, a retenu le second : chez A,
responsabilité locative et contenu sont les deux couvertures de base, pas des options. Aucun cas écarté.

```
uv run couverture banc --contrat assureur-a-habitation-2025 --jeu cinq
uv run couverture banc --contrat assureur-b-habitation-2017 --jeu cinq
uv run couverture banc --contrat assureur-d-habitation-2026 --jeu cinq
uv run couverture juger --contrat assureur-a-habitation-2025 --jeu cinq --regles --mesure-finale
uv run couverture juger --contrat assureur-b-habitation-2017 --jeu cinq --regles --mesure-finale
uv run couverture juger --contrat assureur-d-habitation-2026 --jeu cinq --regles --mesure-finale
```
