from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class ClienteForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    endereco = StringField('Endereço', validators=[DataRequired()])
    cep = StringField('CEP', validators=[DataRequired()])
    cpf = StringField('CPF', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    telefone = StringField('Telefone', validators=[DataRequired()])
    submit = SubmitField('Adicionar Cliente')
