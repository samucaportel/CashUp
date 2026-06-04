"""Sincronização de Naturezas de Operação — ERP → CashUp."""

from typing import Any
from api.endpoints import Endpoints
from sync.base import BaseSyncService


class SyncNaturezas(BaseSyncService):
    entity_name = "naturezas"
    query_file = "naturezas.sql"
    api_endpoint = Endpoints.NATUREZAS

    def transform(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "COD_NATUREZA": str(row.get("COD_NATUREZA", "")),
            "DESCR_NATUREZA": row.get("DESCR_NATUREZA"),
            "ATIVA": row.get("ATIVA", "S"),
            "DESCR_NARRATIVA": row.get("DESCR_NARRATIVA"),
            "COD_FILIAL": str(row.get("COD_FILIAL", "")),
        }
