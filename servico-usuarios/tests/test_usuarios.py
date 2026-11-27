from fastapi.testclient import TestClient
from app import main

def test_saude_e_protecao():
    with TestClient(main.app) as c:
        assert c.get('/saude').status_code == 200
        assert c.get('/usuarios').status_code == 401
