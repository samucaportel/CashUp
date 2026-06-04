"""Envio de histórico de Pedidos — ERP → CashUp."""

import logging
from typing import Any

from api.endpoints import Endpoints
from sync.base import BaseSyncService, SyncResult
from config.settings import settings

logger = logging.getLogger("cashup.sync.pedidos_envio")


class SyncPedidosEnvio(BaseSyncService):
    entity_name = "pedidos_envio"
    query_file = "pedidos.sql"
    api_endpoint = Endpoints.PEDIDOS
    api_batch_size = 10  # CashUp tem limitação de volume; envia 10 pedidos por chamada

    def transform(self, row: dict[str, Any]) -> dict[str, Any]:
        """Transforma cabeçalho do pedido."""
        def s(key: str) -> str:
            v = row.get(key)
            return "" if v is None else str(v)

        return {
            "NUMERO_PEDIDO": s("NUMERO_PEDIDO"),
            "COD_CLI": s("COD_CLI"),
            "CNPJ_CLI": s("CNPJ_CLI"),
            "COD_FILIAL": s("COD_FILIAL"),
            "CNPJ_EMIT": s("CNPJ_EMIT"),
            "NRO_NF": s("NRO_NF"),
            "NRO_ORCAMENTO_CASHUP": s("NRO_ORCAMENTO_CASHUP"),
            "STATUS_PEDIDO": s("STATUS_PEDIDO"),
            "DESCR_STATUS_PEDIDO": s("DESCR_STATUS_PEDIDO"),
            "OBS": s("OBS"),
            "COD_VENDEDOR": s("COD_VENDEDOR"),
            "COD_VENDEDOR2": s("COD_VENDEDOR2"),
            "COD_VENDEDOR3": s("COD_VENDEDOR3"),
            "COD_CONDICAO": s("COD_CONDICAO"),
            "COD_TRANSPORTADORA": s("COD_TRANSPORTADORA"),
            "COD_TRANSPORTADORA_REDESPACHO": s("COD_TRANSPORTADORA_REDESPACHO"),
            "COD_NATUREZA_OP": s("COD_NATUREZA_OP"),
            "NAT_OP": s("NAT_OP"),
            "COD_BANCO": s("COD_BANCO"),
            "COD_FORMAPGTO": s("COD_FORMAPGTO"),
            "COD_ETAPA": s("COD_ETAPA"),
            "DESCR_ETAPA": s("DESCR_ETAPA"),
            "PEDIDO_CLI": s("PEDIDO_CLI"),
            "TIPO_FRETE": str(row.get("TIPO_FRETE") or "0"),
            "DT_INS": row.get("DT_INS").isoformat() if row.get("DT_INS") else None,
            "DT_ALTERACAO": row.get("DT_ALTERACAO").isoformat() if row.get("DT_ALTERACAO") else None,
            "VLR_TOTAL": float(row.get("VLR_TOTAL") or 0),
            "VLR_TOTAL_PRODUTOS": float(row.get("VLR_TOTAL_PRODUTOS") or 0),
            "VLR_TOTAL_LIQ": float(row.get("VLR_TOTAL_LIQ") or 0),
            "VLR_DESCONTO": float(row.get("VLR_DESCONTO") or 0),
            "VLR_FRETE": float(row.get("VLR_FRETE") or 0),
            "VLR_COMISSAO": float(row.get("VLR_COMISSAO") or 0),
            "VLR_ICMS": float(row.get("VLR_ICMS") or 0),
            "VLR_ST": float(row.get("VLR_ST") or 0),
            "VLR_IPI": float(row.get("VLR_IPI") or 0),
            "VLR_PIS": float(row.get("VLR_PIS") or 0),
            "VLR_COFINS": float(row.get("VLR_COFINS") or 0),
            "ITENS": [],
        }

    def _transform_item(self, row: dict[str, Any]) -> dict[str, Any]:
        """Transforma um item de pedido."""
        def s(key: str) -> str:
            v = row.get(key)
            return "" if v is None else str(v)

        return {
            "SEQ": s("SEQ"),
            "COD_PRODUTO": s("COD_PRODUTO"),
            "DESCR_PRODUTO": s("DESCR_PRODUTO"),
            "OBS": s("OBS"),
            "COD_NATUREZA_OP": s("COD_NATUREZA_OP"),
            "NRO_NF": s("NRO_NF"),
            "COD_TABELA": s("COD_TABELA"),
            "COD_ITEM_CLIENTE": s("COD_ITEM_CLIENTE"),
            "STATUS_ITEM": s("STATUS_ITEM"),
            "DESCR_STATUS_ITEM": s("DESCR_STATUS_ITEM"),
            "QUANTIDADE": float(row.get("QUANTIDADE") or 0),
            "QTD_FAT": float(row.get("QTD_FAT") or 0),
            "PRECO": float(row.get("PRECO", row.get("PRECO_UNITARIO", 0)) or 0),
            "VLR_TOTAL": float(row.get("VLR_TOTAL") or 0),
            "VLR_TOTAL_ORIGINAL": float(row.get("VLR_TOTAL_ORIGINAL") or 0),
            "VLR_DESCONTO": float(row.get("VLR_DESCONTO") or 0),
            "PERC_COMISSAO": float(row.get("PERC_COMISSAO") or 0),
            "VLR_FRETE": float(row.get("VLR_FRETE") or 0),
            "PRECO_LIQ": float(row.get("PRECO_LIQ") or 0),
            "VLR_LIQ": float(row.get("VLR_LIQ", row.get("VLR_LIQUIDO", 0)) or 0),
            "VLR_ICMS": float(row.get("VLR_ICMS") or 0),
            "VLR_ST": float(row.get("VLR_ST") or 0),
            "VLR_IPI": float(row.get("VLR_IPI") or 0),
            "VLR_PIS": float(row.get("VLR_PIS") or 0),
            "VLR_COFINS": float(row.get("VLR_COFINS") or 0),
            "VLR_FCP": float(row.get("VLR_FCP") or 0),
            "DT_PREVISTA_FAT": row.get("DT_PREVISTA_FAT").isoformat() if hasattr(row.get("DT_PREVISTA_FAT"), "isoformat") else (row.get("DT_PREVISTA_FAT") if row.get("DT_PREVISTA_FAT") else None),
        }

    def execute(self, **kwargs) -> SyncResult:
        """
        Override do execute para montar Pedidos com itens.
        Busca cabeçalhos e itens separadamente e combina.
        """
        result = SyncResult(self.entity_name)
        self._last_result = result

        logger.info("=== Iniciando sync: %s ===", self.entity_name)

        try:
            # 1. Pega watermark de ID_SINC (prioriza o que vem via kwargs se existir)
            ultimo_db = self.get_ultimo_id_sinc()
            ultimo_id = kwargs.get("ultimo_id", ultimo_db)
            query_params = {**kwargs, "ultimo_id": ultimo_id}

            # 2. Busca todos os cabeçalhos pendentes
            sql_header, params_header = self.get_query(**query_params)
            headers = self.db.execute_query(sql_header, params_header)
            result.total_records = len(headers)

            if not headers:
                result.finish("success")
                logger.info("[%s] Nenhum pedido para sincronizar", self.entity_name)
                self._save_sync_result(result)
                return result

            # 3. Processa em lotes (ex: 50 Pedidos por vez) para evitar limites de IN clause no Oracle
            batch_size = 50
            for i in range(0, len(headers), batch_size):
                batch_headers = headers[i : i + batch_size]
                pedido_numbers = [str(h["NUMERO_PEDIDO"]) for h in batch_headers]
                
                # Busca itens para este lote de Pedidos
                sql_items_raw = self.db.load_query("pedidos_itens.sql", settings.QUERIES_DIR)
                
                # Gera placeholders dinâmicos para a cláusula IN (:p0, :p1, :p2...)
                placeholders = [f":p{idx}" for idx in range(len(pedido_numbers))]
                sql_items = sql_items_raw.replace(":pedido_numbers", ", ".join(placeholders))
                params_items = {f"p{idx}": val for idx, val in enumerate(pedido_numbers)}
                
                items_rows = self.db.execute_query(sql_items, params_items)

                # Agrupa itens por pedido (chave composta numero-filial)
                logger.info("[%s] Itens encontrados para o lote %d: %d", self.entity_name, i // batch_size + 1, len(items_rows))
                items_by_pedido: dict[str, list] = {}
                for item_row in items_rows:
                    ped_num = str(int(item_row["NUMERO_PEDIDO"]))
                    v_filial = item_row.get("COD_FILIAL")
                    ped_filial = "" if v_filial is None else str(v_filial)
                    key = f"{ped_num}-{ped_filial}"
                    if key not in items_by_pedido:
                        items_by_pedido[key] = []
                    items_by_pedido[key].append(self._transform_item(item_row))

                # Monta registros completos para envio
                batch_records = []
                for header in batch_headers:
                    try:
                        pedido = self.transform(header)
                        v_filial = header.get("COD_FILIAL")
                        ped_filial = "" if v_filial is None else str(v_filial)
                        key = f"{str(header['NUMERO_PEDIDO'])}-{ped_filial}"
                        pedido["ITENS"] = items_by_pedido.get(key, [])
                        logger.info("[%s] Pedido %s -> %d itens (chave=%s)", self.entity_name, header['NUMERO_PEDIDO'], len(pedido["ITENS"]), key)
                        if not pedido["ITENS"]:
                            logger.warning("[%s] Pedido %s sem itens. Chaves disponíveis: %s", self.entity_name, header['NUMERO_PEDIDO'], list(items_by_pedido.keys())[:5])
                        batch_records.append(pedido)
                    except Exception as e:
                        result.error_records += 1
                        err_msg = f"Transform Pedido {header.get('NUMERO_PEDIDO')}: {e}"
                        result.errors.append(err_msg)
                        logger.warning("[%s] %s", self.entity_name, err_msg)

                # Envia o lote atual
                if batch_records:
                    batch_results = self.api.post_batch(self.api_endpoint, batch_records, batch_size=self.api_batch_size)
                    for br in batch_results:
                        if br["status"] == "success":
                            result.sent_records += br["count"]
                        else:
                            result.error_records += br["count"]
                            result.errors.append(br.get("error", "API Error"))

            # 4. Atualiza watermark
            if headers:
                max_id_sinc = max((int(h.get("ID_SINC", 0) or 0) for h in headers), default=0)
                if max_id_sinc > ultimo_id:
                    self.update_ultimo_id_sinc(max_id_sinc)

            status = "success" if result.error_records == 0 else "partial"
            result.finish(status)
            self._save_sync_result(result)
            logger.info(
                "[%s] Sync finalizado: %d Pedidos enviados, %d erros",
                self.entity_name, result.sent_records, result.error_records,
            )

        except Exception as e:
            result.errors.append(str(e))
            result.finish("error")
            logger.error("[%s] Sync falhou: %s", self.entity_name, e)
            self._save_sync_result(result)

        return result
