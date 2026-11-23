"""Prépare la base embarquée dans l'image en ligne (DEMARCHE 7.161).

La base du poste contient ce que la mise en ligne n'a pas à emporter : le journal des analyses faites en local
(des déclarations tapées pendant le développement), le texte brut de chaque contrat, d'anciennes tables. On garde
ce que l'API lit : les contrats, leurs clauses, les renvois, et l'index des exemples de lecture.

    python nettoyer_base.py base.sqlite
"""

import sqlite3
import sys

chemin = sys.argv[1]
cx = sqlite3.connect(chemin)
tables = {t for (t,) in cx.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
if "analyses" in tables:
    cx.execute("DELETE FROM analyses")
if "contrats" in tables:
    cx.execute("UPDATE contrats SET texte_brut = ''")
for ancienne in ("vecteurs", "compilations"):
    if ancienne in tables:
        cx.execute(f"DELETE FROM {ancienne}")
cx.commit()
cx.execute("VACUUM")
n_contrats = cx.execute("SELECT COUNT(*) FROM contrats").fetchone()[0]
n_clauses = cx.execute("SELECT COUNT(*) FROM clauses").fetchone()[0]
n_exemples = cx.execute("SELECT COUNT(*) FROM exemples").fetchone()[0] if "exemples" in tables else 0
cx.close()
print(f"Base prête : {n_contrats} contrats, {n_clauses} clauses, {n_exemples} exemples indexés ; journal et texte brut retirés.")
