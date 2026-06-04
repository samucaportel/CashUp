-- View: VW_CASHUP_ESTOQUE
-- Campos seguem nomenclatura da API CashUp
SELECT * FROM VW_CASHUP_ESTOQUE

WHERE ID_SINC > :ultimo_id
