"""Le moteur : les règles Prolog d'un contrat, le vocabulaire commun, et SWI-Prolog qui décide.

    déclaration ─► lecture.py (Mistral) : faits dans le vocabulaire (regles/vocabulaire/)
                ─► prolog.py (SWI-Prolog) : regles/moteur.pl + regles/<contrat>.pl ─► décision, preuves, questions
                ─► chaine.py : la réponse (décision, citations vérifiées, questions)

La décision est un calcul logique, reproductible, et chaque preuve est une phrase du contrat écrite dans la
règle (vérifiée par `couverture regles`).

SWI-Prolog (gratuit, licence BSD) est appelé en sous-processus : `swipl` dans le PATH, ou
COUVERTURE_SWIPL, ou l'emplacement d'installation habituel sous Windows.
"""

from __future__ import annotations

import atexit
import hashlib
import json
import os
import queue
import re
import shutil
import subprocess
import tempfile
import threading
from pathlib import Path


RACINE = Path(__file__).resolve().parents[3]
DOSSIER = RACINE / "regles"
MOTEUR = DOSSIER / "moteur.pl"
EMPLACEMENTS = [r"C:\Program Files\swipl\bin\swipl.exe", "/usr/bin/swipl", "/usr/local/bin/swipl",
                "/opt/homebrew/bin/swipl", "/Applications/SWI-Prolog.app/Contents/MacOS/swipl"]
ATOME = re.compile(r"^[a-z][a-z0-9_]*$")


class ErreurRegles(RuntimeError):
    """SWI-Prolog absent, règles qui ne se chargent pas, ou faits hors du vocabulaire."""


def swipl() -> str | None:
    """Le programme SWI-Prolog : `COUVERTURE_SWIPL`, sinon celui du PATH, sinon les emplacements habituels ; rien s'il
    est introuvable."""
    for candidat in [os.environ.get("COUVERTURE_SWIPL"), shutil.which("swipl"), *EMPLACEMENTS]:
        if candidat and Path(candidat).exists():
            return candidat
    return None


def fichier_regles(contrat_id: str) -> Path:
    """Le fichier de règles d'un contrat (`regles/<contrat>.pl`)."""
    return DOSSIER / f"{contrat_id}.pl"


VOCABULAIRE = DOSSIER / "vocabulaire"
COMMUN = "commun"


def fichiers_vocabulaire(dossier: Path | None = None) -> list[Path]:
    """`commun.json` (le socle et les variables que plusieurs contrats emploient), puis un fichier par contrat
    (les variables que lui seul emploie) (7.119)."""
    dossier = dossier or VOCABULAIRE
    return [dossier / f"{COMMUN}.json", *sorted(f for f in dossier.glob("*.json") if f.stem != COMMUN)]


def vocabulaire(dossier: Path | None = None) -> dict:
    """Tout le vocabulaire : le commun, puis les variables propres à chaque contrat. Les règles d'un contrat
    n'emploient que le commun et les siennes ; la lecture ne lui demande que celles-là (`variables_du_contrat`)."""
    voc: dict = {}
    for f in fichiers_vocabulaire(dossier):
        for v, d in json.loads(f.read_text(encoding="utf-8"))["variables"].items():
            if v in voc:
                raise ErreurRegles(f"vocabulaire : « {v} » est défini deux fois ({f.name})")
            voc[v] = d
    return voc


def libelle(variable: str, voc: dict, valeur: str | None = None) -> str:
    """Le nom à montrer d'une variable, ou d'une de ses valeurs : « libelle » et « libelles » du vocabulaire.
    Sans libellé écrit, l'identifiant sans ses tirets bas (« voie_publique » → « voie publique »)."""
    d = voc.get(variable, {})
    if valeur is None:
        return d.get("libelle") or variable.replace("_", " ")
    return (d.get("libelles") or {}).get(valeur) or str(valeur).replace("_", " ")


CONDITIONS_PARTICULIERES = "conditions_particulieres"


def vocabulaire_du_contrat(contrat_id: str, voc: dict | None = None) -> dict:
    """Le vocabulaire tel qu'un contrat le voit : une variable dont chaque contrat a ses noms (« par_contrat » : la
    formule) n'y garde que les siens, avec leur aide et leurs libellés. La lecture d'une déclaration faite pour C
    ne doit pas pouvoir répondre « excellence », une formule de D (7.154) ; la rédaction ne le peut plus (7.150).
    Un contrat qui ne déclare pas ses noms garde toutes les valeurs : rien ne dit lesquelles sont les siennes."""
    voc = voc if voc is not None else vocabulaire()
    vu = {}
    for v, d in voc.items():
        siens = (d.get("par_contrat") or {}).get(contrat_id)
        if siens:
            d = d | {"valeurs": list(siens)}
            for cle in ("aide", "libelles", "parents"):
                if isinstance(d.get(cle), dict):
                    d[cle] = {x: t for x, t in d[cle].items() if x in siens}
        vu[v] = d
    return vu


def souscription(contrat_id: str, voc: dict | None = None) -> dict:
    """Ce que le contrat du client précise, et que la déclaration ne dit que parfois (7.141) : les variables
    de « source » conditions particulières (la formule, une option, un pack) que les règles de ce contrat
    emploient. Les valeurs sont celles du contrat quand la variable les déclare (« par_contrat » : les formules
    de B ne sont pas celles de D)."""
    voc = voc if voc is not None else vocabulaire()
    employees = variables_employees(contrat_id) if fichier_regles(contrat_id).exists() else set()
    return {v: d for v, d in vocabulaire_du_contrat(contrat_id, voc).items()
            if v in employees and d.get("source") == CONDITIONS_PARTICULIERES}


def retenir_souscription(contrat_id: str, donnee: dict | None, voc: dict | None = None) -> tuple[dict, list[str]]:
    """La souscription donnée avec la déclaration, ramenée à ce que le contrat connaît : (faits, écarts)."""
    connues, faits, ecarts = souscription(contrat_id, voc), {}, []
    for v, x in (donnee or {}).items():
        if x in (None, ""):
            continue
        if v not in connues:
            ecarts.append(f"conditions particulières : « {v} » n'est pas une option de ce contrat, ignorée")
        elif str(x) not in connues[v]["valeurs"]:
            ecarts.append(f"conditions particulières : {v} = {x}, valeur inconnue de ce contrat, ignorée")
        else:
            faits[v] = str(x)
    return faits, ecarts


SOCLE_AFFICHE = ["evenement", "bien", "lieu"]


def faits_affiches(faits: dict, voc: dict | None = None) -> list[dict[str, str]]:
    """Les faits tels qu'on les montre : le libellé de la variable et de ses valeurs (`libelle`), le socle
    (événement, bien, lieu) d'abord. L'écran et la fiche affichent cette liste ; `faits` reste la forme que
    `/decisions` accepte."""
    voc = voc if voc is not None else vocabulaire()
    # Le socle, puis les faits de la déclaration, puis ceux des conditions particulières.
    cles = sorted(faits, key=lambda v: (SOCLE_AFFICHE.index(v) if v in SOCLE_AFFICHE else len(SOCLE_AFFICHE),
                                        voc.get(v, {}).get("source") == CONDITIONS_PARTICULIERES, v))
    return [{"variable": v, "libelle": libelle(v, voc),
             "valeur": ", ".join(libelle(v, voc, x) for x in (faits[v] if isinstance(faits[v], list) else [faits[v]]))}
            for v in cles]


def clauses_citees(contrat_id: str) -> set[str]:
    """Les clauses que les règles du contrat citent : celles qu'une réponse peut montrer. En ligne, ce sont les
    seules dont le texte entier se consulte (7.161) : pas le contrat, les passages qui appuient une décision."""
    fichier = fichier_regles(contrat_id)
    if not fichier.exists():
        return set()
    return set(re.findall(r"'([^'\n]+)',\s*\n?\s*\"", fichier.read_text(encoding="utf-8")))


def a_des_garanties(contrat_id: str) -> bool:
    """Vrai si les règles du contrat traduisent au moins une garantie. Un fichier tout juste créé par la rédaction
    (un en-tête, aucune règle) n'est pas encore un contrat qu'on peut interroger (7.149)."""
    fichier = fichier_regles(contrat_id)
    return fichier.exists() and re.search(r"^garantie\(", fichier.read_text(encoding="utf-8"), flags=re.M) is not None


def traduction_complete(contrat_id: str) -> bool:
    """Les conditions générales de ce contrat sont-elles déclarées traduites en entier (`regles/traduction.json`,
    7.169) ? Faux quand le fichier manque ou ne dit rien du contrat : on ne refuse pas sur une absence."""
    try:
        etat = json.loads((DOSSIER / "traduction.json").read_text(encoding="utf-8")).get(contrat_id) or {}
    except (OSError, ValueError):
        return False
    return etat.get("complet") is True


def contrats_regles() -> list[str]:
    """Les contrats dont les règles traduisent au moins une garantie."""
    return sorted(f.stem for f in DOSSIER.glob("*.pl") if f != MOTEUR and a_des_garanties(f.stem))


def variables_employees(contrat_id: str) -> set[str]:
    """Les variables que les règles du contrat emploient (`f(variable, …)`), commentaires retirés."""
    texte = fichier_regles(contrat_id).read_text(encoding="utf-8")
    texte = re.sub(r"%[^\n]*", "", re.sub(r"/\*.*?\*/", "", texte, flags=re.S))
    return set(re.findall(r"\bf\(\s*'?([a-z][a-z0-9_]*)'?\s*,", texte))


def fichier_domaines() -> Path:
    """Les valeurs de chaque variable, en un seul fichier pour le moteur (`charger_domaines` de moteur.pl), écrit
    dans le dossier temporaire et nommé d'après son contenu : réécrit seulement quand le vocabulaire change."""
    contenu = json.dumps({"variables": {v: {"valeurs": d["valeurs"]} for v, d in vocabulaire().items()}}, ensure_ascii=False)
    chemin = Path(tempfile.gettempdir()) / f"couverture-domaines-{hashlib.sha256(contenu.encode()).hexdigest()[:16]}.json"
    if not chemin.exists():
        provisoire = chemin.with_suffix(f".{os.getpid()}.tmp")
        provisoire.write_text(contenu, encoding="utf-8")
        os.replace(provisoire, chemin)
    return chemin


def hierarchie(voc: dict | None = None) -> list[tuple[str, str, str]]:
    """(variable, valeur, parent) : la hiérarchie du vocabulaire (« parents »), posée en faits pour le moteur.
    Une vitre est un élément du bâtiment : une règle large reconnaît le fait précis, et un fait vague ne
    tranche pas pour une règle précise (le moteur répond « inconnu » et pose la question)."""
    voc = voc or vocabulaire()
    return [(v, x, p) for v, d in voc.items() for x, ps in d.get("parents", {}).items() for p in ps]


def evenements_etendus(evenements, voc: dict | None = None) -> set[str]:
    """Les événements, et ceux dont ils relèvent dans la hiérarchie : un « accident » compte comme un heurt et
    comme un bris (« parents »). Sans cela, la plainte après un heurt était hors sujet pour un accident : la
    question était posée, et la réponse du client retirée (7.125)."""
    voc = voc or vocabulaire()
    parents = voc.get("evenement", {}).get("parents", {})
    vus, pile = set(), [str(e) for e in evenements or ()]
    while pile:
        e = pile.pop()
        if e not in vus:
            vus.add(e)
            pile += parents.get(e, [])
    return vus


def filtrer_faits(faits: dict, voc: dict | None = None) -> tuple[dict, list[str]]:
    """Retire les faits hors sujet : une variable qui déclare les événements auxquels elle s'applique
    (« pour ») n'est gardée que si l'un d'eux est lu. Une cause d'eau pour une bougie, des travaux pour
    un vol : le modèle les invente, le code les retire, quelle que soit la consigne. Sans événement
    lu, on ne peut pas juger : tout est gardé."""
    voc = voc or vocabulaire()
    ev = faits.get("evenement")
    evenements = evenements_etendus(ev if isinstance(ev, list) else [ev], voc) if ev else set()
    if not evenements:
        return dict(faits), []
    gardes, retires = {}, []
    for v, x in faits.items():
        pour = voc.get(v, {}).get("pour")
        if pour and not evenements & set(pour):
            retires.append(f"{v} = {x if not isinstance(x, list) else '/'.join(x)} : hors sujet pour "
                           f"{'/'.join(sorted(set(ev if isinstance(ev, list) else [ev])))}, retiré")
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
        poses.append(f"charger_domaines({atome_chemin(fichier_domaines())})")
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
    """Un processus SWI-Prolog gardé ouvert pour un contrat : moteur, règles et vocabulaire chargés une fois, puis une
    ligne JSON par décision."""

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
                           f"charger_domaines({atome_chemin(fichier_domaines())})", "servir"])
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
        """Les dates de modification du moteur, des règles et du vocabulaire : si l'une change, le processus est relancé."""
        return tuple(f.stat().st_mtime_ns for f in (MOTEUR, regles, *fichiers_vocabulaire()))

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
        """Envoie les faits au processus et rend sa décision ; `ErreurRegles` si un fait est mal formé ou si le moteur
        signale une erreur."""
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
        """Le processus tourne encore, et ses fichiers n'ont pas changé depuis son lancement."""
        return self.p.poll() is None and self.empreinte == self.empreinte_fichiers(self.regles)

    def fermer(self) -> None:
        """Arrête le processus, de force s'il ne répond pas."""
        try:
            self.p.stdin.close()
            self.p.wait(timeout=2)
        except Exception:  # noqa: BLE001
            self.p.kill()


_MOTEURS: dict[str, MoteurPermanent] = {}
_MOTEURS_VERROU = threading.Lock()


def moteur_permanent(contrat_id: str) -> MoteurPermanent:
    """Le processus du contrat, lancé au besoin (relancé s'il est mort ou si ses fichiers ont changé)."""
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
    """La décision du moteur pour des faits. Par défaut avec le processus gardé ouvert, relancé une fois en cas d'erreur ;
    `COUVERTURE_PROLOG_PERMANENT=non` lance un processus par décision."""
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
