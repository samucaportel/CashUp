"""
Classe base para serviços de sincronização ERP → CashUp.
Cada entidade herda desta classe e implementa query + transformação.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from api.client import CashUpClient
from db.base import DatabaseConnector
from config.settings import settings

logger = logging.getLogger("cashup.sync")


class SyncResult:
    """Resultado de uma execução de sync."""

    def __init__(self, entity: str):
        self.entity = entity
        self.started_at: datetime = datetime.now()
        self.finished_at: datetime | None = None
        self.total_records: int = 0
        self.sent_records: int = 0
        self.error_records: int = 0
        self.errors: list[str] = []
        self.status: str = "running"

    def finish(self, status: str = "success"):
        self.finished_at = datetime.now()
        self.status = status

    @property
    def duration_seconds(self) -> float:
        end = self.finished_at or datetime.now()
        return (end - self.started_at).total_seconds()

    def to_dict(self) -> dict:
        return {
            "entity": self.entity,
            "status": self.status,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration_seconds": round(self.duration_seconds, 2),
            "total_records": self.total_records,
            "sent_records": self.sent_records,
            "error_records": self.error_records,
            "errors": self.errors,  # Retorna todos os erros no dict (o log filtra se necessário)
        }


class BaseSyncService(ABC):
    """
    Serviço base de sincronização.
    
    Fluxo:
    1. Carrega query SQL do arquivo
    2. Executa no banco ERP
    3. Transforma cada registro para o formato CashUp
    4. Envia em batches via API
    5. Registra resultado
    """

    entity_name: str = ""
    query_file: str = ""
    api_endpoint: str = ""
    api_batch_size: int | None = None  # Se definido, sobrescreve SYNC_BATCH_SIZE para esta entidade

    def __init__(self, db: DatabaseConnector, api_client: CashUpClient):
        self.db = db
        self.api = api_client
        self._last_result: SyncResult | None = None

    @property
    def last_result(self) -> SyncResult | None:
        return self._last_result

    def get_query(self, **params) -> tuple[str, dict]:
        """Carrega SQL do arquivo e filtra (sql, params)."""
        sql = self.db.load_query(self.query_file, settings.QUERIES_DIR)
        
        # Filtra os parametros para enviar apenas os que existem na query via bind variable :key
        # Usamos regex para encontrar :nome_da_variavel (seguido de fim de linha, espaco, parenteses, virgula ou operador)
        import re
        filtered_params = {}
        for k, v in params.items():
            pattern = rf":{k}\b" # \b garante o limite da palavra (ex: :id não casa :id_sinc)
            if re.search(pattern, sql, re.IGNORECASE):
                filtered_params[k] = v
                
        return sql, filtered_params

    def _apply_period_filter(
        self, sql: str, params: dict, column: str, dt_inicio: str | None, dt_fim: str | None
    ) -> tuple[str, dict]:
        """Adiciona filtro opcional de período (ajuste temporário para testes).

        dt_inicio/dt_fim no formato 'YYYY-MM-DD'. Quando informados, filtra a
        query pela coluna de data indicada.
        """
        if dt_inicio:
            sql += f"\nAND {column} >= TO_DATE(:dt_inicio, 'YYYY-MM-DD')"
            params["dt_inicio"] = dt_inicio
        if dt_fim:
            sql += f"\nAND {column} < TO_DATE(:dt_fim, 'YYYY-MM-DD') + 1"
            params["dt_fim"] = dt_fim
        return sql, params

    @abstractmethod
    def transform(self, row: dict[str, Any]) -> dict[str, Any]:
        """Transforma uma linha do banco para o formato JSON do CashUp."""
        ...

    def pre_sync(self, **kwargs) -> dict:
        """Hook para preparação antes do sync. Retorna params extras para a query."""
        return {}

    def get_ultimo_id_sinc(self) -> int:
        """Busca o último ID_SINC sincronizado com sucesso para esta entidade."""
        sql = "SELECT ULTIMO_ID_SINC FROM CASHUP_CONTROLE_SINC WHERE ENTIDADE = :entity"
        try:
            res = self.db.execute_query(sql, {"entity": self.entity_name})
            return int(res[0]["ULTIMO_ID_SINC"]) if res else 0
        except Exception as e:
            logger.warning("Falha ao ler CASHUP_CONTROLE_SINC (assumindo 0): %s", e)
            return 0

    def update_ultimo_id_sinc(self, new_id: int) -> None:
        """Atualiza a tabela de controle com o maior ID_SINC processado."""
        sql = """
        MERGE INTO CASHUP_CONTROLE_SINC t
        USING (SELECT :entity AS ENTIDADE, :new_id AS ULTIMO_ID_SINC FROM DUAL) s
        ON (t.ENTIDADE = s.ENTIDADE)
        WHEN MATCHED THEN 
            UPDATE SET t.ULTIMO_ID_SINC = s.ULTIMO_ID_SINC
        WHEN NOT MATCHED THEN 
            INSERT (ENTIDADE, ULTIMO_ID_SINC) VALUES (s.ENTIDADE, s.ULTIMO_ID_SINC)
        """
        try:
            self.db.execute_command(sql, {"entity": self.entity_name, "new_id": new_id})
        except Exception as e:
            logger.error("Erro ao atualizar CASHUP_CONTROLE_SINC para %s: %s", self.entity_name, e)

    def post_sync(self, result: SyncResult) -> None:
        """Hook para ações após o sync (ex: atualizar dt_ultima_sync)."""
        pass

    def execute(self, **kwargs) -> SyncResult:
        """Executa o ciclo completo de sincronização."""
        result = SyncResult(self.entity_name)
        self._last_result = result

        logger.info("=== Iniciando sync: %s ===", self.entity_name)

        try:
            # 1. Pega watermark de ID_SINC (force=True ignora e usa 0)
            force = kwargs.get("force", False)
            ultimo_id = 0 if force else self.get_ultimo_id_sinc()
            if force:
                logger.info("[%s] Modo forçado: ignorando ID_SINC, sincronizando tudo", self.entity_name)

            # Preparação
            extra_params = self.pre_sync(**kwargs)
            query_params = {**kwargs, **extra_params, "ultimo_id": ultimo_id}

            # Busca dados no ERP
            sql, params = self.get_query(**query_params)
            logger.debug("[%s] Query params: %s", self.entity_name, params)
            rows = self.db.execute_query(sql, params)
            result.total_records = len(rows)

            # Extrai o maior ID_SINC retornado para atualizar o tracking no final
            max_id_sinc = 0
            if rows:
                max_id_sinc = max((int(row.get("ID_SINC", 0) or 0) for row in rows), default=0)

            logger.info("[%s] %d registros encontrados no ERP", self.entity_name, len(rows))

            if not rows:
                result.finish("success")
                logger.info("[%s] Nenhum registro para sincronizar", self.entity_name)
                self._save_sync_result(result)
                return result

            # Transforma dados
            records = []
            for row in rows:
                try:
                    transformed = self.transform(row)
                    if transformed:
                        records.append(transformed)
                except Exception as e:
                    result.error_records += 1
                    err_msg = f"Transform error: {e} | Row: {row}"
                    result.errors.append(err_msg)
                    logger.warning("[%s] %s", self.entity_name, err_msg)

            # Envia para CashUp
            if records:
                batch_results = self.api.post_batch(self.api_endpoint, records, batch_size=self.api_batch_size)
                for br in batch_results:
                    if br["status"] == "success":
                        result.sent_records += br["count"]
                    else:
                        result.error_records += br["count"]
                        result.errors.append(br.get("error", "Unknown error"))

            # Finaliza
            status = "success" if result.error_records == 0 else "partial"
            result.finish(status)
            
            # Atualiza o controle do ID_SINC para a próxima rodada
            if max_id_sinc > ultimo_id:
                self.update_ultimo_id_sinc(max_id_sinc)
                
            self.post_sync(result)
            self._save_sync_result(result)

            logger.info(
                "[%s] Sync finalizado: %d enviados, %d erros em %.2fs",
                self.entity_name, result.sent_records, result.error_records, result.duration_seconds,
            )

        except Exception as e:
            result.errors.append(str(e))
            result.finish("error")
            logger.error("[%s] Sync falhou: %s", self.entity_name, e)
            self._save_sync_result(result)

        return result

    def _save_sync_result(self, result: SyncResult) -> None:
        """Salva o resultado do sync em um arquivo JSON para auditoria."""
        import json
        import os
        
        results_dir = os.path.join("logs", "results")
        os.makedirs(results_dir, exist_ok=True)
        
        filename = f"sync_{self.entity_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(results_dir, filename)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(result.to_dict(), f, indent=4, ensure_ascii=False)
            logger.info("[%s] Resultado do sync salvo em %s", self.entity_name, filepath)
        except Exception as e:
            logger.error("[%s] Falha ao salvar resultado do sync: %s", self.entity_name, e)
