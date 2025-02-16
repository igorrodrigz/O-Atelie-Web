import mysql.connector
import os

# Configuração do banco de dados MySQL
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="193.203.175.175",
            user="u123466556_igorzinho",
            password="@Anastasia20",
            database="u123466556_atelier_web"
        )
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        raise Exception("Erro ao conectar ao banco de dados")

# Criar tabelas ao iniciar
def create_tables():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cliente (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                endereco VARCHAR(255),
                cep VARCHAR(20),
                cpf VARCHAR(20),
                email VARCHAR(100) NOT NULL UNIQUE,
                telefone VARCHAR(20) NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estoque (
                id INT AUTO_INCREMENT PRIMARY KEY,
                produto VARCHAR(100) NOT NULL,
                quantidade INT NOT NULL,
                tipo_movimentacao VARCHAR(10) NOT NULL,
                data DATE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ferramenta (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                quantidade INT NOT NULL,
                status VARCHAR(50) NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS servico (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome_projeto VARCHAR(100) NOT NULL,
                cliente_id INT NOT NULL,
                data_entrada DATE NOT NULL,
                data_prazo DATE NOT NULL,
                status VARCHAR(50) NOT NULL,
                detalhes TEXT NOT NULL,
                material_adicional TEXT,
                valor FLOAT NOT NULL,
                quem_recebeu VARCHAR(100),
                aprovacao VARCHAR(100),
                data_entregue DATE,
                quem_retirou VARCHAR(100),
                FOREIGN KEY (cliente_id) REFERENCES cliente(id)
            )
        """)

        conn.commit()

    except mysql.connector.Error as err:
        print(f"Erro ao executar as consultas SQL: {err}")
    finally:
        if conn:
            conn.close()

# Chamada para criar as tabelas
create_tables()
