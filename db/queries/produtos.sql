-- View: VW_CASHUP_PRODUTOS
-- Campos seguem nomenclatura da API CashUp
SELECT * FROM VW_CASHUP_PRODUTOS

WHERE ID_SINC > :ultimo_id
