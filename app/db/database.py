import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "corporate_docs.db"

# Conversor explícito de TIMESTAMP → datetime (evita DeprecationWarning do Python 3.12)
sqlite3.register_converter(
    "TIMESTAMP",
    lambda b: datetime.fromisoformat(b.decode()),
)


def get_connection() -> sqlite3.Connection:
    """Retorna uma conexão com o banco, convertendo TIMESTAMP em datetime automaticamente."""
    return sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)


def init_db():
    """Cria o banco de dados e a tabela de logs, se ainda não existirem."""
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id         INTEGER   PRIMARY KEY AUTOINCREMENT,
            pergunta   TEXT      NOT NULL,
            resposta   TEXT      NOT NULL,
            fontes     TEXT      NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()