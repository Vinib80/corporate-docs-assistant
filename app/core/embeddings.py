import os

from dotenv import load_dotenv
from google import genai

load_dotenv()  # carrega GOOGLE_API_KEY do arquivo .env

_MODEL = "gemini-embedding-001"

# Cliente reutilizável ao longo da aplicação.
# load_dotenv() já foi chamado acima, então GOOGLE_API_KEY está disponível.
_client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])


def gerar_embedding(texto: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:

    resposta = _client.models.embed_content(
        model=_MODEL,
        contents=texto,
        config={"task_type": task_type},
    )
    return resposta.embeddings[0].values
