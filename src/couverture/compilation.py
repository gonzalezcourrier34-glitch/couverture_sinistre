"""Compilation du contrat : chaque garantie traduite une fois pour toutes en fiche de questions.

Pourquoi : les garanties, leurs conditions et leurs exclusions sont des propriétés du
**contrat**, pas du sinistre. Les faire reformuler par le modèle à chaque question (méthode
« conditions ») donne une grille un peu différente à chaque fois, et les erreurs de
formulation (sens inversé, mauvais objet, définition non citée) se répètent sans fin.
Compilées une fois, elles sont contrôlées une fois : par le code (chaque extrait doit figurer
mot pour mot dans la clause citée), puis par un humain (export, relecture, import).

Unité de compilation : une garantie (ses morceaux « 2.14~1 », « 2.14~2 » réunis) et son
enveloppe :
  - ses sous-sections (« 2.10 Vol » → « 2.10-a Exclusions ») ;
  - sinon, quand le contrat range exclusions et conditions en fin de section (« 4.4 Ce qui
    n'est pas garanti » pour 4.1, 4.2, 4.3), ces clauses de la même section ;
  - les clauses visées par un renvoi et les définitions des termes employés.
Les exclusions générales sont compilées à part et s'ajoutent à toutes les fiches.
"""

from __future__ import annotations

import copy
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from .juges import extraire_json
from .llm import LLM, ErreurLLM, ReponseTronquee
from .models import Clause, ContratCompile, Fiche, Point, TypeClause
from .texte import normaliser
from .validation import extrait_present, passage_exact

# Vocabulaire commun à la compilation (ce que vise une garantie) et à l'analyse (ce que
# décrit le sinistre, voir `faits.EVENEMENTS`) : c'est lui qui relie les deux.
EVENEMENTS = ("vol", "vandalisme", "incendie", "degat_des_eaux", "bris", "tempete", "catastrophe_naturelle",
              "electricite", "dommage_accidentel", "responsabilite", "autre")

SYSTEME_COMPILATION = """Tu es juriste en assurance. On te donne une garantie de conditions générales et les clauses qui l'encadrent (exclusions, conditions, limites, définitions), chacune précédée de son identifiant entre crochets. Traduis-la en fiche de vérification : des questions fermées, réutilisables pour n'importe quel sinistre, auxquelles un gestionnaire répondra plus tard en lisant la déclaration.

Règles :
- Une clause peut contenir plusieurs garanties distinctes (« extensions », « garanties complémentaires ») : fais alors une fiche par garantie.
- "evenements" : parmi {evenements}. Ce que la garantie indemnise, pas ce qu'elle exclut.
- "conditions" : ce qui doit être vrai pour que la garantie joue. Une condition = un seul fait vérifiable. Formule-la pour que OUI soit favorable à l'assuré (« Le bien volé se trouvait-il dans les locaux d'habitation ? »). La première condition est toujours « L'événement est-il un … au sens du contrat ? » ; quand le terme est défini, cite la définition.
- "exclusions" : ce qui retire la garantie, formulé pour que OUI veuille dire que l'exclusion s'applique. "a_demander" : true si c'est un fait qu'on demanderait à l'assuré (lieu, fermeture à clé, inoccupation, entretien, nature du bien) ; false si l'exclusion est présumée absente tant que la déclaration ne l'évoque pas (faute intentionnelle, guerre, nucléaire, complicité…).
- "limites" : franchises, plafonds, vétusté, sous-limites.
- "extrait" : passage copié mot pour mot de la clause citée, 30 mots au plus, qui contient les mots qui fondent la question.
- Une question ne porte que sur l'objet ou le lieu exact que vise sa clause.
- Au plus 8 conditions, 10 exclusions et 5 limites par fiche. N'invente rien qui ne soit pas dans les clauses.

Réponds uniquement par un objet JSON :
{{"fiches": [{{"nom": "Vol", "clause_id": "2.10", "evenements": ["vol"], "objet": "une phrase : ce que couvre la garantie",
  "conditions": [{{"enonce": "…", "clause_id": "…", "extrait": "…"}}],
  "exclusions": [{{"enonce": "…", "clause_id": "…", "extrait": "…", "a_demander": true}}],
  "limites": [{{"enonce": "…", "clause_id": "…", "extrait": "…"}}]}}]}}""".format(evenements=", ".join(EVENEMENTS))

SYSTEME_EXCLUSIONS_GENERALES = """Tu es juriste en assurance. On te donne les exclusions générales d'un contrat, qui s'appliquent à toutes les garanties. Traduis chaque exclusion en question fermée, formulée pour que OUI veuille dire que l'exclusion s'applique.

- "a_demander" : true si c'est un fait qu'un gestionnaire demanderait à l'assuré ; false si l'exclusion est présumée absente tant que la déclaration ne l'évoque pas (faute intentionnelle, guerre, émeute, nucléaire, usure…).
- "extrait" : passage copié mot pour mot de la clause, 30 mots au plus.
- Au plus 15 questions. N'invente rien.

Réponds uniquement par un objet JSON :
{"exclusions": [{"enonce": "…", "clause_id": "…", "extrait": "…", "a_demander": false}]}"""


def base_id(clause_id: str) -> str:
    """« 2.14~2 » → « 2.14 » : les morceaux d'une longue clause forment une seule garantie."""
    return clause_id.split("~")[0]


def generale(c: Clause) -> bool:
    return c.type == TypeClause.EXCLUSION and "general" in normaliser(" ".join(c.chemin))


def unites(clauses: list[Clause]) -> list[tuple[str, list[Clause]]]:
    """Les garanties à compiler et, pour chacune, les clauses qu'on montre au modèle."""
    garanties: dict[str, list[Clause]] = {}
    for c in clauses:
        if c.type == TypeClause.GARANTIE:
            garanties.setdefault(base_id(c.id), []).append(c)
    index = {c.id: c for c in clauses}
    enveloppe = (TypeClause.EXCLUSION, TypeClause.CONDITION, TypeClause.LIMITE)
    # Le contrat range-t-il les exclusions en sous-sections de chaque garantie (« 2.10-a ») ?
    avec_sous_sections = {c.groupe for c in clauses if c.groupe in garanties}

    resultat = []
    for gid, morceaux in garanties.items():
        groupe = morceaux[0].groupe
        retenues = {c.id: c for c in morceaux}
        for c in clauses:
            if c.id in retenues or generale(c):
                continue
            if base_id(c.groupe) == gid:
                retenues[c.id] = c
            elif not avec_sous_sections and c.groupe == groupe and c.type in enveloppe:
                retenues[c.id] = c
        for c in list(retenues.values()):
            for cible in c.renvois:
                if cible in index and not generale(index[cible]):
                    retenues.setdefault(cible, index[cible])
        contexte = normaliser(" ".join(c.texte for c in retenues.values()))
        for c in clauses:
            if c.type == TypeClause.DEFINITION and normaliser(c.titre) and normaliser(c.titre) in contexte:
                retenues.setdefault(c.id, c)
        ordre = {c.id: n for n, c in enumerate(clauses)}
        resultat.append((gid, sorted(retenues.values(), key=lambda c: ordre[c.id])))
    return resultat


def formater(clauses: list[Clause], limite: int = 4000) -> str:
    return "\n\n".join(f"[{c.id}] ({c.type.value}) {' > '.join(c.chemin)}\n{c.texte[:limite]}" for c in clauses)


def _appeler(llm: LLM, systeme: str, message: str, tentatives: int = 2) -> dict:
    erreur: Exception | None = None
    for _ in range(tentatives):
        try:
            return extraire_json(llm.completer(systeme, message))
        except ErreurLLM:
            raise
        except ReponseTronquee as e:
            erreur = e
            message += "\n\nTa réponse précédente était trop longue. Recommence plus court : moins de questions, extraits brefs."
        except Exception as e:  # noqa: BLE001
            erreur = e
            message += "\n\nTa réponse précédente n'était pas un JSON valide. Réponds uniquement par l'objet JSON."
    raise ValueError(str(erreur))


def reparer_citation(p: Point, clause: Clause | None, clauses: dict[str, Clause]) -> Clause | None:
    """Deux erreurs de citation fréquentes, réparées par le code sans rien inventer :
    1. le bon texte sous le mauvais numéro (une définition citée sous l'article qui emploie le
       mot) : on le rattache à la clause fournie qui le contient vraiment ;
    2. des mots sautés sans « … » : on remplace l'extrait par le passage littéral du contrat
       (`validation.passage_exact`).
    Renvoie la clause qui porte désormais la citation (inchangée si rien n'a pu être réparé)."""
    if not p.extrait or (clause is not None and extrait_present(p.extrait, clause.texte)):
        return clause
    candidates = ([clause] if clause is not None else []) + [c for c in clauses.values() if c is not clause]
    trouvee = next((c for c in candidates if extrait_present(p.extrait, c.texte)), None)
    if trouvee is not None:
        p.clause_id = trouvee.id
        return trouvee
    for c in candidates:
        passage = passage_exact(p.extrait, c.texte)
        if passage:
            p.extrait, p.clause_id = passage, c.id
            return c
    return clause


def reparer_compilation(compilation: ContratCompile, clauses: list[Clause]) -> int:
    """Applique `reparer_citation` aux questions écartées d'une compilation existante, sans
    appeler le modèle. Chaque question n'est cherchée que dans les clauses de sa garantie."""
    par_unite = {gid: {c.id: c for c in cs} for gid, cs in unites(clauses)}
    generales = {c.id: c for c in clauses if generale(c)}
    reparees = 0
    for f in compilation.fiches:
        fournies = par_unite.get(f.id.split("#")[0], {})
        for p in f.conditions + f.exclusions + f.limites:
            if not p.valide:
                clause = reparer_citation(p, fournies.get(p.clause_id), fournies)
                if clause is not None and extrait_present(p.extrait, clause.texte):
                    p.valide, p.pages, reparees = True, clause.pages, reparees + 1
    for p in compilation.exclusions_generales:
        if not p.valide:
            clause = reparer_citation(p, generales.get(p.clause_id), generales)
            if clause is not None and extrait_present(p.extrait, clause.texte):
                p.valide, p.pages, reparees = True, clause.pages, reparees + 1
    if reparees:
        valides = {p.enonce for p in compilation.points() if p.valide}
        compilation.avertissements = [a for a in compilation.avertissements
                                      if not any(f"« {e} »" in a for e in valides)]
        utilisables = {f.id for f in compilation.fiches if any(p.valide for p in f.conditions)}
        compilation.avertissements = [a for a in compilation.avertissements
                                      if not (a.endswith("fiche inutilisable.") and a.split(" ")[0] in utilisables)]
    return reparees


def _points(donnees: list, nature: str, prefixe: str, clauses: dict[str, Clause],
            avertissements: list[str]) -> list[Point]:
    """Lit les questions du modèle et vérifie chaque extrait dans la clause citée."""
    points = []
    for n, d in enumerate(donnees or [], start=1):
        p = Point(id=f"{prefixe}.{nature[0]}{n}", nature=nature, enonce=str(d.get("enonce", "")).strip(),
                  clause_id=str(d.get("clause_id", "")), extrait=str(d.get("extrait", "")).strip(),
                  a_demander=bool(d.get("a_demander", True)))
        clause = clauses.get(p.clause_id)
        if not p.enonce:
            continue
        clause = reparer_citation(p, clause, clauses)
        if clause is None or not extrait_present(p.extrait, clause.texte):
            p.valide = False
            raison = "clause non fournie" if clause is None else "extrait introuvable"
            avertissements.append(f"{prefixe} : « {p.enonce} » écartée ({raison}, art. {p.clause_id}).")
        else:
            p.pages = clause.pages
        points.append(p)
    return points


def compiler_garantie(gid: str, clauses: list[Clause], llm: LLM) -> tuple[list[Fiche], list[str], bool]:
    """Fiches de la garantie, avertissements, et vrai si la compilation a échoué (à refaire)."""
    message = f"## Garantie {gid} et clauses qui l'encadrent\n\n{formater(clauses)}"
    avertissements: list[str] = []
    try:
        donnees = _appeler(llm, SYSTEME_COMPILATION, message)
    except ErreurLLM:
        raise
    except Exception as e:  # noqa: BLE001
        return [], [f"Garantie {gid} non compilée : {e}"], True
    fournies = {c.id: c for c in clauses}
    fiches = []
    brutes = donnees.get("fiches", [])
    for n, f in enumerate(brutes, start=1):
        fid = gid if len(brutes) == 1 else f"{gid}#{n}"
        evts = [e for e in f.get("evenements", []) if e in EVENEMENTS] or ["autre"]
        fiche = Fiche(
            id=fid, nom=str(f.get("nom") or f"Garantie {gid}"), clause_id=str(f.get("clause_id") or gid),
            evenements=evts, objet=str(f.get("objet", "")),
            conditions=_points(f.get("conditions"), "condition", fid, fournies, avertissements),
            exclusions=_points(f.get("exclusions"), "exclusion", fid, fournies, avertissements),
            limites=_points(f.get("limites"), "limite", fid, fournies, avertissements),
        )
        if not any(p.valide for p in fiche.conditions):
            avertissements.append(f"{fid} « {fiche.nom} » : aucune condition vérifiée, fiche inutilisable.")
        fiches.append(fiche)
    if not fiches:
        avertissements.append(f"Garantie {gid} : le modèle n'a produit aucune fiche.")
    return fiches, avertissements, False


def compiler_exclusions_generales(clauses: list[Clause], llm: LLM) -> tuple[list[Point], list[str]]:
    generales = [c for c in clauses if generale(c)]
    if not generales:
        return [], []
    try:
        donnees = _appeler(llm, SYSTEME_EXCLUSIONS_GENERALES, f"## Exclusions générales\n\n{formater(generales)}")
    except ErreurLLM:
        raise
    except Exception as e:  # noqa: BLE001
        return [], [f"Exclusions générales non compilées : {e}"]
    avertissements: list[str] = []
    points = _points(donnees.get("exclusions"), "exclusion", "general", {c.id: c for c in generales}, avertissements)
    return points, avertissements


def pour_compiler(llm: LLM, max_tokens: int = 16000, timeout: int = 300) -> LLM:
    """La compilation se fait une fois par contrat : on laisse au modèle le temps de réfléchir.
    Mistral Large réfléchit longuement sur une clause complexe (jusqu'à 7 500 tokens observés
    sur « Défense et recours ») : avec 8 000 tokens et 120 s, la fiche était coupée."""
    copie = copy.copy(llm)
    if hasattr(copie, "max_tokens"):
        copie.max_tokens = max(getattr(copie, "max_tokens", 0), max_tokens)
    if hasattr(copie, "timeout"):
        copie.timeout = max(getattr(copie, "timeout", 0), timeout)
    if hasattr(copie, "extra"):
        copie.extra = dict(copie.extra)
    return copie


def a_refaire(existante: ContratCompile | None, travaux: list[tuple[str, list[Clause]]]) -> set[str]:
    """Toutes les garanties pour une première compilation ; sinon celles qui avaient échoué."""
    if existante is None:
        return {gid for gid, _ in travaux}
    # Compilations antérieures au champ `echecs` : l'échec est dans les avertissements.
    anciens = {m.group(1) for a in existante.avertissements if (m := re.match(r"Garantie (\S+) non compilée", a))}
    return (set(existante.echecs) | anciens) & {gid for gid, _ in travaux}


def compiler(contrat_id: str, empreinte: str, clauses: list[Clause], llm: LLM, paralleles: int = 4,
             existante: ContratCompile | None = None, progression=None) -> ContratCompile:
    """Une requête par garantie (en parallèle) et une pour les exclusions générales.
    Avec `existante` (même contrat, même consigne), seules les garanties sans fiche sont refaites ;
    les fiches réussies, éventuellement relues, sont gardées. `progression(texte)` est appelée à
    chaque garantie terminée."""
    from .consignes import CONSIGNES

    llm = pour_compiler(llm)
    travaux = unites(clauses)
    refaire = a_refaire(existante, travaux)
    garder = [] if existante is None else [f for f in existante.fiches if f.id.split("#")[0] not in refaire]
    generales_a_faire = existante is None or not existante.exclusions_generales

    def tache(gid, cs):
        debut = time.perf_counter()
        fiches, avs, echec = compiler_garantie(gid, cs, llm)
        if progression:
            etat = "ÉCHEC, à refaire" if echec else f"{len(fiches)} fiche(s)"
            progression(f"  {gid:<8} {etat} en {time.perf_counter() - debut:.0f} s")
        return gid, fiches, avs, echec

    resultats = []
    with ThreadPoolExecutor(max_workers=max(1, paralleles)) as pool:
        futurs = [pool.submit(tache, gid, cs) for gid, cs in travaux if gid in refaire]
        if generales_a_faire:
            generales, avert_gen = compiler_exclusions_generales(clauses, llm)
            if progression:
                progression(f"  {'générales':<8} {len(generales)} exclusion(s)")
        else:
            generales, avert_gen = existante.exclusions_generales, []
        resultats = [f.result() for f in as_completed(futurs)]
    ordre = {gid: n for n, (gid, _) in enumerate(travaux)}
    fiches = sorted(garder + [f for _, fs, _, _ in resultats for f in fs],
                    key=lambda f: (ordre.get(f.id.split("#")[0], 999), f.id))
    anciens = [] if existante is None else [a for a in existante.avertissements
                                            if not any(a.startswith((f"Garantie {g} ", f"{g} ", f"{g}#")) for g in refaire)
                                            and not (generales_a_faire and a.startswith("Exclusions générales"))]
    version = CONSIGNES["couverture-compilation"][2]
    return ContratCompile(
        contrat_id=contrat_id,
        empreinte=f"{empreinte}:{version}",
        modele=llm.nom,
        consigne=version,
        compile_le=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        relu_par=existante.relu_par if existante else "",
        fiches=fiches,
        exclusions_generales=generales,
        avertissements=anciens + [a for _, _, avs, _ in resultats for a in avs] + avert_gen,
        echecs=sorted(gid for gid, _, _, echec in resultats if echec),
    )


def verifier_import(compile_: ContratCompile, clauses: list[Clause]) -> list[str]:
    """Après relecture humaine : chaque extrait doit toujours figurer dans sa clause.
    Un humain peut reformuler une question, pas inventer une citation."""
    index = {c.id: c for c in clauses}
    problemes = []
    for p in compile_.points():
        clause = index.get(p.clause_id)
        ok = clause is not None and extrait_present(p.extrait, clause.texte)
        p.valide = ok
        p.pages = clause.pages if ok else []
        if not ok:
            problemes.append(f"{p.id} : extrait introuvable dans l'art. {p.clause_id} (« {p.enonce} »).")
    return problemes


def resumer(c: ContratCompile) -> str:
    """Affichage d'un contrat compilé, pour la relecture."""
    lignes = [f"Contrat {c.contrat_id} : {len(c.fiches)} fiches, {len(c.exclusions_generales)} exclusions générales "
              f"(compilé le {c.compile_le} par {c.modele}, consigne {c.consigne}"
              + (f", relu par {c.relu_par})" if c.relu_par else ", pas encore relu)"), ""]
    marque = lambda p: "" if p.valide else "  [ÉCARTÉE]"  # noqa: E731
    for f in c.fiches:
        lignes.append(f"[{f.id}] {f.nom}  ({', '.join(f.evenements)})  art. {f.clause_id}")
        if f.objet:
            lignes.append(f"    {f.objet}")
        for p in f.conditions:
            lignes.append(f"    condition  {p.enonce} (art. {p.clause_id}){marque(p)}")
        for p in f.exclusions:
            lignes.append(f"    exclusion  {p.enonce} (art. {p.clause_id}){'' if p.a_demander else ' — présumée absente'}{marque(p)}")
        for p in f.limites:
            lignes.append(f"    limite     {p.enonce} (art. {p.clause_id}){marque(p)}")
        lignes.append("")
    if c.exclusions_generales:
        lignes.append("Exclusions générales :")
        for p in c.exclusions_generales:
            lignes.append(f"    {p.enonce} (art. {p.clause_id}){'' if p.a_demander else ' — présumée absente'}{marque(p)}")
    if c.avertissements:
        lignes += ["", "Avertissements :"] + [f"  - {a}" for a in c.avertissements]
    return "\n".join(lignes)
