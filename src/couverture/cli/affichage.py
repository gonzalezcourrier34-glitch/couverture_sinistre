"""Ce que la ligne de commande affiche d'une analyse : la version courte (ce qu'un gestionnaire lit d'abord) et le
détail (--detail)."""

from __future__ import annotations

from ..models import Resultat


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
    """Le détail d'une analyse (`--detail`) : décision, justification, conditions examinées, clauses citées, points
    à préciser, clauses consultées."""
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
