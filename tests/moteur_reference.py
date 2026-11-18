"""Seconde implémentation du moteur de regles/moteur.pl, en Python, pour les tests seulement.

Elle lit le même fichier de règles (un sous-ensemble de la syntaxe Prolog : des faits) et applique
les mêmes règles de décision. Sur une machine avec SWI-Prolog, `test_prolog.py` vérifie que les
deux donnent les mêmes réponses (test différentiel) ; sans SWI-Prolog, elle permet de tester les
règles d'un contrat quand même. Ce n'est pas le moteur du produit : c'est un oracle de test.
"""

from __future__ import annotations

import re
import json
from pathlib import Path

# --- Lecture des faits Prolog --------------------------------------------------------------------

JETON = re.compile(r"""
    (?P<espace>\s+|%[^\n]*|/\*.*?\*/)
  | (?P<chaine>"(?:[^"\\]|\\.)*")
  | (?P<quote>'(?:[^'\\]|\\.)*')
  | (?P<atome>[a-z][A-Za-z0-9_]*)
  | (?P<variable>[A-Z_][A-Za-z0-9_]*)
  | (?P<nombre>\d+(?:\.\d+)?)
  | (?P<ponct>:-|[(),\[\]|./])
""", re.S | re.X)


class Terme(tuple):
    """Terme composé : Terme((nom, arg1, arg2…))."""

    @property
    def nom(self):
        return self[0]

    @property
    def args(self):
        return self[1:]


def jetons(texte: str):
    pos = 0
    while pos < len(texte):
        m = JETON.match(texte, pos)
        if not m:
            raise SyntaxError(f"caractère inattendu : {texte[pos:pos + 30]!r}")
        pos = m.end()
        if m.lastgroup != "espace":
            yield m.lastgroup, m.group()


def lire_clauses(texte: str) -> list:
    toks = list(jetons(texte))
    i = 0

    def terme():
        nonlocal i
        genre, v = toks[i]
        i += 1
        if genre == "chaine":
            return v[1:-1]
        if genre in ("atome", "quote"):
            nom = v[1:-1] if genre == "quote" else v
            if i < len(toks) and toks[i] == ("ponct", "("):
                i += 1
                args = [terme()]
                while toks[i] == ("ponct", ","):
                    i += 1
                    args.append(terme())
                assert toks[i] == ("ponct", ")"), toks[i]
                i += 1
                return Terme((nom, *args))
            return Atome(nom)
        if genre == "ponct" and v == "[":
            elements = []
            if toks[i] != ("ponct", "]"):
                elements.append(terme())
                while toks[i] == ("ponct", ","):
                    i += 1
                    elements.append(terme())
            assert toks[i] == ("ponct", "]"), toks[i]
            i += 1
            return elements
        if genre == "nombre":
            return float(v) if "." in v else int(v)
        raise SyntaxError(f"terme inattendu : {v}")

    clauses = []
    while i < len(toks):
        if toks[i] == ("ponct", ":-"):  # directive : ignorée jusqu'au point
            while toks[i] != ("ponct", "."):
                i += 1
            i += 1
            continue
        clauses.append(terme())
        assert toks[i] == ("ponct", "."), toks[i]
        i += 1
    return clauses


class Atome(str):
    pass


# --- Le moteur ---------------------------------------------------------------------------------------

OUI, NON, INCONNU = "oui", "non", "inconnu"


class Contrat:
    def __init__(self, chemin: Path):
        self.faits: list[Terme] = lire_clauses(Path(chemin).read_text(encoding="utf-8"))

    def regles(self, nom: str, arite: int) -> list[Terme]:
        return [f for f in self.faits if isinstance(f, Terme) and f.nom == nom and len(f.args) == arite]

    def definition(self, n):
        return next((d for d in self.regles("definition", 4) if d.args[0] == n), None)


def hierarchie_du_vocabulaire() -> list[tuple]:
    voc = json.loads((Path(__file__).resolve().parents[1] / "regles" / "vocabulaire.json").read_text(encoding="utf-8"))
    return [(v, x, p) for v, d in voc["variables"].items() for x, ps in d.get("parents", {}).items() for p in ps]


class Moteur:
    def __init__(self, contrat: Contrat, faits: dict, hierarchie: list[tuple] | None = None):
        self.c = contrat
        self.faits = {v: set(x if isinstance(x, list) else [x]) for v, x in faits.items()}
        self.parents: dict = {}
        for v, x, p in (hierarchie_du_vocabulaire() if hierarchie is None else hierarchie):
            self.parents.setdefault((v, x), []).append(p)

    def ancetres(self, v, x) -> set:
        vus, pile = set(), list(self.parents.get((v, x), []))
        while pile:
            a = pile.pop()
            if a not in vus:
                vus.add(a)
                pile += self.parents.get((v, a), [])
        return vus

    def vague(self, v, x) -> bool:
        faits = self.faits.get(v, set())
        return any(p in self.ancetres(v, x) and not any(c != p and p in self.ancetres(v, c) for c in faits)
                   for p in faits)

    # Logique à trois valeurs
    def eval(self, t) -> str:
        if t == "vrai":
            return OUI
        if t == "faux":
            return NON
        nom = t.nom
        if nom == "f":
            v, x = t.args
            if v not in self.faits:
                return INCONNU
            if x in self.faits[v] or any(x in self.ancetres(v, c) for c in self.faits[v]):
                return OUI
            return INCONNU if self.vague(v, x) else NON
        if nom == "non":
            return {OUI: NON, NON: OUI, INCONNU: INCONNU}[self.eval(t.args[0])]
        if nom == "et":
            return et3([self.eval(c) for c in t.args[0]])
        if nom == "ou":
            return ou3([self.eval(c) for c in t.args[0]])
        if nom == "si":
            return self.eval(Terme(("ou", [Terme(("non", t.args[0])), t.args[1]])))
        if nom == "concept":
            d = self.c.definition(t.args[0])
            if d is None:
                raise KeyError(f"concept inconnu : {t.args[0]}")
            return self.eval(d.args[1])
        raise TypeError(t)

    def variables(self, t) -> list:
        if not isinstance(t, Terme):
            return []
        if t.nom == "f":
            return [t.args[0]]
        if t.nom == "non":
            return self.variables(t.args[0])
        if t.nom in ("et", "ou"):
            return [v for c in t.args[0] for v in self.variables(c)]
        if t.nom == "si":
            return self.variables(t.args[0]) + self.variables(t.args[1])
        if t.nom == "concept":
            d = self.c.definition(t.args[0])
            return self.variables(d.args[1]) if d else []
        return []

    def feuilles(self, t) -> list:
        if not isinstance(t, Terme):
            return []
        if t.nom == "f":
            return [t]
        if t.nom == "non":
            return self.feuilles(t.args[0])
        if t.nom in ("et", "ou"):
            return [f for c in t.args[0] for f in self.feuilles(c)]
        if t.nom == "si":
            return self.feuilles(t.args[0]) + self.feuilles(t.args[1])
        if t.nom == "concept":
            d = self.c.definition(t.args[0])
            return self.feuilles(d.args[1]) if d else []
        return []

    def inconnues(self, t) -> list:
        return sorted({f.args[0] for f in self.feuilles(t) if self.eval(f) == INCONNU})

    # Une garantie
    def garantie(self, g) -> dict:
        ps = [p.args[1] for p in self.c.regles("perimetre", 2) if p.args[0] == g]
        eps = [self.eval(p) for p in ps]
        ep = et3(eps)
        cs = [(c.args[1], c.args[2], c.args[3], self.eval(c.args[1]))
              for c in self.c.regles("circonstance", 4) if c.args[0] == g]
        xs = []
        for x in self.c.regles("exclusion", 6):
            cible, cond, portee, dem, a, t = x.args
            if not (cible == "tous" or cible == g or (isinstance(cible, list) and g in cible)):
                continue
            e = self.eval(cond)
            if e == OUI and portee == "tout":
                xs.append(("totale", a, t, []))
            elif e == OUI:
                b = portee.args[0]
                autres = {x for x in self.faits.get("bien", set()) - {b}
                          if x not in self.ancetres("bien", b) and b not in self.ancetres("bien", x)}
                xs.append(("partielle", a, t, b) if autres else ("totale", a, t, []))
            elif e == INCONNU and dem == "oui":
                xs.append(("inconnue", a, t, self.inconnues(cond)))
        os_ = []
        for o in self.c.regles("obligation", 6):
            if o.args[0] != g:
                continue
            cond, exc, lien, a, t = o.args[1:]
            e = OUI if self.eval(exc) == OUI else self.eval(cond)
            os_.append((e, lien, a, t, cond))

        if ep == NON:
            return {"rattachement": "hors", "decision": "NON_COUVERT", "questions": []}
        if any(e == NON for *_, e in cs):
            return {"rattachement": "rattachée", "decision": "NON_COUVERT", "questions": []}
        if ep == INCONNU and any(x[0] == "totale" for x in xs):
            return {"rattachement": "rattachée", "decision": "NON_COUVERT", "questions": []}
        if ep == INCONNU:
            q = set(self.inconnues(Terme(("et", ps))))
            for c, _, _, e in cs:
                if e == INCONNU:
                    q |= set(self.inconnues(c))
            return {"rattachement": "possible", "decision": "INCERTAIN", "questions": sorted(q)}
        if any(x[0] == "totale" for x in xs):
            return {"rattachement": "rattachée", "decision": "NON_COUVERT", "questions": []}
        for c, _, _, e in cs:
            if e == INCONNU:
                return {"rattachement": "rattachée", "decision": "INCERTAIN", "questions": self.inconnues(c)}
        if any(e == NON and lien == "oui" for e, lien, *_ in os_):
            return {"rattachement": "rattachée", "decision": "INCERTAIN", "questions": ["lien_causal"]}
        if any(e == NON and lien == "non" for e, lien, *_ in os_):
            return {"rattachement": "rattachée", "decision": "NON_COUVERT", "questions": []}
        reserves = sorted({v for x in xs if x[0] == "inconnue" for v in x[3]}
                          | {v for e, _, _, _, c in os_ if e == INCONNU for v in self.inconnues(c)})
        return {"rattachement": "rattachée", "decision": "COUVERT", "questions": [], "reserves": reserves,
                "partielles": [x[3] for x in xs if x[0] == "partielle"]}

    def decider(self) -> dict:
        d = self.combiner()
        traduits = {e.args[0] for e in self.c.regles("evenement_traduit", 1)}
        nt = sorted(e for e in self.faits.get("evenement", set()) if e != "autre" and e not in traduits)
        if nt and d["decision"] != "COUVERT":
            d.update(decision="INCERTAIN", non_traduits=nt, aucune=False)
        return d

    def combiner(self) -> dict:
        rs = []
        for g in self.c.regles("garantie", 4):
            r = self.garantie(g.args[0])
            r["id"] = g.args[0]
            rs.append(r)
        ratt = [r for r in rs if r["rattachement"] == "rattachée"]
        poss = [r for r in rs if r["rattachement"] == "possible"]
        couverts = [r for r in ratt if r["decision"] == "COUVERT"]
        incertains = [r for r in ratt if r["decision"] == "INCERTAIN"]
        if couverts:
            return {"decision": "COUVERT", "retenues": couverts[:1], "possibles": [], "garanties": rs}
        if incertains:
            return {"decision": "INCERTAIN", "retenues": incertains, "possibles": poss, "garanties": rs}
        if ratt:
            return {"decision": "NON_COUVERT", "retenues": ratt, "possibles": poss, "garanties": rs}
        if poss:
            return {"decision": "INCERTAIN", "retenues": poss, "possibles": [], "garanties": rs}
        if rs:
            return {"decision": "NON_COUVERT", "retenues": rs, "possibles": [], "garanties": rs, "aucune": True}
        return {"decision": "INCERTAIN", "retenues": [], "possibles": [], "garanties": rs}


def et3(es):
    return NON if NON in es else INCONNU if INCONNU in es else OUI


def ou3(es):
    return OUI if OUI in es else INCONNU if INCONNU in es else NON


# --- Raisonnement par hypothèses (miroir de explorer/2 dans moteur.pl) ---------------------------------------

def domaines_du_vocabulaire() -> dict:
    voc = json.loads((Path(__file__).resolve().parents[1] / "regles" / "vocabulaire.json").read_text(encoding="utf-8"))
    return {v: list(d["valeurs"]) for v, d in voc["variables"].items()}


RANG = {"décisive": 0, "utile": 1, "inutile": 2}


def ferme(dec: str) -> bool:
    return dec not in ("INCERTAIN", "ERREUR")


class Explorateur:
    """Essaie chaque réponse possible aux questions d'une décision, comme le fait Prolog (assertz, décision, retract)."""

    def __init__(self, contrat: Contrat, faits: dict, domaines: dict | None = None, hierarchie: list | None = None):
        self.c, self.faits, self.h = contrat, faits, hierarchie
        self.domaines = domaines_du_vocabulaire() if domaines is None else domaines
        self.m = Moteur(contrat, faits, hierarchie)

    def essai(self, hyps: list[tuple]) -> str:
        f = {v: set(x if isinstance(x, list) else [x]) for v, x in self.faits.items()}
        for v, x in hyps:
            f.setdefault(v, set()).add(x)
        return Moteur(self.c, {v: sorted(xs) for v, xs in f.items()}, self.h).decider()["decision"]

    def questions_posees(self, d: dict) -> list:
        vs = []
        for r in d.get("retenues", []):
            vs += list(r.get("questions", [])) + list(r.get("reserves", []))
        for r in d.get("possibles", []):
            vs += list(r.get("questions", []))
        return list(dict.fromkeys(v for v in vs if v in self.domaines and self.domaines[v]))

    def valeurs(self, v: str) -> list:
        if v in self.m.faits:
            connus = self.m.faits[v]
            return sorted(x for x in self.domaines[v]
                          if x not in connus and any(p in self.m.ancetres(v, x) for p in connus))
        return sorted(self.domaines[v])

    def question(self, courante: str, v: str) -> dict | None:
        xs = self.valeurs(v)
        if not xs:
            return None
        paires = [(x, self.essai([(v, x)])) for x in xs]
        ds = sorted({d for _, d in paires})
        if all(map(ferme, ds)) and (len(ds) >= 2 or ds[0] != courante):
            effet = "décisive"
        elif ds != [courante]:
            effet = "utile"
        else:
            effet = "inutile"
        return {"variable": v, "effet": effet,
                "issues": [{"decision": d, "valeurs": [x for x, e in paires if e == d]} for d in ds]}

    def paire(self, vs: list) -> list:
        for i, v1 in enumerate(vs):
            for v2 in vs[i + 1:]:
                x1s, x2s = self.valeurs(v1), self.valeurs(v2)
                if len(x1s) * len(x2s) > 400:
                    continue
                if all(ferme(self.essai([(v1, a), (v2, b)])) for a in x1s for b in x2s):
                    return [v1, v2]
        return []

    def decider(self) -> dict:
        d = self.m.decider()
        vs = self.questions_posees(d)
        if not vs:
            return d
        qs = [q for v in vs if (q := self.question(d["decision"], v))]
        qs.sort(key=lambda q: RANG[q["effet"]])
        decisives = [q["variable"] for q in qs if q["effet"] == "décisive"]
        ens = decisives[:1] or self.paire([q["variable"] for q in qs if q["effet"] == "utile"])
        d["exploration"] = {"questions": qs, "ensemble": ens}
        return d
