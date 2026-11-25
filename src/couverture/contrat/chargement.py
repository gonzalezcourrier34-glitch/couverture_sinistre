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

from ..texte import normaliser


@dataclass
class Ligne:
    """Une ligne du document, avec sa page (pour pouvoir citer « page 14 »)."""

    page: int
    texte: str


def lire_pages(chemin: str | Path, colonnes: int = 1) -> list[str]:
    """Texte brut page par page. `colonnes` = 2 (profil d'assureur) : les pages mises en deux colonnes sont lues
    colonne après colonne, au lieu de ligne à ligne à travers la page (7.87)."""
    chemin = Path(chemin)
    suffixe = chemin.suffix.lower()
    if suffixe in {".md", ".txt"}:
        return chemin.read_text(encoding="utf-8").split("\f")
    if suffixe == ".pdf":
        try:
            import pdfplumber

            with pdfplumber.open(str(chemin)) as pdf:
                if colonnes == 2:
                    return [_deux_colonnes(p) for p in pdf.pages]
                return [p.extract_text(**_ecart(p)) or "" for p in pdf.pages]
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


def _ecart(page) -> dict:
    """La tolérance d'espacement pour lire les mots d'une page. Par défaut 1,5 point entre deux lettres. Certaines
    pages ont des lettres espacées (une police dont les largeurs manquent au PDF) : presque tous les « mots » y
    font une ou deux lettres (« L e s di s p o siti o n s »). Pour celles-là, l'écart toléré suit la taille des
    caractères (7.148) ; les autres pages sont lues comme avant."""
    mots = page.extract_words(x_tolerance=1.5, keep_blank_chars=False)
    if len(mots) >= 40 and sum(len(m["text"]) <= 2 for m in mots) > 0.6 * len(mots):
        return {"x_tolerance_ratio": 0.7}
    return {"x_tolerance": 1.5}


def _deux_colonnes(page) -> str:
    """Une page en deux colonnes, lue colonne par colonne. La gouttière est la verticale, entre 40 et 60 % de la
    largeur, que le moins de mots traversent ; si plus de 3 % des mots la traversent, ou si une colonne est presque
    vide, la page est lue comme une seule colonne. Les lignes qui traversent la gouttière (un titre sur toute la
    largeur) coupent la page en bandes : chaque bande est lue colonne gauche puis colonne droite."""
    ecart = _ecart(page)
    mots = page.extract_words(keep_blank_chars=False, **ecart)
    if len(mots) < 40:
        return page.extract_text(**ecart) or ""
    # La gouttière : parmi les verticales de 40 à 60 % de la largeur, celle que le moins de mots traversent.
    x, n = min(((page.width * i / 100, sum(1 for m in mots if m["x0"] < page.width * i / 100 < m["x1"]))
                for i in range(40, 61)), key=lambda t: t[1])
    gauche = sum(m["x1"] <= x for m in mots)
    if n > 0.03 * len(mots) or gauche < 0.2 * len(mots) or len(mots) - gauche - n < 0.2 * len(mots):
        return page.extract_text(**ecart) or ""
    # Les mots regroupés en lignes : même hauteur, à 2 points près.
    lignes: list[list[dict]] = []
    for m in sorted(mots, key=lambda m: (round(m["top"]), m["x0"])):
        if lignes and abs(lignes[-1][0]["top"] - m["top"]) <= 2:
            lignes[-1].append(m)
        else:
            lignes.append([m])
    sortie, g, d = [], [], []

    def vider():
        sortie.extend(g + d)
        g.clear()
        d.clear()

    def texte(ms):
        return " ".join(m["text"] for m in sorted(ms, key=lambda m: m["x0"]))

    for ligne in lignes:
        # Une ligne qui traverse la gouttière (un titre sur toute la largeur) ferme la bande en cours :
        # on écrit d'abord ce qui précède, colonne gauche puis colonne droite.
        if any(m["x0"] < x < m["x1"] for m in ligne):
            vider()
            sortie.append(texte(ligne))
            continue
        cg, cd = [m for m in ligne if m["x1"] <= x], [m for m in ligne if m["x0"] >= x]
        if cg:
            g.append(texte(cg))
        if cd:
            d.append(texte(cd))
    vider()
    return "\n".join(sortie)


_CHIFFRES = re.compile(r"\d+")
_POINTS_DE_CONDUITE = re.compile(r"(\.\s?){4,}\s*\d+\s*$|…{2,}\s*\d+\s*$")
_NUMERO_PAGE_SEUL = re.compile(r"^\s*(page\s*)?\d{1,3}(\s*/\s*\d{1,3})?\s*$", re.IGNORECASE)


def _signature(ligne: str) -> str:
    """Forme d'une ligne sans ses chiffres : « Page 12 / 60 » et « Page 13 / 60 » se ressemblent."""
    return _CHIFFRES.sub("#", normaliser(ligne))


def nettoyer(pages: list[str]) -> list[Ligne]:
    """Retire le bruit des pages : en-têtes et pieds de page répétés, pages de sommaire, mots coupés en fin de ligne.
    Rend les lignes utiles, chacune avec sa page."""
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


def charger_lignes(chemin: str | Path, colonnes: int = 1) -> list[Ligne]:
    """Lit un fichier de conditions générales et rend ses lignes nettoyées ; `colonnes=2` pour des pages en deux colonnes."""
    return nettoyer(lire_pages(chemin, colonnes))

