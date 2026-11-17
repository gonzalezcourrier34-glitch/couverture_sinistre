"""Agent de réparation des contrats mal lus. Il propose, un humain décide.

Même principe que l'agent de SortirIA (`agent/diagnosis.py`, `agent/proposals.py`) :
  1. **classer** ce qui ne va pas, d'après les alertes des contrôles d'ingestion ;
  2. **proposer** une réparation : Mistral lit les lignes qui ressemblent à des titres
     et propose un profil d'assureur (intertitres et leur type, lignes de bruit à ignorer,
     format du lexique) ;
  3. **vérifier** la proposition par du code : chaque ligne citée doit exister dans le
     contrat, chaque motif doit reconnaître son exemple sans effacer de clause, et le
     contrat redécoupé avec le profil doit avoir moins d'alertes qu'avant ;
  4. **enregistrer** la proposition, avec l'avant/après, sans l'appliquer. Elle n'est
     appliquée que si un humain l'accepte : `couverture propositions --accepter N`.

Le système ne modifie jamais seul sa façon de lire un contrat : un profil
« trouvé » pourrait faire passer une exclusion pour une garantie.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from .chargement import Ligne
from .controles import controler
from .juges import extraire_json
from .llm import LLM
from .profils import TYPES_PERMIS, ProfilInvalide, ecrire_profil, valider_profil
from .segmentation import segmenter_lignes
from .texte import normaliser

# Familles de problèmes : de l'alerte des contrôles à ce qu'il faut faire.
FAMILLES = [
    ("decoupage_echoue", r"Peu de clauses", "Les titres ne sont pas reconnus : il faut décrire ceux de cet assureur."),
    ("titres_non_reconnus", r"sans type", "Des intertitres propres à l'assureur ne sont pas compris : leur donner un type."),
    ("sans_exclusion", r"Aucune exclusion", "Les exclusions portent un titre inhabituel : le déclarer comme exclusion."),
    ("sans_garantie", r"Aucune garantie", "Les garanties portent un titre inhabituel : le déclarer comme garantie."),
    ("sans_lexique", r"Aucune définition", "Le lexique n'est pas reconnu : déclarer son titre et son format."),
    ("sans_exclusions_generales", r"exclusions générales", "Repérer le titre des exclusions communes à toutes les garanties."),
    ("typage_douteux", r"Typage douteux", "Le juge de qualité conteste des types : déclarer le bon type pour ces intertitres."),
    ("renvois_casses", r"renvois", "Numérotation mal lue, ou en-têtes de page mêlés au texte : lignes à ignorer."),
]


def diagnostiquer(rapport: dict) -> list[dict]:
    diagnostic = []
    for alerte in rapport.get("alertes", []):
        for famille, motif, conseil in FAMILLES:
            if re.search(motif, alerte, re.IGNORECASE):
                diagnostic.append({"famille": famille, "alerte": alerte, "conseil": conseil})
                break
        else:
            diagnostic.append({"famille": "autre", "alerte": alerte, "conseil": "À examiner à la main."})
    return diagnostic


def candidats_titres(lignes: list[Ligne], maximum: int = 80) -> list[str]:
    """Lignes qui ressemblent à des titres : courtes, sans ponctuation finale, avec une majuscule.
    Les plus fréquentes d'abord (un intertitre comme « Ce que nous ne couvrons pas » revient
    dans chaque section)."""
    compte: Counter[str] = Counter()
    premiere: dict[str, str] = {}
    for l in lignes:
        t = l.texte.strip()
        if not (3 <= len(t) <= 70) or t.endswith((".", ",", ";")) or not t[:1].isalpha() or not t[:1].isupper():
            continue
        cle = normaliser(t)
        compte[cle] += 1
        premiere.setdefault(cle, t)
    return [premiere[c] for c, _ in compte.most_common(maximum)]


SYSTEME_REPARATION = """Tu aides à configurer la lecture automatique des conditions générales d'un assureur. Le découpage automatique de ce contrat a échoué en partie. On te donne le diagnostic, le profil actuel, et des lignes du contrat qui ressemblent à des titres.

Propose un profil qui corrige le découpage :
- "intertitres" : les lignes qui sont des intertitres porteurs de sens et leur type : garantie (ce qui est couvert), exclusion (ce qui ne l'est pas), condition (obligations, mesures de prévention, conditions d'application), limite (plafonds, franchises, indemnisation), definition (lexique, glossaire). Recopie chaque ligne EXACTEMENT telle qu'elle apparaît dans la liste. N'en invente aucune.
- "lignes_ignorees" : seulement des lignes de bruit répétées (en-têtes, pieds de page, références de document), sous forme d'expression régulière Python, avec une ligne d'exemple recopiée exactement. Jamais une ligne qui contient du contenu contractuel.
- "lexique" : "deux_points" si les définitions sont de la forme « Terme : définition », "terme_seul" si le terme est seul sur sa ligne avec la définition dessous, sinon "auto".

Réponds uniquement par un objet JSON :
{
  "intertitres": [{"ligne": "…", "type": "exclusion", "raison": "…"}],
  "lignes_ignorees": [{"motif": "…", "exemple": "…", "raison": "…"}],
  "lexique": "auto",
  "explication": "2 ou 3 phrases"
}"""


def _resume(rapport: dict) -> dict:
    return {k: rapport.get(k) for k in ("statut", "nb_clauses", "par_type", "alertes")}


def _corrections_obtenues(clauses: list, corrections: list[dict]) -> int:
    """Nombre de types contestés par le juge de qualité que ce découpage corrige (même titre, type proposé)."""
    voulus = {(normaliser(c["titre"]), c["type_propose"]) for c in corrections}
    return len({(normaliser(c.titre), c.type.value) for c in clauses} & voulus)


def verifier(proposition: dict, profil_actuel: dict, nom: str, lignes: list[Ligne],
             corrections: list[dict] | None = None) -> dict:
    """Construit le profil proposé et le met à l'épreuve. Ne lève jamais : renvoie
    {"profil", "ecarts", "avant", "apres", "ameliore"}."""
    presentes = {normaliser(l.texte.strip()).rstrip(" :.") for l in lignes}
    ecarts: list[str] = []

    intertitres = dict(profil_actuel.get("intertitres", {}))
    for it in proposition.get("intertitres") or []:
        ligne, type_ = str(it.get("ligne", "")), it.get("type")
        cle = normaliser(ligne).rstrip(" :.").strip()
        if cle not in presentes:
            ecarts.append(f"Intertitre écarté, absent du contrat : « {ligne} »")
        elif type_ not in TYPES_PERMIS:
            ecarts.append(f"Intertitre écarté, type inconnu ({type_}) : « {ligne} »")
        else:
            intertitres[cle] = type_

    ignorees = list(profil_actuel.get("lignes_ignorees", []))
    for li in proposition.get("lignes_ignorees") or []:
        motif, exemple = str(li.get("motif", "")), str(li.get("exemple", ""))
        try:
            rx = re.compile(motif)
        except re.error:
            ecarts.append(f"Motif écarté, expression invalide : {motif}")
            continue
        touchees = [l.texte for l in lignes if rx.search(l.texte)]
        if normaliser(exemple.strip()).rstrip(" :.") not in presentes or not rx.search(exemple):
            ecarts.append(f"Motif écarté, son exemple est absent du contrat ou non reconnu : {motif}")
        elif len(touchees) > max(5, 0.08 * len(lignes)):
            ecarts.append(f"Motif écarté, il effacerait trop de lignes ({len(touchees)}) : {motif}")
        elif any(len(t) > 120 or re.search(r"garanti|exclu|nous (prenons|couvrons)", normaliser(t)) for t in touchees):
            ecarts.append(f"Motif écarté, il effacerait du contenu contractuel : {motif}")
        else:
            ignorees.append(motif)

    lexique = proposition.get("lexique") or profil_actuel.get("lexique", "auto")
    try:
        profil = valider_profil({"nom": nom, "intertitres": intertitres, "lignes_ignorees": ignorees, "lexique": lexique})
    except ProfilInvalide as e:
        ecarts.append(f"Profil invalide : {e}")
        profil = valider_profil({"nom": nom, **{k: v for k, v in profil_actuel.items() if k != "nom"}})

    clauses_avant = segmenter_lignes(lignes, profil_actuel or None)
    clauses_apres = segmenter_lignes(lignes, profil)
    avant, apres = controler(clauses_avant), controler(clauses_apres)
    corrections = corrections or []
    corrige_avant = _corrections_obtenues(clauses_avant, corrections)
    corrige_apres = _corrections_obtenues(clauses_apres, corrections)
    familles_avant = {d["famille"] for d in diagnostiquer(avant)}
    nouvelles = [d["alerte"] for d in diagnostiquer(apres) if d["famille"] not in familles_avant]
    sans_type = lambda r: r["par_type"].get("autre", 0) / max(r["nb_clauses"], 1)  # noqa: E731
    ameliore = not nouvelles and (
        len(apres["alertes"]) < len(avant["alertes"])
        or sans_type(apres) < sans_type(avant) - 0.05
        or corrige_apres > corrige_avant  # types contestés par le juge de qualité, désormais corrigés
    )
    if nouvelles:
        ecarts.append("Nouvelles alertes après réparation : " + " ; ".join(nouvelles))
    if corrections:
        apres["corrections_qualite"] = f"{corrige_apres}/{len(corrections)} (avant : {corrige_avant})"
    return {"profil": profil, "ecarts": ecarts, "avant": _resume(avant), "apres": _resume(apres) | (
        {"corrections_qualite": apres["corrections_qualite"]} if corrections else {}), "ameliore": ameliore}


class Propositions:
    """Les propositions de réparation, une par fichier JSON dans `<donnees>/propositions/`."""

    def __init__(self, donnees: str | Path):
        self.donnees = Path(donnees)
        self.dossier = self.donnees / "propositions"

    def toutes(self) -> list[dict]:
        if not self.dossier.exists():
            return []
        return [json.loads(f.read_text(encoding="utf-8")) for f in sorted(self.dossier.glob("*.json"))]

    def ajouter(self, proposition: dict) -> dict:
        self.dossier.mkdir(parents=True, exist_ok=True)
        numero = max((p["numero"] for p in self.toutes()), default=0) + 1
        proposition = {"numero": numero, **proposition}
        self._ecrire(proposition)
        return proposition

    def _ecrire(self, p: dict) -> None:
        (self.dossier / f"{p['numero']:03d}-{p['contrat_id']}.json").write_text(
            json.dumps(p, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def lire(self, numero: int) -> dict:
        for p in self.toutes():
            if p["numero"] == numero:
                return p
        raise KeyError(f"Proposition inconnue : {numero}")

    def accepter(self, numero: int) -> dict:
        """Écrit le profil et le rattache au contrat dans le catalogue. Il reste à relancer l'ingestion."""
        p = self.lire(numero)
        if p["statut"] != "a_valider":
            raise ValueError(f"La proposition {numero} n'est pas à valider (statut : {p['statut']}).")
        ecrire_profil(self.donnees / "profils", p["profil"])
        chemin = self.donnees / "contrats" / "catalogue.json"
        catalogue = json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists() else {}
        entree = catalogue.setdefault(p["fichier"], {"id": p["contrat_id"]})
        entree["profil"] = p["profil"]["nom"]
        chemin.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        p["statut"] = "acceptee"
        self._ecrire(p)
        return p

    def refuser(self, numero: int) -> dict:
        p = self.lire(numero)
        p["statut"] = "refusee"
        self._ecrire(p)
        return p


def proposer_reparation(contrat_id: str, fichier: str, lignes: list[Ligne], rapport: dict,
                        profil_actuel: dict | None, nom_profil: str, llm: LLM,
                        propositions: Propositions) -> dict:
    """Diagnostic, proposition du modèle, vérification ; enregistre la proposition sans l'appliquer."""
    profil_actuel = profil_actuel or {}
    diagnostic = diagnostiquer(rapport)
    candidats = candidats_titres(lignes)
    corrections = rapport.get("qualite", {}).get("erreurs", [])
    message = (
        "## Diagnostic\n" + json.dumps(diagnostic, ensure_ascii=False, indent=1)
        + ("\n\n## Types contestés par le juge de qualité (titre, type actuel → type proposé)\n"
           + "\n".join(f"- « {c['titre']} » : {c['type']} → {c['type_propose']} ({c['raison']})" for c in corrections)
           if corrections else "")
        + "\n\n## Profil actuel\n" + json.dumps(profil_actuel or {"intertitres": {}}, ensure_ascii=False)
        + "\n\n## Lignes qui ressemblent à des titres (les plus fréquentes d'abord)\n"
        + "\n".join(f"- {c}" for c in candidats)
    )
    try:
        reponse = extraire_json(llm.completer(SYSTEME_REPARATION, message))
    except ValueError as e:
        reponse = {"explication": f"Réponse du modèle illisible : {e}"}
    verification = verifier(reponse, profil_actuel, nom_profil, lignes, corrections)
    return propositions.ajouter({
        "date": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "contrat_id": contrat_id,
        "fichier": fichier,
        "modele": llm.nom,
        "diagnostic": diagnostic,
        "explication": reponse.get("explication", ""),
        "reponse_modele": reponse,
        "profil": verification["profil"],
        "verification": {k: verification[k] for k in ("avant", "apres", "ecarts", "ameliore")},
        "statut": "a_valider" if verification["ameliore"] else "refusee_par_la_verification",
    })


def decrire(p: dict) -> str:
    """Une proposition en quelques lignes, pour la ligne de commande."""
    v = p["verification"]
    lignes = [
        f"#{p['numero']}  {p['contrat_id']}  [{p['statut']}]  profil « {p['profil']['nom']} »  ({p['date']})",
        f"   {p.get('explication', '')}",
        f"   Avant : {v['avant']['nb_clauses']} clauses, {len(v['avant']['alertes'])} alerte(s), types {v['avant']['par_type']}",
        f"   Après : {v['apres']['nb_clauses']} clauses, {len(v['apres']['alertes'])} alerte(s), types {v['apres']['par_type']}",
    ]
    for phrase, type_ in p["profil"]["intertitres"].items():
        lignes.append(f"   + intertitre « {phrase} » → {type_}")
    for motif in p["profil"]["lignes_ignorees"]:
        lignes.append(f"   + lignes ignorées : {motif}")
    lignes += [f"   ! {e}" for e in v["ecarts"]]
    return "\n".join(lignes)
