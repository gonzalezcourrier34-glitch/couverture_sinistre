# Interface de couverture des sinistres (Angular)

Reprise de l'interface de SortirIA : Angular 21 en composants autonomes, signaux, proxy `/api` vers l'API
FastAPI. Couleurs et police du système de design public de foyer.lu (variables `--fds-*`, police Barlow) ; ni logo,
ni nom, ni contenu de la marque.

```bash
npm install
npm start          # http://localhost:4220 (l'API doit tourner : uv run couverture api, port 8001)
npm test           # tests (vitest)
```

La clé de l'API n'entre jamais dans le navigateur : `proxy.conf.mjs` la lit dans le `.env` du projet
(`COUVERTURE_API_KEY`) et l'ajoute aux appels. En production, le serveur placé devant l'API l'ajoute.

| Fichier | Rôle |
|---|---|
| `src/app/app.component.*` | la mise en page de l'écran : la déclaration à gauche, la décision à droite, les fenêtres |
| `src/app/echange.service.ts` | l'état de l'échange en cours, partagé par les composants : contrat, déclaration, méthode, étapes, réponses du client, suivi, article ouvert, fiche ; et ce qu'on en fait (analyser, décider, relire avec les réponses) |
| `src/app/composants/` | un composant par bloc : `en-tete`, `choix-contrat` (et les conditions particulières), `saisie`, `accueil`, `etape` (une étape de l'échange), `decision` (une décision ou un sinistre), `fondements` (réserves, clauses citées, limites), `questions` (au client), `suivi` (l'analyse en cours), `article` (l'article entier) ; aucun ne crée de boîte (`display: contents`) |
| `src/app/couverture.service.ts` | appels à l'API `/api/v1` |
| `src/app/couverture.model.ts` | types échangés avec l'API |
| `src/app/presentation.ts` | libellés, couleurs, faits et réponses (testé) |
| `src/app/*.spec.ts` | les tests (vitest) : la présentation, l'état de l'échange, une étape à deux sinistres |
| `src/styles.scss` | la palette |
| `src/ecran.scss` | les styles de l'écran, globaux |
| `proxy.conf.mjs` | adresse de l'API et clé, en local |

Le circuit : une déclaration est **analysée**, par la méthode choisie. Si la réponse est « à préciser », l'écran
affiche les questions à poser au client, avec les réponses possibles quand elles existent. Deux façons d'y répondre :

- **chaîne de règles, un seul sinistre** : les réponses, ajoutées aux faits, sont soumises au moteur seul
  (`/decisions`) ; la décision tombe tout de suite, sans nouvel appel au modèle ;
- **lecture des clauses, ou plusieurs sinistres** : les réponses, en mots ou d'un clic, s'ajoutent à la déclaration
  (« Précisions du client : … »), relue par la même méthode (7.218, 7.222).

Plusieurs sinistres dans une déclaration : un cadre par sinistre, avec sa décision, son motif, ses faits, ses
réserves et ses clauses ; les questions de tous se répondent d'un bloc (7.222). Les deux méthodes rendent la même
forme (`schemas.Decision`, validée aussi dans le flux `/analyses/suivi`) : l'écran ne lit qu'elle.
