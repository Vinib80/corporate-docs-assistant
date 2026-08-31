from pathlib import Path

import chromadb

# Caminho absoluto da pasta onde o ChromaDB persiste os dados em arquivo
_CHROMA_PATH = str(Path(__file__).resolve().parent.parent.parent / "chroma_db")
_COLLECTION_NAME = "documentos"

# Cliente persistente: os dados sobrevivem entre execuções do processo
_client = chromadb.PersistentClient(path=_CHROMA_PATH)


def obter_colecao() -> chromadb.Collection:
    
    return _client.get_or_create_collection(
        name=_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # distância cosseno para textos
    )


def adicionar_chunks(chunks_com_meta: list[dict]) -> None:
    
    colecao = obter_colecao()

    ids        = [c["id"]        for c in chunks_com_meta]
    documentos = [c["texto"]     for c in chunks_com_meta]
    embeddings = [c["embedding"] for c in chunks_com_meta]
    metadados  = [{"fonte": c["fonte"]} for c in chunks_com_meta]

    colecao.upsert(
        ids=ids,
        documents=documentos,
        embeddings=embeddings,
        metadatas=metadados,
    )


def buscar_similares(embedding_query: list[float], top_k: int = 3) -> list[dict]:
    
    colecao = obter_colecao()

    resultados = colecao.query(
        query_embeddings=[embedding_query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks_retornados = []
    for texto, meta, dist in zip(
        resultados["documents"][0],
        resultados["metadatas"][0],
        resultados["distances"][0],
    ):
        chunks_retornados.append(
            {
                "texto": texto,
                "fonte": meta["fonte"],
                "distancia": dist,
            }
        )

    return chunks_retornados
