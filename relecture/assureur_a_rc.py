"""Relecture de la responsabilité civile et de la défense et recours de l'assureur A (2.5, 2.14, 5), rédigées par
Mistral Large (consigne v12) le 20 nov. : 3 articles, 44 contrôles bloquants, une vingtaine de variables nouvelles
proposées (DEMARCHE 7.99).

Ce que le modèle avait fait, et ce qui change :
- Le vocabulaire. Le modèle proposait une variable par condition (l'âge de l'assuré, le nombre d'enfants gardés, les
  revenus de l'économie de partage, la plateforme agréée…). Le vocabulaire de D les dit déjà : `origine_rc`,
  `victime`, `bien_confie`, l'événement `litige` et `domaine_litige`. Aucune variable nouvelle.
- Les garanties. 5 : huit garanties (biens immeubles, animaux, déplacements, sports, garde d'enfants…) qui ne
  distinguaient que ce qui a causé le dommage ; une seule garantie de vie privée suffit, les exclusions disent ce qui
  n'en relève pas (véhicules à moteur, contrat, profession, biens confiés, le feu parti du bâtiment assuré). 2.5 : la
  responsabilité du fait du bâtiment et du terrain. 2.14 : la défense pénale et le recours, comme 22.1 chez D.
- Hors décision, cité : le trouble de voisinage, l'amiante, les citernes, la chasse (le vocabulaire la confond avec les
  sports en club, que A couvre), les seuils en euros, l'insolvabilité des tiers, l'assistance bénévole.

Usage : python relecture/assureur_a_rc.py  (corrige les propositions en place)"""
import json
from pathlib import Path

DOSSIER = Path(__file__).resolve().parents[1] / "regles" / "propositions" / "assureur-a-habitation-2025"


def f(v, x): return {"f": [v, x]}
def et(*l): return {"et": list(l)}
def ou(*l): return {"ou": list(l)}
def non(x): return {"non": x}
def un_de(v, *xs): return ou(*[f(v, x) for x in xs]) if len(xs) > 1 else f(v, xs[0])
def exc(cond, article, texte, demander=False):
    return {"condition": cond, "portee": "tout", "a_demander": demander, "article": article, "texte": texte}
def hors(article, texte, pourquoi): return {"article": article, "texte": texte, "pourquoi": pourquoi}
def limite(article, texte, montant): return {"article": article, "texte": texte, "montant": montant}
def garantie(id_, nom, article, texte, perimetre, exclusions=(), limites=()):
    return {"id": id_, "nom": nom, "article": article, "texte": texte, "perimetre": list(perimetre),
            "circonstances": [], "obligations": [], "exclusions": list(exclusions), "limites": list(limites)}


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
# « Tiers : toute personne qui n'est pas considérée comme assurée » (12/tiers) : l'auteur, son foyer, son conjoint.
PAS_UN_TIERS = exc(un_de("victime", "assure", "conjoint"), "12/tiers", "Toute personne qui n’est pas considérée comme assurée.")

ecrire("2.5", {
    "evenements": ["responsabilite"],
    "garanties": [garantie(
        "rc_immeuble", "Responsabilité civile immeuble", "2.5",
        "Nous prenons en charge la responsabilité civile que vous pouvez encourir sur base : • du livre 6 du Code civil • de "
        "l’article 1721 du Code civil c'est-à-dire le recours des locataires pour les dommages causés aux tiers du fait : • du "
        "bâtiment, du contenu", [RC, un_de("origine_rc", "immeuble", "habitation")],
        exclusions=[PAS_UN_TIERS,
                    exc(f("bien_confie", "oui"), "2.5-a", "à des biens dont vous avez la garde")],
        limites=[limite("2.5", "18.425.000 EUR pour l’indemnisation des dommages résultant de lésions corporelles", "18425000"),
                 limite("2.5", "3.685.000 EUR pour l’indemnisation des dommages résultant de dégâts matériels", "3685000")])],
    "hors_decision": [
        hors("2.5", "Notre garantie s’étend au trouble de voisinage au sens de l’article 3.101, à l'exclusion de l'article 3.102, "
             "du Code civil s’ils découlent d’un événement soudain, imprévisible pour vous, sauf s’il oppose les occupants d'un "
             "même immeuble à logements multiples", "le vocabulaire ne distingue pas le trouble de voisinage"),
        hors("2.5", "des ascenseurs et monte-charge pour autant qu’ils soient déclarés conformes à la réglementation en vigueur "
             "par un organisme de contrôle entretenus annuellement par une entreprise agréée",
             "lu comme le bâtiment ; la conformité de l'ascenseur : rare, le vocabulaire ne la distingue pas"),
        hors("2.5", "sans dépasser au total 5 hectares", "la superficie du terrain : rare ; le vocabulaire ne la distingue pas"),
        hors("2.5-a", "par l’amiante sous toutes ses formes", "rare ; le vocabulaire ne distingue pas l'amiante"),
        hors("2.5-a", "en cas de non-respect de la réglementation applicable au contrôle des citernes",
             "rare ; le vocabulaire ne distingue pas le contrôle des citernes")]},
    ["le bâtiment, le terrain, le feu ou l'eau partis du logement : `origine_rc` ; les biens gardés : `bien_confie`",
     "les cinq variables proposées (amiante, ascenseur, trouble de voisinage…) : hors décision, citées"])

ecrire("2.14", {
    "evenements": ["litige"],
    "garanties": [
        garantie("defense_penale", "Défense pénale", "2.14~1",
                 "que vous et toutes les personnes assurées auront exposés pour leur défense devant une juridiction pénale où ils "
                 "sont cités à la suite d’un événement garanti par la présente assurance",
                 [LITIGE, f("domaine_litige", "defense_penale")],
                 limites=[limite("2.14~2", "Défense et recours 6.500 EUR", "6500")]),
        garantie("recours", "Recours contre les tiers responsables", "2.14~1",
                 "que les assurés, à l’exception du personnel même occasionnel à leur service privé auront exposés pour l’exercice "
                 "de recours contre les tiers responsables de dommages",
                 [LITIGE, f("domaine_litige", "recours_dommage")],
                 limites=[limite("2.14~2", "Défense et recours 6.500 EUR", "6500")])],
    "hors_decision": [
        hors("2.14~1", "Nous couvrons également l’insolvabilité des tiers", "le vocabulaire ne distingue pas l'insolvabilité du tiers"),
        hors("2.14~1", "les amendes et les dépens de l’instance pénale, ainsi que pour les frais de poursuites pénales",
             "des frais non remboursés, pas un refus du sinistre"),
        hors("2.14~2", "les recours entre assurés", "le vocabulaire ne dit pas contre qui le recours est exercé"),
        hors("2.14~2", "les demandes en réparation de dommages exclus aux termes de la garantie « Responsabilité Civile », ainsi "
             "que pour les dommages inférieurs à 250 EUR", "le montant et le renvoi à la responsabilité civile : hors décision"),
        hors("2.14~2", "pour un pourvoi en Cassation ou devant une juridiction supranationale, si les intérêts en cause "
             "n’atteignent pas 1.250 EUR en principal", "une étape de la procédure, pas la déclaration"),
        hors("2.14~2", "une action ou procédure menée à l’étranger sans notre accord écrit préalable",
             "le vocabulaire ne distingue pas le pays de la procédure")]},
    ["l'événement `litige` et `domaine_litige` (vocabulaire de D) : la défense pénale et le recours après un dommage",
     "`tiers_insolvable` : hors décision"])

ecrire("5", {
    "evenements": ["responsabilite"],
    "garanties": [garantie(
        "rc_vie_privee", "Responsabilité civile vie privée", "5.1",
        "Nous vous assurons dans le monde entier lorsque votre responsabilité est mise en cause pour des dommages occasionnés à "
        "un tiers dans le cadre de votre vie privée et en dehors de tout contrat", [RC],
        exclusions=[
            PAS_UN_TIERS,
            exc(f("origine_rc", "activite_professionnelle"), "5.1", "dans le cadre de votre vie privée"),
            exc(f("origine_rc", "contrat"), "5.1", "en dehors de tout contrat"),
            exc(f("bien_confie", "oui"), "5.10",
                "les dommages causés aux biens mobiliers et immobiliers dont vous avez la garde"),
            exc(f("origine_rc", "vehicule_moteur"), "5.4-a",
                "des véhicules automoteurs ou équipés d’un moteur même non autonomes autres que ceux cités au point 2.4"),
            exc(et(f("origine_rc", "habitation"), un_de("evenement", "incendie", "explosion", "fumee")), "5.2-a",
                "les dommages matériels causés par le feu, par l’incendie, l’explosion ou la fumée consécutive à un feu ou à un "
                "incendie prenant naissance dans ou communiqué par un bâtiment assuré par le présent contrat"),
            exc(f("intentionnel", "oui"), "5.10", "pour les sinistres intentionnels")],
        limites=[limite("5.1", "les dommages résultant de lésions corporelles à concurrence de 24.763.874,96 EUR", "24763874.96"),
                 limite("5.1", "les dommages matériels à concurrence de 7.131.995,99 EUR", "7131995.99"),
                 limite("5.1", "Une franchise de 258,70 EUR est d’application pour les dommages matériels", "franchise 258.70")])],
    "hors_decision": [
        hors("5.3", "La garantie est acquise pour 5 chevaux de selle dont vous êtes propriétaire, ou plus si leur nombre est "
             "mentionné en conditions particulières", "le nombre de chevaux : rare ; le vocabulaire ne le distingue pas"),
        hors("5.3-a", "causés par le gibier ou les animaux sauvages, domptés ou non, à l’exception des cervidés",
             "rare ; le vocabulaire ne distingue pas les animaux sauvages"),
        *[hors("5.4~1", t, "pas une exclusion : un engin que la garantie couvre ; le vocabulaire range les engins lents avec la "
               "personne et les rapides avec les véhicules à moteur (`origine_rc`)") for t in (
            "pour les dommages causés par des chaises roulantes électriques pour personnes à mobilité réduite",
            "pour les dommages causés par des cycles électriques à maximum 3 roues",
            "pour les dommages causés par des engins de déplacement motorisés",
            "pour les dommages causés par les outils motorisés utilisés à des fins privées sur un terrain privé")],
        hors("5.4~1", "pour les dommages corporels causés à un tiers (au sens du présent contrat) en conduisant conformément à la "
             "loi un véhicule automoteur qui vous est confié occasionnellement", "une extension rare ; le vocabulaire ne distingue pas le véhicule confié"),
        hors("5.4~2", "âgé de 16 ans minimum, qui a causé intentionnellement le sinistre",
             "le recours de l'assureur contre l'assuré après avoir indemnisé la victime : pas un refus du sinistre"),
        hors("5.4~3", "âgé de 18 ans minimum, qui a causé le sinistre en raison de l’une des fautes lourdes suivantes",
             "le recours de l'assureur contre l'assuré après avoir indemnisé la victime : pas un refus du sinistre"),
        hors("5.10", "pour les actes de terrorisme", "rare en responsabilité civile ; le vocabulaire ne distingue pas le terrorisme"),
        hors("5.10", "les dommages ou l’aggravation des dommages causés par la modification de la structure du noyau de l’atome",
             "rare ; le vocabulaire ne distingue pas le nucléaire"),
        hors("5.10", "les dommages découlant de la responsabilité civile soumise à une assurance légalement obligatoire",
             "lu par les véhicules à moteur ; le reste (chasse…) rare"),
        hors("12/contenu", "Il s’agit des biens meubles qui se trouvent dans le bâtiment et qui vous appartiennent ou vous sont confiés",
             "le contenu assuré en dommages ; en responsabilité civile, ce qui a causé le dommage est lu par `origine_rc`"),
        hors("5.4-a", "l’emploi de jet-skis ainsi que l’emploi de véhicules aériens", "lu comme un véhicule à moteur ; sinon rare"),
        hors("5.5-a", "Nous n’indemnisons pas les dommages causés par la pratique de la chasse.",
             "le vocabulaire range la chasse avec les sports en club et les compétitions, que A couvre (5.5)"),
        hors("5.6", "lorsque vous assurez la garde, contre rémunération, de maximum 5 enfants de tiers",
             "une activité rémunérée tenue pour privée : rare ; le vocabulaire ne la distingue pas"),
        hors("5.7", "Dans le cadre de l’économie de partage", "rare ; le vocabulaire ne distingue pas l'économie de partage"),
        hors("5.8", "Nous vous assurons pour les dommages subis par un tiers qui aurait participé, dans le cadre de votre vie "
             "privée et en cas de danger imminent, à votre sauvetage", "rare ; le vocabulaire ne distingue pas le sauvetage"),
        hors("5.10", "ivresse ou état analogue résultant de l’utilisation de produits autres que des boissons alcoolisées, actes "
             "de violence commis sur les personnes", "l'ivresse et la violence : le vocabulaire ne les distingue pas"),
        hors("5.10", "les dommages découlant de la pollution graduelle", "rare ; le vocabulaire ne distingue pas la pollution"),
        hors("5.10", "Les dommages résultant d’actes collectifs de violence, d’émeute, de sabotage, de mouvement populaire, de "
             "conflit de travail ou de terrorisme.", "rare en responsabilité civile ; lu par l'événement pour les dommages aux biens")]},
    ["une garantie de vie privée au lieu de huit : seul ce qui a causé le dommage les distinguait (`origine_rc`)",
     "les exclusions : le tiers, la profession, le contrat, les biens gardés, les véhicules à moteur, le feu parti du "
     "bâtiment assuré, l'intention ; le reste hors décision, cité",
     "les seize variables proposées (âge, faute lourde, nombre d'enfants gardés…) : aucune retenue"])
