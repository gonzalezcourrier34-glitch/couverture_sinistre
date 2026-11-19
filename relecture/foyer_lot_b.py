"""Relecture du lot B Foyer (3.1 extensions, 4 garanties complémentaires), rédigé avec la consigne v8 le 19 nov.
(DEMARCHE 7.69).

3.1 : le modèle a fait sept garanties accessoires. Trois élargissent un LIEU assuré (séjour temporaire, nouvelle
adresse, transport pendant le déménagement) : accessoires, elles ne jouaient jamais, puisqu'un incendie à l'hôtel
est hors du « bâtiment » de toutes les garanties de base. Elles deviennent des extensions de la définition du
bâtiment (moteur, 7.69). Les quatre autres touchent la responsabilité locative, pas encore traduite : elles restent
accessoires, sans effet sur une décision, à revoir avec la section 5."""
import json, sys
src, dst = sys.argv[1], sys.argv[2]
DOCS = {a: json.load(open(f"{src}/{a}.json", encoding="utf-8")) for a in ["3.1", "4"]}

def f(v, x): return {"f": [v, x]}
def et(*l): return {"et": list(l)}

def journal(article, lignes):
    d = DOCS[article]
    d["meta"]["relecture"] = {"par": "auteur + Claude", "date": "2026-11-19", "modifications": lignes}
    d.pop("controles", None)

# ---------- 3.1 Extensions
p = DOCS["3.1"]["proposition"]
G = {g["id"]: g for g in p["garanties"]}
sejour, adresse, transport = (G["extension_sejour_temporaire_contenu"], G["extension_demenagement_nouvelle_adresse"],
                              G["extension_transport_contenu_vehicule_demenagement"])
p["extensions"] = [
  {"concept": "batiment", "condition": et(f("sejour_temporaire", "oui"), f("lieu", "autre_batiment"), {"concept": "contenu"}),
   "article": sejour["article"], "texte": sejour["texte"]},
  {"concept": "batiment", "condition": et(f("demenagement", "oui"), f("lieu", "vehicule"), f("detenteur_vehicule", "oui"),
                                          {"concept": "contenu"}),
   "article": transport["article"], "texte": transport["texte"]}]
p["hors_decision"] = (p.get("hors_decision") or []) + [
  {"article": adresse["article"], "texte": adresse["texte"],
   "pourquoi": "la nouvelle adresse est le logement de l'assuré : le vocabulaire ne distingue pas deux adresses, le bâtiment la couvre déjà"}]
p["garanties"] = [g for g in p["garanties"] if g["id"] not in (sejour["id"], adresse["id"], transport["id"])]
p["vocabulaire_manquant"] = [m for m in p["vocabulaire_manquant"]
                             if m["variable"] not in ("type_logement_sejour", "couverture_contenu", "demenagement_depuis_plus_30j")]
journal("3.1", [
  "séjour temporaire et transport pendant le déménagement : extensions de la définition du bâtiment (pour le contenu), "
  "et non garanties accessoires : accessoires, elles ne jouaient jamais (un incendie à l'hôtel est hors du bâtiment)",
  "nouvelle adresse pendant le déménagement : hors décision (le logement est déjà dans le bâtiment)",
  "couverture_contenu (réserve des conditions particulières) retirée avec ces extensions : les garanties de base couvrent "
  "le contenu sans la demander ; demenagement_depuis_plus_30j et type_logement_sejour : plus employés",
  "résidence de remplacement, villégiature, fête de famille, abandon de recours : responsabilité locative, pas encore "
  "traduite (section 5) ; restent accessoires, sans effet sur une décision"])

# ---------- 4 Garanties complémentaires
p = DOCS["4"]["proposition"]
g = p["garanties"][0]
assert g["perimetre"] == [{"concept": "sinistre"}], g["perimetre"]
g["perimetre"] = []
journal("4", [
  "périmètre concept(sinistre) retiré (concept inconnu) : « en cas de sinistre assuré » est implicite pour une garantie "
  "accessoire, qui ne joue qu'après un sinistre couvert (consigne v9)",
  "barème et procédure d'expertise laissés non traduits : sans effet sur la décision (article d'accessoires)"])

for a, d in DOCS.items():
    open(f"{dst}/{a}.json", "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
print("ok", list(DOCS))
