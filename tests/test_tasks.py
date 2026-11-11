# Função auxiliar (não começa com "test_", então o pytest não a executa
# como teste). Evita repetir o código de criação em todo teste.
def create_task(client, title="Tarefa de teste", description=None):
    # json=... envia o dicionário como corpo JSON da requisição.
    response = client.post(
        "/tasks",
        json={"title": title, "description": description},
    )
    return response


# ---------- CREATE ----------
def test_create_task(client):
    response = create_task(client, title="Estudar pytest", description="Etapa 7")

    # 201 = Created
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Estudar pytest"
    assert data["description"] == "Etapa 7"
    # Valores gerados pelo servidor:
    assert data["completed"] is False
    assert data["id"] == 1
    assert "created_at" in data


def test_create_task_without_title_returns_422(client):
    # Corpo sem o campo obrigatório "title".
    response = client.post("/tasks", json={"description": "sem título"})

    # 422 = dados inválidos (validação automática do Pydantic).
    assert response.status_code == 422


def test_create_task_with_empty_title_returns_422(client):
    # Título vazio viola o min_length=1 do schema.
    response = client.post("/tasks", json={"title": ""})

    assert response.status_code == 422


def test_create_task_with_too_long_title_returns_422(client):
    # 101 caracteres viola o max_length=100 do schema.
    response = client.post("/tasks", json={"title": "a" * 101})

    assert response.status_code == 422


# ---------- READ (lista) ----------
def test_list_tasks_empty(client):
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_returns_all_created(client):
    create_task(client, title="Primeira")
    create_task(client, title="Segunda")

    response = client.get("/tasks")

    assert response.status_code == 200
    titles = [task["title"] for task in response.json()]
    # Comparamos como conjunto (set) porque a ordem de retorno
    # não é o foco deste teste.
    assert set(titles) == {"Primeira", "Segunda"}


def test_list_tasks_filter_by_completed(client):
    create_task(client, title="Pendente")
    done = create_task(client, title="Concluída").json()
    # Marca a segunda tarefa como concluída.
    client.patch(f"/tasks/{done['id']}", json={"completed": True})

    response = client.get("/tasks", params={"completed": True})

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Concluída"


def test_list_tasks_pagination_limit(client):
    for i in range(3):
        create_task(client, title=f"Tarefa {i}")

    response = client.get("/tasks", params={"limit": 2})

    assert response.status_code == 200
    assert len(response.json()) == 2


# ---------- READ (uma) ----------
def test_get_task_by_id(client):
    created = create_task(client, title="Buscar esta").json()

    response = client.get(f"/tasks/{created['id']}")

    assert response.status_code == 200
    assert response.json()["title"] == "Buscar esta"


def test_get_task_not_found_returns_404(client):
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Tarefa não encontrada"


# ---------- UPDATE ----------
def test_update_task_partial_keeps_other_fields(client):
    created = create_task(client, title="Título original", description="Desc").json()

    # Enviamos APENAS "completed". O PATCH não deve apagar o resto.
    response = client.patch(f"/tasks/{created['id']}", json={"completed": True})

    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is True
    assert data["title"] == "Título original"
    assert data["description"] == "Desc"


def test_update_task_title(client):
    created = create_task(client, title="Antigo").json()

    response = client.patch(f"/tasks/{created['id']}", json={"title": "Novo"})

    assert response.status_code == 200
    assert response.json()["title"] == "Novo"


def test_update_task_not_found_returns_404(client):
    response = client.patch("/tasks/999", json={"completed": True})

    assert response.status_code == 404


# ---------- DELETE ----------
def test_delete_task(client):
    created = create_task(client).json()

    response = client.delete(f"/tasks/{created['id']}")

    # 204 = sucesso sem corpo.
    assert response.status_code == 204

    # Confirma que a tarefa realmente deixou de existir.
    assert client.get(f"/tasks/{created['id']}").status_code == 404


def test_delete_task_not_found_returns_404(client):
    response = client.delete("/tasks/999")

    assert response.status_code == 404