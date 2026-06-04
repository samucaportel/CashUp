-- View: VW_CASHUP_CONDICOES_PAGTO
-- Campos seguem nomenclatura da API CashUp
SELECT * FROM VW_CASHUP_CONDICOES_PAGTO

WHERE ID_SINC > :ultimo_id
