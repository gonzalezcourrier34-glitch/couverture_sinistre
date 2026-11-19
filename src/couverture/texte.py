"""Normalisation du français : minuscules, accents, ligatures, apostrophes, espaces."""

from __future__ import annotations

import re
import unicodedata


def sans_accents(texte: str) -> str:
    decompose = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in decompose if not unicodedata.combining(c))


def normaliser(texte: str) -> str:
    """Minuscules, sans accents, ligatures et apostrophes harmonisées, espaces compactés."""
    texte = texte.replace("œ", "oe").replace("Œ", "oe").replace("’", "'")
    texte = sans_accents(texte.lower())
    return re.sub(r"\s+", " ", texte).strip()

