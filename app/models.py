from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
# relationship: liga dois models, permitindo navegar de um ao outro
# em Python (task.owner, user.tasks).
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # unique=True: o banco impede dois usuários com o mesmo e-mail,
    # mesmo que o código da API falhe em verificar.
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    # Guardamos o HASH, nunca a senha original.
    hashed_password: Mapped[str] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    # Lado "um" da relação um-para-muitos: um usuário tem várias tarefas.
    # back_populates liga este lado ao atributo "owner" de Task.
    # cascade="all, delete-orphan": se o usuário for apagado, suas
    # tarefas são apagadas junto (não ficam "órfãs" no banco).
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text, default=None)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    # Chave estrangeira: guarda o id do dono na tabela users.
    # É o que cria a ligação "esta tarefa pertence àquele usuário".
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    # Lado "muitos" da relação: cada tarefa tem um dono.
    owner: Mapped["User"] = relationship(back_populates="tasks")