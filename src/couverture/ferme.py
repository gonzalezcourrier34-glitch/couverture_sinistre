"""Le jeu fermé : des cas écrits sans voir les règles (DEMARCHE 7.79).

Deux annotateurs à l'aveugle, d'après le seul texte des conditions générales :
1. un agent (Claude, sans accès aux règles ni au golden set) écrit les déclarations et sa réponse :
   `data/ferme/cas_agent.jsonl` ;
2. un second modèle (Mistral Large) répond aux mêmes déclarations sans voir la première réponse :
   `uv run python -m couverture.ferme annoter` → `data/ferme/avis_second.jsonl` ;
3. `comparer` : les accords entrent dans le jeu ; les désaccords vont dans `data/ferme/arbitrage.csv`, avec les
   deux réponses et leurs citations, pour un arbitrage sur le texte (colonne `choix` : agent, second, ecarter) ;
4. `exporter` : `data/ferme/sinistres.jsonl` et `data/ferme/annotations/<contrat>.jsonl`, au format des jeux de
   cas (`evaluation.fichiers_jeu(…, "ferme")`), sans faits idéaux : ils mettraient le vocabulaire des règles
   dans le jeu. Le banc le rejoue en chaîne complète : `couverture banc --jeu ferme`.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

DOSSIER = Path("data") / "ferme"


def contrats_des_cas(cas: list[dict]) -> dict[str, str]:
    """Le nom court d'un contrat dans les cas (« assureur-a ») vers son identifiant. La table était écrite ici, pour
    trois contrats : elle se lit maintenant dans les cas et dans le dossier des règles, et un contrat de plus ne
    demande pas de toucher au code (7.177)."""
    from . import prolog
    connus = sorted(f.stem for f in prolog.DOSSIER.glob("*.pl") if f != prolog.MOTEUR)
    table = {}
    for court in sorted({c["contrat"] for c in cas}):
        trouves = [i for i in connus if i.startswith(court + "-")]
        if len(trouves) != 1:
            raise LookupError(f"« {court} » : {len(trouves)} fichier(s) de règles dans {prolog.DOSSIER} (un seul attendu)")
        table[court] = trouves[0]
    return table


REPONSES = ("COUVERT", "NON_COUVERT", "INCERTAIN")

SYSTEME_SECOND_AVIS = """Tu es gestionnaire de sinistres. On te donne les conditions générales d'un contrat d'assurance habitation et la déclaration d'un sinistre. Dis si, d'après le seul texte de ces conditions générales, le sinistre est couvert.

Réponds :
- COUVERT : une garantie s'applique et aucune exclusion ne joue, d'après ce que dit la déclaration ;
- NON_COUVERT : aucune garantie ne s'applique, ou une exclusion joue ;
- INCERTAIN : il manque à la déclaration une information qui change la réponse (donne la question qui tranche), ou la réponse dépend d'une option ou des conditions particulières, qu'on ne connaît pas.

Convention du jeu : les garanties de base du contrat sont considérées comme souscrites (et, pour un contrat qui distingue le contenu ou la responsabilité civile vie privée, ceux-ci aussi) ; les options et les formules (Privilège, Active, Confort…) sont inconnues : si la réponse en dépend, c'est INCERTAIN.

Ce que la déclaration ne dit pas reste inconnu : ne le suppose pas. Mais si le texte permet de trancher, tranche. Relis l'article de la garantie et les exclusions (générales et propres à la garantie) avant de conclure. Si une seconde réponse est défendable, mets-la dans "acceptables".

Réponds uniquement par un objet JSON : {"attendu": "COUVERT", "acceptables": [], "articles": ["2.3"], "citation": "phrase exacte du contrat, au plus 40 mots", "question_attendue": "", "justification": "une ou deux phrases"}"""

SCHEMA = {"type": "object", "additionalProperties": False,
          "required": ["attendu", "acceptables", "articles", "citation", "question_attendue", "justification"],
          "properties": {"attendu": {"type": "string", "enum": list(REPONSES)},
                         "acceptables": {"type": "array", "items": {"type": "string", "enum": list(REPONSES)}},
                         "articles": {"type": "array", "items": {"type": "string"}},
                         "citation": {"type": "string"}, "question_attendue": {"type": "string"},
                         "justification": {"type": "string"}}}


def lire(chemin: Path) -> list[dict]:
    return [json.loads(l) for l in chemin.read_text(encoding="utf-8").splitlines() if l.strip()] if chemin.exists() else []


def ecrire(chemin: Path, lignes: list[dict]) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in lignes), encoding="utf-8")


def annoter(modele: str, paralleles: int = 2) -> None:
    """Le second avis : chaque déclaration, avec le texte entier des conditions générales, sans la première
    réponse. Reprend là où il s'était arrêté (les cas déjà annotés sont gardés)."""
    from .base import Base
    from .llm import MistralLLM, completer_avec_schema, extraire_json

    cas = lire(DOSSIER / "cas_agent.jsonl")
    sortie = DOSSIER / "avis_second.jsonl"
    faits = {a["id"]: a for a in lire(sortie)}
    # Le texte entier d'un contrat (jusqu'à 70 000 tokens) à chaque appel : 120 s ne suffisaient pas (19 nov.).
    base, llm = Base(Path("data") / "base.sqlite"), MistralLLM(modele=modele, timeout=600)
    textes = {c: base.texte_brut(i) for c, i in contrats_des_cas(cas).items()}
    a_faire = [c for c in cas if c["id"] not in faits]
    print(f"{len(a_faire)} cas à annoter par {modele} ({len(faits)} déjà faits)…", flush=True)

    def un(c: dict) -> dict | None:
        message = f"## Conditions générales\n{textes[c['contrat']]}\n\n## Déclaration\n{c['declaration']}"
        try:
            r = extraire_json(completer_avec_schema(llm, SYSTEME_SECOND_AVIS, message, SCHEMA))
        except Exception as e:  # noqa: BLE001 — un cas en échec n'arrête pas les autres ; relancer le reprendra
            print(f"  {c['id']} : échec ({type(e).__name__}: {e}) ; à relancer", flush=True)
            return None
        return {"id": c["id"], "modele": modele, **{k: r.get(k) for k in SCHEMA["required"]}}

    echecs = 0
    with ThreadPoolExecutor(max_workers=paralleles) as ex:
        for i, r in enumerate(ex.map(un, a_faire), 1):
            if r is None:
                echecs += 1
                continue
            faits[r["id"]] = r
            ecrire(sortie, [faits[c["id"]] for c in cas if c["id"] in faits])  # sauvé à chaque cas
            print(f"  {i}/{len(a_faire)} {r['id']} → {r['attendu']}", flush=True)
    if echecs:
        print(f"{echecs} cas en échec : relancer `annoter` (les cas faits sont gardés).")


def accord(a: dict, b: dict) -> str | None:
    """« strict » si les deux réponses sont les mêmes ; « souple » si la réponse de l'un est acceptée par
    l'autre ; None : désaccord, à arbitrer."""
    if a["attendu"] == b["attendu"]:
        return "strict"
    if a["attendu"] in (b.get("acceptables") or []) or b["attendu"] in (a.get("acceptables") or []):
        return "souple"
    return None


def comparer() -> None:
    cas, avis = lire(DOSSIER / "cas_agent.jsonl"), {a["id"]: a for a in lire(DOSSIER / "avis_second.jsonl")}
    manquants = [c["id"] for c in cas if c["id"] not in avis]
    if manquants:
        sys.exit(f"Second avis manquant pour {len(manquants)} cas : lancer `annoter` d'abord.")
    desaccords, compte = [], {"strict": 0, "souple": 0, None: 0}
    for c in cas:
        k = accord(c, avis[c["id"]])
        compte[k] += 1
        if k is None:
            desaccords.append((c, avis[c["id"]]))
    chemin = DOSSIER / "arbitrage.csv"
    anciens = {}
    if chemin.exists():
        with chemin.open(encoding="utf-8-sig", newline="") as f:
            anciens = {l["id"]: l.get("choix", "") for l in csv.DictReader(f, delimiter=";")}
    with chemin.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["id", "declaration", "agent_reponse", "agent_articles", "agent_citation", "agent_justification",
                    "second_reponse", "second_articles", "second_citation", "second_justification", "choix"])
        for c, b in desaccords:
            w.writerow([c["id"], c["declaration"], c["attendu"], ", ".join(c.get("articles") or []), c.get("citation", ""),
                        c.get("justification", ""), b["attendu"], ", ".join(b.get("articles") or []),
                        b.get("citation", ""), b.get("justification", ""), anciens.get(c["id"], "")])
    print(f"{len(cas)} cas : {compte['strict']} accords stricts, {compte['souple']} accords souples, "
          f"{compte[None]} désaccords → {chemin} (colonne « choix » : agent, second ou ecarter)")


def exporter() -> None:
    cas, avis = lire(DOSSIER / "cas_agent.jsonl"), {a["id"]: a for a in lire(DOSSIER / "avis_second.jsonl")}
    choix = {}
    chemin = DOSSIER / "arbitrage.csv"
    if chemin.exists():
        with chemin.open(encoding="utf-8-sig", newline="") as f:
            choix = {l["id"]: (l.get("choix") or "").strip().lower() for l in csv.DictReader(f, delimiter=";")}
    contrats = contrats_des_cas(cas)
    sinistres, annotations, ecartes, en_attente = [], {c: [] for c in contrats.values()}, [], []
    for c in cas:
        b = avis.get(c["id"])
        if b is None:
            en_attente.append(c["id"])
            continue
        k = accord(c, b)
        if k is None:
            ch = choix.get(c["id"], "")
            if ch not in ("agent", "second", "ecarter"):
                en_attente.append(c["id"])
                continue
            if ch == "ecarter":
                ecartes.append(c["id"])
                continue
            retenu, origine = (c if ch == "agent" else b), f"arbitré : {ch}"
        else:
            retenu, origine = c, f"accord {k}"
        acceptables = sorted(set(c.get("acceptables") or []) | set(b.get("acceptables") or [])
                             | ({c["attendu"], b["attendu"]} if k == "souple" else set()) - {retenu["attendu"]})
        contrat = contrats[c["contrat"]]
        sinistres.append({"id": c["id"], "famille": ", ".join(retenu.get("articles") or []), "source": "ferme",
                          "sinistre": c["declaration"]})
        annotations[contrat].append({
            "sinistre_id": c["id"], "attendu": retenu["attendu"], "acceptables": acceptables,
            "clauses_attendues": retenu.get("articles") or [],
            "questions_attendues": [q for q in [retenu.get("question_attendue")] if q],
            "themes": [c.get("theme") or "base"], "origine": "ferme", "auteur": "agent+mistral-large",
            "note": retenu.get("justification", ""),
            "statut": f"jeu fermé, écrit sans voir les règles ; {origine}"})
    if en_attente:
        print(f"⚠ {len(en_attente)} cas en attente (second avis ou arbitrage) : {', '.join(en_attente)}")
    ecrire(DOSSIER / "sinistres.jsonl", sinistres)
    for contrat, lignes in annotations.items():
        ecrire(DOSSIER / "annotations" / f"{contrat}.jsonl", lignes)
    print(f"Jeu fermé : {len(sinistres)} cas ({', '.join(f'{k} : {len(v)}' for k, v in annotations.items())}) ; "
          f"{len(ecartes)} écarté(s).")


def main(argv: list[str] | None = None) -> None:
    from .config import charger_env

    charger_env(".env")
    p = argparse.ArgumentParser(prog="python -m couverture.ferme", description=__doc__.splitlines()[0])
    sous = p.add_subparsers(dest="commande", required=True)
    pa = sous.add_parser("annoter", help="Second avis par un autre modèle, à l'aveugle")
    pa.add_argument("--modele", default="mistral-large-latest")
    pa.add_argument("--paralleles", type=int, default=2)
    sous.add_parser("comparer", help="Accords et désaccords ; écrit arbitrage.csv")
    sous.add_parser("exporter", help="Écrit le jeu fermé au format du banc")
    a = p.parse_args(argv)
    if a.commande == "annoter":
        annoter(a.modele, a.paralleles)
    elif a.commande == "comparer":
        comparer()
    else:
        exporter()


if __name__ == "__main__":
    main()
