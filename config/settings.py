"""
Módulo de configuração — lê variáveis de ambiente do arquivo .env
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega .env da raiz do projeto
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)


class Settings:
    """Configurações centralizadas da aplicação."""

    # CashUp API
    CASHUP_BASE_URL: str = os.getenv("CASHUP_BASE_URL", "http://localhost:3000")
    CASHUP_CLIENT_ID: str = os.getenv("CASHUP_CLIENT_ID", "")
    CASHUP_CLIENT_SECRET: str = os.getenv("CASHUP_CLIENT_SECRET", "")

    # Database
    DB_TYPE: str = os.getenv("DB_TYPE", "oracle")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "1521"))
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASS: str = os.getenv("DB_PASS", "")
    DB_NAME: str = os.getenv("DB_NAME", "")
    DB_SERVICE_NAME: str = os.getenv("DB_SERVICE_NAME", "")
    DB_SID: str = os.getenv("DB_SID", "")

    # Sync
    SYNC_BATCH_SIZE: int = int(os.getenv("SYNC_BATCH_SIZE", "50"))
    SYNC_INTERVAL_MINUTES: int = int(os.getenv("SYNC_INTERVAL_MINUTES", "30"))
    DEBUG_SAVE_PAYLOADS: bool = os.getenv("DEBUG_SAVE_PAYLOADS", "false").lower() == "true"

    # Application
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    LOG_DIR: Path = BASE_DIR / "logs"
    QUERIES_DIR: Path = BASE_DIR / "db" / "queries"

    def __init__(self):
        self.LOG_DIR.mkdir(exist_ok=True)

    def validate(self) -> list[str]:
        """Retorna lista de erros de validação."""
        errors = []
        if not self.CASHUP_CLIENT_ID:
            errors.append("CASHUP_CLIENT_ID não configurado")
        if not self.CASHUP_CLIENT_SECRET:
            errors.append("CASHUP_CLIENT_SECRET não configurado")
        if not self.CASHUP_BASE_URL:
            errors.append("CASHUP_BASE_URL não configurado")
        if self.DB_TYPE == "oracle" and not (self.DB_SERVICE_NAME or self.DB_SID or self.DB_NAME):
            errors.append("Configuração Oracle incompleta: DB_SERVICE_NAME, DB_SID ou DB_NAME necessário")
        return errors


settings = Settings()
