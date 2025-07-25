# backend/src/database.py

import mariadb
from fastapi import HTTPException
from . import models
# Importa l'oggetto delle impostazioni invece di 'os'
from .config import settings 

def get_db_connection():
    """
    Questa funzione ora agisce come un "dependency provider" per FastAPI.
    'yield' passa la connessione all'endpoint e attende che finisca,
    per poi eseguire il codice nel blocco 'finally' (chiudere la connessione).
    """
    try:
        conn = mariadb.connect(
            host=settings.DATABASE_HOST,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
            database=settings.DATABASE_NAME,
            port=3306
        )
        yield conn # Passa la connessione all'endpoint che la richiede
    except mariadb.Error as e:
        raise HTTPException(status_code=503, detail=f"Errore di connessione al DB: {e}")
    finally:
        if 'conn' in locals() and conn is not None:
            conn.close() # La connessione viene chiusa qui, dopo che la richiesta è terminata.