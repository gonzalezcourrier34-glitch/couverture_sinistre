"""Analyser un sinistre : de la déclaration à la réponse, avec ses preuves.

    lecture.py      le modèle lit les faits de la déclaration ; chaque fait est vérifié sur ses mots
    exemples.py     la banque d'exemples de lecture, choisis par similarité
    prolog.py       le pont vers le moteur de règles (SWI-Prolog), le vocabulaire des faits
    chaine.py       la chaîne complète : lire, décider, rédiger la réponse
    validation.py   chaque citation est retrouvée mot pour mot dans sa clause, sinon la réponse est rétrogradée
    journal.py      le journal des analyses (sans le texte des déclarations)
    fiche.py        la fiche d'analyse en PDF

Le modèle lit, la logique décide, le code vérifie : aucune décision ne sort du modèle.
"""
