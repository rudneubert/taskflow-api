# create_engine: cria a "conexão" com o banco de dados.
# sessionmaker: fábrica de sessões (explicado abaixo).
# DeclarativeBase: classe base para os modelos (tabelas).
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# URL de conexão. O formato é "tipo_de_banco:///caminho".
# Aqui usamos SQLite e o arquivo "taskflow.db" será criado
# na pasta onde você rodar o uvicorn (a raiz do projeto).
# Mais tarde, para trocar por PostgreSQL, basta mudar esta linha.
DATABASE_URL = "sqlite:///./taskflow.db"

# O "engine" é o ponto central de comunicação com o banco.
# check_same_thread=False é necessário só para SQLite: o FastAPI
# pode usar threads diferentes para atender requisições, e por
# padrão o SQLite proíbe isso.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# SessionLocal é uma fábrica de sessões.
# Uma SESSÃO é uma "conversa" com o banco: você abre, faz
# consultas e alterações, e fecha.
# - autocommit=False: alterações só valem quando você chamar commit().
# - autoflush=False: não envia alterações pendentes ao banco
#   automaticamente antes de cada consulta (mais previsível).
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# Base é a classe da qual todos os modelos herdam.
# O SQLAlchemy usa ela para descobrir quais tabelas existem.
class Base(DeclarativeBase):
    pass


# Esta função é uma "dependência" do FastAPI.
# Ela entrega uma sessão para cada requisição e GARANTE que
# a sessão será fechada no final, mesmo se ocorrer um erro.
# Vamos usá-la nas rotas na próxima etapa.
def get_db():
    db = SessionLocal()
    try:
        # "yield" entrega a sessão para a rota usar.
        # O código depois do yield roda quando a rota termina.
        yield db
    finally:
        # Sempre fecha a sessão, liberando a conexão.
        db.close()