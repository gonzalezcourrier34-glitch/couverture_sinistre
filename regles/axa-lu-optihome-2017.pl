:- encoding(utf8).
/*  Règles du contrat AXA Luxembourg « OptiHome » (conditions d'assurances, 06/2017).

    Deuxième contrat du projet (DEMARCHE 7.51, 7.52) : le même moteur (regles/moteur.pl) et le même
    vocabulaire de faits (regles/vocabulaire.json) que pour Foyer. Les règles ne sont pas écrites à
    la main : chaque garantie est rédigée par Mistral Large (`couverture rediger --contrat
    axa-lu-optihome-2017 --article 3.1.6`), contrôlée par le code, relue, puis ajoutée ici par
    `couverture rediger --accepter`.

    Tant qu'aucune garantie n'est ajoutée, aucun événement n'est traduit : le moteur ne conclut
    jamais à un refus, il répond « à examiner par un gestionnaire ».
*/

:- discontiguous definition/4, precision/3, garantie/4, perimetre/2, circonstance/4,
                 obligation/6, exclusion/6, limite/4, evenement_traduit/1.
