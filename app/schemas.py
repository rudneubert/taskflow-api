from datetime import datetime

# BaseModel: classe base do Pydantic. Quem herda dela ganha
# validação automática de tipos.
# Field: permite adicionar regras extras a um campo.
# ConfigDict: configurações do schema.
from pydantic import BaseModel, ConfigDict, Field


# Schema de ENTRADA para criar uma tarefa.
# É o que o cliente envia no POST.
class TaskCreate(BaseModel):
    # min_length=1: não aceita título vazio.
    # max_length=100: igual ao limite da coluna no banco.
    title: str = Field(min_length=1, max_length=100)

    # Descrição é opcional; se não for enviada, vale None.
    description: str | None = None


# Schema de ENTRADA para atualizar uma tarefa (PATCH).
# Todos os campos são opcionais, porque o cliente envia
# apenas o que quer alterar.
class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    completed: bool | None = None


# Schema de SAÍDA: o que a API devolve ao cliente.
# Inclui campos que o servidor gera (id, created_at).
class TaskResponse(BaseModel):
    # from_attributes=True permite criar este schema a partir de
    # um objeto do SQLAlchemy (models.Task). Sem isso, o Pydantic
    # só aceitaria dicionários.
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    completed: bool
    created_at: datetime