"""Étape 0 — Lecture et nettoyage des conditions générales.

Un PDF de CG réel contient beaucoup de bruit qui casse le découpage :
en-têtes et pieds de page répétés, numéros de page, sommaire avec points de
conduite, mots coupés en fin de ligne. On l'enlève ici, en gardant le numéro
de page de chaque ligne pour pouvoir citer « page 14 ».
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .texte import normaliser


@dataclass
class Ligne:
    page: int
    texte: str


def lire_pages(chemin: str | Path) -> list[str]:
    """Texte brut page par page."""
    chemin = Path(chemin)
    suffixe = chemin.suffix.lower()
    if suffixe in {".md", ".txt"}:
        return chemin.read_text(encoding="utf-8").split("\f")
    if suffixe == ".pdf":
        try:
            import pdfplumber

            with pdfplumber.open(str(chemin)) as pdf:
                return [p.extract_text(x_tolerance=1.5) or "" for p in pdf.pages]
        except ImportError:
            from pypdf import PdfReader

            return [p.extract_text() or "" for p in PdfReader(str(chemin)).pages]
    if suffixe == ".docx":
        import docx

        lignes = []
        for p in docx.Document(str(chemin)).paragraphs:
            style = (p.style.name or "").lower() if p.style is not None else ""
            prefixe = "## " if style.startswith(("heading", "titre")) else ""
            lignes.append(prefixe + p.text)
        return ["\n".join(lignes)]
    raise ValueError(f"Format non pris en charge : {suffixe} (attendu .md, .txt, .pdf ou .docx)")


_CHIFFRES = re.compile(r"\d+")
_POINTS_DE_CONDUITE = re.compile(r"(\.\s?){4,}\s*\d+\s*$|…{2,}\s*\d+\s*$")
_NUMERO_PAGE_SEUL = re.compile(r"^\s*(page\s*)?\d{1,3}(\s*/\s*\d{1,3})?\s*$", re.IGNORECASE)


def _signature(ligne: str) -> str:
    """Forme d'une ligne sans ses chiffres : « Page 12 / 60 » et « Page 13 / 60 » se ressemblent."""
    return _CHIFFRES.sub("#", normaliser(ligne))


def nettoyer(pages: list[str]) -> list[Ligne]:
    # Les puces des PDF sortent souvent en caractères privés (police Symbol/Wingdings) : on les normalise.
    pages = [re.sub(r"[\ue000-\uf8ff]", "•", p) for p in pages]
    pages_lignes = [[l.rstrip() for l in p.splitlines() if l.strip()] for p in pages]
    n = len(pages_lignes)

    # 1. En-têtes et pieds de page : lignes du haut ou du bas présentes sur au moins 40 % des pages.
    repetees: set[str] = set()
    if n >= 4:
        bords = Counter()
        for lignes in pages_lignes:
            bords.update({_signature(l) for l in lignes[:3] + lignes[-3:]})
        repetees = {sig for sig, k in bords.items() if k >= max(3, 0.4 * n)}

    sortie: list[Ligne] = []
    for num, lignes in enumerate(pages_lignes, start=1):
        # 2. Pages de sommaire : majorité de lignes terminées par un numéro de page.
        termine_par_num = sum(bool(re.search(r"\s\d{1,3}\s*$", l)) for l in lignes)
        tete = normaliser(" ".join(lignes[:4]))
        titre_sommaire = "sommaire" in tete or "table des matieres" in tete
        # Suite de sommaire sans titre : dans les premières pages, presque toutes les lignes finissent par un numéro.
        if lignes and termine_par_num > 0.5 * len(lignes) and (titre_sommaire or (num <= 6 and termine_par_num >= 5)):
            continue
        for l in lignes:
            if _signature(l) in repetees or _NUMERO_PAGE_SEUL.match(l) or _POINTS_DE_CONDUITE.search(l):
                continue
            # 3. Mot coupé en fin de ligne : « garan-» + « tie » → « garantie ».
            # On ne recolle que les lignes pleines, pour ne pas fusionner « lave-» d'une liste.
            if sortie and sortie[-1].texte.endswith("-") and len(sortie[-1].texte) >= 50 and l[:1].islower():
                sortie[-1].texte = sortie[-1].texte[:-1] + l.strip()
                continue
            sortie.append(Ligne(page=num, texte=l.strip()))
    return sortie


def charger_lignes(chemin: str | Path) -> list[Ligne]:
    return nettoyer(lire_pages(chemin))


def charger_texte(chemin: str | Path) -> str:
    """Texte nettoyé d'un seul tenant (sert à la méthode « document brut »)."""
    return "\n".join(l.texte for l in charger_lignes(chemin))
