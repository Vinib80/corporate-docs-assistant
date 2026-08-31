"""
Ponto de entrada da aplicação FastAPI.

Como executar (na raiz do projeto, com o venv ativo):
    uvicorn app.main:app --reload

Documentação interativa gerada automaticamente:
    http://localhost:8000/docs
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Garante que o banco SQLite e a tabela de logs existem antes
    de a API começar a receber requisições."""
    init_db()
    yield


app = FastAPI(
    title="Corporate Docs Assistant",
    description=(
        "MVP de Assistente Inteligente Corporativo: responde perguntas "
        "em linguagem natural com base em documentos internos, sempre citando a fonte."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)
