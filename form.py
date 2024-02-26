from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, StringField, EmailField
from wtforms.validators import InputRequired, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Username: ', validators=[InputRequired()])
    email = EmailField('Email: ', validators=[InputRequired()])
    password = PasswordField('Password: ', validators=[InputRequired()])
    re_password = PasswordField('Retype ypur password: ', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Submit')
