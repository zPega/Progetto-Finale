#!/bin/bash
set -e

log() {
    color="$1"
    message="$2"
    printf "\n\033[1;%sm[OLLAMA] %s\033[0m\n" "$color" "$message"
}

# 1. Avvio del server in background
log "34" "Avvio del server in background..."
/bin/ollama serve &
SERVER_PID=$!

# 2. Attesa che il server sia operativo
log "33" "In attesa che il server diventi operativo..."
attempt=0
max_attempts=30
while ! curl -s -f http://localhost:11434 >/dev/null; do
    sleep 1
    attempt=$((attempt+1))
    if [ $attempt -ge $max_attempts ]; then
        log "31" "❌ Timeout: Server non avviato dopo $max_attempts secondi"
        exit 1
    fi
done

# 3. Verifica persistenza directory modelli
log "36" "Contenuto directory modelli:"
ls -la /root/.ollama/models

# 4. Verifica e Download del Modello
MODEL_NAME="gemma3:1b-it-qat"
log "36" "Verifica del modello: $MODEL_NAME"

# Verifica più affidabile della presenza del modello
if [ -d "/root/.ollama/models/blobs/sha256" ] && \
   ollama list | awk '{print $1}' | grep -q "^${MODEL_NAME}$"; then
    log "32" "Modello già presente"
else
    log "35" "Modello non trovato. Avvio del download..."
    if /bin/ollama pull "$MODEL_NAME"; then
        log "32" "✅ Download completato!"
    else
        log "31" "❌ Download fallito!"
        exit 1
    fi
fi

# 5. Verifica funzionalità modello
log "36" "Verifica funzionalità modello..."
if curl -s http://localhost:11434/api/tags | grep -q "$MODEL_NAME"; then
    log "32" "✅ Servizio pronto!"
else
    log "31" "❌ Verifica modello fallita!"
    exit 1
fi

# 6. Mantieni il container attivo
wait "$SERVER_PID"