import os

USUARIOS_URL = os.getenv("USUARIOS_URL", "http://usuarios:8000")
INVENTARIO_URL = os.getenv("INVENTARIO_URL", "http://inventario:8000")
CHAMADOS_URL = os.getenv("CHAMADOS_URL", "http://chamados:8000")
NOTIFICACOES_URL = os.getenv("NOTIFICACOES_URL", "http://notificacoes:8000")

HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "5.0"))
TAMANHO_MAXIMO_REQUISICAO = 64 * 1024
DOCS_ATIVA = os.getenv("DOCS", "1") == "1"
