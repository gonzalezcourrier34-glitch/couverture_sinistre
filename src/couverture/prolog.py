"""Méthode « regles » : le contrat en règles Prolog, un modèle qui lit les faits, un moteur qui décide.

    déclaration ─► Mistral (rapide) : faits dans le vocabulaire commun (regles/vocabulaire.json)
                ─► SWI-Prolog : regles/moteur.pl + regles/<contrat>.pl ─► décision, preuves, questions

Le modèle ne décide rien et ne cite rien : il traduit la déclaration en une dizaine de faits
(« lieu = parties_communes », « effraction = oui »), et laisse inconnu ce que la déclaration ne
dit pas. La décision est un calcul logique, reproductible, et chaque preuve est une phrase du
contrat écrite dans la règle (vérifiée par `couverture regles`).

SWI-Prolog (gratuit, licence BSD) est appelé en sous-processus : `swipl` dans le PATH, ou
COUVERTURE_SWIPL, ou l'emplacement d'installation habituel sous Windows.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from .llm import completer_avec_schema, extraire_json
from .llm import LLM, ErreurLLM
from .models import Citation, Clause, ClauseRetenue, Condition, Decision, EtatCondition, Faits, Resultat, Verdict
from .validation import valider

RACINE = Path(__file__).resolve().parents[2]
DOSSIER = RACINE / "regles"
MOTEUR = DOSSIER / "moteur.pl"
EMPLACEMENTS = [r"C:\Program Files\swipl\bin\swipl.exe", "/usr/bin/swipl", "/usr/local/bin/swipl",
                "/opt/homebrew/bin/swipl", "/Applications/SWI-Prolog.app/Contents/MacOS/swipl"]
ATOME = re.compile(r"^[a-z][a-z0-9_]*$")


class ErreurRegles(RuntimeError):
    """SWI-Prolog absent, règles qui ne se chargent pas, ou faits hors du vocabulaire."""


def swipl() -> str | None:
    for candidat in [os.environ.get("COUVERTURE_SWIPL"), shutil.which("swipl"), *EMPLACEMENTS]:
        if candidat and Path(candidat).exists():
            return candidat
    return None


def fichier_regles(contrat_id: str) -> Path:
    return DOSSIER / f"{contrat_id}.pl"


def vocabulaire() -> dict:
    return json.loads((DOSSIER / "vocabulaire.json").read_text(encoding="utf-8"))["variables"]


def hierarchie(voc: dict | None = None) -> list[tuple[str, str, str]]:
    """(variable, valeur, parent) : la hiérarchie du vocabulaire (« parents »), posée en faits pour le moteur.
    Une vitre est un élément du bâtiment : une règle large reconnaît le fait précis, et un fait vague ne
    tranche pas pour une règle précise (le moteur répond « inconnu » et pose la question)."""
    voc = voc or vocabulaire()
    return [(v, x, p) for v, d in voc.items() for x, ps in d.get("parents", {}).items() for p in ps]


def filtrer_faits(faits: dict, voc: dict | None = None) -> tuple[dict, list[str]]:
    """Retire les faits hors sujet : une variable qui déclare les événements auxquels elle s'applique
    (« pour ») n'est gardée que si l'un d'eux est lu. Une cause d'eau pour une bougie, des travaux pour
    un vol : le modèle les invente, le code les retire, quelle que soit la consigne. Sans événement
    lu, on ne peut pas juger : tout est gardé."""
    voc = voc or vocabulaire()
    ev = faits.get("evenement")
    evenements = set(ev if isinstance(ev, list) else [ev]) if ev else set()
    if not evenements:
        return dict(faits), []
    gardes, retires = {}, []
    for v, x in faits.items():
        pour = voc.get(v, {}).get("pour")
        if pour and not evenements & set(pour):
            retires.append(f"{v} = {x if not isinstance(x, list) else '/'.join(x)} : hors sujet pour "
                           f"{'/'.join(sorted(evenements))}, retiré")
        else:
            gardes[v] = x
    return gardes, retires


def verifier_faits(faits: dict) -> list[str]:
    """Les écarts au vocabulaire : variable inconnue, valeur non permise, plusieurs valeurs interdites."""
    voc, problemes = vocabulaire(), []
    for v, x in faits.items():
        if v not in voc:
            problemes.append(f"variable inconnue : {v}")
            continue
        valeurs = x if isinstance(x, list) else [x]
        if len(valeurs) > 1 and not voc[v].get("plusieurs"):
            problemes.append(f"{v} n'admet qu'une valeur : {valeurs}")
        problemes += [f"{v} = {val} : valeur non permise" for val in valeurs if val not in voc[v]["valeurs"]]
    return problemes


def atome_chemin(chemin: Path) -> str:
    """Un chemin en atome Prolog : barres obliques (acceptées par SWI-Prolog sous Windows, et sans le
    piège des « \\ » dans un atome), apostrophes échappées."""
    return "'" + Path(chemin).resolve().as_posix().replace("\\", "/").replace("'", "\\'") + "'"


def but(faits: dict, point: str = "decider_json", fichiers: tuple = ()) -> str:
    """Le but Prolog : charger le moteur et les règles, poser les faits, appeler le point d'entrée.
    Les noms sont vérifiés (atomes simples du vocabulaire), donc rien ne peut être injecté. Les
    fichiers sont chargés par `consult` dans le but plutôt que passés en arguments : selon les
    versions, SWI-Prolog prend le premier fichier pour un script et les suivants pour ses arguments."""
    charges = [f"consult({atome_chemin(f)})" for f in fichiers]
    poses = []
    for v, x in faits.items():
        for val in (x if isinstance(x, list) else [x]):
            if not (ATOME.match(str(v)) and ATOME.match(str(val))):
                raise ErreurRegles(f"fait mal formé : {v} = {val}")
            poses.append(f"assertz(fait({v}, {val}))")
    for v, x, p in hierarchie():
        if not all(ATOME.match(str(t)) for t in (v, x, p)):
            raise ErreurRegles(f"hiérarchie mal formée : {v} {x} {p}")
        poses.append(f"assertz(parent_valeur({v}, {x}, {p}))")
    if point == "decider_json":
        # Les valeurs possibles de chaque variable, pour le raisonnement par hypothèses (moteur.pl).
        poses.append(f"charger_domaines({atome_chemin(DOSSIER / 'vocabulaire.json')})")
    corps = ", ".join(["set_stream(user_output, encoding(utf8))", *charges, "retractall(fait(_, _))",
                       "retractall(parent_valeur(_, _, _))", *poses, point])
    return f"catch(({corps}), E, (print_message(error, E), halt(2)))"


def executer(contrat_id: str, point: str, faits: dict | None = None, delai: int = 30, regles: Path | None = None):
    """Lance SWI-Prolog sur le moteur et les règles du contrat ; renvoie le JSON écrit par `point`.
    Un avertissement au chargement (erreur de syntaxe, variable isolée…) est une erreur : des règles
    qui se chargent mal ne décident pas."""
    exe = swipl()
    if exe is None:
        raise ErreurRegles("SWI-Prolog introuvable. Windows : `winget install SWI-Prolog.SWI-Prolog`, "
                           "ou indiquer son chemin dans COUVERTURE_SWIPL.")
    regles = regles or fichier_regles(contrat_id)   # `regles` : un autre fichier (règles proposées, fusionnées)
    if not regles.exists():
        raise ErreurRegles(f"Pas de règles pour {contrat_id} : {regles} est absent.")
    commande = [exe, "-q", "-g", but(faits or {}, point, (MOTEUR, regles)), "-t", "halt"]
    try:
        p = subprocess.run(commande, capture_output=True, timeout=delai)
    except subprocess.TimeoutExpired as e:
        raise ErreurRegles(f"SWI-Prolog n'a pas répondu en {delai} s.") from e
    sortie = p.stdout.decode("utf-8", "replace").strip()
    erreurs = p.stderr.decode("utf-8", "replace").strip()
    if p.returncode != 0 or "Warning" in erreurs or "ERROR" in erreurs or not sortie:
        raise ErreurRegles(f"SWI-Prolog ({p.returncode}) : {erreurs or sortie or 'aucune sortie'}")
    return json.loads(sortie.splitlines()[-1])


def decider(contrat_id: str, faits: dict) -> dict:
    return executer(contrat_id, "decider_json", faits)


# --- Lecture des faits par le modèle -------------------------------------------------------------------

SYSTEME_FAITS_REGLES = """Tu lis la déclaration d'un sinistre et tu la traduis en faits, avec un vocabulaire imposé. Tu ne décides pas si le sinistre est couvert.

Le vocabulaire donne, pour chaque variable, la question à laquelle elle répond, ses valeurs, et le sens des valeurs proches. Choisis la valeur dont le sens correspond à ce qui est écrit.

Règles :
- N'utilise que les variables et les valeurs de la liste. Une variable marquée « plusieurs » prend une liste ; les autres, une seule valeur.
- Ne renseigne une variable que si la déclaration la dit ou l'implique clairement. Sinon, ne la mets pas : elle restera inconnue, et le gestionnaire posera la question. Un fait inventé est plus grave qu'un fait manquant.
- Un lieu se déduit de ce qui est écrit : une pièce ou une partie du logement (salon, cuisine, salle de bain, entrée, parquet, plafond, « chez moi », « mon appartement ») donne lieu = logement. Mais ce qui ne dit rien de l'endroit ne donne pas de lieu : « pendant que je faisais mes courses » ne dit pas où était le vélo.
- N'ajoute jamais une absence, des portes ou des fenêtres fermées, un auteur ou une cause qui ne sont pas écrits.
- « Disparu », « je ne retrouve plus » ne disent pas qu'il y a eu vol : ne mets evenement = vol que si un vol est décrit (volé, pris, cambriolé, arraché).
- Ne renseigne pas une variable sans rapport avec ce qui s'est passé (une cause d'eau pour un vol, des travaux pour un incendie).
- evenement : la cause, et aussi le dommage s'il est d'une autre nature. Une tempête qui arrache des tuiles et fait entrer la pluie : ["tempete", "degat_eaux"]. Ne perds jamais la cause, même si aucune valeur ne la nomme exactement : prends la plus proche par son sens, ou « autre ».
- « fermé à clé » sans autre précision : fermeture = cle, et ne renseigne pas serrure_surete.
- Des flammes qui brûlent ou se propagent à d'autres objets : flammes = oui et embrasement = oui. « Avec la chaleur » sans flamme décrite : flammes = non.
- Façade, murs, parquet, plafond, toiture : bien = element_batiment. Tuyau, canalisation : bien = canalisation.
- vol_sur_personne = oui seulement si le bien a été pris sur la personne (arraché, dérobé sur soi).
- Une durée dite se traduit : déposé « il y a deux semaines » donne depot_moins_30j = oui.
- Les précautions décrites se traduisent : une fenêtre laissée ouverte donne fenetres_fermees = non ; un chauffage coupé pendant le gel, sans vidange ni isolation, donne prevention_gel = non.

Réponds uniquement par un objet JSON : {"faits": {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"]}}"""


# --- Lecture en deux temps (DEMARCHE 7.38) ----------------------------------------------------------------
#  Avec tout le vocabulaire d'un coup, Mistral Small oubliait des faits à mesure que la liste s'allongeait
#  (7.32). Temps 1 : ce qui s'est passé, quoi, où. Temps 2 : seulement les questions qui concernent cet
#  événement (« pour » dans le vocabulaire). Chaque règle de la consigne v4 est dans l'un des deux temps.

SOCLE = ("evenement", "bien", "lieu")

REGLES_COMMUNES = """- N'utilise que les variables et les valeurs de la liste. Une variable marquée « plusieurs » prend une liste ; les autres, une seule valeur.
- Ne renseigne une variable que si la déclaration la dit ou l'implique clairement. Sinon, mets null (ou une liste vide) : elle restera inconnue, et le gestionnaire posera la question. Un fait inventé est plus grave qu'un fait manquant."""

SYSTEME_LECTURE_SOCLE = """Tu lis la déclaration d'un sinistre et tu dis ce qui s'est passé, ce qui est touché et où, avec un vocabulaire imposé. Tu ne décides pas si le sinistre est couvert.

Le vocabulaire donne, pour chaque variable, la question à laquelle elle répond, ses valeurs, et le sens des valeurs proches. Choisis la valeur dont le sens correspond à ce qui est écrit.

Règles :
""" + REGLES_COMMUNES + """
- evenement : la cause, et aussi le dommage s'il est d'une autre nature. Une tempête qui arrache des tuiles et fait entrer la pluie : ["tempete", "degat_eaux"]. Ne perds jamais la cause, même si aucune valeur ne la nomme exactement : prends la plus proche par son sens, ou « autre ».
- « Disparu », « je ne retrouve plus » ne disent pas qu'il y a eu vol : ne mets evenement = vol que si un vol est décrit (volé, pris, cambriolé, arraché).
- Un lieu se déduit de ce qui est écrit : une pièce ou une partie du logement (salon, cuisine, salle de bain, entrée, parquet, plafond, « chez moi », « mon appartement ») donne lieu = logement. Mais ce qui ne dit rien de l'endroit ne donne pas de lieu : « pendant que je faisais mes courses » ne dit pas où était le vélo.
- Façade, murs, parquet, plafond, toiture : bien = element_batiment. Tuyau, canalisation : bien = canalisation.

Réponds uniquement par un objet JSON : {"faits": {"evenement": ["vol"], "bien": ["velo"], "lieu": ["cave"]}}"""

SYSTEME_LECTURE_DETAILS = """Tu lis la déclaration d'un sinistre et tu réponds à quelques questions précises, avec un vocabulaire imposé. Ce qui s'est passé, ce qui est touché et où sont déjà établis : ne les répète pas. Tu ne décides pas si le sinistre est couvert.

Le vocabulaire donne, pour chaque variable, la question à laquelle elle répond, ses valeurs, et le sens des valeurs proches. Choisis la valeur dont le sens correspond à ce qui est écrit.

Règles :
""" + REGLES_COMMUNES + """
- N'ajoute jamais une absence, des portes ou des fenêtres fermées, un auteur ou une cause qui ne sont pas écrits.
- Ne renseigne pas une variable sans rapport avec ce qui s'est passé.
- « fermé à clé » sans autre précision : fermeture = cle, et ne renseigne pas serrure_surete.
- Des flammes qui brûlent ou se propagent à d'autres objets : flammes = oui et embrasement = oui. « Avec la chaleur » sans flamme décrite : flammes = non.
- vol_sur_personne = oui seulement si le bien a été pris sur la personne (arraché, dérobé sur soi).
- Une durée dite se traduit : déposé « il y a deux semaines » donne depot_moins_30j = oui.
- Les précautions décrites se traduisent : une fenêtre laissée ouverte donne fenetres_fermees = non ; un chauffage coupé pendant le gel, sans vidange ni isolation, donne prevention_gel = non.

Réponds uniquement par un objet JSON : {"faits": {"variable": "valeur"}}"""


def schema_faits(variables: dict) -> dict:
    """Le schéma JSON de la réponse : chaque variable avec ses seules valeurs permises (listes fermées).
    Toutes sont présentes (null ou liste vide si inconnues) : la forme stricte l'exige."""
    proprietes = {}
    for v, d in variables.items():
        if d.get("plusieurs"):
            proprietes[v] = {"type": "array", "items": {"type": "string", "enum": list(d["valeurs"])}}
        else:
            proprietes[v] = {"type": ["string", "null"], "enum": list(d["valeurs"]) + [None]}
    return {"type": "object", "additionalProperties": False, "required": ["faits"],
            "properties": {"faits": {"type": "object", "additionalProperties": False,
                                     "required": list(proprietes), "properties": proprietes}}}


def mode_lecture() -> str:
    """COUVERTURE_LECTURE=un_temps garde la lecture d'avant (consigne v4, tout le vocabulaire), pour comparer."""
    return "un_temps" if os.environ.get("COUVERTURE_LECTURE", "").strip().lower() == "un_temps" else "deux_temps"


def _lire(llm: LLM, systeme: str, variables: dict, message: str) -> dict:
    liste = "\n".join(description_variable(v, d) for v, d in variables.items())
    texte = completer_avec_schema(llm, systeme, f"## Vocabulaire\n{liste}\n\n{message}", schema_faits(variables))
    return extraire_json(texte).get("faits") or {}


def variables_du_temps_2(voc: dict, evenements: list[str]) -> dict:
    """Les variables à demander une fois l'événement connu : celles qui s'y appliquent (« pour »), et celles
    qui s'appliquent à tout. Sans événement lu, toutes."""
    ev = set(evenements)
    return {v: d for v, d in voc.items() if v not in SOCLE and (not ev or not d.get("pour") or ev & set(d["pour"]))}


def extraire_faits_regles(sinistre: str, llm: LLM) -> tuple[dict, list[str]]:
    """Les faits lus par le modèle, et les écarts au vocabulaire (retirés)."""
    voc = vocabulaire()
    declaration = f"## Déclaration\n{sinistre}"
    if mode_lecture() == "un_temps":
        lus = _lire(llm, SYSTEME_FAITS_REGLES, voc, declaration)
    else:
        lus = _lire(llm, SYSTEME_LECTURE_SOCLE, {v: voc[v] for v in SOCLE}, declaration)
        evenements = [str(e) for e in (lus.get("evenement") or []) if str(e) in voc["evenement"]["valeurs"]]
        details = variables_du_temps_2(voc, evenements)
        if details:
            etabli = "; ".join(f"{v} = {'/'.join(map(str, x)) if isinstance(x, list) else x}"
                               for v, x in lus.items() if x not in (None, "", []))
            lus |= {v: x for v, x in _lire(llm, SYSTEME_LECTURE_DETAILS, details,
                                           f"## Déjà établi\n{etabli or 'rien'}\n\n{declaration}").items()
                    if v not in SOCLE}
    faits, ecarts = {}, []
    for v, x in lus.items():
        if x in (None, "", []):
            continue
        valeurs = [str(e) for e in (x if isinstance(x, list) else [x])]
        if v not in voc:
            ecarts.append(f"variable inconnue ignorée : {v}")
            continue
        bonnes = [e for e in valeurs if e in voc[v]["valeurs"]]
        ecarts += [f"{v} = {e} : valeur hors vocabulaire, ignorée" for e in valeurs if e not in bonnes]
        if bonnes:
            faits[v] = bonnes if voc[v].get("plusieurs") else bonnes[0]
    faits, retires = filtrer_faits(faits, voc)
    return faits, ecarts + retires


def description_variable(v: str, d: dict) -> str:
    """Une ligne de vocabulaire pour le modèle : la question, les valeurs, le sens des valeurs proches."""
    aide = d.get("aide", {})
    valeurs = ", ".join(f"{x} ({aide[x]})" if x in aide else x for x in d["valeurs"])
    return f"- {v}{' (plusieurs)' if d.get('plusieurs') else ''} — {d.get('question', '')} : {valeurs}"


# --- La méthode ------------------------------------------------------------------------------------------

def question(variable: str) -> str:
    if variable == "lien_causal":
        return "Le non-respect de l'obligation de prévention a-t-il permis ou facilité le sinistre ?"
    return vocabulaire().get(variable, {}).get("question", f"Préciser : {variable}")


class PipelineRegles:
    methode = "regles"

    def __init__(self, contrat_id: str, clauses: list[Clause], llm: LLM, decideur=None):
        """`decideur(faits) -> dict` : par défaut SWI-Prolog ; remplaçable dans les tests."""
        self.contrat_id, self.clauses, self.llm = contrat_id, clauses, llm
        self.decideur = decideur or (lambda faits: decider(contrat_id, faits))

    @classmethod
    def depuis_base(cls, base, contrat_id: str, llm: LLM) -> "PipelineRegles":
        if not fichier_regles(contrat_id).exists():
            raise LookupError(f"Pas de règles Prolog pour {contrat_id} (regles/{contrat_id}.pl).")
        if swipl() is None:
            raise LookupError("SWI-Prolog introuvable : `winget install SWI-Prolog.SWI-Prolog` (Windows).")
        return cls(contrat_id, base.clauses(contrat_id), llm)

    def analyser(self, sinistre: str) -> Resultat:
        try:
            faits, ecarts = extraire_faits_regles(sinistre, self.llm)
        except ErreurLLM:
            raise
        except Exception as e:  # noqa: BLE001
            v = Verdict(decision=Decision.INCERTAIN, justification="Le modèle n'a pas pu lire la déclaration.",
                        confiance=0.0, mode=f"regles:{self.llm.nom}", avertissements=[str(e)])
            return Resultat(sinistre=sinistre, contrat_id=self.contrat_id, methode=self.methode, faits=Faits(),
                            clauses_consultees=[], verdict=v)
        d = self.decideur(faits)
        verdict, consultees = self.verdict(d, faits)
        verdict.avertissements = ecarts + verdict.avertissements
        verdict = valider(verdict, consultees)
        return Resultat(sinistre=sinistre, contrat_id=self.contrat_id, methode=self.methode,
                        faits=faits_lisibles(faits), clauses_consultees=consultees, verdict=verdict)

    def verdict(self, d: dict, faits: dict) -> tuple[Verdict, list[ClauseRetenue]]:
        decision = Decision(d["decision"])
        retenues, possibles = d.get("retenues", []), d.get("possibles", [])
        motifs = [f"« {r['garantie']} » ({r['article']}) : {r['motif']}" for r in retenues]
        non_traduits = d.get("non_traduits") or []
        if d.get("aucune"):
            motif = "Non couvert : aucune garantie ne s'applique."
        else:
            motif = {"COUVERT": "Couvert. ", "NON_COUVERT": "Non couvert. ", "INCERTAIN": "À préciser. "}[decision.value] \
                + " ; ".join(motifs[:3]) + "."
        if non_traduits:
            evts = ", ".join(non_traduits)
            motif = (f"À examiner par un gestionnaire : l'événement « {evts} » relève d'une garantie qui n'est pas "
                     f"encore traduite en règles. Ce que disent les garanties traduites : " + (" ; ".join(motifs[:3]) or "rien") + ".")
        vars_ = list(dict.fromkeys(v for r in retenues for v in r.get("questions", []) + r.get("reserves", [])))
        if decision == Decision.NON_COUVERT:
            vars_ += [v for r in possibles for v in r.get("questions", [])]
        demander = list(dict.fromkeys(question(v) for v in vars_))
        exploration = d.get("exploration")
        if exploration:
            demander, motif = questions_explorees(exploration, vars_, motif)
        confiance = {"COUVERT": 0.85, "NON_COUVERT": 0.85, "INCERTAIN": 0.4}[decision.value]
        if non_traduits:
            confiance = 0.3
        if decision == Decision.COUVERT and any(r.get("reserves") for r in retenues):
            confiance = 0.7
        if decision == Decision.NON_COUVERT and demander:
            confiance = 0.6

        index = {c.id: c for c in self.clauses}
        preuves = [p for r in (retenues if not d.get("aucune") else retenues[:3]) for p in r.get("preuves", [])
                   + r.get("partielles", [])]
        conditions, vus = [], set()
        for p in preuves:
            cle = (p["article"], p["texte"])
            if cle in vus:
                continue
            vus.add(cle)
            nature = "exclusion" if "exclusion" in p["role"] else "limite" if p["role"] == "limite" else "garantie"
            conditions.append(Condition(nature=nature, groupe=p["role"], clause_id=p["article"], extrait=p["texte"],
                                        enonce=p["role"].capitalize() + (f" (sauf {p['bien']})" if p.get("bien") else ""),
                                        etat=EtatCondition.REMPLIE, decisive=True,
                                        pages=index[p["article"]].pages if p["article"] in index else []))
        for r in retenues:
            for lim in r.get("limites", []):
                conditions.append(Condition(nature="limite", groupe="Limites", clause_id=lim["article"],
                                            extrait=lim["texte"], enonce=f"{lim['montant']}", etat=EtatCondition.REMPLIE))
        citations = [Citation(clause_id=c.clause_id, extrait=c.extrait, role=c.nature, pages=c.pages)
                     for c in conditions if c.nature != "limite"]
        consultees = [ClauseRetenue(clause=index[i], score=0.0, raison="règle")
                      for i in dict.fromkeys(c.clause_id for c in conditions) if i in index]
        v = Verdict(decision=decision, justification=motif, citations=citations, conditions=conditions,
                    informations_manquantes=demander, confiance=confiance, mode=f"regles:{self.llm.nom}+prolog",
                    preuve=d.get("preuve", []), raisonnement=arbre_lisible(d.get("preuve", [])))
        return v, consultees


# --- Arbre de preuve, en lignes lisibles --------------------------------------------------------------

MARQUE = {"oui": "[oui]", "non": "[non]", "inconnu": "[ ? ]"}


def _vu(n: dict) -> str:
    return f"déclaré : {', '.join(n['declare'])}" if n["declare"] else "non déclaré"


def _condition(n: dict, prof: int, lignes: list[str], complet: bool, cites: set) -> None:
    """Une condition et ses sous-conditions, élaguée : d'un « ou » vrai, la branche vraie ; d'un « et »
    faux, les branches fausses ; un « si » dont la prémisse est fausse est sans objet. Ce qui a décidé
    reste, le reste se compte. Le texte d'une définition n'est cité qu'une fois."""
    ind, m, t = "  " * prof, MARQUE[n["etat"]], n["type"]
    enfants = n["enfants"]
    if t == "fait":
        lignes.append(f"{ind}{m} {n['variable']} = {n['attendu']} ({_vu(n)})")
    elif t in ("vrai", "faux"):
        lignes.append(f"{ind}{m} {t}")
    elif t == "concept":
        texte = "" if n["nom"] in cites and not complet else f" : « {n['texte']} »"
        cites.add(n["nom"])
        lignes.append(f"{ind}{m} {n['nom']} (art. {n['article']}{texte})")
        _condition(enfants[0], prof + 1, lignes, complet, cites)
    elif t == "non":
        lignes.append(f"{ind}{m} pas :")
        _condition(enfants[0], prof + 1, lignes, complet, cites)
    elif t == "si" and enfants[0]["etat"] == "non" and not complet:
        lignes.append(f"{ind}{m} sans objet ici :")
        _condition(enfants[0], prof + 1, lignes, complet, cites)
    elif t == "si":
        lignes.append(f"{ind}{m} si … alors … :")
        for e in enfants:
            _condition(e, prof + 1, lignes, complet, cites)
    elif t == "ou" and all(e["type"] == "fait" for e in enfants) and len({e["variable"] for e in enfants}) == 1:
        lignes.append(f"{ind}{m} {enfants[0]['variable']} parmi {', '.join(e['attendu'] for e in enfants)} ({_vu(enfants[0])})")
    else:
        garder = {("ou", "oui"): "oui", ("et", "non"): "non"}.get((t, n["etat"]))
        montres = enfants if complet or garder is None else [e for e in enfants if e["etat"] == garder]
        lignes.append(f"{ind}{m} {'toutes' if t == 'et' else 'l’une'} de :")
        for e in montres:
            _condition(e, prof + 1, lignes, complet, cites)
        if len(montres) < len(enfants):
            lignes.append(f"{ind}  … {len(enfants) - len(montres)} autre(s), sans effet sur la conclusion")


SENS = {
    "périmètre": ("Périmètre", {"oui": "établi", "non": "non établi", "inconnu": "inconnu"}),
    "condition": ("Condition", {"oui": "remplie", "non": "non remplie", "inconnu": "inconnue"}),
    "obligation": ("Obligation", {"oui": "respectée", "non": "non respectée", "inconnu": "à vérifier"}),
    "exclusion": ("Exclusion", {"oui": "s'applique", "non": "ne s'applique pas", "inconnu": "à établir"}),
}


def arbre_lisible(preuve: list[dict], complet: bool = False) -> list[str]:
    """L'arbre de preuve du moteur (moteur.pl, arbres_de_preuve/2) en lignes : la garantie, puis chaque nœud avec
    sa phrase du contrat et son état, jusqu'aux faits déclarés. Sans `complet`, les exclusions qui ne
    jouent pas, et celles que l'assureur devrait prouver sans que la déclaration les évoque, sont
    comptées au lieu d'être listées."""
    lignes: list[str] = []
    for g in preuve:
        lignes.append(f"Garantie « {g['nom']} » (art. {g['article']}) → {ISSUE.get(g['decision'], g['decision'])}")
        cites: set = set()
        ecartees, presumees = 0, []
        for n in g["enfants"]:
            if n["type"] == "exclusion" and not complet:
                if n["etat"] == "non":
                    ecartees += 1
                    continue
                if n["etat"] == "inconnu" and n.get("a_demander") == "non":
                    presumees.append(n["article"])
                    continue
            role, sens = SENS[n["type"]]
            phrase = f" — art. {n['article']} : « {n['texte']} »" if n.get("article") else ""
            lignes.append(f"  {MARQUE[n['etat']]} {role} {sens[n['etat']]}{phrase}")
            for e in n["enfants"]:
                _condition(e, 3, lignes, complet, cites)
            if n["type"] == "obligation" and n["exception"]["etat"] == "oui":
                lignes.append("      sans incidence ici :")
                _condition(n["exception"], 4, lignes, complet, cites)
        if ecartees:
            lignes.append(f"  {ecartees} exclusion(s) examinée(s) : aucune ne s'applique")
        if presumees:
            arts = ", ".join(dict.fromkeys(presumees))
            lignes.append(f"  {len(presumees)} exclusion(s) que la déclaration n'évoque pas (art. {arts}) : "
                          "l'assureur devrait les prouver, elles ne changent pas la réponse")
    return lignes


ISSUE = {"COUVERT": "couvert", "NON_COUVERT": "non couvert", "INCERTAIN": "encore incertain", "ERREUR": "?"}


def questions_explorees(exploration: dict, vars_: list[str], motif: str) -> tuple[list[str], str]:
    """Les questions classées par le raisonnement par hypothèses du moteur (moteur.pl, explorer/2) :
    décisives d'abord, avec ce que chaque réponse entraîne ; les inutiles ne sont pas posées.
    Les questions sans domaine (le lien de causalité, une appréciation) sont gardées telles quelles."""
    explorees = {q["variable"]: q for q in exploration.get("questions", [])}
    lignes = []
    for q in exploration.get("questions", []):
        if q["effet"] == "inutile":
            continue
        texte = question(q["variable"])
        if q["effet"] == "décisive":
            issues = " ; ".join(f"{'/'.join(i['valeurs'][:4])}{'…' if len(i['valeurs']) > 4 else ''} → {ISSUE[i['decision']]}"
                                for i in q["issues"])
            texte += f" ({issues})"
        lignes.append(texte)
    lignes += [question(v) for v in vars_ if v not in explorees]
    ensemble = exploration.get("ensemble") or []
    if ensemble:
        motif += (" Une seule question tranche : " if len(ensemble) == 1 else " Ces deux questions tranchent : ") \
            + " ; ".join(f"« {question(v)} »" for v in ensemble) + "."
    return list(dict.fromkeys(lignes)), motif


def faits_lisibles(faits: dict) -> Faits:
    def liste(v):
        x = faits.get(v)
        return [] if x is None else (x if isinstance(x, list) else [x])

    autres = [f"{v}={x}" for v, x in faits.items() if v not in ("evenement", "bien", "lieu")]
    return Faits(evenements=liste("evenement"), biens=liste("bien"), lieux=liste("lieu"), circonstances=autres)
