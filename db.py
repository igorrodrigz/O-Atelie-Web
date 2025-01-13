from init_db import app, db


# Criação das tabelas dentro do contexto da aplicação
with app.app_context():
    db.create_all()
    print("Tabelas criadas com sucesso!")
