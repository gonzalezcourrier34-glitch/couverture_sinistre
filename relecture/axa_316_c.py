"""Troisième passe sur AXA 3.1.6, après le premier banc (DEMARCHE 7.60)."""
import json, sys
src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(src, encoding="utf-8")); p = d["proposition"]
xs = p["exclusions_communes"]
k = next(i for i, x in enumerate(xs) if x["texte"].startswith("les vols de véhicules automoteurs"))
x = xs[k]
vehicule = {**x, "condition": {"f": ["bien", "vehicule_moteur"]}, "portee": {"bien": "vehicule_moteur"}, "a_demander": False}
remorque = {**x, "condition": {"et": [{"f": ["bien", "remorque"]}, {"non": {"ou": [{"f": ["lieu", v]} for v in ("logement", "cave", "grenier", "garage")]}}]},
            "portee": {"bien": "remorque"}, "a_demander": False}
xs[k:k + 1] = [vehicule, remorque]
d["meta"]["relecture"]["modifications"].append(
    "3.1.6.2.5 : « le vol de véhicules… » vise le bien, pas le sinistre ; scindé en deux exclusions de portée bien "
    "(véhicule, remorque hors du bâtiment) ; a_demander false : le bien est connu (axa-v10 : vélos volés avec une tondeuse)")
d["meta"]["relecture"]["troisieme_passe"] = "après le premier banc AXA (data/bancs/20261118-222055-…)"
d.pop("controles", None)
open(dst, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
