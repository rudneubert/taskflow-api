from datetime import datetime

# BaseModel: classe base do Pydantic. Quem herda dela ganha
# validação automática de tipos.
# Field: permite adicionar regras extras a um campo.
# ConfigDict: configurações do schema.
from pydantic import BaseModel, ConfigDict, Field, EmailStr


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
    

# ---------- Usuários e autenticação ----------

# Entrada do cadastro.
class UserCreate(BaseModel):
    # EmailStr valida o formato do e-mail (precisa ter @, domínio etc.).
    email: EmailStr

    # Mínimo de 8 caracteres. O máximo evita abuso: hashes de senhas
    # gigantescas consomem CPU do servidor.
    password: str = Field(min_length=8, max_length=128)


# Saída: o que a API devolve sobre um usuário.
# Repare que NÃO existe campo de senha aqui. Como o response_model
# filtra tudo que não está no schema, o hash jamais vaza na resposta.
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime


# Resposta do login. O formato (access_token + token_type) é o padrão
# do protocolo OAuth2, e a documentação /docs espera exatamente isso.
class Token(BaseModel):
    access_token: str
    token_type: str