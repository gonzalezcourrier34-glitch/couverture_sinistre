"""Profils d'assureur : les règles de lecture propres à un assureur.

L'équivalent de `config/sources.yaml` dans SortirIA. Les règles générales de
`segmentation.py` couvrent la plupart des contrats ; quand un assureur rédige
autrement (« Les cas non couverts » au lieu de « Exclusions »), on ne touche pas
au code : on écrit un profil, réutilisé pour toutes les versions de ses contrats.

Un profil est un fichier JSON dans `<donnees>/profils/<nom>.json` :
{
  "nom": "foyer",
  "intertitres": {"les cas non couverts": "exclusion", "ce que signifient les mots": "definition"},
  "lignes_ignorees": ["^Foyer Assurances S\\.A\\. .*$"],
  "lexique": "auto"              // "auto", "deux_points" (Terme : définition) ou "terme_seul"
}
Le catalogue des contrats désigne le profil : "profil": "foyer".

Les profils sont proposés par l'agent de réparation (`reparation.py`) et ne sont
appliqués qu'après validation humaine.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .texte import normaliser

TYPES_PERMIS = {"garantie", "exclusion", "condition", "limite", "definition"}
FORMATS_LEXIQUE = {"auto", "deux_points", "terme_seul"}


class ProfilInvalide(ValueError):
    pass


def valider_profil(profil: dict) -> dict:
    """Vérifie la forme d'un profil et le renvoie normalisé. Lève ProfilInvalide sinon."""
    if not isinstance(profil, dict):
        raise ProfilInvalide("Le profil doit être un objet JSON.")
    nom = str(profil.get("nom", "")).strip()
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,40}", nom):
        raise ProfilInvalide(f"Nom de profil invalide : « {nom} » (minuscules, chiffres, tirets).")
    intertitres = {}
    for phrase, type_ in (profil.get("intertitres") or {}).items():
        cle = normaliser(str(phrase)).rstrip(" :.").strip()
        if not 3 <= len(cle) <= 80:
            raise ProfilInvalide(f"Intertitre de longueur anormale : « {phrase} ».")
        if type_ not in TYPES_PERMIS:
            raise ProfilInvalide(f"Type inconnu pour « {phrase} » : {type_} (attendu : {', '.join(sorted(TYPES_PERMIS))}).")
        intertitres[cle] = type_
    ignorees = []
    for motif in profil.get("lignes_ignorees") or []:
        try:
            re.compile(motif)
        except re.error as e:
            raise ProfilInvalide(f"Expression invalide « {motif} » : {e}") from e
        ignorees.append(str(motif))
    lexique = profil.get("lexique", "auto")
    if lexique not in FORMATS_LEXIQUE:
        raise ProfilInvalide(f"Format de lexique inconnu : {lexique}.")
    return {"nom": nom, "intertitres": intertitres, "lignes_ignorees": ignorees, "lexique": lexique}


def charger_profil(dossier: str | Path, nom: str) -> dict:
    chemin = Path(dossier) / f"{nom}.json"
    if not chemin.exists():
        raise ProfilInvalide(f"Profil introuvable : {chemin}")
    return valider_profil(json.loads(chemin.read_text(encoding="utf-8")))


def ecrire_profil(dossier: str | Path, profil: dict) -> Path:
    profil = valider_profil(profil)
    chemin = Path(dossier) / f"{profil['nom']}.json"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(profil, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return chemin
