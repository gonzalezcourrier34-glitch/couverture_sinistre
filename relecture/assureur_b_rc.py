"""Relecture de la responsabilité civile et de la protection juridique de l'assureur B (3.1.10, 4.1.1, 4.1.3),
rédigées par Mistral Large (consigne v12) le 20 nov. : 4 articles, 77 contrôles bloquants, une quarantaine de
variables nouvelles proposées (DEMARCHE 7.99).

Ce que le modèle avait fait, et ce qui change :
- 3.1.9.10 (recours des tiers) est déjà traduit, avec les frais annexes de l'incendie : la proposition n'est pas
  acceptée.
- Le vocabulaire. Une variable par mot du texte (`soudain`, `imprevu`, `exterieur_victime`, `conjoint_cohabitant`,
  `superficie_terrain`…) : le vocabulaire de D les dit déjà (`origine_rc`, `victime`, `bien_confie`, `litige`,
  `domaine_litige`). Deux variables nouvelles : les options `option_rc_immeuble` et `option_rc_vie_privee`.
- Les trois garanties sont des options (« si les conditions particulières mentionnent que la garantie … est
  accordée ») : en circonstance, avec une question qui ne cite pas les conditions particulières (sinon le code en
  ferait une réserve, comme pour les garanties de base) ; inconnue, la réponse est incertaine (convention du jeu,
  f-b16).
- 4.1.1.8.6 : la vie privée exclut le feu, l'explosion et l'eau partis des locaux de l'assuré (f-b12 relève du
  recours des tiers, pas de la responsabilité civile).

Usage : python relecture/assureur_b_rc.py  (corrige les propositions en place)"""
import json
from pathlib import Path

DOSSIER = Path(__file__).resolve().parents[1] / "regles" / "propositions" / "assureur-b-habitation-2017"


def f(v, x): return {"f": [v, x]}
def et(*l): return {"et": list(l)}
def ou(*l): return {"ou": list(l)}
def non(x): return {"non": x}
def un_de(v, *xs): return ou(*[f(v, x) for x in xs]) if len(xs) > 1 else f(v, xs[0])
def exc(cond, article, texte, demander=False):
    return {"condition": cond, "portee": "tout", "a_demander": demander, "article": article, "texte": texte}
def circ(cond, article, texte): return {"condition": cond, "article": article, "texte": texte}
def hors(article, texte, pourquoi): return {"article": article, "texte": texte, "pourquoi": pourquoi}
def limite(article, texte, montant): return {"article": article, "texte": texte, "montant": montant}
def garantie(id_, nom, article, texte, perimetre, circonstances=(), exclusions=(), limites=()):
    return {"id": id_, "nom": nom, "article": article, "texte": texte, "perimetre": list(perimetre),
            "circonstances": list(circonstances), "obligations": [], "exclusions": list(exclusions), "limites": list(limites)}
# Une option, pas une garantie de base : la question ne cite pas les conditions particulières, sans quoi le code la
# mettrait en réserve (« couvert sous réserve », 7.62) ; inconnue, la réponse est incertaine (convention du jeu, 7.97).
def option(var, garantie, article):
    return {"variable": var, "valeurs": ["oui", "non"], "question": f"Avez-vous souscrit l'option {garantie} ?",
            "pourquoi": f"{article} : une option", "aide": {"oui": f"l'option {garantie} est souscrite",
                                                           "non": "elle ne l'est pas"}, "plus_proche": "aucune"}


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


RC = f("evenement", "responsabilite")
LITIGE = f("evenement", "litige")
TIERS = "Toute personne autre que celle ayant la qualité d’Assuré."

ecrire("3.1.10", {
    "evenements": ["responsabilite"],
    "garanties": [garantie(
        "rc_immeuble", "Responsabilité civile immeuble (option)", "3.1.10.1",
        "La Compagnie garantit la responsabilité civile qu’un Assuré pourrait encourir sur la base des articles 1382 à 1386 du "
        "Code civil, à l’égard d’un tiers, en raison de dommages causés par le fait", [RC, f("origine_rc", "immeuble")],
        circonstances=[circ(f("option_rc_immeuble", "oui"), "3.1.10",
                            "la garantie “ responsabilité civile immeuble ” est accordée")],
        exclusions=[
            exc(un_de("victime", "assure", "conjoint"), "3.1.10.2", TIERS),
            exc(f("bien_confie", "oui"), "3.1.10.3",
                "à des biens dont l’assuré est locataire ou occupant à titre gratuit, ainsi qu’à ceux qui lui ont été confiés"),
            exc(f("origine_rc", "activite_professionnelle"), "3.1.10.3", "par le fait de l’exercice d’une profession")],
        limites=[limite("3.1.10.1", "15.554.864 € par sinistre au titre des dommages corporels", "15554864"),
                 limite("3.1.10.1", "896.823 € par sinistre au titre des dommages matériels et des dommages immatériels", "896823")])],
    "vocabulaire_manquant": [option("option_rc_immeuble", "responsabilité civile immeuble", "3.1.10")],
    "hors_decision": [
        hors("3.1.10", "Cette garantie ne produit aucun effet si seul le contenu et/ou la responsabilité civile locative sont assurés.",
             "lu par l'option : sans elle, la garantie ne joue pas"),
        hors("3.1.10.1", "d ’ascenseurs et d’appareils élévateurs à moteur du bâtiment désigné pour autant qu’ils soient conformes à "
             "la réglementation en vigueur et fassent l’objet d’un entretien annuel",
             "lu comme le bâtiment ; la conformité : rare, le vocabulaire ne la distingue pas"),
        hors("3.1.10.1", "d es terrains y attenant pour autant qu’ils ne dépassent pas un hectare",
             "la superficie du terrain : rare ; le vocabulaire ne la distingue pas"),
        hors("3.1.10.3", "aux biens par le feu, la fumée, l’eau, l’explosion, l’implosion, le déplacement du sol ou du bâtiment",
             "hors du périmètre : la garantie ne vise que le bâtiment ou le terrain lui-même (`origine_rc = immeuble`)"),
        hors("3.1.10.3", "par la présence ou la dispersion d’amiante, de fibres d’amiante ou de produits contenant de l’amiante",
             "rare ; le vocabulaire ne distingue pas l'amiante"),
        hors("3.1.10.3", "par le fait des terrains non attenant dont l’Assuré est propriétaire",
             "rare ; le vocabulaire ne distingue pas les terrains non attenants")]},
    ["l'option en circonstance ; le bâtiment et le terrain : `origine_rc = immeuble` ; le tiers, les biens confiés, la profession",
     "les vingt-six variables proposées (soudain, imprévu, conjoint cohabitant, superficie…) : aucune retenue"])

ecrire("4.1.1", {
    "evenements": ["responsabilite"],
    "garanties": [garantie(
        "rc_vie_privee", "Responsabilité civile vie privée (option)", "4.1.1.5",
        "La garantie s’applique aux conséquences pécuniaires de la responsabilité civile pouvant incomber à l’Assuré en vertu des "
        "articles 1382 à 1386 du Code civil, en raison des dommages corporels, des dommages matériels et des dommages "
        "immatériels, causés accidentellement à des tiers au cours de sa vie familiale et privée", [RC],
        circonstances=[circ(f("option_rc_vie_privee", "oui"), "4.1.1",
                            "la garantie “ responsabilité civile vie privée ” est accordée")],
        exclusions=[
            exc(un_de("victime", "assure", "conjoint"), "4.1.1.2", TIERS),
            exc(f("origine_rc", "activite_professionnelle"), "4.1.1.8", "de l’exercice de l’activité professionnelle de l’Assuré"),
            exc(f("origine_rc", "contrat"), "4.1.1.8",
                "d’obligations contractuelles de l’Assuré, sauf s’il s’agit d’un contrat bénévole visé au point 4.1.1.5.4 ci-avant"),
            exc(f("origine_rc", "vehicule_moteur"), "4.1.1.8",
                "les véhicules ou appareils ci-après, si l’assuré ou les personnes dont il est civilement responsable en ont la "
                "propriété, la conduite, la garde ou l’usage"),
            exc(f("bien_confie", "oui"), "4.1.1.8",
                "les dommages survenant aux objets, immeubles ou animaux qui sont confiés à l’Assuré à un titre quelconque"),
            exc(f("origine_rc", "habitation"), "4.1.1.8",
                "les dommages matériels et immatériels d’incendie, d’explosion, ou d’eau, lorsque l’événement dommageable a son "
                "origine dans les locaux ou immeubles appartenant à l’Assuré ou occupés par lui à quelque titre que ce soit")],
        limites=[limite("4.1.1.5", "8.658.260 € par sinistre au titre des dommages corporels", "8658260"),
                 limite("4.1.1.5", "865.826 € par sinistre au titre des dommages matériels et des dommages immatériels", "865826")])],
    "vocabulaire_manquant": [option("option_rc_vie_privee", "responsabilité civile vie privée", "4.1.1")],
    "hors_decision": [
        hors("4.1.1.3", "pour autant que l’Assuré ait sa résidence principale au Grand-duché de Luxembourg",
             "le pays de résidence n'est pas lu ; le contrat est souscrit au Luxembourg"),
        hors("4.1.1.8", "de la pratique par l’Assuré de sports aériens", "rare ; le vocabulaire range ces sports avec la chasse et les sports en club"),
        hors("4.1.1.8", "de la participation de l’Assuré à des concours hippiques", "rare ; le vocabulaire ne distingue pas les concours hippiques"),
        hors("4.1.1.8", "de la présence ou de la dispersion d’amiante, de fibres d’amiante ou de produits contenant de l’amiante",
             "rare ; le vocabulaire ne distingue pas l'amiante"),
        hors("4.1.1.8", "de la participation à des paris ou défis", "rare ; le vocabulaire ne distingue pas les paris"),
        hors("4.1.1.8", "d’une faute lourde de l’Assuré", "l'ivresse, la maladie contagieuse : le vocabulaire ne les distingue pas"),
        hors("4.1.1.8", "les chevaux propriété de l’Assuré ou gardés à titre gratuit par l’Assuré dès que leur nombre total est "
             "supérieur ou égal à six", "le nombre de chevaux : rare ; le vocabulaire ne le distingue pas"),
        hors("4.1.1.8", "les vols, lorsque l’Assuré responsable est considéré comme auteur, coauteur ou complice",
             "un vol commis par l'assuré n'est pas une responsabilité civile déclarée"),
        hors("4.1.1.8", "les dommages engageant une responsabilité civile soumise à une assurance rendue obligatoire au Grand-Duché "
             "du Luxembourg", "lu par les véhicules à moteur ; le reste (chasse…) rare"),
        hors("4.1.1.8", "tous véhicules terrestres construits en vue d’être attelés à un véhicule terrestre à moteur",
             "la liste des véhicules exclus : lue par `origine_rc = vehicule_moteur` ; les remorques et les aéronefs, rares"),
        hors("4.1.1.8", "les dommages subis par une personne apportant une aide à titre gratuit à l’Assuré, lorsque ceux-ci relèvent "
             "de l’application de la législation sur les Accidents du Travail", "rare ; le vocabulaire ne distingue pas les accidents du travail"),
        hors("4.1.1.8", "les dommages causés par les étangs et autres pièces d’eau situés à une autre adresse que la résidence principale",
             "rare ; le vocabulaire ne distingue pas les pièces d'eau"),
        hors("4.1.1.8", "les dommages liés à un glissement, affaissement ou tassement de terrain",
             "rare ; le vocabulaire ne le distingue pas en responsabilité civile")]},
    ["l'option en circonstance (f-b16 : incertain) ; une garantie, les exclusions par `origine_rc`, `victime`, `bien_confie`",
     "4.1.1.8.6 : le feu, l'explosion, l'eau partis du logement (`origine_rc = habitation`) exclus ; f-b12 relève du recours des tiers"])

ecrire("4.1.3", {
    "evenements": ["litige"],
    "garanties": [garantie(
        "protection_juridique", "Protection juridique (option)", "4.1.3.1",
        "La Compagnie s’engage : 4.1.3.1.1 à assurer la défense pénale de l’Assuré devant les tribunaux répressifs",
        [LITIGE, un_de("domaine_litige", "defense_penale", "recours_dommage", "voisinage")],
        circonstances=[circ(f("option_protection_juridique", "oui"), "4.1.3",
                            "la garantie “ protection juridique ” est accordée")],
        limites=[limite("4.1.3.3", "Les frais énoncés au point 4.1.3.2 sont pris en charge par la Compagnie à concurrence de "
                        "8.658 € par sinistre", "8658")])],
    "hors_decision": [
        hors("4.1.3.1", "Toutefois, en ce qui concerne les animaux, la Compagnie ne couvre pas les sinistres relatifs aux animaux "
             "non domestiques dont l’Assuré est propriétaire ou gardien", "rare ; le vocabulaire ne distingue pas les animaux non domestiques"),
        hors("4.1.3.1", "En ce qui concerne les immeubles, la Compagnie ne couvre que les litiges relatifs",
             "les litiges immobiliers ne sont pas dans le périmètre (défense pénale, recours, voisinage)"),
        hors("4.1.3.1", "En ce qui concerne l’environnement, la Compagnie ne couvre pas les dommages subis par l’Assuré",
             "rare ; le vocabulaire ne distingue pas l'environnement"),
        hors("4.1.3.4", "La Compagnie accorde sa garantie lorsqu’il résulte des renseignements obtenus que le tiers considéré comme "
             "responsable est insolvable", "le vocabulaire ne distingue pas l'insolvabilité du tiers")]},
    ["la défense pénale, le recours après un dommage, le trouble de voisinage : `domaine_litige` ; l'option en circonstance",
     "les treize variables proposées : aucune retenue ; les restrictions (animaux, immeubles, environnement) hors décision"])
