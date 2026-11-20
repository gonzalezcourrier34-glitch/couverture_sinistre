"""`couverture api` : l'API FastAPI (documentation sur /docs), clé COUVERTURE_API_KEY."""

from __future__ import annotations

import os
from pathlib import Path

from ..base import Base


def ajouter(sous) -> None:
    p = sous.add_parser("api", help="Lancer l'API FastAPI (documentation sur /docs)")
    p.add_argument("--hote", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8001)
    p.set_defaults(executer=executer)


def executer(a, base: Base, donnees: Path) -> int:
    import uvicorn

    # L'API lit sa base dans COUVERTURE_BASE : celle de la ligne de commande.
    os.environ.setdefault("COUVERTURE_BASE", base.chemin)
    try:
        uvicorn.run("couverture.api.main:app", host=a.hote, port=a.port)
    except KeyboardInterrupt:
        # Ctrl+C : uvicorn a déjà tout arrêté proprement (« Finished server process ») ; sous Windows avec
        # Python 3.14, il relance l'interruption et la trace s'affiche pour rien.
        pass
    return 0
