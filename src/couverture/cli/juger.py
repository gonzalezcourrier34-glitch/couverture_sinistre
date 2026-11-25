"""`couverture juger` : la lecture des clauses (DEMARCHE 7.188), à l'essai.

Le modèle désigne les chapitres, puis juge chaque clause attendue ; le code décide. Deux appels au modèle par
déclaration, sur un dossier de quelques milliers de mots : c'est une commande payante, à lancer aux moments
choisis. La chaîne de règles n'est pas appelée ici (`--regles` pour la contresignature, qui coûte ses appels).

  couverture juger --contrat assureur-a-habitation-2025 "De l'eau a coulé du plafond…"
  couverture juger --contrat assureur-b-habitation-2017 --jeu aveugle --cas av-b05 --cas av-b13
"""

from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    p.add_argument("--echantillon", type=int, default=0, metavar="N", help="Les N premiers cas du jeu seulement")
    p.add_argument("--mesure-finale", action="store_true",
                   help="Exigé pour le jeu « quatre », qui ne se passe qu'une fois et ne sert pas à régler")
    p.add_argument("--paralleles", type=int, default=4, metavar="N",
                   help="N cas à la fois (4 par défaut, comme le banc) : le temps d'un passage, pas celui d'un cas")
    p.add_argument("--detail", action="store_true", help="Afficher chaque jugement qui n'est pas « sans effet »")
    p.set_defaults(executer=executer)


class _Temoin:
    """Le modèle, plus la mémoire de ses réponses brutes : une réponse illisible est gardée pour être lue."""

    def __init__(self, llm):
        self.llm, self.reponses = llm, []
        self.envoyes = self.recus = self.cache = 0
        self.accepte_schema = getattr(llm, "accepte_schema", False)

    def completer(self, systeme, message, **options):
        try:
            self.reponses.append(self.llm.completer(systeme, message, **options))
            usage = getattr(self.llm, "dernier_usage", None) or {}
            self.envoyes += usage.get("prompt_tokens") or 0
            self.recus += usage.get("completion_tokens") or 0
            self.cache += (usage.get("prompt_tokens_details") or {}).get("cached_tokens") or 0
        except ValueError as e:  # réponse coupée : ce qui a été reçu est dans l'erreur
            self.reponses.append("\n".join(str(x) for x in e.args))
            raise
        return self.reponses[-1]

    def garder(self, dossier: Path, cas: str) -> Path:
        dossier.mkdir(parents=True, exist_ok=True)
        fichier = dossier / f"juger_{cas or 'declaration'}.txt"
        fichier.write_text("\n\n=== réponse suivante ===\n\n".join(self.reponses), encoding="utf-8")
        return fichier


def _afficher(lecture, detail: bool) -> list[str]:
    e, lignes = lecture.etat, []
    lignes.append(f"  chapitres désignés : {', '.join(lecture.designes) or 'aucun'} → {len(lecture.garanties)} "
                  f"garanties, {len(lecture.dossier)} clauses au dossier")
    for nom, js in (("couvre", e.couvrent), ("exclut", e.excluent), ("limite", e.limitent), ("à vérifier", e.a_verifier)):
        for j in js:
            suite = f" — {j.question}" if j.question else ""
            lignes.append(f"  [{nom}] {j.clause_id} : « {j.extrait_contrat[:110]} »{suite}")
            if detail and j.extrait_declaration:
                lignes.append(f"           d'après : « {j.extrait_declaration} »")
    if lecture.relancees:
        lignes.append(f"  clauses redemandées au modèle (un appel de plus) : {', '.join(lecture.relancees[:12])}")
    if e.manquants:
        lignes.append(f"  ! clauses attendues sans jugement : {', '.join(e.manquants[:12])}")
    lignes += [f"  ! jugement écarté — {d}" for d in e.defauts[:8]]
    if lecture.desaccord:
        lignes.append(f"  ! {lecture.desaccord}")
    return lignes


def executer(a, base: Base, donnees: Path) -> int:
    """Juge une déclaration, ou des cas d'un jeu (avec la réponse attendue en regard)."""
    from ..analyse import clauses
    from ..llm import MistralLLM

    if a.jeu:
        if a.jeu == "quatre" and not a.mesure_finale:
            sys.exit("Le jeu « quatre » n'a jamais été regardé : il ne se passe qu'une fois, pour la mesure finale, "
                     "et ne sert pas à régler. Ajouter --mesure-finale pour le lancer en connaissance de cause.")
        cas = charger_cas(*fichiers_jeu(donnees, a.contrat, a.jeu))
        cas = [c for c in cas if not a.cas or c["id"] in a.cas]
        cas = cas[:a.echantillon] if a.echantillon else cas
    elif a.sinistre:
        cas = [{"id": "", "sinistre": a.sinistre}]
    else:
        sys.exit("Donner une déclaration, ou --jeu (et --cas).")
    chaine = None
    if a.regles:
        from .commun import chaine as construire
        chaine = construire(base, a.contrat)

    def un_cas(c: dict) -> tuple[list[str], dict]:
        """Un cas, de bout en bout ; rend son texte et sa ligne de bilan. Chaque cas a son propre client : le compte
        des tokens d'un appel ne se mélange pas à celui d'un autre cas qui tourne en même temps."""
        debut = time.perf_counter()
        # 32 000 : la réflexion de Mistral Large compte dans la limite, et 16 000 a coupé une réponse (7.200).
        modele = MistralLLM(modele=a.modele, timeout=600, max_tokens=32000)
        llm = _Temoin(modele)
        attendu = c.get("attendu")
        try:
            regles = chaine.analyser(c["sinistre"]).verdict.decision if chaine else None
            lecture = clauses.lire(base, a.contrat, llm, c["sinistre"], regles=regles, garder=True)
        except ValueError as e:  # réponse coupée ou illisible : on le dit et on passe au cas suivant
            duree = f"[{time.perf_counter() - debut:.0f} s]"
            texte = [f"{c['id']} : pas de réponse exploitable — {str(e).splitlines()[0]}  {duree}",
                     f"  réponses brutes gardées dans {llm.garder(donnees / 'debug', c['id'])}"]
            return texte, {"id": c["id"], "attendu": attendu, "obtenu": "ERREUR", "juste": False,
                           "envoyes": llm.envoyes, "cache": llm.cache, "recus": llm.recus}
        obtenu = lecture.decision.value
        juste = attendu is None or obtenu == attendu or obtenu in (c.get("acceptables") or [])
        entete = f"{c['id']} : " if c["id"] else ""
        regard = f"  (attendu {attendu}{'' if juste else ' ✗'})" if attendu else ""
        texte = [f"{entete}{obtenu}{regard} — {lecture.etat.motif}  [{time.perf_counter() - debut:.0f} s]",
                 *_afficher(lecture, a.detail)]
        llm.garder(donnees / "debug", c["id"])
        texte.append(f"  tokens : {llm.envoyes} envoyés (dont {llm.cache} repris du cache), {llm.recus} reçus, en "
                     f"{len(llm.reponses)} appels (réflexion du dernier : {getattr(modele, 'derniere_reflexion', 0)} "
                     "caractères)")
        return texte, {"id": c["id"], "attendu": attendu, "obtenu": obtenu, "juste": juste,
                       "motif": lecture.etat.motif, "secondes": round(time.perf_counter() - debut, 1),
                       "envoyes": llm.envoyes, "cache": llm.cache, "recus": llm.recus, "appels": len(llm.reponses),
                       "relancees": lecture.relancees}

    depart = time.perf_counter()
    par_id: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=max(1, a.paralleles)) as pool:
        for fait in as_completed([pool.submit(un_cas, c) for c in cas]):  # affiché dans l'ordre d'arrivée
            texte, ligne = fait.result()
            print("\n".join(texte), flush=True)
            par_id[ligne["id"]] = ligne
    lignes = [par_id[c["id"]] for c in cas]                                  # le bilan, dans l'ordre du jeu
    envoyes, recus = sum(l["envoyes"] for l in lignes), sum(l["recus"] for l in lignes)
    if a.jeu:
        print(_bilan(lignes, envoyes, recus, time.perf_counter() - depart))
        fichier = donnees / "debug" / f"juger_bilan_{a.contrat}_{a.jeu}_{a.modele}.json"
        fichier.write_text(json.dumps({"contrat": a.contrat, "jeu": a.jeu, "modele": a.modele, "regles": a.regles,
                                       "envoyes": envoyes, "recus": recus, "cas": lignes}, ensure_ascii=False, indent=1),
                           encoding="utf-8")
        print(f"Bilan gardé dans {fichier}")
    return 0


def _bilan(lignes: list[dict], envoyes: int, recus: int, secondes: float) -> str:
    """Le compte d'un passage : justes, et les deux erreurs qui ne se valent pas (couvert à tort, refus à tort)."""
    n = len(lignes)
    justes = sum(l["juste"] for l in lignes)
    a_tort = [l["id"] for l in lignes if l["obtenu"] == "COUVERT" and not l["juste"]]
    refus = [l["id"] for l in lignes if l["obtenu"] == "NON_COUVERT" and not l["juste"]]
    prudents = [l["id"] for l in lignes if l["obtenu"] in ("INCERTAIN", "ERREUR") and not l["juste"]]
    return (f"{justes}/{n} réponses justes ou admises. Couverts à tort : {len(a_tort)} {a_tort or ''} ; refus à tort : "
            f"{len(refus)} {refus or ''} ; « à préciser » ou erreur à la place d'une réponse : {len(prudents)} "
            f"{prudents or ''}\nTokens : {envoyes} envoyés, {recus} reçus ; {secondes:.0f} s en tout"
            + (f", {secondes / n:.0f} s par cas." if n else "."))
