% --- Art. 2.5 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(responsabilite).
garantie(rc_immeuble, "Responsabilité civile immeuble", '2.5',
    "Nous prenons en charge la responsabilité civile que vous pouvez encourir sur base : • du livre 6 du Code civil • de l’article 1721 du Code civil c'est-à-dire le recours des locataires pour les dommages causés aux tiers du fait : • du bâtiment, du contenu").
perimetre(rc_immeuble, f(evenement, responsabilite)).
perimetre(rc_immeuble, ou([f(origine_rc, immeuble), f(origine_rc, habitation)])).
exclusion(rc_immeuble, ou([f(victime, assure), f(victime, conjoint)]), tout, non, '12/tiers',
    "Toute personne qui n’est pas considérée comme assurée.").
exclusion(rc_immeuble, f(bien_confie, oui), tout, non, '2.5-a',
    "à des biens dont vous avez la garde").
limite(rc_immeuble, '2.5', "18.425.000 EUR pour l’indemnisation des dommages résultant de lésions corporelles", "18425000").
limite(rc_immeuble, '2.5', "3.685.000 EUR pour l’indemnisation des dommages résultant de dégâts matériels", "3685000").
