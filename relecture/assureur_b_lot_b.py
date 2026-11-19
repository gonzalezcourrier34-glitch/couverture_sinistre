"""Relecture du lot B de l'assureur B (3.1.8 extensions, 3.1.9 frais, 3.2.3 pertes indirectes), rédigé avec la
consigne v9 le 19 nov. (DEMARCHE 7.72).

3.1.8 : onze « extensions » du modèle, sur des concepts que ce contrat n'a pas (`batiment`, `contenu`, `bien` :
ceux de l'assureur A). Le lieu assuré de B est `batiment_designe`. Et la moitié des « extensions » sont des
responsabilités (« les dégâts causés PAR un assuré à l'hôtel, à la chambre louée, à la salle de fête ») : pas un
lieu assuré de plus, mais une garantie de responsabilité, non traduite : accessoires, comme pour A (7.69)."""
import json, sys
src, dst = sys.argv[1], sys.argv[2]
DOCS = {a: json.load(open(f"{src}/{a}.json", encoding="utf-8")) for a in ["3.1.8", "3.1.9", "3.2.3"]}

def f(v, x): return {"f": [v, x]}
def et(*l): return {"et": list(l)}
def ou(*l): return {"ou": list(l)}
UE_CH_NO = ou(*[f("pays", p) for p in ("luxembourg", "allemagne", "belgique", "france", "autre_ue", "suisse", "norvege")])
PAYS = {"variable": "pays", "valeurs": ["luxembourg", "allemagne", "belgique", "france", "autre_ue", "suisse", "norvege", "hors_europe"],
        "question": "Dans quel pays se trouvait le lieu du sinistre ?",
        "pourquoi": "restrictions géographiques des extensions 3.1.8 (Luxembourg ; pays voisins ; UE, Suisse, Norvège)",
        "plus_proche": "lieu : dit le type de lieu, pas le pays",
        "aide": {"luxembourg": "au Grand-Duché de Luxembourg", "allemagne": "en Allemagne", "belgique": "en Belgique",
                 "france": "en France", "autre_ue": "dans un autre pays de l'Union européenne", "suisse": "en Suisse",
                 "norvege": "en Norvège", "hors_europe": "hors de l'Union européenne, de la Suisse et de la Norvège"}}

def journal(a, lignes):
    DOCS[a]["meta"]["relecture"] = {"par": "auteur + Claude", "date": "2026-11-19", "modifications": lignes}
    DOCS[a].pop("controles", None)

# ---------- 3.1.8
p = DOCS["3.1.8"]["proposition"]
T = {(x["article"], x["concept"]): x["texte"] for x in p["extensions"]}
def ext(article, cle, condition):
    return {"concept": "batiment_designe", "condition": condition, "article": article, "texte": T[(article, cle)]}
def rc(gid, nom, article, cle, perimetre):
    return {"id": gid, "nom": nom, "article": article, "texte": T[(article, cle)], "perimetre": perimetre,
            "accessoire": True, "circonstances": [], "obligations": [], "exclusions": [], "limites": []}
p["extensions"] = [
    ext("3.1.8.2", "batiment", et(f("residence_principale_inhabitable", "oui"), f("lieu", "autre_batiment"), f("pays", "luxembourg"))),
    ext("3.1.8.3", "contenu", et(f("sejour_temporaire", "oui"), f("lieu", "autre_batiment"))),
    ext("3.1.8.4", "contenu", et(f("lieu", "chambre_etudiant"), UE_CH_NO)),
    ext("3.1.8.5", "contenu", f("lieu", "maison_repos")),
    ext("3.1.8.7", "bien", et(f("bien", "sepulture"), f("pays", "luxembourg"))),
    ext("3.1.8.8", "batiment", et(f("demenagement", "oui"), f("pays", "luxembourg"), f("duree_demenagement", "moins_90_jours"))),
]
p["garanties"] = [
    rc("rc_sejour_temporaire", "Dégâts causés à l'hôtel ou à la villégiature (responsabilité)", "3.1.8.3", "batiment",
       [f("sejour_temporaire", "oui"), f("lieu", "autre_batiment")]),
    rc("rc_logement_etudiant", "Dégâts causés au logement d'étudiant (responsabilité)", "3.1.8.4", "batiment",
       [f("lieu", "chambre_etudiant"), UE_CH_NO]),
    rc("rc_local_fete", "Dégâts causés au local de fête (responsabilité)", "3.1.8.6", "batiment",
       [f("lieu", "local_fete_privee"), ou(*[f("pays", x) for x in ("luxembourg", "allemagne", "belgique", "france")])]),
]
p["evenements"] = []
p["hors_decision"] = (p.get("hors_decision") or []) + [
    {"article": "3.1.8.1", "texte": T[("3.1.8.1", "batiment")],
     "pourquoi": "un garage est déjà un lieu du bâtiment désigné : le vocabulaire ne distingue pas deux adresses"},
    {"article": "3.1.8", "texte": "Les présentes conditions spéciales sont applicables par extension aux garanties souscrites",
     "pourquoi": "le champ des extensions : elles élargissent les garanties souscrites, ce que fait `extension/4`"},
    {"article": "3.1.8", "texte": "les dégâts occasionnés au bâtiment par un événement soudain",
     "pourquoi": "porte sur les dégâts causés aux bâtiments loués : les extensions de responsabilité, accessoires, sans effet sur une décision"}]
voc = [m for m in p["vocabulaire_manquant"] if m["variable"] not in ("zone_geographique", "occasion")]
for m in voc:
    if m["variable"] == "lieu":
        m["parent"] = {x: "autre_batiment" for x in m["valeurs"]}
    if m["variable"] == "bien":
        m["parent"] = {}
p["vocabulaire_manquant"] = voc + [PAYS]
journal("3.1.8", [
  "extensions sur `batiment_designe`, le lieu assuré de ce contrat (le modèle employait les concepts de l'assureur A)",
  "dégâts causés PAR un assuré à l'hôtel, à la chambre d'étudiant, au local de fête : responsabilité, non traduite ; garanties accessoires",
  "zone_geographique (dix valeurs dont des listes) → pays, une valeur par pays ; « n'importe où dans le monde » : aucune condition",
  "sépultures « au Luxembourg ou à 50 km des frontières » : Luxembourg seulement (prudent : au-delà, la réponse ne sera pas « couvert »)",
  "garages à une autre adresse : hors décision (déjà un lieu du bâtiment désigné)",
  "valeurs de lieu nouvelles rattachées à autre_batiment ; « occasion = fête privée » retirée (le lieu le dit)"])

# ---------- 3.1.9 : frais, accessoires
p = DOCS["3.1.9"]["proposition"]
for g in p["garanties"]:
    if g["id"] == "frais_depollution":
        # « si les garanties de base sont souscrites » : une accessoire suit déjà un sinistre couvert par l'une d'elles.
        g["circonstances"] = [c for c in g["circonstances"] if "garanties de base" not in c.get("texte", "")]
journal("3.1.9", ["frais de dépollution : la condition « garanties de base souscrites » retirée (citation introuvable, et implicite pour une accessoire)"])

# ---------- 3.2.3 : pertes indirectes
p = DOCS["3.2.3"]["proposition"]
g = p["garanties"][0]
listes = [x for x in g["exclusions"] if x["condition"].get("f", [None])[0] == "garantie_indemnite"]
g["exclusions"] = [x for x in g["exclusions"] if x not in listes]
g["perimetre"] = []
p["hors_decision"] = (p.get("hors_decision") or []) + [
    {"article": x["article"], "texte": x["texte"],
     "pourquoi": "indemnités exclues du calcul de la majoration de 10 % : un montant, pas la couverture"}
    for x in listes if x["texte"] != "aux garanties des options : «voyage»"]
p["vocabulaire_manquant"] = [m for m in p["vocabulaire_manquant"] if m["variable"] != "garantie_indemnite"]
journal("3.2.3", ["les garanties dont l'indemnité n'est pas majorée : hors décision (un calcul de montant)",
                  "« «voyage» » : citation introuvable, couverte par la ligne des options"])

for a, d in DOCS.items():
    open(f"{dst}/{a}.json", "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
print("ok", list(DOCS))
