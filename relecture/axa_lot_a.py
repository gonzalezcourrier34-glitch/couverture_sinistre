"""Relecture du lot A AXA (3.1.1, 3.1.2, 3.1.3, 3.1.4, 3.1.5, 3.1.7, 3.2.1, 3.2.2), rédigé en parallèle le 19 nov.
(DEMARCHE 7.65). Chaque modification est tracée dans meta.relecture de la proposition."""
import json, sys
src, dst = sys.argv[1], sys.argv[2]

def f(v, x): return {"f": [v, x]}
def ou(*l): return {"ou": list(l)}
def et(*l): return {"et": list(l)}
def non(c): return {"non": c}
def si(a, b): return {"si": [a, b]}
EXTERIEUR = ou(f("lieu", "jardin"), f("lieu", "terrasse"))
OBJET_EXTERIEUR = et(EXTERIEUR, non(f("bien", "element_batiment")))
DOCS = {a: json.load(open(f"{src}/{a}.json", encoding="utf-8")) for a in ["3.1.1", "3.1.2", "3.1.3", "3.1.4", "3.1.5", "3.1.7", "3.2.1", "3.2.2"]}
CLAUSES = json.load(open(f"{src}/_clauses.json", encoding="utf-8"))

def option(art_clause, var, nom):
    """« applicables si les conditions particulières mentionnent la garantie X » : une réserve, pas une question."""
    return {"condition": f(var, "non"), "portee": "tout", "a_demander": True, "article": art_clause,
            "texte": CLAUSES[art_clause]}

def var(nom, valeurs, question, aide, pourquoi, proche="aucune", **extra):
    return {"variable": nom, "valeurs": valeurs, "question": question, "aide": aide, "pourquoi": pourquoi, "plus_proche": proche, **extra}

def opt_var(nom, garantie):
    return var(nom, ["oui", "non"], f"Vos conditions particulières mentionnent-elles la garantie « {garantie} » ?",
               {"oui": "la garantie figure aux conditions particulières", "non": "elle n'y figure pas"},
               "garantie optionnelle : réserve tant que les conditions particulières ne sont pas lues",
               "aucune ; fait des conditions particulières")

def regler(excls, regles):
    """Applique, par début de texte, une condition, une portée, a_demander, ou le retrait (None) d'une exclusion."""
    garder = []
    for x in excls:
        for debut, r in regles.items():
            if x["texte"].lstrip("n ").startswith(debut):
                if r is None: x = None
                else: x.update(r)
                break
        if x is not None: garder.append(x)
    return garder

def hors(p, art, texte, pourquoi):
    p.setdefault("hors_decision", []).append({"article": art, "texte": texte, "pourquoi": pourquoi})

def fin(a, voc, journal, question=None):
    d = DOCS[a]
    d["proposition"]["vocabulaire_manquant"] = voc
    d["meta"]["relecture"] = {"par": "auteur + Claude", "date": "2026-11-19", "modifications": journal}
    if question: d["meta"]["relecture"]["question_metier"] = question
    d.pop("controles", None)

PORTEE_BIEN = lambda b: {"portee": {"bien": b}, "a_demander": False}
FAIT_ASSUREUR = {"a_demander": False}          # à l'assureur de l'établir : inconnu, il ne joue pas

V_STATUT = var("statut_logement", ["proprietaire", "locataire"], "Êtes-vous propriétaire ou locataire du bâtiment ?",
               {"proprietaire": "vous êtes propriétaire du logement ou de la maison", "locataire": "vous louez le logement"},
               "3.1.1.2.5 (vandalisme : l'assuré est propriétaire), 3.1.5 (vitrages isolants : sauf si l'assuré est locataire)",
               "proprietaire : dit à qui sont les biens, pas qui possède le bâtiment")
V_CATA = var("catastrophe", ["tremblement_terre", "inondation", "ruissellement", "glissement_terrain"],
             "Quel phénomène naturel a causé les dégâts ?",
             {"tremblement_terre": "séisme, tremblement de terre et ses répliques", "inondation": "crue, débordement d'un cours d'eau, refoulement d'égouts",
              "ruissellement": "eau de pluies torrentielles qui ruisselle faute d'absorption du sol", "glissement_terrain": "glissement ou affaissement de terrain"},
             "AXA distingue deux garanties optionnelles : tremblement de terre (3.2.1) et pluies et inondations (3.2.2)",
             "cause_eau = inondation : ne dit ni le séisme ni le glissement")

# ---------------------------------------------------------------- 3.1.1 Incendie et périls assimilés
p = DOCS["3.1.1"]["proposition"]; G = {g["id"]: g for g in p["garanties"]}
G["incendie_base"]["perimetre"] = [ou(f("evenement", "incendie"), f("evenement", "explosion"), f("evenement", "foudre"),
                                      et(f("evenement", "electricite"), f("bien", "animal")), f("evenement", "fumee"),
                                      et(ou(f("evenement", "incendie"), f("evenement", "autre")), f("chaleur_sans_feu", "oui"))),
                                   {"concept": "batiment_designe"}]
G["incendie_base"]["circonstances"][0]["condition"] = si(f("evenement", "incendie"), {"concept": "incendie"})
G["decongelation"]["perimetre"] = [f("bien", "denrees_alimentaires")]
G["linge"]["perimetre"] = [f("bien", "objet_divers"), f("lieu", "logement")]
G["heurt"]["exclusions"] = regler(G["heurt"]["exclusions"], {
    "les dégâts ne résultant pas directement": FAIT_ASSUREUR,
    "les dégâts causés au bâtiment désigné en cas de déménagement": FAIT_ASSUREUR,
    "les dégâts causés par la grêle": FAIT_ASSUREUR})
g = G["degradations_vol"]
g["perimetre"] = [f("evenement", "vol"), f("bien", "element_batiment")]
g["exclusions"] = regler(g["exclusions"], {"les dommages ou le vol des biens se trouvant à l'extérieur": {"condition": OBJET_EXTERIEUR}})
g["exclusions"].append({"condition": f("occupation_irreguliere", "oui"), "portee": "tout", "a_demander": True, "article": "3.1.1.2",
                        "texte": "aux dégradations immobilières causées à l’occasion d’un vol ou d’une tentative de vol dans les locaux à occupation régulière"})
g = G["vandalisme"]
g["perimetre"] = [f("evenement", "vandalisme"), f("bien", "element_batiment"), {"concept": "batiment_designe"}]
for cond, t in [(f("statut_logement", "locataire"), "l’Assuré est propriétaire du bâtiment"),
                (f("occupation_irreguliere", "oui"), "le bâtiment fait l’objet d’une occupation régulière"),
                (f("travaux_construction", "oui"), "le bâtiment n’est pas en cours de construction, ni de transformation, ni de rénovation")]:
    g["exclusions"].append({"condition": cond, "portee": "tout", "a_demander": True, "article": "3.1.1.2", "texte": t})
G["attentats"]["perimetre"] = [ou(f("evenement", "attentat"), f("evenement", "conflit_du_travail")), {"concept": "batiment_designe"}]
p["exclusions_communes"] = (p.get("exclusions_communes") or []) + [option("3.1.1", "option_incendie", "incendie et périls assimilés")]
fin("3.1.1", [opt_var("option_incendie", "incendie et périls assimilés"),
              var("evenement", ["heurt"], "Que s'est-il passé ?", {"heurt": "un véhicule, un arbre ou un objet a percuté le bâtiment ou les biens"},
                  "3.1.1.2.3", "bris : la casse, pas le choc", parent=None),
              var("demenagement", ["oui", "non"], "Les dégâts sont-ils survenus pendant un déménagement ?",
                  {"oui": "en déménageant, en transportant les meubles", "non": "hors de tout déménagement"}, "3.1.1.2.3"),
              var("choc_deux_corps_durs", ["oui", "non"], "Les dégâts viennent-ils directement d'un choc entre deux objets durs ?",
                  {"oui": "percuté, cogné par un objet dur", "non": "rayé, frotté, mouillé, sans choc"}, "3.1.1.2.3"),
              V_STATUT], [
  "« applicables si les conditions particulières mentionnent la garantie » : réserve (option_incendie), retirée du périmètre où elle faisait poser une question à chaque incendie",
  "la définition de l'incendie (flammes qui se propagent) ne vaut que pour l'incendie : circonstance si(incendie, …) ; l'explosion, la foudre, la fumée n'en dépendent pas",
  "électrocution : seulement des animaux (3.1.1.1.4) ; « action subite de la chaleur » : pour un incendie ou un autre événement, pas pour un vol (le banc posait la question pour un cambriolage, axa-v04)",
  "dégradations immobilières à l'occasion d'un vol : limitées aux éléments du bâtiment ; sans cela, tout vol de contenu était couvert par l'article incendie",
  "« à l'extérieur du bâtiment » = jardin ou terrasse, objets et non le bâtiment (règle 3 quater) ; la voie publique tuait le vol par agression de 3.1.6 (axa-v07)",
  "vandalisme : « l'assuré est propriétaire » n'est pas `proprietaire = assure` (à qui sont les biens) : variable statut_logement ; les trois conditions en réserves",
  "occupation régulière, choc entre corps durs, déménagement : des faits que l'assureur établit, pas des questions à chaque sinistre",
  "attentat : « auteur = tiers » retiré du périmètre (inconnu, il faisait demander qui sont les terroristes)"])

# ---------------------------------------------------------------- 3.1.2 Tempête, grêle, neige
p = DOCS["3.1.2"]["proposition"]; g = p["garanties"][0]
g["circonstances"] = [{"condition": si(f("alea_tempete", "vent"), {"concept": "tempete"}), "article": "3.1.2.1", "texte": "la tempête (à partir de 80km/h)"}]
g["exclusions"] = regler(g["exclusions"], {
    "causés à tout objet non fixé": {"condition": OBJET_EXTERIEUR},
    "causés aux objets suivants fixés": FAIT_ASSUREUR,
    "piscines": FAIT_ASSUREUR,
    "constructions totalement ou partiellement ouvertes": FAIT_ASSUREUR, "constructions en démolition": FAIT_ASSUREUR,
    "constructions dont les murs": FAIT_ASSUREUR, "constructions dont la toiture": FAIT_ASSUREUR,
    "causés par la pression de la neige": FAIT_ASSUREUR, "causés par un choc thermique": FAIT_ASSUREUR, "d'ordre purement": FAIT_ASSUREUR,
    "Ne sont toutefois pas couverts les dommages n résultant d'un défaut": FAIT_ASSUREUR})
p["exclusions_communes"] = (p.get("exclusions_communes") or []) + [option("3.1.2", "option_tempete", "tempête, grêle, pression de la neige ou de la glace")]
voc = [x for x in p["vocabulaire_manquant"]] + [opt_var("option_tempete", "tempête, grêle, pression de la neige ou de la glace")]
fin("3.1.2", voc, [
  "la définition de la tempête (80 km/h) ne vaut que pour le vent : circonstance si(vent, tempête) ; la seconde circonstance (grêle ou neige) faisait refuser le vent : retirée",
  "« applicables si… » : réserve (option_tempete)",
  "« objet non fixé à l'extérieur » : jardin ou terrasse, objets (règle 3 quater)",
  "matériaux légers, choc thermique, esthétique, déformation sans perte d'étanchéité, entretien : à l'assureur de l'établir"])

# ---------------------------------------------------------------- 3.1.3 Dégâts électriques
p = DOCS["3.1.3"]["proposition"]; g = p["garanties"][0]
g["perimetre"] = [f("evenement", "electricite"), {"concept": "batiment_designe"}]
X = []
for x in g["exclusions"]:
    t = x["texte"]
    if t.startswith(("les frais de recherche", "la reconstitution des données", "les dégâts assurables par d'autres")):
        hors(p, x["article"], t, "des frais ou une règle de cumul entre garanties : sans effet sur la question de couverture"); continue
    if t.startswith("les équipements informatiques et bureautiques"):
        x.update(condition=et(f("bien", "appareil_informatique"), f("usage_professionnel", "oui")), **PORTEE_BIEN("appareil_informatique"))
    elif t.startswith("les dégâts au contenu des appareils électroménagers"):
        x.update(condition=f("bien", "denrees_alimentaires"), **PORTEE_BIEN("denrees_alimentaires"))
    elif t.startswith(("les dégâts à tous supports", "les dégâts tombant sous la garantie", "les dégâts aux appareils ou installations électriques constituant",
                       "les pertes ou dommages qui sont la conséquence directe")):
        x.update(FAIT_ASSUREUR)
    X.append(x)
g["exclusions"] = X
p["exclusions_communes"] = (p.get("exclusions_communes") or []) + [option("3.1.3", "option_degats_electriques", "dégâts électriques")]
voc = [x for x in p["vocabulaire_manquant"] if x["variable"] not in ("garantie_degats_electriques_souscrite", "cause_domotique", "reconstitution_donnees",
                                                                      "autre_division_assurable", "contenu_appareil_electromenager", "equipement_bureautique")]
voc.append(opt_var("option_degats_electriques", "dégâts électriques"))
fin("3.1.3", voc, [
  "« applicables si… souscrite » : réserve (option_degats_electriques), retirée du périmètre",
  "frais de recherche (domotique), reconstitution des données, cumul avec d'autres divisions : hors décision",
  "équipement bureautique → bien = appareil_informatique (l'aide dit « imprimante ») ; contenu des électroménagers → bien = denrees_alimentaires ; portée limitée au bien",
  "garantie du fabricant, marchandises, supports de données, usure et fonctionnement défectueux : à l'assureur de l'établir"])

# ---------------------------------------------------------------- 3.1.4 Dégâts des eaux
p = DOCS["3.1.4"]["proposition"]; g = p["garanties"][0]
g["circonstances"][0]["condition"] = ou(f("cause_eau", "fuite_installation"), f("cause_eau", "infiltration_toiture"), f("cause_eau", "debordement_aquarium"))
g["obligations"] = [o for o in g["obligations"] if o.get("condition")]
for o in g["obligations"]:
    if o["condition"] == f("periode_gel", "oui"):
        o["condition"] = si(f("periode_gel", "oui"), f("prevention_gel", "oui")); o["lien_causal"] = True
X = []
for x in g["exclusions"]:
    t = x["texte"].lstrip("n ")
    if t.startswith("à la toiture du bâtiment"):
        x.update(condition=f("bien", "toiture"), **PORTEE_BIEN("toiture"))
    elif x["article"] == "3.1.4.2.2" or t.startswith("aux conduites"):
        x["article"] = "3.1.4.2"
        x["texte"] = next(s for s in CLAUSES["3.1.4.2_items"] if s.replace(" ", "").startswith("auxconduites"))
        x.update(condition=f("bien", "canalisation"), **PORTEE_BIEN("canalisation"))
    elif t.startswith("par les dommages causés par un objet non relié"):
        x["condition"] = f("cause_eau", "debordement_recipient")
    elif t.startswith("lorsque le bâtiment désigné est en cours de construction"):
        x["condition"] = et(f("travaux_construction", "oui"), non(f("lien_causal_travaux", "non")))
    elif t.startswith(("par l’hygrométrie", "par des champignons", "par un défaut de réparation", "par la condensation", "par des conduites, installations et appareils apparents")):
        x.update(FAIT_ASSUREUR)
    X.append(x)
g["exclusions"] = X
for n in p.get("non_traduit") or []:
    hors(p, n["article"], n["texte"], "extensions aux frais de recherche de fuite et à l'huile minérale : des frais, sans effet sur la question de couverture")
p["non_traduit"] = []
p["exclusions_communes"] = (p.get("exclusions_communes") or []) + [option("3.1.4", "option_degats_eaux", "dégâts des eaux")]
voc = [x for x in p["vocabulaire_manquant"] if x["variable"] in ("canalisation_encastree", "installation_hydraulique_exterieure")]
voc += [opt_var("option_degats_eaux", "dégâts des eaux"),
        var("bien", ["toiture"], "Quels biens ?", {"toiture": "le toit lui-même, les tuiles, la couverture, son étanchéité"}, "3.1.4.2", "element_batiment", parent="element_batiment")]
fin("3.1.4", voc, [
  "circonstance : fuite d'installation, infiltration par la toiture ou les terrasses, aquarium ; « infiltration_exterieure » (portes, fenêtres, murs) est exclue plus bas, elle ne peut pas être aussi une condition",
  "obligation gel : si période de gel, alors prévention (comme Foyer) ; l'obligation sans condition retirée",
  "toiture : valeur bien = toiture (parent : élément du bâtiment), portée limitée au bien ; sans cela, tout le bâtiment était exclu",
  "« aux conduites… à l'origine du sinistre » : citation exacte, portée canalisation",
  "objet non relié à l'installation : cause_eau = debordement_recipient (l'aquarium est une autre valeur)",
  "lien_causal_travaux_eaux → lien_causal_travaux (variable acceptée avec 3.1.6)",
  "« applicables si… » : réserve (option_degats_eaux) ; frais de recherche et huile minérale : hors décision"])

# ---------------------------------------------------------------- 3.1.5 Bris de vitrages
p = DOCS["3.1.5"]["proposition"]; g = p["garanties"][0]
g["circonstances"][0]["condition"] = si(f("type_dommage", "opacification_ou_perte_etancheite"),
                                        non(ou(f("garantie_fabricant", "oui"), f("statut_logement", "locataire"))))
g["exclusions"] = regler(g["exclusions"], {
    "aux parties vitrées du matériel multimédia": PORTEE_BIEN("appareil_audiovisuel"),
    "aux verres optiques": PORTEE_BIEN("verre_optique"),
    "aux châssis de couche": {"condition": f("bien", "enseigne"), **PORTEE_BIEN("enseigne")},
    "aux objets en verre": PORTEE_BIEN("objet_verre_non_vitre"),
    "au bâtiment désigné lorsqu’il est en cours": {"condition": et(f("travaux_construction", "oui"), non(f("lien_causal_travaux", "non")))},
    "aux vitrages relevant des parties communes": {"condition": et(f("lieu", "parties_communes"), f("occupation_partielle", "oui"))},
    "par un défaut de réparation": FAIT_ASSUREUR})
p["exclusions_communes"] = (p.get("exclusions_communes") or []) + [option("3.1.5", "option_bris_vitrages", "bris de vitrages")]
voc = [var("bien", ["appareil_electromenager", "verre_optique", "enseigne"], "Quels biens ?",
           {"appareil_electromenager": "four, frigo, lave-linge : leurs parties vitrées", "verre_optique": "lunettes, verres de vue",
            "enseigne": "enseigne, panneau publicitaire"}, "3.1.5", "objet_divers", parent={"appareil_electromenager": "objet_divers", "verre_optique": "objet_divers", "enseigne": "element_batiment"}),
       V_STATUT, opt_var("option_bris_vitrages", "bris de vitrages")]
voc += [x for x in p["vocabulaire_manquant"] if x["variable"] in ("vitrage_en_deplacement", "cause_projection_debris")]
fin("3.1.5", voc, [
  "statut_assure_batiment → statut_logement (partagé avec 3.1.1) ; occupant partiel → occupation_partielle (variable existante)",
  "exclusions de biens (lunettes, objets en verre, enseignes, multimédia) : portée limitée au bien ; châssis de couche : la valeur proposée désignait un cadre de lit, retirée",
  "lien_causal_travaux_sinistre → lien_causal_travaux ; parties communes : quand l'assuré n'occupe qu'une partie du bâtiment",
  "« applicables si… » : réserve (option_bris_vitrages) ; valeurs nouvelles rattachées à leur parent"])

# ---------------------------------------------------------------- 3.1.7 Matériel multimédia
p = DOCS["3.1.7"]["proposition"]; G = {g["id"]: g for g in p["garanties"]}
MM = ou(f("bien", "electronique"), f("bien", "equipement_alarme_surveillance"), f("bien", "equipement_domotique"))
G["materiel_multimedia_bris"]["perimetre"] = [f("evenement", "bris"), MM]
c_alarme = G["materiel_multimedia_bris"]["circonstances"].pop(0)
G["materiel_multimedia_bris"]["exclusions"].append({"condition": et(f("bien", "equipement_alarme_surveillance"), f("mise_en_exploitation_satisfaction", "non")),
    "portee": {"bien": "equipement_alarme_surveillance"}, "a_demander": False, "article": c_alarme["article"], "texte": c_alarme["texte"]})
o = G["materiel_multimedia_bris"]["obligations"][0]
o["condition"] = si(f("lieu", "vehicule"), et(f("vehicule_ferme_cle", "oui"), non(f("materiel_laisse_en_vue", "oui"))))
o["article"] = "3.1.7.4"; o["exception"] = None
G["materiel_multimedia_vol"]["obligations"] = [dict(o)]
g = G["materiel_multimedia_vol"]
g["perimetre"] = [f("evenement", "vol"), MM]
g["circonstances"] = [c for c in g["circonstances"] if "garantie_vol_accordee" not in json.dumps(c)]
g["circonstances"][0]["condition"] = ou(non({"concept": "batiment_designe"}),
                                        et(f("lieu", "vehicule"), ou(f("vehicule_vole", "oui"), f("effraction", "oui"))),
                                        et(f("sejour_temporaire", "oui"), f("plainte_deposee", "oui")))
X = []
for x in p["exclusions_communes"]:
    t = x["texte"]
    if t.startswith(("les frais exposés pour réparer", "les frais d'entretien", "les pertes indirectes", "les pertes de données", "les dommages d'un montant inférieur")):
        hors(p, x["article"], t, "des frais, des pertes indirectes ou une franchise : sans effet sur la question de couverture"); continue
    if t.startswith("les pertes ou dommages qui sont la conséquence directe"):
        x["article"] = "3.1.7.2"; x["texte"] = "les pertes ou dommages qui sont la conséquence directe : n des effets continuels de l’exploitation (usure) ; n d’un fonctionnement défectueux"
        x["condition"] = ou(f("manque_entretien", "oui"), f("fonctionnement_defectueux", "oui")); x.update(FAIT_ASSUREUR)
    elif t.startswith("les dommages d'origine électrique"):
        x["condition"] = f("evenement", "electricite")
    elif t.startswith("les dommages causés au contenu des appareils"):
        x.update(condition=f("bien", "denrees_alimentaires"), **PORTEE_BIEN("denrees_alimentaires"))
    elif t.startswith("les pertes ou dommages causés aux lampes"):
        x.update(condition=f("bien", "consommable"), **PORTEE_BIEN("consommable"))
    elif t.startswith("les défauts d'ordre esthétique"):
        x.update(FAIT_ASSUREUR)
    elif t.startswith(("les pertes liées à l'action d'un virus", "les pertes ou dommages dus à des vices", "les pertes ou dommages dont le fabricant")):
        x.update(FAIT_ASSUREUR)
    elif t.startswith("les vols commis par ou avec la complicité"):
        x["article"] = "3.1.7.2"; x["condition"] = ou(f("auteur", "assure"), f("auteur", "famille"), f("auteur", "personnel_prive"))
        x["texte"] = next(s for s in CLAUSES["3.1.7.2_items"] if s.startswith("les vols commis par ou avec la complicité"))
    X.append(x)
X.append(option("3.1.7", "option_materiel_multimedia", "matériel multimédia"))
G["materiel_multimedia_vol"]["exclusions"].append({"condition": f("option_vol", "non"), "portee": "tout", "a_demander": True,
          "article": "3.1.7.1", "texte": "Sous réserve que la garantie vol ait été accordée"})
p["exclusions_communes"] = X
vus = set()
for n in p.get("non_traduit") or []:
    art = n["article"]
    if art.startswith(("3.1.7.3", "3.1.7.4")):          # la citation du modèle portait la numérotation : on cite le début de la clause
        art = art[:7]
        n = {**n, "article": art, "texte": CLAUSES[art].split(" ; ")[0][:200].rstrip(" ,;")}
    if (art, n["texte"]) in vus: continue
    vus.add((art, n["texte"]))
    hors(p, art, n["texte"], "extension des autres garanties en séjour, règles d'indemnisation, obligations après sinistre, subrogation : sans effet sur la question de couverture, ou déjà couvert par les garanties concernées")
p["non_traduit"] = []
hors(p, "3.1.7.2", next(s for s in CLAUSES["3.1.7.2_items"] if s.startswith("et 3.1.7.2.10")), "dérogation aux exclusions pour l'indemnisation : sans effet sur la question de couverture")
voc = [var("bien", ["equipement_alarme_surveillance", "equipement_domotique", "consommable"], "Quels biens ?",
           {"equipement_alarme_surveillance": "alarme, caméra de surveillance, détecteurs", "equipement_domotique": "box domotique, volets ou éclairage pilotés",
            "consommable": "lampe, tube, fusible, joint, courroie, chaîne"}, "3.1.7", "electronique",
           parent={"equipement_alarme_surveillance": "electronique", "equipement_domotique": "electronique", "consommable": "objet_divers"}),
       var("lieu", ["vehicule"], "Où se trouvaient les biens ?", {"vehicule": "dans une voiture, un véhicule"}, "3.1.7.1", "voie_publique"),
       var("vehicule_vole", ["oui", "non"], "Le véhicule lui-même a-t-il été volé ?", {"oui": "la voiture a été volée avec le matériel", "non": "seul le matériel a été pris"}, "3.1.7.1"),
       var("vehicule_ferme_cle", ["oui", "non"], "Le véhicule était-il fermé à clé ?", {"oui": "voiture verrouillée", "non": "voiture ouverte, non verrouillée"}, "3.1.7.4"),
       var("materiel_laisse_en_vue", ["oui", "non"], "Le matériel était-il visible de l'extérieur du véhicule ?", {"oui": "sur le siège, visible à travers la vitre", "non": "dans le coffre, caché"}, "3.1.7.4"),
       var("mise_en_exploitation_satisfaction", ["oui", "non"], "L'alarme fonctionnait-elle correctement depuis son installation ?", {"oui": "installée et en état de marche", "non": "jamais correctement mise en service"}, "3.1.7.1"),
       var("fonctionnement_defectueux", ["oui", "non"], "Le dommage vient-il d'un fonctionnement défectueux de l'appareil ?", {"oui": "panne interne, défaut de l'appareil", "non": "cause extérieure : chute, choc, liquide"}, "3.1.3.2 et 3.1.7.2"),
       var("cause_dommage", ["virus"], "Quelle est la cause du dommage ?", {"virus": "virus informatique, logiciel malveillant"}, "3.1.7.2", "autre"),
       var("vice_defaut_connu", ["oui", "non"], "Le défaut existait-il et était-il connu avant la souscription ?", {"oui": "panne ou défaut déjà connu", "non": "défaut apparu ensuite"}, "3.1.7.2"),
       opt_var("option_materiel_multimedia", "matériel multimédia"), opt_var("option_vol", "vol")]
fin("3.1.7", voc, [
  "matériel multimédia (1.25 : ordinateur, tablette, téléphone, appareil photo…) → bien = electronique et ses sous-valeurs ; alarme et domotique rattachées à electronique",
  "« applicables si… » : réserve (option_materiel_multimedia) ; « sous réserve que la garantie vol ait été accordée » : réserve pour le vol seulement (option_vol)",
  "vol couvert hors du bâtiment désigné, dans un véhicule volé ou forcé, ou en séjour temporaire avec plainte ; « à l'extérieur du bâtiment » = non(bâtiment désigné)",
  "obligation du véhicule : si le matériel est dans un véhicule ; elle s'appliquait à tout sinistre ; lieu = vehicule (pas vehicule_moteur, une valeur de bien)",
  "mise en exploitation satisfaisante : seulement pour l'alarme, en exclusion de portée bien (en circonstance, elle faisait demander si un téléphone était une alarme)",
  "la réserve « garantie vol accordée » sur la seule garantie vol : écrite « vol et option inconnue », elle était entamée par l'événement et posait la question à chaque vol",
  "frais d'entretien, de réparation de défauts, pertes indirectes, pertes de données, franchise de 60 € : hors décision ; « dommages d'origine électrique » = événement électricité",
  "defaut_fonctionnement et fonctionnement_defectueux : une seule variable ; auteur = preneur → assure",
  "les six passages « non traduits » (extension des autres garanties en séjour, indemnisation, obligations après sinistre) : hors décision"],
  question="Le matériel multimédia en séjour temporaire est couvert par les garanties incendie, tempête, eaux… « sous réserve qu'elles aient été accordées » : non traduit ici (hors décision), à vérifier avec un souscripteur.")

# ---------------------------------------------------------------- 3.2.1 Tremblement de terre
p = DOCS["3.2.1"]["proposition"]; g = p["garanties"][0]
g["perimetre"] = [f("evenement", "catastrophe_naturelle"), f("catastrophe", "tremblement_terre"), {"concept": "batiment_designe"}]
p["evenements"] = ["catastrophe_naturelle"]
g["circonstances"] = []
g["exclusions"] = regler(g["exclusions"], {
    "survenus aux objets se trouvant à l’extérieur": {"condition": et(OBJET_EXTERIEUR, non(f("fixe_a_demeure", "oui")))},
    "aux constructions faciles à déplacer": {"condition": ou(f("construction_facilement_deplacable", "oui"), f("construction_delabree", "oui"))},
    "aux jardins et plantations": {"condition": f("bien", "plantation"), **PORTEE_BIEN("plantation")},
    "aux terrains de golf": None,
    "aux véhicules terrestres": {"condition": f("bien", "vehicule_moteur"), **PORTEE_BIEN("vehicule_moteur")}})
p["exclusions_communes"] = (p.get("exclusions_communes") or []) + [option("3.2.1", "option_tremblement_terre", "tremblement de terre")]
fin("3.2.1", [V_CATA, opt_var("option_tremblement_terre", "tremblement de terre"),
              var("fixe_a_demeure", ["oui", "non"], "L'objet à l'extérieur était-il fixé à demeure (scellé, ancré) ?", {"oui": "scellé dans le sol ou le mur", "non": "simplement posé"}, "3.2.1.2"),
              var("construction_facilement_deplacable", ["oui", "non"], "La construction est-elle facile à déplacer ou à démonter ?", {"oui": "cabane démontable, abri posé, tente", "non": "construction fixe"}, "3.2.1.2")], [
  "evenement = tremblement_terre → evenement = catastrophe_naturelle (comme Foyer) et catastrophe = tremblement_terre (variable nouvelle, partagée avec 3.2.2)",
  "formule = serenite_plus → réserve option_tremblement_terre (3.2.1 : « applicables si les conditions particulières mentionnent la garantie »)",
  "circonstance qui répétait le périmètre : retirée",
  "jardins et plantations, véhicules : portée limitée au bien ; terrains de golf et de tennis : hors vocabulaire d'un particulier, retirée de la règle (citée hors décision)",
  "« à l'extérieur » = jardin ou terrasse, objets ; contenu de constructions délabrées : fondu dans l'exclusion de la construction"])
hors(p, "3.2.1.2", "aux terrains de golf ou de tennis", "un terrain de golf ou de tennis n'est pas un bien d'un contrat habitation de particulier : sans effet en pratique")

# ---------------------------------------------------------------- 3.2.2 Pluies et inondations
p = DOCS["3.2.2"]["proposition"]; g = p["garanties"][0]
g["perimetre"] = [f("evenement", "catastrophe_naturelle"), ou(f("catastrophe", "inondation"), f("catastrophe", "ruissellement"), f("catastrophe", "glissement_terrain")),
                  {"concept": "batiment_designe"}]
p["evenements"] = ["catastrophe_naturelle"]
c72 = g["circonstances"][0]; g["circonstances"] = []
g["exclusions"].append({"condition": f("dommages_dans_72h", "non"), "portee": "tout", "a_demander": False, "article": c72["article"], "texte": c72["texte"]})
g["exclusions"] = regler(g["exclusions"], {
    "au contenu se trouvant à l’extérieur": {"condition": et(OBJET_EXTERIEUR, non(f("bien", "mobilier_jardin")))},
    "par l’hygrométrie": {"condition": f("cause_eau", "condensation"), **FAIT_ASSUREUR},
    "par des champignons": {"condition": f("cause_eau", "condensation"), **FAIT_ASSUREUR},
    "par l’humidité, la porosité": {"condition": f("cause_eau", "condensation"), **FAIT_ASSUREUR},
    "par un défaut de réparation": {"condition": f("manque_entretien", "oui"), **FAIT_ASSUREUR},
    "aux bâtiments situés sur un terrain non constructible": FAIT_ASSUREUR,
    "aux bâtiments soumis à l’autorisation": FAIT_ASSUREUR})
p["definitions"] = [d for d in p.get("definitions", []) if d["concept"] != "a_l_exterieur_locaux"]
p["exclusions_communes"] = (p.get("exclusions_communes") or []) + [option("3.2.2", "option_pluies_inondations", "pluies et inondations")]
voc = [V_CATA, opt_var("option_pluies_inondations", "pluies et inondations")]
voc += [x for x in p["vocabulaire_manquant"] if x["variable"] in ("dommages_dans_72h", "ouvertures_non_fermees", "terrain_non_constructible", "autorisation_gestion_eau_non_respectee")]
fin("3.2.2", voc, [
  "événements inondation, ruissellement, glissement → evenement = catastrophe_naturelle et catastrophe = … (partagé avec 3.2.1)",
  "« applicables si… » : réserve (option_pluies_inondations)",
  "dommages dans les 72 heures : exclusion à établir par l'assureur, pas une question à chaque inondation",
  "hygrométrie, champignons, humidité, condensation : cause_eau = condensation ; défaut d'étanchéité → manque_entretien ; « à l'extérieur des locaux » : règle 3 quater"])

for a, d in DOCS.items():
    open(f"{dst}/{a}.json", "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
print("ok", list(DOCS))
