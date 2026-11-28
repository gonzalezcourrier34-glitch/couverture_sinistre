"""Analyser un sinistre : de la déclaration à la réponse, avec ses preuves. Deux méthodes.

La lecture des clauses (méthode par défaut) : le modèle juge chaque clause, une logique fixe décide.
    attendu.py      pour chaque garantie, les clauses qu'un gestionnaire doit relire
    dossier.py      la table des matières, et le dossier d'un sinistre : chapitres désignés et clauses attendues
    clauses.py      les consignes et les appels au modèle (désigner, juger, relire un obstacle), l'analyse entière
    jugement.py     le contrôle de chaque jugement (clause attendue, citations exactes) et la décision
    brut.py         la référence « tout le contrat en un appel », pour comparer seulement (`juger --brut`)

La chaîne de règles : le modèle lit les faits, le moteur Prolog décide.
    lecture.py      le modèle lit les faits de la déclaration ; chaque fait est vérifié sur ses mots
    exemples.py     la banque d'exemples de lecture, choisis par similarité
    prolog.py       le pont vers le moteur de règles (SWI-Prolog), le vocabulaire des faits
    chaine.py       la chaîne complète : lire, décider, rédiger la réponse
    validation.py   chaque citation est retrouvée mot pour mot dans sa clause, sinon la réponse est rétrogradée

Pour les deux :
    journal.py      le journal des analyses (sans le texte des déclarations)
    fiche.py        la fiche d'analyse en PDF

Le modèle lit ou juge, la logique décide, le code vérifie : en service, aucune décision ne sort du modèle (la
référence `brut.py` est la seule exception, et ne sert qu'à mesurer).
"""
