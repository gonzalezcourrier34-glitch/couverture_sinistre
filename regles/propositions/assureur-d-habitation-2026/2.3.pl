% --- Art. 2.3 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-20 ---
evenement_traduit(tempete).
garantie(tempete_grele_neige, "Tempête, grêle, neige sur les toitures", '2.3-a',
    "La garantie couvre les dommages matériels causés aux biens assurés par l’action directe : • du vent ou du choc d’un objet renversé ou projeté par le vent (garantie tempête)").
perimetre(tempete_grele_neige, f(evenement, tempete)).
perimetre(tempete_grele_neige, ou([concept(contenu), f(bien, element_batiment)])).
perimetre(tempete_grele_neige, concept(batiment)).
circonstance(tempete_grele_neige, si(f(alea_tempete, vent), ou([f(vent_dommages_voisins, oui), f(vent_100_kmh, oui)])), '2.3-a',
    "lorsque ces phénomènes ont une intensité telle qu’ils détruisent ou endommagent d’autres bâtiments de bonne construction dans le voisinage ou que leur caractère exceptionnel est attesté par un certificat de la station météorologique la plus proche (vitesse supérieure à 100 km/h dans le cas du vent)").
circonstance(tempete_grele_neige, si(f(alea_tempete, neige_glace), ou([f(neige_dommages_voisins, oui), f(certificat_meteo, oui)])), '2.3-a',
    "lorsque ces phénomènes ont une intensité telle qu’ils détruisent ou endommagent d’autres bâtiments de bonne construction dans le voisinage ou que leur caractère exceptionnel est attesté par un certificat de la station météorologique la plus proche (vitesse supérieure à 100 km/h dans le cas du vent)").
exclusion(tempete_grele_neige, et([f(alea_tempete, vent), f(construction_close, non)]), tout, oui, '2.3-b',
    "les dommages occasionnés par le vent aux bâtiments dont les éléments porteurs ne sont pas ancrés, à ceux qui ne sont pas construits selon les règles de l’art ou qui ne sont pas entièrement clos et couverts, ainsi qu’à leur contenu").
exclusion(tempete_grele_neige, et([ou([f(lieu, jardin), f(lieu, terrasse)]), non(et([f(bien, mobilier_jardin), f(pack_jardin, oui)]))]), tout, oui, '2.3-b',
    "les objets en plein air, sauf pour le mobilier de jardin assuré dans le Pack Jardin s’il est souscrit").
