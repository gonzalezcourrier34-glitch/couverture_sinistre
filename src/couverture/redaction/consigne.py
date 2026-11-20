"""La consigne de rédaction, et le contexte donné au modèle : l'article, ses définitions, les concepts existants."""

from __future__ import annotations

import re

from .. import prolog
from ..models import Clause, TypeClause
from ..texte import normaliser


PROPOSITIONS = prolog.DOSSIER / "propositions"
VERSION = "v12"
IDENT = re.compile(r"^[a-z][a-z0-9_]*$")

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
Un article d'exclusions générales (« ce que nous ne garantissons jamais », valable pour tout le contrat) n'a pas de garantie : laisse "garanties" vide et mets ses exclusions dans "exclusions_communes" ; elles viseront toutes les garanties du contrat.
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
