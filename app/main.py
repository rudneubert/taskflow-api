from fastapi import FastAPI

# Importamos o engine e a Base para criar as tabelas.
from app.database import Base, engine

# IMPORTANTE: precisamos importar o módulo models, mesmo sem usar
# nada dele diretamente. É a importação que "registra" a classe Task
# na Base. Sem ela, create_all não saberia que a tabela existe.
from app import models  # noqa: F401

# Cria no banco todas as tabelas registradas na Base que ainda
# não existem. Se a tabela "tasks" já existir, nada é alterado.
# (Mais adiante, usaremos Alembic para migrações profissionais.)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TaskFlow API",
    description="API REST para gerenciamento de tarefas.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}