"""Profils d'assureur : les règles de lecture propres à un assureur.

L'équivalent de `config/sources.yaml` dans SortirIA. Les règles générales de
`segmentation.py` couvrent la plupart des contrats ; quand un assureur rédige
autrement (« Les cas non couverts » au lieu de « Exclusions »), on ne touche pas
au code : on écrit un profil, réutilisé pour toutes les versions de ses contrats.

Un profil est un fichier JSON dans `<donnees>/profils/<nom>.json` :
{
  "nom": "assureur-a",
  "intertitres": {"les cas non couverts": "exclusion", "ce que signifient les mots": "definition"},
  "lignes_ignorees": ["^Assureur A S\\.A\\. .*$"],
  "lexique": "auto",             // "auto", "deux_points" (Terme : définition), "terme_seul" ou "puce" (■ puis le terme)
  "colonnes": 2,                 // facultatif : pages en deux colonnes, lues colonne par colonne (7.87)
  "pages_ignorees": [[11, 23]],  // facultatif : pages sautées (tableaux récapitulatifs)
  "titres_numerotes": "articles",// facultatif : seuls « Article 3 », « Art. 3 », « ART 3 » ouvrent une clause
  "titres": ["Vol", "Bris de glaces"] // facultatif : un contrat sans numéros ; ses titres de section, pris au sommaire
}
Le catalogue des contrats désigne le profil : "profil": "assureur-a".

Un profil s'écrit à la main quand le découpage d'un contrat est signalé à vérifier
(l'agent de réparation qui en proposait a été retiré le 18 nov. 2026, voir DEMARCHE 7.36).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from ..texte import normaliser

TYPES_PERMIS = {"garantie", "exclusion", "condition", "limite", "definition"}
FORMATS_LEXIQUE = {"auto", "deux_points", "terme_seul", "puce"}


class ProfilInvalide(ValueError):
    """Un profil d'assureur absent ou mal formé."""

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
    pages = profil.get("pages_ignorees") or []
    if not all(isinstance(p, list) and len(p) == 2 and all(isinstance(x, int) for x in p) and p[0] <= p[1] for p in pages):
        raise ProfilInvalide("pages_ignorees : une liste d'intervalles [début, fin].")
    numeros = profil.get("titres_numerotes", "tous")
    if numeros not in ("tous", "articles"):
        raise ProfilInvalide(f"titres_numerotes : « tous » ou « articles », pas « {numeros} ».")
    colonnes = profil.get("colonnes", 1)
    if colonnes not in (1, 2):
        raise ProfilInvalide(f"Nombre de colonnes non pris en charge : {colonnes} (1 ou 2).")
    sortie = {"nom": nom, "intertitres": intertitres, "lignes_ignorees": ignorees, "lexique": lexique}
    # Les clés facultatives ne sont écrites que si elles changent quelque chose : l'empreinte des profils
    # existants (qui fait partie de celle du contrat) ne bouge pas.
    if colonnes == 2:
        sortie["colonnes"] = 2
    if pages:
        sortie["pages_ignorees"] = pages
    if numeros == "articles":
        sortie["titres_numerotes"] = "articles"
    titres = [str(t).strip() for t in profil.get("titres") or []]
    if any(not 2 <= len(t) <= 120 for t in titres):
        raise ProfilInvalide("titres : des titres de section de 2 à 120 caractères.")
    if titres:
        sortie["titres"] = titres
    return sortie


def charger_profil(dossier: str | Path, nom: str) -> dict:
    """Lit et valide le profil `<dossier>/<nom>.json` ; `ProfilInvalide` s'il manque."""
    chemin = Path(dossier) / f"{nom}.json"
    if not chemin.exists():
        raise ProfilInvalide(f"Profil introuvable : {chemin}")
    return valider_profil(json.loads(chemin.read_text(encoding="utf-8")))

