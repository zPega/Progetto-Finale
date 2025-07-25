# --- Fase 1: Base Comune ---
# Usiamo un'immagine base per installare le dipendenze comuni a produzione e test.
FROM python:3.9-slim AS base

# Installa le dipendenze di sistema necessarie per compilare il connettore MariaDB
RUN apt-get update && apt-get install -y build-essential libmariadb-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN pip install poetry
# Forza Poetry a creare .venv nella directory del progetto
RUN poetry config virtualenvs.in-project true

COPY pyproject.toml ./

# --- Fase 2: Immagine di Test ---
# Questa fase eredita dalla base e installa TUTTE le dipendenze.
FROM base AS test
RUN poetry lock
RUN poetry install --no-root
# CORREZIONE: Aggiunge il percorso del virtual environment al PATH del container
ENV PATH="/app/.venv/bin:$PATH"
COPY . .
# Il comando di default per questa immagine è l'esecuzione di pytest.
CMD ["pytest", "-v"]

# --- Fase 3: Immagine di Produzione ---
# Questa fase crea l'immagine finale che andrà in esecuzione per il servizio 'backend'.
FROM base AS production
RUN poetry lock
# Installa SOLO le dipendenze di produzione
RUN poetry install --no-root --only main
# Copia solo il codice sorgente necessario per l'esecuzione.
COPY ./src ./src
# Imposta la variabile d'ambiente PATH per usare l'ambiente virtuale di Poetry.
ENV PATH="/app/.venv/bin:$PATH"
# Comando per avviare il server FastAPI.
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8003"]