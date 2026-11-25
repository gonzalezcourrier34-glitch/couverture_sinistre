# Banc d'essai — assureur-b-habitation-2017, méthode `regles`, lecture par `mistral:mistral-medium-2604` (verifiee, exemples, verification mistral-small-2603)

2026-11-25T12:32:17 · jeu neuf (20 cas, empreinte `945b6dbf60f1cc4e`) · cas validés par l'auteur : 0 sur 20

> ⚠ jeu « neuf » : sans faits idéaux, la chaîne complète seule

## Portes : **ÉCHOUE**

| Couche | Critère | Seuil | Valeur | |
|---|---|---|---|---|
| chaine | faux_couverts | ≤ 0 | 2 | ✗ |
| chaine | faux_refus | ≤ 1 | 0 | ✓ |
| chaine | exactitude | ≥ 0.85 | 0.5 | ✗ |
| chaine | instables | ≤ 3 | 4 | ✗ |
| chaine | latence_seule_p95_s | ≤ 10 | 10.58 | ✗ |

## Couche 3 — chaîne complète (3 exécutions)

| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |
|---|---|---|---|---|
| 50% (45% – 55%) | 47% (45% – 50%) | **2 (2 – 2)** | **0 (0 – 0)** | 53% (50% – 55%) |

Par réponse donnée (moyenne par exécution) :

| Réponse | Justes | Fausses |
|---|---|---|
| Couvert | 4.67 | 2 |
| Non couvert | 1.67 | 1 |
| À préciser | 3.67 | 7 |

Instables : **4** sur 20 · rappel des clauses : 30% · rappel des questions : — · erreurs du fournisseur : 0 · durée moyenne d'une exécution : 33.0 s · par cas, un à la fois (10 cas) : médiane 6.01 s, 95e centile 10.58 s (lecture 3.17 s, décision 0.08 s) · en masse (quatre à la fois) : médiane 5.72 s, 95e centile 11.93 s

| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |
|---|---|---|---|---|
| auteur : agent+mistral-large | 20 | 45% | 2 ⚠ | 0 |
| garantie : ? | 20 | 45% | 2 ⚠ | 0 |
| thème : base | 4 | 75% | 0 | 0 |
| thème : condition | 3 | 0% | 0 | 0 |
| thème : definition | 2 | 50% | 0 | 0 |
| thème : exclusion | 5 | 40% | 0 | 0 |
| thème : manque | 1 | 0% | 1 ⚠ | 0 |
| thème : option | 5 | 60% | 1 ⚠ | 0 |

### Erreurs et instabilités

- **⚠ couvert à tort** `n-b07` attendu ?, obtenu C C C — Notre maison assurée chez vous, dans le nord du pays, a été cambriolée : un volet et une fenêtre ont été forcé… *(Le vol avec effraction est garanti, sauf dans des locaux à occupation irrégulière. Tout dépend du nombre de nuits d'inoc)*
- **⚠ couvert à tort** `n-b08` attendu ?, obtenu C C C — Pendant notre semaine de vacances au Portugal, la porte de l'appartement que nous louions a été fracturée en n… *(La garantie vol de base couvre le vol par effraction d'objets personnels en séjour temporaire, mais le lexique retire de)*
- `n-b03` attendu C, obtenu C ? C — Je suis propriétaire de mon appartement. Dans la nuit, une paroi de mon aquarium de 300 litres a lâché et tout… *(L'exclusion des objets non reliés à l'installation d'eau du bâtiment réserve expressément le cas des aquariums : les dég)*
- `n-b04` attendu NC, obtenu ? ? ? — Je suis locataire de mon appartement. Depuis cet hiver, de la buée s'est installée entre les deux vitres de la… *(Il n'y a ni bris ni fêlure, seulement un double vitrage qui a perdu son étanchéité. Cette extension de la garantie bris )*
- `n-b06` attendu C, obtenu C ? ? — Il y a quinze jours j'ai perdu mon trousseau de clés, avec une étiquette à mon nom dessus. Mardi, en rentrant … *(Le contrat exclut les vols simples, mais la définition du lexique précise qu'un vol commis dans les locaux avec des clés)*
- `n-b09` attendu C, obtenu ? ? ? — En randonnée dans les Vosges, j'avais installé mon appareil photo numérique compact sur son trépied quand un e… *(Un appareil photo numérique est du matériel multimédia au sens du lexique et, utilisable sans installation fixe, du maté)*
- `n-b10` attendu NC, obtenu ? ? ? — La semaine dernière, mon ordinateur de la maison a été bloqué par un programme malveillant qui a rendu tous me… *(La garantie matériel multimédia ne vise que le bris par chute, choc ou corps étranger et exclut les pertes liées à un vi)*
- `n-b11` attendu ?, obtenu NC NC NC — Après l'orage très violent de mardi soir, les égouts de notre rue ont débordé et l'eau sale est remontée par l… *(Le refoulement d'égouts après de fortes pluies relève de la garantie « Pluies & inondations », qui est optionnelle, et l)*
- `n-b12` attendu NC, obtenu ? ? ? — Dimanche matin, le sol de mon jardin s'est enfoncé d'un coup sur plusieurs mètres, au-dessus d'une ancienne ga… *(Les exclusions communes à toutes les garanties écartent les dommages liés à un affaissement de terrain, ce qu'est l'effo)*
- `n-b13` attendu C, obtenu ? C C — Je suis propriétaire de la maison où j'habite. L'antenne parabolique fixée sur ma façade s'est décrochée et es… *(La responsabilité civile immeuble garantit les dommages causés à un tiers par le fait du bâtiment d'habitation, antennes)*
- `n-b16` attendu NC, obtenu ? NC NC — J'ai fait refaire ma salle de bains par un carreleur recommandé par un voisin, devis signé et facture payée. T… *(Le litige naît d'un contrat passé avec un artisan : la protection juridique optionnelle exclut tout litige de responsabi)*
- `n-b17` attendu NC, obtenu ? ? ? — Vendredi soir, plus de chauffage ni d'eau chaude à la maison : la chaudière s'était arrêtée. J'ai appelé mon c… *(L'assistance d'urgence suppose d'appeler la centrale au moment des faits, qui mandate elle-même le réparateur ; les frai)*
- `n-b18` attendu NC, obtenu ? ? ? — Nous devions partir dix jours en Crète, séjour réservé et payé depuis quatre mois. La veille du départ, notre … *(La garantie annulation ne joue que pour une liste limitée d'événements, dont la maladie grave de l'assuré ou de certains)*
