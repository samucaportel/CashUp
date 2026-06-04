"""Sincronização de Fichas Financeiras — ERP → CashUp."""

from typing import Any
from api.endpoints import Endpoints
from sync.base import BaseSyncService


class SyncFichasFinanceiras(BaseSyncService):
    entity_name = "fichas_financeiras"
    query_file = "fichas_financeiras.sql"
    api_endpoint = Endpoints.FICHAS_FINANCEIRAS

    def transform(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "COD_CLI": str(row.get("COD_CLI", "")),
            "CNPJ_CLI": row.get("CNPJ_CLI"),
            "VLR_LIMITE_CONCEDIDO": float(row.get("VLR_LIMITE_CONCEDIDO", 0)),
            "VLR_PED_NAO_FATURADO": float(row.get("VLR_PED_NAO_FATURADO", 0)),
            "VLR_TITULO_ABERTO": float(row.get("VLR_TITULO_ABERTO", 0)),
            "VLR_TOTAL_GASTO": float(row.get("VLR_TOTAL_GASTO", 0)),
            "VLR_LIMITE_DISPONIVEL": float(row.get("VLR_LIMITE_DISPONIVEL", 0)),
            "INADIMPLENTE": row.get("INADIMPLENTE", "N"),
            "DATA_AVALIACAO_CREDITO": row.get("DATA_AVALIACAO_CREDITO").isoformat()[:10] if row.get("DATA_AVALIACAO_CREDITO") else None,
            "NRO_TITULOS_VENCIDOS_HOJE": int(row.get("NRO_TITULOS_VENCIDOS_HOJE") or 0),
            "NRO_DIAS_ATRASO_ATUAL": int(row.get("NRO_DIAS_ATRASO_ATUAL") or 0),
            "NRO_DIAS_MAIOR_ATRASO": int(row.get("NRO_DIAS_MAIOR_ATRASO") or 0),
            "NRO_MEDIA_DIAS_ATRASO": float(row.get("NRO_MEDIA_DIAS_ATRASO") or 0),
            "DATA_ULTIMO_TITULO_PAGO": row.get("DATA_ULTIMO_TITULO_PAGO").isoformat()[:10] if row.get("DATA_ULTIMO_TITULO_PAGO") else None,
        }
