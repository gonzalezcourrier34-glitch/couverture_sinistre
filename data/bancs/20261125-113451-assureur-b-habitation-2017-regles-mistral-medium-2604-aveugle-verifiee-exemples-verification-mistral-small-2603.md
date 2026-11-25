# Banc d'essai — assureur-b-habitation-2017, méthode `regles`, lecture par `mistral:mistral-medium-2604` (verifiee, exemples, verification mistral-small-2603)

2026-11-25T11:33:01 · jeu aveugle (20 cas, empreinte `ea01e3b924865bbe`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « aveugle » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 1.333 | ✗ |
| chaine | faux_refus | ≤ 1 | 2.667 | ✗ |
| chaine | exactitude | ≥ 0.85 | 0.583 | ✗ |
| chaine | instables | ≤ 3 | 4 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 5.64 | ✓ |

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 58% (55% – 60%) | 58% (55% – 60%) | **1.333 (1 – 2)** | **2.667 (2 – 3)** | 50% (45% – 55%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 2 | 1.33 |
| Non couvert | 4 | 2.67 |
| À préciser | 5.67 | 4.33 |

Instables : **4** sur 20 · rappel des clauses : 34% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 22.2 s · par cas, un à la fois (10 cas) : médiane 3.99 s, 95e centile 5.64 s (lecture 3.19 s, décision 0.03 s) · en masse (quatre à la fois) : médiane 4.12 s, 95e centile 6.91 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 60% | 1 ⚠ | 2 |
| garantie : ? | 20 | 60% | 1 ⚠ | 2 |
| thème : base | 6 | 33% | 0 | 1 |
| thème : condition | 2 | 50% | 0 | 0 |
| thème : definition | 2 | 0% | 0 | 1 |
| thème : exclusion | 4 | 75% | 1 ⚠ | 0 |
| thème : manque | 2 | 100% | 0 | 0 |
| thème : option | 4 | 100% | 0 | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `av-b11` attendu ?, obtenu ? C ? — Hier soir, pendant que j'étais au restaurant, on a brisé la vitre arrière de ma voiture garée dans la rue et v… *(La garantie vol écarte le contenu des véhicules, mais la garantie matériel multimédia couvre le vol dans un véhicule fra)*
- **⚠ couvert à tort** `av-b13` attendu NC, obtenu C C C — Un gros bloc de roche s'est détaché du talus rocheux qui surplombe mon terrain et a défoncé le mur arrière de … *(Les dommages qui se rattachent à une chute de pierres ou de rochers figurent dans les exclusions communes à toutes les g)*
- `av-b03` attendu C, obtenu NC NC NC — En rentrant du travail j'ai trouvé le couloir inondé : un tuyau d'eau qui passe dans la cloison de la salle de… *(Rupture d'une conduite intérieure : c'est le cas type de la garantie dégâts des eaux, qui prend aussi en charge la reche)*
- `av-b04` attendu NC, obtenu NC ? NC — J'étais parti pour la journée en laissant la fenêtre de toit de la chambre entrouverte pour aérer. Il y a eu u… *(L'eau de pluie est entrée par une ouverture : exclusion expresse de la garantie dégâts des eaux. La garantie optionnelle)*
- `av-b05` attendu C, obtenu NC NC NC — Pendant la tempête de samedi (la météo a relevé des rafales à plus de 100 km/h dans notre commune), le trampol… *(Le vent dépasse 80 km/h, donc il y a tempête au sens du lexique. Les objets non fixés à l'extérieur sont exclus sauf le )*
- `av-b08` attendu NC, obtenu ? NC ? — Mardi après-midi je jardinais derrière la maison et je n'avais pas fermé à clé la porte d'entrée. Quelqu'un es… *(Sans effraction, sans fausses clés et sans violence, le lexique qualifie ce vol de vol simple, et les vols simples sont )*
- `av-b10` attendu C, obtenu ? ? ? — En passant l'aspirateur j'ai accroché le meuble télé et notre téléviseur, acheté l'an dernier, a basculé et es… *(La garantie bris de vitrages écarte les parties vitrées du matériel multimédia, mais le téléviseur est du matériel multi)*
- `av-b14` attendu C, obtenu ? ? ? — Je suis propriétaire de ma maison. La semaine dernière, avec le gel, je n'avais pas dégagé ni salé le trottoir… *(La responsabilité civile immeuble couvre la responsabilité de l'assuré envers un tiers pour un dommage corporel dû au dé)*
- `av-b16` attendu NC, obtenu ? ? ? — Samedi soir j'ai claqué la porte de chez moi en laissant mes clés à l'intérieur. J'ai trouvé un serrurier de g… *(L'oubli des clés à l'intérieur est bien assimilé à une urgence, mais l'assistance n'intervient que si elle est appelée a)*
- `av-b20` attendu C, obtenu ? NC NC — Pour les 18 ans de ma fille nous avions loué une salle des fêtes à Thionville. En rangeant les tables à la fin… *(L'extension des garanties couvre les dégâts accidentels causés par un assuré à un local loué pour une fête privée en Fra)*
