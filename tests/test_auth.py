def register(client, email="ana@example.com", password="senha12345"):
    return client.post("/auth/register", json={"email": email, "password": password})


def login(client, email="ana@example.com", password="senha12345"):
    # Login usa formulário, por isso data= em vez de json=.
    return client.post("/auth/login", data={"username": email, "password": password})


def auth_header(client, email):
    # Cadastra, faz login e devolve o cabeçalho pronto, para usar
    # por requisição (headers=...). Útil para simular DOIS usuários.
    register(client, email=email)
    token = login(client, email=email).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ---------- Cadastro ----------
def test_register_user(client):
    response = register(client)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "ana@example.com"
    assert "id" in data
    # A senha e o hash NUNCA podem aparecer na resposta.
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email_returns_409(client):
    register(client)

    response = register(client)

    assert response.status_code == 409


def test_register_email_is_case_insensitive(client):
    register(client, email="ana@example.com")

    response = register(client, email="ANA@example.com")

    assert response.status_code == 409


def test_register_short_password_returns_422(client):
    response = register(client, password="123")

    assert response.status_code == 422


def test_register_invalid_email_returns_422(client):
    response = register(client, email="isso-nao-e-email")

    assert response.status_code == 422


# ---------- Login ----------
def test_login_returns_token(client):
    register(client)

    response = login(client)

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]


def test_login_wrong_password_returns_401(client):
    register(client)

    response = login(client, password="senhaerrada")

    assert response.status_code == 401


def test_login_unknown_user_returns_401(client):
    response = login(client, email="naoexiste@example.com")

    assert response.status_code == 401


# ---------- Proteção das rotas ----------
def test_tasks_without_token_returns_401(client):
    response = client.get("/tasks")

    assert response.status_code == 401


def test_tasks_with_invalid_token_returns_401(client):
    response = client.get("/tasks", headers={"Authorization": "Bearer token-falso"})

    assert response.status_code == 401


# ---------- Isolamento entre usuários ----------
def test_user_cannot_access_another_users_task(client):
    ana = auth_header(client, "ana@example.com")
    bob = auth_header(client, "bob@example.com")

    # Ana cria uma tarefa.
    created = client.post("/tasks", json={"title": "Da Ana"}, headers=ana).json()
    task_url = f"/tasks/{created['id']}"

    # Bob não consegue ver, alterar nem apagar a tarefa da Ana.
    assert client.get(task_url, headers=bob).status_code == 404
    assert client.patch(task_url, json={"completed": True}, headers=bob).status_code == 404
    assert client.delete(task_url, headers=bob).status_code == 404

    # A lista do Bob está vazia.
    assert client.get("/tasks", headers=bob).json() == []

    # A tarefa continua intacta para a Ana.
    assert client.get(task_url, headers=ana).status_code == 200