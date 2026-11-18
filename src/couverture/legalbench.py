"""Second banc, externe : LegalBench, tâche `insurance_policy_interpretation`.

Pourquoi : le golden set est écrit par nous, pour un seul contrat. LegalBench (Stanford, CC BY 4.0)
apporte des cas que nous n'avons pas écrits : une clause de police en anglais, un sinistre, et la
réponse donnée par des lecteurs recrutés (Prolific) — couvert, non couvert, ou **ambigu** quand ils ne
s'accordent pas. Cette troisième réponse est ce qui nous intéresse : elle mesure, sur des données
externes, si le système sait dire « je ne sais pas » au bon moment.

Ce que ce banc teste, et ce qu'il ne teste pas : chaque cas a sa propre clause, sans vocabulaire ni
règles Prolog écrites pour elle. On y mesure donc le principe du projet appliqué sans règles : le modèle
doit **citer mot pour mot** la phrase de la police qui fonde sa réponse, et le code vérifie la citation ;
une réponse ferme sans citation retrouvée devient « incertain ». On compare la réponse brute du modèle et
la réponse contrôlée. Faire rédiger des règles pour chacune des 138 clauses est une suite possible.

Données : téléchargées sur le poste (`couverture legalbench --telecharger`) dans
data/externes/legalbench/, avec leur attribution. Citation : Guha et al., « LegalBench », NeurIPS 2023 ;
paires construites par Madigan Brodsky (projet « Vague Contracts »).
"""

from __future__ import annotations

import csv
import io
import json
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from .juges import extraire_json
from .validation import extrait_present

TACHE = "insurance_policy_interpretation"
DOSSIER = Path("externes") / "legalbench"
FICHIER = f"{TACHE}.jsonl"
API_LIGNES = "https://datasets-server.huggingface.co/rows"
TSV = "https://huggingface.co/datasets/nguha/legalbench/resolve/main/data/{tache}/{split}.tsv"
DECISIONS = ("COUVERT", "NON_COUVERT", "INCERTAIN")

ATTRIBUTION = """# LegalBench — insurance_policy_interpretation

Données téléchargées par `couverture legalbench --telecharger`, non modifiées sinon pour la forme
(une ligne JSON par cas, réponse traduite en COUVERT / NON_COUVERT / INCERTAIN).

- Source : LegalBench (Guha et al., « LegalBench: A Collaboratively Built Benchmark for Measuring Legal
  Reasoning in Large Language Models », NeurIPS 2023), https://hazyresearch.stanford.edu/legalbench/
- Paires police-sinistre : Madigan Brodsky, projet « Vague Contracts » ; réponses de lecteurs Prolific :
  « ambigu » quand aucune réponse n'atteint une majorité sûre.
- Licence : CC BY 4.0.
"""


# --- Les données ------------------------------------------------------------------------------------

def normaliser(reponse: str) -> str | None:
    """« A » / « Yes » → COUVERT ; « B » / « No » → NON_COUVERT ; « C » / « It's ambiguous » → INCERTAIN."""
    r = str(reponse).strip().lower().rstrip(".")
    if r in ("a", "yes", "covered", "couvert"):
        return "COUVERT"
    if r in ("b", "no", "not covered", "non_couvert"):
        return "NON_COUVERT"
    if r in ("c", "it's ambiguous", "it’s ambiguous", "ambiguous", "incertain") or "ambig" in r:
        return "INCERTAIN"
    return None


def _champ(ligne: dict, *noms: str) -> str:
    for n in noms:
        for k, v in ligne.items():
            if k.strip().lower() == n:
                return str(v)
    raise KeyError(f"colonne absente : {noms[0]} (colonnes : {', '.join(ligne)})")


def depuis_lignes(lignes: list[dict], split: str) -> list[dict]:
    """Les lignes du jeu (quelle que soit leur forme d'origine) en cas du banc."""
    cas = []
    for i, l in enumerate(lignes):
        brut = _champ(l, "answer", "label")
        attendu = normaliser(brut)
        if attendu is None:
            raise ValueError(f"réponse inattendue dans LegalBench : {brut!r}")
        ident = l.get("index", l.get("idx", i))
        cas.append({"id": f"{split}-{ident}", "split": split, "policy": _champ(l, "policy", "text"),
                    "claim": _champ(l, "claim", "question"), "attendu": attendu, "reponse_brute": brut})
    return cas


def _get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "couverture-sinistre/legalbench"})
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 (adresse fixe, https)
        return r.read()


def _par_api(split: str) -> list[dict]:
    lignes, debut = [], 0
    while True:
        q = urllib.parse.urlencode({"dataset": "nguha/legalbench", "config": TACHE, "split": split,
                                    "offset": debut, "length": 100})
        d = json.loads(_get(f"{API_LIGNES}?{q}"))
        lot = [r["row"] for r in d.get("rows", [])]
        lignes += lot
        debut += len(lot)
        if not lot or debut >= d.get("num_rows_total", 0):
            return lignes


def _par_tsv(split: str) -> list[dict]:
    texte = _get(TSV.format(tache=TACHE, split=split)).decode("utf-8")
    return list(csv.DictReader(io.StringIO(texte), delimiter="\t"))


def telecharger(donnees: Path) -> Path:
    """Les deux parties (train, test) depuis Hugging Face : l'API des lignes, sinon le fichier TSV."""
    cas, erreurs = [], []
    for split in ("train", "test"):
        for source in (_par_api, _par_tsv):
            try:
                cas += depuis_lignes(source(split), split)
                break
            except Exception as e:  # noqa: BLE001
                erreurs.append(f"{split} ({source.__name__}) : {e}")
        else:
            raise RuntimeError("Téléchargement impossible :\n  " + "\n  ".join(erreurs))
    dossier = Path(donnees) / DOSSIER
    dossier.mkdir(parents=True, exist_ok=True)
    f = dossier / FICHIER
    f.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cas), encoding="utf-8")
    (dossier / "LISEZMOI.md").write_text(ATTRIBUTION, encoding="utf-8")
    return f


def charger(chemin: Path) -> list[dict]:
    """Le fichier téléchargé (.jsonl), ou un fichier LegalBench d'origine (.tsv, .csv)."""
    chemin = Path(chemin)
    texte = chemin.read_text(encoding="utf-8")
    if chemin.suffix == ".jsonl":
        return [json.loads(l) for l in texte.splitlines() if l.strip()]
    lignes = list(csv.DictReader(io.StringIO(texte), delimiter="\t" if chemin.suffix == ".tsv" else ","))
    return depuis_lignes(lignes, chemin.stem)


# --- Le juge : une réponse, une citation, et le code qui vérifie ------------------------------------------

SYSTEME_LEGALBENCH = """Tu es gestionnaire de sinistres. On te donne une clause de police d'assurance et une déclaration de sinistre, en anglais.
Dis si la clause couvre le sinistre.

Réponses possibles :
- "COUVERT" : la clause couvre clairement ce sinistre ;
- "NON_COUVERT" : la clause ne le couvre clairement pas ;
- "INCERTAIN" : un lecteur raisonnable pourrait lire la clause dans un sens comme dans l'autre (un mot vague, un cas limite que la clause ne tranche pas), ou il manque un fait pour trancher.

Règles :
1. Ne réponds COUVERT ou NON_COUVERT que si une phrase de la clause le fonde. Recopie cette phrase **mot pour mot**, en anglais, sans la traduire ni la résumer (tu peux couper avec « … »).
2. Si le sens d'un mot de la clause est discutable pour ce sinistre, réponds INCERTAIN et cite ce mot ou ce passage.
3. Ne suppose aucun fait que la déclaration ne donne pas.

Réponds uniquement en JSON :
{"decision": "COUVERT|NON_COUVERT|INCERTAIN", "citation": "…passage exact de la clause…", "raison": "une phrase, en français"}"""


def juger(cas: dict, llm) -> dict:
    """La réponse du modèle, puis le contrôle : une réponse ferme dont la citation n'est pas dans la
    clause devient INCERTAIN (pas de preuve, pas de verdict)."""
    message = f"## Clause de la police\n{cas['policy']}\n\n## Déclaration de sinistre\n{cas['claim']}"
    debut = time.perf_counter()
    try:
        d = extraire_json(llm.completer(SYSTEME_LEGALBENCH, message))
        brute = str(d.get("decision", "")).strip().upper()
        brute = brute if brute in DECISIONS else "ERREUR"
        citation = str(d.get("citation") or "").strip()
        raison = str(d.get("raison") or "")
    except Exception as e:  # noqa: BLE001
        brute, citation, raison = "ERREUR", "", f"réponse illisible : {e}"
    trouvee = bool(citation) and extrait_present(citation, cas["policy"])
    if brute == "ERREUR":
        controlee = "INCERTAIN"
    elif brute != "INCERTAIN" and not trouvee:
        controlee = "INCERTAIN"
    else:
        controlee = brute
    return {"id": cas["id"], "attendu": cas["attendu"], "brute": brute, "decision": controlee,
            "citation": citation, "citation_trouvee": trouvee, "raison": raison,
            "duree_s": round(time.perf_counter() - debut, 2)}


# --- Les métriques --------------------------------------------------------------------------------------

def metriques(lignes: list[dict], cle: str = "decision") -> dict:
    """Mêmes définitions que le banc (docs/METRIQUES.md), plus l'exactitude équilibrée de LegalBench
    (moyenne des rappels par classe : un jeu déséquilibré ne flatte pas un modèle qui répond toujours pareil)."""
    n = len(lignes)
    if not n:
        return {"n": 0}
    rappels = {}
    for c in DECISIONS:
        de_c = [l for l in lignes if l["attendu"] == c]
        if de_c:
            rappels[c] = round(sum(l[cle] == c for l in de_c) / len(de_c), 3)
    dit_incertain = [l for l in lignes if l[cle] == "INCERTAIN"]
    return {
        "n": n,
        "exactitude": round(sum(l[cle] == l["attendu"] for l in lignes) / n, 3),
        "exactitude_equilibree": round(sum(rappels.values()) / len(rappels), 3),
        "faux_couverts": sum(l[cle] == "COUVERT" and l["attendu"] != "COUVERT" for l in lignes),
        "faux_refus": sum(l[cle] == "NON_COUVERT" and l["attendu"] == "COUVERT" for l in lignes),
        "rappel_par_classe": rappels,
        "precision_incertain": round(sum(l["attendu"] == "INCERTAIN" for l in dit_incertain) / len(dit_incertain), 3)
        if dit_incertain else None,
        "taux_incertain": round(len(dit_incertain) / n, 3),
        "erreurs": sum(l.get("brute") == "ERREUR" for l in lignes),
    }


def confusion(lignes: list[dict], cle: str = "decision") -> dict:
    return {a: {o: sum(l["attendu"] == a and l[cle] == o for l in lignes) for o in DECISIONS + ("ERREUR",)}
            for a in DECISIONS}


def passer(cas: list[dict], llm, paralleles: int = 4) -> dict:
    with ThreadPoolExecutor(max_workers=max(1, paralleles)) as ex:
        lignes = list(ex.map(lambda c: juger(c, llm), cas))
    fermes = [l for l in lignes if l["brute"] in ("COUVERT", "NON_COUVERT")]
    return {
        "tache": TACHE, "date": datetime.now().isoformat(timespec="seconds"),
        "modele": getattr(llm, "nom", "?"), "n": len(lignes),
        "brute": metriques(lignes, "brute"), "controlee": metriques(lignes, "decision"),
        "confusion_brute": confusion(lignes, "brute"), "confusion_controlee": confusion(lignes, "decision"),
        "citations_introuvables": sum(not l["citation_trouvee"] for l in fermes),
        "reponses_fermes": len(fermes),
        "changees_par_le_controle": sum(l["brute"] != l["decision"] for l in lignes),
        "cas": lignes,
    }


# --- Le rapport -------------------------------------------------------------------------------------------

LIBELLE = {"COUVERT": "couvert", "NON_COUVERT": "non couvert", "INCERTAIN": "ambigu / incertain", "ERREUR": "erreur"}


def _pct(x) -> str:
    return "—" if x is None else f"{x * 100:.0f} %"


def rapport_md(r: dict) -> str:
    b, c = r["brute"], r["controlee"]
    l = [f"# Banc LegalBench · {r['tache']} · {r['modele']}", "",
         f"{r['date']} · {r['n']} cas · données CC BY 4.0 (Guha et al., 2023 ; « Vague Contracts »)", "",
         "| | Exactitude | Équilibrée | Couverts à tort | Refus à tort | Rappel « ambigu » | Précision « incertain » | Incertains |",
         "|---|---|---|---|---|---|---|---|"]
    for nom, m in (("Réponse du modèle", b), ("Après contrôle des citations", c)):
        l.append(f"| {nom} | {_pct(m['exactitude'])} | {_pct(m['exactitude_equilibree'])} | {m['faux_couverts']} | "
                 f"{m['faux_refus']} | {_pct(m['rappel_par_classe'].get('INCERTAIN'))} | {_pct(m['precision_incertain'])} | "
                 f"{_pct(m['taux_incertain'])} |")
    l += ["", f"Réponses fermes du modèle : {r['reponses_fermes']}, dont **{r['citations_introuvables']} sans citation "
          f"retrouvée dans la clause** ; {r['changees_par_le_controle']} réponse(s) changée(s) par le contrôle.", ""]
    for titre, cle in (("Confusion, après contrôle", "confusion_controlee"), ("Confusion, réponse du modèle", "confusion_brute")):
        l += [f"## {titre}", "", "| attendu \\ obtenu | " + " | ".join(LIBELLE[o] for o in DECISIONS + ("ERREUR",)) + " |",
              "|---|" + "---|" * 4]
        for a, ligne in r[cle].items():
            l.append(f"| {LIBELLE[a]} | " + " | ".join(str(ligne[o]) for o in DECISIONS + ("ERREUR",)) + " |")
        l.append("")
    erreurs = [x for x in r["cas"] if x["decision"] != x["attendu"]]
    l += [f"## Les {len(erreurs)} écarts (après contrôle)", ""]
    for x in erreurs:
        cit = f" — « {x['citation'][:140]} »" + ("" if x["citation_trouvee"] else " (introuvable)") if x["citation"] else ""
        l.append(f"- `{x['id']}` attendu {LIBELLE[x['attendu']]}, obtenu {LIBELLE[x['decision']]}"
                 f" (modèle : {LIBELLE.get(x['brute'], x['brute'])}){cit}. {x['raison']}")
    return "\n".join(l) + "\n"


def enregistrer(donnees: Path, r: dict) -> tuple[Path, Path]:
    dossier = Path(donnees) / "bancs"
    dossier.mkdir(parents=True, exist_ok=True)
    nom = f"{datetime.now():%Y%m%d-%H%M%S}-legalbench-{str(r['modele']).replace(':', '-').replace('/', '-')}"
    j, m = dossier / f"{nom}.json", dossier / f"{nom}.md"
    j.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    m.write_text(rapport_md(r), encoding="utf-8")
    return j, m


def resume_console(r: dict, md: Path | None = None) -> str:
    b, c = r["brute"], r["controlee"]
    l = [f"Banc LegalBench · {r['tache']} · {r['modele']} · {r['n']} cas",
         f"Réponse du modèle    : {_pct(b['exactitude'])} justes (équilibrée {_pct(b['exactitude_equilibree'])}) · "
         f"couverts à tort {b['faux_couverts']} · refus à tort {b['faux_refus']} · ambigus reconnus {_pct(b['rappel_par_classe'].get('INCERTAIN'))}",
         f"Après contrôle       : {_pct(c['exactitude'])} justes (équilibrée {_pct(c['exactitude_equilibree'])}) · "
         f"couverts à tort {c['faux_couverts']} · refus à tort {c['faux_refus']} · ambigus reconnus {_pct(c['rappel_par_classe'].get('INCERTAIN'))}",
         f"Citations introuvables : {r['citations_introuvables']} sur {r['reponses_fermes']} réponses fermes"]
    if md:
        l.append(f"Rapport : {md}")
    return "\n".join(l)
