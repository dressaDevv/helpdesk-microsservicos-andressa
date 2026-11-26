import logging
import os
import secrets

log = logging.getLogger("helpdesk.usuarios")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./usuarios.db")

JWT_SEGREDO = os.getenv("JWT_SEGREDO") or ""
if len(JWT_SEGREDO) < 32:
    if JWT_SEGREDO:
        log.warning("JWT_SEGREDO tem menos de 32 caracteres; usando um segredo aleatório.")
    JWT_SEGREDO = secrets.token_urlsafe(48)

JWT_ALGORITMO = "HS256"
JWT_EMISSOR = "helpdesk-ti"
TOKEN_MINUTOS = int(os.getenv("TOKEN_MINUTOS", "60"))

LOGIN_MAX_FALHAS = int(os.getenv("LOGIN_MAX_FALHAS", "5"))
LOGIN_JANELA_SEGUNDOS = int(os.getenv("LOGIN_JANELA_SEGUNDOS", "300"))

TAMANHO_MAXIMO_REQUISICAO = 64 * 1024
DOCS_ATIVA = os.getenv("DOCS", "1") == "1"
