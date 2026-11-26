from datetime import datetime, timedelta, timezone
import jwt
from app import config
from tests.conftest import SENHA


def test_saude(cliente):
    r = cliente.get("/saude")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_rotas_exigem_login(cliente, contas):
    assert cliente.get("/usuarios").status_code == 401
    assert cliente.get("/auth/eu").status_code == 401


def test_login_e_token_invalido(cliente, contas):
    assert cliente.post("/auth/login", json={"email": "ana@x.com", "senha": "errada123"}).status_code == 401
    falso = jwt.encode(
        {"sub": "1", "iss": config.JWT_EMISSOR, "iat": datetime.now(timezone.utc), "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        "outro-segredo-qualquer-com-mais-de-32-caracteres",
        algorithm="HS256",
    )
    assert cliente.get("/auth/eu", headers={"Authorization": f"Bearer {falso}"}).status_code == 401


def test_bloqueio_tentativas(cliente, contas):
    for _ in range(config.LOGIN_MAX_FALHAS):
        cliente.post("/auth/login", json={"email": "ana@x.com", "senha": "errada123"})
    assert cliente.post("/auth/login", json={"email": "ana@x.com", "senha": SENHA}).status_code == 429


def test_permissoes_e_privacidade(cliente, contas):
    r_negado = cliente.post(
        "/usuarios",
        headers=contas["ana"]["headers"],
        json={"nome": "Eva", "email": "eva@x.com", "perfil": "admin", "senha": "Forte1234"},
    )
    assert r_negado.status_code == 403

    r_ok = cliente.post(
        "/usuarios",
        headers=contas["admin"]["headers"],
        json={"nome": "Eva", "email": "eva@x.com", "perfil": "tecnico", "senha": "Forte1234"},
    )
    assert r_ok.status_code == 201 and "senha_hash" not in r_ok.json()

    lista = cliente.get("/usuarios", headers=contas["ana"]["headers"]).json()
    assert lista and all("email" not in u for u in lista)
