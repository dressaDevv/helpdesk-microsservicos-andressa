import json
from app import consumidor


def test_saude(cliente):
    r = cliente.get("/saude")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_exige_login(cliente):
    assert cliente.get("/notificacoes").status_code == 401


def test_consome_evento_e_isola_por_usuario(sessao, cliente, contas):
    evento = json.dumps(
        {
            "tipo": "ChamadoAberto",
            "destinatario_id": contas["ana"]["id"],
            "mensagem": "Seu chamado #1 foi aberto.",
        }
    )
    with sessao() as db:
        consumidor.processar_mensagem(db, evento)

    avisos_ana = cliente.get("/notificacoes", headers=contas["ana"]["headers"]).json()
    assert len(avisos_ana) == 1 and avisos_ana[0]["tipo"] == "ChamadoAberto"

    # Bia nao ve as notificacoes da Ana
    avisos_bia = cliente.get("/notificacoes", headers=contas["bia"]["headers"]).json()
    assert avisos_bia == []
