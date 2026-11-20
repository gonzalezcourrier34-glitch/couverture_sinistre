:- encoding(utf8).
/*  Règles du contrat Assureur D « Multirisque Habitation » (conditions générales, 04/2026).

    Troisième contrat du projet (DEMARCHE 7.87) : le même moteur (regles/moteur.pl) et le même vocabulaire de
    faits (regles/vocabulaire.json) que pour les assureurs A et B. Contrat français, en trois formules (Eco,
    Confort, Excellence), avec des packs et des garanties optionnels. Aucune règle n'est écrite à la main :
    chaque garantie est rédigée par Mistral Large (`couverture rediger --contrat assureur-d-habitation-2026
    --article 2.5`), contrôlée par le code, relue, puis ajoutée ici par `couverture rediger --accepter`.

    Tant qu'aucune garantie n'est ajoutée, aucun événement n'est traduit : le moteur ne conclut jamais à un
    refus, il répond « à examiner par un gestionnaire ».
*/

:- discontiguous definition/4, precision/3, garantie/4, perimetre/2, circonstance/4,
                 obligation/6, exclusion/6, limite/4, evenement_traduit/1, accessoire/1.

% --- Art. 1.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
definition(batiment, ou([f(lieu, logement), f(lieu, grenier), f(lieu, parties_communes), f(lieu, cave), f(lieu, garage), f(lieu, annexe), f(lieu, abri_jardin)]), '1.1-a',
    "votre local d’habitation, c’est-à-dire les parties immobilières des bâtiments principaux d’habitation destinées à un usage privé").
exclusion(tous, et([f(bien, veranda), non(f(option_veranda, oui))]), bien(veranda), non, '1.1-b',
    "les vérandas, sauf mention aux conditions particulières").
exclusion(tous, f(bien, eolienne), bien(eolienne), non, '1.1-b',
    "les éoliennes").
exclusion(tous, et([f(bien, panneau_solaire), non(f(formule, excellence))]), bien(panneau_solaire), non, '1.1-b',
    "les panneaux solaires et photovoltaïques si vous avez souscrit les formules Eco et Confort").
exclusion(tous, et([f(bien, piscine), non(f(pack_piscine, oui))]), bien(piscine), non, '1.1-b',
    "les piscines, spas et jacuzzi").
exclusion(tous, et([f(bien, plantation), non(f(pack_jardin, oui))]), bien(plantation), non, '1.1-b',
    "les plantations").
exclusion(tous, f(local_inoccupe_12_mois, oui), tout, non, '1.1-b',
    "les locaux inoccupés ou inutilisés depuis plus de 12 mois consécutifs").

% --- Art. S25 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
exclusion(tous, ou([f(intentionnel, oui), et([f(participation_rixe, oui), non(f(legitime_defense, oui))])]), tout, non, 'S25',
    "les dommages causés intentionnellement ou frauduleusement par vous ou par un complice, ou résultant de votre ou de sa participation à une action violente ou à une rixe (sauf légitime défense)").
exclusion(tous, f(manque_entretien, oui), tout, non, 'S25',
    "ceux qui résultent directement d’un défaut de réparation ou d’entretien indispensables vous incombant et dont vous aviez connaissance").
exclusion(tous, et([ou([f(cause_guerre, oui), f(cause_nucleaire, oui)]), non(f(evenement, attentat))]), tout, non, 'S25',
    "de la guerre civile ou étrangère, - de tout combustible, produit ou déchet radioactif, de tout engin destiné à irradier ou à exploser par modification du noyau de l’atome ainsi que leur décontamination, sauf pour les dommages matériels directs causés par un attentat ou un acte de terrorisme").
