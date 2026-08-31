"""
Testes unitários para app/core/chunking.py

Estratégia: testa chunk_por_paragrafo diretamente usando arquivos temporários
em memória. Nenhuma dependência externa (sem Gemini, sem ChromaDB).
"""
import os
import tempfile

import pytest

from app.core.chunking import chunk_por_paragrafo


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _arquivo_com(conteudo: str) -> str:
    """Cria um arquivo temporário com o conteúdo dado e retorna o caminho."""
    arq = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    )
    arq.write(conteudo)
    arq.close()
    return arq.name


# ---------------------------------------------------------------------------
# Cenário 1 – 4 parágrafos, janela=2, overlap=1
# ---------------------------------------------------------------------------

def test_quantidade_chunks_com_overlap():
    """
    4 parágrafos, janela=2, overlap=1 → passo = 1.
    Inícios: 0, 1, 2, 3 → 4 chunks.
    """
    conteudo = "Parágrafo A\n\nParágrafo B\n\nParágrafo C\n\nParágrafo D"
    caminho = _arquivo_com(conteudo)
    try:
        chunks = chunk_por_paragrafo(caminho, tamanho_janela=2, overlap=1)
        assert len(chunks) == 4
    finally:
        os.unlink(caminho)


def test_overlap_conteudo_correto():
    """
    Com overlap=1: o segundo parágrafo deve aparecer no chunk[0] E no chunk[1].
    """
    conteudo = "Parágrafo A\n\nParágrafo B\n\nParágrafo C"
    caminho = _arquivo_com(conteudo)
    try:
        chunks = chunk_por_paragrafo(caminho, tamanho_janela=2, overlap=1)
        assert "Parágrafo B" in chunks[0]
        assert "Parágrafo B" in chunks[1]
    finally:
        os.unlink(caminho)


# ---------------------------------------------------------------------------
# Cenário 2 – 1 único parágrafo
# ---------------------------------------------------------------------------

def test_unico_paragrafo_retorna_um_chunk():
    conteudo = "Somente um parágrafo aqui."
    caminho = _arquivo_com(conteudo)
    try:
        chunks = chunk_por_paragrafo(caminho)
        assert len(chunks) == 1
        assert chunks[0] == "Somente um parágrafo aqui."
    finally:
        os.unlink(caminho)


# ---------------------------------------------------------------------------
# Cenário 3 – texto completamente vazio
# ---------------------------------------------------------------------------

def test_texto_vazio_retorna_lista_vazia():
    caminho = _arquivo_com("")
    try:
        chunks = chunk_por_paragrafo(caminho)
        assert chunks == []
    finally:
        os.unlink(caminho)


# ---------------------------------------------------------------------------
# Cenário 4 – limpeza de espaços e tabs extras
# ---------------------------------------------------------------------------

def test_limpeza_espacos_extras():
    """Cada chunk não deve começar nem terminar com espaço em branco."""
    conteudo = "  Parágrafo com espaços  \n\n\t\tOutro parágrafo com tabs\t\t"
    caminho = _arquivo_com(conteudo)
    try:
        chunks = chunk_por_paragrafo(caminho)
        for chunk in chunks:
            assert chunk == chunk.strip(), f"Chunk não foi limpo: {repr(chunk)}"
    finally:
        os.unlink(caminho)


# ---------------------------------------------------------------------------
# Cenário 5 – múltiplas linhas em branco não geram chunks vazios
# ---------------------------------------------------------------------------

def test_multiplas_linhas_em_branco_nao_geram_chunks_vazios():
    conteudo = "Parágrafo A\n\n\n\n\nParágrafo B"
    caminho = _arquivo_com(conteudo)
    try:
        chunks = chunk_por_paragrafo(caminho)
        for chunk in chunks:
            assert chunk.strip() != "", "Chunk vazio encontrado"
    finally:
        os.unlink(caminho)


# ---------------------------------------------------------------------------
# Cenário 6 – sem overlap (overlap=0)
# ---------------------------------------------------------------------------

def test_sem_overlap_chunks_independentes():
    """
    Com overlap=0 e janela=2, passo=2.
    4 parágrafos → 2 chunks sem conteúdo compartilhado.
    """
    conteudo = "P1\n\nP2\n\nP3\n\nP4"
    caminho = _arquivo_com(conteudo)
    try:
        chunks = chunk_por_paragrafo(caminho, tamanho_janela=2, overlap=0)
        assert len(chunks) == 2
        assert "P1" in chunks[0] and "P2" in chunks[0]
        assert "P3" in chunks[1] and "P4" in chunks[1]
    finally:
        os.unlink(caminho)
