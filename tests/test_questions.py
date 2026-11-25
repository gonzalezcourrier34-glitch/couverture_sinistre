"""Ce qu'on demande au client doit pouvoir servir (7.125).

Pour chaque contrat, sur chaque événement seul, sur chaque événement avec un bien et un lieu, et sur les faits idéaux
de tous les cas : aucune question ni réserve dont la réponse serait jetée (hors sujet pour l'événement), aucune
réserve sur un fait déjà connu, aucun bouton pour une question sans réponses possibles, et jamais « à préciser »
sans rien à demander. L'oracle Python décide : pas besoin de SWI-Prolog ni du modèle."""

from __future__ import annotations

import json

import pytest

from couverture.analyse import chaine, prolog
from couverture.api import service
from moteur_reference import Contrat, Explorateur

VOC = prolog.vocabulaire()


def scenarios(contrat_id: str):
    for e in VOC["evenement"]["valeurs"]:
        yield f"{e} seul", {"evenement": [e]}
        yield f"{e}, mobilier, logement", {"evenement": [e], "bien": ["mobilier"], "lieu": ["logement"]}
    for f in sorted((prolog.DOSSIER / "cas").rglob(f"{contrat_id}.jsonl")):
        for ligne in f.read_text(encoding="utf-8").splitlines():
            if ligne.strip():
                cas = json.loads(ligne)
                yield cas["sinistre_id"], cas["faits"]


@pytest.mark.parametrize("contrat_id", prolog.contrats_regles())
def test_chaque_point_demande_peut_servir(contrat_id):
    contrat, defauts, vus = Contrat(prolog.fichier_regles(contrat_id)), [], 0
    for nom, faits in scenarios(contrat_id):
        faits, _ = prolog.filtrer_faits(faits, VOC)
        d = Explorateur(contrat, faits).decider()
        vus += 1
        ev = faits.get("evenement") or []
        lus = prolog.evenements_etendus(ev if isinstance(ev, list) else [ev], VOC)
        points = chaine.points_a_preciser(d, VOC, faits)
        for v, nature in points:
            pour = set(VOC.get(v, {}).get("pour", []))
            if v in VOC and pour and lus and not pour & lus:
                defauts.append(f"{nom} : {nature} « {v} » hors sujet, la réponse serait retirée")
            if nature == "reserve" and faits.get(v) not in (None, "", []):
                defauts.append(f"{nom} : réserve « {v} » déjà connue ({faits[v]})")
        for p in service.a_preciser(d, VOC, faits):
            if not p["valeurs"]:
                defauts.append(f"{nom} : « {p['variable']} » proposée sans réponses possibles")
            connu = faits.get(p["variable"])
            if connu and set(p["valeurs"]) & set(connu if isinstance(connu, list) else [connu]):
                defauts.append(f"{nom} : « {p['variable']} » repropose la réponse déjà connue ({connu})")
        if d["decision"] == "INCERTAIN" and not points and not d.get("non_traduits"):
            defauts.append(f"{nom} : à préciser, sans rien à demander")
    assert vus > 40 and not defauts, "\n".join(defauts[:20])
