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

import atexit
import json
import os
import queue
from concurrent.futures import ThreadPoolExecutor
import re
import shutil
import subprocess
import tempfile
import threading
import time
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
- Ne renseigne une variable que si la déclaration la dit ou l'implique clairement. Sinon, réponds "inconnu" (ou une liste vide) : elle restera inconnue, et le gestionnaire posera la question. Un fait inventé est plus grave qu'un fait manquant.
- « inconnu » est la réponse normale pour la plupart des variables : une déclaration ne dit presque jamais tout. Ne choisis pas « non », « aucune » ou « tiers » par défaut : seulement si c'est écrit."""

SYSTEME_LECTURE_SOCLE = """Tu lis la déclaration d'un sinistre et tu dis ce qui s'est passé, ce qui est touché et où, avec un vocabulaire imposé. Tu ne décides pas si le sinistre est couvert.

Le vocabulaire donne, pour chaque variable, la question à laquelle elle répond, ses valeurs, et le sens des valeurs proches. Choisis la valeur dont le sens correspond à ce qui est écrit.

Règles :
""" + REGLES_COMMUNES + """
- evenement : la cause, et aussi le dommage s'il est d'une autre nature. Une tempête qui arrache des tuiles et fait entrer la pluie : ["tempete", "degat_eaux"]. Ne perds jamais la cause, même si aucune valeur ne la nomme exactement : prends la plus proche par son sens, ou « autre ».
- « Disparu », « je ne retrouve plus » ne disent pas qu'il y a eu vol : ne mets evenement = vol que si un vol est décrit (volé, pris, cambriolé, arraché).
- Un lieu se déduit de ce qui est écrit : une pièce ou une partie du logement (salon, cuisine, salle de bain, entrée, parquet, plafond, « chez moi », « mon appartement ») donne lieu = logement. Mais ce qui ne dit rien de l'endroit ne donne pas de lieu : « pendant que je faisais mes courses » ne dit pas où était le vélo.
- Façade, murs, parquet, plafond, toiture : bien = element_batiment. Tuyau, canalisation : bien = canalisation.
- bien : ce qui a été volé, perdu ou abîmé. Des clés seulement si ce sont elles qui ont été volées ou perdues : la clé dont le voleur s'est servi (sous le paillasson, dans la boîte aux lettres) n'est pas un bien volé.

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


INCONNU = "inconnu"


def schema_faits(variables: dict) -> dict:
    """Le schéma JSON de la réponse : chaque variable avec ses seules valeurs permises (listes fermées),
    « inconnu » en premier. **Aucune variable n'est obligatoire** : quand le schéma les exigeait toutes,
    Mistral Small remplissait au lieu de laisser vide (« fermeture = aucune » pour « volé dans ma cave »),
    avec null en fin de liste (7.38) comme avec « inconnu » en tête (7.39). La lecture d'un seul coup, sans
    schéma, ne le faisait pas : le modèle n'écrivait que ce qu'il avait trouvé."""
    proprietes = {}
    for v, d in variables.items():
        if d.get("plusieurs"):
            proprietes[v] = {"type": "array", "items": {"type": "string", "enum": list(d["valeurs"])}}
        else:
            proprietes[v] = {"type": "string", "enum": [INCONNU] + list(d["valeurs"])}
    return {"type": "object", "additionalProperties": False, "required": ["faits"],
            "properties": {"faits": {"type": "object", "additionalProperties": False, "properties": proprietes}}}


MODES_LECTURE = ("verifiee", "deux_temps", "en_parallele", "un_temps")


def mode_lecture() -> str:
    """La lecture des faits (DEMARCHE 7.38 à 7.45), choisie par COUVERTURE_LECTURE :
    - verifiee (par défaut, la meilleure mesurée, 7.45) : les deux temps, puis une vérification : chaque fait du
      temps 2 est soumis au modèle sous forme d'affirmation (« la déclaration dit-elle que… ? ») ; un fait
      « non dit » redevient inconnu (7.43), sauf si le retirer ferait couvrir : le moteur arbitre (7.44) ;
    - deux_temps : le socle, puis seulement les questions de cet événement.
      Il trouve les faits qui décident (absence, gel, cause de l'eau) ; il en invente aussi (« fermeture =
      aucune »), ce qui fait moins poser de questions, mais rarement couvrir à tort ;
    - en_parallele : le socle et la lecture complète v4 en même temps. Essayé et écarté (7.42) : la lecture
      complète oublie les faits qui décident, et les couverts à tort reviennent (11,7) ;
    - un_temps : la lecture d'avant, d'un seul coup (9,3 couverts à tort)."""
    m = os.environ.get("COUVERTURE_LECTURE", "").strip().lower()
    return m if m in MODES_LECTURE else "verifiee"


def _lire(llm: LLM, systeme: str, variables: dict, message: str) -> dict:
    liste = "\n".join(description_variable(v, d) for v, d in variables.items())
    texte = completer_avec_schema(llm, systeme, f"## Vocabulaire\n{liste}\n\n{message}", schema_faits(variables))
    lus = {}
    for v, x in (extraire_json(texte).get("faits") or {}).items():
        x = [e for e in x if e != INCONNU] if isinstance(x, list) else (None if x == INCONNU else x)
        if x not in (None, "", []):
            lus[v] = x
    return lus


SYSTEME_VERIFICATION = """Tu relis la déclaration d'un sinistre et tu vérifies des affirmations qu'un collègue en a tirées. Tu ne décides pas si le sinistre est couvert.

Pour chaque affirmation, réponds :
- "dit" si la déclaration l'affirme, ou l'implique sans aucun doute ;
- "non_dit" si la déclaration ne le dit pas : elle n'en parle pas, ou il faudrait le supposer.

Une affirmation plausible mais non écrite est "non_dit". Exemples : « le local n'était pas fermé » pour « on m'a volé mon vélo dans ma cave » est non_dit (la déclaration ne dit rien de la fermeture) ; « l'assuré était absent » pour « pendant mes vacances » est dit.

Réponds uniquement par un objet JSON : {"verdicts": {"variable": "dit"}}"""


def affirmation(v: str, x, voc: dict) -> str:
    """Un fait lu, en phrase à vérifier : la question du vocabulaire et la valeur, avec son sens s'il est donné."""
    aide = voc.get(v, {}).get("aide", {})
    valeurs = x if isinstance(x, list) else [x]
    rendu = ", ".join(f"{e} ({aide[e]})" if e in aide else str(e) for e in valeurs)
    return f"- {v} : {voc.get(v, {}).get('question', v)} → {rendu}"


def juger_affirmations(sinistre: str, faits: dict, llm: LLM, voc: dict) -> dict:
    """{variable: "dit" | "non_dit"} : chaque fait soumis au modèle comme une affirmation sur la déclaration."""
    liste = "\n".join(affirmation(v, x, voc) for v, x in faits.items())
    schema = {"type": "object", "additionalProperties": False, "required": ["verdicts"],
              "properties": {"verdicts": {"type": "object", "additionalProperties": False,
                                          "properties": {v: {"type": "string", "enum": ["dit", "non_dit"]} for v in faits}}}}
    return extraire_json(completer_avec_schema(
        llm, SYSTEME_VERIFICATION, f"## Affirmations\n{liste}\n\n## Déclaration\n{sinistre}", schema)).get("verdicts") or {}


def faits_decisifs(faits: dict, decideur, decision: str) -> list[str]:
    """Les faits qui portent la décision : ceux dont le retrait la change. Le moteur le dit en quelques
    millisecondes ; ce sont eux qu'une réponse ferme doit avoir confirmés (7.49)."""
    return [v for v in faits if decideur({k: x for k, x in faits.items() if k != v})["decision"] != decision]


def verifier_details(sinistre: str, lus: dict, llm: LLM, voc: dict) -> tuple[dict, list[str]]:
    """Le contrôle des faits du temps 2. Les faits du socle (événement, bien, lieu) ne sont pas soumis : retirés,
    ils rendaient tout incertain (7.26). Une vérification illisible ne retire rien (avertissement)."""
    details = {v: x for v, x in lus.items() if v not in SOCLE and x not in (None, "", [])}
    if not details:
        return lus, []
    try:
        verdicts = juger_affirmations(sinistre, details, llm, voc)
    except ErreurLLM:
        raise
    except Exception as e:  # noqa: BLE001
        return lus, [f"vérification des faits illisible ({e}) : faits gardés"]
    gardes, retires = dict(lus), []
    for v, x in details.items():
        if verdicts.get(v) == "non_dit":
            del gardes[v]
            retires.append(f"{v} = {x if not isinstance(x, list) else '/'.join(x)} : non dit dans la déclaration, retiré")
    return gardes, retires


def variables_du_temps_2(voc: dict, evenements: list[str], socle: dict | None = None) -> dict:
    """Les variables à demander une fois l'événement connu : celles qui s'y appliquent (« pour »), et celles
    qui s'appliquent à tout. Sans événement lu, toutes. Une variable d'extension (« si » : le lieu qui
    l'entame, 7.70) est demandée aussi quand le temps 1 a lu ce lieu : le séjour temporaire pour un « autre
    bâtiment », pas pour chaque sinistre au logement."""
    ev = set(evenements)

    def entamee(d):
        return any(set(x if isinstance(x, list) else [x]) & set(vals)
                   for var, vals in (d.get("si") or {}).items() for x in [(socle or {}).get(var) or []])

    def hors_lieu(d):
        # « seulement_si » (7.71) : une variable du véhicule ne se lit pas quand le lieu lu est la cave. Lieu non lu :
        # on la garde, faute de savoir.
        lus = {var: set(x if isinstance(x, list) else [x]) for var, x in (socle or {}).items() if x}
        return any(var in lus and not lus[var] & set(vals) for var, vals in (d.get("seulement_si") or {}).items())

    return {v: d for v, d in voc.items() if v not in SOCLE
            and (not ev or not d.get("pour") or ev & set(d["pour"]) or entamee(d)) and not hors_lieu(d)}


def variables_du_contrat(contrat_id: str) -> set[str] | None:
    """Les variables que les règles du contrat emploient (`f(variable, …)`), ou None sans fichier de règles.
    Le vocabulaire est commun à tous les assureurs ; un contrat n'en lit que ce qu'il emploie (7.57)."""
    chemin = fichier_regles(contrat_id)
    if not chemin.exists():
        return None
    texte = chemin.read_text(encoding="utf-8")
    texte = re.sub(r"%[^\n]*", "", re.sub(r"/\*.*?\*/", "", texte, flags=re.S))
    return set(re.findall(r"\bf\(\s*'?([a-z][a-z0-9_]*)'?\s*,", texte))


def extraire_faits_regles(sinistre: str, llm: LLM, decideur=None,
                          variables: set[str] | None = None) -> tuple[dict, list[str]]:
    """Les faits lus par le modèle, et les écarts au vocabulaire (retirés).
    `decideur(faits) -> dict` (le moteur) arbitre la vérification, en mode « verifiee » (7.44).
    `variables` : celles du contrat (le socle est toujours lu) ; None : tout le vocabulaire."""
    voc = vocabulaire()
    if variables is not None:
        # Les règles d'Assureur B ne doivent pas changer ce qu'on lit pour Assureur A : la plainte ou la formule
        # « Privilège » n'ont rien à faire dans la lecture d'un vol chez Assureur A (7.57).
        voc = {v: d for v, d in voc.items() if v in SOCLE or v in variables}
    declaration = f"## Déclaration\n{sinistre}"
    mode = mode_lecture()
    if mode == "un_temps":
        lus = _lire(llm, SYSTEME_FAITS_REGLES, voc, declaration)
    elif mode == "en_parallele":  # essayé et écarté (7.42)
        # Les deux lectures partent ensemble : la réponse attend la plus lente, pas la somme.
        with ThreadPoolExecutor(max_workers=2) as ex:
            socle = ex.submit(_lire, llm, SYSTEME_LECTURE_SOCLE, {v: voc[v] for v in SOCLE}, declaration)
            complet = ex.submit(_lire, llm, SYSTEME_FAITS_REGLES, voc, declaration)
            lus_socle, lus = socle.result(), complet.result()
        # Le socle vient de la lecture courte (elle ne perd plus le lieu) ; s'il lui manque une variable,
        # la lecture complète la donne.
        lus = {v: x for v, x in lus.items() if v not in SOCLE or v not in lus_socle} | lus_socle
    else:
        lus = _lire(llm, SYSTEME_LECTURE_SOCLE, {v: voc[v] for v in SOCLE}, declaration)
        evenements = [str(e) for e in (lus.get("evenement") or []) if str(e) in voc["evenement"]["valeurs"]]
        details = variables_du_temps_2(voc, evenements, lus)
        if details:
            etabli = "; ".join(f"{v} = {'/'.join(map(str, x)) if isinstance(x, list) else x}"
                               for v, x in lus.items() if x not in (None, "", []))
            lus |= {v: x for v, x in _lire(llm, SYSTEME_LECTURE_DETAILS, details,
                                           f"## Déjà établi\n{etabli or 'rien'}\n\n{declaration}").items()
                    if v not in SOCLE}
    if mode != "verifiee":
        return au_vocabulaire(lus, voc)
    lus_verifies, retraits = verifier_details(sinistre, lus, llm, voc)
    faits, ecarts = au_vocabulaire(lus_verifies, voc)
    if decideur is not None and any("non dit" in r for r in retraits):
        # Un doute ne doit jamais faire couvrir : si retirer les faits « non dits » fait passer la décision à
        # « couvert », la vérification a sans doute écarté un fait vrai qui faisait refuser (la fenêtre laissée
        # ouverte, le chauffage coupé : 7.44). Le moteur tranche : on garde alors la lecture non vérifiée.
        faits_lus, ecarts_lus = au_vocabulaire(lus, voc)
        if decideur(faits)["decision"] == "COUVERT" and decideur(faits_lus)["decision"] != "COUVERT":
            return faits_lus, ecarts_lus + ["vérification écartée : retirer ces faits aurait fait couvrir ("
                                            + "; ".join(r.split(" : ")[0] for r in retraits) + ")"]
    return faits, retraits + ecarts


def au_vocabulaire(lus: dict, voc: dict) -> tuple[dict, list[str]]:
    """Les faits lus, ramenés au vocabulaire : variables et valeurs inconnues retirées, faits hors sujet retirés."""
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
        self.llm_confirmation = None          # COUVERTURE_MODELE_CONFIRMATION, chargé à la première confirmation
        self.decideur = decideur or (lambda faits: decider(contrat_id, faits))
        self.variables = variables_du_contrat(contrat_id)

    @classmethod
    def depuis_base(cls, base, contrat_id: str, llm: LLM) -> "PipelineRegles":
        if not fichier_regles(contrat_id).exists():
            raise LookupError(f"Pas de règles Prolog pour {contrat_id} (regles/{contrat_id}.pl).")
        if swipl() is None:
            raise LookupError("SWI-Prolog introuvable : `winget install SWI-Prolog.SWI-Prolog` (Windows).")
        return cls(contrat_id, base.clauses(contrat_id), llm)

    def analyser(self, sinistre: str) -> Resultat:
        debut = time.perf_counter()
        try:
            faits, ecarts = extraire_faits_regles(sinistre, self.llm, self.decideur, self.variables)
        except ErreurLLM:
            raise
        except Exception as e:  # noqa: BLE001
            v = Verdict(decision=Decision.INCERTAIN, justification="Le modèle n'a pas pu lire la déclaration.",
                        confiance=0.0, mode=f"regles:{self.llm.nom}", avertissements=[str(e)])
            return Resultat(sinistre=sinistre, contrat_id=self.contrat_id, methode=self.methode, faits=Faits(),
                            clauses_consultees=[], verdict=v)
        lu = time.perf_counter()
        d = self.decideur(faits)
        decide = time.perf_counter()
        doutes: list[str] = []
        if mode_lecture() == "verifiee" and d["decision"] in ("COUVERT", "NON_COUVERT"):
            d, doutes, avert = self.confirmer(sinistre, faits, d)
            ecarts = ecarts + avert
        verdict, consultees = self.verdict(d, faits)
        if doutes:
            # « Je ne sais pas » plutôt qu'une réponse fausse : un fait qui porte la décision n'est pas confirmé.
            verdict.decision = Decision.INCERTAIN
            verdict.confiance = min(verdict.confiance, 0.4)
            verdict.justification = ("Je ne peux pas trancher : la déclaration ne dit pas clairement "
                                     + " ; ni ".join(f"« {affirmation(v, faits[v], vocabulaire())[2:]} »" for v in doutes)
                                     + ". " + verdict.justification)
            verdict.informations_manquantes = list(dict.fromkeys(
                [question(v) for v in doutes] + verdict.informations_manquantes))
            verdict.raisonnement = [f"Réponse suspendue : fait décisif non confirmé ({', '.join(doutes)}) ; "
                                    "ci-dessous, le raisonnement sans ce fait."] + verdict.raisonnement
        verdict.avertissements = ecarts + verdict.avertissements
        verdict = valider(verdict, consultees)
        return Resultat(sinistre=sinistre, contrat_id=self.contrat_id, methode=self.methode,
                        faits=faits_lisibles(faits), clauses_consultees=consultees, verdict=verdict,
                        durees_ms={"lecture": int((lu - debut) * 1000), "decision": int((decide - lu) * 1000)})

    def modele_confirmation(self) -> LLM:
        """Le modèle qui confirme les faits décisifs. Le petit modèle confirmait ses propres erreurs de lecture
        (le jardin lu « terrasse », une rayure lue « vandalisme » : 7.66) ; un modèle plus fort peut être
        demandé pour ce seul contrôle, court, avec COUVERTURE_MODELE_CONFIRMATION."""
        if self.llm_confirmation is None:
            from .llm import configurer
            self.llm_confirmation = configurer("confirmation") or self.llm
        return self.llm_confirmation

    def confirmer(self, sinistre: str, faits: dict, d: dict) -> tuple[dict, list[str], list[str]]:
        """Une réponse ferme doit reposer sur des faits confirmés (7.49). Le moteur dit quels faits portent la
        décision ; le modèle confirme, sur la déclaration, que chacun y est écrit. Un seul « non dit » : la
        réponse devient « incertain », avec la question sur ce fait. Rend (décision, faits douteux, avertissements)."""
        decisifs = faits_decisifs(faits, self.decideur, d["decision"])
        if not decisifs:
            return d, [], []
        try:
            verdicts = juger_affirmations(sinistre, {v: faits[v] for v in decisifs}, self.modele_confirmation(), vocabulaire())
        except ErreurLLM:
            raise
        except Exception as e:  # noqa: BLE001
            return d, [], [f"confirmation des faits décisifs illisible ({e}) : réponse gardée"]
        doutes = [v for v in decisifs if verdicts.get(v) == "non_dit"]
        if not doutes:
            return d, [], []
        sans = {k: x for k, x in faits.items() if k not in doutes}
        return self.decideur(sans), doutes, [f"{v} : fait décisif non confirmé par la déclaration" for v in doutes]

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
        accessoires = d.get("accessoires") or []
        if accessoires and decision == Decision.COUVERT:
            # 7.68 : ce qui peut s'ajouter à la garantie qui couvre, sans changer la décision.
            motif += " Peuvent s'y ajouter : " + " ; ".join(
                f"« {a['garantie']} » ({a['article']})" + (" sous réserve de précisions" if a.get("decision") == "INCERTAIN"
                                                          or a.get("reserves") else "") for a in accessoires[:4]) + "."
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
