# Archive des consignes

Chaque consigne envoyée au modèle est versionnée (`src/couverture/consignes.py`) et chaque
version garde ici son **texte intégral**, dans `<consigne>/<version>.txt`.

- Le fichier est écrit par `couverture versions --manifeste` et n'est **jamais réécrit**.
- Un test (donc la CI) échoue si le texte d'une version en service ne correspond plus à son
  archive : on ne modifie pas une version, on en crée une nouvelle.
- Le pourquoi de chaque changement est raconté dans [`../DEMARCHE.md`](../DEMARCHE.md).

## Historique

En service : `faits-regles` v4, `lecture-socle` v2, `lecture-details` v2, `verification-faits` v3, `redaction-regles` v11, `document-brut` v1, `legalbench` v1 (voir `config/versions_consignes.json`). Les autres sont celles des méthodes retirées le 18 nov. 2026 (DEMARCHE 7.36).

| Consigne | Version | Date | Pourquoi |
|---|---|---|---|
| `grille-conditions` | v1 | nov. 2026 | Grille complète : toutes les garanties, toutes les exclusions possibles |
| `grille-conditions` | v2 | 17 nov. 2026 | v1 jamais finie sur un vrai contrat (coupée à 8 000 tokens) : grille bornée (3 garanties, 5 exclusions, justifications courtes) |
| `grille-conditions` | v3 | 17 nov. 2026 | Défauts vus sur Assureur A : lecture du sinistre, bon objet, sens des conditions, définitions citées, trancher quand c'est possible |
| `compilation` | v1 | 17 nov. 2026 | Nouvelle méthode : chaque garantie traduite une fois en fiche de questions |
| `compilation` | v2 | 17 nov. 2026 | Questions rangées par rôle : périmètre (événement, bien, lieu), circonstances, obligations de prévention (avec lien causal), exclusions, limites |
| `exclusions-generales` | v1 | 17 nov. 2026 | Exclusions communes à toutes les garanties, « à demander » ou « présumées absentes » |
| `fiches` | v1 | 17 nov. 2026 | Répondre oui / non / inconnu à des questions déjà écrites |
| `fiches` | v2 | 17 nov. 2026 | Le rôle de chaque question est donné : un périmètre décrit et contraire vaut « non », une circonstance passée sous silence vaut « inconnu » |
| `fiches` | v3 | 17 nov. 2026 | Énumérations (« … ou … »), pièces du logement = bâtiment assuré, exclusions partielles |
| `relecture` | v2 | 17 nov. 2026 | Le relecteur répond lui-même sans voir la première réponse ; le code compare (la v1 donnait des « contestations » d'accord) |
| `faits-regles` | v1 | 17 nov. 2026 | Lire une déclaration dans le vocabulaire commun des règles Prolog ; ce qu'elle ne dit pas reste inconnu |
| `faits-regles` | v2 | 17 nov. 2026 | Événement à plusieurs valeurs (la cause et le dommage), durées traduites, fenêtres et mesures contre le gel (après le jeu de validation, 7.17) |
| `faits-regles` | v3 | 17 nov. 2026 | Le sens de chaque variable et des valeurs proches est donné ; interdiction d'inventer un lieu, une absence, une cause ; faits hors sujet retirés par le code (7.24) |
| `faits-regles` | v4 | 17 nov. 2026 | Rétablit la déduction « pièce du logement → lieu = logement », supprimée par erreur en v3 ; « disparu » n'est pas « volé » (7.24 bis) |
| `faits-regles` | v5 | 17 nov. 2026 | Appuis : pour chaque fait, les mots exacts de la déclaration ; le code retire tout fait sans appui (7.26). **Abandonnée** : retirait trop de faits justes ; retour à la v4 |
| `redaction-regles` | v1 | 17 nov. 2026 | Mistral Large traduit une garantie en règles : schéma JSON, vocabulaire imposé, faits manquants et phrases non traduites déclarés |
| `redaction-regles` | v2 | 17 nov. 2026 | Après la première rédaction réelle : exemples de définition et de limite, définition de l'événement couvert comme condition (7.20) |
| `redaction-regles` | v3 | 18 nov. 2026 | Exclusions communes à toutes les garanties d'un article ; vocabulaire donné avec ses questions ; « la plus proche » des variables existantes (7.53) |
| `redaction-regles` | v4 | 18 nov. 2026 | Condition toujours enveloppée avec sa citation, après des conditions rendues « nues » (7.54) |
| `redaction-regles` | v5 | 18 nov. 2026 | Réserves « à moins que… » et « à l'extérieur » traduits sans tuer les autres garanties (7.58) |
| `redaction-regles` | v6 | 19 nov. 2026 | Une aide de lecture par valeur, proposée avec chaque variable nouvelle (7.62) |
| `redaction-regles` | v7 | 19 nov. 2026 | Une valeur nouvelle dit de quelle valeur existante elle précise le sens (`parent`) (7.64) |
| `redaction-regles` | v8 | 19 nov. 2026 | Garanties accessoires : ce qui s'ajoute à un sinistre couvert, sans décider s'il l'est (7.68) |
| `redaction-regles` | v9 | 19 nov. 2026 | Extensions de définition (un lieu ou un bien assuré élargi) ; le périmètre d'une accessoire ne dit pas « sinistre » (7.69) |
| `redaction-regles` | v10 | 19 nov. 2026 | Le concept d'une extension vient de ce contrat ; les dégâts causés par l'assuré au bien d'un autre sont de la responsabilité ; un pays par valeur (7.72) |
| `redaction-regles` | v11 | 19 nov. 2026 | Une sanction qui réduit l'indemnité est une limite, pas une obligation (7.81) |
| `lecture-socle`, `lecture-details` | v1 | 18 nov. 2026 | La lecture v4 coupée en deux temps : l'événement, le bien et le lieu, puis les seules questions de cet événement (7.38) |
| `lecture-socle`, `lecture-details` | v2 | 18 nov. 2026 | Chaque variable propose d'abord la valeur « inconnu » : le schéma poussait à remplir (7.40) |
| `verification-faits` | v1 | 18 nov. 2026 | Chaque fait lu soumis au modèle comme une affirmation ; un fait « non dit » redevient inconnu (7.43) |
| `verification-faits` | v2 | 19 nov. 2026 | Une négation écrite, ou un détail qui correspond au sens donné de la valeur (« un simple cadenas »), est « dit » (7.75) |
| `verification-faits` | v3 | 19 nov. 2026 | La souplesse de v2 limitée aux « non » ; pour les autres valeurs, le sens et ce qu'il écarte, pas un mot commun (7.77) |
| `legalbench` | v1 | 18 nov. 2026 | Second banc, externe : répondre et citer la phrase de la clause (7.34) |
| `faits` | v1 | 17 nov. 2026 | Événement, bien et lieu extraits par le modèle, pour choisir les fiches |
| `routage` | v1 | 17 nov. 2026 | Choisir les fiches quand l'événement n'est pas reconnu dans la déclaration |
| `relecture`, `verdict-direct`, `document-brut`, `juge-qualite`, `reparation` | v1 | nov. 2026 | Versions d'origine |
| `verdict-direct` | — | 17 nov. 2026 | Retirée avec la méthode « direct » ; v1 archivée |
