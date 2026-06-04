"""Sincronização de Produtos — ERP → CashUp."""

from typing import Any
from api.endpoints import Endpoints
from sync.base import BaseSyncService


class SyncProdutos(BaseSyncService):
    entity_name = "produtos"
    query_file = "produtos.sql"
    api_endpoint = Endpoints.PRODUTOS

    def transform(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "COD_PRODUTO": str(row.get("COD_PRODUTO", "")),
            "DESCR_PRODUTO": row.get("DESCR_PRODUTO"),
            "UM": row.get("UM"),
            "ATIVO": row.get("ATIVO", "S"),
            "PESO_LIQ": float(row["PESO_LIQ"]) if row.get("PESO_LIQ") else None,
            "PESO_PC": float(row["PESO_PC"]) if row.get("PESO_PC") else None,
            "COD_CLASS_FISCAL": row.get("COD_CLASS_FISCAL"),
            "ORIGEM": row.get("ORIGEM"),
            "COMPLEMENTO": row.get("COMPLEMENTO"),
            "COD_DIVISAO": row.get("COD_DIVISAO"),
            "CUSTO_FINANCEIRO": float(row["CUSTO_FINANCEIRO"]) if row.get("CUSTO_FINANCEIRO") else None,
            "PRECO_ATUAL": float(row["PRECO_ATUAL"]) if row.get("PRECO_ATUAL") else None,
            "MULTIPLO": int(row.get("MULTIPLO", 1)),
            "ACEITA_VENDA_FRACIONADA": row.get("ACEITA_VENDA_FRACIONADA", "N"),
            "COD_PRODUTO_AUXILIAR": row.get("COD_PRODUTO_AUXILIAR"),
            "COD_BARRAS": row.get("COD_BARRAS"),
            "COD_FAMILIA": row.get("COD_FAMILIA"),
        }
