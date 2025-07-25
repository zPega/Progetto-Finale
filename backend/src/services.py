# Importa i moduli necessari, inclusi il driver del database e i modelli Pydantic.
import mariadb
from fastapi import HTTPException
from . import database
from . import models
from typing import List

def is_safe_select(query: str) -> bool:
    """
    Funzione di sicurezza di base per validare una query SQL.
    Controlla che sia solo una 'SELECT' e che non contenga parole chiave pericolose
    per prevenire SQL injection e modifiche indesiderate al database.
    """
    query_lower = query.strip().lower()
    unsafe_keywords = ["insert", "update", "delete", "drop", "create", "alter", "truncate", "grant", "revoke"]
    # La query deve iniziare con 'select' e non deve contenere nessuna delle parole chiave vietate.
    return query_lower.startswith("select") and not any(keyword in query_lower for keyword in unsafe_keywords)

def process_sql_query(query: str) -> models.SearchResponse:
    """
    Servizio centralizzato per l'esecuzione di query SQL.
    Valida la query, la esegue e formatta la risposta per il frontend.
    """
    # Primo controllo di sicurezza.
    if not is_safe_select(query):
        return models.SearchResponse(sql=query, sql_validation="unsafe", results=None)
    
    conn = database.get_db_connection()
    try:
        # Esegue la query tramite il modulo 'database'.
        results = database.execute_sql_query(query, conn)
        validation = "valid"
    except mariadb.Error as e:
        # Se la query ha un errore di sintassi, lo gestisce.
        print(f"Errore di sintassi SQL: {e}")
        results = None
        validation = "invalid"
    finally:
        # La connessione al database viene sempre chiusa, anche in caso di errore.
        conn.close()
    
    return models.SearchResponse(sql=query, sql_validation=validation, results=results)

# CORRETTO in services.py

def get_database_schema(conn: mariadb.Connection) -> List[models.SchemaItem]:
    """
    Usa la connessione fornita da FastAPI tramite Dependency Injection.
    """
    # ORA 'conn' È L'OGGETTO GIUSTO
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = DATABASE() ORDER BY table_name, ordinal_position")
    schema = cursor.fetchall()
    
    # Non chiudere il cursore o la connessione qui!
    # Se ne occupa la dipendenza in database.py.
    cursor.close() 
    
    return [models.SchemaItem(table_name=row['table_name'], table_column=row['column_name']) for row in schema]


def add_new_data(data_line: str, conn: mariadb.Connection) -> None:
    """
    Logica per aggiungere dati da una singola stringa CSV, come da specifica.
    """
    cursor = conn.cursor()
    try:
        parts = [p.strip() for p in data_line.split(',')]
        if len(parts) < 5:
            raise HTTPException(status_code=422, detail="Formato data_line non valido, sono richiesti almeno 5 campi.")

        titolo, regista_nome, eta_autore_str, anno_str, genere = parts[0], parts[1], parts[2], parts[3], parts[4]
        piattaforme = parts[5:]

        if not titolo or not regista_nome:
            raise ValueError("Titolo e nome del regista non possono essere vuoti.")
        
        anno_nascita_regista = datetime.datetime.now().year - int(eta_autore_str)

        # Logica UPSERT per regista, film e piattaforme... (questa parte rimane uguale)
        cursor.execute("SELECT id FROM directors WHERE name = ?", (regista_nome,))
        dir_row = cursor.fetchone()
        if dir_row:
            director_id = dir_row[0]
            cursor.execute("UPDATE directors SET birth_year = ? WHERE id = ?", (anno_nascita_regista, director_id))
        else:
            cursor.execute("INSERT INTO directors (name, birth_year) VALUES (?, ?)", (regista_nome, anno_nascita_regista))
            director_id = cursor.lastrowid
        
        cursor.execute("SELECT id FROM movies WHERE titolo = ?", (titolo,))
        mov_row = cursor.fetchone()
        if mov_row:
            movie_id = mov_row[0]
            cursor.execute("UPDATE movies SET anno = ?, genere = ?, director_id = ? WHERE id = ?", (int(anno_str), genere, director_id, movie_id))
            cursor.execute("DELETE FROM movie_platforms WHERE movie_id = ?", (movie_id,))
        else:
            cursor.execute("INSERT INTO movies (titolo, anno, genere, director_id) VALUES (?, ?, ?, ?)", (titolo, int(anno_str), genere, director_id))
            movie_id = cursor.lastrowid

        for nome_piattaforma in piattaforme:
            if not nome_piattaforma: continue
            cursor.execute("SELECT id FROM platforms WHERE name = ?", (nome_piattaforma,))
            plat_row = cursor.fetchone()
            platform_id = plat_row[0] if plat_row else cursor.execute("INSERT INTO platforms (name) VALUES (?)", (nome_piattaforma,)) or cursor.lastrowid
            cursor.execute("INSERT INTO movie_platforms (movie_id, platform_id) VALUES (?, ?)", (movie_id, platform_id))
        
        conn.commit()
    except (mariadb.Error, ValueError, IndexError) as e:
        conn.rollback()
        raise HTTPException(status_code=422, detail=f"Errore nell'elaborazione dei dati: {e}")
    finally:
        cursor.close()
