% --- Art. 12.1 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(responsabilite).
garantie(rc_proprietaire_voisins, "Responsabilité civile du propriétaire : incendie, explosion, eau", '12.1-a~1',
    "• Envers les voisins et les tiers La garantie couvre les conséquences financières de votre responsabilité civile à raison : - des dommages matériels et immatériels consécutifs subis par les voisins et les tiers à la suite d’un incendie, d’une explosion, d’une venue d’eau ayant pris naissance dans le local d’habitation et/ou des dépendances assurés").
perimetre(rc_proprietaire_voisins, f(evenement, responsabilite)).
perimetre(rc_proprietaire_voisins, f(statut_logement, proprietaire)).
perimetre(rc_proprietaire_voisins, f(origine_rc, habitation)).
exclusion(rc_proprietaire_voisins, ou([f(victime, assure), f(victime, conjoint), f(victime, famille), f(victime, prepose)]), tout, non, '12.1-a~2',
    "Toute personne autre que : • vous-même, votre conjoint ou concubin (signataire ou non d’un PACS) non séparé, vos ascendants et descendants, • le personnel de garde ou d’entretien pendant son service").
garantie(rc_proprietaire_immeuble, "Responsabilité civile du propriétaire : accident causé par l'habitation", '12.1-a~2',
    "des dommages corporels, matériels et immatériels consécutifs causés aux tiers à la suite d’un accident occasionné pendant la période de validité du contrat par : • l’habitation désignée aux conditions particulières, y compris le terrain, les plantations, les clôtures et leurs aménagements").
perimetre(rc_proprietaire_immeuble, f(evenement, responsabilite)).
perimetre(rc_proprietaire_immeuble, f(statut_logement, proprietaire)).
perimetre(rc_proprietaire_immeuble, f(origine_rc, immeuble)).
exclusion(rc_proprietaire_immeuble, ou([f(victime, assure), f(victime, conjoint), f(victime, famille), f(victime, prepose)]), tout, non, '12.1-a~2',
    "Toute personne autre que : • vous-même, votre conjoint ou concubin (signataire ou non d’un PACS) non séparé, vos ascendants et descendants, • le personnel de garde ou d’entretien pendant son service").
