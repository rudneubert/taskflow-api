from fastapi import APIRouter, Depends, HTTPException, status
# OAuth2PasswordRequestForm: lê o formulário de login padrão
# (campos "username" e "password").
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # Normaliza o e-mail para minúsculas, evitando contas duplicadas
    # como "Ana@x.com" e "ana@x.com".
    email = user_in.email.lower()

    # Verifica se o e-mail já está em uso.
    existing = db.scalar(select(models.User).where(models.User.email == email))
    if existing is not None:
        # 409 Conflict: o pedido conflita com o estado atual.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado",
        )

    # Cria o usuário guardando apenas o HASH da senha.
    user = models.User(email=email, hashed_password=hash_password(user_in.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=schemas.Token)
# Diferente das outras rotas, o login recebe um FORMULÁRIO
# (application/x-www-form-urlencoded), não JSON. É o padrão OAuth2
# e o que permite o botão "Authorize" do /docs funcionar.
# O campo se chama "username", mas nós o usamos como e-mail.
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.scalar(
        select(models.User).where(models.User.email == form_data.username.lower())
    )

    # Mesma mensagem para "e-mail não existe" e "senha errada".
    # Se fossem diferentes, um atacante descobriria quais e-mails
    # possuem conta. Isso se chama enumeração de usuários.
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Gera o token com o id do usuário e devolve.
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }