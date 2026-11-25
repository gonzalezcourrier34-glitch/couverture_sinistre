% --- Art. 3.1.8 : proposition rédigée par le modèle — mistral:mistral-large-latest, 2026-11-19 ---
extension(batiment_designe, et([f(residence_principale_inhabitable, oui), f(lieu, autre_batiment), f(pays, luxembourg), non(ou([f(evenement, vol), f(evenement, catastrophe_naturelle)]))]), '3.1.8.2',
    "Si le logement couvert par le présent contrat est devenu temporairement inhabitable en raison d'un sinistre couvert, les garanties sont automatiquement transférées sur le bâtiment pris en location au Grand-Duché de Luxembourg pour une période de 18 mois maximum").
extension(batiment_designe, et([f(sejour_temporaire, oui), f(lieu, autre_batiment), non(ou([f(evenement, vol), f(evenement, catastrophe_naturelle)]))]), '3.1.8.3',
    "La Compagnie couvre également les dégâts causés aux objets personnels qu'un Assuré déplace à l'occasion d'un séjour temporaire privé ou professionnel dans un bâtiment situé n'importe où dans le monde").
extension(batiment_designe, et([f(lieu, chambre_etudiant), ou([f(pays, luxembourg), f(pays, allemagne), f(pays, belgique), f(pays, france), f(pays, autre_ue), f(pays, suisse), f(pays, norvege)]), non(ou([f(evenement, vol), f(evenement, catastrophe_naturelle)]))]), '3.1.8.4',
    "Les garanties sont étendues au contenu qui leur appartient et qui est entreposé dans ce logement").
extension(batiment_designe, et([f(lieu, maison_repos), non(ou([f(evenement, vol), f(evenement, catastrophe_naturelle)]))]), '3.1.8.5',
    "La Compagnie couvre les dommages matériels accidentels causés au contenu appartenant au Preneur d'assurance, à son conjoint ou à leurs ascendants entreposé dans la chambre ou l'appartement occupé en maison de repos").
extension(batiment_designe, et([f(bien, sepulture), f(pays, luxembourg), non(ou([f(evenement, vol), f(evenement, catastrophe_naturelle)]))]), '3.1.8.7',
    "La Compagnie couvre les dommages matériels accidentels causés aux sépultures dont un des assurés est propriétaire et situées au Grand-Duché de Luxembourg ou dans un rayon de maximum 50 km au-delà des frontières").
extension(batiment_designe, et([f(demenagement, oui), f(pays, luxembourg), f(duree_demenagement, moins_90_jours), non(ou([f(evenement, vol), f(evenement, catastrophe_naturelle)]))]), '3.1.8.8',
    "En cas de déménagement au Grand-Duché de Luxembourg, les garanties souscrites sont acquises tant à l'ancienne qu'à la nouvelle adresse pendant 90 jours à compter du début du déménagement").
garantie(rc_sejour_temporaire, "Dégâts causés à l'hôtel ou à la villégiature (responsabilité)", '3.1.8.3',
    "Les dégâts matériels accidentels causés par un Assuré à l’occasion d’un séjour temporaire privé ou professionnel n’importe où dans le monde : n à un bâtiment de villégiature loué par un Assuré ; n à l’hôtel ou logement similaire occupé par un Assuré").
perimetre(rc_sejour_temporaire, f(sejour_temporaire, oui)).
perimetre(rc_sejour_temporaire, f(lieu, autre_batiment)).
garantie(rc_logement_etudiant, "Dégâts causés au logement d'étudiant (responsabilité)", '3.1.8.4',
    "La Compagnie couvre les dégâts matériels accidentels causés par les enfants assurés au logement –chambre ou studio– meublé ou non qu'ils louent pendant leurs études dans un des pays membre de l'Union Européenne, en Suisse ou en Norvège").
perimetre(rc_logement_etudiant, f(lieu, chambre_etudiant)).
perimetre(rc_logement_etudiant, ou([f(pays, luxembourg), f(pays, allemagne), f(pays, belgique), f(pays, france), f(pays, autre_ue), f(pays, suisse), f(pays, norvege)])).
garantie(rc_local_fete, "Dégâts causés au local de fête (responsabilité)", '3.1.8.6',
    "La Compagnie couvre les dommages matériels accidentels causés par un Assuré aux locaux situés au Grand-duché de Luxembourg, en Allemagne, en Belgique ou en France, pris en location à l'occasion d'une fête privée").
perimetre(rc_local_fete, f(lieu, local_fete_privee)).
perimetre(rc_local_fete, ou([f(pays, luxembourg), f(pays, allemagne), f(pays, belgique), f(pays, france)])).
accessoire(rc_sejour_temporaire).
accessoire(rc_logement_etudiant).
accessoire(rc_local_fete).
