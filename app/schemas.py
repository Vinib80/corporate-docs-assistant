from datetime import datetime

from pydantic import BaseModel


class PerguntaRequest(BaseModel):
    """Corpo da requisição do endpoint POST /ask."""
    pergunta: str


class RespostaResponse(BaseModel):
    """Corpo da resposta do endpoint POST /ask."""
    resposta: str
    fontes: list[str]
    log_id: int


class LogEntry(BaseModel):
    """Representa uma entrada do histórico de interações."""
    id: int
    pergunta: str
    resposta: str
    fontes: list[str]
    created_at: datetime


class HistoricoResponse(BaseModel):
    """Corpo da resposta do endpoint GET /history."""
    historico: list[LogEntry]
