import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

_MODEL = "gemini-3.5-flash"
_client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

_SYSTEM_PROMPT = """\
Você é um assistente corporativo especializado em responder perguntas \
com base em documentos internos da empresa.

Regras que você DEVE seguir:
1. Responda SOMENTE com informações presentes no contexto fornecido. \
   Nunca use conhecimento geral ou externo.
2. Ao usar uma informação, cite entre parênteses o nome do documento \
   de origem, por exemplo: (Fonte: politica_ferias.md).
3. Se a resposta não estiver no contexto, diga claramente: \
   "Não encontrei essa informação nos documentos disponíveis."
4. Responda sempre em português brasileiro, de forma clara e objetiva.
"""


def _formatar_contexto(chunks: list[dict]) -> str:
    """Formata a lista de chunks como bloco de contexto para o prompt."""
    partes = []
    for i, chunk in enumerate(chunks, start=1):
        partes.append(
            f"[Trecho {i} — Fonte: {chunk['fonte']}]\n{chunk['texto']}"
        )
    return "\n\n---\n\n".join(partes)


def gerar_resposta(pergunta: str, chunks: list[dict]) -> dict:
    
    contexto = _formatar_contexto(chunks)

    prompt_usuario = (
        f"Contexto extraído dos documentos corporativos:\n\n"
        f"{contexto}\n\n"
        f"Pergunta: {pergunta}"
    )

    resposta = _client.models.generate_content(
        model=_MODEL,
        contents=prompt_usuario,
        config=types.GenerateContentConfig(
            system_instruction=_SYSTEM_PROMPT,
            temperature=0.2,  # pouca criatividade: priorizamos fidelidade ao contexto
        ),
    )

    texto_resposta = resposta.text

    # Deduplica preservando a ordem de aparição
    fontes_vistas: set[str] = set()
    fontes_unicas: list[str] = []
    for chunk in chunks:
        fonte = chunk["fonte"]
        if fonte not in fontes_vistas:
            fontes_vistas.add(fonte)
            fontes_unicas.append(fonte)

    return {
        "resposta": texto_resposta,
        "fontes": fontes_unicas,
    }
