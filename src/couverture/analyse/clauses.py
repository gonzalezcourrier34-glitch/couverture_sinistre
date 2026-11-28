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

from collections.abc import Callable
from dataclasses import dataclass, field

from ..llm import LLM, completer_avec_schema, extraire_json
from ..models import Clause, Condition, Decision, EtatCondition
from ..texte import normaliser
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
- "limite" : la clause ne refuse pas le sinistre mais réduit ce qui sera payé, et la déclaration établit qu'elle joue. Trois cas : une obligation dont la sanction écrite est une indemnité réduite (« l'indemnité sera réduite » n'est pas « n'est pas garanti ») ; un plafond que le montant déclaré dépasse ; une exclusion qui n'écarte qu'un poste du dommage quand le reste demeure garanti (les frais de réparation de la pièce à l'origine de la fuite, alors que les dégâts causés par l'eau sont couverts). La franchise ordinaire, qui vaut pour tout sinistre, est "sans_effet". Reste "exclut" : l'exclusion qui écarte tout ce que la déclaration réclame, et l'obligation violée dont la clause ne dit pas la sanction ou dont la sanction est la perte de la garantie.
- "sans_effet" : la clause ne concerne pas ce sinistre, ou la déclaration écarte ce qu'elle vise.

Règles de lecture :
- Une exclusion que rien dans la déclaration n'évoque est "sans_effet", pas "a_verifier" : on ne demande pas à l'assuré s'il a fait exprès, s'il y avait une guerre ou si son bâtiment était délabré quand rien ne le suggère.
- Ce que la déclaration ne dit pas reste inconnu : ne le suppose pas. Mais si elle permet de trancher, tranche.
- Une cause que l'assuré présente comme seulement probable (« je pense que », « sans doute », « peut-être », « on m'a dit que ») n'est pas établie : si l'effet d'une clause dépend de cette cause, cette clause est "a_verifier", avec la question qui l'établirait.
- Une garantie qui pose elle-même une condition (un lieu, une durée, un délai, un moyen de protection, une qualité du bien ou de la personne) ne "couvre" que si la déclaration établit cette condition ; si elle n'en dit rien, elle est "a_verifier", avec la question sur cette condition. Cela ne vaut pas pour les exclusions : une exclusion que rien n'évoque reste "sans_effet".
- Une clause qui énumère les biens assurés par une garantie n'exclut pas un bien qu'elle ne nomme pas : si ce bien relève d'une autre garantie du dossier, elle est "sans_effet".
- Une clause qui contient plusieurs cas (une liste d'exclusions) se juge sur le cas qui joue : "exclut" si l'un d'eux s'applique, "a_verifier" si l'un d'eux est évoqué sans être établi, sinon "sans_effet".
- Une clause qui garantit et exclut à la fois (« nous couvrons… sauf… ») : "exclut" si l'exception joue, sinon "couvre" si elle garantit ce sinistre.
- Une phrase du type « applicable si les conditions particulières mentionnent la garantie » est "sans_effet" : savoir si une garantie est souscrite n'est pas ton affaire. En revanche, une garantie réservée à une formule nommée (« en formule Confort ») est "a_verifier", portée "garantie", avec la question, mais seulement si c'est la garantie de l'événement déclaré : pour une fuite d'eau, la formule qu'exige la garantie des dommages électriques est "sans_effet".
- L'exclusion ou la condition propre à une garantie ne se juge "exclut" que si cette garantie joue pour ce sinistre ; si la garantie ne le concerne pas, ses exclusions sont "sans_effet".
- Un bien ou un dommage que le contrat n'assure que par une option, un pack ou une formule (« sauf si l'option … est souscrite ») : "a_verifier", portée "tout", avec la question sur cette option.
- Les définitions (clauses « à lire, sans jugement ») fixent le sens des mots et l'emportent sur le sens courant : avant de juger une clause, cherche la définition des termes qu'elle emploie. Si la clause exclut « les vols simples » ou excepte « le mobilier de jardin », c'est la définition du contrat qui dit si le fait déclaré en est un.
- Juge chaque clause sous l'identifiant écrit entre crochets, même si son texte numérote des alinéas.

"portee" : "garantie" quand le refus ou le doute ne vaut que pour la garantie de cette clause (une autre garantie pourrait couvrir) ; "tout" quand il vaut pour tout le contrat (un bien que le contrat n'assure nulle part, une obligation générale, une exclusion commune à toutes les garanties).

Pour "couvre", "exclut", "limite" et "a_verifier" : "extrait_contrat" est la phrase de la clause qui fonde le jugement, recopiée mot pour mot (au plus 40 mots). Pour "couvre" et "exclut" : "extrait_declaration" est le passage de la déclaration qui l'établit, recopié mot pour mot et d'un seul tenant (un seul passage, sans le résumer).

Réponds uniquement par un objet JSON. "jugements" : un élément pour chaque clause dont l'effet est "couvre", "exclut", "limite" ou "a_verifier", et pour elles seulement. "sans_effet" : la liste des identifiants de toutes les autres clauses à juger, sans rien d'autre. Chaque clause à juger figure une fois, dans l'une ou dans l'autre :
{"jugements": [{"clause": "2.7", "effet": "couvre", "portee": "garantie", "extrait_contrat": "…", "extrait_declaration": "…", "question": "", "motif": "une phrase courte"}], "sans_effet": ["2.7-b", "2.8"]}"""

RELANCE = ("Ces clauses n'ont pas reçu de jugement exploitable à la première lecture : oubliées, ou citées de façon "
           "inexacte. Juge chacune d'elles, et recopie les citations mot pour mot, sans sauter de mots.\n\n")

SCHEMA_JUGEMENT = {
    "type": "object", "additionalProperties": False, "required": ["jugements"],
    "properties": {"sans_effet": {"type": "array", "items": {"type": "string"}}, "jugements": {"type": "array", "items": {
        "type": "object", "required": ["clause", "effet"],
        "properties": {"clause": {"type": "string"}, "effet": {"type": "string", "enum": [e for e in jugement.EFFETS if e != "sans_effet"]},
                       "portee": {"type": "string", "enum": list(jugement.PORTEES)},
                       "extrait_contrat": {"type": "string"}, "extrait_declaration": {"type": "string"},
                       "question": {"type": "string"}, "motif": {"type": "string"}}}}}}


# L'arbitrage ciblé (7.211) : la lecture couvre, les règles non. Plutôt que de s'en tenir au désaccord, on repose au
# modèle une seule question par obstacle que les règles ont trouvé : la déclaration l'écarte-t-elle ?
SYSTEME_ARBITRAGE = """Tu es gestionnaire de sinistres. Une première lecture des conditions générales conclut que le sinistre déclaré est couvert. Une seconde lecture, faite par des règles traduites du contrat, ne le couvre pas, à cause des obstacles listés ci-dessous : pour chacun, la clause du contrat, ce que les règles ont vérifié, et ce qu'elles en ont conclu.

Pour chaque obstacle, dis si la déclaration l'écarte :
- « ecarte » : la déclaration dit en toutes lettres ce qui fait que l'obstacle ne joue pas (le fait qui remplit la condition, ou qui sort le sinistre de l'exclusion). Recopie mot pour mot, dans « extrait_declaration », la phrase de la déclaration qui le dit.
- « confirme » : l'obstacle joue bien pour ce sinistre.
- « inconnu » : la déclaration ne permet pas de le dire.

Tu n'écartes un obstacle que sur ce qui est écrit dans la déclaration, jamais sur ce qui est probable ou habituel. Dans le doute, réponds « inconnu ». Le sens des mots est celui du contrat."""

SCHEMA_ARBITRAGE = {
    "type": "object", "additionalProperties": False, "required": ["obstacles"],
    "properties": {"obstacles": {"type": "array", "items": {
        "type": "object", "required": ["numero", "avis"],
        "properties": {"numero": {"type": "integer"}, "avis": {"type": "string", "enum": ["ecarte", "confirme", "inconnu"]},
                       "extrait_declaration": {"type": "string"}, "motif": {"type": "string"}}}}}}

MAX_OBSTACLES = 6  # au-delà, le désaccord est trop large pour une relecture ciblée : on reste à préciser


def obstacles_des_regles(regles) -> list[Condition]:
    """Ce qui, dans la réponse des règles, empêche de couvrir : une exclusion établie ou possible, une condition de
    garantie ou une obligation non remplie ou inconnue. `regles` : le résultat de la chaîne (avec son verdict), ou
    une simple décision, qui n'en dit rien."""
    verdict = getattr(regles, "verdict", None)
    if verdict is None:
        return []
    vus, obstacles = set(), []
    for c in verdict.conditions:
        joue = (c.etat in (EtatCondition.REMPLIE, EtatCondition.INCONNUE) if c.nature == "exclusion"
                else c.etat in (EtatCondition.NON_REMPLIE, EtatCondition.INCONNUE) if c.nature in ("garantie", "obligation")
                else False)
        if joue and (c.clause_id, c.enonce) not in vus:
            vus.add((c.clause_id, c.enonce))
            obstacles.append(c)
    return obstacles


def message_arbitrage(obstacles: list[Condition], par_id: dict[str, Clause], decision_regles: Decision,
                      declaration: str) -> str:
    """Chaque obstacle numéroté : la clause entière, la question que les règles lui ont posée, leur conclusion."""
    conclusions = {EtatCondition.REMPLIE: "oui", EtatCondition.NON_REMPLIE: "non", EtatCondition.INCONNUE: "inconnu"}
    blocs = []
    for n, c in enumerate(obstacles, 1):
        texte = par_id[c.clause_id].texte if c.clause_id in par_id else c.extrait
        nature = "exclusion" if c.nature == "exclusion" else "condition de garantie" if c.nature == "garantie" else c.nature
        blocs.append(f"### Obstacle {n} : {nature}, clause [{c.clause_id}]\n{texte}\n"
                     f"Ce que les règles ont vérifié : {c.enonce} → {conclusions[c.etat]}"
                     + (f" ({c.justification})" if c.justification else ""))
    return (f"Réponse des règles : {decision_regles.value}\n\n" + "\n\n".join(blocs)
            + f"\n\n## Déclaration\n{declaration}")


def arbitrage_cible(llm: LLM, obstacles: list[Condition], par_id: dict[str, Clause], decision_regles: Decision,
                    declaration: str) -> tuple[bool, list[str]]:
    """La relecture ciblée : le « couvert » tient si, et seulement si, chaque obstacle est écarté par une phrase de
    la déclaration, retrouvée mot pour mot. Rend ce verdict et une ligne par obstacle, pour le raisonnement."""
    reponse = extraire_json(completer_avec_schema(llm, SYSTEME_ARBITRAGE,
                                                  message_arbitrage(obstacles, par_id, decision_regles, declaration),
                                                  SCHEMA_ARBITRAGE))
    avis = {a.get("numero"): a for a in reponse.get("obstacles") or [] if isinstance(a, dict)}
    declaration_n = normaliser(declaration)
    tient, lignes = True, []
    for n, c in enumerate(obstacles, 1):
        a = avis.get(n) or {}
        extrait = str(a.get("extrait_declaration") or "")
        ecarte = a.get("avis") == "ecarte" and bool(extrait) and jugement._dans_la_declaration(extrait, declaration_n)
        tient = tient and ecarte
        etat = ("écarté" if ecarte else "écarté sans citation exacte : non retenu" if a.get("avis") == "ecarte"
                else "confirmé" if a.get("avis") == "confirme" else "inconnu")
        lignes.append(f"art. {c.clause_id} ({c.enonce}) : {etat}" + (f" ← « {extrait} »" if ecarte else ""))
    return tient, lignes


@dataclass
class Lecture:
    """Ce qu'une lecture des clauses a produit, de la désignation à la décision."""

    etat: jugement.Etat
    designes: list[str] = field(default_factory=list)       # les repères rendus par le modèle
    garanties: list[str] = field(default_factory=list)      # les garanties du contrat que ces repères touchent
    dossier: list[Clause] = field(default_factory=list)
    decision: Decision = Decision.INCERTAIN                 # après la contresignature des règles
    desaccord: str = ""
    relancees: list[str] = field(default_factory=list)      # les clauses redemandées au modèle, faute de jugement
    rappels: list[jugement.Jugement] = field(default_factory=list)   # questions du règlement, sans effet sur la décision
    arbitrage: list[str] = field(default_factory=list)  # la relecture ciblée des obstacles des règles, s'il y en a eu
    ajoutes: list[str] = field(default_factory=list)    # les chapitres ajoutés d'après les règles (13.2)
    # Les jugements sur lesquels la décision repose : gardés pour la relecture après les réponses du client (13.4).
    jugements: list[jugement.Jugement] = field(default_factory=list)
    rejugees: list[str] = field(default_factory=list)   # à cette relecture, les seules clauses redemandées au modèle
    appelees: list[str] = field(default_factory=list)   # les garanties ajoutées parce que le modèle en a jugé une clause


# Au plus deux garanties ajoutées d'après les jugements : au-delà, le modèle juge tout le contrat, et la désignation n'a
# plus de sens.
MAX_APPELEES = 2


def garanties_appelees(base, contrat_id: str, jugements: list[jugement.Jugement], touchees: list[str]) -> list[str]:
    """Les garanties hors du dossier dont le modèle a jugé une clause propre « couvre » ou « à vérifier » (7.245).

    La désignation peut oublier un chapitre que le modèle, en jugeant, reconnaît pourtant : vu sur « six », un téléviseur
    qui prend feu, la garantie incendie exclue, et la question juste posée sur la garantie des dommages électriques,
    qui n'était pas au dossier ; le code jetait ce jugement, et la réponse devenait un refus. Une clause propre est une
    clause de la garantie même (pas une exclusion générale, une définition, un chapeau ou un renvoi, qu'elle emprunte)."""
    garanties_de: dict[str, list[str]] = {}
    for a in attendu.attendues(base, contrat_id):
        if a.role not in jugement.EMPRUNTS:
            garanties_de.setdefault(a.clause_id, []).append(a.garantie)
    appelees: list[str] = []
    for j in jugements:
        if j.effet not in ("couvre", "a_verifier"):
            continue
        for g in garanties_de.get(j.clause_id, []):
            if g not in touchees and g not in appelees:
                appelees.append(g)
    return appelees[:MAX_APPELEES]


def a_rejuger(precedents: list[jugement.Jugement], attendues: list) -> set[str]:
    """Après les réponses du client, ce que la relecture redemande au modèle (13.4) : les clauses « à vérifier » de la
    lecture précédente, et toutes celles qui bloquent pour leur garantie (sa clause, ses exclusions, les exclusions
    générales) : la réponse peut la faire couvrir, ou appeler une exclusion que rien n'évoquait. Le reste du dossier
    (les autres garanties, déjà jugées sur la même déclaration) garde son jugement. Vide : rien n'était à vérifier,
    la relecture est entière."""
    douteuses = {j.clause_id for j in precedents if j.effet == "a_verifier"}
    touchees = {a.garantie for a in attendues if a.clause_id in douteuses}
    if not touchees:
        return set()
    return douteuses | {a.clause_id for a in attendues if a.bloque and a.garantie in touchees}


def chapitres_des_regles(resultat) -> list[str]:
    """Les garanties que la chaîne de règles a trouvées pour ce sinistre, par l'article qui les accorde (13.2). Le
    modèle ne désigne pas les mêmes chapitres d'une lecture à l'autre (92 clauses au dossier une fois, 290 l'autre,
    7.221) ; les règles, elles, lisent les faits et trouvent les garanties de l'événement de façon stable. Leurs
    articles s'ajoutent à la désignation : un chapitre de trop coûte des tokens, un chapitre de moins une garantie ou
    une exclusion oubliée. Rien si les règles n'ont pas répondu."""
    verdict = getattr(resultat, "verdict", None)
    if verdict is None:
        return []
    return list(dict.fromkeys(c.clause_id for c in verdict.citations if c.valide and c.role == "garantie"))


def message_designation(clauses: list[Clause], declaration: str) -> str:
    """Le message du premier appel : la table des matières d'abord (elle ne change pas d'une déclaration à
    l'autre : le fournisseur la relit depuis son cache), la déclaration à la fin."""
    return f"## Table des matières\n{dossier.table_des_matieres(clauses)}\n\n## Déclaration\n{declaration}"


def message_jugement(pieces: list[Clause], a_juger: set[str], declaration: str,
                     d_abord: frozenset[str] | set[str] = frozenset()) -> str:
    """Le message du second appel : chaque clause du dossier avec son identifiant, son chemin, et la mention
    « à juger » ou « à lire, sans jugement » ; la déclaration à la fin.

    L'ordre sert le cache du fournisseur, qui reprend à moindre prix le début d'un envoi déjà vu : d'abord ce
    qui revient à chaque sinistre du même contrat (`d_abord`, les exclusions générales), puis les garanties
    désignées, puis les définitions que les mots de la déclaration appellent, et la déclaration (7.196)."""
    rang = {c.id: (0 if c.id in d_abord else 2 if dossier.est_definition(c) and c.id not in a_juger else 1)
            for c in pieces}
    blocs = []
    for c in sorted(pieces, key=lambda c: rang[c.id]):          # tri stable : l'ordre du contrat dans chaque rang
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


def lire(base, contrat_id: str, llm: LLM, declaration: str, regles: Decision | Callable | None = None,
         llm_designation: LLM | None = None, garder: bool = False, suivi: Callable | None = None,
         chapitres: list[str] | None = None, renfort: Callable | list | None = None,
         precedents: list[jugement.Jugement] | None = None) -> Lecture:
    """L'analyse d'une déclaration par la lecture des clauses. `regles` : la réponse de la chaîne de règles sur
    la même déclaration, pour la contresignature (rien : la lecture tient seule) ; ou une fonction qui la rend,
    appelée au moment de contresigner, pour que la chaîne tourne pendant la lecture. Une simple décision suffit à
    contresigner ; le résultat entier de la chaîne (avec son verdict) permet en plus la relecture ciblée de ses
    obstacles quand elle ne couvre pas (7.211). `suivi(etape, detail=None)` :
    le fil de l'analyse, comme pour la chaîne de règles (7.201). `chapitres` : ceux d'une lecture précédente du même
    sinistre (la relecture après les réponses du client, 7.218) ; la désignation n'est pas redemandée, et le dossier,
    le même, profite du cache du fournisseur. `renfort` : les chapitres que les règles ont trouvés
    (`chapitres_des_regles`), ou une fonction qui les rend (la chaîne tourne pendant la désignation) ; ils s'ajoutent à
    ceux du modèle (13.2), sauf à la relecture, dont les chapitres sont déjà ceux de la première lecture.
    `precedents` : avec `chapitres`, les jugements de cette lecture précédente ; seules les clauses douteuses et leur
    garantie sont rejugées (`a_rejuger`), les autres reprennent leur jugement (13.4) : moins à juger, moins d'attente."""
    suivre = suivi or (lambda etape, detail=None: None)
    clauses = base.clauses(contrat_id)
    garanties = attendu.garanties(base, contrat_id)
    if not garanties:
        attendu.enregistrer(base, contrat_id)
        garanties = attendu.garanties(base, contrat_id)
    suivre("designation")
    if chapitres:
        designes = list(chapitres)
    else:
        reponse = extraire_json(completer_avec_schema(llm_designation or llm, SYSTEME_DESIGNATION,
                                                      message_designation(clauses, declaration), SCHEMA_DESIGNATION))
        designes = [str(r).strip().strip("[]") for r in reponse.get("chapitres") or []]
    ajoutes: list[str] = []
    if renfort is not None and not chapitres:
        ajoutes = [r for r in (renfort() if callable(renfort) else renfort) if r not in designes]
        designes += ajoutes
    touchees = garanties_touchees(garanties, clauses, designes)
    if not touchees:                                   # rien de désigné : ni refus ni couverture, on le dit
        suivre("designation", "aucun chapitre du contrat ne correspond")
        etat = jugement.Etat(Decision.INCERTAIN, motif="aucun chapitre du contrat n'a été désigné : à examiner")
        return Lecture(etat, designes, [], [], Decision.INCERTAIN, "")
    attendues = [a for g in touchees for a in attendu.attendues(base, contrat_id, g)]
    ids = {a.clause_id for a in attendues}
    # Le dossier envoyé est ce que la table attend, ni plus ni moins : toute clause dont on exigera un jugement
    # est sous les yeux du modèle. S'y ajoutent les définitions que les mots de la déclaration appellent.
    lexique = {c.id for c in dossier.composer(clauses, designes, declaration) if dossier.est_definition(c)}
    pieces = [c for c in clauses if c.id in ids or c.id in lexique]
    a_juger = {a.clause_id for a in attendues if a.bloque}
    generales = {a.clause_id for a in attendues if a.role == "exclusion_generale"}
    suivre("designation", f"{len(touchees)} garantie{'s' * (len(touchees) > 1)} à examiner, "
                          f"{len(pieces)} clauses au dossier" + (" (chapitres de la première lecture)" if chapitres else "")
                          + (f" ; ajoutés d'après les règles : {', '.join(ajoutes)}" if ajoutes else ""))
    suivre("jugement")
    rejugees = sorted(a_rejuger(precedents, attendues) & a_juger) if (precedents and chapitres) else []
    repris_avant: list[jugement.Jugement] = []
    if rejugees:                                       # 13.4 : le reste garde le jugement de la lecture précédente
        repris_avant = [j for j in precedents if j.clause_id not in rejugees]
        a_juger = set(rejugees)
    rendus = jugement.depuis_reponse(extraire_json(completer_avec_schema(
        llm, SYSTEME_JUGEMENT, message_jugement(pieces, a_juger, declaration, generales), SCHEMA_JUGEMENT)))
    gardes, defauts = jugement.controler(rendus, pieces, declaration)
    if rejugees:
        gardes = [j for j in gardes if j.clause_id in a_juger]
    appelees = [] if rejugees else garanties_appelees(base, contrat_id, rendus, touchees)
    if appelees:
        # Le modèle a jugé une clause d'une garantie oubliée : elle entre au dossier avec toutes ses clauses attendues,
        # ses jugements comptent, et ce qui lui manque est redemandé avec les oublis, plus bas (7.245).
        touchees = touchees + appelees
        attendues = [a for g in touchees for a in attendu.attendues(base, contrat_id, g)]
        ids = {a.clause_id for a in attendues}
        pieces = [c for c in clauses if c.id in ids or c.id in lexique]
        a_juger = {a.clause_id for a in attendues if a.bloque}
        gardes, defauts = jugement.controler(rendus, pieces, declaration)
    # La jointure dit ce qui manque ; on le redemande une fois, pour ces clauses seulement (7.194) : un oubli parmi
    # quatre-vingts clauses, ou une citation inexacte, ne doit pas coûter la réponse entière.
    oubliees = a_juger - {j.clause_id for j in gardes}
    relancees: list[str] = []
    if oubliees:
        relancees = sorted(oubliees)
        seconde = [c for c in pieces if c.id in oubliees or c.id in lexique]
        rendus = jugement.depuis_reponse(extraire_json(completer_avec_schema(
            llm, SYSTEME_JUGEMENT, RELANCE + message_jugement(seconde, oubliees, declaration), SCHEMA_JUGEMENT)))
        repris, defauts_repris = jugement.controler(rendus, seconde,
                                                    declaration)
        repris = [j for j in repris if j.clause_id in oubliees]
        rattrapees = {j.clause_id for j in repris}
        defauts = [d for d in defauts if d.split(" ")[0] not in rattrapees] + defauts_repris
        gardes += repris
    jugees = list(gardes)                              # ce que le modèle vient de rendre
    gardes = repris_avant + gardes
    # Une question posée par une clause du règlement du sinistre (le délai de déclaration, un plafond, l'âge du bien
    # pour la vétusté) ne dit pas si le sinistre est couvert : elle devient un rappel, affiché avec la réponse, et
    # la clause compte pour lue (7.203). La consigne le demande déjà ; Large la pose quand même (7.200).
    par_id = {c.id: c for c in pieces}
    rappels = [j for j in gardes if j.effet == "a_verifier" and j.clause_id in par_id
               and dossier.est_reglement(par_id[j.clause_id])]
    gardes = [jugement.Jugement(j.clause_id, "sans_effet") if j in rappels else j for j in gardes]
    effets = [j.effet for j in gardes]
    compte = ", ".join(f"{effets.count(e)} {nom}" for e, nom in (("couvre", "couvrent"), ("exclut", "excluent"),
                       ("limite", "limitent"), ("a_verifier", "à vérifier")) if effets.count(e))
    suivre("jugement", (f"{len(jugees)} clauses rejugées après les réponses, {len(repris_avant)} reprises de la lecture "
                        "précédente" if rejugees else f"{len(gardes)} clauses jugées") + (f" : {compte}" if compte else "")
           + (f" ; {len(relancees)} redemandée{'s' * (len(relancees) > 1)}" if relancees else ""))
    lignes, non_attendus = jugement.joindre(base, contrat_id, touchees, gardes)
    options = {"optionnelles": {g.repere for g in garanties if g.optionnelle}, "non_attendus": non_attendus,
               "defauts": defauts, "chemins": {g.repere: g.chemin for g in garanties},
               "sans_couverture": {g.repere for g in garanties if not g.porte_garantie and not g.optionnelle}}
    etat = jugement.decider(lignes, **options)
    # Les questions dont aucune réponse ne changerait la décision ne sont pas posées (7.220).
    etat = jugement.questions_utiles(lignes, etat, **options)
    if callable(regles):                               # avant « décider » : le suivi reste dans l'ordre (7.202)
        regles = regles()
    resultat_regles = regles if hasattr(regles, "verdict") else None
    if resultat_regles is not None:                    # le résultat entier de la chaîne : sa décision, ses obstacles
        regles = resultat_regles.verdict.decision
    decision, desaccord = jugement.arbitrer(etat, regles)
    revue: list[str] = []
    obstacles = obstacles_des_regles(resultat_regles)
    if (etat.decision == Decision.COUVERT and decision == Decision.INCERTAIN and regles is not None
            and 0 < len(obstacles) <= MAX_OBSTACLES):
        # La lecture couvre, les règles non, et elles disent pourquoi : on relit ces seuls obstacles (7.211). Le
        # « couvert » ne tient que si la déclaration écarte chacun d'eux, citation exacte à l'appui.
        par_tout = {c.id: c for c in clauses}
        tient, revue = arbitrage_cible(llm, obstacles, par_tout, regles, declaration)
        if tient:
            decision = Decision.COUVERT
            desaccord = (f"les règles traduites répondaient « {jugement.DITE[regles]} » ; relus un à un, leurs obstacles sont "
                         "écartés par la déclaration")
    suivre("decision")
    suivre("decision", etat.motif + (f" ; {desaccord}" if desaccord else ""))
    if garder:                                         # les jugements en table, pour relire l'analyse après coup
        jugement.garder(base, contrat_id, declaration, gardes, etat, decision)
    # Gardés pour la relecture suivante (13.4) : une question du règlement y est déjà « sans effet », elle ne fait pas
    # rejuger sa garantie.
    return Lecture(etat, designes, touchees, pieces, decision, desaccord, relancees, rappels, revue, ajoutes,
                   gardes, rejugees, appelees)
