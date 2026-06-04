-- View: VW_CASHUP_TABELAS_PRECO
-- Campos seguem nomenclatura da API CashUp
SELECT * FROM VW_CASHUP_TABELAS_PRECO

WHERE ID_SINC > :ultimo_id
