import sqlite3

DB_NAME = "usuarios_banco.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

cursor.execute(
    "INSERT OR IGNORE INTO usuarios (username, password) VALUES (?, ?)",
    ("admin", "1234")
)
cursor.execute(
    "INSERT OR IGNORE INTO usuarios (username, password) VALUES (?, ?)",
    ("andrea", "senha123")
)
cursor.execute(
    "INSERT OR IGNORE INTO usuarios (username, password) VALUES (?, ?)",
    ("teste", "teste123")
)

conn.commit()
conn.close()

print("Banco criado com sucesso.")