% --- Art. 3.3.2 : proposition rédigée par le modèle — mistral:mistral-large-4-0, 2026-11-24 ---
evenement_traduit(assistance).
garantie(assistance_handyman, "Assistance Handyman", '3.3.2',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie ” Assistance Handyman ” est accordée.").
perimetre(assistance_handyman, f(evenement, assistance)).
perimetre(assistance_handyman, concept(batiment_designe)).
exclusion(assistance_handyman, f(facture_prestataire, oui), tout, oui, '3.3.2.2',
    "Le montant total de la facture relative à l’intervention du prestataire n’est jamais prise en charge par Assureur B Assistance. Il reste à la charge exclusive de l’Assuré.").
exclusion(assistance_handyman, ou([f(impossibilite_technique, oui), f(manque_securite, oui)]), tout, oui, '3.3.2.1',
    "Si la prestation ne peut pas être assurée vu le manque de sécurité ou en raison de son impossibilité technique, l’Assuré n’a pas droit à une indemnisation.").
exclusion(assistance_handyman, non(f(option_assistance_handyman, oui)), tout, oui, '3.3.2',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie ” Assistance Handyman ” est accordée.").
