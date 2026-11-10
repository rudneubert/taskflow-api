# Importa a classe principal do FastAPI.
from fastapi import FastAPI

# Cria a aplicação. Este objeto "app" é o coração da API:
# é nele que registramos todas as rotas (endpoints).
# Os parâmetros title, description e version aparecem
# automaticamente na documentação gerada pelo FastAPI.
app = FastAPI(
    title="TaskFlow API",
    description="API REST para gerenciamento de tarefas.",
    version="0.1.0",
)


# O decorador @app.get("/health") diz ao FastAPI:
# "quando alguém fizer uma requisição GET para o caminho /health,
# execute a função logo abaixo".
@app.get("/health")
def health_check():
    # Retornamos um dicionário Python. O FastAPI converte
    # automaticamente para JSON na resposta.
    return {"status": "ok"}