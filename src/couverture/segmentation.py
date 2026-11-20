"""Étape 1 — Découpage des conditions générales en clauses typées.

Les assureurs ne rédigent pas tous de la même façon. Le découpage reconnaît :
  - les articles et sections numérotés : « Article 4 — Vol », « 4.3 Vélos », « 3.5 - Vol et vandalisme » ;
  - les intertitres sans numéro qui portent le sens juridique : « Ce que nous garantissons »,
    « Ce que nous ne garantissons pas », « Exclusions », « Lexique »… ;
  - les titres en capitales : « VOL ET VANDALISME ».
Chaque clause garde son chemin de titres, ses pages et ses renvois vers d'autres clauses.
Les lexiques sont éclatés en une clause par terme défini, et les clauses trop longues
sont coupées pour que les citations restent précises.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .chargement import Ligne
from .models import Clause, TypeClause
from .texte import normaliser

# « ART 2-7 Bris de glaces » (assureur D) : « ART » sans point, en capitales, et des numéros à tirets (7.87).
ARTICLE_RE = re.compile(r"^(?:article|art\.|ART)\s+(\d{1,2}(?:[.\-]\d{1,2}){0,3})(?![\d.\-]?\d)\s*[—–\-:.)]?\s*(.*)$",
                        re.IGNORECASE)
NUMERO_RE = re.compile(r"^(\d{1,2}(?:\.\d{1,2}){0,3})\.?\s*[—–\-)]?\s+(\S.{1,110})$")
CONTENEUR_RE = re.compile(r"^(chapitre|titre|partie)\s+([IVXLC]+|\d+)\b\s*[—–\-:.]?\s*(.*)$", re.IGNORECASE)
UNITE_RE = re.compile(r"^(%|€|euros?\b|ans?\b|jours?\b|mois\b|heures?\b|h\b|m2|m²|kg|km|fois\b)", re.IGNORECASE)
TERME_RE = re.compile(r"^([A-ZÉÈÀÂÊÎÔÛÇ«][^:]{1,50}?)\s*:\s*(\S.*)$")
RENVOI_RE = re.compile(r"\b(?:articles?|art\.|paragraphes?|points?|§)\s*((?:\d+(?:\.\d+)*)(?:\s*(?:,|et|à|ou)\s*\d+(?:\.\d+)*)*)", re.IGNORECASE)

INTERTITRES = [
    "ce que nous garantissons", "ce qui est garanti", "ce qui est couvert", "ce que nous couvrons",
    "ce que nous ne garantissons pas", "ce qui n'est pas garanti", "ce qui n'est pas couvert",
    "ce que nous ne couvrons pas", "ce qui est exclu", "ce que nous excluons", "nous ne garantissons pas",
    "les exclusions", "exclusions", "exclusions generales", "exclusions communes",
    "definitions", "lexique", "les definitions",
    "conditions de garantie", "conditions d'application", "conditions de mise en jeu", "conditions d'indemnisation",
    "mesures de prevention", "les mesures de prevention", "vos obligations", "obligations",
    "plafond", "plafonds", "franchise", "franchises", "montant de la garantie", "limites de garantie",
    "les biens assures", "biens assures", "les evenements garantis", "evenements garantis",
]

TAILLE_MAX = 2500  # au-delà, la clause est coupée (souvent une longue liste d'exclusions)


def _intertitre(texte: str, extra: dict[str, str] | None = None) -> str | None:
    """Intertitre reconnu (liste générale, plus ceux du profil d'assureur)."""
    t = normaliser(texte).rstrip(" :.").strip()
    for kw in list(INTERTITRES) + list(extra or {}):
        if t == kw or (t.startswith(kw) and len(t) <= 50 and not texte.rstrip().endswith((".", ";", ","))):
            return texte.strip().rstrip(" :")
    return None


def _en_capitales(texte: str) -> bool:
    lettres = [c for c in texte if c.isalpha()]
    mots = texte.split()
    return (
        len(lettres) >= 6
        and all(c.isupper() for c in lettres)
        and 2 <= len(mots) <= 10
        and len(texte) <= 70
        and len(lettres) >= 0.6 * len(texte.replace(" ", ""))
    )


def _terme_en_capitales(texte: str) -> bool:
    """Un terme de lexique en capitales, même d'un seul mot (« FRANCHISE », « CODE »)."""
    lettres = [c for c in texte if c.isalpha()]
    return len(lettres) >= 3 and all(c.isupper() for c in lettres) and len(texte) <= 70


def _titre_numerote(texte: str) -> tuple[str, str] | None:
    if m := ARTICLE_RE.match(texte):
        if texte.startswith("ART ") or re.match(r"(?i)(art\.|article\b)", texte):  # pas « Art 3 de la loi »
            return m.group(1).replace("-", "."), _lettrine(m.group(2).strip())
        return None
    m = NUMERO_RE.match(texte)
    if not m:
        return None
    num, titre = m.group(1), m.group(2).strip()
    if UNITE_RE.match(titre) or titre.endswith((",", ";")) or len(titre) > 90:
        return None
    if "." not in num:
        # Un numéro seul (« 3 Vol ») est un titre seulement s'il ressemble à un titre,
        # pas à un élément de liste (« 1. Les dommages causés intentionnellement ; »).
        if not titre[:1].isupper() or len(titre) > 70 or titre.endswith(".") or int(num) > 40:
            return None
    elif not titre[:1].isalpha() and titre[:1] not in "«\"":
        return None
    return num, titre


def _lettrine(titre: str) -> str:
    """« C atastrophes naturelles » → « Catastrophes naturelles » : la lettrine d'un titre, détachée par le PDF.
    Pas pour « A » ni « À », qui sont des mots (« A ttentats » reste tel quel)."""
    return re.sub(r"^([B-ZÉÈÊ]) ([a-zéèêàçôû]{2,})", r"\1\2", titre)


LOI_RE = re.compile(r"\b(loi|code|ar|a\.r|arrete|reglement|rgpd|directive|decret|convention)\b", re.IGNORECASE)


def extraire_renvois(texte: str) -> list[str]:
    """Renvois internes au contrat. « Art. 58 de la loi du 4 avril 2014 » n'en est pas un."""
    refs: list[str] = []
    for m in RENVOI_RE.finditer(texte):
        suite = normaliser(texte[m.end(): m.end() + 25])
        if LOI_RE.search(suite):
            continue
        # Un numéro de clause a des segments courts (« 4.2 ») ; « 1302 » ou « 3.101 » viennent d'un code.
        refs.extend(r for r in re.findall(r"\d+(?:\.\d+)*", m.group(1)) if all(len(x) <= 2 for x in r.split(".")))
    return list(dict.fromkeys(refs))


def resoudre(ref: str, ids: list[str]) -> list[str]:
    if ref in ids:
        return [ref]
    enfants = [i for i in ids if i.startswith(ref + ".") or i.startswith(ref + "-") or i.startswith(ref + "/")]
    if enfants:
        return enfants[:4]
    # Un sous-point énuméré dans le texte d'une clause (« 3.1.7.2.9 les pertes… » dans la clause 3.1.7.2) n'a
    # pas de clause à lui : le renvoi mène à la clause qui le contient (au plus deux niveaux au-dessus).
    parties = ref.split(".")
    for n in (1, 2):
        if len(parties) - n >= 2 and (parent := ".".join(parties[:-n])) in ids:
            return [parent]
    return []


def type_du_profil(titre: str, intertitres: dict[str, str]) -> TypeClause | None:
    # Le titre d'une section numérotée commence par son numéro (« 3.1.6.1 Etendue de la garantie ») :
    # le profil parle du titre seul.
    t = re.sub(r"^[\d.\s'’-]+", "", normaliser(titre)).rstrip(" :.").strip()
    for phrase, type_ in intertitres.items():
        if t == phrase or (t.startswith(phrase) and len(t) <= len(phrase) + 20):
            return TypeClause(type_)
    return None


def classer(chemin: list[str], texte: str, profil: dict | None = None) -> TypeClause:
    """Type d'une clause : le profil d'assureur s'il connaît son titre, puis son propre titre,
    puis sa formulation, puis les titres de ses parents."""
    if profil and chemin and (t := type_du_profil(chemin[-1], profil.get("intertitres", {}))):
        return t

    def par_titre(titre: str) -> TypeClause | None:
        t = normaliser(titre)
        if re.search(r"exclu|ne garantissons pas|ne couvrons pas|n'est pas (garanti|couvert)|ne sont pas (garanti|couvert)", t):
            return TypeClause.EXCLUSION
        if re.search(r"definition|lexique|glossaire", t):
            return TypeClause.DEFINITION
        if re.search(r"franchise|plafond|vetuste|indemnisation|montant de la garantie|limite", t):
            return TypeClause.LIMITE
        if re.search(r"en cas de sinistre|declaration|plainte|justificatif|prevention|obligation|condition", t):
            return TypeClause.CONDITION
        if re.search(r"ce que nous garantissons|ce qui est (garanti|couvert)|ce que nous couvrons", t):
            return TypeClause.GARANTIE
        return None

    if chemin and (t := par_titre(chemin[-1])):
        return t

    corps = normaliser(texte)
    if re.search(r"ne sont (pas|jamais) (garanti|couvert)|n'est pas (garanti|couvert)|ne garantissons pas|ne couvrons pas|sont exclu|est exclu", corps):
        return TypeClause.EXCLUSION
    # « Nous vous assurons pour les dommages causés… » : la formule des garanties de responsabilité civile
    # d'Assureur A (section 5), typées « autre » jusqu'ici ; la vérification refusait alors de les citer (7.100).
    if re.search(r"nous garantissons|nous couvrons|nous prenons en charge|nous (vous )?assurons|sont (garanti|couvert)"
                 r"|est (garanti|couvert)", corps):
        return TypeClause.GARANTIE
    if re.search(r"sous reserve|a condition|vous devez|doit ", corps):
        return TypeClause.CONDITION

    for titre in reversed(chemin[:-1]):
        if t := par_titre(titre):
            return t
    return TypeClause.AUTRE


@dataclass
class _Section:
    id: str
    titre: str
    niveau: int
    chemin: list[str]
    genre: str  # "num" (numérotée), "haut" (titre sans numéro de premier niveau), "sous" (intertitre)
    parent: str
    lignes: list[Ligne] = field(default_factory=list)
    enfants: int = 0


def _decouper_long(base: Clause, lignes: list[Ligne]) -> list[Clause]:
    morceaux: list[list[Ligne]] = [[]]
    taille = 0
    for l in lignes:
        puce = re.match(r"^\s*([•\-–■▪>]|\d{1,2}[.)]\s|[a-z][.)]\s)", l.texte)
        if taille > 1500 and puce:
            morceaux.append([])
            taille = 0
        morceaux[-1].append(l)
        taille += len(l.texte)
    if len(morceaux) == 1:
        return [base]
    return [
        base.model_copy(update={
            "id": f"{base.id}~{k}",
            "titre": base.titre if k == 1 else f"{base.titre} (suite {k})",
            "texte": " ".join(l.texte for l in m),
            "pages": sorted({l.page for l in m}),
        })
        for k, m in enumerate(morceaux, start=1)
    ]


def _terme_seul(ligne: str, precedente: str | None) -> bool:
    """Lexique « terme sur sa ligne, définition dessous » : ligne courte, majuscule, sans ponctuation finale,
    après une définition terminée (point) ou une liste à puces."""
    t = ligne.strip()
    fin_precedente = precedente is None or precedente.rstrip().endswith((".", ")")) or precedente.lstrip().startswith(("•", "-", "–"))
    return (
        fin_precedente
        and 0 < len(t) <= 50
        and len(t.split()) <= 6
        and t[:1].isupper()
        and not t.endswith((".", ",", ";", ":"))
        and not t.startswith(("•", "-", "–"))
    )


def _eclater_lexique(base: Clause, lignes: list[Ligne], format_: str = "auto") -> list[Clause]:
    termes: list[tuple[str, list[Ligne]]] = []
    if format_ == "auto":
        avec_deux_points = sum(bool(TERME_RE.match(l.texte)) for l in lignes) >= 3
    else:
        avec_deux_points = format_ == "deux_points"
    precedente: str | None = None
    for l in lignes:
        if avec_deux_points and (m := TERME_RE.match(l.texte)):
            termes.append((m.group(1).strip(" «»\""), [Ligne(l.page, m.group(2))]))
        elif not avec_deux_points and _terme_seul(l.texte, precedente):
            termes.append((l.texte.strip(), []))
        elif termes:
            termes[-1][1].append(l)
        precedente = l.texte
    termes = [(t, ls) for t, ls in termes if ls]
    if len(termes) < 3:
        return [base]
    sortie = []
    for terme, ls in termes:
        slug = re.sub(r"[^a-z0-9]+", "-", normaliser(terme)).strip("-")[:30]
        sortie.append(base.model_copy(update={
            "id": f"{base.id}/{slug}",
            "titre": terme,
            "chemin": base.chemin + [terme],
            "texte": " ".join(x.texte for x in ls),
            "pages": sorted({x.page for x in ls}),
        }))
    return sortie


def segmenter_lignes(lignes: list[Ligne], profil: dict | None = None) -> list[Clause]:
    """Découpe en clauses. `profil` : règles propres à l'assureur (voir `profils.py`)."""
    profil = profil or {}
    intertitres_profil = profil.get("intertitres", {})
    ignorees = [re.compile(m) for m in profil.get("lignes_ignorees", [])]
    if ignorees:
        lignes = [l for l in lignes if not any(m.search(l.texte) for m in ignorees)]
    if pages := profil.get("pages_ignorees"):  # des tableaux récapitulatifs, numérotés comme des articles (7.87)
        lignes = [l for l in lignes if not any(a <= l.page <= b for a, b in pages)]
    articles_seuls = profil.get("titres_numerotes") == "articles"
    clauses: list[Clause] = []
    deja: dict[str, int] = {}
    pile: list[_Section] = []
    hauts = 0
    courante = _Section("preambule", "Préambule", 0, ["Préambule"], "haut", "preambule")

    def fermer(s: _Section) -> None:
        if not s.lignes:
            return
        texte = " ".join(l.texte for l in s.lignes)
        type_ = classer(s.chemin, texte, profil)
        if s.genre == "sous":
            groupe = s.parent
        elif s.genre == "num":
            groupe = s.id.rsplit(".", 1)[0] if "." in s.id else s.id
        else:
            groupe = s.id
        sid = s.id
        if sid in deja:  # numérotation qui recommence (nouveau chapitre) : on suffixe
            deja[sid] += 1
            sid = f"{sid}'{deja[sid]}"
        else:
            deja[sid] = 1
        base = Clause(
            id=sid,
            article=sid.split(".")[0].split("-")[0],
            titre=s.titre,
            chemin=s.chemin,
            texte=texte,
            type=type_,
            groupe=groupe,
            pages=sorted({l.page for l in s.lignes}),
        )
        if type_ == TypeClause.DEFINITION:
            clauses.extend(_eclater_lexique(base, s.lignes, profil.get("lexique", "auto")))
        elif len(texte) > TAILLE_MAX:
            clauses.extend(_decouper_long(base, s.lignes))
        else:
            clauses.append(base)

    def chemin_de(titre: str) -> list[str]:
        return [p.chemin[-1] for p in pile] + [titre]

    for ligne in lignes:
        t = ligne.texte.lstrip("#").strip()
        if not t:
            continue

        if (num_titre := _titre_numerote(t)) and (not articles_seuls or ARTICLE_RE.match(t)):
            num, titre = num_titre
            fermer(courante)
            niveau = num.count(".") + 1
            while pile and (pile[-1].genre == "sous" or (pile[-1].genre == "num" and pile[-1].niveau >= niveau)):
                pile.pop()
            affiche = f"{'Article ' if ARTICLE_RE.match(t) else ''}{num} {titre}".strip()
            courante = _Section(num, titre, niveau, chemin_de(affiche), "num", num)
            pile.append(courante)
            continue

        # Dans un lexique, un terme en capitales (« DOMMAGE CORPOREL ») est un terme, pas un titre (7.87).
        if courante.genre != "num" and re.search(r"definition|lexique|glossaire", normaliser(courante.titre)) \
                and _terme_en_capitales(t) and not CONTENEUR_RE.match(t):
            courante.lignes.append(ligne)
            continue

        intertitre = _intertitre(t, intertitres_profil)
        capitales = not intertitre and (_en_capitales(t) or CONTENEUR_RE.match(t))
        if intertitre or capitales:
            titre = (intertitre or t).strip()
            fermer(courante)
            a_un_numero = any(p.genre == "num" for p in pile)
            if capitales and (CONTENEUR_RE.match(t) or not a_un_numero):
                # Titre de premier niveau (chapitre, ou section d'un contrat sans numérotation).
                pile.clear()
                hauts += 1
                courante = _Section(f"S{hauts}", titre, 0, [titre], "haut", f"S{hauts}")
            else:
                while pile and pile[-1].genre == "sous":
                    pile.pop()
                if pile:
                    parent = pile[-1]
                    parent.enfants += 1
                    sid = f"{parent.id}-{chr(96 + min(parent.enfants, 26))}"
                    courante = _Section(sid, titre, parent.niveau, chemin_de(titre), "sous", parent.id)
                else:
                    hauts += 1
                    courante = _Section(f"S{hauts}", titre, 0, [titre], "haut", f"S{hauts}")
            pile.append(courante)
            continue

        courante.lignes.append(ligne)

    fermer(courante)

    # Renvois : « au sens de l'article 1.5 » → lien vers la clause 1.5.
    ids = [c.id for c in clauses]
    for c in clauses:
        cibles: list[str] = []
        for ref in extraire_renvois(c.texte):
            cibles.extend(i for i in resoudre(ref, ids) if i != c.id)
        c.renvois = list(dict.fromkeys(cibles))
    return clauses

