"""Évaluation : les mêmes sinistres, rejoués sur chaque contrat.

- `data/sinistres.jsonl` : les sinistres, indépendants de tout contrat ;
- `data/annotations/<contrat_id>.jsonl` : pour ce contrat, la décision attendue et les
  clauses qui doivent être citées ({"sinistre_id", "attendu", "clauses_attendues", "note"}).

Ce découpage tient à l'échelle : un nouveau contrat = un fichier d'annotations de plus.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


def lire_jsonl(chemin: str | Path) -> list[dict]:
    with open(chemin, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def charger_cas(sinistres: str | Path, annotations: str | Path) -> list[dict]:
    par_id = {s["id"]: s for s in lire_jsonl(sinistres)}
    cas = []
    for a in lire_jsonl(annotations):
        s = par_id[a["sinistre_id"]]
        cas.append({**a, "id": a["sinistre_id"], "sinistre": s["sinistre"], "famille": s.get("famille", "")})
    return cas


def _cite(attendue: str, citees: set[str]) -> bool:
    # « 4.4 » est cité si la clause 4.4, ou l'un de ses morceaux (4.4~2, 4.4/terme), l'est.
    return any(c == attendue or c.startswith(attendue + "~") or c.startswith(attendue + "/") for c in citees)


def evaluer(pipeline, cas: list[dict]) -> dict:
    lignes, confusion = [], Counter()
    for c in cas:
        r = pipeline.analyser(c["sinistre"])
        v = r.verdict
        obtenu = v.decision.value
        initiale = (v.decision_initiale or v.decision).value
        citees = {ci.clause_id for ci in v.citations if ci.valide}
        attendues = c.get("clauses_attendues", [])
        trouvees = [a for a in attendues if _cite(a, citees)]
        confusion[(c["attendu"], obtenu)] += 1
        lignes.append({
            "id": c["id"],
            "attendu": c["attendu"],
            "obtenu": obtenu,
            "avant_controle": initiale,
            "ok": obtenu == c["attendu"],
            "clauses_attendues": attendues,
            "clauses_citees": sorted(citees),
            "rappel_clauses": round(len(trouvees) / len(attendues), 2) if attendues else None,
            "citations_rejetees": sum(not ci.valide for ci in v.citations),
            "avant_relecture": v.decision_avant_relecture.value if v.decision_avant_relecture else None,
            "contestations": sum(c.relecture == "contestee" for c in v.conditions),
            "confiance": v.confiance,
        })
    n = len(lignes)
    rappels = [l["rappel_clauses"] for l in lignes if l["rappel_clauses"] is not None]
    taux = lambda k: round(k / n, 3) if n else 0.0  # noqa: E731
    return {
        "n": n,
        "exactitude": taux(sum(l["ok"] for l in lignes)),
        "exactitude_avant_controle": taux(sum(l["avant_controle"] == l["attendu"] for l in lignes)),
        # L'erreur la plus coûteuse : dire « couvert » à tort, c'est une promesse au client.
        "faux_couverts": sum(l["obtenu"] == "COUVERT" and l["attendu"] != "COUVERT" for l in lignes),
        "faux_couverts_avant_controle": sum(l["avant_controle"] == "COUVERT" and l["attendu"] != "COUVERT" for l in lignes),
        "taux_incertain": taux(sum(l["obtenu"] == "INCERTAIN" for l in lignes)),
        "rappel_clauses_moyen": round(sum(rappels) / len(rappels), 3) if rappels else None,
        "citations_rejetees": sum(l["citations_rejetees"] for l in lignes),
        "conditions_contestees": sum(l["contestations"] for l in lignes),
        "decisions_changees_par_relecture": sum(bool(l["avant_relecture"]) for l in lignes),
        # La relecture a-t-elle évité des « couvert » à tort ? Ceux qu'elle a fait passer à autre chose, et qui n'étaient pas couverts.
        "faux_couverts_evites_par_relecture": sum(
            l["avant_relecture"] == "COUVERT" and l["attendu"] != "COUVERT" for l in lignes),
        "confusion": {f"{a}->{o}": k for (a, o), k in sorted(confusion.items())},
        "cas": lignes,
    }
