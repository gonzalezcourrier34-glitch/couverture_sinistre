% --- Art. 2.6 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-18 ---
evenement_traduit(electricite).
garantie(action_electricite, "Action de l'électricité", '2.6',
    "Nous couvrons les dommages matériels directement causés par l’action de l’électricité, y compris : • l’électrocution des animaux domestiques, • la décongélation ou détérioration des denrées alimentaires utilisées dans le cadre de votre vie privée, suite à l’arrêt d’une durée de 6 heures ou au dérangement d’une installation de réfrigération ou de congélation provoqué par l’action de l’électricité ou par une coupure de courant soudaine et imprévisible suite à un dysfonctionnement du réseau de distribution d’électricité. Nous prenons également en charge les frais liés à la recherche, la réparation ou le remplacement de la pièce défectueuse à l'origine du sinistre, ainsi que la remise en état consécutive.").
perimetre(action_electricite, f(evenement, electricite)).
perimetre(action_electricite, concept(batiment)).
circonstance(action_electricite, si(f(bien, denrees_alimentaires), ou([f(cause_perte_alimentaire, arret_6h), f(cause_perte_alimentaire, derangement_installation), f(cause_perte_alimentaire, coupure_soudaine_reseau)])), '2.6',
    "suite à l’arrêt d’une durée de 6 heures ou au dérangement d’une installation de réfrigération ou de congélation provoqué par l’action de l’électricité ou par une coupure de courant soudaine et imprévisible suite à un dysfonctionnement du réseau de distribution d’électricité").
limite(action_electricite, '2.6', "Perte de denrées alimentaires suite à une variation de température due à une panne 500 EUR de courant d’au moins 6 heures (y compris blackout", "500 EUR").
exclusion([action_electricite], et([ou([f(bien, electronique), f(bien, appareil_informatique)]), f(usage_professionnel, oui)]), bien(appareil_informatique), non, '2.6-a',
    "les dommages aux appareils électroniques et informatiques dont l’usage est professionnel").
exclusion([action_electricite], et([f(bien, appareil_informatique), non(concept(batiment)), non(f(usage_professionnel, oui))]), bien(appareil_informatique), non, '2.6-a',
    "ainsi que les dommages aux autres appareils informatiques en dehors du bâtiment assuré").
exclusion([action_electricite], f(garantie_fabricant, oui), tout, non, '2.6-a',
    "les dégâts tombant sous la garantie du fabriquant ou du fournisseur").
