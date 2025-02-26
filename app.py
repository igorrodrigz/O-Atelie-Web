from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required, LoginManager, login_user, logout_user, current_user
from init_db import get_db_connection
from flask_wtf.csrf import CSRFProtect
from auth import auth, login_manager, User, create_admin_user
from models import User  # Assuming you have a User model defined in models.py
from forms import ClienteForm  # Ensure ClienteForm is imported

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abra_cadabra'
app.config['SESSION_PERMANET'] = False
app.config['SESSION_TYPE'] = 'filesystem'
csrf = CSRFProtect(app)

# Inicializar o Login-Manager do Auth.py
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return User(user['id'], user['username'], user['password_hash'])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Entrou em login app.py")
    if request.method == 'POST':
        print("Entrou em POST app.py")
        username = request.form['username']
        print("Pegou o username")
        password = request.form['password']
        print("Pegou a senha")

        conn = get_db_connection()
        print("Conexão com o banco de dados estabelecida")
        cursor = conn.cursor(dictionary=True)
        print("Cursor criado")
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        print("Executou a query")
        user = cursor.fetchone()
        print("Pegou o usuário")
        conn.close()
        print("Fechou a conexão")

        if user and User(user['id'], user['username'], user['password_hash']).check_password(password):
            print("Usuário autenticado")
            user_obj = User(user['id'], user['username'], user['password_hash'])  # Corrigido para 'password_hash'
            print("Objeto de usuário criado")
            login_user(user_obj)
            print("Usuário autenticado: {current_user.is_authenticated} redirecionando...")  # Depuração

            return redirect(url_for('admin_dashboard'))  

        flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# 📌 Página inicial
@app.route('/')
def index():
    return render_template('index.html')

# 📌 Rota principal do painel
@app.route('/admin')
@login_required
def admin_dashboard():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('SELECT COUNT(*) AS total_clientes FROM cliente')
        total_clientes = cursor.fetchone()['total_clientes']

        cursor.execute('SELECT COUNT(*) AS total_servicos FROM servico WHERE status != "Entregue"')
        total_servicos = cursor.fetchone()['total_servicos']

        cursor.execute('SELECT COUNT(*) AS total_ferramentas FROM ferramenta')
        total_ferramentas = cursor.fetchone()['total_ferramentas']

        cursor.execute('SELECT SUM(quantidade) AS total_estoque FROM estoque')
        total_estoque = cursor.fetchone()['total_estoque']

        conn.close()

        return render_template('admin.html', total_clientes=total_clientes, total_servicos=total_servicos, total_ferramentas=total_ferramentas, total_estoque=total_estoque)
    except Exception as e:
        flash(f"Erro ao carregar o painel: {e}", "danger")
        return redirect(url_for('index'))


# 📌 Rotas para Clientes
@app.route('/clientes')
@login_required
def lista_clientes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM cliente')
        clientes = cursor.fetchall()
        conn.close()
        return render_template('clientes.html', clientes=clientes)
    except Exception as e:
        flash(f'Erro ao listar clientes: {e}', 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/clientes/add', methods=['GET', 'POST'])
@login_required
def add_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        try:
            nome = request.form['nome']
            endereco = request.form['endereco']
            cep = request.form['cep']
            cpf = request.form['cpf']
            email = request.form['email']
            telefone = request.form['telefone']

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO cliente (nome, endereco, cep, cpf, email, telefone) VALUES (%s, %s, %s, %s, %s, %s)',
                (nome, endereco, cep, cpf, email, telefone)
            )
            conn.commit()
            conn.close()
            flash('Cliente adicionado com sucesso!', 'success')
            return redirect(url_for('lista_clientes'))
        except Exception as e:
            flash(f'Erro ao adicionar cliente: {e}', 'danger')
            return redirect(url_for('add_cliente'))
    return render_template('add_cliente.html', form=form)

@app.route('/clientes/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_cliente(id):
    form = ClienteForm()
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            nome = request.form['nome']
            endereco = request.form['endereco']
            cep = request.form['cep']
            cpf = request.form['cpf']
            email = request.form['email']
            telefone = request.form['telefone']

            cursor.execute(
                '''UPDATE cliente SET nome = %s, endereco = %s, cep = %s, cpf = %s, email = %s, telefone = %s WHERE id = %s''',
                (nome, endereco, cep, cpf, email, telefone, id)
            )
            conn.commit()
            conn.close()
            flash('Cliente atualizado com sucesso!', 'success')
            return redirect(url_for('lista_clientes'))

        cursor.execute('SELECT * FROM cliente WHERE id = %s', (id,))
        cliente = cursor.fetchone()
        conn.close()
        return render_template('edit_cliente.html', cliente=cliente, form=form)
    except Exception as e:
        flash(f'Erro ao editar cliente: {e}', 'danger')
        return redirect(url_for('lista_clientes'))

@app.route('/clientes/view/<int:id>')
@login_required
def view_cliente(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM cliente WHERE id = %s', (id,))
        cliente = cursor.fetchone()

        cursor.execute('''
            SELECT * FROM servico
            WHERE cliente_id = %s
        ''', (id,))
        servicos = cursor.fetchall()

        conn.close()
        return render_template('view_cliente.html', cliente=cliente, servicos=servicos)
    except Exception as e:
        flash(f'Erro ao visualizar cliente: {e}', 'danger')
        return redirect(url_for('lista_clientes'))

@app.route('/clientes/delete/<int:id>', methods=['POST'])
@login_required
def delete_cliente(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cliente WHERE id = %s', (id,))
        conn.commit()
        conn.close()
        flash('Cliente excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir cliente: {e}', 'danger')
    return redirect(url_for('lista_clientes'))

# 📌 Rotas para Estoque
@app.route('/estoque')
@login_required
def lista_estoque():
    try:
        produto = request.args.get('produto')
        tipo_movimentacao = request.args.get('tipo_movimentacao')
        id = request.args.get('id')

        query = 'SELECT * FROM estoque WHERE 1=1'
        params = []

        if produto:
            query += ' AND produto LIKE %s'
            params.append(f'%{produto}%')
        if tipo_movimentacao:
            query += ' AND tipo_movimentacao = %s'
            params.append(tipo_movimentacao)
        if id:
            query += ' AND id = %s'
            params.append(id)

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        estoque = cursor.fetchall()
        conn.close()
        return render_template('estoque.html', estoque=estoque)
    except Exception as e:
        flash(f'Erro ao listar estoque: {e}', 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/estoque/add', methods=['GET', 'POST'])
@login_required
def add_estoque():
    if request.method == 'POST':
        try:
            produto = request.form['produto']
            quantidade = request.form['quantidade']
            tipo_movimentacao = request.form['tipo_movimentacao']
            data = request.form['data']

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO estoque (produto, quantidade, tipo_movimentacao, data) VALUES (%s, %s, %s, %s)',
                (produto, quantidade, tipo_movimentacao, data)
            )
            conn.commit()
            conn.close()
            flash('Item de estoque adicionado com sucesso!', 'success')
            return redirect(url_for('lista_estoque'))
        except Exception as e:
            flash(f'Erro ao adicionar item de estoque: {e}', 'danger')
            return redirect(url_for('add_estoque'))
    return render_template('add_estoque.html')

@app.route('/estoque/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_estoque(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            produto = request.form['produto']
            quantidade = request.form['quantidade']
            tipo_movimentacao = request.form['tipo_movimentacao']
            data = request.form['data']

            cursor.execute(
                '''UPDATE estoque SET produto = %s, quantidade = %s, tipo_movimentacao = %s, data = %s WHERE id = %s''',
                (produto, quantidade, tipo_movimentacao, data, id)
            )
            conn.commit()
            conn.close()
            flash('Item de estoque atualizado com sucesso!', 'success')
            return redirect(url_for('lista_estoque'))

        cursor.execute('SELECT * FROM estoque WHERE id = %s', (id,))
        item = cursor.fetchone()
        conn.close()
        return render_template('edit_estoque.html', item=item)
    except Exception as e:
        flash(f'Erro ao editar item de estoque: {e}', 'danger')
        return redirect(url_for('lista_estoque'))

@app.route('/estoque/delete/<int:id>', methods=['POST'])
@login_required
def delete_estoque(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM estoque WHERE id = %s', (id,))
        conn.commit()
        conn.close()
        flash('Item de estoque excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir item de estoque: {e}', 'danger')
    return redirect(url_for('lista_estoque'))

@app.route('/estoque/baixa/<int:id>', methods=['POST'])
@login_required
def baixa_estoque(id):
    try:
        quantidade = int(request.form['quantidade'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE estoque SET quantidade = quantidade - %s WHERE id = %s', (quantidade, id))
        conn.commit()
        conn.close()
        flash('Baixa de estoque realizada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao dar baixa no estoque: {e}', 'danger')
    return redirect(url_for('lista_estoque'))

@app.route('/estoque/entrada/<int:id>', methods=['POST'])
@login_required
def entrada_estoque(id):
    try:
        quantidade = int(request.form['quantidade'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE estoque SET quantidade = quantidade + %s WHERE id = %s', (quantidade, id))
        conn.commit()
        conn.close()
        flash('Entrada de estoque realizada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao dar entrada no estoque: {e}', 'danger')
    return redirect(url_for('lista_estoque'))

# 📌 Rotas para Ferramentas
@app.route('/ferramentas')
@login_required
def lista_ferramentas():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM ferramenta')
        ferramentas = cursor.fetchall()
        conn.close()
        return render_template('ferramentas.html', ferramentas=ferramentas)
    except Exception as e:
        flash(f'Erro ao listar ferramentas: {e}', 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/ferramentas/add', methods=['GET', 'POST'])
@login_required
def add_ferramenta():
    if request.method == 'POST':
        try:
            nome = request.form['nome']
            quantidade = request.form['quantidade']
            status = request.form['status']

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO ferramenta (nome, quantidade, status) VALUES (%s, %s, %s)',
                (nome, quantidade, status)
            )
            conn.commit()
            conn.close()
            flash('Ferramenta adicionada com sucesso!', 'success')
            return redirect(url_for('lista_ferramentas'))
        except Exception as e:
            flash(f'Erro ao adicionar ferramenta: {e}', 'danger')
            return redirect(url_for('add_ferramenta'))
    return render_template('add_ferramenta.html')

@app.route('/ferramentas/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_ferramenta(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            nome = request.form['nome']
            quantidade = request.form['quantidade']
            status = request.form['status']

            cursor.execute(
                '''UPDATE ferramenta SET nome = %s, quantidade = %s, status = %s WHERE id = %s''',
                (nome, quantidade, status, id)
            )
            conn.commit()
            conn.close()
            flash('Ferramenta atualizada com sucesso!', 'success')
            return redirect(url_for('lista_ferramentas'))

        cursor.execute('SELECT * FROM ferramenta WHERE id = %s', (id,))
        ferramenta = cursor.fetchone()
        conn.close()
        return render_template('edit_ferramenta.html', ferramenta=ferramenta)
    except Exception as e:
        flash(f'Erro ao editar ferramenta: {e}', 'danger')
        return redirect(url_for('lista_ferramentas'))

@app.route('/ferramentas/delete/<int:id>', methods=['POST'])
@login_required
def delete_ferramenta(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM ferramenta WHERE id = %s', (id,))
        conn.commit()
        conn.close()
        flash('Ferramenta excluída com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir ferramenta: {e}', 'danger')
    return redirect(url_for('lista_ferramentas'))

# 📌 Rotas para Serviços
@app.route('/servicos')
@login_required
def lista_servicos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT servico.*, cliente.nome AS nome_cliente
            FROM servico
            JOIN cliente ON servico.cliente_id = cliente.id
        ''')
        servicos = cursor.fetchall()
        conn.close()
        return render_template('servicos.html', servicos=servicos)
    except Exception as e:
        flash(f'Erro ao listar serviços: {e}', 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/servicos/add', methods=['GET', 'POST'])
@login_required
def add_servico():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, nome FROM cliente')
        clientes = cursor.fetchall()
        conn.close()

        cliente_id = request.args.get('cliente_id')

        if request.method == 'POST':
            nome_projeto = request.form['nome_projeto']
            cliente_id = request.form['cliente_id']
            data_entrada = request.form['data_entrada']
            data_prazo = request.form['data_prazo']
            status = request.form['status']
            detalhes = request.form['detalhes']
            material_adicional = request.form['material_adicional']
            valor = request.form['valor']
            quem_recebeu = request.form['quem_recebeu']
            aprovacao = request.form['aprovacao']
            data_entregue = request.form['data_entregue']
            quem_retirou = request.form['quem_retirou']

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO servico (nome_projeto, cliente_id, data_entrada, data_prazo, status, detalhes, material_adicional, valor, quem_recebeu, aprovacao, data_entregue, quem_retirou)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                (nome_projeto, cliente_id, data_entrada, data_prazo, status, detalhes, material_adicional, valor, quem_recebeu, aprovacao, data_entregue, quem_retirou)
            )
            conn.commit()
            conn.close()
            flash('Serviço adicionado com sucesso!', 'success')
            return redirect(url_for('lista_servicos'))
    except Exception as e:
        flash(f'Erro ao adicionar serviço: {e}', 'danger')
        return redirect(url_for('add_servico'))
    return render_template('add_servico.html', clientes=clientes, cliente_id=cliente_id)

@app.route('/servicos/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_servico(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            nome_projeto = request.form['nome_projeto']
            cliente_id = request.form['cliente_id']
            data_entrada = request.form['data_entrada']
            data_prazo = request.form['data_prazo']
            status = request.form['status']
            detalhes = request.form['detalhes']
            material_adicional = request.form['material_adicional']
            valor = request.form['valor']
            quem_recebeu = request.form['quem_recebeu']
            aprovacao = request.form['aprovacao']
            data_entregue = request.form['data_entregue']
            quem_retirou = request.form['quem_retirou']

            cursor.execute(
                '''UPDATE servico SET nome_projeto = %s, cliente_id = %s, data_entrada = %s, data_prazo = %s, status = %s, detalhes = %s, material_adicional = %s, valor = %s, quem_recebeu = %s, aprovacao = %s, data_entregue = %s, quem_retirou = %s WHERE id = %s''',
                (nome_projeto, cliente_id, data_entrada, data_prazo, status, detalhes, material_adicional, valor, quem_recebeu, aprovacao, data_entregue, quem_retirou, id)
            )
            conn.commit()
            conn.close()
            flash('Serviço atualizado com sucesso!', 'success')
            return redirect(url_for('lista_servicos'))

        cursor.execute('SELECT * FROM servico WHERE id = %s', (id,))
        servico = cursor.fetchone()
        cursor.execute('SELECT id, nome FROM cliente')
        clientes = cursor.fetchall()
        conn.close()
        return render_template('edit_servico.html', servico=servico, clientes=clientes)
    except Exception as e:
        flash(f'Erro ao editar serviço: {e}', 'danger')
        return redirect(url_for('lista_servicos'))

@app.route('/servicos/view/<int:id>')
@login_required
def view_servico(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT servico.*, cliente.nome AS nome_cliente
            FROM servico
            JOIN cliente ON servico.cliente_id = cliente.id
            WHERE servico.id = %s
        ''', (id,))
        servico = cursor.fetchone()
        conn.close()
        return render_template('view_servico.html', servico=servico)
    except Exception as e:
        flash(f'Erro ao visualizar serviço: {e}', 'danger')
        return redirect(url_for('lista_servicos'))

@app.route('/servicos/delete/<int:id>', methods=['POST'])
@login_required
def delete_servico(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM servico WHERE id = %s', (id,))
        conn.commit()
        conn.close()
        flash('Serviço excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir serviço: {e}', 'danger')
    return redirect(url_for('lista_servicos'))

@app.route('/admin/add_user', methods=['POST'])
@login_required
def add_user():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    hashed_password = User.hash_password(password)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)', (username, email, hashed_password))
        conn.commit()
        conn.close()
        flash('Usuário cadastrado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao cadastrar usuário: {e}', 'danger')

    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
