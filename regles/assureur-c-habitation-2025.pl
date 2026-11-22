:- encoding(utf8).
/*  Règles du contrat assureur-c-habitation-2025.

    Le même moteur (regles/moteur.pl) et le même vocabulaire de faits (regles/vocabulaire/) que pour les autres
    contrats. Aucune règle n'est écrite à la main : chaque garantie est rédigée par un modèle (`couverture rediger
    --contrat assureur-c-habitation-2025 --article …`), contrôlée par le code, relue, puis ajoutée ici par
    `couverture rediger --accepter`.

    Tant qu'aucune garantie n'est ajoutée, aucun événement n'est traduit : le moteur ne conclut jamais à un
    refus, il répond « à examiner par un gestionnaire ».
*/

:- discontiguous definition/4, precision/3, garantie/4, perimetre/2, circonstance/4,
                 obligation/6, exclusion/6, limite/4, evenement_traduit/1, accessoire/1.
% --- Art. S8 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-22 ---
evenement_traduit(vol).
definition(dependances, ou([f(lieu, garage), f(lieu, annexe), f(lieu, abri_jardin)]), 'S1/dependances',
    "Ensemble des locaux sous toiture, distincts ou non du bâtiment d’habitation, qui ne sont ni à usage d’habitation ni à usage professionnel, et qui ne sont pas des pièces annexes.").
definition(objets_de_valeur, ou([et([ou([f(bien, bijoux), f(bien, objet_art), f(bien, tapis_fourrure)]), non(f(valeur_unitaire, moins_200))]), f(bien, collection), f(valeur_unitaire, plus_5000)]), 'S1/objets-de-valeur',
    "Il s’agit : - des bijoux, montres et objets d’horlogerie, pierreries, perles, objets en métal précieux massif (or, argent, platine, vermeil) d’une valeur unitaire supérieure à 200 euros, - des sculptures, tableaux, dessins d’art, tapisseries, livres rares d’une valeur unitaire supérieure à 200 euros, - des tapis, fourrures d’une valeur unitaire supérieure à 200 euros, - des collections d’au moins 50 objets et dont la valeur globale par collection est supérieure à 5 000 euros, - de tout objet dont la valeur unitaire est supérieure à 5 000 euros.").
definition(objets_usuels, non(concept(objets_de_valeur)), 'S1/objets-usuels',
    "Tous les objets qui ne sont pas des objets de valeur.").
definition(lieu_de_vacances, et([f(sejour_temporaire, oui), f(lieu, autre_batiment)]), 'S1/lieu-de-vacances',
    "Lieu de séjours temporaires, d’une durée inférieure à 3 mois consécutifs, dans un bâtiment n’appartenant pas à l’assuré, autre que l’habitation assurée désignée aux Conditions Particulières.").
definition(inhabitation, ou([f(inhabitation, plus_3_jours), f(inhabitation, plus_45_jours)]), 'S1/inhabitation',
    "Période, supérieure à 3 jours, pendant laquelle les locaux sont inoccupés par l’assuré ou par toute autre personne connue ou autorisée par l’assuré.").
garantie(vol_batiment, "Vol dans l'habitation et ses dépendances", 'S8-a',
    "Le vol des biens assurés commis à l’intérieur des parties du bâtiment à usage d’habitation ou à l’intérieur des dépendances,").
perimetre(vol_batiment, f(evenement, vol)).
perimetre(vol_batiment, ou([f(lieu, logement), f(lieu, cave), f(lieu, grenier), concept(dependances), f(lieu, parties_communes)])).
circonstance(vol_batiment, ou([f(formule, confort), f(formule, optimale), et([f(formule, initiale), f(option_vol, oui)])]), 'S8',
    "Cette garantie vous est acquise si vous avez souscrit une formule Initiale avec option Vol, une formule Confort ou une formule Optimale.").
circonstance(vol_batiment, ou([f(effraction, oui), et([f(acces_voleur, escalade), f(hauteur_ouverture, plus_3m)]), f(violence, oui), f(acces_voleur, menaces), f(acces_voleur, fausse_qualite)]), 'S8-a',
    "- par effraction extérieure des locaux renfermant les biens assurés, - ou par escalade directe des locaux renfermant les biens assurés par une porte ou une fenêtre située à plus de 3 mètres de hauteur, - ou avec violences ou menaces sur les personnes présentes, - ou avec fausse qualité ou fausse identité prise par un ou plusieurs individus pour s’introduire et voler dans les bâtiments renfermant les biens assurés.").
limite(vol_batiment, 'S8-b', "Des mesures de protection sont exigées, elles sont indiquées dans vos Conditions Particulières.", "réduction de moitié si elles ne sont pas respectées").
limite(vol_batiment, 'S8-b', "En cas d’absence de plus de 24 heures, vous devez utiliser tous les moyens de fermeture et de protection existants. Le non-respect des mesures de protection entrainera une réduction de moitié de l’indemnisation à laquelle vous auriez pu avoir droit, si celui-ci a permis la réalisation du vol pour autant qu’il y ait un lien de cause à effet entre le sinistre et le nonrespect de ces mesures.", "réduction de moitié").
limite(vol_batiment, 'S8-d', "Reportez-vous à la page 19.", "voir « Montants maximums des garanties » (S14)").
garantie(vol_lieu_vacances, "Vol sur le lieu de vacances", 'S8-a',
    "Le vol sur le lieu de vacances des objets usuels de l’assuré commis à l’intérieur d’un bâtiment à usage d’habitation,").
perimetre(vol_lieu_vacances, f(evenement, vol)).
perimetre(vol_lieu_vacances, concept(lieu_de_vacances)).
perimetre(vol_lieu_vacances, concept(objets_usuels)).
circonstance(vol_lieu_vacances, et([ou([f(formule, confort), f(formule, optimale)]), f(residence_principale, oui)]), 'S8-a',
    "Pour les formules Confort et Optimale si l’habitation assurée est une résidence principale").
circonstance(vol_lieu_vacances, ou([f(effraction, oui), et([f(acces_voleur, escalade), f(hauteur_ouverture, plus_3m)]), f(violence, oui), f(acces_voleur, menaces)]), 'S8-a',
    "- par effraction extérieure des locaux renfermant les biens assurés, - ou par escalade directe des locaux renfermant les biens assurés par une porte ou une fenêtre située à plus de 3 mètres de hauteur, - ou avec violences ou menaces sur les personnes présentes.").
exclusion([vol_batiment, vol_lieu_vacances], f(cles_a_proximite, oui), tout, oui, 'S8-e',
    "Le vol consécutif au maintien des clés laissées sur la porte, sous le paillasson, dans un pot de fleurs, dans la boîte aux lettres ou dans une boîte à clés verrouillée").
exclusion([vol_batiment, vol_lieu_vacances], f(changement_serrures_48h, non), tout, non, 'S8-e',
    "ou consécutif à l’absence de changement des serrures dans les 48 heures suivant la constatation d’un vol ou d’une perte de clés.").
exclusion([vol_batiment, vol_lieu_vacances], et([concept(dependances), non(f(porte_pleine_verrou, oui))]), tout, oui, 'S8-f',
    "Le vol dans les dépendances ou dans les locaux sans • communication intérieure et privée avec les locaux d’habitation qui ne seraient pas protégés par une porte pleine munie d’un verrou ou d’une serrure ; les verrous sans clé et les cadenas ne sont pas considérés comme des serrures.").
exclusion([vol_batiment, vol_lieu_vacances], f(auteur, famille), tout, non, 'S8-f',
    "Le vol dont serait auteur ou complice votre conjoint ou concubin ou partenaire d’un Pacte Civil de solidarité (PACS) ou vos ascendants, descendants, frères, sœurs ainsi que leurs conjoints, concubins ou partenaire d’un PACS.").
exclusion([vol_batiment, vol_lieu_vacances], f(auteur, locataire), tout, non, 'S8-f',
    "Le vol commis par vos locataires, sous-locataires, ainsi que leur conjoint ou concubin ou partenaire d’un Pacte Civil de solidarité (PACS), ascendants et descendants.").
exclusion([vol_batiment, vol_lieu_vacances], f(lieu, parties_communes), tout, non, 'S8-f',
    "Les vols des biens déposés dans les locaux à usage commun des occupants de l’immeuble.").
exclusion([vol_batiment, vol_lieu_vacances], et([concept(objets_de_valeur), ou([concept(dependances), f(lieu, veranda)])]), tout, oui, 'S8-f',
    "Le vol des objets de valeur dans les dépendances et les locaux sans communication intérieure et privée avec les locaux d’habitation ou dans les vérandas.").
exclusion([vol_batiment, vol_lieu_vacances], et([concept(objets_de_valeur), ou([et([f(residence_principale, oui), f(inhabitation, plus_45_jours)]), et([f(residence_principale, non), concept(inhabitation)])])]), tout, oui, 'S8-c',
    "La garantie vol des objets de valeur, pour les formules Confort et Optimale, est suspendue : - en résidence principale, si l’inhabitation de vos locaux dépasse 45 jours consécutifs, dès le 46e jour et pendant toute la période d’inhabitation, - en résidence secondaire, dès le début de la période d’inhabitation.").

% --- Art. S10 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-22 ---
evenement_traduit(bris).
garantie(bris_glaces_batiment, "Bris de glaces du bâtiment", 'S10-a',
    "Le bris des produits verriers (ou ceux en matière plastique remplissant les mêmes fonctions) constituant : - la clôture et la couverture de vos locaux y compris les fenêtres de toit, - les miroirs fixés ou accrochés au mur, - les portes et les cloisons intérieures verticales qui séparent une pièce d’une autre, - les parois de balcons, les vérandas.").
perimetre(bris_glaces_batiment, f(evenement, bris)).
perimetre(bris_glaces_batiment, ou([f(bien, vitre), f(bien, miroir), f(bien, coupole), f(bien, panneau_verre_plastique), f(bien, veranda)])).
circonstance(bris_glaces_batiment, ou([f(formule, confort), f(formule, optimale), f(formule, investisseur)]), 'S10',
    "Cette garantie vous est acquise si vous avez souscrit une formule Confort, Optimale ou Investisseur.").
limite(bris_glaces_batiment, 'S10-b', "Reportez-vous à la page 19.", "voir « Montants maximums des garanties » (S14)").
garantie(bris_glaces_meubles, "Bris de glaces des meubles (formule Optimale)", 'S10-a',
    "Est également pris en charge le bris de glaces sur les meubles meublants ci-dessous : les vitres ou miroirs qui constituent des éléments des biens - mobiliers assurés, - les vitres d’inserts, les aquariums, - les parois de douche.").
perimetre(bris_glaces_meubles, f(evenement, bris)).
perimetre(bris_glaces_meubles, ou([f(bien, verre_meuble), f(bien, insert), f(bien, aquarium), f(bien, paroi_douche)])).
circonstance(bris_glaces_meubles, f(formule, optimale), 'S10-a',
    "Si vous avez souscrit la formule Optimale").
garantie(bris_cloture_provisoire, "Frais de clôture provisoire", 'S10-a',
    "nous vous remboursons également les frais de clôture provisoire, par des panneaux non vitrés").
circonstance(bris_cloture_provisoire, f(protection_habitation_compromise, oui), 'S10-a',
    "Dans la mesure où le bris de glaces met en cause la protection de votre habitation,").
limite(bris_cloture_provisoire, 'S10-a', "(voir page 19, montants maximums des pertes pécuniaires et des frais complémentaires)", "voir « Les frais complémentaires » (S16)").
accessoire(bris_cloture_provisoire).
exclusion([bris_glaces_batiment, bris_glaces_meubles, bris_cloture_provisoire], ou([f(travaux_vitres, autres_que_nettoyage), f(vitrage_en_deplacement, oui)]), tout, oui, 'S10-c',
    "Les dommages causés aux objets assurés ou à leurs • encadrements, survenant lors de travaux de toute nature (y compris lors de leur pose, dépose, transport ou entrepôt) à l’exception des travaux de nettoyage.").
exclusion([bris_glaces_batiment, bris_glaces_meubles, bris_cloture_provisoire], f(defaut_encadrement, oui), tout, non, 'S10-c',
    "Les dommages résultant de défauts sur les enchâssements, encadrements et soubassements.").
exclusion([bris_glaces_batiment, bris_glaces_meubles, bris_cloture_provisoire], f(type_dommage, rayure_ou_ecaillement), tout, non, 'S10-c',
    "Les rayures, ébréchures, écaillures.").
exclusion([bris_glaces_batiment, bris_glaces_meubles, bris_cloture_provisoire], f(bien, vitrail), bien(vitrail), non, 'S10-c',
    "Les vitraux, les marquises, les serres.").
exclusion([bris_glaces_batiment, bris_glaces_meubles, bris_cloture_provisoire], f(bien, marquise), bien(marquise), non, 'S10-c',
    "Les vitraux, les marquises, les serres.").
exclusion([bris_glaces_batiment, bris_glaces_meubles, bris_cloture_provisoire], f(bien, serre), bien(serre), non, 'S10-c',
    "Les vitraux, les marquises, les serres.").
exclusion([bris_glaces_batiment, bris_glaces_meubles, bris_cloture_provisoire], et([ou([f(bien, verre_meuble), f(bien, insert), f(bien, aquarium), f(bien, paroi_douche)]), non(f(formule, optimale))]), tout, oui, 'S10-c',
    "Les bris de vitres ou miroirs qui constituent des éléments des biens mobiliers assurés, les vitres d’inserts, les aquariums, les parois de douche, sauf si vous avez souscrit la formule Optimale.").
