# frontend/src/main.py

import os
import requests
import json
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Optional
from fastapi.responses import JSONResponse

app = FastAPI(title="Frontend Service")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8003")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "results": None, "error": None})

@app.post("/", response_class=HTMLResponse)
async def handle_form_submission(
    request: Request,
    action: str = Form(...),
    sql_query: Optional[str] = Form(None),
    question: Optional[str] = Form(None),
    # NUOVO: Riceve i dati del film come stringa JSON
    data_json: Optional[str] = Form(None)
):
    context = {"request": request}
    
    try:
        if action == "schema_summary":
            response = requests.get(f"{BACKEND_URL}/schema_summary")
        elif action == "sql_search":
            response = requests.post(f"{BACKEND_URL}/sql_search", json={"sql_query": sql_query})
        elif action == "search":
            response = requests.post(f"{BACKEND_URL}/search", json={"question": question})
        # MODIFICA: Gestisce la nuova azione 'add'
        elif action == "add":
            if data_json:
                # Converte la stringa JSON in un dizionario Python
                movie_data = json.loads(data_json)
                # Invia il dizionario come payload JSON al backend
                response = requests.post(f"{BACKEND_URL}/add", json=movie_data)
            else:
                # Se non ci sono dati, imposta un errore
                context["error"] = "Nessun dato JSON ricevuto per l'aggiunta."
                return templates.TemplateResponse("index.html", context)
        else:
            context["error"] = "Azione non valida."
            return templates.TemplateResponse("index.html", context)

        response.raise_for_status()
        context["results"] = response.json()

    except requests.RequestException as e:
        context["error"] = f"Errore di comunicazione con il backend: {e}"
        if e.response is not None:
            try:
                context["error_detail"] = e.response.json()
            except json.JSONDecodeError:
                context["error_detail"] = e.response.text

    return templates.TemplateResponse("index.html", context)



# NUOVO ENDPOINT ASINCRONO PER AGGIUNGERE FILM
@app.post("/add_movie_async")
async def handle_add_movie_async(request: Request):
    """
    Endpoint asincrono che riceve dati JSON, li inoltra al backend
    e restituisce una risposta JSON, senza rendering di template.
    """
    try:
        movie_data = await request.json()
        response = requests.post(f"{BACKEND_URL}/add", json=movie_data)
        response.raise_for_status() # Solleva un'eccezione se il backend restituisce un errore
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except requests.RequestException as e:
        status_code = e.response.status_code if e.response is not None else 500
        detail = e.response.json().get("detail") if e.response is not None else str(e)
        return JSONResponse(content={"detail": detail}, status_code=status_code)
    
@app.post("/add_movie_async")
async def handle_add_movie_async(request: Request):
    """
    Endpoint asincrono che riceve dati JSON dal form JavaScript,
    li inoltra al backend e restituisce una risposta JSON.
    """
    try:
        movie_data = await request.json()
        response = requests.post(f"{BACKEND_URL}/add", json=movie_data)
        # Solleva un'eccezione se il backend restituisce un errore (es. 4xx o 5xx)
        response.raise_for_status() 
        return JSONResponse(content=response.json(), status_code=response.status_code)
    except requests.RequestException as e:
        status_code = e.response.status_code if e.response is not None else 500
        detail = e.response.json().get("detail") if e.response is not None else str(e)
        return JSONResponse(content={"detail": detail}, status_code=status_code)