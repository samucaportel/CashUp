"""
Entry point — Inicia FastAPI + APScheduler.
"""

import logging
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from config.settings import settings

# ─── Logging ────────────────────────────────────────────

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            settings.LOG_DIR / "sync.log",
            encoding="utf-8",
        ),
    ],
)

logger = logging.getLogger("cashup")


def main():
    """Função principal — inicia dashboard e scheduler."""
    import uvicorn
    from dashboard.app import app
    from scheduler.jobs import create_scheduler

    # Valida configuração
    errors = settings.validate()
    if errors:
        logger.warning("Avisos de configuração:")
        for err in errors:
            logger.warning("  ! %s", err)
        logger.warning("Configure o arquivo .env antes de usar a sincronização.")

    # Inicia scheduler
    scheduler = create_scheduler()
    scheduler.start()
    logger.info("-----------------------------------------------")
    logger.info("  CashUp Integration v1.0")
    logger.info("  Dashboard: http://%s:%d", settings.APP_HOST, settings.APP_PORT)
    logger.info("  Intervalo de sync: %d minutos", settings.SYNC_INTERVAL_MINUTES)
    logger.info("  DB Type: %s", settings.DB_TYPE)
    logger.info("-----------------------------------------------")

    # Inicia FastAPI
    try:
        uvicorn.run(
            app,
            host=settings.APP_HOST,
            port=settings.APP_PORT,
            log_level=settings.LOG_LEVEL.lower(),
        )
    except KeyboardInterrupt:
        logger.info("Encerrando...")
    finally:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler encerrado")


if __name__ == "__main__":
    main()
