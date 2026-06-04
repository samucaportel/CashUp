"""
Constantes dos endpoints da API CashUp REST v4.
"""


class Endpoints:
    """Paths dos endpoints da API CashUp."""

    # Auth
    AUTH_TOKEN = "/api/v1/rest/auth/token"
    AUTH_VALIDATE = "/api/v1/rest/auth/validate"

    # Entidades
    PRODUTOS = "/api/v1/rest/produtos"
    CLIENTES = "/api/v1/rest/clientes"
    ESTOQUE = "/api/v1/rest/estoque"
    CONDICOES_PAGTO = "/api/v1/rest/condicoespagto"
    NATUREZAS = "/api/v1/rest/naturezas"
    EQUIPES_COMERCIAIS = "/api/v1/rest/equipescomerciais"
    TABELAS_PRECO = "/api/v1/rest/tabelaspreco"
    NOTAS_FISCAIS = "/api/v1/rest/nfs"
    PEDIDOS = "/api/v1/rest/pedidos"
    FICHAS_FINANCEIRAS = "/api/v1/rest/fichasfinanceiras"
    TITULOS_FINANCEIROS = "/api/v1/rest/titulos"
    PRODUTOS_CLIENTES = "/api/v1/rest/produtosclientes"
    TRANSPORTADORAS = "/api/v1/rest/transportadoras"

    # Documentação
    ENDPOINTS_LIST = "/api/v1/rest/endpoints"

    # Health
    HEALTH = "/health"
