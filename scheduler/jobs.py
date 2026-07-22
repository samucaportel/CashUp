"""
Agendador de jobs de sincronização com APScheduler.
"""

import logging
import threading
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from api.client import CashUpClient
from config.settings import settings
from db.base import DatabaseConnector

logger = logging.getLogger("cashup.scheduler")

# Registro de resultados das últimas execuções
sync_history: dict[str, list[dict]] = {}
MAX_HISTORY = 50

# Conector de banco compartilhado (singleton). O pool Oracle é criado uma única
# vez e reutilizado por todos os jobs, em vez de recriado a cada execução.
_db_connector: DatabaseConnector | None = None
_db_lock = threading.Lock()


def _create_db_connector() -> DatabaseConnector:
    """Factory para obter o conector de banco correto."""
    if settings.DB_TYPE == "oracle":
        from db.oracle import OracleConnector
        return OracleConnector()
    # Futuramente: firebird, sqlserver
    raise ValueError(f"DB_TYPE não suportado: {settings.DB_TYPE}")


def get_db_connector() -> DatabaseConnector:
    """Retorna o conector compartilhado, criando o pool sob demanda (thread-safe)."""
    global _db_connector
    if _db_connector is None:
        with _db_lock:
            if _db_connector is None:
                conn = _create_db_connector()
                conn.connect()
                _db_connector = conn
    return _db_connector


def shutdown_db() -> None:
    """Fecha o pool compartilhado (chamado no encerramento da aplicação)."""
    global _db_connector
    with _db_lock:
        if _db_connector is not None:
            _db_connector.disconnect()
            _db_connector = None


def _run_sync(entity_name: str, force: bool = False, dt_inicio: str | None = None, dt_fim: str | None = None):
    """Executa a sincronização de uma entidade específica.

    dt_inicio/dt_fim: filtro de período (ajuste temporário para testes),
    suportado apenas por pedidos_envio e notas_fiscais.
    """
    from sync.clientes import SyncClientes
    from sync.produtos import SyncProdutos
    from sync.estoque import SyncEstoque
    from sync.condicoes_pagto import SyncCondicoesPagto
    from sync.naturezas import SyncNaturezas
    from sync.equipes_comerciais import SyncEquipesComerciais
    from sync.tabelas_preco import SyncTabelasPreco
    from sync.transportadoras import SyncTransportadoras
    from sync.fichas_financeiras import SyncFichasFinanceiras
    from sync.produtos_clientes import SyncProdutosClientes
    from sync.notas_fiscais import SyncNotasFiscais
    from sync.pedidos_envio import SyncPedidosEnvio
    from sync.titulos_financeiros import SyncTitulosFinanceiros

    SYNC_MAP = {
        "clientes": SyncClientes,
        "produtos": SyncProdutos,
        "estoque": SyncEstoque,
        "condicoes_pagto": SyncCondicoesPagto,
        "naturezas": SyncNaturezas,
        "equipes_comerciais": SyncEquipesComerciais,
        "tabelas_preco": SyncTabelasPreco,
        "transportadoras": SyncTransportadoras,
        "fichas_financeiras": SyncFichasFinanceiras,
        "produtos_clientes": SyncProdutosClientes,
        "notas_fiscais": SyncNotasFiscais,
        "pedidos_envio": SyncPedidosEnvio,
        "titulos_financeiros": SyncTitulosFinanceiros,
    }

    if entity_name not in SYNC_MAP:
        logger.error("Entidade desconhecida: %s", entity_name)
        return

    logger.info("-> Job agendado executando: %s", entity_name)

    try:
        db = get_db_connector()  # pool compartilhado, não fecha ao fim do job
        api = CashUpClient()

        sync_class = SYNC_MAP[entity_name]
        service = sync_class(db, api)
        result = service.execute(force=force, dt_inicio=dt_inicio, dt_fim=dt_fim)
        result = result.to_dict()

        # Salva no histórico
        if entity_name not in sync_history:
            sync_history[entity_name] = []
        sync_history[entity_name].insert(0, result)
        sync_history[entity_name] = sync_history[entity_name][:MAX_HISTORY]

    except Exception as e:
        logger.error("Job %s falhou: %s", entity_name, e)
        error_result = {
            "entity": entity_name,
            "status": "error",
            "started_at": datetime.now().isoformat(),
            "finished_at": datetime.now().isoformat(),
            "errors": [str(e)],
        }
        if entity_name not in sync_history:
            sync_history[entity_name] = []
        sync_history[entity_name].insert(0, error_result)


def run_sync_manual(entity_name: str, force: bool = False, dt_inicio: str | None = None, dt_fim: str | None = None) -> dict:
    """Executa sync manualmente e retorna resultado."""
    _run_sync(entity_name, force=force, dt_inicio=dt_inicio, dt_fim=dt_fim)
    if entity_name in sync_history and sync_history[entity_name]:
        return sync_history[entity_name][0]
    return {"entity": entity_name, "status": "unknown"}


def get_available_entities() -> list[str]:
    """Retorna lista de entidades disponíveis para sync."""
    return [
        "clientes",
        "produtos",
        "estoque",
        "condicoes_pagto",
        "naturezas",
        "equipes_comerciais",
        "tabelas_preco",
        "transportadoras",
        "fichas_financeiras",
        "produtos_clientes",
        "notas_fiscais",
        "pedidos_envio",
        "titulos_financeiros",
    ]


def create_scheduler() -> BackgroundScheduler:
    """Cria e configura o scheduler com todos os jobs."""
    scheduler = BackgroundScheduler()

    for entity in get_available_entities():
        # Cada entidade tem seu próprio intervalo (camadas por volatilidade).
        interval_minutes = settings.get_sync_interval(entity)

        # Jitter espalha entidades que compartilham o mesmo intervalo para não
        # baterem no banco ao mesmo tempo. Usa até ~1/4 do intervalo (máx 120s).
        jitter_seconds = min(int(interval_minutes * 60 / 4), 120)

        scheduler.add_job(
            _run_sync,
            trigger=IntervalTrigger(minutes=interval_minutes, jitter=jitter_seconds),
            args=[entity],
            id=f"sync_{entity}",
            name=f"Sync {entity}",
            replace_existing=True,
        )
        logger.info(
            "Job agendado: sync_%s (a cada %d min, jitter até %ds)",
            entity, interval_minutes, jitter_seconds,
        )

    return scheduler
