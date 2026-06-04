-- View: VW_CASHUP_NATUREZAS
-- Campos seguem nomenclatura da API CashUp
SELECT * FROM VW_CASHUP_NATUREZAS

WHERE ID_SINC > :ultimo_id
