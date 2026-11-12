from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Diz onde procurar as variáveis: no arquivo .env e também nas
    # variáveis de ambiente do sistema (que é o que servidores de
    # deploy usam). O Pydantic faz a correspondência ignorando
    # maiúsculas: o campo "secret_key" lê a variável SECRET_KEY.
    model_config = SettingsConfigDict(env_file=".env")

    # Sem valor padrão: é OBRIGATÓRIO. Se faltar, a aplicação nem
    # inicia e mostra um erro claro. É melhor falhar cedo do que rodar
    # com uma chave insegura.
    secret_key: str

    # Algoritmo usado para assinar o token. HS256 é o padrão e usa
    # uma única chave secreta.
    algorithm: str = "HS256"

    # Tempo de vida do token. Depois disso, é preciso fazer login de novo.
    access_token_expire_minutes: int = 30


# Instância única, importada pelo resto do projeto.
settings = Settings()