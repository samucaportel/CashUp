"""
Conector Oracle usando python-oracledb com connection pooling.
"""

import logging
from typing import Any

import oracledb

from config.settings import settings
from db.base import DatabaseConnector

logger = logging.getLogger("cashup.db.oracle")


class OracleConnector(DatabaseConnector):
    """Implementação Oracle do DatabaseConnector."""

    def __init__(self):
        self._pool: oracledb.ConnectionPool | None = None
        self._connection: oracledb.Connection | None = None

        # Tenta inicializar o Thick mode (necessário para Oracle 11g e anteriores)
        try:
            oracledb.init_oracle_client()
            logger.info("Oracle Thick mode ativado com sucesso.")
        except Exception as e:
            logger.warning("Thick mode não ativado (pode ser ignorado se Oracle for >= 12.1): %s", e)

    def _get_dsn(self) -> str:
        """Monta o DSN de conexão Oracle."""
        if settings.DB_SERVICE_NAME:
            return oracledb.makedsn(
                settings.DB_HOST,
                settings.DB_PORT,
                service_name=settings.DB_SERVICE_NAME,
            )
        elif settings.DB_SID:
            return oracledb.makedsn(
                settings.DB_HOST,
                settings.DB_PORT,
                sid=settings.DB_SID,
            )
        else:
            return oracledb.makedsn(
                settings.DB_HOST,
                settings.DB_PORT,
                service_name=settings.DB_NAME,
            )

    def connect(self) -> None:
        """Cria connection pool e obtém uma conexão."""
        if self._pool is not None:
            return

        dsn = self._get_dsn()
        try:
            self._pool = oracledb.create_pool(
                user=settings.DB_USER,
                password=settings.DB_PASS,
                dsn=dsn,
                min=1,
                max=10,
                increment=1,
                getmode=oracledb.POOL_GETMODE_WAIT,
            )
            logger.info("Pool Oracle criado com sucesso: %s@%s", settings.DB_USER, dsn)
        except Exception as e:
            logger.error("Erro ao criar pool Oracle: %s", e)
            raise

    def disconnect(self) -> None:
        """Fecha o pool de conexões."""
        if self._pool:
            try:
                self._pool.close(force=True)
                logger.info("Pool Oracle fechado")
            except Exception as e:
                logger.warning("Erro ao fechar pool Oracle: %s", e)
            finally:
                self._pool = None

    def _get_connection(self) -> oracledb.Connection:
        """Obtém uma conexão do pool."""
        if not self._pool:
            self.connect()
        return self._pool.acquire()

    def execute_query(self, sql: str, params: dict | None = None) -> list[dict[str, Any]]:
        """Executa SELECT e retorna lista de dicts."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params or {})
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error("Erro na query Oracle: %s | SQL: %s", e, sql[:200])
            raise
        finally:
            self._pool.release(conn)

    def execute_command(self, sql: str, params: dict | None = None) -> int:
        """Executa INSERT/UPDATE/DELETE e retorna linhas afetadas."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params or {})
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            conn.rollback()
            logger.error("Erro no comando Oracle: %s | SQL: %s", e, sql[:200])
            raise
        finally:
            self._pool.release(conn)

    def is_connected(self) -> bool:
        """Verifica se o pool está ativo."""
        if not self._pool:
            return False
        try:
            conn = self._pool.acquire()
            conn.ping()
            self._pool.release(conn)
            return True
        except Exception:
            return False
