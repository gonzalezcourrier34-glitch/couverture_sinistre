"""`couverture juger` : la lecture des clauses (DEMARCHE 7.188), à l'essai.

Le modèle désigne les chapitres, puis juge chaque clause attendue ; le code décide. Deux appels au modèle par
déclaration, sur un dossier de quelques milliers de mots : c'est une commande payante, à lancer aux moments
choisis. La chaîne de règles n'est pas appelée ici (`--regles` pour la contresignature, qui coûte ses appels).

  couverture juger --contrat assureur-a-habitation-2025 "De l'eau a coulé du plafond…"
  couverture juger --contrat assureur-b-habitation-2017 --jeu aveugle --cas av-b05 --cas av-b13
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from ..contrat.base import Base
from ..mesure.evaluation import JEUX_FERMES, charger_cas, fichiers_jeu


def ajouter(sous) -> None:
    """Déclare la commande « juger » et ses options."""
    p = sous.add_parser("juger", help="À l'essai : juger un sinistre clause par clause (appels payants au modèle)")
    p.add_argument("--contrat", required=True)
    p.add_argument("sinistre", nargs="?", help="La déclaration ; ou bien --jeu et --cas")
    p.add_argument("--jeu", choices=JEUX_FERMES, help="Prendre les déclarations d'un jeu écrit à l'aveugle")
    p.add_argument("--cas", action="append", default=[], help="Un cas du jeu (répétable) ; sans --cas, tout le jeu")
    p.add_argument("--modele", default="mistral-large-latest", help="Le modèle qui désigne et qui juge")
    p.add_argument("--regles", action="store_true", help="Demander aussi la chaîne de règles, pour la contresignature")
    p.add_argument("--detail", action="store_true", help="Afficher chaque jugement qui n'est pas « sans effet »")
    p.set_defaults(executer=executer)


def _afficher(lecture, detail: bool) -> None:
    e = lecture.etat
    print(f"  chapitres désignés : {', '.join(lecture.designes) or 'aucun'} → {len(lecture.garanties)} garanties, "
          f"{len(lecture.dossier)} clauses au dossier")
    for nom, js in (("couvre", e.couvrent), ("exclut", e.excluent), ("à vérifier", e.a_verifier)):
        for j in js:
            suite = f" — {j.question}" if j.question else ""
            print(f"  [{nom}] {j.clause_id} : « {j.extrait_contrat[:110]} »{suite}")
            if detail and j.extrait_declaration:
                print(f"           d'après : « {j.extrait_declaration} »")
    if e.manquants:
        print(f"  ! clauses attendues sans jugement : {', '.join(e.manquants[:12])}")
    for d in e.defauts[:8]:
        print(f"  ! jugement écarté — {d}")
    if lecture.desaccord:
        print(f"  ! {lecture.desaccord}")


def executer(a, base: Base, donnees: Path) -> int:
    """Juge une déclaration, ou des cas d'un jeu (avec la réponse attendue en regard)."""
    from ..analyse import clauses
    from ..llm import MistralLLM

    if a.jeu:
        cas = charger_cas(*fichiers_jeu(donnees, a.contrat, a.jeu))
        cas = [c for c in cas if not a.cas or c["id"] in a.cas]
    elif a.sinistre:
        cas = [{"id": "", "sinistre": a.sinistre}]
    else:
        sys.exit("Donner une déclaration, ou --jeu (et --cas).")
    llm = MistralLLM(modele=a.modele, timeout=300)
    chaine = None
    if a.regles:
        from .commun import chaine as construire
        chaine = construire(base, a.contrat)
    justes = 0
    for c in cas:
        debut = time.perf_counter()
        regles = chaine.analyser(c["sinistre"]).verdict.decision if chaine else None
        lecture = clauses.lire(base, a.contrat, llm, c["sinistre"], regles=regles)
        attendu = c.get("attendu")
        juste = attendu is None or lecture.decision.value == attendu or lecture.decision.value in (c.get("acceptables") or [])
        justes += bool(attendu) and juste
        entete = f"{c['id']} : " if c["id"] else ""
        regard = f"  (attendu {attendu}{'' if juste else ' ✗'})" if attendu else ""
        print(f"{entete}{lecture.decision.value}{regard} — {lecture.etat.motif}  [{time.perf_counter() - debut:.0f} s]")
        _afficher(lecture, a.detail)
    if a.jeu:
        print(f"{justes}/{len(cas)} réponses justes ou admises.")
    return 0
