"""Relecture de l'art. 6.1 de l'assureur A (pack multimédia, option), rédigé avec la consigne v9 le 19 nov.
(DEMARCHE 7.71). Ce qui relevait de la méthode est passé dans le code (circonstance propre à un événement,
obligation écrite comme une situation) ; restent ici les choix de traduction."""
import json, sys
src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(f"{src}/6.1.json", encoding="utf-8"))
p = d["proposition"]
g = p["garanties"][0]

def f(v, x): return {"f": [v, x]}

# La chute et le corps étranger se lisent souvent « bris » (un écran cassé) : le périmètre les accepte aussi.
g["perimetre"] = [{"concept": "materiel_informatique"},
                  {"ou": [f("evenement", "heurt"), f("evenement", "bris"), f("evenement", "vol")]}]
# « À l'extérieur du bâtiment assuré » : le concept du contrat, pas une variable de plus.
c = g["circonstances"][0]
c["condition"] = {"si": [f("evenement", "vol"), {"et": [{"non": {"concept": "batiment"}}, f("plainte_deposee", "oui")]}]}
# Les deux obligations redisent les exclusions du véhicule (22 h - 7 h ; 7 h - 22 h) : retirées.
g["obligations"] = []
for x in g["exclusions"]:
    t = x["texte"]
    if t.startswith("le vol d’objets ayant été laissé sans surveillance"):
        x["condition"] = {"et": [f("evenement", "vol"), f("laisse_sans_surveillance", "oui")]}
    elif t.startswith("la simple perte, disparition"):
        x["condition"] = {"et": [f("evenement", "vol"), f("simple_disparition", "oui")]}   # rien à réserver pour une chute
p["evenements"] = ["heurt", "bris", "vol"]
# Une valeur doit commencer par une lettre (identifiant du vocabulaire) : « 22h_7h » était refusée en silence.
RENOMME = {"22h_7h": "nuit_22h_7h", "7h_22h": "jour_7h_22h"}
def renommer(c):
    if isinstance(c, dict):
        if isinstance(c.get("f"), list) and c["f"][0] == "periode_horaire":
            c["f"][1] = RENOMME.get(c["f"][1], c["f"][1])
        for x in c.values():
            renommer(x)
    elif isinstance(c, list):
        for x in c:
            renommer(x)
renommer(g["exclusions"])
for m in p["vocabulaire_manquant"]:
    if m["variable"] == "periode_horaire":
        m["valeurs"] = [RENOMME.get(x, x) for x in m["valeurs"]]
        m["aide"] = {RENOMME.get(k, k): x for k, x in (m.get("aide") or {}).items()}
p["vocabulaire_manquant"] = [m for m in p["vocabulaire_manquant"] if m["variable"] != "hors_batiment"]
for m in p["vocabulaire_manquant"]:
    if m["variable"] == "laisse_sans_surveillance":
        m["question"] = "L'objet avait-il été laissé sans surveillance dans un lieu public (gare, café, rue…) ?"
d["meta"]["relecture"] = {"par": "auteur + Claude", "date": "2026-11-19", "modifications": [
    "circonstance du vol (plainte, hors du bâtiment) limitée au vol : écrite « vol et plainte », elle interdisait la chute et le heurt",
    "hors_batiment → non(concept(batiment)) : le bâtiment est un concept du contrat, extensions comprises",
    "périmètre : bris ajouté (un ordinateur tombé se lit souvent « bris »)",
    "obligations du véhicule retirées : écrites comme une situation, elles faisaient refuser tout heurt à la maison ; les exclusions disent déjà la même chose",
    "« laissé sans surveillance dans un lieu public » et « simple perte dans un lieu public » : pas limités à la voie publique (une gare, un café) ; la simple perte réservée au vol (une chute n'en est pas une)",
    "periode_horaire : valeurs nuit_22h_7h et jour_7h_22h (un identifiant commence par une lettre)"]}
d.pop("controles", None)
open(f"{dst}/6.1.json", "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
print("ok")
