"""Assureur B : deux trous des règles trouvés par le jeu fermé (DEMARCHE 7.83).

- 3.1.1.1.6 : « les dégâts occasionnés au mobilier assuré et au bâtiment désigné par un événement soudain, résultant
  de l'action subite de la chaleur ou par le contact direct et immédiat avec un foyer ou une substance incandescente,
  même lorsqu'il n'y a pas eu embrasement ». La règle ne connaissait que la chaleur seule ; une braise tombée sur le
  tapis (f-b01) n'était ni un incendie (pas de flammes) ni de la chaleur seule. Nouvelle variable
  `contact_incandescent` ; et la circonstance « un incendie au sens du contrat » ne s'impose plus quand le dégât
  relève de 3.1.1.1.6.
- 3.1.4.2.12 et 3.2.2.4 : « par des champignons ou des moisissures, même consécutivement à un sinistre couvert »
  était traduit par `cause_eau = condensation`, une autre exclusion : une moisissure après une fuite (f-b04) restait
  couverte. Nouvelle valeur `type_dommage = moisissure`.

Usage : python relecture/assureur_b_jeu_ferme.py  (corrige les propositions en place)"""
import json
from pathlib import Path

DOSSIER = Path(__file__).resolve().parents[1] / "regles" / "propositions" / "assureur-b-habitation-2017"
CHALEUR = {"ou": [{"f": ["chaleur_sans_feu", "oui"]}, {"f": ["contact_incandescent", "oui"]}]}


def charger(article):
    return json.loads((DOSSIER / f"{article}.json").read_text(encoding="utf-8"))


def sauver(article, d, note):
    d["meta"].setdefault("relecture", {}).setdefault("modifications", []).append(note)
    d.pop("controles", None)
    (DOSSIER / f"{article}.json").write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


d = charger("3.1.1")
g = next(g for g in d["proposition"]["garanties"] if g["id"] == "incendie_base")
termes = g["perimetre"][0]["ou"]
k = next(i for i, t in enumerate(termes) if "et" in t and {"f": ["chaleur_sans_feu", "oui"]} in t["et"])
termes[k] = {"et": [t for t in termes[k]["et"] if t != {"f": ["chaleur_sans_feu", "oui"]}] + [CHALEUR]}
c = next(c for c in g["circonstances"] if c["condition"] == {"si": [{"f": ["evenement", "incendie"]}, {"concept": "incendie"}]})
c["condition"] = {"si": [{"f": ["evenement", "incendie"]}, {"ou": [{"concept": "incendie"}, CHALEUR]}]}
sauver("3.1.1", d, "3.1.1.1.6 : contact direct avec un foyer ou une substance incandescente (contact_incandescent) ; "
       "un tel dégât n'a pas à être un incendie au sens de 3.1.1.1.1 (7.83)")
print("3.1.1 : 3.1.1.1.6 complété")

MOISISSURES = "par des champignons ou des moisissures, même consécutivement à un sinistre couvert"
for article in ("3.1.4", "3.2.2"):
    d = charger(article)
    p = d["proposition"]
    xs = [x for g in p["garanties"] for x in g.get("exclusions") or []] + list(p.get("exclusions_communes") or [])
    n = 0
    for x in xs:
        if x.get("texte", "").startswith(MOISISSURES[:40]):
            x["condition"] = {"f": ["type_dommage", "moisissure"]}
            n += 1
    assert n, f"{article} : exclusion des moisissures introuvable"
    sauver(article, d, "moisissures : la condition était `cause_eau = condensation` (une autre exclusion) ; "
           "désormais `type_dommage = moisissure` (7.83)")
    print(f"{article} : {n} exclusion(s) des moisissures corrigée(s)")
