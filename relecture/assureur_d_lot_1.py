"""Relecture du lot 1 de l'assureur D : les biens assurés (1.1, 1.2, 1.5) et les exclusions générales (titre IX,
« S25 »), rédigés par Mistral Large (consigne v12) le 20 nov. (DEMARCHE 7.89).

Ce que le modèle avait fait, et ce qui change :
- Les concepts. Il inventait `bien_immobilier`, `dependances`, `depreciation_collection`, et étendait un concept
  `bien` qui n'existe pas. Comme pour l'assureur A, deux concepts : `batiment`, les lieux assurés (le local
  d'habitation et ses dépendances, 1.1-a), et `contenu`, les biens mobiliers qui s'y trouvent (1.2-a).
- Les exclusions de biens (vérandas, éoliennes, piscines, véhicules, animaux…) excluaient « tout le sinistre » :
  elles n'excluent que le bien (portée `bien`). Elles visent toutes les garanties (un article sans garantie, v12).
- Les exceptions « sauf mention aux conditions particulières », « sauf Pack Piscine », « sauf formule
  Excellence » : la condition non lue (option, pack, formule) reste en réserve, elle n'est jamais demandée.
- 1.3 (objets de valeur, option) : l'exclusion des objets précieux en 1.2-b porte l'exception « sauf option » ;
  les limites sont des montants. 1.4 (véranda, option) : l'exclusion des vérandas en 1.1-b porte l'exception. Ni
  1.3 ni 1.4 ne sont acceptés seuls.
- 1.5 (villégiature) : une extension du lieu assuré, pour le contenu, dans un autre logement occupé en voyage, dans
  l'Union européenne, au Royaume-Uni, en Andorre ou à Monaco ; sans les objets précieux (1.5-b). Le contenu y est
  écrit en biens, pas par le concept `contenu`, défini à partir du `batiment` qu'elle étend (7.91).
- S25 : l'exclusion « tremblement de terre, éruption, raz-de-marée » excluait aussi l'événement « catastrophe
  naturelle », c'est-à-dire la garantie qu'elle épargne expressément ; aucune autre garantie traduite ne couvre ces
  phénomènes : hors décision. Les amendes et les armes illégales : sans effet sur les dommages aux biens. Aucune
  exclusion générale n'est demandée à l'assuré (« non ») : c'est à l'assureur de la prouver.

Usage : python relecture/assureur_d_lot_1.py  (corrige les propositions en place)"""
import json
from pathlib import Path

DOSSIER = Path(__file__).resolve().parents[1] / "regles" / "propositions" / "assureur-d-habitation-2026"


def f(v, x): return {"f": [v, x]}
def et(*l): return {"et": list(l)}
def ou(*l): return {"ou": list(l)}
def non(x): return {"non": x}
def concept(n): return {"concept": n}
def exc(cond, article, texte, demander=False):
    return {"condition": cond, "portee": "tout", "a_demander": demander, "article": article, "texte": texte}
def exc_biens(biens, article, texte, sauf=None):
    """Une exclusion par bien, qui n'exclut que ce bien (portée `bien`), avec l'exception en réserve."""
    return [{"condition": et(f("bien", b), non(sauf)) if sauf else f("bien", b), "portee": {"bien": b},
             "a_demander": False, "article": article, "texte": texte} for b in biens]
def hors(article, texte, pourquoi): return {"article": article, "texte": texte, "pourquoi": pourquoi}
def oui_non(var, question, pourquoi, aide_oui, aide_non):
    return {"variable": var, "valeurs": ["oui", "non"], "question": question, "pourquoi": pourquoi,
            "aide": {"oui": aide_oui, "non": aide_non}}


DEPENDANCES = [f("lieu", x) for x in ("cave", "garage", "annexe", "abri_jardin")]
VOC_BIENS = {"variable": "bien", "valeurs": ["veranda", "eolienne", "piscine"], "question": "Quels biens sont concernés ?",
             "pourquoi": "biens exclus en 1.1-b", "parent": {"veranda": "element_batiment", "eolienne": "element_batiment",
                                                             "piscine": "element_batiment"},
             "aide": {"veranda": "construction vitrée, close et couverte, accolée au logement",
                      "eolienne": "éolienne domestique",
                      "piscine": "piscine, spa, jacuzzi, ou leur abri"}}
VOC_FORMULE = {"variable": "formule", "valeurs": ["eco", "confort", "excellence"],
               "question": "Quelle formule est indiquée dans vos conditions particulières ?",
               "pourquoi": "les formules de l'assureur D", "aide": {"eco": "formule Eco", "confort": "formule Confort",
                                                                  "excellence": "formule Excellence"}}
VOC_PAYS = {"variable": "pays", "valeurs": ["royaume_uni", "andorre", "monaco"],
            "question": "Dans quel pays se trouvait le lieu du sinistre ?", "pourquoi": "1.5-a",
            "aide": {"royaume_uni": "au Royaume-Uni", "andorre": "en Andorre", "monaco": "à Monaco"}}


# Les garanties du titre I (« Dommages subis par vos biens », lot 2) : les biens exclus de 1.1 et 1.2 (véhicules,
# animaux, vérandas…) ne sont exclus que d'elles. Écrites « tous », ces exclusions refusaient aussi la responsabilité
# civile, où le bien endommagé est celui d'un tiers : la voiture rayée par le vélo de l'enfant (f-d09, 7.96).
DOMMAGES = ["incendie_evenements_annexes", "dommages_electriques", "tempete_grele_neige", "venues_eau_gel",
            "recherche_fuite", "debordement_cuves", "vol_vandalisme", "vol_cles", "deteriorations_immobilieres",
            "bris_glaces", "bris_glace_plus", "bris_glace_renforce", "contenu_congelateur", "catastrophes_naturelles",
            "relogement_catnat", "attentats", "emeutes", "intervention_secours"]


def ecrire(article, prop, modifications, cibles=None):
    if cibles:
        for x in prop.get("exclusions_communes", []):
            x["cibles"] = cibles
    chemin = DOSSIER / f"{article}.json"
    d = json.loads(chemin.read_text(encoding="utf-8"))
    base = {"evenements": [], "definitions": [], "garanties": [], "exclusions_communes": [], "extensions": [],
            "vocabulaire_manquant": [], "non_traduit": [], "hors_decision": []}
    d["proposition"] = base | prop
    d["meta"]["relecture"] = {"par": "auteur + Claude", "date": "2026-11-20", "modifications": modifications}
    d.pop("controles", None)
    chemin.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{article} : relu")


ecrire("1.1", {
    "definitions": [{"concept": "batiment", "condition": ou(f("lieu", "logement"), f("lieu", "grenier"),
                                                            f("lieu", "parties_communes"), *DEPENDANCES),
                     "article": "1.1-a", "texte": "votre local d’habitation, c’est-à-dire les parties immobilières des "
                     "bâtiments principaux d’habitation destinées à un usage privé"}],
    "exclusions_communes": [
        *exc_biens(["veranda"], "1.1-b", "les vérandas, sauf mention aux conditions particulières", f("option_veranda", "oui")),
        *exc_biens(["eolienne"], "1.1-b", "les éoliennes"),
        *exc_biens(["panneau_solaire"], "1.1-b", "les panneaux solaires et photovoltaïques si vous avez souscrit les "
                   "formules Eco et Confort", f("formule", "excellence")),
        *exc_biens(["piscine"], "1.1-b", "les piscines, spas et jacuzzi", f("pack_piscine", "oui")),
        *exc_biens(["plantation"], "1.1-b", "les plantations", f("pack_jardin", "oui")),
        exc(f("local_inoccupe_12_mois", "oui"), "1.1-b",
            "les locaux inoccupés ou inutilisés depuis plus de 12 mois consécutifs")],
    "vocabulaire_manquant": [
        VOC_BIENS, VOC_FORMULE,
        oui_non("option_veranda", "Vos conditions particulières mentionnent-elles la garantie « véranda » ?",
                "1.1-b, 1.4 : option", "la véranda est assurée aux conditions particulières", "elle ne l'est pas"),
        oui_non("pack_piscine", "Avez-vous souscrit le Pack Piscine ?", "1.1-b : pack optionnel",
                "le Pack Piscine figure aux conditions particulières", "il n'y figure pas"),
        oui_non("pack_jardin", "Avez-vous souscrit le Pack Jardin ?", "1.1-b : pack optionnel",
                "le Pack Jardin figure aux conditions particulières", "il n'y figure pas"),
        oui_non("local_inoccupe_12_mois", "Les locaux étaient-ils inoccupés ou inutilisés depuis plus de 12 mois ?",
                "1.1-b", "personne n'y vivait ni ne les utilisait depuis plus d'un an", "ils étaient occupés ou utilisés")],
    "hors_decision": [
        hors("1.1-b", "les chemins, les courts de tennis", "biens extérieurs hors des lieux assurés (`batiment`)"),
        hors("1.1-b", "les appareils électroménagers, ces biens sont garantis au titre des « biens mobiliers »",
             "un renvoi : ils font partie du contenu (1.2)"),
        hors("1.1-b", "les aires cimentées, goudronnées, dallées ou gravillonnées",
             "aménagements extérieurs, hors des lieux assurés"),
        hors("1.1-b", "les clôtures végétales", "aménagements extérieurs, hors des lieux assurés"),
        hors("1.1-b", "les serres d’une superficie de plus de 5 m2", "le vocabulaire ne distingue pas la taille d'une serre"),
        hors("1.1-a", "les clôtures, murs d’enceinte, panneaux de signalisation, barrières et portails d’accès",
             "le vocabulaire ne distingue pas une clôture d'un autre élément du bâtiment")]},
    ["concept `batiment` (lieux : le logement et ses dépendances), au lieu de `bien_immobilier` et `dependances`",
     "exclusions de biens en portée `bien`, exceptions (option, pack, formule) en réserve, jamais demandées",
     "chemins, courts de tennis, aires aménagées, électroménager : hors décision"], DOMMAGES)

ecrire("1.2", {
    "definitions": [{"concept": "contenu", "condition": et(ou(*[f("bien", x) for x in (
        "mobilier", "electronique", "objet_divers", "velo", "bijoux", "valeurs", "mobilier_jardin")]), concept("batiment")),
        "article": "1.2-a", "texte": "Tous les objets d’usage courant et les vêtements vous appartenant ou qui vous sont "
        "confiés ou appartenant à toute personne résidant avec vous ou en simple visite, contenus à l’intérieur du local "
        "d’habitation et des dépendances assurés"}],
    "exclusions_communes": [
        exc(et(ou(*DEPENDANCES), f("formule", "eco")), "1.2-b",
            "les biens mobiliers se trouvant dans les dépendances si vous avez souscrit la formule Eco"),
        *exc_biens(["bijoux", "valeurs"], "1.2-b", "les objets précieux, les espèces, titres et valeurs, les objets de "
                   "valeur désignés", f("option_objets_valeur", "oui")),
        *exc_biens(["vehicule_moteur", "remorque"], "1.2-b", "les véhicules terrestres à moteur (y compris les vélos "
                   "électriques circulant à plus de 25 km/h et les engins de déplacement personnel motorisés), les "
                   "remorques, les caravanes, les véhicules aériens"),
        *exc_biens(["animal", "plantation"], "1.2-b", "les animaux et les végétaux")],
    "vocabulaire_manquant": [VOC_FORMULE, oui_non(
        "option_objets_valeur", "Vos conditions particulières mentionnent-elles la garantie « objets de valeur » ?",
        "1.2-b, 1.3 : option", "la garantie objets de valeur est souscrite", "elle ne l'est pas")],
    "hors_decision": [
        hors("1.2-a", "le fauteuil roulant automoteur ou non est assuré pour les garanties mentionnées dans vos conditions "
             "particulières et en cas de bris accidentel en tous lieux", "un bien particulier, ses garanties sont aux conditions particulières"),
        hors("1.2-a", "les vins, alcools et spiritueux en bouteille entreposés dans le local d’habitation et les dépendances "
             "assurés", "font partie du contenu ; le livre de cave est une preuve, pas une condition de couverture"),
        hors("1.2-b", "les timbres et les collections de timbres, ces biens sont garantis au titre de la garantie "
             "optionnelle « objets de valeur » si elle est souscrite", "le vocabulaire ne distingue pas les timbres"),
        hors("1.2-b", "les bateaux de plus de 5,5 m de longueur ou avec un moteur de plus de 6 CV", "pas de bateau dans le vocabulaire"),
        hors("1.2-b", "le matériel professionnel lié à votre activité professionnelle se trouvant dans les dépendances",
             "le vocabulaire ne distingue pas le matériel professionnel"),
        hors("1.2-b", "les armes détenues illégalement", "rare ; le vocabulaire ne distingue pas les armes"),
        hors("1.2-b", "la dépréciation des bouteilles par suite du décollement ou détérioration des étiquettes",
             "un montant, pas la couverture"),
        hors("1.2-b", "les dommages résultant de la manutention et/ou de la casse des bouteilles",
             "le vocabulaire ne distingue pas les bouteilles"),
        hors("1.2-b", "les vols, tentatives de vol ou actes de vandalisme dont seraient auteurs ou complices les membres de votre famille", "exclusion propre au fauteuil roulant, hors décision comme lui"),
        hors("1.2-b", "la panne du fauteuil roulant automoteur", "exclusion propre au fauteuil roulant, hors décision comme lui"),
        hors("1.2-b", "entrant dans le cadre des engagements légaux ou contractuels du vendeur", "exclusion propre au fauteuil roulant, hors décision comme lui"),
        hors("1.2-b", "régulièrement pris en charge dans un contrat d’entretien ou de maintenance", "exclusion propre au fauteuil roulant, hors décision comme lui"),
        hors("1.2-b", "dus à des défauts existants et connus de vous au moment de la souscription du présent contrat", "exclusion propre au fauteuil roulant, hors décision comme lui"),
        hors("1.2-b", "dus à une utilisation non conforme aux prescriptions du constructeur", "exclusion propre au fauteuil roulant, hors décision comme lui"),
        hors("1.2-b", "causés par l’usure, le défaut d’entretien", "exclusion propre au fauteuil roulant, hors décision comme lui"),
        hors("1.2-b", "résultant d’interventions effectuées par un non professionnel de la réparation du fauteuil roulant automoteur", "exclusion propre au fauteuil roulant, hors décision comme lui"),
        hors("1.2-b", "dus à l’humidité ou à la condensation", "exclusion propre au fauteuil roulant, hors décision comme lui"),
        hors("1.2-b", "les rayures, les écaillements, les égratignures lorsqu’elles sont sans influence sur le fonctionnement du fauteuil roulant automoteur ou non", "exclusion propre au fauteuil roulant, hors décision comme lui")]},
    ["concept `contenu` : les biens mobiliers, dans les lieux assurés (`batiment`)",
     "exclusions de biens en portée `bien` ; objets précieux exclus sauf l'option « objets de valeur » (1.3)",
     "fauteuil roulant, bouteilles, bateaux, timbres, matériel professionnel, armes : hors décision"], DOMMAGES)

ecrire("1.5", {
    "extensions": [{"concept": "batiment", "condition": et(
        f("sejour_temporaire", "oui"), f("lieu", "autre_batiment"),
        # Les biens du contenu, écrits en faits : `contenu` est défini « dans le `batiment` », que cette extension
        # élargit ; le concept ici faisait boucler le moteur (7.91).
        ou(*[f("bien", x) for x in ("mobilier", "electronique", "objet_divers", "velo", "mobilier_jardin")]),
        non(ou(f("bien", "bijoux"), f("bien", "valeurs"))),
        ou(*[f("pays", p) for p in ("france", "belgique", "luxembourg", "allemagne", "autre_ue", "royaume_uni", "andorre", "monaco")])),
        "article": "1.5-a", "texte": "Les objets que vous emportez avec vous dans les différents locaux d’habitation, y "
        "compris les chambres d’hôtel, que vous occupez lors de voyages ou de vacances dans les pays de l’Union européenne, "
        "au Royaume-Uni de Grande-Bretagne et d’Irlande du Nord, dans les principautés d’Andorre et de Monaco"}],
    "vocabulaire_manquant": [VOC_PAYS],
    "hors_decision": [
        hors("1.5-b", "les dommages occasionnés en cours de transport", "hors d'un logement : l'extension ne joue pas"),
        hors("1.5-b", "les dommages occasionnés dans une caravane, un bateau, un camping-car ou une tente de camping",
             "pas un « local d'habitation » occupé en voyage : l'extension ne joue pas"),
        hors("1.5-b", "les biens contenus dans une résidence dont vous avez la jouissance permanente",
             "pas un séjour temporaire"),
        hors("1.5-b", "les objets précieux, d’art et les fourrures, les timbres, les collections de timbres, la "
             "dépréciation des collections", "les objets précieux sont retirés de l'extension ; le reste n'est pas "
             "distingué par le vocabulaire")]},
    ["une extension du lieu assuré pour le contenu, en voyage, dans l'UE, au Royaume-Uni, en Andorre, à Monaco",
     "sans les objets précieux (1.5-b)"])

ecrire("S25", {
    "exclusions_communes": [
        # « par vous ou par un complice » : le voleur ou le vandale agit exprès, mais ce n'est pas l'assuré. Le petit
        # modèle lisait « intentionnel = oui » pour chaque vandalisme ; l'exclusion refusait (7.94).
        exc(ou(et(f("intentionnel", "oui"), non(f("auteur", "tiers"))),
               et(f("participation_rixe", "oui"), non(f("legitime_defense", "oui")))), "S25",
            "les dommages causés intentionnellement ou frauduleusement par vous ou par un complice, ou résultant de votre "
            "ou de sa participation à une action violente ou à une rixe (sauf légitime défense)"),
        # Le gel d'une conduite faute de l'avoir vidée relève des mesures de prévention (4.2 : une réduction de
        # l'indemnité), pas du défaut d'entretien ; le petit modèle lisait « manque_entretien » et refusait (f-d04, 7.95).
        # Une fuite lue sans plus de précision peut être du gel (valeur parente) : alors l'exclusion est à demander.
        exc(et(f("manque_entretien", "oui"), ou(non(f("evenement", "degat_eaux")), non(f("cause_eau", "gel")))), "S25",
            "ceux qui résultent directement d’un défaut de réparation ou d’entretien indispensables vous incombant et dont "
            "vous aviez connaissance", demander=True),
        exc(et(ou(f("cause_guerre", "oui"), f("cause_nucleaire", "oui")), non(f("evenement", "attentat"))), "S25",
            "de la guerre civile ou étrangère, - de tout combustible, produit ou déchet radioactif, de tout engin destiné à "
            "irradier ou à exploser par modification du noyau de l’atome ainsi que leur décontamination, sauf pour les "
            "dommages matériels directs causés par un attentat ou un acte de terrorisme")],
    "vocabulaire_manquant": [
        oui_non("participation_rixe", "Les dommages résultent-ils de votre participation à une rixe ou à une action violente ?",
                "S25", "l'assuré a pris part à une bagarre ou à une action violente", "non"),
        oui_non("legitime_defense", "Était-ce de la légitime défense ?", "S25", "l'assuré se défendait", "non"),
        oui_non("cause_guerre", "Les dommages résultent-ils d'une guerre ?", "S25", "guerre civile ou étrangère", "non"),
        oui_non("cause_nucleaire", "Les dommages sont-ils dus à une matière radioactive ou nucléaire ?", "S25",
                "combustible, déchet ou engin radioactif ou nucléaire", "non")],
    "hors_decision": [
        hors("S25", "les paiements des amendes auxquelles vous pourriez être condamné", "pas un dommage aux biens"),
        hors("S25", "les dommages causés par les armes détenues illégalement", "rare ; le vocabulaire ne distingue pas les armes"),
        hors("S25", "les dommages occasionnés par un tremblement de terre, une éruption volcanique, un raz-de-marée ou "
             "cataclysme naturel", "aucune garantie traduite hors « catastrophes naturelles », que l'exclusion épargne"),
        hors("S25", "Les effets du contrat seront suspendus", "la vie du contrat, pas un sinistre")]},
    ["intentionnel ou rixe, défaut d'entretien connu, guerre et nucléaire (sauf attentat) : jamais demandés",
     "tremblement de terre : retiré (il excluait aussi la garantie catastrophes naturelles) ; amendes, armes : hors décision"])
