"""Le dossier de clauses d'un sinistre (DEMARCHE 7.188) : ce que le modèle devra juger, clause par clause.

La chaîne de règles ne connaît du contrat que ce qu'on en a traduit. Ici on repart du texte : le modèle désigne,
dans la table des matières, les chapitres qui peuvent concerner la déclaration ; le code compose ensuite le
dossier, sans rien laisser à son choix :

- chaque chapitre désigné, en entier, avec ce qui en dépend (ses exclusions, ses conditions, ses limites) ;
- s'il est petit, le chapitre qui le contient (désigner « 3.1.4.1 Étendue » amène tout « 3.1.4 Dégâts des eaux ») ;
- les chapeaux : les clauses des titres au-dessus (« 3.1.8 » pour « 3.1.8.6 », le titre d'une option) ;
- les exclusions générales du contrat, toujours ;
- les articles auxquels ces clauses renvoient ;
- les définitions du lexique dont le mot paraît dans la déclaration ou dans les clauses retenues.

Dans le doute, on élargit : une clause de trop coûte quelques tokens, une exclusion oubliée coûte un « couvert »
à tort. Rien ici n'appelle le modèle : la composition se vérifie sans lui.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..models import Clause, TypeClause
from ..texte import normaliser

# Un chapitre désigné qui pèse moins que cela entraîne celui qui le contient, si celui-ci reste sous ce poids :
# les sous-articles d'une garantie (étendue, exclusions, limites) se lisent ensemble.
MOTS_MAX_DU_PARENT = 2500
MOTS_DU_DEBUT = 30          # les premiers mots d'une garantie, montrés dans la table des matières
GENERALES = re.compile(r"exclusions? (generales?|communes?)")
COMMUNES = re.compile(r"communes? a toutes")
LEXIQUE = re.compile(r"lexique|definitions")


@dataclass
class Chapitre:
    """Un nœud de la table des matières : son chemin, ses propres clauses, et ce qu'il contient."""

    chemin: tuple[str, ...]
    clauses: list[Clause] = field(default_factory=list)      # celles dont le chemin est exactement celui-ci
    enfants: list["Chapitre"] = field(default_factory=list)

    @property
    def titre(self) -> str:
        return self.chemin[-1] if self.chemin else ""

    def toutes(self) -> list[Clause]:
        """Ses clauses et celles de tout ce qu'il contient, dans l'ordre du contrat."""
        return self.clauses + [c for e in self.enfants for c in e.toutes()]

    def mots(self) -> int:
        return sum(len(c.texte.split()) for c in self.toutes())


def mots(texte: str) -> list[str]:
    """Les mots d'un texte, sans accents ni casse (pour comparer un titre du lexique à une phrase)."""
    return re.findall(r"[a-z0-9]+", normaliser(texte))


def est_definition(c: Clause) -> bool:
    """Une entrée du lexique : une clause rangée sous un titre de lexique ou de définitions, quel que soit le type
    que le découpage lui a donné (les « objets personnels » de B y sont classés « garantie »)."""
    return any(LEXIQUE.search(normaliser(t)) for t in c.chemin[:-1])


def terme(c: Clause) -> list[str]:
    """Les mots du terme défini : le titre de l'entrée, sans son numéro ni ce qui est entre parenthèses
    (« ENGINS DE DÉPLACEMENT PERSONNEL MOTORISÉS (EDPM) »)."""
    titre = re.sub(r"\([^)]*\)", " ", c.chemin[-1] if c.chemin else c.titre)
    return [m for m in mots(titre) if not m.isdigit()]


def arbre(clauses: list[Clause]) -> Chapitre:
    """La table des matières en arbre, d'après le chemin de chaque clause. Les entrées du lexique n'y sont pas :
    on ne les désigne pas, le code les ajoute d'après les mots."""
    racine = Chapitre(())
    index: dict[tuple[str, ...], Chapitre] = {(): racine}
    for c in clauses:
        if est_definition(c):
            continue
        chemin = tuple(c.chemin)
        for i in range(1, len(chemin) + 1):
            if chemin[:i] not in index:
                index[chemin[:i]] = Chapitre(chemin[:i])
                index[chemin[:i - 1]].enfants.append(index[chemin[:i]])
        index[chemin].clauses.append(c)
    return racine


def chapitres(racine: Chapitre) -> list[Chapitre]:
    """Tous les chapitres de l'arbre, dans l'ordre du contrat, sans la racine."""
    return [x for e in racine.enfants for x in [e, *chapitres(e)]]


def reperes(racine: Chapitre) -> dict[tuple[str, ...], str]:
    """Le repère de chaque chapitre dans la table : l'identifiant de sa première clause propre (« 3.1.4 », « 2.7 »,
    « S25 ») ; pour un titre sans clause à lui (« 3.1.6 Vol », dont le texte est dans ses sous-articles), « §n ».
    Deux chapitres n'ont jamais le même repère."""
    table, n = {}, 0
    for ch in chapitres(racine):
        if ch.clauses:
            table[ch.chemin] = ch.clauses[0].id
        else:
            n += 1
            table[ch.chemin] = f"§{n}"
    return table


def table_des_matieres(clauses: list[Clause]) -> str:
    """La table des matières donnée au modèle : une ligne par chapitre, « [repère] titre (n mots) », indentée
    selon la profondeur. Les repères sont ceux qu'il rend pour désigner un chapitre. Un chapitre qui énonce une
    garantie montre aussi ses premiers mots : un titre ne dit pas tout (le « heurt » du contrat A est couvert sous
    « Incendie et risques connexes »)."""
    racine = arbre(clauses)
    table = reperes(racine)
    lignes = []
    for ch in chapitres(racine):
        ligne = f"{'  ' * (len(ch.chemin) - 1)}[{table[ch.chemin]}] {ch.titre} ({ch.mots()} mots)"
        garantie = next((c for c in ch.clauses if c.type == TypeClause.GARANTIE), None)
        if garantie is not None:
            ligne += " — " + " ".join(garantie.texte.split()[:MOTS_DU_DEBUT]) + "…"
        lignes.append(ligne)
    return "\n".join(lignes)


def est_generale(ch: Chapitre) -> bool:
    """Un chapitre d'exclusions qui vaut pour tout le contrat : « exclusions générales », ou « exclusions » rangé
    sous un titre « communes à toutes les garanties »."""
    titre = normaliser(ch.titre)
    if GENERALES.search(titre):
        return True
    return "exclusion" in titre and any(COMMUNES.search(normaliser(t)) for t in ch.chemin[:-1])


def composer(clauses: list[Clause], designes: list[str], declaration: str = "") -> list[Clause]:
    """Le dossier d'un sinistre : les clauses à juger, dans l'ordre du contrat. `designes` : les repères rendus par
    le modèle (un repère inconnu est ignoré ; la liste des ignorés se lit avec `inconnus`)."""
    racine = arbre(clauses)
    tous = chapitres(racine)
    par_chemin = {ch.chemin: ch for ch in tous}
    table = reperes(racine)
    par_repere = {table[ch.chemin]: ch for ch in tous}
    for ch in tous:                                   # une clause désignée par son identifiant : son chapitre
        for c in ch.clauses:
            par_repere.setdefault(c.id, ch)
    retenus: dict[str, Clause] = {}

    def prendre(cs):
        for c in cs:
            retenus.setdefault(c.id, c)

    for repere in designes:
        ch = par_repere.get(repere)
        if ch is None:
            continue
        parent = par_chemin.get(ch.chemin[:-1])
        if parent is not None and parent.mots() <= MOTS_MAX_DU_PARENT:
            ch = parent                               # les sous-articles d'une garantie se lisent ensemble
        prendre(ch.toutes())
        for i in range(1, len(ch.chemin)):            # les chapeaux : les clauses propres des titres au-dessus
            prendre(par_chemin[ch.chemin[:i]].clauses)
    for ch in tous:
        if est_generale(ch):
            prendre(ch.toutes())
    par_id = {c.id: c for c in clauses}
    for c in list(retenus.values()):                  # les articles auxquels le dossier renvoie
        prendre(par_id[r] for r in c.renvois if r in par_id)
    texte = set(mots(declaration)) | {m for c in retenus.values() for m in mots(" ".join([*c.chemin, c.texte]))}
    definis = [c for c in clauses if est_definition(c) and (t := terme(c)) and set(t) <= texte]
    for d in definis:                                 # le lexique : les termes qui paraissent, et leurs sous-entrées
        prendre(c for c in clauses if est_definition(c) and tuple(c.chemin[:len(d.chemin)]) == tuple(d.chemin))
    ordre = {c.id: i for i, c in enumerate(clauses)}
    return sorted(retenus.values(), key=lambda c: ordre[c.id])


def inconnus(clauses: list[Clause], designes: list[str]) -> list[str]:
    """Les repères désignés qui ne correspondent à aucun chapitre ni à aucune clause du contrat."""
    connus = {c.id for c in clauses} | set(reperes(arbre(clauses)).values())
    return [r for r in designes if r not in connus]
