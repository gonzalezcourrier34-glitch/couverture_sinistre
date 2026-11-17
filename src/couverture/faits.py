"""Étape 2 — Extraction des faits du sinistre et enrichissement de la requête.

Le vocabulaire du client (« on m'a piqué mon vélo ») n'est pas celui du contrat
(« vol », « biens mobiliers », « dépendance »). Ce lexique fait le pont.
"""

from __future__ import annotations

import re

from .models import Faits
from .texte import normaliser

# racine trouvée dans la description -> termes contractuels à ajouter à la requête
EVENEMENTS: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "vol": (("vol", "derob", "pique", "cambriol", "arrach", "disparu"), ("vol", "effraction", "violence")),
    "incendie": (("incendi", "feu", "flamme", "brul", "bougie", "cigarette", "fume"), ("incendie", "flamme", "brulure", "objet incandescent")),
    "degat_des_eaux": (("fuite", "eau", "inond", "lave-linge", "lave-vaisselle", "tuyau", "deborde"), ("degats des eaux", "fuite", "conduite", "appareil a effet d'eau")),
    "bris": (("bris", "casse", "fissur", "eclat", "vitre", "miroir"), ("bris", "vitre", "verre")),
    "dommage_accidentel": (("renvers", "tomb", "tache", "raye", "abime", "endommag"), ("dommages accidentels", "mobilier", "tache", "rayure")),
    "responsabilite": (("voisin", "tiers", "blesse", "chez un ami"), ("responsabilite civile", "tiers")),
}

BIENS: dict[str, tuple[str, ...]] = {
    "velo": ("velo", "bicyclette", "trottinette"),
    "mobilier": ("table", "canape", "chaise", "meuble", "parquet", "rideau", "nappe", "armoire", "lit"),
    "electronique": ("telephone", "ordinateur", "television", "tablette", "console"),
    "objet_de_valeur": ("bijou", "montre", "bague", "collier", "tableau"),
}

LIEUX: dict[str, tuple[str, ...]] = {
    "habitation": ("chez moi", "appartement", "maison", "salon", "cuisine", "chambre", "domicile"),
    "dependance": ("cave", "garage", "box", "grenier", "abri de jardin"),
    "parties_communes": ("local a velo", "local commun", "hall", "parking commun", "parties communes", "local a velos"),
    "exterieur": ("rue", "travail", "gare", "devant", "parking", "en ville", "poteau"),
}

CIRCONSTANCES: dict[str, tuple[str, ...]] = {
    "effraction": ("force", "fracture", "casse la porte", "serrure", "cadenas", "effraction"),
    "ferme_a_cle": ("ferme a cle", "fermee a cle", "verrouill"),
    "sans_flammes": ("sans flamme", "pas de flamme", "sans feu"),
    "antivol": ("antivol", "attache", "cadenas"),
    "violence": ("arrach", "agress", "menace", "violence"),
    "badge": ("badge", "digicode"),
}

TERMES_CONTRAT: dict[str, tuple[str, ...]] = {
    "velo": ("velos", "biens mobiliers"),
    "mobilier": ("mobilier", "biens mobiliers"),
    "dependance": ("dependance", "ferme a cle"),
    "parties_communes": ("parties communes", "local a velos collectif"),
    "exterieur": ("hors des locaux", "option mobilite"),
}


def _detecter(texte: str, table: dict) -> list[str]:
    trouves = []
    for nom, valeur in table.items():
        declencheurs = valeur[0] if isinstance(valeur[0], tuple) else valeur
        # Le déclencheur doit commencer un mot : « eau » ne doit pas matcher « bureau ».
        if any(re.search(r"(?<![a-z])" + re.escape(d), texte) for d in declencheurs):
            trouves.append(nom)
    return trouves


def extraire_faits(description: str) -> Faits:
    texte = normaliser(description)
    return Faits(
        evenements=_detecter(texte, EVENEMENTS),
        biens=_detecter(texte, BIENS),
        lieux=_detecter(texte, LIEUX),
        circonstances=_detecter(texte, CIRCONSTANCES),
    )


def enrichir_requete(description: str, faits: Faits) -> str:
    ajouts: list[str] = []
    for evt in faits.evenements:
        ajouts.extend(EVENEMENTS[evt][1])
    for cle in faits.biens + faits.lieux:
        ajouts.extend(TERMES_CONTRAT.get(cle, ()))
    return description + " " + " ".join(ajouts)
