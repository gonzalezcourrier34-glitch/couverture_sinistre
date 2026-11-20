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
