% --- Art. 4.2.3 : proposition rédigée par le modèle — mistral:mistral-large-4-0, 2026-11-24 ---
definition(accident_corporel, et([f(evenement, accident), f(dommage_tiers, corporel), non(f(intentionnel, oui))]), '4.2.3.1',
    "Accident corporel Evénement soudain indépendant de la volonté de l'Assuré qui entraîne une lésion corporelle constatée par une autorité médicale compétente et dont l'une des causes est extérieure à l'organisme de la victime.").
definition(incident_medical, ou([concept(accident_corporel), f(evenement, maladie)]), '4.2.3.1',
    "Incident médical La maladie ou l'accident corporel survenant à un Assuré.").
garantie(assistance_voyage, "Assistance voyage", '4.2.3',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie \"assistance voyage\" est souscrite.").
perimetre(assistance_voyage, f(evenement, assistance)).
perimetre(assistance_voyage, f(sejour_temporaire, oui)).
circonstance(assistance_voyage, f(duree_sejour, moins_90_jours), '4.2.3.3',
    "La garantie de la présente convention est limitée aux déplacements de 90 jours calendaires consécutifs au maximum.").
obligation(assistance_voyage, f(declaration_assistance, oui), faux, non, '4.2.3.3',
    "Ces événements doivent obligatoirement faire l'objet d'une demande d'intervention auprès d'Assureur B Assistance au moment des faits, sauf disposition contraire expresse propre à certaines garanties.").
exclusion(assistance_voyage, f(cause_guerre, oui), tout, oui, '4.2.3.8',
    "les événements résultant de faits de guerre, une mobilisation générale, une réquisition des hommes et du matériel par les autorités, le terrorisme ou le sabotage, ou de conflits sociaux tels que grève, lock-out, émeute ou mouvement populaire, à moins que l'Assuré démontre qu'il n'a pas participé à cet événement").
exclusion(assistance_voyage, f(intentionnel, oui), tout, oui, '4.2.3.8',
    "les événements provoqués par un acte intentionnel, par suicide ou tentative de suicide de l'Assuré").
exclusion(assistance_voyage, f(activite_dangereuse, oui), tout, oui, '4.2.3.8',
    "les activités à caractère dangereux telles que celles d'acrobate, de dompteur ou scaphandrier ou l'une des activités professionnelles ci-après : des montées sur toit, sur échelles ou échafaudages ; descentes en puits, mines ou carrières en galeries ; fabrication, usage ou manipulation d'artifices ou d'explosifs").
exclusion(assistance_voyage, f(etat_ivresse, oui), tout, oui, '4.2.3.8',
    "le besoin d'assistance qui est survenu alors que l'Assuré se trouve en état d'ivresse, d'intoxication alcoolique punissable ou dans un état analogue résultant de produits autres que des boissons alcoolisées ou accomplit un acte téméraire, un pari ou un défi").
exclusion(assistance_voyage, non(f(option_assistance_voyage, oui)), tout, oui, '4.2.3',
    "Les présentes conditions spéciales sont applicables si les conditions particulières mentionnent que la garantie \"assistance voyage\" est souscrite.").
limite(assistance_voyage, '4.2.3.3', "La garantie de la présente convention est limitée aux déplacements de 90 jours calendaires consécutifs au maximum.", "90 jours").
accessoire(assistance_voyage).
