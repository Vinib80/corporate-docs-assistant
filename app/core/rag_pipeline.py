"""
Pipeline RAG completo: une retrieval e geração numa única função pública.

Fluxo:
    pergunta
      → embedding da pergunta (task_type=RETRIEVAL_QUERY)
      → busca top-k chunks similares no ChromaDB
      → geração da resposta com Gemini 2.5 Flash
      → log da interação salvo no SQLite
      → retorno da resposta, fontes e log_id
"""

from app.core.embeddings import gerar_embedding
from app.core.generation import gerar_resposta
from app.core.vector_store import buscar_similares
from app.db.repository import salvar_log


def executar_pipeline(pergunta: str, top_k: int = 3) -> dict:
    """Executa o pipeline RAG completo para uma pergunta.

    Args:
        pergunta: Pergunta do usuário em linguagem natural.
        top_k:    Número de chunks a recuperar do ChromaDB (padrão: 3).

    Returns:
        Dict com:
            - 'resposta': texto gerado pelo Gemini.
            - 'fontes':   lista de nomes de arquivo usados como contexto.
            - 'log_id':   id do registro salvo no SQLite.
    """
    # 1. Gerar embedding da pergunta (task_type diferente da ingestão!)
    #    RETRIEVAL_QUERY → vetor otimizado para busca
    #    RETRIEVAL_DOCUMENT → vetor otimizado para indexação
    embedding_query = gerar_embedding(pergunta, task_type="RETRIEVAL_QUERY")

    # 2. Recuperar os top_k chunks mais similares do ChromaDB
    chunks = buscar_similares(embedding_query, top_k=top_k)

    # 3. Gerar a resposta contextualizada com o LLM
    resultado = gerar_resposta(pergunta, chunks)

    # 4. Persistir a interação no histórico SQLite
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
