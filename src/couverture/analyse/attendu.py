"""Les clauses attendues par garantie (DEMARCHE 7.189) : ce qui doit être examiné, écrit avant tout sinistre.

On ne constate un manque que si l'on a écrit d'avance ce qui devait être là. Pour chaque garantie d'un contrat,
cette table dit quelles clauses un gestionnaire doit relire avant de répondre : la garantie, ses exclusions, ses
conditions, ses limites, les chapeaux au-dessus d'elle, les exclusions générales du contrat, les articles auxquels
elle renvoie, les définitions du lexique qu'elle emploie. Chaque ligne porte son rôle, et dit si la clause peut
bloquer la couverture (une limite d'indemnité ou une définition ne refusent rien par elles-mêmes).

Tables, dans la base du projet :
  garanties(contrat_id, repere, titre, chemin, optionnelle, mots, porte_garantie)
  clauses_attendues(contrat_id, garantie, clause_id, role, bloque)

Elles se calculent du seul découpage, sans modèle, une fois par contrat (`enregistrer`), et se relisent par des
requêtes : la complétude d'une analyse est une jointure entre ces lignes et les jugements rendus.
"""

from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass

from ..models import Clause, TypeClause
from ..texte import normaliser
from . import dossier

SCHEMA = """
CREATE TABLE IF NOT EXISTS garanties (
    contrat_id TEXT, repere TEXT, titre TEXT, chemin TEXT, optionnelle INTEGER, mots INTEGER, porte_garantie INTEGER,
    PRIMARY KEY (contrat_id, repere)
);
CREATE TABLE IF NOT EXISTS clauses_attendues (
    contrat_id TEXT, garantie TEXT, clause_id TEXT, role TEXT, bloque INTEGER,
    PRIMARY KEY (contrat_id, garantie, clause_id)
);
"""

# Le rôle d'une clause de la garantie, d'après le type que le découpage lui a donné.
ROLE_DU_TYPE = {TypeClause.GARANTIE: "garantie", TypeClause.EXCLUSION: "exclusion", TypeClause.CONDITION: "condition",
                TypeClause.LIMITE: "limite", TypeClause.DEFINITION: "definition", TypeClause.AUTRE: "autre"}
# Ce qui ne refuse rien par soi-même : on le lit, on ne lui demande pas de jugement. Une « limite » en demande un :
# le découpage classe ainsi des clauses qui excluent (un plafond « seulement si la formule… »).
SANS_JUGEMENT = {"definition"}
OPTION = re.compile(r"\boption|\bpacks?\b")


@dataclass(frozen=True)
class Garantie:
    """Une garantie du contrat : le chapitre qui la porte, en entier."""

    repere: str
    titre: str
    chemin: tuple[str, ...]
    optionnelle: bool
    mots: int
    porte_garantie: bool = True


@dataclass(frozen=True)
class Attendue:
    """Une clause à examiner pour une garantie."""

    garantie: str
    clause_id: str
    role: str
    bloque: bool


def est_optionnelle(chemin: tuple[str, ...]) -> bool:
    """Une garantie rangée sous un titre d'option ou de pack : on ne sait pas si elle est souscrite."""
    return any(OPTION.search(normaliser(t)) for t in chemin)


def calculer(clauses: list[Clause]) -> tuple[list[Garantie], list[Attendue]]:
    """Les garanties d'un contrat et, pour chacune, ses clauses attendues.

    Une « garantie » est ici un chapitre qui se lit d'un bloc : le plus grand chapitre qui tient sous
    `MOTS_MAX_DU_PARENT` mots (les sous-articles « étendue », « exclusions », « limites » se lisent ensemble), ou un
    chapitre plus long qui n'a pas de sous-chapitre. Le type que le découpage donne aux clauses ne sert pas à les
    trouver : il se trompe trop souvent (l'assistance de A n'a aucune clause de type « garantie », son pack
    multimédia est classé « exclusion »). Le contrat est donc couvert en entier, y compris par des chapitres qui ne
    garantissent rien (les obligations en cas de sinistre) : `porte_garantie` dit ce que le découpage en pense."""
    racine = dossier.arbre(clauses)
    tous = dossier.chapitres(racine)
    par_chemin = {ch.chemin: ch for ch in tous}
    table = dossier.reperes(racine)
    generales = {c.id for ch in tous if dossier.est_generale(ch) for c in ch.toutes()}
    racines: dict[tuple[str, ...], dossier.Chapitre] = {}
    for ch in tous:
        if dossier.est_generale(ch) or not ch.toutes():
            continue
        parent = par_chemin.get(ch.chemin[:-1])
        petit = ch.mots() <= dossier.MOTS_MAX_DU_PARENT
        if (petit and (parent is None or parent.mots() > dossier.MOTS_MAX_DU_PARENT)) or (not petit and not ch.enfants):
            racines[ch.chemin] = ch
    for ch in tous:                                   # les clauses propres d'un grand titre, que rien d'autre ne lit
        if ch.clauses and not any(ch.chemin[:i] in racines for i in range(1, len(ch.chemin) + 1)) \
                and not dossier.est_generale(ch):
            racines[ch.chemin] = dossier.Chapitre(ch.chemin, ch.clauses, [])
    garanties, attendues = [], []
    for ch in racines.values():
        repere = table[ch.chemin]
        garanties.append(Garantie(repere, ch.titre, ch.chemin, est_optionnelle(ch.chemin), ch.mots(),
                                  any(c.type == TypeClause.GARANTIE for c in ch.toutes())))
        propres = {c.id for c in ch.toutes()}
        chapeaux = {c.id for i in range(1, len(ch.chemin)) for c in par_chemin[ch.chemin[:i]].clauses}
        # Le chapeau d'un grand titre n'attend que ses propres clauses, pas tout ce que le titre contient :
        # les chapitres en dessous sont d'autres lignes de la table.
        dessous = {c.id for c in par_chemin[ch.chemin].toutes()} - propres
        for c in dossier.composer(clauses, [repere]):
            if c.id in dessous:
                continue
            if c.id in propres:
                role = ROLE_DU_TYPE[c.type]
            elif c.id in generales:
                role = "exclusion_generale"
            elif c.id in chapeaux:
                role = "chapeau"
            elif dossier.est_definition(c):
                role = "definition"
            else:
                role = "renvoi"
            attendues.append(Attendue(repere, c.id, role, role not in SANS_JUGEMENT))
    return garanties, attendues


def enregistrer(base, contrat_id: str) -> tuple[int, int]:
    """Calcule et enregistre les deux tables d'un contrat (en remplaçant ce qui s'y trouvait). Rend le nombre de
    garanties et de lignes attendues."""
    garanties, attendues = calculer(base.clauses(contrat_id))
    with sqlite3.connect(base.chemin) as cx:
        cx.executescript(SCHEMA)
        cx.execute("DELETE FROM garanties WHERE contrat_id = ?", (contrat_id,))
        cx.execute("DELETE FROM clauses_attendues WHERE contrat_id = ?", (contrat_id,))
        cx.executemany("INSERT INTO garanties VALUES (?,?,?,?,?,?,?)",
                       [(contrat_id, g.repere, g.titre, json.dumps(list(g.chemin), ensure_ascii=False),
                         int(g.optionnelle), g.mots, int(g.porte_garantie)) for g in garanties])
        cx.executemany("INSERT INTO clauses_attendues VALUES (?,?,?,?,?)",
                       [(contrat_id, a.garantie, a.clause_id, a.role, int(a.bloque)) for a in attendues])
    return len(garanties), len(attendues)


def garanties(base, contrat_id: str) -> list[Garantie]:
    """Les garanties enregistrées d'un contrat, dans l'ordre du contrat ; vide si la table n'a pas été calculée."""
    with sqlite3.connect(base.chemin) as cx:
        cx.executescript(SCHEMA)
        lignes = cx.execute("SELECT repere, titre, chemin, optionnelle, mots, porte_garantie FROM garanties "
                            "WHERE contrat_id = ? ORDER BY rowid", (contrat_id,)).fetchall()
    return [Garantie(l[0], l[1], tuple(json.loads(l[2])), bool(l[3]), l[4], bool(l[5])) for l in lignes]


def attendues(base, contrat_id: str, garantie: str | None = None) -> list[Attendue]:
    """Les clauses attendues d'un contrat, ou d'une seule de ses garanties."""
    requete = "SELECT garantie, clause_id, role, bloque FROM clauses_attendues WHERE contrat_id = ?"
    parametres: tuple = (contrat_id,)
    if garantie is not None:
        requete, parametres = requete + " AND garantie = ?", (contrat_id, garantie)
    with sqlite3.connect(base.chemin) as cx:
        cx.executescript(SCHEMA)
        lignes = cx.execute(requete + " ORDER BY rowid", parametres).fetchall()
    return [Attendue(l[0], l[1], l[2], bool(l[3])) for l in lignes]
