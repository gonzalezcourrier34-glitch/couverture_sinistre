# Jeu « six » : le sixième jeu écrit sans voir les règles (DEMARCHE 7.226)

Écrit pour mesurer la consigne de jugement v2 de la lecture des clauses (deux règles de lecture : une cause
seulement probable n'est pas établie ; une garantie qui pose une condition ne « couvre » que si la déclaration
l'établit). Les deux règles ont été écrites avant les cas, sans les voir. 60 déclarations (20 pour A, 20 pour B,
20 pour D), écrites le 27 novembre 2026 vers 20 h par trois agents Claude neufs, un par contrat, qui n'ont lu que le
texte des conditions générales et la liste des 456 déclarations des jeux précédents (pour ne pas y retomber). Par
contrat : 7 couverts, 7 non couverts, 6 incertains ; au moins six cas par contrat se jouent sur un détail fin (une
condition dite ou non dite, une cause établie ou seulement probable). Ni les règles, ni le code, ni les consignes.

**Règle : ce jeu ne sert qu'à mesurer.** Aucun de ses cas ne sert à régler le vocabulaire, les règles, les
consignes ou les exemples de lecture. Un cas n'est pas corrigé après avoir vu la réponse du système.
`juger --jeu six` refuse de partir sans `--mesure-finale`.

| Fichier | Contenu |
|---|---|
| `cas_agent.jsonl` | les 60 déclarations et la réponse du premier annotateur, avec l'article et la citation |
| `avis_second.jsonl` | la réponse du second annotateur, sans voir la première : trois autres agents Claude neufs, un par contrat |
| `sinistres.jsonl`, `annotations/` | le jeu final, au format du banc, sans faits idéaux |

Convention : les garanties de base sont souscrites ; les options, packs et formules sont inconnus (« incertain »
si la réponse en dépend). Chaque citation des deux avis a été retrouvée mot pour mot dans le texte (sauts de ligne
remplacés par des espaces).

**Accord des annotateurs** : 60 accords sur la réponse attendue, aucun arbitrage. Une réponse de plus n'est
« acceptable » que si les deux annotateurs l'ont proposée (un cas : `s-a03`, l'ascenseur, aussi défendable en
« couvert ») ; cinq fois, le second seul en proposait une (`s-a19`, `s-d03`, `s-d06`, `s-d12`, `s-d15`) : accord
souple, non retenue. Aucun cas écarté.

La v2 (en service) sur les 60 cas, puis la v1 (`--consigne-jugement v1`) sur les seuls cas que la v2 laisse
« à préciser » : les deux règles ne changent qu'un « couvre » en « à vérifier », leur effet ne peut se voir que là.

```
foreach ($c in "assureur-a-habitation-2025","assureur-b-habitation-2017","assureur-d-habitation-2026") {
  uv run couverture juger --contrat $c --jeu six --regles --mesure-finale }
foreach ($c in "assureur-a-habitation-2025","assureur-b-habitation-2017","assureur-d-habitation-2026") {
  $b = Get-Content "data\debug\juger_bilan_${c}_six_mistral-large-latest.json" -Raw | ConvertFrom-Json
  $cas = $b.cas | Where-Object { $_.obtenu -eq "INCERTAIN" } | ForEach-Object { "--cas"; $_.id }
  if ($cas) { uv run couverture juger --contrat $c --jeu six --regles --mesure-finale --consigne-jugement v1 @cas } }
```
