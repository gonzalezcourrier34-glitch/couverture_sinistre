"""Le banc d'essai : le golden set, rejoué couche par couche, avec des portes à franchir.

    data/golden/sinistres.jsonl, annotations/<contrat>.jsonl   les cas, étiquetés (garantie, thèmes, origine, auteur)
    regles/cas/golden/<contrat>.jsonl                           les faits « idéaux » de chaque cas
    data/golden/version.json                                    version et empreinte : le banc est figé
    data/golden/seuils.json                                     les portes (seuils à franchir)
    data/bancs/<date>-<contrat>-<méthode>.{json,md}             chaque passage, pour comparer dans le temps

Trois couches, pour savoir **où** une erreur naît :
  1. règles : les faits idéaux passent dans le moteur Prolog, sans modèle. Une erreur ici est une erreur
     des règles (ou du vocabulaire) ;
  2. lecture : les faits lus par le modèle comparés aux faits idéaux, fait par fait. Une contradiction
     sur un fait décisif est la source d'erreur la plus dangereuse ;
  3. chaîne : la méthode complète, plusieurs exécutions (la variance compte autant que la moyenne).

Les erreurs coûteuses sont comptées à part : « couvert à tort » (une promesse au client) et « refus à
tort ». Les portes (seuils.json) disent si le système est présentable ; la commande sort en erreur
quand une porte échoue, ce qui permet de la brancher sur la CI.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from . import prolog
from .evaluation import charger_cas, fichiers_jeu, lire_jsonl

JEU = "golden"
ABREGE = {"COUVERT": "C", "NON_COUVERT": "NC", "INCERTAIN": "?"}


# --- Le golden set ---------------------------------------------------------------------------------------

def fichiers(donnees: Path, contrat_id: str) -> list[Path]:
    sinistres, annotations = fichiers_jeu(donnees, contrat_id, JEU)
    return [sinistres, annotations, prolog.DOSSIER / "cas" / JEU / f"{contrat_id}.jsonl"]


def empreinte(donnees: Path, contrat_id: str) -> str:
    h = hashlib.sha256()
    for f in fichiers(donnees, contrat_id):
        h.update(f.read_bytes().replace(b"\r\n", b"\n"))
    return h.hexdigest()[:16]


def version(donnees: Path) -> dict:
    f = Path(donnees) / JEU / "version.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def figer(donnees: Path, contrat_id: str, note: str = "") -> dict:
    """Enregistre l'empreinte du golden set ; une nouvelle version si le contenu a changé."""
    v = version(donnees)
    e = empreinte(donnees, contrat_id)
    if v.get("empreintes", {}).get(contrat_id) == e:
        return v
    n = int(v.get("version", 0)) + 1
    v = {"version": n, "date": datetime.now().strftime("%Y-%m-%d"),
         "empreintes": {**v.get("empreintes", {}), contrat_id: e},
         "historique": v.get("historique", []) + [f"v{n} ({datetime.now():%Y-%m-%d}) : {note or 'mise à jour'}"]}
    (Path(donnees) / JEU / "version.json").write_text(json.dumps(v, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return v


def charger(donnees: Path, contrat_id: str) -> tuple[list[dict], dict]:
    """Les cas avec leurs faits idéaux, et l'état du banc (version, empreinte, cohérence)."""
    cas = charger_cas(*fichiers_jeu(donnees, contrat_id, JEU))
    faits = {d["sinistre_id"]: d["faits"] for d in lire_jsonl(fichiers(donnees, contrat_id)[2])}
    for c in cas:
        c["faits"] = faits.get(c["id"])
    v = version(donnees)
    e = empreinte(donnees, contrat_id)
    etat = {"version": v.get("version"), "empreinte": e, "fige": v.get("empreintes", {}).get(contrat_id) == e,
            "n": len(cas), "valides": sum("validé" in c.get("statut", "") and "à valider" not in c.get("statut", "") for c in cas),
            "auteurs": dict(Counter(c.get("auteur", "?") for c in cas))}
    return cas, etat


def seuils(donnees: Path) -> dict:
    f = Path(donnees) / JEU / "seuils.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


# --- Indicateurs ------------------------------------------------------------------------------------------

def ligne(c: dict, obtenu: str) -> dict:
    return {"id": c["id"], "attendu": c["attendu"], "obtenu": obtenu,
            "ok": obtenu == c["attendu"] or obtenu in c.get("acceptables", []),
            "exact": obtenu == c["attendu"]}


def metriques(lignes: list[dict]) -> dict:
    n = len(lignes) or 1
    return {"n": len(lignes),
            "exactitude": round(sum(l["ok"] for l in lignes) / n, 3),
            "exactitude_stricte": round(sum(l["exact"] for l in lignes) / n, 3),
            # Une réponse tolérée par l'annotation (« acceptables ») n'est pas une erreur, même « couvert ».
            "faux_couverts": sum(l["obtenu"] == "COUVERT" and not l["ok"] for l in lignes),
            "faux_refus": sum(l["obtenu"] == "NON_COUVERT" and l["attendu"] == "COUVERT" and not l["ok"] for l in lignes),
            "taux_incertain": round(sum(l["obtenu"] == "INCERTAIN" for l in lignes) / n, 3)}


def par_groupe(lignes: list[dict], cas: list[dict]) -> dict:
    """Indicateurs par thème et par garantie : où le système est faible."""
    index = {c["id"]: c for c in cas}
    groupes: dict[str, list] = defaultdict(list)
    for l in lignes:
        c = index[l["id"]]
        for t in c.get("themes", []):
            groupes[f"thème : {t}"].append(l)
        groupes[f"garantie : {c.get('garantie', '?')}"].append(l)
        groupes[f"auteur : {c.get('auteur', '?')}"].append(l)
    return {k: metriques(v) for k, v in sorted(groupes.items())}


def rappel(attendus: list, obtenus) -> float | None:
    return round(sum(a in obtenus for a in attendus) / len(attendus), 3) if attendus else None


# --- Couche 1 : les règles seules ---------------------------------------------------------------------------

def questions_decision(d: dict) -> list[str]:
    """Les variables demandées par le moteur (comme PipelineRegles.verdict) : sans les questions que le
    raisonnement par hypothèses a jugées inutiles."""
    vs = [v for r in d.get("retenues", []) for v in r.get("questions", []) + r.get("reserves", [])]
    if d.get("decision") == "NON_COUVERT":
        vs += [v for r in d.get("possibles", []) for v in r.get("questions", [])]
    inutiles = {q["variable"] for q in (d.get("exploration") or {}).get("questions", []) if q["effet"] == "inutile"}
    return [v for v in dict.fromkeys(vs) if v not in inutiles]


def couche_regles(cas: list[dict], decideur) -> dict:
    """`decideur(faits) -> dict` : SWI-Prolog (prolog.decider) ou l'oracle dans les tests."""
    lignes = []
    for c in cas:
        if c.get("faits") is None:
            continue
        d = decideur(c["faits"])
        l = ligne(c, d["decision"])
        q = questions_decision(d)
        articles = {p.get("article") for r in d.get("retenues", []) for p in r.get("preuves", [])}
        ex = d.get("exploration") or {}
        l.update(tranchable=bool(ex.get("ensemble")),
                 inutiles=sum(x["effet"] == "inutile" for x in ex.get("questions", [])))
        l.update(questions=q, rappel_questions=rappel(c.get("questions_attendues", []), q),
                 rappel_clauses=rappel(c.get("clauses_attendues", []), articles) if articles else None,
                 non_traduits=d.get("non_traduits", []))
        lignes.append(l)
    m = metriques(lignes)
    rq = [l["rappel_questions"] for l in lignes if l["rappel_questions"] is not None]
    m["rappel_questions"] = round(sum(rq) / len(rq), 3) if rq else None
    # Un gestionnaire qui reçoit six questions pour un vélo volé n'en lit aucune : on compte.
    nq = [len(l["questions"]) for l in lignes if l["obtenu"] == "INCERTAIN"]
    m["questions_par_incertain"] = round(sum(nq) / len(nq), 1) if nq else None
    # Le raisonnement par hypothèses (Prolog) : combien d'incertains une ou deux questions tranchent,
    # et combien de questions inutiles ne sont plus posées.
    inc = [l for l in lignes if l["obtenu"] == "INCERTAIN"]
    m["incertains_tranchables"] = round(sum(l["tranchable"] for l in inc) / len(inc), 3) if inc else None
    m["questions_inutiles_retirees"] = sum(l["inutiles"] for l in lignes)
    return {"metriques": m, "groupes": par_groupe(lignes, cas), "cas": lignes}


# --- Couche 2 : la lecture des faits -------------------------------------------------------------------------

def paires_lues(faits_lus: dict) -> dict[str, set]:
    lus: dict[str, set] = defaultdict(set)
    for cle, v in (("evenements", "evenement"), ("biens", "bien"), ("lieux", "lieu")):
        for x in faits_lus.get(cle, []) or []:
            lus[v].add(str(x))
    for c in faits_lus.get("circonstances", []) or []:
        if "=" in c:
            v, x = c.split("=", 1)
            lus[v.strip()].add(x.strip())
    return lus


def ancetres(voc: dict, v: str, x: str) -> set:
    parents = voc.get(v, {}).get("parents", {})
    vus, pile = set(), list(parents.get(x, []))
    while pile:
        a = pile.pop()
        if a not in vus:
            vus.add(a)
            pile += parents.get(a, [])
    return vus


def comparer_faits(ideaux: dict, faits_lus: dict, voc: dict | None = None) -> dict:
    """Rappel des faits idéaux ; contradictions ; faits « vagues » ; faits en trop.

    Avec la hiérarchie du vocabulaire, lire « vitre » pour « élément du bâtiment » est exact (plus
    précis), et lire « électronique » pour « appareil audiovisuel » est *vague*, pas faux : le moteur
    répond alors « inconnu » et pose la question. Seule une valeur sans lien est une contradiction."""
    voc = voc if voc is not None else prolog.vocabulaire()
    lus = paires_lues(faits_lus)
    ideal = {v: set(x if isinstance(x, list) else [x]) for v, x in ideaux.items()}
    total = sum(len(x) for x in ideal.values())
    trouves, contradictions, vagues = 0, [], []
    for v, xs in ideal.items():
        lv = lus.get(v, set())
        for x in xs:
            if x in lv or any(x in ancetres(voc, v, r) for r in lv):
                trouves += 1
            elif any(r in ancetres(voc, v, x) for r in lv):
                vagues.append(f"{v} : {x} lu {'/'.join(sorted(lv))}")
        if lv and not any(x in lv or any(x in ancetres(voc, v, r) or r in ancetres(voc, v, x) for r in lv) for x in xs):
            contradictions.append(f"{v} : {'/'.join(sorted(xs))} lu {'/'.join(sorted(lv))}")
    manques = sorted(f"{v} = {'/'.join(sorted(x))}" for v, x in ideal.items() if v not in lus and x)
    en_trop = sorted(f"{v} = {'/'.join(sorted(x))}" for v, x in lus.items() if v not in ideal)
    return {"rappel": round(trouves / total, 3) if total else 1.0, "contradictions": sorted(contradictions),
            "vagues": sorted(vagues), "manques": manques, "en_trop": en_trop}


def faits_depuis_lecture(faits_lus: dict) -> dict:
    """Les faits lus (forme Faits) remis dans la forme du moteur."""
    voc = prolog.vocabulaire()
    sortie = {}
    for v, xs in paires_lues(faits_lus).items():
        if v not in voc:
            continue
        valeurs = sorted(xs)
        sortie[v] = valeurs if voc[v].get("plusieurs") else valeurs[0]
    return sortie


def couche_lecture(cas: list[dict], rapports: list[dict], decideur=None) -> dict:
    """La lecture comparée aux faits idéaux, et surtout : **la lecture change-t-elle la décision ?**
    Avec `decideur`, on passe les faits lus dans les règles et on compare à la décision sur les faits
    idéaux : c'est la part des erreurs de la chaîne qui vient de la lecture, et rien d'autre."""
    index = {c["id"]: c for c in cas}
    voc = prolog.vocabulaire()
    par_cas = []
    for i, l0 in enumerate(rapports[0]["cas"] if rapports else []):
        c = index[l0["id"]]
        if not c.get("faits"):
            continue
        lus = [r["cas"][i].get("faits_lus") or {} for r in rapports]
        sans_appui = sorted({w.split(" : ")[0] for r in rapports for w in r["cas"][i].get("avertissements", [])
                             if "sans appui" in w or "non dit" in w})
        comps = [comparer_faits(c["faits"], f, voc) for f in lus]
        x = {"id": c["id"], "rappel": round(sum(y["rappel"] for y in comps) / len(comps), 3),
             **{k: sorted({z for y in comps for z in y[k]}) for k in ("contradictions", "vagues", "manques", "en_trop")},
             "sans_appui": sans_appui}
        if decideur is not None:
            ideal = decideur(c["faits"])["decision"]
            obtenues = [decideur(faits_depuis_lecture(f))["decision"] for f in lus]
            x["decision_ideale"], x["decisions_lues"] = ideal, obtenues
            x["change"] = sum(o != ideal for o in obtenues) / len(obtenues)
            x["grave"] = any(o == "COUVERT" and ideal != "COUVERT" for o in obtenues)
        par_cas.append(x)
    n = len(par_cas) or 1
    m = {"rappel_faits": round(sum(x["rappel"] for x in par_cas) / n, 3),
         "cas_avec_contradiction": sum(bool(x["contradictions"]) for x in par_cas),
         "cas_avec_fait_vague": sum(bool(x["vagues"]) for x in par_cas),
         "cas_avec_fait_en_trop": sum(bool(x["en_trop"]) for x in par_cas),
         "cas_avec_fait_sans_appui": sum(bool(x["sans_appui"]) for x in par_cas)}
    if decideur is not None:
        m["decisions_changees"] = round(sum(x["change"] for x in par_cas), 2)
        m["decisions_changees_vers_couvert"] = sum(x["grave"] for x in par_cas)
    return {"metriques": m, "cas": par_cas}


# --- Couche 3 : la chaîne complète ---------------------------------------------------------------------------

def centile(valeurs: list[float], q: float) -> float | None:
    if not valeurs:
        return None
    v = sorted(valeurs)
    return v[min(len(v) - 1, int(round(q * (len(v) - 1))))]


def latences(durees: list[dict]) -> dict:
    """Le temps d'un cas (médiane et 95e centile, en secondes), et ce que prennent la lecture et la décision.
    Mesuré dans le banc, avec plusieurs cas à la fois : un cas seul est plus rapide (DEMARCHE 7.46)."""
    sortie = {}
    for etape, nom in (("total", "latence"), ("lecture", "latence_lecture"), ("decision", "latence_decision")):
        vals = [d[etape] / 1000 for d in durees if d.get(etape) is not None]
        if vals:
            sortie[f"{nom}_mediane_s"] = round(centile(vals, 0.5), 2)
            sortie[f"{nom}_p95_s"] = round(centile(vals, 0.95), 2)
    return sortie


def couche_chaine(cas: list[dict], rapports: list[dict], durees: list[float]) -> dict:
    index = {c["id"]: c for c in cas}
    par_execution = []
    for r in rapports:
        lignes = [ligne(index[l["id"]], l["obtenu"]) | {"questions": l.get("questions", []),
                                                         "rappel_clauses": l.get("rappel_clauses"),
                                                         "erreur": l.get("erreur", False),
                                                         "durees_ms": l.get("durees_ms") or {}} for l in r["cas"]]
        for l in lignes:
            # Les questions de la chaîne sont des phrases : la variable attendue est trouvée si sa question est posée.
            attendues = index[l["id"]].get("questions_attendues", [])
            l["rappel_questions"] = rappel(attendues, {v for v in attendues
                                                      if any(q.startswith(prolog.question(v)) for q in l["questions"])})
        par_execution.append(lignes)

    def moyenne(cle, filtre=lambda x: x is not None):
        vals = []
        for lignes in par_execution:
            v = [l[cle] for l in lignes if filtre(l[cle])]
            vals.append(sum(v) / len(v) if v else None)
        vals = [v for v in vals if v is not None]
        return round(sum(vals) / len(vals), 3) if vals else None

    mets = [metriques(l) for l in par_execution]
    agreg = {}
    for k in ("exactitude", "exactitude_stricte", "faux_couverts", "faux_refus", "taux_incertain"):
        v = [m[k] for m in mets]
        agreg[k] = {"moyenne": round(sum(v) / len(v), 3), "min": min(v), "max": max(v)}
    reponses = {l["id"]: [lignes[i]["obtenu"] for lignes in par_execution]
                for i, l in enumerate(par_execution[0])} if par_execution else {}
    instables = sorted(i for i, rs in reponses.items() if len(set(rs)) > 1)
    agreg.update(n=len(reponses), executions=len(rapports), instables=len(instables),
                 rappel_clauses=moyenne("rappel_clauses"), rappel_questions=moyenne("rappel_questions"),
                 erreurs_fournisseur=sum(l["erreur"] for lignes in par_execution for l in lignes),
                 duree_moyenne_s=round(sum(durees) / len(durees), 1) if durees else None,
                 **latences([l["durees_ms"] for lignes in par_execution for l in lignes]))
    # Les groupes sur la première exécution suffisent à situer les faiblesses ; les écarts entre
    # exécutions sont dans « instables ».
    return {"metriques": agreg, "groupes": par_groupe(par_execution[0], cas) if par_execution else {},
            "reponses": reponses, "instables": instables, "executions": par_execution}


# --- Portes ---------------------------------------------------------------------------------------------------

def valeur(resultat: dict, couche: str, cle: str):
    m = resultat.get("couches", {}).get(couche, {}).get("metriques", {})
    v = m.get(cle)
    return v["moyenne"] if isinstance(v, dict) else v


def portes(resultat: dict, s: dict) -> list[dict]:
    """Chaque seuil : « *_max » (ne pas dépasser) ou « *_min » (atteindre). Une couche absente n'est pas jugée."""
    sortie = []
    for couche, regles in s.items():
        if couche.startswith("_") or couche not in resultat.get("couches", {}):
            continue
        for nom, seuil in regles.items():
            cle, sens = nom.rsplit("_", 1)
            v = valeur(resultat, couche, cle)
            if v is None:
                continue
            ok = v <= seuil if sens == "max" else v >= seuil
            sortie.append({"couche": couche, "critere": cle, "sens": sens, "seuil": seuil, "valeur": v, "ok": ok})
    return sortie


# --- Le passage complet ---------------------------------------------------------------------------------------

CAS_LATENCE = 10


def mesurer_latence(pipeline, cas: list[dict], n: int = CAS_LATENCE) -> dict:
    """Le temps que vit un gestionnaire : **un cas à la fois**, sans les attentes dues aux limites de débit de
    l'API quand le banc fait tourner plusieurs cas ensemble (DEMARCHE 7.47, 7.48). `n` cas répartis sur le
    golden set (toujours les mêmes), analysés l'un après l'autre."""
    pas = max(1, len(cas) // n)
    choisis = cas[::pas][:n]
    durees = []
    for c in choisis:
        debut = time.perf_counter()
        try:
            r = pipeline.analyser(c["sinistre"])
        except Exception:  # noqa: BLE001  (une panne compte comme un cas long, pas comme une mesure perdue)
            r = None
        total = int((time.perf_counter() - debut) * 1000)
        durees.append({"total": total, **({k: v for k, v in r.durees_ms.items() if k != "total"} if r else {})})
    sortie = {k.replace("latence", "latence_seule", 1): v for k, v in latences(durees).items()}
    sortie["latence_seule_nb"] = len(choisis)
    return sortie


def passer(donnees: Path, contrat_id: str, methode: str, couches: list[str], repetitions: int = 3,
           paralleles: int = 4, pipeline_fabrique=None, decideur=None, evaluer_fn=None) -> dict:
    """Rejoue le golden set. `pipeline_fabrique()` donne une méthode neuve par exécution ; `decideur`
    remplace SWI-Prolog dans les tests ; `evaluer_fn` remplace evaluation.evaluer."""
    from .evaluation import evaluer

    cas, etat = charger(donnees, contrat_id)
    resultat = {"date": datetime.now().isoformat(timespec="seconds"), "contrat": contrat_id, "methode": methode,
                "golden": etat, "couches": {}, "avertissements": []}
    if not etat["fige"]:
        resultat["avertissements"].append("golden set modifié depuis sa dernière version : `couverture banc --figer`")
    if "regles" in couches:
        if decideur is None and prolog.swipl() is None:
            resultat["avertissements"].append("couche règles sautée : SWI-Prolog absent")
        else:
            resultat["couches"]["regles"] = couche_regles(cas, decideur or (lambda f: prolog.decider(contrat_id, f)))
    if "chaine" in couches and pipeline_fabrique is not None:
        rapports, durees = [], []
        for _ in range(max(1, repetitions)):
            debut = time.perf_counter()
            pipeline = pipeline_fabrique()
            resultat["modele"] = getattr(getattr(pipeline, "llm", None), "nom", None) or resultat.get("modele")
            if resultat["methode"] == "regles":
                resultat["lecture"] = prolog.mode_lecture().replace("_", " ")
            rapports.append((evaluer_fn or evaluer)(pipeline, cas, paralleles=paralleles))
            durees.append(time.perf_counter() - debut)
        resultat["couches"]["chaine"] = couche_chaine(cas, rapports, durees)
        if evaluer_fn is None:  # pas dans les tests qui simulent l'évaluation
            print(f"Latence : {min(CAS_LATENCE, len(cas))} cas, un à la fois…", flush=True)
            resultat["couches"]["chaine"]["metriques"].update(mesurer_latence(pipeline_fabrique(), cas))
        if methode == "regles":
            lecteur = None
            if "regles" in resultat["couches"]:
                lecteur = decideur or (lambda f: prolog.decider(contrat_id, f))
            resultat["couches"]["lecture"] = couche_lecture(cas, rapports, lecteur)
    resultat["portes"] = portes(resultat, seuils(donnees))
    resultat["passe"] = all(p["ok"] for p in resultat["portes"])
    resultat["_cas"] = cas
    return resultat


def enregistrer(donnees: Path, resultat: dict, dossier: Path | None = None) -> tuple[Path, Path]:
    dossier = dossier or Path(donnees) / "bancs"
    dossier.mkdir(parents=True, exist_ok=True)
    modele = (resultat.get("modele") or "").split(":")[-1].replace("-latest", "")
    nom = f"{datetime.now():%Y%m%d-%H%M%S}-{resultat['contrat']}-{resultat['methode']}" + (f"-{modele}" if modele else "") \
        + (f"-{resultat['lecture'].replace(' ', '-')}" if resultat.get("lecture") not in (None, "verifiee") else "")
    js, md = dossier / f"{nom}.json", dossier / f"{nom}.md"
    precedent = dernier(dossier, resultat["contrat"], resultat["methode"])
    texte = markdown(resultat, precedent)
    sans_cas = {k: v for k, v in resultat.items() if k != "_cas"}
    js.write_text(json.dumps(sans_cas, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    md.write_text(texte, encoding="utf-8")
    return js, md


def dernier(dossier: Path, contrat_id: str, methode: str) -> dict | None:
    fichiers_ = sorted(Path(dossier).glob(f"*-{contrat_id}-{methode}*.json"))
    return json.loads(fichiers_[-1].read_text(encoding="utf-8")) if fichiers_ else None


# --- Le rapport -------------------------------------------------------------------------------------------------

def pct(x) -> str:
    return "—" if x is None else f"{x:.0%}"


def fmt(v) -> str:
    if isinstance(v, dict):
        return f"{v['moyenne']:g} ({v['min']:g} – {v['max']:g})"
    return "—" if v is None else f"{v:g}"


def tableau_metriques(m: dict) -> list[str]:
    def x(k, p=False):
        v = m.get(k)
        if isinstance(v, dict):
            return f"{pct(v['moyenne'])} ({pct(v['min'])} – {pct(v['max'])})" if p else fmt(v)
        return pct(v) if p else fmt(v)
    return ["| Justes ou acceptables | Exactes | Couverts à tort | Refus à tort | Incertains |",
            "|---|---|---|---|---|",
            f"| {x('exactitude', True)} | {x('exactitude_stricte', True)} | **{x('faux_couverts')}** | "
            f"**{x('faux_refus')}** | {x('taux_incertain', True)} |"]


def tableau_groupes(g: dict) -> list[str]:
    lignes = ["| Groupe | Cas | Justes ou acceptables | Couverts à tort | Refus à tort |", "|---|---|---|---|---|"]
    for k, m in g.items():
        alerte = " ⚠" if m["faux_couverts"] else ""
        lignes.append(f"| {k} | {m['n']} | {pct(m['exactitude'])} | {m['faux_couverts']}{alerte} | {m['faux_refus']} |")
    return lignes


def markdown(r: dict, precedent: dict | None = None) -> str:
    cas = {c["id"]: c for c in r.get("_cas", [])}
    g = r["golden"]
    L = [f"# Banc d'essai — {r['contrat']}, méthode `{r['methode']}`"
         + (f", lecture par `{r['modele']}`" if r.get("modele") else "")
         + (f" ({r['lecture']})" if r.get("lecture") else ""), "",
         f"{r['date']} · golden set v{g.get('version') or '?'} ({g['n']} cas, empreinte `{g['empreinte']}`"
         f"{'' if g['fige'] else ', **modifié depuis sa version**'}) · cas validés par l'auteur : {g['valides']} sur {g['n']}",
         ""]
    for a in r.get("avertissements", []):
        L.append(f"> ⚠ {a}")
    L += ["", f"## Portes : {'**PASSE**' if r['passe'] else '**ÉCHOUE**'}", "",
          "| Couche | Critère | Seuil | Valeur | |", "|---|---|---|---|---|"]
    for p in r.get("portes", []):
        L.append(f"| {p['couche']} | {p['critere']} | {'≤' if p['sens'] == 'max' else '≥'} {p['seuil']:g} | "
                 f"{p['valeur']:g} | {'✓' if p['ok'] else '✗'} |")

    if precedent:
        L += ["", f"## Depuis le banc précédent ({precedent.get('date', '?')})", ""]
        for couche in ("regles", "lecture", "chaine"):
            for k in ("exactitude", "exactitude_stricte", "faux_couverts", "faux_refus", "rappel_faits"):
                a, b = valeur(precedent, couche, k), valeur(r, couche, k)
                if a is not None and b is not None and a != b:
                    L.append(f"- {couche} · {k} : {a:g} → {b:g}")

    reg = r["couches"].get("regles")
    if reg:
        L += ["", "## Couche 1 — règles seules (faits idéaux, sans modèle)", "", *tableau_metriques(reg["metriques"]),
              "", f"Rappel des questions attendues : {pct(reg['metriques'].get('rappel_questions'))} · "
              f"questions posées par réponse « incertain » : {fmt(reg['metriques'].get('questions_par_incertain'))}", "",
              f"Raisonnement par hypothèses : incertains tranchés par une ou deux questions : "
              f"{pct(reg['metriques'].get('incertains_tranchables'))} · questions inutiles retirées : "
              f"{reg['metriques'].get('questions_inutiles_retirees', 0)}", "",
              *tableau_groupes(reg["groupes"]), "", "### Erreurs des règles", ""]
        L += erreurs(reg["cas"], cas) or ["Aucune."]

    lec = r["couches"].get("lecture")
    if lec:
        m = lec["metriques"]
        L += ["", "## Couche 2 — lecture des faits par le modèle", ""]
        if "decisions_changees" in m:
            L += [f"**Décisions changées par la lecture** (faits lus ou idéaux dans les mêmes règles) : "
                  f"**{m['decisions_changees']:g}** par exécution, dont **{m['decisions_changees_vers_couvert']}** cas "
                  f"vers un couvert à tort.", ""]
        L += [f"Rappel des faits idéaux : {pct(m['rappel_faits'])} (les faits négatifs non dits, comme « pas de "
              f"violence », comptent comme manquants : la consigne interdit de les inventer) · contradictions : "
              f"{m['cas_avec_contradiction']} cas · faits vagues : {m['cas_avec_fait_vague']} cas · faits en trop : "
              f"{m['cas_avec_fait_en_trop']} cas · faits retirés (sans appui ou non dits) : {m.get('cas_avec_fait_sans_appui', 0)} cas", ""]
        changes = [x for x in lec["cas"] if x.get("change")]
        if changes:
            L += ["### La lecture change la décision", ""]
            for x in sorted(changes, key=lambda y: not y.get("grave")):
                L.append(f"- {'**⚠ vers couvert** ' if x.get('grave') else ''}`{x['id']}` idéal "
                         f"{ABREGE[x['decision_ideale']]}, lu {' '.join(ABREGE[o] for o in x['decisions_lues'])}"
                         + (f" · **contredit** : {'; '.join(x['contradictions'])}" if x["contradictions"] else "")
                         + (f" · vague : {'; '.join(x['vagues'])}" if x["vagues"] else "")
                         + (f" · manque : {'; '.join(x['manques'])}" if x["manques"] else "")
                         + (f" · en trop : {'; '.join(x['en_trop'])}" if x["en_trop"] else "")
                         + (f" · retiré sans appui : {'; '.join(x['sans_appui'])}" if x.get("sans_appui") else ""))
            L.append("")
        autres = [x for x in lec["cas"] if not x.get("change") and x["contradictions"]]
        if autres:
            L += ["### Contradictions sans effet sur la décision", ""]
            L += [f"- `{x['id']}` : {'; '.join(x['contradictions'])}" for x in autres]

    ch = r["couches"].get("chaine")
    if ch:
        m = ch["metriques"]
        L += ["", f"## Couche 3 — chaîne complète ({m['executions']} exécutions)", "", *tableau_metriques(m), "",
              f"Instables : **{m['instables']}** sur {m['n']} · rappel des clauses : {pct(m['rappel_clauses'])} · "
              f"rappel des questions : {pct(m['rappel_questions'])} · erreurs du fournisseur : {m['erreurs_fournisseur']}"
              f" · durée moyenne d'une exécution : {m['duree_moyenne_s']} s"
              + (f" · par cas, un à la fois ({m.get('latence_seule_nb')} cas) : médiane {m['latence_seule_mediane_s']} s, "
                 f"95e centile {m['latence_seule_p95_s']} s (lecture {m.get('latence_seule_lecture_mediane_s')} s, "
                 f"décision {m.get('latence_seule_decision_mediane_s')} s)" if m.get("latence_seule_mediane_s") is not None else "")
              + (f" · en masse (quatre à la fois) : médiane {m['latence_mediane_s']} s, 95e centile {m['latence_p95_s']} s"
                 if m.get("latence_mediane_s") is not None else ""), "", *tableau_groupes(ch["groupes"]), "",
              "### Erreurs et instabilités", ""]
        lignes = []
        for i, rs in ch["reponses"].items():
            c = cas.get(i, {})
            bons = [o == c.get("attendu") or o in c.get("acceptables", []) for o in rs]
            if all(bons) and len(set(rs)) == 1:
                continue
            grave = any(o == "COUVERT" and c.get("attendu") != "COUVERT" and o not in c.get("acceptables", []) for o in rs)
            lignes.append(f"- {'**⚠ couvert à tort** ' if grave else ''}`{i}` attendu {ABREGE.get(c.get('attendu'), '?')}, "
                          f"obtenu {' '.join(ABREGE.get(o, o) for o in rs)} — {c.get('sinistre', '')[:110]}"
                          f"{'…' if len(c.get('sinistre', '')) > 110 else ''} *({c.get('note', '')[:120]})*")
        L += sorted(lignes, key=lambda x: not x.startswith("- **⚠")) or ["Aucune."]
    return "\n".join(L) + "\n"


def erreurs(lignes: list[dict], cas: dict) -> list[str]:
    sortie = []
    for l in lignes:
        if l["ok"]:
            continue
        c = cas.get(l["id"], {})
        grave = l["obtenu"] == "COUVERT"
        sortie.append(f"- {'**⚠ couvert à tort** ' if grave else ''}`{l['id']}` attendu {ABREGE[l['attendu']]}, "
                      f"obtenu {ABREGE[l['obtenu']]} — {c.get('sinistre', '')[:110]}"
                      f"{'…' if len(c.get('sinistre', '')) > 110 else ''} *({c.get('note', '')[:120]})*")
    return sorted(sortie, key=lambda x: not x.startswith("- **⚠"))


def resume_console(r: dict, md: Path | None = None) -> str:
    L = [f"Banc {r['contrat']} · {r['methode']} · golden v{r['golden'].get('version') or '?'} ({r['golden']['n']} cas)"
         + (f" · lecture : {r['modele']}" if r.get("modele") else "")
         + (f" ({r['lecture']})" if r.get("lecture") else "")]
    for a in r.get("avertissements", []):
        L.append(f"! {a}")
    for nom, titre in (("regles", "Règles seules "), ("lecture", "Lecture       "), ("chaine", "Chaîne        ")):
        c = r["couches"].get(nom)
        if not c:
            continue
        m = c["metriques"]
        if nom == "lecture":
            L.append(f"{titre}" + (f"décisions changées par la lecture {m['decisions_changees']:g} par exécution "
                                   f"({m['decisions_changees_vers_couvert']} vers un couvert à tort) · "
                                   if "decisions_changees" in m else "")
                     + f"rappel des faits {pct(m['rappel_faits'])}, {m['cas_avec_contradiction']} cas avec contradiction")
            continue
        v = lambda k: m[k]["moyenne"] if isinstance(m[k], dict) else m[k]  # noqa: E731
        L.append(f"{titre}{pct(v('exactitude'))} justes · {pct(v('exactitude_stricte'))} exactes · "
                 f"couverts à tort {v('faux_couverts'):g} · refus à tort {v('faux_refus'):g}"
                 + (f" · instables {m['instables']}" if nom == "chaine" else ""))
        if nom == "chaine" and m.get("latence_seule_mediane_s") is not None:
            L.append(f"Temps par cas  un à la fois : médiane {m['latence_seule_mediane_s']:g} s · 95e centile "
                     f"{m['latence_seule_p95_s']:g} s (lecture {m.get('latence_seule_lecture_mediane_s', 0):g} s, "
                     f"décision {m.get('latence_seule_decision_mediane_s', 0):g} s)"
                     + (f" · en masse ({m['latence_mediane_s']:g} s médiane, {m['latence_p95_s']:g} s au 95e centile)"
                        if m.get("latence_mediane_s") is not None else ""))
        elif nom == "chaine" and m.get("latence_mediane_s") is not None:
            L.append(f"Temps par cas  médiane {m['latence_mediane_s']:g} s · 95e centile {m['latence_p95_s']:g} s · "
                     f"lecture {m.get('latence_lecture_mediane_s', 0):g} s · décision {m.get('latence_decision_mediane_s', 0):g} s")
    echecs = [p for p in r.get("portes", []) if not p["ok"]]
    L.append("Portes : PASSE" if not echecs else
             "Portes : ÉCHOUE — " + " ; ".join(f"{p['couche']} {p['critere']} {p['valeur']:g} "
                                               f"({'≤' if p['sens'] == 'max' else '≥'} {p['seuil']:g})" for p in echecs))
    if md:
        L.append(f"Rapport : {md}")
    return "\n".join(L)


def fiche_validation(donnees: Path, contrat_id: str) -> str:
    """Les cas à relire, par garantie : la déclaration, la réponse attendue et la phrase du contrat qui la fonde.
    Pour valider : corriger « attendu » si besoin, et mettre « statut » à « validé par <nom> » dans
    data/golden/annotations/<contrat>.jsonl, puis `couverture banc --figer "validation"`."""
    cas, etat = charger(donnees, contrat_id)
    L = [f"# Golden set — fiche de validation ({contrat_id}, v{etat.get('version') or '?'}, {etat['n']} cas)", "",
         "Pour chaque cas : la réponse attendue est-elle celle d'un gestionnaire qui lit les conditions générales ? "
         "C = couvert, NC = non couvert, ? = incertain (il manque une information, ou la garantie n'est pas traduite).",
         "Une réponse « acceptable » est tolérée sans être exacte.", "",
         "Pour valider ou corriger : `data/golden/annotations/" + contrat_id + ".jsonl` (champs `attendu`, `acceptables`, "
         "`statut` → « validé par … »), puis `uv run couverture banc --contrat " + contrat_id + " --figer \"validation\"`.", ""]
    par_garantie: dict[str, list] = defaultdict(list)
    for c in cas:
        par_garantie[c.get("garantie", "?")].append(c)
    for g in sorted(par_garantie, key=lambda x: (x == "aucune", [int(p) if p.isdigit() else p for p in x.split(".")])):
        L += [f"## Garantie {g}", "", "| Cas | Déclaration | Attendu | Acceptable | Fondement | Validé |", "|---|---|---|---|---|---|"]
        for c in par_garantie[g]:
            valide = "✓" if "validé" in c.get("statut", "") and "à valider" not in c.get("statut", "") else ""
            L.append(f"| `{c['id']}` | {c['sinistre'].replace('|', '/')} | **{ABREGE[c['attendu']]}** | "
                     f"{' '.join(ABREGE[a] for a in c.get('acceptables', []))} | {c.get('note', '').replace('|', '/')} | {valide} |")
        L.append("")
    return "\n".join(L)
