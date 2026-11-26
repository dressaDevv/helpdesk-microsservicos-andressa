def test_saude(cliente):
    r = cliente.get("/saude")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_exige_login(cliente):
    assert cliente.get("/ativos").status_code == 401


def test_solicitante_nao_cadastra_ativo(cliente, contas):
    r = cliente.post(
        "/ativos",
        headers=contas["ana"]["headers"],
        json={"patrimonio": "PAT-99", "tipo": "outro", "descricao": "Monitor", "setor": "TI"},
    )
    assert r.status_code == 403


def test_tecnico_cadastra_lista_e_obtem_ativo(cliente, contas):
    h = contas["carla"]["headers"]
    r1 = cliente.post("/ativos", headers=h, json={"patrimonio": "PAT-1", "tipo": "impressora", "descricao": "HP", "setor": "RH"})
    assert r1.status_code == 201
    ativo_id = r1.json()["id"]

    r_dup = cliente.post("/ativos", headers=h, json={"patrimonio": "PAT-1", "tipo": "impressora", "descricao": "HP", "setor": "RH"})
    assert r_dup.status_code == 422

    cliente.post("/ativos", headers=h, json={"patrimonio": "PAT-2", "tipo": "computador", "descricao": "Dell", "setor": "TI"})
    assert len(cliente.get("/ativos", params={"setor": "RH"}, headers=contas["ana"]["headers"]).json()) == 1
    assert cliente.get(f"/ativos/{ativo_id}", headers=contas["ana"]["headers"]).status_code == 200
    assert cliente.get("/ativos/999", headers=contas["ana"]["headers"]).status_code == 404
