# Importa i moduli necessari da Pydantic e typing.
from pydantic import BaseModel
from typing import List, Optional, Literal, Any

# Modello per la richiesta di aggiunta dati.
class AddRequest(BaseModel):
    data_line: str

# Modello per la richiesta di ricerca tramite SQL diretto.
class SqlSearchRequest(BaseModel):
    sql_query: str

# Modello per la richiesta di ricerca tramite linguaggio naturale.
class SearchRequest(BaseModel):
    question: str
    # 'model' ha un valore di default, che verrà usato se il client non lo specifica.
    model: str = "gemma3:1b-it-qat"

# Modello per una singola proprietà di un risultato (es. "titolo": "Inception").
class ItemProperty(BaseModel):
    property_name: str
    property_value: Any # 'Any' permette qualsiasi tipo di valore.

# Modello per un singolo item nei risultati della ricerca (es. un film o un regista).
class ResultItem(BaseModel):
    item_type: str
    properties: List[ItemProperty]

# Modello completo per la risposta di una ricerca.
class SearchResponse(BaseModel):
    sql: str # La query SQL eseguita.
    # Lo stato di validazione della query: può essere 'valid', 'invalid' (sintassi errata), o 'unsafe'.
    sql_validation: Literal["valid", "invalid", "unsafe"]
    # La lista dei risultati, che può essere assente (Optional).
    results: Optional[List[ResultItem]]

# Modello per un item dello schema del database (una coppia tabella-colonna).
class SchemaItem(BaseModel):
    table_name: str
    table_column: str


from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Any



# definisce la struttura per aggiungere un film
from pydantic import BaseModel
from typing import List, Optional, Literal, Any

# Modello originale per la richiesta di aggiunta dati, come da specifica.
class AddRequest(BaseModel):
    data_line: str

class SqlSearchRequest(BaseModel):
    sql_query: str

class SearchRequest(BaseModel):
    question: str
    model: str = "gemma3:1b-it-qat"


class ItemProperty(BaseModel):
    property_name: str
    property_value: Any

class ResultItem(BaseModel):
    item_type: str
    properties: List[ItemProperty]

class SearchResponse(BaseModel):
    sql: str
    sql_validation: Literal["valid", "invalid", "unsafe"]
    results: Optional[List[ResultItem]]

class SchemaItem(BaseModel):
    table_name: str
    table_column: str

class StatusResponse(BaseModel):
    status: str
    message: Optional[str] = None


class StatusResponse(BaseModel):
    status: str
    message: Optional[str] = None
