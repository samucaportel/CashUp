"""Sincronização de Clientes — ERP → CashUp."""

from typing import Any
from api.endpoints import Endpoints
from sync.base import BaseSyncService


class SyncClientes(BaseSyncService):
    entity_name = "clientes"
    query_file = "clientes.sql"
    api_endpoint = Endpoints.CLIENTES

    def transform(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "COD_CLI": str(row.get("COD_CLI", "")),
            "CNPJ_CLI": row.get("CNPJ_CLI"),
            "NOME_CLI": row.get("NOME_CLI"),
            "RAZAO_CLI": row.get("RAZAO_CLI"),
            "IE": row.get("IE"),
            "ENDERECO": row.get("ENDERECO"),
            "NUMERO": row.get("NUMERO"),
            "BAIRRO": row.get("BAIRRO"),
            "COMPLEMENTO": row.get("COMPLEMENTO"),
            "CEP": row.get("CEP"),
            "UF": row.get("UF"),
            "CODCIDADE": row.get("CODCIDADE"),
            "TEL_GERAL": row.get("TEL_GERAL"),
            "EMAIL_GERAL": row.get("EMAIL_GERAL"),
            "SITE": row.get("SITE"),
            "CIDADE": row.get("CIDADE"),
            "ATIVO": row.get("ATIVO", "S"),
            "DT_CRIACAO": row.get("DT_CRIACAO").isoformat() if row.get("DT_CRIACAO") else None,
        }
