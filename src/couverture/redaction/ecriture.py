"""Du JSON de la proposition aux règles Prolog : c'est le code qui écrit les règles, jamais le modèle."""

from __future__ import annotations

import json

from .consigne import IDENT, ErreurProposition


# --- JSON → Prolog -----------------------------------------------------------------------------------------

def atome(x) -> str:
    """Un atome Prolog : tel quel s'il est simple, entre apostrophes sinon."""
    x = str(x)
    return x if IDENT.match(x) else "'" + x.replace("\\", "\\\\").replace("'", "\\'") + "'"


def chaine(s) -> str:
    """Une chaîne Prolog entre guillemets, sur une seule ligne."""
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ") + '"'


def terme(c) -> str:
    """Une condition JSON en terme Prolog ; ErreurProposition si elle est mal formée."""
    if c is None:
        return "faux"
    if not isinstance(c, dict) or len(c) != 1:
        raise ErreurProposition(f"condition mal formée : {json.dumps(c, ensure_ascii=False)[:120]}")
    (cle, v), = c.items()
    if cle == "f" and isinstance(v, list) and len(v) == 2:
        return f"f({atome(v[0])}, {atome(v[1])})"
    if cle in ("et", "ou") and isinstance(v, list) and v:
        return f"{cle}([{', '.join(terme(x) for x in v)}])"
    if cle == "non":
        return f"non({terme(v)})"
    if cle == "si" and isinstance(v, list) and len(v) == 2:
        return f"si({terme(v[0])}, {terme(v[1])})"
    if cle == "concept" and isinstance(v, str):
        return f"concept({atome(v)})"
    raise ErreurProposition(f"condition mal formée : {json.dumps(c, ensure_ascii=False)[:120]}")


def portee(p) -> str:
    """La portée d'une exclusion, en Prolog : `tout`, ou `bien(x)` quand elle ne retire qu'un bien."""
    if p in (None, "tout"):
        return "tout"
    if isinstance(p, dict) and set(p) == {"bien"}:
        return f"bien({atome(p['bien'])})"
    raise ErreurProposition(f"portée mal formée : {p}")


def oui_non(b) -> str:
    """Un booléen en `oui` ou `non`."""
    return "oui" if b else "non"


def en_prolog(prop: dict, article: str, entete: str = "") -> str:
    """Les règles d'une proposition, sans directive : elles s'ajoutent à la suite du fichier du contrat."""
    lignes = [f"% --- Art. {article} : proposition rédigée par le modèle{(' — ' + entete) if entete else ''} ---"]
    # Un événement n'est « traduit » que par une garantie de base : des frais accessoires ne disent pas si une
    # tempête est couverte (7.68).
    if any(not g.get("accessoire") for g in prop.get("garanties", [])) or not prop.get("garanties"):
        for e in prop.get("evenements", []):
            lignes.append(f"evenement_traduit({atome(e)}).")
    for d in prop.get("definitions", []):
        lignes.append(f"definition({atome(d['concept'])}, {terme(d['condition'])}, {atome(d['article'])},\n    {chaine(d['texte'])}).")
    for d in prop.get("extensions") or []:       # 7.69 : élargit une définition, pour toutes les garanties
        lignes.append(f"extension({atome(d['concept'])}, {terme(d['condition'])}, {atome(d['article'])},\n    {chaine(d['texte'])}).")
    for g in prop.get("garanties", []):
        gid = atome(g["id"])
        lignes.append(f"garantie({gid}, {chaine(g['nom'])}, {atome(g['article'])},\n    {chaine(g['texte'])}).")
        for p in g.get("perimetre", []):
            lignes.append(f"perimetre({gid}, {terme(p)}).")
        for c in g.get("circonstances", []):
            lignes.append(f"circonstance({gid}, {terme(c['condition'])}, {atome(c['article'])},\n    {chaine(c['texte'])}).")
        for o in g.get("obligations", []):
            lignes.append(f"obligation({gid}, {terme(o['condition'])}, {terme(o.get('exception'))}, "
                          f"{oui_non(o.get('lien_causal'))}, {atome(o['article'])},\n    {chaine(o['texte'])}).")
        for x in g.get("exclusions", []):
            lignes.append(f"exclusion({gid}, {terme(x['condition'])}, {portee(x.get('portee'))}, "
                          f"{oui_non(x.get('a_demander'))}, {atome(x['article'])},\n    {chaine(x['texte'])}).")
        for lim in g.get("limites", []):
            lignes.append(f"limite({gid}, {atome(lim['article'])}, {chaine(lim['texte'])}, {chaine(lim.get('montant', ''))}).")
    for g in prop.get("garanties", []):
        if g.get("accessoire"):
            lignes.append(f"accessoire({atome(g['id'])}).")
    if prop.get("exclusions_communes"):
        # Un article d'exclusions générales (« Titre IX : ce que nous ne garantissons jamais ») n'a pas de
        # garantie à lui : ses exclusions visent toutes celles du contrat (`tous`, 7.88).
        cibles = ("[" + ", ".join(atome(g["id"]) for g in prop["garanties"]) + "]") if prop.get("garanties") else "tous"
        for x in prop["exclusions_communes"]:
            # « cibles » (7.96) : les garanties que l'exclusion vise, quand ce ne sont ni celles de l'article ni toutes.
            # Les biens exclus du titre « Dommages aux biens » (véhicules, animaux) ne doivent pas exclure la
            # responsabilité civile, où le bien endommagé est celui d'un tiers (la voiture rayée par le vélo).
            c = ("[" + ", ".join(atome(i) for i in x["cibles"]) + "]") if x.get("cibles") else cibles
            lignes.append(f"exclusion({c}, {terme(x['condition'])}, {portee(x.get('portee'))}, "
                          f"{oui_non(x.get('a_demander'))}, {atome(x['article'])},\n    {chaine(x['texte'])}).")
    return "\n".join(lignes) + "\n"


def exclusions(prop: dict) -> list[dict]:
    """Toutes les exclusions de la proposition : celles des garanties et celles communes à l'article."""
    return [x for g in prop.get("garanties", []) for x in g.get("exclusions", [])] + list(prop.get("exclusions_communes") or [])


def fusionner(contrat_pl: str, *propositions_pl: str) -> str:
    """Les règles du contrat, suivies de celles des propositions."""
    return contrat_pl.rstrip("\n") + "\n\n" + "\n".join(propositions_pl)
