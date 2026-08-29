import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pergunta TEXT,
            resposta TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    conn.commit()
    conn.close()