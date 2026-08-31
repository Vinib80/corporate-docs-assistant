# Corporate Docs Assistant

Assistente inteligente que responde perguntas em linguagem natural com base em documentos corporativos internos, usando o padrão **RAG (Retrieval-Augmented Generation)** — busca semântica nos documentos seguida de geração de resposta com IA generativa, **sempre citando a fonte** usada.

> Projeto desenvolvido como desafio técnico do processo seletivo de Estágio em Engenharia de Software e IA — HUB de Dados & IA, Grupo Moura.

---

## Índice

- [Contexto do problema](#contexto-do-problema)
- [Como funciona (arquitetura)](#como-funciona-arquitetura)
- [Stack tecnológica](#stack-tecnológica)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e configuração](#instalação-e-configuração)
- [Como rodar](#como-rodar)
- [Uso da API](#uso-da-api)
- [Documentos de exemplo](#documentos-de-exemplo)
- [Testes](#testes)
- [Decisões de projeto](#decisões-de-projeto)
- [Limitações conhecidas / próximos passos](#limitações-conhecidas--próximos-passos)
- [Vídeo de apresentação](#vídeo-de-apresentação)

---

## Contexto do problema

Colaboradores do Grupo Moura precisam consultar informações espalhadas em diversos documentos internos (políticas de RH, manuais de segurança, procedimentos de acesso, FAQs de benefícios). Hoje essa busca é manual ou depende de abrir um chamado. Este projeto prototipa um assistente que recebe uma pergunta em linguagem natural, recupera o trecho relevante nos documentos e gera uma resposta clara **com base apenas nesse conteúdo**, indicando de qual documento a informação veio.

## Como funciona (arquitetura)

```
Pergunta do usuário
      │
      ▼
Gera embedding da pergunta (Gemini Embeddings)
      │
      ▼
Busca os chunks mais similares no ChromaDB (top-k)
      │
      ▼
Monta prompt com os trechos recuperados como contexto
      │
      ▼
Gemini gera a resposta SOMENTE com base no contexto
      │
      ▼
Resposta + fontes são salvas no SQLite (log) e retornadas na API
```

Etapas do pipeline (ver `app/core/rag_pipeline.py`):

1. **Ingestão** (`scripts/ingest.py`): lê os documentos de `/data`, divide em chunks por parágrafo (com overlap), gera embeddings e indexa no ChromaDB.
2. **Retrieval**: a pergunta do usuário é transformada em embedding e comparada por similaridade (distância cosseno) com os chunks indexados.
3. **Generation**: os chunks recuperados são injetados no prompt como contexto; o modelo é instruído a responder apenas com base neles e a citar a fonte.
4. **Persistência**: cada interação (pergunta, resposta, fontes) é registrada no SQLite para consulta posterior via `/history`.

## Stack tecnológica

| Camada                  | Tecnologia                              |
|-------------------------|-----------------------------------------|
| API                     | [FastAPI](https://fastapi.tiangolo.com/)|
| IA generativa           | Google Gemini (`google-genai`)          |
| Embeddings              | `gemini-embedding-001`                  |
| Geração de texto        | `gemini-3.5-flash`                      |
| Banco vetorial          | [ChromaDB](https://www.trychroma.com/) (persistente em disco) |
| Persistência relacional | SQLite (`sqlite3` nativo, sem ORM)      |
| Validação/schemas       | Pydantic                                |

> Por que sem framework de orquestração (ex.: LangChain) e sem ORM? Optei por implementar chunking, retrieval e persistência com bibliotecas nativas/mínimas para poder entender e explicar cada peça do pipeline em detalhe — trade-off consciente de simplicidade e transparência em vez de abstração.

## Estrutura do repositório

```
corporate-docs-assistant/
├── app/
│   ├── main.py              # Ponto de entrada da aplicação FastAPI
│   ├── schemas.py           # Modelos Pydantic (request/response)
│   ├── api/
│   │   └── routes.py        # Endpoints: /ask, /history, /health
│   ├── core/
│   │   ├── chunking.py      # Divisão dos documentos em chunks (com overlap)
│   │   ├── embeddings.py    # Geração de embeddings (Gemini)
│   │   ├── vector_store.py  # Indexação e busca por similaridade (ChromaDB)
│   │   ├── generation.py    # Geração da resposta final (Gemini)
│   │   └── rag_pipeline.py  # Orquestra retrieval + generation + log
│   └── db/
│       ├── database.py      # Conexão e criação do schema SQLite
│       └── repository.py    # Funções de leitura/escrita dos logs
├── data/                    # Documentos corporativos fictícios (.md / .txt)
├── scripts/
│   └── ingest.py            # Script de ingestão: indexa /data no ChromaDB
├── tests/                   # Testes automatizados
├── requirements.txt
├── .env.example
└── README.md
```

## Pré-requisitos

- Python 3.11+
- Uma chave de API gratuita do Google Gemini ([Google AI Studio](https://aistudio.google.com/apikey))

## Instalação e configuração

```bash
# 1. Clone o repositório
git clone https://github.com/Vinib80/corporate-docs-assistant.git
cd corporate-docs-assistant

# 2. Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure sua chave de API
cp .env.example .env
# edite o .env e substitua "sua_chave_aqui" pela sua GOOGLE_API_KEY
```

## Como rodar

```bash
# 1. Ingestão: indexa os documentos de /data no ChromaDB (rode sempre que /data mudar)
python scripts/ingest.py

# 2. Suba a API
uvicorn app.main:app --reload
```

A API sobe em `http://localhost:8000`. Documentação interativa (Swagger) disponível em `http://localhost:8000/docs`.

## Uso da API

### `POST /ask`

Faz uma pergunta em linguagem natural com base nos documentos indexados.

**Request**
```json
{
  "pergunta": "Quantos dias de férias eu acumulo por ano?"
}
```

**Response**
```json
{
  "resposta": "De acordo com a Política de Férias, o colaborador acumula 30 dias corridos por ano trabalhado (Fonte: politicas_ferias.md).",
  "fontes": ["politicas_ferias.md"],
  "log_id": 1
}
```

### `GET /history?limite=20`

Retorna o histórico das últimas perguntas e respostas registradas.

### `GET /health`

Health check simples (`{"status": "ok"}`).

## Documentos de exemplo

A pasta `/data` contém documentos corporativos **fictícios**, criados para este desafio:

- `politicas_ferias.md` — política de férias
- `manual_seguranca_info.txt` — manual de segurança da informação
- `faq_beneficios.txt` — FAQ de benefícios
- `procedimento_acesso_sistema.md` — procedimento de solicitação de acesso a sistemas

## Testes

```bash
pytest
```

Os testes automatizados cobrem as principais partes do pipeline e da API, utilizando mocks ou instâncias em memória para garantir isolamento e execução rápida:

- `test_api.py`: Testa os endpoints do FastAPI (`/ask`, `/history`, `/health`), validando as rotas, modelos Pydantic de entrada/saída e status codes, com auxílio do `TestClient`.
- `test_chunking.py`: Valida a lógica de divisão de textos em partes menores (chunks), garantindo que o limite de tamanho seja respeitado e que exista a sobreposição (overlap) correta entre os blocos.
- `test_retrieval.py`: Verifica as operações no ChromaDB usando um `EphemeralClient` (em memória) isolado. Garante a indexação correta dos dados (e prevenção de duplicatas via ID), além de validar o retorno das buscas baseadas em similaridade.
- `test_repository.py`: Verifica a camada de persistência relacional com o SQLite configurado em memória (`:memory:`), validando as operações de salvar logs de interações e buscar o histórico corretamente.

## Decisões de projeto

- **Chunking por parágrafo com overlap**, em vez de chunking por número fixo de caracteres, para preservar melhor o sentido semântico de cada trecho.
- **SQLite nativo** em vez de ORM, por ser uma necessidade de persistência simples (log de interações).

---

**Autor:** Vinicius Bernardo

