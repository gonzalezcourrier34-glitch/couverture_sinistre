"""Assureur B 3.1.4 et 3.1.6 : deux devoirs de prévention dont la sanction réduit l'indemnité (DEMARCHE 7.81).

Le jeu fermé (f-b02 : une conduite gelée pendant un mois d'absence, chauffage coupé) a montré l'erreur : la règle
refusait le sinistre, alors que le contrat dit « l'indemnité due sera réduite de moitié » (3.1.4.3.1). Même forme
en 3.1.6.4 (mesures de sécurité contre le vol) : « la Compagnie se réserve le droit de réduire l'indemnité à
concurrence de l'aggravation ». Une réduction n'est pas un refus : les deux obligations deviennent des limites.
(Le défaut d'entretien des installations, 3.1.4.3.2, peut, lui, faire refuser : il n'est pas traduit en obligation
ici et le reste.)

Usage : python relecture/assureur_b_reductions.py  (corrige les propositions en place)"""
import json
from pathlib import Path

DOSSIER = Path(__file__).resolve().parents[1] / "regles" / "propositions" / "assureur-b-habitation-2017"
LIMITES = {
    ("3.1.4", "3.1.4.3"): {
        "article": "3.1.4.3",
        "texte": "Si l’Assuré ne respecte pas ces prescriptions, sauf cas de force majeure, et si un sinistre survient "
                 "ou est aggravé de ce fait, l’indemnité due sera réduite de moitié.",
        "montant": "indemnité réduite de moitié si les conduites n'ont pas été vidangées ou protégées"},
    ("3.1.6", "3.1.6.4"): {
        "article": "3.1.6.4",
        "texte": "En cas de sinistre dont la charge est aggravée en raison de la non-utilisation de ces systèmes de "
                 "protection, la Compagnie se réserve le droit de réduire l’indemnité à concurrence de l’aggravation "
                 "de son préjudice.",
        "montant": "indemnité réduite à concurrence de l'aggravation si les protections n'étaient pas utilisées"},
}

for (fichier, article), limite in LIMITES.items():
    chemin = DOSSIER / f"{fichier}.json"
    d = json.loads(chemin.read_text(encoding="utf-8"))
    n = 0
    for g in d["proposition"]["garanties"]:
        gardees = [o for o in g.get("obligations") or [] if o.get("article") != article]
        if len(gardees) != len(g.get("obligations") or []):
            n += len(g["obligations"]) - len(gardees)
            g["obligations"] = gardees
            g.setdefault("limites", []).append(dict(limite))
    assert n, f"{fichier} : aucune obligation {article}"
    d["meta"].setdefault("relecture", {}).setdefault("modifications", []).append(
        f"{article} : la sanction réduit l'indemnité, elle ne refuse pas ; obligation remplacée par une limite (7.81)")
    d.pop("controles", None)
    chemin.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{fichier} : {n} obligation(s) {article} remplacée(s) par une limite")
