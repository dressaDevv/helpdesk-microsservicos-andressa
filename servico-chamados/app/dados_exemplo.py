from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app import repositorio
from app.modelos import Chamado


def carregar(db: Session) -> None:
    if repositorio.listar(db):
        return
    agora = datetime.now()
    # IDs alinhados com os dados de exemplo de usuarios (2=Ana, 3=Bruno, 4=Carla) e inventario (1=PC, 2=Impressora)
    c1 = Chamado(
        titulo="Computador não liga",
        descricao="Apertei o botão e nada acontece.",
        prioridade="alta",
        status="em_atendimento",
        solicitante_id=2,
        tecnico_id=4,
        ativo_id=1,
        criado_em=agora,
        prazo_sla=agora + timedelta(hours=8),
    )
    c2 = Chamado(
        titulo="Impressora atolando papel",
        descricao="Atola a cada 3 folhas.",
        prioridade="media",
        status="aberto",
        solicitante_id=3,
        tecnico_id=None,
        ativo_id=2,
        criado_em=agora,
        prazo_sla=agora + timedelta(hours=24),
    )
    c3 = Chamado(
        titulo="Acesso ao sistema de RH",
        descricao="Preciso de acesso para a nova estagiária.",
        prioridade="baixa",
        status="aberto",
        solicitante_id=3,
        tecnico_id=None,
        ativo_id=None,
        criado_em=agora,
        prazo_sla=agora + timedelta(hours=72),
    )
    repositorio.salvar(db, c1)
    repositorio.salvar(db, c2)
    repositorio.salvar(db, c3)
