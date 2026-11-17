FROM python:3.12-slim
WORKDIR /app
# EXTRAS=suivi installe MLflow (docker-compose.yml) ; vide, l'image reste légère.
ARG EXTRAS=""
# SWI-Prolog : la méthode « regles » appelle le programme swipl (ce n'est pas un paquet Python, uv.lock ne le connaît pas).
RUN apt-get update && apt-get install -y --no-install-recommends swi-prolog-nox && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml README.md ./
COPY src ./src
COPY config ./config
COPY regles ./regles
RUN pip install --no-cache-dir ".${EXTRAS:+[$EXTRAS]}"
COPY data ./data
# Sans docker compose : les contrats sont lus à la construction de l'image.
RUN MLFLOW_ACTIF=false couverture ingerer
EXPOSE 8000
CMD ["couverture", "serveur", "--hote", "0.0.0.0", "--port", "8000"]
