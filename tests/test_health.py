# Toda função de teste precisa começar com "test_", senão o pytest
# não a reconhece. O parâmetro "client" é preenchido pela fixture
# definida no conftest.py.
def test_health_check_returns_ok(client):
    # ACT: faz uma requisição GET, como se fosse um navegador.
    response = client.get("/health")

    # ASSERT: "assert" falha o teste se a condição for falsa.
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    
def test_cors_allows_configured_origin(client):
    # Simula o navegador perguntando: "o site localhost:5173 pode
    # chamar esta API?" (requisição preflight, método OPTIONS).
    response = client.options(
        "/tasks",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_blocks_unknown_origin(client):
    response = client.options(
        "/tasks",
        headers={
            "Origin": "http://site-malicioso.com",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert "access-control-allow-origin" not in response.headers