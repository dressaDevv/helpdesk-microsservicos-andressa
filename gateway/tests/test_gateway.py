import httpx
from fastapi.testclient import TestClient

from app import main


def test_tela_e_cabecalhos_seguranca():
    with TestClient(main.app) as cliente:
        r = cliente.get("/")
        assert r.status_code == 200
        assert "script-src 'self'" in r.headers["content-security-policy"]
        assert r.headers["x-frame-options"] == "DENY"


def test_servico_indisponivel_retorna_503(monkeypatch):
    async def falha_request(self, *args, **kwargs):
        raise httpx.ConnectError("Conexao recusada")

    monkeypatch.setattr(httpx.AsyncClient, "request", falha_request)
    with TestClient(main.app) as cliente:
        r = cliente.get("/ativos")
        assert r.status_code == 503
        assert "indisponível" in r.json()["detail"]
