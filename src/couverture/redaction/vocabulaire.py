"""Le vocabulaire complété par une proposition, et rangé (le commun, puis un fichier par contrat) : les faits nouveaux, et les événements pour lesquels on lit chaque variable."""

from __future__ import annotations

import json
from pathlib import Path

from .. import lecture, prolog
from .consigne import IDENT
from .controles import feuilles, feuilles_positives
from .ecriture import exclusions


DESCRIPTIONS = {
    True: "Vocabulaire commun : le socle (événement, bien, lieu) et les variables que plusieurs contrats emploient. "
          "« plusieurs » : la variable prend une liste. « parents » : la hiérarchie des valeurs (une vitre est un "
          "élément du bâtiment). « pour » : les événements auxquels une variable s'applique. « aide » : le sens des "
          "valeurs proches, donné au modèle qui lit. « libelle » : le nom montré d'une variable ; « libelles » : "
          "celui d'une valeur, quand l'identifiant s'écrit mal. Rangé par `couverture regles --ranger`.",
    False: "Variables que seules les règles de ce contrat emploient (regles/{contrat}.pl). Même format que "
           "commun.json. Rangé par `couverture regles --ranger` : une variable qu'un autre contrat se met à employer "
           "passe dans commun.json.",
}


def repartir(voc: dict) -> dict[str, dict]:
    """{fichier : ses variables}, dans l'ordre du vocabulaire. Une variable que les règles d'un seul contrat
    emploient va dans le fichier de ce contrat ; le socle, celles que plusieurs emploient et celles qu'aucun
    n'emploie encore restent dans le commun (7.119)."""
    contrats = prolog.contrats_regles()
    emplois = {c: prolog.variables_employees(c) for c in contrats}
    fichiers: dict[str, dict] = {prolog.COMMUN: {}, **{c: {} for c in contrats}}
    for v, d in voc.items():
        qui = [c for c in contrats if v in emplois[c]]
        fichiers[qui[0] if len(qui) == 1 and v not in lecture.SOCLE else prolog.COMMUN][v] = d
    return fichiers


def ranger(voc: dict | None = None, dossier: Path | None = None) -> list[str]:
    """Écrit le vocabulaire rangé (`repartir`). Rend les variables qui ont changé de fichier."""
    dossier = dossier or prolog.VOCABULAIRE
    avant = {v: f.stem for f in prolog.fichiers_vocabulaire(dossier) if f.exists()
             for v in json.loads(f.read_text(encoding="utf-8"))["variables"]}
    voc = prolog.vocabulaire(dossier) if voc is None else voc
    deplacees = []
    for nom, variables in repartir(voc).items():
        deplacees += [f"{v} : {avant[v]} → {nom}" for v in variables if avant.get(v, nom) != nom]
        doc = {"_description": DESCRIPTIONS[nom == prolog.COMMUN].replace("{contrat}", nom), "variables": variables}
        (dossier / f"{nom}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
                                            newline="\n")
    return deplacees


SOUSCRIPTION = ("conditions particulières", "souscrit")


def bilan(dossier: Path | None = None) -> dict:
    """Ce que le vocabulaire coûte à chaque contrat, calculé d'après les règles (7.140) : par contrat, les
    variables qu'il emploie, celles qu'il partage avec un autre et celles qu'il est seul à employer ; et, dans
    tout le vocabulaire, les faits de souscription (la question porte sur les conditions particulières ou sur
    ce qui est souscrit : ce n'est pas la déclaration qui le dit), les variables jamais lues dans une
    déclaration (« pour » : jamais, accessoire, extension) et celles qu'aucune règle n'emploie encore."""
    voc = prolog.vocabulaire(dossier)
    emplois = {c: prolog.variables_employees(c) & set(voc) for c in prolog.contrats_regles()}
    nb = {v: sum(v in e for e in emplois.values()) for v in voc}
    souscription = [v for v, d in voc.items() if any(m in d.get("question", "") for m in SOUSCRIPTION)]
    non_lues = [v for v, d in voc.items() if d.get("pour") and set(d["pour"]) <= set(PSEUDO_EVENEMENTS)]
    propres = [v for v in voc if nb[v] == 1 and v not in lecture.SOCLE]
    return {"variables": len(voc),
            "contrats": {c: {"employees": len(e), "partagees": sum(nb[v] > 1 or v in lecture.SOCLE for v in e),
                             "propres": sum(nb[v] == 1 and v not in lecture.SOCLE for v in e)}
                         for c, e in emplois.items()},
            "propres": propres,
            "souscription": souscription,
            "non_lues": non_lues,
            "sans_regle": [v for v in voc if nb[v] == 0 and v not in lecture.SOCLE],
            "propres_lues_dans_la_declaration": [v for v in propres if v not in souscription and v not in non_lues]}


def mal_rangees(dossier: Path | None = None) -> list[str]:
    """Les variables qui ne sont pas dans le fichier que `repartir` leur donne (après des règles écrites à la main)."""
    dossier = dossier or prolog.VOCABULAIRE
    ou = {v: f.stem for f in prolog.fichiers_vocabulaire(dossier)
          for v in json.loads(f.read_text(encoding="utf-8"))["variables"]}
    return [f"{v} : dans {ou[v]}, attendue dans {nom}" for nom, variables in repartir(prolog.vocabulaire(dossier)).items()
            for v in variables if ou[v] != nom]


def accepter_vocabulaire(prop: dict, dossier: Path | None = None) -> list[str]:
    """Ajoute au vocabulaire les faits déclarés par le modèle, puis le range. Décision humaine : c'est la commande
    qu'on lance après avoir lu les questions proposées."""
    dossier = dossier or prolog.VOCABULAIRE
    voc, ajouts = prolog.vocabulaire(dossier), []
    nouvelles_variables = {m.get("variable") for m in prop.get("vocabulaire_manquant", []) if m.get("variable") not in voc}
    lieux = lieux_par_variable(prop)
    for m in prop.get("vocabulaire_manquant", []):
        v, valeurs = m.get("variable"), [str(x) for x in m.get("valeurs", [])]
        if not (v and IDENT.match(v) and valeurs and all(IDENT.match(x) for x in valeurs)):
            # Refusée en clair : en silence, elle restait « à accepter » à chaque contrôle (6.1, « 22h_7h »).
            ajouts.append(f"! {v} refusée : nom ou valeur hors des identifiants permis (minuscule d'abord) : "
                          f"{', '.join(x for x in [v, *valeurs] if not (x and IDENT.match(x)))} — à renommer dans la proposition")
            continue
        if v in voc:
            nouvelles = [x for x in valeurs if x not in voc[v]["valeurs"]]
            voc[v]["valeurs"] += nouvelles
            avant = list(voc[v].get("pour") or [])
            evs = evenements_par_variable(prop).get(v) or list(prop.get("evenements") or [])
            evs = [e for e in evs if e not in PSEUDO_EVENEMENTS]
            # « jamais » (7.90) : une option des conditions particulières, réserve d'exclusion partout ; qu'une garantie
            # l'emploie ne la rend pas lisible dans une déclaration (le Pack Jardin pour la tempête, 2.3 de D).
            if avant == [JAMAIS]:
                evs = []
            if avant and evs:
                voc[v]["pour"] = avant + [e for e in evs if e not in avant]
                ajouts += [f"{v} : lue aussi pour {e}" for e in evs if e not in avant]
            for x in nouvelles:
                if (m.get("aide") or {}).get(x):
                    voc[v].setdefault("aide", {})[x] = str(m["aide"][x])
                # Une valeur plus fine qu'une valeur existante doit y être rattachée : sans cela, un ordinateur lu
                # `appareil_informatique` n'est plus de l'« electronique » pour les règles déjà écrites (7.64).
                parent = (m.get("parent") or {}).get(x) if isinstance(m.get("parent"), dict) else m.get("parent")
                if parent and parent in voc[v]["valeurs"] and parent != x:
                    voc[v].setdefault("parents", {})[x] = [parent]
            ajouts += [f"{v} = {x}" for x in nouvelles]
        else:
            voc[v] = {"valeurs": valeurs, "question": m.get("question") or f"Préciser : {v}"}
            # Une variable nouvelle doit apprendre à être lue : sans aide, le premier banc Assureur B a lu « hôte »
            # comme « hôtel » (7.59). La rédaction propose l'aide, le relecteur l'accepte avec la variable.
            aide = {str(k): str(x) for k, x in (m.get("aide") or {}).items() if str(k) in valeurs}
            if aide:
                voc[v]["aide"] = aide
            # Sans « pour », la variable serait lue pour tous les sinistres (un dégât des eaux se verrait demander
            # la formule « Privilège ») : elle vaut pour les événements de la garantie qui l'a fait naître (7.56).
            evs = evenements_par_variable(prop).get(v) or list(prop.get("evenements") or [])
            if evs:
                voc[v]["pour"] = evs
            elif not prop.get("garanties") and v in reserve_seulement(prop):
                # Un article sans garantie (les biens assurés, les exclusions générales) n'a pas d'événement : sa
                # variable aurait été lue pour chaque sinistre. Quand elle ne sert qu'à des exclusions jamais
                # demandées (une option, un pack, une rixe), elle n'est pas lue : la réserve suffit (7.90).
                voc[v]["pour"] = [JAMAIS]
                ajouts.append(f"{v} : jamais lue (réserve d'une exclusion que l'assureur prouve)")
                ajouts.append(f"{v} ({', '.join(valeurs)}) : « {voc[v]['question']} »")
                continue
            if lieux.get(v):
                voc[v]["seulement_si"] = {"lieu": lieux[v]}
            ajouts.append(f"{v} ({', '.join(valeurs)}) : « {voc[v]['question']} »")
    ajouts += etendre_pour(prop, voc)
    # Une variable d'extension (le séjour temporaire élargit le bâtiment) vaut pour toutes les garanties qui
    # emploient le concept, mais seulement quand la déclaration l'entame : elle est lue si le temps 1 a lu le
    # lieu que l'extension demande (« si »), pas pour chaque sinistre (7.70 : lue partout, elle allongeait la
    # lecture de tous). Une variable nouvelle, née de l'extension, n'est lue que là.
    for x in prop.get("extensions") or []:
        feuilles_x = feuilles(x.get("condition"))
        declencheurs = {}
        # Un lieu ou un bien sous un « non » n'entame pas l'extension : « sans les objets précieux » (1.5 de
        # l'assureur D) faisait lire le pays de chaque vol de bijoux (7.90).
        for v, val in feuilles_positives(x.get("condition")):
            if v in lecture.SOCLE:
                declencheurs.setdefault(v, [])
                if val not in declencheurs[v]:
                    declencheurs[v].append(val)
        for v, _ in feuilles_x:
            if v in lecture.SOCLE or v not in voc:
                continue
            if not declencheurs:
                # Sans lieu ni bien qui la déclenche (« déménagement depuis moins de 90 jours »), une variable née
                # de l'extension n'est pas lue d'emblée : sans « pour », elle l'était pour chaque sinistre (7.73).
                # L'extension, entamée par ses autres faits, la pose en question.
                if v in nouvelles_variables and voc[v].get("pour") != [EXTENSION]:
                    voc[v]["pour"] = [EXTENSION]
                    ajouts.append(f"{v} : lue seulement en question (extension de « {x.get('concept')} »)")
                continue
            si = voc[v].setdefault("si", {})
            for var, vals in declencheurs.items():
                si[var] = si.get(var, []) + [y for y in vals if y not in si.get(var, [])]
            if v in nouvelles_variables:
                voc[v]["pour"] = [EXTENSION]
            ajouts.append(f"{v} : lue aussi si " + " ; ".join(f"{var} = {'/'.join(vals)}" for var, vals in declencheurs.items())
                          + f" (extension de « {x.get('concept')} »)")
    ajouts = list(dict.fromkeys(ajouts))  # une ligne par fait, pas une par extension qui l'emploie
    if ajouts:
        ranger(voc, dossier)
    return ajouts


ACCESSOIRE = "accessoire"      # « pour » d'une variable que seules des garanties accessoires emploient : pas lue
EXTENSION = "extension"        # « pour » d'une variable née d'une extension : lue seulement si son lieu est lu
JAMAIS = "jamais"              # « pour » d'une variable qui n'est jamais lue dans la déclaration (7.90)
# Ces « pour » ne sont pas des événements : ajoutés à une variable déjà lue pour un vol, ils n'y changent
# rien et brouillent le vocabulaire (« option_incendie : lue aussi pour accessoire », 7.73).
PSEUDO_EVENEMENTS = (ACCESSOIRE, EXTENSION, JAMAIS)


def reserve_seulement(prop: dict) -> set[str]:
    """Les variables qui n'apparaissent que dans des exclusions jamais demandées (« a_demander » faux)."""
    dans, ailleurs = set(), set()
    for x in exclusions(prop):
        (dans if not x.get("a_demander") else ailleurs).update(v for v, _ in feuilles(x.get("condition")))
    autres = [d.get("condition") for d in (prop.get("definitions") or []) + (prop.get("extensions") or [])]
    autres += [g.get(k) for g in prop.get("garanties") or [] for k in ("perimetre",)]
    for c in autres:
        ailleurs.update(v for v, _ in feuilles(c if isinstance(c, dict) else {"et": c} if isinstance(c, list) else None))
    return dans - ailleurs


def evenements_par_variable(prop: dict) -> dict[str, list[str]]:
    """Pour chaque variable employée, les événements des garanties qui l'emploient. Un article peut réunir des
    garanties d'événements différents (Assureur B 3.1.1 : incendie, heurt, vol, vandalisme…) : les flammes ne sont
    pas à lire pour un vol (7.65). Une exclusion commune vaut pour les événements de toutes les garanties."""
    defs = {d.get("concept"): d.get("condition") for d in prop.get("definitions", []) if d.get("concept")}

    tous = list(prop.get("evenements") or [])
    res: dict[str, list[str]] = {}

    def noter(c, evs):
        # Une variable posée dans un « et » ou un « si » qui nomme l'événement (« vol et laissé sans surveillance »)
        # ne se lit que pour cet événement, même si la garantie en couvre d'autres (6.1, 7.71).
        for v, evs_v, _ in occurrences(c, defs, evs):
            res.setdefault(v, [])
            res[v] += [e for e in evs_v if e not in res[v]]

    union = []
    for g in prop.get("garanties", []):
        evs = [x for c in g.get("perimetre", []) for v, x in feuilles(c) if v == "evenement"] or tous
        if g.get("accessoire"):
            # Une accessoire ne décide rien (7.68) : ses faits ne sont pas lus à chaque déclaration, ils allongeaient
            # la lecture de toutes (« malveillance », « RC locative » cherchées dans une simple perte, 7.70).
            evs = [ACCESSOIRE]
        union += [e for e in evs if e not in union]
        for c in g.get("perimetre", []):
            noter(c, evs)
        for cle in ("circonstances", "obligations", "exclusions"):
            for x in g.get(cle, []):
                noter(x.get("condition"), evs)
                if x.get("exception") is not None:
                    noter(x["exception"], evs)
    for x in prop.get("exclusions_communes") or []:
        noter(x.get("condition"), union or tous)
    return res


def occurrences(c, defs: dict, evs, lieux=None, vus=()):
    """(variable, événements, lieux) pour chaque fait employé par la condition : les événements et les lieux que
    le « et » ou le « si » qui l'entoure exige. `lieux` vaut None quand rien n'en exige."""
    if not isinstance(c, dict) or len(c) != 1:
        return []
    (cle, v), = c.items()
    if cle == "f":
        return [] if str(v[0]) in lecture.SOCLE else [(str(v[0]), list(evs), lieux)]
    if cle == "concept":
        return occurrences(defs[v], defs, evs, lieux, vus + (v,)) if v in defs and v not in vus else []

    def restreint(conds, evs, lieux):
        dits = [x["f"] for x in conds if isinstance(x, dict) and isinstance(x.get("f"), list) and len(x["f"]) == 2]
        e = [x for _, x in (d for d in dits if d[0] == "evenement")]
        l = [x for _, x in (d for d in dits if d[0] == "lieu")]
        evs = [x for x in evs if x in e] or (list(evs) if not e else e)
        if l:
            lieux = sorted(set(l) & set(lieux)) if lieux is not None else sorted(set(l))
        return evs, lieux

    if cle == "et":
        evs2, lieux2 = restreint(v, evs, lieux)
        return [o for x in v for o in occurrences(x, defs, evs2, lieux2, vus)]
    if cle == "si":
        evs2, lieux2 = restreint([v[0]] + (v[0].get("et", []) if isinstance(v[0], dict) else []), evs, lieux)
        return occurrences(v[0], defs, evs, lieux, vus) + occurrences(v[1], defs, evs2, lieux2, vus)
    if cle == "ou":
        return [o for x in v for o in occurrences(x, defs, evs, lieux, vus)]
    if cle == "non":
        return occurrences(v, defs, evs, lieux, vus)
    return []


def lieux_par_variable(prop: dict) -> dict[str, list[str]]:
    """Les variables que la proposition n'emploie que dans un lieu donné (« véhicule sur la voie publique,
    habitacle fermé ») : elles ne se lisent que si le lieu lu est celui-là (7.71). Une seule occurrence sans lieu
    exigé, et la variable se lit partout."""
    defs = {d.get("concept"): d.get("condition") for d in prop.get("definitions", []) if d.get("concept")}
    vus: dict[str, set | None] = {}
    conds = [c for g in prop.get("garanties", []) for c in g.get("perimetre", [])]
    conds += [x.get(k) for g in prop.get("garanties", []) for cle in ("circonstances", "obligations", "exclusions")
              for x in g.get(cle, []) for k in ("condition", "exception") if x.get(k) is not None]
    conds += [x.get("condition") for x in prop.get("exclusions_communes") or []]
    for c in conds:
        for v, _, lieux in occurrences(c, defs, []):
            if lieux is None:
                vus[v] = None
            elif v not in vus:
                vus[v] = set(lieux)
            elif vus[v] is not None:
                vus[v] |= set(lieux)
    return {v: sorted(l) for v, l in vus.items() if l}


def etendre_pour(prop: dict, voc: dict) -> list[str]:
    """Une variable existante que la proposition emploie doit être lue pour les événements des garanties qui
    l'emploient : `prevention_gel`, lue pour les dégâts des eaux, sert aussi au mazout (2.8). Sans cela, la
    lecture restreinte aux événements (7.56) ne la chercherait jamais dans une déclaration de mazout (7.63)."""
    ajouts = []
    for v, evenements in sorted(evenements_par_variable(prop).items()):
        d = voc.get(v)
        if not d or not d.get("pour") or not evenements or d["pour"] == [JAMAIS]:
            continue
        manquants = [e for e in evenements if e not in d["pour"] and e not in PSEUDO_EVENEMENTS]
        if manquants:
            d["pour"] = d["pour"] + manquants
            ajouts.append(f"{v} : lue aussi pour {', '.join(manquants)}")
    return ajouts
