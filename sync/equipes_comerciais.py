"""Sincronização de Equipes Comerciais — ERP → CashUp."""

from typing import Any
from api.endpoints import Endpoints
from sync.base import BaseSyncService


class SyncEquipesComerciais(BaseSyncService):
    entity_name = "equipes_comerciais"
    query_file = "equipes_comerciais.sql"
    api_endpoint = Endpoints.EQUIPES_COMERCIAIS

    def transform(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "COD_CLI": str(row.get("COD_CLI", "")),
            "COD_USUARIO": str(row.get("COD_USUARIO", "")),
        }
