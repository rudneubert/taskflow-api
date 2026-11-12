from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.dependencies import get_current_user

# dependencies=[...] no router aplica a exigência de login a TODAS as
# rotas deste arquivo de uma vez. Ainda precisamos do usuário dentro
# das funções, por isso cada uma também declara current_user.
router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    dependencies=[Depends(get_current_user)],
)


# Função auxiliar (começa com "_" por ser de uso interno do arquivo).
# Busca a tarefa pelo id SOMENTE se ela pertencer ao usuário.
# Isso evita repetir o mesmo código em get, update e delete.
def _get_owned_task(db: Session, task_id: int, user: models.User) -> models.Task:
    task = db.scalar(
        select(models.Task).where(
            models.Task.id == task_id,
            models.Task.owner_id == user.id,
        )
    )
    # Se a tarefa existe mas é de OUTRO usuário, também devolvemos 404.
    # Responder 403 ("proibido") confirmaria que o id existe. Com 404,
    # não vazamos nenhuma informação sobre tarefas alheias.
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa não encontrada",
        )
    return task


@router.post(
    "",
    response_model=schemas.TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    task_in: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # O dono vem do TOKEN, nunca do corpo da requisição. Assim o
    # cliente não consegue criar tarefas em nome de outra pessoa.
    task = models.Task(**task_in.model_dump(), owner_id=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("", response_model=list[schemas.TaskResponse])
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    completed: bool | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Parte sempre do filtro por dono: só as tarefas do usuário logado.
    query = select(models.Task).where(models.Task.owner_id == current_user.id)

    if completed is not None:
        query = query.where(models.Task.completed == completed)

    query = query.order_by(models.Task.created_at.desc()).offset(skip).limit(limit)
    return db.scalars(query).all()


@router.get("/{task_id}", response_model=schemas.TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return _get_owned_task(db, task_id, current_user)


@router.patch("/{task_id}", response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task_in: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = _get_owned_task(db, task_id, current_user)

    for field, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    task = _get_owned_task(db, task_id, current_user)
    db.delete(task)
    db.commit()