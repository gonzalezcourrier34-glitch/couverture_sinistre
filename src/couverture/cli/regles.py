"""`couverture regles` : vérifie les règles Prolog d'un contrat, sans appel au modèle."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from ..analyse import chaine, prolog
from ..analyse.validation import extrait_present
from ..contrat import tableaux
from ..contrat.base import Base
from ..mesure.evaluation import charger_cas, fichiers_jeu, lire_jsonl


def ajouter(sous) -> None:
    """Déclare la commande « regles » et ses options."""
    p = sous.add_parser("regles", help="Vérifier les règles Prolog d'un contrat (chargement, vocabulaire, citations, cas)")
    p.add_argument("--contrat", required=True)
    p.add_argument("--faits", help="Décider un cas : JSON des faits, ex. '{\"evenement\": \"vol\", \"lieu\": [\"cave\"]}'")
    p.add_argument("--jeu", choices=["mise_au_point", "validation", "redaction", "golden", "ferme"], default="mise_au_point",
                   help="Cas de mise au point (défaut), de validation (data/validation) ou des garanties rédigées par le modèle (data/redaction)")
    p.add_argument("--ranger", action="store_true",
                   help="Ranger le vocabulaire : commun.json, et un fichier par contrat pour ce que lui seul emploie")
    p.add_argument("--fusionner", metavar="ANCIENNE:NOUVELLE",
                   help="Deux variables qui posent la même question : l'ancienne est renommée partout (règles, "
                        "vocabulaire, cas, exemples) ; refusé si leurs valeurs diffèrent")
    p.add_argument("--bilan", action="store_true",
                   help="Le vocabulaire en chiffres : ce que chaque contrat partage, ce qu'il est seul à employer")
    p.set_defaults(executer=executer)


def _ranger() -> int:
    """`--ranger` : range le vocabulaire (commun, et un fichier par contrat)."""
    from .. import redaction
    deplacees = redaction.ranger()
    print("Vocabulaire rangé (regles/vocabulaire/)." + ("" if deplacees else " Rien n'a bougé."))
    for x in deplacees:
        print(f"  {x}")
    return 0


def _fusionner(a, donnees: Path) -> int:
    """`--fusionner ANCIENNE:NOUVELLE` : renomme une variable partout, si ses valeurs le permettent."""
    from .. import redaction
    ancienne, _, nouvelle = a.fusionner.partition(":")
    try:
        for ligne in redaction.fusionner_variables(ancienne.strip(), nouvelle.strip(), donnees=donnees):
            print(ligne)
    except ValueError as e:
        print(f"Refusé : {e}")
        return 1
    print("Puis : `couverture banc --contrat … --figer \"raison\"` si le golden set a changé, "
          "`couverture exemples --indexer`, et les bancs des contrats dont les règles ont changé.")
    return 0


def _bilan() -> int:
    """`--bilan` : le vocabulaire en chiffres."""
    from .. import redaction
    b = redaction.bilan()
    print(f"Vocabulaire : {b['variables']} variables.")
    for c, n in b["contrats"].items():
        print(f"  {c} : {n['employees']} employées, {n['partagees']} partagées "
              f"({n['partagees'] / n['employees']:.0%}), {n['propres']} propres")
    lues = b["propres_lues_dans_la_declaration"]
    print(f"Propres à un seul contrat : {len(b['propres'])}, dont {len(lues)} lues dans la déclaration.")
    print(f"Faits de souscription (conditions particulières) : {len(b['souscription'])} — {', '.join(b['souscription'])}")
    print(f"Jamais lues dans une déclaration : {len(b['non_lues'])}")
    if b["sans_regle"]:
        print(f"Employées par aucune règle : {', '.join(b['sans_regle'])}")
    return 0


def _decider_un_cas(contrat_id: str, faits_json: str) -> int:
    """`--faits` : décide un seul cas et montre l'arbre de preuve."""
    faits = json.loads(faits_json)
    for p_ in prolog.verifier_faits(faits):
        print(f"! {p_}")
    d = prolog.decider(contrat_id, faits)
    print(f"Décision : {d['decision']}")
    for r in d["retenues"]:
        print(f"  « {r['garantie']} » ({r['article']}) : {r['motif']}")
    if d.get("preuve"):
        print("Arbre de preuve :")
        print("\n".join(f"  {l}" for l in chaine.arbre_lisible(d["preuve"])))
    return 0


def _hors_vocabulaire(employes: list[dict]) -> list[str]:
    """2. Chaque variable et chaque valeur employées par les règles sont dans le vocabulaire."""
    voc, problemes = prolog.vocabulaire(), []
    for e in employes:
        if e["variable"] not in voc or e["valeur"] not in voc[e["variable"]]["valeurs"]:
            problemes.append(f"hors vocabulaire : {e['variable']} = {e['valeur']}")
    print(f"Vocabulaire : {len(employes)} couples (variable, valeur) employés, {len(problemes)} hors vocabulaire.")
    return problemes


def _citations_absentes(base: Base, contrat_id: str, citations: list[dict]) -> list[str]:
    """3. Chaque citation figure mot pour mot dans sa clause (si le contrat est en base)."""
    problemes: list[str] = []
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
    return problemes


def _ecarts_avec_les_formules(contrat_id: str) -> list[str]:
    """Le tableau des garanties par formule, lu à part (7.92) : une garantie ne doit pas jouer, dans les règles, pour
    une formule que le tableau ne lui donne pas."""
    pb_formules, notes_formules = tableaux.verifier(contrat_id, prolog.fichier_regles(contrat_id).read_text(encoding="utf-8"))
    if tableaux.chemin(contrat_id).exists():
        print(f"Tableau des formules : {len(pb_formules)} écart(s) avec les règles.")
    for n_ in notes_formules:
        print(f"  · {n_}")
    return pb_formules


def _cas_sur_faits_ideaux(contrat_id: str, jeu: str, donnees: Path) -> list[str]:
    """4. Les cas du jeu, décidés sur leurs faits idéaux, sans modèle : un couvert à tort est un problème."""
    problemes: list[str] = []
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
    return problemes


def executer(a, base: Base, donnees: Path) -> int:
    """Vérifie les règles Prolog d'un contrat, sans appel au modèle :
    1. SWI-Prolog est là et les règles se chargent sans avertissement ;
    2. chaque variable et chaque valeur employées sont dans le vocabulaire commun ;
    3. chaque citation figure mot pour mot dans la clause citée (si le contrat est en base) ;
    4. les cas de regles/cas/<contrat>.jsonl (faits « idéaux ») donnent la réponse attendue.
    Avec --faits '{"evenement": "vol", …}' : décide un seul cas."""
    contrat_id, faits_json, jeu = a.contrat, a.faits, a.jeu
    if a.ranger:
        return _ranger()
    if a.fusionner:
        return _fusionner(a, donnees)
    if a.bilan:
        return _bilan()
    exe = prolog.swipl()
    if exe is None:
        print("SWI-Prolog introuvable. Windows : `winget install SWI-Prolog.SWI-Prolog`, puis rouvrir PowerShell.")
        return 1
    version = subprocess.run([exe, "--version"], capture_output=True).stdout.decode("utf-8", "replace").strip()
    print(f"{version} ({exe})")
    try:
        if faits_json:
            return _decider_un_cas(contrat_id, faits_json)
        employes = prolog.executer(contrat_id, "vocabulaire_json")
        citations = prolog.executer(contrat_id, "citations_json")
    except prolog.ErreurRegles as e:
        print(f"Les règles ne se chargent pas : {e}")
        return 1
    print(f"Règles chargées : regles/{contrat_id}.pl")

    problemes = _hors_vocabulaire(employes)
    problemes += _citations_absentes(base, contrat_id, citations)
    problemes += _ecarts_avec_les_formules(contrat_id)
    problemes += _cas_sur_faits_ideaux(contrat_id, jeu, donnees)
    for p_ in problemes:
        print(f"! {p_}")
    print("Tout est en ordre." if not problemes else f"{len(problemes)} problème(s).")
    return 1 if problemes else 0


def tableau(rapport: dict) -> str:
    """Une ligne par cas, puis les indicateurs qui comptent."""
    lignes = [f"{'cas':<11}{'attendu':<14}{'obtenu':<14}{'':<4}confiance"]
    for c in rapport["cas"]:
        marque = "err" if c.get("erreur") else "ok" if c["obtenu"] == c["attendu"] else ("~" if c.get("acceptable") else "X")
        lignes.append(f"{c['id']:<11}{c['attendu']:<14}{c['obtenu']:<14}{marque:<4}{c['confiance']:.2f}")
    lignes.append("")
    lignes.append(f"Exactitude {rapport['exactitude']:.0%} (stricte {rapport['exactitude_stricte']:.0%})  ·  "
                  f"couverts à tort {rapport['faux_couverts']}  ·  refus à tort {rapport['faux_refus']}  ·  "
                  f"incertains {rapport['taux_incertain']:.0%}"
                  + (f"  ·  erreurs du fournisseur {rapport['erreurs_fournisseur']} (relancer)" if rapport.get("erreurs_fournisseur") else ""))
    lignes.append("ok : exact   ~ : réponse acceptable (cas ambigu)   X : erreur   err : pas de réponse du fournisseur   ·   détail : --detail")
    return "\n".join(lignes)
