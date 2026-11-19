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
VERSION = "v11"
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
Une sanction qui RÉDUIT l'indemnité (« l'indemnité sera réduite de moitié », « réduite à concurrence de l'aggravation », « proportionnellement ») ne refuse pas le sinistre : ce n'est pas une obligation, c'est une limite (le devoir et sa réduction, cités dans "texte"). N'écris une obligation que si le contrat refuse (« pas de garantie », « refuser son intervention », « exclu »).
Une garantie qui ne joue qu'après un sinistre couvert par une autre (frais de sauvetage, de déblai, de logement provisoire, pertes indirectes) porte "accessoire": true : elle ne décide pas si le sinistre est couvert, elle dit ce qui s'y ajoute. Ne mets pas dans son périmètre tous les événements du contrat, ni un concept « sinistre » : « après un sinistre couvert » est implicite. Son périmètre ne dit que ce qui la restreint (une fête de famille, un déménagement) ; s'il n'y a rien, laisse-le vide ([]).
Une extension qui élargit un LIEU ou un BIEN assuré (« le contenu lors d'un séjour temporaire », « pendant son transport lors d'un déménagement ») n'est pas une garantie : elle élargit la définition du contrat que les garanties emploient déjà : prends son nom dans « Concepts déjà définis dans les règles du contrat » (le lieu assuré, le contenu), jamais un nom d'un autre contrat. Mets-la dans "extensions" : {"concept": "<un concept du contrat>", "condition": …, "article", "texte"} ; elle vaut alors pour toutes les garanties du contrat.
Des dégâts causés PAR un assuré au bien d'un autre (l'hôtel, la chambre louée, la salle de fête) relèvent de sa responsabilité, pas d'une extension : une garantie accessoire tant que la responsabilité civile n'est pas traduite. Une restriction à un pays s'écrit avec une variable pays, une valeur par pays (jamais une valeur « liste de pays »).
Les exclusions d'un article (« vols exclus ») valent pour TOUTES ses garanties, extensions comprises : mets-les dans "exclusions_communes", pas dans une seule garantie. N'attache à une garantie que les exclusions qui ne valent que pour elle.
Une condition est un terme JSON : {"f": ["variable", "valeur"]}, {"et": [c1, c2]}, {"ou": [c1, c2]}, {"non": c}, {"si": [a, b]} (si a alors b), {"concept": "nom"} (une définition).
La logique a trois valeurs : un fait que la déclaration ne donne pas est « inconnu », et le moteur pose alors la question. N'essaie pas de compenser un fait inconnu.

## Règles d'écriture
1. Chaque garantie, définition, circonstance, obligation, exclusion et limite porte "article" (l'identifiant de clause fourni) et "texte" : une phrase COPIÉE MOT POUR MOT de cette clause. Pas de reformulation, pas de coupure, pas de « … ».
2. N'emploie que les variables et les valeurs du vocabulaire. Si le texte exige un fait que le vocabulaire n'a pas, n'approxime pas avec un fait voisin : emploie une variable ou une valeur nouvelle ET déclare-la dans "vocabulaire_manquant" (variable, valeurs, question à poser à l'assuré, pourquoi, "plus_proche" : la variable existante la plus proche et pourquoi elle ne suffit pas, "aide" : pour chaque valeur, ce qu'un assuré dirait dans sa déclaration pour qu'on la retienne ; pour une valeur nouvelle d'une variable existante, "parent" : la valeur existante qui la contient, ex. un ordinateur est de l'« electronique »). Un humain décidera. Avant de créer une variable, relis les questions du vocabulaire : « agression » est une violence, « complicité de l'assuré » est un auteur, « vol simple » est un vol sans effraction ni violence ; une notion qui se dit avec des faits existants s'écrit avec eux, au besoin par un concept.
3. Traduis TOUT le texte : chaque élément d'une liste d'exclusions devient une exclusion. Ce que tu ne sais pas exprimer va dans "non_traduit" sous la forme {"article", "texte", "pourquoi"}. N'omets jamais rien en silence : une exclusion oubliée fait couvrir à tort.
3 bis. Une exclusion garde ses réserves et ses conditions : « à l'exception du mobilier de jardin » s'écrit {"et": [condition, {"non": réserve}]}, et « si l'Assuré n'occupe que partiellement le bâtiment » fait partie de la condition. Une réserve perdue fait refuser à tort.
3 ter. « À moins que l'Assuré ne démontre… » est une réserve de l'exclusion : {"et": [condition, {"non": preuve}]}, avec "a_demander": true. Le moteur pose la question dès que la déclaration établit la condition (les travaux), et ne la pose pas sinon.
3 quater. « À l'extérieur » d'un bâtiment, dans une liste d'exclusions, désigne ce qui est à l'adresse du risque hors des locaux (cours, jardins, couloirs) : pas la voie publique ni un autre bâtiment, que d'autres garanties couvrent.
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
   "circonstances": [{"condition": {"f": ["plainte_deposee", "oui"]}, "article": "2.7", "texte": "pour autant qu'une plainte ait été déposée"}],
   "obligations": [],
   "exclusions": [{"condition": {"f": ["cause_eau", "inondation"]}, "portee": "tout", "a_demander": true, "article": "2.7-b", "texte": "par une inondation ou un débordement ou refoulement d'égouts publics"},
                  {"condition": {"f": ["bien", "canalisation"]}, "portee": {"bien": "canalisation"}, "a_demander": true, "article": "2.7-b", "texte": "aux canalisations, radiateurs, robinets, citernes, chaudières et autres appareils chauffant de l'eau, qui sont à l'origine du sinistre"}],
   "limites": [{"article": "2.7", "texte": "Dégâts causés par l'eau", "montant": "valeur à neuf"}]}],
 "exclusions_communes": [],
 "extensions": [],
 "vocabulaire_manquant": [{"variable": "piscine", "valeurs": ["oui", "non"], "question": "L'eau venait-elle d'une piscine ?", "pourquoi": "exclusion de l'écoulement des piscines", "plus_proche": "cause_eau : aucune de ses valeurs ne dit d'où vient l'eau", "aide": {"oui": "l'eau venait de la piscine, du bassin", "non": "l'eau venait d'ailleurs"}}],
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
        voc = json.loads((prolog.DOSSIER / "vocabulaire.json").read_text(encoding="utf-8"))["variables"]
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
            f"({', '.join(sorted(set(hors_si(o.get('condition'))) & set(prolog.SOCLE)))}) au lieu d'un devoir : "
            f"l'écrire « si situation, alors devoir », ou en faire une exclusion"
            for g in prop.get("garanties") or [] if isinstance(g, dict)
            for o in g.get("obligations") or [] if isinstance(o, dict)
            and set(hors_si(o.get("condition"))) & set(prolog.SOCLE)]


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
    if not garanties and not prop.get("extensions"):
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


def controler(prop: dict, clauses: list[Clause], contrat_pl: str, article: str) -> list[dict]:
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
            if v in voc and x in voc[v]["valeurs"]:
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
    for g in prop.get("garanties", []):
        for o in g.get("obligations") or []:
            c = index.get(o.get("article"))
            t, d = (normaliser(c.texte), normaliser(str(o.get("texte", "")))) if c is not None else ("", "")
            i = t.find(d[:60]) if d else -1
            fenetre = t[i:i + len(d) + 400] if i >= 0 else ""
            if c is None or not fenetre:
                continue
            if re.search(r"\br[ée]dui|proportionnel", fenetre) \
                    and not re.search(r"refuser|pas de garantie|n.?est pas garanti", fenetre):
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
    # Un concept déjà défini dans les règles du contrat, et employé par la proposition, compte aussi (7.63) :
    # `concept(vol)` renvoie à la définition 12/vol acceptée avec la garantie vol.
    employes_c = {n for c in conditions(prop) for n in re.findall(r'"concept":\s*"([a-z0-9_]+)"', json.dumps(c))}
    employes |= {a for n, a in re.findall(r"^definition\(\s*([a-z0-9_]+)\s*,.*?,\s*'([^']+)'", contrat_pl or "", re.M | re.S)
                 if n in employes_c}
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
    for x in prop.get("extensions") or []:
        if x.get("concept") not in existants | nouveaux:
            # Le nom vient de ce contrat, pas d'un autre : l'assureur B appelle son lieu assuré
            # `batiment_designe`, le modèle écrivait `batiment` comme pour A (7.72).
            noter(BLOQUANT, "concept", f"extension d'un concept inconnu : {x.get('concept')} (concepts de ce contrat : "
                  f"{', '.join(sorted(existants | nouveaux)) or 'aucun'})")
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
    contrat_pl = retirer_article(prolog.fichier_regles(contrat_id).read_text(encoding="utf-8"), article)
    textes = clauses_article(clauses, article)
    if not textes:
        raise LookupError(f"Aucune clause {article} dans le contrat {contrat_id}.")
    message = message_redaction(article, textes, definitions_utiles(clauses, textes), contrat_pl)
    llm_long = pour_compiler(llm, timeout=600)   # 300 s n'ont pas suffi pour 2.2 (7.22)
    prop = _appeler(llm_long, SYSTEME_REDACTION, message)
    meta = {"article": article, "modele": getattr(llm, "nom", "?"), "date": date.today().isoformat(),
            "consigne": "redaction-regles " + VERSION}
    sauver(contrat_id, article, {"meta": meta, "proposition": prop}, dossier)   # une rédaction coûte des minutes
    if isinstance(prop, dict):
        # Ce que le code sait remettre en forme ne vaut pas une reprise de plus de dix minutes (7.54).
        envelopper_conditions_nues(prop)
        prop["non_traduit"] = non_traduits(prop)
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
    contrat_pl = retirer_article(prolog.fichier_regles(contrat_id).read_text(encoding="utf-8"), article)
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
        for v, val in feuilles_x:
            if v in prolog.SOCLE:
                declencheurs.setdefault(v, [])
                if val not in declencheurs[v]:
                    declencheurs[v].append(val)
        for v, _ in feuilles_x:
            if v in prolog.SOCLE or v not in voc:
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
        chemin.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ajouts


ACCESSOIRE = "accessoire"      # « pour » d'une variable que seules des garanties accessoires emploient : pas lue
EXTENSION = "extension"        # « pour » d'une variable née d'une extension : lue seulement si son lieu est lu
# Ces deux « pour » ne sont pas des événements : ajoutés à une variable déjà lue pour un vol, ils n'y changent
# rien et brouillent le vocabulaire (« option_incendie : lue aussi pour accessoire », 7.73).
PSEUDO_EVENEMENTS = (ACCESSOIRE, EXTENSION)


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
        return [] if str(v[0]) in prolog.SOCLE else [(str(v[0]), list(evs), lieux)]
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
        if not d or not d.get("pour") or not evenements:
            continue
        manquants = [e for e in evenements if e not in d["pour"] and e not in PSEUDO_EVENEMENTS]
        if manquants:
            d["pour"] = d["pour"] + manquants
            ajouts.append(f"{v} : lue aussi pour {', '.join(manquants)}")
    return ajouts


def accepter(contrat_id: str, article: str, dossier: Path | None = None) -> Path:
    """Ajoute la proposition aux règles du contrat, si aucun contrôle ne bloque."""
    js, pl = chemins(contrat_id, article, dossier)
    doc = json.loads(js.read_text(encoding="utf-8"))
    bloquants = [p for p in doc.get("controles", []) if p["gravite"] == BLOQUANT]
    if bloquants:
        raise ErreurProposition(f"{len(bloquants)} contrôle(s) bloquant(s) : relancer `--controler` après correction")
    cible = prolog.fichier_regles(contrat_id)
    cible.write_text(fusionner(retirer_article(cible.read_text(encoding="utf-8"), article), pl.read_text(encoding="utf-8")),
                     encoding="utf-8")
    return cible


def retirer_article(contrat_pl: str, article: str) -> str:
    """Les règles du contrat sans le bloc d'une proposition déjà acceptée pour cet article : une proposition
    corrigée puis acceptée de nouveau remplace l'ancienne au lieu de s'y ajouter (7.58)."""
    entete = re.compile(rf"^% --- Art\. {re.escape(article)} : proposition.*$", re.M)
    m = entete.search(contrat_pl)
    if not m:
        return contrat_pl
    suite = re.compile(r"^% --- Art\. ", re.M).search(contrat_pl, m.end())
    return (contrat_pl[:m.start()].rstrip("\n") + "\n" + (contrat_pl[suite.start():] if suite else "")).rstrip("\n") + "\n"


def resumer(doc: dict) -> str:
    prop, ctl = doc["proposition"], doc.get("controles", [])
    g = prop.get("garanties", [])
    n = lambda cle: sum(len(x.get(cle, [])) for x in g) + (len(prop.get("exclusions_communes") or [])  # noqa: E731
                                                           if cle == "exclusions" else 0)
    lignes = [f"Art. {doc.get('meta', {}).get('article', '?')} : {len(g)} garantie(s) "
              f"({', '.join(x.get('id', '?') for x in g)}), {n('exclusions')} exclusion(s), "
              f"{n('circonstances')} circonstance(s), {n('obligations')} obligation(s), {n('limites')} limite(s)"
              + (f", {len(prop['extensions'])} extension(s) ({', '.join(sorted({x.get('concept', '?') for x in prop['extensions']}))})"
                 if prop.get("extensions") else "") + " ; "
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
