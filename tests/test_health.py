# Toda função de teste precisa começar com "test_", senão o pytest
# não a reconhece. O parâmetro "client" é preenchido pela fixture
# definida no conftest.py.
def test_health_check_returns_ok(client):
    # ACT: faz uma requisição GET, como se fosse um navegador.
    response = client.get("/health")

    # ASSERT: "assert" falha o teste se a condição for falsa.
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}