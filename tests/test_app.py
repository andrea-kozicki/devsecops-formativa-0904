from fastapi.testclient import TestClient
from app import API, metricas

client = TestClient(API)

def resetar_metricas():
    metricas["requisicoes"] = 0
    metricas["erros"] = 0
    metricas["logins_falhos"] = 0

def test_health_deve_retornar_ok():
    resetar_metricas()
    resposta = client.get("/health")

    assert resposta.status_code == 200
    assert resposta.json() == "OK"

def test_login_valido():
    resetar_metricas()
    resposta = client.post("/login", data={
        "usuario": "admin",
        "senha": "1234"
    })

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "logged in"
    assert resposta.json()["usuario"] == "admin"

def test_login_invalido():
    resetar_metricas()
    resposta = client.post("/login", data={
        "usuario": "admin",
        "senha": "senha_errada"
    })

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "Credenciais inválidas"

def test_login_sem_campos():
    resetar_metricas()
    resposta = client.post("/login", data={})

    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "Usuário e senha são obrigatórios"

def test_metricas_existem():
    resetar_metricas()

    client.get("/health")
    client.post("/login", data={"usuario": "admin", "senha": "senha_errada"})
    resposta = client.get("/metricas")

    assert resposta.status_code == 200

    dados = resposta.json()
    assert "requisicoes" in dados
    assert "erros" in dados
    assert "logins_falhos" in dados