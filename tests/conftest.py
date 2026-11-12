import os

# Define o SECRET_KEY ANTES de importar o app, porque o app lê essa
# variável no momento do import (app/config.py). setdefault só define
# se ainda não existir. Assim os testes funcionam em qualquer máquina
# e no CI, sem precisar do arquivo .env.
os.environ.setdefault("SECRET_KEY", "chave-secreta-apenas-para-testes")
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Engine de TESTE: "sqlite://" (sem nome de arquivo) cria um banco
# que vive apenas na memória RAM.
#
# StaticPool força o SQLAlchemy a reutilizar UMA única conexão.
# Isso é necessário: um banco em memória pertence à conexão que o
# criou. Com várias conexões, cada uma enxergaria um banco vazio
# diferente e as tabelas "sumiriam".
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Fábrica de sessões ligada ao banco de teste.
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
)


# @pytest.fixture marca esta função como uma fixture.
# Qualquer teste que tenha um parâmetro chamado "client" recebe
# automaticamente o valor entregue por ela.
#
# Como o escopo padrão é "function", esta fixture roda ANTES DE CADA
# TESTE. Isso garante que um teste nunca é afetado pelos dados de outro.
@pytest.fixture()
def client():
    # PREPARAÇÃO: cria todas as tabelas no banco em memória.
    Base.metadata.create_all(bind=test_engine)

    # Versão alternativa do get_db que entrega sessões do banco de teste
    # em vez do banco real.
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Aqui está o truque: dizemos ao FastAPI "sempre que alguma rota
    # pedir get_db, use override_get_db no lugar". As rotas não mudam
    # nada; só a origem da sessão é trocada. É a principal vantagem de
    # usar Depends(get_db).
    app.dependency_overrides[get_db] = override_get_db

    # Cria o cliente de teste. O "with" garante que ele é encerrado
    # corretamente ao final.
    with TestClient(app) as test_client:
        # "yield" entrega o client ao teste. O teste roda neste ponto.
        yield test_client

    # LIMPEZA (roda depois do teste): remove a substituição e apaga
    # as tabelas, deixando o banco vazio para o próximo teste.
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    

# Fixture que entrega um client JÁ LOGADO.
# Ela depende da fixture "client": o pytest resolve isso sozinho.
@pytest.fixture()
def auth_client(client):
    credentials = {"email": "ana@example.com", "password": "senha12345"}

    # Cadastra e faz login com um usuário padrão de teste.
    client.post("/auth/register", json=credentials)
    response = client.post(
        "/auth/login",
        # data= envia como formulário (o login não aceita JSON).
        data={"username": credentials["email"], "password": credentials["password"]},
    )
    token = response.json()["access_token"]

    # Adiciona o cabeçalho a TODAS as requisições seguintes deste client.
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client