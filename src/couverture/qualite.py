"""Juge de qualité à l'ingestion : les clauses ont-elles le bon type ?

Les contrôles (`controles.py`) vérifient qu'un contrat a des garanties et des exclusions.
Ils ne vérifient pas que ce sont les bonnes : une exclusion typée « garantie » passe
les contrôles, et peut faire dire « couvert » à tort.

Comme le juge de qualité de SortirIA (`agent/nodes.py:judge_quality`) :
  - un échantillon de clauses, tiré de façon reproductible (même contrat, même échantillon) ;
  - Mistral dit, pour chacune, si son type est juste, et lequel il proposerait ;
  - le score est la part de types confirmés ; sous le seuil, le contrat passe « à vérifier »
    et les erreurs relevées guident l'agent de réparation ;
  - une panne du juge ne bloque jamais l'ingestion : le score est simplement absent.
"""

from __future__ import annotations

import json
import random

from .juges import extraire_json
from .llm import LLM
from .models import Clause, TypeClause

TAILLE_ECHANTILLON = 16
SEUIL = 0.8
TYPES_JUGES = [TypeClause.GARANTIE, TypeClause.EXCLUSION, TypeClause.CONDITION, TypeClause.LIMITE, TypeClause.DEFINITION]

SYSTEME_QUALITE = """Tu contrôles le découpage automatique des conditions générales d'un contrat d'assurance. Chaque extrait a reçu un type :
- garantie : décrit ce qui est couvert ;
- exclusion : décrit ce qui n'est pas couvert ;
- condition : une obligation de l'assuré ou une condition d'application (fermer à clé, déclarer dans un délai…) ;
- limite : plafond, franchise, vétusté, modalité d'indemnisation ;
- definition : définit un terme du contrat.

Pour chaque extrait, dis si le type est juste. Un extrait qui mélange plusieurs natures est juste si son type correspond à l'essentiel de son contenu.

Réponds uniquement par un objet JSON :
{"jugements": [{"id": "…", "juste": true, "type_propose": "exclusion", "raison": "une phrase"}]}"""


def echantillon(clauses: list[Clause], graine: str, taille: int = TAILLE_ECHANTILLON) -> list[Clause]:
    """Échantillon stratifié par type (chaque type est représenté), reproductible pour une même graine."""
    hasard = random.Random(graine)
    par_type = {t: [c for c in clauses if c.type == t] for t in TYPES_JUGES}
    choisies: list[Clause] = []
    tour = 0
    while len(choisies) < taille and any(par_type.values()):
        t = TYPES_JUGES[tour % len(TYPES_JUGES)]
        if par_type[t]:
            choisies.append(par_type[t].pop(hasard.randrange(len(par_type[t]))))
        tour += 1
    return choisies


def juger_qualite(clauses: list[Clause], llm: LLM, graine: str, seuil: float = SEUIL) -> dict:
    """Renvoie {"score", "echantillon", "erreurs": [{clause_id, titre, type, type_propose, raison}], "seuil", "modele"}
    ou {"erreur": …} si le juge n'a pas pu répondre."""
    choisies = echantillon(clauses, graine)
    if not choisies:
        return {"erreur": "aucune clause typée à juger"}
    extraits = [
        {"id": c.id, "type": c.type.value, "titres": " > ".join(c.chemin), "texte": c.texte[:1200]} for c in choisies
    ]
    try:
        reponse = extraire_json(llm.completer(SYSTEME_QUALITE, json.dumps(extraits, ensure_ascii=False, indent=1)))
        jugements = {str(j.get("id")): j for j in reponse.get("jugements", [])}
    except Exception as e:  # noqa: BLE001 (le juge est un contrôle, pas une étape indispensable)
        return {"erreur": str(e), "modele": llm.nom}

    erreurs, juges = [], 0
    for c in choisies:
        j = jugements.get(c.id)
        if j is None:
            continue
        juges += 1
        propose = str(j.get("type_propose", "")).strip().lower()
        if not j.get("juste", True) and propose != c.type.value:
            erreurs.append({"clause_id": c.id, "titre": c.titre, "type": c.type.value,
                            "type_propose": propose, "raison": str(j.get("raison", ""))})
    if not juges:
        return {"erreur": "le juge n'a jugé aucun extrait", "modele": llm.nom}
    return {
        "score": round((juges - len(erreurs)) / juges, 3),
        "echantillon": juges,
        "erreurs": erreurs,
        "seuil": seuil,
        "modele": llm.nom,
    }


def appliquer(rapport: dict, qualite: dict) -> dict:
    """Ajoute le jugement au rapport des contrôles ; sous le seuil, une alerte et le statut A_VERIFIER."""
    rapport = {**rapport, "qualite": qualite}
    score = qualite.get("score")
    if score is not None and score < qualite.get("seuil", SEUIL):
        titres = ", ".join(f"« {e['titre']} » ({e['type']} → {e['type_propose']})" for e in qualite["erreurs"][:4])
        rapport["alertes"] = rapport.get("alertes", []) + [
            f"Typage douteux selon le juge de qualité ({score:.0%} de types confirmés) : {titres}."
        ]
        rapport["statut"] = "A_VERIFIER"
    return rapport
