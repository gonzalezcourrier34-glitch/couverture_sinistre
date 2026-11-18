"""Ligne de commande.

  couverture ingerer                               # lit data/contrats/ et remplit la base
  couverture contrats                              # liste les contrats et leur statut
  couverture clauses  --contrat foyer-appart123-2025
  couverture regles   --contrat foyer-appart123-2025 [--faits '{"evenement": "vol"}']   # sans modèle
  couverture rediger  --contrat foyer-appart123-2025 --article 2.2                     # Mistral Large rédige
  couverture analyser --contrat foyer-appart123-2025 "Mon vélo a été volé dans le local commun…"
  couverture banc     --contrat foyer-appart123-2025 [--methode brut]                  # golden set, portes
  couverture legalbench [--telecharger]                                                # second banc, externe
  couverture serveur  --port 8000
  couverture versions [--manifeste | --enregistrer] # consignes versionnées (manifeste, MLflow)
  couverture modele                                # modèle configuré, test de connexion
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .base import Base
from .config import charger_env
from .ingestion import ingerer_dossier
from .models import Resultat
from .pipeline import PipelineDocumentBrut, llm_configure


ROLES = {"evenement": "‹événement›", "bien": "‹bien›", "lieu": "‹lieu›", "circonstance": "‹circonstance›"}


def afficher_court(r: Resultat) -> str:
    """Ce qu'un gestionnaire lit d'abord : la décision, son motif, les preuves décisives, ce qu'il
    faut demander. Tout le reste (chaque fiche, chaque exclusion) : --detail."""
    v = r.verdict
    lignes = [f"Décision : {v.decision.value}  (confiance {v.confiance:.2f})", f"Motif : {v.justification}"]
    if r.methode == "regles":
        f = r.faits
        lus = [f"événement {'/'.join(f.evenements)}" if f.evenements else "", f"biens {'/'.join(f.biens)}" if f.biens else "",
               f"lieu {'/'.join(f.lieux)}" if f.lieux else "", ", ".join(f.circonstances)]
        lignes.append("Faits lus : " + ("; ".join(x for x in lus if x) or "aucun"))
    if v.decision_avant_relecture:
        lignes.append(f"  (la relecture a corrigé une première réponse {v.decision_avant_relecture.value})")
    preuves = [c for c in v.conditions if c.decisive and c.valide]
    if preuves:
        lignes.append("Preuves :")
        for c in preuves:
            page = f", p. {', '.join(map(str, c.pages))}" if c.pages else ""
            etat = {"REMPLIE": "oui", "NON_REMPLIE": "non", "INCONNUE": "?"}[c.etat.value]
            lignes.append(f"  [{etat}] {c.enonce}")
            lignes.append(f"        art. {c.clause_id}{page} : « {c.extrait} »")
    elif v.citations:
        lignes.append("Preuves :")
        for c in v.citations:
            if c.valide:
                page = f", p. {', '.join(map(str, c.pages))}" if c.pages else ""
                lignes.append(f"  art. {c.clause_id}{page} : « {c.extrait} »")
    if v.informations_manquantes:
        lignes.append("À demander à l'assuré :")
        lignes += [f"  - {q}" for q in v.informations_manquantes]
    if v.decision.value == "COUVERT":
        limites = [c for c in v.conditions if c.nature == "limite" and c.valide]
        if limites:
            lignes.append("Limites :")
            lignes += [f"  - {c.enonce} (art. {c.clause_id})" for c in limites]
    if v.raisonnement:
        lignes.append("Arbre de preuve (moteur Prolog) :")
        lignes += [f"  {l}" for l in v.raisonnement]
    if v.avertissements:
        lignes.append(f"{len(v.avertissements)} avertissement(s) : --detail.")
    return "\n".join(lignes)


def afficher(r: Resultat) -> str:
    v = r.verdict
    lignes = [
        f"Contrat : {r.contrat_id}   Méthode : {r.methode}",
        f"Décision : {v.decision.value}  (confiance {v.confiance:.2f}, juge : {v.mode})",
        "",
        v.justification,
        "",
    ]
    if v.decision_initiale and v.decision_initiale != v.decision:
        lignes.insert(2, f"  (le juge avait répondu {v.decision_initiale.value} ; corrigé par le contrôle des citations)")
    if v.conditions:
        symbole = {"REMPLIE": "oui", "NON_REMPLIE": "non", "INCONNUE": " ? "}
        groupe = None
        presumees = [c for c in v.conditions if c.justification.startswith("Présumée absente")]
        for c in (c for c in v.conditions if not c.justification.startswith("Présumée absente")):
            if c.groupe != groupe:
                groupe = c.groupe
                titre = f"Garantie « {groupe} »" if c.nature == "garantie" else groupe
                lignes.append(titre + " :")
            etat = "" if c.nature == "limite" else f"[{symbole[c.etat.value]}] "
            preuve = f"art. {c.clause_id}" + (f", p. {', '.join(map(str, c.pages))}" if c.pages else "")
            marque = "  ← décisif" if c.decisive else ("  [ÉCARTÉE : citation introuvable]" if not c.valide else "")
            role = f"{ROLES.get(c.role, '')} " if c.role else ""
            lignes.append(f"  {etat}{role}{c.enonce} ({preuve}){marque}")
            if c.valide and c.nature != "limite":
                lignes.append(f"        « {c.extrait} »")
        if presumees:
            lignes.append(f"{len(presumees)} exclusion(s) présumée(s) absente(s), la déclaration ne les évoquant pas "
                          f"(faute intentionnelle, guerre…) : voir --json.")
        lignes.append("")
    elif v.citations:
        lignes.append("Clauses citées :")
        for c in v.citations:
            etat = "" if c.valide else "  [REJETÉE]"
            page = f", p. {', '.join(map(str, c.pages))}" if c.pages else ""
            lignes.append(f"  - Art. {c.clause_id} ({c.role}{page}) : « {c.extrait} »{etat}")
    for titre, items in (("Ambiguïtés", v.ambiguites), ("À vérifier", v.informations_manquantes), ("Avertissements", v.avertissements)):
        if items:
            lignes.append(f"{titre} :")
            lignes.extend(f"  - {i}" for i in items)
    if r.clauses_consultees:
        lignes.append("")
        lignes.append("Clauses consultées : " + ", ".join(c.clause.id for c in r.clauses_consultees))
    return "\n".join(lignes)


METHODES = ["regles", "brut"]


def construire(base: Base, contrat_id: str, methode: str = "regles"):
    """regles : le modèle lit les faits, Prolog décide (le système) ;
    brut : le contrat entier dans le prompt (la référence « chatbot », pour comparer)."""
    if llm_configure() is None:
        sys.exit(f"La méthode « {methode} » a besoin d'un modèle : définir MISTRAL_API_KEY dans .env.")
    if methode == "brut":
        return PipelineDocumentBrut.depuis_base(base, contrat_id, llm_configure())
    from .prolog import PipelineRegles

    try:
        return PipelineRegles.depuis_base(base, contrat_id, llm_configure())
    except LookupError as e:
        sys.exit(str(e))


def ingerer(donnees: Path, base: Base, forcer: bool = False) -> int:
    from .ingestion import fichiers_contrats
    from .progression import Barre
    from .suivi import EXPERIENCE_INGESTION, execution, metriques_ingestion

    with execution(EXPERIENCE_INGESTION, "ingestion") as suivi:
        barre = Barre(len(fichiers_contrats(donnees / "contrats")), "Ingestion")
        contrats = ingerer_dossier(donnees / "contrats", base, forcer=forcer, barre=barre)
        barre.terminer()
        suivi.parametres({"forcer": forcer})
        suivi.metriques(metriques_ingestion(contrats))
        suivi.artefact_json("rapports.json", {c.id: c.rapport for c in contrats})
    for c in contrats:
        print(f"{c.statut:<11} {c.id:<28} {c.rapport.get('nb_clauses', 0):>4} clauses  {c.rapport.get('par_type', {})}")
        for alerte in c.rapport.get("alertes", []):
            print(f"{'':<11} ! {alerte}")
    if any(c.statut != "OK" for c in base.contrats()):
        print("\nDes contrats sont à vérifier : un profil d'assureur (data/profils/) corrige le découpage.")
    return 0


def rediger_cli(base: Base, contrat_id: str, articles: list[str], controler: bool, a_accepter: str | None,
                vocabulaire: str | None) -> int:
    """Rédaction des règles d'une garantie par le modèle (Mistral Large), contrôles, acceptation."""
    from . import prolog, redaction
    from .evaluation import lire_jsonl

    clauses = base.clauses(contrat_id)
    cas = []
    for f in sorted((prolog.DOSSIER / "cas").rglob(f"{contrat_id}.jsonl")):
        cas += [(d["sinistre_id"], d["faits"]) for d in lire_jsonl(f)]

    if vocabulaire:
        js, _ = redaction.chemins(contrat_id, vocabulaire)
        ajouts = redaction.accepter_vocabulaire(json.loads(js.read_text(encoding="utf-8"))["proposition"])
        print("Vocabulaire commun complété :" if ajouts else "Rien à ajouter au vocabulaire.")
        for x in ajouts:
            print(f"  + {x}")
        if ajouts:
            print(redaction.resumer(redaction.recontroler(contrat_id, vocabulaire, clauses, cas=cas)))
        return 0
    if a_accepter:
        try:
            cible = redaction.accepter(contrat_id, a_accepter)
        except redaction.ErreurProposition as e:
            print(f"Refusé : {e}")
            return 1
        print(f"Règles de l'art. {a_accepter} ajoutées à {cible}. Vérifier : `couverture regles --contrat {contrat_id}`.")
        return 0
    if controler:
        articles = articles or redaction.articles_proposes(contrat_id)
        if not articles:
            print("Aucune proposition enregistrée : `couverture rediger --contrat … --article 2.2`.")
            return 1
        for art in articles:
            print(redaction.resumer(redaction.recontroler(contrat_id, art, clauses, cas=cas)))
        return 0
    if not articles:
        print("Préciser au moins un article : --article 2.2")
        return 1

    llm = llm_configure("contrat")
    if llm is None:
        sys.exit("La rédaction a besoin d'un modèle : définir MISTRAL_API_KEY dans .env.")
    from .progression import Barre

    barre = Barre(len(articles), "Rédaction")
    docs = []
    for art in articles:
        barre.ecrire(f"art. {art} : rédaction par {llm.nom}…")
        try:
            docs.append(redaction.rediger(contrat_id, art, clauses, llm, cas=cas))
        except (LookupError, ValueError, prolog.ErreurRegles) as e:
            barre.ecrire(f"art. {art} : échec ({e}) ; la réponse du modèle, si elle est arrivée, est gardée : "
                         f"`couverture rediger --contrat {contrat_id} --controler --article {art}`")
        barre.avancer(art)
    barre.terminer()
    for d in docs:
        print(redaction.resumer(d))
    print(f"Propositions dans regles/propositions/{contrat_id}/ (JSON : la source, corrigible à la main ; .pl : les règles).")
    return 0


def banc_cli(base: Base, donnees: Path, contrat_id: str, methode: str, couches: str, repetitions: int,
             paralleles: int, a_figer: str | None, fiche: bool = False) -> int:
    """Le golden set rejoué couche par couche ; sort en erreur si une porte échoue (pour la CI)."""
    from . import banc

    if fiche:
        f = Path(donnees) / "golden" / "A_VALIDER.md"
        f.write_text(banc.fiche_validation(donnees, contrat_id), encoding="utf-8")
        print(f"Fiche de validation : {f}")
        return 0

    if a_figer is not None:
        v = banc.figer(donnees, contrat_id, a_figer)
        print(f"Golden set figé : version {v['version']} (empreinte {v['empreintes'][contrat_id]}).")
        return 0
    voulues = [c.strip() for c in couches.split(",") if c.strip()]
    fabrique = (lambda: construire(base, contrat_id, methode)) if "chaine" in voulues else None
    from .suivi import EXPERIENCE_EVALUATION, execution, metriques_banc, parametres_communs

    with execution(EXPERIENCE_EVALUATION, f"banc {contrat_id} · {methode}") as suivi:
        r = banc.passer(donnees, contrat_id, methode, voulues, repetitions, paralleles, pipeline_fabrique=fabrique)
        suivi.parametres(parametres_communs(str(r.get("modele", "aucun"))) | {
            "contrat": contrat_id, "methode": methode, "couches": ",".join(voulues),
            "golden": str(r.get("golden", {}).get("version") if isinstance(r.get("golden"), dict) else r.get("golden"))})
        suivi.metriques(metriques_banc(r) | {"portes_passees": float(bool(r["passe"]))})
    _, md = banc.enregistrer(donnees, r)
    print(banc.resume_console(r, md))
    return 0 if r["passe"] else 1


def legalbench_cli(donnees: Path, telecharger: bool, fichier: str | None, split: str, limite: int | None,
                   paralleles: int) -> int:
    """LegalBench : le modèle répond et cite, le code vérifie la citation ; réponse brute et contrôlée comparées."""
    from . import legalbench as lb
    from .llm import configurer

    if telecharger:
        f = lb.telecharger(donnees)
        cas = lb.charger(f)
        print(f"{len(cas)} cas téléchargés : {f}")
        return 0
    f = Path(fichier) if fichier else Path(donnees) / lb.DOSSIER / lb.FICHIER
    if not f.exists():
        print(f"Données absentes ({f}) : `couverture legalbench --telecharger` d'abord.")
        return 1
    cas = [c for c in lb.charger(f) if split == "tout" or c.get("split", split) == split]
    if limite:
        cas = cas[:limite]
    llm = configurer("analyse")
    if llm is None:
        print("Aucun modèle configuré (MISTRAL_API_KEY dans .env) : ce banc juge avec le modèle.")
        return 1
    r = lb.passer(cas, llm, paralleles)
    _, md = lb.enregistrer(donnees, r)
    print(lb.resume_console(r, md))
    return 0


def regles_cli(base: Base, donnees: Path, contrat_id: str, faits_json: str | None, jeu: str = "mise_au_point") -> int:
    """Vérifie les règles Prolog d'un contrat, sans appel au modèle :
    1. SWI-Prolog est là et les règles se chargent sans avertissement ;
    2. chaque variable et chaque valeur employées sont dans le vocabulaire commun ;
    3. chaque citation figure mot pour mot dans la clause citée (si le contrat est en base) ;
    4. les cas de regles/cas/<contrat>.jsonl (faits « idéaux ») donnent la réponse attendue.
    Avec --faits '{"evenement": "vol", …}' : décide un seul cas."""
    import subprocess

    from . import prolog
    from .evaluation import charger_cas, fichiers_jeu, lire_jsonl
    from .validation import extrait_present

    exe = prolog.swipl()
    if exe is None:
        print("SWI-Prolog introuvable. Windows : `winget install SWI-Prolog.SWI-Prolog`, puis rouvrir PowerShell.")
        return 1
    version = subprocess.run([exe, "--version"], capture_output=True).stdout.decode("utf-8", "replace").strip()
    print(f"{version} ({exe})")
    try:
        if faits_json:
            faits = json.loads(faits_json)
            for p_ in prolog.verifier_faits(faits):
                print(f"! {p_}")
            d = prolog.decider(contrat_id, faits)
            print(f"Décision : {d['decision']}")
            for r in d["retenues"]:
                print(f"  « {r['garantie']} » ({r['article']}) : {r['motif']}")
            if d.get("preuve"):
                print("Arbre de preuve :")
                print("\n".join(f"  {l}" for l in prolog.arbre_lisible(d["preuve"])))
            return 0
        employes = prolog.executer(contrat_id, "vocabulaire_json")
        citations = prolog.executer(contrat_id, "citations_json")
    except prolog.ErreurRegles as e:
        print(f"Les règles ne se chargent pas : {e}")
        return 1
    print(f"Règles chargées : regles/{contrat_id}.pl")

    voc, problemes = prolog.vocabulaire(), []
    for e in employes:
        if e["variable"] not in voc or e["valeur"] not in voc[e["variable"]]["valeurs"]:
            problemes.append(f"hors vocabulaire : {e['variable']} = {e['valeur']}")
    print(f"Vocabulaire : {len(employes)} couples (variable, valeur) employés, {len(problemes)} hors vocabulaire.")

    try:
        clauses = {c.id: c.texte for c in base.clauses(contrat_id)}
    except KeyError:
        clauses = {}
    if clauses:
        absentes = [c for c in citations if not (c["article"] in clauses and extrait_present(c["texte"], clauses[c["article"]]))]
        problemes += [f"citation absente de l'art. {c['article']} : « {c['texte']} »" for c in absentes]
        print(f"Citations : {len(citations)} phrases du contrat, {len(absentes)} introuvable(s).")
    else:
        print(f"Citations : {len(citations)} (contrat absent de la base : `couverture ingerer` pour les vérifier).")

    chemin_cas = prolog.DOSSIER / "cas" / ("" if jeu == "mise_au_point" else jeu) / f"{contrat_id}.jsonl"
    sinistres, annotations = fichiers_jeu(donnees, contrat_id, jeu)
    if chemin_cas.exists() and annotations.exists():
        faits_par_cas = {d["sinistre_id"]: d["faits"] for d in lire_jsonl(chemin_cas)}
        lignes = []
        for c in charger_cas(sinistres, annotations):
            if c["id"] not in faits_par_cas:
                continue
            problemes += [f"{c['id']} : {p_}" for p_ in prolog.verifier_faits(faits_par_cas[c["id"]])]
            obtenu = prolog.decider(contrat_id, faits_par_cas[c["id"]])["decision"]
            lignes.append({"id": c["id"], "attendu": c["attendu"], "obtenu": obtenu, "confiance": 1.0,
                           "acceptable": obtenu != c["attendu"] and obtenu in c.get("acceptables", [])})
        n = len(lignes) or 1
        rapport = {"cas": lignes,
                   "exactitude": round(sum(l["obtenu"] == l["attendu"] or l["acceptable"] for l in lignes) / n, 3),
                   "exactitude_stricte": round(sum(l["obtenu"] == l["attendu"] for l in lignes) / n, 3),
                   "faux_couverts": sum(l["obtenu"] == "COUVERT" and l["attendu"] != "COUVERT" for l in lignes),
                   "faux_refus": sum(l["obtenu"] == "NON_COUVERT" and l["attendu"] == "COUVERT" for l in lignes),
                   "taux_incertain": round(sum(l["obtenu"] == "INCERTAIN" for l in lignes) / n, 3)}
        print(f"\nRègles seules, sur les faits idéaux des cas (jeu {jeu}, sans modèle) :")
        print(tableau(rapport))
        if rapport["faux_couverts"]:
            problemes.append(f"{rapport['faux_couverts']} couvert(s) à tort sur les faits idéaux")
    for p_ in problemes:
        print(f"! {p_}")
    print("Tout est en ordre." if not problemes else f"{len(problemes)} problème(s).")
    return 1 if problemes else 0


def tester_modele() -> int:
    from .llm import ErreurLLM

    try:
        llm = llm_configure()
    except ErreurLLM as e:
        print(f"Configuration invalide : {e}")
        return 1
    if llm is None:
        print("Aucun modèle configuré.")
        print("Créer un fichier .env à la racine du projet avec la ligne : MISTRAL_API_KEY=votre-clé")
        return 1
    contrat = llm_configure("contrat")
    print(f"Modèle des analyses : {llm.nom}")
    if contrat is not None and contrat.nom != llm.nom:
        print(f"Modèle des contrats (rédaction des règles) : {contrat.nom}")
    try:
        reponse = llm.completer('Réponds uniquement par un objet JSON.', 'Renvoie {"ok": true}.')
    except ErreurLLM as e:
        print(f"Échec de la connexion : {e}")
        return 1
    print(f"Connexion réussie. Réponse : {reponse.strip()[:200]}")
    if hasattr(llm, "reflexion_refusee"):
        niveau = llm.extra.get("reasoning_effort")
        etat = ("refusé par ce modèle, il réfléchit à son niveau par défaut" if llm.reflexion_refusee
                else f"« {niveau} » accepté" if niveau else "non demandé (niveau par défaut du modèle)")
        print(f"Réflexion : {etat} ; {llm.derniere_reflexion} caractères de réflexion pour ce test.")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="couverture", description="Le sinistre est-il couvert par les conditions générales ?")
    p.add_argument("--donnees", default="data", help="Dossier des données (défaut : data)")
    p.add_argument("--base", default=None, help="Base SQLite (défaut : <donnees>/base.sqlite)")
    sous = p.add_subparsers(dest="commande", required=True)

    pi = sous.add_parser("ingerer", help="Lire les contrats de <donnees>/contrats et remplir la base")
    pi.add_argument("--forcer", action="store_true", help="Relire même les fichiers inchangés")

    sous.add_parser("contrats", help="Lister les contrats de la base")

    pg = sous.add_parser("regles", help="Vérifier les règles Prolog d'un contrat (chargement, vocabulaire, citations, cas)")
    pg.add_argument("--contrat", required=True)
    pg.add_argument("--faits", help="Décider un cas : JSON des faits, ex. '{\"evenement\": \"vol\", \"lieu\": [\"cave\"]}'")
    pg.add_argument("--jeu", choices=["mise_au_point", "validation", "redaction", "golden"], default="mise_au_point",
                    help="Cas de mise au point (défaut), de validation (data/validation) ou des garanties rédigées par le modèle (data/redaction)")

    pb_ = sous.add_parser("banc", help="Banc d'essai : le golden set rejoué (règles, lecture, chaîne), avec des portes")
    pb_.add_argument("--contrat", required=True)
    pb_.add_argument("--methode", choices=METHODES, default="regles")
    pb_.add_argument("--couches", default="regles,chaine",
                     help="regles (sans modèle, SWI-Prolog), chaine (avec le modèle ; donne aussi la lecture pour « regles »)")
    pb_.add_argument("--repetitions", type=int, default=3)
    pb_.add_argument("--paralleles", type=int, default=4)
    pb_.add_argument("--figer", nargs="?", const="", metavar="NOTE",
                     help="Enregistrer la version du golden set (après l'avoir modifié ou validé)")
    pb_.add_argument("--fiche", action="store_true", help="Écrire data/golden/A_VALIDER.md, la fiche de relecture des cas")

    pl_ = sous.add_parser("legalbench", help="Second banc, externe : LegalBench insurance_policy_interpretation (Stanford, CC BY 4.0)")
    pl_.add_argument("--telecharger", action="store_true", help="Télécharger les données (Hugging Face) dans data/externes/legalbench/")
    pl_.add_argument("--fichier", help="Un autre fichier de cas (.jsonl téléchargé, ou .tsv / .csv LegalBench d'origine)")
    pl_.add_argument("--split", choices=["test", "train", "tout"], default="test")
    pl_.add_argument("--limite", type=int, help="Seulement les N premiers cas (essai rapide)")
    pl_.add_argument("--paralleles", type=int, default=4)

    pw = sous.add_parser("rediger", help="Faire rédiger par le modèle les règles Prolog d'une garantie, puis les contrôler")
    pw.add_argument("--contrat", required=True)
    pw.add_argument("--article", action="append", help="Article à traduire (répétable), ex. --article 2.2 --article 2.9")
    pw.add_argument("--controler", action="store_true", help="Refaire les contrôles des propositions enregistrées, sans modèle")
    pw.add_argument("--accepter", metavar="ARTICLE", help="Ajouter la proposition aux règles du contrat (si rien ne bloque)")
    pw.add_argument("--accepter-vocabulaire", metavar="ARTICLE",
                    help="Ajouter au vocabulaire commun les faits nouveaux déclarés par le modèle pour cet article")

    pc = sous.add_parser("clauses", help="Afficher le découpage d'un contrat")
    pc.add_argument("--contrat", required=True)

    pa = sous.add_parser("analyser", help="Analyser un sinistre sur un contrat")
    pa.add_argument("--contrat", required=True)
    pa.add_argument("sinistre")
    pa.add_argument("--methode", choices=METHODES, default="regles")
    pa.add_argument("--json", action="store_true", help="Sortie JSON complète (traçabilité)")
    pa.add_argument("--detail", action="store_true", help="Toutes les conditions et l'arbre de preuve complet")

    sous.add_parser("modele", help="Afficher le modèle configuré et tester la connexion")

    pv = sous.add_parser("versions", help="Versions des consignes : vérifier, réécrire le manifeste, enregistrer dans MLflow")
    groupe = pv.add_mutually_exclusive_group()
    groupe.add_argument("--manifeste", action="store_true", help="Réécrire config/versions_consignes.json")
    groupe.add_argument("--enregistrer", action="store_true", help="Enregistrer les consignes dans MLflow (Prompt Registry)")

    ps = sous.add_parser("serveur", help="Lancer l'interface web")
    ps.add_argument("--hote", default="127.0.0.1")
    ps.add_argument("--port", type=int, default=8000)

    a = p.parse_args(argv)
    charger_env(".env")  # clés API : fichier .env à la racine du projet
    donnees = Path(a.donnees)
    base = Base(a.base or donnees / "base.sqlite")

    if a.commande == "ingerer":
        return ingerer(donnees, base, a.forcer)

    if a.commande == "regles":
        return regles_cli(base, donnees, a.contrat, a.faits, a.jeu)

    if a.commande == "banc":
        return banc_cli(base, donnees, a.contrat, a.methode, a.couches, a.repetitions, a.paralleles, a.figer, a.fiche)

    if a.commande == "legalbench":
        return legalbench_cli(donnees, a.telecharger, a.fichier, a.split, a.limite, a.paralleles)

    if a.commande == "rediger":
        return rediger_cli(base, a.contrat, a.article or [], a.controler, a.accepter, a.accepter_vocabulaire)

    if a.commande == "versions":
        from . import consignes

        if a.manifeste:
            for nom, info in consignes.ecrire_manifeste().items():
                print(f"{nom:<32} {info['version']:<8} {info['empreinte']}")
            print(f"Manifeste écrit : {consignes.MANIFESTE}")
            return 0
        if a.enregistrer:
            from .suivi import module_mlflow

            mlflow = module_mlflow()
            if mlflow is None:
                print("MLflow n'est pas disponible (pip install -e \".[suivi]\", ou MLFLOW_ACTIF=false).")
                return 1
            for ligne in consignes.enregistrer_dans_mlflow(mlflow):
                print(ligne)
            return 0
        problemes = consignes.verifier()
        for nom, info in consignes.etat_actuel().items():
            print(f"{nom:<32} {info['version']:<8} {info['empreinte']}")
        for p_ in problemes:
            print(f"! {p_}")
        return 1 if problemes else 0

    if a.commande == "modele":
        return tester_modele()

    if a.commande == "contrats":
        for c in base.contrats():
            print(f"{c.statut:<11} {c.id:<28} {c.assureur} — {c.produit} ({c.version})")
        return 0

    if a.commande == "clauses":
        for c in base.clauses(a.contrat):
            print(f"{c.id:>24}  {c.type.value:<10}  p.{','.join(map(str, c.pages)):<6}  {c.titre}")
        return 0

    if a.commande == "serveur":
        from .web import lancer

        lancer(base, hote=a.hote, port=a.port)
        return 0

    if a.commande == "analyser":
        import time

        from .journal import Journal

        debut = time.perf_counter()
        r = construire(base, a.contrat, a.methode).analyser(a.sinistre)
        Journal(base.chemin).noter(r, duree_ms=int((time.perf_counter() - debut) * 1000))
        print(r.model_dump_json(indent=2) if a.json else afficher(r) if a.detail else afficher_court(r))
        return 0

    return 1


def principal() -> int:
    """Point d'entrée : une erreur du fournisseur de modèle s'affiche en une ligne, sans trace."""
    from .llm import ErreurLLM

    try:
        return main()
    except ErreurLLM as e:
        print(f"Erreur du modèle : {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(principal())
