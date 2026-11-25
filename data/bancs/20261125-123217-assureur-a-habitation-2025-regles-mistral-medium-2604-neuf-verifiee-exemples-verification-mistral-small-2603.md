# Banc d'essai — assureur-a-habitation-2025, méthode `regles`, lecture par `mistral:mistral-medium-2604` (verifiee, exemples, verification mistral-small-2603)

2026-11-25T12:30:28 · jeu neuf (20 cas, empreinte `79a34c6529145427`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « neuf » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 4 | ✗ |
| chaine | faux_refus | ≤ 1 | 1 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.6 | ✗ |
| chaine | instables | ≤ 3 | 0 | ✓ |
| chaine | latence_seule_p95_s | ≤ 10 | 4.85 | ✓ |

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 60% (60% – 60%) | 55% (55% – 55%) | **4 (4 – 4)** | **1 (1 – 1)** | 20% (20% – 20%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 6 | 4 |
| Non couvert | 4 | 2 |
| À préciser | 2 | 2 |

Instables : **0** sur 20 · rappel des clauses : 38% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 22.1 s · par cas, un à la fois (10 cas) : médiane 4.28 s, 95e centile 4.85 s (lecture 3.18 s, décision 0.01 s) · en masse (quatre à la fois) : médiane 3.98 s, 95e centile 5.75 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 60% | 4 ⚠ | 1 |
| garantie : ? | 20 | 60% | 4 ⚠ | 1 |
| thème : base | 4 | 100% | 0 | 0 |
| thème : condition | 4 | 50% | 1 ⚠ | 0 |
| thème : definition | 3 | 33% | 1 ⚠ | 0 |
| thème : exclusion | 5 | 60% | 1 ⚠ | 1 |
| thème : manque | 3 | 33% | 1 ⚠ | 0 |
| thème : option | 1 | 100% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `n-a03` attendu ?, obtenu C C C — Il y a eu une panne de courant dans toute ma rue pendant que j'étais au travail. Le soir, tout ce qu'il y avai… *(La perte de denrées après une coupure du réseau est garantie, mais seulement si l'arrêt a duré au moins 6 heures ; la dé)*
- **⚠ couvert à tort** `n-a04` attendu ?, obtenu C C C — Avant-hier soir, un violent coup de vent a arraché la fenêtre de toit de ma chambre sous les combles. La pluie… *(Le vent n'est une tempête que s'il atteint 80 km/h à la station la plus proche ou s'il a abîmé d'autres biens dans les 1)*
- **⚠ couvert à tort** `n-a16` attendu NC, obtenu C C C — Samedi, après mon pot de départ à la retraite, j'avais beaucoup trop bu. Chez l'ami qui m'hébergeait pour la n… *(Le dommage à un tiers relèverait de la responsabilité civile vie privée, mais la responsabilité personnelle d'un assuré )*
- **⚠ couvert à tort** `n-a20` attendu NC, obtenu C C C — Au parc, le chien d'un autre promeneur a sauté sur moi et a déchiré la manche de mon manteau : 140 euros de ré… *(Le recours contre un tiers n'est pas pris en charge pour un dommage inférieur à 250 EUR ; le manteau, abîmé hors du loge)*
- `n-a08` attendu C, obtenu ? ? ? — Hier soir il y a eu un tremblement de terre, annoncé à 4,7 sur l'échelle de Richter aux informations. Chez moi… *(La magnitude dépasse le seuil de quatre degrés fixé par le lexique : c'est une catastrophe naturelle garantie, et les bi)*
- `n-a14` attendu ?, obtenu NC NC NC — Cet été au lac, j'ai loué un petit bateau à moteur pour l'après-midi. En rentrant au ponton, j'ai mal manœuvré… *(La responsabilité civile ne joue pour un bateau à moteur que jusqu'à 10 CV ; au-delà, l'engin motorisé est exclu. La pui)*
- `n-a15` attendu C, obtenu NC NC NC — Ma voisine m'avait confié son chat pendant ses vacances, gratuitement. J'ai laissé une fenêtre ouverte, il est… *(Les biens dont on a la garde sont en principe exclus, mais l'exclusion réserve les dommages aux animaux de tiers gardés )*
- `n-a17` attendu NC, obtenu ? ? ? — Depuis l'incendie de notre cuisine la semaine dernière (les pompiers sont intervenus), l'appartement est inhab… *(L'assistance organise la garde des animaux quand l'hôtel les refuse, mais seulement pour les chiens et les chats, et ce )*
