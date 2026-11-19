"""Suivi des exécutions avec MLflow, sur le modèle de SortirIA (`agent/tracking.py`).

Deux expériences :
  - `couverture-ingestion` : **une ingestion = une exécution**. Métriques par contrat : clauses
    par type, alertes, statut ;
  - `couverture-evaluation` : **un banc = une exécution**. Paramètres : contrat, méthode, modèle de
    lecture, versions des consignes, version du golden set ; métriques : celles de chaque couche du
    banc (`regles/exactitude`, `lecture/decisions_changees`, `chaine/faux_couverts`…).

C'est ce qui permet de comparer deux versions d'une consigne, ou deux modèles, sur les mêmes
cas : chaque exécution porte les versions qui l'ont produite.

**Le suivi ne fait jamais échouer le travail** : sans MLflow installé, avec `MLFLOW_ACTIF=false`,
avec un serveur qui ne répond pas en 3 s, ou en cas d'erreur, le travail continue sans suivi.

Réglages (`.env`) :
  - `MLFLOW_TRACKING_URI` : serveur MLflow (`http://localhost:5010` avec docker compose) ;
    par défaut, une base SQLite locale `data/mlflow/mlflow.db` ;
  - `MLFLOW_ACTIF=false` : désactive le suivi.

Les fonctions qui calculent paramètres et métriques sont pures et testées sans MLflow.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
import urllib.request
from contextlib import contextmanager
from pathlib import Path

from .consignes import CONSIGNES

EXPERIENCE_INGESTION = "couverture-ingestion"
EXPERIENCE_EVALUATION = "couverture-evaluation"
CLE_RE = re.compile(r"[^A-Za-z0-9_\-./ ]")


def cle(*parties) -> str:
    """Nom de métrique accepté par MLflow : « contrat/assureur-a-habitation-2025/clauses/exclusion »."""
    return "/".join(CLE_RE.sub("_", str(p)) for p in parties if str(p))


# --- Ce qu'on enregistre (fonctions pures) -----------------------------------------------------

def parametres_communs(modele: str = "aucun") -> dict[str, str]:
    p = {f"consigne/{nom.removeprefix('couverture-')}": v for nom, (_, _, v) in CONSIGNES.items()}
    p["modele/lecture"] = modele
    return p


def metriques_banc(resultat: dict) -> dict[str, float]:
    """Les métriques numériques de chaque couche du banc : « chaine/exactitude », « lecture/rappel_faits »…"""
    m = {}
    for couche, r in resultat.get("couches", {}).items():
        for k, v in r.get("metriques", {}).items():
            if isinstance(v, dict) and isinstance(v.get("moyenne"), (int, float)):  # plusieurs exécutions
                v = v["moyenne"]
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                m[cle(couche, k)] = float(v)
    return m


def metriques_ingestion(contrats) -> dict[str, float]:
    m: dict[str, float] = {"contrats": float(len(contrats)),
                           "contrats_a_verifier": float(sum(c.statut != "OK" for c in contrats))}
    for c in contrats:
        r = c.rapport
        m[cle("contrat", c.id, "clauses")] = float(r.get("nb_clauses", 0))
        m[cle("contrat", c.id, "alertes")] = float(len(r.get("alertes", [])))
        m[cle("contrat", c.id, "ok")] = 1.0 if c.statut == "OK" else 0.0
        for type_, n in r.get("par_type", {}).items():
            m[cle("contrat", c.id, "clauses", type_)] = float(n)
        if "score" in r.get("qualite", {}):
            m[cle("contrat", c.id, "qualite_typage")] = float(r["qualite"]["score"])
    return m


def empreinte_fichiers(*chemins: Path) -> str:
    h = hashlib.sha256()
    for c in chemins:
        h.update(Path(c).read_bytes())
    return h.hexdigest()[:16]


# --- MLflow, facultatif et jamais bloquant ---------------------------------------------------------

def module_mlflow():
    """Le module mlflow configuré, ou None (absent, désactivé, ou serveur injoignable)."""
    if os.environ.get("MLFLOW_ACTIF", "true").strip().lower() in ("false", "non", "0"):
        return None
    try:
        import mlflow
    except ImportError:
        return None
    uri = os.environ.get("MLFLOW_TRACKING_URI", "").strip()
    if not uri:
        dossier = Path("data") / "mlflow"
        dossier.mkdir(parents=True, exist_ok=True)
        uri = f"sqlite:///{(dossier / 'mlflow.db').as_posix()}"
    elif uri.startswith("http"):
        try:
            urllib.request.urlopen(uri.rstrip("/") + "/health", timeout=3)
        except Exception as e:  # noqa: BLE001
            print(f"Suivi MLflow coupé : {uri} ne répond pas ({e}).", file=sys.stderr)
            return None
    mlflow.set_tracking_uri(uri)
    return mlflow


class _Execution:
    """Ce que le code appelant voit d'une exécution : des méthodes qui ne lèvent jamais."""

    def __init__(self, mlflow):
        self.mlflow = mlflow

    def _sur(self, action, *args):
        if self.mlflow is None:
            return
        try:
            action(*args)
        except Exception as e:  # noqa: BLE001
            print(f"Suivi MLflow : {e}", file=sys.stderr)

    def parametres(self, p: dict) -> None:
        self._sur(self.mlflow.log_params if self.mlflow else None, {k: str(v)[:500] for k, v in p.items()})

    def metriques(self, m: dict) -> None:
        self._sur(self.mlflow.log_metrics if self.mlflow else None, m)

    def etiquettes(self, t: dict) -> None:
        self._sur(self.mlflow.set_tags if self.mlflow else None, t)

    def artefact_json(self, nom: str, contenu: dict) -> None:
        if self.mlflow is None:
            return
        with tempfile.TemporaryDirectory() as d:
            chemin = Path(d) / nom
            chemin.write_text(json.dumps(contenu, ensure_ascii=False, indent=2), encoding="utf-8")
            self._sur(self.mlflow.log_artifact, str(chemin))


@contextmanager
def execution(experience: str, nom: str):
    """Une exécution MLflow, ou rien si le suivi n'est pas disponible. Ne lève jamais à cause du suivi."""
    mlflow = module_mlflow()
    run = None
    if mlflow is not None:
        try:
            mlflow.set_experiment(experience)
            run = mlflow.start_run(run_name=nom)
        except Exception as e:  # noqa: BLE001
            print(f"Suivi MLflow coupé : {e}", file=sys.stderr)
            mlflow = None
    try:
        yield _Execution(mlflow)
    finally:
        if mlflow is not None and run is not None:
            try:
                mlflow.end_run()
            except Exception:  # noqa: BLE001
                pass
