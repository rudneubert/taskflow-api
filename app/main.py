from fastapi import FastAPI

from app import models  # noqa: F401  (registra a tabela na Base)
from app.database import Base, engine
# Importamos o router de tarefas.
from app.routers import tasks

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TaskFlow API",
    description="API REST para gerenciamento de tarefas.",
    version="0.2.0",
)

# Registra o router na aplicação. A partir daqui, todas as
# rotas definidas em tasks.py passam a existir na API.
app.include_router(tasks.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}