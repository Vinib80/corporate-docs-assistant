"""
Testes de integração para app/core/vector_store.py

Estratégia: usa chromadb.EphemeralClient() (sem persistência em arquivo) para
isolar completamente os testes do chroma_db/ de produção. Os embeddings são
vetores aleatórios fixos (não chamamos a API do Gemini): o objetivo é testar
a interface com o ChromaDB, não a qualidade semântica dos vetores.
"""
import random
from unittest.mock import patch, MagicMock

import chromadb
import pytest

import app.core.vector_store as vs_module
from app.core.vector_store import adicionar_chunks, buscar_similares


# ---------------------------------------------------------------------------
# Dimensão dos vetores usada pelo gemini-embedding-001
# ---------------------------------------------------------------------------
EMBEDDING_DIM = 768


def _vetor_aleatorio(seed: int = 0) -> list[float]:
    """Vetor unitário de dimensão EMBEDDING_DIM, reproducível por seed."""
    random.seed(seed)
    vetor = [random.gauss(0, 1) for _ in range(EMBEDDING_DIM)]
    norma = sum(v ** 2 for v in vetor) ** 0.5
    return [v / norma for v in vetor]


# ---------------------------------------------------------------------------
# Fixture: coleção efêmera isolada por teste
# ---------------------------------------------------------------------------

@pytest.fixture()
def colecao_efemera(monkeypatch):
    """
    Substitui obter_colecao para usar um EphemeralClient com um nome de
    coleção único por teste (uuid4). Isso garante isolamento mesmo que o
    EphemeralClient compartilhe estado global em memória entre testes
    consecutivos na mesma sessão pytest.
    """
    import uuid

    client_efemero = chromadb.EphemeralClient()
    # Nome único por invocação: garante que testes não compartilham coleção
    nome_colecao = f"teste_{uuid.uuid4().hex}"

    def _obter_colecao_efemera():
        return client_efemero.get_or_create_collection(
            name=nome_colecao,
            metadata={"hnsw:space": "cosine"},
        )

    monkeypatch.setattr(vs_module, "obter_colecao", _obter_colecao_efemera)
    return _obter_colecao_efemera()


# ---------------------------------------------------------------------------
# Cenário 1 – chunks inseridos aparecem nos resultados da busca
# ---------------------------------------------------------------------------

def test_chunks_inseridos_aparecem_na_busca(colecao_efemera):
    chunks = [
        {
            "id": "doc1_chunk0",
            "texto": "Política de férias: 30 dias corridos.",
            "embedding": _vetor_aleatorio(seed=1),
            "fonte": "politica_ferias.md",
        }
    ]
    adicionar_chunks(chunks)

    resultado = buscar_similares(_vetor_aleatorio(seed=1), top_k=1)
    assert len(resultado) == 1
    assert resultado[0]["texto"] == "Política de férias: 30 dias corridos."
    assert resultado[0]["fonte"] == "politica_ferias.md"


# ---------------------------------------------------------------------------
# Cenário 2 – busca retorna no máximo top_k resultados
# ---------------------------------------------------------------------------

def test_busca_respeita_top_k(colecao_efemera):
    chunks = [
        {
            "id": f"doc_chunk{i}",
            "texto": f"Texto do chunk {i}",
            "embedding": _vetor_aleatorio(seed=i),
            "fonte": "doc.md",
        }
        for i in range(10)
    ]
    adicionar_chunks(chunks)

    resultado = buscar_similares(_vetor_aleatorio(seed=99), top_k=3)
    assert len(resultado) == 3


# ---------------------------------------------------------------------------
# Cenário 3 – cada resultado possui os campos obrigatórios
# ---------------------------------------------------------------------------

def test_formato_dos_resultados(colecao_efemera):
    chunks = [
        {
            "id": "chunk_formato",
            "texto": "Conteúdo de exemplo.",
            "embedding": _vetor_aleatorio(seed=42),
            "fonte": "manual.md",
        }
    ]
    adicionar_chunks(chunks)

    resultado = buscar_similares(_vetor_aleatorio(seed=42), top_k=1)
    assert len(resultado) == 1
    item = resultado[0]
    assert "texto" in item
    assert "fonte" in item
    assert "distancia" in item


# ---------------------------------------------------------------------------
# Cenário 4 – upsert com mesmo ID não duplica o registro
# ---------------------------------------------------------------------------

def test_upsert_nao_duplica_registro(colecao_efemera):
    chunk = {
        "id": "chunk_unico",
        "texto": "Versão original.",
        "embedding": _vetor_aleatorio(seed=7),
        "fonte": "doc.md",
    }
    adicionar_chunks([chunk])
    # Upsert com mesmo ID, texto diferente
    chunk["texto"] = "Versão atualizada."
    adicionar_chunks([chunk])

    resultado = buscar_similares(_vetor_aleatorio(seed=7), top_k=5)
    # Deve existir apenas 1 item na coleção
    assert len(resultado) == 1
    assert resultado[0]["texto"] == "Versão atualizada."


# ---------------------------------------------------------------------------
# Cenário 5 – distância retornada é um número (float)
# ---------------------------------------------------------------------------

def test_distancia_e_numerica(colecao_efemera):
    chunks = [
        {
            "id": "chunk_dist",
            "texto": "Texto para teste de distância.",
            "embedding": _vetor_aleatorio(seed=3),
            "fonte": "doc.md",
        }
    ]
    adicionar_chunks(chunks)

    resultado = buscar_similares(_vetor_aleatorio(seed=3), top_k=1)
    assert isinstance(resultado[0]["distancia"], (int, float))
