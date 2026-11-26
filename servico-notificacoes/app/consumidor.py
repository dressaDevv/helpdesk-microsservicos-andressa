"""Consumidor assincrono da fila de eventos no Redis."""
import json
import logging
import threading
import time
from datetime import datetime

import redis
from sqlalchemy.orm import Session

from app import servico
from app.config import FILA_EVENTOS, REDIS_URL
from app.database import SessionLocal

log = logging.getLogger("helpdesk.notificacoes.consumidor")


def processar_mensagem(db: Session, bruto: str) -> None:
    dados = json.loads(bruto)
    criada_em = datetime.fromisoformat(dados["criada_em"]) if dados.get("criada_em") else datetime.now()
    servico.registrar(
        db=db,
        tipo=dados["tipo"],
        destinatario_id=int(dados["destinatario_id"]),
        mensagem=dados["mensagem"],
        criada_em=criada_em,
    )


def _loop_consumo(parar: threading.Event) -> None:
    while not parar.is_set():
        try:
            cliente = redis.Redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2.0)
            while not parar.is_set():
                item = cliente.blpop(FILA_EVENTOS, timeout=2)
                if item:
                    _, bruto = item
                    with SessionLocal() as db:
                        processar_mensagem(db, bruto)
        except Exception as erro:
            log.warning("Aguardando conexao com o Redis (%s)...", erro)
            parar.wait(2.0)


def iniciar(parar: threading.Event) -> threading.Thread:
    thread = threading.Thread(target=_loop_consumo, args=(parar,), daemon=True)
    thread.start()
    return thread
