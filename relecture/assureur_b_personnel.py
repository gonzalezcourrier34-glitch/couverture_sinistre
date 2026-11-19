"""Assureur B 3.1.6 et 3.1.7 : l'exclusion des vols commis par une personne au service de l'Assuré (DEMARCHE 7.75).

Le texte : « toute personne au service de l'Assuré pendant les heures de service et, si ces vols ont été commis
en dehors de celles-ci, autrement que par effraction ou avec violence ». Deux cas exclus : pendant les heures de
service, quoi qu'il arrive ; en dehors, sauf effraction ou violence.
- 3.1.6 ne gardait que le second : la femme de ménage qui prend des bijoux en travaillant n'était pas exclue
  sans qu'on sache s'il y avait eu violence (b-v12 « incertain »).
- 3.1.7 excluait le personnel en toute circonstance : un cambriolage avec effraction par un employé, un jour de
  congé, aurait été refusé à tort.

Usage : python relecture/assureur_b_personnel.py  (corrige les deux propositions en place)"""
import json
from pathlib import Path

DOSSIER = Path(__file__).resolve().parents[1] / "regles" / "propositions" / "assureur-b-habitation-2017"
PERSONNEL = {"et": [{"f": ["auteur", "personnel_prive"]},
                    {"ou": [{"f": ["heures_service", "oui"]},
                            {"non": {"ou": [{"f": ["effraction", "oui"]}, {"f": ["violence", "oui"]}]}}]}]}
CONDITION = {"ou": [{"f": ["auteur", "assure"]}, {"f": ["auteur", "famille"]}, PERSONNEL]}

for article in ("3.1.6", "3.1.7"):
    chemin = DOSSIER / f"{article}.json"
    d = json.loads(chemin.read_text(encoding="utf-8"))
    p = d["proposition"]
    xs = [x for x in p.get("exclusions_communes") or [] if x["texte"].startswith("les vols commis par ou avec la complicité")]
    xs += [x for g in p["garanties"] for x in g.get("exclusions", [])
           if x["texte"].startswith("les vols commis par ou avec la complicité")]
    assert xs, f"{article} : exclusion du personnel introuvable"
    for x in xs:
        x["condition"] = CONDITION
    rel = d["meta"].setdefault("relecture", {})
    rel.setdefault("modifications", []).append(
        "personnel au service de l'Assuré : exclu pendant les heures de service, et en dehors sauf effraction ou "
        "violence (variable heures_service) ; 7.75")
    d.pop("controles", None)
    chemin.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{article} : {len(xs)} exclusion(s) corrigée(s)")
