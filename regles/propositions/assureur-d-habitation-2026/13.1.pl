% --- Art. 13.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(responsabilite).
garantie(rc_vie_privee, "Responsabilité civile vie privée", '13.1-a~1',
    "La garantie couvre les conséquences financières de la responsabilité civile que les assurés peuvent encourir dans le cadre de leur vie privée, en raison de dommages corporels, matériels et immatériels consécutifs causés aux tiers").
perimetre(rc_vie_privee, f(evenement, responsabilite)).
exclusion(rc_vie_privee, f(origine_rc, activite_professionnelle), tout, non, '13.1-a~1',
    "dans le cadre de leur vie privée").
exclusion(rc_vie_privee, ou([f(victime, assure), f(victime, conjoint)]), tout, non, '13.1-a~3',
    "le responsable du sinistre et son conjoint ou concubin (signataire ou non d’un PACS)").
exclusion(rc_vie_privee, et([f(victime, famille), f(dommage_tiers, materiel)]), tout, oui, '13.1-a~3',
    "leurs ascendants et descendants, frères et sœurs et leurs conjoints pour les dommages matériels").
exclusion(rc_vie_privee, f(victime, prepose), tout, non, '13.1-a~3',
    "les préposés attachés à votre service privé pendant la durée de leur service").
