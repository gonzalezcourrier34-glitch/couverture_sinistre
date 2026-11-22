"""La banque d'exemples de lecture, et le partage des cas entre mise au point et test (DEMARCHE 7.107).

Un exemple est une déclaration avec les faits qu'il fallait y lire, validés : les faits idéaux du golden set. À
terme, les plus proches d'une déclaration montreront au petit modèle comment lire (les cas proches qui finissent
autrement : un orage avec grêle, un orage avec tempête), à la place des exceptions écrites dans les aides du
vocabulaire. Rien n'est encore branché dans l'analyse : d'abord la banque, et un banc qui saura dire si elle aide.

Le partage protège la mesure. Un cas « test » ne sert jamais à corriger le vocabulaire ni les règles, et n'entre
jamais dans la banque : sinon le banc mesurerait ce qu'on a appris. Le partage est figé dans
`data/lecture/partage.json` ; un cas ajouté plus tard est tiré au sort par son identifiant (une empreinte, pas le
hasard : le même cas tombe toujours du même côté), sans déplacer les anciens.

    couverture exemples --partager             fige le partage (les cas déjà partagés ne bougent pas)
    couverture exemples --indexer              calcule les vecteurs des exemples (mistral-embed), dans la base
    couverture exemples --proches "texte"      les exemples les plus proches d'une déclaration, avec leur score
    couverture banc --contrat … --partie test  le banc sur les seuls cas de test

Le choix des exemples : similarité cosinus entre les vecteurs, un seuil sous lequel on n'envoie rien (un exemple
éloigné égare plus qu'il n'aide), et la diversité (MMR) : on prend le plus proche, puis le suivant le plus proche qui
ne ressemble pas trop à ceux déjà pris. Pour les détails (appel 2), seuls les exemples du même événement comptent.
Pas de base vectorielle : quelques centaines de vecteurs se comparent en Python.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sqlite3
from array import array
from pathlib import Path

from . import prolog
from .evaluation import lire_jsonl

PARTIES = ("mise_au_point", "test")
TAUX_TEST = 0.3
MODELE = "mistral-embed"
SEUIL = 0.85        # calibré sur la banque (7.108) : 42 % des paires du même événement, 4 % des autres
DIVERSITE = 0.7     # MMR : 1 = la seule proximité, 0 = la seule différence avec les exemples déjà pris

SCHEMA = """
CREATE TABLE IF NOT EXISTS exemples (
    id TEXT PRIMARY KEY, contrat TEXT, declaration TEXT, faits TEXT, evenements TEXT,
    modele TEXT, empreinte TEXT, vecteur BLOB
);
"""


# --- Le partage -------------------------------------------------------------------------------------------------

def chemin_partage(donnees: Path) -> Path:
    return Path(donnees) / "lecture" / "partage.json"


def cas_golden(donnees: Path) -> list[dict]:
    """Les cas du golden set qui ont des faits idéaux, tous contrats confondus : id, contrat, déclaration, faits."""
    sinistres = {s["id"]: s["sinistre"] for s in lire_jsonl(Path(donnees) / "golden" / "sinistres.jsonl")}
    sortie = []
    for f in sorted((prolog.DOSSIER / "cas" / "golden").glob("*.jsonl")):
        for d in lire_jsonl(f):
            if d.get("faits") and d["sinistre_id"] in sinistres:
                sortie.append({"id": d["sinistre_id"], "contrat": f.stem, "declaration": sinistres[d["sinistre_id"]],
                               "faits": d["faits"]})
    return sortie


def tirage(identifiant: str, taux: float = TAUX_TEST) -> str:
    """Le côté d'un cas, d'après son identifiant seul : stable d'une machine et d'une exécution à l'autre."""
    x = int(hashlib.sha256(identifiant.encode("utf-8")).hexdigest()[:8], 16) / 0xFFFFFFFF
    return "test" if x < taux else "mise_au_point"


def charger_partage(donnees: Path) -> dict:
    f = chemin_partage(donnees)
    if not f.exists():
        return {"taux_test": TAUX_TEST, "test": [], "mise_au_point": []}
    return json.loads(f.read_text(encoding="utf-8"))


def partager(donnees: Path, taux: float | None = None) -> dict:
    """Ajoute au partage les cas qui n'y sont pas encore, sans déplacer les autres ; l'écrit."""
    p = charger_partage(donnees)
    taux = p.get("taux_test", TAUX_TEST) if taux is None else taux
    deja = set(p["test"]) | set(p["mise_au_point"])
    for c in cas_golden(donnees):
        if c["id"] not in deja:
            p[tirage(c["id"], taux)].append(c["id"])
            deja.add(c["id"])
    p = {"taux_test": taux, "test": sorted(p["test"]), "mise_au_point": sorted(p["mise_au_point"])}
    f = chemin_partage(donnees)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(p, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return p


def partie(donnees: Path, identifiant: str) -> str | None:
    p = charger_partage(donnees)
    return next((k for k in PARTIES if identifiant in p.get(k, [])), None)


def filtrer(cas: list[dict], donnees: Path, voulue: str) -> list[dict]:
    """Les cas d'une partie. « tout » les garde tous. Un cas absent du partage n'est d'aucune partie : il faut
    `--partager` (on ne le range pas en silence, de peur qu'un cas de test serve à corriger)."""
    if voulue == "tout":
        return cas
    p = charger_partage(donnees)
    ids = set(p.get(voulue, []))
    absents = [c["id"] for c in cas if c["id"] not in set(p["test"]) | set(p["mise_au_point"])]
    if absents:
        raise ValueError(f"{len(absents)} cas hors du partage ({', '.join(absents[:5])}…) : `couverture exemples --partager`")
    return [c for c in cas if c["id"] in ids]


# --- La banque ----------------------------------------------------------------------------------------------------

def evenements(faits: dict) -> list[str]:
    e = faits.get("evenement", [])
    return sorted([e] if isinstance(e, str) else e)


def banque(donnees: Path) -> list[dict]:
    """Les exemples : les cas de mise au point, jamais un cas de test, ni une déclaration identique à un cas de test ;
    et les exemples ajoutés (`data/lecture/exemples.jsonl`) une fois validés (7.144)."""
    p = charger_partage(donnees)
    test = set(p["test"])
    tous = cas_golden(donnees)
    textes_test = {c["declaration"].strip() for c in tous if c["id"] in test}
    sortie = [c | {"evenements": evenements(c["faits"])} for c in tous
              if c["id"] in set(p["mise_au_point"]) and c["declaration"].strip() not in textes_test]
    assert not {c["id"] for c in sortie} & test
    refuses = {x.split(" : ")[0] for x in controler_ajoutes(donnees)}
    sortie += [{"id": x["id"], "contrat": x["contrat"], "declaration": x["declaration"], "faits": x["faits"],
                "evenements": evenements(x["faits"])}
               for x in exemples_ajoutes(donnees) if x.get("statut") == VALIDE and x["id"] not in refuses]
    return sortie


# --- Les exemples ajoutés : écrits pour montrer une lecture, validés par une personne (7.144) ---------------------

VALIDE = "valide"
PROXIMITE_MAX = 0.3   # part de mots communs au-delà de laquelle un exemple ressemble trop à un cas de mesure
MOTS_VIDES = set("le la les un une des de du et ou a au aux en dans par pour sur avec sans est il elle on je j mon ma mes "
                 "me m ce cette ces son sa ses qui que qu d l n ne pas plus y ai ete etait ont se s nous notre nos".split())


def chemin_ajoutes(donnees: Path) -> Path:
    return Path(donnees) / "lecture" / "exemples.jsonl"


def exemples_ajoutes(donnees: Path) -> list[dict]:
    """Les exemples écrits à la main, validés ou non (`statut` : « propose » ou « valide »)."""
    chemin = chemin_ajoutes(donnees)
    return lire_jsonl(chemin) if chemin.exists() else []


def mots(texte: str) -> set[str]:
    """Les mots d'une déclaration, sans accents ni mots vides, réduits à leurs six premières lettres."""
    import re
    import unicodedata
    plat = "".join(c for c in unicodedata.normalize("NFD", texte.lower()) if unicodedata.category(c) != "Mn")
    return {m[:6] for m in re.findall(r"[a-z0-9]+", plat) if m not in MOTS_VIDES and len(m) > 2}


def proximite(a: str, b: str) -> float:
    """La part de mots communs entre deux déclarations (indice de Jaccard), de 0 à 1."""
    ma, mb = mots(a), mots(b)
    return len(ma & mb) / len(ma | mb) if ma | mb else 0.0


def cas_de_mesure(donnees: Path) -> list[dict]:
    """Les déclarations qui servent à mesurer : la partie test du golden set et les jeux fermés."""
    test = set(charger_partage(donnees)["test"])
    sinistres = lire_jsonl(Path(donnees) / "golden" / "sinistres.jsonl")
    ferme = Path(donnees) / "ferme" / "sinistres.jsonl"
    return ([{"id": s["id"], "declaration": s["sinistre"]} for s in sinistres if s["id"] in test]
            + [{"id": s["id"], "declaration": s["sinistre"]} for s in (lire_jsonl(ferme) if ferme.exists() else [])])


def valider_ajoutes(donnees: Path, ids: list[str] | None = None, retirer: list[str] | None = None) -> dict:
    """La décision de la personne qui relit : `ids` deviennent « valide » (None : tous les proposés), `retirer`
    sort des exemples du fichier. Rend le compte : validés, retirés, restant à relire."""
    ajoutes = [x for x in exemples_ajoutes(donnees) if x["id"] not in set(retirer or [])]
    n = 0
    for x in ajoutes:
        if x.get("statut") != VALIDE and (ids is None or x["id"] in ids):
            x["statut"], n = VALIDE, n + 1
    chemin_ajoutes(donnees).write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in ajoutes),
                                       encoding="utf-8", newline="\n")
    return {"valides": n, "retires": len(retirer or []), "a_relire": sum(x.get("statut") != VALIDE for x in ajoutes)}


def controler_ajoutes(donnees: Path) -> list[str]:
    """Ce qui empêche un exemple ajouté d'entrer dans la banque, en une ligne « id : raison » :
    - un fait hors du vocabulaire, ou que le filtre retirerait comme hors sujet pour son événement ;
    - une déclaration trop proche d'un cas de mesure (`PROXIMITE_MAX`) : un exemple qui ressemble à un cas du banc
      lui soufflerait la réponse, et le banc mesurerait ce qu'on lui a appris ;
    - un identifiant en double, ou déjà pris par un cas du golden set."""
    ajoutes, problemes = exemples_ajoutes(donnees), []
    mesure = cas_de_mesure(donnees)
    pris = {s["id"] for s in lire_jsonl(Path(donnees) / "golden" / "sinistres.jsonl")}
    vus: set[str] = set()
    for x in ajoutes:
        if x["id"] in vus or x["id"] in pris:
            problemes.append(f"{x['id']} : identifiant déjà pris")
        vus.add(x["id"])
        problemes += [f"{x['id']} : {p}" for p in prolog.verifier_faits(x["faits"])]
        problemes += [f"{x['id']} : {r}" for r in prolog.filtrer_faits(x["faits"])[1]]
        if not x["faits"].get("evenement"):
            problemes.append(f"{x['id']} : pas d'événement")
        proche = max(mesure, key=lambda c: proximite(x["declaration"], c["declaration"]), default=None)
        if proche and proximite(x["declaration"], proche["declaration"]) >= PROXIMITE_MAX:
            problemes.append(f"{x['id']} : trop proche du cas de mesure {proche['id']} "
                             f"({proximite(x['declaration'], proche['declaration']):.2f})")
    return problemes


def empreinte(exemple: dict, modele: str) -> str:
    return hashlib.sha256(json.dumps([exemple["declaration"], exemple["faits"], modele], ensure_ascii=False,
                                     sort_keys=True).encode("utf-8")).hexdigest()[:16]


# --- Les vecteurs --------------------------------------------------------------------------------------------------

class EmbeddingsMistral:
    """L'API d'embeddings de Mistral : un texte → 1 024 nombres. Pas un appel de lecture : rien n'est généré."""

    URL = "https://api.mistral.ai/v1"

    def __init__(self, modele: str = MODELE, cle_api: str | None = None, lot: int = 32, timeout: int = 60):
        self.modele, self.lot, self.timeout = modele, lot, timeout
        self.url = os.environ.get("MISTRAL_URL", self.URL).rstrip("/")
        self.cle_api = cle_api or os.environ["MISTRAL_API_KEY"]

    def __call__(self, textes: list[str]) -> list[list[float]]:
        from .llm import _poster

        sortie = []
        for i in range(0, len(textes), self.lot):
            r = _poster(f"{self.url}/embeddings", {"model": self.modele, "input": textes[i:i + self.lot]},
                        {"authorization": f"Bearer {self.cle_api}"}, self.timeout)
            sortie += [d["embedding"] for d in sorted(r["data"], key=lambda d: d["index"])]
        return sortie


def _cx(chemin_base: str | Path) -> sqlite3.Connection:
    cx = sqlite3.connect(str(chemin_base))
    cx.executescript(SCHEMA)
    return cx


def indexer(chemin_base: str | Path, donnees: Path, embed, modele: str = MODELE) -> dict:
    """Calcule les vecteurs des exemples nouveaux ou changés ; retire ceux qui ne sont plus dans la banque."""
    exemples = banque(donnees)
    with _cx(chemin_base) as cx:
        connus = {i: e for i, e in cx.execute("SELECT id, empreinte FROM exemples")}
        a_faire = [x for x in exemples if connus.get(x["id"]) != empreinte(x, modele)]
        vecteurs = embed([x["declaration"] for x in a_faire]) if a_faire else []
        for x, v in zip(a_faire, vecteurs):
            cx.execute("INSERT OR REPLACE INTO exemples VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (x["id"], x["contrat"], x["declaration"], json.dumps(x["faits"], ensure_ascii=False),
                        json.dumps(x["evenements"]), modele, empreinte(x, modele), array("f", v).tobytes()))
        gardes = {x["id"] for x in exemples}
        retires = [i for i in connus if i not in gardes]
        cx.executemany("DELETE FROM exemples WHERE id = ?", [(i,) for i in retires])
    return {"exemples": len(exemples), "calcules": len(a_faire), "retires": len(retires)}


def charger_index(chemin_base: str | Path) -> list[dict]:
    with _cx(chemin_base) as cx:
        lignes = cx.execute("SELECT id, contrat, declaration, faits, evenements, vecteur FROM exemples").fetchall()
    return [{"id": i, "contrat": c, "declaration": d, "faits": json.loads(f), "evenements": json.loads(e),
             "vecteur": array("f", v).tolist()} for i, c, d, f, e, v in lignes]


# --- Le choix ------------------------------------------------------------------------------------------------------

def cosinus(a: list[float], b: list[float]) -> float:
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / (na * nb) if na and nb else 0.0


def choisir(requete: list[float], exemples: list[dict], k: int = 4, seuil: float = SEUIL,
            diversite: float = DIVERSITE, evenement: str | None = None) -> list[tuple[dict, float]]:
    """Les k exemples à montrer : au-dessus du seuil, du même événement si on le donne, et divers (MMR)."""
    candidats = [(x, cosinus(requete, x["vecteur"])) for x in exemples
                 if evenement is None or evenement in x["evenements"]]
    candidats = [(x, s) for x, s in candidats if s >= seuil]
    pris: list[tuple[dict, float]] = []
    while candidats and len(pris) < k:
        def note(c):
            redondance = max((cosinus(c[0]["vecteur"], p[0]["vecteur"]) for p in pris), default=0.0)
            return diversite * c[1] - (1 - diversite) * redondance
        meilleur = max(candidats, key=note)
        pris.append(meilleur)
        candidats.remove(meilleur)
    return pris


def proches(texte: str, chemin_base: str | Path, embed, **options) -> list[tuple[dict, float]]:
    return choisir(embed([texte])[0], charger_index(chemin_base), **options)


# --- Dans la lecture (par défaut depuis 7.112 ; COUVERTURE_EXEMPLES=non pour s'en passer) ----------------------------

def actifs() -> bool:
    return os.environ.get("COUVERTURE_EXEMPLES", "").strip().lower() not in ("0", "non", "false", "no")


class Banque:
    """Les exemples d'une analyse : un seul vecteur par déclaration (un appel à mistral-embed), puis un choix pour
    les détails, parmi ceux du même événement (le socle n'en reçoit plus, 7.116). La déclaration elle-même n'est
    jamais son propre exemple (sur un cas de mise au point, elle est dans la banque)."""

    def __init__(self, chemin_base: str | Path, embed, k: int = 3, seuil: float = SEUIL):
        self.index, self.embed, self.k, self.seuil = charger_index(chemin_base), embed, k, seuil

    def pour(self, texte: str):
        """Rend `choix(evenement=None) -> [exemple]`, ou None si la banque est vide ou l'appel échoue."""
        autres = [x for x in self.index if x["declaration"].strip() != texte.strip()]
        if not autres:
            return None
        try:
            vq = self.embed([texte])[0]
        except Exception:  # noqa: BLE001 — sans exemples, la lecture reste celle d'avant
            return None
        return lambda evenement=None: [x for x, _ in choisir(vq, autres, k=self.k, seuil=self.seuil, evenement=evenement)]


def bloc(exemples: list[dict], variables) -> str:
    """Les exemples pour un appel de lecture, réduits aux variables de cet appel. Vide s'il n'y a rien à montrer."""
    lignes = []
    for x in exemples:
        faits = {v: x["faits"][v] for v in variables if v in x["faits"] and x["faits"][v] not in (None, "", [])}
        if faits:
            dit = " ; ".join(f"{v} = {'/'.join(map(str, val)) if isinstance(val, list) else val}" for v, val in faits.items())
            lignes.append(f"- « {x['declaration']} » → {dit}")
    if not lignes:
        return ""
    return ("## Exemples de lecture\nDes déclarations proches, et ce qu'il fallait y lire. Ils montrent la façon de "
            "lire ; ce ne sont pas les faits de la déclaration à lire : n'en recopie aucun qu'elle ne dit pas.\n"
            + "\n".join(lignes) + "\n\n")
