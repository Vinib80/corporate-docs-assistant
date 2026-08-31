"""
Testes da camada HTTP para app/api/routes.py

Estratégia: usa FastAPI TestClient (HTTPX síncrono embutido no FastAPI).
Todos os módulos externos (pipeline RAG, Gemini, ChromaDB) são mockados via
unittest.mock.patch — nenhuma chamada real à API é feita.

O TestClient é criado importando diretamente o router (sem o lifespan de
produção que chama init_db), para evitar efeitos colaterais no banco real.
"""
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import router


# ---------------------------------------------------------------------------
# App de teste sem lifespan (não executa init_db)
# ---------------------------------------------------------------------------

app_teste = FastAPI()
app_teste.include_router(router)
client = TestClient(app_teste)


# ---------------------------------------------------------------------------
# Dados fictícios reutilizados nos testes
# ---------------------------------------------------------------------------

PIPELINE_RESULTADO_OK = {
    "resposta": "De acordo com a política, você tem 30 dias de férias.",
    "fontes": ["politica_ferias.md"],
    "log_id": 1,
}

HISTORICO_RESULTADO_OK = [
    {
        "id": 1,
        "pergunta": "Quantos dias de férias?",
        "resposta": "30 dias.",
        "fontes": ["politica_ferias.md"],
        "created_at": "2024-01-01T12:00:00",
    }
]


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

def test_health_retorna_200_e_status_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# POST /ask – caminho feliz (pipeline mockado com sucesso)
# ---------------------------------------------------------------------------

@patch("app.api.routes.executar_pipeline", return_value=PIPELINE_RESULTADO_OK)
def test_ask_retorna_200_com_campos_corretos(mock_pipeline):
    response = client.post("/ask", json={"pergunta": "Quantos dias de férias tenho?"})
    assert response.status_code == 200
    corpo = response.json()
    assert "resposta" in corpo
    assert "fontes" in corpo
    assert "log_id" in corpo
    assert isinstance(corpo["fontes"], list)
    assert isinstance(corpo["log_id"], int)


@patch("app.api.routes.executar_pipeline", return_value=PIPELINE_RESULTADO_OK)
def test_ask_conteudo_da_resposta_e_correto(mock_pipeline):
    response = client.post("/ask", json={"pergunta": "Pergunta qualquer"})
    corpo = response.json()
    assert corpo["resposta"] == PIPELINE_RESULTADO_OK["resposta"]
    assert corpo["fontes"] == PIPELINE_RESULTADO_OK["fontes"]
    assert corpo["log_id"] == PIPELINE_RESULTADO_OK["log_id"]


# ---------------------------------------------------------------------------
# POST /ask – body inválido (Pydantic deve rejeitar com 422)
# ---------------------------------------------------------------------------

def test_ask_sem_campo_pergunta_retorna_422():
    """Body sem o campo obrigatório 'pergunta' deve gerar erro de validação."""
    response = client.post("/ask", json={"outra_coisa": "valor"})
    assert response.status_code == 422


def test_ask_body_vazio_retorna_422():
    response = client.post("/ask", json={})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /ask – pipeline lança exceção (deve retornar 500)
# ---------------------------------------------------------------------------

@patch("app.api.routes.executar_pipeline", side_effect=RuntimeError("Falha simulada no pipeline"))
def test_ask_quando_pipeline_falha_retorna_500(mock_pipeline):
    response = client.post("/ask", json={"pergunta": "Pergunta qualquer"})
    assert response.status_code == 500
    assert "detail" in response.json()


# ---------------------------------------------------------------------------
# GET /history – caminho feliz
# ---------------------------------------------------------------------------

@patch("app.api.routes.buscar_historico", return_value=HISTORICO_RESULTADO_OK)
def test_history_retorna_200_com_lista(mock_historico):
    response = client.get("/history")
    assert response.status_code == 200
    corpo = response.json()
    assert "historico" in corpo
    assert isinstance(corpo["historico"], list)
    assert len(corpo["historico"]) == 1


@patch("app.api.routes.buscar_historico", return_value=[])
def test_history_retorna_lista_vazia_quando_sem_logs(mock_historico):
    response = client.get("/history")
    assert response.status_code == 200
    assert response.json()["historico"] == []


# ---------------------------------------------------------------------------
# GET /history – validação do parâmetro limite
# ---------------------------------------------------------------------------

@patch("app.api.routes.buscar_historico", return_value=[])
def test_history_limite_zero_retorna_422(mock_historico):
    """limite=0 está abaixo do mínimo ge=1 → 422."""
    response = client.get("/history?limite=0")
    assert response.status_code == 422


@patch("app.api.routes.buscar_historico", return_value=[])
def test_history_limite_acima_do_maximo_retorna_422(mock_historico):
    """limite=200 está acima do máximo le=100 → 422."""
    response = client.get("/history?limite=200")
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /history – buscar_historico lança exceção (deve retornar 500)
# ---------------------------------------------------------------------------

@patch("app.api.routes.buscar_historico", side_effect=Exception("Erro no banco"))
def test_history_quando_repositorio_falha_retorna_500(mock_historico):
    response = client.get("/history")
    assert response.status_code == 500
    assert "detail" in response.json()
