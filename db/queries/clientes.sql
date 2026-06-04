-- View: VW_CASHUP_CLIENTES
-- Campos seguem nomenclatura da API CashUp
SELECT * FROM VW_CASHUP_CLIENTES

WHERE ID_SINC > :ultimo_id
