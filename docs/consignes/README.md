# Archive des consignes

Chaque consigne envoyée au modèle est versionnée (`src/couverture/consignes.py`) et chaque
version garde ici son **texte intégral**, dans `<consigne>/<version>.txt`.

- Le fichier est écrit par `couverture versions --manifeste` et n'est **jamais réécrit**.
- Un test (donc la CI) échoue si le texte d'une version en service ne correspond plus à son
  archive : on ne modifie pas une version, on en crée une nouvelle.
- Le pourquoi de chaque changement est raconté dans [`../DEMARCHE.md`](../DEMARCHE.md).

## Historique

| Consigne | Version | Date | Pourquoi |
|---|---|---|---|
| `grille-conditions` | v1 | nov. 2026 | Grille complète : toutes les garanties, toutes les exclusions possibles |
| `grille-conditions` | v2 | 17 nov. 2026 | v1 jamais finie sur un vrai contrat (coupée à 8 000 tokens) : grille bornée (3 garanties, 5 exclusions, justifications courtes) |
| `grille-conditions` | v3 | 17 nov. 2026 | Défauts vus sur Foyer : lecture du sinistre, bon objet, sens des conditions, définitions citées, trancher quand c'est possible |
| `compilation` | v1 | 17 nov. 2026 | Nouvelle méthode : chaque garantie traduite une fois en fiche de questions |
| `exclusions-generales` | v1 | 17 nov. 2026 | Exclusions communes à toutes les garanties, « à demander » ou « présumées absentes » |
| `fiches` | v1 | 17 nov. 2026 | Répondre oui / non / inconnu à des questions déjà écrites |
| `routage` | v1 | 17 nov. 2026 | Choisir les fiches quand l'événement n'est pas reconnu dans la déclaration |
| `relecture`, `verdict-direct`, `document-brut`, `juge-qualite`, `reparation` | v1 | nov. 2026 | Versions d'origine |
