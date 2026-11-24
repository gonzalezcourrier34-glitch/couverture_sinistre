# Image de la démonstration en ligne : l'écran et l'API dans un seul conteneur (DEMARCHE 7.161).
#
#   docker build -f deploiement/Dockerfile -t couverture-enligne .
#   docker run --rm -p 8080:8001 --env-file deploiement/enligne.env couverture-enligne
#   puis http://localhost:8080 : le navigateur demande le code d'accès (nom libre, mot de passe = le code).
#
# À construire sur le poste, après `couverture ingerer` et `couverture exemples --indexer` : l'image embarque la
# base du poste (data/base.sqlite), déjà anonymisée, pas les PDF des assureurs ni la liste des noms. Elle
# contient le texte des clauses : elle se range dans un registre PRIVÉ.

# 1. L'écran, construit par Angular.
FROM node:22-slim AS ecran
WORKDIR /ecran
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# 2. La base, sans le journal local ni le texte brut des contrats.
FROM python:3.12-slim AS donnees
WORKDIR /prep
COPY data/base.sqlite ./base.sqlite
COPY deploiement/nettoyer_base.py ./
RUN python nettoyer_base.py base.sqlite

# 3. L'image servie.
FROM python:3.12-slim
# SWI-Prolog : le moteur appelle le programme swipl.
RUN apt-get update && apt-get install -y --no-install-recommends swi-prolog-nox && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY config ./config
# Tout le dossier des règles : le moteur, les règles, le vocabulaire, les formules, l'état de traduction. Les
# fichiers étaient copiés un par un, et `traduction.json` avait été oublié (7.173). Ce qui ne sert qu'à rédiger
# (propositions, cas de non-régression) est écarté par .dockerignore.
COPY regles ./regles
# Installation « éditable » : le code cherche regles/ et config/ à côté de src/, donc dans /app.
RUN pip install --no-cache-dir -e .
COPY data/lecture ./data/lecture
COPY --from=donnees /prep/base.sqlite ./data/base.sqlite
COPY --from=ecran /ecran/dist/couverture-front/browser ./ecran
# Le journal des analyses sort aussi sur la sortie standard : la base du conteneur ne survit pas à un réveil.
ENV COUVERTURE_FRONT=/app/ecran \
    COUVERTURE_BASE=/app/data/base.sqlite \
    COUVERTURE_JOURNAL_SORTIE=1
EXPOSE 8001
# Les secrets viennent de l'environnement, jamais de l'image : MISTRAL_API_KEY, COUVERTURE_CODE_ACCES,
# et les noms de modèles (COUVERTURE_MODELE, COUVERTURE_MODELE_VERIFICATION).
CMD ["couverture", "api", "--hote", "0.0.0.0", "--port", "8001"]
