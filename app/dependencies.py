import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.security import decode_access_token

# Diz ao FastAPI: "o token vem no cabeçalho Authorization: Bearer ...".
# tokenUrl indica a rota de login, e é o que faz aparecer o botão
# "Authorize" na página /docs.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    # Erro padrão para qualquer problema com o token.
    # O cabeçalho WWW-Authenticate é exigido pela especificação HTTP
    # em respostas 401.
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        # Converte o "sub" (texto) de volta para número.
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        # InvalidTokenError: assinatura errada, token expirado ou malformado.
        # KeyError: o token não tem o campo "sub".
        # ValueError: o "sub" não é um número.
        raise credentials_error

    # O token pode ser válido, mas o usuário pode ter sido apagado.
    user = db.get(models.User, user_id)
    if user is None:
        raise credentials_error

    return user