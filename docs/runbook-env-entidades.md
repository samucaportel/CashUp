# Runbook — Parâmetros de sync por entidade (`.env`)

Como configurar, por entidade, **de quanto em quanto tempo** ela sincroniza e se ela
faz **carga total** (ignorando o controle de alterações) a cada ciclo.

> Todas as variáveis abaixo são **opcionais**. Sem elas, cada entidade usa o padrão
> de código definido em `config/settings.py`.

---

## 1. As duas variáveis

| Variável | O que faz | Valores |
|---|---|---|
| `SYNC_INTERVAL_<ENTIDADE>` | Intervalo de sync da entidade, em **minutos** | número inteiro (ex: `5`) |
| `SYNC_FULL_<ENTIDADE>` | Se `true`, a entidade **sempre carrega tudo** a cada ciclo, ignorando o `ID_SINC` | `true` / `false` |

`<ENTIDADE>` é o nome da entidade em **MAIÚSCULAS**. Ex: `estoque` → `SYNC_INTERVAL_ESTOQUE`,
`notas_fiscais` → `SYNC_FULL_NOTAS_FISCAIS`.

Valores aceitos como "ligado" em `SYNC_FULL_*`: `true`, `1`, `yes`, `on`, `sim`
(qualquer outra coisa = desligado).

---

## 2. Nomes das entidades

| Entidade | Sufixo da variável |
|---|---|
| clientes | `_CLIENTES` |
| produtos | `_PRODUTOS` |
| estoque | `_ESTOQUE` |
| condicoes_pagto | `_CONDICOES_PAGTO` |
| naturezas | `_NATUREZAS` |
| equipes_comerciais | `_EQUIPES_COMERCIAIS` |
| tabelas_preco | `_TABELAS_PRECO` |
| transportadoras | `_TRANSPORTADORAS` |
| fichas_financeiras | `_FICHAS_FINANCEIRAS` |
| produtos_clientes | `_PRODUTOS_CLIENTES` |
| notas_fiscais | `_NOTAS_FISCAIS` |
| pedidos_envio | `_PEDIDOS_ENVIO` |
| titulos_financeiros | `_TITULOS_FINANCEIROS` |

---

## 3. Padrões atuais (sem nenhuma variável no `.env`)

**Intervalos** (camadas por volatilidade do dado):

| Camada | Entidades | Intervalo |
|---|---|---|
| 🔴 Rápida | `estoque` | 5 min |
| 🟡 Média | `pedidos_envio`, `notas_fiscais`, `titulos_financeiros`, `fichas_financeiras` | 15 min |
| 🟢 Lenta | demais cadastros (`clientes`, `produtos`, etc.) | 60 min |

**Carga total (full-sync):** apenas `estoque` = ligado. Todas as outras usam o
controle incremental por `ID_SINC`.

---

## 4. Ordem de resolução (quem vence)

**Intervalo:**
1. `SYNC_INTERVAL_<ENTIDADE>` no `.env` (se definido)
2. Camada padrão do código (tabela acima)
3. `SYNC_INTERVAL_MINUTES` (fallback global — só para entidades sem camada)

**Full-sync:**
1. `SYNC_FULL_<ENTIDADE>` no `.env` (se definido — vale `true` **ou** `false`)
2. Padrão do código (apenas `estoque` ligado)

Ou seja: o que estiver no `.env` **sempre ganha** do padrão do código.

---

## 5. Exemplos práticos

### Estoque ainda mais rápido (a cada 2 min)
```env
SYNC_INTERVAL_ESTOQUE=2
```

### Notas fiscais de hora em hora
```env
SYNC_INTERVAL_NOTAS_FISCAIS=60
```

### Forçar carga total também nos títulos financeiros
```env
SYNC_FULL_TITULOS_FINANCEIROS=true
```

### Desligar a carga total do estoque (voltar ao incremental por ID_SINC)
```env
SYNC_FULL_ESTOQUE=false
```

### Testar tudo rápido (todas as entidades a cada 1 min)
> O `SYNC_INTERVAL_MINUTES` global **não** afeta as entidades que já têm camada.
> Para testar rápido, defina o intervalo de cada uma:
```env
SYNC_INTERVAL_CLIENTES=1
SYNC_INTERVAL_PRODUTOS=1
SYNC_INTERVAL_ESTOQUE=1
# ... e assim por diante para as que quiser testar
```

---

## 6. Aplicar as mudanças

O `.env` é lido **na inicialização**. Depois de editar:

```bash
# parar o processo (Ctrl+C) e subir de novo
venv\Scripts\activate
python run.py
```

Confirme nos logs de startup a linha de cada job, ex:
```
Job agendado: sync_estoque (a cada 2 min, jitter até 30s)
```
E, na primeira execução de uma entidade full-sync:
```
[estoque] Full sync: entidade em carga total, ignorando ID_SINC
```

---

## 7. Notas

- **Jitter:** cada job recebe automaticamente um atraso aleatório de até ~1/4 do
  intervalo (máx 120s) para as entidades não baterem no banco ao mesmo tempo.
  Não é configurável por `.env` — é derivado do intervalo.
- **Full-sync e o watermark:** mesmo em full-sync, o `ULTIMO_ID_SINC` continua sendo
  atualizado. Assim, se você desligar o full-sync depois, a entidade retoma o
  incremental do ponto correto (sem reenviar tudo de novo).
- **Onde mudar os padrões de código:** `config/settings.py` →
  `SYNC_INTERVAL_DEFAULTS` (intervalos) e `SYNC_FULL_DEFAULTS` (full-sync).
