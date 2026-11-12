from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.config import settings

# recommended() configura o Argon2 com parâmetros seguros.
# O hash já embute um "salt" aleatório: duas pessoas com a mesma
# senha terminam com hashes diferentes.
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    # Transforma "minhasenha123" no hash que vai para o banco.
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Confere se a senha digitada corresponde ao hash salvo.
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    # Momento em que o token expira (sempre em UTC).
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    # Payload do token:
    # - "sub" (subject): quem é o dono do token. Por padrão do JWT
    #   precisa ser texto, por isso str(user_id).
    # - "exp": validade. O PyJWT rejeita tokens expirados sozinho.
    payload = {"sub": str(user_id), "exp": expire}

    # Assina o payload com a chave secreta.
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    # Verifica a assinatura e a validade; devolve o payload.
    # Se algo estiver errado, levanta jwt.InvalidTokenError.
    # Passar "algorithms" explicitamente é obrigatório por segurança:
    # impede que um atacante escolha um algoritmo mais fraco.
    return jwt.decode(
        token, settings.secret_key, algorithms=[settings.algorithm]
    )