"""
Script de ingestão: popula o ChromaDB com os embeddings de todos os
documentos corporativos da pasta data/.

Fluxo por documento:
    1. chunk_por_paragrafo()  → divide o texto em trechos com overlap
    2. gerar_embedding()      → converte cada trecho em vetor (Gemini API)
    3. adicionar_chunks()     → persiste vetores + metadados no ChromaDB

Como executar:
    source .venv/bin/activate
    python scripts/ingest.py

O script é idempotente: pode ser rodado mais de uma vez sem duplicar dados,
pois usa upsert internamente (chunks com o mesmo id são sobrescritos).
"""

import sys
import time
from pathlib import Path

# Garante que os módulos em app/ são encontrados independente de onde o
# script é chamado
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))

from core.chunking import chunk_por_paragrafo
from core.embeddings import gerar_embedding
from core.vector_store import adicionar_chunks, obter_colecao

DATA_DIR = ROOT / "data"


def ingerir_documento(caminho: Path) -> int:
    """Chunka, embeda e indexa um único documento (.md ou .txt).

    Args:
        caminho: Caminho absoluto para o arquivo de documento.

    Returns:
        Quantidade de chunks indexados para este documento.
    """
    nome_arquivo = caminho.name
    chunks = chunk_por_paragrafo(str(caminho))

    if not chunks:
        print(f"  [aviso] {nome_arquivo} não gerou nenhum chunk — arquivo vazio?")
        return 0

    print(f"  {nome_arquivo}: {len(chunks)} chunk(s) encontrado(s). Gerando embeddings...")

    chunks_com_meta = []
    for indice, texto in enumerate(chunks):
        embedding = gerar_embedding(texto, task_type="RETRIEVAL_DOCUMENT")

        chunks_com_meta.append(
            {
                # ID único e rastreável: "politica_ferias.md_0", "manual_ti.txt_0", ...
                "id": f"{nome_arquivo}_{indice}",
                "texto": texto,
                "embedding": embedding,
                "fonte": nome_arquivo,
            }
        )

        # Pequena pausa para respeitar o rate limit do plano gratuito da API
        time.sleep(0.3)

    adicionar_chunks(chunks_com_meta)
    return len(chunks_com_meta)


def main():
    # Coleta arquivos .md e .txt, ordenados por nome para execução determinística
    arquivos = sorted(
        [*DATA_DIR.glob("*.md"), *DATA_DIR.glob("*.txt")]
    )

    if not arquivos:
        print(f"Nenhum arquivo .md ou .txt encontrado em {DATA_DIR}. Abortando.")
        sys.exit(1)

    print(f"Iniciando ingestão de {len(arquivos)} documento(s)...\n")

    # Exibe aviso se a coleção já tiver dados (ingestão prévia detectada)
    colecao = obter_colecao()
    total_existente = colecao.count()
    if total_existente > 0:
        print(
            f"[aviso] A coleção já contém {total_existente} chunk(s). "
            "Os existentes serão sobrescritos (upsert).\n"
        )

    total_chunks = 0
    for caminho in arquivos:
        total_chunks += ingerir_documento(caminho)

    print(f"\nIngestão concluída! Total de chunks indexados: {total_chunks}")
    print(f"Chunks na coleção agora: {colecao.count()}")


if __name__ == "__main__":
    main()

