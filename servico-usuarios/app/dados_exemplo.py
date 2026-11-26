import os

from sqlalchemy.orm import Session

from app import servico
from app.esquemas import UsuarioCriar

SENHA = os.getenv("SENHA_EXEMPLO", "Helpdesk2026")


def carregar(db: Session) -> None:
    if servico.listar(db):
        return
    novo = lambda nome, email, perfil: servico.criar(
        db, UsuarioCriar(nome=nome, email=email, perfil=perfil, senha=SENHA)
    )
    novo("Admin TI", "admin@empresa.com", "admin")
    novo("Ana Souza", "ana@empresa.com", "solicitante")
    novo("Bruno Lima", "bruno@empresa.com", "solicitante")
    novo("Carla Dias", "carla@empresa.com", "tecnico")
    novo("Diego Rocha", "diego@empresa.com", "tecnico")
