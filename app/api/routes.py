"""
Endpoints da API REST do Corporate Docs Assistant.

Rotas disponíveis:
    POST /ask      → executa o pipeline RAG e retorna a resposta gerada
    GET  /history  → retorna o histórico de interações salvas no SQLite
    GET  /health   → verifica se a API está no ar
"""

from fastapi import APIRouter, HTTPException, Query

from app.core.rag_pipeline import executar_pipeline
from app.db.repository import buscar_historico
from app.schemas import HistoricoResponse, LogEntry, PerguntaRequest, RespostaResponse

router = APIRouter()


@router.post("/ask", response_model=RespostaResponse, summary="Faz uma pergunta aos documentos")
def ask(body: PerguntaRequest):
    """Recebe uma pergunta em linguagem natural, executa o pipeline RAG
    (retrieval no ChromaDB + geração com Gemini 2.5 Flash) e retorna a
    resposta gerada com as fontes e o id do log salvo.
    """
    try:
        resultado = executar_pipeline(body.pergunta)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro no pipeline RAG: {exc}") from exc

    return RespostaResponse(
        resposta=resultado["resposta"],
        fontes=resultado["fontes"],
        log_id=resultado["log_id"],
    )


@router.get("/history", response_model=HistoricoResponse, summary="Retorna o histórico de perguntas")
def history(limite: int = Query(default=20, ge=1, le=100, description="Número máximo de entradas")):
    """Retorna as últimas interações registradas no banco SQLite,
    em ordem decrescente de data (mais recente primeiro).
    """
    try:
        entradas = buscar_historico(limite)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar histórico: {exc}") from exc

    return HistoricoResponse(
        historico=[LogEntry(**entrada) for entrada in entradas]
    )


@router.get("/health", summary="Health check")
def health():
    """Verifica se a API está no ar. Retorna status 200 com {'status': 'ok'}."""
    return {"status": "ok"}
