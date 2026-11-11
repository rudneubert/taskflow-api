from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

# Cria o router.
# prefix="/tasks": todas as rotas daqui começam com /tasks.
# tags=["tasks"]: agrupa as rotas na documentação /docs.
router = APIRouter(prefix="/tasks", tags=["tasks"])


# ---------- CREATE ----------
# status_code=201: devolve "Created" em vez do 200 padrão.
# response_model: o FastAPI converte o retorno para este schema,
# filtrando qualquer campo que não pertença a ele.
@router.post(
    "",
    response_model=schemas.TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
# Os parâmetros da função são "injetados" pelo FastAPI:
# - task_in: vem do corpo JSON da requisição, validado pelo TaskCreate.
# - db: sessão do banco, entregue pela função get_db (Depends).
def create_task(task_in: schemas.TaskCreate, db: Session = Depends(get_db)):
    # model_dump() transforma o schema em dicionário;
    # ** "espalha" o dicionário como argumentos nomeados.
    # Equivale a: models.Task(title=..., description=...)
    task = models.Task(**task_in.model_dump())

    db.add(task)       # coloca o objeto na sessão (ainda não gravou)
    db.commit()        # grava de fato no banco
    db.refresh(task)   # recarrega o objeto para pegar id e created_at
    return task


# ---------- READ (lista) ----------
# Parâmetros simples da função (skip, limit) viram "query params":
# /tasks?skip=0&limit=10  (paginação básica)
@router.get("", response_model=list[schemas.TaskResponse])
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    completed: bool | None = None,   # filtro opcional: /tasks?completed=true
    db: Session = Depends(get_db),
):
    # select(models.Task) equivale a "SELECT * FROM tasks".
    query = select(models.Task)

    # Só aplica o filtro se o cliente o enviou.
    if completed is not None:
        query = query.where(models.Task.completed == completed)

    # order_by: mais recentes primeiro.
    # offset/limit: pulam "skip" registros e devolvem no máximo "limit".
    query = query.order_by(models.Task.created_at.desc()).offset(skip).limit(limit)

    # scalars().all() executa a consulta e devolve uma lista de Task.
    return db.scalars(query).all()


# ---------- READ (uma) ----------
# {task_id} na rota é uma variável de caminho.
# O FastAPI converte para int automaticamente (por causa do ": int").
@router.get("/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    # db.get busca direto pela chave primária.
    task = db.get(models.Task, task_id)

    # Se não existir, devolve erro 404 com uma mensagem.
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada",
        )
    return task


# ---------- UPDATE ----------
@router.patch("/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task_in: schemas.TaskUpdate,
    db: Session = Depends(get_db),
):
    task = db.get(models.Task, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada",
        )

    # exclude_unset=True é a chave do PATCH: o dicionário traz
    # SOMENTE os campos que o cliente realmente enviou.
    # Assim, enviar só {"completed": true} não apaga o título.
    changes = task_in.model_dump(exclude_unset=True)

    # Para cada campo enviado, atualiza o atributo do objeto.
    # setattr(task, "title", "novo") equivale a task.title = "novo".
    for field, value in changes.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


# ---------- DELETE ----------
# 204: sucesso sem corpo de resposta.
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada",
        )

    db.delete(task)
    db.commit()
    # Não retornamos nada: o 204 não tem corpo.