"""Les contrôles d'une proposition, tous automatiques (voir la liste dans redaction/__init__.py)."""

from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path

from .. import lecture, prolog
from ..models import Clause, TypeClause
from ..texte import normaliser
from ..validation import _compact, extrait_present, passage_exact
from .consigne import (IDENT, ErreurProposition, clauses_article, concepts_existants, definitions_utiles,
                       valeurs_du_contrat)
from .ecriture import en_prolog, exclusions, fusionner, portee, terme


# --- Contrôles ------------------------------------------------------------------------------------------

BLOQUANT, A_RELIRE, INFO = "bloquant", "à relire", "info"

CHAMPS = {
    "definitions": ("concept", "condition", "article", "texte"),
    "extensions": ("concept", "condition", "article", "texte"),
    "garanties": ("id", "nom", "article", "texte", "perimetre"),
    "circonstances": ("condition", "article", "texte"),
    "obligations": ("condition", "article", "texte"),
    "exclusions": ("condition", "article", "texte"),
    "limites": ("article", "texte"),
    "non_traduit": ("article", "texte", "pourquoi"),
    "hors_decision": ("article", "texte", "pourquoi"),
}


def envelopper_conditions_nues(prop: dict) -> list[str]:
    """Une circonstance, obligation ou exclusion rendue comme une condition nue ({"f": …} au lieu de
    {"condition", "article", "texte"}) : Mistral Large l'a fait sur Assureur B 3.1.6 (7.54), et la reprise demandée ne
    l'a pas corrigé. On l'enveloppe avec l'article et la citation de sa garantie, qui sont dans la même clause,
    plutôt que de payer une nouvelle rédaction ; la citation reste à préciser par le relecteur."""
    notes = []
    for g in prop.get("garanties") or []:
        if not isinstance(g, dict):
            continue
        for nature in ("circonstances", "obligations", "exclusions"):
            for k, x in enumerate(g.get(nature) or []):
                if isinstance(x, dict) and len(x) == 1 and next(iter(x)) in ("f", "et", "ou", "non", "si", "concept"):
                    g[nature][k] = x = {"condition": x, "article": g.get("article"), "texte": g.get("texte", ""),
                                        "a_preciser": True}
                if isinstance(x, dict) and x.get("a_preciser"):
                    # Le marqueur reste dans le JSON enregistré : l'avertissement revient à chaque contrôle tant que
                    # le relecteur n'a pas remplacé la citation et retiré « a_preciser ».
                    notes.append(f"garantie {g.get('id')} : {nature[:-1]} {json.dumps(x['condition'], ensure_ascii=False)[:60]} "
                                 f"rendue sans citation ; rattachée à celle de la garantie, à préciser")
    return notes


def questions_connues(prop: dict) -> dict:
    """La question de chaque variable : celles que propose le modèle, puis celles du vocabulaire commun."""
    qs = {}
    try:
        voc = prolog.vocabulaire()
        qs.update({v: d.get("question", "") for v, d in voc.items()})
    except (OSError, ValueError, KeyError):
        pass
    qs.update({m.get("variable"): m.get("question", "") for m in prop.get("vocabulaire_manquant") or []
               if isinstance(m, dict)})
    return qs


def conditions_particulieres_en_reserve(prop: dict) -> list[str]:
    """« En fonction des couvertures mentionnées dans vos conditions particulières » : le déclarant ne les a pas
    sous les yeux, et le moteur ne les lit pas. Une telle condition est une RÉSERVE (« sous réserve que vos
    conditions particulières… »), pas une question posée à chaque sinistre (7.62, 7.69). Le relecteur le faisait
    à la main pour chaque garantie optionnelle d'Assureur B ; le code le fait désormais pour tout contrat : la
    circonstance (ou le terme de périmètre) devient une exclusion « non condition », à demander, sur la même
    garantie. Inconnue et non évoquée, elle reste une réserve (règle 6 bis du moteur)."""
    qs, notes = questions_connues(prop), []

    def vise_les_cp(texte, condition):
        # Seulement « la couverture X est-elle mentionnée » (oui/non) : une formule à plusieurs valeurs (Assureur A,
        # Privilège ou Active) décide de ce qui est couvert, et la question reste posée.
        if not (isinstance(condition, dict) and isinstance(condition.get("f"), list)
                and len(condition["f"]) == 2 and condition["f"][1] == "oui"):
            return False
        return "conditions particulieres" in normaliser((texte or "") + " " + (qs.get(condition["f"][0]) or ""))

    for g in prop.get("garanties") or []:
        if not isinstance(g, dict):
            continue
        garder = []
        for c in g.get("circonstances") or []:
            if isinstance(c, dict) and "condition" in c and vise_les_cp(c.get("texte"), c["condition"]):
                g.setdefault("exclusions", []).append({"condition": {"non": c["condition"]}, "portee": "tout",
                                                       "a_demander": True, "article": c.get("article"),
                                                       "texte": c.get("texte", "")})
                notes.append(f"garantie {g.get('id')} : {json.dumps(c['condition'], ensure_ascii=False)[:60]} "
                             f"(conditions particulières) mise en réserve, et non en question")
            else:
                garder.append(c)
        if "circonstances" in g:
            g["circonstances"] = garder
        perimetre = []
        for t in g.get("perimetre") or []:
            if isinstance(t, dict) and "f" in t and vise_les_cp("", t):
                g.setdefault("exclusions", []).append({"condition": {"non": t}, "portee": "tout", "a_demander": True,
                                                       "article": g.get("article"), "texte": g.get("texte", "")})
                notes.append(f"garantie {g.get('id')} : {json.dumps(t, ensure_ascii=False)[:60]} retiré du périmètre "
                             f"(conditions particulières) et mis en réserve")
            else:
                perimetre.append(t)
        if "perimetre" in g:
            g["perimetre"] = perimetre
    return notes


def circonstances_par_evenement(prop: dict) -> list[str]:
    """Une garantie qui couvre plusieurs événements (« la chute, le heurt… ; le vol hors du bâtiment, pour autant
    qu'une plainte soit déposée ») pose parfois une condition propre à l'un d'eux. Rendue comme une circonstance
    « vol et plainte », elle interdit tous les autres événements : un ordinateur tombé ne serait jamais couvert
    (6.1, 7.71). Le code la réécrit « si vol, alors plainte », pour tout contrat."""
    notes = []
    for g in prop.get("garanties") or []:
        if not isinstance(g, dict):
            continue
        evs = {x for c in g.get("perimetre") or [] for v, x in feuilles(c) if v == "evenement"}
        for c in g.get("circonstances") or []:
            cond = c.get("condition") if isinstance(c, dict) else None
            if not (isinstance(cond, dict) and isinstance(cond.get("et"), list)):
                continue
            propres = [x for x in cond["et"] if isinstance(x, dict) and isinstance(x.get("f"), list)
                       and len(x["f"]) == 2 and x["f"][0] == "evenement"]
            if len(propres) == 1 and len(evs) > 1 and propres[0]["f"][1] in evs:
                reste = [x for x in cond["et"] if x is not propres[0]]
                c["condition"] = {"si": [propres[0], reste[0] if len(reste) == 1 else {"et": reste}]}
                notes.append(f"garantie {g.get('id')} : la circonstance propre à « {propres[0]['f'][1]} » "
                             f"réécrite « si {propres[0]['f'][1]}, alors… » (les autres événements restent couverts)")
    return notes


def obligations_mal_formees(prop: dict) -> list[str]:
    """Une obligation dit un devoir (fermer, retirer, prévenir) ; la situation où il s'applique (un véhicule, une
    absence) va dans « si situation alors devoir ». Écrite comme une situation (« véhicule et voie publique et
    nuit »), elle serait « violée » par tout sinistre hors de cette situation : un refus pour chaque heurt à la
    maison (6.1, 7.71)."""
    def hors_si(c):
        if not isinstance(c, dict) or len(c) != 1:
            return []
        (cle, v), = c.items()
        if cle == "f":
            return [str(v[0])]
        if cle == "si":
            return hors_si(v[1])
        if cle in ("et", "ou"):
            return [x for y in v for x in hors_si(y)]
        if cle == "non":
            return hors_si(v)
        return []
    return [f"garantie {g.get('id')} : l'obligation « {str(o.get('texte'))[:70]} » décrit une situation "
            f"({', '.join(sorted(set(hors_si(o.get('condition'))) & set(lecture.SOCLE)))}) au lieu d'un devoir : "
            f"l'écrire « si situation, alors devoir », ou en faire une exclusion"
            for g in prop.get("garanties") or [] if isinstance(g, dict)
            for o in g.get("obligations") or [] if isinstance(o, dict)
            and set(hors_si(o.get("condition"))) & set(lecture.SOCLE)]


def non_traduits(prop: dict) -> list[dict]:
    """Les passages déclarés non traduits. Le modèle renvoie parfois une simple phrase au lieu de l'objet
    {"article", "texte", "pourquoi"} (Assureur B 3.1.6, 7.53) : on la garde, sans article, plutôt que de planter."""
    return [n if isinstance(n, dict) else {"article": None, "texte": str(n), "pourquoi": "rendu sans article ni raison"}
            for n in prop.get("non_traduit") or []]


def erreurs_schema(prop) -> list[str]:
    """Les écarts au schéma, en clair : ils sont renvoyés tels quels au modèle pour qu'il corrige."""
    if not isinstance(prop, dict):
        return ["la réponse n'est pas un objet JSON"]
    erreurs = []

    def champs(liste, nature, ou):
        for k, x in enumerate(liste or []):
            if not isinstance(x, dict):
                erreurs.append(f"{ou} : l'élément {k + 1} de « {nature} » n'est pas un objet")
                continue
            manquants = [c for c in CHAMPS[nature] if c not in x]
            if manquants:
                erreurs.append(f"{ou} : un élément de « {nature} » n'a pas {', '.join(manquants)} "
                               f"(champs reçus : {', '.join(x)})")
            for c in ("condition", "exception"):
                if x.get(c) is not None:
                    try:
                        terme(x[c])
                    except ErreurProposition as e:
                        erreurs.append(f"{ou}, « {nature} » : {e}")
            if nature == "exclusions":
                try:
                    portee(x.get("portee"))
                except ErreurProposition as e:
                    erreurs.append(f"{ou} : {e}")

    champs(prop.get("definitions"), "definitions", "definitions")
    champs(prop.get("extensions"), "extensions", "extensions")
    champs(prop.get("non_traduit"), "non_traduit", "non_traduit")
    champs(prop.get("hors_decision"), "hors_decision", "hors_decision")
    champs(prop.get("exclusions_communes"), "exclusions", "exclusions_communes")
    garanties = prop.get("garanties")
    if not garanties and not prop.get("extensions") and not prop.get("exclusions_communes"):
        erreurs.append("aucune garantie proposée")
    champs(garanties, "garanties", "garanties")
    for g in garanties or []:
        if not isinstance(g, dict):
            continue
        ou = f"garantie {g.get('id', '?')}"
        for k, p in enumerate(g.get("perimetre") or []):
            try:
                terme(p)
            except ErreurProposition as e:
                erreurs.append(f"{ou}, périmètre {k + 1} : {e}")
        for nature in ("circonstances", "obligations", "exclusions", "limites"):
            champs(g.get(nature), nature, ou)
    return erreurs


def exclusions_hors_perimetre(prop: dict, voc: dict) -> list[str]:
    """Les exclusions qui visent un lieu ou un bien que le périmètre de leurs garanties n'admet pas (7.152).
    Une telle exclusion n'est jamais atteinte : le sinistre est écarté comme « hors garantie », sans la clause
    qui le dit en toutes lettres (« les locaux à usage commun »). Le lieu ou le bien qu'un contrat exclut
    expressément appartient au périmètre : c'est l'exclusion qui décide, et qu'on cite. La règle ne vaut que pour
    une exclusion de tout le sinistre (portée « tout »).
    Sans réponse quand un périmètre emploie un concept que la proposition ne définit pas (on ne sait pas l'ouvrir)."""
    definitions = {d.get("concept"): d.get("condition") for d in prop.get("definitions") or []}

    def admis(c, variable, vus=()):
        """Les valeurs de `variable` qu'une condition admet ; None : on ne sait pas."""
        if not isinstance(c, dict) or len(c) != 1:
            return set()
        (cle, v), = c.items()
        if cle == "f":
            return {str(v[1])} if str(v[0]) == variable else set()
        if cle == "concept":
            return admis(definitions[v], variable, (*vus, v)) if v in definitions and v not in vus else None
        if cle in ("et", "ou", "si"):
            parts = [admis(x, variable, vus) for x in v]
            return None if any(x is None for x in parts) else set().union(*parts)
        return set()

    notes = []
    garanties = [g for g in prop.get("garanties") or [] if isinstance(g, dict) and not g.get("accessoire")]
    visees = [(x, [g]) for g in garanties for x in g.get("exclusions") or []]
    visees += [(x, garanties) for x in prop.get("exclusions_communes") or []]
    for x, gs in visees:
        c = x.get("condition")
        if not (isinstance(c, dict) and list(c) == ["f"] and c["f"][0] in ("lieu", "bien")) or not gs:
            continue
        # Seulement une exclusion qui écarte tout le sinistre. Celle qui n'écarte qu'un bien (« les vitraux »)
        # doit rester hors du périmètre : le périmètre est établi dès qu'UN bien y entre, et l'exclusion n'en
        # retire qu'un ; deux biens exclus déclarés ensemble donnaient « couvert » (7.156).
        if x.get("portee") not in (None, "tout"):
            continue
        variable, valeur = str(c["f"][0]), str(c["f"][1])
        parents = set((voc.get(variable, {}).get("parents") or {}).get(valeur) or [])
        atteinte = False
        for g in gs:
            ensembles = [admis(p, variable) for p in g.get("perimetre") or []]
            if any(e is None for e in ensembles):
                atteinte = True
                break
            restreint = [e for e in ensembles if e]
            if not restreint or all(valeur in e or parents & e for e in restreint):
                atteinte = True
                break
        if not atteinte:
            notes.append(f"exclusion « {str(x.get('texte'))[:60]} » : {variable} = {valeur} n'est dans le périmètre d'aucune "
                         f"de ses garanties ; elle ne sera jamais citée : l'ajouter au périmètre (c'est l'exclusion qui décide)")
    return notes


def feuilles(c) -> list[tuple[str, str]]:
    if not isinstance(c, dict) or len(c) != 1:
        return []
    (cle, v), = c.items()
    if cle == "f":
        return [(str(v[0]), str(v[1]))]
    if cle in ("et", "ou", "si"):
        return [f for x in v for f in feuilles(x)]
    if cle == "non":
        return feuilles(v)
    return []


def feuilles_positives(c) -> list[tuple[str, str]]:
    """Les feuilles d'une condition, sauf celles sous un « non »."""
    if not isinstance(c, dict) or len(c) != 1:
        return []
    (cle, v), = c.items()
    if cle == "f":
        return [(str(v[0]), str(v[1]))]
    if cle in ("et", "ou", "si"):
        return [f for x in v for f in feuilles_positives(x)]
    return []


def cycle_de_concepts(contrat_pl: str, prop: dict) -> list[str]:
    """Un cycle entre concepts (définitions et extensions, du contrat et de la proposition), ou []."""
    graphe: dict[str, set[str]] = {}
    for bloc in re.split(r"\n(?=[a-z_]+\()", contrat_pl):
        m = re.match(r"(definition|extension)\((\w+),", bloc)
        if m:
            graphe.setdefault(m.group(2), set()).update(re.findall(r"concept\((\w+)\)", bloc))
    for d in (prop.get("definitions") or []) + (prop.get("extensions") or []):
        if isinstance(d, dict) and d.get("concept"):
            graphe.setdefault(str(d["concept"]), set()).update(concepts_employes(d.get("condition")))

    def chercher(n, chemin):
        if n in chemin:
            return chemin[chemin.index(n):] + [n]
        for m in sorted(graphe.get(n, ())):
            trouve = chercher(m, chemin + [n])
            if trouve:
                return trouve
        return []

    for n in sorted(graphe):
        trouve = chercher(n, [])
        if trouve:
            return trouve
    return []


def concepts_employes(c) -> list[str]:
    if not isinstance(c, dict) or len(c) != 1:
        return []
    (cle, v), = c.items()
    if cle == "concept":
        return [v]
    if cle in ("et", "ou", "si"):
        return [n for x in v for n in concepts_employes(x)]
    if cle == "non":
        return concepts_employes(v)
    return []


def elements_cites(prop: dict):
    """(rôle, élément) pour tout ce qui porte article et texte."""
    for d in prop.get("definitions", []):
        yield "définition", d
    for d in prop.get("extensions") or []:
        yield "extension", d
    for g in prop.get("garanties", []):
        yield "garantie", g
        for role, cle in (("circonstance", "circonstances"), ("obligation", "obligations"),
                          ("exclusion", "exclusions"), ("limite", "limites")):
            for x in g.get(cle, []):
                yield role, x
    for x in prop.get("exclusions_communes") or []:
        yield "exclusion", x


def conditions(prop: dict):
    for d in prop.get("definitions", []):
        yield d.get("condition")
    for d in prop.get("extensions") or []:
        yield d.get("condition")
    for g in prop.get("garanties", []):
        yield from g.get("perimetre", [])
        for cle in ("circonstances", "obligations", "exclusions"):
            for x in g.get(cle, []):
                yield x.get("condition")
                if cle == "obligations" and x.get("exception") is not None:
                    yield x["exception"]
    for x in prop.get("exclusions_communes") or []:
        yield x.get("condition")


def items_exclusion(texte: str) -> list[str]:
    """Les éléments d'une liste d'exclusions (puces « • » ou « - », ou sous-points numérotés « 3.1.6.2.4 »), sans
    la phrase d'introduction. Un tiret au milieu d'une phrase (« automoteurs – à l'exception des engins – ») est une
    incise, pas une puce : le tiret long ne coupe qu'en début de ligne ou après « : ; . » (Assureur B, 7.54)."""
    morceaux = re.split(r"(?:^|\s)[•\-]\s|(?:^|[:;.]\s*|\n\s*)–\s|(?:^|\s)\d+(?:\.\d+){2,}\s+", texte)
    return [m.strip(" .;") for m in morceaux if len(_compact(m).split()) >= 3 and not m.strip().endswith(":")]


def couvert_par(item: str, textes: list[str]) -> bool:
    ci = _compact(item)
    return any((ct := _compact(t)) and (ct in ci or ci in ct) for t in textes)


def controler(prop: dict, clauses: list[Clause], contrat_pl: str, article: str,
              contrat_id: str | None = None) -> list[dict]:
    """Les problèmes d'une proposition. Répare en place les citations dont les mots sont dans l'ordre."""
    problemes: list[dict] = []

    def noter(gravite, controle, message):
        problemes.append({"gravite": gravite, "controle": controle, "message": message})

    # 1. Structure. Un « non_traduit » en simple phrase est mis en forme (sans article) : il reste bloquant
    # plus bas, et une seconde rédaction de plusieurs minutes pour une question de forme serait du gaspillage.
    if isinstance(prop, dict) and prop.get("non_traduit"):
        prop["non_traduit"] = non_traduits(prop)
    for note in envelopper_conditions_nues(prop) if isinstance(prop, dict) else []:
        noter(A_RELIRE, "structure", note)
    for note in conditions_particulieres_en_reserve(prop) if isinstance(prop, dict) and not erreurs_schema(prop) else []:
        noter(INFO, "couverture", note)
    for note in circonstances_par_evenement(prop) if isinstance(prop, dict) and not erreurs_schema(prop) else []:
        noter(INFO, "couverture", note)
    for note in obligations_mal_formees(prop) if isinstance(prop, dict) and not erreurs_schema(prop) else []:
        noter(BLOQUANT, "couverture", note)
    schema = erreurs_schema(prop)
    if not schema:
        try:
            en_prolog(prop, article)
        except (ErreurProposition, KeyError, TypeError, ValueError) as e:
            schema = [str(e)]
    for e in schema:
        noter(BLOQUANT, "structure", e)
    if schema:
        return problemes

    # 2. Vocabulaire
    voc = prolog.vocabulaire()
    declares = {(m.get("variable"), v) for m in prop.get("vocabulaire_manquant", []) for v in m.get("valeurs", [])}
    vus = set()
    for c in conditions(prop):
        for v, x in feuilles(c):
            if (v, x) in vus:
                continue
            vus.add((v, x))
            # Une valeur propre à un contrat (une formule) ne vaut que dans le sien (7.150) : « excellence » est une
            # formule de D ; l'écrire pour l'« Optimale » de C, c'est décider avec le contrat d'un autre.
            propres = valeurs_du_contrat(voc[v], contrat_id) if v in voc else None
            if propres is not None and x not in propres and (v, x) not in declares:
                noter(BLOQUANT, "vocabulaire", f"{v} = {x} : ce n'est pas un nom de ce contrat"
                      f"{' (' + ', '.join(propres) + ')' if propres else ''} ; employer le nom du texte et le déclarer")
                continue
            if v in voc and x in voc[v]["valeurs"] and (propres is None or x in propres):
                continue
            if (v, x) in declares:
                noter(BLOQUANT, "vocabulaire", f"{v} = {x} : fait nouveau déclaré par le modèle, à accepter "
                      f"(`--accepter-vocabulaire {article}`) ou à remplacer")
            else:
                noter(BLOQUANT, "vocabulaire", f"{v} = {x} : hors vocabulaire, et non déclaré")
    for m in prop.get("vocabulaire_manquant", []):
        if m.get("variable") in voc and voc[m["variable"]].get("parents") and not m.get("parent"):
            nouvelles = [x for x in m.get("valeurs", []) if x not in voc[m["variable"]]["valeurs"]]
            if nouvelles:
                noter(A_RELIRE, "vocabulaire", f"{m['variable']} = {', '.join(nouvelles)} : valeur nouvelle sans « parent » ; "
                      f"les règles déjà écrites ne la reconnaîtront pas (un ordinateur qui n'est plus de l'électronique, 7.64)")
        if m.get("variable") not in voc and not m.get("aide"):
            noter(A_RELIRE, "vocabulaire", f"{m.get('variable')} : variable nouvelle sans « aide » par valeur ; "
                  f"elle sera mal lue (7.59)")
        if m.get("variable") not in voc and not str(m.get("libelle") or "").strip():
            noter(A_RELIRE, "vocabulaire", f"{m.get('variable')} : variable nouvelle sans « libelle » ; l'écran et la "
                  f"fiche montreraient l'identifiant (7.146)")
        if m.get("variable") not in voc and not m.get("plus_proche"):
            noter(A_RELIRE, "vocabulaire", f"{m.get('variable')} : variable nouvelle sans « plus_proche » ; "
                  f"vérifier qu'un fait existant ne la dit pas déjà")
    for e in prop.get("evenements", []):
        if e not in voc["evenement"]["valeurs"] and ("evenement", e) not in declares:
            noter(BLOQUANT, "vocabulaire", f"evenement = {e} : hors vocabulaire, et non déclaré")

    # 3. Citations
    index = {c.id: c for c in clauses}
    # 2 bis. Une réduction n'est pas un refus (7.81) : le gel sans vidange chez l'assureur B réduit l'indemnité de
    # moitié, et la règle refusait ; le jeu fermé l'a montré (f-b02).
    # Seule compte la sanction qui suit le devoir (3.1.1.2 de B, une longue clause, parle ailleurs d'une réduction).
    # « La garantie intervient uniquement si… » est un refus (3.1.7.4 de B, signalé à tort : l'alinéa suivant
    # demande de « réduire l'étendue des dommages », 7.156).
    for g in prop.get("garanties", []):
        for o in g.get("obligations") or []:
            c = index.get(o.get("article"))
            t, d = (normaliser(c.texte), normaliser(str(o.get("texte", "")))) if c is not None else ("", "")
            i = t.find(d[:60]) if d else -1
            fenetre = t[i:i + len(d) + 400] if i >= 0 else ""
            if c is None or not fenetre:
                continue
            if re.search(r"\br[ée]dui|proportionnel", fenetre) \
                    and not re.search(r"refuser|pas de garantie|n.?est pas garanti|uniquement si|seulement si|qu.a (la )?condition", fenetre):
                noter(BLOQUANT, "couverture", f"garantie {g.get('id')} : l'obligation « {str(o.get('texte'))[:60]} » : "
                      f"sa clause ({o.get('article')}) réduit l'indemnité sans refuser ; une limite, pas une obligation")
            elif re.search(r"\br[ée]dui|proportionnel", fenetre):
                noter(A_RELIRE, "couverture", f"garantie {g.get('id')} : l'obligation « {str(o.get('texte'))[:60]} » : "
                      f"sa clause ({o.get('article')}) parle d'une réduction ; vérifier que ce devoir-ci refuse")
    for role, x in elements_cites(prop):
        art, texte = x.get("article"), x.get("texte", "")
        clause = index.get(art)
        if clause is None or not extrait_present(texte, clause.texte):
            # Le texte est peut-être exact, mais rattaché à la mauvaise clause (« 12 » pour « 12/sanitaires ») :
            # s'il figure dans une seule clause, on la rattache, comme la compilation des fiches le faisait.
            ailleurs = [c.id for c in clauses if texte and extrait_present(texte, c.texte)]
            # Les sous-points numérotés d'une liste (« 3.1.6.2.4 ») ne sont pas des clauses : leur clause est le
            # parent (3.1.6.2), à préférer à un texte identique ailleurs dans le contrat (Assureur B, 7.54).
            prefixees = [i for i in ailleurs if art and (i.startswith(str(art) + "/") or i.startswith(str(art) + "-")
                                                        or str(art).startswith(i + "."))]
            choix = prefixees if len(prefixees) == 1 else ailleurs
            if len(choix) == 1:
                x["article"] = choix[0]
                noter(INFO, "citation", f"{role} : citation rattachée à {choix[0]} (et non {art})")
                continue
        if clause is None:
            noter(BLOQUANT, "citation", f"{role} : article {art} inconnu")
        elif not extrait_present(texte, clause.texte):
            exact = passage_exact(texte, clause.texte)
            if exact:
                x["texte"] = exact
                noter(INFO, "citation", f"{role} ({art}) : citation réparée en « {exact[:80]} »")
            else:
                noter(BLOQUANT, "citation", f"{role} ({art}) : « {texte[:80]} » ne figure pas dans la clause")

    # 3 bis. Une exclusion qui ne vise qu'un bien n'exclut que ce bien (le reste du sinistre reste couvert).
    for x in exclusions(prop):
        fs = feuilles(x.get("condition"))
        if fs and all(v == "bien" for v, _ in fs) and x.get("portee") in (None, "tout"):
            biens = ", ".join(sorted({b for _, b in fs}))
            noter(A_RELIRE, "portée", f"exclusion « {str(x.get('texte'))[:60]} » : ne vise que {biens}, mais exclut "
                  f"tout le sinistre ; portée {{\"bien\": …}} ?")

    # 3 ter. Les exclusions de l'article valent pour toutes ses garanties (Assureur B 3.1.6, 7.53 : les extensions
    # « Privilège » et « Active » couvraient un vol sans aucune exclusion). Une garantie sans exclusion, à côté
    # d'une liste d'exclusions de l'article non mise en commun, est bloquante.
    if any(c.type == TypeClause.EXCLUSION for c in clauses_article(clauses, article)) and not prop.get("exclusions_communes"):
        for g in prop.get("garanties", []):
            # Une accessoire ne décide rien (7.68) : ses exclusions ne changeraient aucune décision (7.73).
            if not g.get("exclusions") and not g.get("accessoire"):
                noter(BLOQUANT, "exclusions", f"garantie {g.get('id')} : aucune exclusion, alors que l'article en a ; "
                      f"les mettre dans « exclusions_communes »")
    for x in exclusions(prop):
        if re.search(r"\b(a|à) l['’]exception\b|\bsauf\b|\bhormis\b", normaliser(str(x.get("texte", "")))) \
                and "non" not in json.dumps(x.get("condition"), ensure_ascii=False):
            noter(A_RELIRE, "réserve", f"exclusion « {str(x.get('texte'))[:60]} » : le texte a une réserve "
                  f"(« à l'exception de… ») que la condition ne reprend pas")
    for g in prop.get("garanties", []):
        for lim in g.get("limites", []):
            if re.search(r"\bs['’]?ils?\b|\bsi\b|\blorsque\b", normaliser(str(lim.get("texte", "")))):
                noter(A_RELIRE, "limite", f"limite « {str(lim.get('texte'))[:60]} » ({g.get('id')}) : elle pose une "
                      f"condition ; circonstance ou garantie à part ?")

    # 4. Couverture des listes d'exclusions
    textes = [x.get("texte", "") for x in exclusions(prop)]
    textes += [n.get("texte", "") for n in non_traduits(prop)]
    textes += [n.get("texte", "") for n in prop.get("hors_decision") or []]
    for c in clauses_article(clauses, article):
        if c.type != TypeClause.EXCLUSION:
            continue
        for item in items_exclusion(c.texte):
            if not couvert_par(item, textes):
                noter(BLOQUANT, "couverture", f"exclusion du contrat absente des règles ({c.id}) : « {item[:100]} »")
    # Un passage sans effet sur la décision de couverture (procédure après sinistre) : le relecteur le classe
    # « hors décision » au lieu de le laisser non traduit (7.55). Il reste cité, donc vérifié mot pour mot.
    index_h = {c.id: c for c in clauses}
    for n in prop.get("hors_decision") or []:
        clause = index_h.get(n.get("article"))
        if clause is None or not extrait_present(n.get("texte", ""), clause.texte):
            noter(BLOQUANT, "citation", f"hors décision ({n.get('article')}) : « {str(n.get('texte'))[:80]} » ne figure pas dans la clause")
        else:
            noter(INFO, "couverture", f"hors décision ({n.get('article')}) : {n.get('pourquoi', '')}")
    # Dans un article fait seulement de garanties accessoires, ce qui reste non traduit (un barème, une procédure
    # d'expertise) ne peut pas changer une décision : le moteur ne les consulte qu'après un sinistre couvert (7.68).
    seulement_accessoires = bool(prop.get("garanties")) and all(isinstance(g, dict) and g.get("accessoire")
                                                                for g in prop["garanties"])
    for n in non_traduits(prop):
        noter(INFO if seulement_accessoires else BLOQUANT, "couverture",
              f"déclaré non traduit ({n.get('article')}) : « {str(n.get('texte'))[:100]} » — {n.get('pourquoi', '')}"
              + (" (garanties accessoires : sans effet sur la décision)" if seulement_accessoires else ""))

    # 4 bis. La définition de l'événement couvert (« tempête ») est une condition de la garantie.
    titres = normaliser(" ".join(c.chemin[-1] for c in clauses_article(clauses, article) if c.chemin))
    employes = {x.get("article") for _, x in elements_cites(prop)} | {n.get("article") for n in non_traduits(prop)}
    # Une définition classée « hors décision » par le relecteur, citée, compte aussi : le contenu assuré (12/contenu)
    # ne restreint pas une responsabilité civile, que « contenu » figure dans un titre de l'article ou non (7.99).
    employes |= {n.get("article") for n in prop.get("hors_decision") or []}
    # Un concept déjà défini dans les règles du contrat, et employé par la proposition, compte aussi (7.63) :
    # `concept(vol)` renvoie à la définition 12/vol acceptée avec la garantie vol.
    employes_c = {n for c in conditions(prop) for n in re.findall(r'"concept":\s*"([a-z0-9_]+)"', json.dumps(c))}
    employes |= {a for n, a in re.findall(r"^definition\(\s*([a-z0-9_]+)\s*,.*?,\s*'([^']+)'", contrat_pl or "", re.M | re.S)
                 if n in employes_c}
    for d in definitions_utiles(clauses, clauses_article(clauses, article)):
        terme_defini = normaliser((d.chemin[-1] if d.chemin else d.id.split("/")[-1]).replace("-", " "))
        # « NOUS », « VOUS » : le lexique de l'assureur D les définit, et « Ce que nous garantissons » est le titre
        # de chaque garantie ; ce ne sont pas des restrictions (7.89).
        if terme_defini and terme_defini not in ("nous", "vous") and re.search(rf"\b{re.escape(terme_defini)}", titres) \
                and d.id not in employes:
            noter(BLOQUANT, "couverture", f"la définition {d.id} de l'événement couvert n'est pas traduite "
                  f"(elle restreint la garantie) : l'employer ou la déclarer non traduite")

    for note in exclusions_hors_perimetre(prop, voc):
        noter(A_RELIRE, "portée", note)

    # 5. Concepts et identifiants
    existants = set(concepts_existants(contrat_pl))
    nouveaux = {d.get("concept") for d in prop.get("definitions", [])}
    for n in nouveaux & existants:
        noter(BLOQUANT, "concept", f"le concept {n} est déjà défini dans les règles du contrat")
    for c in conditions(prop):
        for n in concepts_employes(c):
            if n not in existants | nouveaux:
                noter(BLOQUANT, "concept", f"concept inconnu : {n}")
    for x in prop.get("extensions") or []:
        if x.get("concept") not in existants | nouveaux:
            # Le nom vient de ce contrat, pas d'un autre : l'assureur B appelle son lieu assuré
            # `batiment_designe`, le modèle écrivait `batiment` comme pour A (7.72).
            noter(BLOQUANT, "concept", f"extension d'un concept inconnu : {x.get('concept')} (concepts de ce contrat : "
                  f"{', '.join(sorted(existants | nouveaux)) or 'aucun'})")
    connues = set(re.findall(r"^garantie\((\w+),", contrat_pl, re.M)) | {str(g.get("id")) for g in prop.get("garanties", [])}
    for x in prop.get("exclusions_communes") or []:
        inconnues = [i for i in x.get("cibles") or [] if i not in connues]
        if inconnues:
            noter(BLOQUANT, "identifiant", f"exclusion ({x.get('article')}) : garanties visées inconnues : {', '.join(inconnues)}")
    cycle = cycle_de_concepts(contrat_pl, prop)
    if cycle:
        # 1.5 de l'assureur D : `batiment` étendu au logement de vacances pour le `contenu`, lui-même défini « dans le
        # `batiment` » ; l'oracle et Prolog bouclaient sans fin à la première question sur le lieu (7.91).
        noter(BLOQUANT, "concept", f"concepts définis l'un par l'autre : {' → '.join(cycle)} ; écrire les faits au lieu du concept")
    deja = set(re.findall(r"^garantie\((\w+),", contrat_pl, re.M))
    ids = [g.get("id", "") for g in prop.get("garanties", [])]
    for i in ids:
        if not IDENT.match(str(i)):
            noter(BLOQUANT, "identifiant", f"identifiant invalide : {i}")
        elif i in deja:
            noter(BLOQUANT, "identifiant", f"la garantie {i} existe déjà dans les règles du contrat")
    if len(ids) != len(set(ids)):
        noter(BLOQUANT, "identifiant", "deux garanties portent le même identifiant")
    return problemes


def controler_avec_prolog(contrat_id: str, contrat_pl: str, prop_pl: str, cas: list[tuple[str, dict]]) -> list[dict]:
    """Chargement sans avertissement des règles fusionnées, puis non-régression sur les cas annotés."""
    if prolog.swipl() is None:
        return [{"gravite": A_RELIRE, "controle": "prolog",
                 "message": "SWI-Prolog absent : chargement et non-régression non vérifiés"}]
    problemes = []
    with tempfile.TemporaryDirectory() as d:
        fusion = Path(d) / f"{contrat_id}.pl"
        fusion.write_text(fusionner(contrat_pl, prop_pl), encoding="utf-8")
        try:
            prolog.executer(contrat_id, "vocabulaire_json", regles=fusion)
        except prolog.ErreurRegles as e:
            return [{"gravite": BLOQUANT, "controle": "prolog", "message": f"les règles ne se chargent pas : {e}"}]
        for i, faits in cas:
            try:
                avant = prolog.decider(contrat_id, faits)["decision"]
                apres = prolog.executer(contrat_id, "decider_json", faits, regles=fusion)["decision"]
            except prolog.ErreurRegles as e:
                problemes.append({"gravite": BLOQUANT, "controle": "prolog", "message": f"{i} : {e}"})
                continue
            if avant != apres:
                problemes.append({"gravite": A_RELIRE, "controle": "non-régression",
                                  "message": f"{i} : {avant} → {apres} avec les nouvelles règles"})
    return problemes
