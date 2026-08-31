"""
Pipeline RAG completo: une retrieval e geração numa única função pública.

Fluxo:
    pergunta
      → embedding da pergunta (task_type=RETRIEVAL_QUERY)
      → busca top-k chunks similares no ChromaDB
      → geração da resposta com Gemini 3.5 Flash
      → log da interação salvo no SQLite
      → retorno da resposta, fontes e log_id
"""

from app.core.embeddings import gerar_embedding
from app.core.generation import gerar_resposta
from app.core.vector_store import buscar_similares
from app.db.repository import salvar_log


def executar_pipeline(pergunta: str, top_k: int = 3) -> dict:
    
    
    embedding_query = gerar_embedding(pergunta, task_type="RETRIEVAL_QUERY")

    chunks = buscar_similares(embedding_query, top_k=top_k)

    resultado = gerar_resposta(pergunta, chunks)

    log_id = salvar_log(
        pergunta=pergunta,
        resposta=resultado["resposta"],
        fontes=resultado["fontes"],
    )

    return {
        "resposta": resultado["resposta"],
        "fontes": resultado["fontes"],
        "log_id": log_id,
    }
