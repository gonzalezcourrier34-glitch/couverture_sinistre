"""La lecture des clauses (DEMARCHE 7.188, 7.189) : les deux appels au modèle, et l'analyse de bout en bout.

1. **Désigner** : le modèle reçoit la table des matières et la déclaration, et désigne les chapitres à relire.
2. Le code compose le dossier (`dossier.py`) et sait, par la table des clauses attendues (`attendu.py`), ce qui
   doit recevoir un jugement.
3. **Juger** : le modèle reçoit les clauses du dossier et la déclaration, et rend un jugement par clause.
4. Le code contrôle les citations, fait la jointure, décide (`jugement.py`), puis rapproche la décision de celle
   de la chaîne de règles.

Le modèle ne voit jamais la question « ce sinistre est-il couvert ? » : il choisit des chapitres, puis lit des
clauses une à une. La réponse est calculée.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..llm import LLM, completer_avec_schema, extraire_json
from ..models import Clause, Decision
from . import attendu, dossier, jugement

SYSTEME_DESIGNATION = """Tu prépares le dossier d'un sinistre pour un gestionnaire d'assurance habitation. On te donne la table des matières des conditions générales du contrat et la déclaration de l'assuré. Désigne les chapitres qu'il faut relire pour dire si le sinistre est couvert.

Chaque ligne de la table est de la forme « [repère] titre (taille) », parfois suivie des premiers mots du chapitre. Un chapitre désigné est lu en entier, avec tout ce qu'il contient.

Désigne :
1. chaque garantie qui pourrait jouer, même en concurrence avec une autre (un téléviseur cassé peut relever du bris de vitrages ET du matériel multimédia ; de l'eau entrée après un coup de vent, de la tempête ET des dégâts des eaux) ;
2. les garanties optionnelles, packs ou extensions qui pourraient couvrir ce que la garantie de base ne couvre pas (un séjour hors du logement, un objet de valeur, le jardin, une piscine…) ;
3. le chapitre qui dit quels biens ou quelles personnes sont assurés, quand la réponse peut en dépendre ;
4. les mesures de prévention ou de sécurité et les obligations en cas de sinistre qui visent ce type de sinistre (plainte après un vol, eau coupée en cas d'absence…) ;
5. les définitions propres à la garantie, quand le contrat leur consacre un chapitre.

Dans le doute, désigne : un chapitre de trop ne coûte rien, un chapitre oublié fausse la réponse. Inutile de désigner le lexique général ni les exclusions générales : ils sont toujours ajoutés.

Réponds uniquement par un objet JSON : {"chapitres": ["repère", "repère"], "motif": "une phrase"}. Les repères sont recopiés tels quels, sans les crochets."""

SCHEMA_DESIGNATION = {"type": "object", "additionalProperties": False, "required": ["chapitres", "motif"],
                      "properties": {"chapitres": {"type": "array", "items": {"type": "string"}},
                                     "motif": {"type": "string"}}}

SYSTEME_JUGEMENT = """Tu es gestionnaire de sinistres. On te donne des clauses des conditions générales d'un contrat d'assurance habitation, puis la déclaration d'un assuré. Tu ne dis pas si le sinistre est couvert : tu lis chaque clause marquée « à juger » et tu dis son effet sur CE sinistre, d'après ce que dit la déclaration et rien d'autre.

Pour chaque clause à juger, un effet parmi :
- "couvre" : la clause accorde une garantie pour ce qui est arrivé (l'événement ET le bien ou la personne déclarés entrent dans ce qu'elle assure). Une clause qui dit seulement quels biens ou quelles personnes sont assurés, sans garantir un événement, ne "couvre" pas : "sans_effet" si le bien déclaré en fait partie, "exclut" s'il en est écarté ;
- "exclut" : la clause refuse ce sinistre : une exclusion dont la déclaration établit le fait, un bien que le contrat n'assure pas, une condition ou une obligation que la déclaration montre non remplie ;
- "a_verifier" : la déclaration évoque la situation que vise la clause, mais ne dit pas le fait précis qui tranche (une durée, un montant, une serrure, une formule souscrite) ; donne alors la question à poser à l'assuré ;
- "sans_effet" : la clause ne concerne pas ce sinistre, ou la déclaration écarte ce qu'elle vise.

Règles de lecture :
- Une exclusion que rien dans la déclaration n'évoque est "sans_effet", pas "a_verifier" : on ne demande pas à l'assuré s'il a fait exprès, s'il y avait une guerre ou si son bâtiment était délabré quand rien ne le suggère.
- Ce que la déclaration ne dit pas reste inconnu : ne le suppose pas. Mais si elle permet de trancher, tranche.
- Une clause qui contient plusieurs cas (une liste d'exclusions) se juge sur le cas qui joue : "exclut" si l'un d'eux s'applique, "a_verifier" si l'un d'eux est évoqué sans être établi, sinon "sans_effet".
- Une clause qui garantit et exclut à la fois (« nous couvrons… sauf… ») : "exclut" si l'exception joue, sinon "couvre" si elle garantit ce sinistre.
- Une phrase du type « applicable si les conditions particulières mentionnent la garantie » est "sans_effet" : savoir si une garantie est souscrite n'est pas ton affaire. En revanche, une garantie réservée à une formule nommée (« en formule Confort ») est "a_verifier", avec la question.
- L'exclusion ou la condition propre à une garantie ne se juge "exclut" que si cette garantie joue pour ce sinistre ; si la garantie ne le concerne pas, ses exclusions sont "sans_effet".
- Un bien ou un dommage que le contrat n'assure que par une option, un pack ou une formule (« sauf si l'option … est souscrite ») : "a_verifier", portée "tout", avec la question sur cette option.
- Les définitions sont données pour fixer le sens des mots : applique-les, sans les juger.

"portee" : "garantie" quand le refus ou le doute ne vaut que pour la garantie de cette clause (une autre garantie pourrait couvrir) ; "tout" quand il vaut pour tout le contrat (un bien que le contrat n'assure nulle part, une obligation générale, une exclusion commune à toutes les garanties).

Pour "couvre", "exclut" et "a_verifier" : "extrait_contrat" est la phrase de la clause qui fonde le jugement, recopiée mot pour mot (au plus 40 mots). Pour "couvre" et "exclut" : "extrait_declaration" est le passage de la déclaration qui l'établit, recopié mot pour mot. Pour "sans_effet", la clause et l'effet suffisent.

Réponds uniquement par un objet JSON, avec un élément par clause à juger, dans l'ordre :
{"jugements": [{"clause": "2.7", "effet": "couvre", "portee": "garantie", "extrait_contrat": "…", "extrait_declaration": "…", "question": "", "motif": "une phrase"}, {"clause": "2.7-b", "effet": "sans_effet"}]}"""

SCHEMA_JUGEMENT = {
    "type": "object", "additionalProperties": False, "required": ["jugements"],
    "properties": {"jugements": {"type": "array", "items": {
        "type": "object", "required": ["clause", "effet"],
        "properties": {"clause": {"type": "string"}, "effet": {"type": "string", "enum": list(jugement.EFFETS)},
                       "portee": {"type": "string", "enum": list(jugement.PORTEES)},
                       "extrait_contrat": {"type": "string"}, "extrait_declaration": {"type": "string"},
                       "question": {"type": "string"}, "motif": {"type": "string"}}}}}}


@dataclass
class Lecture:
    """Ce qu'une lecture des clauses a produit, de la désignation à la décision."""

    etat: jugement.Etat
    designes: list[str] = field(default_factory=list)       # les repères rendus par le modèle
    garanties: list[str] = field(default_factory=list)      # les garanties du contrat que ces repères touchent
    dossier: list[Clause] = field(default_factory=list)
    decision: Decision = Decision.INCERTAIN                 # après la contresignature des règles
    desaccord: str = ""


def message_designation(clauses: list[Clause], declaration: str) -> str:
    """Le message du premier appel : la table des matières d'abord (elle ne change pas d'une déclaration à
    l'autre : le fournisseur la relit depuis son cache), la déclaration à la fin."""
    return f"## Table des matières\n{dossier.table_des_matieres(clauses)}\n\n## Déclaration\n{declaration}"


def message_jugement(pieces: list[Clause], a_juger: set[str], declaration: str) -> str:
    """Le message du second appel : chaque clause du dossier avec son identifiant, son chemin, et la mention
    « à juger » ou « définition, à lire » ; la déclaration à la fin."""
    blocs = []
    for c in pieces:
        mention = "à juger" if c.id in a_juger else "à lire, sans jugement"
        blocs.append(f"[{c.id}] ({mention}) {' > '.join(c.chemin)}\n{c.texte}")
    return "## Clauses\n" + "\n\n".join(blocs) + f"\n\n## Déclaration\n{declaration}"


def garanties_touchees(garanties: list[attendu.Garantie], clauses: list[Clause], designes: list[str]) -> list[str]:
    """Les garanties de la table que les repères désignés touchent : celle qui porte ce repère, celles qui sont
    dans le chapitre désigné, ou celle qui contient la clause désignée."""
    racine = dossier.arbre(clauses)
    table = dossier.reperes(racine)
    par_repere = {table[ch.chemin]: ch.chemin for ch in dossier.chapitres(racine)}
    for c in clauses:
        par_repere.setdefault(c.id, tuple(c.chemin))
    touchees = []
    for r in designes:
        chemin = par_repere.get(r)
        if chemin is None:
            continue
        for g in garanties:
            n = min(len(chemin), len(g.chemin))
            if chemin[:n] == g.chemin[:n] and g.repere not in touchees:
                touchees.append(g.repere)
    return touchees


def lire(base, contrat_id: str, llm: LLM, declaration: str, regles: Decision | None = None,
         llm_designation: LLM | None = None) -> Lecture:
    """L'analyse d'une déclaration par la lecture des clauses. `regles` : la décision de la chaîne de règles sur
    la même déclaration, pour la contresignature (rien : la lecture tient seule)."""
    clauses = base.clauses(contrat_id)
    garanties = attendu.garanties(base, contrat_id)
    if not garanties:
        attendu.enregistrer(base, contrat_id)
        garanties = attendu.garanties(base, contrat_id)
    reponse = extraire_json(completer_avec_schema(llm_designation or llm, SYSTEME_DESIGNATION,
                                                  message_designation(clauses, declaration), SCHEMA_DESIGNATION))
    designes = [str(r).strip().strip("[]") for r in reponse.get("chapitres") or []]
    touchees = garanties_touchees(garanties, clauses, designes)
    if not touchees:                                   # rien de désigné : ni refus ni couverture, on le dit
        etat = jugement.Etat(Decision.INCERTAIN, motif="aucun chapitre du contrat n'a été désigné : à examiner")
        return Lecture(etat, designes, [], [], Decision.INCERTAIN, "")
    attendues = [a for g in touchees for a in attendu.attendues(base, contrat_id, g)]
    ids = {a.clause_id for a in attendues}
    # Le dossier envoyé est ce que la table attend, ni plus ni moins : toute clause dont on exigera un jugement
    # est sous les yeux du modèle. S'y ajoutent les définitions que les mots de la déclaration appellent.
    lexique = {c.id for c in dossier.composer(clauses, designes, declaration) if dossier.est_definition(c)}
    pieces = [c for c in clauses if c.id in ids or c.id in lexique]
    a_juger = {a.clause_id for a in attendues if a.bloque}
    rendus = jugement.depuis_reponse(extraire_json(completer_avec_schema(
        llm, SYSTEME_JUGEMENT, message_jugement(pieces, a_juger, declaration), SCHEMA_JUGEMENT)))
    gardes, defauts = jugement.controler(rendus, pieces, declaration)
    lignes, non_attendus = jugement.joindre(base, contrat_id, touchees, gardes)
    etat = jugement.decider(lignes, {g.repere for g in garanties if g.optionnelle}, non_attendus, defauts,
                            {g.repere: g.chemin for g in garanties})
    decision, desaccord = jugement.arbitrer(etat, regles)
    return Lecture(etat, designes, touchees, pieces, decision, desaccord)
