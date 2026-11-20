"""Ingestion : fichier de CG → clauses contrôlées → base.

Les métadonnées (assureur, produit, version) viennent de `catalogue.json`, placé à côté
des contrats. Un fichier non référencé reçoit un identifiant tiré de son nom.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .base import Base, Contrat
from .chargement import charger_lignes
from .controles import controler
from .segmentation import segmenter_lignes
from .texte import normaliser

FORMATS = {".pdf", ".md", ".txt", ".docx"}
# Fichiers de documentation rangés avec les contrats, qui n'en sont pas.
IGNORES = {"sources.md", "readme.md", "lisezmoi.md"}


def identifiant(fichier: Path) -> str:
    return re.sub(r"[^a-z0-9]+", "-", normaliser(fichier.stem)).strip("-")


def charger_catalogue(dossier: Path) -> dict:
    chemin = dossier / "catalogue.json"
    return json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists() else {}


def ingerer_fichier(fichier: str | Path, base: Base, meta: dict | None = None, forcer: bool = False,
                    profil: dict | None = None) -> Contrat:
    """Lit, découpe, contrôle et enregistre un contrat.
    `profil` : règles propres à l'assureur (voir `profils.py`), qui font partie de l'empreinte :
    changer le profil relance le découpage."""
    fichier = Path(fichier)
    meta = meta or {}
    contrat_id = meta.get("id") or identifiant(fichier)
    contenu = fichier.read_bytes() + json.dumps(profil or {}, sort_keys=True).encode()
    empreinte = hashlib.sha256(contenu).hexdigest()[:16]

    if not forcer and base.empreinte(contrat_id) == empreinte:
        return base.contrat(contrat_id)  # fichier inchangé : rien à redécouper

    lignes = charger_lignes(fichier, (profil or {}).get("colonnes", 1))
    clauses = segmenter_lignes(lignes, profil)
    rapport = controler(clauses)
    contrat = Contrat(
        id=contrat_id,
        assureur=meta.get("assureur", ""),
        produit=meta.get("produit", ""),
        version=meta.get("version", ""),
        fichier=fichier.name,
        empreinte=empreinte,
        statut=rapport["statut"],
        rapport=rapport,
    )
    base.enregistrer(contrat, clauses, "\n".join(l.texte for l in lignes))
    return contrat


def fichiers_contrats(dossier: Path) -> list[Path]:
    return [f for f in sorted(dossier.iterdir())
            if f.suffix.lower() in FORMATS and f.name.lower() not in IGNORES and not f.name.startswith((".", "~$"))]


def ingerer_dossier(dossier: str | Path, base: Base, forcer: bool = False, barre=None) -> list[Contrat]:
    """Tous les contrats du dossier, avec les métadonnées de `catalogue.json` et, si le catalogue
    en désigne un, le profil d'assureur (`<donnees>/profils/<nom>.json`). Les contrats dont le
    fichier n'est plus dans le dossier sont retirés de la base : elle reflète le dossier."""
    from .profils import charger_profil

    dossier = Path(dossier)
    catalogue = charger_catalogue(dossier)
    contrats = []
    for f in fichiers_contrats(dossier):
        meta = catalogue.get(f.name) or {}
        profil = charger_profil(dossier.parent / "profils", meta.get("profil")) if meta.get("profil") else None
        contrats.append(ingerer_fichier(f, base, meta, forcer=forcer, profil=profil))
        if barre is not None:
            barre.avancer(f.name)
    gardes = {c.id for c in contrats}
    for ancien in base.contrats():
        if ancien.id not in gardes:
            base.supprimer(ancien.id)
    return contrats
