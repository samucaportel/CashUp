"""Sincronização de Notas Fiscais — ERP → CashUp (com itens)."""

import logging
from typing import Any

from api.endpoints import Endpoints
from sync.base import BaseSyncService, SyncResult
from config.settings import settings

logger = logging.getLogger("cashup.sync.nfs")


class SyncNotasFiscais(BaseSyncService):
    entity_name = "notas_fiscais"
    query_file = "notas_fiscais.sql"
    api_endpoint = Endpoints.NOTAS_FISCAIS
    api_batch_size = 10  # CashUp tem limitação de volume; envia 10 NFs por chamada

    def transform(self, row: dict[str, Any]) -> dict[str, Any]:
        """Transforma cabeçalho da NF. Itens são adicionados separadamente."""
        def s(key: str) -> str:
            v = row.get(key)
            return "" if v is None else str(v)

        cod_transp = row.get("COD_TRNASPORTADORA") if row.get("COD_TRNASPORTADORA") is not None else row.get("COD_TRANSPORTADORA")
        cod_redespacho = row.get("COD_REDESPACHO") if row.get("COD_REDESPACHO") is not None else row.get("COD_TRANSPORTADORA_REDESPACHO")

        return {
            "NUMERO_NF": s("NUMERO_NF"),
            "SERIE_NF": str(row.get("SERIE_NF") or "0"),
            "CHAVE_NF": s("CHAVE_NF"),
            "COD_CLI": s("COD_CLI"),
            "CNPJ_CLI": s("CNPJ_CLI"),
            "COD_FILIAL": s("COD_FILIAL"),
            "CNPJ_EMIT": s("CNPJ_EMIT"),
            "NRO_PEDIDO": int(row.get("NRO_PEDIDO") or 0) if row.get("NRO_PEDIDO") else None,
            "OBS": s("OBS"),
            "COD_VENDEDOR": s("COD_VENDEDOR"),
            "COD_VENDEDOR2": s("COD_VENDEDOR2"),
            "COD_VENDEDOR3": s("COD_VENDEDOR3"),
            "COD_CONDICAO": s("COD_CONDICAO"),
            "COD_TRANSPORTADORA": "" if cod_transp is None else str(cod_transp),
            "COD_TRANSPORTADORA_REDESPACHO": "" if cod_redespacho is None else str(cod_redespacho),
            "COD_NATUREZA_OP": s("COD_NATUREZA_OP"),
            "NAT_OP": s("NAT_OP"),
            "PEDIDO_CLI": s("PEDIDO_CLI"),
            "TIPO_FRETE": str(row.get("TIPO_FRETE") or "0"),
            "CANCELADA": str(row.get("CANCELADA") or "N"),
            "DEVOLUCAO": str(row.get("DEVOLUCAO") or "N"),
            "AMOSTRA": str(row.get("AMOSTRA") or "N"),
            "DT_EMIS": row.get("DT_EMIS").isoformat() if row.get("DT_EMIS") else None,
            "CANCELAMENTO": row.get("CANCELAMENTO").isoformat() if hasattr(row.get("CANCELAMENTO"), "isoformat") else None,
            "VLR_TOTAL_PRODUTOS": float(row.get("VLR_TOT_PRODUTOS") or row.get("VLR_TOTAL_PRODUTOS") or 0),
            "VLR_TOTAL_NF": float(row.get("VLR_TOT_NF") or row.get("VLR_TOTAL_NF") or 0),
            "VLR_TOTAL_LIQ": float(row.get("VLR_TOTAL_LIQ") or 0),
            "VLR_DESCONTO": float(row.get("VLR_DESCONTO") or 0),
            "VLR_FRETE": float(row.get("VLR_FRETE") or 0),
            "VLR_ICMS": float(row.get("VLR_ICMS") or 0),
            "VLR_ST": float(row.get("VLR_ST") or 0),
            "VLR_IPI": float(row.get("VLR_IPI") or 0),
            "VLR_PIS": float(row.get("VLR_PIS") or 0),
            "VLR_COFINS": float(row.get("VLR_COFINS") or 0),
            "VLR_FCP": float(row.get("VLR_FCP") or 0),
            "VLR_CBS": float(row.get("VLR_CBS") or 0),
            "VLR_IBS": float(row.get("VLR_IBS") or 0),
            "VLR_BC_ICMS": float(row.get("VLR_BC_ICMS") or 0),
            "VLR_BC_ST": float(row.get("VLR_BC_ST") or 0),
            "PESO_BRUTO": float(row.get("PESO_BRUTO") or 0),
            "PESO_LIQ": float(row.get("PESO_LIQ") or 0),
            "ITENS": [],
        }

    def _transform_item(self, row: dict[str, Any]) -> dict[str, Any]:
        """Transforma um item de NF."""
        def s(key: str) -> str:
            v = row.get(key)
            return "" if v is None else str(v)

        return {
            "SEQ": s("SEQ"),
            "COD_PRODUTO": s("COD_PRODUTO"),
            "DESCR_PRODUTO": s("DESCR_PRODUTO"),
            "NRO_PEDIDO": int(row.get("NRO_PEDIDO") or 0) if row.get("NRO_PEDIDO") else None,
            "OBS": s("OBS"),
            "NCM": s("NCM"),
            "COD_BARRAS": s("COD_BARRAS"),
            "CFOP": s("CFOP"),
            "CST_ICMS": s("CST_ICMS"),
            "QUANTIDADE": float(row.get("QUANTIDADE") or 0),
            "PRECO": float(row.get("PRECO") or 0),
            "VLR_TOTAL": float(row.get("VLR_TOTAL") or 0),
            "VLR_TOTAL_ORIGINAL": float(row.get("VLR_TOTAL_ORIGINAL") or 0),
            "VLR_DESCONTO": float(row.get("VLR_DESCONTO") or 0),
            "PERC_COMISSAO": float(row.get("PERC_COMISSAO") or 0),
            "CUSTO_ITEM": float(row.get("CUSTO_ITEM") or 0),
            "VLR_FRETE": float(row.get("VLR_FRETE") or 0),
            "PRECO_LIQ": float(row.get("PRECO_LIQ") or 0),
            "VLR_LIQ": float(row.get("VLR_LIQ") or 0),
            "VLR_ICMS": float(row.get("VLR_ICMS") or 0),
            "VLR_ST": float(row.get("VLR_ST") or 0),
            "VLR_IPI": float(row.get("VLR_IPI") or 0),
            "VLR_PIS": float(row.get("VLR_PIS") or 0),
            "VLR_COFINS": float(row.get("VLR_COFINS") or 0),
            "VLR_FCP": float(row.get("VLR_FCP") or 0),
            "VLR_II": float(row.get("VLR_II") or 0),
            "VLR_SEGURO": float(row.get("VLR_SEGURO") or 0),
            "VLR_DIFAL": float(row.get("VLR_DIFAL") or 0),
            "VLR_CBS": float(row.get("VLR_CBS") or 0),
            "VLR_IBS": float(row.get("VLR_IBS") or 0),
            "PERC_ICMS": float(row.get("PERC_ICMS") or 0),
            "PERC_ST": float(row.get("PERC_ST") or 0),
            "PERC_IPI": float(row.get("PERC_IPI") or 0),
            "PERC_PIS": float(row.get("PERC_PIS") or 0),
            "PERC_COFINS": float(row.get("PERC_COFINS") or 0),
            "PERC_CBS": float(row.get("PERC_CBS") or 0),
            "PERC_IBS": float(row.get("PERC_IBS") or 0),
        }

    def execute(self, **kwargs) -> SyncResult:
        """
        Override do execute para montar NFs com itens.
        Busca cabeçalhos e itens separadamente e combina.
        """
        result = SyncResult(self.entity_name)
        self._last_result = result

        logger.info("=== Iniciando sync: %s ===", self.entity_name)

        try:
            # 1. Pega watermark de ID_SINC (prioriza o que vem via kwargs se existir)
            # Filtro de período (ajuste temporário para testes): ignora o watermark
            # e não atualiza o ID_SINC, retornando apenas NFs no intervalo informado.
            dt_inicio = kwargs.get("dt_inicio")
            dt_fim = kwargs.get("dt_fim")
            periodo_filtro = bool(dt_inicio or dt_fim)

            ultimo_db = 0 if (kwargs.get("force") or periodo_filtro) else self.get_ultimo_id_sinc()
            ultimo_id = kwargs.get("ultimo_id", ultimo_db)
            query_params = {**kwargs, "ultimo_id": ultimo_id}

            # 2. Busca todos os cabeçalhos pendentes
            sql_header, params_header = self.get_query(**query_params)
            sql_header, params_header = self._apply_period_filter(
                sql_header, params_header, "DT_EMIS", dt_inicio, dt_fim
            )
            headers = self.db.execute_query(sql_header, params_header)
            result.total_records = len(headers)

            if not headers:
                result.finish("success")
                logger.info("[%s] Nenhuma NF para sincronizar", self.entity_name)
                return result

            # 3. Processa em lotes (ex: 50 NFs por vez) para evitar estouro de bind variables no Oracle
            batch_size = 50
            for i in range(0, len(headers), batch_size):
                batch_headers = headers[i : i + batch_size]
                nf_numbers = [str(h["NUMERO_NF"]) for h in batch_headers]
                
                # Busca itens para este lote de NFs
                sql_items_raw = self.db.load_query("notas_fiscais_itens.sql", settings.QUERIES_DIR)
                
                # Gera placeholders dinâmicos para a cláusula IN (:h0, :h1, :h2...)
                placeholders = [f":h{idx}" for idx in range(len(nf_numbers))]
                sql_items = sql_items_raw.replace(":nf_numbers", ", ".join(placeholders))
                params_items = {f"h{idx}": val for idx, val in enumerate(nf_numbers)}
                
                items_rows = self.db.execute_query(sql_items, params_items)

                # Agrupa itens por NF (chave composta)
                items_by_nf: dict[str, list] = {}
                for item_row in items_rows:
                    nf_num = str(item_row["NUMERO_NF"])
                    nf_serie = str(item_row.get("SERIE_NF", "0"))
                    key = f"{nf_num}-{nf_serie}"
                    if key not in items_by_nf:
                        items_by_nf[key] = []
                    items_by_nf[key].append(self._transform_item(item_row))

                # Monta registros completos para envio
                batch_records = []
                for header in batch_headers:
                    try:
                        nf = self.transform(header)
                        key = f"{str(header['NUMERO_NF'])}-{str(header.get('SERIE_NF', '0'))}"
                        nf["ITENS"] = items_by_nf.get(key, [])
                        batch_records.append(nf)
                    except Exception as e:
                        result.error_records += 1
                        result.errors.append(f"Transform NF {header.get('NUMERO_NF')}: {e}")

                # Envia o lote atual
                if batch_records:
                    batch_results = self.api.post_batch(self.api_endpoint, batch_records, batch_size=self.api_batch_size)
                    for br in batch_results:
                        if br["status"] == "success":
                            result.sent_records += br["count"]
                        else:
                            result.error_records += br["count"]
                            result.errors.append(br.get("error", "API Error"))

            # 4. Atualiza watermark (maior ID_SINC do lote todo; não atualiza com filtro de período)
            if headers and not periodo_filtro:
                max_id_sinc = max((int(h.get("ID_SINC", 0) or 0) for h in headers), default=0)
                if max_id_sinc > ultimo_id:
                    self.update_ultimo_id_sinc(max_id_sinc)

            status = "success" if result.error_records == 0 else "partial"
            result.finish(status)
            self._save_sync_result(result)
            logger.info(
                "[%s] Sync finalizado: %d NFs enviadas, %d erros",
                self.entity_name, result.sent_records, result.error_records,
            )

        except Exception as e:
            result.errors.append(str(e))
            result.finish("error")
            logger.error("[%s] Sync falhou: %s", self.entity_name, e)

        return result
