% --- Art. S10 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-22 ---
evenement_traduit(bris).
garantie(bris_glaces_batiment, "Bris de glaces du bâtiment", 'S10-a',
    "Le bris des produits verriers (ou ceux en matière plastique remplissant les mêmes fonctions) constituant : - la clôture et la couverture de vos locaux y compris les fenêtres de toit, - les miroirs fixés ou accrochés au mur, - les portes et les cloisons intérieures verticales qui séparent une pièce d’une autre, - les parois de balcons, les vérandas.").
perimetre(bris_glaces_batiment, f(evenement, bris)).
perimetre(bris_glaces_batiment, ou([f(bien, vitre), f(bien, miroir), f(bien, coupole), f(bien, panneau_verre_plastique), f(bien, veranda)])).
circonstance(bris_glaces_batiment, ou([f(formule, confort), f(formule, optimale), f(formule, investisseur)]), 'S10',
    "Cette garantie vous est acquise si vous avez souscrit une formule Confort, Optimale ou Investisseur.").
limite(bris_glaces_batiment, 'S10-b', "Reportez-vous à la page 19.", "voir « Montants maximums des garanties » (S14)").
garantie(bris_glaces_meubles, "Bris de glaces des meubles (formule Optimale)", 'S10-a',
    "Est également pris en charge le bris de glaces sur les meubles meublants ci-dessous : les vitres ou miroirs qui constituent des éléments des biens - mobiliers assurés, - les vitres d’inserts, les aquariums, - les parois de douche.").
perimetre(bris_glaces_meubles, f(evenement, bris)).
perimetre(bris_glaces_meubles, ou([f(bien, verre_meuble), f(bien, insert), f(bien, aquarium), f(bien, paroi_douche)])).
circonstance(bris_glaces_meubles, f(formule, optimale), 'S10-a',
    "Si vous avez souscrit la formule Optimale").
garantie(bris_cloture_provisoire, "Frais de clôture provisoire", 'S10-a',
    "nous vous remboursons également les frais de clôture provisoire, par des panneaux non vitrés").
circonstance(bris_cloture_provisoire, f(protection_habitation_compromise, oui), 'S10-a',
    "Dans la mesure où le bris de glaces met en cause la protection de votre habitation,").
limite(bris_cloture_provisoire, 'S10-a', "(voir page 19, montants maximums des pertes pécuniaires et des frais complémentaires)", "voir « Les frais complémentaires » (S16)").
accessoire(bris_cloture_provisoire).
exclusion([bris_glaces_batiment, bris_glaces_meubles, bris_cloture_provisoire], ou([f(travaux_vitres, autres_que_nettoyage), f(vitrage_en_deplacement, oui)]), tout, oui, 'S10-c',
    "Les dommages causés aux objets assurés ou à leurs • encadrements, survenant lors de travaux de toute nature (y compris lors de leur pose, dépose, transport ou entrepôt) à l’exception des travaux de nettoyage.").
exclusion([bris_glaces_batiment, bris_glaces_meubles, bris_cloture_provisoire], f(defaut_encadrement, oui), tout, non, 'S10-c',
    "Les dommages résultant de défauts sur les enchâssements, encadrements et soubassements.").
exclusion([bris_glaces_batiment, bris_glaces_meubles, bris_cloture_provisoire], f(type_dommage, rayure_ou_ecaillement), tout, non, 'S10-c',
    "Les rayures, ébréchures, écaillures.").
exclusion([bris_glaces_batiment, bris_glaces_meubles, bris_cloture_provisoire], f(bien, vitrail), bien(vitrail), non, 'S10-c',
    "Les vitraux, les marquises, les serres.").
exclusion([bris_glaces_batiment, bris_glaces_meubles, bris_cloture_provisoire], f(bien, marquise), bien(marquise), non, 'S10-c',
    "Les vitraux, les marquises, les serres.").
exclusion([bris_glaces_batiment, bris_glaces_meubles, bris_cloture_provisoire], f(bien, serre), bien(serre), non, 'S10-c',
    "Les vitraux, les marquises, les serres.").
exclusion([bris_glaces_batiment, bris_glaces_meubles, bris_cloture_provisoire], et([ou([f(bien, verre_meuble), f(bien, insert), f(bien, aquarium), f(bien, paroi_douche)]), non(f(formule, optimale))]), tout, oui, 'S10-c',
    "Les bris de vitres ou miroirs qui constituent des éléments des biens mobiliers assurés, les vitres d’inserts, les aquariums, les parois de douche, sauf si vous avez souscrit la formule Optimale.").
