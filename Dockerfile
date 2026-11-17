FROM python:3.12-slim
WORKDIR /app
# EXTRAS=suivi installe MLflow (docker-compose.yml) ; vide, l'image reste légère.
ARG EXTRAS=""
COPY pyproject.toml README.md ./
COPY src ./src
COPY config ./config
RUN pip install --no-cache-dir ".${EXTRAS:+[$EXTRAS]}"
COPY data ./data
# Sans docker compose : les contrats sont lus à la construction de l'image.
RUN MLFLOW_ACTIF=false couverture ingerer
EXPOSE 8000
CMD ["couverture", "serveur", "--hote", "0.0.0.0", "--port", "8000"]
