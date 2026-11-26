# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-medium-2604` (verifiee, exemples, verification mistral-small-2603)

2026-11-26T13:31:25 · jeu cinq (20 cas, empreinte `8751b4037bf20034`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « cinq » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 2 | ✗ |
| chaine | faux_refus | ≤ 1 | 1 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.783 | ✗ |
| chaine | instables | ≤ 3 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 7.96 | ✓ |

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 78% (75% – 80%) | 73% (70% – 75%) | **2 (2 – 2)** | **1 (1 – 1)** | 22% (20% – 25%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 7.67 | 2 |
| Non couvert | 5 | 1 |
| À préciser | 3 | 1.33 |

Instables : **1** sur 20 · rappel des clauses : 48% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 26.7 s · par cas, un à la fois (10 cas) : médiane 5.23 s, 95e centile 7.96 s (lecture 4.19 s, décision 0.02 s) · en masse (quatre à la fois) : médiane 4.89 s, 95e centile 6.58 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 80% | 2 ⚠ | 1 |
| garantie : ? | 20 | 80% | 2 ⚠ | 1 |
| thème : base | 1 | 100% | 0 | 0 |
| thème : condition | 4 | 75% | 1 ⚠ | 0 |
| thème : definition | 7 | 71% | 1 ⚠ | 0 |
| thème : exclusion | 6 | 83% | 0 | 1 |
| thème : option | 2 | 100% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `c-a13` attendu NC, obtenu C C C — Je suis photographe indépendant. Pendant un cambriolage chez moi, porte forcée, on m'a pris mes deux boîtiers … *(Des biens à usage même partiellement professionnel sont du « matériel », que la définition du contenu exclut ; le vol n')*
- **⚠ couvert à tort** `c-a19` attendu ?, obtenu C C C — J'ai six chevaux de selle qui m'appartiennent, en pension dans un manège. L'un d'eux s'est échappé du paddock … *(La RC pour les chevaux de selle est acquise pour 5 chevaux, ou plus seulement si leur nombre figure aux conditions parti)*
- `c-a02` attendu C, obtenu C C ? — Hier soir la terre a tremblé quelques secondes ; la radio a parlé d'une magnitude de 3,6. Plusieurs maisons du… *(Sous 4 de magnitude, le séisme reste un tremblement de terre au sens du lexique s'il endommage des biens dans les 10 km,)*
- `c-a07` attendu C, obtenu NC NC NC — Mon fils de 17 ans avait beaucoup bu à la fête d'anniversaire d'un copain. En titubant dans le jardin, il est … *(L'exclusion pour ivresse ne vise que l'assuré de 18 ans ou plus ; le fils mineur vivant au foyer est assuré et sa RC vie)*
- `c-a08` attendu NC, obtenu ? ? ? — Ma liseuse électronique, avec un écran de 6 pouces, a glissé de ma poche dans l'escalier de chez moi et l'écra… *(La chute par l'assuré n'est pas un péril de base, et même le pack multimédia ne vise que le matériel informatique, dont )*
