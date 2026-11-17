"""Ligne de commande.

  couverture ingerer                               # lit data/contrats/ et remplit la base
  couverture contrats                              # liste les contrats et leur statut
  couverture clauses  --contrat foyer-appart123-2025
  couverture analyser --contrat foyer-appart123-2025 "Mon vélo a été volé dans le local commun…"
  couverture evaluer  --contrat fictif-habitat-serein [--methode brut]
  couverture comparer --contrat fictif-habitat-serein
  couverture serveur  --port 8000
  couverture reparer                              # propose un profil pour les contrats à vérifier
  couverture propositions [--accepter N | --refuser N]
  couverture versions [--manifeste | --enregistrer] # consignes versionnées (manifeste, MLflow)
  couverture derive                               # PSI des 7 derniers jours contre les 28 précédents
  couverture bilan [--envoyer]                    # ce qui demande une intervention, puis les chiffres
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from .base import Base
from .config import charger_env
from .evaluation import charger_cas, evaluer
from .ingestion import ingerer_dossier
from .juges import JugeHeuristique
from .models import Resultat
from .pipeline import Pipeline, PipelineDocumentBrut, llm_configure


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
        for c in v.conditions:
            if c.groupe != groupe:
                groupe = c.groupe
                titre = f"Garantie « {groupe} »" if c.nature == "garantie" else groupe
                lignes.append(titre + " :")
            etat = "" if c.nature == "limite" else f"[{symbole[c.etat.value]}] "
            preuve = f"art. {c.clause_id}" + (f", p. {', '.join(map(str, c.pages))}" if c.pages else "")
            marque = "  ← décisif" if c.decisive else ("  [ÉCARTÉE : citation introuvable]" if not c.valide else "")
            lignes.append(f"  {etat}{c.enonce} ({preuve}){marque}")
            if c.valide and c.nature != "limite":
                lignes.append(f"        « {c.extrait} »")
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


METHODES = ["conditions", "direct", "brut"]


def construire(base: Base, contrat_id: str, methode: str, hors_ligne: bool):
    """conditions : grille condition par condition, décision calculée (méthode principale) ;
    direct : verdict du modèle en un coup sur les clauses retenues ;
    brut : contrat entier dans le prompt, sans recherche (référence « chatbot »)."""
    if hors_ligne:
        return Pipeline.depuis_base(base, contrat_id, juge=JugeHeuristique())
    if methode in ("brut", "direct") and llm_configure() is None:
        sys.exit(f"La méthode « {methode} » a besoin d'un modèle : définir ANTHROPIC_API_KEY ou COUVERTURE_LLM_URL.")
    if methode == "brut":
        return PipelineDocumentBrut.depuis_base(base, contrat_id, llm_configure())
    return Pipeline.depuis_base(base, contrat_id, methode=methode)


def ingerer(donnees: Path, base: Base, forcer: bool = False) -> int:
    from .llm import configurer_embeddings

    vectoriseur = configurer_embeddings()
    if vectoriseur is None:
        print("Sans clé Mistral : pas d'embeddings, la recherche se fera par les mots seuls.")
    juge_qualite = llm_configure()
    from .suivi import EXPERIENCE_INGESTION, execution, metriques_ingestion, parametres_communs

    with execution(EXPERIENCE_INGESTION, "ingestion") as suivi:
        contrats = ingerer_dossier(donnees / "contrats", base, forcer=forcer, vectoriseur=vectoriseur,
                                   juge_qualite=juge_qualite)
        suivi.parametres(parametres_communs(juge_qualite, None, vectoriseur) | {"forcer": forcer})
        suivi.metriques(metriques_ingestion(contrats))
        suivi.artefact_json("rapports.json", {c.id: c.rapport for c in contrats})
    for c in contrats:
        print(f"{c.statut:<11} {c.id:<28} {c.rapport.get('nb_clauses', 0):>4} clauses  {c.rapport.get('par_type', {})}")
        if "embeddings" in c.rapport:
            print(f"{'':<11}   embeddings : {c.rapport['embeddings']}")
        q = c.rapport.get("qualite", {})
        if "score" in q:
            print(f"{'':<11}   qualité du typage : {q['score']:.0%} confirmés sur {q['echantillon']} clauses ({q['modele']})")
        elif "erreur" in q:
            print(f"{'':<11}   qualité du typage : non jugée ({q['erreur']})")
        for alerte in c.rapport.get("alertes", []):
            print(f"{'':<11} ! {alerte}")
    if any(c.statut != "OK" for c in base.contrats()):
        print("\nDes contrats sont à vérifier : `couverture reparer` propose une correction (validée par vous).")
    return 0


def reparer(donnees: Path, base: Base, contrat_id: str | None) -> int:
    from .chargement import charger_lignes
    from .ingestion import charger_catalogue
    from .profils import charger_profil
    from .reparation import Propositions, decrire, proposer_reparation
    from .texte import normaliser

    llm = llm_configure()
    if llm is None:
        print("La réparation a besoin d'un modèle : renseigner MISTRAL_API_KEY dans le fichier .env.")
        return 1
    cibles = [base.contrat(contrat_id)] if contrat_id else [c for c in base.contrats() if c.statut != "OK"]
    if not cibles:
        print("Aucun contrat à vérifier.")
        return 0
    catalogue = charger_catalogue(donnees / "contrats")
    depot = Propositions(donnees)
    for c in cibles:
        meta = catalogue.get(c.fichier, {})
        nom = meta.get("profil") or re.sub(r"[^a-z0-9]+", "-", normaliser(c.assureur or c.id)).strip("-")[:40]
        actuel = charger_profil(donnees / "profils", meta["profil"]) if meta.get("profil") else None
        lignes = charger_lignes(donnees / "contrats" / c.fichier)
        print(f"Analyse de {c.id} ({llm.nom})…")
        p = proposer_reparation(c.id, c.fichier, lignes, c.rapport, actuel, nom, llm, depot)
        print(decrire(p))
    print("\nRien n'est appliqué sans vous : `couverture propositions --accepter N` ou `--refuser N`.")
    return 0


def propositions(donnees: Path, base: Base, accepter: int | None, refuser: int | None) -> int:
    from .reparation import Propositions, decrire

    depot = Propositions(donnees)
    if accepter is not None:
        p = depot.accepter(accepter)
        print(f"Proposition {accepter} acceptée : profil « {p['profil']['nom']} » écrit, rattaché à {p['fichier']}.")
        print("Relecture du contrat avec ce profil :")
        return ingerer(donnees, base)
    if refuser is not None:
        depot.refuser(refuser)
        print(f"Proposition {refuser} refusée.")
        return 0
    toutes = depot.toutes()
    if not toutes:
        print("Aucune proposition.")
    for p in toutes:
        print(decrire(p) + "\n")
    return 0


def tester_modele() -> int:
    from .llm import ErreurLLM

    try:
        llm = llm_configure()
    except ErreurLLM as e:
        print(f"Configuration invalide : {e}")
        return 1
    if llm is None:
        print("Aucun modèle configuré : le juge heuristique (sans modèle) sera utilisé.")
        print("Créer un fichier .env à la racine du projet avec la ligne : MISTRAL_API_KEY=votre-clé")
        return 1
    print(f"Modèle configuré : {llm.nom}")
    try:
        reponse = llm.completer('Réponds uniquement par un objet JSON.', 'Renvoie {"ok": true}.')
    except ErreurLLM as e:
        print(f"Échec de la connexion : {e}")
        return 1
    print(f"Connexion réussie. Réponse : {reponse.strip()[:200]}")
    from .llm import configurer_embeddings

    vectoriseur = configurer_embeddings()
    if vectoriseur:
        try:
            dim = len(vectoriseur.vectoriser(["vol de vélo"])[0])
            print(f"Embeddings : {vectoriseur.nom}, vecteurs de dimension {dim}.")
        except ErreurLLM as e:
            print(f"Embeddings indisponibles ({e}) : la recherche se fera par les mots seuls.")
    return 0


def evaluer_suivi(base: Base, donnees: Path, contrat_id: str, methode: str, hors_ligne: bool, cas: list) -> dict:
    """Une évaluation, enregistrée comme une exécution MLflow (si le suivi est disponible)."""
    from .suivi import EXPERIENCE_EVALUATION, empreinte_fichiers, execution, metriques_evaluation, parametres_communs

    pipeline = construire(base, contrat_id, methode, hors_ligne)
    juge = getattr(pipeline, "juge", None)
    llm = getattr(juge, "llm", None)
    relecteur = getattr(juge, "relecteur", None)
    vectoriseur = getattr(getattr(pipeline, "recherche", None), "vectoriseur", None)
    nom = f"{contrat_id} · {getattr(pipeline, 'methode', methode)}"
    with execution(EXPERIENCE_EVALUATION, nom) as suivi:
        rapport = evaluer(pipeline, cas)
        suivi.parametres(parametres_communs(llm, relecteur, vectoriseur) | {
            "contrat": contrat_id,
            "methode": getattr(pipeline, "methode", methode),
            "jeu_de_test": empreinte_fichiers(donnees / "sinistres.jsonl", donnees / "annotations" / f"{contrat_id}.jsonl"),
            "contrat_empreinte": base.empreinte(contrat_id) or "",
        })
        suivi.metriques(metriques_evaluation(rapport))
        suivi.artefact_json("rapport.json", rapport)
    return rapport


def resume(rapport: dict) -> dict:
    return {k: v for k, v in rapport.items() if k != "cas"}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="couverture", description="Le sinistre est-il couvert par les conditions générales ?")
    p.add_argument("--donnees", default="data", help="Dossier des données (défaut : data)")
    p.add_argument("--base", default=None, help="Base SQLite (défaut : <donnees>/base.sqlite)")
    sous = p.add_subparsers(dest="commande", required=True)

    pi = sous.add_parser("ingerer", help="Lire les contrats de <donnees>/contrats et remplir la base")
    pi.add_argument("--forcer", action="store_true", help="Relire même les fichiers inchangés")

    sous.add_parser("contrats", help="Lister les contrats de la base")

    pc = sous.add_parser("clauses", help="Afficher le découpage d'un contrat")
    pc.add_argument("--contrat", required=True)

    pa = sous.add_parser("analyser", help="Analyser un sinistre sur un contrat")
    pa.add_argument("--contrat", required=True)
    pa.add_argument("sinistre")
    pa.add_argument("--methode", choices=METHODES, default="conditions")
    pa.add_argument("--json", action="store_true", help="Sortie JSON complète (traçabilité)")
    pa.add_argument("--hors-ligne", action="store_true", help="Juge heuristique, sans modèle")

    pe = sous.add_parser("evaluer", help="Évaluer sur les sinistres annotés d'un contrat")
    pe.add_argument("--contrat", required=True)
    pe.add_argument("--methode", choices=METHODES, default="conditions")
    pe.add_argument("--hors-ligne", action="store_true")
    pe.add_argument("--detail", action="store_true", help="Afficher chaque cas")

    pk = sous.add_parser("comparer", help="Conditions, verdict direct et document brut, sur les mêmes cas")
    pk.add_argument("--contrat", required=True)

    sous.add_parser("modele", help="Afficher le modèle configuré et tester la connexion")

    pr = sous.add_parser("reparer", help="Proposer un profil d'assureur pour un contrat mal lu (à valider)")
    pr.add_argument("--contrat", help="Un contrat précis (par défaut : tous ceux à vérifier)")

    pp = sous.add_parser("propositions", help="Lister, accepter ou refuser les propositions de réparation")
    pp.add_argument("--accepter", type=int, metavar="N")
    pp.add_argument("--refuser", type=int, metavar="N")

    pv = sous.add_parser("versions", help="Versions des consignes : vérifier, réécrire le manifeste, enregistrer dans MLflow")
    groupe = pv.add_mutually_exclusive_group()
    groupe.add_argument("--manifeste", action="store_true", help="Réécrire config/versions_consignes.json")
    groupe.add_argument("--enregistrer", action="store_true", help="Enregistrer les consignes dans MLflow (Prompt Registry)")

    pd = sous.add_parser("derive", help="Dérive des questions et des réponses (PSI, 7 jours contre 28)")
    pd.add_argument("--jours", type=int, default=7)
    pd.add_argument("--reference", type=int, default=28)

    pb = sous.add_parser("bilan", help="Bilan de la période : à faire, contrats, activité, ce qui manque, dérive")
    pb.add_argument("--jours", type=int, default=7)
    pb.add_argument("--sortie", help="Fichier Markdown (défaut : <donnees>/bilans/bilan-AAAA-MM-JJ.md)")
    pb.add_argument("--envoyer", action="store_true", help="Envoyer par mail (SMTP configuré dans .env)")

    ps = sous.add_parser("serveur", help="Lancer l'interface web")
    ps.add_argument("--hote", default="127.0.0.1")
    ps.add_argument("--port", type=int, default=8000)

    a = p.parse_args(argv)
    charger_env(".env")  # clés API : fichier .env à la racine du projet
    donnees = Path(a.donnees)
    base = Base(a.base or donnees / "base.sqlite")

    if a.commande == "ingerer":
        return ingerer(donnees, base, a.forcer)

    if a.commande == "reparer":
        return reparer(donnees, base, a.contrat)

    if a.commande == "propositions":
        return propositions(donnees, base, a.accepter, a.refuser)

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

    if a.commande == "derive":
        from .derive import calculer
        from .journal import Journal

        d = calculer(Journal(base.chemin), jours=a.jours, reference=a.reference)
        print(f"{d['periode']} : {d['volumes']['recent']} analyses contre {d['volumes']['reference']}. Statut : {d['statut']}.")
        for nom, v in d["variables"].items():
            print(f"  {nom:<18} {v['famille']:<10} PSI {v['psi']:<7} {v['niveau']}")
        for contrat, v in d["contrats"].items():
            print(f"  {contrat:<28} INCERTAIN {v['incertain_recent']:.0%} (référence : "
                  f"{'—' if v['incertain_reference'] is None else format(v['incertain_reference'], '.0%')})")
        for alerte in d["alertes"]:
            print(f"  ! {alerte}")
        return 0

    if a.commande == "bilan":
        from datetime import date

        from .bilan import construire_bilan, envoyer

        texte, chiffres = construire_bilan(base, donnees, jours=a.jours)
        sortie = Path(a.sortie) if a.sortie else donnees / "bilans" / f"bilan-{date.today().isoformat()}.md"
        sortie.parent.mkdir(parents=True, exist_ok=True)
        sortie.write_text(texte, encoding="utf-8")
        print(texte)
        print(f"Bilan écrit dans {sortie}.")
        if a.envoyer:
            print(envoyer(texte, f"Couverture sinistre — bilan ({chiffres['a_faire']} point(s) à traiter)"))
        return 0

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
        r = construire(base, a.contrat, a.methode, a.hors_ligne).analyser(a.sinistre)
        Journal(base.chemin).noter(r, duree_ms=int((time.perf_counter() - debut) * 1000))
        print(r.model_dump_json(indent=2) if a.json else afficher(r))
        return 0

    cas = charger_cas(donnees / "sinistres.jsonl", donnees / "annotations" / f"{a.contrat}.jsonl")

    if a.commande == "evaluer":
        rapport = evaluer_suivi(base, donnees, a.contrat, a.methode, a.hors_ligne, cas)
        json.dump(rapport if a.detail else resume(rapport), sys.stdout, ensure_ascii=False, indent=2)
        print()
        return 0

    # comparer
    ordre = ["brut", "direct", "conditions"]
    resultats = {m: resume(evaluer_suivi(base, donnees, a.contrat, m, False, cas)) for m in ordre}
    cles = ["exactitude", "exactitude_avant_controle", "faux_couverts", "faux_couverts_avant_controle",
            "taux_incertain", "rappel_clauses_moyen", "citations_rejetees",
            "decisions_changees_par_relecture", "faux_couverts_evites_par_relecture"]
    print(f"{'':<30}" + "".join(f"{m:>14}" for m in ordre))
    for k in cles:
        print(f"{k:<30}" + "".join(f"{str(resultats[m][k]):>14}" for m in ordre))
    return 0


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
