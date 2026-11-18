# Golden set — fiche de validation (foyer-appart123-2025, v5, 97 cas)

Pour chaque cas : la réponse attendue est-elle celle d'un gestionnaire qui lit les conditions générales ? C = couvert, NC = non couvert, ? = incertain (il manque une information, ou la garantie n'est pas traduite).
Une réponse « acceptable » est tolérée sans être exacte.

Pour valider ou corriger : `data/golden/annotations/foyer-appart123-2025.jsonl` (champs `attendu`, `acceptables`, `statut` → « validé par … »), puis `uv run couverture banc --contrat foyer-appart123-2025 --figer "validation"`.

## Garantie 1.4

| Cas | Déclaration | Attendu | Acceptable | Fondement | Validé |
|---|---|---|---|---|---|
| `g2-i13` | Le joint de la douche fuyait depuis des mois ; l'eau a fini par abîmer le mur de la salle de bain. | **NC** | ? | Exclusion générale 1.4 : manque d'entretien, détérioration lente et progressive. |  |
| `g2-p12` | Énervé, j'ai donné un coup de poing dans la vitre de la porte-fenêtre, qui s'est brisée. | **NC** |  | Exclusion générale 1.4 : un sinistre intentionnel dont l'assuré est l'auteur. |  |

## Garantie 2.1

| Cas | Déclaration | Attendu | Acceptable | Fondement | Validé |
|---|---|---|---|---|---|
| `bougie-01` | J'ai laissé une bougie sur la table de mon jardin pendant mes vacances. Avec la chaleur, la bougie a fondu et a abîmé la table. | **NC** |  | Pas d'embrasement : « l'excès de chaleur … sans qu'il y ait embrasement » n'est pas un incendie (12/incendie). Et le contenu du jardin n'est pas du contenu assuré (12/contenu). |  |
| `bougie-02` | Une bougie allumée est tombée dans le salon, la nappe a pris feu et les flammes ont brûlé la table. | **C** |  | Flammes, embrasement de la nappe : incendie au sens du contrat (2.1, 12/incendie). |  |
| `bougie-03` | Une bougie posée sur la table du salon a coulé et laissé une marque de brûlure superficielle, sans flammes. | **NC** |  | Brûlure sans flammes : « les brûlures » ne constituent pas un incendie (12/incendie). |  |
| `bougie-04` | Pendant mes vacances, une bougie laissée sur la table du jardin s'est enflammée et a brûlé la table et le salon de jardin. | **NC** | ? | Vrai incendie, mais table et salon de jardin = contenu du jardin, exclu du contenu assuré (12/contenu). INCERTAIN défendable si une option jardin figure aux conditions particulières. |  |
| `bougie-05` | J'ai oublié une bougie allumée sur la terrasse avant de partir trois semaines. Le feu s'est propagé à la façade et au séjour. | **C** |  | Incendie qui atteint la façade et le séjour : couvert, même par imprudence. L'absence de trois semaines n'est pas une inoccupation de plus de 90 jours. |  |
| `val-08` | Un court-circuit dans le grille-pain a mis le feu à la cuisine : les flammes ont détruit les placards et le réfrigérateur. | **C** |  | 2.1 : l'incendie ; flammes et embrasement, c'est un incendie au sens de la définition. |  |
| `val-09` | Mon fer à repasser, laissé à plat sur la planche, a brûlé la housse et laissé une marque sur le tissu, sans flammes. | **NC** |  | Définition de l'incendie : les brûlures et le contact d'une source de chaleur sans embrasement ne sont pas un incendie. |  |
| `g-l03` | jai laisser une bougie alumé sur la table du jardin pendan les vacance, avec le soleil elle a fondu et a taché la table, pas de feu | **NC** |  | Fautes de frappe. Pas d'embrasement, donc pas d'incendie ; et le mobilier de jardin n'est pas du contenu. |  |
| `g-l04` | La friteuse a pris feu ; les flammes sont montées jusqu'à la hotte et ont brûlé les placards de la cuisine. | **C** |  | 2.1 : incendie (flammes et embrasement). |  |
| `g-p07` | Une casserole oubliée sur le feu a dégagé une épaisse fumée qui a noirci les murs et le plafond de la cuisine ; les flammes sont restées dans la casserole. | **C** | ? | 2.1 couvre aussi « le dégagement de suie et de fumée », sans incendie. |  |
| `g-m02` | Un incendie chez le voisin s'est propagé à mon appartement ; les pompiers ont inondé le salon en l'éteignant. | **C** |  | 2.1 : incendie ; l'eau d'extinction en est la conséquence. |  |
| `g2-i05` | Il y a eu un début de feu dans la cuisine. | **?** |  | L'incendie suppose flammes et embrasement ; les dégâts et l'embrasement sont à préciser. |  |
| `g2-m01` | Un court-circuit a provoqué un incendie dans le salon ; pour entrer, les pompiers ont dû casser la porte d'entrée. | **C** |  | 2.1 : l'incendie, et les dégâts causés pour l'éteindre. |  |

## Garantie 2.2

| Cas | Déclaration | Attendu | Acceptable | Fondement | Validé |
|---|---|---|---|---|---|
| `val-13` | La tempête a arraché des tuiles de l'immeuble et la pluie est entrée dans mon salon, abîmant le plafond et le canapé. | **C** | ? | 2.2 : les dommages matériels directement causés par la tempête. Garantie non écrite en règles : test de l'aveu de limite. |  |
| `red-t01` | Lors de la tempête de la nuit dernière, des rafales mesurées à 110 km/h ont arraché une partie de la toiture de l'immeuble ; la pluie a abîmé le plafond et le canapé de mon salon. | **C** | ? | 2.2 : dommages matériels directement causés par la tempête ; vent de plus de 80 km/h (définition de la tempête). |  |
| `red-t02` | Pendant la tempête, le vent a emporté la table et les chaises de ma terrasse, qui se sont brisées en tombant. | **NC** | ? | Exclusion 2.2 : « à tout objet situé à l'extérieur même ceux fixés à demeure ». |  |
| `red-t03` | Le poids de la neige a fait s'effondrer mon carport en bois, simplement posé sur des plots, sans ancrage en béton. | **NC** | ? | Exclusion 2.2 : annexes faisant partie du bâtiment non fixées au sol par un ancrage en béton. |  |
| `red-t04` | Un vent violent a soufflé dans la région, et plusieurs maisons voisines ont eu leurs toitures abîmées. Chez moi, la fenêtre de la chambre a été arrachée et la moquette trempée. | **C** | ? | 2.2 et définition de la tempête : le vent endommage d'autres biens dans les 10 km du bâtiment. |  |
| `g2-i11` | Après le gros coup de vent d'hier, des tuiles de l'immeuble sont tombées sur mon balcon et l'ont abîmé. | **?** | C | La tempête suppose un vent d'au moins 80 km/h ou des dégâts aux biens voisins (définition) : non précisé. Garantie 2.2 non traduite. |  |

## Garantie 2.3

| Cas | Déclaration | Attendu | Acceptable | Fondement | Validé |
|---|---|---|---|---|---|
| `g-h04` | Après des pluies exceptionnelles, la rivière a débordé et l'eau a envahi mon appartement au rez-de-chaussée. | **C** | ? | 2.3 : l'inondation est couverte par les catastrophes naturelles, alors que 2.7 l'exclut. Non traduite. |  |
| `g-h05` | Les égouts publics ont refoulé pendant un gros orage et l'eau sale a envahi la salle de bain. | **C** | ? | 2.3 : le refoulement d'égouts publics est une catastrophe naturelle couverte ; 2.7 l'exclut. Non traduite. |  |

## Garantie 2.4

| Cas | Déclaration | Attendu | Acceptable | Fondement | Validé |
|---|---|---|---|---|---|
| `g-h06` | Pendant une manifestation qui a dégénéré, des émeutiers ont brisé les fenêtres de mon appartement au rez-de-chaussée. | **C** | ? | 2.4 : détérioration par des personnes prenant part à un attentat (émeutes) ; aussi 2.9. Non traduites. |  |

## Garantie 2.5

| Cas | Déclaration | Attendu | Acceptable | Fondement | Validé |
|---|---|---|---|---|---|
| `g2-i16` | De l'eau de mon appartement s'est infiltrée chez le voisin du dessous, qui me demande de payer ses réparations. | **C** | ? | 2.5 : responsabilité civile du fait du bâtiment et du contenu envers les tiers. Garantie non traduite. |  |

## Garantie 2.6

| Cas | Déclaration | Attendu | Acceptable | Fondement | Validé |
|---|---|---|---|---|---|
| `g-h01` | Un orage a provoqué une surtension : le réfrigérateur et la box internet ne fonctionnent plus. | **C** | ? | 2.6 : action de l'électricité. Garantie non traduite : jamais un refus. |  |
| `g-h02` | Une panne de courant de dix heures a fait décongeler tout le contenu de mon congélateur. | **C** | ? | 2.6 : denrées décongelées après 6 heures d'arrêt (limite 500 EUR). Non traduite. |  |
| `g-h07` | Mon chat s'est électrocuté en mordant un câble électrique. | **C** | ? | 2.6 : l'électrocution des animaux domestiques. Non traduite. |  |
| `g2-p10` | Une surtension a grillé l'ordinateur que j'utilise pour mon activité d'indépendant. | **NC** | ? | Exclusion 2.6 : les appareils électroniques et informatiques à usage professionnel. Garantie non traduite. |  |

## Garantie 2.7

| Cas | Déclaration | Attendu | Acceptable | Fondement | Validé |
|---|---|---|---|---|---|
| `autre-02` | Le tuyau du lave-linge a cédé et l'eau a abîmé le parquet et le canapé. | **C** |  | Dégâts des eaux couverts (2.7) ; le tuyau à l'origine est exclu (2.7-b) mais sa réparation relève des garanties complémentaires (4~1). |  |
| `val-10` | En janvier, je suis parti deux semaines en coupant le chauffage. Une canalisation a gelé puis éclaté ; l'eau a abîmé mon parquet. | **NC** | ? | 2.7 : en période de gel, maintenir une température positive, vidanger ou isoler ; refus s'il y a un lien causal direct. La canalisation elle-même est exclue. |  |
| `val-11` | Pendant un orage, la pluie s'est infiltrée par la fenêtre mal jointée de ma chambre et a abîmé le mur et la moquette. | **NC** |  | Exclusion 2.7 : une infiltration par les fenêtres, autre que celle due à une fuite des installations hydrauliques extérieures. |  |
| `val-12` | Ma baignoire a débordé pendant que j'étais au téléphone ; l'eau a abîmé mon parquet. | **C** |  | 2.7 couvre l'ensemble des dégâts des eaux ; l'exclusion du récipient vise un récipient NON relié à l'installation hydraulique, ce que n'est pas une baignoire. |  |
| `g-l05` | Fuite d'eau sous l'évier : le meuble de cuisine a gonflé et le parquet est abîmé. | **C** |  | 2.7 : l'ensemble des dommages causés par l'eau. |  |
| `g-q04` | De l'eau coule du plafond de ma salle de bain et a abîmé le mur. | **C** | ? | 2.7 couvre l'ensemble des dégâts des eaux ; la cause inconnue n'établit aucune exclusion (c'est à l'assureur de la prouver). |  |
| `g-p04` | Le chauffe-eau a fui ; le parquet est abîmé et le chauffe-eau lui-même est hors d'usage. | **C** |  | 2.7 : le parquet est couvert ; le chauffe-eau à l'origine du sinistre est exclu (exclusion partielle). |  |
| `g-p05` | L'aquarium du salon s'est brisé et l'eau a abîmé le parquet. | **C** |  | 2.7 : l'exclusion du récipient non relié excepte l'aquarium. |  |
| `g-p06` | J'ai renversé le seau d'eau du ménage et l'eau a abîmé le parquet. | **NC** | ? | Exclusion 2.7 : le renversement d'un récipient non relié à l'installation hydraulique. |  |
| `g2-i03` | Une tache d'humidité est apparue au plafond de ma chambre, juste sous la salle de bain du voisin du dessus. | **?** | C | 2.7 couvre l'ensemble des dégâts des eaux, mais la condensation et certaines infiltrations sont exclues : la cause est à établir. |  |
| `g2-i06` | Pendant mon absence d'une semaine en février, une canalisation a gelé et a éclaté ; l'eau a abîmé le sol de la salle de bain. | **?** | C | Le gel est exclu, sauf si les mesures de prévention (chauffer, vidanger ou isoler) ont été respectées : à demander. |  |
| `g2-i14` | Le tuyau apparent de ma cave, très rouillé depuis longtemps, a cédé et l'eau a abîmé les cartons que j'y stockais. | **NC** | ? | Exclusion 2.7 : les canalisations apparentes présentant plusieurs points de corrosion visibles et non traités. |  |
| `g2-p08` | Le bain à bulles installé sur ma terrasse a fui et l'eau a abîmé le canapé du salon. | **NC** | ? | Exclusion 2.7 : l'écoulement d'eau des piscines et des bains à bulles extérieurs. |  |
| `g2-p09` | Des infiltrations par la toiture de l'immeuble ont taché le plafond de mon salon. | **C** | ? | L'exclusion vise les infiltrations par terrasses, balcons, portes, fenêtres ou murs, et les dégâts à la partie extérieure de la toiture, pas le plafond abîmé par une infiltration par le toit. |  |
| `g2-l02` | Bonjour, suite à notre conversation téléphonique de lundi avec votre collègue, je vous confirme par écrit que mardi, en rentrant du travail vers 18 h, j'ai constaté que le flexible de la machine à laver s'était détaché ; l'eau a coulé sur le parquet du couloir et de la chambre. Le plombier est passé le lendemain. Je joins les photos. | **C** |  | 2.7 : l'ensemble des dommages causés par l'eau. |  |
| `g2-l04` | Le lave-vaisselle est tombé en panne et a fui pendant la nuit ; le parquet de la cuisine est gondolé. | **C** |  | 2.7 : l'ensemble des dommages causés par l'eau. |  |

## Garantie 2.8

| Cas | Déclaration | Attendu | Acceptable | Fondement | Validé |
|---|---|---|---|---|---|
| `g-h03` | La cuve de fioul de l'immeuble a fui et le fioul a imprégné le sol de ma cave. | **C** | ? | 2.8 : dégâts causés par le mazout. Non traduite. |  |

## Garantie 2.9

| Cas | Déclaration | Attendu | Acceptable | Fondement | Validé |
|---|---|---|---|---|---|
| `red-b01` | Mon fils a cassé la vitre de la porte-fenêtre du salon avec un ballon. | **C** |  | 2.9 : le bris de vitres. |  |
| `red-b02` | J'ai fait tomber une casserole sur ma table de cuisson vitrocéramique, qui s'est fendue. | **C** | ? | 2.9 : les tables de cuisson en vitrocéramique sont assimilées aux vitres. |  |
| `red-b03` | Ma télévision est tombée du meuble et l'écran s'est fissuré. | **NC** | ? | Exclusion 2.9 : les parties vitrées des appareils audiovisuels y compris les écrans de télévision. |  |
| `red-b04` | Un vase en cristal est tombé de l'étagère et s'est brisé. | **NC** | ? | Exclusion 2.9 : les objets en verre autres que des vitres et biens assimilés. |  |
| `red-b05` | Le grand miroir que je venais d'acheter, encore dans son carton et pas encore accroché, s'est brisé quand je l'ai fait tomber. | **NC** | ? | Exclusion 2.9 : les dommages aux vitres et biens assimilés non placés. |  |
| `red-b06` | La vitre de la fenêtre de la cuisine est rayée sur toute sa largeur. | **NC** | ? | Exclusion 2.9 : les rayures et écaillements des vitres. |  |
| `g2-m02` | La tempête a cassé la fenêtre du salon et la pluie a abîmé le canapé. | **C** | ? | La vitre est couverte par le bris de vitrages (2.9) ; le canapé relève de la tempête (2.2), non traduite. |  |

## Garantie 2.10

| Cas | Déclaration | Attendu | Acceptable | Fondement | Validé |
|---|---|---|---|---|---|
| `velo-01` | Je me fais voler mon vélo dans le local commun de l'immeuble, qui n'était pas fermé à clé. | **NC** |  | Exclusion : « le vol ou le vandalisme dans les parties communes du bâtiment » (2.10-a, p. 12). Le local commun est une partie commune. |  |
| `velo-02` | Mon vélo a été volé dans le local à vélos commun de l'immeuble. Le local était fermé à clé et la serrure a été forcée. | **NC** |  | Même exclusion : l'effraction ne change rien, les parties communes restent exclues. |  |
| `velo-03` | Mon vélo a été volé dans ma cave privative, fermée à clé. Le cadenas de la porte a été forcé. | **NC** | ? | Cave en immeuble à appartements : vol couvert à 1 000 EUR « si ces locaux sont fermés avec une serrure de sûreté » (2.10). La définition exclut le cadenas (« sauf cadenas »). Lecture stricte : non couvert ; INCERTAIN défendable (condition de garantie ou de plafond ?). |  |
| `velo-04` | Mon vélo a été volé dans ma cave privative. J'avais oublié de la fermer à clé et il n'y a aucune trace d'effraction. | **NC** | ? | Cave non fermée : pas de serrure de sûreté (condition du plafond caves), et obligation de prévention non respectée avec lien causal direct (2.10). |  |
| `velo-05` | Des cambrioleurs ont fracturé la porte de mon appartement et ont volé mon vélo, rangé dans l'entrée. | **C** |  | Vol du contenu dans le bâtiment, avec effraction. Le vélo non motorisé est du contenu (12/contenu). Franchise 7.7. |  |
| `velo-06` | Mon vélo était attaché à un arceau dans la rue avec un antivol. L'antivol a été coupé et le vélo volé. | **NC** |  | Vol dans la rue, sans violence : hors du bâtiment, et ce n'est pas un « vol commis sur l'assuré … suite à violences ». |  |
| `velo-07` | Mon vélo électrique acheté 3 500 € a été volé dans mon garage privatif fermé à clé. La porte du garage a été forcée. | **C** | ? | Garage privatif = bâtiment (12/batiment) ; effraction. Plafond 1 000 EUR si sans communication directe et serrure de sûreté (2.10). Vélo électrique ≤ 45 km/h = contenu. |  |
| `autre-01` | Mon téléphone m'a été arraché des mains dans la rue. | **C** | ? | « Vol commis sur l'assuré, en dehors des biens assurés, suite à violences physiques et/ou menaces » (2.10), plafond 2 500 EUR. L'arrachage est une violence ; INCERTAIN défendable. |  |
| `val-01` | Pendant que j'étais au travail, quelqu'un est entré par la fenêtre de ma chambre, au rez-de-chaussée, que j'avais laissée grande ouverte, et a volé mon ordinateur portable. La porte était fermée à clé, aucune trace d'effraction. | **NC** | ? | Obligation de prévention (2.10) : en cas d'absence, « fermer correctement les fenêtres […] facilement accessibles ». Lien causal direct, pas d'effraction pour l'excuser. |  |
| `val-02` | Ma femme de ménage, qui a les clés de l'appartement, m'a volé une bague en or estimée à 2 000 €. | **NC** |  | Exclusion 2.10 : le vol commis par des personnes au service privé de l'assuré. |  |
| `val-03` | Des amis que j'hébergeais pour le week-end se sont fait voler leur ordinateur lors d'un cambriolage de mon appartement : la porte d'entrée a été fracturée. | **NC** |  | Exclusion 2.10 : le vol des biens appartenant à des hôtes (alors que la définition du contenu les inclut : piège). |  |
| `val-04` | Pendant la nuit, on m'a volé la table et les chaises de jardin posées sur ma terrasse. | **NC** |  | Exclusion 2.10 : le vol du mobilier extérieur ; de plus le contenu exclut les biens destinés au jardin. |  |
| `val-05` | Au retour de vacances, je ne retrouve plus ma montre de valeur. Aucune trace de passage ni d'effraction dans l'appartement. | **NC** | ? | 2.10 : « le vol du contenu situé dans le bâtiment sauf la simple disparition ». |  |
| `val-06` | J'ai déposé mon ordinateur chez un réparateur il y a deux semaines ; la boutique a été cambriolée et mon ordinateur volé. | **C** | ? | 2.10 : le vol du contenu déposé chez un réparateur pendant max. 30 jours (limite 500 EUR). |  |
| `val-07` | Dans le métro, deux individus m'ont menacé avec un couteau et ont pris mon portefeuille et mon téléphone. | **C** | ? | 2.10 : le vol commis sur l'assuré, en dehors des biens assurés, suite à violences et/ou menaces (limite 2 500 EUR). |  |
| `val-14` | Lors d'un cambriolage avec la porte fracturée, on m'a volé mon chat de race. | **NC** |  | Exclusion 2.10 : le vol des animaux. |  |
| `val-15` | Mon scooter de 125 cm³ a été volé dans mon garage fermé à clé ; la porte a été forcée. | **NC** |  | Le contenu ne comprend pas les véhicules automoteurs de plus de 50 cc : hors garantie vol. |  |
| `g-l01` | on m'a piqué mon vélo dans le local à vélos de la résidence, la porte était même pas fermée | **NC** |  | Langue familière. Exclusion 2.10 : le vol dans les parties communes du bâtiment. |  |
| `g-l02` | Bonjour, je vous écris parce que je suis vraiment embêté. Samedi soir nous étions chez ma belle-sœur pour son anniversaire (on est rentrés vers minuit) et en rentrant on a vu que la porte de l'appartement avait été forcée, la serrure arrachée. Ils ont pris la télé, l'ordinateur de mon fils et deux vélos qu'on gardait dans l'entrée. On a porté plainte dimanche matin. | **C** |  | Déclaration longue et bavarde. 2.10 : vol du contenu dans le bâtiment, avec effraction (l'obligation de fermer est alors sans incidence). |  |
| `g-l06` | Deux types m'ont bousculé à la sortie du bus et m'ont arraché mon sac avec mon portefeuille dedans. | **C** | ? | 2.10 : vol commis sur l'assuré, en dehors des biens assurés, avec violences. |  |
| `g-q01` | On m'a volé mon vélo dans ma cave. | **?** |  | La cave n'est couverte que fermée par une serrure de sûreté : il faut le demander. |  |
| `g-q02` | Mon ordinateur portable a disparu de mon appartement. | **?** | NC | « Disparu » n'est pas « volé » : la simple disparition est exclue ; il faut établir le vol. |  |
| `g-q03` | Mon vélo a été volé pendant que je faisais mes courses. | **?** | NC | Le lieu décide (dans le bâtiment ou dehors) : il faut le demander. |  |
| `g-p01` | Mon vélo a été volé dans le local poubelles commun de la résidence, fermé à clé ; la porte a été forcée. | **NC** |  | Exclusion 2.10 : parties communes, même avec effraction. |  |
| `g-p02` | Lors d'un cambriolage avec la porte fracturée, on m'a volé des bijoux d'une valeur de 8 000 €. | **C** |  | 2.10 : couvert, mais limité à 3 500 EUR pour les bijoux (la limite n'est pas encore dans les règles). |  |
| `g-p03` | Pendant mes vacances, des cambrioleurs sont entrés avec la clé que j'avais laissée sous le paillasson ; aucune trace d'effraction. | **NC** | ? | Obligation 2.10 : ne pas laisser les clés d'accès à proximité des locaux ; lien causal direct. |  |
| `g-p09` | Mon vélo a été volé dans mon casier du club de sport. | **NC** |  | Exclusion 2.10 : le vol du contenu entreposé dans un casier d'une association sportive (et hors du bâtiment). |  |
| `g-m01` | Des cambrioleurs ont forcé la porte, volé mon ordinateur et cassé la vitre de la porte-fenêtre en partant. | **C** |  | 2.10 : vol avec effraction, et vandalisme au contenu à l'occasion du vol. |  |
| `g2-i01` | Mon vélo a été volé dans le local de mon immeuble. | **?** |  | « Le local de mon immeuble » : local commun (vol exclu dans les parties communes) ou cave privative (couverte si serrure de sûreté). Le lieu décide. |  |
| `g2-i02` | On a cambriolé mon appartement pendant le week-end où j'étais absent. La serrure porte des rayures, mais la porte s'ouvre et se ferme normalement. | **?** | C | Des traces sans réparation nécessaire ne sont pas une effraction (définition). Sans effraction, l'obligation de fermer à clé pendant l'absence joue : il faut savoir si la porte était fermée à clé. |  |
| `g2-i04` | Mes bijoux ont disparu de ma chambre après le passage du plombier. | **?** | NC | Une disparition n'est pas un vol établi (simple disparition exclue) ; et un vol par une personne autorisée à se trouver dans les locaux est exclu. |  |
| `g2-i08` | On m'a volé mon sac au restaurant. | **?** |  | Hors du bâtiment, seul le vol commis sur l'assuré avec violences ou menaces est couvert : à préciser. |  |
| `g2-i12` | Pendant mes vacances, quelqu'un est entré chez moi et a volé ma télévision ; je ne sais pas comment il est entré. | **?** | C | Vol dans le bâtiment couvert ; sans effraction connue, l'obligation de fermer à clé pendant l'absence est à vérifier. |  |
| `g2-p01` | Pendant mes vacances, des cambrioleurs ont ouvert ma porte sans la casser : il n'y a que des traces de tournevis. J'avais bien fermé à clé. | **C** |  | Pas d'effraction au sens du contrat, mais la porte était fermée à clé : l'obligation est respectée, le vol dans le bâtiment est couvert. |  |
| `g2-i07` | Mon ordinateur portable a été volé dans ma voiture, garée devant chez moi. | **NC** |  | La voiture n'est pas le bâtiment, et ce n'est pas un vol commis sur l'assuré avec violences. |  |
| `g2-p03` | On a arraché et volé les rosiers de mon jardin. | **NC** |  | Exclusion 2.10 : le vol des plantations du jardin. |  |
| `g2-p04` | On a siphonné le fioul de la cuve de chauffage, dans ma cave. | **NC** |  | Exclusion 2.10 : le vol de mazout de chauffage. |  |
| `g2-p06` | On m'a volé mes clés d'appartement dans la poche, dans le tram, sans violence. | **C** | ? | Limites de la garantie vol : le vol ou la perte des clés (500 EUR) et le remplacement des serrures. |  |
| `g2-l01` | cambriolage chez moi cette nuit, porte défoncée, ils ont pris la tv, la console et 200 € en liquide | **C** |  | Vol avec effraction dans le bâtiment (les valeurs sont limitées à 250 EUR). |  |
| `g2-l03` | Je n'étais pas absente et la porte n'était pas ouverte : quelqu'un est entré pendant que je dormais et a pris mon sac dans l'entrée. | **C** | ? | Vol du contenu dans le bâtiment ; l'obligation de fermer à clé ne vaut qu'en cas d'absence. |  |

## Garantie 2.11

| Cas | Déclaration | Attendu | Acceptable | Fondement | Validé |
|---|---|---|---|---|---|
| `g2-i17` | Des inconnus ont tagué et rayé la porte d'entrée de mon appartement. | **C** | ? | 2.11 : dégradations immobilières suite à des actes de vandalisme. Garantie non traduite. |  |

## Garantie 2.12

| Cas | Déclaration | Attendu | Acceptable | Fondement | Validé |
|---|---|---|---|---|---|
| `g2-i15` | Un champignon s'est développé derrière les plinthes et a attaqué le parquet ; l'expert parle de mérule. | **?** | C | 2.12 couvre la mérule survenue après la prise d'effet de la garantie : la date est à établir. Garantie non traduite. |  |

## Garantie aucune

| Cas | Déclaration | Attendu | Acceptable | Fondement | Validé |
|---|---|---|---|---|---|
| `g-l07` | Ce n'est pas un vol : mon fils a pris mon vélo sans me le dire et il l'a cassé en tombant. | **NC** | ? | Négation. Pas de vol (et un vol par un descendant serait exclu, 2.10-a) ; aucune garantie de base ne couvre la casse d'un vélo. |  |
| `g-p08` | Pendant la tempête, un arbre est tombé sur ma voiture garée dans la rue. | **NC** | ? | Un véhicule à moteur n'est pas du contenu, et il était hors du bâtiment. |  |
