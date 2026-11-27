from datetime import datetime

from app import clientes
from app.erros import ServicoIndisponivel


def test_saude(cliente):
    r = cliente.get("/saude")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_exige_login(cliente):
    assert cliente.get("/chamados").status_code == 401
    assert cliente.post("/chamados", json={"titulo": "PC com defeito", "descricao": "Erro", "prioridade": "baixa"}).status_code == 401


def test_abrir_calcula_sla_e_publica_evento(cliente, contas, mocks_rede):
    r = cliente.post(
        "/chamados",
        headers=contas["ana"]["headers"],
        json={"titulo": "PC não liga", "descricao": "Nada acontece", "prioridade": "critica", "ativo_id": 1},
    )
    assert r.status_code == 201
    c = r.json()
    assert c["solicitante_id"] == contas["ana"]["id"]
    horas = (datetime.fromisoformat(c["prazo_sla"]) - datetime.fromisoformat(c["criado_em"])).total_seconds() / 3600
    assert round(horas) == 4
    assert mocks_rede[0][0] == "ChamadoAberto"


def test_abrir_com_ativo_inexistente(cliente, contas, mocks_rede):
    r = cliente.post(
        "/chamados",
        headers=contas["ana"]["headers"],
        json={"titulo": "PC com defeito", "descricao": "Erro", "prioridade": "alta", "ativo_id": 999},
    )
    assert r.status_code == 404


def test_inventario_fora_do_ar_retorna_503(cliente, contas, monkeypatch):
    def falha_rede(ativo_id: int, token: str):
        raise ServicoIndisponivel("Serviço de inventário indisponível no momento.")

    monkeypatch.setattr(clientes, "conferir_ativo", falha_rede)
    r = cliente.post(
        "/chamados",
        headers=contas["ana"]["headers"],
        json={"titulo": "PC com defeito", "descricao": "Erro", "prioridade": "alta", "ativo_id": 1},
    )
    assert r.status_code == 503


def test_permissoes_e_fluxo_completo(cliente, contas, mocks_rede):
    cid = cliente.post(
        "/chamados",
        headers=contas["ana"]["headers"],
        json={"titulo": "Monitor piscando", "descricao": "Tela preta", "prioridade": "media"},
    ).json()["id"]

    # Bia (outra solicitante) nao ve o chamado da Ana
    assert cliente.get(f"/chamados/{cid}", headers=contas["bia"]["headers"]).status_code == 404
    assert cliente.get("/chamados", headers=contas["bia"]["headers"]).json() == []

    # Ana nao pode atribuir
    assert cliente.patch(
        f"/chamados/{cid}/atribuir", headers=contas["ana"]["headers"], json={"tecnico_id": 4}
    ).status_code == 403

    # Carla (tecnica) atribui e resolve
    r_atrib = cliente.patch(f"/chamados/{cid}/atribuir", headers=contas["carla"]["headers"], json={"tecnico_id": 4})
    assert r_atrib.status_code == 200 and r_atrib.json()["status"] == "em_atendimento"

    r_res = cliente.patch(f"/chamados/{cid}/status", headers=contas["carla"]["headers"], json={"status": "resolvido"})
    assert r_res.status_code == 200

    # Ana (solicitante) fecha o proprio chamado
    r_fec = cliente.patch(f"/chamados/{cid}/status", headers=contas["ana"]["headers"], json={"status": "fechado"})
    assert r_fec.status_code == 200 and r_fec.json()["status"] == "fechado"
