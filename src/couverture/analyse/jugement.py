"""Les jugements clause par clause, la jointure et la décision (DEMARCHE 7.188, 7.189).

Le modèle ne décide pas du sinistre : il lit une clause à la fois et dit son effet sur la déclaration. Le reste est
du code.

- Un **jugement** : pour une clause, `couvre` (elle garantit ce sinistre), `exclut` (elle le refuse : une exclusion
  qui joue, une condition non remplie), `sans_effet` (elle ne le concerne pas, ou la déclaration l'écarte),
  `a_verifier` (la déclaration évoque la situation sans dire le fait qui tranche : une question). Avec la phrase
  du contrat et, pour `couvre` et `exclut`, la phrase de la déclaration qui le fonde.
- Les **contrôles** : la clause est au dossier ; la phrase du contrat s'y trouve mot pour mot ; la phrase de la
  déclaration aussi ; une question accompagne ce qui reste à vérifier. Un jugement qui échoue est écarté, donc
  manquant.
- La **jointure** : les clauses attendues des garanties désignées (`analyse/attendu.py`) face aux jugements
  rendus. Trois issues, comme dans l'article dont la méthode s'inspire : jugée ; attendue sans jugement ; jugée
  sans être attendue. C'est une requête SQL, pas un appel au modèle.
- La **décision**, une logique fixe : voir `decider`.
- La **contresignature** : `arbitrer` rapproche cette décision de celle de la chaîne de règles.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field

from ..models import Clause, Decision
from ..texte import normaliser
from . import attendu
from .validation import extrait_present

EFFETS = ("couvre", "exclut", "sans_effet", "a_verifier")
PORTEES = ("garantie", "tout")
# Les rôles d'une clause lue pour une garantie qui n'est pas la sienne.
EMPRUNTS = ("renvoi", "chapeau", "exclusion_generale", "definition")


@dataclass
class Jugement:
    """L'effet d'une clause sur une déclaration, tel que le modèle le rend."""

    clause_id: str
    effet: str
    extrait_contrat: str = ""
    extrait_declaration: str = ""
    question: str = ""
    motif: str = ""
    # Ce qu'un refus ou un doute atteint : la seule garantie de la clause, ou tout le contrat (un bien que le
    # contrat n'assure pas, une obligation générale). Une exclusion générale atteint toujours tout.
    portee: str = "garantie"


@dataclass
class Ligne:
    """Une ligne de la jointure : une clause attendue et son jugement, s'il existe."""

    garantie: str
    clause_id: str
    role: str
    bloque: bool
    jugement: Jugement | None


@dataclass
class Etat:
    """L'état d'un sinistre : la décision et ce qui la fonde, chaque entrée liée à sa clause."""

    decision: Decision
    couvrent: list[Jugement] = field(default_factory=list)
    excluent: list[Jugement] = field(default_factory=list)
    a_verifier: list[Jugement] = field(default_factory=list)
    garanties: dict[str, str] = field(default_factory=dict)     # repère → couvre, exclue, a_verifier, hors_jeu
    questions: list[str] = field(default_factory=list)
    manquants: list[str] = field(default_factory=list)          # clauses attendues restées sans jugement
    non_attendus: list[str] = field(default_factory=list)       # jugements sur une clause hors du dossier attendu
    defauts: list[str] = field(default_factory=list)            # jugements écartés par les contrôles, et pourquoi
    motif: str = ""


def depuis_reponse(reponse: dict) -> list[Jugement]:
    """Les jugements d'une réponse du modèle ; un élément mal formé (effet inconnu, pas de clause) est ignoré : la
    clause restera sans jugement, ce que la jointure dira."""
    jugements = []
    for j in reponse.get("jugements") or []:
        if not isinstance(j, dict) or j.get("effet") not in EFFETS or not j.get("clause"):
            continue
        jugements.append(Jugement(str(j["clause"]), j["effet"], str(j.get("extrait_contrat") or ""),
                                  str(j.get("extrait_declaration") or ""), str(j.get("question") or ""),
                                  str(j.get("motif") or ""), j.get("portee") if j.get("portee") in PORTEES else "garantie"))
    return jugements


def controler(jugements: list[Jugement], clauses: list[Clause], declaration: str) -> tuple[list[Jugement], list[str]]:
    """Garde les jugements vérifiables, écarte les autres en disant pourquoi. Un jugement `sans_effet` n'a rien à
    prouver ; les trois autres citent le contrat, et `couvre` ou `exclut` citent aussi la déclaration."""
    par_id = {c.id: c for c in clauses}
    declaration_n = normaliser(declaration)
    gardes, defauts, vus = [], [], set()
    for j in jugements:
        c = par_id.get(j.clause_id)
        if c is None:
            defauts.append(f"{j.clause_id} : clause hors du dossier")
        elif j.clause_id in vus:
            defauts.append(f"{j.clause_id} : jugée deux fois, le second jugement est ignoré")
        elif j.effet != "sans_effet" and not (j.extrait_contrat.strip() and extrait_present(j.extrait_contrat, c.texte)):
            defauts.append(f"{j.clause_id} : la phrase citée n'est pas dans la clause")
        elif j.effet in ("couvre", "exclut") and not (
                j.extrait_declaration.strip() and normaliser(j.extrait_declaration) in declaration_n):
            defauts.append(f"{j.clause_id} : la phrase citée n'est pas dans la déclaration")
        elif j.effet == "a_verifier" and not j.question.strip():
            defauts.append(f"{j.clause_id} : à vérifier, sans question")
        else:
            vus.add(j.clause_id)
            gardes.append(j)
    return gardes, defauts


def joindre(base, contrat_id: str, designees: list[str], jugements: list[Jugement]) -> tuple[list[Ligne], list[str]]:
    """La jointure de complétude : pour les garanties désignées, chaque clause attendue avec son jugement, ou sans.
    Rend aussi les clauses jugées qui n'étaient attendues pour aucune de ces garanties (signalées, pas jetées)."""
    par_id = {j.clause_id: j for j in jugements}
    with sqlite3.connect(base.chemin) as cx:
        cx.executescript(attendu.SCHEMA)
        cx.execute("CREATE TEMP TABLE juges (clause_id TEXT PRIMARY KEY)")
        cx.executemany("INSERT INTO juges VALUES (?)", [(i,) for i in par_id])
        cx.execute("CREATE TEMP TABLE designees (repere TEXT PRIMARY KEY)")
        cx.executemany("INSERT OR IGNORE INTO designees VALUES (?)", [(r,) for r in designees])
        lignes = cx.execute(
            "SELECT a.garantie, a.clause_id, a.role, a.bloque, j.clause_id FROM clauses_attendues a "
            "JOIN designees d ON d.repere = a.garantie LEFT JOIN juges j ON j.clause_id = a.clause_id "
            "WHERE a.contrat_id = ? ORDER BY a.rowid", (contrat_id,)).fetchall()
        non_attendus = [l[0] for l in cx.execute(
            "SELECT j.clause_id FROM juges j WHERE j.clause_id NOT IN (SELECT a.clause_id FROM clauses_attendues a "
            "JOIN designees d ON d.repere = a.garantie WHERE a.contrat_id = ?) ORDER BY j.clause_id", (contrat_id,))]
    return ([Ligne(g, c, role, bool(bloque), par_id.get(c) if juge else None) for g, c, role, bloque, juge in lignes],
            non_attendus)


def decider(lignes: list[Ligne], optionnelles: set[str] = frozenset(), non_attendus: list[str] = (),
            defauts: list[str] = (), chemins: dict[str, tuple[str, ...]] | None = None) -> Etat:
    """La décision, d'après la jointure. Une logique fixe :

    1. une clause attendue qui bloque et n'a pas de jugement : pas de réponse franche (à préciser, et on le dit) ;
    2. un refus qui atteint tout le contrat (exclusion générale, bien non assuré) : non couvert ;
    3. sinon, garantie par garantie : exclue si une de ses clauses exclut ; elle couvre si une clause couvre et que
       rien n'y reste à vérifier ; à vérifier s'il reste une question ; hors jeu si rien ne la concerne ;
    4. couvert si une garantie couvre, qu'elle n'est pas une option, et que rien d'atteignant tout le contrat ne
       reste à vérifier ; à préciser si une garantie reste à vérifier, ou si seule une option couvre ; non couvert
       si aucune garantie ne couvre ni ne reste à vérifier ;
    5. un refus prononcé ailleurs que dans une garantie voisine de celle qui couvre interdit le « couvert » franc.
       Deux garanties voisines (rangées sous le même titre : le bris de vitrages et le matériel multimédia) se
       font concurrence, et le refus de l'une laisse l'autre couvrir. Un refus venu d'un autre endroit du contrat
       (les biens assurés, une option, les obligations) peut valoir pour tout : le modèle a pu mal en dire la
       portée, on ne promet pas. `chemins` : le chemin de chaque garantie dans le contrat (sans lui, pas de 5)."""
    etat = Etat(Decision.INCERTAIN, non_attendus=list(non_attendus), defauts=list(defauts))
    vus: set[str] = set()

    def une_fois(js):
        return [j for j in js if not (j.clause_id in vus or vus.add(j.clause_id))]

    juges = [l for l in lignes if l.jugement is not None]
    for l in juges:                                    # une exclusion générale atteint toujours tout le contrat
        if l.role == "exclusion_generale":
            l.jugement.portee = "tout"
    etat.manquants = sorted({l.clause_id for l in lignes if l.bloque and l.jugement is None})
    globaux = {l.clause_id: l.jugement for l in juges if l.jugement.portee == "tout"}
    refus = [j for j in globaux.values() if j.effet == "exclut"]
    doutes = [j for j in globaux.values() if j.effet == "a_verifier"]
    # Une clause ne « couvre » que dans sa propre garantie : citée ailleurs comme renvoi ou comme chapeau, elle y
    # apporterait sa couverture sans ses exclusions. Un refus ou un doute, lui, compte partout où la clause est lue.
    par_garantie: dict[str, set[str]] = {}
    for l in lignes:
        par_garantie.setdefault(l.garantie, set())
        if l.jugement is not None and not (l.jugement.effet == "couvre" and l.role in EMPRUNTS):
            par_garantie[l.garantie].add(l.jugement.effet)
    for g, effets in par_garantie.items():
        if "exclut" in effets:
            etat.garanties[g] = "exclue"
        elif "couvre" in effets:
            etat.garanties[g] = "a_verifier" if "a_verifier" in effets else "couvre"
        else:
            etat.garanties[g] = "a_verifier" if "a_verifier" in effets else "hors_jeu"
    etat.excluent = une_fois([l.jugement for l in juges if l.jugement.effet == "exclut"])
    vus.clear()
    etat.couvrent = une_fois([l.jugement for l in juges if l.jugement.effet == "couvre" and l.role not in EMPRUNTS
                              and etat.garanties[l.garantie] in ("couvre", "a_verifier")])
    vus.clear()
    etat.a_verifier = une_fois(doutes + [l.jugement for l in juges if l.jugement.effet == "a_verifier"
                                         and etat.garanties[l.garantie] == "a_verifier"])
    couvrent = [g for g, s in etat.garanties.items() if s == "couvre"]
    franches = [g for g in couvrent if g not in optionnelles]
    en_suspens = [g for g, s in etat.garanties.items() if s == "a_verifier"]
    exclues = [g for g, s in etat.garanties.items() if s == "exclue"]
    ailleurs = [e for e in exclues if chemins and not any(
        chemins.get(e, ())[:-1] == chemins.get(g, (None,))[:-1] for g in franches)]
    if refus:
        etat.decision, etat.motif = Decision.NON_COUVERT, "une clause qui vaut pour tout le contrat exclut ce sinistre"
        etat.a_verifier = []
    elif franches and ailleurs and not etat.manquants:
        etat.motif = ("une garantie couvre, mais une clause d'une autre partie du contrat exclut : sa portée est à "
                      "examiner")
    elif etat.manquants:
        etat.motif = "des clauses attendues n'ont pas été jugées : pas de réponse franche"
    elif franches and not doutes:
        etat.decision, etat.motif = Decision.COUVERT, "une garantie couvre, aucune clause examinée n'exclut"
        etat.a_verifier = []
    elif franches or en_suspens:
        etat.motif = "un point reste à vérifier"
    elif couvrent:
        etat.motif = "seule une garantie optionnelle couvre : on ne sait pas si elle est souscrite"
        etat.questions.append("Vos conditions particulières mentionnent-elles cette garantie optionnelle ?")
    else:
        etat.decision, etat.motif = Decision.NON_COUVERT, "aucune garantie examinée ne couvre ce sinistre"
        etat.a_verifier = []
    etat.questions += [j.question for j in etat.a_verifier if j.question and j.question not in etat.questions]
    return etat


def arbitrer(etat: Etat, regles: Decision | None) -> tuple[Decision, str]:
    """La contresignature. « Couvert » n'est rendu que si la chaîne de règles le dit aussi ; un refus ou un doute
    fondé sur une clause citée tient seul. Rend la décision finale et, s'il y a lieu, le désaccord à afficher.
    `regles` : la décision de la chaîne de règles, ou rien si elle n'a pas répondu."""
    if etat.decision == Decision.COUVERT and regles is not None and regles != Decision.COUVERT:
        return Decision.INCERTAIN, ("la lecture des clauses conclut « couvert », les règles traduites répondent "
                                    f"« {regles.value} » : à examiner")
    if regles is not None and regles != etat.decision:
        return etat.decision, (f"les règles traduites répondaient « {regles.value} » ; la lecture des clauses "
                               "l'emporte, avec la clause citée")
    return etat.decision, ""
