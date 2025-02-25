from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from init_db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from models import User

auth = Blueprint('auth', __name__)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = "Faça login para acessar esta página."

# Buscar usuário no banco
def get_user_by_username(username):
    print(f"Buscando usuário por username: {username}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()

        if user:
            print(f"Usuário encontrado: {user}")
            return User(user['id'], user['username'], user['password_hash'])
        print("Usuário não encontrado")
        return None
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        return None

# Criar usuário administrador se não existir
def create_admin_user():
    print("Verificando se usuário administrador existe")
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", ('admin',))
        admin = cursor.fetchone()

        if not admin:
            print("Usuário administrador não encontrado, criando novo usuário")
            hashed_password = generate_password_hash('admin', method='sha256')
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                           ('admin', hashed_password))
            conn.commit()
            print("Usuário administrador criado com sucesso.")
        else:
            print("Usuário administrador já existe")
        conn.close()
    except Exception as e:
        print(f"Erro ao criar usuário administrador: {e}")

# Inicializar o login manager e criar o usuário administrador
@login_manager.user_loader
def load_user(user_id):
    print(f"Carregando usuário com ID: {user_id}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            print(f"Usuário carregado: {user}")
            return User(user['id'], user['username'], user['password_hash'])
        print("Usuário não encontrado")
        return None
    except Exception as e:
        print(f"Erro ao carregar usuário: {e}")
        return None

create_admin_user()

# Rota de login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    print("Entrou na rota de login")
    if request.method == 'POST':
        print("Método POST recebido na rota de login")
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)

        if user and user.check_password(password):
            login_user(user)
            print(f"Usuário {username} logado com sucesso.")
            return redirect(url_for('index.html'))
        else:
            print("Credenciais inválidas")
            flash("Credenciais inválidas", "danger")
    return render_template('login.html')

# Rota de logout
@auth.route('/logout')
@login_required
def logout():
    print("Usuário deslogando")
    logout_user()
    return redirect(url_for('auth.login'))