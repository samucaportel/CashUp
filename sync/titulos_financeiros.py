"""Sincronização de Títulos Financeiros (contas a receber) — ERP → CashUp."""

import logging
from typing import Any

from api.endpoints import Endpoints
from sync.base import BaseSyncService, SyncResult

logger = logging.getLogger("cashup.sync.titulos")


class SyncTitulosFinanceiros(BaseSyncService):
    entity_name = "titulos_financeiros"
    query_file = "titulos_financeiros.sql"
    api_endpoint = Endpoints.TITULOS_FINANCEIROS

    def transform(self, row: dict[str, Any]) -> dict[str, Any]:
        def s(key: str) -> str:
            v = row.get(key)
            return "" if v is None else str(v)

        return {
            "COD_CLI": s("COD_CLI"),
            "CNPJ_CLI": row.get("CNPJ_CLI"),
            "NRO_TITULO": s("NRO_TITULO"),
            "COD_FILIAL": row.get("COD_FILIAL"),
            "CNPJ_EMIT": row.get("CNPJ_EMIT"),
            "NUMERO_NF": row.get("NUMERO_NF"),
            "SERIE_NF": row.get("SERIE_NF"),
            "PARCELA": row.get("PARCELA"),
            "VLR_TITULO": float(row.get("VLR_TITULO") or 0),
            "VLR_PAGO": float(row.get("VLR_PAGO") or 0),
            "VLR_PENDENTE": float(row.get("VLR_PENDENTE") or 0),
            "DT_EMIS": row.get("DT_EMIS").isoformat()[:10] if row.get("DT_EMIS") else None,
            "DT_VENC": row.get("DT_VENC").isoformat()[:10] if row.get("DT_VENC") else None,
        }

    def execute(self, **kwargs) -> SyncResult:
        """Agrupa títulos por COD_CLI antes de enviar.
        A API CashUp espera {COD_CLI, CNPJ_CLI, TITULOS: [...]}.
        """
        result = SyncResult(self.entity_name)
        self._last_result = result

        logger.info("=== Iniciando sync: %s ===", self.entity_name)

        try:
            ultimo_id = self._resolve_ultimo_id(**kwargs)
            query_params = {**kwargs, "ultimo_id": ultimo_id}

            sql, params = self.get_query(**query_params)
            rows = self.db.execute_query(sql, params)
            result.total_records = len(rows)

            if not rows:
                result.finish("success")
                logger.info("[%s] Nenhum título para sincronizar", self.entity_name)
                self._save_sync_result(result)
                return result

            # Agrupa títulos por COD_CLI mantendo a ordem de chegada
            clientes: dict[str, dict] = {}
            for row in rows:
                try:
                    titulo = self.transform(row)
                    cod_cli = titulo.pop("COD_CLI")
                    cnpj_cli = titulo.pop("CNPJ_CLI")

                    if cod_cli not in clientes:
                        clientes[cod_cli] = {
                            "COD_CLI": cod_cli,
                            "CNPJ_CLI": cnpj_cli,
                            "TITULOS": [],
                        }
                    clientes[cod_cli]["TITULOS"].append(titulo)
                except Exception as e:
                    result.error_records += 1
                    result.errors.append(f"Transform error: {e} | Row: {row}")
                    logger.warning("[%s] %s", self.entity_name, result.errors[-1])

            records = list(clientes.values())
            logger.info("[%s] %d clientes com títulos para enviar", self.entity_name, len(records))

            batch_results = self.api.post_batch(self.api_endpoint, records, batch_size=self.api_batch_size)
            for br in batch_results:
                if br["status"] == "success":
                    result.sent_records += br["count"]
                else:
                    result.error_records += br["count"]
                    result.errors.append(br.get("error", "API Error"))

            max_id_sinc = max((int(r.get("ID_SINC", 0) or 0) for r in rows), default=0)
            if max_id_sinc > ultimo_id:
                self.update_ultimo_id_sinc(max_id_sinc)

            status = "success" if result.error_records == 0 else "partial"
            result.finish(status)
            self._save_sync_result(result)
            logger.info(
                "[%s] Sync finalizado: %d clientes enviados, %d erros",
                self.entity_name, result.sent_records, result.error_records,
            )

        except Exception as e:
            result.errors.append(str(e))
            result.finish("error")
            logger.error("[%s] Sync falhou: %s", self.entity_name, e)
            self._save_sync_result(result)

        return result
