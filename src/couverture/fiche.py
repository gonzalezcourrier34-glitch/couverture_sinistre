"""La fiche d'analyse d'un sinistre, en PDF : une page à verser au dossier.

**Provenance** : nouveau module (21/11/2026, DEMARCHE 7.130). La fiche reprend ce que l'écran montre : la
déclaration, la décision et son motif, les faits retenus, ce qu'il faut demander au client ou ce qui reste sous
réserve, les clauses citées (article, pages, phrase exacte) et les limites. Elle ne recalcule rien : elle met en
page une réponse de l'API (`api/schemas.py`, `Decision`).

Couleurs de l'interface (`frontend/src/styles.scss`) ; ni logo, ni nom de marque. Police Helvetica, fournie par
tout lecteur de PDF : les caractères qu'elle n'a pas (la flèche des questions classées) sont remplacés.
"""

from __future__ import annotations

from datetime import datetime
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (HRFlowable, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

PRIMAIRE, NUIT = colors.HexColor("#2957c8"), colors.HexColor("#041d58")
DOUX, PLUME, FOND = colors.HexColor("#454f5f"), colors.HexColor("#67768e"), colors.HexColor("#f8f9fc")
BORD = colors.HexColor("#eaeef6")
# Fond, bordure et texte de la décision : les mêmes tons que les pastilles de l'écran.
TONS = {"COUVERT": ("#e0f5f3", "#00a88c", "#006353"), "NON_COUVERT": ("#fff0f0", "#ed5e63", "#a32c30"),
        "INCERTAIN": ("#fefae8", "#f5ce22", "#7b6711")}
LIBELLES = {"COUVERT": "Couvert", "NON_COUVERT": "Non couvert", "INCERTAIN": "À préciser"}
REMPLACEMENTS = {"→": ":", "›": ">", "≥": ">=", "≤": "<=", "\u202f": "\u00a0"}
MENTION = ("Démonstration. Cette fiche est produite automatiquement à partir des conditions générales ; elle ne "
           "remplace pas l'examen du dossier par un gestionnaire.")


def _style(nom: str, **kw) -> ParagraphStyle:
    base = {"fontName": "Helvetica", "fontSize": 10, "leading": 14, "textColor": colors.HexColor("#1a1d23")}
    return ParagraphStyle(nom, **(base | kw))


TEXTE = _style("texte")
PETIT = _style("petit", fontSize=8.5, leading=11.5, textColor=PLUME)
TITRE = _style("titre", fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=NUIT)
RUBRIQUE = _style("rubrique", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=PRIMAIRE, spaceBefore=10,
                  spaceAfter=4)
CITE = _style("cite", fontName="Helvetica-Oblique", textColor=DOUX)
DROITE = _style("droite", fontSize=8.5, leading=11.5, textColor=PLUME, alignment=TA_RIGHT)


def propre(texte: object) -> str:
    """Le texte prêt pour un paragraphe : caractères hors de la police remplacés, balises échappées."""
    t = str(texte if texte is not None else "")
    for a, b in REMPLACEMENTS.items():
        t = t.replace(a, b)
    return escape(t.encode("cp1252", "replace").decode("cp1252"))


def lisible(identifiant: str) -> str:
    return str(identifiant).replace("_", " ")


def _puces(lignes: list[str], style: ParagraphStyle = TEXTE) -> list:
    return [Paragraph(f"• {propre(x)}", style) for x in lignes]


def _citations_par_article(citations: list[dict]) -> list[dict]:
    """Un article, une entrée, ses extraits : comme à l'écran (`citationsParArticle`)."""
    articles: dict[str, dict] = {}
    for c in citations:
        a = articles.setdefault(c["clause_id"], {"clause_id": c["clause_id"], "role": c.get("role", ""),
                                                 "pages": list(c.get("pages") or []), "extraits": []})
        if c.get("extrait") and c["extrait"] not in a["extraits"]:
            a["extraits"].append(c["extrait"])
    return list(articles.values())


def surligne(texte: str, extraits: list[str]) -> str:
    """Le texte d'un article, prêt pour un paragraphe, les extraits cités surlignés (comme `surligner` à l'écran).
    Un extrait qui n'est pas retrouvé tel quel n'est pas surligné : l'article s'affiche quand même en entier."""
    plages = sorted((d, d + len(x)) for x in extraits if x for d in [texte.find(x)] if d != -1)
    morceaux, position = [], 0
    for debut, fin in plages:
        if fin <= position:
            continue
        morceaux.append(propre(texte[position:debut]))
        morceaux.append(f'<span backColor="#fdf3bf">{propre(texte[max(debut, position):fin])}</span>')
        position = fin
    morceaux.append(propre(texte[position:]))
    return "".join(morceaux).replace("\n", "<br/>")


def fiche_pdf(sinistre: str, reponse: dict, contrat: dict | None = None, date: datetime | None = None,
              clauses: dict[str, dict] | None = None) -> bytes:
    """La fiche en PDF. `reponse` : une réponse de l'API (`Decision`) ; `contrat` : assureur, produit, version ;
    `clauses` : {identifiant : {texte, chemin, pages}} des articles cités, pour les joindre en entier."""
    date = date or datetime.now()
    contrat = contrat or {}
    decision = reponse.get("decision", "INCERTAIN")
    fond, bord, encre = (colors.HexColor(c) for c in TONS.get(decision, TONS["INCERTAIN"]))
    largeur = A4[0] - 36 * mm

    nom_contrat = " · ".join(str(x) for x in (contrat.get("assureur"), contrat.get("produit"), contrat.get("version")) if x)
    entete = Table([[Paragraph("Fiche d'analyse de sinistre", TITRE),
                     Paragraph(f"{propre(nom_contrat or reponse.get('contrat_id') or '')}<br/>"
                               f"Établie le {date:%d/%m/%Y à %H:%M}", DROITE)]], colWidths=[largeur * 0.55, largeur * 0.45])
    entete.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "BOTTOM"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    blocs: list = [entete, HRFlowable(width="100%", thickness=1.5, color=PRIMAIRE, spaceBefore=4, spaceAfter=8)]

    blocs.append(Paragraph("LA DÉCLARATION DU CLIENT", RUBRIQUE))
    declaration = Table([[Paragraph(propre(sinistre), CITE)]], colWidths=[largeur])
    declaration.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), FOND), ("LINEBEFORE", (0, 0), (0, -1), 2, PRIMAIRE),
                                     ("LEFTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 6),
                                     ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    blocs.append(declaration)

    blocs.append(Paragraph("LA DÉCISION", RUBRIQUE))
    confiance = reponse.get("confiance")
    pastille = Table([[Paragraph(f"<b>{LIBELLES.get(decision, decision)}</b>",
                                 _style("verdict", fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=encre)),
                       Paragraph(f"confiance {round(float(confiance) * 100)} %" if confiance is not None else "",
                                 _style("confiance", fontSize=9, textColor=encre, alignment=TA_RIGHT))]],
                     colWidths=[largeur * 0.6, largeur * 0.4])
    pastille.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), fond), ("BOX", (0, 0), (-1, -1), 1.2, bord),
                                  ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 10),
                                  ("RIGHTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 6),
                                  ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    blocs += [pastille, Spacer(1, 6), Paragraph(propre(reponse.get("justification", "")), TEXTE)]

    faits = reponse.get("faits") or {}
    if faits:
        ordre = ["evenement", "bien", "lieu"]
        cles = sorted(faits, key=lambda v: (ordre.index(v) if v in ordre else 99, v))
        ligne = " &nbsp;·&nbsp; ".join(
            f"<font color='#67768e'>{propre(lisible(v))}</font> "
            f"{propre(', '.join(lisible(x) for x in (faits[v] if isinstance(faits[v], list) else [faits[v]])))}"
            for v in cles)
        blocs += [Paragraph("FAITS RETENUS", RUBRIQUE), Paragraph(ligne, TEXTE)]

    points = reponse.get("a_preciser") or []
    questions = [p["question"] for p in points if p.get("nature") == "question"]
    reserves = [p["question"] for p in points if p.get("nature") == "reserve"]
    # Les questions en phrase (le lien de causalité) n'ont pas de point à cliquer : elles figurent ici aussi.
    for q in reponse.get("questions") or []:
        if decision != "COUVERT" and not any(q.startswith(x) for x in questions):
            questions.append(q)
    if questions:
        blocs += [Paragraph("À DEMANDER AU CLIENT", RUBRIQUE), *_puces(questions)]
    if reserves:
        blocs += [Paragraph("SOUS RÉSERVE · CE QUE L'ASSUREUR POURRA VÉRIFIER", RUBRIQUE), *_puces(reserves)]

    articles = _citations_par_article(reponse.get("citations") or [])
    if articles:
        blocs.append(Paragraph("CLAUSES CITÉES", RUBRIQUE))
        for a in articles:
            pages = f" · p. {', '.join(str(p) for p in a['pages'])}" if a["pages"] else ""
            tete = Paragraph(f"<font color='#2957c8'><b>Art. {propre(a['clause_id'])}</b></font> "
                             f"<font color='#67768e' size='8'>{propre(a['role']).upper()}{pages}</font>", TEXTE)
            corps = [[tete]] + [[Paragraph(f"«\u00a0{propre(x)}\u00a0»", CITE)] for x in a["extraits"]]
            t = Table(corps, colWidths=[largeur])
            t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), FOND),
                                   ("LINEBEFORE", (0, 0), (0, -1), 2.5, colors.HexColor("#ed5e63") if a["role"] == "exclusion" else PRIMAIRE),
                                   ("LEFTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 3),
                                   ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
            blocs += [KeepTogether(t), Spacer(1, 4)]

    limites = reponse.get("limites") or []
    if limites:
        blocs += [Paragraph("LIMITES", RUBRIQUE),
                  *_puces([f"Art. {l['clause_id']} : {l.get('extrait', '')}" for l in limites])]

    avertissements = reponse.get("avertissements") or []
    if avertissements:
        blocs += [Paragraph("CONTRÔLES DE LA LECTURE", RUBRIQUE), *_puces(avertissements[:8], PETIT)]

    # Les articles cités, en entier, à la suite de la fiche : le lecteur n'a pas à ouvrir le contrat.
    entiers = [(a, (clauses or {}).get(a["clause_id"])) for a in articles]
    entiers = [(a, c) for a, c in entiers if c and c.get("texte")]
    if entiers:
        blocs += [PageBreak(), Paragraph("Les articles cités, en entier", TITRE),
                  HRFlowable(width="100%", thickness=1.5, color=PRIMAIRE, spaceBefore=4, spaceAfter=4),
                  Paragraph("Texte des conditions générales. Surlignés : les passages sur lesquels la décision s'appuie.",
                            PETIT)]
        for a, c in entiers:
            pages = c.get("pages") or a["pages"]
            chemin = " > ".join(str(x) for x in c.get("chemin") or [])
            blocs += [Spacer(1, 10),
                      Paragraph(f"<font color='#2957c8'><b>Art. {propre(a['clause_id'])}</b></font>",
                                _style("article", fontName="Helvetica-Bold", fontSize=12, leading=15)),
                      Paragraph(propre(chemin) + (f" · p. {', '.join(str(p) for p in pages)}" if pages else ""), PETIT),
                      Spacer(1, 4), Paragraph(surligne(c["texte"], a["extraits"]), TEXTE)]

    def pied(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(BORD)
        canvas.line(18 * mm, 16 * mm, A4[0] - 18 * mm, 16 * mm)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(PLUME)
        canvas.drawString(18 * mm, 11.5 * mm, propre_canvas(MENTION))
        canvas.drawRightString(A4[0] - 18 * mm, 7.5 * mm, f"{reponse.get('mode', '')}   ·   page {doc.page}")
        canvas.restoreState()

    tampon = BytesIO()
    doc = SimpleDocTemplate(tampon, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm,
                            bottomMargin=22 * mm, title="Fiche d'analyse de sinistre", author="Couverture des sinistres")
    doc.build(blocs, onFirstPage=pied, onLaterPages=pied)
    return tampon.getvalue()


def propre_canvas(texte: str) -> str:
    """Comme `propre`, sans l'échappement XML : pour le texte dessiné directement (le pied de page)."""
    for a, b in REMPLACEMENTS.items():
        texte = texte.replace(a, b)
    return texte.encode("cp1252", "replace").decode("cp1252")


def nom_fichier(reponse: dict, date: datetime | None = None) -> str:
    date = date or datetime.now()
    return f"fiche-sinistre-{reponse.get('contrat_id') or 'contrat'}-{date:%Y%m%d-%H%M}.pdf"
