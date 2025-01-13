import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dados simulados
clientes = [
    {"id": 1, "nome": "João Silva", "email": "joao@email.com", "telefone": "1234-5678"},
    {"id": 2, "nome": "Maria Oliveira", "email": "maria@email.com", "telefone": "8765-4321"}
]

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with open('database.sql') as f:
        conn.executescript(f.read())
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clientes')
def lista_clientes():
    conn = get_db_connection()
    clientes = conn.execute('SELECT * FROM cliente').fetchall()
    conn.close()
    return render_template('clientes.html', clientes=clientes)

@app.route('/clientes/add', methods=['GET', 'POST'])
def add_cliente():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        conn = get_db_connection()
        conn.execute('INSERT INTO cliente (nome, email, telefone) VALUES (?, ?, ?)',
                     (nome, email, telefone))
        conn.commit()
        conn.close()
        return redirect(url_for('lista_clientes'))
    return render_template('add_cliente.html')

@app.route('/estoque', methods=['GET'])
def lista_estoque():
    nome = request.args.get('nome')
    categoria = request.args.get('categoria')

    query = 'SELECT * FROM estoque WHERE 1=1'
    params = []

    if nome:
        query += ' AND nome LIKE ?'
        params.append(f'%{nome}%')
    if categoria:
        query += ' AND categoria = ?'
        params.append(categoria)

    conn = get_db_connection()
    itens = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('estoque.html', itens=itens)

@app.route('/estoque/add', methods=['GET', 'POST'])
def add_estoque():
    if request.method == 'POST':
        produto = request.form['produto']
        quantidade = request.form['quantidade']
        tipo_movimentacao = request.form['tipo_movimentacao']
        data = request.form['data']
        conn = get_db_connection()
        conn.execute('INSERT INTO estoque (produto, quantidade, tipo_movimentacao, data) VALUES (?, ?, ?, ?)',
                     (produto, quantidade, tipo_movimentacao, data))
        conn.commit()
        conn.close()
        return redirect(url_for('lista_estoque'))
    return render_template('add_estoque.html')

@app.route('/ferramentas')
def lista_ferramentas():
    conn = get_db_connection()
    ferramentas = conn.execute('SELECT * FROM ferramenta').fetchall()
    conn.close()
    return render_template('ferramentas.html', ferramentas=ferramentas)

@app.route('/ferramentas/add', methods=['GET', 'POST'])
def add_ferramentas():
    if request.method == 'POST':
        ferramenta = request.form['ferramenta']
        quantidade = request.form['quantidade']
        tipo_movimentacao = request.form['tipo_movimentacao']
        data = request.form['data']
        conn = get_db_connection()
        conn.execute('INSERT INTO ferramentas (ferramenta, quantidade, tipo_movimentacao, data) VALUES (?, ?, ?, ?)',
                     (ferramenta, quantidade, tipo_movimentacao, data))
        conn.commit()
        conn.close()
        return redirect(url_for('lista_ferramentas'))
    return render_template('add_ferramentas.html')


@app.route('/servico')
def lista_servicos():
    conn = get_db_connection()
    servicos = conn.execute('SELECT * FROM servico').fetchall()
    conn.close()
    return render_template('servicos.html', servicos=servicos)

@app.route('/add_servico', methods=('GET', 'POST'))
def add_servico():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = request.form['preco']

        conn = get_db_connection()
        conn.execute('INSERT INTO servico (nome, descricao, preco) VALUES (?, ?, ?)',
                     (nome, descricao, preco))
        conn.commit()
        conn.close()
        return redirect(url_for('lista_servicos'))
    return render_template('add_servico.html')

@app.route('/edit_servico/<int:id>', methods=('GET', 'POST'))
def edit_servico(id):
    conn = get_db_connection()
    servico = conn.execute('SELECT * FROM servico WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = request.form['preco']

        conn.execute('UPDATE servico SET nome = ?, descricao = ?, preco = ? WHERE id = ?',
                     (nome, descricao, preco, id))
        conn.commit()
        conn.close()
        return redirect(url_for('lista_servicos'))
    
@app.route('/view_servico/<int:id>')
def view_servico(id):
    conn = get_db_connection()
    servico = conn.execute('SELECT * FROM servico WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('view_servico.html', servico=servico)

    conn.close()
    return render_template('edit_servico.html', servico=servico)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
