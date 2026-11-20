"""Deux corrections de règles trouvées en relisant les erreurs du jeu fermé de A et B (DEMARCHE 7.101).

- A 2.6 (action de l'électricité) : « les dommages aux appareils électroniques et informatiques dont l'usage est
  professionnel ». L'exclusion ne visait que l'ordinateur : l'écran fourni avec lui (`f-a13`, lu
  `appareil_audiovisuel`) restait couvert. Elle vise désormais chacun des appareils électroniques, un par un (la
  portée d'une exclusion est un bien, ou tout).
- B 3.1.5 (bris de vitrages) : la perte d'étanchéité des vitrages isolants était une circonstance « si opacification,
  alors ni garantie du fabricant ni locataire ». Le type de dommage inconnu laissait la circonstance inconnue : le
  miroir fendu à l'aspirateur (`f-b08`) devenait incertain, avec la question « quel est le type de dommage ? ». C'est
  une exclusion, à demander : sans opacification, elle ne joue pas ; avec (`f-b20`, le double vitrage embué), elle
  est entamée, et la réponse reste incertaine.
- B 3.1.1 (décongélation des denrées) : « imputable à un sinistre couvert » (incendie, explosion, foudre,
  électricité) était une circonstance. Le périmètre (`bien = denrees_alimentaires`) rattachait la garantie dès qu'un
  bien vague était lu (`objet_divers`), et la circonstance fausse la refusait : un refus rattaché l'emporte sur les
  garanties possibles, et le vol dans la remise (`f-b17`) devenait un refus. L'événement fait partie du périmètre.

Usage : python relecture/lecture_ab.py  (corrige les propositions en place, puis les réaccepter)"""
import json
from pathlib import Path

REGLES = Path(__file__).resolve().parents[1] / "regles" / "propositions"


def f(v, x): return {"f": [v, x]}


def corriger(contrat, article, changer, modification):
    chemin = REGLES / contrat / f"{article}.json"
    d = json.loads(chemin.read_text(encoding="utf-8"))
    changer(d["proposition"])
    relu = d["meta"].setdefault("relecture", {"par": "auteur + Claude", "modifications": []})
    relu["date"] = "2026-11-20"
    relu.setdefault("modifications", []).append(modification)
    d.pop("controles", None)
    chemin.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{contrat} {article} : corrigé")


def a_2_6(p):
    texte = "les dommages aux appareils électroniques et informatiques dont l’usage est professionnel"
    garder = [x for x in p["exclusions_communes"] if x.get("texte") != texte]
    assert len(garder) == len(p["exclusions_communes"]) - 1, "exclusion d'usage professionnel introuvable"
    pro = [{"condition": {"et": [f("bien", b), f("usage_professionnel", "oui")]}, "portee": {"bien": b},
            "a_demander": False, "article": "2.6-a", "texte": texte}
           for b in ("appareil_informatique", "electronique", "appareil_audiovisuel")]
    p["exclusions_communes"] = pro + garder


def b_3_1_5(p):
    g = next(g for g in p["garanties"] if g["id"] == "bris_vitrages")
    c = next(c for c in g["circonstances"] if "si" in c["condition"])
    g["circonstances"].remove(c)
    opacite, sauf = c["condition"]["si"]
    g["exclusions"].append({"condition": {"et": [opacite, sauf["non"]]}, "portee": "tout", "a_demander": True,
                            "article": c["article"], "texte": c["texte"]})


def b_3_1_1(p):
    g = next(g for g in p["garanties"] if g["id"] == "decongelation")
    c = next(c for c in g["circonstances"] if "evenement" in json.dumps(c["condition"]))
    g["circonstances"].remove(c)
    g["perimetre"].append(c["condition"])


corriger("assureur-a-habitation-2025", "2.6", a_2_6,
         "usage professionnel : l'exclusion vise chaque appareil électronique (informatique, audiovisuel, électronique)")
corriger("assureur-b-habitation-2017", "3.1.5", b_3_1_5,
         "perte d'étanchéité : une exclusion à demander, plus une circonstance (le type de dommage inconnu ne suspend plus)")
corriger("assureur-b-habitation-2017", "3.1.1", b_3_1_1,
         "décongélation : l'événement (incendie, explosion, foudre, électricité) au périmètre, plus en circonstance")
