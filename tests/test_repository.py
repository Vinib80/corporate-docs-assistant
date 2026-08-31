"""
Testes de integração para app/db/repository.py

Estratégia: cada teste cria um banco SQLite em arquivo temporário e redireciona
app.db.database.DB_PATH para esse arquivo via monkeypatch. Assim o banco de
produção (corporate_docs.db) nunca é tocado.
"""
import json
import sqlite3
import tempfile
from pathlib import Path

import pytest

import app.db.database as database_module
from app.db.database import init_db
from app.db.repository import buscar_historico, salvar_log


# ---------------------------------------------------------------------------
# Fixture: banco temporário isolado por teste
# ---------------------------------------------------------------------------

@pytest.fixture()
def banco_tmp(monkeypatch, tmp_path):
    """
    Cria um arquivo .db temporário, aponta DB_PATH para ele,
    inicializa a tabela e devolve o caminho.
    Após o teste, o arquivo é deletado automaticamente pelo pytest (tmp_path).
    """
    caminho_db = tmp_path / "test.db"
    monkeypatch.setattr(database_module, "DB_PATH", caminho_db)
    init_db()
    return caminho_db


# ---------------------------------------------------------------------------
# Cenário 1 – salvar_log retorna um ID inteiro positivo
# ---------------------------------------------------------------------------

def test_salvar_log_retorna_id_inteiro_positivo(banco_tmp):
    log_id = salvar_log(
        pergunta="Quantos dias de férias tenho?",
        resposta="30 dias corridos.",
        fontes=["politica_ferias.md"],
    )
    assert isinstance(log_id, int)
    assert log_id > 0


# ---------------------------------------------------------------------------
# Cenário 2 – registro salvo aparece no histórico
# ---------------------------------------------------------------------------

def test_log_salvo_aparece_no_historico(banco_tmp):
    salvar_log(
        pergunta="Qual é a política de acesso?",
        resposta="Acesso via VPN obrigatório.",
        fontes=["manual_seguranca.md"],
    )
    historico = buscar_historico()
    assert len(historico) == 1
    entrada = historico[0]
    assert entrada["pergunta"] == "Qual é a política de acesso?"
    assert entrada["resposta"] == "Acesso via VPN obrigatório."
    assert entrada["fontes"] == ["manual_seguranca.md"]


# ---------------------------------------------------------------------------
# Cenário 3 – buscar_historico respeita o parâmetro limite
# ---------------------------------------------------------------------------

def test_buscar_historico_respeita_limite(banco_tmp):
    for i in range(5):
        salvar_log(
            pergunta=f"Pergunta {i}",
            resposta=f"Resposta {i}",
            fontes=["doc.md"],
        )
    historico = buscar_historico(limite=2)
    assert len(historico) == 2


# ---------------------------------------------------------------------------
# Cenário 4 – banco vazio retorna lista vazia
# ---------------------------------------------------------------------------

def test_banco_vazio_retorna_lista_vazia(banco_tmp):
    historico = buscar_historico()
    assert historico == []


# ---------------------------------------------------------------------------
# Cenário 5 – campo fontes é serializado como JSON e recuperado como lista
# ---------------------------------------------------------------------------

def test_fontes_serializacao_e_desserializacao(banco_tmp):
    fontes_originais = ["doc_a.md", "doc_b.md", "doc_c.md"]
    salvar_log(
        pergunta="Pergunta de múltiplas fontes",
        resposta="Resposta combinada.",
        fontes=fontes_originais,
    )
    historico = buscar_historico()
    assert historico[0]["fontes"] == fontes_originais
    assert isinstance(historico[0]["fontes"], list)


# ---------------------------------------------------------------------------
# Cenário 6 – IDs são autoincrementados corretamente
# ---------------------------------------------------------------------------

def test_ids_sao_autoincrementados(banco_tmp):
    id1 = salvar_log("P1", "R1", [])
    id2 = salvar_log("P2", "R2", [])
    id3 = salvar_log("P3", "R3", [])
    assert id2 == id1 + 1
    assert id3 == id2 + 1


# ---------------------------------------------------------------------------
# Cenário 7 – historico retorna entradas em ordem decrescente de data
# ---------------------------------------------------------------------------

def test_historico_ordem_decrescente(banco_tmp):
    """
    Insere os logs com timestamps explícitos e distintos diretamente via SQL,
    evitando a ambiguidade de CURRENT_TIMESTAMP (resolução de segundos) quando
    os três INSERTs ocorrem dentro do mesmo segundo.
    """
    import sqlite3 as _sqlite3

    conn = _sqlite3.connect(str(banco_tmp))
    conn.execute(
        "INSERT INTO logs (pergunta, resposta, fontes, created_at) VALUES (?, ?, ?, ?)",
        ("Primeira", "R1", "[]", "2024-01-01 10:00:00"),
    )
    conn.execute(
        "INSERT INTO logs (pergunta, resposta, fontes, created_at) VALUES (?, ?, ?, ?)",
        ("Segunda", "R2", "[]", "2024-01-01 11:00:00"),
    )
    conn.execute(
        "INSERT INTO logs (pergunta, resposta, fontes, created_at) VALUES (?, ?, ?, ?)",
        ("Terceira", "R3", "[]", "2024-01-01 12:00:00"),
    )
    conn.commit()
    conn.close()

    historico = buscar_historico()
    # ORDER BY created_at DESC → mais recente primeiro
    assert historico[0]["pergunta"] == "Terceira"
    assert historico[-1]["pergunta"] == "Primeira"
