"""`couverture rediger` : Mistral Large rédige les règles d'une garantie, le code les contrôle."""

from __future__ import annotations

import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .. import redaction
from ..analyse import prolog
from ..contrat.base import Base
from ..llm import ErreurLLM, configurer
from ..mesure.evaluation import lire_jsonl
from ..progression import Barre


def ajouter(sous) -> None:
    """Déclare la commande « rediger » et ses options."""
    p = sous.add_parser("rediger", help="Faire rédiger par le modèle les règles Prolog d'une garantie, puis les contrôler")
    p.add_argument("--contrat", required=True)
    p.add_argument("--article", action="append", help="Article à traduire (répétable), ex. --article 2.2 --article 2.9")
    p.add_argument("--controler", action="store_true", help="Refaire les contrôles des propositions enregistrées, sans modèle")
    p.add_argument("--paralleles", type=int, default=3, help="Articles rédigés à la fois (défaut 3)")
    p.add_argument("--accepter", metavar="ARTICLE", help="Ajouter la proposition aux règles du contrat (si rien ne bloque)")
    p.add_argument("--accepter-vocabulaire", metavar="ARTICLE",
                   help="Ajouter au vocabulaire commun les faits nouveaux déclarés par le modèle pour cet article")
    p.set_defaults(executer=executer)


def executer(a, base: Base, donnees: Path) -> int:
    """Rédaction des règles d'une garantie par le modèle (Mistral Large), contrôles, acceptation."""
    contrat_id, articles, controler = a.contrat, a.article or [], a.controler
    a_accepter, vocabulaire, paralleles = a.accepter, a.accepter_vocabulaire, a.paralleles

    clauses = base.clauses(contrat_id)
    cas = []
    for f in sorted((prolog.DOSSIER / "cas").rglob(f"{contrat_id}.jsonl")):
        cas += [(d["sinistre_id"], d["faits"]) for d in lire_jsonl(f)]

    if vocabulaire:
        js, _ = redaction.chemins(contrat_id, vocabulaire)
        ajouts = redaction.accepter_vocabulaire(json.loads(js.read_text(encoding="utf-8"))["proposition"],
                                                 contrat_id=contrat_id)
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

    llm = configurer("contrat")
    if llm is None:
        sys.exit("La rédaction a besoin d'un modèle : définir MISTRAL_API_KEY dans .env.")
    barre = Barre(len(articles), "Rédaction")
    docs = []

    def une(art):
        try:
            return redaction.rediger(contrat_id, art, clauses, llm, cas=cas)
        except (LookupError, ValueError, prolog.ErreurRegles, ErreurLLM) as e:
            barre.ecrire(f"art. {art} : échec ({e}) ; la réponse du modèle, si elle est arrivée, est gardée : "
                         f"`couverture rediger --contrat {contrat_id} --controler --article {art}`")
            return None

    # Les articles sont indépendants : une rédaction attend surtout le modèle (6 à 27 min), on en lance
    # plusieurs à la fois (7.62). Les doublons entre propositions (un concept défini deux fois) sont vus
    # au contrôle qui suit chaque acceptation.
    barre.ecrire(f"{len(articles)} article(s), {max(1, paralleles)} à la fois, par {llm.nom}…")
    with ThreadPoolExecutor(max_workers=max(1, paralleles)) as ex:
        futurs = {ex.submit(une, art): art for art in articles}
        for f in as_completed(futurs):
            d = f.result()
            if d is not None:
                docs.append(d)
            barre.avancer(futurs[f])
    barre.terminer()
    docs.sort(key=lambda d: [(0, int(x), "") if x.isdigit() else (1, 0, x) for x in re.split(r"[.~-]", d["meta"]["article"])])
    for d in docs:
        print(redaction.resumer(d))
    print(f"Propositions dans regles/propositions/{contrat_id}/ (JSON : la source, corrigible à la main ; .pl : les règles).")
    return 0
