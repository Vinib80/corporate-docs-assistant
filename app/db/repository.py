import json
import sqlite3

from app.db.database import get_connection, init_db


def salvar_log(pergunta: str, resposta: str, fontes: list[str]) -> int:

    fontes_json = json.dumps(fontes, ensure_ascii=False)

    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO logs (pergunta, resposta, fontes) VALUES (?, ?, ?)",
        (pergunta, resposta, fontes_json),
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()

    return novo_id


def buscar_historico(limite: int = 20) -> list[dict]:

    conn = get_connection()
    conn.row_factory = sqlite3.Row  # permite acessar colunas pelo nome

    cursor = conn.execute(
        "SELECT id, pergunta, resposta, fontes, created_at FROM logs ORDER BY created_at DESC LIMIT ?",
        (limite,),
    )
    linhas = cursor.fetchall()
    conn.close()

    return [
        {
            "id": linha["id"],
            "pergunta": linha["pergunta"],
            "resposta": linha["resposta"],
            "fontes": json.loads(linha["fontes"]),  # JSON → lista Python
            "created_at": linha["created_at"],
        }
        for linha in linhas
    ]


if __name__ == "__main__":
    print("Inicializando banco de dados...")
    init_db()

    print("Inserindo log fictício...")
    log_id = salvar_log(
        pergunta="Quantos dias de férias tenho direito?",
        resposta="De acordo com a Política de Férias, o colaborador tem direito a 30 dias corridos.",
        fontes=["politica_ferias.md"],
    )
    print(f"  → Log salvo com id={log_id}")

    print("\nBuscando histórico...")
    historico = buscar_historico()
    for entrada in historico:
        print(f"  [{entrada['id']}] {entrada['created_at']}")
        print(f"       Pergunta : {entrada['pergunta']}")
        print(f"       Resposta : {entrada['resposta'][:60]}...")
        print(f"       Fontes   : {entrada['fontes']}")

    print("\nSmoke-test concluído com sucesso!")
