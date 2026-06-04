-- View: VW_CASHUP_PEDIDOS
-- Campos seguem nomenclatura da API CashUp
SELECT * FROM VW_CASHUP_PEDIDOS

WHERE ID_SINC > :ultimo_id
