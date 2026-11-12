from fastapi import FastAPI

from app import models  # noqa: F401  (registra as tabelas na Base)
from app.database import Base, engine
from app.routers import auth, tasks

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TaskFlow API",
    description="API REST para gerenciamento de tarefas com autenticação JWT.",
    version="0.3.0",
)

app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}