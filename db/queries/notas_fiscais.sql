-- View: VW_CASHUP_NOTAS_FISCAIS
-- Campos seguem nomenclatura da API CashUp (cabeçalho)
SELECT * FROM VW_CASHUP_NOTAS_FISCAIS

WHERE ID_SINC > :ultimo_id
