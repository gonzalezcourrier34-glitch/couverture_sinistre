"""`couverture modele` : le modèle configuré, et un test de connexion."""

from __future__ import annotations

from pathlib import Path

from ..contrat.base import Base
from ..llm import ErreurLLM, configurer, modele_de_verification, noms_du_modele


def ajouter(sous) -> None:
    """Déclare la commande « modele »."""
    sous.add_parser("modele", help="Afficher le modèle configuré et tester la connexion").set_defaults(executer=executer)


def executer(a, base: Base, donnees: Path) -> int:
    """Le modèle configuré, et un appel pour tester la connexion."""
    try:
        llm = configurer()
    except ErreurLLM as e:
        print(f"Configuration invalide : {e}")
        return 1
    if llm is None:
        print("Aucun modèle configuré.")
        print("Créer un fichier .env à la racine du projet avec la ligne : MISTRAL_API_KEY=votre-clé")
        return 1
    contrat = configurer("contrat")
    print(f"Modèle des analyses : {llm.nom}")
    if contrat is not None and contrat.nom != llm.nom:
        print(f"Modèle des contrats (rédaction des règles) : {contrat.nom}")
    try:
        reponse = llm.completer('Réponds uniquement par un objet JSON.', 'Renvoie {"ok": true}.')
    except ErreurLLM as e:
        print(f"Échec de la connexion : {e}")
        return 1
    print(f"Connexion réussie. Réponse : {reponse.strip()[:200]}")
    # Ce que désignent aujourd'hui les noms configurés : « -latest » est un alias, qui change sans prévenir (7.145).
    for role, m in (("analyses", llm), ("vérification", modele_de_verification(llm))):
        noms = noms_du_modele(m) if m is not None and hasattr(m, "modele") else []
        autres = [n for n in noms if n != m.modele] if noms else []
        if autres:
            print(f"Modèle des {role if role == 'analyses' else 'vérifications'} : « {m.modele} » désigne aujourd'hui "
                  f"le même modèle que {', '.join(autres)}.")
    if hasattr(llm, "reflexion_refusee"):
        niveau = llm.extra.get("reasoning_effort")
        etat = ("refusé par ce modèle, il réfléchit à son niveau par défaut" if llm.reflexion_refusee
                else f"« {niveau} » accepté" if niveau else "non demandé (niveau par défaut du modèle)")
        print(f"Réflexion : {etat} ; {llm.derniere_reflexion} caractères de réflexion pour ce test.")
    return 0
