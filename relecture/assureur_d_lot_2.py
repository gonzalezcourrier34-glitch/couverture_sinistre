"""Relecture du lot 2 de l'assureur D : les garanties 2.1 à 2.13 (« Dommages subis par vos biens »), rédigées par
Mistral Large (consigne v12) le 20 nov., 99 contrôles bloquants (DEMARCHE 7.90, 7.91).

Ce que le modèle avait fait, et ce qui change :
- Les concepts. Il redéfinissait `contenu` (« SUBIS PAR VOS BIENS »), inventait `dependances`, `objets_precieux`,
  `appareil_electrique`, et un concept par événement (incendie, foudre, mur du son…). Les garanties emploient les
  concepts du lot 1 : `batiment` (les lieux assurés) et `contenu` (les biens mobiliers qui s'y trouvent) ; le
  bâtiment lui-même est `bien = element_batiment`.
- Les formules. Une garantie « acquise uniquement pour les formules Confort et Excellence » (2.2, bris de glace +,
  vol des clés) porte la formule en circonstance : formule inconnue → incertain, comme le veut le jeu fermé. Dans
  le périmètre, la garantie n'était que « possible », et le refus d'une autre garantie l'emportait (7.92).
  « Les + de la formule Excellence » (cuves de combustible, bris de glace renforcé) de même. L'exclusion « les vols
  dans les dépendances, si vous avez souscrit la formule Eco » est à demander : un vol au garage, formule inconnue,
  est incertain (f-d25).
- Le vol (2.5) et les détériorations (2.6). La condition « par effraction ou escalade, menaces, vol des clés,
  introduction par fausse qualité » était une disjonction de cinq faits oui/non : un seul inconnu rendait chaque
  vol sans effraction incertain. Une seule variable nouvelle, `acces_voleur` (escalade, menaces, clés volées,
  fausse qualité, « sans effraction » : porte ouverte ou non verrouillée), avec `effraction` qui existe déjà : une
  porte non fermée à clé et sans trace donne un refus (f-d18).
- Les exclusions de famille : « sauf plainte nominative » → `plainte_deposee` (déjà au vocabulaire) ; les clés
  laissées dans une boîte aux lettres → `cles_deposees_exterieur` ; les tags à l'extérieur → `graffiti_mur_exterieur`
  (déjà au vocabulaire, pour l'attentat chez A).
- Venues d'eau (2.4) : les causes du contrat sont rapportées aux valeurs existantes de `cause_eau` (le ruissellement
  et le refoulement des égouts : `inondation` ; les terrasses formant toiture, les murs et façades :
  `infiltration_exterieure` ; les piscines : `piscine_exterieure`) plutôt que d'en créer six, qui auraient pris les
  lectures des contrats A et B (leçon 96). Une canalisation **enterrée** n'est pas une canalisation **encastrée**
  (`canalisation_encastree`, qu'avait employée le modèle) : variable `canalisation_enterree`. La décennale : variable
  `batiment_moins_10_ans`, à demander (f-d23).
- « Les frais de réparation ou de remplacement de l'élément à l'origine du dommage » excluaient tout le sinistre :
  c'est le tuyau qui n'est pas payé, pas le parquet (f-d03) ; hors décision.
- Tempête (2.3) : l'intensité (« d'autres bâtiments de bonne construction dans le voisinage », ou certificat
  météo, plus de 100 km/h pour le vent) vaut pour le vent comme pour la neige ; les objets en plein air sont exclus
  par le lieu (jardin, terrasse), sauf le mobilier de jardin du Pack Jardin.
- Bris de glaces (2.7) : trois garanties, la base (vitrages, miroirs, glaces de meubles), « Bris de glace + »
  (vitrocéramique, sanitaires : Confort et Excellence) et « renforcé » (vitres d'électroménager, panneaux solaires :
  Excellence). Les extensions sur un concept inconnu `bris_glaces` sont retirées.
- 2.13 (intervention des secours) déclarait traduits tous les événements, y compris la responsabilité civile et
  l'assistance : un sinistre de responsabilité civile aurait été refusé au lieu d'être incertain. Aucun événement.
- Les renvois aux mesures de sécurité (« voir ART. 4.1 / 4.2 ») : elles seront traduites avec le titre IV (lot 3) ;
  hors décision ici, où elles ne bloquent plus.
- 2.8 (congélateur) n'est que pour la formule Excellence : le tableau des garanties par formule le dit, l'article
  non (`regles/formules/`, `couverture formules`, 7.92).
- 2.10 (catastrophes technologiques) n'est pas traduit : le vocabulaire n'a pas cet événement, qui reste incertain.

Usage : python relecture/assureur_d_lot_2.py  (corrige les propositions en place)"""
import json
from pathlib import Path

DOSSIER = Path(__file__).resolve().parents[1] / "regles" / "propositions" / "assureur-d-habitation-2026"


def f(v, x): return {"f": [v, x]}
def et(*l): return {"et": list(l)}
def ou(*l): return {"ou": list(l)}
def non(x): return {"non": x}
def si(a, b): return {"si": [a, b]}
def concept(n): return {"concept": n}
def ev(*evs): return ou(*[f("evenement", e) for e in evs]) if len(evs) > 1 else f("evenement", evs[0])
def biens(*bs): return ou(*[f("bien", b) for b in bs]) if len(bs) > 1 else f("bien", bs[0])
def exc(cond, article, texte, demander=False, portee="tout"):
    return {"condition": cond, "portee": portee, "a_demander": demander, "article": article, "texte": texte}
def circ(cond, article, texte): return {"condition": cond, "article": article, "texte": texte}
def hors(article, texte, pourquoi): return {"article": article, "texte": texte, "pourquoi": pourquoi}
def garantie(id_, nom, article, texte, perimetre, circonstances=(), exclusions=(), limites=(), accessoire=False):
    g = {"id": id_, "nom": nom, "article": article, "texte": texte, "perimetre": list(perimetre),
         "circonstances": list(circonstances), "obligations": [], "exclusions": list(exclusions), "limites": list(limites)}
    if accessoire:
        g["accessoire"] = True
    return g
def oui_non(var, question, pourquoi, aide_oui, aide_non, proche):
    return {"variable": var, "valeurs": ["oui", "non"], "question": question, "pourquoi": pourquoi,
            "aide": {"oui": aide_oui, "non": aide_non}, "plus_proche": proche}


BIENS_ASSURES = ou(concept("contenu"), f("bien", "element_batiment"))   # le contenu, ou le bâtiment lui-même
DANS_LES_LIEUX = concept("batiment")
DEPENDANCES = ou(*[f("lieu", x) for x in ("cave", "garage", "annexe", "abri_jardin")])
CONFORT_EXCELLENCE = ou(f("formule", "confort"), f("formule", "excellence"))
# La formule est une circonstance, pas un terme du périmètre (7.92) : une garantie au périmètre inconnu n'est que
# « possible », et un refus d'une autre garantie l'emportait sur elle (le congélateur, refusé parce que le contenu
# des appareils est exclu des dommages électriques). Circonstance inconnue : la garantie est retenue, incertaine.
def formule(cond, article, texte): return circ(cond, article, texte)
EXCELLENCE = f("formule", "excellence")
SECURITE_41 = "ATTENTION Vous devez respecter certaines mesures de sécurité pour bénéficier pleinement de la garantie (voir ART. 4.1)"
SECURITE_42 = "ATTENTION Vous devez respecter certaines mesures de sécurité pour bénéficier pleinement de la garantie (voir ART. 4.2)"
LOT_3 = "renvoi au titre IV (mesures de sécurité), traduit avec lui (lot 3)"

# L'accès des voleurs : une variable, pas cinq faits oui/non dont un seul inconnu rendait tout incertain.
VOC_ACCES = {"variable": "acces_voleur", "valeurs": ["escalade", "menaces", "cles_volees", "fausse_qualite", "sans_effraction"],
             "question": "Comment le voleur ou l'auteur est-il entré (hors effraction) ?",
             "pourquoi": "2.5-a, 2.6-a : effraction ou escalade, menaces, vol des clés, introduction par fausse qualité",
             "aide": {"escalade": "par escalade : mur, balcon, fenêtre en hauteur",
                      "menaces": "par menaces ou violences physiques sur l'assuré ou un proche",
                      "cles_volees": "avec les clés de l'assuré, volées auparavant",
                      "fausse_qualite": "en se faisant passer pour un employé, un agent, un livreur",
                      "sans_effraction": "porte ou fenêtre ouverte ou non verrouillée, aucune trace"},
             "plus_proche": "effraction, violence : oui/non chacun ; cinq faits oui/non dont un seul inconnu rend tout incertain"}
ACCES_GARANTI = ou(f("effraction", "oui"), *[f("acces_voleur", x) for x in ("escalade", "menaces", "cles_volees", "fausse_qualite")])
FAMILLE = exc(et(ou(f("auteur", "famille"), f("auteur", "personnel_prive")), non(f("plainte_deposee", "oui"))), "2.5-c",
              "les vols, tentatives de vol, actes de vandalisme ou actes de sabotage dont seraient auteurs ou complices les "
              "membres de votre famille (article 311-12 du Code pénal) ou vos préposés pendant leur service, sauf si une "
              "plainte nominative est déposée à leur encontre", demander=True)


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


# --- 2.1 Incendie et événements annexes -------------------------------------------------------------------------
ecrire("2.1", {
    "evenements": ["incendie", "explosion", "fumee", "foudre", "heurt"],
    "garanties": [garantie(
        "incendie_evenements_annexes", "Incendie, explosion, enfumage, foudre, choc d'un véhicule", "2.1-a",
        "La garantie couvre les dommages matériels causés par : • l ’incendie, c’est-à-dire la combustion avec flammes en "
        "dehors d’un foyer normal…• l ’explosion…• l’enfumage accidentel…• la chute de la foudre…• le choc d’un véhicule",
        [ev("incendie", "explosion", "fumee", "foudre", "heurt"), BIENS_ASSURES, DANS_LES_LIEUX],
        circonstances=[circ(si(f("evenement", "heurt"), ou(f("vehicule_identifie", "oui"), f("plainte_deposee", "oui"))),
                            "2.1-a", "Le véhicule doit être identifié, sinon vous devez déposer une plainte auprès des autorités.")],
        exclusions=[
            exc(et(f("evenement", "incendie"), f("chaleur_sans_feu", "oui")), "2.1-a",
                "l ’incendie, c’est-à-dire la combustion avec flammes en dehors d’un foyer normal"),
            exc(et(f("evenement", "heurt"), ou(f("auteur", "assure"), f("auteur", "famille"))), "2.1-a",
                "le choc d’un véhicule dont ni vous, ni votre conjoint ou concubin, ni vos enfants, n’avez la propriété, "
                "la conduite ou la garde"),
            exc(et(ev("incendie", "explosion"), f("bien_a_l_origine_sinistre", "oui"), biens("electronique", "appareil_electromenager")),
                "2.1-b", "les dommages aux appareils électriques ou électroniques qui ont pour origine l’incendie ou "
                "l’explosion prenant naissance dans l’appareil", portee={"bien": "electronique"}),
            # La foudre tombée au loin (un poteau, le réseau) ne frappe pas le logement : la surtension qu'elle
            # envoie dans les appareils relève des dommages électriques, pour Confort et Excellence (f-d19, 7.93).
            exc(et(f("evenement", "foudre"), f("evenement", "electricite"), biens("electronique", "appareil_electromenager")),
                "2.1-a", "la chute de la foudre, c’est-à-dire du fait de l’ébranlement ou de la calcination causés directement "
                "par l’impact de la foudre", portee={"bien": "electronique"}),
            exc(et(f("evenement", "fumee"), f("cheminee_ouverte", "oui")), "2.1-b",
                "la fumée provenant de cheminées à feu apparent (dits « à l’ouvert »)")])],
    "vocabulaire_manquant": [
        oui_non("vehicule_identifie", "Le véhicule qui a heurté le bâtiment a-t-il été identifié ?", "2.1-a",
                "le conducteur ou la plaque sont connus", "le véhicule est reparti sans être identifié", "plainte_deposee : l'autre branche de la condition, pas l'identification"),
        oui_non("cheminee_ouverte", "La fumée venait-elle d'une cheminée à feu ouvert ?", "2.1-b",
                "cheminée à foyer ouvert, feu apparent", "autre origine (poêle, incendie, appareil)", "evenement = fumee : dit la fumée, pas son origine")],
    "hors_decision": [
        hors("2.1-a", "La garantie couvre également les dommages matériels causés par la chute d’engins volants ou d’objets "
             "provenant de ces derniers", "le vocabulaire ne distingue pas la chute d'un aéronef (« autre » reste incertain)"),
        hors("2.1-a", "le mur du son, c’est-à-dire l’ébranlement consécutif au franchissement du mur du son",
             "le vocabulaire ne distingue pas le mur du son (« autre » reste incertain)"),
        hors("2.1-b", "Ces dommages sont indemnisés au titre de la garantie dommages électriques",
             "un renvoi : l'appareil relève de 2.2")]},
    ["les événements de la garantie dans son périmètre ; plus de concept par événement, ni de `contenu` redéfini",
     "choc d'un véhicule : identifié ou plainte (circonstance) ; pas celui de l'assuré ou de sa famille",
     "« autre » (aéronef, mur du son) n'est plus déclaré traduit : il restait couvert pour n'importe quel événement"])

# --- 2.2 Dommages électriques (Confort et Excellence) ----------------------------------------------------------
ecrire("2.2", {
    "evenements": ["electricite"],
    "garanties": [garantie(
        "dommages_electriques", "Dommages électriques (Confort et Excellence)", "2.2-a",
        "La garantie couvre les dommages matériels causés par les effets d’une surtension, d’une sous-tension ou d’une "
        "surintensité accidentelle, y compris du fait de la foudre, aux installations ou aux appareils électriques",
        [f("evenement", "electricite"), BIENS_ASSURES, DANS_LES_LIEUX],
        circonstances=[formule(CONFORT_EXCELLENCE, "2.2", "Cette garantie est acquise uniquement pour les formules Confort et Excellence")],
        exclusions=[
            exc(f("bien", "consommable"), "2.2-b", "les résistances chauffantes, les fusibles, les disjoncteurs, les "
                "lampes éclairantes, les transformateurs", portee={"bien": "consommable"}),
            exc(f("bien", "denrees_alimentaires"), "2.2-b", "le contenu des appareils endommagés",
                portee={"bien": "denrees_alimentaires"}),
            exc(f("garantie_fabricant", "oui"), "2.2-b", "les dommages sous garantie ou faisant l’objet d’un contrat de "
                "maintenance", demander=True)],
        limites=[{"article": "2.2-a", "texte": "L’indemnisation est égale au coût de réparation ou de remplacement du "
                  "sous-ensemble endommagé, dans la limite de la valeur de remplacement, vétusté déduite au taux de 1 % par "
                  "mois, du bien mobilier endommagé, avec un maximum de 80 %", "montant": "vétusté 1 % par mois, au plus 80 %"}])],
    # Des frais, pas l'appareil : écrites en exclusions, elles refusaient la télé grillée dès qu'un ordinateur
    # était lu avec ses données (f-d19, 7.94).
    "hors_decision": [hors("2.2-b", "les frais de reconstitution des fichiers informatiques", "des frais, pas le dommage à l'appareil"),
                      hors("2.2-b", "les frais de reconstitution de données", "des frais, pas le dommage à l'appareil")]},
    ["formule Confort ou Excellence en circonstance : formule inconnue, réponse incertaine (f-d19)",
     "résistances, fusibles, lampes : `consommable` ; contenu des appareils : `denrees_alimentaires` (portée bien)",
     "plus de `cause_electrique` : l'événement `electricite` suffit ; la foudre directe relève de 2.1",
     "la vétusté est une limite (un montant), pas une condition"])

# --- 2.3 Tempête, grêle, neige -------------------------------------------------------------------------------
INTENSITE = ("lorsque ces phénomènes ont une intensité telle qu’ils détruisent ou endommagent d’autres bâtiments de bonne "
             "construction dans le voisinage ou que leur caractère exceptionnel est attesté par un certificat de la station "
             "météorologique la plus proche (vitesse supérieure à 100 km/h dans le cas du vent)")
ecrire("2.3", {
    "evenements": ["tempete"],
    "garanties": [garantie(
        "tempete_grele_neige", "Tempête, grêle, neige sur les toitures", "2.3-a",
        "La garantie couvre les dommages matériels causés aux biens assurés par l’action directe : • du vent ou du choc "
        "d’un objet renversé ou projeté par le vent (garantie tempête)",
        [f("evenement", "tempete"), BIENS_ASSURES, DANS_LES_LIEUX],
        circonstances=[
            circ(si(f("alea_tempete", "vent"), ou(f("vent_dommages_voisins", "oui"), f("vent_100_kmh", "oui"))), "2.3-a", INTENSITE),
            circ(si(f("alea_tempete", "neige_glace"), ou(f("neige_dommages_voisins", "oui"), f("certificat_meteo", "oui"))), "2.3-a", INTENSITE)],
        exclusions=[
            exc(et(f("alea_tempete", "vent"), f("construction_close", "non")), "2.3-b",
                "les dommages occasionnés par le vent aux bâtiments dont les éléments porteurs ne sont pas ancrés, à ceux "
                "qui ne sont pas construits selon les règles de l’art ou qui ne sont pas entièrement clos et couverts, ainsi "
                "qu’à leur contenu", demander=True),
            exc(et(ou(f("lieu", "jardin"), f("lieu", "terrasse")), non(et(f("bien", "mobilier_jardin"), f("pack_jardin", "oui")))),
                "2.3-b", "les objets en plein air, sauf pour le mobilier de jardin assuré dans le Pack Jardin s’il est souscrit",
                demander=True)])],
    "vocabulaire_manquant": [
        oui_non("vent_100_kmh", "Le vent a-t-il dépassé 100 km/h selon la station météo la plus proche ?", "2.3-a",
                "rafales de plus de 100 km/h relevées ou attestées", "vent moins fort", "vent_80_kmh_irm : un autre seuil (80 km/h, IRM belge)"),
        oui_non("neige_dommages_voisins", "Le poids de la neige ou de la glace a-t-il aussi endommagé d'autres bâtiments du voisinage ?",
                "2.3-a", "d'autres toitures du voisinage ont cédé ou sont abîmées", "seul le bâtiment assuré est touché", "vent_dommages_voisins : la question parle du vent"),
        oui_non("certificat_meteo", "Un certificat de la station météorologique atteste-t-il le caractère exceptionnel du phénomène ?",
                "2.3-a", "un certificat météo l'atteste", "aucun certificat", "vent_80_kmh_irm : un seuil de vent, pas un certificat pour la neige")],
    "hors_decision": [
        hors("2.3-a", "des avalanches de toutes natures", "le vocabulaire n'a pas l'avalanche (événement non traduit : incertain)"),
        hors("2.3-a", "de la grêle, du poids de la neige ou de la glace sur votre piscine et votre abri de piscine (si l’option "
             "est souscrite pour chacun de ces biens dans le Pack Piscine)", "la piscine est exclue sauf Pack Piscine (1.1-b)"),
        hors("2.3-a", "Sont considérés comme constituant un seul et même sinistre les dommages causés par la pluie, la neige ou "
             "la grêle pénétrant à l’intérieur du bâtiment, consécutifs à l’événement garanti et survenus dans les 48 heures",
             "le décompte des sinistres, pas la couverture ; la pluie entrée par le toit relève aussi de 2.4")]},
    ["intensité (voisinage, certificat, plus de 100 km/h) pour le vent et pour la neige",
     "objets en plein air : par le lieu (jardin, terrasse), sauf mobilier de jardin avec Pack Jardin (f-d14)",
     "ancrage, règles de l'art : la construction non close (variable existante) ; avalanche hors décision"])

# --- 2.4 Dégâts des eaux et gel ------------------------------------------------------------------------------
CAUSES_GARANTIES = ou(*[f("cause_eau", c) for c in ("inondation", "infiltration_toiture", "infiltration_exterieure",
                                                     "fuite_installation", "gel", "piscine_exterieure",
                                                     "debordement_recipient", "debordement_aquarium")])
ecrire("2.4", {
    "evenements": ["degat_eaux", "mazout"],
    "garanties": [
        garantie("venues_eau_gel", "Venues d'eau et gel", "2.4-a", "La garantie couvre les dommages résultant : • d’eaux de "
                 "ruissellement à la surface du sol, • du refoulement des égouts, • d’infiltrations par les toitures",
                 [f("evenement", "degat_eaux"), BIENS_ASSURES, DANS_LES_LIEUX],
                 circonstances=[circ(CAUSES_GARANTIES, "2.4-a", "La garantie couvre les dommages résultant : • d’eaux de "
                                     "ruissellement à la surface du sol…• de débordements et renversements de récipients ou d’aquariums")],
                 exclusions=[
                     exc(et(f("cause_eau", "fuite_installation"), f("canalisation_enterree", "oui")), "2.4-c",
                         "les dommages consécutifs à des fuites d’eau ou débordements provenant des canalisations enterrées"),
                     exc(et(f("bien", "canalisation"), f("canalisation_enterree", "oui")), "2.4-c",
                         "les dommages sur les canalisations enterrées", portee={"bien": "canalisation"}),
                     exc(et(f("cause_eau", "infiltration_exterieure"), f("batiment_moins_10_ans", "oui")), "2.4-c",
                         "les dommages résultant d’infiltrations à travers les murs et façades extérieurs lorsque la garantie "
                         "décennale du constructeur doit s’appliquer", demander=True),
                     exc(f("evenement", "catastrophe_naturelle"), "2.4-c", "les dommages relevant de la garantie Catastrophes naturelles"),
                     exc(f("cause_eau", "condensation"), "2.4-c", "les dommages dus à l’humidité et/ou à la condensation")]),
        garantie("recherche_fuite", "Recherche de fuite", "2.4-a", "Sont prises en charge au titre de la recherche de fuite",
                 [f("evenement", "degat_eaux"), DANS_LES_LIEUX], accessoire=True),
        garantie("debordement_cuves", "Débordement des cuves de combustible (Excellence)", "2.4-b",
                 "les dommages résultant du débordement accidentel des cuves situées à l’intérieur des bâtiments principaux "
                 "d’habitation et de leurs dépendances et contenant le combustible nécessaire à l’alimentation du chauffage",
                 [f("evenement", "mazout"), BIENS_ASSURES, DANS_LES_LIEUX],
                 circonstances=[formule(EXCELLENCE, "2.4-b", "Sont également garantis : • les dommages résultant du "
                                        "débordement accidentel des cuves")],
                 exclusions=[exc(f("bien", "mazout"), "2.4-c", "le coût du combustible perdu, en cas de débordement accidentel "
                                 "des cuves", portee={"bien": "mazout"})])],
    "vocabulaire_manquant": [
        oui_non("canalisation_enterree", "La canalisation qui fuit est-elle enterrée (dans le sol, hors du bâtiment) ?", "2.4-c",
                "tuyau enterré dans le jardin ou sous la dalle", "tuyau apparent, ou dans les murs", "canalisation_encastree : une canalisation dans les murs, pas dans le sol"),
        oui_non("batiment_moins_10_ans", "La construction a-t-elle été réceptionnée il y a moins de dix ans ?", "2.4-c (décennale)",
                "la déclaration dit la maison neuve, récente, ou achevée il y a moins de dix ans (« fait construire » ne "
                "dit pas quand)", "construction plus ancienne", "aucune : le vocabulaire ne dit pas l'âge du bâtiment")],
    "hors_decision": [
        hors("2.4-a", "Dès la constatation de l’origine du sinistre et pour ce type d’événement, la garantie sera suspendue de "
             "plein droit", "la suite du contrat après le sinistre, pas la couverture de celui-ci"),
        hors("2.4-a", "d’infiltrations par les gaines d’aération ou de ventilation",
             "pas de valeur propre ; lue comme une infiltration extérieure, couverte aussi"),
        hors("2.4-b", "les frais de surconsommation d’eau consécutifs à une venue d’eaux", "des frais, pas un dommage à décider"),
        hors("2.4-c", "les frais de réparation ou de remplacement de l’élément à l’origine du dommage couvert par le contrat",
             "un montant : le tuyau n'est pas payé, les dommages qu'il cause le sont (f-d03)"),
        hors("2.4-c", SECURITE_42, LOT_3)]},
    ["causes du contrat rapportées aux valeurs existantes de `cause_eau` (aucune valeur nouvelle)",
     "canalisation enterrée (et non encastrée) ; décennale à demander (f-d23)",
     "élément à l'origine : un montant, hors décision ; cuves de combustible : événement `mazout`, formule Excellence",
     "surconsommation, gaines d'aération, suspension : hors décision ; mesures de sécurité au lot 3"])

# --- 2.5 Vol et vandalisme -----------------------------------------------------------------------------------
ecrire("2.5", {
    "evenements": ["vol", "vandalisme"],
    "garanties": [
        garantie("vol_vandalisme", "Vol, tentative de vol, vandalisme", "2.5-a",
                 "La garantie couvre la disparition, la destruction ou la détérioration des biens assurés résultant : • d’un "
                 "vol, • d’une tentative de vol, • d ’un acte de vandalisme ou de sabotage",
                 [ev("vol", "vandalisme"), concept("contenu"), DANS_LES_LIEUX],
                 circonstances=[circ(ACCES_GARANTI, "2.5-a", "lorsque ces méfaits sont commis à l’intérieur des locaux "
                                     "assurés, par effraction ou escalade de ces locaux…au vol dans les locaux assurés par menaces "
                                     "physiques…au vol à la suite du vol des clés…au vol à la suite d’une introduction par fausse qualité")],
                 exclusions=[
                     FAMILLE,
                     exc(f("cles_deposees_exterieur", "oui"), "2.5-c", "les vols des clés déposées, sans protection, à "
                         "l’extérieur des locaux y compris dans une boîte à clé ou dans une boîte à lettres ainsi que toutes "
                         "leurs conséquences"),
                     *[exc(et(f("bien", b), DEPENDANCES), "2.5-c", "l es vols des objets précieux dans les dépendances",
                           portee={"bien": b}) for b in ("bijoux", "valeurs")],
                     exc(et(DEPENDANCES, f("formule", "eco")), "2.5-c", "les vols dans les dépendances, si vous avez souscrit "
                         "la formule Eco", demander=True),
                     exc(f("construction_close", "non"), "2.5-c", "les vols, tentatives de vol, actes de vandalisme ou actes "
                         "de sabotage commis sur les terrasses, les balcons, dans les jardins et dans les locaux non entièrement "
                         "clos ou couverts")]),
        garantie("vol_cles", "Vol des clés (Confort et Excellence)", "2.5-a",
                 "au vol des clés, en tous lieux de l’Union européenne, du Royaume-Uni de Grande-Bretagne et d’Irlande du "
                 "Nord, de votre local d’habitation et/ou des dépendances assurés dès lors que le dépôt de plainte fait état d’un vol",
                 [f("evenement", "vol"), f("bien", "cles")],
                 circonstances=[circ(f("plainte_deposee", "oui"), "2.5-a", "dès lors que le dépôt de plainte fait état d’un vol"),
                                formule(CONFORT_EXCELLENCE, "2.5-a", "Extensions de garantie pour les formules Confort et Excellence")],
                 exclusions=[exc(f("cles_deposees_exterieur", "oui"), "2.5-c", "les vols des clés déposées, sans protection, "
                                 "à l’extérieur des locaux y compris dans une boîte à clé ou dans une boîte à lettres")])],
    "vocabulaire_manquant": [
        VOC_ACCES,
        oui_non("cles_deposees_exterieur", "Les clés avaient-elles été laissées dehors (boîte aux lettres, boîte à clé, sous le paillasson) ?",
                "2.5-c", "clés laissées sans protection à l'extérieur", "non", "cles_a_proximite : des clés laissées près d'une porte, pas dehors sans protection")],
    "hors_decision": [
        hors("2.5", "Il vous appartient de réunir tous moyens de preuve", "la preuve, pas la couverture"),
        hors("2.5-a", "ayant laissé des traces apparentes", "porté par l'effraction"),
        hors("2.5-a", "exclusivement dans les 48 h qui suivent l’heure à laquelle vous avez eu connaissance du vol des clés",
             "un délai que le vocabulaire ne mesure pas"),
        hors("2.5-a", "au vol des papiers d’identité, du permis de conduire, du certificat d’immatriculation (ex. carte grise) "
             "et de la carte de crédit", "le vocabulaire ne distingue pas les papiers ni la carte de crédit"),
        hors("2.5-b", "le vol des objets précieux vous appartenant de la résidence principale dans votre résidence secondaire "
             "lorsque vous y séjournez", "option et formule Excellence ; le vocabulaire ne distingue pas la résidence secondaire"),
        hors("2.5-b", "les frais de remplacement des clés, barillets, système de téléc ommande de véhicule",
             "les clés du véhicule : des frais, le véhicule n'est pas assuré"),
        hors("2.5-b", "le vol de votre plaque signalétique professionnelle située à l’extérieur de votre local d’habitation",
             "le vocabulaire ne distingue pas une plaque professionnelle"),
        hors("2.5-c", "les vols des objets d’art et de fourrures - lorsque leur valeur excède 2 000 € - dans les dépendances et "
             "les résidences secondaires", "le vocabulaire ne distingue ni les fourrures ni la valeur d'un objet"),
        hors("2.5-c", "le vol des rampes amovibles d’accès pour personne à mobilité réduite",
             "le vocabulaire ne distingue pas ces rampes"),
        hors("2.5-c", SECURITE_41, LOT_3)]},
    ["effraction (existante) ou `acces_voleur` (escalade, menaces, clés volées, fausse qualité) : sans effraction ni "
     "accès garanti, un refus (f-d18)",
     "famille ou préposés sans plainte (`plainte_deposee`) ; clés laissées dehors (f-d12) ; dépendances en Eco à "
     "demander (f-d25) ; objets précieux en dépendance (portée bien)",
     "vol des clés en tous lieux : une garantie à part, Confort ou Excellence, sur plainte",
     "terrasses, jardins : hors des lieux assurés ; locaux non clos : `construction_close`"])

# --- 2.6 Détériorations immobilières -------------------------------------------------------------------------
INTERIEUR = ou(*[f("lieu", x) for x in ("logement", "grenier", "cave", "garage", "annexe", "abri_jardin")])
ecrire("2.6", {
    "evenements": ["vandalisme", "vol"],
    "garanties": [garantie(
        "deteriorations_immobilieres", "Détériorations immobilières", "2.6-a",
        "La garantie couvre la détérioration de : - vos biens immobiliers…à la suite d’un acte de vandalisme, d’une tentative "
        "de vol ou d’un vol",
        [ev("vandalisme", "vol"), f("bien", "element_batiment"), DANS_LES_LIEUX],
        circonstances=[circ(si(INTERIEUR, ACCES_GARANTI), "2.6-a",
                            "Si les dommages sont commis à l’intérieur de votre habitation ou de ses dépendances, les "
                            "détériorations doivent être commises à la suite : - de l’effraction ou de l’escalade des locaux "
                            "assurés, ayant laissé des traces apparentes, - de menaces physiques ou violences physiques, - du vol "
                            "des clés, - de l’introduction par fausse qualité")],
        exclusions=[
            {**FAMILLE, "article": "2.6-b", "texte": "les vols, tentatives de vol ou actes de vandalisme dont seraient auteurs "
             "ou complices les membres de votre famille (article 311-12 du Code pénal) ou vos préposés pendant leur service, "
             "sauf si une plainte nominative est déposée à leur encontre"},
            exc(f("graffiti_mur_exterieur", "oui"), "2.6-b", "les graffitis, tags, pochoirs et inscriptions de toute nature, "
                "affichages, salissures, rayures commis à l’extérieur de votre local d’habitation et de ses dépendances",
                demander=True)])],
    "vocabulaire_manquant": [VOC_ACCES],
    "hors_decision": [
        hors("2.6-a", "votre piscine, spa ou jacuzzi (si l’option du Pack Piscine est souscrite)",
             "la piscine est exclue sauf Pack Piscine (1.1-b)"),
        hors("2.6-a", "votre véranda (si l’option est souscrite)", "la véranda est exclue sauf option (1.1-b)"),
        hors("2.6-a", "La garantie couvre également les frais de remplacement à l’identique des moyens de protection équipant ces locaux",
             "des frais, compris dans la garantie"),
        hors("2.6-b", "le vol des biens immobiliers", "la garantie couvre la détérioration, pas le vol d'un élément du bâtiment"),
        hors("2.6-b", SECURITE_41, LOT_3)]},
    ["le bâtiment (`element_batiment`) détérioré par vandalisme ou vol ; à l'intérieur, effraction ou accès garanti",
     "tags à l'extérieur : `graffiti_mur_exterieur`, à demander (f-d10)"])

# --- 2.7 Bris de glaces --------------------------------------------------------------------------------------
ecrire("2.7", {
    "evenements": ["bris"],
    "garanties": [
        garantie("bris_glaces", "Bris de glaces", "2.7-a",
                 "La garantie couvre, lorsqu’ils sont brisés accidentellement, les frais de remplacement : • des miroirs "
                 "intérieurs, des glaces équipant les meubles et les aquariums, • des vitrages des portes, portes-fenêtres, "
                 "baies et fenêtres, y compris en toiture",
                 [f("evenement", "bris"), biens("vitre", "miroir", "verre_meuble", "panneau_verre_plastique", "serre"), DANS_LES_LIEUX]),
        garantie("bris_glace_plus", "Bris de glace + (Confort et Excellence)", "2.7-a",
                 "La garantie est étendue pour les formules Confort et Excellence aux : • plaques vitrocéramiques, plaques "
                 "induction, • vérandas ou loggias (si l’option est souscrite), • vitraux, marquises, • appareils sanitaires",
                 [f("evenement", "bris"), biens("table_cuisson_vitroceramique", "sanitaire", "veranda"), DANS_LES_LIEUX],
                 circonstances=[formule(CONFORT_EXCELLENCE, "2.7-a", "La garantie est étendue pour les formules Confort et Excellence aux")]),
        garantie("bris_glace_renforce", "Bris de glace renforcé (Excellence)", "2.7-a",
                 "La garantie est étendue pour la formule Excellence aux survitrages mobiles, vitres d’insert, vitres "
                 "d’appareils électroménagers, ainsi que les panneaux solaires et photovoltaïques",
                 [f("evenement", "bris"), biens("appareil_electromenager", "panneau_solaire"), DANS_LES_LIEUX],
                 circonstances=[formule(EXCELLENCE, "2.7-a", "La garantie est étendue pour la formule Excellence aux")])],
    "exclusions_communes": [exc(et(f("bien", "appareil_electromenager"), non(EXCELLENCE)), "2.7-b",
                                "les appareils électroménagers, sauf ceux garantis dans le « Bris de glace renforcé » ci-dessus",
                                portee={"bien": "appareil_electromenager"})],
    "hors_decision": [
        hors("2.7-a", "des panneaux de signalisation", "le vocabulaire ne les distingue pas (« enseigne » est autre chose)"),
        hors("2.7-a", "d’une superficie jusqu’à 5 m2", "le vocabulaire ne distingue pas la taille d'une serre"),
        hors("2.7-a", "les frais de clôture provisoire lorsque cette dernière est indispensable pour la sécurité des locaux",
             "des frais, compris dans la garantie"),
        hors("2.7-a", "les dommages matériels occasionnés par les éclats de verre", "compris dans la garantie"),
        hors("2.7-b", "les serres d’une superficie de plus de 5 m2, sauf si le Pack Jardin est souscrit",
             "le vocabulaire ne distingue pas la taille d'une serre"),
        hors("2.7-b", "les ébréchures ainsi que tous dommages résultant de la vétusté ou de l’impropriété du support",
             "le vocabulaire ne distingue ni l'ébréchure ni le support")]},
    ["trois garanties : la base, « Bris de glace + » (Confort, Excellence : vitrocéramique, f-d21), « renforcé » (Excellence)",
     "plus d'extensions sur un concept inconnu ; panneaux de signalisation, taille des serres : hors décision"])

# --- 2.8 Contenu du congélateur ------------------------------------------------------------------------------
ecrire("2.8", {
    "evenements": ["electricite"],
    "garanties": [garantie(
        "contenu_congelateur", "Contenu du congélateur et/ou réfrigérateur", "2.8-b",
        "La garantie couvre les pertes ou détériorations causes aux denrées alimentaires contenues dans les congélateurs et/ou "
        "réfrigérateurs endommagés",
        # Formule Excellence : le tableau des garanties par formule le dit (page 11), aucun article (7.92, f-d20).
        [f("evenement", "electricite"), f("bien", "denrees_alimentaires"), DANS_LES_LIEUX],
        circonstances=[formule(EXCELLENCE, "2.8-b", "La garantie couvre les pertes ou détériorations causes aux denrées "
                               "alimentaires"),
                       circ(ou(f("cause_perte_alimentaire", "coupure_soudaine_reseau"),
                               f("cause_perte_alimentaire", "derangement_installation")), "2.8-b",
                            "à l’occasion d’un sinistre dommages électrique indemnisé (ART 2-2), à la suite d’un sinistre "
                            "indemnisé au titre de la garantie panne électroménager (TITRE III) ou d’une coupure électrique "
                            "accidentelle avec justificatif de votre fournisseur d’électricité")],
        exclusions=[exc(f("manque_entretien", "oui"), "2.8-c", "dues à un mauvais entretien ou à une utilisation non "
                        "conforme du congélateur et/ou réfrigérateur aux instructions du fabricant")])],
    "hors_decision": [
        hors("2.8-c", "provenant de l’arrêt d’un courant électrique, lorsqu’il est dû : - à une grève du fournisseur, - à des "
             "ordres émanant d’un service public ou des autorités civiles ou militaires, - au fait de l’assuré",
             "rare ; le vocabulaire ne distingue pas l'origine d'une coupure"),
        hors("2.8-c", "consécutives à une fuite du liquide frigorigène", "le vocabulaire ne distingue pas cette panne")]},
    ["formule Excellence seulement : le tableau des garanties par formule (page 11), pas le texte de l'article (7.92)",
     "denrées perdues après une coupure du réseau, ou un dommage électrique de l'installation",
     "grève, ordre des autorités, liquide frigorigène : hors décision ; le justificatif est une preuve"])

# --- 2.9 Catastrophes naturelles -----------------------------------------------------------------------------
ecrire("2.9", {
    "evenements": ["catastrophe_naturelle"],
    "garanties": [
        garantie("catastrophes_naturelles", "Catastrophes naturelles", "2.9-a",
                 "La garantie couvre les dommages matériels directs non assurables ayant eu pour cause déterminante "
                 "l’intensité anormale d’un agent naturel",
                 [f("evenement", "catastrophe_naturelle"), BIENS_ASSURES, DANS_LES_LIEUX],
                 circonstances=[circ(f("arrete_catnat_30j", "oui"), "2.9-a", "La garantie est mise en jeu par une déclaration "
                                     "faite au plus tard trente jours après publication au Journal Officiel d’un arrêté "
                                     "interministériel constatant l’état de catastrophe naturelle")],
                 exclusions=[exc(f("terrain_non_constructible", "oui"), "2.9-b", "les biens assurés construits sur des terrains "
                                 "classés inconstructibles par un plan de prévention des risques à l’exception toutefois des biens "
                                 "existants antérieurement à la publication de ce plan")]),
        garantie("relogement_catnat", "Relogement d'urgence après une catastrophe naturelle", "2.9-a",
                 "les frais de relogement d’urgence des personnes sinistrées dont la résidence principale est rendue impropre à "
                 "l’habitation", [f("evenement", "catastrophe_naturelle"), f("residence_principale_inhabitable", "oui")],
                 accessoire=True)],
    "vocabulaire_manquant": [oui_non(
        "arrete_catnat_30j", "Un arrêté de catastrophe naturelle a-t-il été publié, et déclarez-vous le sinistre au plus tard 30 jours après ?",
        "2.9-a", "l'arrêté est paru au Journal officiel et la déclaration suit de moins de 30 jours",
        "pas d'arrêté, ou déclaration plus tardive", "aucune : le vocabulaire ne dit pas l'arrêté")],
    "hors_decision": [
        hors("2.9-a", "lorsque les mesures habituelles à prendre pour prévenir ces dommages n’ont pu empêcher leur survenance ou "
             "n’ont pu être prises", "constaté par l'arrêté, pas par l'assuré"),
        hors("2.9-a", "les mouvements de terrain différentiels consécutifs à la sécheresse et à la réhydratation des sols",
             "le vocabulaire ne distingue pas la sécheresse"),
        hors("2.9-a", "Vous devez également nous faire savoir, dans le même délai, si d’autres assurances sont concernées",
             "procédure après sinistre"),
        hors("2.9-a", "Nos obligations", "les délais de l'assureur, pas la couverture"),
        hors("2.9-b", "les biens immobiliers construits en violation des règles administratives en vigueur lors de leur mise en "
             "place et tendant à prévenir les dommages causés par une catastrophe naturelle", "rare ; le vocabulaire ne le distingue pas"),
        hors("2.9-b", "en cas de dommages ayant eu pour cause déterminante les mouvements de terrain différentiels consécutifs à "
             "la sécheresse et à la réhydratation des sols, les dommages survenus sur les constructions constitutives d’éléments "
             "annexes", "le vocabulaire ne distingue pas la sécheresse")]},
    ["l'arrêté publié et la déclaration dans les 30 jours : une seule circonstance (f-d08)",
     "relogement d'urgence : garantie accessoire ; sécheresse, violation des règles : hors décision"])

# --- 2.11 et 2.12 Attentats, émeutes -------------------------------------------------------------------------
ecrire("2.11", {
    "evenements": ["attentat"],
    "garanties": [garantie(
        "attentats", "Attentats et actes de terrorisme", "2.11-a",
        "La garantie couvre les dommages matériels directs (y compris les frais de décontamination), subis sur le territoire "
        "national, causés aux biens assurés par un attentat ou un acte de terrorisme",
        [f("evenement", "attentat"), BIENS_ASSURES, DANS_LES_LIEUX])],
    # Des frais, pas un dommage : l'exclusion est écrite pour être citée, sa condition (null, « faux ») ne joue jamais.
    "exclusions_communes": [exc(None, "2.11-b", "les frais de décontamination des déblais ainsi que leur confinement")]},
    ["les biens assurés, dans les lieux assurés ; décontamination des déblais : hors décision"])

ecrire("2.12", {
    "evenements": ["attentat"],
    "garanties": [garantie(
        "emeutes", "Émeutes et mouvements populaires", "2.12-a",
        "La garantie couvre, dans les conditions et limites prévues pour chaque garantie si elle est souscrite, les dommages "
        "matériels causés aux biens assurés survenant lors d’émeutes ou de mouvements populaires",
        [f("evenement", "attentat"), BIENS_ASSURES, DANS_LES_LIEUX])]},
    ["émeutes : l'événement `attentat` (émeute, manifestation qui dégénère)"])

# --- 2.13 Intervention des secours ---------------------------------------------------------------------------
ecrire("2.13", {
    "garanties": [garantie(
        "intervention_secours", "Intervention des moyens de secours", "2.13-a",
        "La garantie couvre les dommages matériels occasionnés par l’intervention des services de secours à proximité des "
        "locaux assurés", [DANS_LES_LIEUX], accessoire=True)]},
    ["aucun événement déclaré traduit (le modèle les déclarait tous, responsabilité civile et assistance comprises)"])
