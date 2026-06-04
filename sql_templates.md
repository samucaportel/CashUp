# SQL Templates for CashUp Integration

Use these templates to prepare your Oracle ERP data for synchronization or to handle incoming orders.

## 1. Product Insertion Template
To populate products so the synchronization service can pick them up (via `VW_CASHUP_PRODUTOS`):

```sql
INSERT INTO SEU_SCHEMA.SUA_TABELA_PRODUTOS (
    ID_SINC,
    COD_PRODUTO,
    DESCR_PRODUTO,
    UM,
    ATIVO,
    PESO_LIQ,
    PESO_PC,
    COD_CLASS_FISCAL,
    ORIGEM,
    COMPLEMENTO,
    COD_DIVISAO,
    CUSTO_FINANCEIRO,
    PRECO_ATUAL,
    MULTIPLO,
    ACEITA_VENDA_FRACIONADA
) VALUES (
    SEQ_CASHUP_ID_SINC.NEXTVAL, -- Use a sequence to ensure delta sync works
    'PROD001',
    'PRODUTO EXEMPLO 01',
    'UN',
    'S',
    1.500,
    1.650,
    '33041000',
    '0',
    'LINHA PREMIUM',
    'DIV01',
    150.50,
    299.99,
    1,
    'N'
);

COMMIT;
```

---

## 2. Orders View (Mestre-Detalhe)
For receiving orders into your ERP, you can use these view structures to map the JSON incoming from your API to your `PEDIDO` and `PEDIDO_ITEM` tables.

### Master (Pedido)
```sql
CREATE OR REPLACE VIEW VW_CASHUP_PEDIDO_MESTRE AS
SELECT 
    COD_EMPRESA,
    NUM_PEDIDO,
    COD_CLIENTE,
    DT_EMISSAO,
    VALOR_TOTAL,
    COND_PAGTO,
    OBSERVACAO
FROM PEDIDO;
```

### Detail (Itens)
```sql
CREATE OR REPLACE VIEW VW_CASHUP_PEDIDO_ITEM AS
SELECT 
    COD_EMPRESA,
    NUM_PEDIDO,
    SEQ_ITEM,
    COD_PRODUTO,
    QUANTIDADE,
    PRECO_UNITARIO,
    DESCONTO
FROM PEDIDO_ITEM;
```

> [!IMPORTANT]
> Ensure that `COD_EMPRESA` and `NUM_PEDIDO` are present in both to allow the join (Mestre-Detalhe).
