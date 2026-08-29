def chunk_por_paragrafo(caminho_arquivo, tamanho_janela=2, overlap=1):
    # 1. Abre e lê o arquivo inteiro
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        texto = arquivo.read()

    # 2. Divide o texto em parágrafos (linha em branco como separador)
    paragrafos = texto.split('\n\n')

    # 3. Limpa espaços extras e descarta trechos vazios
    paragrafos_limpos = [p.strip() for p in paragrafos if p.strip()]

    passo = tamanho_janela - overlap
    chunks = []

    for inicio in range(0, len(paragrafos_limpos), passo):
        janela = paragrafos_limpos[inicio : inicio + tamanho_janela]
        # Une os parágrafos da janela num único texto, separados por linha em branco
        chunk = '\n\n'.join(janela)
        chunks.append(chunk)

    return chunks


if __name__ == '__main__':
    caminho_teste = '../../data/politica_ferias.md'
    chunks = chunk_por_paragrafo(caminho_teste)

    for indice, chunk in enumerate(chunks, start=1):
        print(f'--- Chunk {indice} ---')
        print(chunk)
        print()