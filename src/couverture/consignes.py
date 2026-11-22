"""Versionnage des consignes (prompts), comme dans SortirIA (`scripts/versionnage.py`).

Le projet n'entraîne aucun modèle : ce qui change d'une version à l'autre, ce sont les
**consignes** envoyées au modèle. Une consigne modifiée change les réponses ; il faut
donc savoir laquelle était en service quand une réponse a été donnée.

- `CONSIGNES` : chaque consigne, le texte qui la porte dans le code, et **sa version** ;
- `config/versions_consignes.json` (le manifeste) : pour chaque consigne, sa version et
  l'empreinte de son texte ;
- **garde-fou** (test, donc CI) : il échoue si un texte change sans que sa version change,
  ou si le manifeste n'est pas à jour ;
- les versions en service sont notées dans le journal des analyses.

Pour modifier une consigne : changer le texte, augmenter sa version ici, puis
`couverture versions --manifeste`.

Archive : chaque version garde son texte intégral dans `docs/consignes/<nom>/<version>.txt`,
écrit par `couverture versions --manifeste`. Une version archivée n'est jamais réécrite :
c'est l'histoire des consignes, à lire avec `docs/DEMARCHE.md` qui dit pourquoi chacune a changé.
"""

from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path

# nom → (module, variable, version)
# Les consignes des méthodes retirées (grille de conditions, relecture, fiches, compilation, routage, réparation,
# juge de qualité le 18 nov. 2026 ; lecture en un temps, document brut et LegalBench le 20 nov.) restent archivées
# dans docs/consignes/ : c'est leur histoire.
CONSIGNES: dict[str, tuple[str, str, str]] = {
    "couverture-lecture-socle": ("couverture.lecture", "SYSTEME_LECTURE_SOCLE", "v2"),
    "couverture-lecture-details": ("couverture.lecture", "SYSTEME_LECTURE_DETAILS", "v3"),
    "couverture-verification-faits": ("couverture.lecture", "SYSTEME_VERIFICATION", "v3"),
    "couverture-redaction-regles": ("couverture.redaction", "SYSTEME_REDACTION", "v13"),
}

RACINE = Path(__file__).resolve().parents[2]
MANIFESTE = RACINE / "config" / "versions_consignes.json"
ARCHIVE = RACINE / "docs" / "consignes"


def texte(nom: str) -> str:
    module, variable, _ = CONSIGNES[nom]
    return getattr(importlib.import_module(module), variable)


def empreinte(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:16]


def etat_actuel() -> dict[str, dict]:
    return {
        nom: {"version": version, "empreinte": empreinte(texte(nom)), "source": f"{module}.{variable}"}
        for nom, (module, variable, version) in sorted(CONSIGNES.items())
    }


def lire_manifeste(chemin: Path = MANIFESTE) -> dict:
    return json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists() else {}


def archive(nom: str, version: str, dossier: Path = ARCHIVE) -> Path:
    return dossier / nom.removeprefix("couverture-") / f"{version}.txt"


def archiver(dossier: Path = ARCHIVE) -> list[str]:
    """Écrit le texte de chaque version en service qui n'est pas encore archivée."""
    ecrites = []
    for nom, (_, _, version) in CONSIGNES.items():
        f = archive(nom, version, dossier)
        if not f.exists():
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(texte(nom), encoding="utf-8")
            # Chemins écrits avec « / » sur tous les systèmes (Windows compris).
            ecrites.append((f.relative_to(dossier.parent.parent) if dossier == ARCHIVE else f).as_posix())
    return ecrites


def ecrire_manifeste(chemin: Path = MANIFESTE) -> dict:
    archiver()
    etat = etat_actuel()
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(etat, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return etat


def verifier(manifeste: dict | None = None) -> list[str]:
    """Problèmes entre le code et le manifeste. Vide si tout est cohérent."""
    manifeste = lire_manifeste() if manifeste is None else manifeste
    problemes = []
    for nom, actuel in etat_actuel().items():
        connu = manifeste.get(nom)
        if connu is None:
            problemes.append(f"{nom} : absente du manifeste (lancer `couverture versions --manifeste`).")
        elif actuel["empreinte"] != connu["empreinte"] and actuel["version"] == connu["version"]:
            problemes.append(f"{nom} : le texte a changé mais pas sa version ({actuel['version']}). "
                             f"Augmenter la version dans consignes.py.")
        elif actuel != connu:
            problemes.append(f"{nom} : manifeste pas à jour (lancer `couverture versions --manifeste`).")
    for nom, (_, _, version) in CONSIGNES.items():
        f = archive(nom, version)
        if not f.exists():
            problemes.append(f"{nom} : {version} pas archivée (lancer `couverture versions --manifeste`).")
        elif f.read_text(encoding="utf-8") != texte(nom):
            problemes.append(f"{nom} : le texte archivé de {version} ne correspond plus au code. "
                             f"Une version archivée ne change pas : augmenter la version.")
    for nom in set(manifeste) - set(CONSIGNES):
        problemes.append(f"{nom} : dans le manifeste, mais plus dans le code.")
    return problemes


def versions_courtes() -> str:
    """« lecture-socle:v2,lecture-details:v2,… » : ce qu'on note dans le journal."""
    return ",".join(f"{nom.removeprefix('couverture-')}:{v}" for nom, (_, _, v) in sorted(CONSIGNES.items()))
