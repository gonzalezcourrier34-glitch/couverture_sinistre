"""Relecture du lot 3 de l'assureur D : la responsabilité civile (12.1 à 12.4, 13.1, 13.3) et la défense pénale et
la protection juridique (22.1 à 22.3), rédigées par Mistral Large (consigne v12) le 20 nov. : 13 articles en 23 min
38 s, 238 contrôles bloquants, près de 140 variables nouvelles proposées (DEMARCHE 7.96).

Ce que le modèle avait fait, et ce qui change :
- Le vocabulaire. Une variable par condition du texte (le nombre de chiens adultes, la cylindrée d'un véhicule
  jouet, la longueur d'un voilier, l'épandage de boues…) : la lecture d'une déclaration de responsabilité civile
  aurait reçu une consigne de plusieurs pages. Ce que le modèle lisait en vingt variables se dit en quelques-unes,
  à plusieurs valeurs : `origine_rc` (ce qui a causé le dommage : une personne, un animal de compagnie, un autre
  animal, un véhicule à moteur, le logement…), `victime`, `dommage_tiers`, `bien_confie` ; pour la protection
  juridique, l'événement `litige` et `domaine_litige`. Le reste des exclusions, rares ou que la déclaration ne dit
  jamais (épandage, phytosanitaires, ball-trap…), est hors décision, cité mot pour mot.
- Les garanties. La responsabilité civile « liée à l'habitation » dépend du statut : propriétaire (12.1 : le feu
  ou l'eau partis du logement ; l'accident causé par le bâtiment ou le terrain), locataire (12.2 : le feu ou l'eau,
  envers le propriétaire et les voisins), en vacances (12.3). La vie privée (13.1) couvre le reste, sauf ce que 13.3
  renvoie ailleurs (le logement, les véhicules, les animaux autres que de compagnie, la chasse…).
- Les exclusions de 12.4, 13.3 et 22.3 n'ont pas de garantie dans leur article : écrites « tous », elles auraient
  touché les dommages aux biens. Elles visent les garanties qu'elles nomment (« cibles », 7.96).
- La protection juridique (22.2) est une option : en circonstance, option inconnue → incertain (convention du jeu).
- 13.2 (fêtes familiales, chambres d'hôtes, une option) n'est pas traduit ; les mesures de sécurité (4.1 à 4.3) ne
  sont pas des garanties mais des réductions de l'indemnité : des limites des garanties qu'elles touchent (lot 2).

Usage : python relecture/assureur_d_lot_3.py  (corrige les propositions en place)"""
import json
from pathlib import Path

DOSSIER = Path(__file__).resolve().parents[1] / "regles" / "propositions" / "assureur-d-habitation-2026"


def f(v, x): return {"f": [v, x]}
def et(*l): return {"et": list(l)}
def ou(*l): return {"ou": list(l)}
def non(x): return {"non": x}
def un_de(v, *xs): return ou(*[f(v, x) for x in xs]) if len(xs) > 1 else f(v, xs[0])
def exc(cond, article, texte, demander=False, cibles=None):
    x = {"condition": cond, "portee": "tout", "a_demander": demander, "article": article, "texte": texte}
    if cibles:
        x["cibles"] = cibles
    return x
def circ(cond, article, texte): return {"condition": cond, "article": article, "texte": texte}
def hors(article, texte, pourquoi): return {"article": article, "texte": texte, "pourquoi": pourquoi}
def garantie(id_, nom, article, texte, perimetre, circonstances=(), exclusions=()):
    return {"id": id_, "nom": nom, "article": article, "texte": texte, "perimetre": list(perimetre),
            "circonstances": list(circonstances), "obligations": [], "exclusions": list(exclusions), "limites": []}
def variable(var, valeurs_aides, question, pourquoi, proche):
    return {"variable": var, "valeurs": [v for v, _ in valeurs_aides], "question": question, "pourquoi": pourquoi,
            "aide": dict(valeurs_aides), "plus_proche": proche}


def ecrire(article, prop, modifications):
    chemin = DOSSIER / f"{article}.json"
    d = json.loads(chemin.read_text(encoding="utf-8"))
    base = {"evenements": [], "definitions": [], "garanties": [], "exclusions_communes": [], "extensions": [],
            "vocabulaire_manquant": [], "non_traduit": [], "hors_decision": []}
    d["proposition"] = base | prop
    d["meta"]["relecture"] = {"par": "auteur + Claude", "date": "2026-11-20", "modifications": modifications}
    d.pop("controles", None)
    chemin.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{article} : relu")


# Les éléments des listes d'exclusions de 12.4, 13.3 et 22.3, mot pour mot (découpés comme le contrôle les découpe).
ITEMS = {
    '12.4-a': [
        'les dommages susceptibles d’engager votre responsabilité en qualité de maître d’ouvrage, de vendeur, d’administrateur de biens ou de syndic de copropriété,',
        'les accidents résultant de la non-observation des règlements et instructions des services publics quant à l’élagage ou l’émondage d’arbres, ou le débroussaillage,',
        'les dommages de toute nature causés par des véhicules à moteur (y compris les vélos électriques circulant à plus de 25 km/h et les engins de déplacement personnel motorisés) soumis à la législation sur l’assurance automobile obligatoire, ou qui y seraient soumis en France,',
        'les dommages subis par les biens dont vous avez la propriété, la conduite ou la garde,',
        'les acceptations conventionnelles de responsabilité,',
        'les terrains d’une superficie supérieure à 10 000 m2 si une mention spéciale n’est pas portée aux conditions particulières,',
        'les dépenses effectuées pour prévenir ou réparer un dommage, pour modifier ou améliorer un bien ayant été à l’origine d’un sinistre,',
        'résultant de pollutions lentes, graduelles ou progressives,',
        'résultant de l’absence ou de défaut d’entretien d’une installation, étant entendu que les causes non supprimées d’un précédent sinistre sont considérées automatiquement comme un défaut d’entretien,',
        'dus aux conséquences d’une pollution résultant d’une contamination virale ou microbienne d’origine animale,',
        'causés directement ou indirectement par des produits phytosanitaires,',
        'causés du fait de l’épandage de boues, effluents ou déchets de toute nature,',
        'causés du fait de votre non-respect du règlement sanitaire départemental',
    ],
    '13.3': [
        'responsabilité civile vie privée et à ses extensions',
    ],
    '13.3-a~1': [
        'les dommages matériels et immatériels consécutifs à un incendie, une explosion, une venue d’eau ayant pris naissance dans un local dont vous êtes propriétaire, locataire ou occupant à titre gratuit, sauf pour la garantie « Responsa bilité civile fêtes familiales » lorsque la garantie est acquise,',
        'les dommages causés par tous les animaux (y compris les chevaux) autres que les animaux de compagnie. Pour les animaux ayant mordu une personne ou un autre animal, la garantie couvre le coût de leurs visites sanitaires obligatoires,',
        'les chiens lorsque vous en gardez habituellement plus de quatre adultes,',
        'les conséquences de la responsabilité que les assurés peuvent encourir du fait de dommages corporels matériels et immatériels causés par tous biens et animaux qu’ils auraient vendus,',
        'les vols commis par une personne dont vous êtes civilement responsable, en l’absence de plainte nominative,',
        'les conséquences pécuniaires des responsabilités résultant de l’exécution, de la mauvaise exécution et de l’inexécution d’un contrat, sauf lors de vos activités bénévoles,',
        'les dommages relevant d’un régime de réparation des accidents du travail et du fait des préposés non déclarés,',
        'les dommages résultant de la prescription et/ou de la pratique d’actes ou d’une activité de recherche, lors de stages dans le domaine médical ou paramédical ou lors de vos activités bénévoles,',
    ],
    '13.3-a~2': [
        'tous véhicules terrestres à moteur (y compris les vélos électriques circulant à plus de 25 km/h et les engins de déplacement personnel motorisés) soumis à l’obligation d’assurance et leurs remorques ou matériels attelés, ou qui y seraient soumis en France, à l’exception des cas décrits ci-avant,',
        'les dommages causés par les chiens de première catégorie (chiens d’attaque) et deuxième catégorie (chiens de garde et de défense) tels que définis dans la loi n°99-5 du 6 janvier 1999 modifiée par la loi n°2008-582 du 20 juin 2008 et soumis à l’obligation d’assurance,',
        'un appareil de déplacement aérien, par toute embarcation à rame ou à voile de plus de 5,5 mètres de long ou à moteur de plus de 6 CV, dont vous avez la conduite, la propriété ou la garde,',
        'la pratique du ball-trap, de la chasse, y compris les faits des chiens en action de chasse, des sports aériens, de tout sport à titre professionnel,',
        'votre participation à toutes épreuves, courses ou compétitions sportives, soumises à une obligation d’assurance légale, ainsi qu’à leurs essais préparatoires,',
        'toute activité physique ou sportive que vous exercez en tant que membre d’un club ou d’un groupement sportif agréé conformément à la loi du 29 octobre 1975. Toutefois, la garantie reste acquise en cas d’absence ou d’insuffisance d’assurance du club',
        'tout bien immobilier dont vous êtes propriétaire ou copropriétaire,',
        'vous en tant qu’organisateur, même bénévole, de kermesses, rallyes, réunions ou fêtes dans tout lieu dont vous n’êtes pas propriétaire, ni copropriétaire, ni locataire habituel, sauf si les conditions de notre extension « Responsabilité civile fêtes familiales » sont remplies',
    ],
    '13.3-a~3': [
        'résultant de pollutions lentes, graduelles ou progressives,',
        'résultant de l’absence ou de défaut d’entretien d’une installation, étant entendu que les causes non supprimées d’un précédent sinistre sont considérées automatiquement comme un défaut d’entretien,',
        'dus aux conséquences d’une pollution résultant d’une contamination virale ou microbienne d’origine animale,',
        'causés directement ou indirectement par des produits phytosanitaires,',
        'causés du fait de l’épandage de boues, effluents ou déchets de toute nature,',
        'causés du fait de votre non-respect du règlement sanitaire départemental',
    ],
    '22.3': [
        'aux articles 22-1 et 22-2',
    ],
    '22.3-a~1': [
        'lorsque l’événement préjudiciable ou l’acte répréhensible à l’origine du litige est porté à votre connaissance avant la prise d’effet ou après la cessation des effets de votre garantie,',
        'lorsque votre demande est juridiquement insoutenable, prescrite ou lorsque son enjeu est inférieur au seuil d’intervention,',
        'lorsque le litige découle de votre responsabilité civile quand elle est couverte par un contrat d’assurances,',
        'd’une activité professionnelle non salariée ou de l’administration d’une entreprise, d’une collectivité ou d’une association lorsque cette dernière emploie un ou des salariés,',
        'de votre qualité d’employeur n’ayant pas déclaré une assistante maternelle, une femme de ménage ou un(e) employé(e) de maison,',
        'de l’application des statuts d’une société ou de l’achat, la vente, la détention de droits sociaux d’une société non cotée officiellement à une Bourse Française de Valeurs,',
        'd’un conflit collectif du travail,',
        'de l’expression par vous d’opinions politiques, syndicales ou religieuses,',
        'de la propriété ou de l’usufruit de biens immobiliers non destinés exclusivement à votre usage privatif,',
        'de l’achat, la vente, la propriété, la location, l’entretien, la réparation, la conduite ou l’assurance d’un aéronef,',
        'de travaux immobiliers et de leurs prolongements relatifs à votre résidence, lorsque ces travaux sont soumis à la délivrance d’un permis de construire, de démolir ou de déclaration préalable ou encore lorsqu’ils sont soumis à l’obligation d’assurance édictée par l’article L. 242.1 du Code,',
    ],
    '22.3-a~2': [
        'de la protection de vos brevets, titres de propriété industrielle ou droits d’auteur,',
        'de votre qualité de donneur d’aval, de caution ou cessionnaire de droits,',
        'de l’achat, la vente, la propriété, la location (sauf pour la location de courte durée n’excédant pas deux mois), l’entretien, la réparation, la conduite ou l’assurance d’un véhicule terrestre à moteur (sauf les engins de jardinage et les jouets télécommandés),',
        'de poursuites pénales, mesure d’instruction ou réclamation diligentée à votre encontre pour crime, délit impliquant la volonté de causer un dommage, rixe ou injure,',
        'de l’application du Livre I du Code civil, excepté les litiges découlant des incapacités (sauvegarde de justice, tutelle, curatelle) et de la filiation (légitime, naturelle, adoptive),',
        'des régimes matrimoniaux, des successions (excepté les litiges découlant des successions en ligne directe), des donations entre vifs et legs (excepté les litiges découlant des donations entre vifs et legs en ligne directe),',
        'de l’application de la présente garantie',
        'En matière de copropriété, nous n’intervenons jamais dans le règlement de votre quote-part de charges liée aux procédures opposant un (des) tiers au syndicat des copropriétaires',
    ],
}


def hors_restants(cle, traduits, pourquoi):
    """Les éléments d'une liste d'exclusions qui ne sont pas traduits : hors décision, chacun cité."""
    return [hors(cle.split("~")[0] if cle in ("13.3", "22.3") else cle, x, pourquoi)
            for i, x in enumerate(ITEMS[cle]) if i not in traduits]


ORIGINE = variable("origine_rc", [
    ("personne", "l'assuré, un enfant ou une personne de son foyer : maladresse, chute, jeu, sport en loisir, vélo"),
    ("animal_compagnie", "un chien, un chat ou un autre animal de compagnie"),
    ("animal_autre", "un cheval, un âne, du bétail, des volailles : un animal qui n'est pas de compagnie"),
    ("chien_dangereux", "un chien de 1re ou 2e catégorie (chien d'attaque, de garde ou de défense)"),
    ("vehicule_moteur", "une voiture, une moto, un scooter, une trottinette ou un vélo électriques rapides"),
    ("habitation", "un incendie, une explosion ou une fuite d'eau partis du logement ou des dépendances occupés"),
    ("immeuble", "le bâtiment ou le terrain lui-même : une tuile ou une branche qui tombe, une clôture, un mur"),
    ("chasse_sport", "la chasse, le ball-trap, un sport aérien, une compétition, un sport en club ou professionnel"),
    ("contrat", "un service ou un travail promis à quelqu'un, mal fait ou pas fait"),
    ("activite_professionnelle", "le travail ou l'activité professionnelle de l'assuré")],
    "Qu'est-ce qui a causé le dommage à l'autre personne ?", "responsabilité civile : ce que les garanties et "
    "exclusions distinguent", "auteur : dit qui, pas par quoi (un animal, un véhicule, le logement)")
VICTIME = variable("victime", [
    ("tiers", "une personne extérieure au foyer : voisin, passant, ami, propriétaire bailleur"),
    ("assure", "l'auteur du dommage lui-même ou une personne vivant à son foyer"),
    ("conjoint", "le conjoint ou le concubin de l'auteur du dommage"),
    ("famille", "les ascendants, descendants, frères et sœurs de l'auteur, ou leurs conjoints"),
    ("prepose", "un employé de maison, un gardien, un jardinier, pendant son service")],
    "Qui a subi le dommage ?", "les personnes qui ne peuvent pas être indemnisées (12.1, 13.1)",
    "proprietaire : dit à qui est le bien, pas qui demande réparation")
DOMMAGE = variable("dommage_tiers", [("corporel", "une personne blessée"), ("materiel", "un objet, un véhicule, un bâtiment abîmé")],
                   "Le dommage causé est-il corporel (une blessure) ou matériel (un bien abîmé) ?",
                   "13.1 : la famille n'est pas indemnisée des dommages matériels", "type_dommage : la nature d'un bris, pas d'un dommage à autrui")
CONFIE = variable("bien_confie", [("oui", "le bien abîmé avait été prêté, loué ou confié à l'assuré"), ("non", "non")],
                  "Le bien abîmé vous avait-il été prêté, loué ou confié ?", "12.4 : les biens dont vous avez la garde",
                  "proprietaire : à qui est le bien, pas qui l'a en garde")
RC_HABITATION = ["rc_proprietaire_voisins", "rc_proprietaire_immeuble", "rc_locataire", "rc_villegiature"]
VICTIMES_12 = exc(un_de("victime", "assure", "conjoint", "famille", "prepose"), "12.1-a~2",
                  "Toute personne autre que : • vous-même, votre conjoint ou concubin (signataire ou non d’un PACS) non "
                  "séparé, vos ascendants et descendants, • le personnel de garde ou d’entretien pendant son service")
RC = f("evenement", "responsabilite")

ecrire("12.1", {
    "evenements": ["responsabilite"],
    "garanties": [
        garantie("rc_proprietaire_voisins", "Responsabilité civile du propriétaire : incendie, explosion, eau", "12.1-a~1",
                 "• Envers les voisins et les tiers La garantie couvre les conséquences financières de votre responsabilité "
                 "civile à raison : - des dommages matériels et immatériels consécutifs subis par les voisins et les tiers à la "
                 "suite d’un incendie, d’une explosion, d’une venue d’eau ayant pris naissance dans le local d’habitation et/ou "
                 "des dépendances assurés", [RC, f("statut_logement", "proprietaire"), f("origine_rc", "habitation")],
                 exclusions=[VICTIMES_12]),
        garantie("rc_proprietaire_immeuble", "Responsabilité civile du propriétaire : accident causé par l'habitation", "12.1-a~2",
                 "des dommages corporels, matériels et immatériels consécutifs causés aux tiers à la suite d’un accident occasionné "
                 "pendant la période de validité du contrat par : • l’habitation désignée aux conditions particulières, y compris "
                 "le terrain, les plantations, les clôtures et leurs aménagements",
                 [RC, f("statut_logement", "proprietaire"), f("origine_rc", "immeuble")], exclusions=[VICTIMES_12])],
    "vocabulaire_manquant": [ORIGINE, VICTIME],
    "hors_decision": [
        hors("12.1-a~1", "• Envers les locataires La garantie couvre les conséquences financières de votre responsabilité civile "
             "à raison : - des dommages matériels et des dommages immatériels consécutifs causés aux biens de votre locataire",
             "le propriétaire bailleur : le vocabulaire ne distingue pas le bail ; le bâtiment en cause relève de l'accident causé par l'habitation"),
        hors("12.1-a~1", "La garantie est étendue aux responsabilités liées à l’environnement", "rare ; le vocabulaire ne distingue pas la pollution"),
        hors("12.1-a~1", "responsabilité civile « production d’électricité »", "rare ; le vocabulaire ne distingue pas la production d'électricité"),
        hors("12.1-a~2", "• le personnel de garde ou d’entretien", "rare ; lu comme un accident causé par l'habitation"),
        hors("12.1-a~2", "Toutefois, nous garantissons le recours que la Sécurité Sociale ou tout autre organisme de prévoyance oblig "
             "atoire peut être fondé à exercer contre vous", "un recours d'organisme social, pas une déclaration de sinistre")]},
    ["deux garanties du propriétaire : le feu ou l'eau partis du logement, l'accident causé par le bâtiment ou le terrain",
     "`origine_rc` et `victime` au lieu de six variables ; les personnes non indemnisées en exclusion"])

ecrire("12.2", {
    "evenements": ["responsabilite"],
    "garanties": [garantie(
        "rc_locataire", "Responsabilité civile du locataire : incendie, explosion, eau", "12.2-a",
        "• Envers le propriétaire La garantie couvre les conséquences financières de votre responsabilité civile de locataire "
        "vis-à-vis de votre propriétaire…• Envers les voisins et les tiers La garantie couvre les conséquences financières de "
        "votre responsabilité civile à raison des dommages matériels et immatériels consécutifs subis par les voisins et les "
        "tiers à la suite d’un incendie, d’une explosion, d’une venue d’eau ayant pris naissance dans l’habitation assurée",
        [RC, f("statut_logement", "locataire"), f("origine_rc", "habitation")])],
    "vocabulaire_manquant": [ORIGINE],
    "hors_decision": [hors("12.2-a", "La garantie est étendue aux responsabilités liées à l’environnement",
                           "rare ; le vocabulaire ne distingue pas la pollution")]},
    ["le locataire : le feu ou l'eau partis du logement, envers le propriétaire et les voisins ; `statut_logement` existant"])

ecrire("12.3", {
    "evenements": ["responsabilite"],
    "garanties": [garantie(
        "rc_villegiature", "Responsabilité civile villégiature", "12.3",
        "La garantie couvre les conséquences financières de votre responsabilité civile locative et le recours des voisins et des "
        "tiers en raison des dommages par incendie, explosion, venue d’eau, détériorations immobilières ou bris de glaces "
        "occasionnés à une habitation que vous occupez temporairement ou dont vous êtes occupant à titre gratuit pour des séjours "
        "d’agrément d’une durée inférieure à 3 mois", [RC, f("origine_rc", "habitation"), f("sejour_temporaire", "oui")])],
    "vocabulaire_manquant": [ORIGINE],
    "hors_decision": [hors("12.3", "dans les pays de l’Union européenne, au Royaume-Uni de Grande-Bretagne et d’Irlande du Nord, "
                           "en Suisse et dans les Principautés d’Andorre et de Monaco", "le pays n'est lu que pour les extensions du lieu assuré")]},
    ["le logement de vacances : `sejour_temporaire` (existant) et le feu ou l'eau partis du logement occupé"])

ecrire("12.4", {
    "evenements": ["responsabilite"],   # pour que les faits nés de ces exclusions soient lus pour la responsabilité civile
    "exclusions_communes": [
        exc(f("origine_rc", "vehicule_moteur"), "12.4-a", ITEMS["12.4-a"][2], cibles=RC_HABITATION),
        exc(f("bien_confie", "oui"), "12.4-a", ITEMS["12.4-a"][3], cibles=RC_HABITATION)],
    "vocabulaire_manquant": [ORIGINE, CONFIE],
    "hors_decision": hors_restants("12.4-a", {2, 3}, "rare, ou que la déclaration ne dit pas ; le vocabulaire ne le distingue pas")},
    ["véhicules à moteur, biens confiés : traduits, pour les garanties de 12.1 à 12.3 seulement (« cibles ») ; le reste hors décision"])

ecrire("13.1", {
    "evenements": ["responsabilite"],
    "garanties": [garantie(
        "rc_vie_privee", "Responsabilité civile vie privée", "13.1-a~1",
        "La garantie couvre les conséquences financières de la responsabilité civile que les assurés peuvent encourir dans le cadre "
        "de leur vie privée, en raison de dommages corporels, matériels et immatériels consécutifs causés aux tiers", [RC],
        exclusions=[
            exc(f("origine_rc", "activite_professionnelle"), "13.1-a~1", "dans le cadre de leur vie privée"),
            exc(un_de("victime", "assure", "conjoint"), "13.1-a~3",
                "le responsable du sinistre et son conjoint ou concubin (signataire ou non d’un PACS)"),
            exc(et(f("victime", "famille"), f("dommage_tiers", "materiel")), "13.1-a~3",
                "leurs ascendants et descendants, frères et sœurs et leurs conjoints pour les dommages matériels", demander=True),
            exc(f("victime", "prepose"), "13.1-a~3",
                "les préposés attachés à votre service privé pendant la durée de leur service")])],
    "vocabulaire_manquant": [ORIGINE, VICTIME, DOMMAGE],
    "hors_decision": [
        hors("13.1-a~3", "Toutefois, nous garantissons le recours que la Sécurité Sociale ou tout autre organisme de prévoyance "
             "obligatoire peut être fondé à exercer contre vous", "un recours d'organisme social, pas une déclaration de sinistre"),
        hors("13.1-a~3", "Étendue territoriale Pour bénéficier de la garantie, le fait dommageable doit s’être produit pendant la "
             "période de validité du contrat", "le pays n'est lu que pour les extensions du lieu assuré")]},
    ["la vie privée : toute responsabilité, sauf ce que 13.3 exclut ou renvoie à 12.x ; les personnes non indemnisées",
     "la famille n'est exclue que pour les dommages matériels : à demander (`dommage_tiers`)"])

TRADUITS_13 = {"13.3-a~1": {0: "habitation", 1: "animal_autre", 5: "contrat"},
               "13.3-a~2": {0: "vehicule_moteur", 1: "chien_dangereux", 3: "chasse_sport", 4: "chasse_sport", 5: "chasse_sport",
                            6: "immeuble"}}
ecrire("13.3", {
    "evenements": ["responsabilite"],
    "exclusions_communes": [exc(f("origine_rc", origine), cle, ITEMS[cle][i], cibles=["rc_vie_privee"])
                            for cle, t in TRADUITS_13.items() for i, origine in t.items()],
    "vocabulaire_manquant": [ORIGINE],
    "hors_decision": [hors("13.3", ITEMS["13.3"][0], "l'intitulé de la liste, pas une exclusion"),
                      *hors_restants("13.3-a~1", set(TRADUITS_13["13.3-a~1"]), "rare, ou que la déclaration ne dit pas ; le vocabulaire ne le distingue pas"),
                      *hors_restants("13.3-a~2", set(TRADUITS_13["13.3-a~2"]), "rare ; le vocabulaire ne le distingue pas"),
                      *hors_restants("13.3-a~3", set(), "pollution : rare ; le vocabulaire ne la distingue pas")]},
    ["le logement (renvoyé à 12.x), les animaux autres que de compagnie (f-d15), les chiens dangereux, les véhicules à "
     "moteur, la chasse et les sports à risque, le contrat, le bâtiment dont on est propriétaire : par `origine_rc`",
     "les vingt autres exclusions : hors décision, citées"])

DOMAINE = variable("domaine_litige", [
    ("travail", "avec votre employeur, en tant que salarié"),
    ("logement", "votre résidence principale ou secondaire, comme propriétaire, copropriétaire ou locataire"),
    ("travaux", "des travaux intérieurs d'entretien, d'embellissement ou de réparation"),
    ("sante", "un organisme de soins ou de retraite, un médecin, un hôpital"),
    ("consommation", "l'achat, la vente, la location ou la commande d'un bien ou d'un service (pas d'un véhicule à moteur)"),
    ("administration", "un service public, une administration, les impôts"),
    ("voisinage", "un voisin : servitude, trouble de voisinage"),
    ("employeur_domestique", "votre assistante maternelle, femme de ménage ou employé de maison déclarés"),
    ("location_vacances", "une location saisonnière de vacances, comme locataire"),
    ("bateau", "un petit voilier, un engin nautique, un bateau de plaisance à moteur de 15 CV au plus"),
    ("association", "votre participation bénévole à une association"),
    ("famille", "succession, legs ou donation en ligne directe ; tutelle, curatelle ; filiation ; violences intrafamiliales"),
    ("recours_dommage", "vous réclamez réparation d'un dommage subi lors d'un accident causé par quelqu'un d'autre"),
    ("defense_penale", "vous êtes poursuivi devant un tribunal pour une contravention ou un délit après un accident"),
    ("vehicule_moteur", "l'achat, la réparation, l'entretien, la conduite ou l'assurance d'une voiture, d'une moto, même avec un garagiste"),
    ("activite_professionnelle", "une activité professionnelle non salariée, une entreprise, une société"),
    ("divorce_succession", "un divorce, un régime matrimonial, une succession ou une donation hors ligne directe"),
    ("autre", "un autre litige")],
    "Sur quoi porte le litige ?", "les domaines de la défense pénale, du recours et de la protection juridique (22.1 à 22.3)",
    "aucune : le vocabulaire ne disait que des dommages")
LITIGE = {"variable": "evenement", "valeurs": ["litige"], "question": "Que s'est-il passé ?", "pourquoi": "22.1 à 22.3",
          "aide": {"litige": "un différend avec quelqu'un (employeur, vendeur, artisan, voisin, administration) pour lequel "
                             "l'assuré veut être conseillé, aidé ou défendu ; pas un dommage à indemniser"},
          "plus_proche": "assistance : une aide pratique, pas juridique"}
LITIGE_F = f("evenement", "litige")
PJ = ["recours_accident", "defense_penale", "protection_juridique"]

ecrire("22.1", {
    "evenements": ["litige"],
    "garanties": [
        garantie("recours_accident", "Recours suite à accident", "22.1",
                 "pour réclamer amiablement et au besoin judiciairement la réparation pécuniaire des dommages subis par vous, ou "
                 "causés aux biens assurés par le contrat, lorsque ces dommages résultent d’un accident survenu au cours de votre vie "
                 "privée, engagent la responsabilité d’une personne n’ayant pas la qualité d’assuré au titre du contrat, et ne "
                 "peuvent être indemnisés au titre d’une garantie du présent contrat", [LITIGE_F, {"concept": "accident"}]),
        garantie("defense_penale", "Défense pénale", "22.1",
                 "pour vous défendre devant les juridictions répressives et les commissions administratives, si vous êtes poursuivi "
                 "pour contravention ou délit à la suite d’un événement dont les conséquences pécuniaires à l’égard du tiers sont "
                 "couvertes par la garantie responsabilité civile du contrat", [LITIGE_F, f("domaine_litige", "defense_penale")])],
    # L'accident du lexique : le recours suppose un accident (« soudain, imprévu et extérieur ») ; la déclaration le dit
    # par le domaine du litige (une réparation demandée après un accident causé par un autre).
    "definitions": [{"concept": "accident", "condition": f("domaine_litige", "recours_dommage"), "article": "S10-a/accident",
                     "texte": "Tout événement soudain, imprévu et extérieur à la victime à la chose endommagée"}],
    "vocabulaire_manquant": [LITIGE, DOMAINE]},
    ["l'événement `litige` (nouveau) et `domaine_litige` : recours après un accident, défense pénale ; incluses dans les formules"])

ecrire("22.2", {
    "evenements": ["litige"],
    "garanties": [garantie(
        "protection_juridique", "Protection juridique (option)", "22.2",
        "Nous intervenons quand un litige survient dans votre vie privée ou salariée",
        [LITIGE_F, un_de("domaine_litige", "travail", "logement", "travaux", "sante", "consommation", "administration", "voisinage",
                         "employeur_domestique", "location_vacances", "bateau", "association", "famille")],
        circonstances=[circ(f("option_protection_juridique", "oui"), "22.2", "(garantie optionnelle)")])],
    "vocabulaire_manquant": [LITIGE, DOMAINE, {"variable": "option_protection_juridique", "valeurs": ["oui", "non"],
                                       "question": "Avez-vous souscrit l'option protection juridique ?", "pourquoi": "22.2 : une option",
                                       "aide": {"oui": "l'option protection juridique est souscrite", "non": "elle ne l'est pas"},
                                       "plus_proche": "aucune"}],
    "hors_decision": [hors("22.2", "à l’exception des questions de bornage", "le vocabulaire ne distingue pas le bornage"),
                      hors("22.2", "d’un voilier d’une longueur inférieure ou égale à six mètres", "la taille d'un bateau : rare ; le vocabulaire ne la distingue pas")]},
    ["les domaines couverts par `domaine_litige` ; l'option en circonstance : inconnue, la réponse est incertaine"])

ecrire("22.3", {
    "evenements": ["litige"],
    "exclusions_communes": [
        exc(f("domaine_litige", "activite_professionnelle"), "22.3-a~1", ITEMS["22.3-a~1"][3], cibles=PJ),
        exc(f("domaine_litige", "vehicule_moteur"), "22.3-a~2", ITEMS["22.3-a~2"][2], cibles=PJ),
        exc(f("domaine_litige", "divorce_succession"), "22.3-a~2", ITEMS["22.3-a~2"][4], cibles=PJ),
        exc(f("domaine_litige", "divorce_succession"), "22.3-a~2", ITEMS["22.3-a~2"][5], cibles=PJ)],
    "vocabulaire_manquant": [DOMAINE],
    "hors_decision": [hors("22.3", ITEMS["22.3"][0], "l'intitulé de la liste, pas une exclusion"),
                      *hors_restants("22.3-a~1", {3}, "rare, ou que la déclaration ne dit pas ; le vocabulaire ne le distingue pas"),
                      *hors_restants("22.3-a~2", {2, 4, 5}, "rare, ou que la déclaration ne dit pas ; le vocabulaire ne le distingue pas")]},
    ["véhicule à moteur (f-d16), activité professionnelle, divorce et successions hors ligne directe : par `domaine_litige`"])
