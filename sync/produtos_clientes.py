"""Sincronização de Produtos do Cliente — ERP → CashUp."""

from typing import Any
from api.endpoints import Endpoints
from sync.base import BaseSyncService


class SyncProdutosClientes(BaseSyncService):
    entity_name = "produtos_clientes"
    query_file = "produtos_clientes.sql"
    api_endpoint = Endpoints.PRODUTOS_CLIENTES

    def transform(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "COD_CLI": str(row.get("COD_CLI", "")),
            "CNPJ_CLI": row.get("CNPJ_CLI"),
            "COD_PRODUTO": str(row.get("COD_PRODUTO", "")),
            "COD_PRODUTO_CLI": row.get("COD_PRODUTO_CLI"),
            "DESCR_PRODUTO_CLI": row.get("DESCR_PRODUTO_CLI"),
            "PRECO_PRODUTO_CLI": float(row.get("PRECO_PRODUTO_CLI", 0)),
            "CUSTO_PRODUTO_CLI": float(row.get("CUSTO_PRODUTO_CLI", 0)),
        }
