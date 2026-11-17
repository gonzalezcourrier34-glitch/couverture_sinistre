"""Normalisation du français : accents, mots vides, racinisation légère."""

from __future__ import annotations

import re
import unicodedata

MOTS_VIDES = set(
    """
    a au aux avec ce ces cet cette dans de des du elle en et eux il ils je la le les leur lui ma mais me
    meme mes moi mon ne nos notre nous on ou par pas pour qu que qui sa se ses son sur ta te tes toi ton
    tu un une vos votre vous y d l j m n s t c est sont ete etre avoir ont a lorsqu lorsque si sauf
    tout toute tous toutes plus ni dont ainsi
    """.split()
)

_SUFFIXES = (
    "issements", "issement", "ements", "ement", "ations", "ation", "ances", "ance",
    "ences", "ence", "euses", "euse", "eurs", "eur", "ives", "ive", "ifs", "if",
    "ees", "ee", "es", "e", "s", "x",
)


def sans_accents(texte: str) -> str:
    decompose = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in decompose if not unicodedata.combining(c))


def normaliser(texte: str) -> str:
    """Minuscules, sans accents, ligatures et apostrophes harmonisées, espaces compactés."""
    texte = texte.replace("œ", "oe").replace("Œ", "oe").replace("’", "'")
    texte = sans_accents(texte.lower())
    return re.sub(r"\s+", " ", texte).strip()


def mots(texte: str) -> list[str]:
    return [m for m in re.findall(r"[a-z0-9]+", normaliser(texte)) if m not in MOTS_VIDES and len(m) > 1]


def raciniser(mot: str) -> str:
    for suffixe in _SUFFIXES:
        if mot.endswith(suffixe) and len(mot) - len(suffixe) >= 4:
            return mot[: -len(suffixe)]
    return mot


def jetons(texte: str) -> list[str]:
    return [raciniser(m) for m in mots(texte)]
