# CashUp Integration — Contexto do Projeto

## O que é
Serviço Python que sincroniza dados do ERP Oracle para o CRM CashUp via REST API.
Roda como um processo único que combina um dashboard FastAPI (porta 8000) com um agendador APScheduler.

## Instalação no servidor
```bash
# 1. Clonar o repositório
git clone https://github.com/samucaportel/CashUp.git
cd CashUp

# 2. Criar e ativar ambiente virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar ambiente
copy .env.example .env       # Windows
# cp .env.example .env       # Linux/Mac
# Editar .env com as credenciais do ambiente
```

## Como rodar
```bash
venv\Scripts\activate   # ativar o ambiente virtual antes
python run.py
```
Requer o arquivo `.env` configurado (copiar de `.env.example`).

## Atualizações futuras
```bash
git pull
pip install -r requirements.txt   # somente se houver novos pacotes
python run.py
```

## Variáveis de ambiente (.env)
| Variável | Descrição |
|---|---|
| `CASHUP_BASE_URL` | URL base da API CashUp |
| `CASHUP_CLIENT_ID` | Client ID OAuth2 |
| `CASHUP_CLIENT_SECRET` | Client Secret OAuth2 |
| `DB_TYPE` | Tipo do banco (`oracle`) |
| `DB_HOST` / `DB_PORT` | Host e porta do Oracle |
| `DB_USER` / `DB_PASS` | Credenciais do banco |
| `DB_SERVICE_NAME` | Service name Oracle |
| `SYNC_BATCH_SIZE` | Registros por batch (padrão: 50) |
| `SYNC_INTERVAL_MINUTES` | Intervalo global padrão do agendador em minutos (fallback; padrão: 30) |
| `SYNC_INTERVAL_<ENTIDADE>` | (Opcional) Intervalo específico de uma entidade, ex: `SYNC_INTERVAL_ESTOQUE=5`. Sobrescreve a camada padrão |
| `SYNC_FULL_<ENTIDADE>` | (Opcional) `true` força carga total da entidade a cada ciclo, ignorando o `ID_SINC`, ex: `SYNC_FULL_ESTOQUE=true`. Por padrão nenhuma entidade é full-sync |
| `DEBUG_SAVE_PAYLOADS` | `true` para gravar JSONs enviados em `logs/payloads/` |
| `LOG_LEVEL` | Nível de log (padrão: `INFO`) |

## Arquitetura

```
run.py                  → Entry point (FastAPI + APScheduler)
config/settings.py      → Configurações via .env
api/
  client.py             → CashUpClient: HTTP com auth Bearer + retry + batching
  endpoints.py          → Constantes dos endpoints da API CashUp
db/
  oracle.py             → OracleConnector com connection pool
  queries/*.sql         → Queries SQL por entidade
scheduler/jobs.py       → Agendamento e execução dos jobs de sync
sync/
  base.py               → BaseSyncService: fluxo padrão de sync
  *.py                  → Uma classe por entidade
dashboard/
  app.py                → Rotas FastAPI do dashboard
  templates/index.html  → UI do painel
  static/js/app.js      → Lógica do dashboard (labels, botões, gráficos)
```

## Intervalos por entidade
Cada entidade tem seu próprio intervalo de sync, em camadas por volatilidade do dado
(definidas em `config/settings.py` → `SYNC_INTERVAL_DEFAULTS`):
- **Rápida (5 min):** `estoque`
- **Média (15 min):** `pedidos_envio`, `notas_fiscais`, `titulos_financeiros`, `fichas_financeiras`
- **Lenta (60 min):** demais cadastros (`clientes`, `produtos`, etc.)

Resolução do intervalo (`settings.get_sync_interval(entity)`): env `SYNC_INTERVAL_<ENTIDADE>` →
camada padrão → `SYNC_INTERVAL_MINUTES` (fallback global). Cada job ainda recebe um *jitter*
de até ~1/4 do intervalo (máx 120s) para desincronizar entidades de mesmo intervalo.

## Fluxo de sincronização
1. APScheduler chama `_run_sync(entity)` no intervalo da entidade (ver acima)
2. Lê `ULTIMO_ID_SINC` da tabela `CASHUP_CONTROLE_SINC` (watermark). Entidades
   marcadas como full-sync via `SYNC_FULL_<ENTIDADE>` (`settings.is_full_sync`)
   ignoram o watermark e carregam tudo a cada ciclo — a decisão é centralizada
   em `BaseSyncService._resolve_ultimo_id()`
3. Executa `SELECT * FROM VW_CASHUP_{ENTIDADE} WHERE ID_SINC > :ultimo_id`
4. Transforma cada linha com `transform(row)`
5. Envia em batches via `POST` para a API CashUp
6. Atualiza `CASHUP_CONTROLE_SINC` com o novo `max(ID_SINC)`

## Tabela de controle no ERP (Oracle)
```sql
CREATE TABLE CASHUP_CONTROLE_SINC (
    ENTIDADE       VARCHAR2(50) PRIMARY KEY,
    ULTIMO_ID_SINC NUMBER
);
```
Cada view Oracle deve ter a coluna `ID_SINC` (incrementa a cada insert/update via trigger).

## Entidades disponíveis
| Entidade | Endpoint CashUp | Observação |
|---|---|---|
| `clientes` | `/api/v1/rest/clientes` | |
| `produtos` | `/api/v1/rest/produtos` | |
| `estoque` | `/api/v1/rest/estoque` | Agrupa por produto com array `LOTES` |
| `notas_fiscais` | `/api/v1/rest/nfs` | Cabeçalho + array `ITENS`; batch=10 |
| `pedidos_envio` | `/api/v1/rest/pedidos` | |
| `fichas_financeiras` | `/api/v1/rest/fichasfinanceiras` | |
| `titulos_financeiros` | `/api/v1/rest/titulos` | Agrupa por cliente com array `TITULOS` |
| `condicoes_pagto` | `/api/v1/rest/condicoespagto` | |
| `naturezas` | `/api/v1/rest/naturezas` | |
| `equipes_comerciais` | `/api/v1/rest/equipescomerciais` | |
| `tabelas_preco` | `/api/v1/rest/tabelaspreco` | |
| `transportadoras` | `/api/v1/rest/transportadoras` | |
| `produtos_clientes` | `/api/v1/rest/produtosclientes` | |

## Como adicionar uma nova entidade
1. `api/endpoints.py` — adicionar constante do endpoint
2. `db/queries/{entidade}.sql` — query `SELECT * FROM VW_CASHUP_{ENTIDADE} WHERE ID_SINC > :ultimo_id`
3. `sync/{entidade}.py` — criar classe herdando `BaseSyncService` com `transform()`
4. `scheduler/jobs.py` — adicionar import, entrada no `SYNC_MAP` e em `get_available_entities()`
5. `dashboard/static/js/app.js` — adicionar label em `ENTITY_LABELS` e ícone em `ENTITY_ICONS`

### Entidades com estrutura aninhada
Quando a API espera um array dentro do registro (ex: `TITULOS`, `LOTES`, `ITENS`), sobrescrever `execute()` para agrupar as linhas antes de enviar. Ver `sync/estoque.py` (lotes) ou `sync/titulos_financeiros.py` (títulos por cliente) como referência.

## Dashboard — endpoints úteis
| Método | URL | Descrição |
|---|---|---|
| `GET` | `/` | Painel web |
| `GET` | `/api/status` | Status de todas as entidades |
| `POST` | `/api/sync/{entity}` | Sync manual (`?force=true` ignora watermark) |
| `POST` | `/api/sync/all` | Sync manual de todas as entidades |
| `GET` | `/api/history/{entity}` | Histórico de execuções |
| `GET` | `/api/crm/{entity}` | Consulta dados diretamente no CashUp |
| `GET` | `/api/crm/endpoints` | Lista endpoints disponíveis na API CashUp |
| `GET` | `/api/health` | Health check da app + API CashUp |

## Observações importantes
- **Autenticação CashUp:** OAuth2 `client_credentials`. Token expira em 15 min, renovado automaticamente com margem de 60s.
- **Retry:** 3 tentativas com backoff exponencial (`2^attempt` segundos) em todos os requests.
- **Debug de payloads:** `DEBUG_SAVE_PAYLOADS=true` no `.env` grava cada batch enviado em `logs/payloads/{entidade}_{timestamp}.json`.
- **Batch em erro:** Em caso de erro de POST, o payload do batch é salvo em `debug_last_payload.json` na raiz.
- **`notas_fiscais` usa `api_batch_size = 10`** — CashUp tem limitação de volume nesse endpoint.
- **Views Oracle:** Cada entidade depende de uma view `VW_CASHUP_{ENTIDADE}` no ERP com coluna `ID_SINC`.
