from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from init_db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# Modelo de Usuário
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.username = username
        self.password = password

# Buscar usuário no banco
def get_user_by_username(username):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()

        if user:
            return User(user['id'], user['username'], user['password'])
        return None
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        return None

# Criar usuário administrador
def create_admin_user():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin WHERE username = %s", ('admin',))
        admin = cursor.fetchone()

        if not admin:
            hashed_password = generate_password_hash('admin', method='sha256')
            cursor.execute("INSERT INTO admin (username, password) VALUES (%s, %s)", ('admin', hashed_password))
            conn.commit()
            print("Usuário administrador criado com sucesso.")
        conn.close()
    except Exception as e:
        print(f"Erro ao criar usuário administrador: {e}")

# Inicializar o login manager e criar o usuário administrador
@login_manager.user_loader
def load_user(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            return User(user['id'], user['username'], user['password'])
        return None
    except Exception as e:
        print(f"Erro ao carregar usuário: {e}")
        return None

create_admin_user()

# Rota de login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Credenciais inválidas", "danger")

    return render_template('login.html')

# Rota de logout
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))