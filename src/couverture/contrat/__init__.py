"""Lire un contrat : du fichier des conditions générales aux clauses rangées dans la base.

    chargement.py           lit le PDF ou le document Word, retire le bruit (en-têtes, sommaire, mots coupés)
    segmentation.py         découpe le texte en clauses typées (garantie, exclusion, définition…) et relève les renvois
    profils.py              les habitudes de rédaction d'un assureur, quand les règles générales ne suffisent pas
    anonymisation.py        masque les noms des assureurs dans le texte, d'après une liste privée
    controle_decoupage.py   contrôle le découpage : un contrat mal lu est marqué « à vérifier »
    ingestion.py            enchaîne le tout pour chaque fichier de `data/contrats`
    tableaux.py             lit le tableau des garanties par formule, par la position des mots sur la page
    base.py                 la base SQLite : contrats, clauses, renvois

Rien ici n'appelle un modèle : un contrat se lit une fois, à l'ingestion, et se contrôle par le code.
"""
