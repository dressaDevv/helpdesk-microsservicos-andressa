from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import servico
from app.auth.dependencias import usuario_atual
from app.auth.tokens import UsuarioToken
from app.database import get_db
from app.esquemas import NotificacaoSaida

router = APIRouter(prefix="/notificacoes", tags=["Notificações"])


@router.get("", response_model=list[NotificacaoSaida])
def minhas_notificacoes(usuario: UsuarioToken = Depends(usuario_atual), db: Session = Depends(get_db)):
    return servico.listar(db, usuario.id)
