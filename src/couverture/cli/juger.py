"""`couverture juger` : la lecture des clauses (DEMARCHE 7.188), à l'essai.

Le modèle désigne les chapitres, puis juge chaque clause attendue ; le code décide. Deux appels au modèle par
déclaration, sur un dossier de quelques milliers de mots : c'est une commande payante, à lancer aux moments
choisis. La chaîne de règles n'est pas appelée ici (`--regles` pour la contresignature, qui coûte ses appels).

  couverture juger --contrat assureur-a-habitation-2025 "De l'eau a coulé du plafond…"
  couverture juger --contrat assureur-b-habitation-2017 --jeu aveugle --cas av-b05 --cas av-b13

La stabilité (7.220) : repasser un jeu avec `--passage 2`, `--passage 3` (chaque passe garde son bilan et ses réponses
brutes à part), puis `couverture juger --stabilite --jeu cinq --contrat tous` compare les passes, sans appel au modèle.
"""

from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ..contrat.base import Base
from ..mesure.evaluation import JEUX_FERMES, JEUX_JAMAIS_VUS, charger_cas, fichiers_jeu


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
                   help="Exigé pour un jeu jamais regardé (« cinq »), qui ne se passe qu'une fois et ne sert pas à régler")
    p.add_argument("--paralleles", type=int, default=4, metavar="N",
                   help="N cas à la fois (4 par défaut, comme le banc) : le temps d'un passage, pas celui d'un cas")
    p.add_argument("--detail", action="store_true", help="Afficher chaque jugement qui n'est pas « sans effet »")
    p.add_argument("--passage", type=int, default=1, metavar="N",
                   help="Le numéro de la passe, pour mesurer la stabilité (7.220) : à partir de 2, le bilan et les réponses "
                        "brutes sont gardés à part (suffixe _pN) ; la passe 1 est celle sans suffixe")
    p.add_argument("--stabilite", action="store_true",
                   help="Comparer les passes déjà faites d'un jeu (`--contrat tous` pour tous les contrats) : cas dont la "
                        "réponse change, justesse moyenne, minimale, maximale. Aucun appel au modèle")
    p.add_argument("--consigne-jugement", metavar="VERSION",
                   help="Juger avec une version archivée de la consigne de jugement (docs/consignes/clauses-jugement/"
                        "<VERSION>.txt), pour comparer deux versions sur le même jeu (7.226) ; le bilan porte le suffixe "
                        "_<VERSION>")
    p.add_argument("--depuis", type=int, default=1, metavar="N",
                   help="Avec --stabilite : seulement les passes N et suivantes (celles d'un même état du code)")
    p.add_argument("--rejouer", action="store_true",
                   help="Reprendre les réponses gardées d'un passage précédent (data/debug/juger_<cas>.txt) ; seul ce "
                        "qui est nouveau (la relecture ciblée, 7.211) est demandé au modèle. Presque gratuit.")
    p.set_defaults(executer=executer)


class _Temoin:
    """Le modèle, plus la mémoire de ses réponses brutes : une réponse illisible est gardée pour être lue."""

    def __init__(self, llm, rejouees: list[str] | None = None):
        self.llm, self.reponses, self.rejouees = llm, [], list(rejouees or [])
        self.envoyes = self.recus = self.cache = 0
        self.accepte_schema = getattr(llm, "accepte_schema", False)

    def completer(self, systeme, message, **options):
        if self.rejouees:                              # --rejouer : la réponse d'alors, sans appel au modèle
            self.reponses.append(self.rejouees.pop(0))
            return self.reponses[-1]
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
                  f"garanties, {len(lecture.dossier)} clauses au dossier"
                  + (f" (ajoutés d'après les règles : {', '.join(lecture.ajoutes)})" if lecture.ajoutes else ""))
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
    for ligne in lecture.arbitrage:
        lignes.append(f"  relecture ciblée — {ligne}")
    if lecture.desaccord:
        lignes.append(f"  ! {lecture.desaccord}")
    return lignes


def executer(a, base: Base, donnees: Path) -> int:
    """Juge une déclaration, ou des cas d'un jeu (avec la réponse attendue en regard)."""
    from ..analyse import clauses
    from ..llm import CleRefusee, ErreurLLM, MistralLLM

    if getattr(a, "stabilite", False):
        if not a.jeu:
            sys.exit("--stabilite demande --jeu.")
        print(stabilite(donnees / "debug", a.jeu, a.modele, None if a.contrat == "tous" else a.contrat,
                        getattr(a, "depuis", 1)))
        return 0
    passe = f"_p{a.passage}" if getattr(a, "passage", 1) > 1 else ""
    version = getattr(a, "consigne_jugement", None)
    if version:
        archive = Path(__file__).resolve().parents[3] / "docs" / "consignes" / "clauses-jugement" / f"{version}.txt"
        if not archive.exists():
            sys.exit(f"Pas de consigne de jugement archivée en {version} ({archive}).")
        clauses.SYSTEME_JUGEMENT = archive.read_text(encoding="utf-8")
        passe = f"_{version}" + passe
    if a.jeu:
        if a.jeu in JEUX_JAMAIS_VUS and not a.mesure_finale and not a.rejouer:
            sys.exit(f"Le jeu « {a.jeu} » n'a jamais été regardé : il ne se passe qu'une fois, pour la mesure finale, "
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
        rejouees = None
        if a.rejouer:                                  # les réponses d'un passage précédent, dans l'ordre des appels
            gardees = donnees / "debug" / f"juger_{c['id'] or 'declaration'}.txt"
            if not gardees.exists():
                return [f"{c['id']} : rien à rejouer ({gardees} absent)"], {
                    "id": c["id"], "attendu": c.get("attendu"), "obtenu": "ERREUR", "juste": False,
                    "envoyes": 0, "cache": 0, "recus": 0}
            rejouees = gardees.read_text(encoding="utf-8").split("\n\n=== réponse suivante ===\n\n")
        llm = _Temoin(modele, rejouees)
        suffixe = ("_rejeu" if a.rejouer else "") + passe
        attendu = c.get("attendu")
        try:
            # Le résultat entier des règles, pas seulement leur décision : la relecture ciblée part de leurs
            # obstacles (7.211).
            regles = chaine.analyser(c["sinistre"]) if chaine else None
            # Les chapitres des garanties que les règles ont trouvées s'ajoutent à la désignation (13.2).
            lecture = clauses.lire(base, a.contrat, llm, c["sinistre"], regles=regles, garder=True,
                                   renfort=clauses.chapitres_des_regles(regles) if regles else None)
        except (ValueError, ErreurLLM) as e:  # réponse coupée ou illisible, ou panne du fournisseur (une erreur 520
            # a arrêté tout un passage du jeu « quatre », 7.207) : on le dit et on passe au cas suivant
            if isinstance(e, CleRefusee):  # une clé refusée vaut pour tous les cas : on s'arrête
                raise
            duree = f"[{time.perf_counter() - debut:.0f} s]"
            texte = [f"{c['id']} : pas de réponse exploitable — {str(e).splitlines()[0]}  {duree}",
                     f"  réponses brutes gardées dans {llm.garder(donnees / 'debug', (c['id'] or 'declaration') + suffixe)}"]
            return texte, {"id": c["id"], "attendu": attendu, "obtenu": "ERREUR", "juste": False,
                           "envoyes": llm.envoyes, "cache": llm.cache, "recus": llm.recus}
        obtenu = lecture.decision.value
        juste = attendu is None or obtenu == attendu or obtenu in (c.get("acceptables") or [])
        entete = f"{c['id']} : " if c["id"] else ""
        regard = f"  (attendu {attendu}{'' if juste else ' ✗'})" if attendu else ""
        texte = [f"{entete}{obtenu}{regard} — {lecture.etat.motif}  [{time.perf_counter() - debut:.0f} s]",
                 *_afficher(lecture, a.detail)]
        llm.garder(donnees / "debug", (c["id"] or "declaration") + suffixe)
        texte.append(f"  tokens : {llm.envoyes} envoyés (dont {llm.cache} repris du cache), {llm.recus} reçus, en "
                     f"{len(llm.reponses)} appels (réflexion du dernier : {getattr(modele, 'derniere_reflexion', 0)} "
                     "caractères)")
        return texte, {"id": c["id"], "attendu": attendu, "obtenu": obtenu, "juste": juste,
                       "motif": lecture.etat.motif, "secondes": round(time.perf_counter() - debut, 1),
                       "envoyes": llm.envoyes, "cache": llm.cache, "recus": llm.recus, "appels": len(llm.reponses),
                       "relancees": lecture.relancees,
                       # Les clauses qui fondent la réponse : pour voir, d'une passe à l'autre, si la même décision
                       # s'appuie sur les mêmes clauses (7.220).
                       "clauses": sorted({j.clause_id for j in [*lecture.etat.couvrent, *lecture.etat.excluent,
                                                                *lecture.etat.a_verifier]})}

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
        fichier = donnees / "debug" / f"juger_bilan_{a.contrat}_{a.jeu}_{a.modele}{'_rejeu' if a.rejouer else ''}{passe}.json"
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


def stabilite(dossier: Path, jeu: str, modele: str, contrat: str | None = None, depuis: int = 1) -> str:
    """La stabilité de la lecture des clauses sur un jeu (7.220), d'après les bilans de ses passes : la passe 1
    (`juger_bilan_<contrat>_<jeu>_<modele>.json`), puis `_p2`, `_p3`… Sur les cas présents dans toutes les passes
    d'un contrat : les cas dont la décision change, ceux dont la décision tient mais pas les clauses qui la fondent,
    et la justesse de chaque passe. Comme pour le banc de la chaîne de règles, qui passe chaque jeu trois fois."""
    import re

    motif = re.compile(rf"juger_bilan_(.+)_{re.escape(jeu)}_{re.escape(modele)}(?:_p(\d+))?\.json$")
    passes: dict[str, dict[int, dict]] = {}
    for f in sorted(dossier.glob(f"juger_bilan_*_{jeu}_{modele}*.json")):
        m = motif.match(f.name)
        if not m or (contrat and m.group(1) != contrat) or int(m.group(2) or 1) < depuis:
            continue
        passes.setdefault(m.group(1), {})[int(m.group(2) or 1)] = json.loads(f.read_text(encoding="utf-8"))
    if not passes:
        return f"Aucun bilan pour le jeu « {jeu} » ({modele}) dans {dossier}."
    lignes, total = [], {"cas": 0, "instables": 0, "clauses": 0, "comparables": 0}
    for c, par_passe in sorted(passes.items()):
        numeros = sorted(par_passe)
        cas = [{l["id"]: l for l in par_passe[n]["cas"]} for n in numeros]
        communs = [i for i in cas[0] if all(i in x for x in cas[1:])]
        instables = [i for i in communs if len({x[i]["obtenu"] for x in cas}) > 1]
        # Les clauses ne sont gardées au bilan que depuis 7.220 : on compare les passes qui les ont, s'il y en a deux.
        avec_clauses = lambda i: [x[i]["clauses"] for x in cas if "clauses" in x[i]]  # noqa: E731
        comparables = [i for i in communs if i not in instables and len(avec_clauses(i)) >= 2]
        autres_clauses = [i for i in comparables if len({tuple(c) for c in avec_clauses(i)}) > 1]
        justes = [sum(x[i]["juste"] for i in communs) for x in cas]
        a_tort = [sum(x[i]["obtenu"] == "COUVERT" and not x[i]["juste"] for i in communs) for x in cas]
        refus = [sum(x[i]["obtenu"] == "NON_COUVERT" and not x[i]["juste"] for i in communs) for x in cas]
        lignes.append(f"{c} · {len(numeros)} passe{'s' * (len(numeros) > 1)} ({', '.join(map(str, numeros))}) · "
                      f"{len(communs)} cas communs")
        lignes.append(f"  justes : {', '.join(map(str, justes))} (moyenne {sum(justes) / len(justes):.1f}) · "
                      f"couverts à tort : {', '.join(map(str, a_tort))} · refus à tort : {', '.join(map(str, refus))}")
        lignes.append(f"  instables : {len(instables)} sur {len(communs)}"
                      + (" — " + " ; ".join(f"{i} {' → '.join(x[i]['obtenu'] for x in cas)}" for i in instables)
                         if instables else ""))
        if comparables:
            lignes.append(f"  même décision, autres clauses : {len(autres_clauses)} sur {len(comparables)}"
                          + (f" — {', '.join(autres_clauses)}" if autres_clauses else ""))
        total["cas"] += len(communs)
        total["instables"] += len(instables)
        total["clauses"] += len(autres_clauses)
        total["comparables"] += len(comparables)
    if len(passes) > 1:
        lignes.append(f"Ensemble : {total['instables']} cas instables sur {total['cas']}"
                      + (f" ; même décision, autres clauses : {total['clauses']} sur {total['comparables']}"
                         if total["comparables"] else ""))
    return "\n".join(lignes)
