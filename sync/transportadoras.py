"""Sincronização de Transportadoras — ERP → CashUp."""

from typing import Any
from api.endpoints import Endpoints
from sync.base import BaseSyncService


class SyncTransportadoras(BaseSyncService):
    entity_name = "transportadoras"
    query_file = "transportadoras.sql"
    api_endpoint = Endpoints.TRANSPORTADORAS

    def transform(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "COD_TRANSP": str(row.get("COD_TRANSP", "")),
            "NOME_TRANSP": row.get("NOME_TRANSP"),
            "CNPJ_TRANSP": row.get("CNPJ_TRANSP"),
            "IE_TRANSP": row.get("IE_TRANSP"),
            "END_TRANSP": row.get("END_TRANSP"),
            "BAIRRO_TRANSP": row.get("BAIRRO_TRANSP"),
            "CEP_TRANSP": row.get("CEP_TRANSP"),
            "CID_TRANSP": row.get("CID_TRANSP"),
            "UF_TRANSP": row.get("UF_TRANSP"),
            "ATIVA": row.get("ATIVA", "S"),
            "DT_CRIACAO": row.get("DT_CRIACAO").isoformat()[:10] if row.get("DT_CRIACAO") else None,
            "DT_ALTERACAO": row.get("DT_ALTERACAO").isoformat()[:10] if row.get("DT_ALTERACAO") else None,
        }
