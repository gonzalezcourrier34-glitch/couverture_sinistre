FROM python:3.12-slim
WORKDIR /app
# SWI-Prolog : le moteur appelle le programme swipl (ce n'est pas un paquet Python, uv.lock ne le connaît pas).
RUN apt-get update && apt-get install -y --no-install-recommends swi-prolog-nox && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml README.md ./
COPY src ./src
COPY config ./config
COPY regles ./regles
RUN pip install --no-cache-dir .
COPY data ./data
# Sans docker compose : les contrats sont lus à la construction de l'image.
RUN couverture ingerer
EXPOSE 8001
# L'API (documentation sur /docs) ; la clé COUVERTURE_API_KEY vient de l'environnement.
CMD ["couverture", "api", "--hote", "0.0.0.0", "--port", "8001"]
