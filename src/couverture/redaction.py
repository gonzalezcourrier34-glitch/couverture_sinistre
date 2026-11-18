"""Méthode « regles », étape de rédaction : le modèle traduit une garantie du contrat en règles.

    clauses de l'article (et ses définitions) ─► Mistral Large ─► proposition JSON
        ─► règles Prolog générées par le code ─► contrôles ─► relecture humaine ─► --accepter

Le modèle n'écrit pas de Prolog : il remplit un schéma JSON (périmètre, circonstances,
obligations, exclusions, limites), et c'est le code qui écrit les règles. Un JSON se contrôle
champ par champ ; une syntaxe Prolog inventée ne se contrôle qu'en la chargeant.

Les contrôles, tous automatiques :
  1. structure : chaque condition est un terme connu (f, et, ou, non, si, concept) ;
  2. vocabulaire : chaque fait est dans regles/vocabulaire.json ; un fait nouveau doit être
     **déclaré** par le modèle (vocabulaire_manquant), et c'est un humain qui l'accepte ;
  3. citations : chaque phrase figure mot pour mot dans la clause citée (réparée si les mots sont
     dans l'ordre, refusée sinon) ;
  4. couverture : chaque exclusion de la liste du contrat est traduite, ou déclarée non traduite.
     Une exclusion oubliée, c'est un « couvert à tort » ;
  5. concepts et identifiants : rien d'inconnu, aucune collision avec les règles existantes ;
  6. avec SWI-Prolog : les règles fusionnées se chargent sans avertissement, et les cas déjà
     annotés gardent leur décision (les changements sont listés pour relecture).

La proposition (JSON) est la source : on peut la corriger à la main, puis relancer les contrôles
sans rappeler le modèle (`couverture rediger --controler`).
"""

from __future__ import annotations

import json
import re
import tempfile
from datetime import date
from pathlib import Path

from . import prolog
from .llm import appeler_json as _appeler, pour_travail_long as pour_compiler
from .models import Clause, TypeClause
from .texte import normaliser
from .validation import _compact, extrait_present, passage_exact

PROPOSITIONS = prolog.DOSSIER / "propositions"
VERSION = "v3"
IDENT = re.compile(r"^[a-z][a-z0-9_]*$")
BLOQUANT, A_RELIRE, INFO = "bloquant", "à relire", "info"

SYSTEME_REDACTION = """Tu traduis une garantie d'un contrat d'assurance habitation en règles pour un moteur logique. Tu ne juges aucun sinistre.

## Le moteur
Une garantie a :
- un périmètre : des conditions qui doivent toutes tenir pour qu'elle concerne le sinistre (événement, bien, lieu) ;
- des circonstances : les autres conditions que pose le texte pour qu'elle joue ;
- des obligations de prévention : ce que l'assuré doit faire ; « exception » est ce qui l'excuse (ou null) ; « lien_causal » vaut true si le contrat ne refuse que s'il y a un lien causal avec le sinistre ;
- des exclusions : « portee » vaut "tout", ou {"bien": "valeur"} si elle n'exclut qu'un bien ; « a_demander » vaut true si l'on doit poser la question quand le fait est inconnu (circonstance que le déclarant ne mentionnerait pas de lui-même), false sinon ;
- des limites : un plafond, sans condition.
Les exclusions d'un article (« vols exclus ») valent pour TOUTES ses garanties, extensions comprises : mets-les dans "exclusions_communes", pas dans une seule garantie. N'attache à une garantie que les exclusions qui ne valent que pour elle.
Une condition est un terme JSON : {"f": ["variable", "valeur"]}, {"et": [c1, c2]}, {"ou": [c1, c2]}, {"non": c}, {"si": [a, b]} (si a alors b), {"concept": "nom"} (une définition).
La logique a trois valeurs : un fait que la déclaration ne donne pas est « inconnu », et le moteur pose alors la question. N'essaie pas de compenser un fait inconnu.

## Règles d'écriture
1. Chaque garantie, définition, circonstance, obligation, exclusion et limite porte "article" (l'identifiant de clause fourni) et "texte" : une phrase COPIÉE MOT POUR MOT de cette clause. Pas de reformulation, pas de coupure, pas de « … ».
2. N'emploie que les variables et les valeurs du vocabulaire. Si le texte exige un fait que le vocabulaire n'a pas, n'approxime pas avec un fait voisin : emploie une variable ou une valeur nouvelle ET déclare-la dans "vocabulaire_manquant" (variable, valeurs, question à poser à l'assuré, pourquoi, "plus_proche" : la variable existante la plus proche et pourquoi elle ne suffit pas). Un humain décidera. Avant de créer une variable, relis les questions du vocabulaire : « agression » est une violence, « complicité de l'assuré » est un auteur, « vol simple » est un vol sans effraction ni violence ; une notion qui se dit avec des faits existants s'écrit avec eux, au besoin par un concept.
3. Traduis TOUT le texte : chaque élément d'une liste d'exclusions devient une exclusion. Ce que tu ne sais pas exprimer va dans "non_traduit" sous la forme {"article", "texte", "pourquoi"}. N'omets jamais rien en silence : une exclusion oubliée fait couvrir à tort.
3 bis. Une exclusion garde ses réserves et ses conditions : « à l'exception du mobilier de jardin » s'écrit {"et": [condition, {"non": réserve}]}, et « si l'Assuré n'occupe que partiellement le bâtiment » fait partie de la condition. Une réserve perdue fait refuser à tort.
4. Une condition cachée dans un tableau de limites (« si ces locaux sont fermés par… ») est une circonstance. Une limite n'a pas de condition : {"article", "texte", "montant"}. Un plafond qui ne vaut que dans un cas (« s'ils ne se trouvent pas sous clefs ») se cite tel quel ; n'invente pas de variable pour lui.
5. Un terme défini par le contrat (« tempête », « bâtiment ») s'emploie par {"concept": "nom"} : réutilise un concept existant, ou ajoute sa définition dans "definitions" sous la forme {"concept": "nom", "condition": …, "article", "texte"}. Tout concept employé doit exister ou être défini.
6. Si l'événement couvert est lui-même défini par le contrat (une définition de la tempête est fournie), cette définition est une condition de la garantie : mets {"concept": …} dans ses circonstances.
7. "evenements" : les valeurs de la variable evenement que cette garantie couvre (le moteur refusera de conclure pour un événement absent de toutes les règles).
8. Identifiants : minuscules, chiffres et « _ », préfixés par le thème (ex. tempete_batiment).

## Réponse : un objet JSON, rien d'autre
{"evenements": ["degat_eaux"],
 "definitions": [{"concept": "gel_prevenu", "condition": {"f": ["prevention_gel", "oui"]}, "article": "2.7", "texte": "maintenir une température positive dans tous les locaux"}],
 "garanties": [{"id": "degats_eaux", "nom": "Dégâts causés par l'eau", "article": "2.7", "texte": "Nous couvrons l'ensemble des dommages causés par l'eau",
   "perimetre": [{"f": ["evenement", "degat_eaux"]}, {"ou": [{"concept": "contenu"}, {"f": ["bien", "element_batiment"]}]}, {"concept": "batiment"}],
   "circonstances": [],
   "obligations": [],
   "exclusions": [{"condition": {"f": ["cause_eau", "inondation"]}, "portee": "tout", "a_demander": true, "article": "2.7-b", "texte": "par une inondation ou un débordement ou refoulement d'égouts publics"},
                  {"condition": {"f": ["bien", "canalisation"]}, "portee": {"bien": "canalisation"}, "a_demander": true, "article": "2.7-b", "texte": "aux canalisations, radiateurs, robinets, citernes, chaudières et autres appareils chauffant de l'eau, qui sont à l'origine du sinistre"}],
   "limites": [{"article": "2.7", "texte": "Dégâts causés par l'eau", "montant": "valeur à neuf"}]}],
 "exclusions_communes": [],
 "vocabulaire_manquant": [{"variable": "piscine", "valeurs": ["oui", "non"], "question": "L'eau venait-elle d'une piscine ?", "pourquoi": "exclusion de l'écoulement des piscines", "plus_proche": "cause_eau : aucune de ses valeurs ne dit d'où vient l'eau"}],
 "non_traduit": []}"""


class ErreurProposition(ValueError):
    """Une proposition dont la structure ne permet pas d'écrire des règles."""


# --- Le contexte donné au modèle ------------------------------------------------------------------------

def clauses_article(clauses: list[Clause], article: str) -> list[Clause]:
    """La clause de l'article et ses sous-sections (« 2.2 » → 2.2, 2.2-a…)."""
    return [c for c in clauses if c.id == article or c.groupe == article
            or c.id.startswith(article + "-") or c.id.startswith(article + "~")]


def definitions_utiles(clauses: list[Clause], textes: list[Clause]) -> list[Clause]:
    """Les définitions (art. 12) dont le terme apparaît dans le texte ou les titres de l'article."""
    corpus = normaliser(" ".join(" ".join(c.chemin) + " " + c.texte for c in textes))
    retenues = []
    for c in clauses:
        if c.type != TypeClause.DEFINITION:
            continue
        terme = normaliser((c.chemin[-1] if c.chemin else c.id.split("/")[-1]).replace("-", " "))
        if terme and re.search(rf"\b{re.escape(terme)}", corpus):
            retenues.append(c)
    return retenues


def concepts_existants(contrat_pl: str) -> dict[str, str]:
    """Les concepts définis par les règles du contrat, avec leur citation."""
    return {m.group(1): m.group(2) for m in re.finditer(
        r"^definition\((\w+),.*?'[^']*',\s*\"((?:[^\"\\]|\\.)*)\"\)\.", contrat_pl, re.M | re.S)}


def message_redaction(article: str, textes: list[Clause], definitions: list[Clause], contrat_pl: str) -> str:
    voc = prolog.vocabulaire()
    vocab = "\n".join(f"- {v}{' (plusieurs)' if d.get('plusieurs') else ''} : {', '.join(d['valeurs'])}"
                      f"{' — « ' + d['question'] + ' »' if d.get('question') else ''}" for v, d in voc.items())
    concepts = "\n".join(f"- {n} : « {t} »" for n, t in concepts_existants(contrat_pl).items()) or "(aucun)"
    bloc = "\n\n".join(f"### Clause {c.id} ({' > '.join(c.chemin)})\n{c.texte}" for c in textes)
    defs = "\n\n".join(f"### Clause {c.id}\n{c.texte}" for c in definitions) or "(aucune)"
    return (f"## Vocabulaire\n{vocab}\n\n## Concepts déjà définis dans les règles du contrat\n{concepts}\n\n"
            f"## Garantie à traduire : article {article}\n{bloc}\n\n## Définitions du contrat qui peuvent servir\n{defs}")


# --- JSON → Prolog -----------------------------------------------------------------------------------------

def atome(x) -> str:
    x = str(x)
    return x if IDENT.match(x) else "'" + x.replace("\\", "\\\\").replace("'", "\\'") + "'"


def chaine(s) -> str:
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
    if p in (None, "tout"):
        return "tout"
    if isinstance(p, dict) and set(p) == {"bien"}:
        return f"bien({atome(p['bien'])})"
    raise ErreurProposition(f"portée mal formée : {p}")


def oui_non(b) -> str:
    return "oui" if b else "non"


def en_prolog(prop: dict, article: str, entete: str = "") -> str:
    """Les règles d'une proposition, sans directive : elles s'ajoutent à la suite du fichier du contrat."""
    lignes = [f"% --- Art. {article} : proposition rédigée par le modèle{(' — ' + entete) if entete else ''} ---"]
    for e in prop.get("evenements", []):
        lignes.append(f"evenement_traduit({atome(e)}).")
    for d in prop.get("definitions", []):
        lignes.append(f"definition({atome(d['concept'])}, {terme(d['condition'])}, {atome(d['article'])},\n    {chaine(d['texte'])}).")
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
    if prop.get("exclusions_communes"):
        cibles = "[" + ", ".join(atome(g["id"]) for g in prop.get("garanties", [])) + "]"
        for x in prop["exclusions_communes"]:
            lignes.append(f"exclusion({cibles}, {terme(x['condition'])}, {portee(x.get('portee'))}, "
                          f"{oui_non(x.get('a_demander'))}, {atome(x['article'])},\n    {chaine(x['texte'])}).")
    return "\n".join(lignes) + "\n"


def exclusions(prop: dict) -> list[dict]:
    """Toutes les exclusions de la proposition : celles des garanties et celles communes à l'article."""
    return [x for g in prop.get("garanties", []) for x in g.get("exclusions", [])] + list(prop.get("exclusions_communes") or [])


def fusionner(contrat_pl: str, *propositions_pl: str) -> str:
    return contrat_pl.rstrip("\n") + "\n\n" + "\n".join(propositions_pl)


# --- Contrôles ------------------------------------------------------------------------------------------

CHAMPS = {
    "definitions": ("concept", "condition", "article", "texte"),
    "garanties": ("id", "nom", "article", "texte", "perimetre"),
    "circonstances": ("condition", "article", "texte"),
    "obligations": ("condition", "article", "texte"),
    "exclusions": ("condition", "article", "texte"),
    "limites": ("article", "texte"),
    "non_traduit": ("article", "texte", "pourquoi"),
}


def non_traduits(prop: dict) -> list[dict]:
    """Les passages déclarés non traduits. Le modèle renvoie parfois une simple phrase au lieu de l'objet
    {"article", "texte", "pourquoi"} (AXA 3.1.6, 7.53) : on la garde, sans article, plutôt que de planter."""
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
    champs(prop.get("non_traduit"), "non_traduit", "non_traduit")
    champs(prop.get("exclusions_communes"), "exclusions", "exclusions_communes")
    garanties = prop.get("garanties")
    if not garanties:
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
    """Les éléments d'une liste d'exclusions (puces « • » ou « - »), sans la phrase d'introduction."""
    morceaux = re.split(r"(?:^|\s)[•\-–]\s", texte)
    return [m.strip(" .;") for m in morceaux if len(_compact(m).split()) >= 3 and not m.strip().endswith(":")]


def couvert_par(item: str, textes: list[str]) -> bool:
    ci = _compact(item)
    return any((ct := _compact(t)) and (ct in ci or ci in ct) for t in textes)


def controler(prop: dict, clauses: list[Clause], contrat_pl: str, article: str) -> list[dict]:
    """Les problèmes d'une proposition. Répare en place les citations dont les mots sont dans l'ordre."""
    problemes: list[dict] = []

    def noter(gravite, controle, message):
        problemes.append({"gravite": gravite, "controle": controle, "message": message})

    # 1. Structure. Un « non_traduit » en simple phrase est mis en forme (sans article) : il reste bloquant
    # plus bas, et une seconde rédaction de plusieurs minutes pour une question de forme serait du gaspillage.
    if isinstance(prop, dict) and prop.get("non_traduit"):
        prop["non_traduit"] = non_traduits(prop)
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
            if v in voc and x in voc[v]["valeurs"]:
                continue
            if (v, x) in declares:
                noter(BLOQUANT, "vocabulaire", f"{v} = {x} : fait nouveau déclaré par le modèle, à accepter "
                      f"(`--accepter-vocabulaire {article}`) ou à remplacer")
            else:
                noter(BLOQUANT, "vocabulaire", f"{v} = {x} : hors vocabulaire, et non déclaré")
    for m in prop.get("vocabulaire_manquant", []):
        if m.get("variable") not in voc and not m.get("plus_proche"):
            noter(A_RELIRE, "vocabulaire", f"{m.get('variable')} : variable nouvelle sans « plus_proche » ; "
                  f"vérifier qu'un fait existant ne la dit pas déjà")
    for e in prop.get("evenements", []):
        if e not in voc["evenement"]["valeurs"] and ("evenement", e) not in declares:
            noter(BLOQUANT, "vocabulaire", f"evenement = {e} : hors vocabulaire, et non déclaré")

    # 3. Citations
    index = {c.id: c for c in clauses}
    for role, x in elements_cites(prop):
        art, texte = x.get("article"), x.get("texte", "")
        clause = index.get(art)
        if clause is None or not extrait_present(texte, clause.texte):
            # Le texte est peut-être exact, mais rattaché à la mauvaise clause (« 12 » pour « 12/sanitaires ») :
            # s'il figure dans une seule clause, on la rattache, comme la compilation des fiches le faisait.
            ailleurs = [c.id for c in clauses if texte and extrait_present(texte, c.texte)]
            prefixees = [i for i in ailleurs if art and (i.startswith(str(art) + "/") or i.startswith(str(art) + "-"))]
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

    # 3 ter. Les exclusions de l'article valent pour toutes ses garanties (AXA 3.1.6, 7.53 : les extensions
    # « Privilège » et « Active » couvraient un vol sans aucune exclusion). Une garantie sans exclusion, à côté
    # d'une liste d'exclusions de l'article non mise en commun, est bloquante.
    if any(c.type == TypeClause.EXCLUSION for c in clauses_article(clauses, article)) and not prop.get("exclusions_communes"):
        for g in prop.get("garanties", []):
            if not g.get("exclusions"):
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
    for c in clauses_article(clauses, article):
        if c.type != TypeClause.EXCLUSION:
            continue
        for item in items_exclusion(c.texte):
            if not couvert_par(item, textes):
                noter(BLOQUANT, "couverture", f"exclusion du contrat absente des règles ({c.id}) : « {item[:100]} »")
    for n in non_traduits(prop):
        noter(BLOQUANT, "couverture", f"déclaré non traduit ({n.get('article')}) : « {str(n.get('texte'))[:100]} » "
              f"— {n.get('pourquoi', '')}")

    # 4 bis. La définition de l'événement couvert (« tempête ») est une condition de la garantie.
    titres = normaliser(" ".join(c.chemin[-1] for c in clauses_article(clauses, article) if c.chemin))
    employes = {x.get("article") for _, x in elements_cites(prop)} | {n.get("article") for n in non_traduits(prop)}
    for d in definitions_utiles(clauses, clauses_article(clauses, article)):
        terme_defini = normaliser((d.chemin[-1] if d.chemin else d.id.split("/")[-1]).replace("-", " "))
        if terme_defini and re.search(rf"\b{re.escape(terme_defini)}", titres) and d.id not in employes:
            noter(BLOQUANT, "couverture", f"la définition {d.id} de l'événement couvert n'est pas traduite "
                  f"(elle restreint la garantie) : l'employer ou la déclarer non traduite")

    # 5. Concepts et identifiants
    existants = set(concepts_existants(contrat_pl))
    nouveaux = {d.get("concept") for d in prop.get("definitions", [])}
    for n in nouveaux & existants:
        noter(BLOQUANT, "concept", f"le concept {n} est déjà défini dans les règles du contrat")
    for c in conditions(prop):
        for n in concepts_employes(c):
            if n not in existants | nouveaux:
                noter(BLOQUANT, "concept", f"concept inconnu : {n}")
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


# --- Les commandes ------------------------------------------------------------------------------------------

def chemins(contrat_id: str, article: str, dossier: Path | None = None) -> tuple[Path, Path]:
    base = (dossier or PROPOSITIONS) / contrat_id
    return base / f"{article}.json", base / f"{article}.pl"


def rediger(contrat_id: str, article: str, clauses: list[Clause], llm, dossier: Path | None = None,
            cas: list[tuple[str, dict]] | None = None) -> dict:
    """Fait rédiger la proposition par le modèle, l'enregistre et la contrôle."""
    contrat_pl = prolog.fichier_regles(contrat_id).read_text(encoding="utf-8")
    textes = clauses_article(clauses, article)
    if not textes:
        raise LookupError(f"Aucune clause {article} dans le contrat {contrat_id}.")
    message = message_redaction(article, textes, definitions_utiles(clauses, textes), contrat_pl)
    llm_long = pour_compiler(llm, timeout=600)   # 300 s n'ont pas suffi pour 2.2 (7.22)
    prop = _appeler(llm_long, SYSTEME_REDACTION, message)
    meta = {"article": article, "modele": getattr(llm, "nom", "?"), "date": date.today().isoformat(),
            "consigne": "redaction-regles " + VERSION}
    sauver(contrat_id, article, {"meta": meta, "proposition": prop}, dossier)   # une rédaction coûte des minutes
    schema = erreurs_schema(prop)
    if schema:
        # Une seule reprise : on renvoie au modèle ses écarts au schéma, en clair.
        meta["premiere_reponse"] = {"proposition": prop, "ecarts": schema}
        message += ("\n\n## Ta réponse précédente ne respecte pas le schéma\n" + "\n".join(f"- {e}" for e in schema)
                    + "\nRenvoie l'objet JSON complet, corrigé.")
        try:
            prop = _appeler(llm_long, SYSTEME_REDACTION, message)
        except ValueError:
            pass
    return enregistrer(contrat_id, article, {"meta": meta, "proposition": prop}, clauses, contrat_pl, dossier, cas)


def sauver(contrat_id: str, article: str, doc: dict, dossier: Path | None = None) -> None:
    js, _ = chemins(contrat_id, article, dossier)
    js.parent.mkdir(parents=True, exist_ok=True)
    js.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def enregistrer(contrat_id: str, article: str, doc: dict, clauses: list[Clause], contrat_pl: str,
                dossier: Path | None = None, cas: list[tuple[str, dict]] | None = None) -> dict:
    """Contrôle, écrit le JSON et les règles. `cas` (faits idéaux annotés) : avec SWI-Prolog, vérifie le
    chargement et la non-régression ; None : ces contrôles ne sont pas faits."""
    prop = doc["proposition"]
    doc["controles"] = controler(prop, clauses, contrat_pl, article)
    _, pl = chemins(contrat_id, article, dossier)
    sauver(contrat_id, article, doc, dossier)
    if pl.exists():
        pl.unlink()                       # des règles d'une version précédente ne doivent pas traîner
    if not any(p["controle"] == "structure" for p in doc["controles"]):
        m = doc.get("meta", {})
        texte = en_prolog(prop, article, f"{m.get('modele', '?')}, {m.get('date', '')}")
        pl.write_text(texte, encoding="utf-8")
        # Prolog s'arrête sur un concept inconnu : inutile de le lancer tant que les concepts bloquent.
        if cas is not None and not any(p["controle"] == "concept" and p["gravite"] == BLOQUANT for p in doc["controles"]):
            doc["controles"] += controler_avec_prolog(contrat_id, contrat_pl, texte, cas)
    sauver(contrat_id, article, doc, dossier)
    return doc


def recontroler(contrat_id: str, article: str, clauses: list[Clause], dossier: Path | None = None,
                cas: list[tuple[str, dict]] | None = None) -> dict:
    """Relit la proposition enregistrée (éventuellement corrigée à la main) et refait les contrôles."""
    js, _ = chemins(contrat_id, article, dossier)
    doc = json.loads(js.read_text(encoding="utf-8"))
    contrat_pl = prolog.fichier_regles(contrat_id).read_text(encoding="utf-8")
    return enregistrer(contrat_id, article, doc, clauses, contrat_pl, dossier, cas)


def articles_proposes(contrat_id: str, dossier: Path | None = None) -> list[str]:
    base = (dossier or PROPOSITIONS) / contrat_id
    return sorted(p.stem for p in base.glob("*.json")) if base.exists() else []


def accepter_vocabulaire(prop: dict, chemin: Path | None = None) -> list[str]:
    """Ajoute au vocabulaire commun les faits déclarés par le modèle. Décision humaine : c'est la commande
    qu'on lance après avoir lu les questions proposées."""
    chemin = chemin or prolog.DOSSIER / "vocabulaire.json"
    doc = json.loads(chemin.read_text(encoding="utf-8"))
    voc, ajouts = doc["variables"], []
    for m in prop.get("vocabulaire_manquant", []):
        v, valeurs = m.get("variable"), [str(x) for x in m.get("valeurs", [])]
        if not (v and IDENT.match(v) and valeurs and all(IDENT.match(x) for x in valeurs)):
            continue
        if v in voc:
            nouvelles = [x for x in valeurs if x not in voc[v]["valeurs"]]
            voc[v]["valeurs"] += nouvelles
            ajouts += [f"{v} = {x}" for x in nouvelles]
        else:
            voc[v] = {"valeurs": valeurs, "question": m.get("question") or f"Préciser : {v}"}
            ajouts.append(f"{v} ({', '.join(valeurs)}) : « {voc[v]['question']} »")
    if ajouts:
        chemin.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ajouts


def accepter(contrat_id: str, article: str, dossier: Path | None = None) -> Path:
    """Ajoute la proposition aux règles du contrat, si aucun contrôle ne bloque."""
    js, pl = chemins(contrat_id, article, dossier)
    doc = json.loads(js.read_text(encoding="utf-8"))
    bloquants = [p for p in doc.get("controles", []) if p["gravite"] == BLOQUANT]
    if bloquants:
        raise ErreurProposition(f"{len(bloquants)} contrôle(s) bloquant(s) : relancer `--controler` après correction")
    cible = prolog.fichier_regles(contrat_id)
    cible.write_text(fusionner(cible.read_text(encoding="utf-8"), pl.read_text(encoding="utf-8")), encoding="utf-8")
    return cible


def resumer(doc: dict) -> str:
    prop, ctl = doc["proposition"], doc.get("controles", [])
    g = prop.get("garanties", [])
    n = lambda cle: sum(len(x.get(cle, [])) for x in g) + (len(prop.get("exclusions_communes") or [])  # noqa: E731
                                                           if cle == "exclusions" else 0)
    lignes = [f"Art. {doc.get('meta', {}).get('article', '?')} : {len(g)} garantie(s) "
              f"({', '.join(x.get('id', '?') for x in g)}), {n('exclusions')} exclusion(s), "
              f"{n('circonstances')} circonstance(s), {n('obligations')} obligation(s), {n('limites')} limite(s) ; "
              f"événements : {', '.join(prop.get('evenements', [])) or 'aucun'}"]
    for m in prop.get("vocabulaire_manquant", []):
        lignes.append(f"  + vocabulaire proposé : {m.get('variable')} = {', '.join(map(str, m.get('valeurs', [])))} "
                      f"— « {m.get('question', '')} » ({m.get('pourquoi', '')})")
    for gravite in (BLOQUANT, A_RELIRE, INFO):
        for p in ctl:
            if p["gravite"] == gravite:
                lignes.append(f"  {'!' if gravite == BLOQUANT else '?' if gravite == A_RELIRE else '·'} "
                              f"[{p['controle']}] {p['message']}")
    nb = sum(p["gravite"] == BLOQUANT for p in ctl)
    lignes.append("  → aucun contrôle bloquant : `--accepter` possible après relecture" if not nb
                  else f"  → {nb} contrôle(s) bloquant(s)")
    return "\n".join(lignes)
