"""Bilan : ce qu'un humain doit savoir, et seulement ça.

Comme le bilan du lundi de SortirIA (`agent/report.py`), il ne raconte pas tout :
il dit ce qui demande une intervention, puis donne les chiffres.

  1. À faire : contrats à vérifier, propositions de réparation en attente, dérive forte,
     erreurs du modèle ;
  2. Les contrats : statut de lecture, score du juge de qualité ;
  3. L'activité de la période : décisions, INCERTAIN, contestations de la relecture,
     citations rejetées, temps de réponse ;
  4. Ce qui manque : les questions à poser à l'assuré qui reviennent le plus. C'est la liste
     des informations à aller chercher ailleurs (souvent les conditions particulières) ;
  5. La dérive.

Le bilan est écrit en Markdown. Il peut être envoyé par mail si un serveur SMTP est configuré
(SMTP_HOTE, SMTP_PORT, SMTP_UTILISATEUR, SMTP_MOT_DE_PASSE, BILAN_EXPEDITEUR, BILAN_DESTINATAIRE).
"""

from __future__ import annotations

import json
import os
import smtplib
from collections import Counter
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path

from .base import Base
from .derive import calculer
from .journal import Journal
from .reparation import Propositions


def _pct(x: float | None) -> str:
    return "—" if x is None else f"{x:.0%}"


def construire_bilan(base: Base, donnees: str | Path, jours: int = 7, maintenant: datetime | None = None) -> tuple[str, dict]:
    """Renvoie (texte Markdown, résumé chiffré)."""
    maintenant = maintenant or datetime.now(timezone.utc)
    journal = Journal(base.chemin)
    lignes = journal.lignes(maintenant - timedelta(days=jours), maintenant + timedelta(seconds=1))
    erreurs = [r for r in lignes if r["erreur"]]
    ok = [r for r in lignes if not r["erreur"]]
    contrats = base.contrats()
    en_attente = [p for p in Propositions(donnees).toutes() if p["statut"] == "a_valider"]
    derive = calculer(journal, maintenant, jours=jours)

    a_faire = []
    for c in contrats:
        if c.statut != "OK":
            a_faire.append(f"Contrat **{c.id}** à vérifier : {' '.join(c.rapport.get('alertes', [])[:2])} → `couverture reparer --contrat {c.id}`")
    for p in en_attente:
        a_faire.append(f"Proposition **#{p['numero']}** ({p['contrat_id']}) en attente → `couverture propositions --accepter {p['numero']}` ou `--refuser {p['numero']}`")
    a_faire += [f"{a}" for a in derive.get("alertes", [])]
    if erreurs:
        motifs = Counter(r["erreur"][:80] for r in erreurs).most_common(2)
        a_faire.append(f"{len(erreurs)} analyse(s) en erreur côté modèle, surtout : " + " ; ".join(f"{m} ({n})" for m, n in motifs))

    decisions = Counter(r["decision"] for r in ok)
    n = len(ok)
    taux = lambda k: k / n if n else None  # noqa: E731
    resume = {
        "periode_jours": jours,
        "analyses": n,
        "erreurs": len(erreurs),
        "decisions": dict(decisions),
        "taux_incertain": taux(decisions.get("INCERTAIN", 0)),
        "analyses_contestees": sum((r["contestations"] or 0) > 0 for r in ok),
        "decisions_changees_par_relecture": sum(bool(r["decision_avant_relecture"]) for r in ok),
        "decisions_corrigees_par_controle": sum(r["decision_initiale"] != r["decision"] for r in ok),
        "citations_rejetees": sum((r["citations_rejetees"] or 0) + (r["conditions_ecartees"] or 0) for r in ok),
        "duree_mediane_ms": sorted(r["duree_ms"] or 0 for r in ok)[n // 2] if n else None,
        "a_faire": len(a_faire),
        "derive": derive.get("statut"),
    }
    questions = Counter(q for r in ok for q in json.loads(r["questions"] or "[]"))

    md = [f"# Bilan — {maintenant.astimezone().strftime('%d/%m/%Y')} ({jours} derniers jours)", ""]
    md += ["## À faire", ""] + ([f"- {a}" for a in a_faire] or ["Rien : aucune intervention nécessaire."]) + [""]

    md += ["## Contrats", "", "| Contrat | Assureur | Lecture | Qualité du typage | Alertes |", "|---|---|---|---|---|"]
    for c in contrats:
        q = c.rapport.get("qualite", {})
        qualite = _pct(q["score"]) + f" sur {q['echantillon']}" if "score" in q else ("non jugée" if not q else "erreur du juge")
        md.append(f"| {c.id} | {c.assureur or '—'} | {c.statut} | {qualite} | {len(c.rapport.get('alertes', []))} |")
    md.append("")

    md += ["## Activité", ""]
    if not n:
        md += ["Aucune analyse sur la période.", ""]
    else:
        md += [
            f"- **{n}** analyses, {len(erreurs)} en erreur.",
            "- Décisions : " + ", ".join(f"{k} {v} ({v / n:.0%})" for k, v in decisions.most_common()) + ".",
            f"- Réponses corrigées par le contrôle des citations : {resume['decisions_corrigees_par_controle']}.",
            f"- Analyses où la relecture a contesté une condition : {resume['analyses_contestees']}, "
            f"dont {resume['decisions_changees_par_relecture']} où la décision a changé.",
            f"- Citations ou conditions écartées faute de preuve : {resume['citations_rejetees']}.",
            f"- Temps de réponse médian : {resume['duree_mediane_ms']} ms.",
            "",
        ]

    md += ["## Ce qui manque", "", "Les questions à poser à l'assuré qui reviennent le plus. Ce sont les informations "
           "que le système devrait aller chercher ailleurs (conditions particulières, déclaration détaillée).", ""]
    md += [f"- {q} ({k} fois)" for q, k in questions.most_common(8)] or ["Aucune."]
    md.append("")

    md += ["## Dérive", "", f"{derive['periode']} : {derive['volumes']['recent']} analyses contre {derive['volumes']['reference']}."]
    if derive.get("variables"):
        md += ["", "| Variable | Famille | PSI | Niveau |", "|---|---|---|---|"]
        md += [f"| {k} | {v['famille']} | {v['psi']} | {v['niveau']} |" for k, v in derive["variables"].items()]
    else:
        md.append(f"Non calculée : {derive.get('statut')}.")
    md.append("")
    return "\n".join(md), resume


def envoyer(texte: str, sujet: str) -> str:
    """Envoie le bilan par mail si SMTP est configuré. Renvoie ce qui s'est passé, en une phrase."""
    hote, destinataire = os.environ.get("SMTP_HOTE"), os.environ.get("BILAN_DESTINATAIRE")
    if not hote or not destinataire:
        return "Mail non envoyé : SMTP_HOTE et BILAN_DESTINATAIRE ne sont pas configurés."
    msg = EmailMessage()
    msg["Subject"] = sujet
    msg["From"] = os.environ.get("BILAN_EXPEDITEUR") or os.environ.get("SMTP_UTILISATEUR") or destinataire
    msg["To"] = destinataire
    msg.set_content(texte)
    with smtplib.SMTP(hote, int(os.environ.get("SMTP_PORT", "587")), timeout=30) as smtp:
        smtp.starttls()
        if os.environ.get("SMTP_UTILISATEUR"):
            smtp.login(os.environ["SMTP_UTILISATEUR"], os.environ.get("SMTP_MOT_DE_PASSE", ""))
        smtp.send_message(msg)
    return f"Bilan envoyé à {destinataire}."
