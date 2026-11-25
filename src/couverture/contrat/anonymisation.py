"""Anonymisation du texte des contrats, à l'ingestion (DEMARCHE 7.160).

Le dépôt nomme les assureurs « A », « B », « C », « D » ; le texte de leurs conditions générales, lui, les nomme
en toutes lettres, avec leur assisteur, leur adresse et leurs numéros d'immatriculation. Ce texte est ce que
l'écran et la fiche citent. Une liste privée (`<donnees>/contrats/noms.prive.json`, jamais versionnée : elle
contient les vrais noms) dit, par contrat, ce qu'il faut remplacer et par quoi ; les courriels, les sites et les
numéros de téléphone le sont pour tout contrat qui figure dans la liste.

    {"assureur-x-habitation-2025": [{"motif": "Nom de l'assureur", "par": "Assureur X"},
                                    {"motif": "TVA LU [\\\\d ]+", "par": "TVA [numéro]", "regex": true}]}

Les motifs sont appliqués dans l'ordre de la liste (le plus long d'abord). Sans cette liste, rien n'est changé.

Ce que l'anonymisation ne fait pas : le texte reste celui de l'assureur, reconnaissable par qui le connaît ou le
cherche. Elle retire les noms, elle ne rend pas le texte publiable.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

FICHIER = "noms.prive.json"
GENERIQUES = [
    (re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"), "[courriel]"),
    (re.compile(r"(?:https?://\s?(?:www\.)?|www\.)[^\s,;)»]+[^\s,;)».]"), "[site]"),
    # Téléphones : international (+33 1 40 25 50 01, (+352) 44 24 24 - 1) ou national français (01 40 25 50 01,
    # 0 969 327 326). Pas les montants : ils n'ont ni « + » ni « 0 » en tête suivi de groupes de chiffres.
    (re.compile(r"\(?\+ ?\d{2,3}\)?(?:[ .]?\d{1,3}){3,5}(?: - \d\b)?"), "[téléphone]"),
    (re.compile(r"\b0 ?\d(?:[ .]\d{2,3}){3,4}\b\*?"), "[téléphone]"),
]


def chemin_noms(dossier_contrats: Path) -> Path:
    """Où se trouve la liste privée des noms à masquer : `COUVERTURE_NOMS`, sinon le fichier privé à côté des contrats."""
    return Path(os.environ.get("COUVERTURE_NOMS") or Path(dossier_contrats) / FICHIER)


def charger_noms(dossier_contrats: Path) -> dict:
    """La liste privée, par contrat ; vide si le fichier n'existe pas (rien n'est alors masqué)."""
    f = chemin_noms(dossier_contrats)
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def motifs(noms: dict, contrat_id: str) -> list[tuple[re.Pattern, str]]:
    """Les remplacements d'un contrat ; vide s'il n'est pas dans la liste. Un motif littéral accepte tout
    blanc là où il a une espace : un nom coupé par une fin de ligne est le même nom."""
    entrees = list(noms.get(contrat_id) or [])
    if not entrees:
        return []
    regles = []
    for e in entrees + list(noms.get("*") or []):
        motif = e["motif"] if e.get("regex") else r"\s+".join(re.escape(m) for m in e["motif"].split())
        regles.append((re.compile(motif), e["par"]))
    # Les courriels et les sites d'abord : ils contiennent les noms, et un nom masqué au milieu les couperait.
    return GENERIQUES + regles


def empreinte(noms: dict, contrat_id: str) -> str:
    """Entre dans l'empreinte du contrat : changer la liste relance son ingestion."""
    entrees = [noms.get(contrat_id) or [], noms.get("*") or []] if noms.get(contrat_id) else []
    return hashlib.sha256(json.dumps(entrees, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:8] if entrees else ""


def masquer(texte: str, regles: list[tuple[re.Pattern, str]]) -> tuple[str, int]:
    """Applique les remplacements dans l'ordre ; rend le texte masqué et le nombre de remplacements faits."""
    total = 0
    for motif, par in regles:
        texte, n = motif.subn(par, texte)
        total += n
    return texte, total


def masquer_clauses(clauses: list, regles: list[tuple[re.Pattern, str]]) -> int:
    """Masque le texte, le titre et le chemin de chaque clause, en place. Rend le nombre de remplacements."""
    total = 0
    if not regles:
        return 0
    for c in clauses:
        c.texte, n1 = masquer(c.texte, regles)
        c.titre, n2 = masquer(c.titre, regles)
        chemin = [masquer(x, regles) for x in c.chemin]
        c.chemin = [x for x, _ in chemin]
        total += n1 + n2 + sum(n for _, n in chemin)
    return total
