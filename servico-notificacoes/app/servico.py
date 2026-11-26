from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modelos import Notificacao


def registrar(
    db: Session,
    tipo: str,
    destinatario_id: int,
    mensagem: str,
    criada_em: datetime | None = None,
) -> Notificacao:
    aviso = Notificacao(
        tipo=tipo,
        destinatario_id=destinatario_id,
        mensagem=mensagem,
        criada_em=criada_em or datetime.now(),
    )
    db.add(aviso)
    db.commit()
    db.refresh(aviso)
    return aviso


def listar(db: Session, destinatario_id: int) -> list[Notificacao]:
    consulta = (
        select(Notificacao)
        .where(Notificacao.destinatario_id == destinatario_id)
        .order_by(Notificacao.id)
    )
    return list(db.scalars(consulta))
