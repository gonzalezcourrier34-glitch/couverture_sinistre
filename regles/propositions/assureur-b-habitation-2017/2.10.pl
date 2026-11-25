% --- Art. 2.10 : proposition rédigée par le modèle — aucun : écrite à la main, 2026-11-25 ---
exclusion(tous, et([f(intentionnel, oui), non(f(auteur, tiers))]), tout, non, '2.10',
    "les dommages occasionnés par la faute intentionnelle ou dolosive de l’Assuré ou bien avec sa complicité").
exclusion(tous, et([f(glissement_terrain, oui), non(f(evenement, catastrophe_naturelle))]), tout, non, '2.10',
    "une chute de pierres ou de rochers, un glissement de terrain ou un affaissement").
exclusion(tous, f(cause_guerre, oui), tout, non, '2.10',
    "les dommages résultant d’une guerre ou des faits de même nature, d’une agression bactériologique ou chimique, d’une guerre civile").
exclusion(tous, f(cause_nucleaire, oui), tout, non, '2.10',
    "provenant de transmutation de noyaux d’atome ou de la radioactivité").
