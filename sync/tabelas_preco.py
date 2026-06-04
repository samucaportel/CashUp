"""Sincronização de Tabelas de Preço — ERP → CashUp."""

from typing import Any
from api.endpoints import Endpoints
from sync.base import BaseSyncService


class SyncTabelasPreco(BaseSyncService):
    entity_name = "tabelas_preco"
    query_file = "tabelas_preco.sql"
    api_endpoint = Endpoints.TABELAS_PRECO

    def transform(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "COD_TABELA": str(row.get("COD_TABELA", "")),
            "DESCR_TABELA": row.get("DESCR_TABELA"),
            "COD_FILIAL": str(row.get("COD_FILIAL", "")),
            "ATIVA": row.get("ATIVA", "S"),
            "DT_CRIACAO": row.get("DT_CRIACAO").isoformat() if row.get("DT_CRIACAO") else None,
            "DT_INICIO_VIGENCIA": row.get("DT_INICIO_VIGENCIA").isoformat()[:10] if row.get("DT_INICIO_VIGENCIA") else None,
            "DT_FINAL_VIGENCIA": row.get("DT_FINAL_VIGENCIA").isoformat() if row.get("DT_FINAL_VIGENCIA") else None,
            "PRECOS": [],  # Será preenchido com sub-query dos preços
        }
