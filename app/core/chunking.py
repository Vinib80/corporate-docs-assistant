def chunk_por_paragrafo(caminho_arquivo):
    # 1. Abre e lê o arquivo inteiro
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        texto = arquivo.read()

    # 2. Divide o texto em parágrafos (assumindo por linha em branco)
    paragrafos = texto.split('\n\n')

    # 3. Limpa espaços extras e descarta trechos vazios
    chunks_limpos = [p.strip() for p in paragrafos if p.strip()]

    return chunks_limpos


if __name__ == '__main__':
    caminho_teste = '../../data/politica_ferias.md'
    chunks = chunk_por_paragrafo(caminho_teste)

    for indice, chunk in enumerate(chunks, start=1):
        print(f'--- Divisão {indice} ---')
        print(chunk)