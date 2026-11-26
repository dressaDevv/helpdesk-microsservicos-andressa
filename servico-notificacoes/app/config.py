import logging
import os
import secrets

log = logging.getLogger("helpdesk.notificacoes")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./notificacoes.db")

JWT_SEGREDO = os.getenv("JWT_SEGREDO") or ""
if len(JWT_SEGREDO) < 32:
    if JWT_SEGREDO:
        log.warning("JWT_SEGREDO tem menos de 32 caracteres; usando um segredo aleatório.")
    JWT_SEGREDO = secrets.token_urlsafe(48)

JWT_ALGORITMO = "HS256"
JWT_EMISSOR = "helpdesk-ti"

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
FILA_EVENTOS = os.getenv("FILA_EVENTOS", "helpdesk:eventos")
CONSUMIDOR_ATIVO = os.getenv("CONSUMIDOR_ATIVO", "1") == "1"

TAMANHO_MAXIMO_REQUISICAO = 64 * 1024
DOCS_ATIVA = os.getenv("DOCS", "1") == "1"
