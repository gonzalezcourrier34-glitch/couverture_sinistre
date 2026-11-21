"""Méthode « regles », étape de rédaction : le modèle traduit une garantie du contrat en règles.

    clauses de l'article (et ses définitions) ─► Mistral Large ─► proposition JSON
        ─► règles Prolog générées par le code ─► contrôles ─► relecture humaine ─► --accepter

Le modèle n'écrit pas de Prolog : il remplit un schéma JSON (périmètre, circonstances,
obligations, exclusions, limites), et c'est le code qui écrit les règles. Un JSON se contrôle
champ par champ ; une syntaxe Prolog inventée ne se contrôle qu'en la chargeant.

Les contrôles, tous automatiques :
  1. structure : chaque condition est un terme connu (f, et, ou, non, si, concept) ;
  2. vocabulaire : chaque fait est dans regles/vocabulaire/ ; un fait nouveau doit être
     **déclaré** par le modèle (vocabulaire_manquant), et c'est un humain qui l'accepte ;
  3. citations : chaque phrase figure mot pour mot dans la clause citée (réparée si les mots sont
     dans l'ordre, refusée sinon) ;
  4. couverture : chaque exclusion de la liste du contrat est traduite, ou déclarée non traduite.
     Une exclusion oubliée, c'est un « couvert à tort » ;
  5. concepts et identifiants : rien d'inconnu, aucune collision avec les règles existantes ;
  6. avec SWI-Prolog : les règles fusionnées se chargent sans avertissement, et les cas déjà
     annotés gardent leur décision (les changements sont listés pour relecture).

La proposition (JSON) est la source : on peut la corriger à la main, puis relancer les contrôles
sans rappeler le modèle (`couverture rediger --controler`).
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from .. import prolog
from ..llm import appeler_json as _appeler, pour_travail_long as pour_compiler
from ..models import Clause
from .consigne import (PROPOSITIONS, SYSTEME_REDACTION, VERSION, ErreurProposition, clauses_article,
                       definitions_utiles, message_redaction)
from .controles import (A_RELIRE, BLOQUANT, INFO, circonstances_par_evenement, conditions_particulieres_en_reserve,
                        controler, controler_avec_prolog, cycle_de_concepts, envelopper_conditions_nues, erreurs_schema,
                        items_exclusion, non_traduits, obligations_mal_formees)
from .ecriture import atome, chaine, en_prolog, fusionner, terme
from .vocabulaire import (ACCESSOIRE, EXTENSION, JAMAIS, accepter_vocabulaire, mal_rangees, ranger, evenements_par_variable,
                          lieux_par_variable)

# Ce que le reste du code et les tests emploient, d'où qu'il vienne dans le paquet.
__all__ = ["ACCESSOIRE", "A_RELIRE", "BLOQUANT", "EXTENSION", "INFO", "JAMAIS", "PROPOSITIONS", "SYSTEME_REDACTION",
           "VERSION", "ErreurProposition", "accepter", "accepter_vocabulaire", "articles_proposes", "mal_rangees", "ranger", "atome", "chaine",
           "chemins", "circonstances_par_evenement", "conditions_particulieres_en_reserve", "controler",
           "controler_avec_prolog", "cycle_de_concepts", "en_prolog", "enregistrer", "erreurs_schema",
           "evenements_par_variable", "fusionner", "items_exclusion", "lieux_par_variable", "message_redaction",
           "obligations_mal_formees", "recontroler", "rediger", "resumer", "retirer_article", "sauver", "terme"]


# --- Les commandes ------------------------------------------------------------------------------------------

def chemins(contrat_id: str, article: str, dossier: Path | None = None) -> tuple[Path, Path]:
    base = (dossier or PROPOSITIONS) / contrat_id
    return base / f"{article}.json", base / f"{article}.pl"


def rediger(contrat_id: str, article: str, clauses: list[Clause], llm, dossier: Path | None = None,
            cas: list[tuple[str, dict]] | None = None) -> dict:
    """Fait rédiger la proposition par le modèle, l'enregistre et la contrôle."""
    contrat_pl = retirer_article(prolog.fichier_regles(contrat_id).read_text(encoding="utf-8"), article)
    textes = clauses_article(clauses, article)
    if not textes:
        raise LookupError(f"Aucune clause {article} dans le contrat {contrat_id}.")
    message = message_redaction(article, textes, definitions_utiles(clauses, textes), contrat_pl)
    llm_long = pour_compiler(llm, timeout=600)   # 300 s n'ont pas suffi pour 2.2 (7.22)
    prop = _appeler(llm_long, SYSTEME_REDACTION, message)
    meta = {"article": article, "modele": getattr(llm, "nom", "?"), "date": date.today().isoformat(),
            "consigne": "redaction-regles " + VERSION}
    sauver(contrat_id, article, {"meta": meta, "proposition": prop}, dossier)   # une rédaction coûte des minutes
    if isinstance(prop, dict):
        # Ce que le code sait remettre en forme ne vaut pas une reprise de plus de dix minutes (7.54).
        envelopper_conditions_nues(prop)
        prop["non_traduit"] = non_traduits(prop)
    schema = erreurs_schema(prop)
    if schema:
        # Une seule reprise : on renvoie au modèle ses écarts au schéma, en clair.
        meta["premiere_reponse"] = {"proposition": prop, "ecarts": schema}
        message += ("\n\n## Ta réponse précédente ne respecte pas le schéma\n" + "\n".join(f"- {e}" for e in schema)
                    + "\nRenvoie l'objet JSON complet, corrigé.")
        try:
            prop = _appeler(llm_long, SYSTEME_REDACTION, message)
        except ValueError:
            pass
    return enregistrer(contrat_id, article, {"meta": meta, "proposition": prop}, clauses, contrat_pl, dossier, cas)


def sauver(contrat_id: str, article: str, doc: dict, dossier: Path | None = None) -> None:
    js, _ = chemins(contrat_id, article, dossier)
    js.parent.mkdir(parents=True, exist_ok=True)
    js.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def enregistrer(contrat_id: str, article: str, doc: dict, clauses: list[Clause], contrat_pl: str,
                dossier: Path | None = None, cas: list[tuple[str, dict]] | None = None) -> dict:
    """Contrôle, écrit le JSON et les règles. `cas` (faits idéaux annotés) : avec SWI-Prolog, vérifie le
    chargement et la non-régression ; None : ces contrôles ne sont pas faits."""
    prop = doc["proposition"]
    doc["controles"] = controler(prop, clauses, contrat_pl, article)
    _, pl = chemins(contrat_id, article, dossier)
    sauver(contrat_id, article, doc, dossier)
    if pl.exists():
        pl.unlink()                       # des règles d'une version précédente ne doivent pas traîner
    if not any(p["controle"] == "structure" for p in doc["controles"]):
        m = doc.get("meta", {})
        texte = en_prolog(prop, article, f"{m.get('modele', '?')}, {m.get('date', '')}")
        pl.write_text(texte, encoding="utf-8")
        # Prolog s'arrête sur un concept inconnu : inutile de le lancer tant que les concepts bloquent.
        if cas is not None and not any(p["controle"] == "concept" and p["gravite"] == BLOQUANT for p in doc["controles"]):
            doc["controles"] += controler_avec_prolog(contrat_id, contrat_pl, texte, cas)
    sauver(contrat_id, article, doc, dossier)
    return doc


def recontroler(contrat_id: str, article: str, clauses: list[Clause], dossier: Path | None = None,
                cas: list[tuple[str, dict]] | None = None) -> dict:
    """Relit la proposition enregistrée (éventuellement corrigée à la main) et refait les contrôles."""
    js, _ = chemins(contrat_id, article, dossier)
    doc = json.loads(js.read_text(encoding="utf-8"))
    contrat_pl = retirer_article(prolog.fichier_regles(contrat_id).read_text(encoding="utf-8"), article)
    return enregistrer(contrat_id, article, doc, clauses, contrat_pl, dossier, cas)


def articles_proposes(contrat_id: str, dossier: Path | None = None) -> list[str]:
    base = (dossier or PROPOSITIONS) / contrat_id
    return sorted(p.stem for p in base.glob("*.json")) if base.exists() else []


def accepter(contrat_id: str, article: str, dossier: Path | None = None) -> Path:
    """Ajoute la proposition aux règles du contrat, si aucun contrôle ne bloque."""
    js, pl = chemins(contrat_id, article, dossier)
    doc = json.loads(js.read_text(encoding="utf-8"))
    bloquants = [p for p in doc.get("controles", []) if p["gravite"] == BLOQUANT]
    if bloquants:
        raise ErreurProposition(f"{len(bloquants)} contrôle(s) bloquant(s) : relancer `--controler` après correction")
    cible = prolog.fichier_regles(contrat_id)
    cible.write_text(fusionner(retirer_article(cible.read_text(encoding="utf-8"), article), pl.read_text(encoding="utf-8")),
                     encoding="utf-8")
    ranger()   # les variables que ces règles sont seules à employer vont dans le fichier du contrat (7.119)
    return cible


def retirer_article(contrat_pl: str, article: str) -> str:
    """Les règles du contrat sans le bloc d'une proposition déjà acceptée pour cet article : une proposition
    corrigée puis acceptée de nouveau remplace l'ancienne au lieu de s'y ajouter (7.58)."""
    entete = re.compile(rf"^% --- Art\. {re.escape(article)} : proposition.*$", re.M)
    m = entete.search(contrat_pl)
    if not m:
        return contrat_pl
    suite = re.compile(r"^% --- Art\. ", re.M).search(contrat_pl, m.end())
    return (contrat_pl[:m.start()].rstrip("\n") + "\n" + (contrat_pl[suite.start():] if suite else "")).rstrip("\n") + "\n"


def resumer(doc: dict) -> str:
    prop, ctl = doc["proposition"], doc.get("controles", [])
    g = prop.get("garanties", [])
    n = lambda cle: sum(len(x.get(cle, [])) for x in g) + (len(prop.get("exclusions_communes") or [])  # noqa: E731
                                                           if cle == "exclusions" else 0)
    lignes = [f"Art. {doc.get('meta', {}).get('article', '?')} : {len(g)} garantie(s) "
              f"({', '.join(x.get('id', '?') for x in g)}), {n('exclusions')} exclusion(s), "
              f"{n('circonstances')} circonstance(s), {n('obligations')} obligation(s), {n('limites')} limite(s)"
              + (f", {len(prop['extensions'])} extension(s) ({', '.join(sorted({x.get('concept', '?') for x in prop['extensions']}))})"
                 if prop.get("extensions") else "") + " ; "
              f"événements : {', '.join(prop.get('evenements', [])) or 'aucun'}"]
    for m in prop.get("vocabulaire_manquant", []):
        lignes.append(f"  + vocabulaire proposé : {m.get('variable')} = {', '.join(map(str, m.get('valeurs', [])))} "
                      f"— « {m.get('question', '')} » ({m.get('pourquoi', '')})")
    for gravite in (BLOQUANT, A_RELIRE, INFO):
        for p in ctl:
            if p["gravite"] == gravite:
                lignes.append(f"  {'!' if gravite == BLOQUANT else '?' if gravite == A_RELIRE else '·'} "
                              f"[{p['controle']}] {p['message']}")
    nb = sum(p["gravite"] == BLOQUANT for p in ctl)
    lignes.append("  → aucun contrôle bloquant : `--accepter` possible après relecture" if not nb
                  else f"  → {nb} contrôle(s) bloquant(s)")
    return "\n".join(lignes)
