"""
Dashboard FastAPI — Painel web para monitoramento e controle da sincronização.
"""

import logging
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api.client import CashUpClient
from api.endpoints import Endpoints
from scheduler.jobs import (
    get_available_entities,
    run_sync_manual,
    sync_history,
)

logger = logging.getLogger("cashup.dashboard")

DASHBOARD_DIR = Path(__file__).parent
TEMPLATES_DIR = DASHBOARD_DIR / "templates"
STATIC_DIR = DASHBOARD_DIR / "static"

app = FastAPI(title="CashUp Integration", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Página principal do dashboard."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "entities": get_available_entities(),
    })


@app.get("/api/status")
async def api_status():
    """Retorna status atual de todas as entidades."""
    entities = get_available_entities()
    status = {}

    for entity in entities:
        history = sync_history.get(entity, [])
        last = history[0] if history else None

        status[entity] = {
            "last_sync": last,
            "total_executions": len(history),
            "last_status": last.get("status") if last else "never",
            "last_time": last.get("finished_at") if last else None,
        }

    return JSONResponse(content={
        "entities": status,
        "server_time": datetime.now().isoformat(),
    })


@app.post("/api/sync/{entity}")
async def trigger_sync(entity: str, force: bool = False):
    """Dispara sincronização manual de uma entidade.
    Query param ?force=true ignora o ID_SINC e sincroniza tudo.
    """
    if entity == "all":
        results = {}
        for ent in get_available_entities():
            results[ent] = run_sync_manual(ent, force=force)
        return JSONResponse(content={"results": results})

    if entity not in get_available_entities():
        return JSONResponse(
            status_code=400,
            content={"error": f"Entidade desconhecida: {entity}"},
        )

    result = run_sync_manual(entity, force=force)
    return JSONResponse(content={"result": result})


@app.get("/api/history/{entity}")
async def entity_history(entity: str, limit: int = 10):
    """Retorna histórico de execuções de uma entidade."""
    if entity not in get_available_entities():
        return JSONResponse(
            status_code=400,
            content={"error": f"Entidade desconhecida: {entity}"},
        )

    history = sync_history.get(entity, [])
    return JSONResponse(content={
        "entity": entity,
        "history": history[:limit],
    })


_CRM_ENDPOINTS: dict[str, str] = {
    "clientes":           Endpoints.CLIENTES,
    "produtos":           Endpoints.PRODUTOS,
    "estoque":            Endpoints.ESTOQUE,
    "condicoes_pagto":    Endpoints.CONDICOES_PAGTO,
    "naturezas":          Endpoints.NATUREZAS,
    "equipes_comerciais": Endpoints.EQUIPES_COMERCIAIS,
    "tabelas_preco":      Endpoints.TABELAS_PRECO,
    "transportadoras":    Endpoints.TRANSPORTADORAS,
    "fichas_financeiras": Endpoints.FICHAS_FINANCEIRAS,
    "produtos_clientes":  Endpoints.PRODUTOS_CLIENTES,
    "notas_fiscais":      Endpoints.NOTAS_FISCAIS,
    "pedidos_envio":      Endpoints.PEDIDOS,
}


@app.get("/api/crm/endpoints")
async def crm_list_endpoints():
    """Lista todos os endpoints disponíveis na API CashUp."""
    try:
        client = CashUpClient()
        data = client.list_endpoints()
        return JSONResponse(content={"endpoints": data})
    except Exception as e:
        logger.error("Erro ao listar endpoints CashUp: %s", e)
        return JSONResponse(status_code=502, content={"error": str(e)})


@app.get("/api/crm/{entity}")
async def crm_get(entity: str, request: Request):
    """Consulta dados de uma entidade diretamente no CashUp CRM.
    Query params são repassados à API (ex: ?page=1&limit=50).
    """
    if entity not in _CRM_ENDPOINTS:
        return JSONResponse(
            status_code=400,
            content={"error": f"Entidade desconhecida: {entity}"},
        )

    params = dict(request.query_params)

    try:
        client = CashUpClient()
        data = client.get(_CRM_ENDPOINTS[entity], params=params or None)
        return JSONResponse(content={"entity": entity, "data": data})
    except Exception as e:
        logger.error("Erro ao consultar CRM [%s]: %s", entity, e)
        return JSONResponse(
            status_code=502,
            content={"error": str(e)},
        )


@app.get("/api/health")
async def health_check():
    """Health check da aplicação + CashUp API."""
    try:
        client = CashUpClient()
        cashup_health = client.health_check()
    except Exception as e:
        cashup_health = {"status": "error", "error": str(e)}

    return JSONResponse(content={
        "app": {"status": "online", "time": datetime.now().isoformat()},
        "cashup_api": cashup_health,
    })
