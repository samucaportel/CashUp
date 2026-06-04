"""
Cliente HTTP para a API CashUp REST v4.
Gerencia autenticação (token Bearer com auto-refresh), retry e batching.
"""

import logging
import time
from datetime import datetime, timedelta

import requests

from api.endpoints import Endpoints
from config.settings import settings

logger = logging.getLogger("cashup.api.client")


class CashUpClient:
    """Cliente para a API REST do CashUp com gerenciamento automático de token."""

    TOKEN_MARGIN_SECONDS = 60  # Renova token 1 min antes de expirar

    def __init__(self):
        self.base_url = settings.CASHUP_BASE_URL.rstrip("/")
        self.client_id = settings.CASHUP_CLIENT_ID
        self.client_secret = settings.CASHUP_CLIENT_SECRET
        self.batch_size = settings.SYNC_BATCH_SIZE

        self._access_token: str | None = None
        self._token_expires_at: datetime | None = None

        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})

    # ─── Autenticação ───────────────────────────────────────────

    def _is_token_valid(self) -> bool:
        """Verifica se o token atual ainda é válido."""
        if not self._access_token or not self._token_expires_at:
            return False
        return datetime.now() < (self._token_expires_at - timedelta(seconds=self.TOKEN_MARGIN_SECONDS))

    def _authenticate(self) -> None:
        """Obtém novo token via client_credentials."""
        url = f"{self.base_url}{Endpoints.AUTH_TOKEN}"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }

        logger.info("Solicitando novo token CashUp...")
        try:
            resp = requests.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            self._access_token = data["access_token"]
            # Token expira em 15 min; guardamos o momento de expiração
            expires_in = data.get("expires_in", 900)
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in)

            self._session.headers.update({"Authorization": f"Bearer {self._access_token}"})
            logger.info("Token obtido com sucesso. Expira em %d segundos", expires_in)

        except requests.exceptions.RequestException as e:
            logger.error("Falha na autenticação CashUp: %s", e)
            raise

    def _ensure_auth(self) -> None:
        """Garante que temos um token válido."""
        if not self._is_token_valid():
            self._authenticate()

    # ─── Métodos HTTP ───────────────────────────────────────────

    def get(self, endpoint: str, params: dict | None = None, max_retries: int = 3) -> dict | list:
        """GET com retry e auto-refresh de token."""
        self._ensure_auth()
        url = f"{self.base_url}{endpoint}"

        for attempt in range(1, max_retries + 1):
            try:
                resp = self._session.get(url, params=params, timeout=60)

                if resp.status_code == 401:
                    logger.warning("Token expirado, renovando... (tentativa %d)", attempt)
                    self._authenticate()
                    resp = self._session.get(url, params=params, timeout=60)

                resp.raise_for_status()
                return resp.json()

            except requests.exceptions.RequestException as e:
                logger.warning("GET %s falhou (tentativa %d/%d): %s", endpoint, attempt, max_retries, e)
                if attempt == max_retries:
                    raise
                time.sleep(2 ** attempt)

    def _save_payload_debug(self, endpoint: str, data: dict | list) -> None:
        """Salva payload em logs/payloads/ quando DEBUG_SAVE_PAYLOADS=true."""
        import json, os
        from datetime import datetime
        payloads_dir = os.path.join("logs", "payloads")
        os.makedirs(payloads_dir, exist_ok=True)
        entity = endpoint.rstrip("/").split("/")[-1]
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]
        filepath = os.path.join(payloads_dir, f"{entity}_{ts}.json")
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.debug("Payload salvo: %s", filepath)
        except Exception as e:
            logger.warning("Falha ao salvar payload debug: %s", e)

    def post(self, endpoint: str, data: dict | list, max_retries: int = 3) -> dict:
        """POST com retry e auto-refresh de token."""
        self._ensure_auth()
        url = f"{self.base_url}{endpoint}"

        if settings.DEBUG_SAVE_PAYLOADS:
            self._save_payload_debug(endpoint, data)

        for attempt in range(1, max_retries + 1):
            try:
                resp = self._session.post(url, json=data, timeout=120)

                if resp.status_code == 401:
                    logger.warning("Token expirado, renovando... (tentativa %d)", attempt)
                    self._authenticate()
                    resp = self._session.post(url, json=data, timeout=120)

                resp.raise_for_status()
                return resp.json()

            except requests.exceptions.RequestException as e:
                error_body = ""
                if hasattr(e, "response") and e.response is not None:
                    try:
                        # Tenta extrair e formatar o JSON de erro específico do CashUp
                        err_json = e.response.json()
                        if "errors" in err_json and isinstance(err_json["errors"], list):
                            details = []
                            for item in err_json["errors"]:
                                cod = item.get("codigo", "?")
                                msgs = " | ".join(item.get("errors", []))
                                details.append(f"[Cód {cod}] {msgs}")
                            
                            # Limita a exibição para não quebrar a UI
                            error_body = err_json.get("message", "Falha na API") + " -> " + " ; ".join(details[:5])
                            if len(details) > 5:
                                error_body += f" ... (e mais {len(details)-5} registros com erro)"
                        else:
                            error_body = e.response.text
                    except Exception as e:
                        error_body = getattr(e.response, "text", "")
                        logger.debug("Falha ao analisar JSON de erro: %s | Body original: %s", e, error_body)
                
                logger.warning("POST %s falhou (tentativa %d/%d): %s | Body: %s", endpoint, attempt, max_retries, e, error_body)
                if attempt == max_retries:
                    msg = f"CashUp API Recusou: {error_body}" if error_body else str(e)
                    raise Exception(msg) from e
                time.sleep(2 ** attempt)

    # ─── Batching ───────────────────────────────────────────────

    def post_batch(self, endpoint: str, records: list[dict], batch_size: int | None = None) -> list[dict]:
        """
        Envia registros em batches de tamanho configurável.
        Retorna lista de respostas (uma por batch).
        """
        results = []
        total = len(records)
        batch_size = batch_size or self.batch_size

        for i in range(0, total, batch_size):
            batch = records[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total + batch_size - 1) // batch_size

            logger.info(
                "Enviando batch %d/%d (%d registros) para %s",
                batch_num, total_batches, len(batch), endpoint,
            )

            try:
                result = self.post(endpoint, batch)
                results.append({
                    "batch": batch_num,
                    "count": len(batch),
                    "status": "success",
                    "response": result,
                })
            except Exception as e:
                # Debug: Salva o payload que falhou para inspeção
                import json
                try:
                    with open("debug_last_payload.json", "w", encoding="utf-8") as f:
                        json.dump(batch, f, indent=4, ensure_ascii=False)
                except:
                    pass
                
                logger.error("Erro no batch %d/%d: %s", batch_num, total_batches, e)
                results.append({
                    "batch": batch_num,
                    "count": len(batch),
                    "status": "error",
                    "error": str(e),
                })

        return results

    # ─── Conveniência ───────────────────────────────────────────

    def health_check(self) -> dict:
        """Verifica se a API está online."""
        url = f"{self.base_url}{Endpoints.HEALTH}"
        try:
            resp = requests.get(url, timeout=10)
            return {"status": "online", "code": resp.status_code, "body": resp.json()}
        except Exception as e:
            return {"status": "offline", "error": str(e)}

    def validate_token(self) -> dict:
        """Valida o token atual."""
        self._ensure_auth()
        return self.get(Endpoints.AUTH_VALIDATE)

    def list_endpoints(self) -> dict:
        """Lista endpoints disponíveis na API."""
        return self.get(Endpoints.ENDPOINTS_LIST)
