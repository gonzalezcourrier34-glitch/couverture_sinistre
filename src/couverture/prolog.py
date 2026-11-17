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

from .juges import extraire_json
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
    corps = ", ".join(["set_stream(user_output, encoding(utf8))", *charges, "retractall(fait(_, _))", *poses, point])
    return f"catch(({corps}), E, (print_message(error, E), halt(2)))"


def executer(contrat_id: str, point: str, faits: dict | None = None, delai: int = 30):
    """Lance SWI-Prolog sur le moteur et les règles du contrat ; renvoie le JSON écrit par `point`.
    Un avertissement au chargement (erreur de syntaxe, variable isolée…) est une erreur : des règles
    qui se chargent mal ne décident pas."""
    exe = swipl()
    if exe is None:
        raise ErreurRegles("SWI-Prolog introuvable. Windows : `winget install SWI-Prolog.SWI-Prolog`, "
                           "ou indiquer son chemin dans COUVERTURE_SWIPL.")
    regles = fichier_regles(contrat_id)
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

Règles :
- N'utilise que les variables et les valeurs de la liste. Une variable marquée « plusieurs » prend une liste ; les autres, une seule valeur.
- Ne renseigne une variable que si la déclaration le dit ou l'implique clairement. Sinon, ne la mets pas : elle restera inconnue. N'invente rien.
- « fermé à clé » sans autre précision : fermeture = cle, et ne renseigne pas serrure_surete.
- Une pièce ou une partie du logement (salon, cuisine, entrée, « chez moi ») : lieu = logement.
- « Avec la chaleur » sans flamme décrite : flammes = non.
- Des flammes qui brûlent ou se propagent à d'autres objets : flammes = oui et embrasement = oui.
- Façade, murs, parquet, toiture : bien = element_batiment. Tuyau, canalisation : bien = canalisation.
- vol_sur_personne = oui seulement si le bien a été pris sur la personne (arraché, dérobé sur soi).

Réponds uniquement par un objet JSON : {"faits": {"evenement": "vol", "bien": ["velo"], "lieu": ["cave"]}}"""


def extraire_faits_regles(sinistre: str, llm: LLM) -> tuple[dict, list[str]]:
    """Les faits lus par le modèle, et les écarts au vocabulaire (retirés)."""
    voc = vocabulaire()
    liste = "\n".join(f"- {v}{' (plusieurs)' if d.get('plusieurs') else ''} : {', '.join(d['valeurs'])}"
                      for v, d in voc.items())
    message = f"## Vocabulaire\n{liste}\n\n## Déclaration\n{sinistre}"
    donnees = extraire_json(llm.completer(SYSTEME_FAITS_REGLES, message))
    faits, ecarts = {}, []
    for v, x in (donnees.get("faits") or {}).items():
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
    return faits, ecarts


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
        if d.get("aucune"):
            motif = "Non couvert : aucune garantie ne s'applique."
        else:
            motif = {"COUVERT": "Couvert. ", "NON_COUVERT": "Non couvert. ", "INCERTAIN": "À préciser. "}[decision.value] \
                + " ; ".join(motifs[:3]) + "."
        vars_ = list(dict.fromkeys(v for r in retenues for v in r.get("questions", []) + r.get("reserves", [])))
        if decision == Decision.NON_COUVERT:
            vars_ += [v for r in possibles for v in r.get("questions", [])]
        demander = list(dict.fromkeys(question(v) for v in vars_))
        confiance = {"COUVERT": 0.85, "NON_COUVERT": 0.85, "INCERTAIN": 0.4}[decision.value]
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
                    informations_manquantes=demander, confiance=confiance, mode=f"regles:{self.llm.nom}+prolog")
        return v, consultees


def faits_lisibles(faits: dict) -> Faits:
    def liste(v):
        x = faits.get(v)
        return [] if x is None else (x if isinstance(x, list) else [x])

    autres = [f"{v}={x}" for v, x in faits.items() if v not in ("evenement", "bien", "lieu")]
    return Faits(evenements=liste("evenement"), biens=liste("bien"), lieux=liste("lieu"), circonstances=autres)
