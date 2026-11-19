"""Relecture du lot A Foyer (2.2, 2.3, 2.4, 2.6, 2.8, 2.11, 2.12), rédigé en parallèle le 18 nov. (DEMARCHE 7.63).
Harmonise le vocabulaire entre propositions : chacune ignorait ce que proposaient les autres."""
import json, sys, copy
src, dst = sys.argv[1], sys.argv[2]

def f(v, x): return {"f": [v, x]}
def ou(*l): return {"ou": list(l)}
def et(*l): return {"et": list(l)}
def non(c): return {"non": c}
EXTERIEUR = ou(f("lieu", "jardin"), f("lieu", "terrasse"))          # « à l'extérieur » : 3 quater (7.58)
# « tout OBJET situé à l'extérieur » : les objets, pas le bâtiment (un balcon abîmé par des tuiles, g2-i11)
OBJET_EXTERIEUR = et(EXTERIEUR, non(f("bien", "element_batiment")))
BATIMENT_CLOS = f("construction_close", "non")

# Vocabulaire harmonisé : un nom, une question, des aides ; partagé par les articles qui l'emploient.
V = {
 "construction_delabree": {"variable": "construction_delabree", "valeurs": ["oui", "non"],
    "question": "La construction était-elle délabrée ou en cours de démolition ?",
    "aide": {"oui": "bâtiment en ruine, abandonné, en démolition", "non": "bâtiment en état normal"},
    "pourquoi": "exclusions 2.2-a, 2.3-a", "plus_proche": "travaux_construction : construire n'est pas démolir"},
 "residence_principale": {"variable": "residence_principale", "valeurs": ["oui", "non"],
    "question": "Ce bâtiment est-il votre logement principal ?",
    "aide": {"oui": "vous y habitez à l'année", "non": "seconde résidence, bien loué, dépendance"},
    "pourquoi": "réserve des exclusions 2.2-a, 2.3-a", "plus_proche": "aucune"},
 "construction_close": {"variable": "construction_close", "valeurs": ["oui", "non"],
    "question": "Le bâtiment ou l'annexe était-il entièrement clos et couvert ?",
    "aide": {"oui": "murs, toit, portes et fenêtres en place", "non": "toit ou mur manquant, ouvert sur un côté, chantier, carport"},
    "pourquoi": "exclusions 2.2-a, 2.3-a", "plus_proche": "fermeture : dit comment on ferme, pas si le bâtiment est clos"},
 "annexe_ancree_beton": {"variable": "annexe_ancree_beton", "valeurs": ["oui", "non"],
    "question": "L'annexe (abri, remise) est-elle fixée au sol par un ancrage en béton ?",
    "aide": {"oui": "posée sur une dalle ou des plots en béton", "non": "simplement posée sur le sol"},
    "pourquoi": "exclusion 2.2-a", "plus_proche": "aucune"},
 "alea_tempete": {"variable": "alea_tempete", "valeurs": ["vent", "grele", "neige_glace"],
    "question": "Quel phénomène a causé les dégâts : le vent, la grêle, ou le poids de la neige ou de la glace ?",
    "aide": {"vent": "tempête, rafales, arbre ou tuiles arrachés par le vent", "grele": "grêlons, impacts de grêle",
             "neige_glace": "toit ou auvent écrasé par la neige, la glace"},
    "pourquoi": "2.2 couvre trois aléas ; la définition de la tempête ne vaut que pour le vent", "plus_proche": "evenement = tempete : ne distingue pas les trois"},
 "vent_80_kmh_irm": None, "vent_dommages_voisins": None,       # repris de la proposition 2.2, aides ajoutées
 "risque_aggrave": {"variable": "risque_aggrave", "valeurs": ["oui", "non"],
    "question": "Les conditions particulières mentionnent-elles un « risque aggravé » pour les catastrophes naturelles ?",
    "aide": {"oui": "les conditions particulières renvoient au Bureau de Tarification", "non": "aucune mention de risque aggravé"},
    "pourquoi": "2.3 : la garantie est alors celle du Bureau de Tarification", "plus_proche": "aucune ; fait des conditions particulières"},
 "reparation_loi_particuliere": None, "batiment_construit_plus_18_mois_apres_classement": None,
 "extension_sol_avant_classement": None, "contenu_moins_10cm_sol": None,
 "cause_nucleaire": None, "graffiti_mur_exterieur": None,
 "conflit_du_travail": {"variable": "evenement", "valeurs": ["conflit_du_travail"], "question": "Que s'est-il passé ?",
    "aide": {"conflit_du_travail": "grève, lock-out, manifestation de travailleurs"},
    "pourquoi": "2.4", "plus_proche": "attentat : distinct"},
 "usage_professionnel": None, "garantie_fabricant": None, "cause_perte_alimentaire": None,
 "bien_2_6": {"variable": "bien", "valeurs": ["denrees_alimentaires", "appareil_informatique"], "question": "Quels biens ?",
    "aide": {"denrees_alimentaires": "aliments du frigo ou du congélateur", "appareil_informatique": "ordinateur, portable, tablette, imprimante"},
    "pourquoi": "2.6", "plus_proche": "electronique : ne distingue pas l'informatique"},
 "citerne": {"variable": "bien", "valeurs": ["citerne", "materiaux_construction"], "question": "Quels biens ?",
    "aide": {"citerne": "cuve à mazout, citerne", "materiaux_construction": "matériaux de construction pas encore posés : briques, ciment, tuiles sur le chantier"},
    "pourquoi": "2.8-b ; 2.2-a et 2.11 (« matériaux à pied d'œuvre »)", "plus_proche": "canalisation, element_batiment : déjà posés"},
 "bien_a_l_origine_sinistre": None, "periode_gel": None,
 "controle_citerne_conforme": {"variable": "controle_citerne_conforme", "valeurs": ["oui", "non"],
    "question": "La citerne avait-elle passé les contrôles réglementaires ?",
    "aide": {"oui": "contrôle périodique fait, attestation", "non": "contrôle non fait ou citerne non conforme"},
    "pourquoi": "2.8-b (et 2.5-a)", "plus_proche": "aucune"},
 "batiment_vacant_90j": None, "dispositifs_antivol_installes": None,
 "materiel_jardin_range": {"variable": "materiel_jardin_range", "valeurs": ["oui", "non"],
    "question": "Le matériel de jardin était-il rangé dans un local fermé à clé ?",
    "aide": {"oui": "tondeuse, outils rangés dans l'abri ou le garage fermé", "non": "laissés dehors ou dans un local ouvert"},
    "pourquoi": "2.11-a", "plus_proche": "fermeture : dit comment le local est fermé, pas si le matériel y était"},
 "auteur_locataire": {"variable": "auteur", "valeurs": ["locataire"], "question": "Qui est l'auteur ?",
    "aide": {"locataire": "la personne qui loue le logement, ou quelqu'un vivant chez elle"},
    "pourquoi": "2.11", "plus_proche": "tiers"},
 "merule_apres_prise_effet": None,
}

def reprendre(prop, nom):
    """Une variable gardée telle que la rédaction l'a proposée (avec son aide)."""
    for m in prop.get("vocabulaire_manquant", []):
        if m["variable"] == nom:
            return m
    raise KeyError(nom)

def ecrire(article, garder, nouveau_voc, journal, question=None):
    d = DOCS[article]; p = d["proposition"]
    voc = [reprendre(p, n) if V.get(n) is None and n in V else V[n] for n in garder]
    p["vocabulaire_manquant"] = voc
    d["meta"]["relecture"] = {"par": "auteur + Claude", "date": "2026-11-19", "modifications": journal}
    if question:
        d["meta"]["relecture"]["question_metier"] = question
    d.pop("controles", None)

DOCS = {a: json.load(open(f"{src}/{a}.json", encoding="utf-8")) for a in ["2.2", "2.3", "2.4", "2.6", "2.8", "2.11", "2.12"]}

# ---------- 2.2 Tempête, grêle, neige
p = DOCS["2.2"]["proposition"]; g = p["garanties"][0]
g["circonstances"] = [{"condition": {"si": [f("alea_tempete", "vent"), {"concept": "tempete"}]}, "article": "12/tempete",
    "texte": "L’action du vent mesurée à une vitesse de pointe d’au moins 80 km/h par la station de l’I.R.M. la plus proche du bâtiment"}]
X = []
for x in g["exclusions"]:
    t = x["texte"]
    if t.startswith("aux constructions délabrées"):
        x["condition"] = et(f("construction_delabree", "oui"), non(f("residence_principale", "oui")))
    elif t == "aux constructions non entièrement closes ou couvertes":
        continue                                            # doublon de la dernière, plus complète
    elif t.startswith("aux constructions non entièrement closes"):
        x["condition"] = BATIMENT_CLOS
    elif t.startswith("à tout objet situé à l'extérieur"):
        x["condition"] = OBJET_EXTERIEUR
    elif t.startswith("à tout objet situé dans une annexe"):
        x["condition"] = et(ou(f("lieu", "annexe"), f("lieu", "abri_jardin")), BATIMENT_CLOS)
    elif t.startswith("aux matériaux à pied"):
        x["condition"] = f("bien", "materiaux_construction"); x["portee"] = {"bien": "materiaux_construction"}; x["a_demander"] = False
    elif t.startswith("aux annexes contiguës"):
        x["condition"] = et(ou(f("lieu", "annexe"), f("lieu", "abri_jardin")), f("annexe_ancree_beton", "non"))
    X.append(x)
g["exclusions"] = X
ecrire("2.2", ["construction_delabree", "residence_principale", "construction_close", "annexe_ancree_beton", "alea_tempete",
               "vent_80_kmh_irm", "vent_dommages_voisins", "citerne"], None, [
  "la définition de la tempête (vent ≥ 80 km/h ou dégâts dans les 10 km) ne vaut que pour le vent : circonstance si(alea_tempete = vent, tempête) ; grêle et neige restent couvertes sans elle",
  "citation de la circonstance : la définition 12/tempete (au lieu de celle de la garantie)",
  "vocabulaire harmonisé avec 2.3 et 2.11 : construction_delabree, residence_principale, construction_close, bien = materiaux_construction ; « à l'extérieur » = jardin ou terrasse (règle 3 quater)",
  "« à tout objet situé à l'extérieur » : les objets, pas le bâtiment (bien ≠ element_batiment ; g2-i11, un balcon abîmé par des tuiles)",
  "exclusion « constructions non closes » en double : gardée une fois (la plus complète)",
  "matériaux à pied d'œuvre : portée limitée au bien"])

# ---------- 2.3 Catastrophes naturelles
p = DOCS["2.3"]["proposition"]; g = p["garanties"][0]
def sans_reconstruit(c):
    if isinstance(c, dict):
        for k in ("et", "ou"):
            if k in c:
                l = [sans_reconstruit(x) for x in c[k] if json.dumps(x) != json.dumps(non(f("bien_reconstruit_apres_sinistre", "oui")))]
                return l[0] if len(l) == 1 else {k: l}
        if "si" in c: return {"si": [sans_reconstruit(c["si"][0]), sans_reconstruit(c["si"][1])]}
        if "non" in c: return {"non": sans_reconstruit(c["non"])}
    return c
for x in g["exclusions"]:
    x["condition"] = sans_reconstruit(x["condition"])
    t = x["texte"]
    if t.startswith("aux constructions délabrées"):
        x["condition"] = et(f("construction_delabree", "oui"), non(f("residence_principale", "oui")))
    elif t.startswith("à tout objet situé à l'extérieur"):
        x["condition"] = OBJET_EXTERIEUR
    elif t.startswith("à tout objet situé dans une annexe"):
        x["condition"] = et(ou(f("lieu", "annexe"), f("lieu", "abri_jardin")), BATIMENT_CLOS)
    elif t.startswith("au contenu entreposé à moins de 10 cm"):
        x["condition"] = {"si": [ou({"concept": "inondation"}, {"concept": "debordement_ou_refoulement_egouts"}),
                                 et(f("lieu", "cave"), f("contenu_moins_10cm_sol", "oui"), f("occupation_partielle", "oui"))]}
aggrave = g["circonstances"][0]
g["circonstances"] = []
p["hors_decision"] = (p.get("hors_decision") or []) + [{"article": aggrave["article"], "texte": aggrave["texte"],
    "pourquoi": "un risque aggravé change de régime (Bureau de Tarification), il n'exclut pas : fait des conditions particulières, à lire avec elles"},
    {"article": "2.3-a", "texte": "Sont toutefois couverts, les dégâts causés aux biens ou parties de biens qui sont reconstruits ou reconstitués après un sinistre et qui correspondent à la valeur de reconstruction ou de reconstitution des biens avant le sinistre.",
    "pourquoi": "règle d'indemnisation des biens reconstruits, sans effet sur la question de couverture"}]
ecrire("2.3", ["construction_delabree", "residence_principale", "construction_close", "reparation_loi_particuliere",
               "batiment_construit_plus_18_mois_apres_classement", "extension_sol_avant_classement", "contenu_moins_10cm_sol"], None, [
  "vocabulaire harmonisé avec 2.2 : construction_delabree, residence_principale, construction_close ; « à l'extérieur » = jardin ou terrasse",
  "immeuble_appartements_multiples → occupation_partielle (variable existante, « un appartement dans un immeuble »)",
  "risque aggravé : hors décision (un autre régime, indiqué aux conditions particulières) ; en circonstance, il faisait poser la question à chaque catastrophe naturelle",
  "« à tout objet situé à l'extérieur » : les objets, pas le bâtiment (bien ≠ element_batiment)",
  "bien_reconstruit_apres_sinistre retiré de toutes les exclusions : la phrase vise l'indemnisation des biens reconstruits ; classée hors décision"])

# ---------- 2.4 Attentat, conflit du travail
p = DOCS["2.4"]["proposition"]; g = p["garanties"][0]
g["circonstances"] = []
p["hors_decision"] = [{**n, "pourquoi": "suspension de la garantie par arrêté ministériel : procédure de l'assureur, sans effet sur un sinistre déclaré"} for n in p.get("non_traduit") or []]
p["non_traduit"] = []
ecrire("2.4", ["conflit_du_travail", "cause_nucleaire", "graffiti_mur_exterieur"], None, [
  "circonstance « détruits par des participants ou par les mesures de l'autorité » retirée : c'est ce que l'événement attentat ou conflit du travail désigne ; la garder faisait poser la question à chaque déclaration",
  "evenement = conflit_du_travail accepté, avec son aide",
  "suspension par arrêté ministériel : hors décision"])

# ---------- 2.6 Électricité
p = DOCS["2.6"]["proposition"]
for x in p["exclusions_communes"]:
    if x["texte"].startswith("les dommages aux appareils électroniques"):
        x["condition"] = et(ou(f("bien", "electronique"), f("bien", "appareil_informatique")), f("usage_professionnel", "oui"))
        x["portee"] = {"bien": "appareil_informatique"}; x["a_demander"] = False
    elif x["texte"].startswith("ainsi que les dommages aux autres appareils"):
        x["condition"] = et(f("bien", "appareil_informatique"), non({"concept": "batiment"}), non(f("usage_professionnel", "oui")))
        x["portee"] = {"bien": "appareil_informatique"}; x["a_demander"] = False
    elif x["texte"].startswith("les dégâts tombant sous la garantie"):
        x["a_demander"] = False
p["definitions"] = [dd for dd in p["definitions"] if dd["concept"] != "materiel"]
ecrire("2.6", ["bien_2_6", "usage_professionnel", "garantie_fabricant", "cause_perte_alimentaire"], None, [
  "usage professionnel : la variable directement, pas le concept « materiel » (une définition du lexique qui ne dit pas l'usage)",
  "hors_batiment → non(concept batiment), déjà défini",
  "exclusions des appareils : portée limitée au bien (un congélateur et un ordinateur grillés : le congélateur reste couvert)",
  "garantie du fabricant : a_demander false ; c'est à l'assureur de l'établir (comme la corrosion en 2.7)"])

# ---------- 2.8 Mazout
p = DOCS["2.8"]["proposition"]; g = p["garanties"][0]
X = []
for x in g["exclusions"]:
    t = x["texte"]
    if t.startswith("les dégâts causés en cas de non-respect"):
        x["condition"] = f("controle_citerne_conforme", "non")
    elif t.startswith("les frais liés à l’assainissement"):
        p["hors_decision"] = (p.get("hors_decision") or []) + [{"article": x["article"], "texte": t, "pourquoi": "des frais exclus, pas un sinistre exclu : sans effet sur la couverture"}]
        continue
    X.append(x)
g["exclusions"] = X
ecrire("2.8", ["citerne", "bien_a_l_origine_sinistre", "periode_gel", "controle_citerne_conforme"], None, [
  "variable citerne → bien = citerne (valeur nouvelle de bien) ; respect_reglementation_citerne → controle_citerne_conforme (nom partagé avec 2.5)",
  "frais d'assainissement des terres : hors décision (des frais exclus, pas un sinistre exclu)",
  "prevention_gel : variable existante, désormais lue aussi pour le mazout (accepter étend « pour »)"])

# ---------- 2.11 Dégradations immobilières
p = DOCS["2.11"]["proposition"]; g = p["garanties"][0]
g["perimetre"][0] = ou({"concept": "vol"}, f("evenement", "vandalisme"))
O = []
for o in g["obligations"]:
    t = o["texte"]
    if t.startswith("fermer l’abri de jardin"):
        o["condition"] = {"si": [f("lieu", "abri_jardin"), f("serrure_surete", "oui")]}
    elif t.startswith("ranger le matériel de jardin"):
        o["condition"] = {"si": [f("bien", "mobilier_jardin"), f("materiel_jardin_range", "oui")]}
    O.append(o)
g["obligations"] = O
for x in g["exclusions"]:
    if x["texte"].startswith("aux matériaux à pied"):
        x["condition"] = et(f("bien", "materiaux_construction"), ou(EXTERIEUR, f("fermeture", "aucune")))
        x["portee"] = {"bien": "materiaux_construction"}; x["a_demander"] = False
p["evenements"] = ["vol", "vandalisme"]
ecrire("2.11", ["batiment_vacant_90j", "dispositifs_antivol_installes", "materiel_jardin_range", "auteur_locataire", "citerne"], None, [
  "evenement = malveillance retiré : le vandalisme est un acte de malveillance ; périmètre concept(vol) ou vandalisme (la définition 12/vol est employée, comme le demandait le contrôle)",
  "obligations de l'abri de jardin et du matériel de jardin : conditionnées (si lieu = abri de jardin ; si bien = mobilier de jardin) ; non conditionnées, elles s'appliquaient à tout sinistre",
  "bien = materiaux_pied_oeuvre → materiaux_construction (partagé avec 2.2) ; lieu = exterieur → jardin ou terrasse",
  "materiel_jardin_rangé → materiel_jardin_range (pas d'accent dans un nom de variable)"])

# ---------- 2.12 Mérule
ecrire("2.12", ["merule_apres_prise_effet"], None, ["acceptée telle quelle"])

for a, d in DOCS.items():
    open(f"{dst}/{a}.json", "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
print("ok", list(DOCS))
