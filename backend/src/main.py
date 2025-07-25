# Importa i moduli necessari da FastAPI e dalla libreria standard.
from fastapi import FastAPI, Depends, HTTPException
import mariadb
from typing import List
import time
import requests

# Importa i moduli locali usando la notazione relativa (con il punto),
# che è essenziale per il corretto funzionamento dei package Python.
from . import models
from . import services
from . import database
from .text_to_sql import translator
from .text_to_sql import generate_sql_from_question

# Inizializza l'applicazione FastAPI.
app = FastAPI(
    title="Natural Language to SQL API",
    description="Servizio backend per convertire linguaggio naturale in query SQL ed eseguire operazioni sul database.",
    version="1.0.0"
)

# --- Dependency Injection ---
# Creiamo un alias per la dipendenza del database. In questo modo, ogni endpoint
# che necessita di una connessione al DB può semplicemente richiederla.
# FastAPI si occuperà di creare la connessione all'inizio della richiesta
# e di chiuderla alla fine, grazie alla logica nel file database.py.
DbConnection = Depends(database.get_db_connection)

# --- Endpoints ---

@app.get("/schema_summary",
    response_model=List[models.SchemaItem],
    tags=["Database"],
    summary="Recupera lo schema del database"
)
def get_schema_summary(conn: mariadb.Connection = DbConnection):
    """
    Restituisce una lista di tutte le tabelle e colonne presenti nel database.
    Questa informazione è utile sia per l'interfaccia utente sia per costruire
    il prompt per l'LLM.
    """
    return services.get_database_schema(conn)


@app.post("/add",
    response_model=models.StatusResponse,
    status_code=201, # 201 Created è più appropriato per un'aggiunta
    tags=["Database"],
    summary="Aggiunge nuovi dati da una stringa"
)
def add_data(request: models.AddRequest, conn: mariadb.Connection = DbConnection):
    """
    Aggiunge nuovi dati partendo da una singola stringa con valori separati da virgola.
    Es: "Pulp Fiction,Quentin Tarantino,61,1994,Crime,Netflix"
    """

    try:
        services.add_new_data(request.data_line, conn)
        return {"status": "ok", "message": "Dati aggiunti con successo"}
    except HTTPException as e:
        # Rilancia le eccezioni HTTP sollevate dal servizio per restituire l'errore corretto.
        raise e
    except Exception as e:
        # Gestisce errori generici non previsti.
        raise HTTPException(status_code=500, detail=f"Un errore interno è occorso: {e}")


@app.post("/sql_search",
    response_model=models.SearchResponse,
    tags=["Search"],
    summary="Esegue una query SQL diretta"
)
def sql_search(request: models.SqlSearchRequest, conn: mariadb.Connection = DbConnection):
    """
    Permette di eseguire una query SQL (solo SELECT) direttamente sul database.
    Questo endpoint è utile per il debug e per i test automatici.
    Include una validazione di sicurezza per prevenire comandi dannosi.
    """
    return services.process_sql_query(request.sql_query, conn)


@app.post("/search",
    response_model=models.SearchResponse,
    tags=["Search"],
    summary="Converte linguaggio naturale in SQL e cerca"
)
@app.post("/search")
def search(request: models.SearchRequest, conn: mariadb.Connection = DbConnection):
    try:
        # Aggiungi log per debug
        print(f"Starting SQL generation for: {request.question}")
        
        sql_query = translator.generate_sql_from_question(
            question=request.question,
            model=request.model
        )
        
        print(f"Generated SQL: {sql_query}")
        return services.process_sql_query(sql_query, conn)
        
    except Exception as e:
        # Log dettagliato dell'errore
        error_trace = traceback.format_exc()
        print(f"SQL generation error: {error_trace}")
        
        raise HTTPException(
            status_code=503,
            detail=f"Errore durante la generazione SQL: {str(e)}"
        )

@app.on_event("startup")
async def startup_event():
    """Wait for Ollama service to be ready"""
    from .config import settings
    attempts = 0
    max_attempts = 30
    
    while attempts < max_attempts:
        try:
            # Check basic API availability
            resp = requests.get(settings.OLLAMA_API_URL.replace("/api/generate", "/api/tags"))
            if resp.status_code == 200:
                return
        except:
            pass
        
        time.sleep(1)
        attempts += 1
    
    print("⚠️ Warning: Ollama service not fully ready")
