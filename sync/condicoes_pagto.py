"""Sincronização de Condições de Pagamento — ERP → CashUp."""

from typing import Any
from api.endpoints import Endpoints
from sync.base import BaseSyncService


class SyncCondicoesPagto(BaseSyncService):
    entity_name = "condicoes_pagto"
    query_file = "condicoes_pagto.sql"
    api_endpoint = Endpoints.CONDICOES_PAGTO

    def transform(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "COD_COND_PGTO": str(row.get("COD_COND_PGTO", "")),
            "DESCR_COND_PGTO": row.get("DESCR_COND_PGTO"),
            "ATIVA": row.get("ATIVA", "S"),
            "DT_ALTERACAO": row.get("DT_ALTERACAO").isoformat()[:10] if row.get("DT_ALTERACAO") else None,
            "MEDIA_DIAS": float(row.get("MEDIA_DIAS") or 0),
        }
