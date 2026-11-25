# Banc d'essai — assureur-d-habitation-2026, méthode `regles`, lecture par `mistral:mistral-medium-2604` (verifiee, exemples, verification mistral-small-2603)

2026-11-25T11:34:53 · jeu aveugle (20 cas, empreinte `63fadc633d584ebe`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « aveugle » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 2 | ✗ |
| chaine | faux_refus | ≤ 1 | 1 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.783 | ✗ |
| chaine | instables | ≤ 3 | 2 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 5.66 | ✓ |

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 78% (75% – 80%) | 73% (70% – 75%) | **2 (2 – 2)** | **1 (1 – 1)** | 27% (25% – 30%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 5.33 | 2 |
| Non couvert | 6.33 | 1 |
| À préciser | 4 | 1.33 |

Instables : **2** sur 20 · rappel des clauses : 43% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 24.8 s · par cas, un à la fois (10 cas) : médiane 4.24 s, 95e centile 5.66 s (lecture 3.07 s, décision 0.02 s) · en masse (quatre à la fois) : médiane 4.07 s, 95e centile 6.53 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 75% | 2 ⚠ | 1 |
| garantie : ? | 20 | 75% | 2 ⚠ | 1 |
| thème : base | 6 | 67% | 0 | 1 |
| thème : condition | 1 | 100% | 0 | 0 |
| thème : definition | 2 | 50% | 1 ⚠ | 0 |
| thème : exclusion | 5 | 80% | 0 | 0 |
| thème : manque | 2 | 100% | 0 | 0 |
| thème : option | 4 | 75% | 1 ⚠ | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `av-d11` attendu ?, obtenu C C C — Des cambrioleurs sont entrés en forçant la fenêtre de la chambre pendant que nous étions au restaurant. Ils n'… *(Le vol par effraction est garanti, mais les bijoux sont des objets précieux, exclus du contenu ordinaire et assurés seul)*
- **⚠ couvert à tort** `av-d16` attendu NC, obtenu C C C — Ma fille de 16 ans a renversé une dame âgée sur le trottoir avec sa trottinette électrique. La dame a le col d… *(La trottinette électrique est, d'après le lexique, un engin de déplacement personnel motorisé soumis à l'assurance oblig)*
- `av-d04` attendu C, obtenu ? C ? — La tempête de la nuit de mardi a arraché une trentaine de tuiles de mon toit et la pluie est entrée dans une c… *(Action directe du vent sur la toiture, avec d'autres bâtiments du voisinage endommagés : la condition d'intensité est re)*
- `av-d15` attendu NC, obtenu ? ? NC — En passant l'aspirateur vendredi, j'ai débranché le congélateur du cellier pour libérer la prise et j'ai oubli… *(Les denrées ne sont garanties qu'après un dommage électrique, une panne indemnisée ou une coupure accidentelle attestée )*
- `av-d19` attendu C, obtenu NC NC NC — Un cycliste m'a percuté alors que je marchais sur le trottoir : j'ai eu le poignet fracturé et mes lunettes so… *(Dommages subis dans la vie privée lors d'un accident dont un tiers non assuré au contrat est responsable et qu'aucune au)*
