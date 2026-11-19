"""Relecture humaine de la proposition AXA 3.1.6 (DEMARCHE 7.55). Chaque modification est tracée dans meta.relecture."""
import json, sys
src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(src, encoding="utf-8"))
p = d["proposition"]
G = {g["id"]: g for g in p["garanties"]}
journal = []
def note(m): journal.append(m)

PLAINTE = {"condition": {"f": ["plainte_deposee", "oui"]}, "article": "3.1.6.1",
           "texte": "pour autant qu’une plainte ait été déposée auprès des autorités judiciaires ou de police compétentes"}
for g in p["garanties"]:
    g["circonstances"] = [PLAINTE if c["condition"] == {"f": ["plainte_deposee", "oui"]} else c for c in g["circonstances"]]
note("plainte déposée : citation précise au lieu de celle de la garantie (9 circonstances)")

# agression -> violence (variable existante)
G["vol_agression"]["perimetre"] = [{"f": ["violence", "oui"]} if x == {"f": ["agression", "oui"]} else x
                                   for x in G["vol_agression"]["perimetre"]]
note("agression → violence = oui (la question existante couvre « violences physiques ou menaces »)")

# vandalisme à l'occasion d'un vol : evenement a plusieurs valeurs
G["vandalisme_vol"]["perimetre"] = [{"f": ["evenement", "vandalisme"]}, {"f": ["evenement", "vol"]}]
note("vol_associe → evenement = vandalisme ET evenement = vol (la variable evenement admet plusieurs valeurs)")

# clés : la portée en cas d'occupation partielle est une limite de l'intervention, pas une condition
g = G["remplacement_cles"]
g["circonstances"] = [c for c in g["circonstances"] if "acces_direct_partie_occupee" not in json.dumps(c)]
g["limites"].append({"article": "3.1.6.1", "texte": "Pour ce qui concerne les bâtiments dont l’Assuré est occupant partiel, "
                     "cette intervention ne vise que les portes donnant directement accès à la partie occupée par lui.",
                     "montant": "portes de la partie occupée"})
note("acces_direct_partie_occupee retiré : c'est une limite de l'intervention (quelles portes), citée telle quelle")

# mesures de sécurité : variable existante, et le lien causal porte déjà « charge aggravée »
G["vol_batiment"]["obligations"] = [{"condition": {"f": ["serrure_surete", "oui"]}, "exception": None, "lien_causal": True,
    "article": "3.1.6.4", "texte": "portes donnant sur l’extérieur ou sur les parties communes de l’immeuble : au moins une serrure de sûreté ou un verrou de sûreté"}]
note("dispositifs_securite_conformes → serrure_surete ; aggravation_non_utilisation retiré : lien_causal = true l'exprime")

# bâtiment désigné : pas seulement le logement
for dfn in p["definitions"]:
    if dfn["concept"] == "batiment_designe":
        dfn["condition"] = {"ou": [{"f": ["lieu", v]} for v in ("logement", "cave", "grenier", "garage")]}
note("batiment_designe : logement, cave, grenier, garage (et non le seul logement)")

for x in p["exclusions_communes"]:
    t = x["texte"]
    if t.startswith("les vols commis par ou avec la complicité"):
        x["condition"] = {"ou": [{"f": ["auteur", "assure"]}, {"f": ["auteur", "famille"]},
            {"et": [{"f": ["auteur", "personnel_prive"]}, {"non": {"ou": [{"f": ["effraction", "oui"]}, {"f": ["violence", "oui"]}]}}]}]}
        note("complicite_assure → auteur ; personnel exclu sauf effraction ou violence (les heures de service ne sont pas un fait du vocabulaire)")
    elif t.startswith("les vols de véhicules automoteurs"):
        x["condition"] = {"ou": [{"f": ["bien", "vehicule_moteur"]},
            {"et": [{"f": ["bien", "remorque"]}, {"non": {"ou": [{"f": ["lieu", v]} for v in ("logement", "cave", "grenier", "garage")]}}]}]}
        note("remorque_non_fermee → bien = remorque (valeur nouvelle) hors du bâtiment désigné")
    elif t.startswith("les vols à la tire"):
        x["condition"] = {"et": [{"f": ["vol_sur_personne", "oui"]}, {"f": ["lieu", "voie_publique"]}, {"non": {"f": ["violence", "oui"]}}]}
        note("CONFLIT : le vol à la tire excluait aussi le vol par agression (vol sur la personne, sur la voie publique) ; ajouté « sans violence »")
    elif t == "le vol des animaux":
        x["portee"] = {"bien": "animal"}
        note("vol des animaux : portée limitée au bien animal")

# 3.1.6.3 : des plafonds, cités sans condition ; 3.1.6.5 : procédure après sinistre
p["non_traduit"] = []
for t, m in [("à concurrence de 40% du montant indiqué aux conditions particulières au titre du contenu, pour les objets tels que meubles d’époque et objets de valeur", "40 % du contenu"),
             ("concernant les timbres de collection, l’indemnité par timbre ne pourra être supérieure à 500 €", "500 € par timbre"),
             ("à concurrence de 1500 € par sinistre pour l’ensemble constitué de l’argent comptant", "1 500 € (750 € hors clefs)")]:
    G["vol_batiment"]["limites"].append({"article": "3.1.6.3", "texte": t, "montant": m})
p["hors_decision"] = [{"article": "3.1.6.5", "texte": "Si les objets volés sont retrouvés, l’Assuré doit en aviser immédiatement la Compagnie.",
                       "pourquoi": "procédure après sinistre, sans effet sur la couverture"}]
note("3.1.6.3 : plafonds cités en limites ; 3.1.6.5 : hors décision")

retires = {"agression", "complicite_assure", "dispositifs_securite_conformes", "aggravation_non_utilisation",
           "vol_associe", "remorque_non_fermee", "acces_direct_partie_occupee", "sous_clefs"}
p["vocabulaire_manquant"] = [v for v in p["vocabulaire_manquant"] if v["variable"] not in retires]
p["vocabulaire_manquant"].append({"variable": "bien", "valeurs": ["remorque"], "question": "Quels biens sont concernés ?",
    "pourquoi": "exclusion 3.1.6.2.5", "plus_proche": "vehicule_moteur : une remorque n'a pas de moteur"})
note("sous_clefs retiré : le plafond est cité, il ne décide pas de la couverture")

d["meta"]["relecture"] = {"par": "auteur + Claude", "date": "2026-11-18", "modifications": journal,
    "question_metier": "le vol simple (ni effraction ni violence) est exclu pour toutes les garanties : il vide l'extension « mobilier de jardin » (Privilège) de presque tout son sens. Lecture à confirmer par un souscripteur."}
d.pop("controles", None)
json.dump(d, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
open(dst, "a", encoding="utf-8").write("\n")
print("\n".join(journal))
