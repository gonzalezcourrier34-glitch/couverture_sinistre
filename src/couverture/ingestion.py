"""Ingestion : fichier de CG → clauses contrôlées → base.

Les métadonnées (assureur, produit, version) viennent de `catalogue.json`, placé à côté
des contrats. Un fichier non référencé reçoit un identifiant tiré de son nom.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from . import anonymisation
from .base import Base, Contrat
from .chargement import charger_lignes
from .controles import controler
from .segmentation import segmenter_lignes
from .texte import normaliser

FORMATS = {".pdf", ".md", ".txt", ".docx"}
# Fichiers de documentation rangés avec les contrats, qui n'en sont pas.
# SOURCES.prive.md (les vrais noms, 7.70) a été ingéré comme un contrat le 20 nov. : tout « sources* » est ignoré.
IGNORES = {"sources.md", "sources.prive.md", "readme.md", "lisezmoi.md"}


def identifiant(fichier: Path) -> str:
    return re.sub(r"[^a-z0-9]+", "-", normaliser(fichier.stem)).strip("-")


def charger_catalogue(dossier: Path) -> dict:
    chemin = dossier / "catalogue.json"
    return json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists() else {}


def ingerer_fichier(fichier: str | Path, base: Base, meta: dict | None = None, forcer: bool = False,
                    profil: dict | None = None, noms: dict | None = None) -> Contrat:
    """Lit, découpe, contrôle et enregistre un contrat.
    `profil` : règles propres à l'assureur (voir `profils.py`), qui font partie de l'empreinte :
    changer le profil relance le découpage.
    `noms` : la liste privée des noms à masquer (voir `anonymisation.py`) ; elle aussi entre dans l'empreinte.
    Le masquage vient après le découpage, pour ne pas le changer : il porte sur les clauses et sur le texte brut."""
    fichier = Path(fichier)
    meta = meta or {}
    contrat_id = meta.get("id") or identifiant(fichier)
    regles_noms = anonymisation.motifs(noms or {}, contrat_id)
    contenu = (fichier.read_bytes() + json.dumps(profil or {}, sort_keys=True).encode()
               + anonymisation.empreinte(noms or {}, contrat_id).encode())
    empreinte = hashlib.sha256(contenu).hexdigest()[:16]

    if not forcer and base.empreinte(contrat_id) == empreinte:
        return base.contrat(contrat_id)  # fichier inchangé : rien à redécouper

    lignes = charger_lignes(fichier, (profil or {}).get("colonnes", 1))
    clauses = segmenter_lignes(lignes, profil)
    masques = anonymisation.masquer_clauses(clauses, regles_noms)
    rapport = controler(clauses)
    if regles_noms:
        rapport["noms_masques"] = masques
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
    base.enregistrer(contrat, clauses, anonymisation.masquer("\n".join(l.texte for l in lignes), regles_noms)[0])
    return contrat


def fichiers_contrats(dossier: Path) -> list[Path]:
    return [f for f in sorted(dossier.iterdir())
            if f.suffix.lower() in FORMATS and f.name.lower() not in IGNORES and not f.name.lower().startswith("sources")
            and not f.name.startswith((".", "~$"))]


def ingerer_dossier(dossier: str | Path, base: Base, forcer: bool = False, barre=None) -> list[Contrat]:
    """Tous les contrats du dossier, avec les métadonnées de `catalogue.json` et, si le catalogue
    en désigne un, le profil d'assureur (`<donnees>/profils/<nom>.json`). Les contrats dont le
    fichier n'est plus dans le dossier sont retirés de la base : elle reflète le dossier."""
    from .profils import charger_profil

    dossier = Path(dossier)
    catalogue = charger_catalogue(dossier)
    noms = anonymisation.charger_noms(dossier)
    contrats = []
    for f in fichiers_contrats(dossier):
        meta = catalogue.get(f.name) or {}
        profil = charger_profil(dossier.parent / "profils", meta.get("profil")) if meta.get("profil") else None
        contrats.append(ingerer_fichier(f, base, meta, forcer=forcer, profil=profil, noms=noms))
        if barre is not None:
            barre.avancer(f.name)
    gardes = {c.id for c in contrats}
    for ancien in base.contrats():
        if ancien.id not in gardes:
            base.supprimer(ancien.id)
    return contrats
