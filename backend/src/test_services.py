# backend/tests/test_services.py

# Importa il modulo pytest, lo standard de-facto per il testing in Python.
import pytest
# Importa il modulo 'services' dall'applicazione per poter testare le sue funzioni.
from src import services

# --- Test per la funzione di validazione SQL: is_safe_select ---
# Questi test verificano che la funzione di sicurezza per le query SQL
# si comporti come previsto, bloccando query potenzialmente dannose.

def test_is_safe_select_valid():
    """
    Scopo del test: Verificare che una query SELECT semplice e sicura venga accettata.
    Questo è il caso d'uso più comune e importante.
    """
    query = "SELECT titolo FROM movies WHERE genere = 'Sci-Fi'"
    # L'asserzione 'assert' controlla che la condizione sia vera. Se è falsa, il test fallisce.
    assert services.is_safe_select(query) is True

def test_is_safe_select_with_join():
    """
    Scopo del test: Verificare che anche una query SELECT più complessa,
    contenente una clausola JOIN, sia considerata sicura.
    """
    query = "SELECT m.titolo FROM movies m JOIN directors d ON m.director_id = d.id"
    assert services.is_safe_select(query) is True

def test_is_safe_select_unsafe_keyword_drop():
    """
    Scopo del test: Verificare che una query che tenta di eseguire un'operazione
    distruttiva (DROP TABLE) venga correttamente identificata come non sicura.
    Questo previene attacchi di tipo SQL Injection.
    """
    query = "SELECT * FROM movies; DROP TABLE users;"
    assert services.is_safe_select(query) is False

def test_is_safe_select_unsafe_keyword_update():
    """
    Scopo del test: Verificare che una query che tenta di modificare dati (UPDATE)
    venga rifiutata, poiché l'endpoint è pensato solo per la lettura.
    """
    query = "UPDATE movies SET genere = 'Comedy' WHERE id = 1"
    assert services.is_safe_select(query) is False

def test_is_safe_select_not_starting_with_select():
    """
    Scopo del test: Verificare che la funzione applichi rigorosamente la regola
    che la query DEVE iniziare con 'SELECT'. Anche query legittime che non iniziano
    con SELECT (come quelle che usano Common Table Expressions, CTE) vengono bloccate
    da questa semplice regola di sicurezza.
    """
    # Nota: Questa query non è dannosa, ma viene bloccata per la regola di sicurezza scelta.
    query = "WITH my_cte AS (SELECT 1) SELECT * FROM my_cte;"
    assert services.is_safe_select(query) is False