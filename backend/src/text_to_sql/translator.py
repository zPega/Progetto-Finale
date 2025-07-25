# Importa i moduli necessari
import os
import mariadb
import requests
from typing import Dict

# Usa un import relativo per trovare i prompt
from .prompts import SQL_PROMPT_TEMPLATE
from ..config import settings
from tenacity import retry, stop_after_attempt, wait_fixed
import json
from json import JSONDecodeError
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type


def _get_db_connection():
    try:
        conn = mariadb.connect(
            host=settings.DATABASE_HOST,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
            database=settings.DATABASE_NAME,
            port=3306
        )
        return conn
    except mariadb.Error as e:
        raise ConnectionError(f"Errore di connessione al DB per recupero schema: {e}")
    
def _get_db_schema_prompt_str() -> str:
    """Recupera dinamicamente lo schema del DB."""
    conn = _get_db_connection()
    cursor = conn.cursor(dictionary=True)
    prompt_lines = ["### Schema del database MariaDB:"]
    
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE()")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table['table_name']
        prompt_lines.append(f"Tabella `{table_name}` con colonne:")
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = cursor.fetchall()
        for col in columns:
            prompt_lines.append(f" - `{col['Field']}` (tipo: {col['Type']})")
            
    cursor.close()
    conn.close()
    return "\n".join(prompt_lines)



@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    retry=retry_if_exception_type((requests.RequestException, ValueError, JSONDecodeError))
)
def _call_ollama(model: str, prompt: str) -> str:
    try:
        ollama_url = f"http://{settings.OLLAMA_HOST}:11434/api/generate"
        
        response = requests.post(
            ollama_url,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=30  # Aumenta il timeout
        )
        
        # Verifica lo stato HTTP
        if response.status_code != 200:
            raise ValueError(f"Ollama API returned {response.status_code}: {response.text}")
        
        # Parsing sicuro del JSON
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON response: {response.text[:200]}")
        
        # Estrazione sicura della risposta
        if "response" not in data:
            raise ValueError(f"Missing 'response' field in Ollama output: {data}")
        
        return data["response"]
    
    except requests.RequestException as e:
        raise ConnectionError(f"Errore di rete: {e}")

def _clean_sql(raw_sql: str) -> str:
    """Pulisce l'output SQL grezzo."""
    cleaned_sql = raw_sql
    if "```sql" in cleaned_sql:
        cleaned_sql = cleaned_sql.split("```sql", 1)[1]
    cleaned_sql = cleaned_sql.replace("```", "").replace(";", "").strip()
    return cleaned_sql

def generate_sql_from_question(question: str, model: str) -> str:
    """Funzione principale che orchestra il processo."""
    schema_prompt = _get_db_schema_prompt_str()
    full_prompt = SQL_PROMPT_TEMPLATE.format(schema=schema_prompt, question=question)
    raw_sql = _call_ollama(model, full_prompt)
    cleaned_sql = _clean_sql(raw_sql)
    return cleaned_sql