"""Publicacao assincrona de eventos de dominio no Redis."""
import json
import logging
from datetime import datetime

import redis

from app.config import FILA_EVENTOS, REDIS_URL

log = logging.getLogger("helpdesk.chamados.eventos")


def publicar(tipo: str, destinatario_id: int, mensagem: str) -> None:
    evento = json.dumps(
        {
            "tipo": tipo,
            "destinatario_id": destinatario_id,
            "mensagem": mensagem,
            "criada_em": datetime.now().isoformat(),
        },
        ensure_ascii=False,
    )
    try:
        cliente = redis.Redis.from_url(REDIS_URL, socket_connect_timeout=1.5, socket_timeout=1.5)
        cliente.rpush(FILA_EVENTOS, evento)
    except Exception as erro:
        # Se a fila ou o servico de notificacoes cair, os chamados continuam operando normalmente
        log.warning("Nao foi possivel publicar o evento %s: %s", tipo, erro)
