from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import config
from app.database import Base, get_db
from app.main import app


def gerar_token(usuario_id: int, perfil: str) -> str:
    agora = datetime.now(timezone.utc)
    dados = {
        "sub": str(usuario_id),
        "perfil": perfil,
        "iat": agora,
        "exp": agora + timedelta(hours=1),
        "iss": config.JWT_EMISSOR,
    }
    return jwt.encode(dados, config.JWT_SEGREDO, algorithm=config.JWT_ALGORITMO)


@pytest.fixture
def sessao(monkeypatch):
    monkeypatch.setenv("CONSUMIDOR_ATIVO", "0")
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Sessao = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def db_de_teste():
        db = Sessao()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = db_de_teste
    yield Sessao
    app.dependency_overrides.clear()


@pytest.fixture
def cliente(sessao):
    with TestClient(app) as c:
        yield c


@pytest.fixture
def contas():
    return {
        "ana": {"headers": {"Authorization": f"Bearer {gerar_token(2, 'solicitante')}"}, "id": 2},
        "bia": {"headers": {"Authorization": f"Bearer {gerar_token(3, 'solicitante')}"}, "id": 3},
    }
