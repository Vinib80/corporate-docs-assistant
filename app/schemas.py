from datetime import datetime

from pydantic import BaseModel


class PerguntaRequest(BaseModel):
    pergunta: str


class RespostaResponse(BaseModel):
    resposta: str
    fontes: list[str]
    log_id: int


class LogEntry(BaseModel):
    id: int
    pergunta: str
    resposta: str
    fontes: list[str]
    created_at: datetime


class HistoricoResponse(BaseModel):
    historico: list[LogEntry]
