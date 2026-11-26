"""Les jeux de cas, et le rejeu d'une chaîne sur un jeu (utilisé par le banc, couche « chaîne »).

- `data/sinistres.jsonl` : les sinistres, indépendants de tout contrat ;
- `data/annotations/<contrat_id>.jsonl` : pour ce contrat, la décision attendue et les
  clauses qui doivent être citées ({"sinistre_id", "attendu", "clauses_attendues", "note"}).
  "acceptables" (facultatif) : d'autres décisions défendables quand le contrat seul ne permet pas
  de trancher (une option des conditions particulières, une serrure dont on ne sait pas le type).
  Un INCERTAIN honnête n'y est alors pas compté comme une erreur ; un COUVERT à tort l'est toujours.

Ce découpage tient à l'échelle : un nouveau contrat = un fichier d'annotations de plus.
"""

from __future__ import annotations

import time

import json
from collections import Counter
from pathlib import Path


def lire_jsonl(chemin: str | Path) -> list[dict]:
    """Lit un fichier JSON Lines : un objet par ligne non vide."""
    with open(chemin, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


# Les jeux écrits sans voir les règles, par deux annotateurs à l'aveugle : sans faits idéaux, chaîne complète seule.
# « aveugle » est le second (25 nov. 2026, 7.185) : trois cas du premier avaient fini par servir à corriger une règle.
# « neuf » est le troisième (7.186) : le second a montré de vrais défauts, corrigés d'après lui ; il est donc « vu ».
# « quatre » est le quatrième (7.187), après les corrections tirées du troisième ; « cinq », le cinquième (7.215),
# écrit après la mesure du quatrième et les corrections de justesse.
JEUX_FERMES = ("ferme", "aveugle", "neuf", "quatre", "cinq")
# Les jeux jamais regardés : ils ne se passent qu'une fois, pour la mesure finale (`juger --mesure-finale`).
JEUX_JAMAIS_VUS = ("cinq",)
JEUX = ("mise_au_point", "validation", "redaction", "golden", *JEUX_FERMES)


def fichiers_jeu(donnees: str | Path, contrat_id: str, jeu: str = "mise_au_point") -> tuple[Path, Path]:
    """Sinistres et annotations d'un jeu de cas.
    - mise_au_point : data/sinistres.jsonl, data/annotations/<contrat>.jsonl, les cas qui ont servi à écrire
      les consignes et les règles ;
    - validation : data/validation/…, des cas écrits après coup, à ne pas utiliser pour corriger
      (sinon ils deviennent des cas de mise au point et il en faut de nouveaux) ;
    - redaction : data/redaction/…, des cas des garanties dont les règles sont rédigées par le modèle,
      écrits d'après le texte du contrat avant la rédaction ;
    - golden : data/golden/…, le banc d'essai figé (tous les cas, étiquetés), voir `couverture banc` ;
    - ferme : data/ferme/…, des cas écrits sans voir les règles, par deux annotateurs à l'aveugle (7.79),
      sans faits idéaux : `couverture banc --jeu ferme` ;
    - aveugle : data/aveugle/…, un second jeu écrit de la même façon (7.185) ; mesuré une fois, puis vu (7.186) ;
    - neuf : data/neuf/…, le troisième, écrit après les corrections tirées du second ; mesuré une fois, puis vu ;
    - quatre : data/quatre/…, le quatrième (7.187) ; mesuré une fois (7.207), puis vu ;
    - cinq : data/cinq/…, le cinquième (7.215), jamais regardé pour régler."""
    if jeu not in JEUX:
        raise ValueError(f"jeu inconnu : {jeu}")
    racine = Path(donnees) / ("" if jeu == "mise_au_point" else jeu)
    return racine / "sinistres.jsonl", racine / "annotations" / f"{contrat_id}.jsonl"


def charger_cas(sinistres: str | Path, annotations: str | Path) -> list[dict]:
    """Les cas d'un jeu : chaque annotation, complétée par la déclaration de son sinistre."""
    par_id = {s["id"]: s for s in lire_jsonl(sinistres)}
    cas = []
    for a in lire_jsonl(annotations):
        s = par_id[a["sinistre_id"]]
        cas.append({**a, "id": a["sinistre_id"], "sinistre": s["sinistre"], "famille": s.get("famille", "")})
    return cas


def _cite(attendue: str, citees: set[str]) -> bool:
    # « 4.4 » est cité si la clause 4.4, ou l'un de ses morceaux (4.4~2, 4.4/terme), l'est.
    return any(c == attendue or c.startswith(attendue + "~") or c.startswith(attendue + "/") for c in citees)


def _rejouer(pipeline, cas: list[dict], paralleles: int) -> list:
    """Analyse chaque cas, `paralleles` à la fois ; rend les résultats dans l'ordre des cas. Lève `ErreurLLM` si
    toutes les analyses ont échoué chez le fournisseur."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    from ..progression import Barre

    from ..llm import CleRefusee, ErreurLLM
    from ..models import Decision, Faits, Resultat, Verdict

    def analyser(c: dict):
        """Une panne du fournisseur sur un cas (limite de débit persistante, réseau) ne fait pas
        perdre les autres : le cas est compté en erreur. Une clé refusée arrête tout."""
        try:
            debut = time.perf_counter()
            r = pipeline.analyser(c["sinistre"])
            r.durees_ms = {**r.durees_ms, "total": int((time.perf_counter() - debut) * 1000)}
            return r
        except CleRefusee:
            raise
        except ErreurLLM as e:
            v = Verdict(decision=Decision.INCERTAIN, justification="Erreur du fournisseur.", confiance=0.0,
                        mode="erreur", avertissements=[f"Erreur du modèle : {e}"])
            return Resultat(sinistre=c["sinistre"], faits=Faits(), clauses_consultees=[], verdict=v)

    barre = Barre(len(cas), "Évaluation")
    resultats: list = [None] * len(cas)
    with ThreadPoolExecutor(max_workers=max(1, paralleles)) as pool:
        futurs = {pool.submit(analyser, c): i for i, c in enumerate(cas)}
        for f in as_completed(futurs):
            i = futurs[f]
            resultats[i] = f.result()
            barre.avancer(f"{cas[i]['id']} → {resultats[i].verdict.decision.value}")
    barre.terminer()
    if resultats and all(r.verdict.mode == "erreur" for r in resultats):
        raise ErreurLLM(resultats[0].verdict.avertissements[0].removeprefix("Erreur du modèle : "))
    return resultats


def _ligne_du_cas(c: dict, r) -> dict:
    """Le résultat d'un cas, pour le rapport : attendu, obtenu, clauses citées, questions, durées."""
    v = r.verdict
    obtenu = v.decision.value
    initiale = (v.decision_initiale or v.decision).value
    citees = {ci.clause_id for ci in v.citations if ci.valide}
    attendues = c.get("clauses_attendues", [])
    trouvees = [a for a in attendues if _cite(a, citees)]
    return {
        "id": c["id"],
        "attendu": c["attendu"],
        "obtenu": obtenu,
        "avant_controle": initiale,
        "ok": obtenu == c["attendu"] or obtenu in c.get("acceptables", []),
        "acceptable": obtenu != c["attendu"] and obtenu in c.get("acceptables", []),
        "clauses_attendues": attendues,
        "clauses_citees": sorted(citees),
        "rappel_clauses": round(len(trouvees) / len(attendues), 2) if attendues else None,
        "citations_rejetees": sum(not ci.valide for ci in v.citations),
        "confiance": v.confiance,
        "erreur": v.mode == "erreur",
        # Pour le banc : ce que le modèle a lu, et les questions posées.
        "faits_lus": r.faits.model_dump() if r.faits else {},
        "questions": list(v.informations_manquantes),
        "avertissements": list(v.avertissements),
        "durees_ms": dict(r.durees_ms),
    }


def _bilan(lignes: list[dict], confusion: Counter) -> dict:
    """Les chiffres du jeu : exactitude, couverts et refus à tort, taux d'« incertain », rappel des clauses."""
    n = len(lignes)
    rappels = [l["rappel_clauses"] for l in lignes if l["rappel_clauses"] is not None]
    taux = lambda k: round(k / n, 3) if n else 0.0  # noqa: E731
    return {
        "n": n,
        "exactitude": taux(sum(l["ok"] for l in lignes)),
        "exactitude_stricte": taux(sum(l["obtenu"] == l["attendu"] for l in lignes)),
        # L'autre erreur coûteuse : refuser à tort un sinistre couvert.
        "faux_refus": sum(l["obtenu"] == "NON_COUVERT" and l["attendu"] == "COUVERT" for l in lignes),
        "exactitude_avant_controle": taux(sum(l["avant_controle"] == l["attendu"] for l in lignes)),
        # L'erreur la plus coûteuse : dire « couvert » à tort, c'est une promesse au client.
        "faux_couverts": sum(l["obtenu"] == "COUVERT" and l["attendu"] != "COUVERT" for l in lignes),
        "faux_couverts_avant_controle": sum(l["avant_controle"] == "COUVERT" and l["attendu"] != "COUVERT" for l in lignes),
        "taux_incertain": taux(sum(l["obtenu"] == "INCERTAIN" for l in lignes)),
        "erreurs_fournisseur": sum(l["erreur"] for l in lignes),
        "rappel_clauses_moyen": round(sum(rappels) / len(rappels), 3) if rappels else None,
        "citations_rejetees": sum(l["citations_rejetees"] for l in lignes),
        "confusion": {f"{a}->{o}": k for (a, o), k in sorted(confusion.items())},
        "cas": lignes,
    }


def evaluer(pipeline, cas: list[dict], paralleles: int = 1) -> dict:
    """Rejoue les cas ; `paralleles` cas à la fois (les analyses sont indépendantes, et chacune
    attend surtout le modèle). L'ordre des résultats reste celui des cas."""
    resultats = _rejouer(pipeline, cas, paralleles)
    lignes = [_ligne_du_cas(c, r) for c, r in zip(cas, resultats)]
    return _bilan(lignes, Counter((x["attendu"], x["obtenu"]) for x in lignes))
