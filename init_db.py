import sqlite3

# Conexão com o banco de dados
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Criação das tabelas
cursor.execute('''
CREATE TABLE IF NOT EXISTS cliente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    telefone TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS estoque (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto TEXT NOT NULL,
    quantidade INTEGER NOT NULL,
    tipo_movimentacao TEXT NOT NULL,
    data TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS ferramenta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    quantidade INTEGER NOT NULL,
    status TEXT NOT NULL
)
''')

# Fechando a conexão
conn.commit()
conn.close()

print("Banco de dados inicializado com sucesso!")
