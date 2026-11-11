from datetime import datetime, timezone

# Tipos de coluna que vamos usar na tabela.
from sqlalchemy import Boolean, DateTime, String, Text
# Mapped e mapped_column: forma moderna (SQLAlchemy 2.0) de
# declarar colunas com tipagem do Python.
from sqlalchemy.orm import Mapped, mapped_column

# Importamos a Base criada no database.py.
from app.database import Base


def utc_now() -> datetime:
    # Função auxiliar que devolve a data/hora atual em UTC.
    # Guardar em UTC é boa prática: evita confusão de fuso horário.
    return datetime.now(timezone.utc)


# Esta classe representa a tabela "tasks".
# Herdar de Base é o que a registra como tabela no SQLAlchemy.
class Task(Base):
    # Nome da tabela no banco.
    __tablename__ = "tasks"

    # Chave primária: identificador único de cada tarefa.
    # O banco gera 1, 2, 3... automaticamente.
    # index=True cria um índice, que acelera buscas por id.
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Título da tarefa: texto de até 100 caracteres, obrigatório.
    title: Mapped[str] = mapped_column(String(100))

    # Descrição: texto longo e opcional.
    # "str | None" significa que o valor pode ser texto ou nulo.
    description: Mapped[str | None] = mapped_column(Text, default=None)

    # Indica se a tarefa foi concluída. Começa como False.
    completed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Data de criação, preenchida automaticamente com utc_now.
    # Passamos a função SEM parênteses: o SQLAlchemy a chama
    # no momento de salvar cada registro.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )