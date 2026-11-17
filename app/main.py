from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app import models  # noqa: F401  (registra as tabelas na Base)
from app.database import Base, engine
from app.routers import auth, tasks

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TaskFlow API",
    description="API REST para gerenciamento de tarefas com autenticação JWT.",
    version="0.3.0",
)

# Middleware é um código que roda em TODA requisição, antes das rotas.
# O CORSMiddleware responde ao navegador dizendo quais origens podem
# chamar a API.
app.add_middleware(
    CORSMiddleware,
    # Transforma "a,b,c" em ["a", "b", "c"], removendo espaços.
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_methods=["*"],   # GET, POST, PATCH, DELETE...
    allow_headers=["*"],   # inclui o cabeçalho Authorization
)


app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}