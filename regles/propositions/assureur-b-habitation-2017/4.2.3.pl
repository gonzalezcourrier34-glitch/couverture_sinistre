% --- Art. 4.2.3 : proposition rédigée par le modèle — mistral:mistral-large-4-0 (proposition écartée), 2026-11-24 ---
evenement_traduit(voyage).
garantie(assistance_voyage, "Assistance voyage (option)", '4.2.3.2',
    "Assureur B Assistance garantit, à concurrence des montants indiqués, taxes comprises, un service d’assistance lorsque les Assurés sont victimes des événements aléatoires définis dans le présent contrat").
perimetre(assistance_voyage, f(evenement, voyage)).
perimetre(assistance_voyage, ou([f(objet_voyage, incident_medical), f(objet_voyage, soins_sans_hospitalisation), f(objet_voyage, sauvetage_ou_ski), f(objet_voyage, deces), f(objet_voyage, retour_anticipe), f(objet_voyage, perte_bagage), f(objet_voyage, retard_bagage), f(objet_voyage, perte_papiers), f(objet_voyage, poursuites_etranger), f(objet_voyage, enfant_hospitalise), f(objet_voyage, animal)])).
circonstance(assistance_voyage, f(option_assistance_voyage, oui), '4.2.3',
    "la garantie “assistance voyage” est souscrite").
circonstance(assistance_voyage, ou([ou([f(objet_voyage, soins_sans_hospitalisation), f(objet_voyage, sauvetage_ou_ski), f(objet_voyage, animal)]), f(assistance_voyage_appelee, oui)]), '4.2.3.3',
    "Ces événements doivent obligatoirement faire l’objet d’une demande d’intervention auprès d’Assureur B Assistance au moment des faits, sauf disposition contraire expresse propre à certaines garanties").
exclusion(assistance_voyage, f(voyage_plus_90_jours, oui), tout, non, '4.2.3.3',
    "La garantie de la présente convention est limitée aux déplacements de 90 jours calendaires consécutifs au maximum").
exclusion(assistance_voyage, f(destination_deconseillee, oui), tout, non, '4.2.3.3',
    "La garantie n’est pas acquise lorsque, nonobstant la déclaration officielle du Ministère desAffaires Etrangères qui déconseille à ses ressortissants de se rendre dans un pays en état de troubles, d’émeutes, de guerres ou de guerres civiles, l’Assuré décide néanmoins d’entreprendre son voyage").
exclusion(assistance_voyage, ou([f(cause_assistance_exclue, activite_dangereuse), f(cause_assistance_exclue, acte_intentionnel), f(cause_assistance_exclue, ivresse_ou_defi), f(cause_assistance_exclue, guerre_greve_emeute), f(cause_assistance_exclue, nucleaire), f(cause_assistance_exclue, competition_ou_sport_dangereux)]), tout, non, '4.2.3.8',
    "les activités à caractère dangereux telles que celles d’acrobate, de dompteur ou scaphandrier").
exclusion(assistance_voyage, et([ou([f(objet_voyage, incident_medical), f(objet_voyage, soins_sans_hospitalisation)]), ou([f(etat_sante_exclu, affection_benigne), f(etat_sante_exclu, maladie_mentale_deja_traitee), f(etat_sante_exclu, grossesse_avancee_ou_ivg), f(etat_sante_exclu, maladie_chronique_ou_en_traitement), f(etat_sante_exclu, soins_au_pays), f(etat_sante_exclu, prothese_cure_prevention)])]), tout, non, '4.2.3.8',
    "les affections ou lésions bénignes qui n’empêchent pas l’Assuré de poursuivre son voyage ; n les maladies mentales et les états psychiatriques ayant déjà fait l’objet d’un traitement ; n les états de grossesse après la 26ème semaine et les interruptions volontaires de grossesse").
exclusion(assistance_voyage, et([f(objet_voyage, sauvetage_ou_ski), f(ski_hors_piste, oui)]), tout, non, '4.2.3.4',
    "Cette garantie est exclue lorsque le sinistre survient suite à la pratique du ski effectué hors pistes balisées sans guide agréé par les autorités du pays").
exclusion(assistance_voyage, et([f(objet_voyage, retour_anticipe), f(evenement_previsible_au_depart, oui)]), tout, non, '4.2.3.4',
    "uniquement si la maladie ou le décès présente un caractère imprévisible au moment du départ de l’Assuré à l’étranger").
exclusion(assistance_voyage, et([f(objet_voyage, poursuites_etranger), f(suite_accident_circulation, non)]), tout, non, '4.2.3.6',
    "Si, à la suite d’un accident de la circulation à l’étranger, l’Assuré tombe sous le coup de poursuites judiciaires").
limite(assistance_voyage, '4.2.3.4', "à concurrence d’un maximum de 150.000 f par Assuré", "150000").
