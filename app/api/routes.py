from fastapi import APIRouter, HTTPException, Query

from app.core.rag_pipeline import executar_pipeline
from app.db.repository import buscar_historico
from app.schemas import HistoricoResponse, LogEntry, PerguntaRequest, RespostaResponse

router = APIRouter()


@router.post("/ask", response_model=RespostaResponse, summary="Faz uma pergunta aos documentos")
def ask(body: PerguntaRequest):
    
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

    try:
        entradas = buscar_historico(limite)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar histórico: {exc}") from exc

    return HistoricoResponse(
        historico=[LogEntry(**entrada) for entrada in entradas]
    )


@router.get("/health", summary="Health check")
def health():
    
    return {"status": "ok"}
