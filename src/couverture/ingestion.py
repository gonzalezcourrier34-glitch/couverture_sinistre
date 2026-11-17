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


def identifiant(fichier: Path) -> str:
    return re.sub(r"[^a-z0-9]+", "-", normaliser(fichier.stem)).strip("-")


def charger_catalogue(dossier: Path) -> dict:
    chemin = dossier / "catalogue.json"
    return json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists() else {}


def calculer_vecteurs(contrat_id: str, clauses: list, base: Base, vectoriseur) -> str:
    """Embeddings de toutes les clauses, une fois à l'ingestion. Une panne ne bloque jamais
    l'ingestion (comme le juge de qualité de SortirIA) : la recherche se fera par les mots seuls."""
    from .recherche import texte_a_vectoriser

    try:
        vecteurs = vectoriseur.vectoriser([texte_a_vectoriser(c) for c in clauses])
    except Exception as e:  # noqa: BLE001
        return f"échec ({e}) : recherche par les mots seuls"
    base.enregistrer_vecteurs(contrat_id, vectoriseur.nom, {c.id: v for c, v in zip(clauses, vecteurs)})
    return f"{len(vecteurs)} vecteurs ({vectoriseur.nom})"


def juger(contrat: Contrat, clauses: list, base: Base, juge_qualite) -> None:
    """Juge de qualité (voir `qualite.py`) : ajoute son score au rapport, et peut faire passer le contrat
    à A_VERIFIER. L'échantillon dépend de l'empreinte : même contrat, même échantillon."""
    from .controles import controler
    from .qualite import appliquer, juger_qualite

    qualite = juger_qualite(clauses, juge_qualite, graine=contrat.empreinte)
    base_rapport = {**controler(clauses), **{k: v for k, v in contrat.rapport.items() if k == "embeddings"}}
    contrat.rapport = appliquer(base_rapport, qualite)
    contrat.statut = contrat.rapport["statut"]
    base.maj_rapport(contrat.id, contrat.rapport)


def ingerer_fichier(fichier: str | Path, base: Base, meta: dict | None = None, forcer: bool = False,
                    vectoriseur=None, profil: dict | None = None, juge_qualite=None) -> Contrat:
    """Lit, découpe, contrôle et enregistre un contrat ; calcule ses embeddings si un vectoriseur est donné.
    `profil` : règles propres à l'assureur (voir `profils.py`), qui font partie de l'empreinte :
    changer le profil relance le découpage."""
    fichier = Path(fichier)
    meta = meta or {}
    contrat_id = meta.get("id") or identifiant(fichier)
    contenu = fichier.read_bytes() + json.dumps(profil or {}, sort_keys=True).encode()
    empreinte = hashlib.sha256(contenu).hexdigest()[:16]

    if not forcer and base.empreinte(contrat_id) == empreinte:
        contrat = base.contrat(contrat_id)  # fichier inchangé : rien à redécouper
        if vectoriseur and not base.vecteurs(contrat_id, vectoriseur.nom):
            # Clé ajoutée après la première ingestion : seuls les embeddings manquent.
            contrat.rapport["embeddings"] = calculer_vecteurs(contrat_id, base.clauses(contrat_id), base, vectoriseur)
            base.maj_rapport(contrat_id, contrat.rapport)
        if juge_qualite and "score" not in contrat.rapport.get("qualite", {}):
            juger(contrat, base.clauses(contrat_id), base, juge_qualite)
        return contrat

    lignes = charger_lignes(fichier)
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
    if vectoriseur:
        contrat.rapport["embeddings"] = calculer_vecteurs(contrat_id, clauses, base, vectoriseur)
        base.maj_rapport(contrat_id, contrat.rapport)
    if juge_qualite:
        juger(contrat, clauses, base, juge_qualite)
    return contrat


def ingerer_dossier(dossier: str | Path, base: Base, forcer: bool = False, vectoriseur=None,
                    juge_qualite=None) -> list[Contrat]:
    """Tous les contrats du dossier, avec les métadonnées de `catalogue.json` et, si le catalogue
    en désigne un, le profil d'assureur (`<donnees>/profils/<nom>.json`)."""
    from .profils import charger_profil

    dossier = Path(dossier)
    catalogue = charger_catalogue(dossier)
    contrats = []
    for f in sorted(dossier.iterdir()):
        if f.suffix.lower() not in FORMATS:
            continue
        meta = catalogue.get(f.name) or {}
        profil = charger_profil(dossier.parent / "profils", meta.get("profil")) if meta.get("profil") else None
        contrats.append(ingerer_fichier(f, base, meta, forcer=forcer, vectoriseur=vectoriseur, profil=profil,
                                        juge_qualite=juge_qualite))
    return contrats
