"""Les tableaux de garanties par formule, lus comme des tableaux (DEMARCHE 7.92).

À l'ingestion, les pages de tableaux sont ignorées (profil `pages_ignorees`) : lues comme du texte, leurs lignes
numérotées « 2.1 », « 2.5 » se confondaient avec les articles, et leurs cellules se mêlaient en phrases sans sens.
Mais un seul de ces tableaux dit ce qu'aucun article ne dit : quelle garantie est comprise dans quelle formule.
Le contenu du congélateur de l'assureur D n'est réservé à la formule Excellence que là (`f-d20`).

Ce module lit ce tableau par la position des mots sur la page : la ligne d'en-tête nomme les formules (ECO,
CONFORT, EXCELLENCE), chaque « X » ou « option » est rattaché à la colonne la plus proche. Le résultat est écrit
dans `regles/formules/<contrat>.json`, avec la page d'où il vient. Le lien entre une ligne du tableau et les
garanties des règles (« Contenu du congélateur » → `contenu_congelateur`) est écrit par le relecteur, dans le même
fichier (« correspondance ») : une nouvelle extraction le conserve. Le code vérifie ensuite qu'une garantie n'est
pas couverte, par les règles, dans une formule que le tableau ne lui donne pas (`couverture regles`).

La règle peut être plus étroite que le tableau (le vol des clés, une extension du vol, n'est que pour Confort et
Excellence), jamais plus large."""
from __future__ import annotations

import json
import re
from pathlib import Path

from ..analyse import prolog
from ..texte import normaliser

DOSSIER = prolog.DOSSIER / "formules"
MARQUES = {"x": "inclus", "option": "option"}


def chemin(contrat_id: str) -> Path:
    """Le fichier des formules d'un contrat (`regles/formules/<contrat>.json`)."""
    return DOSSIER / f"{contrat_id}.json"


def _lignes(mots: list[dict], tolerance: float = 3.0) -> list[list[dict]]:
    """Les mots regroupés par ligne (même hauteur, à `tolerance` points près), de haut en bas, de gauche à droite."""
    lignes: list[list[dict]] = []
    for m in sorted(mots, key=lambda m: (m["top"], m["x0"])):
        if lignes and abs(lignes[-1][0]["top"] - m["top"]) <= tolerance:
            lignes[-1].append(m)
        else:
            lignes.append([m])
    return [sorted(l, key=lambda m: m["x0"]) for l in lignes]


def lire_mots(mots: list[dict], formules: list[str]) -> dict:
    """Le tableau, à partir des mots d'une page (x0, x1, top, text). `formules` : les noms possibles des colonnes."""
    noms = {normaliser(f): f for f in formules}
    lignes = _lignes(mots)
    entete = next((l for l in lignes if sum(normaliser(m["text"]) in noms for m in l) >= 2), None)
    if entete is None:
        raise ValueError(f"aucune ligne d'en-tête ne nomme au moins deux formules parmi : {', '.join(formules)}")
    colonnes = [(noms[normaliser(m["text"])], (m["x0"] + m["x1"]) / 2, m["x0"]) for m in entete
                if normaliser(m["text"]) in noms]
    debut_colonnes = min(x0 for _, _, x0 in colonnes) - 5
    largeur = min((b[1] - a[1] for a, b in zip(colonnes, colonnes[1:])), default=60) / 2
    resultat = []
    for l in lignes[lignes.index(entete) + 1:]:
        libelle = " ".join(m["text"] for m in l if m["x1"] < debut_colonnes).strip()
        cellules = {"inclus": [], "option": []}
        for m in l:
            nature = MARQUES.get(m["text"].strip().lower())
            if nature is None or m["x1"] < debut_colonnes:
                continue
            centre = (m["x0"] + m["x1"]) / 2
            nom, cx, _ = min(colonnes, key=lambda c: abs(c[1] - centre))
            if abs(cx - centre) <= largeur:
                cellules[nature].append(nom)
        if libelle and (cellules["inclus"] or cellules["option"]):
            resultat.append({"libelle": libelle, **cellules})
    return {"formules": [c[0] for c in colonnes], "lignes": resultat}


def extraire(pdf: Path, page: int, contrat_id: str, formules: list[str]) -> dict:
    """Lit la page (numérotée à partir de 1) et écrit `regles/formules/<contrat>.json`, en gardant la correspondance
    déjà écrite par le relecteur."""
    import pdfplumber

    with pdfplumber.open(pdf) as doc:
        mots = doc.pages[page - 1].extract_words()
    tableau = lire_mots(mots, formules)
    ancien = json.loads(chemin(contrat_id).read_text(encoding="utf-8")) if chemin(contrat_id).exists() else {}
    doc = {"contrat": contrat_id, "source": {"fichier": pdf.name, "page": page}, **tableau,
           "correspondance": ancien.get("correspondance", {})}
    DOSSIER.mkdir(parents=True, exist_ok=True)
    chemin(contrat_id).write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return doc


def formules_des_regles(contrat_pl: str, garantie: str, toutes: list[str]) -> list[str] | None:
    """Les formules pour lesquelles le périmètre d'une garantie la laisse jouer ; None si la garantie n'existe pas."""
    if not re.search(rf"^garantie\({re.escape(garantie)},", contrat_pl, re.M):
        return None
    # Le périmètre et les circonstances : la formule est une circonstance (7.92), un ancien contrat la mettait au
    # périmètre. Une formule sous un « non » (« sauf formule Eco ») n'est pas comptée : la règle reste alors large.
    lignes = re.findall(rf"^(?:perimetre|circonstance)\({re.escape(garantie)},(.*)$", contrat_pl, re.M)
    citees = [f for l in lignes if "non(" not in l for f in re.findall(r"f\(formule, (\w+)\)", l)]
    return [f for f in toutes if f in citees] if citees else list(toutes)


def verifier(contrat_id: str, contrat_pl: str) -> tuple[list[str], list[str]]:
    """(problèmes, notes) : une garantie couverte par les règles dans une formule que le tableau ne lui donne pas
    est un problème ; une ligne du tableau sans correspondance, une note."""
    if not chemin(contrat_id).exists():
        return [], []
    doc = json.loads(chemin(contrat_id).read_text(encoding="utf-8"))
    toutes, problemes, notes = doc["formules"], [], []
    lignes = {l["libelle"]: l for l in doc["lignes"]}
    for libelle, garanties in doc.get("correspondance", {}).items():
        ligne = lignes.get(libelle)
        if ligne is None:
            problemes.append(f"tableau des formules : ligne inconnue « {libelle} »")
            continue
        for g in garanties:
            regle = formules_des_regles(contrat_pl, g, toutes)
            if regle is None:
                problemes.append(f"tableau des formules : garantie inconnue des règles « {g} » (ligne « {libelle} »)")
            elif set(regle) - set(ligne["inclus"]):
                problemes.append(f"garantie {g} : couverte par les règles en {', '.join(sorted(set(regle) - set(ligne['inclus'])))}, "
                                 f"que le tableau des formules ne lui donne pas (« {libelle} » : {', '.join(ligne['inclus']) or 'en option seulement'})")
    sans = [l for l in lignes if l not in doc.get("correspondance", {})]
    if sans:
        notes.append(f"tableau des formules : {len(sans)} ligne(s) sans garantie correspondante dans les règles")
    return problemes, notes
