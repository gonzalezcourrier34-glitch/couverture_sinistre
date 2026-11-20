"""Le moteur : les règles Prolog d'un contrat, le vocabulaire commun, et SWI-Prolog qui décide.

    déclaration ─► lecture.py (Mistral) : faits dans le vocabulaire commun (regles/vocabulaire.json)
                ─► prolog.py (SWI-Prolog) : regles/moteur.pl + regles/<contrat>.pl ─► décision, preuves, questions
                ─► chaine.py : la réponse (décision, citations vérifiées, questions)

La décision est un calcul logique, reproductible, et chaque preuve est une phrase du contrat écrite dans la
règle (vérifiée par `couverture regles`).

SWI-Prolog (gratuit, licence BSD) est appelé en sous-processus : `swipl` dans le PATH, ou
COUVERTURE_SWIPL, ou l'emplacement d'installation habituel sous Windows.
"""

from __future__ import annotations

import atexit
import json
import os
import queue
import re
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path


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


# --- Le moteur chargé une fois (DEMARCHE 7.46) -----------------------------------------------------------
#  Lancer SWI-Prolog pour chaque décision coûte le démarrage et le chargement du moteur et des règles, et la
#  lecture vérifiée décide jusqu'à trois fois par cas. Un processus par contrat reste ouvert : on lui envoie
#  les faits, il répond une ligne JSON (`servir` dans moteur.pl). Les règles modifiées sur le disque relancent
#  le processus. COUVERTURE_PROLOG_PERMANENT=non revient à un processus par décision.

class MoteurPermanent:
    def __init__(self, contrat_id: str, regles: Path, delai: int = 30):
        exe = swipl()
        if exe is None:
            raise ErreurRegles("SWI-Prolog introuvable. Windows : `winget install SWI-Prolog.SWI-Prolog`, "
                               "ou indiquer son chemin dans COUVERTURE_SWIPL.")
        self.contrat_id, self.regles, self.delai = contrat_id, regles, delai
        self.empreinte = self.empreinte_fichiers(regles)
        self.verrou = threading.Lock()
        poses = [f"assertz(parent_valeur({v}, {x}, {p}))" for v, x, p in hierarchie()
                 if all(ATOME.match(str(t)) for t in (v, x, p))]
        corps = ", ".join([f"consult({atome_chemin(MOTEUR)})", f"consult({atome_chemin(regles)})",
                           "retractall(parent_valeur(_, _, _))", *poses,
                           f"charger_domaines({atome_chemin(DOSSIER / 'vocabulaire.json')})", "servir"])
        self.journal = tempfile.TemporaryFile(mode="w+b")   # messages de SWI-Prolog (avertissements au chargement)
        self.p = subprocess.Popen([exe, "-q", "-g", f"catch(({corps}), E, (print_message(error, E), halt(2)))",
                                   "-t", "halt"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=self.journal)
        self.lignes: queue.Queue = queue.Queue()
        threading.Thread(target=self._lire, daemon=True).start()
        if self._demander("pret.").get("pret") is not True:
            self.fermer()
            raise ErreurRegles("SWI-Prolog ne s'est pas mis en service.")
        self.journal.seek(0)
        messages = self.journal.read().decode("utf-8", "replace")
        if "Warning" in messages or "ERROR" in messages:
            self.fermer()
            raise ErreurRegles(f"SWI-Prolog au chargement : {messages.strip()}")

    @staticmethod
    def empreinte_fichiers(regles: Path) -> tuple:
        return tuple(f.stat().st_mtime_ns for f in (MOTEUR, regles, DOSSIER / "vocabulaire.json"))

    def _lire(self) -> None:
        for ligne in self.p.stdout:
            self.lignes.put(ligne)
        self.lignes.put(None)  # fin du processus

    def _demander(self, demande: str) -> dict:
        self.p.stdin.write((demande + "\n").encode("utf-8"))
        self.p.stdin.flush()
        try:
            ligne = self.lignes.get(timeout=self.delai)
        except queue.Empty as e:
            self.fermer()
            raise ErreurRegles(f"SWI-Prolog n'a pas répondu en {self.delai} s.") from e
        if ligne is None:
            self.journal.seek(0)
            raise ErreurRegles(f"SWI-Prolog s'est arrêté : {self.journal.read().decode('utf-8', 'replace').strip()}")
        return json.loads(ligne.decode("utf-8"))

    def decider(self, faits: dict) -> dict:
        couples = []
        for v, x in faits.items():
            for val in (x if isinstance(x, list) else [x]):
                if not (ATOME.match(str(v)) and ATOME.match(str(val))):
                    raise ErreurRegles(f"fait mal formé : {v} = {val}")
                couples.append(f"{v}-{val}")
        with self.verrou:
            d = self._demander(f"faits([{', '.join(couples)}]).")
        if "erreur" in d:
            raise ErreurRegles(f"SWI-Prolog : {d['erreur']}")
        return d

    def vivant(self) -> bool:
        return self.p.poll() is None and self.empreinte == self.empreinte_fichiers(self.regles)

    def fermer(self) -> None:
        try:
            self.p.stdin.close()
            self.p.wait(timeout=2)
        except Exception:  # noqa: BLE001
            self.p.kill()


_MOTEURS: dict[str, MoteurPermanent] = {}
_MOTEURS_VERROU = threading.Lock()


def moteur_permanent(contrat_id: str) -> MoteurPermanent:
    with _MOTEURS_VERROU:
        m = _MOTEURS.get(contrat_id)
        if m is None or not m.vivant():
            if m is not None:
                m.fermer()
            regles = fichier_regles(contrat_id)
            if not regles.exists():
                raise ErreurRegles(f"Pas de règles pour {contrat_id} : {regles} est absent.")
            m = _MOTEURS[contrat_id] = MoteurPermanent(contrat_id, regles)
        return m


@atexit.register
def _fermer_moteurs() -> None:
    for m in _MOTEURS.values():
        m.fermer()


def decider(contrat_id: str, faits: dict) -> dict:
    if os.environ.get("COUVERTURE_PROLOG_PERMANENT", "oui").strip().lower() in {"non", "0", "false"}:
        return executer(contrat_id, "decider_json", faits)
    try:
        return moteur_permanent(contrat_id).decider(faits)
    except ErreurRegles:
        # Une seule nouvelle tentative, avec un processus neuf ; sinon l'erreur remonte.
        with _MOTEURS_VERROU:
            ancien = _MOTEURS.pop(contrat_id, None)
        if ancien is not None:
            ancien.fermer()
        return moteur_permanent(contrat_id).decider(faits)
