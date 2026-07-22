"""Sincronização de Estoque — ERP → CashUp (com lotes)."""

import logging
from typing import Any

from api.endpoints import Endpoints
from sync.base import BaseSyncService, SyncResult

logger = logging.getLogger("cashup.sync.estoque")


class SyncEstoque(BaseSyncService):
    entity_name = "estoque"
    query_file = "estoque.sql"
    api_endpoint = Endpoints.ESTOQUE
    api_batch_size = 10

    def transform(self, row: dict[str, Any]) -> dict[str, Any]:
        """Transforma campos do produto (cabeçalho). LOTES é preenchido no execute."""
        return {
            "COD_FILIAL": str(row.get("COD_FILIAL", "")),
            "COD_PROD": str(row.get("COD_PROD", "")),
            "CNPJ_FILIAL": row.get("CNPJ_FILIAL"),
            "LOCAL": row.get("LOCAL"),
            "QTD_FISICO": float(row.get("QTD_FISICO") or 0),
            "QTD_FUTURO": float(row.get("QTD_FUTURO") or 0),
            "QTD_FATURAR": float(row.get("QTD_FATURAR") or 0),
            "PRECO_VENDA": float(row.get("PRECO_VENDA") or 0),
            "PRECO_COMPRA": float(row.get("PRECO_COMPRA") or 0),
            "SALDO_LOCAL": float(row.get("SALDO_LOCAL") or 0),
            "QTDE_ULTIMA_ENTRADA": float(row.get("QTDE_ULTIMA_ENTRADA") or 0),
            "DT_CRIACAO": row.get("DT_CRIACAO").isoformat()[:10] if row.get("DT_CRIACAO") else None,
            "DT_ALTERACAO": row.get("DT_ALTERACAO").isoformat()[:10] if row.get("DT_ALTERACAO") else None,
            "LOTES": [],
        }

    def _transform_lote(self, row: dict[str, Any]) -> dict[str, Any] | None:
        """Transforma campos de lote. Retorna None se a linha não tiver lote."""
        if not row.get("COD_LOTE"):
            return None
        return {
            "COD_LOTE": str(row.get("COD_LOTE", "")),
            "DESCRICAO_LOTE": row.get("DESCRICAO_LOTE"),
            "DT_VALIDADE": row.get("DT_VALIDADE").isoformat()[:10] if row.get("DT_VALIDADE") else None,
            "DT_FABRICACAO": row.get("DT_FABRICACAO").isoformat()[:10] if row.get("DT_FABRICACAO") else None,
            # A view entrega uma linha por lote; a quantidade do lote está em
            # QTD_FISICO (não há coluna QTD_*_LOTE nesta view). DESCRICAO_LOTE,
            # DT_VALIDADE, DT_FABRICACAO e QTD_RESERVA não têm coluna de origem.
            "QTD_FISICO": float(row.get("QTD_FISICO") or 0),
            "QTD_RESERVA": float(row.get("QTD_RESERVA") or 0),
        }

    def execute(self, **kwargs) -> SyncResult:
        """Agrupa linhas por (COD_FILIAL, COD_PROD) e anexa LOTES antes de enviar."""
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
                logger.info("[%s] Nenhum registro para sincronizar", self.entity_name)
                self._save_sync_result(result)
                return result

            # Agrupa por (COD_FILIAL, COD_PROD). Cada linha da view é um lote:
            # o cabeçalho (identidade/preços) vem da 1ª linha, e as quantidades
            # do produto são SOMADAS entre os lotes.
            AGG = ("QTD_FISICO", "QTD_FUTURO", "QTD_FATURAR", "SALDO_LOCAL")
            produtos: dict[str, dict] = {}
            for row in rows:
                try:
                    key = f"{row.get('COD_FILIAL')}|{row.get('COD_PROD')}"
                    if key not in produtos:
                        produtos[key] = self.transform(row)
                        for campo in AGG:
                            produtos[key][campo] = 0.0  # zera para somar entre os lotes
                    prod = produtos[key]
                    for campo in AGG:
                        prod[campo] += float(row.get(campo) or 0)
                    lote = self._transform_lote(row)
                    if lote:
                        prod["LOTES"].append(lote)
                except Exception as e:
                    result.error_records += 1
                    result.errors.append(f"Transform error: {e} | Row: {row}")
                    logger.warning("[%s] %s", self.entity_name, result.errors[-1])

            records = list(produtos.values())
            logger.info("[%s] %d produtos para enviar", self.entity_name, len(records))

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
                "[%s] Sync finalizado: %d produtos enviados, %d erros",
                self.entity_name, result.sent_records, result.error_records,
            )

        except Exception as e:
            result.errors.append(str(e))
            result.finish("error")
            logger.error("[%s] Sync falhou: %s", self.entity_name, e)
            self._save_sync_result(result)

        return result
