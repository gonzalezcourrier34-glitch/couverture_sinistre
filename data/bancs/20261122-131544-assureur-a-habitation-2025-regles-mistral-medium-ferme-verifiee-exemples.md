# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-medium-latest` (verifiee, exemples)

2026-11-22T13:13:54 · jeu ferme (20 cas, empreinte `6997c9e1e2012a80`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « ferme » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 0 | ✓ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.917 | ✓ |
| chaine | instables | ≤ 3 | 1 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 16.19 | ✗ |

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 92% (90% – 95%) | 82% (80% – 85%) | **0 (0 – 0)** | **0 (0 – 0)** | 38% (35% – 40%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 8 | 0 |
| Non couvert | 4.33 | 0 |
| À préciser | 6 | 1.67 |

Instables : **1** sur 20 · rappel des clauses : 41% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 19.3 s · par cas, un à la fois (10 cas) : médiane 3.88 s, 95e centile 16.19 s (lecture 2.96 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.53 s, 95e centile 5.27 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 90% | 0 | 0 |
| garantie : ? | 20 | 90% | 0 | 0 |
| thème : assistance | 1 | 100% | 0 | 0 |
| thème : base | 3 | 100% | 0 | 0 |
| thème : exclusion | 3 | 100% | 0 | 0 |
| thème : extension | 2 | 100% | 0 | 0 |
| thème : incertain | 5 | 100% | 0 | 0 |
| thème : piege | 4 | 50% | 0 | 0 |
| thème : rc | 2 | 100% | 0 | 0 |

### Erreurs et instabilités

- `f-a02` attendu NC, obtenu ? NC ? — J'ai oublié le fer à repasser posé sur une chemise pendant que je répondais au téléphone. La chemise et la hou… *(Le lexique précise que les brûlures aux linges et vêtements et l'excès de chaleur sans embrasement ne constituent pas un)*
- `f-a14` attendu NC, obtenu ? ? ? — Pendant le gros coup de vent de mardi, le store banne de mon balcon a été arraché et ses bras sont complètemen… *(Quelle que soit la vitesse du vent, la garantie tempête exclut les dégâts à tout objet situé à l'extérieur, même fixé à )*
